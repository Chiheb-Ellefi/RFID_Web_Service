package com.example.RFID.entities;

import com.fasterxml.jackson.annotation.JsonProperty;

public enum Role {
    @JsonProperty("MANAGER") MANAGER,
    @JsonProperty("SIMPLE") SIMPLE,
    @JsonProperty("ADMIN") ADMIN
}
