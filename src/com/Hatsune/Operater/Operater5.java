package com.Hatsune.Operater;

public class Operater5 {
    static void main() {
        //实现字母的大小写转换
        //char强制转换为int，再加32，再强制转换为char
        char c = 'A';
        char c1 = (char)(c + 32);
        System.out.println(c1);
    }
}
