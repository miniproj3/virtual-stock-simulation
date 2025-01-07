from flask import *

app = Flask(__name__)
app.secret_key='1234'

stock_kr_bp = Blueprint('stock_kr', __name__)

@stock_kr_bp.route('/stock_kr')
def stock_kr():

    return render_template()