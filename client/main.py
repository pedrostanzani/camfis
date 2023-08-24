import random


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
}

def generate():
    ### Escolhe n comandos e devolve uma lista contendo todos eles
    lstCommands = []
    indexList = []
    n = random.randint(10,30)
    for _ in range(n):
        indexList.append(random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9]))
    for index in indexList:
        lstCommands.append(commands[index])

    return [bytearray(hx) for hx in lstCommands]


def generate_protocol_message(command_key: int):
    m = commands[command_key]
    return bytearray([len(m)] + m)
    

def main():
    print(generate())


if __name__ == '__main__':
    main()
