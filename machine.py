# C:\Users\yaniv\AppData\Local\Programs\Thonny\Lib\site-packages\thonny\plugins\micropython\api_stubs
import random
import subprocess
from time import sleep
import datetime
class Pin :
    IN=1
    OUT=2
    PULL_UP=1
    PULL_DOWN=0
    def __init__(self, pinNumber, pinDirection=1, pull=1, value=1):
        def randoms(self):
            random.randint(0, 1)
        return None

    def on(self):
        return 0

    def off(self):
        return 1

    def irq(self, btn_change):
        return None

    def value(self):
        return random.randint(0, 1)

class ADC :
    ATTN_11DB=1
    def __init__(self, pinNumber):
        def randoms(self):
            random.randint(0, 1)
        return None

    def atten(self, atten):
        pass

    def read(self):
        return random.randint(0, 4095)

class SoftI2C:
    def __init__(self, scl=1, sda=2):
        return None

class I2C:
    def __init__(self, scl=1, sda=2):
        return None
class ssd1306:
    def __init__(self):
        pass
    def SSD1306_I2C(self,a,b):
        return ssd1306()
    def SH1106_I2C(self,a,b):
        return ssd1306()
    def text(self,a,b,c):
        pass
    def show(self):
        pass
    def sleep(self,a):
        pass
    def fill(self,a):
        pass

class Timer:
    def __init__(self, timerNumber):
        pass
    def deinit(self):
        pass
    def init(self, period=3000, callback=None):
        pass

class WDT:
    last_time = datetime.datetime.now()
    def __init__(self, timeout=5000):
        pass
    def feed(self):
        pass
        # now_time = datetime.datetime.now()
        # print('WDT: ',now_time - self.last_time)
        # self.last_time = now_time

class PWM:
    _duty = None
    _freq = None
    def __init__(self, pinNumber, freq=0 , duty=0):
        global _freq, _duty
        _freq = freq
        _duty = duty
        return None
    def duty(self, *duty):
        global _duty
        if len(duty) == 1 and isinstance(duty[0], int):
            _duty = duty[0]
            return _duty
        elif len(duty) == 0:
            return _duty
        else: raise ValueError('duty function get 0 or 1 int parameters')
    def freq(self, *freq):
        global _freq
        if len(freq) == 1 and isinstance(freq[0], int):
            _freq = freq[0]
            return _freq
        elif len(freq) == 0:
            return _freq
        else: raise ValueError('freq function get 0 or 1 int parameters')

def time_pulse_us(pin, level):
    return random.randint(1, int(100*2/0.034))

def sleep_us(num):
    sleep(num/1000000)

def ticks_ms(num):
    return datetime.datetime.now()

def ticks_diff(last, now):
    return now - last