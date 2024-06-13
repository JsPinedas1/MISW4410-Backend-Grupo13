from flask import request
from flask_jwt_extended import jwt_required, create_access_token
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from flask import jsonify
from itertools import groupby
from operator import itemgetter
import hashlib

from modelos import \
    db, \
    Ingrediente, IngredienteSchema, \
    RecetaIngrediente, RecetaIngredienteSchema, \
    Receta, RecetaSchema, \
    Menu, MenuReceta, \
    Usuario, UsuarioSchema, \
    Restaurante, RestauranteSchema, \
    UsuarioRestaurante, UsuarioRestauranteSchema, \
    RedSocial, AplicacionMovil, Horario, RedSocialSchema, \
    AplicacionMovilSchema, HorarioSchema, MenuSchema, \
    RestauranteIngrediente, MenuRecetaSchema


ingrediente_schema = IngredienteSchema()
receta_ingrediente_schema = RecetaIngredienteSchema()
receta_schema = RecetaSchema()
usuario_schema = UsuarioSchema()
restaurante_schema = RestauranteSchema()
usuario_restaurante = UsuarioRestaurante()
usuario_restaurante_schema = UsuarioRestauranteSchema()
red_social = RedSocial()
red_social_schema = RedSocialSchema()
aplicacion_movil = AplicacionMovil()
aplicacion_movil_schema = AplicacionMovilSchema()
horario_bd = Horario()
horario_bd_schema = HorarioSchema()
menu_bd_schema = MenuSchema()
menu_receta_bd_schema = MenuRecetaSchema()

    
class VistaSignIn(Resource):

    def post(self):
        usuario = Usuario.query.filter(Usuario.usuario == request.json["usuario"]).first()
        if usuario is None:
            contrasena_encriptada = hashlib.md5(request.json["contrasena"].encode('utf-8')).hexdigest()
            nuevo_usuario = Usuario(usuario=request.json["usuario"], nombre=request.json["nombre"], contrasena=contrasena_encriptada, rol=request.json["rol"])
            db.session.add(nuevo_usuario)
            db.session.commit()
            token_de_acceso = create_access_token(identity=nuevo_usuario.id)
            return {"mensaje": "usuario creado exitosamente", "id": nuevo_usuario.id}
        else:
            return "El usuario ya existe", 404

    def put(self, id_usuario):
        usuario = Usuario.query.get_or_404(id_usuario)
        usuario.contrasena = request.json.get("contrasena", usuario.contrasena)
        db.session.commit()
        return usuario_schema.dump(usuario)

    def delete(self, id_usuario):
        usuario = Usuario.query.get_or_404(id_usuario)
        db.session.delete(usuario)
        db.session.commit()
        return '', 204


class VistaLogIn(Resource):

    def post(self):
        contrasena_encriptada = hashlib.md5(request.json["contrasena"].encode('utf-8')).hexdigest()
        usuario = Usuario.query.filter(Usuario.usuario == request.json["usuario"],
                                       Usuario.contrasena == contrasena_encriptada).first()
        db.session.commit()
        print(str(hashlib.md5("admin".encode('utf-8')).hexdigest()))
        if usuario is None:
            return "El usuario no existe", 404
        else:
            token_de_acceso = create_access_token(identity=usuario.id)
            print("TOKEN DE ACCESO {}".format(token_de_acceso))
            return {"mensaje": "Inicio de sesión exitoso", "token": token_de_acceso, "id": usuario.id, "rol": usuario.rol}

class VistaIngredientePorRestaurante(Resource):
    @jwt_required()
    def get(self, id_restaurante):
        ingredientes = db.session.query(Ingrediente).\
        join(RestauranteIngrediente, RestauranteIngrediente.ingrediente == Ingrediente.id).\
        filter(RestauranteIngrediente.restaurante == id_restaurante).all()

