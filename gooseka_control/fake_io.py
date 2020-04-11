import logging
import scipy.stats
import random
import numpy as np
from math import exp
from .utils import millis

logger = logging.getLogger(__name__)

VOLTAGE_MEAN = 1725
VOLTAGE_STD = 21


class FakeComm(object):

    def _get_current(self):

        if self.last_duty_left == 0 or self.last_duty_right == 0:
            self.last_duty_left = self.duty_left
            self.last_duty_right = self.duty_right

        if self.duty_left > 0:
            current_left = self.duty_left * 0.3 + np.random.random() * 2
            if self.last_duty_left > 0: # TODO
                if self.duty_left > self.last_duty_left:
                    current_left += (self.duty_left -
                                     self.last_duty_left) * 0.3

        else:
            current_left = 0

        if self.duty_right > 0:
            current_right = self.duty_right * 0.3 + np.random.random() * 2
            if self.last_duty_right > 0: # TODO
                if self.duty_right > self.last_duty_right:
                    current_right += (self.duty_right -
                                      self.last_duty_right) * 0.3

        else:
            current_right = 0
            
        self.last_duty_left = self.duty_left
        self.last_duty_right = self.duty_right

        return int(current_left), int(current_right)
        
    def send_packet(self, duty_left, duty_right):
        """ Send the packet with motor duties """

        self.duty_left = duty_left
        self.duty_right = duty_right

    def receive_telemetry(self):
        """ Receive telemetry """

        total_duty = self.duty_left + self.duty_right
        current_left, current_right = self._get_current()
        
        voltage = int(np.random.normal(VOLTAGE_MEAN, VOLTAGE_STD))
        total_current = current_left + current_right

        if total_duty > self.mu:
            logger.info("LIMITATION DUTY {} MU {}".format(
                total_duty, self.mu))
            
            prob = self.mptt_dist.pdf(total_duty)
            current_left = int(current_left * prob)
            current_right = int(current_right * prob)
            total_power = current_left + current_right

        panel_power = voltage * total_current    
        erpm_left = panel_power + random.random()
        erpm_right = panel_power + random.random()

        current_left = current_left
        current_right = current_right

        #logger.info("MAX_POWER {} CUR_POWER {} DUTY {} VOLTAGE {} CURRL {} CURRR {} DUTYL {} DUTYR {}".format(
        #    self.mu * 0.3 * VOLTAGE_MEAN,
        #    panel_power, total_duty, voltage,
        #    current_left,
        #    current_right,
        #    self.duty_left,
        #    self.duty_right))
        
        telemetry = {
            "left": {
                "timestamp": 125,
                "temperature": 45,
                "voltage": voltage,
                "current": current_left,
                "power": 559,
                "erpm": erpm_left,
                "duty": 25,
            },
            "right": {
                "timestamp": 125,
                "temperature": 45,
                "voltage": voltage,
                "current": current_right,
                "power": 440,
                "erpm": erpm_right,
                "duty": 35,
            }}

        if millis() - self.now > self.change_every_ms:
            self.mu = np.random.uniform(100, 500)
            self.sigma = np.random.uniform(50, 100)
            self.mptt_dist = scipy.stats.norm(self.mu, self.sigma)
            self.now = millis()
        
        return telemetry

    def __init__(self, serial_port, serial_rate, radio_idle_timeout,
                 mqtt_address, mqtt_port, mqtt_user, mqtt_pass, mqtt_topic):
        """ Initialization """

        self.duty_left = 0
        self.duty_right = 0
        self.last_duty_left = 0
        self.last_duty_right = 0
    
        self.mu = 300
        self.sigma = 100

        self.mptt_dist = scipy.stats.norm(self.mu, self.sigma)
        
        self.mptt_max = 1725 * 100
        
        self.now = millis()

        self.change_every_ms = 30000
