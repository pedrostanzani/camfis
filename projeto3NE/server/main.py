import time
import numpy as np
from core.enlace import enlace


serialName = '/dev/cu.usbmodem101'

EOP_SIZE = 3


def build_datagram_message(packet_id: int, payload: bytes):
    EOP = b'\xff\xff\xff'
    payload_size = len(payload)
    head = packet_id.to_bytes(6, 'big') + payload_size.to_bytes(6, 'big')
    return head + payload + EOP


def build_confirmation_message(packet_id: int, ok=True):
    if ok:
        return build_datagram_message(packet_id, b'\x00\x00\x00') 
    return build_datagram_message(packet_id, b'\x00\x00\x01') 


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

    # Once the handshake is approved, we can start receiving data packages from the client
    payload_dump = bytearray()

    total_number_of_packets = 1
    last_packet_received = 0
    i = 0
    while True:
        rxBuffer, nRx = com1.getData(12)

        # Datagram head
        packet_id = int.from_bytes(rxBuffer[0:4], byteorder='big')
        total_number_of_packets = int.from_bytes(rxBuffer[4:8], byteorder='big')
        payload_size = int.from_bytes(rxBuffer[8:12], byteorder='big')

        print("Packet ID:", packet_id)
        print("Total number of packets:", total_number_of_packets)
        print("Payload size:", payload_size)

        # Fetch payload up until EOP
        rxBuffer, nRx = com1.getData(payload_size + EOP_SIZE)
        print("Recebeu:", rxBuffer, "\n")
        potential_payload = rxBuffer[:payload_size]
        potential_eof = rxBuffer[payload_size:]

        packet_ok = True

        # Verify if the EOP is in the right place.
        # TODO: what if 0xFF 0xFF 0xFF is in the payload?
        if potential_eof != b'\xff\xff\xff':
            print("[ERROR] The last bytes did not correspond to the EOP: the message must have gotten cut off.")
            packet_ok = False

        # Verify if current packet is in the right order
        if packet_id != last_packet_received + 1:
            print(f"[ERROR] Packets got sent in the wrong order. Expected: packet {last_packet_received + 1} | Received: packet: {packet_id}")
            packet_ok = False
        else:
            last_packet_received += 1

        # If everything is ok, then add payload to overall dump
        if packet_ok:
            payload_dump += potential_payload
            if total_number_of_packets == i + 1:
                print("All packets have been received.")
                print(payload_dump)

        message = build_confirmation_message(packet_id, ok=packet_ok)
        com1.sendData(message)

        # TODO: iter does not correspond to packet in case of continuing after errors
        i += 1

    print(rxBuffer)