class VistaIngredientes(Resource):
    @jwt_required()
    def get(self):
        arregloIngredientes = []
        ingredientes = Ingrediente.query.all()
        for ingrediente in ingredientes:
            restaurante = Restaurante.query.filter_by(id=ingrediente.restaurante).first()  # Get the Restaurante object by its ID
            print("ESTE RESTAURANTE", restaurante)
            objetoIngrediente = {
                "id": ingrediente.id,
                "nombre": ingrediente.nombre,
                "unidad": ingrediente.unidad,
                "costo": str(ingrediente.costo),
                "calorias": str(ingrediente.calorias),
                "sitio": ingrediente.sitio,
                "restaurante": restaurante.nombre
            }
            arregloIngredientes.append(objetoIngrediente)
        return jsonify(arregloIngredientes)

    @jwt_required()
    def post(self):
        try:
            nombre = request.json["nombre"]
            unidad = request.json["unidad"]
            costo = float(request.json["costo"])
            calorias = float(request.json["calorias"])
            sitio = request.json["sitio"]
            restaurante_id = int(request.json["restaurante"])  # Assuming the key is "restaurante_id"
            nuevo_ingrediente = Ingrediente(
                nombre=nombre,
                unidad=unidad,
                costo=costo,
                calorias=calorias,
                sitio=sitio,
                restaurante=restaurante_id  # Set the restaurante object, not just its ID
            )
            db.session.add(nuevo_ingrediente)
            db.session.commit()
            return ingrediente_schema.dump(nuevo_ingrediente), 201  # Return 201 status code for created resource
        except KeyError as e:
            return {"message": f"Missing required field: {e}"}, 400  # Bad request for missing fields
        except ValueError as e:
            return {"message": f"Invalid value for field: {e}"}, 400  # Bad request for invalid values


class VistaIngrediente(Resource):
    @jwt_required()
    def get(self, id_ingrediente):
        return ingrediente_schema.dump(Ingrediente.query.get_or_404(id_ingrediente))
        
    @jwt_required()
    def put(self, id_ingrediente):
        ingrediente = Ingrediente.query.get_or_404(id_ingrediente)
        ingrediente.nombre = request.json["nombre"]
        ingrediente.unidad = request.json["unidad"]
        ingrediente.costo = float(request.json["costo"])
        ingrediente.calorias = float(request.json["calorias"])
        ingrediente.sitio = request.json["sitio"]
        db.session.commit()
        return ingrediente_schema.dump(ingrediente)

    @jwt_required()
    def delete(self, id_ingrediente):
        ingrediente = Ingrediente.query.get_or_404(id_ingrediente)
        recetasIngrediente = RecetaIngrediente.query.filter_by(ingrediente=id_ingrediente).all()
        if not recetasIngrediente:
            db.session.delete(ingrediente)
            db.session.commit()
            return '', 204
        else:
            return 'El ingrediente se está usando en diferentes recetas', 409


class VistaRecetas(Resource):
    @jwt_required()
    def get(self, id_usuario):
        recetas = Receta.query.filter_by(usuario=str(id_usuario)).all()
        resultados = [receta_schema.dump(receta) for receta in recetas]
        ingredientes = Ingrediente.query.all()
        for receta in resultados:
            for receta_ingrediente in receta['ingredientes']:
                self.actualizar_ingredientes_util(receta_ingrediente, ingredientes)

        return resultados

    @jwt_required()
    def post(self, id_usuario):
        nueva_receta = Receta( \
            nombre = request.json["nombre"], \
            preparacion = request.json["preparacion"], \
            ingredientes = [], \
            usuario = id_usuario, \
            duracion = float(request.json["duracion"]), \
            porcion = float(request.json["porcion"]) \
        )
        for receta_ingrediente in request.json["ingredientes"]:
            nueva_receta_ingrediente = RecetaIngrediente( \
                cantidad = receta_ingrediente["cantidad"], \
                ingrediente = int(receta_ingrediente["idIngrediente"])
            )
            nueva_receta.ingredientes.append(nueva_receta_ingrediente)
            
        db.session.add(nueva_receta)
        db.session.commit()
        return ingrediente_schema.dump(nueva_receta)
        
    def actualizar_ingredientes_util(self, receta_ingrediente, ingredientes):
        for ingrediente in ingredientes: 
            if str(ingrediente.id)==receta_ingrediente['ingrediente']:
                receta_ingrediente['ingrediente'] = ingrediente_schema.dump(ingrediente)
                receta_ingrediente['ingrediente']['costo'] = float(receta_ingrediente['ingrediente']['costo'])
        

