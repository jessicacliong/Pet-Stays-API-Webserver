from flask import Flask
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
# set the database URI via SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://db_dev:12345abc@localhost:5432/pet_sitting_api"
# to avoid the deprecation warning
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

#create the database object
db = SQLAlchemy(app)

def create_app():
  # using a list comprehension and multiple assignment 
  # to grab the environment variables we need
  
  # Creating the flask app object - this is the core of our app!
  app = Flask(__name__)

  # configuring our app:
  app.config.from_object("config.app_config")

  # creating our database object! This allows us to use our ORM
  db = SQLAlchemy(app)
  
  return app