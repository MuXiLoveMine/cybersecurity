# System.out.println

> **分类**：输出
> **说明**：标准输出流打印并换行

---

## 语法

```java
System.out.println(Object obj);
```

## 相关方法

System.out.print() - 不换行\nSystem.out.printf() - 格式化输出\nSystem.err.println() - 错误输出

## 示例代码

```java
// 基本输出
System.out.println("Hello, World!");
System.out.println(42);
System.out.println(3.14);

// 不换行
System.out.print("输入: ");

// 格式化输出
System.out.printf("姓名: %s, 年龄: %d%n", "Alice", 25);
System.out.printf("浮点数: %.2f%n", 3.14159);

// 错误输出
System.err.println("发生错误！");

// 字符串拼接输出
String name = "Bob";
int age = 30;
System.out.println("姓名: " + name + ", 年龄: " + age);

// 数组输出（需要 Arrays.toString）
int[] arr = {1, 2, 3};
System.out.println(java.util.Arrays.toString(arr));

// 对象输出（自动调用 toString）
Object obj = "test";
System.out.println(obj);

// 多行输出
System.out.println("第一行");
System.out.println("第二行");
```