class VistaReceta(Resource):
    @jwt_required()
    def get(self, id_receta):
        receta = Receta.query.get_or_404(id_receta)
        ingredientes = Ingrediente.query.all()
        resultados = receta_schema.dump(Receta.query.get_or_404(id_receta))
        recetaIngredientes = resultados['ingredientes']
        for recetaIngrediente in recetaIngredientes:
            for ingrediente in ingredientes: 
                if str(ingrediente.id)==recetaIngrediente['ingrediente']:
                    recetaIngrediente['ingrediente'] = ingrediente_schema.dump(ingrediente)
                    recetaIngrediente['ingrediente']['costo'] = float(recetaIngrediente['ingrediente']['costo'])
        
        return resultados

    @jwt_required()
    def put(self, id_receta):
        receta = Receta.query.get_or_404(id_receta)
        receta.nombre = request.json["nombre"]
        receta.preparacion = request.json["preparacion"]
        receta.duracion = float(request.json["duracion"])
        receta.porcion = float(request.json["porcion"])
        
        #Verificar los ingredientes que se borraron
        for receta_ingrediente in receta.ingredientes:
            borrar = self.borrar_ingrediente_util(request.json["ingredientes"], receta_ingrediente)
                
            if borrar==True:
                db.session.delete(receta_ingrediente)
            
        db.session.commit()
        
        for receta_ingrediente_editar in request.json["ingredientes"]:
            if receta_ingrediente_editar['id']=='':
                #Es un nuevo ingrediente de la receta porque no tiene código
                nueva_receta_ingrediente = RecetaIngrediente( \
                    cantidad = receta_ingrediente_editar["cantidad"], \
                    ingrediente = int(receta_ingrediente_editar["idIngrediente"])
                    
                )
                receta.ingredientes.append(nueva_receta_ingrediente)
            else:
                #Se actualiza el ingrediente de la receta
                receta_ingrediente = self.actualizar_ingrediente_util(receta.ingredientes, receta_ingrediente_editar)
                db.session.add(receta_ingrediente)
        
        db.session.add(receta)
        db.session.commit()
        return ingrediente_schema.dump(receta)

    @jwt_required()
    def delete(self, id_receta):
        receta = Receta.query.get_or_404(id_receta)
        db.session.delete(receta)
        db.session.commit()
        return '', 204 
        
    def borrar_ingrediente_util(self, receta_ingredientes, receta_ingrediente):
        borrar = True
        for receta_ingrediente_editar in receta_ingredientes:
            if receta_ingrediente_editar['id']!='':
                if int(receta_ingrediente_editar['id']) == receta_ingrediente.id:
                    borrar = False
        
        return(borrar)

    def actualizar_ingrediente_util(self, receta_ingredientes, receta_ingrediente_editar):
        receta_ingrediente_retornar = None
        for receta_ingrediente in receta_ingredientes:
            if int(receta_ingrediente_editar['id']) == receta_ingrediente.id:
                receta_ingrediente.cantidad = receta_ingrediente_editar['cantidad']
                receta_ingrediente.ingrediente = receta_ingrediente_editar['idIngrediente']
                receta_ingrediente_retornar = receta_ingrediente
                
        return receta_ingrediente_retornar
    
class VistaChefs(Resource):
    @jwt_required()
    def get(self):
      restaurante_ids_as_string = request.args.get("restaurantes_ids")
      restaurante_ids_as_int = [int(id) for id in restaurante_ids_as_string.split(",")]
      
      usuarios = db.session.query(Usuario.id, Usuario.nombre, Usuario.rol, UsuarioRestaurante.restaurante).\
        join(UsuarioRestaurante, UsuarioRestaurante.usuario == Usuario.id).\
        filter(UsuarioRestaurante.restaurante.in_(restaurante_ids_as_int)).all()
      
      usuarios_json = [{"nombre": nombre, "id":str(id), "rol": rol, "restaurante_id": restaurante} for id, nombre, rol, restaurante in usuarios]
      print(usuarios_json)
      return jsonify(usuarios_json)
    
class VistaChef(Resource):
    @jwt_required()
    def get(self, chef_id):
        usuario = db.session.query(Usuario.id, Usuario.nombre, Usuario.rol, Usuario.usuario, Usuario.contrasena).\
        filter(Usuario.id == chef_id).first()
        return usuario_schema.dump(usuario)

class VistaTransferirChef(Resource):
    @jwt_required()
    def post(self, id_usuario):
        transferir = UsuarioRestaurante.query.filter_by(usuario=id_usuario).first()
        if transferir:
            transferir = UsuarioRestaurante.query.get_or_404(transferir.id)
            db.session.delete(transferir)
            db.session.commit()

            id_restaurante = request.json["id_restaurante"]
            new_usuario_restaurante = UsuarioRestaurante(usuario=id_usuario, restaurante=id_restaurante)
            db.session.add(new_usuario_restaurante)
            db.session.commit()
            return {'message': 'Chef transferido exitosamente', 'usuario_id': id_usuario, 'restaurante_id': id_restaurante}, 200
        else:
            db.session.rollback()  
            return {'message': 'No se encontró ningun chef'}, 404
        

