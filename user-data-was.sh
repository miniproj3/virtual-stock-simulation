#!/bin/bash
#
docker pull nginx
docker run -d --name nginx -p 5000:2222 nginx

docker exec nginx bash -c "apt update && apt install vim -y"
docker exec nginx bash -c "echo '${INSTANCE_NAME}' > /usr/share/nginx/html/index.html"
docker exec nginx bash -c "cat <<EOL > /etc/nginx/conf.d/default.conf
server {
    listen       2222;
    listen  [::]:2222;
    server_name  localhost;

    location / {
        root   /usr/share/nginx/html;
        index  index.html index.htm;
    }

    error_page   500 502 503 504  /50x.html;
    location = /50x.html {
        root   /usr/share/nginx/html;
    }
}
EOL
    "
docker restart nginx
