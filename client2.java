import java.io.*;
import java.net.Socket;
import java.util.Scanner;

public class BulletinBoardClient {
    private Socket socket;
    private PrintWriter out;
    private BufferedReader in;

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
            Scanner scanner = new Scanner(System.in);
            System.out.print("Enter username: ");
            String username = scanner.nextLine();
            System.out.println("Sending username: " + username);  // Debugging line
            out.println(username);

            // Start a thread to listen for messages from the server
            Thread listenerThread = new Thread(() -> {
                try {
                    String serverMessage;
                    while ((serverMessage = in.readLine()) != null) {
                        System.out.println(serverMessage);
                    }
                } catch (IOException e) {
                    System.out.println("Error reading from server: " + e.getMessage());
                }
            });

            listenerThread.start();

            // Read and send messages to server
            while (true) {
                String message = scanner.nextLine();
                System.out.println("Sending message: " + message);  // Debugging line
                out.println(message);

                if ("exit".equalsIgnoreCase(message)) {
                    break;
                }
            }

            listenerThread.join();  // Wait for listener thread to finish
            socket.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public static void main(String[] args) {
        BulletinBoardClient client = new BulletinBoardClient("localhost", 8888); // Adjust the port if needed
        client.start();
    }
}
