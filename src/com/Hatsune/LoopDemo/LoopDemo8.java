package com.Hatsune.LoopDemo;

public class LoopDemo8 {
    static void main() {
        //循环嵌套的核心:内循环
        //print只打印不换行，println打印换行
        //换行代码写在外面，打印代码写在里面
        //换行在内循环之后不放在内循环之前，否则会多一个空行
        for (int i = 1; i <= 4; i++) {
            for (int i1 = 1; i1 <= 5; i1++) {
                System.out.print("*");
            }
            System.out.println();
        }
    }
}
