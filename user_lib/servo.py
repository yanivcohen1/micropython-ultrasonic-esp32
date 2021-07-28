# the micro servo 9g, need external power supply for the motor and the grnd connected to esp32 grnd
# brown = grnd, red = 5v, yellow = signal
# micro servo PWM freq=50(20ms cycle), dutycycle[30=0°, 140=180°]
# spec: https://www.jameco.com/z/RS001B-Dagu-HiTech-Electronic-9g-2-kg-cm-Micro-Servo-Motor_2214601.html
# No-Load Speed (4.8V): 0.08 sec/60°
# Torque: 1.5 kg.cm @ 4.8V; 2.0 kg/cm @ 6V
# angle range: 0° - 180°
# Current: < 500mA
# Operating Temperature Range: 0°-60°
from machine import Pin, ADC, PWM
from time import sleep

servo = PWM(Pin(4), freq=50) # 50HZ = 20ms cycle
SERVO_MAX_ANGLE = 180
SERVO_MIN_ANGLE = 0
SERVO_MAX_DUTY = 140 # angle=180'
SERVO_MIN_DUTY = 30 # angle=0'
SERVO_RANG_DUTY = SERVO_MAX_DUTY - SERVO_MIN_DUTY
POT_MAX_READ = 4095
sliderPot = ADC(Pin(34))
sliderPot.atten(ADC.ATTN_11DB) # Full range: 3.3v
lastDuty = SERVO_MIN_DUTY # init angle=0'

def dutyForAngle(angle):
    duty = None
    if 0 <= angle <= 180: duty = int(SERVO_MIN_DUTY + SERVO_RANG_DUTY * angle / SERVO_MAX_ANGLE)
    else: print('error angle, need to be 0 <= angle <= 180')
    return duty

def angleForDuty(duty):
    angle = None
    if 30 <= duty <= 140: angle = int(SERVO_MAX_ANGLE * (duty - SERVO_MIN_DUTY) / SERVO_RANG_DUTY)
    else: print('error duty, need to be 30 <= duty <= 140')
    return angle

def tester():
    try:
        while True:
            global lastDuty
            current_sliderPot = sliderPot.read() # min is 0, max read 4095
            # print(current_sliderPot)
            calcPotDuty = int(SERVO_MIN_DUTY + SERVO_RANG_DUTY * current_sliderPot / POT_MAX_READ)
            if not(calcPotDuty == lastDuty or calcPotDuty == lastDuty + 1  \
                or calcPotDuty == lastDuty - 1):
                lastDuty = calcPotDuty
                servo.duty(calcPotDuty)
                print('angle is:', current_sliderPot * SERVO_MAX_ANGLE / POT_MAX_READ)
                sleep(15/1000) # 15ms time take the motor to get to position
            else: sleep(1/1000) # 1ms loop delay
    except KeyboardInterrupt : # control+C press
        pass
    servo.deinit()

# run tester - change potentiometer to change servo angle
# tester()
