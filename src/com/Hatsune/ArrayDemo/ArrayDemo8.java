package com.Hatsune.ArrayDemo;

import java.util.Random;

public class ArrayDemo8 {
    static void main() {
        Random r = new Random();
        int[] arr = new int[10];
        for (int i = 0; i < arr.length;) {
            //随机数自动生成origin(开始，包含开始的数据),bound(结束,不包含结束的数字)
            int n = r.nextInt(1, 101);
            int count = 0;
            for (int i1 = 0; i1 < arr.length; i1++) {
                if(n == arr[i1]){
                    count++;
                    break;
                }
            }
            if(count == 0){
                arr[i] = n;
                i++;
            }
        }
        for (int i = 0; i < arr.length; i++) {
            System.out.print(arr[i]+" ");
        }
        System.out.println();
    }
}