class VistaActualizarUsuario(Resource):
    @jwt_required()
    def put(self, id_usuario):
        try:     
            data = request.get_json()
            usuario = Usuario.query.get(id_usuario)
            if usuario:
                if 'usuario' in data:
                    usuario.usuario = data['usuario']
                if 'contrasena' in data:
                    contrasena_encriptada = hashlib.md5(data['contrasena'].encode('utf-8')).hexdigest()
                    usuario.contrasena = contrasena_encriptada
                if 'nombre' in data:
                    usuario.nombre = data['nombre']
                db.session.commit()
                return {'message': 'Usuario updated successfully'}, 200
            else:
                return {'message': 'Usuario not found'}, 404
        except Exception as e:
            db.session.rollback()  
            return {'message': 'An error occurred', 'error': str(e)}, 500
        finally:
            db.session.close()  
     
    @jwt_required()
    def delete(self, id_usuario):
        try:
            usuario = Usuario.query.get(id_usuario)
            usuario_restaurante = UsuarioRestaurante.query.filter_by(usuario = id_usuario).first()
            if usuario and usuario_restaurante:
                db.session.delete(usuario)
                db.session.delete(usuario_restaurante)
                db.session.commit()
                return {'message': f'El chef con id {id_usuario} ha sido eliminado correctamente.'}
            else:
                return {'message': f'Chef no encontrado.'}, 404
        except Exception as e:
            db.session.rollback()
            print(e)
            return {'error': f'Error al eliminar el chef {e}.'}, 500
        finally:
            db.session.close()


class VistaRestaurantes(Resource):
    @jwt_required()
    def get(self, id_usuario):
        ids_restaurantes = UsuarioRestaurante.query.filter_by(usuario=int(id_usuario)).all()
        restaurantes = Restaurante.query.filter(
                Restaurante.id.in_(tuple([restaurante_por_usuario.restaurante for restaurante_por_usuario in ids_restaurantes]))
            ).all()
        return [restaurante_schema.dump(restaurante) for restaurante in restaurantes]
    
    @jwt_required()
    def delete(self, id_restaurante):
        restaurante = Restaurante.query.get_or_404(id_restaurante)
        db.session.delete(restaurante)
        db.session.commit()
        return '', 204 
    @jwt_required()
    def get(self, id_usuario):
        ids_restaurantes = UsuarioRestaurante.query.filter_by(usuario=int(id_usuario)).all()
        restaurantes = Restaurante.query.filter(
        Restaurante.id.in_(tuple([restaurante_por_usuario.restaurante for restaurante_por_usuario in ids_restaurantes]))).all()
        return [restaurante_schema.dump(restaurante) for restaurante in restaurantes]
        
class VistaModificarRestaurante(Resource):
    @jwt_required()
    def delete(self, id_restaurante):
        try:
            restaurante = Restaurante.query.get(id_restaurante)
            if not restaurante:
                return {"message": "Restaurante no encontrado"}, 404
            chefs_asociados = UsuarioRestaurante.query.join(Usuario).filter(
			    UsuarioRestaurante.restaurante == id_restaurante,
			    Usuario.rol == 'Chef'
		    ).count()
            if chefs_asociados > 0:
                return {"message": "No se puede eliminar el restaurante porque hay Chefs asociados"}, 403
            usuarios_restaurantes = UsuarioRestaurante.query.filter_by(restaurante = id_restaurante)
            if usuarios_restaurantes:
                for usuario_restaurante in usuarios_restaurantes:
                    db.session.delete(usuario_restaurante)
                    usuario = Usuario.query.get(usuario_restaurante.id)
                    if usuario:
                        db.session.delete(usuario)
            
            redes_sociales = RedSocial.query.filter_by(restaurante = id_restaurante)
            if redes_sociales:
                for red_social in redes_sociales:
                    print(red_social)
                    db.session.delete(red_social)
            aplicaciones_moviles = AplicacionMovil.query.filter_by(restaurante = id_restaurante)
            if aplicaciones_moviles:
                for aplicacion_movil in aplicaciones_moviles:
                    db.session.delete(aplicacion_movil)
            horarios = Horario.query.filter_by(restaurante = id_restaurante)
            if horarios:
                for horario in horarios:
                    db.session.delete(horario)
            
            restaurante = Restaurante.query.get(id_restaurante)
            if restaurante:
                db.session.delete(restaurante)
                db.session.commit()
                return {"message": "Restaurante Elimnado"}, 200
            else:
                return {"message": "Restaurante no encontrado"}, 404
        except Exception as error:
            lineaError = error.__traceback__
            print({ "ERROR": str(error), "LINEA": str(lineaError.tb_lineno)})
            return { "ERROR": str(error), "LINEA": str(lineaError.tb_lineno)}
        
