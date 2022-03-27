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
        events = devices.gamepads[0]._do_iter()
        if events is not None:            
            for event in events:
                # Ignore events that are not expected
                # if((event.code != "ABS_X") and (event.code != "ABS_RZ")):
                #     continue

                # logger.info("EVENT {}:{}".format(event.code, event.state))
                
                if (event.code == "ABS_X"):
                    if abs(event.state - self.last_X) < 5:
                        pass
                    else:
                        self.last_X = event.state
                        self.steering = (event.state - 128) / 128.0 # Input Range: [0,255]; Output range: [-1,1]
                if (event.code == "ABS_RZ"):
                    if abs(event.state - self.last_Z) < 5:
                        pass
                    else:
                        self.last_Z = event.state
                        self.throttle = event.state # Input Range: [0,255]; Output range: [0,255]

                duty_left = self.throttle * min(1, (1 + self.steering))
                duty_right = self.throttle * min(1, (1 - self.steering))
                logger.info("LEFT: {:>3}\tRIGHT: {:>3}".format(int(duty_left), int(duty_right)))

                code_list.append(self._set_duty_linear(duty_left))
                code_list.append(self._set_duty_angular(duty_right))
        return code_list
    
    def __init__(self, config):
        """ Initialization """
        
        super(ManualCommands, self).__init__(config)
        self.steering = 0
        self.throttle = 0
        self.last_X = 128
        self.last_Z = 0
