from microWebSrv.microWebSrv import MicroWebSrv
import json
# from time import sleep
from _thread import allocate_lock  # ,start_new_thread
# C:\Users\yaniv\AppData\Local\Programs\Thonny\Lib\site-packages\thonny\plugins\micropython\api_stubs
from machine import Pin

routeHandlers = []
#	( "/test",	"GET",	_httpHandlerTestGet ),
#	( "/test",	"POST",	_httpHandlerTestPost )
# ]

led = Pin(5, Pin.OUT, value=1) # 1, Pin.PULL_UP
# btn = Pin(0, Pin.IN) # Pin.PULL_UP
# led.value(1)
# led.off()  # the opesit on is off and off in on

print('events_data page load')

global _chatWebSockets
_chatWebSockets = [ ]

global _chatLock
_chatLock = allocate_lock()

global res

def btn_change(pin):
    cur_btn = 1 # btn()
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

# test get query parameters [/send?name=yaniv&last=cohen]
@MicroWebSrv.route('/led')
def _httpHandlerEditWithArgs(httpClient, httpResponse):
    args = httpClient.GetRequestQueryParams()
    # print('QueryParams', args)
    content = ""
    if 'status' in args:
        if args['status'] == 'false':
            led.on()
        else:
            led.off()
        print('led is: ', args['status'])
        with _chatLock:
            for ws in _chatWebSockets:
                send = {}
                send['led'] = str(args['status'] == 'false')
                try: ws.SendText(json.dumps(send))
                except: pass
                # ws.SendText('{"led": "'+ str(args['status'] == 'false')+'"}')
                print('ws sending: ', args['status'] == 'false')
    httpResponse.WriteResponseOk(headers=None,
                                 contentType="text/html",
                                 contentCharset="UTF-8",
                                 content=content)

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

def OnWSChatTextMsg(webSocket, msg):
    print('msg is: ', msg)
    recv = json.loads(msg)
    if 'msg' in recv:
        msgIn = recv['msg']
        print('msg is: ', msgIn)
        global res
        res = None
        exec(msgIn)
        if res != None:
            print('res is: ', res)
            send = {}
            send['res'] = str(res)
            try: webSocket.SendText(json.dumps(send))
            except: pass

def OnWSChatClosed(webSocket) :
    _chatWebSockets.remove(webSocket)
    print("WS CLOSED")
# ============================================================================
