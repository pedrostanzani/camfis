from suaBibSignal import *
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt

def interpret_key(key: str):
    keys = {
        "1": (1209, 697),
        "2": (1336, 697),
        "3": (1477, 697),
        "4": (1209, 770),
        "5": (1336, 770),
        "6": (1477, 770),
        "7": (1209, 852),
        "8": (1336, 852),
        "9": (1477, 852),
        "X": (1209, 941),
        "*": (1209, 941),
        "0": (1336, 941),
        "#": (1477, 941),
        "A": (1633, 697),
        "B": (1633, 770),
        "C": (1633, 852),
        "D": (1633, 941),
    }

    return keys[key]

def main():
    #********************************************instruções*********************************************** 
    # seu objetivo aqui é gerar duas senoides. Cada uma com frequencia corresposndente à tecla pressionada
    # então inicialmente peça ao usuário para digitar uma tecla do teclado numérico DTMF
    # agora, voce tem que gerar, por alguns segundos, suficiente para a outra aplicação gravar o audio, duas senoides com as frequencias corresposndentes à tecla pressionada, segundo a tabela DTMF
    # Essas senoides tem que ter taxa de amostragem de 44100 amostras por segundo, entao voce tera que gerar uma lista de tempo correspondente a isso e entao gerar as senoides
    # Lembre-se que a senoide pode ser construída com A*sin(2*pi*f*t)
    # O tamanho da lista tempo estará associada à duração do som. A intensidade é controlada pela constante A (amplitude da senoide). Construa com amplitude 1.
    # Some as senoides. A soma será o sinal a ser emitido.
    # Utilize a funcao da biblioteca sounddevice para reproduzir o som. Entenda seus argumento.
    # Grave o som com seu celular ou qualquer outro microfone. Cuidado, algumas placas de som não gravam sons gerados por elas mesmas. (Isso evita microfonia).
    
    # construa o gráfico do sinal emitido e o gráfico da transformada de Fourier. Cuidado. Como as frequencias sao relativamente altas, voce deve plotar apenas alguns pontos (alguns periodos) para conseguirmos ver o sinal
    taxa_amostragem = 44100
    duracao = 1

    tecla = input("Inpsira uma tecla do teclado numérico DTMF: ").upper().strip()
    frequencia1, frequencia2 = interpret_key(key=tecla)

    tempo = np.linspace(0, duracao, int(taxa_amostragem * duracao), endpoint=False)

    amplitude = 1
    sinal1 = amplitude * np.sin(2 * np.pi * frequencia1 * tempo)
    sinal2 = amplitude * np.sin(2 * np.pi * frequencia2 * tempo)

    sinal_combinado = sinal1 + sinal2
    sd.play(sinal_combinado, taxa_amostragem)
    sd.wait()

    # Plotar o sinal no domínio do tempo
    # plt.figure(figsize=(12, 6))
    # plt.subplot(2, 1, 1)
    # plt.title('Sinal no Domínio do Tempo')
    # plt.plot(tempo, sinal_combinado)
    # plt.xlabel('Tempo (s)')
    # plt.ylabel('Amplitude')
    # plt.xlim(0, 0.02)
    # plt.show()

    # Fourier transform
    smeu = signalMeu()
    smeu.plotFFT(sinal_combinado, taxa_amostragem)


    # print("Inicializando encoder")
    # print("Aguardando usuário")
    # print("Gerando Tons base")
    # print("Executando as senoides (emitindo o som)")
    # print("Gerando Tom referente ao símbolo : {}".format(NUM))
    # sd.play(tone, fs)
    # # Exibe gráficos
    # plt.show()
    # # aguarda fim do audio
    # sd.wait()
    # plotFFT(self, signal, fs)
    

if __name__ == "__main__":
    #********************************************instruções*********************************************** 
    # seu objetivo aqui é gerar duas senoides. Cada uma com frequencia corresposndente à tecla pressionada
    # então inicialmente peça ao usuário para digitar uma tecla do teclado numérico DTMF
    # agora, voce tem que gerar, por alguns segundos, suficiente para a outra aplicação gravar o audio, duas senoides com as frequencias corresposndentes à tecla pressionada, segundo a tabela DTMF
    # Essas senoides tem que ter taxa de amostragem de 44100 amostras por segundo, entao voce tera que gerar uma lista de tempo correspondente a isso e entao gerar as senoides
    # Lembre-se que a senoide pode ser construída com A*sin(2*pi*f*t)
    # O tamanho da lista tempo estará associada à duração do som. A intensidade é controlada pela constante A (amplitude da senoide). Construa com amplitude 1.
    # Some as senoides. A soma será o sinal a ser emitido.
    # Utilize a funcao da biblioteca sounddevice para reproduzir o som. Entenda seus argumento.
    # Grave o som com seu celular ou qualquer outro microfone. Cuidado, algumas placas de som não gravam sons gerados por elas mesmas. (Isso evita microfonia).
    
    # construa o gráfico do sinal emitido e o gráfico da transformada de Fourier. Cuidado. Como as frequencias sao relativamente altas, voce deve plotar apenas alguns pontos (alguns periodos) para conseguirmos ver o sinal
    taxa_amostragem = 44100
    duracao = 5

    tecla = input("Inpsira uma tecla do teclado numérico DTMF: ").upper().strip()
    frequencia1, frequencia2 = interpret_key(key=tecla)

    tempo = np.linspace(0, duracao, int(taxa_amostragem * duracao), endpoint=False)

    amplitude = 1
    sinal1 = amplitude * np.sin(2 * np.pi * frequencia1 * tempo)
    sinal2 = amplitude * np.sin(2 * np.pi * frequencia2 * tempo)

    sinal_combinado = sinal1 + sinal2
    sd.play(sinal_combinado, taxa_amostragem)
    sd.wait()

    # Plotar o sinal no domínio do tempo
    # plt.figure(figsize=(12, 6))
    # plt.subplot(2, 1, 1)
    # plt.title('Sinal no Domínio do Tempo')
    # plt.plot(tempo, sinal_combinado)
    # plt.xlabel('Tempo (s)')
    # plt.ylabel('Amplitude')
    # plt.xlim(0, 0.02)
    # plt.show()

    # Fourier transform
    smeu = signalMeu()
    smeu.plotFFT(sinal_combinado, taxa_amostragem)