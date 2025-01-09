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
