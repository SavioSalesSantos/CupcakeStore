from flask import Blueprint

bp = Blueprint('main', __name__)

@bp.route('/sobre')
def sobre():
    return "Esta é uma loja de cupcakes!"