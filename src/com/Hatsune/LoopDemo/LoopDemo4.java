package com.Hatsune.LoopDemo;

import java.util.Scanner;

public class LoopDemo4 {
    static void main() {
        Scanner sc = new Scanner(System.in);
        int n = 0;
        int count = 0;
        while(true) {
            n = sc.nextInt();
            if(n>=2){
                break;
            }else{
                System.out.println("起来重写");
            }
        }
        for(int i=2;i<=n-1;i++){
            if(n%i==0){
                count++;
                //只要找到一个数字能被n整除，直接判断是否为质数
                break;
            }
        }
        if(count==0){
            System.out.println("true");
        }else{
            System.out.println("false");
        }
    }
}
