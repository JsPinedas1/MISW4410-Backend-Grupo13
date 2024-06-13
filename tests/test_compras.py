import json
import hashlib
from unittest import TestCase

from faker import Faker
from faker.generator import random
from modelos import db, Usuario, UsuarioRestaurante, Restaurante, \
                        Menu, Ingrediente, Receta, RecetaIngrediente, \
                        MenuReceta

from app import app


class TestChef(TestCase):

    def setUp(self):
        self.data_factory = Faker()
        self.client = app.test_client()
        
        nombre_usuario = 'test_chef_' + self.data_factory.name()
        contrasena = 'T1$' + self.data_factory.word()
        contrasena_encriptada = hashlib.md5(contrasena.encode('utf-8')).hexdigest()

        restaurante_1 = Restaurante(id=1, nombre="Restaurante 1", direccion="Calle 35 #20-10", telefono="3214545645", domicilio=1, tipo_comida="Colombiana", consumo=1)
        db.session.add(restaurante_1)

        nuevo_chef_1 = Usuario(id=1, nombre=nombre_usuario, usuario=nombre_usuario, contrasena=contrasena_encriptada, rol="Administrador")
        nuevo_chef_2 = Usuario(id=2, nombre=nombre_usuario, usuario=nombre_usuario, contrasena=contrasena_encriptada, rol="Chef")
        db.session.add(nuevo_chef_1)
        db.session.add(nuevo_chef_2)

        asociacion_usuario_restaurante_1 = UsuarioRestaurante(id=1, usuario=1, restaurante=1)
        asociacion_usuario_restaurante_2 = UsuarioRestaurante(id=2, usuario=2, restaurante=1)
        db.session.add(asociacion_usuario_restaurante_1)
        db.session.add(asociacion_usuario_restaurante_2)

        ingrediente_1 = Ingrediente(nombre = "Lenteja",
                              unidad=self.data_factory.sentence(),
                              calorias=round(random.uniform(0.1, 0.99), 2),
                              costo=100,
                              sitio="Sitio 1")
        
        ingrediente_2 = Ingrediente(nombre = "Frijol",
                              unidad=self.data_factory.sentence(),
                              calorias=round(random.uniform(0.1, 0.99), 2),
                              costo=200,
                              sitio="Sitio 1")
       
        ingrediente_3 = Ingrediente(nombre = "Huevo",
                              unidad=self.data_factory.sentence(),
                              calorias=round(random.uniform(0.1, 0.99), 2),
                              costo=100,
                              sitio="Sitio 2")
        db.session.add(ingrediente_1)
        db.session.add(ingrediente_2)
        db.session.add(ingrediente_3)

        receta_1 = Receta(nombre = "Receta 1",
               duracion = 2,
               preparacion = "Preparacion 1",
               usuario = 2,
               menu = 1)
        
        receta_2 = Receta(nombre = "Receta 2",
               duracion = 2,
               preparacion = "Preparacion 2",
               usuario = 2,
               menu = 1)
        
        receta_3 = Receta(nombre = "Receta 3",
               duracion = 2,
               preparacion = "Preparacion 3",
               usuario = 2,
               menu = 1)
        db.session.add(receta_1)
        db.session.add(receta_2)
        db.session.add(receta_3)

        receta_restaurante_1 = RecetaIngrediente(cantidad = 2, ingrediente = 1, receta = 1)
        receta_restaurante_2 = RecetaIngrediente(cantidad = 3, ingrediente = 1, receta = 2)
        receta_restaurante_3 = RecetaIngrediente(cantidad = 6, ingrediente = 2, receta = 2)
        receta_restaurante_4 = RecetaIngrediente(cantidad = 10, ingrediente = 3, receta = 3)
        db.session.add(receta_restaurante_1)
        db.session.add(receta_restaurante_2)
        db.session.add(receta_restaurante_3)
        db.session.add(receta_restaurante_4)
        db.session.commit()
        
        menu_1 = Menu(id=1, 
                      nombre="Menu 1",
                      fechainicio = "2023-09-23T00:00:00",
                      fechafinal = "2023-09-30T23:59:59",
                      usuario=2,
                      restaurante = 1)
        db.session.add(menu_1)

        menu_receta_1 = MenuReceta(id_menu = 1,
                            id_receta = 1,
                            porcion = 5
                        )
        menu_receta_2 = MenuReceta(id_menu = 1,
                            id_receta = 2,
                            porcion = 5
                        )
        menu_receta_3 = MenuReceta(id_menu = 1,
                            id_receta = 3,
                            porcion = 5
                        )
        db.session.add(menu_receta_1)
        db.session.add(menu_receta_2)
        db.session.add(menu_receta_3)


        usuario_login = {
            "usuario": nombre_usuario,
            "contrasena": contrasena
        }

        solicitud_login = self.client.post("/login",
                                                data=json.dumps(usuario_login),
                                                headers={'Content-Type': 'application/json'})

        respuesta_login = json.loads(solicitud_login.get_data())

        self.token = respuesta_login["token"]
        self.usuario_id = respuesta_login["id"]
    
    def test_get_compras(self):
        endpoint_chefs = f"/compras/1"
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
#
        resultado_compras = self.client.get(
            endpoint_chefs,
            headers=headers
        )
        datos_respuesta = json.loads(resultado_compras.get_data())
        print(datos_respuesta)
        self.assertEqual(datos_respuesta[0]["ingrediente"], "Frijol")
        self.assertEqual(datos_respuesta[0]["cantidad"], 6.0)
        self.assertEqual(datos_respuesta[0]["sitio"], "Sitio 1")
        self.assertEqual(datos_respuesta[0]["precio"], 1200.0)
        self.assertEqual(datos_respuesta[0]["recetas"], ["Receta 2"])

        self.assertEqual(datos_respuesta[1]["ingrediente"], "Lenteja")
        self.assertEqual(datos_respuesta[1]["cantidad"], 5)
        self.assertEqual(datos_respuesta[1]["sitio"], "Sitio 1")
        self.assertEqual(datos_respuesta[1]["precio"], 1000.0)
        self.assertEqual(datos_respuesta[1]["recetas"], ["Receta 1", "Receta 2"])

        self.assertEqual(datos_respuesta[2]["ingrediente"], "Huevo")
        self.assertEqual(datos_respuesta[2]["cantidad"], 10)
        self.assertEqual(datos_respuesta[2]["sitio"], "Sitio 2")
        self.assertEqual(datos_respuesta[2]["precio"], 1000.0)
        self.assertEqual(datos_respuesta[2]["recetas"], ["Receta 3"])

    def tearDown(self):
        receta_ingrediente_1 = RecetaIngrediente.query.get(1)
        receta_ingrediente_2 = RecetaIngrediente.query.get(2)
        receta_ingrediente_3 = RecetaIngrediente.query.get(3)
        receta_ingrediente_4 = RecetaIngrediente.query.get(4)
        db.session.delete(receta_ingrediente_1)
        db.session.delete(receta_ingrediente_2)
        db.session.delete(receta_ingrediente_3)
        db.session.delete(receta_ingrediente_4)

        ingrediente_1 = Ingrediente.query.get(1)
        ingrediente_2 = Ingrediente.query.get(2)
        ingrediente_3 = Ingrediente.query.get(3)
        db.session.delete(ingrediente_1)
        db.session.delete(ingrediente_2)
        db.session.delete(ingrediente_3)

        receta_1 = Receta.query.get(1)
        receta_2 = Receta.query.get(2)
        receta_3 = Receta.query.get(3)
        db.session.delete(receta_1)
        db.session.delete(receta_2)
        db.session.delete(receta_3)

        menu_receta_1 = MenuReceta.query.get(1)
        menu_receta_2 = MenuReceta.query.get(2)
        menu_receta_3 = MenuReceta.query.get(3)
        db.session.delete(menu_receta_1)
        db.session.delete(menu_receta_2)
        db.session.delete(menu_receta_3)

        menu_1 = Menu.query.get(1)
        db.session.delete(menu_1)

        usuario_restaurante_1 = UsuarioRestaurante.query.get(1)
        usuario_restaurante_2 = UsuarioRestaurante.query.get(2)
        db.session.delete(usuario_restaurante_1)
        db.session.delete(usuario_restaurante_2)

        restaurante_1 = Restaurante.query.get(1)
        db.session.delete(restaurante_1)

        usuario_1 = Usuario.query.get(1)
        usuario_2 = Usuario.query.get(2)
        db.session.delete(usuario_1)
        db.session.delete(usuario_2)
        db.session.commit()