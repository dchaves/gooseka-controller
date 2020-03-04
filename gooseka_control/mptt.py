import logging


logger = logging.getLogger(__name__)


class MPTT(object):
    """ Implementation of a MPTT algorithm """

    def step(self, telemetry, current_duty):
        """ Execute a step of MPTT """

        voltage = 0
        current = 0
        
        for _key in telemetry.keys():
            voltage += telemetry[_key]["voltage"]
            current += telemetry[_key]["current"]

        voltage /= len(telemetry.keys())

        if self.last_voltage is not None:
            dev_voltage = voltage - self.last_voltage
            dev_current = current - self.last_current

            dev_p = (1.0 * dev_current/dev_voltage)
            cur_p = (1.0 * current)/voltage

            m_r = 1 + 1.0/cur_p * dev_p
 
            if dev_voltage == 0:
                if dev_current == 0:
                    # we are at the MPP. Doing nothing
                    pass

                elif dev_current > 0:
                    # increase duty
                    # How much?
                    current_duty += mptt_control.step(m_r, 1)
                    
                else:
                    # decrease duty
                    # How much?
                    current_duty -= mptt_control.step(m_r, 1)
           
            if dev_p == -cur_p:
                # we are at the MPP. Doing nothing
                pass

            elif dev_p > -cur_p:
                # increase duty
                # How Much?
                current_duty += mptt_control.step(m_r, 1)

            else:
                # decrease duty
                # How much?
                current_duty -= mptt_control.step(m_r, 1)
            
        self.last_current = current
        self.last_current = voltage

        return current_duty

    def reset(self):
        """ Reset MPTT state """
        self.last_current = None
        self.last_current = None
        
    def __init__(self, mptt_control):
        """ Initialization """
        # TODO
        self.last_voltage = None
        self.last_current = None
        self.mptt_control = mptt_control
