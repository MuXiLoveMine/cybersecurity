# class_js

> **分类**：类与面向对象
> **说明**：ES6 Class 语法

---

## 语法

```javascript
class ClassName extends Parent {\n  constructor() { ... }\n  method() { ... }\n}
```

## 特性

- 构造函数
- 实例方法
- 静态方法
- 继承
- getter
- setter

## 示例代码

```javascript
// 基本类
class Person {
    // 静态属性
    static species = "Homo sapiens";

    // 构造函数
    constructor(name, age) {
        this.name = name;
        this.age = age;
    }

    // 实例方法
    greet() {
        return `Hello, I'm ${this.name}`;
    }

    // getter
    get isAdult() {
        return this.age >= 18;
    }

    // setter
    set name(value) {
        if (value.length < 2) {
            throw new Error("名字太短");
        }
        this._name = value;
    }

    // 静态方法
    static create(name, age) {
        return new Person(name, age);
    }
}

const p = new Person("Alice", 25);
console.log(p.greet());    // "Hello, I'm Alice"
console.log(p.isAdult);    // true
const p2 = Person.create("Bob", 30);  // 静态方法

// 继承
class Student extends Person {
    constructor(name, age, studentId) {
        super(name, age);  // 调用父类构造函数
        this.studentId = studentId;
    }

    study(subject) {
        return `${this.name} is studying ${subject}`;
    }

    // 重写方法
    greet() {
        return super.greet() + " I'm a student.";
    }
}

const s = new Student("Bob", 20, "2024001");
console.log(s.study("Math"));
console.log(s.greet());

// 私有字段（# 开头，真正私有）
class Counter {
    #count = 0;  // 私有字段

    increment() {
        this.#count++;
        return this.#count;
    }

    get value() {
        return this.#count;
    }
}

const c = new Counter();
c.increment();
// c.#count;  // 错误，无法从外部访问

// 类表达式
const MyClass = class {
    constructor(name) {
        this.name = name;
    }
};
```
