package com.Hatsune.ArrayDemo;

import java.util.Scanner;

public class ArrayDemo4 {
    //数组的动态初始化:创建数组的时候指定长度，由系统为数组分配初始值
    //格式:int arr[] = new int[lehgth]
    static void main() {
        Scanner sc = new Scanner(System.in);
        int arr[] = new int[5];
        for (int i = 0; i < arr.length; i++) {
            int num = sc.nextInt();
            arr[i] = num;
        }
        for (int i = 0; i < arr.length; i++) {
            System.out.print(arr[i]);
        }
    }
}
