class Packet:
    EOP = b'\xaa\xbb\xcc\xdd'
    MAX_PAYLOAD = 114

    def __init__(self,
                 payload: bytes,
                 message_type: int,
                 total_number_of_packets: int,
                 packet_id: int,
                 last_successfully_received_packet_id: int,
                 is_handshake: bool = False,
                 server_id: int = 0,
                 file_id: int = 0,):
        # Verify that the payload respects maximum size set by the protocol.
        self.payload = payload
        if len(self.payload) > self.MAX_PAYLOAD:
            raise Exception(
                f"The payload cannot exceed {self.MAX_PAYLOAD} bytes.")
        
        self.message_type = message_type
        self.server_id = server_id
        self.total_number_of_packets = total_number_of_packets
        self.packet_id = packet_id
        self.file_id = file_id
        self.last_successfully_received_packet_id = last_successfully_received_packet_id
        self.is_handshake = is_handshake


    def head(self):
        _head = bytes()
        _head += self.message_type.to_bytes(1, 'big')
        _head += self.server_id.to_bytes(1, 'big') if self.message_type == 1 else b'\x00'
        _head += b'\x00'
        _head += self.total_number_of_packets.to_bytes(1, 'big')
        _head += self.packet_id.to_bytes(1, 'big')
        _head += self.file_id.to_bytes(1, 'big') if self.is_handshake else len(self.payload).to_bytes(1, 'big')
        _head += b'\x00'  # TODO: Pacote solicitado para recomeço quando a erro no envio.
        _head += self.last_successfully_received_packet_id.to_bytes(1, 'big')
        _head += b'\x00\x00'
        
        return _head

    def message(self):
        return self.head() + self.payload + self.EOP


if __name__ == '__main__':
    p = Packet(b'\xff\x00\x01', 1, 64, 4, 6, 3, server_id=4)
    msg = p.message()
    print(msg)
