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
    
    def printConfig(self, config):
        for k, v in config.items():
            print(k, v)
    
    def main(self):
        serialName = '/dev/cu.usbmodem21101'
        com1 = enlace(serialName)
        com1.enable()

        contador = 0
        ocioso = True
        print("Estou ocioso!")

        while ocioso: 
            if ocioso and com1.rx.getBufferLen() >= 9:
                print('\n Mensagem 1 Recebida, aguardando verificação \n')
                # Message 1 received
                head = com1.getData(9)[0]
                EOP = com1.getData(com1.rx.getBufferLen())[0][-4:]
                if integer(head[0]) == 1 and integer(head[1]) == self.serverID and EOP == b'\xaa\xbb\xcc\xdd':
                    print("Verificado com sucesso:")
                    print("h0 recebido igual ao esperado (1)")
                    print("h1 recebido igual ao esperado (17) \n")
                    print("EOP recebido igual ao esperado (b'\xaa\xbb\xcc\xdd')")
                    ocioso = False
                else:
                    print("Erro na Verificação do handshake: ") 
                    print("h0 recebido: " + str(integer(head[0])) + "\n h0 esperado: 1")
                    print()
                    print("h1 recebido: " + str(integer(head[1])) + "\n h0 esperado: 17")
                    print()
                    print("EOP recebido: " + str(EOP) + "\n EOP esperado: b'\xaa\xbb\xcc\xdd'")
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

        print("-------------------------")
        print("Mensagem 0 enviada: ")
        self.printConfig(config)
        print("-------------------------")

        contador +=1 
        message=[0,0,0,0,0,0,0,0,0,0]
        while contador <= head[3]:
            timeout_limit_1 = time.time()
            timeout_limit_2 = time.time() 
            if com1.rx.getBufferLen() >= 9:
                print("--------------------------------------------------")
                print("\nMENSAGEM RECEBIDA: ")
                message = com1.getData(com1.rx.getBufferLen())[0]
                print(message)
                print("--------------------------------------------------")
                print()

                if self.verifyType3(message[0:10], contador-1, len(message)-10-4) and message[-4:] == b'\xaa\xbb\xcc\xdd':
                    print("--------------------------------------------------")
                    print('PACKET RECEBIDO CONFORME ESPERADO!')
                    # packet ok
                    config = {
                    'messageType': 4,
                    'serverID': 17,
                    'totalNumberOfPackets': integer(message[3]),
                    'packetID': contador,
                    'fileID': 0,
                    'lastSuccessfulPacket': contador-1,
                    }
                    p = Packet(b'', config)
                    contador+=1
                else: 
                    print("--------------------------------------------------")
                    print('PACKET RECEBIDO DIFERNTE DO ESPERADO!')
                    #packet not ok
                    config = {
                    'messageType': 6,
                    'serverID': 17,
                    'totalNumberOfPackets': integer(message[3]),
                    'packetID': contador,
                    'fileID': 0,
                    'lastSuccessfulPacket': contador-1,
                    'resendPacket': integer(message[4])
                    }
                    p = Packet(b'', config)
                com1.sendData(p)
                print("MENSAGEM ENVIADA: ")
                self.printConfig(config)
                print("--------------------------------------------------")
                
            else: 
                print("MENSAGEM NÃO RECEBIDA\n")
                time.sleep(1)
                if time.time() - timeout_limit_2 > 20: 
                    ocioso = True
                    print("------------ TIMER 2 PASSOU DE 20 SEGUNDOS ------------")
                    config = {
                    'messageType': 5,
                    'serverID': 17,
                    'totalNumberOfPackets': integer(message[3]),
                    'packetID': contador,
                    'fileID': 0,
                    'lastSuccessfulPacket': contador-1,
                    'resendPacket': integer(message[4])
                    }
                    p = Packet(b'', config)
                    com1.sendData(p)

                    print("TEMPO ESGOTADO, mensagem tipo 5 enviada")
                    self.printConfig(config)
                    exit()

                elif time.time() - timeout_limit_1 > 2:
                    print("ZERANDO TIMER 1 SEI LA PRA QUE!!!!!!!!!!!")
                    print("Nao vou mandar mensagem porra nenhuma porque nao faz sentido enviar tipo 4")
                    timeout_limit_1 = time.time()

                    
s = Server(17)
Server.main()




