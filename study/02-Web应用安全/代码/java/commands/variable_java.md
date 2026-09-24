# variable_java

> **分类**：变量与类型
> **说明**：Java 是强类型语言，变量必须声明类型

---

## 语法

```java
type variableName = value;
```

## 基本类型

byte/short/int/long/float/double/char/boolean

## 引用类型

String/数组/类/接口

## 包装类

Integer/Long/Double/Boolean/Character

## 示例代码

```java
// 整数类型
byte b = 127;
short s = 32767;
int i = 2147483647;
long l = 9223372036854775807L;

// 浮点类型
float f = 3.14f;
double d = 3.14159265359;

// 字符和布尔
char c = 'A';
boolean bool = true;

// 字符串
String str = "Hello, World!";

// 数组
int[] nums = {1, 2, 3, 4, 5};
String[] names = new String[3];
int[][] matrix = new int[3][3];

// 常量
final int MAX_SIZE = 100;
final double PI = 3.14159;

// 类型转换
// 自动转换（小到大）
int x = 100;
long y = x;
double z = y;

// 强制转换（大到小，可能丢失精度）
double pi = 3.14;
int intPi = (int) pi;  // 3

// 包装类
Integer num = 42;          // 自动装箱
int primitive = num;       // 自动拆箱
int parsed = Integer.parseInt("123");
String strNum = Integer.toString(456);

// 字符串转数字
int a = Integer.parseInt("123");
double b = Double.parseDouble("3.14");
long c = Long.parseLong("999999999");

// 常用方法
String s = "Hello World";
s.length();          // 长度
s.charAt(0);         // 第0个字符
s.substring(0, 5);   // 子串
s.toLowerCase();     // 转小写
s.toUpperCase();     // 转大写
s.contains("World"); // 是否包含
s.equals("hello");   // 相等比较
```
