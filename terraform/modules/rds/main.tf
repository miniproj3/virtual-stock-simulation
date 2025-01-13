resource "aws_db_instance" "default" {
 identifier_prefix = "terraform-mysql"
 engine = "mysql"
 allocated_storage = 10
 instance_class = "db.t3.micro"
 skip_final_snapshot = true
 db_name = "vssdb"
 # How should we set the username and password?
 username = var.db_username
 password = var.db_password
}

resource "aws_db_instance" "read_replica" {
  depends_on           = [aws_db_instance.default]
  allocated_storage    = 20
  engine               = aws_db_instance.default.engine
  instance_class       = "db.t3.micro"
  username             = var.db_username
  password             = var.db_password

  publicly_accessible  = false
  replicate_source_db  = aws_db_instance.default.id
  vpc_security_group_ids = [module.security_group.security_group_id]
}
