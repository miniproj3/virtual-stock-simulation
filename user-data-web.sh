#!/bin/bash
# Update and install Docker
yum update -y
yum install -y docker
systemctl start docker
systemctl enable docker

# Create working directory for Web
mkdir -p /home/ec2-user/webapp
cd /home/ec2-user/webapp
chown -R ec2-user:ec2-user /home/ec2-user/webapp

# Create Nginx Dockerfile
cat << 'EOF' > Dockerfile
FROM nginx:latest
COPY default.conf /etc/nginx/conf.d/default.conf
EOF

# Create Nginx configuration
cat << EOF > default.conf
server {
    listen 8080;
    server_name localhost;

    location / {
        proxy_pass http://${NLB_DNS_NAME}:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Build and run Nginx container
docker build -t web-nginx .
docker run -d --name web-nginx -p 8080:8080 web-nginx # Host 8080 → Container 9090

