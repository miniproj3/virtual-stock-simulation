from flask import *
from db import *

mypage = Blueprint('mypage', __name__)

@mypage.route('/')
def mypage_home():
    user_info = session.get('user')
    if not user_info:
        return redirect(url_for('auth.kakaologin'))  # 로그인 페이지로 리디렉트 

    user_id = user_info['id']
    user = User.query.get(user_id)
    if not user:
        return "사용자를 찾을 수 없습니다.", 404

    # 사용자의 주문 내역 가져오기
    orders = Order.query.filter_by(user_id=user.id).all()
    
    return render_template(
        'mypage.html',
        user=user,
        orders=orders  # 포트폴리오 대신 주문 내역을 전달
    )

