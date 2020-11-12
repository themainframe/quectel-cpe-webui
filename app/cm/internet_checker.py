import time
import datetime
import logging
import threading
import socket

logger = logging.getLogger(__name__)

class InternetChecker:
    """
    Checks to see if we have IPv4 capability.
    Spawns a thread that periodically checks Internet connectivity and updates the instance.
    """

    def __init__(self, poll_delay=30000, max_failures=3):
        """
        Create a new InternetChecker
        """

        # The delay in ms between polls
        self.poll_delay = poll_delay

        # Are we polling periodically?
        self.is_polling = False

        # Maximum allowed failures before we mark as no-internet
        self.max_failures = max_failures

        # Failure count
        self.failures = 0

        # The thread on which the serial port sending will be performed
        self.__poll_thread = threading.Thread(target=self.__poll)
        self.__poll_thread.daemon = True

    def start(self):
        """
        Start polling
        """
        logger.info("Starting Internet Connectivity Monitoring")
        self.is_polling = True
        self.__poll_thread.start()

    def stop(self):
        """
        Stop polling
        """
        logger.info("Stopping Internet Connectivity Monitoring")
        self.is_polling = False

    def reset(self):
        """
        Reset the failure count.
        """
        if self.failures > 0:
            logger.info("Failure count reset to 0 - was %d" % self.failures)
            self.failures = 0

    def has_internet(self):
        """
        Indicate whether we have internet or not.
        """
        return self.failures < self.max_failures

    @staticmethod
    def __internet_on(host='8.8.8.8', port=53, timeout=3):
        """
        Poll a host to see if we have an internet connection.
        By default polls Google Public DNS on port 53 (dns).
        """
        try:
            socket.setdefaulttimeout(timeout)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
            sock.close()
            logger.info("Internet connectivity OK.")
            return True
        except socket.error as ex:
            logger.warn("Internet checker fault: %s" % ex)
            return False

    def __poll(self):
        """
        The main poll loop.
        """
        self.is_polling = True
        self.failures = 0

        # While we've not been terminated
        while self.is_polling:

            # Wait a while before opening
            time.sleep(self.poll_delay / 1000)

            try:
                if not InternetChecker.__internet_on():
                    self.failures += 1
                    logger.warn("No internet connectivity - %d consecutive failures now" % self.failures)
                else:
                    if self.failures > 0:
                        logger.info("Connectivity Restored - resetting failure count to 0 (was %d)" % self.failures)
                        self.failures = 0

            except Exception as ic_check_err:
                logger.error("Internet connectivity check error: %s" % ic_check_err)
                continue

