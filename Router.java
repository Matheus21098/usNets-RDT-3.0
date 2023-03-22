import java.io.*;
import java.net.*;
import java.util.Scanner;
import java.util.ArrayList;
import java.util.List;

public class Router {
    public static final int MODE_DEFAULT = 0;
    public static final int MODE_TIMEOUT = 1;
    public static final int MODE_CORRUPT = 2;
    public static final int MODE_ACK     = 3;
    public static final int DEST_PORT    = 5000;

    public static List<String> hosts = new ArrayList<String>();

    public static class ProcessClient extends Thread{

        private DatagramSocket socketUDP;
        private DatagramPacket receive;
        private int MODE_SERVER;

        public ProcessClient(DatagramSocket socketUDP, DatagramPacket receive, int MODE_SERVER){
            this.socketUDP = socketUDP;
            this.receive = receive;
            this.MODE_SERVER = MODE_SERVER;
        }

        public void run(){
            try{
                switch(MODE_SERVER){
                    case MODE_DEFAULT:{
                        String message = new String(receive.getData(), 0, receive.getLength());
                        String splitedMessage[] = message.split(",");

                        InetAddress reSendAddress = InetAddress.getByName(splitedMessage[splitedMessage.length-1]);
                        
                        System.out.println("mensagem recebidade bytes:"+receive.getData());
                        System.out.println("mensagem recebida String:"+message);

                        // System.out.println("Mensagem recebida de:"+receive.getSocketAddress());
                        // System.out.println("Enviando para:"+reSendAddress);

                        DatagramPacket reSendPacket = new DatagramPacket(receive.getData(), receive.getData().length, reSendAddress, DEST_PORT);
                        socketUDP.send(reSendPacket);                     
                        break;
                    }
                    case MODE_TIMEOUT:{
                        String message = new String(receive.getData(), 0, receive.getLength());
                        String splitedMessage[] = message.split(",");

                        InetAddress reSendAddress = InetAddress.getByName(splitedMessage[splitedMessage.length-1]);

                        if(splitedMessage[0].equals("0")){
                            if(hosts.contains(splitedMessage[4])){
                                hosts.remove(splitedMessage[4]);
                                System.out.println("Mensagem recebida apos timeout. Repassando...");
                                
                                DatagramPacket reSendPacket = new DatagramPacket(receive.getData(), receive.getData().length, reSendAddress, DEST_PORT);
                                socketUDP.send(reSendPacket); 
                            }else{
                                System.out.println("Mensagem recebida de:"+splitedMessage[4]);
                                System.out.println("Proxima mensagem sera enviada...");
                                hosts.add(splitedMessage[4]);
                            }
                        }else{                                
                            DatagramPacket reSendPacket = new DatagramPacket(receive.getData(), receive.getData().length, reSendAddress, DEST_PORT);
                            socketUDP.send(reSendPacket); 
                        }
                        break;
                    }
                    case MODE_CORRUPT:{                        
                        String message = new String(receive.getData(), 0, receive.getLength());
                        // System.out.println("antes ala vei:"+message);
                        String splitedMessage[] = message.split(",");


                        if(splitedMessage[0].equals("0")){
                            InetAddress reSendAddress = InetAddress.getByName(splitedMessage[splitedMessage.length-1]);
                            if(hosts.contains(splitedMessage[4])){
                                hosts.remove(splitedMessage[4]);
                                System.out.println("Tal host ja teve seu dado corrompido anteriormente.");
                                System.out.println("Enviando mensagem normalmente...");
                                
                                DatagramPacket reSendPacket = new DatagramPacket(receive.getData(), receive.getData().length, reSendAddress, DEST_PORT);
                                socketUDP.send(reSendPacket);
                            }else{
                                hosts.add(splitedMessage[4]);
                                System.out.println("Corrompendo dado...");
                                System.out.println("antigo dado="+splitedMessage[1]);
                                splitedMessage[1] = splitedMessage[1]+"a";
                                System.out.println("Novo dado="+splitedMessage[1]);
                                String newMessage = String.join(",", splitedMessage);
                                System.out.println("Nova messagem="+newMessage);
                                System.out.println("len="+newMessage.getBytes().length);
                                
                                DatagramPacket reSendPacket = new DatagramPacket(newMessage.getBytes(), newMessage.getBytes().length, reSendAddress, DEST_PORT);
                                socketUDP.send(reSendPacket);
                            }
                        }else{
                            // System.out.println("ala vei"+splitedMessage[3]);
                            InetAddress reSendAddress = InetAddress.getByName(splitedMessage[splitedMessage.length-1]);
                            DatagramPacket reSendPacket = new DatagramPacket(receive.getData(), receive.getData().length, reSendAddress, DEST_PORT);
                            socketUDP.send(reSendPacket);
                        }
                        break;
                    }
                    case MODE_ACK:{
                        String message = new String(receive.getData(), 0, receive.getLength());
                        String splitedMessage[] = message.split(",");

                        InetAddress reSendAddress = InetAddress.getByName(splitedMessage[splitedMessage.length-1]);

                        if(splitedMessage[0].equals("0")){
                            if(hosts.contains(splitedMessage[4])){
                                hosts.remove(splitedMessage[4]);
                                System.out.println("Tal host ja teve seu ACK mudado anteriormente.");
                                System.out.println("Enviando mensagem normalmente...");
                                
                                DatagramPacket reSendPacket = new DatagramPacket(receive.getData(), receive.getData().length, reSendAddress, DEST_PORT);
                                socketUDP.send(reSendPacket);
                            }else{
                                hosts.add(splitedMessage[4]);
                                System.out.println("Numero de sequencia da mensagem="+splitedMessage[2]);
                                if(splitedMessage[2].equals("1")){
                                    splitedMessage[2] = "0";
                                }else{
                                    splitedMessage[2] = "1";
                                }
                                System.out.println("Novo Numero de sequencia da mensagem="+splitedMessage[2]);
                                String newMessage = String.join(",", splitedMessage);
                                System.out.println("Nova messagem="+newMessage);

                                DatagramPacket reSendPacket = new DatagramPacket(newMessage.getBytes(), newMessage.getBytes().length, receive.getAddress(), DEST_PORT);
                                socketUDP.send(reSendPacket);
                            }
                        }else{
                            DatagramPacket reSendPacket = new DatagramPacket(receive.getData(), receive.getData().length, reSendAddress, DEST_PORT);
                            socketUDP.send(reSendPacket);
                        }
                        break;
                    }
                }
            }catch(Exception e){
                e.printStackTrace();
            }
        }

    }

