import time
import random
import numpy as np
from core.enlace import enlace

SERIAL_NAME = "/dev/tty.usbmodem101"

protocol_translator = {
    1: (4, 4),
    2: (4, 3),
    3: (4, 2),
    4: (4, 1),
    5: (3, 4),
    6: (3, 3),
    7: (3, 2),
    8: (3, 1),
    9: (2, 4),
    10: (2, 3),
    11: (2, 2),
    12: (2, 1),
    13: (1, 4),
    14: (1, 3),
    15: (1, 2),
    16: (1, 1),
}


commands = {
    1: [0x00, 0x00, 0x00, 0x00],
    2: [0x00, 0x00, 0xBB, 0x00],
    3: [0xBB, 0x00, 0x00],
    4: [0x00, 0xBB, 0x00],
    5: [0x00, 0x00, 0xBB],
    6: [0x00, 0xAA],
    7: [0xBB, 0x00],
    8: [0x00],
    9: [0xBB],
    10: [0xFF],
}


def generate_protocol_compliant_message(command_key: int):
    m = commands[command_key]
    return bytearray([len(m)] + m)


def inverse_protocol_translator(size_a, size_b):
    if size_a == 4:
        if size_b == 4: return 1
        if size_b == 3: return 2
        if size_b == 2: return 3
        if size_b == 1: return 4

    if size_a == 3:
        if size_b == 4: return 5
        if size_b == 3: return 6
        if size_b == 2: return 7
        if size_b == 1: return 8

    if size_a == 2:
        if size_b == 4: return 9
        if size_b == 3: return 10
        if size_b == 2: return 11
        if size_b == 1: return 12

    if size_a == 1:
        if size_b == 4: return 13
        if size_b == 3: return 14
        if size_b == 2: return 15
        if size_b == 1: return 16


def generate_new_protocol_compliant_message(commands_: list, eom=False):
    a, b = commands_
    m = commands[a] + commands[b]
    authority_digit = inverse_protocol_translator(len(commands[a]), len(commands[b]))
    new_pcm = bytearray([authority_digit] + m)
    if eom:
        print(f"Client has paired up command {a} with EOM (end of message) sequence 0xFF.")
    else:
        print(f"Client has paired up 2 commands: {a} and {b}.")
    return new_pcm


if __name__ == '__main__':
    number_of_commands = random.randint(10, 30)
    list_of_commands = [random.randint(1, 9) for _ in range(number_of_commands)]

    print("Client has randomly generated a list of commands to send out:")
    print(list_of_commands)
    print(f"Number of commands: {number_of_commands}")
    print()

    all_data = []

    i = 0
    while i < len(list_of_commands):
        if i == len(list_of_commands) - 1:
            m = generate_new_protocol_compliant_message([list_of_commands[i], 10], eom=True)
            all_data.append(m)
        else:
            m = generate_new_protocol_compliant_message([list_of_commands[i], list_of_commands[i + 1]])
            all_data.append(m)
        i += 2

    print()

    full_message = bytearray()
    for message in all_data:
        full_message += message

    if len(list_of_commands) % 2 == 0:
        full_message += bytearray([255])

    com1 = enlace(SERIAL_NAME)
    com1.enable()

    # Martyr byte
    time.sleep(0.2)
    com1.sendData(b'00')
    time.sleep(1)

    # Client sends data out to the server
    com1.sendData(np.asarray(full_message))
    while com1.tx.threadMutex:
        pass
    txSize = com1.tx.getStatus()
    print('Client has sent {} bytes.\n' .format(txSize))  # unit is bytes?

    # Client expects server to send out feedback
    timeout_limit = time.time() + 5
    while com1.rx.getBufferLen() == 0:
        if time.time() > timeout_limit:
            print("[ERROR] The timeout limit has been reached.")
            exit()

    rxBuffer, nRx = com1.getData(1)
    control_integer = int.from_bytes(rxBuffer, byteorder='big')
    if control_integer > 4:
        print("No message was sent from the server.")
    rxBuffer, nRx = com1.getData(control_integer)
    number_of_commands_received = int.from_bytes(rxBuffer, byteorder='big')
    print(f"Server sent: {number_of_commands_received}")

    # Detects inconsistency
    if (number_of_commands_received != number_of_commands):
        print("[ERROR] The server has sent an inconsistent number of commands.")
        exit()

