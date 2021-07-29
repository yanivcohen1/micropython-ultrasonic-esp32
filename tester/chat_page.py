from events_data_page import _chatLock

global _chatWebSockets
_chatWebSockets = [ ]

def WSJoinChat(webSocket, addr) :
    webSocket.RecvTextCallback = OnWSChatTextMsg
    # webSocket.RecvBinaryCallback = _recvBinaryCallback
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