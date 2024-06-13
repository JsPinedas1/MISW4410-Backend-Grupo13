from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields, Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

db = SQLAlchemy()

class RecetaIngrediente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cantidad = db.Column(db.Numeric)
    ingrediente = db.Column(db.Integer, db.ForeignKey('ingrediente.id'))
    receta = db.Column(db.Integer, db.ForeignKey('receta.id'))

class Ingrediente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(128))
    unidad = db.Column(db.String(128))
    costo = db.Column(db.Numeric)
    calorias = db.Column(db.Numeric)
    sitio = db.Column(db.String(128))
    restaurante = db.Column(db.Integer, db.ForeignKey('restaurante.id'))

class Receta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(128))
    duracion = db.Column(db.Numeric)
    preparacion = db.Column(db.String)
    ingredientes = db.relationship('RecetaIngrediente', cascade='all, delete, delete-orphan')
    usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    menu = db.Column(db.Integer, db.ForeignKey('menu.id'))
    porcion = db.Column(db.String)

class MenuReceta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_menu = db.Column(db.Integer, db.ForeignKey('menu.id'))
    porcion = db.Column(db.Integer)
    id_receta = db.Column(db.Integer, db.ForeignKey('receta.id'))

class Menu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(128))
    fechainicio = db.Column(db.String(20))
    fechafinal = db.Column(db.String(20))
    recetas = db.relationship('MenuReceta', cascade='all, delete, delete-orphan')
    usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    restaurante = db.Column(db.Integer, db.ForeignKey('restaurante.id')) 

class AplicacionMovil(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(500))
    restaurante = db.Column(db.Integer, db.ForeignKey('restaurante.id'))

class Horario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dia_apertura = db.Column(db.String(10))
    hora_inicio = db.Column(db.String(5))
    hora_fin = db.Column(db.String(5))
    restaurante = db.Column(db.Integer, db.ForeignKey('restaurante.id'))

class RedSocial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(500))
    restaurante = db.Column(db.Integer, db.ForeignKey('restaurante.id'))

class Restaurante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200))
    direccion = db.Column(db.String(200))
    telefono = db.Column(db.String(200))
    domicilio = db.Column(db.Integer)
    tipo_comida = db.Column(db.String(500))
    consumo = db.Column(db.Integer)

class RestauranteIngrediente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ingrediente = db.Column(db.Integer, db.ForeignKey('ingrediente.id'))
    restaurante = db.Column(db.Integer, db.ForeignKey('restaurante.id'))

class RestauranteReceta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    receta = db.Column(db.Integer, db.ForeignKey('receta.id'))
    restaurante = db.Column(db.Integer, db.ForeignKey('restaurante.id'))

class UsuarioRestaurante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    restaurante = db.Column(db.Integer, db.ForeignKey('restaurante.id'))

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50))
    nombre = db.Column(db.String(50))
    contrasena = db.Column(db.String(50))
    rol = db.Column(db.String(50))
    recetas = db.relationship('Receta', cascade='all, delete, delete-orphan')

class IngredienteSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Ingrediente
        load_instance = True
        
    id = fields.String()
    costo = fields.String()
    calorias = fields.String()

class RecetaIngredienteSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = RecetaIngrediente
        include_relationships = True
        include_fk = True
        load_instance = True
        
    id = fields.String()
    cantidad = fields.String()
    ingrediente = fields.String()

class RecetaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Receta
        include_relationships = True
        include_fk = True
        load_instance = True
        
    id = fields.String()
    duracion = fields.String()
    ingredientes = fields.List(fields.Nested(RecetaIngredienteSchema()))

class MenuRecetaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MenuReceta
        include_relationships = True
        include_fk = True
        load_instance = True
        
    id = fields.String()
    porcion = fields.String()
    receta = fields.String()

class MenuSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Menu
        include_relationships = True
        include_fk = True
        load_instance = True
        
    id = fields.String()
    nombre = fields.String()
    fechainicio = fields.String()
    fechafin = fields.String()
    recetas = fields.List(fields.Nested(MenuRecetaSchema()))

class AplicacionMovilSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = RedSocial
        include_relationships = True
        include_fk = True
        load_instance = True
        
    id = fields.String()
    nombre = fields.String()

class HorarioSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = RedSocial
        include_relationships = True
        include_fk = True
        load_instance = True
        
    id = fields.String()
    dia_apertura = fields.String()
    hora_inicio = fields.String()
    hora_fin = fields.String()

class RedSocialSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = RedSocial
        include_relationships = True
        include_fk = True
        load_instance = True
        
    id = fields.String()
    nombre = fields.String()

class RestauranteIngredienteSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = UsuarioRestaurante
        include_relationships = True
        include_fk = True
        load_instance = True
        
    id = fields.String()

class RestauranteSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Restaurante
        include_relationships = True
        load_instance = True
        
    id = fields.String()
    nombre = fields.String()
    direccion = fields.String()
    telefono = fields.String()
    domicilio = fields.String()
    tipo_comida = fields.String()
    consumo = fields.String()

class UsuarioRestauranteSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = UsuarioRestaurante
        include_relationships = True
        include_fk = True
        load_instance = True
        
    id = fields.String()

class UsuarioSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Usuario
        include_relationships = True
        load_instance = True
        
    id = fields.String()
