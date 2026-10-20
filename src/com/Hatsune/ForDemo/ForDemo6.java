package com.Hatsune.ForDemo;

public class ForDemo6 {
    static void main() {
        int a = 0;
        int b = 1;
        int c = 0;
        for(int i=3;i<=10;i++){
            //将a，b的值赋值给c
            c=a+b;
            //不断更改a，b的值
            a=b;
            b=c;
        }
        System.out.println(c);
    }
}
