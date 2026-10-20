package com.Hatsune.Operater;

import java.util.Scanner;

public class Operater8 {
    static void main() {
        Scanner sc = new Scanner(System.in);
        int a = sc.nextInt();
        int b = a % 3;
        System.out.println(b);
        boolean result = b == 0;
        System.out.println(result);
    }
}
