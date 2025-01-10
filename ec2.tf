# Bastion EC2 Instance
resource "aws_instance" "tf_bastion" {
  ami             = "ami-0cdfea847ba37bca3" # Amazon Linux 2 AMI
  instance_type   = "t2.medium"
  key_name        = "stock-key-bastion"
  subnet_id       = aws_subnet.tf_sub_pub[0].id
  security_groups = [aws_security_group.tf_sg_bastion.id]
  tags = {
    Name = "tf_bastion"
  }
  user_data = templatefile("user-data-bastion.sh", {
    WEB1IP = aws_instance.tf_web[0].private_ip
    WEB2IP = aws_instance.tf_web[1].private_ip
  })
  user_data_replace_on_change = true
}

# Web EC2 Instances
resource "aws_instance" "tf_web" {
  count           = 2
  ami             = "ami-0cdfea847ba37bca3" # Amazon Linux 2 AMI
  instance_type   = "t2.medium"
  key_name        = "stock-key-bastion"
  subnet_id       = aws_subnet.tf_sub_pri[count.index].id
  security_groups = [aws_security_group.tf_sg_web.id]
  user_data = templatefile("user-data-web.sh", {
    NLB_DNS_NAME = aws_lb.tf_nlb.dns_name
  })
  user_data_replace_on_change = true

  tags = {
    Name = "tf_web${count.index + 1}"
  }
}

# WAS EC2 Instances
/*resource "aws_instance" "tf_was" {
  count           = 2
  ami             = "ami-0cdfea847ba37bca3" # Amazon Linux 2 AMI
  instance_type   = "t2.medium"
  key_name        = "stock-key-bastion"
  subnet_id       = aws_subnet.tf_sub_pri[count.index + 2].id
  security_groups = [aws_security_group.tf_sg_was.id]
  user_data = templatefile("user-data-was.sh", {
    INSTANCE_NAME = "tf_was${count.index + 1}"
  })
  user_data_replace_on_change = true
  tags = {
    Name = "tf_was${count.index + 1}"
  }
}*/

# 시작 템플릿으로 재구성 (WAS)
resource "aws_launch_template" "tf_st_was" {
  image_id = "ami-0cdfea847ba37bca3"
  instance_type = "t2.medium"
  # Auto Scaling Group 생성할 때, Subnet 선택 할 것 ! (시작 템플릿에서는 하나만 가능해서)
  vpc_security_group_ids = [aws_security_group.tf_sg_was.id]
  # Base64로 인코딩된 user_data
  user_data = base64encode(templatefile("user-data-was.sh", {
    RDS_ENDPOINT = aws_db_instance.tf_rds.endpoint,
    DB_NAME      = aws_db_instance.tf_rds.db_name,
    USERNAME     = aws_db_instance.tf_rds.username,
    PASSWORD     = var.db_password
  }))
  tags = {
    Name = "tf_st_was"
  }
}  
  resource "aws_autoscaling_group" "tf_auto_was" {
    launch_template {
      id = aws_launch_template.tf_st_was.id
    }
    
    target_group_arns = [aws_lb_target_group.tf_tg_was.arn]
    
    vpc_zone_identifier = [aws_subnet.tf_sub_pri[2].id, aws_subnet.tf_sub_pri[3].id]
    min_size = 3
    max_size = 6
    tag {
      key = "Name"
      value = "tf_auto_was"
      propagate_at_launch = true
    }
  }
  

