import socket
from traceback import print_tb

HOST = ''
PORT = 5002

udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # esta usando tcp
udp.bind((HOST, PORT))


lista_port_cliente = set()



def servidor_B():
    print('modos: \n ')
    print('   "0"-> padrao ')
    print('   "1"-> teste time_out ')
    print('   "2"-> teste checkSum ')
    print('   "3"-> teste Ack ')
    selecionar_teste = input("selecione o modo de teste : ")
    if selecionar_teste == "0":
        padrao()
    if selecionar_teste == "1":
        teste_timeout()
    if selecionar_teste == "2":
        teste_Checksum()
    if selecionar_teste == "3":
        teste_Ack()



def teste_timeout():
    cont = False
    aux = 0
    print ('Aguardando conexão ')
    while True:
        mensagem, endereço_cliente = udp.recvfrom(1024)         #recebe
        #print('Cliente -> ',endereço_cliente )
        print(endereço_cliente,' ->  ',mensagem.decode('utf-8'))
        lista_port_cliente.add(endereço_cliente)
        #print('lista das portas cliente ->',lista_port_cliente)

        for ips in lista_port_cliente:
            #print('ipList: ',ips,'  ipAtua ->',endereço_cliente)
            if ips != endereço_cliente:
                mensagem = mensagem.decode('utf-8')
                print('s---> ',mensagem)
                if cont: 
                    udp.sendto(bytes(mensagem,'utf-8'),(ips))
                else:
                    print('n enviou ')
        
        aux += 1
        if aux % 2 == 0:
            cont = not cont
   
    
def padrao():
    
    print ('Aguardando conexão ')
    while True:
        mensagem, endereço_cliente = udp.recvfrom(1024)         #recebe
        
        print(endereço_cliente,' ->  ',mensagem.decode('utf-8'))
        lista_port_cliente.add(endereço_cliente)
        

        for ips in lista_port_cliente:
            #print('ipList: ',ips,'  ipAtua ->',endereço_cliente)
            if ips != endereço_cliente:
                
                mensagem = mensagem.decode('utf-8')
                print('s---> ',mensagem)
                udp.sendto(bytes(mensagem,'utf-8'),(ips))
    udp.close()

def teste_Checksum():
    
    print ('Aguardando conexão ')
    while True:
        mensagem, endereço_cliente = udp.recvfrom(1024)         #recebe
        #print('Cliente -> ',endereço_cliente )
        print(endereço_cliente,' ->  ',mensagem.decode('utf-8'))
        lista_port_cliente.add(endereço_cliente)
        #print('lista das portas cliente ->',lista_port_cliente)

        for ips in lista_port_cliente:
            #print('ipList: ',ips,'  ipAtua ->',endereço_cliente)
            if ips != endereço_cliente:
                
                mensagem = mensagem.decode('utf-8')
                print('s---> ',mensagem)
                mensagemDiv = mensagem.split('|')
                if(len(mensagemDiv) > 1):
                    corrompe =  mensagemDiv[2][1:]
                    mensagem =  mensagemDiv[0] + '|' + mensagemDiv[1] + '|' +  corrompe 
                udp.sendto(bytes(mensagem,'utf-8'),(ips))
       
        



def teste_Ack():
    
    print ('Aguardando conexão ')
    while True:
        mensagem, endereço_cliente = udp.recvfrom(1024)         #recebe
        #print('Cliente -> ',endereço_cliente )
        print(endereço_cliente,' ->  ',mensagem.decode('utf-8'))
        lista_port_cliente.add(endereço_cliente)
        #print('lista das portas cliente ->',lista_port_cliente)

        for ips in lista_port_cliente:
            #print('ipList: ',ips,'  ipAtua ->',endereço_cliente)
            if ips != endereço_cliente:
                
                mensagem = mensagem.decode('utf-8')
                print('s---> ',mensagem)
                mensagemDiv = mensagem.split('|')
                if(len(mensagemDiv) > 1):
                    if mensagemDiv[0] == '0':
                        corrompeAck =  '1'
                    else:
                        corrompeAck = '0'
                    mensagem =  corrompeAck + '|' + mensagemDiv[1] + '|' +  mensagemDiv[2] 
                udp.sendto(bytes(mensagem,'utf-8'),(ips))
       
        
       
    
servidor_B()