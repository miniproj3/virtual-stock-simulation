from flask import *

app = Flask(__name__)
app.secret_key='1234'

mypage_bp = Blueprint('mypage', __name__)

@mypage_bp.route('/auth')
def mypage():

    return render_template()