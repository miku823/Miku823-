package com.Hatsune.IfDemo;

import java.util.Scanner;

public class IfDemo2 {
    static void main() {
        int blood = 200;
        Scanner sc = new Scanner(System.in);
        int attack = sc.nextInt();
        int recover = sc.nextInt();
        if(blood <= attack){
            int blood1 = 1 + recover;
            if(blood1 >= 200){
                System.out.println("剩余血量为200");
            }
            else{
                System.out.println("剩余血量为" + blood1);
            }
        }
        else{
            int blood2 = blood - attack + recover;
            if(blood2 >= blood){
                System.out.println("剩余血量为200");
            }
            else{
                System.out.println("剩余血量为" + blood2);
            }
        }
    }
}
