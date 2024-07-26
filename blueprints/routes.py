# routes.py
from flask import Blueprint
from flask_restful import Api
from vistas import (
    VistaIngrediente, VistaIngredientes,
    VistaReceta, VistaRecetas, VistaMenus, VistaModificarMenus, 
    VistaMenusRecetas, VistaValidarFechasEditarMenu, VistaValidarFechasCrearMenu,
    VistaSignIn, VistaLogIn, VistaActualizarUsuario, VistaInfoUsuario,
    VistaRestaurantes, VistaRestaurante, VistaTransferirChef, VistaModificarRestaurante,
    VistaCrearChef, VistaChef, VistaRestauranteConsultaEditar, VistaRestauranteEditar,
    VistaHorario, VistaChefs, VistaCompras
)

routesBlueprint = Blueprint('routes', __name__)
api = Api(routesBlueprint)

def initializeBlueprint(api: Api):
    api.add_resource(VistaSignIn, "/signin")
    api.add_resource(VistaLogIn, "/login")
    api.add_resource(VistaIngredientes, "/ingredientes")
    api.add_resource(VistaIngrediente, "/ingrediente/<int:id_ingrediente>")
    api.add_resource(VistaRecetas, "/recetas/<int:id_usuario>")
    api.add_resource(VistaRestaurantes, "/restaurantes/<int:id_usuario>")
    api.add_resource(VistaRestaurante, "/restaurantes")
    api.add_resource(VistaRestauranteEditar, "/restaurante_editar")
    api.add_resource(VistaRestauranteConsultaEditar, "/restaurante_editar/<int:idRestaurante>")
    api.add_resource(VistaHorario, "/horario/<int:idRestaurante>")
    api.add_resource(VistaReceta, "/receta/<string:id_receta>")
    api.add_resource(VistaChefs, "/chefs")
    api.add_resource(VistaTransferirChef, "/transferir/<int:id_usuario>")
    api.add_resource(VistaActualizarUsuario, "/usuario/editar/<string:id_usuario>")
    api.add_resource(VistaModificarRestaurante, "/restaurante/<int:id_restaurante>")
    api.add_resource(VistaCrearChef, "/usuario")
    api.add_resource(VistaChef, "/dar/chef/<int:chef_id>")
    api.add_resource(VistaInfoUsuario, "/usuario/info/<int:id_usuario>")
    api.add_resource(VistaMenus, "/menus/<string:id_usuario>/<int:id_restaurante>")
    api.add_resource(VistaModificarMenus, "/menu/<int:id_menu>")
    api.add_resource(VistaMenusRecetas, "/menu/recetas/<int:id_menu>")
    api.add_resource(VistaValidarFechasEditarMenu, "/menu/editar/validar-fechas/")
    api.add_resource(VistaValidarFechasCrearMenu, "/menu/crear/validar-fechas/")
    api.add_resource(VistaCompras, "/compras/<int:menu_id>")

initializeBlueprint(api)
