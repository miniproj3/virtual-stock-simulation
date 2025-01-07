from flask import *
from flask_session import Session
from flask_login import *
from db import *
from auth import auth
from stock_kr import stock_kr
from exchange import exchange
from mypage import mypage

from socketio_instance import socketio

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'my_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'#여기다 rds 주소넣으면 됩니다
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SESSION_TYPE'] = 'filesystem'

    db.init_app(app)
    Session(app)
    socketio.init_app(app)

    # 블루프린트 등록
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(stock_kr, url_prefix='/stock_kr')
    app.register_blueprint(exchange, url_prefix='/exchange')
    app.register_blueprint(mypage, url_prefix='/mypage')

    @app.route('/')
    def main():
        user = User.query.filter_by(username='testuser').first()
        if user:
            session['username'] = user.username
            session['seed_krw'] = user.seed_krw
            session['seed_usd'] = user.seed_usd
            return render_template('main.html', user=user)
        else:
            return "User not found", 404

    return app

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='testuser').first():
            test_user = User(username='testuser', password='testpass', seed_krw=1000000, seed_usd=0)
            db.session.add(test_user)
            db.session.commit()
            
    socketio.run(app, debug=True)
