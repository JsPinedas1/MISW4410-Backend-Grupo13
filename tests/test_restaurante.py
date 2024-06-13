import json
import hashlib
from unittest import TestCase

from faker import Faker
from modelos import db, Usuario, UsuarioRestaurante, Restaurante

from app import app


class TestRestaurante(TestCase):

    def setUp(self):
        self.data_factory = Faker()
        self.client = app.test_client()
        
        nombre_usuario = 'test_' + self.data_factory.name()
        contrasena = 'T1$' + self.data_factory.word()
        contrasena_encriptada = hashlib.md5(contrasena.encode('utf-8')).hexdigest()
        
        # Se crea el usuario para identificarse en la aplicación
        usuario_nuevo = Usuario(usuario=nombre_usuario, contrasena=contrasena_encriptada)
        db.session.add(usuario_nuevo)
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
        
    
    def tearDown(self):
        for restaurante_creado in self.restaurantes_creados:
            restaurante = Restaurante.query.get(restaurante_creado.id)
            db.session.delete(restaurante)
            db.session.commit()

        for usuario_restaurante_creado in self.usuarios_restaurantes_creados:
            usuario_restaurante = UsuarioRestaurante.query.get(usuario_restaurante_creado.id)
            db.session.delete(usuario_restaurante)
            db.session.commit()
            
        usuario_login = Usuario.query.get(self.usuario_id)
        db.session.delete(usuario_login)
        db.session.commit()

    def test_listar_restaurantes(self):
        #Generar 10 restaurantes con datos aleatorios
        for i in range(0,10):
            #Crear los datos del restaurante
            nombre_nuevo_restaurante = self.data_factory.sentence()
            direccion_nuevo_restaurante = self.data_factory.address()
            telefono_nuevo_restaurante = self.data_factory.phone_number()
            domicilio_nuevo_restaurante = True if self.data_factory.random_int(min=0, max=1) == 1 else False
            tipo_comida_nuevo_restaurante = self.data_factory.word(ext_word_list=['Colombiana', 'Asiatica', 'Mexicana'])
            consumo_nuevo_restaurante = False if self.data_factory.random_int(min=0, max=1) == 1 else True
            
            #Crear el restaurante con los datos originales para obtener su id
            restaurante = Restaurante(nombre = nombre_nuevo_restaurante,
                                  direccion=direccion_nuevo_restaurante,
                                  telefono=telefono_nuevo_restaurante,
                                  domicilio=domicilio_nuevo_restaurante,
                                  tipo_comida=tipo_comida_nuevo_restaurante,
                                  consumo=consumo_nuevo_restaurante)
            db.session.add(restaurante)
            db.session.commit()

            #Asociar cada restaurante al usuario
            usuario_restaurante = UsuarioRestaurante(usuario = self.usuario_id, restaurante = restaurante.id)
            db.session.add(usuario_restaurante)
            db.session.commit()
            self.usuarios_restaurantes_creados.append(usuario_restaurante)
            self.restaurantes_creados.append(restaurante)

        #Definir endpoint, encabezados y hacer el llamado
        endpoint_restaurantes = f"/restaurantes/{self.usuario_id}"
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
        
        resultado_consulta_restaurantes = self.client.get(endpoint_restaurantes,
                                                        headers=headers)
                                                   
        #Obtener los datos de respuesta y dejarlos un objeto json
        datos_respuesta = json.loads(resultado_consulta_restaurantes.get_data())
                                                   
        #Verificar que el llamado fue exitoso
        self.assertEqual(resultado_consulta_restaurantes.status_code, 200)
        
        #Verificar los restaurantes creados con sus datos
        for restaurante in datos_respuesta:
            for restaurante_creado in self.restaurantes_creados:
                if restaurante['id'] == str(restaurante_creado.id):
                    self.assertEqual(restaurante['nombre'], restaurante_creado.nombre)
                    self.assertEqual(restaurante['direccion'], restaurante_creado.direccion)
                    self.assertEqual(restaurante['telefono'], restaurante_creado.telefono)
                    self.assertEqual(restaurante['domicilio'], str(restaurante_creado.domicilio))
                    self.assertEqual(restaurante['tipo_comida'], restaurante_creado.tipo_comida)
                    self.assertEqual(restaurante['consumo'], str(restaurante_creado.consumo))
