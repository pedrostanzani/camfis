from core.enlace import enlace

from time import sleep

serialName = '/dev/cu.usbmodem1101'
com1 = enlace(serialName)
com1.enable()


rxBuffer, nRx = com1.getData(1024)
print("recebeu {} bytes" .format(len(rxBuffer)))
for i in range(len(rxBuffer)):
    print("recebeu {}" .format(rxBuffer[i]))
print("-------------------------")
print("Comunicação encerrada")
print("-------------------------")
# com1.disable()

# import numpy as np
# from core.enlace import enlace

# serialName = "/dev/tty.usbmodem1101"

# com1 = enlace(serialName)
# com1.enable()
# txBuffer = bytearray([22, 23, 34, 45, 50, 2])
# com1.sendData(np.asarray(txBuffer))

# while com1.tx.threadMutex:
#     pass
# txSize = com1.tx.getStatus()
# print('enviou = {}' .format(txSize))

# # ===================================================

# rxBuffer, nRx = com1.getData(6)
# print("recebeu {} bytes" .format(len(rxBuffer)))
# for i in range(len(rxBuffer)):
#     print("recebeu {}" .format(rxBuffer[i]))