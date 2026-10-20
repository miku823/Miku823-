package com.Hatsune.ToolsDemo;

public class ToolsDemo4 {
    //制表符:是一个长度可变的大空格，打印表格时可以使其上写对其(\t)
    //定义打印99乘法表
    //没有参数的方法,在调用的时候实参也是空着的
    public static void printMulTable(){
        for (int i = 1; i <= 9; i++) {
            for (int i1 = 1; i1 <= i; i1++) {
                System.out.print(i + "*" + i1 + "=" + i * i1 + "\t");
            }
            System.out.println();
        }
    }
    static void main() {
        printMulTable();
    }
}
