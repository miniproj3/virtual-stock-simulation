# VPC 생성
resource "aws_vpc" "tf_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = false
  tags = {
    Name = "tf_vpc"
  }
}

# 퍼블릭 서브넷 생성 (Bastion, NAT)
resource "aws_subnet" "tf_sub_pub" {
  count                   = 2
  vpc_id                  = aws_vpc.tf_vpc.id
  availability_zone       = ["us-east-2a", "us-east-2c"][count.index]
  cidr_block              = ["10.0.10.0/24", "10.0.20.0/24"][count.index]
  map_public_ip_on_launch = true
  tags = {
    Name = "${count.index == 0 ? "tf_sub_bastion" : "tf_sub_nat"}"
  }
}

# 프라이빗 서브넷 생성 (Web, WAS, DB)
resource "aws_subnet" "tf_sub_pri" {
  count                   = 6
  vpc_id                  = aws_vpc.tf_vpc.id
  availability_zone       = ["us-east-2a", "us-east-2c", "us-east-2a", "us-east-2c", "us-east-2a", "us-east-2c"][count.index]
  cidr_block              = ["10.0.11.0/24", "10.0.21.0/24", "10.0.12.0/24", "10.0.22.0/24", "10.0.13.0/24", "10.0.23.0/24"][count.index]
  map_public_ip_on_launch = false
  tags = {
    Name = [
      "tf_sub_web1",
      "tf_sub_web2",
      "tf_sub_was1",
      "tf_sub_was2",
      "tf_sub_db1",
      "tf_sub_db2"
    ][count.index]
  }
}

# 인터넷 게이트웨이 생성
resource "aws_internet_gateway" "tf_igw" {
  vpc_id = aws_vpc.tf_vpc.id
  tags = {
    Name = "tf_igw"
  }
}

# NAT 게이트웨이 용 EIP 생성
resource "aws_eip" "tf_eip" {
  #vpc = true
  tags = {
    Name = "tf_eip"
  }
}

# NAT 게이트웨이 생성
resource "aws_nat_gateway" "tf_nat" {
  allocation_id = aws_eip.tf_eip.id
  subnet_id     = aws_subnet.tf_sub_pub[1].id
  tags = {
    Name = "tf_nat"
  }
}

# 퍼블릭 라우팅테이블 생성
resource "aws_route_table" "tf_rtb_pub" {
  vpc_id = aws_vpc.tf_vpc.id
  tags = {
    Name = "tf_rtb_pub"
  }
}

# 퍼블릭 라우팅 테이블에 IGW 연결
resource "aws_route" "public_route" {
  route_table_id         = aws_route_table.tf_rtb_pub.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.tf_igw.id
}

# 퍼블릭 서브넷과 라우팅 테이블 연결
resource "aws_route_table_association" "public_rtb_association" {
  count          = 2
  subnet_id      = aws_subnet.tf_sub_pub[count.index].id
  route_table_id = aws_route_table.tf_rtb_pub.id
}

# 프라이빗 라우팅 테이블 생성
resource "aws_route_table" "tf_rtb_pri" {
  vpc_id = aws_vpc.tf_vpc.id
  tags = {
    Name = "tf_rtb_pri"
  }
}

# 프라이빗 라우팅 테이블에 NAT 연결
resource "aws_route" "private_route" {
  route_table_id         = aws_route_table.tf_rtb_pri.id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.tf_nat.id
}

# 프라이빗 서브넷과 라우팅 테이블 연결
resource "aws_route_table_association" "private_rtb_association" {
  count          = 6
  subnet_id      = aws_subnet.tf_sub_pri[count.index].id
  route_table_id = aws_route_table.tf_rtb_pri.id
}

# RDS용 서브넷 그룹
resource "aws_db_subnet_group" "tf_sub_group_db"{
  subnet_ids = [aws_subnet.tf_sub_pri[4].id, aws_subnet.tf_sub_pri[5].id]
  tags = {
    Name = "tf_sub_group_db"
  }
}
