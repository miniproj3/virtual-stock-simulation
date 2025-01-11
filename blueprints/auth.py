from flask import *
import requests
from db import db, User
from datetime import datetime

# 카카오 API 설정
REST_API_KEY = "d37e3286aa4a1b7e3a2c084309f70d72"
REDIRECT_URI = "http://127.0.0.1:5000/auth/kakaoLoginLogicRedirect"

# 블루프린트 생성
auth = Blueprint('auth', __name__)

# 카카오 로그인 메인 페이지
@auth.route("/", methods=["GET"])
def kakaologin():
    access_token = session.get("access_token")
    user_info = session.get("user")  # 세션에서 사용자 정보 가져오기

    if access_token and user_info:
        return f"안녕하세요, {user_info.get('name', 'Guest')}님!"

    return render_template("auth.html")

# 카카오 로그인 로직
@auth.route("/kakaoLoginLogic", methods=["GET"])
def kakaoLoginLogic():
    url = (
        f"https://kauth.kakao.com/oauth/authorize"
        f"?client_id={REST_API_KEY}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
    )
    return redirect(url)

# 카카오 로그인 리다이렉트 처리
@auth.route("/kakaoLoginLogicRedirect", methods=["GET"])
def kakaoLoginLogicRedirect():
    code = request.args.get("code")
    if not code:
        print("Error: 인증 코드가 없습니다.")
        return "카카오 로그인 인증 코드가 없습니다.", 400

    token_url = "https://kauth.kakao.com/oauth/token"

    response = requests.post(
        token_url,
        data={
            "grant_type": "authorization_code",
            "client_id": REST_API_KEY,
            "redirect_uri": REDIRECT_URI,
            "code": code,
        },
    )

    access_token = response.json().get("access_token")
    if access_token:
        session["access_token"] = access_token
        print("Access token 저장 성공:", access_token)

        # 카카오 사용자 정보 가져오기
        kakao_user_info = requests.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {access_token}"}
        ).json()

        # 사용자 정보 처리
        kakao_id = kakao_user_info.get('id')  # 카카오 계정 고유 ID
        nickname = kakao_user_info.get('properties', {}).get('nickname', 'No nickname')
        email = kakao_user_info.get('kakao_account', {}).get('email', None)

        # 데이터베이스에 사용자 추가 로직
        existing_user = User.query.filter_by(id=kakao_id).first()

        if not existing_user:
            new_user = User(
                id=kakao_id,  # 카카오 ID를 primary key로 사용
                username=nickname,
                seed_krw=1000000.0,  # 초기 KRW 자본
                seed_usd=0.0,  # 초기 USD 자본
                created_at=datetime.utcnow(),
                last_login=datetime.utcnow()
            )
            db.session.add(new_user)
            db.session.commit()
            print(f"[DEBUG] 새로운 사용자 추가: ID={kakao_id}, 이름={nickname}")
        else:
            # 기존 사용자 마지막 로그인 시간 갱신
            existing_user.last_login = datetime.utcnow()
            db.session.commit()
            print(f"[DEBUG] 기존 사용자 로그인: ID={kakao_id}, 이름={nickname}")

        # 사용자 정보를 세션에 저장
        session['user'] = {
            'id': kakao_id,
            'name': nickname,
            'email': email
        }

        return redirect("/stock_kr")  # 로그인 성공 후 홈으로 리다이렉트
    else:
        print("Access token 발급 실패:", response.json())
        return "Access token 발급 실패.", 500