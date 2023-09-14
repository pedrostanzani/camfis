import time
import numpy as np
from core.enlace import enlace

# --------------------------------------------------------------------------------------------------
# byte para int: int. from_bytes() -------- z = b'\x00\x00\x00\x00\x00\x01'; int.from_bytes(z,'big')
# int para bytestring: int. to_bytes() ---- h = 1; h = h.to_bytes(6,'big')
#   python -m serial.tools.list_ports
# --------------------------------------------------------------------------------------------------

serialName = '/dev/cu.usbmodem21101'


def fetch_payload(data_buffer):
    LENGTH = 50

    if len(data_buffer) < LENGTH:
        payload = data_buffer[:]
        data_buffer = []
    else:
        payload = data_buffer[0:LENGTH]
        data_buffer = data_buffer[LENGTH:]

    return data_buffer, payload


def build_datagram_message(packet_id: int, total_number_of_packets: int, payload: bytes):
    """
    [Warning]: this function payload-size-agnostic.
    It will build a message with no restraints when it comes to the payload size.
    Make sure to send a payload that respects the maximum size established by the protocol.

    Example heading: \x00\x00\x00\x03 \x00\x00\x00\x07 \x00\x00\x00\x50
    Packet ID: 3
    Total number of packets: 7
    Payload size (in bytes): 50
    """
    def force_wrong_payload_size(pl, force=True):
        return 48 if force else pl

    EOP = b'\xff\xff\xff'
    payload_size = len(payload)
    # head = packet_id.to_bytes(4, 'big') + total_number_of_packets.to_bytes(4, 'big') + force_wrong_payload_size(payload_size).to_bytes(4, 'big')
    head = packet_id.to_bytes(4, 'big') + total_number_of_packets.to_bytes(4, 'big') + payload_size.to_bytes(4, 'big')
    return head + payload + EOP


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
                # Send handshake to server
                com1.sendData(np.asarray(b'\xff'))
                # Client expects server to send out feedback
                timeout_limit = time.time() + 5

    rxBuffer, nRx = com1.getData(1)
    if rxBuffer != b'\xff':
        print("[ERROR] Wrong handshake.")
        exit()

    print("Handshake approved.")

    #data = ([22] * 50) + ([23] * 50) + ([24] * 35)
    with open('/Users/pedroventura/Semestres/4/Camada_Insper/Projeto2/camfis-projeto-2/projeto3/agro.png', 'rb') as image:
        data = image.read()
    total_number_of_packets = len(data) // 50
    total_number_of_packets += 1 if len(data) % 50 != 0 else 0

    i = 0
    while True:
        data, payload = fetch_payload(data)
        if len(payload) == 0:
            # This means that there is no more data left to send out.
            break

        def force_wrong_package_number(pn):
            return 4 if pn == 2 else pn

        # message = build_datagram_message(force_wrong_package_number(i + 1), total_number_of_packets, bytes(payload))
        message = build_datagram_message(i + 1, total_number_of_packets, bytes(payload))
        com1.rx.clearBuffer()
        com1.sendData(message)

        print(f"[{i + 1}] Just sent to client ({len(message)} bytes): ", message)
        print()

        # Expect confirmation and resend message if no confirmation is received
        confirmed = False
        while not confirmed:
            timeout_limit = time.time() + 2
            confirmed = True
            while com1.rx.getBufferLen() == 0:
                if time.time() > timeout_limit:
                    com1.sendData(message)
                    print(f"[{i + 1}] Just sent to client ({len(message)} bytes): ", message)
                    print()
                    confirmed = False
                    break
        
        print("Confirmation confirmed.")

        # Send package every 2 seconds when no confirmation in received
        # timeout_limit = time.time() + 1
        # while com1.rx.getBufferLen() == 0:
        #     if time.time() > timeout_limit:
        #         time.sleep(1)
        #         com1.sendData(message)
        #         print(f"[{i + 1}] Just sent to client ({len(message)} bytes): ", message)
        #         print()

        rxBuffer, nRx = com1.getData(18)
        packet_id_received = rxBuffer[0:6]
        payload = rxBuffer[12:15]
        if int.from_bytes(payload, 'big') != 0:
            print(f"[ERROR] The server has informed that there has been a transmission error with packet of id = {packet_id_received}.")
            exit()
            pass
        else:
            if int.from_bytes(packet_id_received, 'big') == total_number_of_packets:
                print("Success.")

        i += 1
