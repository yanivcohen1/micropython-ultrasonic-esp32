
import network
from user_lib.encryption import decrypt

sta_if = network.WLAN(network.STA_IF)
if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect("SSID-name", decrypt(b'C\xfcC\xe00>\xf7\xc2i\x87Da?\xd1\x83\x84'))
        while not sta_if.isconnected():
            pass

print('network config:', sta_if.ifconfig())


