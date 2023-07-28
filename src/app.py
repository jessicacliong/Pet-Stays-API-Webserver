from flask import Flask, jsonify, request, abort
from flask_marshmallow import Marshmallow 
from flask_sqlalchemy import SQLAlchemy 
from marshmallow.validate import Length 
from flask_bcrypt import Bcrypt
from datetime import date, timedelta
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
import functools

app = Flask(__name__)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# set the database URI via SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://db_dev:12345abc@localhost:5432/pet_sitting_api"
# to avoid the deprecation warning
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# secret key for jwt module to use
app.config["JWT_SECRET_KEY"] = "Backend best end" 
#create the database object
db = SQLAlchemy(app)

#after becomes a main.py, uncomment these 
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

#single pet sitter schema, when one customer needs to be retrieved
customer_schema = CustomerSchema()
#multiple message schema, when many customers need to be retrieved
customers_schema = CustomerSchema(many=True)

class PetSchema(ma.Schema):
    class Meta:
        ordered = True
        fields = ["id", "name", "drop_off_date", "pick_up_date"]

#single pet sitter schema, when one pet needs to be retrieved
pet_schema = PetSchema()
#multiple message schema, when many pets need to be retrieved
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

# Messages Routes

# @app.route("/messages", methods=["GET"])
# def get_messages():
#   # get all the cards from the database table
#   messages_list = Message.query.all()
#   # Convert the messages from the database into a JSON format and store them in result
#   result = messages_schema.dump(messages_list)
#   # return the data in JSON format
#   return jsonify(result)    


#Authorisation Routes

@app.route("/auth/customer/register", methods=["POST"])
def auth_register_customer():
  #The request data will be loaded in a customer_schema converted to JSON
    customer_fields = customer_schema.load(request.json)
    # find the customer
    customer = Customer.query.filter_by(email=customer_fields["email"]).first()

    if customer:
      # return an abort message to inform the customer. That will end the request
      return abort(400, description="Email already registered")
    #Create the customer object
    customer = Customer()
    #Add first name attribute
    customer.first_name = customer_fields["first_name"]
    #Add last name attribute
    customer.last_name = customer_fields["last_name"]
    #Add the email attribute
    customer.email = customer_fields["email"]
    #Add the password attribute hashed by bcrypt
    customer.password = bcrypt.generate_password_hash(customer_fields["password"]).decode("utf-8")
    #Add it to the database and commit the changes
    db.session.add(customer)
    db.session.commit()
    #create a variable that sets an expiry date
    expiry = timedelta(days=1)
    #create the access token
    access_token = create_access_token(identity=str(customer.id), expires_delta=expiry)
    #Return the user to check the request was successful
    return jsonify(customer_schema.dump(customer))

@app.route("/auth/customer/login", methods=["POST"])
def auth_login():
  #get the user data from the request
  customer_fields = customer_schema.load(request.json)
  #find the user in the database by email
  customer = Customer.query.filter_by(email=customer_fields["email"]).first()
  # there is not a user with that email or if the password is no correct send an error
  if not customer or not bcrypt.check_password_hash(customer.password, customer_fields["password"]):
      return abort(401, description="Incorrect username and password")
  
  #create a variable that sets an expiry date
  expiry = timedelta(days=1)
  #create the access token
  access_token = create_access_token(identity=str(customer.id), expires_delta=expiry)
  # return the user email and the access token
  return jsonify({"customer":customer.email, "token": access_token })


#Customer routes

@app.route("/customer/<int:id>", methods=["GET"])
@jwt_required
def get_customer_details():
  # get all the cards from the database table
  customer_list = Customer.query.all()
  # Convert the messages from the database into a JSON format and store them in result
  result = messages_schema.dump(messages_list)
  # return the data in JSON format
  return jsonify(result)  

@app.route("/customer/<int:id>", methods=["PUT", "PATCH"])
@jwt_required()
def update_customer(id):
  customer_fields = customer_schema.load(request.json)
  #get the customer id invoking get_jwt_identity
  customer_id = get_jwt_identity()
  #Find it in the db
  customer = Customer.query.get(customer_id)
  if customer:
    if id != get_jwt_identity():
      return {'error': 'Only corresponding customers can edit their details'}, 403
      customer.first_name = customer_fields['first_name']
      customer.last_name = customer_fields["last_name"]
      customer.email = customer_fields["email"]
      customer.password = bcrypt.generate_password_hash(customer_fields["password"]).decode("utf-8")
      # (how to crypt the password?)
      db.session.commit()
      return jsonify(customer_schema.dump(customer))


