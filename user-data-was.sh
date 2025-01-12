#!/bin/bash
# 필수 패키지 설치 및 서비스 활성화
yum update -y
yum install -y docker redis
systemctl start docker
systemctl enable docker
sudo yum install git -y
sudo amazon-linux-extras enable epel
sudo amazon-linux-extras enable redis6
sudo yum install -y redis
sudo systemctl start redis
sudo systemctl enable redis


# WAS 작업 디렉토리 생성 및 Git 클론
mkdir -p /home/ec2-user/wasapp
cd /home/ec2-user/wasapp
chown -R ec2-user:ec2-user /home/ec2-user/wasapp
git clone -b 0112 https://github.com/miniproj3/virtual-stock-simulation.git
cd virtual-stock-simulation

# 환경 변수 파일 생성
cat << EOF > .env
RDS_ENDPOINT="${RDS_ENDPOINT}"
DB_NAME="${DB_NAME}"
DB_USERNAME="${USERNAME}"
DB_PASSWORD="${PASSWORD}"
NLB_DNS_NAME="${NLB_DNS_NAME}"
DATABASE_URL="mysql+pymysql://${USERNAME}:${PASSWORD}@${RDS_ENDPOINT}/${DB_NAME}"
REDIRECT_URI="http://${ALB_DNS_NAME}/auth/kakaoLoginLogicRedirect"
EOF

#Kafka 설정 파일 수정 (localhost -> NLB_DNS_NAME)
sed -i "s/localhost/${NLB_DNS_NAME}/g" kafka/docker-compose.yml
sed -i "s/localhost:9092/${NLB_DNS_NAME}:9092/g" kafka/kafka_config.py

# Kafka Docker Compose 실행
cd kafka
docker-compose up -d
cd ..

# Gunicorn Flask 애플리케이션을 위한 Dockerfile 생성
cat << 'EOF' > Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . .

RUN apt-get update && apt-get install -y python3-pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:app"]
EOF

# Flask 애플리케이션 Docker 컨테이너 빌드 및 실행
docker build -t was-flask .
docker run -d --name was-flask -p 5000:5000 --env-file .env was-flask

