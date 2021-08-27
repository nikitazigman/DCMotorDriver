from enum import Enum

import board
import pydantic
import digitalio
from Adafruit_MCP4725 import MCP4725
       

class Driver(pydantic.BaseModel):
    """the class incapsulate interface of the driver

        it uses 2 GPIO keys to control switches of propulsion and steering drivers and 
        I2C DAC to provide value [0:100] to the drivers 
    """

    class Direction(Enum):
        forward = 1
        backward = 2
        stop = 3
    
    MAX_VALUE = 4095

    forward_pin: int
    backward_pin: int
    i2c_adress: int = 0x60
    
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.current_direction = self.Direction.stop

        self.dac = MCP4725(address=self.i2c_adress)
        self.dac.set_voltage(self.MAX_VALUE)

        self.forward_gpio = digitalio.DigitalInOut(board.__dict__[f'D{self.forward_pin}'])
        self.forward_gpio.direction = digitalio.Direction.OUTPUT
        self.forward_gpio.value = False

        self.backward_gpio = digitalio.DigitalInOut(board.__dict__[f'D{self.backward_pin}'])
        self.backward_gpio.direction = digitalio.Direction.OUTPUT
        self.backward_gpio.value = False
    
    def __del__(self):
        self.stop_motor()
        self.dac.set_voltage(4096, persist=True)
   
    def move(self, value: int) -> None: 
       
        if not -100 <= value <= 100:
            raise ValueError("value should be in range of [0:127]")

        inverted_value = 100 - abs(value)

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
            
        self.dac.set_voltage(int((4096 * inverted_value) / 100))
      
    def stop_motor(self) -> None:
        if self.current_direction != self.Direction.stop:

            self.dac.set_voltage(4096)
            
            self.forward_gpio.value = False
            self.backward_gpio.value = False

            self.current_direction = self.Direction.stop