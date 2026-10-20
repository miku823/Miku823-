package com.Hatsune.variable;

public class variableDEMO {
    static void main() {
        int attack = 220;
        int defence = 85;
        double blood = 1012.5;
        double skill = 1.2;
        int attack2 = 210;
        int defence2 = 80;
        double blood2 = 1223.3;
        double skill2 = 1.3;
        double damage = attack - defence2;
        blood2 = blood2 - damage;
        System.out.println(blood2);//1083.3
        double damage2 = attack * skill - defence2;
        blood2 = blood2 - damage2;
        System.out.println(blood2);//899.3
    }
}
