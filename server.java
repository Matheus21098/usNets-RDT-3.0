import java.io.*;
import java.net.*;
import java.util.*;

public class ServerB {
    private static final int PORT = 5002;
    private static Set<InetSocketAddress> clientAddresses = new HashSet<>();

    public static void main(String[] args) {
        try {
            DatagramSocket socket = new DatagramSocket(PORT);
            System.out.println("Modos: ");
            System.out.println("   \"0\"-> padrao ");
            System.out.println("   \"1\"-> teste time_out ");
            System.out.println("   \"2\"-> teste checkSum ");
            System.out.println("   \"3\"-> teste Ack ");
            System.out.print("Selecione o modo de teste: \n");
            Scanner scanner = new Scanner(System.in);
            String mode = scanner.nextLine();
            scanner.close();
            switch (mode) {
                case "0":
                    try {
                        padrao(socket);
                    } catch (IOException e) {
                        // TODO Auto-generated catch block
                        e.printStackTrace();
                    }
                    break;
                case "1":
                    try {
                        testeTimeout(socket);
                    } catch (IOException e) {
                        // TODO Auto-generated catch block
                        e.printStackTrace();
                    }
                    break;
                case "2":
                    try {
                        testeChecksum(socket);
                    } catch (IOException e) {
                        // TODO Auto-generated catch block
                        e.printStackTrace();
                    }
                    break;
                case "3":
                    try {
                        testeAck(socket);
                    } catch (IOException e) {
                        // TODO Auto-generated catch block
                        e.printStackTrace();
                    }
                    break;
                default:
                    System.err.println("Modo inválido!\n");
            }
            socket.close();
        } catch (SocketException e) {
            e.printStackTrace();
        }
    }

    private static void padrao(DatagramSocket socket) throws IOException {
        System.out.println("Aguardando conexão.\n");
        while (true) {
            byte[] buffer = new byte[1024];
            DatagramPacket packet = new DatagramPacket(buffer, buffer.length);
            socket.receive(packet);
            InetSocketAddress clientAddress = (InetSocketAddress) packet.getSocketAddress();
            System.out.println(clientAddress + " -> " + new String(packet.getData(), 0, packet.getLength()));
            clientAddresses.add(clientAddress);
            for (InetSocketAddress address : clientAddresses) {
                if (!address.equals(clientAddress)) {
                    DatagramPacket responsePacket = new DatagramPacket(buffer, packet.getLength(), address);
                    socket.send(responsePacket);
                }
            }
        }
    }


    private static void testeTimeout(DatagramSocket socket) throws IOException {
        System.out.println("Aguardando conexão.\n");
        boolean cont = false;
        int aux = 0;

        while (true) {
            byte[] buffer = new byte[1024]; // aqui ficava buffer size
            DatagramPacket packet = new DatagramPacket(buffer, buffer.length);
            socket.receive(packet);

            InetSocketAddress clientAddress = (InetSocketAddress) packet.getSocketAddress();
            clientAddresses.add(clientAddress);

            String message = new String(packet.getData(), 0, packet.getLength());
            System.out.println(clientAddress + " -> " + message);

            for (InetSocketAddress address : clientAddresses) {
                if (!address.equals(clientAddress)) {
                    if (cont) {
                        packet.setSocketAddress(address);
                        socket.send(packet);
                    } else {
                        System.out.println("Mensagem nao enviada!");
                    }
                }
            }

            aux++;
            if (aux % 2 == 0) {
                cont = !cont;
            }
        }
    }
    private static void testeChecksum(DatagramSocket socket) throws IOException{
		System.out.println("Aguardando conexão.\n");
		while (true) {
			byte[] buffer = new byte[1024];
			DatagramPacket receivePacket = new DatagramPacket(buffer, buffer.length);
			socket.receive(receivePacket);
			String mensagem = new String(receivePacket.getData(), 0, receivePacket.getLength());
			System.out.println(receivePacket.getSocketAddress() + " -> " + mensagem);

			clientAddresses.add((InetSocketAddress) receivePacket.getSocketAddress());

			for (InetSocketAddress ips : clientAddresses) {
				if (!ips.equals(receivePacket.getSocketAddress())) {
					String corrompe = mensagem.split("\\|")[2].substring(1);
					mensagem = mensagem.split("\\|")[0] + "|" + mensagem.split("\\|")[1] + "|" + corrompe;
					byte[] sendData = mensagem.getBytes();
					DatagramPacket sendPacket = new DatagramPacket(sendData, sendData.length, ips.getAddress(), ips.getPort());
					socket.send(sendPacket);
				}
			}
		}
	}
	
	
	private static void testeAck(DatagramSocket socket) throws IOException{
        System.out.println("Aguardando conexão.\n");
        while (true) {
            byte[] buffer = new byte[1024];
            DatagramPacket pacote = new DatagramPacket(buffer, buffer.length);
            socket.receive(pacote);
            
            String mensagem = new String(pacote.getData(), 0, pacote.getLength(), "UTF-8");
            InetSocketAddress enderecoCliente = new InetSocketAddress(pacote.getAddress(), pacote.getPort());
            
            System.out.println(enderecoCliente + " -> " + mensagem);
            clientAddresses.add(enderecoCliente);
            
            for (InetSocketAddress ips : clientAddresses) {
                if (!ips.equals(enderecoCliente)) {
                    String mensagemDiv[] = mensagem.split("\\|");
                    
                    if (mensagemDiv.length > 1) {
                        String corrompeAck = (mensagemDiv[0].equals("0")) ? "1" : "0";
                        mensagem = corrompeAck + "|" + mensagemDiv[1] + "|" + mensagemDiv[2];
                    }
                    
                    byte[] resposta = mensagem.getBytes("UTF-8");
                    DatagramPacket pacoteResposta = new DatagramPacket(resposta, resposta.length, ips.getAddress(), ips.getPort());
                    socket.send(pacoteResposta);
                }
            }
        }
    }
}