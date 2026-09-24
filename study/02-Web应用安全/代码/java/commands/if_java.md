# if_java

> **分类**：条件与循环
> **说明**：条件判断和循环语句

---

## 语法

```java
if (condition) { ... } else if (cond2) { ... } else { ... }
```

## 循环类型

for / while / do...while / for-each

## 控制语句

break / continue / return

## 示例代码

```java
// if/else if/else
int age = 18;
if (age >= 18) {
    System.out.println("成年");
} else if (age >= 6) {
    System.out.println("少年");
} else {
    System.out.println("儿童");
}

// 三元运算符
int x = 10;
String result = x > 5 ? "大于5" : "小于等于5";

// switch
int day = 1;
switch (day) {
    case 1:
        System.out.println("星期一");
        break;
    case 2:
        System.out.println("星期二");
        break;
    default:
        System.out.println("其他");
}

// switch 表达式 (Java 14+)
String dayName = switch (day) {
    case 1 -> "星期一";
    case 2 -> "星期二";
    default -> "其他";
};

// for 循环
for (int i = 0; i < 5; i++) {
    System.out.println(i);
}

// for-each 循环（遍历数组/集合）
int[] nums = {1, 2, 3, 4, 5};
for (int num : nums) {
    System.out.println(num);
}

// while 循环
int count = 0;
while (count < 5) {
    System.out.println(count);
    count++;
}

// do...while 循环（至少执行一次）
int i = 0;
do {
    System.out.println(i);
    i++;
} while (i < 5);

// break 和 continue
for (int j = 0; j < 10; j++) {
    if (j == 3) continue;  // 跳过3
    if (j == 7) break;     // 到7停止
    System.out.println(j);
}

// 带标签的 break
outer:
for (int i = 0; i < 3; i++) {
    for (int j = 0; j < 3; j++) {
        if (i == 1 && j == 1) break outer;
        System.out.println(i + ", " + j);
    }
}
```
