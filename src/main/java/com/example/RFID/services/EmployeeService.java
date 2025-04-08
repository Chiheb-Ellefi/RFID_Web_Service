package com.example.RFID.services;

import com.example.RFID.dto.EmployeeDto;
import com.example.RFID.mappers.EmployeeMapper;
import com.example.RFID.repositories.EmployeeRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

@Service
public class EmployeeService {
    private final EmployeeRepository employeeRepository;
    @Autowired
    public EmployeeService(EmployeeRepository employeeRepository) {
        this.employeeRepository = employeeRepository;
    }
    public List<EmployeeDto> findAll() {
        return employeeRepository.findAll().stream().map(EmployeeMapper::toDto).collect(Collectors.toList());
    }
    public EmployeeDto findOne(String rfid) {
        return employeeRepository.findById(rfid).map(EmployeeMapper::toDto).orElseThrow(()->new  RuntimeException("Employee with RFID "+rfid+" not found"));
    }
    public EmployeeDto createOne(EmployeeDto employee) {
        return EmployeeMapper.toDto(employeeRepository.save(EmployeeMapper.toEntity(employee)));
    }
    public void delete(String rfid) {
        employeeRepository.deleteById(rfid);
    }
}
