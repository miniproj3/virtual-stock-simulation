resource "aws_db_instance" "tf_rds" {
  allocated_storage    = 200  # 스토리지 크기 (GB)
  engine               = "mysql"
  engine_version       = "5.7.44"
  instance_class       = "db.m5.large"  # RDS 인스턴스 
  db_name              = "tf_stocktestdb"  # 초기  데이터베이스 이름
  username             = "admin"  # 마스터 사용자 이름
  password             = var.db_password
  publicly_accessible  = false  # 퍼블릭 IP 비활성화
  multi_az             = true # 단일 AZ 설정 (true로 설정 시 다중 AZ)
  skip_final_snapshot  = true
  vpc_security_group_ids = [aws_security_group.tf_sg_rds.id]
  db_subnet_group_name = aws_db_subnet_group.tf_sub_group_db.id  # RDS 서브넷 그룹
  tags = {
    Name = "tf_rds"
  }
}

