import java.io.*;
import java.net.Socket;
import java.util.Scanner;

public class BulletinBoardClient {
    private Socket socket;
    private PrintWriter out;
    private BufferedReader in;
    private Scanner scanner;

    public BulletinBoardClient(String serverHost, int serverPort) {
        try {
            socket = new Socket(serverHost, serverPort);
            out = new PrintWriter(socket.getOutputStream(), true);
            in = new BufferedReader(new InputStreamReader(socket.getInputStream));
            scanner = new Scanner(System.in);

            // Implement initialization steps here, e.g., user login or group selection
            // You can create methods for these tasks and call them from the constructor.
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public void start() {
        try {
            // Implement the main client logic here, e.g., sending and receiving messages
            // You can create methods for these tasks and call them from this method.
        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            try {
                if (socket != null) {
                    socket.close();
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    public void sendMessage(String message) {
        out.println(message);
    }

    public String receiveMessage() throws IOException {
        return in.readLine();
    }

    public static void main(String[] args) {
        String serverHost = "localhost"; // Update with the actual server host
        int serverPort = 12345; // Update with the actual server port

        BulletinBoardClient client = new BulletinBoardClient(serverHost, serverPort);
        client.start();
    }
}
