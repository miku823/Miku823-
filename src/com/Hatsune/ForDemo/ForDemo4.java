package com.Hatsune.ForDemo;

public class ForDemo4 {
    static void main() {
        int a=0;
        for(int i=1;i<=100;i++){
            if(i%2==0) {
                a += i;
            }
        }
        System.out.println(a);
    }
}
