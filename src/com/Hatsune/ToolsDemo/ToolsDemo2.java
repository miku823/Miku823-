package com.Hatsune.ToolsDemo;

import java.util.Random;

public class ToolsDemo2 {
    public static boolean contain(int n,int[] arr) {
        for (int i = 0; i < arr.length; i++) {
            //遇到一个符合条件的,直接返回true
            //此时方法直接结束
            if(arr[i] == n){
                return true;
            }
        }
        //如果循环结束,数组里面所有的元素都判断完毕,还没找到一样的,直接返回false,表示num在arr中是不存在的
        return false;
    }
    static void main() {
        Random r = new Random();
        int[] arr = new int[10];
        for (int i = 0; i < arr.length;) {
            //随机数自动生成origin(开始，包含开始的数据),bound(结束,不包含结束的数字)
            int n = r.nextInt(1, 101);
            //对n进行判断,存在——不存,不存在——存
            boolean flag = contain(n, arr);
            //对flag进行判断
            if(!flag){
                arr[i] = n;
                //只有生成一个满足要求的随机数,索引才会自增
                i++;
            }
        }
        //遍历
        for (int i = 0; i < arr.length; i++) {
            System.out.print(arr[i]+" ");
        }
        System.out.println();
    }

}
