# class_java

> **分类**：类与对象
> **说明**：Java 面向对象编程

---

## 语法

```java
public class ClassName {\n  // fields\n  // constructors\n  // methods\n}
```

## 关键字

public/private/protected / static / final / abstract / interface / extends / implements

## 特性

封装 / 继承 / 多态 / 抽象

## 示例代码

```java
// 基本类
public class Person {
    // 字段（属性）
    private String name;
    private int age;

    // 构造函数
    public Person() {
        this.name = "Unknown";
        this.age = 0;
    }

    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }

    // getter 和 setter
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public int getAge() { return age; }
    public void setAge(int age) { this.age = age; }

    // 方法
    public void greet() {
        System.out.println("Hello, I'm " + name);
    }

    // toString
    @Override
    public String toString() {
        return "Person{name='" + name + "', age=" + age + "}";
    }
}

// 使用
Person p = new Person("Alice", 25);
p.greet();
System.out.println(p.getName());

// 继承
public class Student extends Person {
    private String studentId;

    public Student(String name, int age, String studentId) {
        super(name, age);  // 调用父类构造函数
        this.studentId = studentId;
    }

    public void study(String subject) {
        System.out.println(getName() + " is studying " + subject);
    }

    @Override
    public void greet() {
        super.greet();
        System.out.println("I'm a student.");
    }
}

// 接口
interface Animal {
    void eat();
    void sleep();
}

public class Dog implements Animal {
    @Override
    public void eat() {
        System.out.println("Dog is eating");
    }

    @Override
    public void sleep() {
        System.out.println("Dog is sleeping");
    }
}

// 抽象类
abstract class Shape {
    abstract double area();

    void printInfo() {
        System.out.println("面积: " + area());
    }
}

// 静态方法和变量
class MathUtils {
    public static final double PI = 3.14159;

    public static int add(int a, int b) {
        return a + b;
    }
}
// 直接通过类名调用
int sum = MathUtils.add(2, 3);
```
