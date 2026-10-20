package com.Hatsune.variable;

public class variable {
    static void main() {
        /*微信余额：0元
        * 支付宝余额：10元
        * 银行卡余额：20元
        * 问题一：现在一共多少钱
        * 问题二：微信收了10元红包，又发了2元红包，余额多少*/

        //1.定义一个变量记录微信余额（浮点类型）
        double wechatBalance = 0;

        //2.定义一个变量记录支付宝余额（浮点类型）
        double alipayBalance = 10;

        //3.定义一个变量记录银行卡余额（浮点类型）
        double bankBalance = 20;

        //4.输出现在一共多少钱
        System.out.println(wechatBalance + alipayBalance + bankBalance) ;

        //5.微信收了10元红包
        wechatBalance += 10;
        System.out.println(wechatBalance);

        //6.又发了2元红包
        wechatBalance -= 2;

        //7.输出微信余额
        System.out.println(wechatBalance);
    }
}
