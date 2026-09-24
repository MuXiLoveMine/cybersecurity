# class

> **分类**：类定义
> **说明**：定义一个类，用于面向对象编程

---

## 语法

```c
class 类名(父类列表):\n    类体
```

## 魔术方法

- __init__: 构造方法
- __str__: 字符串表示（print用）
- __repr__: 正式字符串表示
- __len__: len() 支持
- __getitem__: [] 访问
- __setitem__: [] 赋值
- __call__: 对象可调用
- __enter__/__exit__: 上下文管理器

## 示例代码

```python
# 基本类定义
class Person:
    # 类属性
    species = "Homo sapiens"

    # 构造方法
    def __init__(self, name, age):
        # 实例属性
        self.name = name
        self.age = age

    # 实例方法
    def greet(self):
        return f"我是{self.name}，{self.age}岁"

    # 类方法
    @classmethod
    def from_birth_year(cls, name, birth_year):
        age = 2024 - birth_year
        return cls(name, age)

    # 静态方法
    @staticmethod
    def is_adult(age):
        return age >= 18

# 创建实例
p = Person("Alice", 25)
print(p.name)       # "Alice"
print(p.greet())    # "我是Alice，25岁"

# 继承
class Student(Person):
    def __init__(self, name, age, student_id):
        super().__init__(name, age)  # 调用父类构造
        self.student_id = student_id

    def study(self, subject):
        return f"{self.name}正在学习{subject}"

s = Student("Bob", 20, "2024001")
print(s.study("Python"))  # "Bob正在学习Python"

# 魔术方法
class MyList:
    def __init__(self, data=None):
        self.data = data or []

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.data[index]

    def __str__(self):
        return str(self.data)
```
