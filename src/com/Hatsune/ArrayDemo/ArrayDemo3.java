package com.Hatsune.ArrayDemo;

public class ArrayDemo3 {
    static void main() {
        //数组的遍历:
        int[] arr = {1, 2, 3, 4, 5};
        //获取数组的长度:arr.length
        int a = arr.length;
        for (int i = 0; i < a ; i++) {
            int num = arr[i];
            System.out.println(num);
        }
    }
}
