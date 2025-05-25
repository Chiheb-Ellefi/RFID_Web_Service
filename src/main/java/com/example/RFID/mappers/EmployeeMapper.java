package com.example.RFID.mappers;

import com.example.RFID.dto.EmployeeDto;
import com.example.RFID.entities.Employee;

public class EmployeeMapper {
    public static EmployeeDto toDto(Employee employee) {
        return EmployeeDto.builder()
                .birthDate(employee.getBirthDate())
                .rfid(employee.getRfid())
                .email(employee.getEmail())
                .department(employee.getDepartment())
                .gender(employee.getGender())
                .phoneNumber(employee.getPhoneNumber())
                .role(employee.getRole())
                .username(employee.getUsername())
                .imageUrl(employee.getImageUrl())
                .build();

    }
    public static Employee toEntity(EmployeeDto employee) {
        return Employee.builder()
                .birthDate(employee.getBirthDate())
                .rfid(employee.getRfid())
                .email(employee.getEmail())
                .department(employee.getDepartment())
                .gender(employee.getGender())
                .phoneNumber(employee.getPhoneNumber())
                .role(employee.getRole())
                .username(employee.getUsername())
                .imageUrl(employee.getImageUrl())
                .build();
    }
}
