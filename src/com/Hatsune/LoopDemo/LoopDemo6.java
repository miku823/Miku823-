package com.Hatsune.LoopDemo;

public class LoopDemo6 {
    static void main() {
        for (int i = 1; i <= 100; i++) {
            int a = i % 7;
            int b = i % 10;
            int c = i / 10 % 10;
            if (a == 0 | b == 7 | c == 7) {
                System.out.println("过");
                continue;
            }
            System.out.println(i);
        }
    }
}