class VistaCrearChef(Resource):
    @jwt_required()
    def post(self):
        try:
            data = request.get_json()
            usuario = data.get('usuario')
            contrasena = data.get('contrasena')
            nombre_usuario = data.get('nombre')
            idRestaurante = data.get('idRestaurante')
            contrasena_encriptada = hashlib.md5(contrasena.encode('utf-8')).hexdigest()
            # Check if the usuario already exists
            existing_usuario = Usuario.query.filter_by(usuario=usuario).first()
            if existing_usuario:
                return {'error': 'El usuario ya existe en la base de datos.'}, 400
            new_usuario = Usuario(usuario=usuario, contrasena=contrasena_encriptada, nombre=nombre_usuario, rol="Chef")
            db.session.add(new_usuario)
            db.session.commit()
            #Se consulta el usuario recien guardado para poder guardar su id en la tabla UsuarioRestaurante
            usuario_recien_creado = Usuario.query.filter_by(nombre=nombre_usuario).first()
            new_usuario_restaurante = UsuarioRestaurante(usuario=usuario_recien_creado.id, restaurante=idRestaurante)
            db.session.add(new_usuario_restaurante)
            db.session.commit()
            return {'message': f'Usuario {nombre_usuario} creado correctamente.'}, 201
        except Exception as e:
            db.session.rollback()
            print(f'Ocurrio un error: {e}')
            return {'error': f'Ocurrió un error mientras se creaba el usuario {e}.'}, 500
        finally:
            db.session.close()

class VistaRestaurante(Resource):
    @jwt_required()
    def post(self):
        try:
            print(request)
            nuevoRestaurante = Restaurante(
                nombre = str(request.json["nombre"]),
                direccion = str(request.json["direccion"]),
                telefono = str(request.json["telefono"]),
                tipo_comida = str(request.json["tipo_comida"]),
                domicilio = int(request.json["domicilio"]),
                consumo = int(request.json["consumo"])
            )
            db.session.add(nuevoRestaurante)
            db.session.commit()
            idRestaurante = Restaurante.query.filter_by(
                nombre = str(request.json["nombre"]),
                direccion = str(request.json["direccion"]),
                telefono = str(request.json["telefono"]),
                tipo_comida = str(request.json["tipo_comida"]),
                domicilio = int(request.json["domicilio"]),
                consumo = int(request.json["consumo"])
            ).first()
            usuarioRestaurante = UsuarioRestaurante(
                usuario = int(request.json["idUsuario"]),
                restaurante = int(idRestaurante.id)
            )
            db.session.add(usuarioRestaurante)
            db.session.commit()
            redSocialNueva = RedSocial(
                nombre = str(request.json["redesSociales"]),
                restaurante = int(idRestaurante.id)
            )
            db.session.add(redSocialNueva)
            db.session.commit()
            # if len(request.json["redesSociales"]) > 0:
            #     for redSocial in request.json["redesSociales"]:
            #         redSocialNueva = RedSocial(
            #             nombre = str(redSocial),
            #             restaurante = int(idRestaurante.id)
            #         )
            #         db.session.add(redSocialNueva)
            #         db.session.commit()
            aplicacionMovilNueva = AplicacionMovil(
                nombre = str(request.json["aplicacionesMoviles"]),
                restaurante = int(idRestaurante.id)
            )
            db.session.add(aplicacionMovilNueva)
            db.session.commit()
            # if len(request.json["aplicacionesMoviles"]) > 0:
            #     for aplicacionMovil in request.json["aplicacionesMoviles"]:
            #         aplicacionMovilNueva = AplicacionMovil(
            #             nombre = str(aplicacionMovil),
            #             restaurante = int(idRestaurante.id)
            #         )
            #         db.session.add(aplicacionMovilNueva)
            #         db.session.commit()
            if len(request.json["horario"]) > 0:
                for horario in request.json["horario"]:
                    horarioNuevo = Horario(
                        dia_apertura = str(horario["id"]),
                        hora_inicio = str(horario["horaInicio"]),
                        hora_fin = str(horario["horaFin"]),
                        restaurante = int(idRestaurante.id)
                    )
                    db.session.add(horarioNuevo)
                    db.session.commit()
            
            return restaurante_schema.dump(nuevoRestaurante)
        except Exception as error:
            lineaError = error.__traceback__
            print({ "ERROR": str(error), "LINEA": str(lineaError.tb_lineno) })
            return "Error"

