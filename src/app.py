from flask import Flask, jsonify, request, abort
from flask_marshmallow import Marshmallow
from marshmallow import fields
from flask_sqlalchemy import SQLAlchemy
from marshmallow.validate import Length, And, Regexp, OneOf
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

  pet_sitter1 = PetSitter(
    first_name="Jake",
    last_name="Daniels",
    email = "admin@petstays.com",
    password = bcrypt.generate_password_hash("password123").decode("utf-8"),
    admin = True
  )
  db.session.add(pet_sitter1)

  pet_sitter2 = PetSitter(
    first_name="Kathy",
    last_name="Lee",
    email = "kathylee@petstays.com",
    password = bcrypt.generate_password_hash("123456").decode("utf-8"),
    staff = True,

   )
  db.session.add(pet_sitter2)

  pet_sitter3 = PetSitter(
    first_name="Jared",
    last_name="Mcdonald",
    email="jaredmcdonald@petstays.com",
    password = bcrypt.generate_password_hash("5678910").decode("utf-8"),
    staff = True
  )
  db.session.add(pet_sitter3)

  # This extra commit will end the transaction and generate the ids for the staff and admin
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

  pet1 = Pet(
    name = "Bruno",
    drop_off_date = "14.06.2023",
    pick_up_date = "20.06.2023",
    customer = customer1,
    pet_sitter = pet_sitter1
  )

  db.session.add(pet1)

  pet2 = Pet(
    name = "Diego",
    drop_off_date = "15.06.2023",
    pick_up_date = "25.06.2023",
    customer = customer2,
    pet_sitter = pet_sitter2
  )

  db.session.add(pet2)

  # Further Iteration
  # pet_description_1 = PetDescription(
  #   name = "Bruno",
  #   animal_type = "Dog",
  #   breed = "Chihuahua",
  #   pet = pet1
  # )

  # db.session.add(pet_description_1)

  # pet_description_2 = PetDescription(
  #    name = "Diego",
  #   animal_type = "Hamster",
  #   breed = "Dwarf",
  #   pet = pet2
  # )

  # db.session.add(pet_description_2)

  message1 = Message(
    date = date.today(),
    title ="Drop off",
    content ="Hi Mary, you can drop off Bruno any time between 9am - 5pm on the 14th of June. See you soon!",
    customer = customer1,
    pet_sitter = pet_sitter1
  )
  # Add the object as a new row to the table
  db.session.add(message1)

  message2 = Message(
    date = date.today(),
    title ="Pick Up",
    content ="Hi Mary! Bruno is ready to be picked up any time today between 9am - 5pm on the 20th of June. Hope to see you soon!",
    customer = customer1,
    pet_sitter = pet_sitter1
  )

  db.session.add(message2)

  message3 = Message(
    date = date.today(),
    title ="Drop off",
    content ="Hi John, you can drop off Diego any time between 9am - 5pm on the 15th of June. See you soon!",
    customer = customer2,
    pet_sitter = pet_sitter2
  )

  db.session.add(message3)

  message4 = Message(
  date = date.today(),
  title ="Pick Up",
  content = "Hi John, you can pick up Diego any time between 9am - 5pm on the 25th of June. See you soon!",
  customer = customer2,
  pet_sitter = pet_sitter2
  )

  # Add the object as a new row to the table
  db.session.add(message4)
  # commit the changes
  db.session.commit()
  print("Table seeded")

@app.cli.command("drop")
def drop_db():
    db.drop_all()
    print("Tables dropped")


class Pet(db.Model):
  # define the table name for the db
  __tablename__= "pet"
  # Set the primary key, we need to define that each attribute is also a column in the db table
  id = db.Column(db.Integer,primary_key=True)
  # Add the rest of the attributes.
  name = db.Column(db.String(), nullable=False)
  drop_off_date = db.Column(db.String(), nullable=False)
  pick_up_date = db.Column(db.String(), nullable=False)
   # two foreign keys
  customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"),nullable=False)
  pet_sitter_id = db.Column(db.Integer, db.ForeignKey("pet_sitter.id"),nullable=False)

class PetSchema(ma.Schema):
    class Meta:
        ordered = True
        fields = ("id", "name", "drop_off_date", "pick_up_date", "customer_id", "pet_sitter_id")
    name = fields.String(required=True, validate=And(
    Length(min=2, error='Title must be at least 2 characters long'),
    Regexp('^[a-zA-Z0-9 ]+$', error='Only letters, spaces and numbers are allowed')
    ))
    #set the password's length to a minimum of 6 characters
    password = ma.String(validate=Length(min=6))
