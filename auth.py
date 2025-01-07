from flask import *

app = Flask(__name__)
app.secret_key='1234'

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth')
def auth():

    return render_template()