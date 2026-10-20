package com.Hatsune.SwitchDemo;

import java.util.Scanner;

public class SwitchDemo2 {
    static void main() {
        //default的位置
        //位置：case和default没有上下之分，位置可以任意书写
        //一般来讲，default放在最后面，其他case放在前面，且case一般按顺序书写
        //省略：default可以省略，当所有的case都不满足时，没有任何的输出结果
    /*    Scanner sc = new Scanner(System.in);
        int a = sc.nextInt();
        switch (a) {
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
        }   */
        //case穿透：当case没有break时，会继续执行下一个case
        Scanner sc = new Scanner(System.in);
        int a = sc.nextInt();
        switch(a) {
            case 1:
                System.out.println("run");
            case 2:
                System.out.println("swim");
            case 3:
                System.out.println("walk");
            case 4:
                System.out.println("cycle");
            case 5:
                System.out.println("boxing");
            case 6:
                System.out.println("climb");
            case 7:
                System.out.println("eating");
            default:
                System.out.println("error");
        }
    }
}