import java.io.*;
import java.net.Socket;
import java.util.Scanner;

public class BulletinBoardClient {
    private Socket socket;
    private PrintWriter out;
    private BufferedReader in;
    private boolean running = true;

    public BulletinBoardClient(String host, int port) {
        try {
            socket = new Socket(host, port);
            out = new PrintWriter(socket.getOutputStream(), true);
            in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public void start() {
        try {
            // Start a new thread for listening to messages from the server
            Thread listenerThread = new Thread(this::listenToServer);
            listenerThread.start();

            // Prompt for and send the username to the server
            Scanner scanner = new Scanner(System.in);
            System.out.print("-----Welcome to the message board!-----\n");
            System.out.print("Enter your username: ");
            String username = scanner.nextLine();
            out.println(username);

            // Main loop for sending messages
            System.out.println("\nTo send a message, type \"POST\" followed by the message subject.");
            System.out.println("To retrieve a message, type \"RETRIEVE\" followed by the message ID.");
            while (running) {
                String message = scanner.nextLine();
                out.println(message);

                if ("exit".equalsIgnoreCase(message)) {
                    running = false;
                    break;
                }
            }

            listenerThread.join();  // Wait for listener thread to finish
            socket.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }


    private void listenToServer() {
        try {
            String messageFromServer;
            while ((messageFromServer = in.readLine()) != null && running) {
                System.out.println(messageFromServer);
            }
        } catch (IOException e) {
            System.out.println("Error reading from server: " + e.getMessage());
        }
    }

    public static void main(String[] args) {
        BulletinBoardClient client = new BulletinBoardClient("localhost", 8888); // Adjust the port if needed
        client.start();
    }
}
