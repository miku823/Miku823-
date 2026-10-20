package com.Hatsune.LoopDemo;

import java.util.Scanner;

public class LoopDemo3 {
    static void main() {
        int blood = 200;
        int attack = 0;
        int recover = 0;
        Scanner sc = new Scanner(System.in);
        while(true){
            attack = sc.nextInt();
            if(attack>0){
                break;
            }else{
                System.out.println("当前受到的伤害不能为负数");
            }
        }
        while(true){
            recover = sc.nextInt();
            if(recover>0){
                break;
            }else{
                System.out.println("当前所回血量不能为负数");
            }
        }

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
