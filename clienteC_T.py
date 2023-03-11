
import socket

HOST = socket.gethostbyname(socket.gethostname()) #'192.168.225.186'
HOSTLOCAL = '26.115.61.11'
PORT = 5002
PORT_MYC = 9050


udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp.bind((HOSTLOCAL, PORT_MYC))

def cliente_C():
    udp.sendto(bytes('Iniciando cliente C ...',"utf-8"),(HOST, PORT))
    print(HOST)
    confirm = None
    while True:
        if confirm == None or confirm == '0':
            print('estado 1')
        else:
            print('estado 2')
        
        mensagemR, endereço_cliente = udp.recvfrom(1024) 
        
        mensagemR = mensagemR.decode('utf-8')
        aux = mensagemR.split('|')
        confirm = aux[0]    #Ack
        checkSumR = aux[1]  #Check sum
        mensagem = aux[2]   #Mensagem
        
        calculoCheckSum = findChecksum(mensagem,checkSumR)
        if calculoCheckSum == "1111111111111111":
            print('Mensagem Recebida:---> ',mensagemR, end="")
            print('          (checkSum OK)')
            udp.sendto(bytes(confirm,"utf-8"),(HOST, PORT) )
        
        else:
            print('Mensagem Recebida:---> ',mensagemR, end="")
            print('          (checkSum Error)')
            if confirm == '0':
                confirm = '1'
            else:
                confirm = '0'    
            udp.sendto(bytes(confirm,"utf-8"),(HOST, PORT) ) 
        
        
    udp.close()



def findChecksum(mensagem,checkSumR):
    # Dividindo a mensagem em 4 pacotes de K bits
   
    # Convertendo em binário
    binary_converted = ' '.join(map(bin, bytearray(mensagem, "utf-8")))

    # Transformando em lista para poder somar 
    list_binary_converted = binary_converted.split(' ')

    # Somando tudo
    checksumV = somaBinaria(list_binary_converted)

    #checksumV + checkSumR
    soma = bin(int(checksumV,2) + int(checkSumR,2))
    print('soma ',soma )
    
    
    return soma[2:]

def somaBinaria(lista_binaria):
    soma = "0"
    for bit in range(len(lista_binaria)):
        soma = bin(int(soma, 2) + int(lista_binaria[bit], 2))
        while len(soma) > 18:
            soma = soma[0:2] + soma[3:len(soma)]
            soma = bin(int(soma, 2) + int(1))

    # Salva o resultado da soma
    checkSum = str(soma[2:])
    while (len(checkSum) < 16):
        checkSum = "0" + checkSum
    
    '''if (len(checkSum) > 16):
        # retirar o bit mais a esquerda
        checkSum = checkSum[(len(checkSum) - 16):]'''
    
    
    return checkSum

cliente_C()
