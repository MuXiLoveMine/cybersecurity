# Smali 语法基础

### 1.1 Smali 简介

Smali 是 Android Dalvik/ART 虚拟机使用的字节码的汇编语言表示形式。简单来说，DEX 文件是 Android 虚拟机执行的二进制字节码，而 Smali 是这种字节码的可读文本形式。

**相关概念**：
- **DEX**：Dalvik Executable，Android 虚拟机执行的二进制字节码文件
- **Smali**：DEX 的反汇编文本形式（人类可读）
- **baksmali**：将 DEX 反汇编为 Smali 的工具
- **smali**：将 Smali 汇编回 DEX 的工具

### 1.2 数据类型

| Smali 类型 | Java 类型 | 说明 |
|-----------|-----------|------|
| V | void | 空类型 |
| Z | boolean | 布尔类型 |
| B | byte | 字节 |
| S | short | 短整型 |
| C | char | 字符 |
| I | int | 整型 |
| J | long | 长整型（64位） |
| F | float | 单精度浮点 |
| D | double | 双精度浮点 |
| L<package>/<name>; | 引用类型 | 对象类型，如 Ljava/lang/String; |
| [类型 | 数组类型 | 如 [I 表示 int[]，[[I 表示 int[][] |

**示例**：
```
Ljava/lang/String;       →  java.lang.String
Landroid/os/Bundle;      →  android.os.Bundle
[I                       →  int[]
[Ljava/lang/String;      →  String[]
[[I                      →  int[][]
```

### 1.3 寄存器

Dalvik 虚拟机是基于寄存器的虚拟机（与 JVM 基于栈不同）。每个方法都有一定数量的寄存器用于存储数据。

**寄存器表示**：
- `v0, v1, v2...`：虚拟寄存器编号
- `p0, p1, p2...`：参数寄存器（p0 对应 this，非静态方法）

**寄存器数量声明**：
```smali
.method public static test(II)V
    .registers 4        # 总共 4 个寄存器
    # 两个 int 参数，分别用 v0, v1 或 p0, p1 表示
    # 具体取决于使用 .locals 还是 .registers
.end method
```

**静态方法 vs 非静态方法的参数寄存器**：
```smali
# 非静态方法：p0 = this, p1 = 第一个参数, p2 = 第二个参数...
.method public login(Ljava/lang/String;Ljava/lang/String;)Z
    .registers 5
    # p0 = this
    # p1 = username (String)
    # p2 = password (String)
    # v0, v1 是局部变量
.end method

# 静态方法：p0 = 第一个参数, p1 = 第二个参数...
.method public static encrypt(Ljava/lang/String;)Ljava/lang/String;
    .registers 3
    # p0 = input (String)
    # v0, v1 是局部变量
.end method
```

### 1.4 类结构

```smali
# 类定义：Lcom/example/MainActivity;
.class public Lcom/example/MainActivity;
# 父类：Landroid/app/Activity;
.super Landroid/app/Activity;
# 源文件名
.source "MainActivity.java"

# 实例字段
.field private username:Ljava/lang/String;
.field private password:Ljava/lang/String;

# 静态字段
.field private static final TAG:Ljava/lang/String; = "MainActivity"

# 直接方法（构造方法、静态方法、私有方法）
.method static constructor <clinit>()V
    .registers 1
    # 静态初始化
    return-void
.end method

.method public constructor <init>()V
    .registers 1
    # 构造方法
    invoke-direct {p0}, Landroid/app/Activity;-><init>()V
    return-void
.end method

# 虚方法（public/protected 等可继承方法）
.method protected onCreate(Landroid/os/Bundle;)V
    .registers 3
    # ... 方法体
    return-void
.end method
```

### 1.5 方法调用

#### 调用类型

| 调用指令 | 用途 | 示例 |
|----------|------|------|
| invoke-virtual | 调用虚方法（实例方法） | 调用普通成员方法 |
| invoke-direct | 调用直接方法 | 调用 private 方法、构造方法 |
| invoke-static | 调用静态方法 | 调用 static 方法 |
| invoke-super | 调用父类方法 | 调用 super.xxx() |
| invoke-interface | 调用接口方法 | 通过接口引用调用方法 |

#### 调用语法

```smali
# 格式：invoke-xx {参数寄存器}, 类名;->方法名(参数类型)返回类型

# 示例1：调用静态方法，无参数
invoke-static {}, Lcom/example/Utils;->getVersion()I

# 示例2：调用实例方法，有参数
# v0 = this, v1 = username, v2 = password
invoke-virtual {v0, v1, v2}, Lcom/example/UserManager;->login(Ljava/lang/String;Ljava/lang/String;)Z

# 示例3：调用构造方法
invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

# 示例4：调用父类方法
invoke-super {p0, p1}, Landroid/app/Activity;->onCreate(Landroid/os/Bundle;)V
```

#### 返回值处理

```smali
# 使用 move-result 系列指令获取方法返回值

# 示例：获取 boolean 返回值
invoke-virtual {v0, v1, v2}, Lcom/example/UserManager;->login(Ljava/lang/String;Ljava/lang/String;)Z
move-result v0                    # v0 = 返回值（boolean 用 int 表示，0=false, 1=true）

# 示例：获取对象返回值
invoke-static {v0}, Lcom/example/Utils;->encrypt(Ljava/lang/String;)Ljava/lang/String;
move-result-object v0             # v0 = 返回的 String 对象

# 示例：获取 int 返回值
invoke-virtual {v0}, Ljava/lang/String;->length()I
move-result v0                    # v0 = 字符串长度
```

### 1.6 字段访问

```smali
# 读取实例字段
iget v0, p0, Lcom/example/MainActivity;->count:I
# 含义：v0 = p0.count

# 写入实例字段
iput v0, p0, Lcom/example/MainActivity;->count:I
# 含义：p0.count = v0

# 读取静态字段
sget-object v0, Lcom/example/MainActivity;->TAG:Ljava/lang/String;
# 含义：v0 = MainActivity.TAG

# 写入静态字段
sput-object v0, Lcom/example/MainActivity;->instance:Lcom/example/MainActivity;
# 含义：MainActivity.instance = v0
```

### 1.7 条件判断与跳转

```smali
# if 系列指令：比较两个寄存器的值，满足条件则跳转

# 等于/不等于
if-eq v0, v1, :cond_equal        # if (v0 == v1)
if-ne v0, v1, :cond_not_equal    # if (v0 != v1)

# 小于/大于/小于等于/大于等于
if-lt v0, v1, :cond_less         # if (v0 < v1)
if-gt v0, v1, :cond_greater      # if (v0 > v1)
if-le v0, v1, :cond_less_eq      # if (v0 <= v1)
if-ge v0, v1, :cond_greater_eq   # if (v0 >= v1)

# 与0比较
if-eqz v0, :cond_zero            # if (v0 == 0)
if-nez v0, :cond_not_zero        # if (v0 != 0)
if-ltz v0, :cond_less_zero       # if (v0 < 0)
if-gtz v0, :cond_greater_zero    # if (v0 > 0)
if-lez v0, :cond_less_eq_zero    # if (v0 <= 0)
if-gez v0, :cond_greater_eq_zero # if (v0 >= 0)

# 无条件跳转
goto :target_label

# switch 语句
packed-switch v0, :pswitch_data   # 密集 switch
sparse-switch v0, :sswitch_data   # 稀疏 switch
```

**完整示例（if-else）**：

Java 代码：
```java
public boolean checkPassword(String input) {
    if (input == null) {
        return false;
    }
    if (input.length() >= 6) {
        return true;
    } else {
        return false;
    }
}
```

对应的 Smali 代码：
```smali
.method public checkPassword(Ljava/lang/String;)Z
    .registers 3
    
    # if (input == null) return false
    if-eqz p1, :cond_false
    
    # input.length()
    invoke-virtual {p1}, Ljava/lang/String;->length()I
    move-result v0
    
    # if (length >= 6) goto :cond_true
    if-ge v0, 6, :cond_true
    
    :cond_false
    const/4 v0, 0x0    # return false
    return v0
    
    :cond_true
    const/4 v0, 0x1    # return true
    return v0
.end method
```

### 1.8 循环结构

**Java 代码**：
```java
public int sum(int n) {
    int result = 0;
    for (int i = 0; i < n; i++) {
        result += i;
    }
    return result;
}
```

**Smali 代码**：
```smali
.method public sum(I)I
    .registers 4
    # p0 = this
    # p1 = n
    # v0 = result
    # v1 = i
    
    # int result = 0
    const/4 v0, 0x0
    
    # int i = 0
    const/4 v1, 0x0
    
    # 跳转到循环条件判断
    goto :cond_check
    
    :loop_body
    # result += i
    add-int/2addr v0, v1
    
    # i++
    add-int/lit8 v1, v1, 0x1
    
    :cond_check
    # if (i < n) goto loop_body
    if-lt v1, p1, :loop_body
    
    # return result
    return v0
.end method
```

### 1.9 字符串与常量

```smali
# 字符串常量
const-string v0, "Hello World"

# 整数常量
const/4 v0, 0x0          # v0 = 0  (4位有符号)
const/16 v0, 0x64        # v0 = 100 (16位有符号)
const v0, 0x12345678     # v0 = 0x12345678 (32位)

# 宽整型（long, 64位）
const-wide v0, 0x1234567890ABCDEFL

# 浮点型
const/4 v0, 0x0          # float 0.0
const v0, 0x3f800000     # float 1.0

# 空对象
const/4 v0, 0x0          # null
```

### 1.10 数组操作

```smali
# 创建数组
new-array v0, v1, [I            # int[v1]
new-instance v0, [Ljava/lang/String;  # 不对，对象数组用 filled-new-array

# 获取数组长度
array-length v0, v1              # v0 = v1.length

# 读取数组元素
aget v0, v1, v2                  # v0 = v1[v2]  (int数组)
aget-object v0, v1, v2           # v0 = v1[v2]  (对象数组)
aget-boolean v0, v1, v2          # v0 = v1[v2]  (boolean数组)
aget-byte v0, v1, v2             # v0 = v1[v2]  (byte数组)
aget-char v0, v1, v2             # v0 = v1[v2]  (char数组)
aget-wide v0, v1, v2             # v0 = v1[v2]  (long数组)

# 写入数组元素
aput v0, v1, v2                  # v1[v2] = v0  (int数组)
aput-object v0, v1, v2           # v1[v2] = v0  (对象数组)
aput-boolean v0, v1, v2          # v1[v2] = v0  (boolean数组)
aput-byte v0, v1, v2             # v1[v2] = v0  (byte数组)
```

### 1.11 常见指令速查

| 指令 | 作用 |
|------|------|
| move vA, vB | 复制寄存器值 |
| move-object vA, vB | 复制对象引用 |
| move-result vA | 获取方法返回值（基本类型） |
| move-result-object vA | 获取方法返回值（对象） |
| move-exception vA | 获取异常对象 |
| new-instance vA, 类 | 创建对象实例 |
| instance-of vA, vB, 类 | 判断对象类型 |
| check-cast vA, 类 | 类型转换 |
| throw vA | 抛出异常 |
| return-void | 无返回值 |
| return vA | 返回基本类型 |
| return-object vA | 返回对象 |
| return-wide vA | 返回长整型/双精度 |

---

---

## 📋 内容审核与补充建议

> 针对「Smali 语法基础」部分的内容审核结果：

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

### ⚔️ 攻击技术
- ⚠️ 缺少attack相关内容

---

## 📌 拓展学习资源

### 推荐学习路径
- 理论基础 → 工具实践 → 实战演练 → 深度研究
- 建议搭建本地实验环境进行动手练习

### 相关工具与资源
- 在线实验平台：Hack The Box、TryHackMe、VulnHub
- 技术文档：官方文档、RFC、OWASP 指南
- 社区资源：GitHub、安全论坛、技术博客
