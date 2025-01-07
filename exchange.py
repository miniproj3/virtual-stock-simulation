from flask import *

app = Flask(__name__)
app.secret_key='1234'

exchange_bp = Blueprint('exchange', __name__)

@exchange_bp.route('/exchange')
def exchange():

    return render_template()