package com.Hatsune.IfDemo;

import java.util.Scanner;

public class IfDemo {
    static void main() {
        Scanner sc = new Scanner(System.in);
        double temperture = sc.nextDouble();
        if(temperture >= 37.3){
            System.out.println("体温异常");
        }
        else{
            System.out.println("体温正常");
        }
    }
}
