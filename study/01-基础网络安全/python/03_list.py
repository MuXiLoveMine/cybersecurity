# 03_list.py
# 列表操作

# ===== 创建列表 =====
fruits = ["apple", "banana", "cherry", "date", "elderberry"]
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
mixed = [1, "hello", 3.14, True, [1, 2, 3]]
empty = []

print("原始列表:", fruits)
print("列表长度:", len(fruits))

# ===== 访问元素 =====
print("\n===== 访问元素 =====")
print("fruits[0] =", fruits[0])      # 第一个
print("fruits[2] =", fruits[2])      # 第三个
print("fruits[-1] =", fruits[-1])    # 最后一个
print("fruits[-2] =", fruits[-2])    # 倒数第二个

# ===== 切片 =====
print("\n===== 切片 =====")
print("fruits[1:3] =", fruits[1:3])      # 索引1到2
print("fruits[:3] =", fruits[:3])        # 前3个
print("fruits[2:] =", fruits[2:])        # 从第3个开始
print("fruits[::2] =", fruits[::2])      # 步长2
print("fruits[::-1] =", fruits[::-1])    # 反转

# ===== 修改与添加 =====
print("\n===== 修改与添加 =====")
fruits[0] = "ant"
print("修改后:", fruits)

fruits.append("fig")
print("append后:", fruits)

fruits.insert(1, "apricot")
print("insert后:", fruits)

fruits.extend(["grape", "honeydew"])
print("extend后:", fruits)

# ===== 删除 =====
print("\n===== 删除 =====")
fruits.remove("banana")
print("remove banana后:", fruits)

del fruits[0]
print("del 索引0后:", fruits)

last = fruits.pop()
print(f"pop 最后一个: {last}，剩余:", fruits)

# ===== 查找与统计 =====
print("\n===== 查找与统计 =====")
print("'cherry' 索引:", fruits.index("cherry"))
print("'cherry' 是否存在:", "cherry" in fruits)
print("'mango' 是否存在:", "mango" in fruits)
print("出现次数:", fruits.count("cherry"))

# ===== 排序 =====
print("\n===== 排序 =====")
nums = [3, 1, 4, 1, 5, 9, 2, 6]
print("原始:", nums)

nums.sort()
print("升序排序:", nums)

nums.sort(reverse=True)
print("降序排序:", nums)

fruits_sorted = sorted(fruits)  # 不修改原列表
print("sorted 结果:", fruits_sorted)

# ===== 遍历 =====
print("\n===== 遍历 =====")
print("方式一:")
for fruit in fruits:
    print(f"  {fruit}")

print("方式二（带索引）:")
for i, fruit in enumerate(fruits):
    print(f"  {i}: {fruit}")

# ===== 列表推导式 =====
print("\n===== 列表推导式 =====")
squares = [x**2 for x in range(10)]
print("平方数:", squares)

evens = [x for x in range(10) if x % 2 == 0]
print("偶数:", evens)

# ===== 其他常用 =====
print("\n===== 其他常用 =====")
print("numbers 最大值:", max(numbers))
print("numbers 最小值:", min(numbers))
print("numbers 总和:", sum(numbers))

list1 = [1, 2, 3]
list2 = [4, 5, 6]
print("拼接:", list1 + list2)

list1_copy = list1.copy()
print("复制:", list1_copy)
