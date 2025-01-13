# Lambda IAM 역할 정의
resource "aws_iam_role" "lambda_role" {
  name               = "lambda-execution-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

# IAM 역할 정책 문서 (Lambda가 이 역할을 맡을 수 있도록 설정)
data "aws_iam_policy_document" "assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

# Lambda 함수 정의
resource "aws_lambda_function" "lambda" {
  function_name    = "flask-app-handler"
  runtime          = var.runtime
  handler          = "lambda_function.lambda_handler"
  role             = aws_iam_role.lambda_role.arn
  source_code_hash = filebase64sha256("lambda.zip")
  filename         = "lambda.zip"

  environment {
    variables = {
      RDS_HOST     = var.rds_host   # 수정된 변수명
      RDS_USER     = var.rds_user
      RDS_PASSWORD = var.rds_password
      RDS_DB       = var.rds_db
    }
  }
}

# Lambda 기본 실행 정책 사용 (CloudWatch Logs에 대한 권한 포함)
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Lambda 함수가 RDS에 접근할 수 있도록 RDS 관련 권한 추가
resource "aws_iam_policy" "lambda_rds_policy" {
  name        = "lambda-rds-policy"
  description = "Policy to allow Lambda function access to RDS"
  policy      = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = [
          "rds:DescribeDBInstances",
          "rds:Connect"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

# Lambda IAM 역할에 RDS 권한 정책을 첨부
resource "aws_iam_role_policy_attachment" "lambda_rds_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_rds_policy.arn
}
