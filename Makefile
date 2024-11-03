# Via https://github.com/aclark4life/project-makefile

EB_DJANGO_DATABASE_URL = $(shell eb ssh -c "source /opt/elasticbeanstalk/deployment/custom_env_var; env | grep DATABASE_URL" | awk -F= '{print $$2}')

EB_DJANGO_DATABASE_HOST = $(call EB_DJANGO_DATABASE,HOST)
EB_DJANGO_DATABASE_NAME = $(call EB_DJANGO_DATABASE,NAME)
EB_DJANGO_DATABASE_PASS = $(call EB_DJANGO_DATABASE,PASSWORD)
EB_DJANGO_DATABASE_USER = $(call EB_DJANGO_DATABASE,USER)

EB_DIR_NAME := .elasticbeanstalk
EB_ENV_NAME ?= $(PROJECT_NAME)-$(GIT_BRANCH)-$(GIT_REV)
EB_PLATFORM ?= "Python 3.11 running on 64bit Amazon Linux 2023"

EC2_INSTANCE_MAX ?= 1
EC2_INSTANCE_MIN ?= 1
EC2_INSTANCE_PROFILE ?= aws-elasticbeanstalk-ec2-role
EC2_INSTANCE_TYPE ?= t4g.small
EC2_LB_TYPE ?= application

define EB_DJANGO_DATABASE
    $(shell echo $(EB_DJANGO_DATABASE_URL) | python -c 'import dj_database_url; url = input(); url = dj_database_url.parse(url); print(url["$1"])')
endef

export EB_DJANGO_DATABASE
