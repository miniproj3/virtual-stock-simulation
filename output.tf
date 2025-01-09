output "tf_bastion_public_ip" {
  value       = aws_instance.tf_bastion.public_ip
  description = "tf_bastion_public_ip"
}

output "alb_dns_name" {
  value       = aws_lb.tf_alb.dns_name
  description = "alb_dns_name"
}

output "nlb_dns_name" {
  value       = aws_lb.tf_nlb.dns_name
  description = "nlb_dns_name"
}
