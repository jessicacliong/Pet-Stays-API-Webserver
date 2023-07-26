# from main import db

# class PetSitter(db.Model):
#   __tablename__= "pet_sitter"
#   # Set the primary key, we need to define that each attribute is also a column in the db table, remember "db" is the object we created in the previous step.
#   id = db.Column(db.Integer,primary_key=True)
#   # Add the rest of the attributes. 
#   first_name = db.Column(db.String())
#   last_name = db.Column(db.String())
#   email = db.Column(db.String())
#   password = db.Column(db.String())
#   pet = db.relationship(
#       "Pet",
#       backref="pet_sitter",
#       cascade="all, delete"
#   )
#   message = db.relationship(
#       "Message",
#       backref="pet_sitter",
#       cascade="all, delete"
#   )