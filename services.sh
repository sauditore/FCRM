#!/usr/bin/env bash
export C_FORCE_ROOT="true"
redis-server &
if [! -d '/var/log/celery/'] ; then
    mkdir /var/log/celery/
    touch /var/log/celery/work
    touch /var/log/celery/beat
fi
celery -A Jobs worker -l debug --logfile=/var/log/celery/work &
celery -A Jobs beat -l error --logfile=/var/log/celery/beat &
memcached -p 1112 -u root -vvv &
echo "Services Started..."

