package com.Hatsune.IfDemo;

import java.util.Scanner;

public class IfDemo3 {
    static void main() {
        Scanner sc = new Scanner(System.in);
        int a = sc.nextInt();
        double zongjiaX = a * 0.8;
        System.out.println(zongjiaX);
        if(a >= 10 & a < 50){
            double zongjia = a - 8;
            double flag1 = zongjia < zongjiaX ? zongjia : zongjiaX;
            System.out.println(zongjia);
            System.out.println(flag1);
        }
        else if(a >= 50 & a < 100){
            double zongjia2 = a - 30;
            double flag2 = zongjia2 < zongjiaX ? zongjia2 : zongjiaX;
            System.out.println(zongjia2);
            System.out.println(flag2);
        }
        else if(a >= 100 & a < 200){
            double zongjia3 = a - 50;
            double flag3 = zongjia3 < zongjiaX ? zongjia3 : zongjiaX;
            System.out.println(zongjia3);
            System.out.println(flag3);
        }
        else if(a >= 200){
            double zongjia4 = a - 90;
            double flag4 = zongjia4 < zongjiaX ? zongjia4 : zongjiaX;
            System.out.println(zongjia4);
            System.out.println(flag4);
        }
        else if(a < 10 & a > 0){
            System.out.println(a);
        }
        else{
            System.out.println("输入错误");
        }
    }
}
