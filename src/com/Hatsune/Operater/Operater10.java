package com.Hatsune.Operater;

import java.util.Scanner;

public class Operater10 {
    static void main() {
        //&&是逻辑与操作符，只有两个操作数都为true时，结果才为true，否则为false。
        //||是逻辑或操作符，至少有一个操作数为true时，结果才为true，否则为false。

        //验证一个四位数是否是回文数
        Scanner sc = new Scanner(System.in);
        int a = sc.nextInt();
        int b = a % 10;
        int c = a / 10 % 10;
        int d = a / 100 % 10;
        int e = a / 1000 % 10;
        boolean flag = b == e && c == d;
        System.out.println(flag);

        //验证一个数是否为7的有缘数
        int number = sc.nextInt();
        int f = number % 10;
        int g = number / 10 % 10;
        boolean flag2 = f == 7 || g == 7 || number % 7 == 0;
        System.out.println(flag2);
    }
}
