package com.Hatsune.ArrayDemo;

import java.util.Random;

public class ArrayDemo7 {
    static void main() {
        //前置练习
        /*int a = 10;
        int b = 20;
        int mid = a;
        a = b;
        b = mid;
        System.out.println(a);
        System.out.println(b);*/

        //打乱数组中的数据
        int[] arr = {1,2,3,4,5,6,7,8,9,10};

        Random r = new Random();

        for (int i = 0; i < arr.length; i++) {
            int randomling = r.nextInt(arr.length);
            int temp = arr[i];
            arr[i] = arr[randomling];
            arr[randomling] = temp;
        }
        for (int i = 0; i < arr.length; i++) {
            System.out.println(arr[i]);
        }
    }
}
