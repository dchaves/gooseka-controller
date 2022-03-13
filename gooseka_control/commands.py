
class CommandCodes(object):
    DUTY_LINEAR=0
    DUTY_ANGULAR=1


class Commands(object):

    def _set_duty_linear(self, value):
        return (CommandCodes.DUTY_LINEAR, value)

    def _set_duty_angular(self, value):
        return (CommandCodes.DUTY_ANGULAR, value)

    def get_command(self, telemetry):
        """ Obtain the list of commands 

        Keyword arguments:
        telemetry -- dict with telemetry information

        """

        return []
    
    def __init__(self, config):
        """ Initialization """
        
        self.config = config
