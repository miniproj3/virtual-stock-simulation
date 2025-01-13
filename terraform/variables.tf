variable "region" {
  description = "AWS region"
  default     = "ap-northeast-2"
}

variable "admin" {
  description = "RDS database username"
}

variable "testpass" {
  description = "RDS database password"
}

variable "vssDB" {
  description = "RDS instance name"
}

variable "rds_host" {
  description = "RDS endpoint"
}

variable "runtime" {
  description = "Lambda runtime environment"
}

variable "vsss3" {
  description = "Name of the S3 bucket"
  type        = string
}


variable "cidr_ingress_1" {
  description = "CIDR block for ingress rule 1"
  type        = string
}

variable "cidr_ingress_2" {
  description = "CIDR block for ingress rule 2"
  type        = string
}

variable "cidr_ingress_3" {
  description = "CIDR block for ingress rule 3"
  type        = string
}

variable "cidr_egress" {
  description = "CIDR block for egress rule"
  type        = string
}
