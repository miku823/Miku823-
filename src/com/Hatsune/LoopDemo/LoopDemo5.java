package com.Hatsune.LoopDemo;

public class LoopDemo5 {
    static void main() {
        for (int i = 1; i <= 10; i++) {
            if(i==3){
                continue;
            }
            System.out.println(i);
        }
    }
}
//break:不能单独书写，只能写在switch或者循环之中，表示结束
//continue:不能单独书写，只能写在循环中，结束本次循环，继续下次循环
