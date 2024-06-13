from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restful import Api


from modelos import db
from vistas import \
    VistaIngrediente, VistaIngredientes, \
    VistaReceta, VistaRecetas, VistaMenus, VistaModificarMenus, VistaMenusRecetas, VistaValidarFechasEditarMenu, VistaValidarFechasCrearMenu, \
    VistaSignIn, VistaLogIn, VistaActualizarUsuario, VistaInfoUsuario, \
    VistaRestaurantes, VistaRestaurante, VistaTransferirChef, VistaModificarRestaurante, \
    VistaCrearChef, VistaChef, VistaRestauranteConsultaEditar, VistaRestauranteEditar, VistaHorario, VistaChefs, \
    VistaCompras

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dbapp.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'frase-secreta'
app.config['PROPAGATE_EXCEPTIONS'] = True

app_context = app.app_context()
app_context.push()

db.init_app(app)
print("PRUEBA 1")
db.drop_all()
db.session.commit()
db.create_all()
print("PRUEBA 2")

cors = CORS(app)

api = Api(app)
api.add_resource(VistaSignIn, '/signin')
api.add_resource(VistaLogIn, '/login')
api.add_resource(VistaIngredientes, '/ingredientes')
api.add_resource(VistaIngrediente, '/ingrediente/<int:id_ingrediente>')
api.add_resource(VistaRecetas, '/recetas/<int:id_usuario>')

api.add_resource(VistaRestaurantes, '/restaurantes/<int:id_usuario>')
api.add_resource(VistaRestaurante, "/restaurantes")
api.add_resource(VistaRestauranteEditar, "/restaurante_editar")

api.add_resource(VistaRestauranteConsultaEditar, "/restaurante_editar/<int:idRestaurante>")
api.add_resource(VistaHorario, "/horario/<int:idRestaurante>")

api.add_resource(VistaReceta, '/receta/<string:id_receta>')
api.add_resource(VistaChefs, '/chefs')
api.add_resource(VistaTransferirChef, '/transferir/<int:id_usuario>')
api.add_resource(VistaActualizarUsuario, '/usuario/editar/<string:id_usuario>')
api.add_resource(VistaModificarRestaurante, '/restaurante/<int:id_restaurante>')
api.add_resource(VistaCrearChef, '/usuario')
api.add_resource(VistaChef, '/dar/chef/<int:chef_id>')
api.add_resource(VistaInfoUsuario, '/usuario/info/<int:id_usuario>')

api.add_resource(VistaMenus, '/menus/<string:id_usuario>/<int:id_restaurante>')
api.add_resource(VistaModificarMenus, '/menu/<int:id_menu>')
api.add_resource(VistaMenusRecetas, '/menu/recetas/<int:id_menu>')
api.add_resource(VistaValidarFechasEditarMenu, '/menu/editar/validar-fechas/')
api.add_resource(VistaValidarFechasCrearMenu, '/menu/crear/validar-fechas/')
api.add_resource(VistaCompras, '/compras/<int:menu_id>')
##api.add_resource(VistaRestauranteIngrediente)

jwt = JWTManager(app)