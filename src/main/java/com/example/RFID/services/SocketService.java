package com.example.RFID.services;

import com.example.RFID.ClientHandler;
import com.example.RFID.repositories.EmployeeRepository;
import jakarta.annotation.PostConstruct;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;

@Service
public class SocketService {
  private final   EmployeeRepository employeeRepository;
    @Value("${spring.application.port}")
    private int port;
    public SocketService(EmployeeRepository employeeRepository) {
        this.employeeRepository = employeeRepository;
    }
    @PostConstruct
    public void startListening() {
        new Thread(() -> {
            try (ServerSocket serverSocket = new ServerSocket(5000)) {
                while (true) {
                    Socket socket = serverSocket.accept();
                    ClientHandler handler = new ClientHandler(socket, employeeRepository);
                    new Thread(handler).start();
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
        }).start();
    }


}
