from enum import Enum

import pydantic
import digitalio
from Adafruit_MCP4725 import MCP4725
       

class Driver:
    """the class incapsulate interface of the driver

        it uses 2 GPIO keys to control switches of propulsion and steering drivers and 
        I2C DAC to provide value [0:100] to the drivers 
    """

    class Direction(Enum):
        forward = 1
        backward = 2
        stop = 3

    DELAY_COEFICIENT = 10

    def __init__(self, motor_dict: dict, name: str) -> None:
        """it's initializes the driver class

        Args:
            motor_dict (dict): part of setting dict related to the driver (propulsion or steering)
        """
        self.name = name

        self.current_direction = self.Direction.stop

        self.dac = MCP4725(address=motor_dict['I2C']['address'])
        self.dac.set_voltage(4095)

        self.forward_gpio = digitalio.DigitalInOut(motor_dict['forward']['pin'])
        self.forward_gpio.direction = motor_dict['forward']['direction']
        self.forward_gpio.value = False

        self.backward_gpio = digitalio.DigitalInOut(motor_dict['backward']['pin'])
        self.backward_gpio.direction = motor_dict['backward']['direction']
        self.backward_gpio.value = False
    
    def __del__(self):
        self.stop_motor()
        self.dac.set_voltage(4096, persist=True)

    def _check_dict(self, motor_dict: dict) -> None:
        """it checks the structure of the dict

        Args:
            motor_dict (dict): part of setting dict related to the driver (propulsion or steering)

        Returns:
            bool: True - all is fine, False - structure of @motor_dict is wrong
        """

        if not {'forward','backward','I2C'} <= set(motor_dict.keys()):
            raise Exception("motor_settig should have 'forward' and 'backward' keys")
        
        for key,value in motor_dict.items():
            
            if not {'pin','direction'} <= set(value.keys()):
                raise Exception(f"{key} of motor_settig should have 'pin' and 'direction' keys")
            elif not 'address' in value.keys():
                raise Exception(f"{key} of motor_settig should have 'address' key")
        
        return True
    
    def move(self, value: int) -> None: 
        """it makes robot move

        Args: 
            value (int): the value in [0:127] of moter power
        """
        
        if not -127 <= value <= 127:
            raise Exception("value should be in range of [0:127]")

        normalised_value = (value / 127.0)*100
        normalised_value_inverted = 100 - abs(normalised_value)

        if normalised_value > 0:
            
            if self.current_direction == self.Direction.backward:
                self.stop_motor()

            self.current_direction = self.Direction.forward
            self.forward_gpio.value = True

        elif normalised_value < 0:

            if self.current_direction == self.Direction.forward:
                self.stop_motor()
            
            self.current_direction = self.Direction.backward
            self.backward_gpio.value = True

        elif normalised_value == 0:
            self.stop_motor()
            
        self.dac.set_voltage(int((4096 * normalised_value_inverted) / 100))
      
    def stop_motor(self) -> None:
        if self.current_direction != self.Direction.stop:

            self.dac.set_voltage(4096)
            
            self.forward_gpio.value = False
            self.backward_gpio.value = False

            self.current_direction = self.Direction.stop