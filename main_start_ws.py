
from microWebSrv.microWebSrv import MicroWebSrv
import json
# from time import sleep
from   _thread   import allocate_lock # ,start_new_thread
from events_data_page import WSJoinChat as MyWSJoinChat
from events_data_page import _chatLock, routeHandlers
import socket
import tester.tester_page
# for ultrasonic page auto load
# from ultrasonic_page import WSJoin as ultrasonicWSJoin 	
# ultrasonicWSJoin(None, None) # for page auto load	

global _chatWebSockets
_chatWebSockets = [ ]

# test web socket [/wstest.html]
def _acceptWebSocketCallback(webSocket, httpClient):
	print('Example WebSocket accepted:')
	print('   - User   : %s:%s' % (httpClient.GetAddr()[0], httpClient.GetAddr()[1]))
	print('   - Path   : %s'    % httpClient.GetRequestTotalPath())
	# print('   - Origin : %s'    % webSocket.Request.Origin)
	if httpClient.GetRequestTotalPath().lower() == '/wschat' :
	    WSJoinChat(webSocket, httpClient.GetAddr())
	elif httpClient.GetRequestTotalPath().lower() == '/wstest' :
		webSocket.RecvTextCallback   = _recvTextCallback
		webSocket.RecvBinaryCallback = _recvBinaryCallback
		webSocket.ClosedCallback 	 = _closedCallback
	elif httpClient.GetRequestTotalPath().lower() == '/events_data_page' :
		MyWSJoinChat(webSocket, httpClient.GetAddr())
	elif httpClient.GetRequestTotalPath().lower() == '/contineuse-data-read' :
		from contiuse_data_page import WSJoinChat as ContiuseWSJoinChat
		ContiuseWSJoinChat(webSocket, httpClient.GetAddr())
	elif httpClient.GetRequestTotalPath().lower() == '/boiler' :
		from boiler_page import WSJoinChat as BoilerWSJoinChat
		BoilerWSJoinChat(webSocket, httpClient.GetAddr())
	elif httpClient.GetRequestTotalPath().lower() == '/ultrasonic_page' :
		from ultrasonic_page import WSJoin as ultrasonicWSJoin
		ultrasonicWSJoin(webSocket, httpClient.GetAddr())     
	# For looping see swTimerServer.py
	# _thread.start_new_thread(cb_timer, (3, webSocket)
	# OR Using the HW Timer
	# from machine import Onewire, RTC, Timer
	# cb = lambda timer: cb_timer(timer, webSocket)
	# Init and start timer to poll evry 3 sec temperature sensor
	# tm = Timer(0)
	# tm.init(period=3000, callback=cb)

	# for sending in timer the results in time period
	# def cb_timer(delay_sec, websocket): 
	# time.sleep(delay_sec)
    # Read data from sensors and Store in dict
    # Convert dictionary data to JSON and send
    # websocket.SendText(json.dumps(dict))

def _recvTextCallback(webSocket, msg) :
	print("WS RECV TEXT : %s" % msg)
	webSocket.SendText("Reply for %s" % msg)

def _recvBinaryCallback(webSocket, data) :
	print("WS RECV DATA : %s" % data)

def _closedCallback(webSocket) :
	print("WS CLOSED")

# ----------------------------------------------------------------------------


# routeHandlers = [
#	( "/test",	"GET",	_httpHandlerTestGet ),
#	( "/test",	"POST",	_httpHandlerTestPost )
# ]

# ============================================================================

def WSJoinChat(webSocket, addr) :
    webSocket.RecvTextCallback = OnWSChatTextMsg
    webSocket.RecvBinaryCallback = _recvBinaryCallback
    webSocket.ClosedCallback      = OnWSChatClosed
    with _chatLock :
        for ws in _chatWebSockets :
            ws[0].SendText('<%s:%s HAS JOINED THE CHAT>' % addr) # ws[1] self addr
        _chatWebSockets.append([webSocket, addr])
        webSocket.SendText('<WELCOME %s:%s>' % addr)

def OnWSChatTextMsg(webSocket, msg) :
    # addr = _calcAddr(webSocket) # webSocket.Request.UserAddress
	addr = None
	for ws in _chatWebSockets :
		if ws[0] == webSocket: addr=ws[1]
	with _chatLock :
		for ws in _chatWebSockets :
			ws[0].SendText('<%s:%s> %s' % (addr[0], addr[1], msg)) # ws[1][0], sw[1][1] self addr

def OnWSChatClosed(webSocket) :
    # addr =  _calcAddr(webSocket) # webSocket.Request.UserAddress
	addr = None
	for ws in _chatWebSockets :
		if ws[0] == webSocket: addr=ws[1]
	with _chatLock :
		if webSocket in _chatWebSockets :
			_chatWebSockets.remove(webSocket)
			for ws in _chatWebSockets :
				ws[0].SendText('<%s:%s HAS LEFT THE CHAT>' % addr) # ws[1] self addr

def _calcAddr(webSocket):
	addr= str(webSocket._socket)
	x = addr.find("raddr=('") + 8
	y= addr[x:]
	z = y.find("'")
	host=addr[x:x+z]
	y= addr[x+z:]
	z = y.find(")")
	port=y[3:z]
	return [host, port]

# ============================================================================

srv = MicroWebSrv(webPath='www/', routeHandlers=routeHandlers) # port=<portNumber> default is 80
srv.MaxWebSocketRecvLen     = 500
srv.WebSocketThreaded		= True
srv.AcceptWebSocketCallback = _acceptWebSocketCallback
print('running WebServer')
# control+C press
srv.Start(threaded=False) 
""" try : # srv.Start(threaded=True)
    while True :
        sleep(2)
except KeyboardInterrupt : # control+C press
    pass """
print('stopping server and cleanup')
srv.Stop()
# ----------------------------------------------------------------------------
