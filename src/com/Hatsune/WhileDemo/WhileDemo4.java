package com.Hatsune.WhileDemo;

public class WhileDemo4 {
    static void main() {
        double height=8848860;
        double a=0.1;
        int times=0;
        while(a<=height){
            //变量名*=2即为指数级增加
            a*=2;
            times++;
        }
        System.out.println(times);
    }
}
