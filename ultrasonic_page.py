import json
from machine import Pin, ADC, time_pulse_us, SoftI2C, Timer, I2C, WDT, PWM
from events_data_page import _chatLock
from   _thread     import start_new_thread
from time import sleep
import user_lib.settings as settings
from user_lib.servo import dutyForAngle

simulation = False
try:
    from time import sleep_us, ticks_ms, ticks_diff
    # import user_lib.SSD1315_OLED_DISP as ssd1306
    import user_lib.sh1106 as ssd1306
except:
    from machine import sleep_us, ticks_ms, ticks_diff
    from machine import ssd1306
    simulation = True 

servo = PWM(Pin(4), freq=50) # 50HZ = 20ms cycle
# wdt_last = ticks_ms()
sliderPot = ADC(Pin(34))
sliderPot.atten(ADC.ATTN_11DB) # Full range: 3.3v
# ESP32 Pin assignment 
# i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
i2c = I2C(scl=Pin(22), sda=Pin(21))
oled_width = 128
oled_height = 64
oled = ssd1306.SH1106_I2C(oled_width, oled_height, i2c) # SSD1306_I2C

# display in 4 rows
oled.sleep(False)
oled.fill(0) # clear display

global _chatWebSockets
_chatWebSockets = [ ]

firstLoad = True
led = Pin(0, Pin.OUT, Pin.PULL_UP)
echoPin = Pin(15, Pin.IN, pull=None)
trigPin = Pin(2, Pin.OUT, pull=None)
timer0 = Timer(0)
# led.value(1)
led.off()
ledOn = False
current_distance = 0
last_sliderPot = -1
sliderIn = None
markForSave = False
lastDistances = [0,0,0]
print('ultrasonic page load')
# ----------------------------------------------------------------------------

def WSJoin(webSocket, addr):
    global sliderIn
    if sliderIn == None:
        global last_sliderPot
        last_sliderPot = int(sliderPot.read() * 100 / 4095)
        sliderIn = readLastSlider()
    if webSocket != None:
        webSocket.RecvTextCallback = OnWSTextMsg
        # webSocket.RecvBinaryCallback = _recvBinaryCallback
        webSocket.ClosedCallback = OnWSClosed
        _chatWebSockets.append(webSocket)
        print('<WELCOME %s:%s>' % addr)
    # addr = webSocket.Request.UserAddress
    with _chatLock:
        send = {}
        send[SendData.slider] = str(sliderIn)
        try: webSocket.SendText(json.dumps(send))
        except: pass
        
    OLED_display()
    # For looping see swTimerServer.py
    global firstLoad
    if firstLoad:
        if True: 
            start_new_thread(cb_timer, (1, webSocket))
        else: # for WH Timer - if not simulation:
            cb = lambda timer: fun_timer(timer, webSocket)
            timer0.init(period=1000, callback=cb)
        firstLoad = False
    
# for sending in timer the results in time period cb(callback)
def cb_timer(delay_sec, websocket):
    while True:
        # global wdt_last
        sleep(delay_sec)
        # wtd_now = ticks_ms()
        # print('wtd: ', wtd_now - wdt_last)
        #wdt_last = wtd_now
        
        with _chatLock:
            # need wochdog
            wdt = WDT(timeout=10000) # enable the wachdog with a timeout of 20s (1s is the minimum)
            wdt.feed() # need to call this wachdog fun minimum evry 20s or the bord will restart itself
            # print('auarer lock')
            fun_timer(None, websocket)
        
