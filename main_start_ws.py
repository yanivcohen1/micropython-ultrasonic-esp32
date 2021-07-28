
from microWebSrv.microWebSrv import MicroWebSrv
import json
# from time import sleep
from   _thread   import allocate_lock # ,start_new_thread
from events_data_page import WSJoinChat as MyWSJoinChat
from events_data_page import _chatLock, routeHandlers
import socket
# for ultrasonic page auto load
# from ultrasonic_page import WSJoin as ultrasonicWSJoin 	
# ultrasonicWSJoin(None, None) # for page auto load	

global _chatWebSockets
_chatWebSockets = [ ]

@MicroWebSrv.route('/test-redir')
def _httpHandlerTestGet(httpClient, httpResponse):
	httpResponse.WriteResponseRedirect('/pdf.png')

# ----------------------------------------------------------------------------

# test get page [/test-post]
@MicroWebSrv.route('/test-post')
def _httpHandlerTestGet(httpClient, httpResponse):
	content = """\
	<!DOCTYPE html>
	<html lang=en>
        <head>
        	<meta charset="UTF-8" />
            <title>TEST GET</title>
        </head>
        <body>
            <h1>TEST GET</h1>
            Client IP address = %s
            <br />
			<form action="/test-post" method="post" accept-charset="ISO-8859-1">
				First name: <input type="text" name="firstname"><br />
				Last name: <input type="text" name="lastname"><br />
				<input type="submit" value="Submit">
			</form>
        </body>
    </html>
	""" % httpClient.GetIPAddr()
	httpResponse.WriteResponseOk(headers=None,
								  contentType="text/html",
								  contentCharset="UTF-8",
								  content=content)

# ----------------------------------------------------------------------------

# test post data [/test-post]
@MicroWebSrv.route('/test-post', 'POST')
def _httpHandlerTestPost(httpClient, httpResponse):
	formData = httpClient.ReadRequestPostedFormData()
	firstname = formData["firstname"]
	lastname = formData["lastname"]
	content = """\
	<!DOCTYPE html>
	<html lang=en>
		<head>
			<meta charset="UTF-8" />
            <title>TEST POST</title>
        </head>
        <body>
            <h1>TEST POST</h1>
            Firstname = %s<br />
            Lastname = %s<br />
        </body>
    </html>
	""" % (MicroWebSrv.HTMLEscape(firstname),
		    MicroWebSrv.HTMLEscape(lastname))
	httpResponse.WriteResponseOk(headers=None,
								  contentType="text/html",
								  contentCharset="UTF-8",
								  content=content)

# ----------------------------------------------------------------------------

# test get query parameters [/send?name=yaniv&last=cohen]
@MicroWebSrv.route('/send')
def _httpHandlerEditWithArgs(httpClient, httpResponse):
	args = httpClient.GetRequestQueryParams()
	# print('QueryParams', args)
	content = """\
	<!DOCTYPE html>
	<html lang=en>
        <head>
        	<meta charset="UTF-8" />
            <title>TEST EDIT</title>
        </head>
        <body>
	"""
	content += "<h1>EDIT item with {} query arguments</h1>".format(len(args))
	if 'name' in args:
		content += "<p>name = {}</p>".format(args['name'])

	# if 'last' in args :
	#	content += "<p>last name = {}</p>".format(args['last'])

	for key in args:
		if key != "name": content += "<p>{key} = {val}</p>".format(
		    key=key, val=args[key])

	content += """
        </body>
    </html>
	"""
	httpResponse.WriteResponseOk(headers=None,
								  contentType="text/html",
								  contentCharset="UTF-8",
								  content=content)

# ----------------------------------------------------------------------------

# test path variable [see comments]
# <IP>/edit/123           ->   args['index']=123
@MicroWebSrv.route('/edit/<index>')
# <IP>/edit/123/abc/bar   ->   args['index']=123  args['foo']='bar'
@MicroWebSrv.route('/edit/<index>/abc/<foo>')
# <IP>/edit               ->   args={}
@MicroWebSrv.route('/edit')
def _httpHandlerEditWithArgs(httpClient, httpResponse, args={}):
	content = """\
	<!DOCTYPE html>
	<html lang=en>
        <head>
        	<meta charset="UTF-8" />
            <title>TEST EDIT</title>
        </head>
        <body>
	"""
	content += "<h1>EDIT item with {} variable arguments</h1>".format(len(args))

	if 'index' in args:
		content += "<p>index = {}</p>".format(args['index'])

	if 'foo' in args:
		content += "<p>foo = {}</p>".format(args['foo'])

	content += """
        </body>
    </html>
	"""

	httpResponse.WriteResponseOk(headers=None,
								  contentType="text/html",
								  contentCharset="UTF-8",
								  content=content)

# ----------------------------------------------------------------------------

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

def _recvTextCallback(webSocket, msg) :
	print("WS RECV TEXT : %s" % msg)
	webSocket.SendText("Reply for %s" % msg)

def _recvBinaryCallback(webSocket, data) :
	print("WS RECV DATA : %s" % data)

def _closedCallback(webSocket) :
	print("WS CLOSED")



# for sending in timer the results in time period
# def cb_timer(delay_sec, websocket): 
	# time.sleep(delay_sec)
    # Read data from sensors and Store in dict
    # Convert dictionary data to JSON and send
    # websocket.SendText(json.dumps(dict))
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
