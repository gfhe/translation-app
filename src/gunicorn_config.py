import multiprocessing
import datetime

workers = 2
#workers = multiprocessing.cpu_count() * 2 + 1
bind = '0.0.0.0:7000'
daemon = False
backlog = 2048
timeout = 500
keepalive = 2
worker_connections = 1000
#worker_class = "gevent"
pidfile = './logs/gunicorn.pid'
loglevel = 'debug'
accesslog = './logs/access_'+datetime.datetime.now().strftime("%Y-%m-%d")+'.log'
errorlog = "logs/debug_"+datetime.datetime.now().strftime("%Y-%m-%d")+".log"