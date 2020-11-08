import time
import datetime
import logging
import threading
import subprocess
from os import path, system
from subprocess import Popen, PIPE
from nbsr import NonBlockingStreamReader

logger = logging.getLogger(__name__)

class Supervisor:
    """
    Supervises Quectel_CM.
    Keeps it alive & collects an output buffer.
    """

    def __init__(self, path, respawn_delay, apn, log_lines):
        """
        Create a new supervisor.
        """

        # The path to the quectel_CM binary
        self.path = path

        # The delay in ms between respawns if quectel_CM dies
        self.respawn_delay = respawn_delay

        # The APN details
        self.apn = apn

        # The number of log lines to buffer up
        self.log_lines = log_lines

        # Is quectel_CM being supervised? 
        self.is_supervising = False

        # The log buffer
        self.log = []

        # QCM Popen handle
        self.qcm_handle = None

        # The thread on which the supervision will be done
        self.__supervise_thread = threading.Thread(target=self.__supervise)
        self.__supervise_thread.daemon = True

    def start(self):
        """
        Start quectel_CM
        """
        logger.info("Starting supervision of quectel_CM @ %s" % self.path)
        self.is_supervising = True
        self.__supervise_thread.start()

    def stop(self):
        """
        Stop quectel_CM
        """
        self.is_supervising = False

    def restart(self):
        """
        Restart quectel_CM
        """
        try:
            system('sudo kill -9 %d' % self.qcm_handle.pid)
            self.__log_line(" *** KILLED due to restart @ %s" % datetime.datetime.now())
        except:
            pass

    def __log_line(self, line):
        """
        Log a line, shifting out the oldest data if we're over log_lines.
        """
        logger.info("CM: %s" % line)
        self.log.append(line)
        if len(self.log) > self.log_lines:
            self.log = self.log[-(self.log_lines):]

    def __supervise(self):
        """
        Maintain the quectel_CM instance
        """
        self.is_supervising = True

        try:

            # While we've not been terminated
            while self.is_supervising:

                # If the binary can't be found, stop supervising
                if not path.isfile(self.path):
                    logger.error("Quectel_CM path %s does not exist - cannot start" % self.path)
                    self.is_supervising = False
                    return None
                    
                command = ['sudo', self.path]

                # APN configured?
                if self.apn is not None:
                    if 'name' in self.apn:
                        command.append('-s')
                        command.append(self.apn['name'])
                        if 'user' in self.apn:
                            command.append(self.apn['user'])
                        if 'pass' in self.apn:
                            command.append(self.apn['pass'])

                logger.info("Starting quectel_CM %s..." % ' '.join(command))
                self.qcm_handle = Popen(command, stdin = PIPE, stdout = PIPE, stderr = subprocess.STDOUT, shell=True)
                qcm_out = NonBlockingStreamReader(self.qcm_handle.stdout)
                qcm_err = NonBlockingStreamReader(self.qcm_handle.stderr)

                # Log the start
                self.__log_line(" *** STARTED PID %d @ %s" % (self.qcm_handle.pid, datetime.datetime.now()))
                
                # While running...
                while True:

                    # Check the process each second
                    time.sleep(1.0)

                    # Read all output
                    while True:
                        output = qcm_out.readline(0.1)
                        if not output:
                            break
                        self.__log_line(output.decode().strip())
                        err = qcm_err.readline(0.1)
                        if not err:
                            break
                        self.__log_line(err.decode().strip())

                    retcode = self.qcm_handle.poll()
                    
                    if retcode is not None:
                        self.qcm_handle = None
                        logger.warn("Quectel_CM terminated with code %d - waiting %dms before relaunch..." % (retcode, self.respawn_delay))

                        # Log the termination
                        self.__log_line(" *** TERMINATED @ %s with exit code %d" % (datetime.datetime.now(), retcode))

                        # Wait the delay time...
                        time.sleep(self.respawn_delay / 1000)
                        
                        # Break out to respawn...
                        break

        except Exception as supervise_ex:
            logger.error('Error supervising CM %s: %s' % (self.path, supervise_ex))
            raise supervise_ex
