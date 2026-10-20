package com.Hatsune.Operater;

import java.util.Scanner;

public class Operater2 {
    static void main() {
        Scanner sc = new Scanner(System.in);
        int a = sc.nextInt();
        /*double number1 = a / 100;
        double number2 = a / 10 - number1 * 10;
        double number3 = a / 1 - number2 * 10 - number1 * 100;*/
        // 用取余运算符实现,获取a的个位数,十位数,百位数
        double number1 = a % 10;
        double number2 = a / 10 % 10;
        double number3 = a / 100 % 10;
        System.out.println("个位是：" + number1);
        System.out.println("十位是：" + number2);
        System.out.println("百位是：" + number3);

    }
}
