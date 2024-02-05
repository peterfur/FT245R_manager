import datetime
import serial
import serial.tools.list_ports as port_list
import io
from time import sleep
import json
import os
import ftd2xx as ftd


class Relay():
    def __init__(self,relay="FT245R",mode="json",config=os.path.dirname(os.path.abspath(__file__))+'\\config.json'):
        self.initialize_modem()

        # relay turn on on bit format (relay 1, relay2, relay3... relay 8)
        # On config only put the first 4 settings, because they will duplicate
        # to secure that CANL and CANH go to the same objective and make it more robust

        self.data= {
        "FT245R":{
            "IVI":"OFF OFF OFF OFF",
            "IVC":"OFF ON OFF OFF",
            "METER":"ON OFF OFF OFF",
            "SGW":"ON OFF ON OFF"
        }
        }
        if mode=="dic":
            #load configuration from variable

            self.configure_dic(self.data,relay)
        else:
            #load configuration from json file
            self.configure_json(config)            

    def initialize_modem(self):
        self.ports=list(port_list.comports())
        #load with ftd library to set bitbang mode
        self.ftd= ftd.open(0)
        self.ftd.setBitMode(0xFF,0x1)
        self.ftd.close()

        for x in self.ports:
            print(f'{x.device} : {x.description}' )

        index = self.getModemIndex(self.ports)
        self.port = self.ports[index].device
        self.modem= serial.Serial(port=self.port,baudrate=9600, timeout=2)
        print("Wellcome 2 -> "+str(self.ports[index]))

    def getModemIndex(self,_ports):
        i=0
        for x in _ports:
            if "USB Serial Port" in x.description:
                return i
            i=i+1
        return -1

    def configure_dic(self,data,relay):
        self.__set_relay__(data,relay)
        self.verify_data(relay)

    
    def configure_json(self,json_path,relay="FT245R"):
        with open(json_path) as json_file:
            self.data = json.load(json_file)
            print(self.data)
            self.__set_relay__(self.data,relay)
            json_file.close()
        self.verify_data(relay)


    def write(self,item="IVI"):
        on_off= self.relay[str(item)].split()
        self.message=""
        for x in on_off:
            if x=="ON":
                self.message+="1"
            elif x=="OFF":
                self.message +="0"
            else:
                print("bad format, only accept ON or OFF: text detected ",x)
        self.message+=self.message
        self.modem.write(bytes([0x0,0x18,0xF3,int(self.message[::-1], 2)]))
    
    def verify_data(self,relay):
        rev_dict = {}
        for key, value in self.data[relay].items():
            rev_dict.setdefault(value, set()).add(key)
            
        result = [key for key, values in rev_dict.items()
                                    if len(values) > 1]        
        if result!=[]:
            print("WARNING, duplicated values!! ",result)

    def __set_relay__(self,data, name):
        self.relay=data[name]
        return self.relay
    
    def __close__(self):
        self.modem.close()