    public static class Server extends Thread{

        private int MODE_SERVER;

        public Server(int MODE_SERVER){
            this.MODE_SERVER = MODE_SERVER;
        }

        public void run(){
            try{
                DatagramSocket socketUDP = new DatagramSocket(5000);
                byte[] receiveData = new byte[1024];
                while(true){
                    DatagramPacket receive = new DatagramPacket(receiveData, receiveData.length);
                    socketUDP.receive(receive);
                    new ProcessClient(socketUDP, receive, MODE_SERVER).start();
                }

            }catch(Exception e){
                System.out.println(e.getMessage());
            }
        }

    }

    public static void main (String[] args){
        Scanner scanner = new Scanner(System.in);
        int MODE_SERVER;
        do{
            System.out.println("Digite a configuracao que o roteador ira seguir:");
            System.out.println("0 - Modo Normal (Ira reenviar o pacote para o destinatario)");
            System.out.println("1 - Modo Timeout (Ira \"segurar\" o pacote)");
            System.out.println("2 - Modo Corrupcao (Ira alterar o dado)");
            System.out.println("3 - Modo ACK (Ira responder para o remetente um ACK para um numero de sequencia diferente)");
            MODE_SERVER = Integer.parseInt(scanner.nextLine());
        }while(MODE_SERVER<0 & MODE_SERVER>3);
        
        try{
            DatagramSocket socketUDP = new DatagramSocket(5001);
            byte[] receiveData = new byte[1024];
            while(true){
                DatagramPacket receive = new DatagramPacket(receiveData, receiveData.length);
                socketUDP.receive(receive);
                new ProcessClient(socketUDP, receive, MODE_SERVER).start();
            }

        }catch(Exception e){
            System.out.println(e.getMessage());
        }

        //new Server(MODE_DEFAULT).start();

    }

}
