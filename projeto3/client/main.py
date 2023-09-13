from core.enlace import *
import time
import numpy as np

# --------------------------------------------------------------------------------------------------
# byte para int: int. from_bytes() -------- z = b'\x00\x00\x00\x00\x00\x01'; int.from_bytes(z,'big')
# int para bytestring: int. to_bytes() ---- h = 1; h = h.to_bytes(6,'big')
# --------------------------------------------------------------------------------------------------

serialName = '/dev/cu.usbmodem101'
com1 = enlace(serialName)
com1.enable()

def payload(txBuffer):
    # payload de 50 bytes
    lenpayload = 50
    if len(txBuffer)<lenpayload:
        payload = txBuffer[0:len(txBuffer)]
        txBuffer = txBuffer[0:0]
        return [txBuffer, payload]
    payload = txBuffer[0:lenpayload]
    txBuffer = txBuffer[lenpayload:]
    return [txBuffer, payload]

def handshake(message = b'\xff'):
    com1.sendData(np.asarray(message))

    time.sleep(5)
    if com1.rx.getBufferLen() == 0:
        response = input("Servidor inativo. Tentar novamente? S/N: ")
        if response == "s" or response == "S":
            handshake()
        else:
            exit()
    else:
        if com1.getData(1) == b'\xff':
            return True
        else:
            return False

def confirmacao(NumeroDoPacote):
    time.sleep(0.1)
    if com1.rx.getBufferLen() == 0:
        com1.rx.clearBuffer()
        return False
    else: 
        if int.from_bytes(com1.getData(1)[0:5], 'big') == NumeroDoPacote:
            com1.rx.clearBuffer()
            return True
        else:
            com1.rx.clearBuffer()
            return False
    

def main():
    with open('agro.png', 'rb') as image:
        BytesImage = image.read()

    if handshake() == False:
        print("HANDSHAKE RECEBIDO DIFERENTE DO ESPERADO")
        exit()
    else:
        pass


    NumeroDoPacote = 1
    txBuffer = BytesImage
    # enviando as mensagens: 
    while len(txBuffer) > 0:
        #   O HEAD terá os primeiros 6 bytes (mais significativos) sendo o numero do pacote
        # e os ultimos 6 bytes (menos significativos) sendo o numero de pacotes totais (será sempre o mesmo valor)
        HEAD_MaisSignificativos = NumeroDoPacote
        HEAD_MenosSignificativos = len(BytesImage)

        HEAD_MaisSignificativos = HEAD_MaisSignificativos.to_bytes(6,'big')
        HEAD_MenosSignificativos = HEAD_MenosSignificativos.to_bytes(6,'big')

        HEAD = HEAD_MaisSignificativos + HEAD_MenosSignificativos

        #   O EOM (End Of Message) será FF FF FF fixo
        EOM = b'\xff\xff\xff'

        # funçao para cortar o txBuffer até o ponto que pegamos o payload
        txBuffer, payload = payload(txBuffer)

        DATAGRAMA = HEAD+payload+EOM
        
        while confirmacao(NumeroDoPacote) == False:
            com1.sendData(np.asarray(DATAGRAMA))

        NumeroDoPacote+=1


#print(main())