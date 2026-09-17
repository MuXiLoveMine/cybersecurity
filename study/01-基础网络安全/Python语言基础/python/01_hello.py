# 01_hello.py
# 第一个 Python 程序

print("Hello, World!")

# 多种输出方式
name = "张三"
age = 25

print("姓名:", name, "年龄:", age)
print(f"姓名: {name}, 年龄: {age}")  # f-string（推荐）
print("姓名: %s, 年龄: %d" % (name, age))  # 旧风格
print("姓名: {}, 年龄: {}".format(name, age))  # format 方法

# 带颜色输出（ANSI 转义码）
print("\033[31m红色文字\033[0m")
print("\033[32m绿色文字\033[0m")
print("\033[33m黄色文字\033[0m")
print("\033[34m蓝色文字\033[0m")

# 输入
# name = input("请输入你的名字：")
# print(f"你好，{name}！")
