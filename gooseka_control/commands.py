
class CommandCodes(object):
    DUTY_LINEAL=0
    ANGULAR_VELOCITY=1


class Commands(object):

    def _set_duty_lineal(self, value):
        return (CommandCodes.DUTY_LINEAL, value)

    def _set_angular_velocity(self, value):
        return (CommandCodes.ANGULAR_VELOCITY, value)

    def get_command(self, telemetry):
        """ Obtain the list of commands 

        Keyword arguments:
        telemetry -- dict with telemetry information

        """

        return []
    
    def __init__(self, config):
        """ Initialization """
        
        self.config = config
