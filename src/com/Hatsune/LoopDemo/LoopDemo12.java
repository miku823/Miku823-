package com.Hatsune.LoopDemo;

public class LoopDemo12 {
    //制表符:是一个长度可变的大空格，打印表格时可以使其上写对其(\t)
    static void main() {
        for (int i = 1; i <= 9; i++) {
            for (int i1 = 1; i1 <= i; i1++) {
                //\t是制表符，可用空格代替
                System.out.print(i+"*"+i1+"="+i*i1+"\t");
            }
            System.out.println();
        }
    }
}
