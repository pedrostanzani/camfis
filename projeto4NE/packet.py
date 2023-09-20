class Packet:
    EOP = b'\xaa\xbb\xcc\xdd'
    MAX_PAYLOAD = 114

    def __init__(self, payload: bytes, config: dict):
        self.payload = payload

        if not self.payload:
            self.payload = b''

        if len(self.payload) > self.MAX_PAYLOAD:
            raise Exception(f"The payload cannot exceed {self.MAX_PAYLOAD} bytes.")
        
        self.message_type = config['messageType']
        self.server_id = config['serverID']
        self.total_number_of_packets = config['totalNumberOfPackets']
        self.packet_id = config['packetID']
        self.file_id = config['fileID']
        self.last_successful_packet = config['lastSuccessfulPacket']
        self.is_handshake = config['messageType'] == 1
        if 'resendPacket' in config:
            self.resend_packet = config['resendPacket']

    def head(self):
        _head = bytes()
        _head += self.message_type.to_bytes(1, 'big') # H0
        _head += self.server_id.to_bytes(1, 'big') if self.message_type == 1 else b'\x00' # H1
        _head += b'\x00' # H2
        _head += self.total_number_of_packets.to_bytes(1, 'big') # H3
        _head += self.packet_id.to_bytes(1, 'big') # H4
        _head += self.file_id.to_bytes(1, 'big') if self.is_handshake else len(self.payload).to_bytes(1, 'big') # H5
        _head += self.resend_packet.to_bytes(1, 'big') if self.message_type == 6 else b'\x00' # H6
        _head += self.last_successful_packet.to_bytes(1, 'big') # H7
        _head += b'\x00\x00' # H8, H9
        return _head

    def message(self):
        return self.head() + self.payload + self.EOP
    
    def debug_header(self):
        h = [n for n in self.head()]
        for i in range(len(h)):
            print(f"h{i} --> {h[i]}")



if __name__ == '__main__':
    # Exemplo 1: estamos enviando um arquivo que foi dividido em 70 pacotes.
    # O client acabou de enviar o pacote 34, e agora vai enviar o pacote 35.
    config = {
        'messageType': 3,
        'serverID': 17,
        'totalNumberOfPackets': 70,
        'packetID': 35,
        'fileID': 1,
        'lastSuccessfulPacket': 34,
    }
    p = Packet(b'\x03\xff', config)
    print(p.message())
    p.debug_header()
    print()

    # Exemplo 2: estamos enviando uma mensagem de tipo 1 do cliente ao servidor.
    config = {
        'messageType': 1,
        'serverID': 17,
        'totalNumberOfPackets': 70,
        'packetID': 35,
        'fileID': 1,
        'lastSuccessfulPacket': 0,
    }
    p = Packet(b'\x03', config)
    print(p.message())
    p.debug_header()

