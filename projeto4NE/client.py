import time
from packet import Packet
from core.enlace import enlace

from pprint import pprint


"""
Variable name mapping:
inicia --> start
cont   --> counter
numPck --> number_of_packets
"""

MESSAGE_TYPE_2 = 2
MESSAGE_TYPE_4 = 4
MESSAGE_TYPE_6 = 6

SERVER_ID = 17

class PacketWrapper(Packet):
    @classmethod
    def create_type_1(cls, config: dict):
        _config = {
            'messageType': 1,
            'serverID': SERVER_ID,
            'totalNumberOfPackets': config['totalNumberOfPackets'],
            'packetID': 0,
            'fileID': 0,
            'lastSuccessfulPacket': 0,
            'resendPacket': 0
        }
        return cls(None, _config)
    
    @classmethod
    def create_type_5(cls, config: dict):
        _config = {
            'messageType': 5,
            'serverID': SERVER_ID,
            'totalNumberOfPackets': config['totalNumberOfPackets'],
            'packetID': 0,
            'fileID': 0,
            'lastSuccessfulPacket': 0,
            'resendPacket': 0
        }
        return cls(None, _config)



class Client:
    SERIAL_NAME = '/dev/cu.usbmodem101'

    def __init__(self):
        self.com = enlace(self.SERIAL_NAME)
        self.data_packets = []

        # Control variables (see variable name mapping above)
        self.start = False
        self.counter = 0
        self.number_of_packets = 0

        self.has_timed_out = False

    def handshake_protocol(self):
        while not self.start:
            print("Initiating handshake protocol...")
            p = PacketWrapper.create_type_1({'totalNumberOfPackets': self.number_of_packets})
            self.com.sendData(p.message())
            print("Just sent message type 1 to the server.")

            timeout_limit = time.time() + 5
            while self.com.rx.getBufferLen() < 10:
                if time.time() > timeout_limit:
                    break

            if not self.com.rx.getBufferLen() < 10:
                print("A message has been received.")
                rxBuffer, _ = self.com.getData(10)
                message_type = rxBuffer[0]
                print(f"Message type: {message_type}")
                if message_type == MESSAGE_TYPE_2:
                    self.start = True
                    continue
            
            self.com.rx.clearBuffer()

    def send_packet(self, packet_id: int):
        p = self.data_packets[packet_id - 1]
        self.com.rx.clearBuffer()
        self.com.sendData(p.message())
        print(f"Sent out: {str(p)}")

        timeout_limit_1 = time.time() + 5
        timeout_limit_2 = time.time() + 20
        while self.com.rx.getBufferLen() < 10:
            if time.time() > timeout_limit_1:
                print(f"Just hit 5 second threshold. Resending message. Current buffer length: {self.com.rx.getBufferLen()}")
                self.com.sendData(p.message())
                timeout_limit_1 = time.time() + 5

            if time.time() > timeout_limit_2:
                break

        # Breaking out means that:
        # (a) there has been a time out (t > 20); or
        # (b) header of type 4 has been received; or
        # (c) header of type 6 has been received
        if not self.com.rx.getBufferLen() < 10:
            rxBuffer, _ = self.com.getData(10)
            self.com.rx.clearBuffer()
            message_type = rxBuffer[0]

            # Refactored EOP clutter hack
            # type_is_eop_clutter = message_type in [170, 187, 204, 221]
            # clutter_fix_i = 1
            # while clutter_fix_i <= 3 or message_type < 6:
            #     message_type = rxBuffer[clutter_fix_i]
            #     clutter_fix_i += 1
            # End of EOP clutter hack

            # EOP clutter hack (experimental)
            eop_clutter_fix_iterations = 1
            while message_type > 6:
                if message_type not in [170, 187, 204, 221]:
                    print(f"Invalid message type. Forcing time-out.")
                    self.has_timed_out = True
                    return None
                message_type = rxBuffer[eop_clutter_fix_iterations]
                eop_clutter_fix_iterations += 1
                if eop_clutter_fix_iterations > 3:
                    print(f"Invalid message type. Forcing time-out.")
                    self.has_timed_out = True
                    return None
            # End of EOP clutter hack

            print(f"A message has been received. Message type: {message_type}")
            print(rxBuffer)
            print([n for n in rxBuffer])

            # handler for scenario (b)
            if message_type == MESSAGE_TYPE_4:
                success_confirmation = True
                self.counter += 1
                return None

            # handler for scenario (c)
            elif message_type == MESSAGE_TYPE_6:
                resend_packet = rxBuffer[6]
                self.counter = resend_packet
                return None
            
            else:
                print(f"Invalid message type. Forcing time-out.")
                self.has_timed_out = True
                return None
        
        # handler for scenario (a)
        # If it gets here, then it means that it definitely timed-out
        print("Since there has been a time-out, client is sending out a message type 5 to the server.")
        px = PacketWrapper.create_type_5({'totalNumberOfPackets': self.number_of_packets})
        self.has_timed_out = True
        self.com.sendData(px.message())
        return None
            

    def main(self):
        print("Now running Client.main()...")

        # Load file...
        with open('./assets/agro.png', 'rb') as file:
            all_data = file.read()
        self.data_packets = Packet.packets_from_data(all_data)
        self.number_of_packets = len(self.data_packets)
        print("Just loaded asset: agro.png.")
        print(f"Total of {self.number_of_packets} packets.")

        self.com.enable()

        # TODO: Send a martyr byte
        time.sleep(0.2)
        self.com.sendData(b'00')
        time.sleep(1)
        print("Just sent out a martyr byte.")

        self.handshake_protocol()
        self.com.rx.clearBuffer()

        i = 0
        self.counter = 1
        while self.counter <= self.number_of_packets:
            print(f"\nStarting iteration {i}...")
            self.com.rx.clearBuffer()
            self.send_packet(self.counter)
            if self.has_timed_out:
                return print("Communication has timed out.")
            i += 1
        print("Operation completed successfully.")


if __name__ == '__main__':
    c = Client()
    c.main()
