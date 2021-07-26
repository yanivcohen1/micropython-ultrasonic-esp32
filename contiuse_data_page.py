from microWebSrv.microWebSrv import MicroWebSrv
import json
# from time import sleep
from _thread import allocate_lock  # ,start_new_thread
from machine import Pin, Timer
from events_data_page import _chatLock
from   _thread     import start_new_thread
from time import sleep

global _chatWebSockets
_chatWebSockets = [ ]

timer0 = Timer(0)
# timer0.deinit() # destroy timer
led = Pin(5, Pin.OUT, value=1)
# btn = Pin(0, Pin.IN)
# led.value(1)
# led.off()  # the opesit on is off and off in on
firstLoad = True
print('contiuse_data page load')

# -----------------------------------------------------------

def btn_change(pin):
    cur_btn = 1 # btn.value()
    with _chatLock:
        for ws in _chatWebSockets:
            send = {}
            send['btn'] = str(cur_btn == 1)
            try: ws.SendText(json.dumps(send))
            except: pass
            print('ws sending: ', cur_btn)

    if cur_btn == 1:  # btn is not press
        print('btn not pressed')
    else:
        print('btn pressed')

# btn.irq(btn_change)

# ----------------------------------------------------------------------------

def WSJoinChat(webSocket, addr):
    webSocket.RecvTextCallback = OnWSChatTextMsg
    # webSocket.RecvBinaryCallback = _recvBinaryCallback
    webSocket.ClosedCallback = OnWSChatClosed
    # addr = webSocket.Request.UserAddress
    with _chatLock:
        for ws in _chatWebSockets:
            print('<%s:%s HAS JOINED THE CHAT>' % addr)
        _chatWebSockets.append(webSocket)
        print('<WELCOME %s:%s>' % addr)
    # For looping see swTimerServer.py
    try:
        global firstLoad
        if firstLoad:
	        start_new_thread(cb_thread, (3, webSocket))
	        firstLoad = False
    except:
        print ("Error: unable to start thread")
	# OR Using the HW Timer
	# from machine import Onewire, RTC, Timer
	# cb = lambda timer: cb_timer(timer, webSocket)
	# Init and start timer to poll evry 3 sec temperature sensor
	# tm = Timer(0)
	# tm.init(period=3000, callback=cb)

# for sending in timer the results in time period
def cb_thread(delay_sec, websocket):
    while True: 
        sleep(delay_sec)
        #Read data from sensors and Store in dict
        #Convert dictionary data to JSON and send
        curt_btn = 1 # btn.value()
        with _chatLock:
            for ws in _chatWebSockets:
                send = {}
                send['btn'] = str(curt_btn == 1)
                try: ws.SendText(json.dumps(send))
                except: pass
                # print('ws sending: ', curt_btn)

def OnWSChatTextMsg(webSocket, msg):
    print('msg is: ', msg)
    recv = json.loads(msg)
    if 'blink' in recv and not recv['blink']:
        timer0.deinit()
        led1(str(recv['led']))
    elif 'blink' in recv and recv['blink']:
        cb = lambda timer: cb_timer(timer, webSocket)
        # Init and start timer to poll temperature sensor
        timer0.init(period=3000, callback=cb)

def cb_timer(timer, webSocket):
    led1('True')
    sleep(1)
    led1('False')


def led1(status):
    if  status == 'False':
        led.on()
    else:
        led.off()
    print('led is: ', status)
    with _chatLock:
        for ws in _chatWebSockets:
            send = {}
            send['led'] = str(status == 'True')
            try: ws.SendText(json.dumps(send))
            except: pass
            # ws.SendText('{"led": "'+ str(args['status'] == 'false')+'"}')
            print('ws sending: ', status == 'True')

def OnWSChatClosed(webSocket) :
    _chatWebSockets.remove(webSocket)
    print("WS CLOSED")
# ============================================================================
