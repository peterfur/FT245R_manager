from relay_ft245r import Relay

if __name__ =="__main__": 
    
    relay= Relay()
    #atexit.register(relay.__close__())

    relay.write("1")
