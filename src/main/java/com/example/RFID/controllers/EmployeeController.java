package com.example.RFID.controllers;

import com.example.RFID.dto.EmployeeDto;
import com.example.RFID.services.EmployeeService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/employees")
public class EmployeeController {
    private final EmployeeService employeeService;
    EmployeeController(EmployeeService employeeService) {
        this.employeeService = employeeService;
    }
    @GetMapping
    public ResponseEntity<List<EmployeeDto>> getAllEmployees() {
        List<EmployeeDto> response= employeeService.findAll();
        return new ResponseEntity<>(response, HttpStatus.OK);
    }
    @GetMapping("/{rfid}")
    public ResponseEntity<EmployeeDto> getEmployeeByRFID(@PathVariable String rfid) {
        EmployeeDto response= employeeService.findOne(rfid);
        if(response==null){
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);
        }
        return new ResponseEntity<>(response, HttpStatus.OK);
    }
    @PostMapping
    public ResponseEntity<EmployeeDto> createEmployee(@RequestBody EmployeeDto employeeDto) {

        EmployeeDto response=employeeService.createOne(employeeDto);
        return new ResponseEntity<>(response, HttpStatus.CREATED);
    }
    @DeleteMapping("/{rfid}")
    public ResponseEntity<String> deleteEmployee(@PathVariable String rfid) {
        employeeService.delete(rfid);
        return new ResponseEntity<>("Employee deleted successfully", HttpStatus.NO_CONTENT);
    }



}
