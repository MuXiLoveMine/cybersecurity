# class_cs

> **分类**：类与面向对象
> **说明**：C# 类定义和面向对象编程

---

## 语法

```csharp
public class ClassName {\n  public string Property { get; set; }\n  public void Method() { }\n}
```

## 访问修饰符

public / private / protected / internal / protected internal

## 特性

封装 / 继承 / 多态 / 抽象类 / 接口 / 密封类 / 静态类

## 示例代码

```csharp
using System;

// 基本类
public class Person {
    // 字段（私有）
    private string _name;
    private int _age;

    // 自动属性
    public string Name { get; set; }
    public int Age { get; set; }
    public string City { get; set; } = "Beijing";  // 默认值

    // 只读属性
    public string Info => $"{Name}, {Age}岁";

    // 带 backing field 的属性
    public string Name2 {
        get { return _name; }
        set { _name = value; }
    }

    // 构造函数
    public Person() {
        Name = "Unknown";
        Age = 0;
    }

    public Person(string name, int age) {
        Name = name;
        Age = age;
    }

    // 方法
    public void Greet() {
        Console.WriteLine($"Hello, I'm {Name}");
    }

    // 虚方法（可重写）
    public virtual void Work() {
        Console.WriteLine($"{Name} 在工作");
    }

    // 重写 ToString
    public override string ToString() {
        return $"Person {{ Name = {Name}, Age = {Age} }}";
    }
}

// 继承
public class Student : Person {
    public string StudentId { get; set; }
    public string Major { get; set; }

    public Student(string name, int age, string id)
        : base(name, age)  // 调用父类构造函数
    {
        StudentId = id;
    }

    public void Study(string subject) {
        Console.WriteLine($"{Name} 正在学习 {subject}");
    }

    // 重写方法
    public override void Work() {
        Console.WriteLine($"{Name} 在学习");
    }
}

// 接口
public interface IShape {
    double Area { get; }
    double Perimeter { get; }
    void Draw();
}

public class Circle : IShape {
    public double Radius { get; set; }

    public double Area => Math.PI * Radius * Radius;
    public double Perimeter => 2 * Math.PI * Radius;

    public void Draw() {
        Console.WriteLine($"画圆，半径 {Radius}");
    }
}

// 抽象类
public abstract class Animal {
    public string Name { get; set; }
    public abstract void MakeSound();  // 抽象方法

    public void Eat() {
        Console.WriteLine($"{Name} 在吃东西");
    }
}

public class Dog : Animal {
    public override void MakeSound() {
        Console.WriteLine("汪汪！");
    }
}

// 静态类
public static class MathUtils {
    public const double PI = 3.14159;

    public static int Add(int a, int b) {
        return a + b;
    }
}

class Program {
    static void Main() {
        var p = new Person("Alice", 25);
        p.Greet();

        var s = new Student("Bob", 20, "2024001");
        s.Study("C#");
        s.Work();  // 多态

        // 接口使用
        IShape shape = new Circle { Radius = 5 };
        Console.WriteLine($"面积: {shape.Area:F2}");

        // 静态类
        Console.WriteLine(MathUtils.Add(2, 3));
    }
}
```
