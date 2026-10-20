package com.Hatsune.Operater;

public class Operater11 {
    //?是三元运算符，它的作用是根据条件判断执行不同的操作
    //语法：条件表达式？表达式1：表达式2
    //如果条件表达式为true，就执行表达式1，否则执行表达式2
    //注意：条件表达式必须是布尔值，不能是其他类型的值

    //实现两个整数的比较，返回较大的那个
    static void main(){
        int a = 10;
        int b = 20;
        int c = a > b ? a : b;
        System.out.println(c);
    }
}
