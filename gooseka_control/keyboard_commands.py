import logging
import math
from inputs import get_gamepad
from inputs import devices
from .commands import Commands


logger = logging.getLogger(__name__)

class ManualCommands(Commands):
    """ Gamepad controller """

    def get_command(self, telemetry):
        """ Obtain the list of commands from the keyboard 

        Keyword arguments:
        telemetry -- dict with telemetry information
        """
        
        code_list = []
        return code_list
    
    def __init__(self, config):
        """ Initialization """
        
        super(ManualCommands, self).__init__(config)
        self.steering = 0
        self.throttle = 0
        self.last_X = 128
        self.last_Z = 0
