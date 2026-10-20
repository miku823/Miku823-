package com.Hatsune.WhileDemo;

import java.util.Scanner;

public class WhileDemo5 {
    static void main() {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int sum = 0;
        if (n < 0) {
            n = n * -1;
        }
        //以下的while循环的含义:当数字不为0时，取最后一位数字
        while(n!=0){//!=是不等于的意思
            int a = n%10;//取余删掉最后一位
            sum+=a;//对最后一位进行累加
            n/=10;//整数除法舍弃小数，只留小数点前的整数
        }
        System.out.println(sum);
    }
}
