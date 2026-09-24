# class_cpp

> **分类**：类与对象
> **说明**：C++ 面向对象编程

---

## 语法

```cpp
class ClassName {\n  private:\n    members;\n  public:\n    methods;\n};
```

## 访问控制

public / private / protected

## 特殊函数

构造函数 / 析构函数 / 拷贝构造 / 拷贝赋值 / 移动构造 / 移动赋值

## 特性

封装 / 继承 / 多态 / 抽象 / 虚函数

## 示例代码

```cpp
#include <iostream>
#include <string>
using namespace std;

// 基本类
class Person {
private:
    string name;
    int age;

public:
    // 默认构造函数
    Person() : name("Unknown"), age(0) {}

    // 带参数构造函数
    Person(string name, int age) : name(name), age(age) {}

    // 析构函数
    ~Person() {
        cout << name << " 被销毁" << endl;
    }

    // 拷贝构造函数
    Person(const Person& other) : name(other.name), age(other.age) {
        cout << "拷贝构造" << endl;
    }

    // 成员函数
    void greet() const {
        cout << "Hello, I'm " << name << ", " << age << "岁" << endl;
    }

    // getter/setter
    string getName() const { return name; }
    void setName(string name) { this->name = name; }
    int getAge() const { return age; }
    void setAge(int age) { this->age = age; }

    // 虚函数（支持多态）
    virtual void work() const {
        cout << name << " 在工作" << endl;
    }
};

// 继承
class Student : public Person {
private:
    string studentId;

public:
    Student(string name, int age, string id)
        : Person(name, age), studentId(id) {}

    void study(string subject) const {
        cout << getName() << " 正在学习 " << subject << endl;
    }

    // 重写虚函数
    void work() const override {
        cout << getName() << " 在学习" << endl;
    }
};

// 抽象类（含有纯虚函数）
class Shape {
public:
    virtual double area() const = 0;  // 纯虚函数
    virtual ~Shape() {}  // 虚析构函数
};

class Circle : public Shape {
private:
    double radius;
public:
    Circle(double r) : radius(r) {}
    double area() const override {
        return 3.14159 * radius * radius;
    }
};

int main() {
    // 使用类
    Person p("Alice", 25);
    p.greet();

    Student s("Bob", 20, "2024001");
    s.greet();
    s.study("C++");

    // 多态
    Person* personPtr = &s;
    personPtr->work();  // 调用 Student::work()

    // 抽象类使用
    Shape* shape = new Circle(5.0);
    cout << "面积: " << shape->area() << endl;
    delete shape;

    // 智能指针 (C++11)
    #include <memory>
    auto person = make_unique<Person>("Charlie", 30);
    person->greet();

    return 0;
}
```