# Pet Sitter Routes

@app.route("/auth/staff/register", methods=["POST"])
def auth_register():
  #The request data will be loaded in a pet_sitter_schema converted to JSON
    pet_sitter_fields = pet_sitter_schema.load(request.json)
    # find the staff details
    pet_sitter = PetSitter.query.filter_by(email=pet_sitter_fields["email"]).first()

    if pet_sitter:
      # return an abort message to inform the customer. That will end the request
      return abort(400, description="Email already registered")
    #Create the user object
    pet_sitter = PetSitter()
    #Add first name attribute
    pet_sitter.first_name = pet_sitter_fields["first_name"]
    #Add last name attribute
    pet_sitter.last_name = pet_sitter_fields["last_name"]
    #Add the email attribute
    pet_sitter.email = pet_sitter_fields["email"]
    #Add the password attribute hashed by bcrypt
    pet_sitter.password = bcrypt.generate_password_hash(pet_sitter_fields["password"]).decode("utf-8")
    #Add it to the database and commit the changes
    db.session.add(pet_sitter)
    db.session.commit()
    #Return the user to check the request was successful
    return jsonify(customer_schema.dump(pet_sitter))


# Admin Routes

# @cards_bp.route('/customer/<int:id>', methods=['DELETE'])
# @jwt_required()
# def delete_customer(id):
#     is_admin = authorise_as_admin 
#     if not is_admin:
#         return {'error': 'Not authorised to delete cards'}, 403
#     stmt = db.select(Customer).filter_by(id=id)
#     card = db.session.scalar(stmt)
#     if customer:
#         db.session.delete(customer)
#         db.session.commit()
#         return {'message': f'Card {card.title} deleted successfully'}
#     else:
#         return {'error': f'Card not found with id {id}'}, 404


#add the id to let the server know the card we want to delete
@app.route("/customer/<int:id>", methods=["DELETE"])
@jwt_required()
#Includes the id parameter
def customer_delete(id):
    #get the user id invoking get_jwt_identity
    customer_id = get_jwt_identity()
    #Find it in the db
    customer = Customer.query.get(customer_id)
    #Make sure it is in the database
    if not customer:
        return abort(401, description="Invalid user")
    # Stop the request if the user is not an admin
    if not admin_pet_sitter:
        return abort(401, description="Unauthorised user")
    # find the card
    card = Card.query.filter_by(id=id).first()
    #return an error if the card doesn't exist
    if not Card:
        return abort(400, description= "Card doesn't exist")
    #Delete the card from the database and commit
    db.session.delete(card)
    db.session.commit()
    #return the card in the response
    return jsonify(card_schema.dump(card))


# @app.route("/customer/<int:id>", methods=["GET"])
# @jwt_required()
# def get_customer_details(id):
#   stmt = db.select(Customer).filter_by(id=id)
#   customer = db.session.scalar(stmt)
#   if customer:
#       return customer_schema.dump(customer)
#   else:
#       return {'error': f'Customer not found with id {id}'}, 404

# @app.route("/customer/", methods=["POST"])
# #Decorator to make sure the jwt is included in the request
# @jwt_required()
# def customer_details():
#   #create new customer details
#   customer_fields = customer_schema.load(request.json)
#   new_customer = Customer()
#   new_customer.first_name = customer_fields["first_name"]
#   new_customer.last_name = customer_fields["last_name"]
#   new_customer.email = customer_fields["email"]
#   new_customer.password = customer_fields["password"]
#   # add to the database and commit
#   db.session.add(new_customer)
#   db.session.commit()
#   #return the card in the response
#   return jsonify(customer_schema.dump(new_customer))

# def authorise_customer(fn):
#     @functools.wraps(fn)
#     def wrapper(*args, **kwargs):
#         customer_id = get_jwt_identity()
#         stmt = db.select(Customer).filter_by(id=customer_id)
#         user = db.session.scalar(stmt)
#         if customer_id:
#             return fn(*args, **kwargs)
#         else:
#             return {'error': 'Not authorised to perform edit'}, 403
#     return wrapper