#!/bin/bash

sudo pkill supervisord
sudo pkill gunicorn
sudo supervisord -c simple.conf