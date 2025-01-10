#!/bin/bash
yum update -y
yum install -y docker
systemctl start docker
systemctl enable docker

# 작업 디렉토리 생성 및 권한 설정
mkdir -p /home/ec2-user/webapp
cd /home/ec2-user/webapp
chown -R ec2-user:ec2-user /home/ec2-user/webapp

# FastAPI 프론트엔드 앱 생성
cat << 'EOF' > app.py
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import httpx
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/submit")
async def submit_data(name: str = Form(...), value: str = Form(...)):
    # NLB를 통해 WAS로 데이터 전송 (8080 포트 사용)
    async with httpx.AsyncClient() as client:
        response = await client.post(f'http://${NLB_DNS_NAME}:8080/data', 
                                   json={"name": name, "value": value})
    return response.json()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
EOF

mkdir -p templates
cat << 'EOF' > templates/index.html
<!DOCTYPE html>
<html>
<head>
    <title>Data Input</title>
</head>
<body>
    <h1>Enter Data</h1>
    <form action="/submit" method="post">
        <p>Name: <input type="text" name="name"></p>
        <p>Value: <input type="text" name="value"></p>
        <input type="submit" value="Submit">
    </form>
</body>
</html>
EOF

# Dockerfile 생성
cat << 'EOF' > Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY app.py /app/
COPY templates /app/templates
RUN pip install fastapi uvicorn jinja2 python-multipart httpx
CMD ["python", "app.py"]
EOF

# Docker 이미지 빌드 및 실행 (ec2-user 권한으로)
chown -R ec2-user:ec2-user .
docker build -t webapp .
docker run -d --name webapp -p 8080:8080 webapp
