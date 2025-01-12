# Application Load Balancer (ALB)
resource "aws_lb" "tf_alb" {
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.tf_sg_alb.id]
  subnets            = [aws_subnet.tf_sub_pub[0].id, aws_subnet.tf_sub_pub[1].id]
  
  tags = {
    Name = "tf_alb"
  }
}

# ALB Listener
resource "aws_lb_listener" "tf_alb_listener" {
  load_balancer_arn = aws_lb.tf_alb.arn
  port              = 80
  protocol          = "HTTP"
  
  default_action {
    type = "forward"
    target_group_arn = aws_lb_target_group.tf_tg_web.arn
  }
}

# ALB Target Group for Web Instances
resource "aws_lb_target_group" "tf_tg_web" {
  port     = 8080
  protocol = "HTTP"
  vpc_id   = aws_vpc.tf_vpc.id
  
  health_check {
    path                = "/"
    protocol            = "HTTP"
    matcher             = "200"
    interval            = 15
    timeout             = 3
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }
  tags = {
    Name = "tf_tg_web"
  }
}

# Network Load Balancer (NLB)
resource "aws_lb" "tf_nlb" {
  internal           = true
  load_balancer_type = "network"
  security_groups    = [aws_security_group.tf_sg_nlb.id]
  subnets            = [aws_subnet.tf_sub_pri[2].id, aws_subnet.tf_sub_pri[3].id]
  tags = {
    Name = "tf_nlb"
  }
}

# NLB Listener
resource "aws_lb_listener" "tf_nlb_listener" {
  load_balancer_arn = aws_lb.tf_nlb.arn
  port              = 8080
  protocol          = "TCP"
  default_action {
    type = "forward"
    target_group_arn = aws_lb_target_group.tf_tg_was.arn
  }
}

# NLB Target Group for WAS Instances
resource "aws_lb_target_group" "tf_tg_was" {
  port     = 5000
  protocol = "TCP"
  vpc_id   = aws_vpc.tf_vpc.id
  health_check {
    protocol            = "TCP"
    interval            = 15
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }
  tags = {
    Name = "tf_tg_was"
  }
}

