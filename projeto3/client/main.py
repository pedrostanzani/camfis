from core.enlace import *
import time
import numpy as np

# --------------------------------------------------------------------------------------------------
# byte para int: int. from_bytes() -------- z = b'\x00\x00\x00\x00\x00\x01'; int.from_bytes(z,'big')
# int para bytestring: int. to_bytes() ---- h = 1; h = h.to_bytes(6,'big')
# --------------------------------------------------------------------------------------------------

# Entrada superior esquerda
#serialName = '/dev/cu.usbmodem101'

# Entrada direita
serialName = '/dev/cu.usbmodem21101'
com1 = enlace(serialName)
com1.enable()

# Martyr byte (Byte de sacrificio)
time.sleep(0.2)
com1.sendData(b'00')
time.sleep(1)


def payload_(txBuffer):
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
    timeout_limit = time.time() + 5
    while com1.rx.getBufferLen() == 0:
        if time.time() > timeout_limit:
            response = input("Servidor inativo. Tentar novamente? S/N: ")
            if response == "s" or response == "S":
                return handshake()
            else:
                exit()
    _handshake = com1.getData(1)[0]
    if _handshake == b'\xff':
        return True
    else:
        return False

            
def confirmacao(NumeroDoPacote):

    if com1.rx.getBufferLen() == 0:
        return False

    if com1.rx.getBufferLen() > 5:
        IR = com1.getData(com1.rx.getBufferLen())[0]
        
        ndp = IR[0:6]
        print()
        print("INFO RECEBIDA:", IR)
        print("TAMANHO DA INFO:", len(IR))
        print("INFO IMPORTANTE:", ndp)
        print("INFO ESPERADA:", NumeroDoPacote)
        

        com1.rx.clearBuffer()
        if int.from_bytes(ndp, 'big') == NumeroDoPacote:
            print("PASSOU NO PACOTE " + str(NumeroDoPacote))
            return True
        else:
            return False
    

def main():
    with open('/Users/pedroventura/Semestres/4/Camada_Insper/Projeto2/camfis-projeto-2/projeto3/agro.png', 'rb') as image:
        BytesImage = image.read()

    if not handshake():
        print("HANDSHAKE RECEBIDO DIFERENTE DO ESPERADO")
        exit()


    NumeroDoPacote = 1
    txBuffer = BytesImage
    # enviando as mensagens: 
    while len(txBuffer) > 0:
       
        #   O HEAD terá os primeiros 6 bytes (mais significativos) sendo o numero do pacote
        # e os ultimos 6 bytes (menos significativos) sendo o numero de pacotes totais (será sempre o mesmo valor)
        
        #   O EOM (End Of Message) será FF FF FF fixo
        EOM = b'\xff\xff\xff'

        # funçao para cortar o txBuffer até o ponto que pegamos o payload
        txBuffer, payload = payload_(txBuffer)

        HEAD_MaisSignificativos = NumeroDoPacote
        HEAD_MenosSignificativos = len(payload)
        HEAD_MaisSignificativos = HEAD_MaisSignificativos.to_bytes(6,'big')
        HEAD_MenosSignificativos = HEAD_MenosSignificativos.to_bytes(6,'big')
        HEAD = HEAD_MaisSignificativos + HEAD_MenosSignificativos

        DATAGRAMA = HEAD+payload+EOM
        
        #com1.rx.clearBuffer()
        com1.sendData(DATAGRAMA)

        while not confirmacao(NumeroDoPacote):
            pass

        NumeroDoPacote+=1

    return "finalizou"


main()