from flask import *
from datetime import datetime, timezone
from db import db, User
import requests
from db import db, User
from datetime import datetime

# 카카오 API 설정
REST_API_KEY = "d37e3286aa4a1b7e3a2c084309f70d72"
REDIRECT_URI = "http://127.0.0.1:5000/auth/kakaoLoginLogicRedirect"

auth = Blueprint('auth', __name__)

@auth.route("/", methods=["GET"])
def kakaologin():
    access_token = session.get("access_token")
<<<<<<< HEAD
    user_info = session.get("user")

    if access_token and user_info:
        return f"안녕하세요, {user_info.get('username', 'Guest')}님!"
=======
    user_info = session.get("user")  # 세션에서 사용자 정보 가져오기

    if access_token and user_info:
        return f"안녕하세요, {user_info.get('name', 'Guest')}님!"
>>>>>>> 17b07bf2a76299b349a0cc91a67803d826858b35

    return render_template("auth.html")

@auth.route("/kakaoLoginLogic", methods=["GET"])
def kakaoLoginLogic():
    url = (
        f"https://kauth.kakao.com/oauth/authorize?"
        f"client_id={REST_API_KEY}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
    )
    return redirect(url)

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

        kakao_user_info = requests.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {access_token}"}
        ).json()

<<<<<<< HEAD
        kakao_id = kakao_user_info.get('id')
        username = kakao_user_info.get('properties', {}).get('nickname', 'No username')  # 닉네임 필드
=======
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
>>>>>>> 17b07bf2a76299b349a0cc91a67803d826858b35

        print(f"[DEBUG] User ID: {kakao_id}")
        print(f"[DEBUG] 닉네임: {username}")

        if not username:
            print("[ERROR] 카카오에서 닉네임을 가져오지 못했습니다.")

        existing_user = User.query.filter_by(kakao_id=kakao_id).first()

        if not existing_user:
            try:
                new_user = User(
                    kakao_id=kakao_id,
                    username=username,
                    email=None,
                    seed_krw=1000000.0,
                    seed_usd=0.0,
                    created_at=datetime.now(timezone.utc),
                    last_login=datetime.now(timezone.utc)
                )
                db.session.add(new_user)
                db.session.commit()
                user_to_store = new_user
                print(f"[DEBUG] 새로운 사용자 추가: ID={new_user.id}, 이름={username}")
            except Exception as e:
                db.session.rollback()
                print(f"[ERROR] 사용자 추가 중 오류 발생: {e}")
                return "사용자 저장 중 오류가 발생했습니다.", 500
        else:
            try:
                existing_user.last_login = datetime.now(timezone.utc)
                db.session.commit()
                user_to_store = existing_user
                print(f"[DEBUG] 기존 사용자 로그인: ID={existing_user.id}, 이름={username}")
            except Exception as e:
                db.session.rollback()
                print(f"[ERROR] 사용자 업데이트 중 오류 발생: {e}")
                return "사용자 업데이트 중 오류가 발생했습니다.", 500

        session.clear()
        session['user'] = {
<<<<<<< HEAD
            'id': user_to_store.id,
            'kakao_id': kakao_id,
            'username': username,
            'email': 'No email'
=======
            'id': kakao_id,
            'name': nickname,
            'email': email
>>>>>>> 17b07bf2a76299b349a0cc91a67803d826858b35
        }

        print("[DEBUG] 사용자 세션 저장:", session['user'])
        return redirect("/stock_kr")
    else:
        print("Access token 발급 실패:", response.json())
        return "Access token 발급 실패.", 500

@auth.route("/logout", methods=["GET"])
def logout():
    session.pop("user", None)
    session.pop("access_token", None)
    return redirect("/")

