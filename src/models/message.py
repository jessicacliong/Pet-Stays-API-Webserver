from main import db

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