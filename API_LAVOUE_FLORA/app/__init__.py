# -*- coding: utf-8 -*-
"""
Created on Thu Oct  6 15:39:41 2022

@author: flola
"""
import sqlite3
from flask import Flask
app= Flask(__name__)
from app import views
from flask_swagger_ui import get_swaggerui_blueprint

conn = sqlite3.connect ( 'database.db' ) 
conn.execute ('CREATE TABLE IF NOT EXISTS recette (id INTEGER PRIMARY KEY,prenom TEXT, nom TEXT, mdp TEXT, ingredient TEXT)' )
conn.close ()

### swagger specific ###
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Seans-Python-Flask-REST-Boilerplate"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)

# python app.py
