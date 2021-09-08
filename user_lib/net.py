
import network
from user_lib.encryption import decrypt

sta_if = network.WLAN(network.STA_IF)
if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect("ssid-name", decrypt(b'C\xfdC\xe10>\xf9\xc4i\x88Da?\xd4\x82\x86'))
        while not sta_if.isconnected():
            pass

print('network config:', sta_if.ifconfig())


