#!/bin/bash

set -ueo pipefail

echo "Building and migrating..."
echo
sudo -p "local sudo password for docker: " docker compose --profile \
     first-run up --build --abort-on-container-exit
echo
echo "Creating local super user"
echo
sudo -p "local sudo password for docker: " docker compose run django \
     python manage.py createsuperuser
echo     
echo "You must still add your user to the group \"Primaire Secretaris\""
echo "manually via django-admin at http://localhost:8000/admin "
echo
echo "Press enter to start container, or ctrl-C to exit."
read enter
sudo -p "local root password for docker: " docker compose --profile default up --remove-orphans --force-recreate
