import os


basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')


SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
# Adrien's sheets
# SPREADSHEET_ID = '185s4y0PR0vvNY0wCL8cTjSOtFg2V1s3e1FqwtUZynjw'
# IMPORT = 'Feuille 1'
# Etienne's sheets
# SPREADSHEET_ID = '1ce-Ub6gJGc2Fi_p0KA6GqePhKvEclzc51sanYShblcU'
SPREADSHEET_ID = '1lOWe3j-4KG62wcKCsBd7T0Yj4iduFzH5QB76wS7dc9M'
IMPORT = 'Import'