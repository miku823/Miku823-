package com.Hatsune.ToolsDemo;

//创建方法类型
//定义格式:public static 返回值类型 方法名(参数1,参数2){
//                  方法体
//                  return 返回值}
//以下为实例
public class ToolsDemo1 {
    public static int getSum(int a,int b) {
        int sum = a + b;
        return sum;
    }
    //方法之间相互平行,不能嵌套
    //方法不会自己运行,需要调用
    //小括号的参数需要一一对应(个数，类型对应)

    //调用格式:方法名(参数1,参数2);
    static void main() {
        int add = getSum(10,20);
        System.out.println(add);
    }
}
