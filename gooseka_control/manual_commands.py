import logging
import math
from inputs import get_gamepad
from inputs import devices
from .commands import Commands


logger = logging.getLogger(__name__)

class ManualCommands(Commands):
    """ Gamepad controller """

    def get_command(self, telemetry):
        """ Obtain the list of commands from the gamepad 

        Keyword arguments:
        telemetry -- dict with telemetry information
        """
        
        code_list = []
        steering = 0
        throttle = 0

        events = get_gamepad()
        for event in events:
            logger.info("EVENT {}:{}".format(event.code, event.state))
            
            # print(event.code, event.state)
            if (event.code == "ABS_X"):
                steering = event.state / 255.0 # Input Range: [-255,255] ???
            if (event.code == "ABS_RZ"):
                throttle = event.state # Inputn Range: [0,255] ???

            duty_left = throttle * min(1, (1 + steering))
            duty_right = throttle * min(1, (1 - steering))

            code_list.append(self._set_duty_left(duty_left))
            code_list.append(self._set_duty_right(duty_right))
        return code_list
    
    def __init__(self, config):
        """ Initialization """
        
        super(ManualCommands, self).__init__(config)
