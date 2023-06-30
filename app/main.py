import os
import sys
import logging
import yaml
import time
import signal

from cm import Supervisor, InternetChecker
from at import Poller
from webserver import Webserver

# Set up signal handlers
def signal_handler(sig, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Set up the logging subsystem
logger = logging.getLogger()
logger.setLevel(logging.INFO)
stdout_handler = logging.StreamHandler(sys.stderr)
stdout_handler.setFormatter(logging.Formatter('<%(levelname)s> %(name)s: %(message)s'))
logger.addHandler(stdout_handler)

# Make sure that npm install has been run
node_modules_path = os.path.join(os.path.dirname(__file__), 'webserver', 'static', 'node_modules')
if not os.path.exists(node_modules_path):
    logging.error("The node_modules directory does not exist. Please run 'npm install' in the webserver/static directory.")
    exit(1)

# Read configuration
config_path = os.path.dirname(__file__) + '/config.yml'
if not os.path.exists(config_path):
    raise IOError("The configuration file - %s - could not be found." % config_path)

config = {}
with open(config_path, 'r') as ymlfile:
    config = yaml.load(ymlfile, Loader=yaml.SafeLoader)
    logger.info("Loaded %d configuration items from %s" % (len(config), config_path))

# Create the AT command poller
at_poller = Poller(
    config['at']['dev'],
    config['at']['poll_delay'],
    config['at']['statsd'] if 'statsd' in config['at'] else None
)
at_poller.start()

# Create the internet connection checker
ip_checker = InternetChecker()

# Create the supervisor instance
cm_supervisor = Supervisor(
    #config['cm']['path'],
    #config['cm']['respawn_delay'],
    #config['cm']['apn'],
    #config['cm']['log_lines'],
    at_poller,
    ip_checker
)
cm_supervisor.start()

# Create the webserver
server = Webserver(config['web']['port'], at_poller, cm_supervisor, ip_checker)

# Start the server
server.start_server()

# Keep the main thread alive in case the web server was configured not to start
while cm_supervisor.is_supervising:
    time.sleep(1)
