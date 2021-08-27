import unittest

import pydantic

from driver import Driver


class DirverTest(unittest.TestCase):
    def setUp(self):
        super().setUp()
        settings = {
            'forward_pin': 23,
            'backward_pin': 24,
            'adress': 0x60,
        }
    
    def test_can_drive_forward(self):
        driver = Driver(self.settings)
        value = 10
        driver.move(value)

        expected_value = 100 - 10

        self.assertTrue(driver.current_direction == Driver.Direction.forward)
        self.assertTrue(driver.forward_gpio.value == True)
        self.assertTrue(driver.backward_gpio.value == False)
        self.assertEqual(driver.sended_value == expected_value)
    
    def test_can_drive_backward(self):
        driver = Driver(self.settings)
        value = -10
        driver.move(value)

        expected_value = 100 + value
        
        self.assertTrue(driver.current_direction == Driver.Direction.backward)
        self.assertTrue(driver.forward_gpio.value == False)
        self.assertTrue(driver.backward_gpio.value == True)
        self.assertEqual(driver.sended_value == expected_value)
    
    def test_can_stop_when_value_is_0(self):
        driver = Driver(self.settings)
        driver.move(10)
        
        value = 0
        driver.move(value)
        expected_value = 100 - value

        self.assertTrue(driver.current_direction == Driver.Direction.stop)
        self.assertTrue(driver.forward_gpio.value == False)
        self.assertTrue(driver.backward_gpio.value == False)
        self.assertEqual(driver.sended_value == expected_value)
    
    def test_original_state_is_stop(self):
        driver = Driver(self.settings)

        self.assertTrue(driver.current_direction == Driver.Direction.stop)
        self.assertTrue(driver.forward_gpio.value == False)
        self.assertTrue(driver.backward_gpio.value == False)
        self.assertEqual(driver.sended_value == 100)

    def test_cannot_send_wrong_value(self):
        driver = Driver(self.settings)
        value = 110 

        with self.assertRaises(ValueError):
            driver.move(value)
    
    def test_cannot_send_wrong_value_type(self):
        driver = Driver(self.settings)
        value = 1.5 

        with self.assertRaises(TypeError):
            driver.move(value)
    
    
    def test_cannot_send_wrong_options(self):
        self.settings['forward_pin'] = 21.5
        with self.assertRaises(pydantic.ValidationError):
            driver = Driver(self.settings)