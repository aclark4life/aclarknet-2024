#!/bin/bash

#from https://aws.amazon.com/premiumsupport/knowledge-center/elastic-beanstalk-env-variables-linux2/

#Create a copy of the environment variable file.
cat /opt/elasticbeanstalk/deployment/env | perl -p -e 's/(.*)=(.*)/export $1="$2"/;' > /opt/elasticbeanstalk/deployment/custom_env_var

#Set permissions to the custom_env_var file so this file can be accessed by any user on the instance. You can restrict permissions as per your requirements.
chmod 644 /opt/elasticbeanstalk/deployment/custom_env_var

# add the virtual env path in. 
VENV=/var/app/venv/`ls /var/app/venv`
cat <<EOF >> /opt/elasticbeanstalk/deployment/custom_env_var
VENV=$VENV
EOF

#Remove duplicate files upon deployment.
rm -f /opt/elasticbeanstalk/deployment/*.bak
