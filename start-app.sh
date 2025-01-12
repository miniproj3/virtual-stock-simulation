#!/bin/bash

# 퍼블릭 IP/DNS 가져오기
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
echo "PUBLIC_IP=$PUBLIC_IP" > .env

# RDS 설정
DB_HOST="testdb001.caruphjxuyij.ap-northeast-2.rds.amazonaws.com"
DB_NAME="testdb001"
DB_USER="admin001"
DB_PASS="admin001"
echo "DB_HOST=$DB_HOST" >> .env
echo "DB_NAME=$DB_NAME" >> .env
echo "DB_USER=$DB_USER" >> .env
echo "DB_PASS=$DB_PASS" >> .env
echo "SECRET_KEY=vss" >> .env
echo "DATABASE_URL=mysql+pymysql://$DB_USER:$DB_PASS@$DB_HOST/$DB_NAME" >> .env
echo "FLASK_ENV=production" >> .env
echo "REDIS_HOST=redis" >> .env
echo "REDIS_PORT=6379" >> .env

# Docker Compose 빌드 및 실행
docker-compose --env-file .env build
docker-compose --env-file .env up -d
