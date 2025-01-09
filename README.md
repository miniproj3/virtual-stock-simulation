# Terraform

### docker만 설치된 EC2 인스턴스를 AMI 이미지로 만들어서 terraform 이미지로 배포

AMI NAME: tf-web1-image-docker <br>
AMI ID : ami-0cdfea847ba37bca3

```bash
sudo yum update
sudo yum install docker -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user
```
<br>

### 생성된 VPC 리소스맵 확인

![image](https://github.com/user-attachments/assets/ec38ab20-b437-44e5-bfdb-70684e0a5c32)

![image](https://github.com/user-attachments/assets/77e42a9c-a62c-4398-8dc5-749b40b88fa5)
