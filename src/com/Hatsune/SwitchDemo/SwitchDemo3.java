package com.Hatsune.SwitchDemo;

import java.util.Scanner;

public class SwitchDemo3 {
    static void main() {
        Scanner sc = new Scanner(System.in);
        int month = sc.nextInt();
        switch(month){
            case 12,1,2:
                System.out.println("winter");
                break;
            case 3,4,5:
                System.out.println("spring");
                break;
            case 6,7,8:
                System.out.println("summer");
                break;
            case 9,10,11:
                System.out.println("autumn");
                break;
        }
    }
}
