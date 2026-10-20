package com.Hatsune.variable;

import java.util.Scanner;

public class varableDEMO4 {
    static void main() {
        Scanner sc = new Scanner(System.in);
        double weight = sc.nextDouble();
        double height = sc.nextDouble();
        double bmi = weight / (height * height);
        System.out.println(bmi);


    }
}
