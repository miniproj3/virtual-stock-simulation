provider "aws" {
  region = var.region
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "3.0.0"
  name = "my-vpc"
  cidr = "172.16.0.0/16"
  azs             = ["ap-northeast-2a", "ap-northeast-2b"]
  private_subnets = ["172.16.11.0/24", "172.16.21.0/24", "172.16.12.0/24", "172.16.22.0/24"]
  public_subnets  = ["172.16.10.0/24", "172.16.20.0/24"]
  enable_nat_gateway = true
  single_nat_gateway = true
}

module "security_group" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "4.0.0"
  name        = "allow-lambda-rds-access"
  description = "Security group for allowing access to RDS from Lambda"
  vpc_id      = module.vpc.vpc_id
  ingress_with_cidr_blocks = [
    {
      from_port   = 22
      to_port     = 22
      protocol    = "tcp"
      cidr_blocks = var.cidr_ingress_1
    },
    {
      from_port   = 80
      to_port     = 80
      protocol    = "tcp"
      cidr_blocks = var.cidr_ingress_2
    },
    {
      from_port   = 8080
      to_port     = 8080
      protocol    = "tcp"
      cidr_blocks = "0.0.0.0/0"  # 문자열 값으로 수정
    },
    {
      from_port   = 443
      to_port     = 443
      protocol    = "tcp"
      cidr_blocks = "0.0.0.0/0"  # 문자열 값으로 수정
    }
  ]
  egress_with_cidr_blocks = [
    {
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      cidr_blocks = var.cidr_egress
    }
  ]
}


module "s3" {
  source = "./modules/s3"
  bucket_name  = var.bucket_name
}


module "rds" {
  source      = "./modules/rds"
  db_name       = var.db_name
  db_username       = var.db_username
  db_password    = var.db_password
  runtime     = var.runtime
}

resource "aws_instance" "bastion" {
  ami             = "ami-06a52a9e45eb70209"
  instance_type   = "t3.micro"
  subnet_id       = module.vpc.public_subnets[0]
  key_name        = var.key_pair
  security_groups = [module.security_group.security_group_id]
}

resource "aws_lb" "stock-alb" {
  name               = "stock-alb"
  security_groups    = [module.security_group.security_group_id]
  subnets            = module.vpc.public_subnets
  internal           = false
  load_balancer_type = "application"
}

resource "aws_lb" "stock-nlb" {
  name               = "stock-nlb"
  security_groups    = [module.security_group.security_group_id]
  subnets            = module.vpc.public_subnets
  internal           = true
  load_balancer_type = "network"
}

resource "aws_lb_listener" "app_listener" {
  load_balancer_arn = aws_lb.stock-alb.arn
  port              = 80
  protocol          = "HTTP"
  default_action {
    type             = "fixed-response"
    fixed_response {
      content_type  = "text/plain"
      message_body  = "Under Maintenance."
      status_code   = "503"
    }
  }
}

resource "aws_lb_listener" "network_listener" {
  load_balancer_arn = aws_lb.stock-nlb.arn
  port              = 8080
  protocol          = "TCP"
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.tg.arn
  }
}

resource "aws_lb_target_group" "tg" {
  name     = "stock-tg"
  port     = 8080
  protocol = "HTTP"
  vpc_id   = module.vpc.vpc_id
}
