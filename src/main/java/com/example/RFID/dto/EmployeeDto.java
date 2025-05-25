package com.example.RFID.dto;

import com.example.RFID.entities.Gender;
import com.example.RFID.entities.Role;
import lombok.*;


import java.io.Serializable;
import java.util.Date;
@Builder
@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
public class EmployeeDto  implements Serializable {
    private String rfid;
    private String username;
    private String email;
    private String phoneNumber;
    private Date birthDate;
    private String department;
    private Role role;
    private Gender gender;
    private String imageUrl;
}
