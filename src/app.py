from flask import Flask, jsonify
from flask_marshmallow import Marshmallow 
app = Flask(__name__)
ma = Marshmallow(app)
from flask_sqlalchemy import SQLAlchemy 

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
  from datetime import date
  message1 = Message(
    date = date.today(),
    title = "Pick Up",
    content = "Hi, my name is Grace and I'll be your pet sitter for Bruno while you're away on holidays. I'll come around 9am to pick him up. See you then!"
  )
  # Add the object as a new row to the table
  db.session.add(message1)

  message2 = Message(
    date = date.today(),
    title = "Drop off",
    content = "Hi Mary, what time would you like to drop Bruno off at Pet Stays?"
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

class Message(db.Model):
  __tablename__= "message"
  # Set the primary key, we need to define that each attribute is also a column in the db table, remember "db" is the object we created in the previous step.
  id = db.Column(db.Integer,primary_key=True)
  # Add the rest of the attributes.
  date = db.Column(db.Date())
  title = db.Column(db.String())
  content = db.Column(db.String())

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