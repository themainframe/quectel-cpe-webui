import time
import re
import logging
from ..command import Command, ResultValue, ResultValueState

logger = logging.getLogger(__name__)

class TemperatureCommand(Command):
    """
    Checks MT Temperature Information
    """

    def __init__(self):
        super().__init__("UE Temperature", "User Equipment Temperature")

    @staticmethod
    def __get_temperature_state(temp):
        """
        Get a state classification for a temperature.
        """
        if temp > 50:
            return ResultValueState.ERROR
        elif temp > 40 :
            return ResultValueState.WARNING
        else:
            return ResultValueState.OK

    def poll(self, serial_port):

        # Send the Temperature query
        logger.debug("Polling Temperature...")
        serial_port.write("AT+QTEMP\r\n".encode("utf-8"))

        # Wait for the response to be written
        time.sleep(0.5)

        # Read the response content
        cmd_result = self.receive(serial_port, multi_result=True)

        # Clear the results
        self.results = []
        
        if not cmd_result[0]:
            logger.warn("No response to Temperature query")
            # No results to work with
            return

        # Parse the output
        for result_line in cmd_result[1]:
            temp_matches = re.match(r'\+QTEMP:\s?"([a-z0-9\-]+)","(\d+)"', result_line)
            if temp_matches is None:
                continue
            
            self.results.append(ResultValue(
                "temp_" + temp_matches.group(1),
                temp_matches.group(1) + " Temperature",
                "Temperature of the \"%s\" region of the UE" % temp_matches.group(1),
                temp_matches.group(2),
                self.__get_temperature_state(int(temp_matches.group(2)))
            ))

        self.last_update = time.time()