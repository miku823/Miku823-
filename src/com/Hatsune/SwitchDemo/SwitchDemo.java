package com.Hatsune.SwitchDemo;

import java.util.Scanner;

public class SwitchDemo {
    static void main() {
        Scanner sc = new Scanner(System.in);
        int a = sc.nextInt();
        switch(a) {
            case 1:
                System.out.println("run");
                break;
            case 2:
                System.out.println("swim");
                break;
            case 3:
                System.out.println("walk");
                break;
            case 4:
                System.out.println("cycle");
                break;
            case 5:
                System.out.println("boxing");
                break;
            case 6:
                System.out.println("climb");
                break;
            case 7:
                System.out.println("eating");
                break;
            default:
                System.out.println("error");
                break;
        }
    }
}
