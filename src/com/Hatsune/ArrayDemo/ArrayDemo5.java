package com.Hatsune.ArrayDemo;

import java.util.Scanner;

public class ArrayDemo5 {
    static void main() {
        int[] arr = {33,5,22,44,55,33};
        Scanner sc = new Scanner(System.in);
        int number = sc.nextInt();

        //boolean flag = false;
        int count = 0;

        for (int i = 0; i < arr.length; i++) {
            if(number == arr[i]){
                System.out.println(i);
                count++;
                break;
            }
        }
        //if(!flag){
            //System.out.println("数据不存在");
        //}
        if(count==0){
            System.out.println("数据不存在");
        }
    }
}