#single pet schema, when one pet needs to be retrieved
pet_schema = PetSchema()
#multiple pet schema, when many pets need to be retrieved
pets_schema = PetSchema(many=True)

# class PetDescription(db.Model):
#   # define the table name for the db
#   __tablename__= "pet_description"
#   # Set the primary key, we need to define that each attribute is also a column in the db table
#   id = db.Column(db.Integer,primary_key=True)
#   # Add the rest of the attributes.
#   name = db.Column(db.String())
#   animal_type = db.Column(db.String())
#   breed = db.Column(db.String())
#    # foreign keys
#   # pet = db.Column(db.Integer, db.ForeignKey("pet.id"),nullable=False)
#   pet_id = db.relationship(
#     "Pet",
#     backref="PetDescription",
#     cascade="all, delete"
#   )

# class PetDescriptionSchema(ma.Schema):
#     class Meta:
#         ordered = True
#         fields = ("id", "name", "animal_type", "breed", )

# #single pet sitter schema, when one pet needs to be retrieved
# pet_description_schema = PetDescriptionSchema()
# #multiple message schema, when many pets need to be retrieved
# pet_descriptions_schema = PetDescriptionSchema(many=True)

class Message(db.Model):
  __tablename__= "message"
  # Set the primary key, we need to define that each attribute is also a column in the db table
  id = db.Column(db.Integer,primary_key=True)
  # Add the rest of the attributes.
  date = db.Column(db.Date(), nullable=False)
  title = db.Column(db.String(), nullable=False)
  content = db.Column(db.String(), nullable=False)
  # # two foreign keys
  customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"),nullable=False)
  pet_sitter_id = db.Column(db.Integer, db.ForeignKey("pet_sitter.id"),nullable=False)

#create the Message Schema with Marshmallow, it will provide the serialization needed for converting the data into JSON
class MessageSchema(ma.Schema):
    class Meta:
        ordered = True
        # Fields to expose
        fields = ("id", "date", "title", "content", "customer", "pet_sitter")
    
    customer = fields.Nested("CustomerSchema", only=("first_name",))
    pet_sitter = fields.Nested("PetSitterSchema", only=("first_name",))

#single message schema, when one card needs to be retrieved
message_schema = MessageSchema()
#multiple message schema, when many cards need to be retrieved
messages_schema = MessageSchema(many=True)


class PetSitter(db.Model):
  __tablename__= "pet_sitter"
  # Set the primary key, we need to define that each attribute is also a column in the db table
  id = db.Column(db.Integer,primary_key=True)
  # Add the rest of the attributes.
  first_name = db.Column(db.String(), nullable=False)
  last_name = db.Column(db.String(), nullable=False)
  email = db.Column(db.String(), nullable=False, unique=True)
  password = db.Column(db.String(), nullable=False)
  staff = db.Column(db.Boolean(), nullable=False, default=True)
  admin = db.Column(db.Boolean(), default=False)
  pet_id = db.relationship(
      "Pet",
      backref="pet_sitter",
      cascade="all, delete"
  )
  message_id = db.relationship(
      "Message",
      backref="pet_sitter",
      cascade="all, delete"
  )

#create the Pet Sitter Schema with Marshmallow, it will provide the serialization needed for converting the data into JSON
class PetSitterSchema(ma.Schema):
    class Meta:
        ordered = True
        fields = ("id", "first_name", "last_name", "email", "password", "staff", "admin", "customer", "pet")
        load_only = ("password")
    first_name = fields.String(required=True, validate=And(
    Length(min=2, error='Title must be at least 2 characters long'),
    Regexp('^[a-zA-Z0-9 ]+$', error='Only letters, spaces and numbers are allowed')
    ))
    last_name = fields.String(required=True, validate=And(
    Length(min=2, error='Title must be at least 2 characters long'),
    Regexp('^[a-zA-Z0-9 ]+$', error='Only letters, spaces and numbers are allowed')
    ))
#single pet sitter schema, when one card needs to be retrieved
pet_sitter_schema = PetSitterSchema()
#multiple pet sitter schema, when many cards need to be retrieved
pet_sitters_schema = PetSitterSchema(many=True)


