from threading import Thread
import socket
import time
import sys

def getMyIp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    myIp = s.getsockname()[0]
    s.close()
    return myIp

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

    # print('soma->>', soma)
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


# ROUTER = None
# DEST = None
ROUTERIP = '127.0.0.1'
ROUTERPORT = 5001
# MYIP = socket.gethostbyname_ex(socket.getfqdn())[2][1]
MYIP = getMyIp()
print(MYIP)
DEST = '127.0.0.1'
MYPORT = 5000
timeoutSock = 0
timeoutCtrl = False
receivedMessage = False
sendMessage = False
sequence = 0
ACKReceive = False
message = ""
blockSendMessage=False

socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socketUDP.bind( ("", MYPORT) )

def timeoutSocket():
    global timeoutSock
    global timeoutCtrl
    global sendMessage
    while True:
        if(timeoutCtrl==True):
            # if(sendMessage==True):
            while(sendMessage==False):
                pass
            time.sleep(timeoutSock)
            # print(receivedMessage)
            # print(sendMessage)
            if(receivedMessage==False and sendMessage==True):
                print("Estouro de tempo (Timeout) de "+str(timeoutSock)+". Reenviando mensagem...")
                socketUDP.sendto(message, (ROUTERIP, ROUTERPORT))

def client():
    global timeoutSock
    global timeoutCtrl
    global sendMessage
    global ROUTERIP
    global ROUTERPORT
    global MYIP
    global DEST
    global sequence
    global message
    global blockSendMessage
    while(True):
        resp = int(input("1-Configurar Roteador\n2-Configurar destinatario\n3-Configurar Tempo Timeout\n4-Ver timeout\n5-Enviar mensagem\n6-Ativar/Desativar Timeout\n7-Descartar recebimento da ultima mensagem\n8-Sair\n"))
        if(resp == 1):
            ROUTERIP = input("Digite o ip do roteador:")
        elif(resp == 2):
            DEST = input("Digite o ip do destinatario:")
        elif(resp == 3):
            timeoutSock = int(input("Digite o tempo para o timeout (s):"))
            # socketUDP.settimeout(timeoutSock)
        elif(resp == 4):
            # print(socketUDP.gettimeout())]
            print("Ativado?"+str(timeoutCtrl))
            print("Tempo:"+str(timeoutSock))
        elif(resp == 5):
            if ROUTERIP==None or DEST==None:
                print("Roteador ou destino nao configurado.\n")
            else:
                if(blockSendMessage==False):
                    # socketUDP.settimeout(timeoutSock)                        
                    data = input("Digite a mensagem a ser enviada:")
                    checksum = findChecksum(data)
                    message = (str(0)+","+data+","+str(sequence)+","+checksum+","+MYIP+","+DEST).encode()

                    print("Corpo do mensagem a ser enviada:\n"+message.decode()+"\n")

                    # if socketUDP.gettimeout()!=None:
                    #     timeDecision = int(input("Timeout ativado! Desativar timeout? 1-SIM 2-NAO:"))
                    #     if(timeDecision==1):
                    #         socketUDP.settimeout(None)
                    #         print("Timeout desativado. Caso queria usar novamente, configure-o")
                    #     else:
                    #         print("Timeout sera usado!\n")

                    print("Enviando mensagem...\n")
                    socketUDP.sendto(message, (ROUTERIP, ROUTERPORT) )
                    if(timeoutCtrl==True):
                        sendMessage = True
                    blockSendMessage=True
                    print("Esperando resposta...")
                else:
                    print("Ainda na espera do ACK da ultima mensagem.")
        elif(resp == 6):
            if(timeoutCtrl==False):
                active = int(input("Ativar Timeout? 1-SIM 2-NAO"))
                if(active==1):
                    timeoutCtrl=True
            else:
                active = int(input("Desativar Timeout? 1-SIM 2-NAO"))
                if(active==1):
                    timeoutCtrl=False
        elif(resp == 7):
            blockSendMessage = False
        elif(resp == 8):
            exit()
        else:
            print("Opcao invalida")

def dataProcess(msg):
    global sequence
    global blockSendMessage
    global sendMessage
    msg = msg.decode()
    print("Dados recebidos na thread server:"+msg)
    splittedMsg = msg.split(",")
    type = int(splittedMsg[0])
    if(type == 0):
        # socketUDP.settimeout(None)
        check = findChecksum(splittedMsg[1])
        print("dado="+splittedMsg[1]+" mycheck="+check+" check da msg="+splittedMsg[3])
        if(check == splittedMsg[3]):
            print("Dado recebido com sucesso sem corrupcao. Checksum OK!")
            res = ("1,"+splittedMsg[2]+","+MYIP+","+splittedMsg[4]).encode()
            print("resposta:"+res.decode())
            socketUDP.sendto(res, (ROUTERIP, ROUTERPORT))
        else:
            print("Dado corrompido. Enviando pedido de retransmissao...")
            res = ("2,"+MYIP+","+splittedMsg[4]).encode()
            print(res)
            socketUDP.sendto(res, (ROUTERIP, ROUTERPORT))
    if(type == 1):
        if(int(splittedMsg[1]) == sequence):
            print("ACK recebido para a ultima mensagem")
            print("Numero de sequencia antes:"+str(sequence))
            if(sequence==1):
                sequence = 0
            else:
                sequence = 1
            print("Numero de sequencia depois:"+str(sequence))

            blockSendMessage = False
        else:
            print("ACK recebido para um numero de sequencia desconhecido")
            if(timeoutCtrl==True):
                sendMessage=True
    if(type == 2):
        # socketUDP.settimeout(None)
        print("Pedido de retransmissao da ultima mensagem...")
        socketUDP.sendto(message, (ROUTERIP, ROUTERPORT))
        sendMessage=True

def server():
    global ROUTERPORT
    global ROUTERIP
    global socketUDP
    global timeoutCtrl
    global receivedMessage
    global sendMessage
    while True:
        try:
            msg, host = socketUDP.recvfrom(1025)
            receivedMessage  = True
            sendMessage = False
            # print("o timeout:"+str(socketUDP.gettimeout()));
            # print(str(id(socketUDP)))
            dataProcess(msg)
            receivedMessage = False

        except socket.timeout:
            print("Estouro de tempo. Reenviando mensagem...")
            socketUDP.sendto(message, (ROUTERIP, ROUTERPORT))


if __name__ == "__main__":
    clientTh = Thread(target = client, args=())
    serverTh = Thread(target = server, args=())
    timeoutSocketTh = Thread(target=timeoutSocket, args=())
    clientTh.start()
    serverTh.start()
    timeoutSocketTh.start()