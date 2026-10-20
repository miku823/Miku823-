package com.Hatsune.Operater;

public class Operater3 {
    static void main() {
        int seconds = 3661;
        int minutes = seconds / 60 % 60;
        int hours = seconds / 3600 % 24;
        int second2 = seconds - hours * 3600 - minutes * 60;
        System.out.println(hours + " " + minutes + " " + second2);
    }
}
