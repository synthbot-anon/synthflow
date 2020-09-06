#!/bin/bash

# set up postgres installation
echo "deb http://apt.postgresql.org/pub/repos/apt $(cat /etc/os-release | grep 'VERSION_CODENAME' | cut -d '=' -f2)-pgdg main" > /etc/apt/sources.list.d/pgdg.list
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
