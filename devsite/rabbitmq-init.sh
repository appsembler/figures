#!/bin/sh
#
# Run this script from within the RabbitMQ docker container

rabbitmqctl add_user figures_user figures_pwd
rabbitmqctl add_vhost figures_vhost
rabbitmqctl set_user_tags figures_user figures_tag
rabbitmqctl set_permissions -p figures_vhost figures_user ".*" ".*" ".*"
