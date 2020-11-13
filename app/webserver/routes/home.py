import json
import logging
from at.command import ResultValueState
from flask import Blueprint, render_template, request

logger = logging.getLogger(__name__)

class Home:
    """
    Route class for the Home page.
    """

    blueprint = Blueprint('home', __name__)
    at_poller = None
    cm_supervisor = None
    ip_checker = None

    @staticmethod
    def __bulma_class(state):
        """
        Get the Bulma class name for a given result state
        """
        if state == ResultValueState.OK:
            return 'has-background-success-light'
        elif state == ResultValueState.WARNING:
            return 'has-background-warning-light'
        elif state == ResultValueState.ERROR:
            return 'has-background-danger-light'
        else:
            return 'has-background-grey-lighter'

    @staticmethod
    @blueprint.route('/')
    def index():
        return render_template(
            'home.j2',
            commands=Home.at_poller.commands,
            bulma_class=Home.__bulma_class,
            supervisor=Home.cm_supervisor,
            ip_checker=Home.ip_checker
        )

    @staticmethod
    @blueprint.route('/cmlog')
    def cmlog():
        return render_template(
            'cmlog.j2',
            cm_log="\r\n".join(Home.cm_supervisor.log)
        )

    @staticmethod
    @blueprint.route('/restart')
    def restart():
        Home.cm_supervisor.restart()
        return render_template(
            'restart.j2'
        )