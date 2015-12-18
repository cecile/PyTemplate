package com.{{lower application}};

import org.springframework.boot.*;
import org.springframework.boot.autoconfigure.*;
import org.springframework.stereotype.*;
import org.springframework.web.bind.annotation.*;

@RestController
@EnableAutoConfiguration
public class {{application}}Application {

    @RequestMapping("/")
    String home() {
        return "Hello from {{application}}!";
    }

    public static void main(String[] args) throws Exception {
        SpringApplication.run({{application}}Application.class, args);
    }

}