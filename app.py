import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from blueprints.routes import routesBlueprint
from modelos import Usuario

app = Flask(__name__)

print("DATABASE_URL:", os.getenv("DATABASE_URL"))
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/postgres")
print("DATABASE_URL DECLARED:", DATABASE_URL)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "frase-secreta"
app.config["PROPAGATE_EXCEPTIONS"] = True

db = SQLAlchemy(app)

app.register_blueprint(routesBlueprint)

@app.route("/ping")
def ping():
  return "pong"

def createDefaultUser():
  with app.app_context():
    if not Usuario.query.first():
      default_user = Usuario(
        usuario="admin",
        nombre="Administrador",
        contrasena="recetario2024*",
        rol="admin"
      )
      db.session.add(default_user)
      db.session.commit()
      print("USUARIO CREADO")

if __name__ == "__main__":
  db.drop_all()
  db.create_all()
  createDefaultUser()
  app.run(host="0.0.0.0")
  cors = CORS(app)
  jwt = JWTManager(app)
