import time

# only test for uln2003
# spec: http://www.geeetech.com/wiki/index.php/Stepper_Motor_5V_4-Phase_5-Wire_%26_ULN2003_Driver_Board_for_Arduino#Interfacing_circuits
# driver web: https://github.com/zhcong/ULN2003-for-ESP32
class Stepper:
    # http://www.jangeox.be/2013/10/stepper-motor-28byj-48_25.html
    # from spec- Speed Variation Ratio ：1/64, the ratio between input wheel to output wheel is 64
    # from the spec (5.625'/64) angle for one HALF_STEP, and for one internal cycle you need 8 HALF_STEPs
    # so for 360' - (360/(5.625'/64))/8=512(befor any step) and multipy it by one cycle(8 HALF_STEPs or 4 FULL_STEPs)
    FULL_ROTATION = int(4075.7728395061727 / 8) # 512

    HALF_STEP = [
        [0, 0, 0, 1],
        [0, 0, 1, 1],
        [0, 0, 1, 0],
        [0, 1, 1, 0],
        [0, 1, 0, 0],
        [1, 1, 0, 0],
        [1, 0, 0, 0],
        [1, 0, 0, 1],
    ]

    FULL_STEP = [
        [1, 0, 1, 0],
        [0, 1, 1, 0],
        [0, 1, 0, 1],
        [1, 0, 0, 1]
    ]
    def __init__(self, mode, pin1, pin2, pin3, pin4, delay):
    	if mode=='FULL_STEP':
        	self.mode = self.FULL_STEP
        else:
        	self.mode = self.HALF_STEP
        self.pin1 = pin1
        self.pin2 = pin2
        self.pin3 = pin3
        self.pin4 = pin4
        self.delay = delay  # Recommend 10+ for FULL_STEP, 1 is OK for HALF_STEP
        
        # Initialize all to 0
        self.reset()
        
    def step(self, count, direction=1):
        """Rotate count steps. direction = -1 means backwards"""
        for x in range(count):
            for bit in self.mode[::direction]:
                self.pin1(bit[0])
                self.pin2(bit[1])
                self.pin3(bit[2])
                self.pin4(bit[3])
                time.sleep_ms(self.delay)
        self.reset()
    def angle(self, r, direction=1):
    	self.step(int(self.FULL_ROTATION * r / 360), direction)
    def reset(self):
        # Reset to 0, no holding, these are geared, you can't move them
        self.pin1(0) 
        self.pin2(0) 
        self.pin3(0) 
        self.pin4(0)

def create(pin1, pin2, pin3, pin4, delay=2, mode='HALF_STEP'):
	return Stepper(mode, pin1, pin2, pin3, pin4, delay)

# use it
# import Stepper
# from machine import Pin
# Recommend 10+ for FULL_STEP, 1 is OK for HALF_STEP, the defoult is HALF_STEP 
# s1 = Stepper.create(Pin(16,Pin.OUT),Pin(17,Pin.OUT),Pin(5,Pin.OUT),Pin(18,Pin.OUT), delay=2)
# s1.step(100) # 100 steps of 8 HALF_STEPs eche step, step mode(Full/Half) is init on create
# s1.step(100,-1) # backwards 100 steps of 8 HALF_STEPs eche step, step mode(Full/Half) is init on create
# s1.angle(180) # forwards 180', step mode(Full/Half) is init on create
# s1.angle(360,-1) # backwards 360', step mode(Full/Half) is init on create