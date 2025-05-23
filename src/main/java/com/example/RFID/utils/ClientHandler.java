package com.example.RFID.utils;

import com.example.RFID.dto.EmployeeDto;
import com.example.RFID.mappers.EmployeeMapper;
import com.example.RFID.repositories.EmployeeRepository;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.*;
import java.net.Socket;
import java.nio.charset.StandardCharsets;

public class ClientHandler implements Runnable {
    private final Socket socket;
    private final BufferedReader in;
    private final BufferedWriter out;
    private final ObjectMapper mapper;
    private final EmployeeRepository employeeRepository;

    public ClientHandler(Socket socket, EmployeeRepository employeeRepository) throws IOException {
        this.socket = socket;
        this.in = new BufferedReader(new InputStreamReader(socket.getInputStream(), StandardCharsets.UTF_8));
        this.out = new BufferedWriter(new OutputStreamWriter(socket.getOutputStream(), StandardCharsets.UTF_8));
        this.employeeRepository = employeeRepository;
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
                    if (command != null && command.equals("RFID")) {
                        handleEmployeeMessage();
                    }
                }
            } catch (IOException e) {
                System.out.println("End of stream reached. No more data to read.");
            }
        });

        listenerThread.setDaemon(true);
        listenerThread.start();
    }

    private void handleEmployeeMessage() throws IOException {
        String rfid = in.readLine();
        System.out.println("Received RFID: " + rfid);

        EmployeeDto employee = employeeRepository.findById(rfid)
                .map(EmployeeMapper::toDto)
                .orElse(null);

        if (employee == null) {
            System.out.println("Employee not found in database");
            out.write("404");
            out.newLine();
            out.flush();
        } else {
            // Employee found in database, now verify with face recognition
            System.out.println("Employee found in database, starting face recognition...");

            boolean faceVerified = performFaceRecognition(rfid);

            if (faceVerified) {
                // Face recognition successful, send employee data
                String json = mapper.writeValueAsString(employee);
                System.out.println("Face verified! Sending employee data: " + json);
                out.write(json);
                out.newLine();
                out.flush();
            } else {
                // Face recognition failed
                System.out.println("Face recognition failed for RFID: " + rfid);
                out.write("FACE_VERIFICATION_FAILED");
                out.newLine();
                out.flush();
            }
        }
    }

    private boolean performFaceRecognition(String rfid) {
        try {
            System.out.println("Starting face recognition process for RFID: " + rfid);

            // Get the absolute path to the known_faces directory
            String knownFacesPath = new File("src/main/resources/known_faces").getAbsolutePath();

            ProcessBuilder processBuilder = new ProcessBuilder(
                    "python3",
                    "src/main/java/com/example/RFID/utils/face_recognition_server.py",
                    rfid,
                    knownFacesPath
            );

            // Set working directory if needed (adjust path as necessary)
            processBuilder.directory(new File("."));

            // Redirect error stream to output stream for debugging
            processBuilder.redirectErrorStream(true);

            // Start the process
            Process process = processBuilder.start();

            // Read the output
            BufferedReader reader = new BufferedReader(
                    new InputStreamReader(process.getInputStream())
            );

            String line;
            StringBuilder output = new StringBuilder();
            while ((line = reader.readLine()) != null) {
                output.append(line).append("\n");
                System.out.println("Face recognition output: " + line);
            }

            // Wait for the process to complete (with timeout)
            boolean finished = process.waitFor(30, java.util.concurrent.TimeUnit.SECONDS);

            if (!finished) {
                System.out.println("Face recognition timed out");
                process.destroyForcibly();
                return false;
            }

            int exitCode = process.exitValue();
            System.out.println("Face recognition process exit code: " + exitCode);

            // Exit code 0 means face verified successfully
            return exitCode == 0;

        } catch (Exception e) {
            System.err.println("Error during face recognition: " + e.getMessage());
            e.printStackTrace();
            return false;
        }
    }
}