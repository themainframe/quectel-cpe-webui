import time
import logging

logger = logging.getLogger(__name__)

class ResultValueState:
    OK = 0
    WARNING = 1
    ERROR = 2
    NOT_APPLICABLE = 3

class ResultValue:
    def __init__(self, key, name, description, value, state=ResultValueState.OK):
        self.key = key
        self.name = name
        self.description = description
        self.value = value
        self.state = state

class Command:
    """
    Abstract AT command.
    """

    def __init__(self, name, description):
        """
        Create a new command.
        """
        self.name = name
        self.description = description
        self.results = []

        # The time when the command was last checked
        self.last_update = None

    def receive(self, port, timeout=3, multi_result=False, success=['OK'], failure=['ERROR']):
        """
        Receive a typical AT response.
        Returns a tuple containing the result state (None=Timeout, True=OK, False=ERROR) and the result line(s).
        If multi_result=False, a maximum of one result line will be returned, otherwise a list of result lines will always be returned.
        """
        # Timeout handling
        start_time = time.time()

        # The receive buffer
        r_buf = ""

        # The result state -
        result_state = None
        result_lines = []

        while True:

            # Have we waited too long?
            #if total_waited > timeout:
            if time.time() - start_time > timeout:
                logger.debug('Receive timed out')
                break

            # Read bytes from the interface (python3 needs decode from bytes to string)
            got = port.read(1024).decode('ascii')
            if not got:
                continue
            r_buf += got

            # Have we received a linebreak?
            split_str = '\r\n'
            if split_str in r_buf:

                # Process the lines
                r_lines = r_buf.split(split_str)
                for r_line in r_lines:

                    # Just skip completely empty lines
                    if r_line == '':
                        continue

                    # Good result?
                    if r_line.upper() in success:
                        result_state = True
                        break

                    # Bad result?
                    if r_line.upper() in failure:
                        result_state = False
                        break

                    result_lines.append(r_line)

                # Clear the receive buffer
                r_buf = ''

                # Have we got a result state?
                if result_state is not None:
                    break

        if multi_result:
            return (result_state, result_lines)
        else:
            return (result_state, result_lines[0] if len(result_lines) > 0 else '')
