from microWebSrv.microWebSrv import MicroWebSrv
import json
# from time import sleep
from _thread import allocate_lock  # ,start_new_thread
from machine import Pin, ADC
from events_data_page import _chatLock , routeHandlers
from   _thread     import start_new_thread
from time import sleep

global _chatWebSockets
_chatWebSockets = [ ]

led = Pin(5, Pin.OUT, value=1)
slider = ADC(Pin(34))
slider.atten(ADC.ATTN_11DB)       #Full range: 3.3v
# led.value(1)
# led.off()
firstLoad = True
print('boiler page load')
sliderIn = 1
ledOn = False
last_slider = 1
last_temp = 0
# ----------------------------------------------------------------------------
# in comment to not upload all page on the web load
# @MicroWebSrv.route('/boiler')
# def _httpHandlerEditWithArgs(httpClient, httpResponse):
#     args = httpClient.GetRequestQueryParams()
#     # print('QueryParams', args)
#     content = ""
#     if 'value' in args:
#         global sliderIn
#         sliderIn = args['value']
#         print('slider set to is: ', args['value'])
#     httpResponse.WriteResponseOk(headers=None,
#                                  contentType="text/html",
#                                  contentCharset="UTF-8",
#                                  content=content)

# routeHandlers.insert(0, ( "/boiler",	"GET",	_httpHandlerEditWithArgs ))

# ----------------------------------------------------------------------------

def WSJoinChat(webSocket, addr):
    webSocket.RecvTextCallback = OnWSChatTextMsg
    # webSocket.RecvBinaryCallback = _recvBinaryCallback
    webSocket.ClosedCallback = OnWSChatClosed
    # addr = webSocket.Request.UserAddress
    with _chatLock:
        print('<%s:%s HAS JOINED THE CHAT>' % addr)
        send = {}
        send[SendData.slider] = str(sliderIn)
        try: webSocket.SendText(json.dumps(send))
        except: pass
        _chatWebSockets.append(webSocket)
        print('<WELCOME %s:%s>' % addr)
    # For looping see swTimerServer.py
    try:
        global firstLoad
        if firstLoad:
	        start_new_thread(cb_timer, (3, webSocket))
	        firstLoad = False
    except:
        print ("Error: unable to start thread")
	# OR Using the HW Timer
	# from machine import Onewire, RTC, Timer
	# cb = lambda timer: cb_timer(timer, webSocket)
	# Init and start timer to poll evry 3 sec temperature sensor
	# tm = Timer(0)
	# tm.init(period=3000, callback=cb)

def OnWSChatClosed(webSocket) :
    _chatWebSockets.remove(webSocket)
    print("WS CLOSED")
    
# for sending in timer the results in time period
def cb_timer(delay_sec, websocket):
    while True: 
        sleep(delay_sec)
        #Read data from sensors and Store in dict
        #Convert dictionary data to JSON and send
        curt_slider = slider.read()
        with _chatLock:
            for ws in _chatWebSockets:
                send = {}
                send[SendData.temp] = str(curt_slider)
                try: ws.SendText(json.dumps(send))
                except: pass
                print('ws sending temp: ', curt_slider)
        global ledOn
        if curt_slider > sliderIn and ledOn :
            with _chatLock:
                for ws in _chatWebSockets:
                    send = {}
                    send[SendData.led] = str(False)
                    try: ws.SendText(json.dumps(send))
                    except: pass
                    print('ws sending led: ', False)
                    ledOn = False
                    led.on()
        elif curt_slider <= sliderIn and not ledOn :
            with _chatLock:
                for ws in _chatWebSockets:
                    send = {}
                    send[SendData.led] = str(True)
                    try: ws.SendText(json.dumps(send))
                    except: pass
                    print('ws sending led: ', True)
                    ledOn = True
                    led.off()

def OnWSChatTextMsg(webSocket, msg):
    recv = json.loads(msg)
    if RecData.temp in recv:
        global sliderIn
        sliderIn = int(recv[RecData.temp])
        print('slider set to is: ', recv[RecData.temp])
        with _chatLock:
            for ws in _chatWebSockets:
                send = {}
                send[SendData.slider] = str(sliderIn)
                try: ws.SendText(json.dumps(send))
                except: pass

# =============================================================================

class SendData :
    temp = 'temp'
    led = 'led'
    slider = 'slider'

class RecData:
   temp = 'temp' 

