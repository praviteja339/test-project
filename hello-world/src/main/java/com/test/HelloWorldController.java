package com.test;

import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

// @Controller
// @ResponseBody
@RestController
public class HelloWorldController {

    @RequestMapping("/")
    String hello() {
        return "Hello World";
    }

}