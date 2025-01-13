terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  required_version = ">= 1.3.0"

  backend "s3" {
    bucket         = "vss-tfstate-bucket"
    key            = "admin/tfstate/key"
    region         = "ap-northeast-2"
    encrypt        = true
    dynamodb_table = "vss-state-lock-table"
  }
}
