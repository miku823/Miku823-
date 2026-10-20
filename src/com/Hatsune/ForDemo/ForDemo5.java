package com.Hatsune.ForDemo;

import java.util.Scanner;

public class ForDemo5 {
    static void main() {
        Scanner sc=new Scanner(System.in);
        int i = sc.nextInt();
        int j = sc.nextInt();
        int max = i>j?i:j;
        int min = i<j?i:j;
        int count = 0;
        for(int a=min;a<=max;a++){
            if(a%3==0 && a%5==0){
                count++;
            }
        }
        System.out.println(count);
    }
}
