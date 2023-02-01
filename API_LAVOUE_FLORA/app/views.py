# -*- coding: utf-8 -*-
"""
Created on Thu Oct  6 15:37:58 2022

@author: flola
"""
from app import app
from flask import render_template, request,jsonify, Flask, redirect, url_for
import json, urlopen
import sqlite3
import requests
import openfoodfacts
from flask_swagger_ui import get_swaggerui_blueprint

# cur.execute('select * from recette').fetchall()[-1])



@app.route('/')
def index():
    global id
    with sqlite3.connect("database.db") as con:
        cur = con.cursor()
        id = cur.execute('select * from recette').fetchall()  #recuperer l'id de la dernière ligne insérée = compter le nombre de lignes de la table +1
        id=int(len(id))
        cur.close()
    con.close()
    id+=1
    return render_template ('inscription.html')

@app.route('/recettes', methods=["GET","POST"])
def inscription():
    global id
    if request.method == "POST":
        prenom=request.form.get("prenom")
        nom=request.form.get("nom")
        mdp=request.form.get("mdp")
        liste_ingredient=''
        user={'prenom':'flora','nom':'lavoue','mdp':'mdp'}
        with sqlite3.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("INSERT OR REPLACE INTO recette (id,prenom,nom,mdp,ingredient) VALUES (?,?,?,?,?)", (str(id),prenom,nom,mdp,liste_ingredient))
            
            con.commit()
            cur.close()
        con.close()
        return render_template ('recette.html', title='MDM',utilisateur=user, prenom=prenom, nom=nom, mdp=mdp)
    
    elif request.method == 'GET':
        prenom=request.form.get("prenom")
        nom=request.form.get("nom")
        mdp=request.form.get("mdp")
        user={'prenom':'flora','nom':'lavoue','mdp':'mdp'}
        return render_template ('recette.html', title='MDM',utilisateur=user)
    


@app.route('/recettes/nutrition', methods=["GET","POST"]) 
def recette(): 
    global id
    #faire zone de texte avec ingrédients, photo
    #proposition de produits + quantité consommé
    # text = request.form['text']
    # processed_text = text.upper()
    # return processed_text    
    #importer la base de donnée
    # result=request.args
    # prenom=result['prenom']
    # nom=result['nom']
    # mdp=result['mdp']

    if request.method == "POST":
        ingredient=request.form.get("story")
        if ingredient != '':
            liste_ingredient=str(ingredient).splitlines()
            n=len(liste_ingredient)
            print(liste_ingredient)   
            
            with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                sql = "UPDATE recette SET ingredient = ? WHERE id = ?"
                value = (ingredient, str(id))
                cur.execute(sql, value)
                id=id+1
                con.commit()
                
                #récupérer les ingrédients de la recette qui vient d'être enregistrée
                # cur.Cursor.execute("""SELECT id, ingredient FROM recette WHERE id=?""", (id,))
                # response = cur.Cursor.fetchone()
                
                cur.close()
            con.close()
            
        #dictionnaire des produits
        produits={'nutella':3017620425035,'banane':3523680438224,'frites':8710438109351,'compote':3608580789758 ,'Maïzena':8712100338694, 'jambon':7613035989443}
        
        
        URL=[]
        ingredients=[]
        nutri_score= []
        Analyses=''
        additifs=''
        
        #analyse
        palm_oil=[]
        non_vegan=[]
        non_vegetarian=[]
        
        
        for i in range(n):
            produit=liste_ingredient[i]
            code=produits[produit]
            former_url='https://fr.openfoodfacts.org/api/v0/produit/'
            former_url+=str(code)
            former_url+='.json'
            URL.append( former_url)
            
            
            
        for url in URL: 
            info_produit=requests.get(url)
            data=json.loads(info_produit.text)
            ingredients.append(data['product']['ingredients_text']) 
            
            #extract de l'analyse
            analyse= data['product']['ingredients_analysis_tags']
            for i in range(len(analyse)):
                if analyse[i][3:]=='palm-oil':
                    palm_oil.append(analyse[i][3:])
                if (analyse[i][3:]=='palm-oil-free') and (palm_oil==False):
                    palm_oil.append(analyse[i][3:])
                    
                    
                if analyse[i][3:]=='non-vegan':
                    non_vegan.append(analyse[i][3:])
                if analyse[i][3:]=='vegan':
                    non_vegan.append(analyse[i][3:])
                    
                    
                if analyse[i][3:]=='non-vegetarian':
                    non_vegetarian.append(analyse[i][3:])
                if analyse[i][3:]=='vegetarian':
                    non_vegetarian.append(analyse[i][3:])
             

            
            #extract des additifs
            addi_tif=data['product']['additives_old_tags']
            for i in range(len(addi_tif)):                
                additifs+=addi_tif[i][3:]
                additifs+=', '
                
            
            #calcul du nutriscore
            nutri_score.append(data['product']['nutriscore_score'])
            
        palm=False
        v=False
        vg=False
        for oil in palm_oil:
            if oil=='palm-oil':
                palm=True
                break
        if palm==True:
            Analyses+='huile de palme'
            Analyses+=', ' 
        else :
            Analyses+='Sans Huile de palme'
            Analyses+=', ' 
            
        for vegan in non_vegan:
            if vegan=='non-vegan':
                v=True
                break
        if v==True:
            Analyses+='non-vegan'
            Analyses+=', ' 
        else :
            Analyses+='vegan'
            Analyses+=', ' 
            
        for vege in non_vegetarian:
            if vege=='non_vegetarian':
                vg=True
                break
        if vg==True:
            Analyses+='non_vegetarien'
            Analyses+=', ' 
        else :
            Analyses+='vegetarien'
            Analyses+=', ' 
                
        nutriscore=calcul_nutriscore(nutri_score)
        
            
        return render_template ('nutrition.html', title='Recettes', ingredients=ingredients, nutriscore=nutriscore, analyse=Analyses, additif=additifs)
    


@app.route('/recettes/nutrition', methods=["GET","POST"]) 
def nutrition(): 
    #donner nutrition du plats, empreinte carbone
    #calories,huile de palme , additifs
    if request.method == "POST":
        return render_template ('nutrition.html')





def insert_into(name, address):
  try:
    conn = sqlite3.connect('my.db')
    cur = conn.cursor()
    print("Connexion réussie à SQLite")
    sql = "INSERT INTO person (name, address) VALUES (?, ?)"
    value = (name, address)
    cur.execute(sql, value)
    conn.commit()
    print("Enregistrement inséré avec succès dans la table person")
    cur.close()
    conn.close()
    print("Connexion SQLite est fermée")
  except sqlite3.Error as error:
    print("Erreur lors de l'insertion dans la table person", error)
    
def calcul_nutriscore(nutriscore):
    nutriscore=int(sum(nutriscore) / len(nutriscore))
    if nutriscore<=-1:
        resultat='A'
    if 0<=nutriscore<=2:
        resultat='B'
    if 3<=nutriscore<=10:
        resultat='C'
    if 11<=nutriscore<=18:
        resultat='D'
    if 19<=nutriscore<=40:
        resultat='E'
    return resultat
    
        


    