package com.Hatsune.WhileDemo;

//本程序主要研究While与For的区别
//for循环主要用于知道循环的次数和范围
//while循环主要用于不知道循环的次数和范围，只知道循环的结束条件

public class WhileDemo2 {
    static void main() {
        for(int i=1;i<=10;i++){
            System.out.println(i);
        }
        //for类型代码下方无法再使用for循环内部的变量，即在for下方进行变量i有关运算程序无法识别

        int j = 1;
        while(j<=10){
            System.out.println(j);
            j++;
        }
        //while类型代码下方可以继续使用while循环使用过的变量，即变量j仍可在其他代码中参与运算
    }
}
