import time
import numpy as np
from core.enlace import enlace


serialName = '/dev/cu.usbmodem101'

if __name__ == '__main__':
    com1 = enlace(serialName)
    com1.enable()

    # Martyr byte
    print("Waiting for a martyr byte.")
    rxBuffer, nRx = com1.getData(1) 
    com1.rx.clearBuffer()
    time.sleep(.1)

    # Handshake
    rxBuffer, nRx = com1.getData(1)
    handshake_message = int.from_bytes(rxBuffer, byteorder='big')
    com1.sendData(np.asarray([handshake_message]))
