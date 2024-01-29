import serial.tools.list_ports as port_list
from time import sleep
from relay_ft245r import Relay

if __name__ =="__main__": 
    
    relay= Relay()
    #atexit.register(relay.__close__())

    relay.write("1")