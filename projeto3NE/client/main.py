import time
import numpy as np
from core.enlace import enlace

# --------------------------------------------------------------------------------------------------
# byte para int: int. from_bytes() -------- z = b'\x00\x00\x00\x00\x00\x01'; int.from_bytes(z,'big')
# int para bytestring: int. to_bytes() ---- h = 1; h = h.to_bytes(6,'big')
# --------------------------------------------------------------------------------------------------

serialName = '/dev/cu.usbmodem101'

if __name__ == '__main__':
    com1 = enlace(serialName)
    com1.enable()

    # Send a martyr byte
    time.sleep(0.2)
    com1.sendData(b'00')
    time.sleep(1)

    # Send handshake to server
    com1.sendData(np.asarray(b'\xff'))

    # Client expects server to send out feedback
    timeout_limit = time.time() + 5
    while com1.rx.getBufferLen() == 0:
        if time.time() > timeout_limit:
            print("[ERROR] The server is not active.")
            response = input("Would you like to try again? [Y/N]: ")
            if response.strip().lower() not in ['s', 'y']:
                print("Client no longer wishes to continue. Exiting program...")
                exit()
            else:
                timeout_limit = time.time() + 5

    rxBuffer, nRx = com1.getData(1)
    if rxBuffer != b'\xff':
        print("[ERROR] Wrong handshake.")
        exit()
