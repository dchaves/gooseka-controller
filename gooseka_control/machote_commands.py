import logging
from inputs import get_gamepad
from inputs import devices
from .commands import Commands


logger = logging.getLogger(__name__)

class MachoteCommands(Commands):
    """ Gamepad controller """

    def get_command(self, telemetry):
        """ Obtain the list of commands from the gamepad 

        Keyword arguments:
        telemetry -- dict with telemetry information
        """
        
        code_list = []
        events = get_gamepad()
        for event in events:
            logger.info("EVENT {}:{}".format(event.code, event.state))
            
            # print(event.code, event.state)
            if (event.code == "ABS_Z"):
                code_list.append(self._set_duty_left(event.state))
            if (event.code == "ABS_RZ"):
                code_list.append(self._set_duty_right(event.state))

        return code_list
    
    def __init__(self, config):
        """ Initialization """
        
        super(MachoteCommands, self).__init__(config)