def fun_timer(delay, websocket):
    global current_distance
    global sliderIn
    global last_sliderPot
    global markForSave
    curt_slider = int(sliderPot.read() * 100 / 4095)
    if not (last_sliderPot == curt_slider or last_sliderPot + 1 == curt_slider or
            last_sliderPot - 1 == curt_slider):
        markForSave = True
        last_sliderPot = curt_slider
        sliderIn = curt_slider
        print('slider set to is: ', sliderIn)
        # with _chatLock:
        for ws in _chatWebSockets:
            send = {}
            send[SendData.slider] = str(sliderIn)
            try: ws.SendText(json.dumps(send))
            except: pass
    else:
        if markForSave:
            saveLastSlider(sliderIn)
            markForSave = False
    distance = calcDistance()
    if (distance > 180 and current_distance == 180): return
    if (distance > 180 and current_distance != 180):
        current_distance = 180 
    else: current_distance = distance
    # with _chatLock:
    for ws in _chatWebSockets:
        send = {}
        send[SendData.distance] = str(current_distance)
        try: ws.SendText(json.dumps(send))
        except: pass
    global ledOn
    if current_distance > sliderIn and ledOn :
        ledOn = False
        led.off()
        # with _chatLock:
        for ws in _chatWebSockets:
            send = {}
            send[SendData.led] = str(False)
            try: ws.SendText(json.dumps(send))
            except: pass
            print('ws sending led: ', False)
    elif current_distance <= sliderIn and not ledOn :
        ledOn = True
        led.on()
        # with _chatLock:
        for ws in _chatWebSockets:
            send = {}
            send[SendData.led] = str(True)
            try: ws.SendText(json.dumps(send))
            except: pass
            print('ws sending led: ', True)
    servo_distance = int(current_distance)
    servo_dist_min_move = 60
    if servo_distance > servo_dist_min_move: servo_distance = servo_dist_min_move
    servo.duty(dutyForAngle(int(servo_distance * 180/servo_dist_min_move)))
    OLED_display()
    # print('ws sending distance: ', current_distance)

def OnWSTextMsg(webSocket, msg):
    recv = json.loads(msg)
    if RecData.slider in recv:
        global sliderIn
        sliderIn = int(recv[RecData.slider])
        print('slider set to is: ', recv[RecData.slider])
        with _chatLock:
            saveLastSlider(sliderIn)
            for ws in _chatWebSockets:
                send = {}
                send[SendData.slider] = str(sliderIn)
                try: ws.SendText(json.dumps(send))
                except: pass
            OLED_display()

def OnWSClosed(webSocket) :
    _chatWebSockets.remove(webSocket)
    print("WS CLOSED")

#https://create.arduino.cc/projecthub/abdularbi17/ultrasonic-sensor-hc-sr04-with-arduino-tutorial-327ff6
def calcDistance():
    distance = 0
    arry = []
    for i in range(10):
        trigPin.off() # digitalWrite(trigPin, LOW);
        sleep_us(2) # delayMicroseconds(2);
        # Sets the trigPin on HIGH state for 10 micro seconds
        trigPin.on() # digitalWrite(trigPin, HIGH);
        sleep_us(10) # delayMicroseconds(10);
        trigPin.off() # digitalWrite(trigPin, LOW);
        # Reads the echoPin, returns the sound wave travel time in microseconds
        # calculate how mach time is on (time to go forword and back)
        duration = time_pulse_us(echoPin, 1) # pulseIn(echoPin, HIGH);
        # Calculating the distance(cm) = duration(µs) * 0.034cm/µs (speed of sound) / 2(distance is duble forword and backword)
        arry.append(duration)
        # distance += duration # *0.034/2
    arry.sort()
    median = arry[4]
    # print(arry)
    send = int(median * 0.034 / 2)
    global lastDistances
    lastDistances.pop()
    lastDistances.insert(0, send)
    _lastDistances = lastDistances.copy()
    _lastDistances.sort()  
    send = _lastDistances[int(len(_lastDistances)/2)] # median of last 3 readings
    # print('sending: ', send)
    return send # distace in (cm)

def OLED_display():
    oled.fill(0)
    oled.text('Distance System!', 0, 0) # 16 lines
    oled.text('Distance is: ' + str(current_distance), 0, 10)
    oled.text('Distance Set ' + str(sliderIn), 0, 20)
    oled.text('Alarm is ' + ("ON" if ledOn else "OFF"), 0, 30)
    oled.show()

def saveLastSlider(sliderIn: int):
    data = settings.readFromDataFile()
    try: 
        jsonData = json.loads(data)
        jsonData[RecData.slider] = sliderIn
        if not simulation: settings.saveToDataFile(json.dumps(jsonData))
    except:
        send = {}
        send[RecData.slider] = sliderIn
        if not simulation: settings.saveToDataFile(json.dumps(send))

def readLastSlider():
    data = settings.readFromDataFile()
    sliderIn = None
    try: 
        jsonData = json.loads(data)
        if RecData.slider in jsonData:
            sliderIn = int(jsonData[RecData.slider])
        else: sliderIn = 25
    except:
        sliderIn = 25
    return sliderIn

class SendData :
    distance = 'distance'
    led = 'led'
    slider = 'slider'

class RecData:
   slider = 'slider' 

