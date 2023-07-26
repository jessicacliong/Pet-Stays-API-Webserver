from main import db
from models.customer import Customer
from models.message import Message
from models.pet import Pet
from models.pet_sitter import PetSitter

@app.route('/')
def hello_world():
    return 'Hello, World!'

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