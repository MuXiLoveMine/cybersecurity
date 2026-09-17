# 06_control_flow.py
# 条件判断与循环

# ===== if 条件判断 =====
print("===== if 条件判断 =====")
age = 20

if age >= 18:
    print("成年")
    print("可以投票")
elif age >= 13:
    print("青少年")
else:
    print("儿童")

# 多分支
score = 85
if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 60:
    grade = "C"
else:
    grade = "D"
print(f"分数 {score} 的等级: {grade}")

# 三目表达式
result = "及格" if score >= 60 else "不及格"
print(f"三目表达式结果: {result}")

# 逻辑运算符
print("\n===== 逻辑运算 =====")
if age >= 18 and score >= 60:
    print("成年且及格")

if age < 18 or score >= 90:
    print("未成年或者优秀")

if not (age < 18):
    print("不是未成年人")

# ===== for 循环 =====
print("\n===== for 循环 =====")
fruits = ["apple", "banana", "cherry"]

print("遍历列表:")
for fruit in fruits:
    print(f"  {fruit}")

print("\n带索引遍历:")
for i, fruit in enumerate(fruits):
    print(f"  {i}: {fruit}")

print("\nrange(5):")
for i in range(5):
    print(f"  {i}", end=" ")
print()

print("range(2, 7):")
for i in range(2, 7):
    print(f"  {i}", end=" ")
print()

print("range(0, 10, 2):")
for i in range(0, 10, 2):
    print(f"  {i}", end=" ")
print()

print("\n遍历字典:")
person = {"name": "张三", "age": 25, "city": "北京"}
for key, value in person.items():
    print(f"  {key}: {value}")

print("\n遍历字符串:")
for char in "Python":
    print(f"  {char}")

# ===== while 循环 =====
print("\n===== while 循环 =====")
count = 0
while count < 5:
    print(f"  count = {count}")
    count += 1

# ===== break 和 continue =====
print("\n===== break 和 continue =====")
print("break 示例（遇到5跳出）:")
for i in range(10):
    if i == 5:
        break
    print(f"  {i}", end=" ")
print()

print("continue 示例（跳过偶数）:")
for i in range(10):
    if i % 2 == 0:
        continue
    print(f"  {i}", end=" ")
print()

# ===== while-else / for-else =====
print("\n===== for-else =====")
for i in range(5):
    if i == 10:
        break
else:
    print("循环正常结束（没有 break 跳出）")

# ===== 猜数字小游戏 =====
print("\n===== 猜数字 =====")
import random
target = random.randint(1, 20)
print("我想了一个 1-20 之间的数字，猜猜看！")
tries = 0
while True:
    # guess = int(input("请输入你的猜测: "))
    guess = random.randint(1, 20)  # 模拟输入
    tries += 1
    if guess < target:
        print(f"  猜 {guess}: 太小了")
    elif guess > target:
        print(f"  猜 {guess}: 太大了")
    else:
        print(f"  猜 {guess}: 恭喜你猜对了！用了 {tries} 次")
        break
