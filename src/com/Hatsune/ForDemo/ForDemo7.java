package com.Hatsune.ForDemo;

import java.util.Scanner;

public class ForDemo7 {
    static void main() {
        Scanner sc=new Scanner(System.in);
        int sum = 0;
        int a = sc.nextInt();
        for(int i=1;i<=a;i++){
            if(i%2==0){
                sum-=i;
            }
            else{
                sum+=i;
            }
        }
        System.out.println(sum);
    }
}
