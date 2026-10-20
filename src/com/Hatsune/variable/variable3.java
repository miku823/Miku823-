package com.Hatsune.variable;

public class variable3 {
    static void main() {
        double weight = 67.0;
        double height = 1.75;
        double bmi = weight / (height * height);
        System.out.println(bmi);
        //Math.sqrt()方法可以计算平方根
        //Math.pow()方法可以计算指数,参数为底数和指数
        double height2 = Math.sqrt(weight / bmi);
        System.out.println(height2);
    }
}
