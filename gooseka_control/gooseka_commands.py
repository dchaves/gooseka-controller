from inputs import get_gamepad
from inputs import devices
from .commands import Commands
from pid import PID


class GoosekaCommands(Commands):
    """ Gamepad controller """

    def get_command(self, telemetry):
        """ Obtain the list of commands from the gamepad 

        Keyword arguments:
        telemetry -- dict with telemetry information
        """
        
        code_list = []
        events = get_gamepad()
        for event in events:
            # print(event.code, event.state)
            if (event.code == "ABS_Z"):
                code_list.append(self._set_duty_left(event.state))
            if (event.code == "ABS_RZ"):
                code_list.append(self._set_duty_right(event.state))

        return code_list
    
    def __init__(self, config):
        """ Initialization """
        
        super(GoosekaCommands, self).__init__(config)

        self.linear_pid = PID(self.config["LINEAR_KP"],
                              self.config["LINEAR_KD"],
                              self.config["LINEAR_KI"],
                              self.config["LINEAR_MAX_I"])
        
        
                              
