from protocol.packet import Packet
def split_and_assemble(imagePath, payloadSize=114):
    MESSAGES_SENT_BEFORE = 1


    payloadList = []
    with open(imagePath, 'rb') as image:
        data = image.read()
    while len(data)>0:
        if len(data)>payloadSize:
            payload = data[0:payloadSize]
            data = data[payloadSize:]
        else:
            payload = data
            data = []
        payloadList.append(payload)

    [Packet(n, 3, len(payloadList), i+(1+MESSAGES_SENT_BEFORE), i+MESSAGES_SENT_BEFORE) for i, n in enumerate(payloadList)]
    
    
    