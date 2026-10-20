package com.Hatsune.LoopDemo;

public class LoopDemo9 {
    static void main() {
        for (int i = 1; i <= 5; i++) {
            for (int i1 = 1; i1 <= i; i1++) {
                System.out.print("*");
            }
            System.out.println();
        }
        for (int i = 0; i < 5; i++) {
            for (int i1 = 5; i1 > i; i1--) {
                System.out.print("*");
            }
            System.out.println();
        }
    }
}
