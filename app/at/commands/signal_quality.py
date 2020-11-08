import time
import re
import logging
from ..command import Command, ResultValue, ResultValueState

logger = logging.getLogger(__name__)

class SignalQualityCommand(Command):
    """
    Checks Signal Quality
    """

    def __init__(self):
        super().__init__("Signal Quality", "Cell Signal Quality Information")

    def poll(self, serial_port):

        # Send the Serving Cell query
        logger.debug("Polling CSQ...")
        serial_port.write("AT+CSQ\r\n".encode("utf-8"))

        # Wait for the response to be written
        time.sleep(0.5)

        # Read the response content
        cmd_result = self.receive(serial_port, multi_result=True)

        # Clear the results
        self.results = []
        
        if not cmd_result[0]:
            logger.warn("No response to CSQ query")
            # No results to work with
            return

        # Parse the CSQ output
        for result_line in cmd_result[1]:
            csq_matches = re.match(r'\+CSQ:\s?(\d+),(\d+)', result_line)
            if csq_matches is None:
                continue
            
            self.results.append(ResultValue("csq", "Signal Quality (CSQ)", "Signal Strength Indication (0-31)", csq_matches.group(1)))
            self.results.append(ResultValue("csq_ber", "Channel BER", "Channel Bit Error Rate", csq_matches.group(2)))


        self.last_update = time.time()