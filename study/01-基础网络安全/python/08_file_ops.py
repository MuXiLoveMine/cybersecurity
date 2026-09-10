# 08_file_ops.py
# 文件与目录操作

import os
import glob

# ===== 写入文件 =====
print("===== 写入文件 =====")

# 覆盖写入
with open("test_output.txt", "w", encoding="utf-8") as f:
    f.write("第一行\n")
    f.write("第二行\n")
    f.write("第三行\n")

print("写入完成: test_output.txt")

# 追加写入
with open("test_output.txt", "a", encoding="utf-8") as f:
    f.write("追加的一行\n")

print("追加完成")

# ===== 读取文件 =====
print("\n===== 读取文件 =====")

# 读取全部
with open("test_output.txt", "r", encoding="utf-8") as f:
    content = f.read()
    print("全部内容:")
    print(content)

# 逐行读取
print("逐行读取:")
with open("test_output.txt", "r", encoding="utf-8") as f:
    for i, line in enumerate(f, 1):
        print(f"  行{i}: {line.strip()}")

# 读取所有行到列表
with open("test_output.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()
    print(f"共 {len(lines)} 行")

# ===== 目录操作 =====
print("\n===== 目录操作 =====")

# 当前目录
cwd = os.getcwd()
print(f"当前目录: {cwd}")

# 列出目录内容
print("\n当前目录内容（前10个）:")
items = os.listdir(".")
for item in items[:10]:
    print(f"  {item}")

# 创建目录
os.makedirs("test_dir/sub_dir", exist_ok=True)
print("\n创建目录: test_dir/sub_dir")

# 判断
print(f"\ntest_dir 是否存在: {os.path.exists('test_dir')}")
print(f"test_dir 是否为目录: {os.path.isdir('test_dir')}")
print(f"test_output.txt 是否为文件: {os.path.isfile('test_output.txt')}")

# 路径操作
path = os.path.join("test_dir", "sub_dir", "file.txt")
print(f"\n路径拼接: {path}")
print(f"目录名: {os.path.dirname(path)}")
print(f"文件名: {os.path.basename(path)}")
print(f"扩展名: {os.path.splitext(path)}")

# ===== glob 匹配 =====
print("\n===== glob 匹配 =====")

# 匹配当前目录的 .py 文件
py_files = glob.glob("*.py")
print(f"当前目录的 .py 文件数: {len(py_files)}")
for f in py_files[:5]:
    print(f"  {f}")

# ===== 清理 =====
print("\n===== 清理测试文件 =====")
os.remove("test_output.txt")
os.rmdir("test_dir/sub_dir")
os.rmdir("test_dir")
print("测试文件已清理")
