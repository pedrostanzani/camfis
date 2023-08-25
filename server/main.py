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

#rxBuffer, nRx = com1.getData(32)
commandList = []
while True:
    rxBuffer, nRx = com1.getData(1)
    control_integer = int.from_bytes(rxBuffer, byteorder='big')
    if control_integer > 16:
        break

    rxBuffer, nRx = com1.getData(control_integer)
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