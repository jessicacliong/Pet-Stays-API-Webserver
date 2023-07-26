from main import db

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