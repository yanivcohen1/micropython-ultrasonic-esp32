import os
try:
    os.remove("machine.py")
except :
    pass
    # print ("machine not exist")
print (os.listdir())
import user_lib.net
import main_start_ws