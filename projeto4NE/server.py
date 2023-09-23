import time
import numpy as np
from core.enlace import enlace
from packet import Packet
from datetime import datetime

# --------------------------------------------------------------------------------------------------
# byte para int: int. from_bytes() -------- z = b'\x00\x00\x00\x00\x00\x01'; int.from_bytes(z,'big')
# int para bytestring: int. to_bytes() ---- h = 1; h = h.to_bytes(6,'big')
#   python -m serial.tools.list_ports
# --------------------------------------------------------------------------------------------------


class Server:

    def __init__(self, serverID):
        self.serverID = serverID
        self.LIST = []
    
    def integer(self, b):
        if isinstance(b, int):
            return b
        return int.from_bytes(b, 'big')
    def byte(self, i, n):
        return i.to_bytes(n, 'big')

    def verifyType3(self, head, lr, payload_length):
        # lr = last received
        if self.integer(head[0]) == 3 and self.integer(head[4]) == lr+1 and payload_length==self.integer(head[5]) and self.integer(head[7]) == lr:
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
        print("esperando 1 byte de sacrifício") 
        rxBuffer, nRx = com1.getData(1) 
        com1.rx.clearBuffer()
        time.sleep(0.1)

        contador = 0
        ocioso = True
        print("Estou ocioso!")

        while ocioso: 
            if ocioso and com1.rx.getBufferLen() >= 9:
                print('\n Mensagem 1 Recebida, aguardando verificação \n')
                # Message 1 received
                head = com1.getData(9)[0]
                EOP = com1.getData(com1.rx.getBufferLen())[0][-4:]
                t = datetime.now()
                string = f"{t.day}/{t.month}/{t.year} {t.hour}:{t.minute}:{t.second} /receb/type: {head[0]}/MessageSize: {len(head)}/TotalNumberOfPackets: {head[3]}/PacketID: {head[4]}/PayloadCRC: \n"
                self.LIST.append(string)
                if self.integer(head[0]) == 1 and self.integer(head[1]) == self.serverID and EOP == b'\xaa\xbb\xcc\xdd':
                    print("Verificado com sucesso:")
                    print("h0 recebido igual ao esperado (1)")
                    print("h1 recebido igual ao esperado (17)")
                    print("EOP recebido igual ao esperado (b'\xaa\xbb\xcc\xdd')\n")
                    ocioso = False
                else:
                    print("Erro na Verificação do handshake: ") 
                    print("h0 recebido: " + str(self.integer(head[0])) + "\n h0 esperado: 1")
                    print()
                    print("h1 recebido: " + str(self.integer(head[1])) + "\n h0 esperado: 17")
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
        com1.sendData(message1.message())
        h = message1.message()[0:10]
        t = datetime.now()
        string = f"{t.day}/{t.month}/{t.year} {t.hour}:{t.minute}:{t.second} /envio/type: {h[0]}/MessageSize: {len(h)}/TotalNumberOfPackets: {h[3]}/PacketID: {h[4]}/PayloadCRC: \n"
        self.LIST.append(string)

        print("-------------------------")
        print("Mensagem 0 enviada: ")
        self.printConfig(config)
        print("-------------------------")

        contador +=1 
        message=[0,0,0,0,0,0,0,0,0,0]
        print(h[3])
        timeout_limit_1 = time.time()
        timeout_limit_2 = time.time()
        while contador <= head[3]: 
            if com1.rx.getBufferLen() >= 9:
                timeout_limit_1 = time.time()
                timeout_limit_2 = time.time()
                print("--------------------------------------------------")
                print("\nMENSAGEM RECEBIDA: ")
                message = com1.getData(com1.rx.getBufferLen())[0]
                print(message)
                print("--------------------------------------------------")
                print()

                t = datetime.now()
                head = message[0:10]
                string = f"{t.day}/{t.month}/{t.year} {t.hour}:{t.minute}:{t.second} /receb/type: {head[0]}/MessageSize: {len(head)}/TotalNumberOfPackets: {head[3]}/PacketID: {head[4]}/PayloadCRC: \n"
                self.LIST.append(string)

                if self.verifyType3(message[0:10], contador-1, len(message)-10-4) and message[-4:] == b'\xaa\xbb\xcc\xdd':
                    print("--------------------------------------------------")
                    print('PACKET RECEBIDO CONFORME ESPERADO!')
                    # packet ok
                    config = {
                    'messageType': 4,
                    'serverID': 17,
                    'totalNumberOfPackets': self.integer(message[3]),
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
                    'totalNumberOfPackets': self.integer(message[3]),
                    'packetID': contador,
                    'fileID': 0,
                    'lastSuccessfulPacket': contador-2,
                    'resendPacket': contador
                    }
                    
                    p = Packet(b'', config)
                    print("MENSAGEM TIPO 6 ENVIADA: ")
                print([n for n in p.message()])
                com1.sendData(p.message())
                self.printConfig(config)
                print("--------------------------------------------------")

                head = p.message()[0:10]
                t = datetime.now()
                string = f"{t.day}/{t.month}/{t.year} {t.hour}:{t.minute}:{t.second} /envio/type: {head[0]}/MessageSize: {len(head)}/TotalNumberOfPackets: {head[3]}/PacketID: {head[4]}/PayloadCRC: \n"
                self.LIST.append(string)
                
            else: 
                print("MENSAGEM NÃO RECEBIDA\n")
                time.sleep(1)
                if time.time() - timeout_limit_2 > 20: 
                    ocioso = True
                    print("------------ TIMER 2 PASSOU DE 20 SEGUNDOS ------------")
                    config = {
                    'messageType': 5,
                    'serverID': 17,
                    'totalNumberOfPackets': self.integer(message[3]),
                    'packetID': contador,
                    'fileID': 0,
                    'lastSuccessfulPacket': contador-1,
                    'resendPacket': self.integer(message[4])
                    }
                    p = Packet(b'', config)
                    com1.sendData(p.message())

                    head = p.message()[0:10]
                    t = datetime.now()
                    string = f"{t.day}/{t.month}/{t.year} {t.hour}:{t.minute}:{t.second} /envio/type: {head[0]}/MessageSize: {len(head)}/TotalNumberOfPackets: {head[3]}/PacketID: {head[4]}/PayloadCRC: \n"
                    self.LIST.append(string)

                    print("TEMPO ESGOTADO, mensagem tipo 5 enviada")
                    self.printConfig(config)
                    break

                elif time.time() - timeout_limit_1 > 2:
                    
                    # Confirm the last successfully received mensage again
                    config = {
                    'messageType': 4,
                    'serverID': 17,
                    'totalNumberOfPackets': self.integer(message[3]),
                    'packetID': contador,
                    'fileID': 0,
                    'lastSuccessfulPacket': contador-1,
                    }
                    p = Packet(b'', config)
                    com1.sendData(p.message())

                    head = p.message()[0:10]
                    t = datetime.now()
                    string = f"{t.day}/{t.month}/{t.year} {t.hour}:{t.minute}:{t.second} /envio/type: {head[0]}/MessageSize: {len(head)}/TotalNumberOfPackets: {head[3]}/PacketID: {head[4]}/PayloadCRC: \n"
                    self.LIST.append(string)

                    print("--------------------------------------------------")
                    print("MENSAGEM DE CONFIRMAÇÃO ENVIADA NOVAMENTE: ")
                    self.printConfig(config)
                    print("--------------------------------------------------")
                    

        print("COMUNICAÇÃO FINALIZADA")
            

                    
s = Server(17)
s.main()

with open('serverLOG.txt', 'w') as f:
    for line in s.LIST:
        f.write(line)


