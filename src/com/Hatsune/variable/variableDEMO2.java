package com.Hatsune.variable;

public class variableDEMO2 {
    static void main() {
        byte a = 10;
        System.out.println(a);
        short b = 32677;
        System.out.println(b);
        int c = 2147483647;
        System.out.println(c);
        //定义long类型变量，需要以L结尾，否则会被默认识别为int类型
        long d = 9223372036854775807L;
        System.out.println(d);
        //定义float类型变量，需要以F结尾，否则会被默认识别为double类型
        float e = 10.5F;
        System.out.println(e);
        double f = 10.5;
        System.out.println(f);
        char g = 'm';
        System.out.println(g);
        boolean h = true;
        System.out.println(h);
    }
}
