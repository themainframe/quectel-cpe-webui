import time
import datetime
import logging
import threading
import pexpect
from os import path, system
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

        # Was the process killed by us?
        self.is_killed = False

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
        self.__supervise_thread.start()

    def stop(self):
        """
        Stop quectel_CM
        """
        self.is_supervising = False
        self.__kill()

    def restart(self):
        """
        Restart quectel_CM
        """
        self.__log_line(" *** KILLED due to restart @ %s" % datetime.datetime.now())
        self.__kill()

    def __kill(self):
        """
        Kill quectel_CM
        """

        try:
            self.qcm_handle.kill(sig=9)
            self.is_killed = True
            logger.info("Killed using kill()")
            return
        except Exception as int_kill_ex:
            logger.warn("Failed to kill using kill() method: %s" % int_kill_ex)

        try:
            system('sudo kill -9 %d' % self.qcm_handle.pid)
            self.is_killed = True
            logger.info("Killed using kill signal")
        except Exception as ext_kill_ex:
            logger.warn("Failed to kill using kill signal: %s" % ext_kill_ex)

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
                    
                command = [self.path]

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
                self.qcm_handle = pexpect.spawn('sudo', command)
                self.is_killed = False

                # Log the start
                self.__log_line(" *** STARTED PID %d @ %s" % (self.qcm_handle.pid, datetime.datetime.now()))
                
                # While running...
                while True:

                    # Check the process each second
                    time.sleep(1.0)

                    # Read all output
                    while True:
                        try:
                            output = self.qcm_handle.read_nonblocking(1024, 1)
                            if not output:
                                break
                            lines = output.split(b"\n")
                            for line in lines:
                                if line.decode().strip() != '':
                                    self.__log_line(line.decode().strip())
                        except:
                            break
                        
                    if not self.qcm_handle.isalive() or self.is_killed:
                        exitcode = self.qcm_handle.exitstatus if self.qcm_handle.exitstatus is not None else -1
                        logger.warn("Quectel_CM terminated with code %d - waiting %dms before relaunch..." % (exitcode, self.respawn_delay))

                        # Log the termination
                        self.__log_line(" *** TERMINATED @ %s with exit code %d" % (datetime.datetime.now(), exitcode))

                        # Wait the delay time...
                        time.sleep(self.respawn_delay / 1000)
                        
                        # Break out to respawn...
                        break

        except Exception as supervise_ex:
            logger.error('Error supervising CM %s: %s' % (self.path, supervise_ex))
            raise supervise_ex
