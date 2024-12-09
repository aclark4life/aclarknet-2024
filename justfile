EC2_INSTANCE_MIN := "1"
EC2_INSTANCE_MAX := "1"
EC2_INSTANCE_PROFILE := "aws-elasticbeanstalk-ec2-role"
EC2_INSTANCE_TYPE := "t4g.small"
EB_SSH_KEY := "aclarknet"
EB_PLATFORM := "Python 3.12 running on 64bit Amazon Linux 2023"
EC2_LB_TYPE := "application"
VPC_ID := "vpc-9dc18be5"
VPC_SUBNET_EC2 := "subnet-7e1dae23,subnet-2333d62c"
VPC_SUBNET_ELB := "subnet-7e1dae23,subnet-2333d62c"
VPC_SG := "sg-0b545a7e,sg-0258ae68f8a5a1185"
GIT_BRANCH := `git rev-parse --abbrev-ref HEAD`
GIT_HASH := `git rev-parse --short HEAD`

default:
    echo 'Hello, world!'

[group("python")]
pip-install:
    pip install -e .
alias i := pip-install

[group("aclarknet")]
fix-lounge:
	eb ssh -c "sudo rm -rvf /var/app/current/lounge/node_modules"
	eb ssh -c "cd /var/app/current/lounge; sudo npm install"
	eb ssh -c "sudo cp /tmp/aclark.json /var/app/current/lounge/.thelounge/users/aclark.json"
	eb ssh -c "sudo systemctl restart lounge"

[group("django")]
django-open:
    open http://localhost:8000
alias o := django-open

[group("django")]
django-serve:
    python manage.py runserver
alias s := django-serve

[group("eb")]
eb-create:
    eb create "aclarknet-{{GIT_BRANCH}}-{{GIT_HASH}}" \
         -im {{EC2_INSTANCE_MIN}} \
         -ix {{EC2_INSTANCE_MAX}} \
         -ip {{EC2_INSTANCE_PROFILE}} \
         -i {{EC2_INSTANCE_TYPE}} \
         -k {{EB_SSH_KEY}} \
         -p "{{EB_PLATFORM}}" \
         --elb-type {{EC2_LB_TYPE}} \
         --vpc \
         --vpc.id {{VPC_ID}} \
         --vpc.elbpublic \
         --vpc.publicip \
         --vpc.ec2subnets {{VPC_SUBNET_EC2}} \
         --vpc.elbsubnets {{VPC_SUBNET_ELB}} \
         --vpc.securitygroups {{VPC_SG}}

[group("eb")]
eb-deploy:
    eb deploy
alias d := eb-deploy

[group("eb")]
eb-logs:
    eb logs
alias l := eb-logs

[group("ec2")]
sgs:
    aws ec2 describe-security-groups --output table

[group("ec2")]
vpc:
    aws ec2 describe-vpcs --output table

[group("ec2")]
sub:
    aws ec2 describe-subnets --output table
