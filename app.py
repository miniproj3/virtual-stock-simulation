from flask import *
from auth import auth_bp
from exchange import exchange_bp
from mypage import mypage_bp
from stock_kr import stock_kr_bp
from stock_us import stock_us_bp

app = Flask(__name__)
app.secret_key='1234'

app.register_blueprint(auth_bp)
app.register_blueprint(exchange_bp)
app.register_blueprint(mypage_bp)
app.register_blueprint(stock_kr_bp)
app.register_blueprint(stock_us_bp)

@app.route('/')
def index():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)