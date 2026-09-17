// HelloWorld.java
// 第一个 Java 程序

public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");

        // 变量
        String name = "张三";
        int age = 25;
        double height = 1.75;
        boolean isStudent = true;

        System.out.println("姓名: " + name);
        System.out.println("年龄: " + age);
        System.out.println("身高: " + height);
        System.out.println("是否学生: " + isStudent);

        // 基本数据类型演示
        byte b = 127;
        short s = 32767;
        int i = 100000;
        long l = 9999999999L;
        float f = 3.14f;
        double d = 3.1415926;
        char c = 'A';
        boolean bool = true;

        System.out.println("\n基本数据类型:");
        System.out.println("byte: " + b);
        System.out.println("short: " + s);
        System.out.println("int: " + i);
        System.out.println("long: " + l);
        System.out.println("float: " + f);
        System.out.println("double: " + d);
        System.out.println("char: " + c);
        System.out.println("boolean: " + bool);

        // 算术运算
        int x = 10, y = 3;
        System.out.println("\n算术运算:");
        System.out.println(x + " + " + y + " = " + (x + y));
        System.out.println(x + " - " + y + " = " + (x - y));
        System.out.println(x + " * " + y + " = " + (x * y));
        System.out.println(x + " / " + y + " = " + (x / y));
        System.out.println(x + " % " + y + " = " + (x % y));

        // 字符串
        String str = "Hello World";
        System.out.println("\n字符串操作:");
        System.out.println("长度: " + str.length());
        System.out.println("大写: " + str.toUpperCase());
        System.out.println("小写: " + str.toLowerCase());
        System.out.println("子串: " + str.substring(0, 5));
        System.out.println("拼接: " + str.concat("!"));

        // 格式化输出
        System.out.println("\n格式化输出:");
        System.out.printf("姓名: %s, 年龄: %d%n", name, age);
        System.out.printf("价格: ¥%.2f%n", 99.9);

        // 数组
        System.out.println("\n数组:");
        int[] nums = {1, 2, 3, 4, 5};
        for (int j = 0; j < nums.length; j++) {
            System.out.println("  nums[" + j + "] = " + nums[j]);
        }

        // 增强 for 循环
        System.out.println("\n增强 for 循环:");
        for (int num : nums) {
            System.out.print(num + " ");
        }
        System.out.println();
    }
}
