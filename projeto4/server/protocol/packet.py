class Packet:
    EOP = b'\xff\xff\xff'

    def __init__(self, payload: bytes, packet_id: int, total_number_of_packets: int):
        """
        The Packet class is payload-size-agnostic.
        It will build a message with no restraints when it comes to the payload 
        size. Make sure to send a payload that respects the maximum size 
        established by the protocol.
        """
        self.payload = payload
        self.packet_id = packet_id
        self.total_number_of_packets = total_number_of_packets

    def head(self):
        """
        Example head: 00-00-00-03 00-00-00-07 00-00-00-50'
        - Packet ID: 3
        - Total number of packets: 7
        - Payload size (in bytes): 50
        """
        payload_size = len(self.payload)
        return self.packet_id.to_bytes(4, 'big') + self.total_number_of_packets.to_bytes(4, 'big') + payload_size.to_bytes(4, 'big')

    def message(self):
        return self.head() + self.payload + self.EOP


if __name__ == '__main__':
    p = Packet(b'\x00\x00\x01', 3, 7)
    msg = p.message()
    print(msg)
