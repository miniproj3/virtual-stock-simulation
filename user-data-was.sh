#!/bin/bash
yum update -y
yum install -y docker
systemctl start docker
systemctl enable docker

# 작업 디렉토리 생성 및 권한 설정
mkdir -p /home/ec2-user/wasapp
cd /home/ec2-user/wasapp
chown -R ec2-user:ec2-user /home/ec2-user/wasapp

# FastAPI 백엔드 앱 생성
cat << 'EOF' > app.py
from fastapi import FastAPI
import mysql.connector
import uvicorn
from pydantic import BaseModel

app = FastAPI()

class Data(BaseModel):
    name: str
    value: str

@app.post("/data")
async def save_data(data: Data):
    try:
        conn = mysql.connector.connect(
            host="${RDS_ENDPOINT}".split(':')[0],
            user="${USERNAME}",
            password="${PASSWORD}",
            database="${DB_NAME}"
        )
        cursor = conn.cursor()
        
        # 테이블이 없다면 생성
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255),
                value VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 데이터 삽입
        cursor.execute(
            "INSERT INTO user_data (name, value) VALUES (%s, %s)",
            (data.name, data.value)
        )
        conn.commit()
        
        return {"status": "success", "message": "Data saved successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
EOF

# Dockerfile 생성
cat << 'EOF' > Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY app.py /app/
RUN pip install fastapi uvicorn mysql-connector-python
CMD ["python", "app.py"]
EOF

# Docker 이미지 빌드 및 실행 (ec2-user 권한으로)
chown -R ec2-user:ec2-user .
docker build -t wasapp .
docker run -d --name wasapp -p 5000:5000 wasapp
