# dict

> **分类**：字典方法
> **说明**：字典是键值对的无序集合，通过键快速查找

---

## 语法

```c
dict() 或使用 {key1: value1, key2: value2, ...}
```

## 常用方法/属性

- get(key, default) - 获取值，键不存在返回默认值
- keys() - 返回所有键
- values() - 返回所有值
- items() - 返回所有键值对
- update(dict2) - 更新字典
- pop(key, default) - 删除并返回值
- popitem() - 弹出最后一个键值对
- setdefault(key, default) - 获取或设置默认值
- clear() - 清空字典
- copy() - 浅拷贝

## 示例代码

```python
# 创建字典
person = {"name": "Alice", "age": 25, "city": "Beijing"}
d = dict(name="Bob", age=30)

# 访问值
print(person["name"])        # "Alice"
print(person.get("age"))     # 25
print(person.get("email", "未知"))  # "未知"（键不存在返回默认值）

# 修改/添加
person["age"] = 26           # 修改
person["email"] = "a@test.com"  # 添加

# 删除
del person["city"]           # 删除键值对
age = person.pop("age")      # 弹出值

# 遍历
for key in person:
    print(key, person[key])

for key, value in person.items():
    print(key, value)

for val in person.values():
    print(val)

# 字典推导式
squares = {x: x*x for x in range(5)}
# {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

# 合并字典（Python 3.9+）
d1 = {"a": 1, "b": 2}
d2 = {"b": 3, "c": 4}
merged = d1 | d2    # {"a": 1, "b": 3, "c": 4}
```
