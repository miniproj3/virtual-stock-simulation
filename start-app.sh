#!/bin/bash

# 퍼블릭 IP 가져오기
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
if [ -z "$PUBLIC_IP" ]; then
  echo "퍼블릭 IP를 가져오지 못했습니다."
  exit 1
fi
echo "PUBLIC_IP=$PUBLIC_IP" > .env

# RDS 설정
DB_HOST="testdb001.caruphjxuyij.ap-northeast-2.rds.amazonaws.com"
DB_NAME="testdb001"
DB_USER="admin001"
DB_PASS="admin001"

# .env 파일에 환경 변수 추가
{
  echo "DB_HOST=$DB_HOST"
  echo "DB_NAME=$DB_NAME"
  echo "DB_USER=$DB_USER"
  echo "DB_PASS=$DB_PASS"
  echo "SECRET_KEY=vss"
  echo "DATABASE_URL=mysql+pymysql://$DB_USER:$DB_PASS@$DB_HOST/$DB_NAME"
  echo "FLASK_ENV=production"
  echo "REDIS_HOST=redis"
  echo "REDIS_PORT=6379"
} >> .env

# .env 파일에서 환경 변수 로드
source .env

# Docker Compose 실행
docker-compose --env-file .env build
docker-compose --env-file .env up -d

# 그래프나 및 프로메테우스 URL 출력
echo "Grafana URL: http://$PUBLIC_IP:3000"
echo "Prometheus URL: http://$PUBLIC_IP:9090"
