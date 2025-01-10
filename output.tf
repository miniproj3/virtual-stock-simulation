output "tf_bastion_public_ip" {
  value       = aws_instance.tf_bastion.public_ip
  description = "tf_bastion_public_ip"
}

output "tf_web1_private_ip" {
  value       = aws_instance.tf_web[0].private_ip
  description = "tf_web1_private_ip"
}

output "tf_web2_private_ip" {
  value       = aws_instance.tf_web[1].private_ip
  description = "tf_web2_private_ip"
}

output "alb_dns_name" {
  value       = aws_lb.tf_alb.dns_name
  description = "alb_dns_name"
}

output "nlb_dns_name" {
  value       = aws_lb.tf_nlb.dns_name
  description = "nlb_dns_name"
}

output "rds_endpoint" {
  value       = aws_db_instance.tf_rds.endpoint
  description = "RDS endpoint to connect to the database"
}


output "db_name" {
  value = aws_db_instance.tf_rds.db_name
}

output "username" {
  value = aws_db_instance.tf_rds.username
}

# 비밀번호는 민감 정보이므로 출력하지 않거나 제한
# 아래 출력은 sensitive 설정으로 숨김 처리됩니다.
output "db_password" {
  value     = var.db_password
  sensitive = true
}
