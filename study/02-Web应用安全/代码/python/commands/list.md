# list

> **分类**：列表方法
> **说明**：列表是可变的有序序列，支持增删改查

---

## 语法

```c
list(iterable) 或使用 [item1, item2, ...]
```

## 常用方法/属性

- append(x) - 末尾添加元素
- extend(iter) - 扩展列表
- insert(i, x) - 指定位置插入
- remove(x) - 删除第一个x
- pop([i]) - 弹出指定位置元素
- clear() - 清空列表
- index(x) - 查找元素索引
- count(x) - 统计元素个数
- sort() - 排序
- reverse() - 反转
- copy() - 浅拷贝

## 示例代码

```python
# 创建列表
fruits = ["apple", "banana", "cherry"]
nums = list(range(5))  # [0, 1, 2, 3, 4]

# 访问元素
print(fruits[0])       # "apple"
print(fruits[-1])      # "cherry"
print(fruits[1:3])     # ["banana", "cherry"]

# 添加元素
fruits.append("orange")     # 末尾添加
fruits.insert(1, "grape")   # 指定位置插入
fruits.extend(["kiwi", "mango"])  # 扩展

# 删除元素
fruits.remove("banana")  # 删除指定元素
popped = fruits.pop()    # 弹出最后一个
del fruits[0]            # 删除指定位置

# 排序
nums = [3, 1, 4, 1, 5, 9]
nums.sort()                    # 升序（修改原列表）
sorted_nums = sorted(nums)     # 升序（返回新列表）
nums.sort(reverse=True)        # 降序

# 列表推导式
squares = [x*x for x in range(10)]
evens = [x for x in range(20) if x % 2 == 0]

# 常用操作
print(len(fruits))   # 长度
print(3 in nums)     # 包含判断
print(nums + [10])   # 列表拼接
```