class Customer(db.Model):
  # define the table name for the db
  __tablename__= "customer"
  # Set the primary key, we need to define that each attribute is also a column in the db table
  id = db.Column(db.Integer,primary_key=True)
  # Add the rest of the attributes.
  first_name = db.Column(db.String(), nullable=False)
  last_name = db.Column(db.String(), nullable=False)
  email = db.Column(db.String(), nullable=False, unique=True)
  password = db.Column(db.String(), nullable=False)
  pet_id = db.relationship(
    "Pet",
    backref="customer",
    cascade="all, delete"
  )
  message_id = db.relationship(
    "Message",
    backref="customer",
    cascade="all, delete"
  )

class CustomerSchema(ma.Schema):
    class Meta:
        ordered = True
        fields = ("id", "first_name", "last_name", "email", "password", "pet", "message")
        load_only = ("password", )
    name = fields.String(required=True, validate=And(
    Length(min=2, error='Title must be at least 2 characters long'),
    Regexp('^[a-zA-Z0-9 ]+$', error='Only letters, spaces and numbers are allowed')
    ))
    #set the password's length to a minimum of 6 characters
    password = ma.String(validate=Length(min=6))

#single pet sitter schema, when one customer needs to be retrieved
customer_schema = CustomerSchema()
#multiple message schema, when many customers need to be retrieved
customers_schema = CustomerSchema(many=True)

# Staff Routes

@app.route("/auth/staff/register", methods=["POST"])
def auth_register_staff():
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
    #set the staff attribute to true
    pet_sitter.staff = True
    #set the admin attribute to false
    pet_sitter.admin = False
    #Add it to the database and commit the changes
    db.session.add(pet_sitter)
    db.session.commit()
    #Return the user to check the request was successful
    return jsonify(customer_schema.dump(pet_sitter))

# (Working)
@app.route("/auth/staff/login", methods=["POST"])
def auth_login_staff():
  #get the user data from the request
  pet_sitter_fields = pet_sitter_schema.load(request.json)
  #find the user in the database by email
  pet_sitter = PetSitter.query.filter_by(email=pet_sitter_fields["email"]).first()
  # there is not a user with that email or if the password is no correct send an error
  if not pet_sitter or not bcrypt.check_password_hash(pet_sitter.password, pet_sitter_fields["password"]):
    return abort(401, description="Incorrect username and password")
  #create a variable that sets an expiry date
  expiry = timedelta(days=1)
  #create the access token
  access_token = create_access_token(identity=str(pet_sitter.id), expires_delta=expiry)
  # return the user email and the access token
  return jsonify({"user":pet_sitter.email, "token": access_token })


#Customer routes

@app.route("/auth/customer/register", methods=["POST"])
def auth_register_customer():
  #The request data will be loaded in a customer_schema converted to JSON
    customer_fields = customer_schema.load(request.json)
    # find the customer
    customer = Customer.query.filter_by(email=customer_fields["email"]).first()

    if customer:
      # return an abort message to inform the customer. That will end the request
      return abort(400, description="Email already registered")
    #Create the user object
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

