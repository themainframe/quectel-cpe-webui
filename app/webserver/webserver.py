import logging
from flask import Flask
from .routes import Home

logger = logging.getLogger(__name__)

class Webserver:
    """
    Provides a web console for viewing CPE information.
    """

    def __init__(self, port, at_poller, cm_supervisor, ip_checker):
        """
        Create a new webserver.
        """

        # Provide the AT poller & supervisor objects to routes that need it
        self.port = port
        Home.ip_checker = ip_checker
        Home.at_poller = at_poller
        Home.cm_supervisor = cm_supervisor
        
        # The WSGI app
        self.app = None

    def start_server(self):
        """
        Start the web server.
        """
        self.app = Flask(__name__, template_folder='templates/')    
        self.app.config["SECRET_KEY"] = "appkey"
        self.app.jinja_env.add_extension('jinja2.ext.loopcontrols')
        self.app.register_blueprint(Home.blueprint, url_prefix='/')

        # Disable excessive logging
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

        # Start the server
        self.app.run(host='0.0.0.0', port=self.port)