class VistaRestauranteEditar(Resource):
    @jwt_required()
    def post(self):
        try:
            restauranteEditado = Restaurante.query.get_or_404(int(request.json["id"]))
            restauranteEditado.nombre = str(request.json["nombre"])
            restauranteEditado.direccion = str(request.json["direccion"])
            restauranteEditado.telefono = str(request.json["telefono"])
            restauranteEditado.tipo_comida = str(request.json["tipo_comida"])
            restauranteEditado.domicilio = int(request.json["domicilio"])
            restauranteEditado.consumo = int(request.json["consumo"])
            db.session.commit()
            redesSocialesEliminar = RedSocial.query.filter_by(
                restaurante = int(request.json["id"])
            ).all()
            if (redesSocialesEliminar != None):
                if (len(redesSocialesEliminar) > 0):
                    for redSocialEliminar in redesSocialesEliminar:
                        redSocialEliminada = db.session.query(RedSocial).get(redSocialEliminar.id)
                        db.session.delete(redSocialEliminada)
                        db.session.commit()
            redSocialNueva = RedSocial(
                nombre = str(request.json["redesSociales"]),
                restaurante = int(int(request.json["idRedSocial"]))
            )
            db.session.add(redSocialNueva)
            db.session.commit()
            # if len(request.json["redesSociales"]) > 0:
            #     for redSocial in request.json["redesSociales"]:
            #         redSocialNueva = RedSocial(
            #             nombre = str(redSocial["id"]),
            #             restaurante = int(int(request.json["id"]))
            #         )
            #         db.session.add(redSocialNueva)
            #         db.session.commit()
            aplicacionesMovilesEliminar = AplicacionMovil.query.filter_by(
                restaurante = int(request.json["id"])
            ).all()
            if (aplicacionesMovilesEliminar != None):
                if (len(aplicacionesMovilesEliminar) > 0):
                    for aplicacionMovilEliminar in aplicacionesMovilesEliminar:
                        aplicacionMovilEliminada = db.session.query(AplicacionMovil).get(aplicacionMovilEliminar.id)
                        db.session.delete(aplicacionMovilEliminada)
                        db.session.commit()
            aplicacionMovilNueva = AplicacionMovil(
                nombre = str(request.json["aplicacionesMoviles"]),
                restaurante = int(int(request.json["idAplicacionMovil"]))
            )
            db.session.add(aplicacionMovilNueva)
            db.session.commit()
            # if len(request.json["aplicacionesMoviles"]) > 0:
            #     for aplicacionMovil in request.json["aplicacionesMoviles"]:
            #         aplicacionMovilNueva = AplicacionMovil(
            #             nombre = str(aplicacionMovil["id"]),
            #             restaurante = int(int(request.json["id"]))
            #         )
            #         db.session.add(aplicacionMovilNueva)
            #         db.session.commit()
            horariosEliminar = Horario.query.filter_by(
                restaurante = int(request.json["id"])
            ).all()
            if (horariosEliminar != None):
                if (len(horariosEliminar) > 0):
                    for horarioEliminar in horariosEliminar:
                        horarioEliminada = db.session.query(Horario).get(horarioEliminar.id)
                        db.session.delete(horarioEliminada)
                        db.session.commit()
            if len(request.json["horario"]) > 0:
                for horario in request.json["horario"]:
                    horarioNuevo = Horario(
                        dia_apertura = str(horario["id"]),
                        hora_inicio = str(horario["horaInicio"]),
                        hora_fin = str(horario["horaFin"]),
                        restaurante = int(int(request.json["id"]))
                    )
                    db.session.add(horarioNuevo)
                    db.session.commit()            
            return restaurante_schema.dump(restauranteEditado)
        except:
            return "Error"

class VistaRestauranteConsultaEditar(Resource):
    @jwt_required()
    def get(self, idRestaurante):
        try:
            restaurante_objeto = restaurante_schema.dump(Restaurante.query.get_or_404(idRestaurante))
            redes_sociales = RedSocial.query.filter_by(restaurante=int(idRestaurante)).all()
            aplicacion_movil = AplicacionMovil.query.filter_by(restaurante=int(idRestaurante)).all()
            resultado = {
                "id": restaurante_objeto["id"],
                "domicilio": restaurante_objeto["domicilio"],
                "direccion": restaurante_objeto["direccion"],
                "consumo": restaurante_objeto["consumo"],
                "telefono": restaurante_objeto["telefono"],
                "tipo_comida": restaurante_objeto["tipo_comida"],
                "nombre": restaurante_objeto["nombre"],
                "idRedSocial": redes_sociales[0].id,
                "nombreRedSocial": redes_sociales[0].nombre,
                "idAplicacionMovil": aplicacion_movil[0].id,
                "nombreAplicacionMovil": aplicacion_movil[0].nombre,
            }
            return resultado
        except:
            return "Error"
        
# class VistaRestauranteConsultaEditar(Resource):
#     @jwt_required()
#     def get(self, idRestaurante):
#         try:
#             resultado = restaurante_schema.dump(Restaurante.query.get_or_404(idRestaurante))
#             return resultado
#         except:
#             return "Error"

# class VistaRedSocial(Resource):
#     @jwt_required()
#     def get(self, idRestaurante):
#         try:
#             redes_sociales = RedSocial.query.filter_by(restaurante=int(idRestaurante)).all()
#             return [red_social_schema.dump(red_social) for red_social in redes_sociales]
#         except:
#             return "Error"

