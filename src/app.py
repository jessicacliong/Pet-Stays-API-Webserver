from flask import Flask, jsonify
from flask_marshmallow import Marshmallow 
app = Flask(__name__)
ma = Marshmallow(app)
from flask_sqlalchemy import SQLAlchemy 
from datetime import date 
from marshmallow.validate import Length 
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

# set the database URI via SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://db_dev:12345abc@localhost:5432/pet_sitting_api"
# to avoid the deprecation warning
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
#create the database object
db = SQLAlchemy(app)

# def create_app():
#   # using a list comprehension and multiple assignment 
#   # to grab the environment variables we need
  
#   # Creating the flask app object - this is the core of our app!
#   app = Flask(__name__)

#   # configuring our app:
#   app.config.from_object("config.app_config")

#   # creating our database object! This allows us to use our ORM
#   db.init_app(app)
  
#   return app

@app.cli.command("create")
def create_db():
  db.create_all()
  print("Tables created")

@app.cli.command("seed")
def seed_db():

  admin_pet_sitter = PetSitter(
    first_name="Jake",
    last_name="Daniels",
    email = "admin@petstays.com",
    password = bcrypt.generate_password_hash("password123").decode("utf-8"),
    admin = True
  )
  db.session.add(admin_pet_sitter)

  staff1 = PetSitter(
    first_name="Kathy",
    last_name="Lee",
    email = "kathylee@petstays.com",
    password = bcrypt.generate_password_hash("123456").decode("utf-8"),
  )
  db.session.add(staff1)

  # This extra commit will end the transaction and generate the ids for the user
  db.session.commit()

  customer1 = Customer(
  first_name="Mary",
  last_name="Brown",
  email="marybrown@email.com",
  password=bcrypt.generate_password_hash("123password").decode("utf-8")
  )

  db.session.add(customer1)

  customer2 = Customer(
  first_name="John",
  last_name="Smith",
  email="johnsmith@email.com",
  password=bcrypt.generate_password_hash("12345pass").decode("utf-8")
  )

  db.session.add(customer2)

  pet1 =  Pet(
    name = "Bruno",
    drop_off_date = "20-06-2023", 
    pick_up_date = "20-07-2023"
  )

  db.session.add(pet1)

  pet2 = Pet(
    name = "Diego",
    drop_off_date = "25-06-2023", 
    pick_up_date = "25-07-2023"
  )

  db.session.add(pet2)

  message1 = Message(
    date = date.today(),
    title = "Pick Up",
    content = "Hi Mary! Bruno is ready to be picked up any time today. Hope to see you soon!"
  )
  # Add the object as a new row to the table
  db.session.add(message1)

  message2 = Message(
    date = date.today(),
    title = "Drop off",
    content = "Hi Mary, you can drop off Bruno any time between 9am - 5pm on the 20th of July. See you soon!"
  )
  # Add the object as a new row to the table
  db.session.add(message2)
  # commit the changes
  db.session.commit()
  print("Table seeded")

@app.cli.command("drop")
def drop_db():
    db.drop_all()
    print("Tables dropped")

class PetSitter(db.Model):
  __tablename__= "Pet Sitter"
  # Set the primary key, we need to define that each attribute is also a column in the db table
  id = db.Column(db.Integer,primary_key=True)
  # Add the rest of the attributes. 
  first_name = db.Column(db.String())
  last_name = db.Column(db.String())
  email = db.Column(db.String())
  password = db.Column(db.String())
  admin = db.Column(db.Boolean(), default=False)

class Customer(db.Model):
  # define the table name for the db
  __tablename__= "Customer"
  # Set the primary key, we need to define that each attribute is also a column in the db table
  id = db.Column(db.Integer,primary_key=True)
  # Add the rest of the attributes. 
  first_name = db.Column(db.String())
  last_name = db.Column(db.String())
  email = db.Column(db.String())
  password = db.Column(db.String())

class Pet(db.Model):
  # define the table name for the db
  __tablename__= "Pet"
   # Set the primary key, we need to define that each attribute is also a column in the db table
  id = db.Column(db.Integer,primary_key=True)
  # Add the rest of the attributes. 
  name = db.Column(db.String())
  drop_off_date = db.Column(db.String())
  pick_up_date = db.Column(db.String())

class Message(db.Model):
  __tablename__= "Message"
  # Set the primary key, we need to define that each attribute is also a column in the db table
  id = db.Column(db.Integer,primary_key=True)
  # Add the rest of the attributes.
  date = db.Column(db.Date())
  title = db.Column(db.String())
  content = db.Column(db.String())

#create the Pet Sitter Schema with Marshmallow, it will provide the serialization needed for converting the data into JSON
class PetSitterSchema(ma.Schema):
    class Meta:
        ordered = True
        fields = ["id", "first_name", "last_name", "email", "password", "admin"]

    #set the password's length to a minimum of 6 characters
    password = ma.String(validate=Length(min=6))

#single pet sitter schema, when one card needs to be retrieved
pet_sitter_schema = PetSitterSchema()
#multiple message schema, when many cards need to be retrieved
pet_sitters_schema = PetSitterSchema(many=True)

class CustomerSchema(ma.Schema):
    class Meta:
        ordered = True
        fields = ["id", "first_name", "last_name", "email", "password"]

    #set the password's length to a minimum of 6 characters
    password = ma.String(validate=Length(min=6))

#single pet sitter schema, when one card needs to be retrieved
customer_schema = CustomerSchema()
#multiple message schema, when many cards need to be retrieved
customers_schema = CustomerSchema(many=True)

class PetSchema(ma.Schema):
    class Meta:
        ordered = True
        fields = ["id", "name", "drop_off_date", "pick_up_date"]

#single pet sitter schema, when one card needs to be retrieved
pet_schema = PetSchema()
#multiple message schema, when many cards need to be retrieved
pets_schema = PetSchema(many=True)

#create the Message Schema with Marshmallow, it will provide the serialization needed for converting the data into JSON
class MessageSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ("id", "date", "title", "content")

#single message schema, when one card needs to be retrieved
message_schema = MessageSchema()
#multiple message schema, when many cards need to be retrieved
messages_schema = MessageSchema(many=True)


@app.route("/messages", methods=["GET"])
def get_messages():
  # get all the cards from the database table
  messages_list = Message.query.all()
  # Convert the messages from the database into a JSON format and store them in result
  result = messages_schema.dump(messages_list)
  # return the data in JSON format
  return jsonify(result)