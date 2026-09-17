# 04_dict.py
# 字典操作

# ===== 创建字典 =====
person = {
    "name": "张三",
    "age": 25,
    "city": "北京",
    "job": "工程师"
}

print("原始字典:", person)
print("字典长度:", len(person))

# ===== 访问 =====
print("\n===== 访问 =====")
print("name:", person["name"])
print("age:", person.get("age"))
print("gender:", person.get("gender", "未知"))  # 键不存在返回默认值

print("所有键:", list(person.keys()))
print("所有值:", list(person.values()))
print("所有键值对:", list(person.items()))

# ===== 修改与添加 =====
print("\n===== 修改与添加 =====")
person["age"] = 26
print("修改 age:", person)

person["gender"] = "男"
print("添加 gender:", person)

person.update({"email": "zhangsan@example.com", "city": "上海"})
print("update 后:", person)

# ===== 删除 =====
print("\n===== 删除 =====")
del person["gender"]
print("del gender 后:", person)

job = person.pop("job")
print(f"pop job: {job}，剩余:", person)

last_key, last_val = person.popitem()
print(f"popitem: {last_key}={last_val}")

# ===== 判断 =====
print("\n===== 判断 =====")
print("'name' in person:", "name" in person)
print("'salary' in person:", "salary" in person)

# ===== 遍历 =====
print("\n===== 遍历 =====")
print("方式一（键）:")
for key in person:
    print(f"  {key}: {person[key]}")

print("方式二（键值对，推荐）:")
for key, value in person.items():
    print(f"  {key}: {value}")

print("方式三（值）:")
for value in person.values():
    print(f"  {value}")

# ===== 字典推导式 =====
print("\n===== 字典推导式 =====")
squares = {x: x**2 for x in range(6)}
print("平方字典:", squares)

# ===== 嵌套字典 =====
print("\n===== 嵌套字典 =====")
users = {
    "user1": {"name": "张三", "age": 25},
    "user2": {"name": "李四", "age": 30}
}
print("user1 姓名:", users["user1"]["name"])

for user_id, user_info in users.items():
    print(f"  {user_id}: {user_info['name']}, {user_info['age']}岁")
