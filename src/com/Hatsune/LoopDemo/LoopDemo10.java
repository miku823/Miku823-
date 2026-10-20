package com.Hatsune.LoopDemo;

public class LoopDemo10 {
    static void main() {
        for (int i = 1; i <= 3; i++) {
            for (int i1 = 2; i1 >= i; i1--) {
                System.out.print(" ");
            }
            for (int i2 = 1; i2 <= 5; i2++) {
                System.out.print("*");
            }
            System.out.println();
        }
    }
}
