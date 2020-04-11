#!/bin/bash

# This script brings up the container and shuts it down on receiving a ctrl-c kill signal.

function usage() {
  echo "usage: bash $0 [clean]"
  echo "clean: this flag causes the script to delete any existing version of the image and rebuild it"
}

# ctrl-c is used to abort a running container session. To keep the session self-contained by this script,
# we will capture the ctrl-c SIGINT signal and use it to call docker-compose down.
# That way, we do not have behavior where the script calls docker-compose up, but we have to remember
# to call docker-compose down separately.
function trap_ctrlc() {
  sudo docker-compose down
  exit 0
}
trap "trap_ctrlc" 2

# accept an argument of "clean", but nothing else
if [[ $1 == "clean" ]]; then
  sudo rm -rf pgdata
  sudo docker image rm flask-server:v1
elif [[ $1 != "" ]]; then
  usage
  exit 0
fi

# if the image doesn't exist (or we've just deleted it), build it fresh
sudo docker image inspect flask-server:v1 >/dev/null 2>&1
[[ $? != 0 ]] && echo "Image does not exist; building image" && sudo docker build -t flask-server:v1 .

# bring up the container
sudo docker-compose up
