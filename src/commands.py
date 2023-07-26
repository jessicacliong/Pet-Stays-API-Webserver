# from main import db
# from models.customer import Customer
# from models.message import Message
# from models.pet import Pet
# from models.pet_sitter import PetSitter

# @app.cli.command("create")
# def create_db():
#   db.create_all()
#   print("Tables created")

# @app.cli.command("seed")
# def seed_db():
#   admin_user = User(
#       email = "admin@email.com",
#       password = bcrypt.generate_password_hash("password123").decode("utf-8"),
#       admin = True
#   )
#   db.session.add(admin_user)

#   user1 = User(
#       email = "user1@email.com",
#       password = bcrypt.generate_password_hash("123456").decode("utf-8")
#   )
#   db.session.add(user1)
#   # This extra commit will end the transaction and generate the ids for the user
#   db.session.commit()

#   Mary = Customer(
#     first_name="Mary",
#     last_name="Brown",
#     email="marybrown@email.com",
#     password=bcrypt.generate_password_hash("123password").decode("utf-8")
#   )

#   John = Customer(
#      first_name="John",
#     last_name="Smith",
#     email="johnsmith@email.com",
#     password=bcrypt.generate_password_hash("12345pass").decode("utf-8")
#   )

# @app.cli.command("drop")
# def drop_db():
#     db.drop_all()
#     print("Tables dropped")