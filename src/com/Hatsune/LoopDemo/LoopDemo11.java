package com.Hatsune.LoopDemo;

public class LoopDemo11 {
    static void main() {
        //打印平行四边形
        for (int i = 1; i <= 3; i++) {
            for (int i1 = 1; i1 <= 3 - i; i1++) {
                System.out.print(" ");
            }
            for (int i2 = 1; i2 <= 1 + 2 * i; i2++) {
                System.out.print("*");
            }
            System.out.println();
        }

        System.out.println();

        //打印菱形
        for (int i = 1; i <= 4; i++) {
            for (int i1 = 1; i1 <= 4 - i; i1++) {
                System.out.print(" ");
            }
            for (int i2 = 1; i2 <= -1 + 2 * i; i2++) {
                System.out.print("*");
            }
            System.out.println();
        }
        for (int i = 1; i <= 3; i++) {
            for (int i1 = 2; i1 >= 3 - i; i1--) {
                System.out.print(" ");
            }
            for (int i2 = 5; i2 >= -1 + 2 * i; i2--) {
                System.out.print("*");
            }
            System.out.println();
        }

        System.out.println();

        //打印空心菱形
        for (int i = 1; i <= 3; i++) {
            for (int i1 = 1; i1 <= 3 - i; i1++) {
                System.out.print(" ");
            }
            for (int i2 = 1; i2 <= -1 + 2 * i; i2++) {
                //保头保尾去中间
                if(i2==1 || i2==-1+2*i){
                    System.out.print("*");
                }else{
                    System.out.print(" ");
                }
            }
            System.out.println();
        }
        for (int i = 1; i <= 3; i++) {
            for (int i1 = 2; i1 >= 3 - i; i1--) {
                System.out.print(" ");
            }
            for (int i2 = 3; i2 >= -1 + 2 * i; i2--) {
                //保头保尾去中间
                if(i2==3 || i2==-1+2*i){
                    System.out.print("*");
                }else{
                    System.out.print(" ");
                }
            }
            System.out.println();
        }
    }
}
