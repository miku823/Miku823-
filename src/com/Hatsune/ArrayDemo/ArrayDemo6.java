package com.Hatsune.ArrayDemo;

public class ArrayDemo6 {
    //max记录的数据一定是数组里面的数据
    //max的初始值不能设置为0
    static void main() {
        int[] arr = {33,5,22,44,55};
        int max = arr[0];
        for (int i = 1; i < arr.length; i++) {
            if(max<arr[i]){
                max = arr[i];
            }
        }
        System.out.println(max);
    }
}
