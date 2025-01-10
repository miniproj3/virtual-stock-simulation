#!/bin/bash

echo 'alias web1in="ssh -i ~/stock-key-bastion.pem ec2-user@${WEB1IP}"' >> /home/ec2-user/.bashrc
echo 'alias web2in="ssh -i ~/stock-key-bastion.pem ec2-user@${WEB2IP}"' >> /home/ec2-user/.bashrc

source /home/ec2-user/.bashrc
