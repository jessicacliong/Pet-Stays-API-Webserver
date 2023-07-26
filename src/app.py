from flask import Flask
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
# set the database URI via SQLAlchemy, 
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://db_dev:12345abc@localhost:5432/pet_sitting_api"
# to avoid the deprecation warning
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

#create the database object
db = SQLAlchemy(app)

@app.cli.command("create")
def create_db():
  db.create_all()
  print("Tables created")

@app.cli.command("seed")
def seed_db():
  pass

@app.cli.command("drop")
def drop_db():
    db.drop_all()
    print("Tables dropped")

class Customer(db.Model):
  # define the table name for the db
  __tablename__= "customer"
  # Set the primary key, we need to define that each attribute is also a column in the db table, remember "db" is the object we created in the previous step.
  id = db.Column(db.Integer,primary_key=True)
  # Add the rest of the attributes. 
  first_name = db.Column(db.String())
  last_name = db.Column(db.String())
  email = db.Column(db.String())
  password = db.Column(db.String())
  pet = db.relationship(
    "Pet",
    backref="customer",
    cascade="all, delete"
  )
  message = db.relationship(
    "Message",
    backref="customer",
    cascade="all, delete"
  )

class Pet(db.Model):
  __tablename__= "pet"
  id = db.Column(db.Integer,primary_key=True)
  # Add the rest of the attributes.
  name = db.Column(db.String())
  pickup_date = db.Column(db.Date())
  dropoff_date = db.Column(db.Date())
  # two foreign keys
  customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"),nullable=False)
  pet_sitter_id = db.Column(db.Integer, db.ForeignKey("pet_sitter.id"),nullable=False)

class PetSitter(db.Model):
  __tablename__= "pet_sitter"
  # Set the primary key, we need to define that each attribute is also a column in the db table, remember "db" is the object we created in the previous step.
  id = db.Column(db.Integer,primary_key=True)
  # Add the rest of the attributes. 
  first_name = db.Column(db.String())
  last_name = db.Column(db.String())
  email = db.Column(db.String())
  password = db.Column(db.String())
  pet = db.relationship(
      "Pet",
      backref="pet_sitter",
      cascade="all, delete"
  )
  message = db.relationship(
      "Message",
      backref="pet_sitter",
      cascade="all, delete"
  )

class Messages(db.Model):
  __tablename__= "message"
  # Set the primary key, we need to define that each attribute is also a column in the db table, remember "db" is the object we created in the previous step.
  id = db.Column(db.Integer,primary_key=True)
  # Add the rest of the attributes.
  date = db.Column(db.Date())
  content = db.Column(db.String())
  # two foreign keys
  customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"),nullable=False)
  pet_sitter_id = db.Column(db.Integer, db.ForeignKey("pet_sitter.id"),nullable=False)
  


