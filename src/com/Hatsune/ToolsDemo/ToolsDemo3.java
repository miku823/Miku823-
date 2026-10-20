package com.Hatsune.ToolsDemo;

public class ToolsDemo3 {
    public static void printarr(int[] arr){
        //定义方法遍历数组
        //没有返回值,不需要把结果返回调用
        for (int i = 0; i < arr.length; i++) {
            if(i==arr.length-1){
                System.out.print(arr[i]);
            }
            else{
                System.out.print(arr[i]+", ");
            }
        }
    }

    static void main() {
        System.out.print("[");
        int[] arr = {1,2,3,4,5};
        printarr(arr);
        System.out.print("]");
    }
}
