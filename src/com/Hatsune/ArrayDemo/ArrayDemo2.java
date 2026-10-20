package com.Hatsune.ArrayDemo;

public class ArrayDemo2 {
    static void main() {
        //数据的访问:利用索引(从0开始，连续加1，不间断)获取数据和修改数据
        /*
        数据的获取
        变量 = 数组名[索引]
        如:int num = arr[5]

        数据的修改
        数据名[索引] = 数据值
        如:arr[5] = 10
         */

        int[] arr = new int[]{10,20,30,40,50};
        int num = arr[4];
        System.out.println(num);
        arr[1] = 100;
        System.out.println(arr[1]);
    }
}
