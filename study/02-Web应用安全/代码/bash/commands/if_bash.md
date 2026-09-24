# if_bash

> **分类**：条件判断
> **说明**：if/else 条件语句

---

## 语法

```bash
if [ condition ]; then\n  ...\nelif [ condition ]; then\n  ...\nelse\n  ...\nfi
```

## 操作符

文件测试: -f/-d/-e/-r/-w/-x/-s/-nt
  字符串: =/!=/-z/-n
  数字: -eq/-ne/-lt/-le/-gt/-ge
  逻辑: !/&&/||

## 示例代码

```bash
#!/bin/bash

# 基本 if/else
age=18
if [ $age -ge 18 ]; then
    echo "成年"
else
    echo "未成年"
fi

# 多分支
score=85
if [ $score -ge 90 ]; then
    echo "优秀"
elif [ $score -ge 60 ]; then
    echo "及格"
else
    echo "不及格"
fi

# ===== 文件测试 =====
file="test.txt"
if [ -f $file ]; then
    echo "$file 是普通文件"
fi

if [ -d $file ]; then
    echo "是目录"
fi

if [ -e $file ]; then
    echo "文件存在"
fi

if [ -r $file ]; then
    echo "可读"
fi

if [ -s $file ]; then
    echo "文件非空"
fi

# ===== 字符串比较 =====
str1="hello"
str2="world"
if [ "$str1" = "$str2" ]; then
    echo "相等"
fi

if [ "$str1" != "$str2" ]; then
    echo "不相等"
fi

if [ -z "$str1" ]; then
    echo "字符串为空"
fi

if [ -n "$str1" ]; then
    echo "字符串非空"
fi

# ===== 数字比较 =====
a=10
b=20
if [ $a -eq $b ]; then echo "相等"; fi
if [ $a -ne $b ]; then echo "不等"; fi
if [ $a -lt $b ]; then echo "小于"; fi
if [ $a -gt $b ]; then echo "大于"; fi
if [ $a -le $b ]; then echo "小于等于"; fi
if [ $a -ge $b ]; then echo "大于等于"; fi

# ===== 逻辑运算 =====
if [ $a -gt 5 ] && [ $a -lt 15 ]; then
    echo "在5-15之间"
fi

if [ $a -lt 5 ] || [ $a -gt 15 ]; then
    echo "不在5-15之间"
fi

if [ ! -f $file ]; then
    echo "文件不存在"
fi

# ===== case =====
day="Monday"
case $day in
    Monday|monday)
        echo "星期一"
        ;;
    Tuesday)
        echo "星期二"
        ;;
    *)
        echo "其他"
        ;;
esac

# 三元运算（简写）
[ $a -gt 10 ] && echo "大于10" || echo "小于等于10"

# [[ ]] 高级测试（支持正则）
if [[ $string =~ ^[0-9]+$ ]]; then
    echo "是数字"
fi
```
