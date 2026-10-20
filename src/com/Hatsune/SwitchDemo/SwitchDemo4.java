package com.Hatsune.SwitchDemo;

import java.util.Scanner;

public class SwitchDemo4 {
    static void main() {
        //switch的新特性：
        //1.箭头标签,->表示结束,大括号可以省略
        //2.case后面可以写多个值
        //3.switch可以有运行结果
        //yield关键字
        /*int number = 3;
        switch(number){
            case 1 ->"1";
            case 2 -> "2";
            case 3 -> "3";
            default -> "error;
        }*/
       /* int number = 3;
        String name = switch(number) {
            case 1 -> {
                yield "1";
            }
            case 2 -> {
                yield "2";
            }
            case 3 -> {
                yield "3";
            }
            default -> {
                yield "default";
            }
        };
        System.out.println(name);*/
        Scanner sc = new Scanner(System.in);
        int a = sc.nextInt();
        int b = sc.nextInt();
        Scanner IO = new Scanner(System.in);
        String operater = IO.nextLine();
        int result =switch(operater){
            case "+" -> a+b;
            case "-" -> a-b;
            case "*" -> a*b;
            case "/" -> a/b;
            default -> 0;

        };
        System.out.println(result);
    }
}
