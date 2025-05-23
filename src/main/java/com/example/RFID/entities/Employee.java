    package com.example.RFID.entities;

    import jakarta.persistence.*;
    import lombok.*;

    import java.util.Date;
    @Builder
    @Getter
    @Setter
    @AllArgsConstructor
    @NoArgsConstructor
    @Entity
    @Table(name = "employees")
    public class Employee {
        @Id
        private String rfid;
        @Column(nullable = false)
        private String username;
        @Column(nullable = false,unique = true)
        private String email;
        private String phoneNumber;
        private Date birthDate;
        private String department;
        @Column(nullable = false)
        @Enumerated(EnumType.STRING)
        private Role role;
        @Column(nullable = false)
        @Enumerated(EnumType.STRING)
        private Gender gender;

    }
