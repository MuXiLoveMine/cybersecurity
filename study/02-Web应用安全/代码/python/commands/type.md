# type

> **分类**：内置函数
> **说明**：返回对象的类型，或创建新的类型

---

## 语法

```c
type(object) 或 type(name, bases, dict)
```

## 参数说明

- object: 要检查类型的对象
- name: 新类型的名称
- bases: 基类元组
- dict: 类属性/方法字典

## 示例代码

```python
# 获取类型
print(type(42))        # <class 'int'>
print(type("hello"))   # <class 'str'>
print(type([1,2]))     # <class 'list'>
print(type({}))        # <class 'dict'>

# 类型判断
if type(x) == int:
    print("是整数")

# isinstance 更推荐（支持继承关系）
if isinstance(x, int):
    print("是整数或其子类")

# 动态创建类
MyClass = type('MyClass', (object,), {'x': 10, 'hello': lambda self: "hi"})
obj = MyClass()
print(obj.x)         # 10
print(obj.hello())   # hi
```
