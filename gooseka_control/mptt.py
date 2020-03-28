import logging


logger = logging.getLogger(__name__)


class MPTT(object):
    """ Implementation of a MPTT algorithm """

    def step(self, telemetry, current_duty):
        """ Execute a step of MPTT """

        voltage = 0.0
        current = 0.0
        
        for _key in telemetry.keys():
            voltage += telemetry[_key]["voltage"]
            current += telemetry[_key]["current"]

        voltage /= len(telemetry.keys())

        if current_duty == 0:
            current_duty += 5  
        
        elif self.last_voltage is not None:
            dev_voltage = voltage - self.last_voltage
            dev_current = current - self.last_current

            if dev_voltage > 0:
                dev_p = (1.0 * dev_current)/dev_voltage

            else:
                dev_p = 0
                
            if voltage > 0:    
                cur_p = (1.0 * current)/voltage

            else:
                cur_p = 0

            #m_r = 1 + (1.0/cur_p) * dev_p
            m_r = 5

            logger.info("MR {} DEVP {} CURP {} CURR {} VOLT {}".format(m_r, dev_p, cur_p, current, voltage))
            
            if dev_voltage == 0:
                if dev_current == 0:
                    # we are at the MPP. Doing nothing
                    logger.info("MPTTV0 NOTHING")

                elif dev_current > 0:
                    # increase duty
                    # How much?
                    #current_duty += m_r
                    current_duty += self.mptt_control.step(m_r, 1)
                    logger.info("MPTTV0 UP")
                    
                else:
                    # decrease duty
                    # How much?
                    #current_duty -= m_r
                    current_duty += self.mptt_control.step(-m_r, 1)
                    logger.info("MPTTV0 DOWN")
           
            elif dev_p == -cur_p:
                # we are at the MPP. Doing nothing
                logger.info("MPTTV NOTHING")

            elif dev_p > -cur_p:
                # increase duty
                # How Much?
                #current_duty += m_r
                current_duty += self.mptt_control.step(m_r, 1)
                logger.info("MPTTV UP")
            else:
                # decrease duty
                # How much?
                #current_duty -= m_r #
                current_duty += self.mptt_control.step(-m_r, 1)
                logger.info("MPTTV DOWN")
            
        self.last_current = current
        self.last_voltage = voltage

        return current_duty

    def reset(self):
        """ Reset MPTT state """
        self.last_current = None
        self.last_voltage = None
        
    def __init__(self, mptt_control):
        """ Initialization """
        # TODO
        self.last_voltage = None
        self.last_current = None
        self.mptt_control = mptt_control
