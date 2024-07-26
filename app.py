import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from blueprints.routes import routesBlueprint

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:postgres@db:5432/postgres"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "frase-secreta"
app.config["PROPAGATE_EXCEPTIONS"] = True

db = SQLAlchemy(app)

app.register_blueprint(routesBlueprint)

@app.route("/")
def hello():
  return "Hello World!"

if __name__ == "__main__":
  db.drop_all()
  db.create_all()
  cors = CORS(app)
  jwt = JWTManager(app)
  app.run(host="0.0.0.0")
