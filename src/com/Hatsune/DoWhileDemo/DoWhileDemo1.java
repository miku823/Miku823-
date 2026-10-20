package com.Hatsune.DoWhileDemo;

public class DoWhileDemo1 {
    static void main() {
        //do……while循环格式:
        /*do{
        循环体语句;
        条件控制语句;
        }while(条件判断语句)
         */
        //特点:先执行后判断
        int i = 1;
        do{
            System.out.println("Hello World");
            i++;
        }while(i<=5);
    }
}
