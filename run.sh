#!/bin/bash

function load_env_file()
{
	if [ -f "bot.env" ]
	then
		set -a
		source "bot.env"
		set +a
	else
		echo "WARNING: NO ENV FILE"
	fi
}

function setup_web()
{
	if [ -z $PORT ]
	then
		echo "WARNING: missing PORT env var"
		return 0
	fi
	which apache2
	if [ $? -eq 0 ]
	then
		# PORT env var goes here!
		sed -i "s/Listen 80/Listen $PORT/" /etc/apache2/ports.conf
		cp -va index.html /var/www/html/
		/etc/init.d/apache2 start
		return 0
	fi
	echo "WARNING: apache2 is not installed"
	return 0
}

load_env_file

setup_web

echo "RUNNING MAIN SCRIPT..."

python3 main.py
