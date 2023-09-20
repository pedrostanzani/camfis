import time
import numpy as np
from core.enlace import enlace
from packet import Packet

# --------------------------------------------------------------------------------------------------
# byte para int: int. from_bytes() -------- z = b'\x00\x00\x00\x00\x00\x01'; int.from_bytes(z,'big')
# int para bytestring: int. to_bytes() ---- h = 1; h = h.to_bytes(6,'big')
#   python -m serial.tools.list_ports
# --------------------------------------------------------------------------------------------------

def integer(b):
    return int.from_bytes(b, 'big')
def byte(i, n):
    return i.to_bytes(n, 'big')


class Server:

    def __init__(self, serverID):
        self.serverID = serverID
        self.LIST = []

    def verifyType3(self, head, lr, payload_length):
        # lr = last received
        if integer(head[0]) == 3 and integer(head[4]) == lr+1 and payload_length==integer(head[5]) and integer(head[7]) == lr:
            return True
        else: 
            return False
    
    def main(self):
        serialName = '/dev/cu.usbmodem21101'
        com1 = enlace(serialName)
        com1.enable()

        contador = 0
        ocioso = True

        while ocioso: 
            if ocioso and com1.rx.getBufferLen() >= 9:
                # Message 1 received
                head = com1.getData(9)
                if integer(head[0]) == 1 and integer(head[1]) == self.serverID:
                    ocioso = False
                else: 
                    time.sleep(1)
        
        # ocioso = False: 
        config = {
        'messageType': 2,
        'serverID': 17,
        'totalNumberOfPackets': 0,
        'packetID': contador,
        'fileID': 0,
        'lastSuccessfulPacket': 0,
        }
        message1 = Packet(b'', config)
        com1.sendData(message1)

        contador +=1 
        message=[0,0,0,0,0,0,0,0,0,0]
        while contador <= head[3]:
            timeout_limit_1 = time.time()
            timeout_limit_2 = time.time() 
            if com1.rx.getBufferLen() >= 9:
                message = com1.getData(com1.rx.getBufferLen())
                if self.verifyType3(message[0:10], contador-1, len(message)-10-4):
                    # packet ok
                    config = {
                    'messageType': 4,
                    'serverID': 17,
                    'totalNumberOfPackets': integer(message[4]),
                    'packetID': contador,
                    'fileID': 0,
                    'lastSuccessfulPacket': contador-1,
                    }
                    p = Packet(b'', config)
                    contador+=1
                else: 
                    #packet not ok
                    config = {
                    'messageType': 6,
                    'serverID': 17,
                    'totalNumberOfPackets': integer(message[4]),
                    'packetID': contador,
                    'fileID': 0,
                    'lastSuccessfulPacket': contador-1,
                    }
                    p = Packet(b'', config)





