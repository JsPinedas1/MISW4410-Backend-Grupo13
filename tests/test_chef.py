import json
import hashlib
from unittest import TestCase

from faker import Faker
from modelos import db, Usuario, UsuarioRestaurante, Restaurante, RedSocial, Horario, AplicacionMovil

from app import app


class TestChef(TestCase):

    def setUp(self):
        self.data_factory = Faker()
        self.client = app.test_client()
        
        nombre_usuario = 'test_chef_' + self.data_factory.name()
        contrasena = 'T1$' + self.data_factory.word()
        contrasena_encriptada = hashlib.md5(contrasena.encode('utf-8')).hexdigest()
        
        # Se crea el usuario para identificarse en la aplicación
        nuevo_chef_1 = Usuario(id=1, nombre=nombre_usuario, usuario=nombre_usuario, contrasena=contrasena_encriptada, rol="Administrador")
        nuevo_chef_2 = Usuario(id=2, nombre=nombre_usuario, usuario=nombre_usuario, contrasena=contrasena_encriptada, rol="Chef")
        nuevo_chef_3 = Usuario(id=3, nombre=nombre_usuario, usuario=nombre_usuario, contrasena=contrasena_encriptada, rol="Chef")
        db.session.add(nuevo_chef_1)
        db.session.add(nuevo_chef_2)
        db.session.add(nuevo_chef_3)

        restaurante_1 = Restaurante(id=1, nombre="Restaurante 1", direccion="Calle 35 #20-10", telefono="3214545645", domicilio=1, tipo_comida="Colombiana", consumo=1)
        restaurante_2 = Restaurante(id=2, nombre="Restaurante 2", direccion="Calle 43 #21-58", telefono="3213456897", domicilio=1, tipo_comida="Colombiana", consumo=1)
        db.session.add(restaurante_1)
        db.session.add(restaurante_2)

        red_social_1 = RedSocial(id=1, nombre="Facebook", restaurante=1)
        red_social_2 = RedSocial(id=2, nombre="Facebook", restaurante=2)
        db.session.add(red_social_1)
        db.session.add(red_social_2)
        
        horario_1 = Horario(id=1, dia_apertura="Lunes", hora_inicio="8:00", hora_fin="18:00", restaurante=1)
        horario_2 = Horario(id=2, dia_apertura="Lunes", hora_inicio="8:00", hora_fin="18:00", restaurante=2)
        db.session.add(horario_1)
        db.session.add(horario_2)

        aplicacion_movil_1 = AplicacionMovil(id=1, nombre="Rappi", restaurante=1)
        aplicacion_movil_2 = AplicacionMovil(id=2, nombre="Rappi", restaurante=2)
        db.session.add(aplicacion_movil_1)
        db.session.add(aplicacion_movil_2)

        asociacion_usuario_restaurante_1 = UsuarioRestaurante(id=1, usuario=1, restaurante=1)
        asociacion_usuario_restaurante_2 = UsuarioRestaurante(id=2, usuario=2, restaurante=2)
        asociacion_usuario_restaurante_3 = UsuarioRestaurante(id=3, usuario=3, restaurante=2)
        db.session.add(asociacion_usuario_restaurante_1)
        db.session.add(asociacion_usuario_restaurante_2)
        db.session.add(asociacion_usuario_restaurante_3)

        db.session.commit()
        
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
        
        self.restaurantes_creados = []
        self.usuarios_restaurantes_creados = []
    
    def test_get_chefs(self):
        endpoint_chefs = f"/chefs?restaurantes_ids=1,2"
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}

        resultado_chefs = self.client.get(
            endpoint_chefs,
            headers=headers
        )
        datos_respuesta = json.loads(resultado_chefs.get_data())
        usuario_ids = [dato_respuesta["id"] for dato_respuesta in datos_respuesta]
        usuario_nombres = [dato_respuesta["nombre"] for dato_respuesta in datos_respuesta]

        usuarios = Usuario.query.filter(Usuario.id.in_(usuario_ids)).all()
        self.assertEqual(resultado_chefs.status_code, 200)
        for usuario in usuarios:
            if usuario.rol == "Chef":
                self.assertIn(usuario.nombre, usuario_nombres)

    def test_transferir_chef(self):
        transferencia_chef = {
            "id_restaurante": 1
        }
        endpoint_transferir_chef = f"/transferir/2"
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}

        resultado_transferencia_chef = self.client.post(
            endpoint_transferir_chef,
            data=json.dumps(transferencia_chef),
            headers=headers
        )
        datos_respuesta = json.loads(resultado_transferencia_chef.get_data())
        print(datos_respuesta)
        usuario_restaurante = UsuarioRestaurante.query.filter_by(usuario = datos_respuesta['usuario_id']).first()
        print(usuario_restaurante)               
        self.assertEqual(resultado_transferencia_chef.status_code, 200)
        self.assertEqual(datos_respuesta['usuario_id'], usuario_restaurante.usuario)
        self.assertEqual(datos_respuesta['restaurante_id'], usuario_restaurante.restaurante)

    def tearDown(self):
        usuario_restaurante_1 = UsuarioRestaurante.query.get(1)
        usuario_restaurante_2 = UsuarioRestaurante.query.get(2)
        usuario_restaurante_3 = UsuarioRestaurante.query.get(3)
        db.session.delete(usuario_restaurante_1)
        try:
            db.session.delete(usuario_restaurante_2)
        except Exception:
            usuario_restaurante_4 = UsuarioRestaurante.query.get(4)
            db.session.delete(usuario_restaurante_4)
        db.session.delete(usuario_restaurante_3)

        usuario_1 = Usuario.query.get(1)
        usuario_2 = Usuario.query.get(2)
        usuario_3 = Usuario.query.get(3)
        db.session.delete(usuario_1)
        db.session.delete(usuario_2)
        db.session.delete(usuario_3)

        restaurante_1 = Restaurante.query.get(1)
        restaurante_2 = Restaurante.query.get(2)
        db.session.delete(restaurante_1)
        db.session.delete(restaurante_2)

        red_social_1 = RedSocial.query.get(1)
        red_social_2 = RedSocial.query.get(2)
        db.session.delete(red_social_1)
        db.session.delete(red_social_2)

        horario_1 = Horario.query.get(1)
        horario_2 = Horario.query.get(2)
        db.session.delete(horario_1)
        db.session.delete(horario_2)

        aplicacion_movil_1 = AplicacionMovil.query.get(1)
        aplicacion_movil_2 = AplicacionMovil.query.get(2)
        db.session.delete(aplicacion_movil_1)
        db.session.delete(aplicacion_movil_2)
        db.session.commit()