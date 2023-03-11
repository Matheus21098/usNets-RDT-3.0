from asyncio.windows_events import NULL
import socket
from time import sleep
import select
import sys

#globais
HOST = socket.gethostbyname(socket.gethostname()) #'26.74.145.27'#'192.168.15.4' #'192.168.26.28'
HOSTLOCAL = ''
PORT = 5002
PORT_MYA = 5001
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket.setdefaulttimeout(4)
udp.settimeout(4)
#udp.setblocking(True) #nao deixa entrar no estado bloqueado
udp.bind((HOSTLOCAL, PORT_MYA))

def cliente_A():

    Ack = '0'
    
    while True:
        estTimeout = 0
        estCorrupcao = 0


        mensagemInput = input('Digite a mensagem : ')
        
        checkS = findChecksum(mensagemInput)
        # juntando Ack, checkSum, mensagem
        mensagem = (Ack + '|' + checkS + '|' + mensagemInput)
        
        print(mensagem)
        
           
        mensagem = str(mensagem)
        
        ack_r = False
        
        
        
        while not ack_r:
            if Ack == '0': 
                print("Estado 1 ")
            else:
                print("Estado 4 ")
            udp.sendto(bytes(mensagem,"utf-8"),(HOST, PORT))
                    
            try:
                print("estado 2")
                mensagemVoltou, endereço_cliente = udp.recvfrom(1024)
                
             
            except socket.timeout:
                print('Timeout ')
                sleep(1)
                estTimeout += 1
                
            else:
                print('Mensagem ', mensagemVoltou.decode('utf-8'))
                
            
                if mensagemVoltou.decode('utf-8') == Ack:
                    #esta certo
                    ack_r = True
                    print("Estado 3") 
                    if Ack == '0':    
                        Ack = '1'
                    else:
                        Ack = '0'
                else:
                    #ack errado
                    estCorrupcao += 1

            if estCorrupcao > 50 or estTimeout > 25:
                print("conecxão perdida ")
                ack_r = True

                
           
    


def findChecksum(mensagem):
    
   
    # Convertendo em binário
    binary_converted = ' '.join(map(bin, bytearray(mensagem, "utf-8")))

    # Transformando em lista para poder somar 
    list_binary_converted = binary_converted.split(' ')

    # Somando tudo
    checksumV = somaBinaria(list_binary_converted)

    return checksumV

def somaBinaria(lista_binaria):
    soma = "0"
    for bit in range(len(lista_binaria)):
        soma = bin(int(soma,2) + int(lista_binaria[bit],2))
        while len(soma) > 18:
            soma = soma[0:2] + soma[3:len(soma)]
            soma = bin(int(soma,2) + int(1))

    print('soma->>', soma)
    # Inverter somatório
    checkSum = ''
    strSoma = str(soma[2:])
    while (len(strSoma) < 16):
        strSoma = "0" + strSoma
    '''
    if (len(strSoma) > 16):
        
        strSoma = strSoma[(len(strSoma) - 16):]
'''

    for caracDsoma in range(len(strSoma)):
        if strSoma[caracDsoma] == '1':
            checkSum += "0"
        else:
            checkSum += "1"
    
    return checkSum
    
cliente_A()
