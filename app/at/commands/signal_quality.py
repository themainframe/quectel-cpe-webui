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

    @staticmethod
    def __get_csq_state(csq):
        """
        Get a state classification for a CSQ level.

        Returns:

        +CSQ: <RSSI>,<BER>
        ..or..
        +CME ERROR: <err>

        RSSI:
        0 = -113dBm or less
        1 = -111dBm
        2-30= - 109dBm to -53dBm
        31 = -51dBm or greater
        99 = not known or not detectable

        BER:
        0-7 = as RXQUAL values in the table in GSM 05.08 [20] subclause 7.2.4
        99 = not known or not detectable

        ERR:
        0 = phone failure
        1 = no connection to phone
        2 = phone-adaptor link reserved
        3 = operation not allowed
        4 = operation not supported
        5 = PH_SIM PIN required
        6 = PH_FSIM PIN required
        7 = PH_FSIM PUK required
        10 = SIM not inserted
        11 = SIM PIN required
        12 = SIM PUK required
        13 = SIM failure
        14 = SIM busy
        15 = SIM wrong
        16 = incorrect password
        17 = SIM PIN2 required
        18 = SIM PUK2 required
        20 = memory full
        21 = invalid index
        22 = not found
        23 = memory failure
        24 = text string too long
        25 = invalid characters in text string
        26 = dial string too long
        27 = invalid characters in dial string
        30 = no network service
        31 = network timeout
        32 = network not allowed, emergency calls only
        40 = network personalization PIN required
        41 = network personalization PUK required
        42 = network subset personalization PIN required
        43 = network subset personalization PUK required
        44 = service provider personalization PIN required
        45 = service provider personalization PUK required
        46 = corporate personalization PIN required
        47 = corporate personalization PUK required
        901 = audio unknown error
        902 = audio invalid parameters
        903 = audio operation is not supported
        904 = audio device is busy



        """
        if csq >= 99 or csq < 6:
            return ResultValueState.ERROR
        elif csq < 12:
            return ResultValueState.WARNING
        else:
            return ResultValueState.OK

    def poll(self, serial_port):

        # Send the CSQ query
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

            self.results.append(ResultValue(
                "csq",
                "Signal Quality (CSQ)",
                "Signal Strength Indication (0-31)",
                csq_matches.group(1),
                self.__get_csq_state(int(csq_matches.group(1)))
            ))
            self.results.append(ResultValue("csq_ber", "Channel BER", "Channel Bit Error Rate", csq_matches.group(2)))


        self.last_update = time.time()
