package com.example.RFID;


import com.example.RFID.dto.EmployeeDto;
import com.example.RFID.mappers.EmployeeMapper;
import com.example.RFID.repositories.EmployeeRepository;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.*;
import java.net.Socket;
import java.nio.charset.StandardCharsets;


public class ClientHandler implements Runnable{
    private final Socket socket;
  private final  BufferedReader in ;
   private final BufferedWriter out;
   private final ObjectMapper mapper ;

    private final   EmployeeRepository employeeRepository;
  public   ClientHandler(  Socket socket, EmployeeRepository employeeRepository) throws IOException {
        this.socket = socket;
        this.in=new BufferedReader(new InputStreamReader(socket.getInputStream(), StandardCharsets.UTF_8));
        this.out= new BufferedWriter(new OutputStreamWriter(socket.getOutputStream(), StandardCharsets.UTF_8));
        this.employeeRepository=employeeRepository;
        this.mapper = new ObjectMapper();
    }
    @Override
    public void run() {
        startMessageListener();

    }
    public void startMessageListener() {
        Thread listenerThread = new Thread(() -> {
            try {
                while (!socket.isClosed()) {
                    String command = in.readLine();
                    if (command.equals("RFID")) {
                        handleEmployeeMessage();
                    }
                }
            } catch (IOException  e) {
                System.out.println("End of stream reached. No more data to read.");
            }
        });

        listenerThread.setDaemon(true);
        listenerThread.start();
    }
    private void handleEmployeeMessage() throws IOException {
        String rfid = in.readLine();
        System.out.println(rfid);
        EmployeeDto employee= employeeRepository.findById(rfid).map(EmployeeMapper::toDto).orElseThrow(()->new  RuntimeException("Employee with RFID "+rfid+" not found"));
        String json=mapper.writeValueAsString(employee);
        System.out.println(json);
        out.write(json);
        out.newLine();
        out.flush();


    }
}
