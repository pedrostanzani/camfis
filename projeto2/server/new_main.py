from core.enlace import enlace
from time import sleep
import numpy as np

c = {
    1: [0x00, 0x00, 0x00, 0x00],
    2: [0x00, 0x00, 0xBB, 0x00],
    3: [0xBB, 0x00, 0x00],
    4: [0x00, 0xBB, 0x00],
    5: [0x00, 0x00, 0xBB],
    6: [0x00, 0xAA],
    7: [0xBB, 0x00],
    8: [0x00],
    9: [0xBB]
}

protocol_translator = {
    1: (4, 4),
    2: (4, 3),
    3: (4, 2),
    4: (4, 1),
    5: (3, 4),
    6: (3, 3),
    7: (3, 2),
    8: (3, 1),
    9: (2, 4),
    10: (2, 3),
    11: (2, 2),
    12: (2, 1),
    13: (1, 4),
    14: (1, 3),
    15: (1, 2),
    16: (1, 1),
}

def commandTranslator(command):
    for n in c.keys():
        if bytearray(c[n]) == command:
            return n

serialName = '/dev/cu.usbmodem1101'
com1 = enlace(serialName)
com1.enable()
print("esperando 1 byte de sacrifício") 
rxBuffer, nRx = com1.getData(1) 
com1.rx.clearBuffer()
sleep(.1)

def split(byteInicial):
    return protocol_translator[byteInicial]

#rxBuffer, nRx = com1.getData(32)
commandList = []
while True:
    rxBuffer, nRx = com1.getData(1)
    control_integer = int.from_bytes(rxBuffer, byteorder='big')
    if control_integer > 16:
        break

    rxBuffer, nRx = com1.getData(split(control_integer)[0])
    commandList.append(commandTranslator(rxBuffer))
    rxBuffer, nRx = com1.getData(split(control_integer)[1])
    if int.from_bytes(rxBuffer, byteorder='big') == 255:
        break
    commandList.append(commandTranslator(rxBuffer))
    print(rxBuffer)

print("Comandos recebidos: " + str(commandList))


print("recebeu {} bytes" .format(len(rxBuffer)))
# for i in range(len(rxBuffer)):
#     print("recebeu {}" .format(rxBuffer[i]))


com1.sendData(np.asarray(bytearray([1, len(commandList), 255])))  

print(str(len(commandList)) + " é a quantidade de comandos recebidos")

print("-------------------------")
print("Comunicação encerrada")
print("-------------------------")
print()
exit()

#   Geralmente os protocolos tem um head no começo e um EOP (end of program) no final, apenas
#   Não há bytes jogados no meio do programa. Nesse exemplo acima, o protocolo que nos criamos envia um byte
# a cada dois comandos. Isso deveria ser feito tudo no começo, utilizando o byte de forma mais completa, talvez sub-
# dividindo os bytes e evitando envio de bytes de protocolo soltos no meio da mensagem.