# class VistaAplicacionMovil(Resource):
#     @jwt_required()
#     def get(self, idRestaurante):
#         try:
#             aplicacion_movil = AplicacionMovil.query.filter_by(restaurante=int(idRestaurante)).all()
#             return [aplicacion_movil_schema.dump(aplicacion) for aplicacion in aplicacion_movil]
#         except:
#             return "Error"

class VistaHorario(Resource):
    @jwt_required()
    def get(self, idRestaurante):
        try:
            horario_bd = Horario.query.filter_by(restaurante=int(idRestaurante)).all()
            return [horario_bd_schema.dump(horario) for horario in horario_bd]
        except:
            return "Error"

class VistaInfoUsuario(Resource):
    def get(self, id_usuario):
        user = Usuario.query.get(id_usuario)

        if user is None:
            return jsonify({'message': 'Usuario no encontrado'}), 404

        response_data = {
            'usuario': user.usuario,
            'nombre': user.nombre,
            'rol': user.rol
        }

        return jsonify(response_data)

class VistaMenus(Resource):
    @jwt_required()
    def get(self, id_usuario, id_restaurante):
        try:
            
            matching_menus = Menu.query.filter_by(restaurante=id_restaurante).all()

            if matching_menus:
                menu_data_list = []

                
                for matching_menu in matching_menus:
                    
                    matching_usuario_restaurante = UsuarioRestaurante.query.filter_by(
                        usuario=id_usuario, restaurante=id_restaurante
                    ).first()

                    if matching_usuario_restaurante:
                       
                        menu_data = {
                            'id_menu': matching_menu.id,
                            'nombre': matching_menu.nombre,
                            'fechainicio': matching_menu.fechainicio,
                            'fechafinal': matching_menu.fechafinal
                            
                        }
                        menu_data_list.append(menu_data)

                return jsonify(menu_data_list)
            else:
                return jsonify([])  

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @jwt_required()
    def post(self, id_usuario, id_restaurante):
        nuevo_menu = Menu( \
            nombre = request.json["nombre"], \
            fechainicio = request.json["fechainicio"], \
            fechafinal = request.json["fechafinal"], \
            restaurante = id_restaurante, \
            recetas = [], \
            usuario = id_usuario, \
        )

        for menu_receta in request.json["recetas"]:
            nuevo_menu_receta = MenuReceta(
                porcion = menu_receta["porcion"],
                id_receta = int(menu_receta["idReceta"]),
            )
            nuevo_menu.recetas.append(nuevo_menu_receta)
            
        db.session.add(nuevo_menu)
        db.session.commit()

        menu = Menu.query.filter_by(nombre=request.json["nombre"]).order_by(Menu.id.desc()).first()

        for menu_receta_2 in request.json["recetas"]:
            menu_receta = MenuReceta.query.get_or_404(int(menu_receta_2["idReceta"]))
            menu_receta.id_menu = menu.id

        return {'message': f'Menu {nuevo_menu.nombre} creado correctamente.'}, 201

class VistaModificarMenus(Resource):    
    @jwt_required()
    def delete(self, id_menu):
        try:
            menu = Menu.query.get(id_menu)
            if menu is not None:
                db.session.delete(menu)
                db.session.commit()
                MenuReceta.query.filter_by(id_menu=id_menu).delete()
                db.session.commit()

                return jsonify({'message': 'El menú se borro de manera correcta'})
            else:
                return jsonify({'message': 'Menú no encontrado'}), 404

        except Exception as e:
            db.session.rollback()
            return jsonify({'message': 'Error borrando menú: ' + str(e)}), 500
    
    @jwt_required()
    def put(self, id_menu):
        
        menu = Menu.query.get(id_menu)
        if not menu:
            return {'message': 'Menu not found'}, 404

        print(request.json)
        if 'nombre' in request.json:
            menu.nombre = request.json['nombre']
        if 'fechainicio' in request.json:
            menu.fechainicio = request.json['fechainicio']
        if 'fechafinal' in request.json:
            menu.fechafinal = request.json['fechafinal']

        
        menu.recetas[:] = []  
        
        for menu_receta_data in request.json.get('recetas', []):
            nuevo_menu_receta = MenuReceta(
                porcion=menu_receta_data.get('porcion', 0),
                id_receta=menu_receta_data.get('id', 0)
            )
            menu.recetas.append(nuevo_menu_receta)

        db.session.commit()
        return {'message': f'Menu {menu.nombre} updated successfully'}, 200
        
