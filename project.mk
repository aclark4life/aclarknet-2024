PROJECT_NAME := aclarknet

db-init-hstore:
	psql $(PROJECT_NAME) -c 'CREATE EXTENSION IF NOT EXISTS hstore;'
	psql test_$(PROJECT_NAME) -c 'CREATE EXTENSION IF NOT EXISTS hstore;'

db-init: db-pg-init-default db-pg-init-test-default db-init-hstore

