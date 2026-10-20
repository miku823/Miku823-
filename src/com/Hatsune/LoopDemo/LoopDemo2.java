package com.Hatsune.LoopDemo;

public class LoopDemo2 {
    //break:不能单独书写，只能写在switch或者循环中，表示结束，跳出
    //(100.fori)可以快速生成for循环
    static void main() {
        for (int i = 1; i <= 100; i++) {
            if (i == 15) {
                System.out.println(i);
                break;
            }
        }
    }
}