class VistaMenusRecetas(Resource):
    @jwt_required()
    def get(self,id_menu):
        try:
            menu_details = db.session.query(
                Menu.nombre.label('menu_nombre'),
                Menu.fechainicio,
                Menu.fechafinal,
                Receta.nombre,
                MenuReceta.porcion,
                MenuReceta.id_receta
            ).join(
                MenuReceta,
                MenuReceta.id_menu == Menu.id
            ).join(
                Receta,
                Receta.id == MenuReceta.id_receta
            ).filter(
                Menu.id == id_menu
            ).all()

            if not menu_details:
                return jsonify({'message': 'Menu not found'}), 404
            
            result = {
                'nombre': menu_details[0].menu_nombre,
                'fechainicio': menu_details[0].fechainicio,
                'fechafinal': menu_details[0].fechafinal,
                'recetas': [{
                    'id': row.id_receta,
                    'nombre': row.nombre,
                    'porcion': row.porcion
                } for row in menu_details]
            }

            return jsonify(result)

        except Exception as e:
            return jsonify({'message': str(e)}), 500

class VistaValidarFechasEditarMenu(Resource):
    @jwt_required()
    def post(self):
        
        fecha_inicio_str = request.json.get('fechainicio')
        fecha_final_str = request.json.get('fechafinal')
        id_menu_actual = request.json.get('id_menu')
        
        overlap = db.session.query(Menu).filter(
        (Menu.id != id_menu_actual) &
        (Menu.fechainicio <= fecha_final_str) &
        (Menu.fechafinal >= fecha_inicio_str)
    ).count() > 0

        return jsonify({'overlap': overlap})

class VistaValidarFechasCrearMenu(Resource):
    @jwt_required()
    def post(self):
        fecha_inicio_str = request.json.get('fechainicio')
        fecha_final_str = request.json.get('fechafinal')
        
        overlap = db.session.query(Menu).filter(
            (Menu.fechainicio <= fecha_final_str) &
            (Menu.fechafinal >= fecha_inicio_str)
        ).count() > 0

        return jsonify({'overlap': overlap})

class VistaCompras(Resource):

    def _get_ingredientes_desde_bd(self):
        resultados = []
        for receta in self.menu["recetas"]:
            receta_bd = receta_schema.dump(Receta.query.get_or_404(receta["id"]))
            for ingrediente in receta_bd["ingredientes"]:
                ingrediente_bd = ingrediente_schema.dump(Ingrediente.query.get_or_404(ingrediente["ingrediente"]))
                resultados.append({
                    "ingrediente": ingrediente_bd["nombre"],
                    "cantidad": ingrediente["cantidad"],
                    "sitio": ingrediente_bd["sitio"],
                    "precio": ingrediente_bd["costo"],
                    "receta": receta_bd["nombre"]
                })
        return resultados
    
    def _calcular_costo_y_cantidad(self):
        resultado_calculado = []
        print(self.menu_receta)
        menu_receta_porcion = int(self.menu_receta['porcion'])
        resultados_desde_bd = self._get_ingredientes_desde_bd()
        ingredientes = {ingrediente_item["ingrediente"] for ingrediente_item in resultados_desde_bd}
        for ingrediente in ingredientes:
            cantidad = 0
            precio = 0
            sitio = ""
            receta_array = []
            for item in resultados_desde_bd:
                if item["ingrediente"] == ingrediente:
                    sitio = item["sitio"]
                    cantidad = cantidad + float(item["cantidad"])
                    precio = precio + float(item["precio"])
                    receta_array.append(item["receta"])
            resultado_calculado.append({
                "ingrediente": ingrediente,
                "cantidad": cantidad * menu_receta_porcion,
                "sitio": sitio,
                "precio": precio * cantidad * menu_receta_porcion,
                "recetas": receta_array
            })
        return resultado_calculado

    def _agrupar_compras_por(self, contenido_a_ordenar, key):
        contenido_ordenado = sorted(contenido_a_ordenar, key = itemgetter('sitio'))

        resultado_final = []
        for _, value in groupby(contenido_ordenado, key = itemgetter("sitio")):
            grouped_values = list(value)
            for val in grouped_values:
                resultado_final.append(val)
        return resultado_final

    @jwt_required()
    def get(self, menu_id):
        self.menu = menu_bd_schema.dump(Menu.query.get_or_404(menu_id))
        self.menu_receta = menu_receta_bd_schema.dump(MenuReceta.query.filter(MenuReceta.id_menu == menu_id).first())
        print(self.menu_receta)
        ingredientes_calculados = self._calcular_costo_y_cantidad()
        return jsonify(self._agrupar_compras_por(
            contenido_a_ordenar = ingredientes_calculados,
            key= 'sitio'
        ))
