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
    WAS1IP = aws_instance.tf_was[0].private_ip
    WAS2IP = aws_instance.tf_was[1].private_ip
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
resource "aws_instance" "tf_was" {
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
}
