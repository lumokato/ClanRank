from flask import Blueprint, render_template, request
from ..services import farm_service

farm_bp = Blueprint('farm', __name__)

@farm_bp.route('/farm', methods=['GET', 'POST'])
def index_farm():
    return render_template('farm.html')

@farm_bp.route('/remove_user', methods=['POST'])
def test_post():
    clanid = request.form.get("clanid")
    passwd = request.form.get("passwd")
    clear_type = request.form.get("type")
    msg = farm_service.user_clear(clanid, passwd, clear_type)
    return msg
