from flask import *

app = Flask(__name__)
app.secret_key='1234'

stock_us_bp = Blueprint('stock_us', __name__)

@stock_us_bp.route('/stock_us')
def stock_us():

    return render_template()