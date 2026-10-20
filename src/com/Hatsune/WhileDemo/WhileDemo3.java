package com.Hatsune.WhileDemo;

public class WhileDemo3 {
    static void main() {
        double i = 100000;
        int year = 0;
        while (i <= 200000) {
            i = i + i * 0.017;
            year++;
        }
        System.out.println(year);
    }
}