package com.Hatsune.LoopDemo;

import java.util.Random;
import java.util.Scanner;

public class LoopDemo7 {
    static void main() {
        Random sc = new Random();
        //在括号里写的数据不包含在范围内，并且默认从0开始(idle会自动补充bound:和origin:)
        int n = sc.nextInt(1,101);
        Scanner io = new Scanner(System.in);
        int a = 0;
        while (true) {
            a = io.nextInt();
            if (a == n) {
                System.out.println("正确");
                break;
            } else if (a < n) {
                System.out.println("偏小，请重新输入");
            } else if (a > n) {
                System.out.println("偏大，请重新输入");
            }
        }
    }
}