def authorise_as_admin(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
      pet_sitter_id = get_jwt_identity()
      stmt = db.select(PetSitter).filter_by(id=pet_sitter_id)
      pet_sitter = db.session.scalar(stmt)
      if pet_sitter.admin is True:
        return fn(*args, **kwargs)
      else:
          return {'error': 'Only admins are authorised to perform this action'}, 403
    return wrapper

#further iteration
# def authorise_staff(fn):
#   @functools.wraps(fn)
#   def wrapper(*args, **kwargs):
#     pet_sitter_id = get_jwt_identity()
#     stmt_2 = db.select(PetSitter).filter_by(id=pet_sitter_id)
#     pet_sitter_2 = db.session.scalar(stmt_2)
#     if pet_sitter_2:
#       return fn(*args, **kwargs)
#     else:
#         return {'error': 'Only staff are authorised to perform this action'}, 403
#   return wrapper


# Messages Routes

@app.route("/customer/messages", methods=["GET"])
@jwt_required()
def get_all_customer_messages():
  # get all the messages from the database table
  messages_list = Message.query.all()
  # Convert the messages from the database into a JSON format and store them in result
  result = messages_schema.dump(messages_list)
  # return the data in JSON format
  return jsonify(result)

@app.route("/customer/<int:customer_id>/messages", methods=["GET"])
@jwt_required()
def get_one_customers_messages(customer_id):
  customer_id = get_jwt_identity()
  stmt = db.select(Customer).filter_by(id=customer_id)
  customer = db.session.scalar(stmt)
  if str(customer.id) == get_jwt_identity(): # the user who sent the request / they are trying to edit
    # get all the messages from the database table
    messages = Message.query.filter_by(customer_id=customer_id)
    # return the data in JSON format
    result = messages_schema.dump(messages)
    return jsonify(result)
  else:
    return {'error': f'Messages not found for customer id {customer_id}'}, 404


@app.route('/customer/<int:customer_id>/message', methods=['POST'])
@jwt_required()
def create_message_to_customer(customer_id):
  #get the user id invoking get_jwt_identity
  pet_sitter_id = get_jwt_identity()
  #Find it in the db
  pet_sitter_stmt = db.Select(PetSitter).filter_by(id=pet_sitter_id)
  pet_sitter = db.session.scalar(pet_sitter_stmt)
  #Make sure it is in the database
  if pet_sitter:
    stmt = db.Select(Customer).filter_by(id=customer_id)
    customer = db.session.scalar(stmt)
    if customer:
      #create the message with the given values
      body_data = message_schema.load(request.json)
      # create a new Message model instance
      message = Message(
        date = date.today(),
        title = body_data.get('title'),
        content = body_data.get('content'),
        customer_id= customer_id,
        pet_sitter_id= get_jwt_identity(),
      )
        # Add that message to the session
      db.session.add(message)
      # Commit
      db.session.commit()
      # Respond to the client
      return message_schema.dump(message), 201
    else:
      return {'error': f'Customer with id {customer_id} not found'}, 404
  else:
    return {'error': f'Invalid staff with id {pet_sitter_id}, unable to create a message'}, 401


@app.route('/customer/<int:customer_id>/message/<int:message_id>', methods=['DELETE'])
@jwt_required()
@authorise_as_admin
def delete_customer_message(customer_id, message_id):
    admin = authorise_as_admin
    if admin:        
      customer_stmt = db.select(Customer).filter_by(id=customer_id)
      customer = db.session.scalar(customer_stmt)
      if customer:
        stmt = db.select(Message).filter_by(id=message_id)
        message = db.session.scalar(stmt)
        if message:
            db.session.delete(message)
            db.session.commit()
            return {'message': f'Message with id number {message_id} deleted successfully'}
        else: 
            return {'error': f'Message not found with id {message_id}'}, 404
      else:
          return {'error': f'Customer not found with id {customer_id}'}, 404
    else:
      return {'error': 'Not authorised to delete messages'}, 403



@app.route("/customer", methods=["GET"])
@jwt_required()
def get_all_customers():
  # get all the customer details from the database table
  customers_list = Customer.query.all()
  # Convert the customers from the database into a JSON format and store them in result
  result = customers_schema.dump(customers_list)
  # return the data in JSON format
  return jsonify(result)


@app.route('/customer/<int:customer_id>', methods=['GET'])
@jwt_required()
def get_one_customer_detail(customer_id):
  customer_jwt = get_jwt_identity()
  customer_stmt = db.select(Customer).filter_by(id=customer_id)
  customer = db.session.scalar(customer_stmt)
  if customer:
    if str(customer.id) == get_jwt_identity():
        return customer_schema.dump(customer)
    else:
      return {'error': f'Not authorised to see customer {customer_id}\'s information'}, 403
  else: 
    return {'error': f'Customer with id {customer_id} cannot be found'}, 404

#For further iteration to allow only staff and customers to access customer information
# #(Working, authorisation not done properly)
# @app.route('/customer/<int:customer_id>', methods=['GET'])
# @jwt_required()
# # @authorise_staff
# def get_one_customer_detail(customer_id):
#   # is_staff = authorise_staff
#   # if not is_staff:
#   #   return {'error': 'Not authorised to delete cards'}, 403
#   # pet_sitter_id = get_jwt_identity()
#   # pet_sitter_stmt = db.select(PetSitter).filter_by(id=pet_sitter_id)
#   # pet_sitter = db.session.scalar(pet_sitter_stmt)
#   # if customer:
#     # if str(customer.id) == get_jwt_identity() or str(pet_sitter.id) == get_jwt_identity():
#   customer_jwt = get_jwt_identity()
#   customer_stmt = db.select(Customer).filter_by(id=customer_id)
#   customer = db.session.scalar(customer_stmt)
#   if customer:
#     # if str(customer.id) == get_jwt_identity() or str(pet_sitter.id) == get_jwt_identity():
#     if str(customer.id) == get_jwt_identity():
#         return customer_schema.dump(customer)
#     else:
#       return {'error': 'Not authorised to see information'}, 403
#   else: 
#     return {'error': f'Customer with id {customer_id} not found or staff with id not found'}, 404


@app.route("/customer/<int:customer_id>", methods=["PUT", "PATCH"])
@jwt_required()
def update_customer(customer_id):
  customer_jwt = get_jwt_identity()
  #Find it in the db
  customer_stmt = db.select(Customer).filter_by(id=customer_id)
  customer = db.session.scalar(customer_stmt)
  if customer:
    if str(customer.id) == get_jwt_identity():
      #update the customer details with the given values
      customer.first_name = customer_fields['first_name']
      customer.last_name = customer_fields["last_name"]
      customer.email = customer_fields["email"]
      customer.password = bcrypt.generate_password_hash(customer_fields["password"]).decode("utf-8")
      db.session.commit()
      return jsonify(customer_schema.dump(customer))
    else:
      return { 'error': f'Not authorised to update customer id {customer_id}\'s information.'}
  else:
    return { 'error': f'Customer with id {customer_id} cannot be found.'}


@app.route('/customer/<int:customer_id>', methods=['DELETE'])
@jwt_required()
@authorise_as_admin
def delete_one_customer(customer_id):
    admin = authorise_as_admin
    stmt = db.select(Customer).filter_by(id=customer_id)
    customer = db.session.scalar(stmt)
    if customer:
        db.session.delete(customer)
        db.session.commit()
        return {'message': f'Customer {customer.first_name} {customer.last_name} deleted successfully'}
    else:
        return {'error': f'Customer not found with id {customer_id}'}, 404


@app.route("/pets", methods=["GET"])
@jwt_required()
@authorise_as_admin
def get_all_pets_detail():
  admin = authorise_as_admin
# get all the messages from the database table
  pets_list = Pet.query.all()
  # Convert the messages from the database into a JSON format and store them in result
  result = pets_schema.dump(pets_list)
  # return the data in JSON format
  return jsonify(result)


@app.route("/customer/<int:customer_id>/pets", methods=["GET"])
@jwt_required()
def get_pet_detail(customer_id):
  customer_jwt = get_jwt_identity()
  customer_stmt = db.select(Customer).filter_by(id=customer_id)
  customer = db.session.scalar(customer_stmt)
  if customer:
    if str(customer.id) == get_jwt_identity():
      stmt = db.select(Pet).filter_by(customer_id=customer_id)
      pets = db.session.scalars(stmt)
      if pets:
        return pets_schema.dump(pets)
      else:
        return {'error': f'Customer does not have pets registered'}, 404
    else:
      return {'error': 'Not authorised to see information'}, 403
  else: 
    return {'error': f'Customer with id {customer_id} not found'}, 404


@app.route("/customer/<int:customer_id>/pet", methods=["POST"])
#Decorator to make sure the jwt is included in the request
@jwt_required()
def pet_details(customer_id):
  #create new pet details
  body_data = pet_schema.load(request.json)
  pet = Pet(
    name = body_data.get('name'),
    drop_off_date = body_data.get('drop_off_date'),
    pick_up_date = body_data.get('pick_up_date'),
    customer_id = body_data.get('customer_id'),
    pet_sitter_id = body_data.get('pet_sitter_id'),
  )
  # add to the database and commit
  db.session.add(pet)
  #commit
  db.session.commit()
  #return the card in the response
  return pet_schema.dump(pet), 201

@app.route('/customer/<int:customer_id>/pet/<int:pet_id>', methods=['DELETE'])
@jwt_required()
@authorise_as_admin
def delete_one_pet(customer_id, pet_id):
    is_admin = authorise_as_admin
    if not is_admin:
        return {'error': 'Not authorised to delete pet information'}, 403
    customer_stmt = db.select(Customer).filter_by(id=customer_id)
    customer = db.session.scalar(customer_stmt)
    if customer:
      pet_stmt = db.select(Pet).filter_by(id=pet_id)
      pet = db.session.scalar(pet_stmt)
    else:
      return {'error': f'Customer not found with id {id}'}, 404
    if pet:
      db.session.delete(pet)
      db.session.commit()
      return {'message': f'Pet {pet.name} deleted successfully'}
    else:
      return {'error': f'Pet not found with id {id}'}, 404