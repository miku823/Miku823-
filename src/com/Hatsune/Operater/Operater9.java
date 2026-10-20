package com.Hatsune.Operater;

import java.util.Scanner;

public class Operater9 {
    static void main() {
        //&是与操作符，只有两个操作数都为true时，结果才为true，否则为false。
        //|是或操作符，至少有一个操作数为true时，结果才为true，否则为false。
        //^是异或操作符，当两个操作数不相同时，结果为true，否则为false。
        //~是取反操作符，对操作数进行取反操作，结果为true变false，false变true。
        //!是逻辑操作符，对操作数进行逻辑取反操作，结果为true变false，false变true。
        //&&是逻辑与操作符，只有两个操作数都为true时，结果才为true，否则为false。
        //||是逻辑或操作符，至少有一个操作数为true时，结果才为true，否则为false。
        //?:三目操作符，根据条件判断执行不同的语句。
        Scanner sc = new Scanner(System.in);
        int a = sc.nextInt();
        boolean result = a > 1 & a < 10;
        System.out.println(result);

        int b = sc.nextInt();
        boolean result1 = b <= 1 | b >= 10;
        System.out.println(result1);
    }
}
