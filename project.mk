# Custom Makefile
# Add your custom makefile commands here
#
PROJECT_NAME := aclarknet

db-init-hstore:
	psql $(PROJECT_NAME) -c 'CREATE EXTENSION IF NOT EXISTS hstore;'
	psql test_$(PROJECT_NAME) -c 'CREATE EXTENSION IF NOT EXISTS hstore;'

db-init: db-init-default db-init-hstore

install:
	$(MAKE) pip-install
	cd frontend; npm install

serve:
	cd frontend; npm run watch &
	python manage.py runserver 0.0.0.0:8000

fix-lounge:
	eb ssh -c "sudo rm -rvf /var/app/current/lounge/node_modules"
	eb ssh -c "cd /var/app/current/lounge; sudo npm install"
	eb ssh -c "sudo cp /tmp/aclark.json /var/app/current/lounge/.thelounge/users/aclark.json"
	eb ssh -c "sudo systemctl restart lounge"
