default:
    just -l

d:
    eb deploy

e:
    nvim justfile

l: default

em:
    nvim Makefile

pg-dump:
    make pg-dump

pg-import:
    psql aclarknet < aclarknet.sql

pg-init:
    dropdb aclarknet
    createdb aclarknet

fix-lounge:
	eb ssh -c "sudo rm -rvf /var/app/current/lounge/node_modules"
	eb ssh -c "cd /var/app/current/lounge; sudo npm install"
	eb ssh -c "sudo cp /tmp/aclark.json /var/app/current/lounge/.thelounge/users/aclark.json"
	eb ssh -c "sudo systemctl restart lounge"
