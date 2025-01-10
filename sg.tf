# Bastion Host Security Group
resource "aws_security_group" "tf_sg_bastion" {
  description = "Allow SSH access to bastion host"
  vpc_id      = aws_vpc.tf_vpc.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "tf_sg_bastion"
  }
}

# Web Security Group
resource "aws_security_group" "tf_sg_web" {
  description = "Allow traffic from ALB to web servers"
  vpc_id      = aws_vpc.tf_vpc.id

  ingress {
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    #cidr_blocks = ["10.0.10.0/24","10.0.20.0/24"]
    security_groups = [aws_security_group.tf_sg_alb.id] 
  }

  ingress {
    from_port       = 22
    to_port         = 22
    protocol        = "tcp"
    security_groups = [aws_security_group.tf_sg_bastion.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "tf_sg_web"
  }
}

# WAS Security Group
resource "aws_security_group" "tf_sg_was" {
  description = "Allow traffic from NLB to WAS servers"
  vpc_id      = aws_vpc.tf_vpc.id

  ingress {
    from_port       = 5000
    to_port         = 5000
    protocol        = "tcp"
    #cidr_blocks = ["10.0.11.0/24", "10.0.21.0/24"]
    security_groups = [aws_security_group.tf_sg_nlb.id]
 }
  ingress {
    from_port       = 22
    to_port         = 22
    protocol        = "tcp"
    security_groups = [aws_security_group.tf_sg_bastion.id]
  }

  ingress {
    from_port       = 5000
    to_port         = 5000
    protocol        = "tcp"
    security_groups = [aws_security_group.tf_sg_web.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "tf_sg_was"
  }
}

# ALB Security Group
resource "aws_security_group" "tf_sg_alb" {
  description = "Allow HTTP traffic to ALB"
  vpc_id      = aws_vpc.tf_vpc.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "tf_sg_alb"
  }
}

# NLB Security Group
resource "aws_security_group" "tf_sg_nlb" {
  description = "Allow traffic from Web to NLB"
  vpc_id      = aws_vpc.tf_vpc.id

  ingress {
    from_port       = 0
    to_port         = 65535
    protocol        = "tcp"
    security_groups = [aws_security_group.tf_sg_web.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "tf_sg_nlb"
  }
}

# RDS Security Group
resource "aws_security_group" "tf_sg_rds" {
  vpc_id = aws_vpc.tf_vpc.id

  ingress {
    from_port       = 3306 
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.tf_sg_was.id] 
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "tf_sg_rds"
  }
}

