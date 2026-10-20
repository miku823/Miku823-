package com.Hatsune.Operater;

import java.util.Scanner;

public class Operater7 {
    static void main() {
        // 输入两个double类型的数据
        Scanner sc = new Scanner(System.in);
        System.out.println();
        double a = sc.nextDouble();
        System.out.println();
        double b = sc.nextDouble();
        // 比较a和b的大小
        boolean result = a >= b;
        System.out.println(result);
    }
}
