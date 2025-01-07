from flask import Flask, session, redirect, request, render_template
import requests

app = Flask(__name__)
app.secret_key='1234'

auth_bp = Blueprint('auth', __name__)

@app.route("/auth", methods=["GET"])
def kakaologin():
    access_token = session.get("access_token")

    if access_token:
        account_info = requests.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {access_token}"}
        ).json()

    return render_template("auth.html")


@app.route("/kakaoLoginLogic", methods=["GET"])
def kakaoLoginLogic():
    url = (
        f"https://kauth.kakao.com/oauth/authorize"
        f"?client_id={REST_API_KEY}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
    )
    return redirect(url)

# 카카오 로그인 리다이렉트 처리
@app.route("/kakaoLoginLogicRedirect", methods=["GET"])
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

        # 카카오 사용자 정보에 'properties'와 'kakao_account'가 존재하는지 확인
        if 'properties' in kakao_user_info and 'nickname' in kakao_user_info['properties']:
            nickname = kakao_user_info['properties']['nickname']
        else:
            nickname = "No nickname"

        email = kakao_user_info.get('kakao_account', {}).get('email', 'No email')
        
        # 사용자 정보를 세션에 저장
        session['user'] = {
            'id': kakao_user_info['id'],
            'name': nickname,
            'email': email
        }

        return redirect("/home")  # 로그인 성공 후 홈으로 리다이렉트
    else:
        print("Access token 발급 실패:", response.json())
        return "Access token 발급 실패.", 500