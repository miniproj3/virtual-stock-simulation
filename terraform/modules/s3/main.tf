resource "aws_s3_bucket" "bucket" {
  bucket = var.vsss3
}

output "bucket_name" {
  value = aws_s3_bucket.bucket.id
}