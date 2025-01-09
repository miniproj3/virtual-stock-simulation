#!/bin/bash
docker pull nginx
docker run -d --name nginx -p 8080:1111 nginx

docker exec nginx bash -c "apt update && apt install vim -y"
echo "server {
    listen       1111;
    listen  [::]:1111;
    server_name  localhost;

    location / {
        proxy_pass http://${NLB_DNS_NAME}:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}" > default.conf

docker cp /default.conf nginx:/etc/nginx/conf.d/default.conf
docker restart nginx
