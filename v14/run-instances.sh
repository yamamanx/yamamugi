aws ec2 run-instances --image-id ami-048f6ed62451373d9 --instance-type t3.micro --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=CLI}]'
