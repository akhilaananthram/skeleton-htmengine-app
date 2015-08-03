#!/bin/bash

mysql.server start
mysql -u root --execute="CREATE DATABASE thebigone"
rabbitmq-server -detached
export APPLICATION_CONFIG_PATH="/Users/aanantham/Documents/skeleton-htmengine-app/conf"
supervisord -c conf/supervisord.conf
