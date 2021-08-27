from enum import Enum

import pydantic

import board
import digitalio
from Adafruit_MCP4725 import MCP4725
       
       
# think about state design pattern [start, forward, backward, stop, killed]

class DriverSettings(pydantic.BaseModel):
    forward_pin: int
    backward_pin: int
    i2c_adress: int = 0x60


class Driver:
    """the class incapsulate interface of the driver

        it uses 2 GPIO keys to control switches of propulsion and steering drivers and 
        I2C DAC to provide value [0:100] to the drivers 
    """

    class Direction(Enum):
        forward = 1
        backward = 2
        stop = 3
    
    MAX_VALUE = 4095
    
    def __init__(self, driver_settings: DriverSettings) -> None:
               
        self.current_direction = self.Direction.stop

        self.dac = MCP4725(address=driver_settings.i2c_adress)
        self._send_value(0)
        
        self.forward_gpio = digitalio.DigitalInOut(board.__dict__[f'D{driver_settings.forward_pin}'])
        self.forward_gpio.direction = digitalio.Direction.OUTPUT
        self.forward_gpio.value = False

        self.backward_gpio = digitalio.DigitalInOut(board.__dict__[f'D{driver_settings.backward_pin}'])
        self.backward_gpio.direction = digitalio.Direction.OUTPUT
        self.backward_gpio.value = False
    
    def __del__(self):
        self.stop_motor()
        self.dac.set_voltage(self.MAX_VALUE, persist=True)
   
    def move(self, value: int) -> None: 
        
        if type(value) is not int:
            raise TypeError("value has to be int type")

        if not -100 <= value <= 100:
            raise ValueError("value should be in range of [0:127]")

        if value > 0:
            
            if self.current_direction == self.Direction.backward:
                self.stop_motor()

            self.current_direction = self.Direction.forward
            self.forward_gpio.value = True

        elif value < 0:

            if self.current_direction == self.Direction.forward:
                self.stop_motor()
            
            self.current_direction = self.Direction.backward
            self.backward_gpio.value = True

        elif value == 0:
            self.stop_motor()
            
        self._send_value(value)

    def _send_value(self, value):
        self.sended_value = 100 - abs(value)
        self.dac.set_voltage(int((self.MAX_VALUE * self.sended_value) / 100))

    def stop_motor(self) -> None:
        if self.current_direction != self.Direction.stop:

            self.dac.set_voltage(self.MAX_VALUE)
            
            self.forward_gpio.value = False
            self.backward_gpio.value = False

            self.current_direction = self.Direction.stop