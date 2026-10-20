package com.Hatsune.Operater;

public class Operater4 {
    static void main(){
        //数据转换类型隐性转换，转换为double
        //第一步b+s，将byte,short转换为int
        //第二步s+d，将int转换为double
        //输出为double
       byte b = 100;
       short s = 100;
       double d = 20.3;
       double result1 = b + s + d;
       System.out.println(result1);

       //数据转换类型为强制转换，转换为byte（可能会丢失精度）
       //第一步s1+s2，将short转化为int
       //第二步将int强制转化为byte，输出结果为44
       short s1 = 100;
       short s2 = 200;
       //修改方案1：将s1,s2转换为int，再强制转换为byte
       byte result2 = (byte)(s1 + s2);
       System.out.println(result2);
       //修改方案2：将和数定义为int
       int result3 = s1 + s2;
       System.out.println(result3);

    }
}
