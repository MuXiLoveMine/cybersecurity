# Android 逆向基础

> 本文档详细介绍 Android 逆向分析的方法、工具和实战技巧，包含 Smali 语法、静态分析、动态分析、Native 逆向和脱壳技术。

---

## 一、Smali 语法基础

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

## 二、逆向工具介绍

### 2.1 JEB

#### 简介
JEB 是一款专业的 Android 逆向工程平台，支持 DEX 反编译、Smali 调试、Native 代码分析等功能。

#### 核心功能
- **DEX 反编译**：将 DEX 反编译为 Java 代码（质量较高）
- **Smali 调试**：支持动态调试 Smali 代码
- **交叉引用**：类、方法、字段的引用关系
- **重命名**：可以给混淆的类/方法/字段重命名
- **注释**：支持添加注释
- **Native 分析**：支持 SO 文件的反汇编分析
- **脚本支持**：支持 Python 脚本自动化分析

#### 使用技巧
1. **快捷键**：
   - `Tab`：在 Smali 和 Java 之间切换
   - `X`：查看交叉引用
   - `N`：重命名
   - `/`：添加注释
   - `Ctrl+F`：搜索

2. **分析流程**：
   - 导入 APK → 等待解析完成
   - 查看 AndroidManifest.xml 了解应用结构
   - 搜索关键词（如"login"、"password"、"encrypt"）
   - 定位关键类和方法
   - 结合交叉引用分析调用链

### 2.2 IDA Pro

#### 简介
IDA Pro 是业界最强大的反汇编工具，支持多种架构和文件格式，是 Native 层逆向的首选工具。

#### 核心功能
- **多架构支持**：ARM、ARM64、x86、x64 等
- **反编译（F5）**：将汇编代码转换为伪 C 代码
- **交叉引用**：函数、字符串、数据的引用关系
- **动态调试**：支持远程调试 Android Native 代码
- **脚本支持**：IDC / IDAPython
- **插件系统**：丰富的第三方插件

#### 常用快捷键
| 快捷键 | 功能 |
|--------|------|
| F5 | 反编译为伪 C 代码 |
| Space | 切换图形视图/文本视图 |
| X | 查看交叉引用 |
| N | 重命名 |
| ; | 添加注释 |
| G | 跳转到地址 |
| Ctrl+S | 查看段列表 |
| Shift+F12 | 查看字符串 |
| Alt+T | 搜索文本 |

#### ARM 汇编基础

**寄存器**：
- R0-R3：函数参数和返回值
- R4-R11：通用寄存器（需保存）
- R12 (IP)：内部过程调用寄存器
- R13 (SP)：栈指针
- R14 (LR)：链接寄存器（保存返回地址）
- R15 (PC)：程序计数器

**常见指令**：
```arm
MOV R0, R1          @ R0 = R1
ADD R0, R1, R2      @ R0 = R1 + R2
SUB R0, R1, R2      @ R0 = R1 - R2
MUL R0, R1, R2      @ R0 = R1 * R2
LDR R0, [R1]        @ R0 = 内存[R1]
STR R0, [R1]        @ 内存[R1] = R0
BL function         @ 调用函数（LR = 返回地址, PC = function）
BX LR               @ 函数返回
CMP R0, R1          @ 比较 R0 和 R1
BEQ label           @ 相等则跳转
BNE label           @ 不等则跳转
BGT label           @ 大于则跳转
BLT label           @ 小于则跳转
```

### 2.3 Frida

#### 简介
Frida 是一款动态插桩工具，可以在运行时注入代码到目标进程，实现 Hook、内存修改、函数调用等功能。

#### 核心功能
- **Java 层 Hook**：Hook Java 方法，修改参数和返回值
- **Native 层 Hook**：Hook Native 函数
- **内存操作**：读写内存、搜索内存
- **模块操作**：加载/查找 SO 模块
- **函数调用**：主动调用应用内的函数
- **脚本注入**：动态注入 JavaScript 脚本

#### 安装与使用

```bash
# 安装 Frida 工具（电脑端）
pip install frida-tools

# 手机端安装 frida-server
# 1. 下载对应架构的 frida-server
# 2. push 到手机
adb push frida-server /data/local/tmp/
adb shell chmod 755 /data/local/tmp/frida-server

# 运行 frida-server
adb shell su -c /data/local/tmp/frida-server &

# 列出运行中的进程
frida-ps -U

# 附加到进程并执行脚本
frida -U -f com.example.app -l script.js --no-pause
```

---

## 三、APK 反编译流程

### 3.1 Apktool 反编译

#### 简介
Apktool 是最常用的 APK 反编译工具，可以提取资源文件和 Smali 代码，也可以重新打包 APK。

#### 基本使用

```bash
# 反编译 APK
apktool d app.apk -o app_output/

# 常用参数
apktool d app.apk -o app_output/ -r      # 不反编译资源文件（更快）
apktool d app.apk -o app_output/ -s      # 不反编译 dex（只解资源）
apktool d app.apk -o app_output/ -f      # 强制覆盖输出目录

# 重新打包
apktool b app_output/ -o rebuilt.apk

# 签名（重新打包后必须签名才能安装）
apksigner sign --ks mykey.keystore rebuilt.apk
# 或
jarsigner -verbose -keystore mykey.keystore rebuilt.apk alias_name
```

#### 反编译后的目录结构

```
app_output/
├── AndroidManifest.xml      # 明文 XML 格式的清单文件
├── apktool.yml              # apktool 配置文件
├── smali/                   # Smali 代码（主 dex）
│   └── com/example/
│       ├── MainActivity.smali
│       └── ...
├── smali_classes2/          # 第二个 dex 的 Smali 代码
├── res/                     # 资源文件（明文 XML + 图片）
│   ├── layout/
│   ├── drawable/
│   ├── values/
│   └── ...
├── assets/                  # 资产文件
├── lib/                     # Native 库
├── original/                # 原始文件（META-INF 等）
└── unknown/                 # 未知文件
```

### 3.2 JADX 反编译

#### 简介
JADX 是一个将 DEX 文件反编译为 Java 源代码的工具，有 GUI 和命令行两种版本。

#### 基本使用

```bash
# 命令行使用
jadx app.apk -d output_dir/

# 常用参数
jadx app.apk -d output_dir/ --no-res       # 不反编译资源
jadx app.apk -d output_dir/ --no-src       # 不反编译代码（只看资源）
jadx app.apk -d output_dir/ --show-bad-code  # 显示反编译失败的代码

# 启动 GUI
jadx-gui
```

#### JADX GUI 使用技巧
1. **搜索功能**：双击 Shift 全局搜索，支持类名、方法名、字符串
2. **反混淆**：可以导入映射文件还原混淆的名称
3. **导出 Gradle 项目**：File → Save as Gradle project
4. **查看交叉引用**：右键方法 → Find Usage
5. **注释与重命名**：支持对反编译结果添加注释和重命名

### 3.3 反编译实战流程

```
APK 文件
  │
  ├── Apktool → 资源文件 + Smali 代码 → 修改资源/代码 → 重新打包
  │
  ├── JADX → Java 源码 → 静态分析、理解逻辑
  │
  ├── JEB → Java + Smali → 深度分析、交叉引用
  │
  └── IDA → SO 反汇编 → Native 层分析
```

---

## 四、静态分析方法

### 4.1 信息收集

#### 基础信息
```bash
# 查看包名、版本号、权限、组件
aapt dump badging app.apk

# 查看 APK 签名信息
apksigner verify --verbose app.apk

# 查看 APK 中的文件列表
unzip -l app.apk
```

#### 第三方 SDK 识别
- 查看包名结构（如 com.qq.e.* 是广点通，com.umeng.* 是友盟）
- 使用 MobSF 自动识别
- 查看 AndroidManifest.xml 中的 Activity/Service 等组件

### 4.2 AndroidManifest.xml 分析

重点关注：
1. **权限申请**：申请了哪些危险权限，是否有不必要的权限
2. **组件导出**：哪些组件设置了 exported=true 或有 intent-filter
3. **自定义权限**：保护级别是 normal 还是 signature
4. **debuggable**：是否设置了 android:debuggable="true"
5. **allowBackup**：是否允许备份（android:allowBackup="true"）
6. **网络安全配置**：是否配置了 networkSecurityConfig
7. **usesCleartextTraffic**：是否允许明文 HTTP 流量

### 4.3 代码分析思路

#### 搜索敏感关键词
| 关键词 | 可能的用途 |
|--------|-----------|
| password / passwd / pwd | 密码相关 |
| encrypt / decrypt / cipher / AES / DES / RSA | 加密相关 |
| token / sign / signature | 签名/令牌 |
| secret / key | 密钥/秘密 |
| http:// / https:// | URL 地址 |
| SharedPreferences / getSharedPreferences | 数据存储 |
| Log. | 日志输出 |
| addJavascriptInterface | WebView 接口 |
| Runtime.getRuntime().exec | 命令执行 |

#### 分析入口点
- **Application 类**：attachBaseContext、onCreate
- **MainActivity**：主入口 Activity
- **自定义 ContentProvider**：onCreate 会在 Application 之前执行
- **App 启动广播**：BOOT_COMPLETED
- **Native 入口**：JNI_OnLoad

#### 分析调用链
1. 找到目标函数
2. 查看谁调用了它（交叉引用）
3. 向上追溯调用来源
4. 向下分析调用的子函数

### 4.4 加密算法识别

#### 常见特征

**AES 加密**：
- S-box 常量（256 个字节的查找表）
- 固定的轮常数
- 常见密钥长度：128/192/256 位

**RSA 加密**：
- 大整数运算
- 常见的公钥指数 0x10001 (65537)
- Base64 编码的公钥/私钥

**MD5/SHA 哈希**：
- 固定的初始化常量（MD5: 0x67452301, 0xEFCDAB89...）
- 固定的输出长度（MD5: 16字节, SHA1: 20字节, SHA256: 32字节）

**Base64 编码**：
- 特征字符表：`ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/`
- 末尾可能有 `=` 填充

#### 识别方法
1. 搜索算法相关的类名/方法名（如 Cipher、MessageDigest）
2. 搜索常量特征（如 AES S-box、MD5 初始化常量）
3. 使用工具自动识别（如 FindCrypt、Signsrch、IDA 插件）

### 4.5 资源文件分析

#### strings.xml
- 搜索敏感字符串
- 查找 URL、密钥、密码等

#### 布局文件
- 分析界面结构
- 查找敏感输入框（id 可能暗示用途）

#### assets/ 目录
- 可能包含配置文件、HTML、JS、数据库等
- 检查是否有明文存储的敏感信息

---

## 五、动态分析方法

### 5.1 Frida Hook 基础

#### Hook Java 方法

```javascript
// 基本的 Java 层 Hook
Java.perform(function() {
    // 获取目标类
    var LoginActivity = Java.use("com.example.LoginActivity");
    
    // Hook 方法
    LoginActivity.login.implementation = function(username, password) {
        // 打印参数
        console.log("[*] login 被调用");
        console.log("    username: " + username);
        console.log("    password: " + password);
        
        // 调用原方法
        var result = this.login(username, password);
        console.log("    返回值: " + result);
        
        // 修改返回值
        return true;
    };
});
```

#### Hook 构造方法

```javascript
Java.perform(function() {
    var StringBuilder = Java.use("java.lang.StringBuilder");
    
    // Hook 构造方法
    StringBuilder.$init.overload('java.lang.String').implementation = function(str) {
        console.log("[*] StringBuilder 构造: " + str);
        return this.$init(str);
    };
});
```

#### Hook 重载方法

```javascript
Java.perform(function() {
    var TextUtils = Java.use("android.text.TextUtils");
    
    // 获取指定参数的重载版本
    var isEmpty = TextUtils.isEmpty.overload('java.lang.CharSequence');
    
    isEmpty.implementation = function(str) {
        var result = isEmpty.call(this, str);
        console.log("[*] TextUtils.isEmpty(" + str + ") = " + result);
        return result;
    };
});
```

### 5.2 Xposed Hook 基础

#### 简介
Xposed 是一个 Android 平台的 Hook 框架，可以在不修改 APK 的情况下修改应用行为。

#### 基本使用

```java
// Xposed 模块示例
public class Main implements IXposedHookLoadPackage {
    
    @Override
    public void handleLoadPackage(XC_LoadPackage.LoadPackageParam lpparam) throws Throwable {
        // 只 Hook 目标应用
        if (!lpparam.packageName.equals("com.example.app")) {
            return;
        }
        
        final Class<?> clazz = XposedHelpers.findClass(
                "com.example.LoginActivity", lpparam.classLoader);
        
        XposedHelpers.findAndHookMethod(clazz, "login",
                String.class, String.class,
                new XC_MethodHook() {
                    @Override
                    protected void beforeHookedMethod(MethodHookParam param) throws Throwable {
                        // 方法执行前
                        XposedBridge.log("login 调用前");
                        XposedBridge.log("参数1: " + param.args[0]);
                        XposedBridge.log("参数2: " + param.args[1]);
                    }
                    
                    @Override
                    protected void afterHookedMethod(MethodHookParam param) throws Throwable {
                        // 方法执行后
                        XposedBridge.log("login 返回: " + param.getResult());
                        // 修改返回值
                        param.setResult(true);
                    }
                });
    }
}
```

### 5.3 动态调试

#### 使用 Android Studio 调试 Smali

1. **准备工作**：
   - 使用 apktool 反编译 APK
   - 修改 AndroidManifest.xml，设置 `android:debuggable="true"`
   - 重新打包并签名

2. **调试步骤**：
   - 安装修改后的 APK
   - 使用 Android Studio 打开 Smali 项目（或使用 Smalidea 插件）
   - 下断点
   - 启动调试

#### 使用 IDA 调试 Native 代码

1. **准备工作**：
   - 复制 android_server 到手机
   - 运行 android_server

2. **调试步骤**：
   - IDA → Debugger → Remote ARM Linux/Android debugger
   - 配置调试参数（主机地址、端口）
   - 选择要调试的进程
   - 下断点，开始调试

### 5.4 抓包分析

#### HTTP/HTTPS 抓包

**工具**：Charles、Burp Suite、Fiddler

**步骤**：
1. 手机和电脑连接同一网络
2. 手机设置代理指向电脑
3. 电脑上安装抓包工具
4. 手机安装抓包工具的 CA 证书
5. 开始抓包分析

**注意事项**：
- Android 7.0+ 默认不信任用户证书，需要系统级证书或使用 Frida 绕过
- 使用 SSL Pinning 的应用需要先绕过才能抓包

---

## 六、Native 层逆向（SO 分析）

### 6.1 JNI 基础

#### JNI 函数命名

静态注册（按命名规则）：
```
Java_包名_类名_方法名(参数列表)
```

示例：
```c
// Java 层
package com.example;
public class NativeLib {
    public native String getSign(String input);
}

// Native 层对应的函数名
Java_com_example_NativeLib_getSign(JNIEnv *env, jobject thiz, jstring input)
```

动态注册（使用 RegisterNatives）：
```c
// 方法映射表
static JNINativeMethod methods[] = {
    {"getSign", "(Ljava/lang/String;)Ljava/lang/String;", (void *)native_getSign},
    {"encrypt", "([B)[B", (void *)native_encrypt}
};

// 在 JNI_OnLoad 中注册
jint JNI_OnLoad(JavaVM *vm, void *reserved) {
    JNIEnv *env = NULL;
    (*vm)->GetEnv(vm, (void **)&env, JNI_VERSION_1_6);
    
    jclass clazz = (*env)->FindClass(env, "com/example/NativeLib");
    (*env)->RegisterNatives(env, clazz, methods, sizeof(methods)/sizeof(methods[0]));
    
    return JNI_VERSION_1_6;
}
```

#### JNI 类型映射

| Java 类型 | Native 类型 | 签名 |
|-----------|------------|------|
| boolean | jboolean | Z |
| byte | jbyte | B |
| char | jchar | C |
| short | jshort | S |
| int | jint | I |
| long | jlong | J |
| float | jfloat | F |
| double | jdouble | D |
| String | jstring | Ljava/lang/String; |
| int[] | jintArray | [I |
| byte[] | jbyteArray | [B |

### 6.2 SO 文件分析步骤

#### 1. 确定目标 SO
- 查看 APK 的 lib/ 目录
- 搜索 Java 层的 `System.loadLibrary()` 调用
- 查看 native 方法声明

#### 2. 加载到 IDA
- 打开 IDA Pro
- 拖入 .so 文件
- 选择 ARM/ARM64 架构
- 等待自动分析完成

#### 3. 查找关键函数

**方法1：搜索导出函数**
- 打开 Exports 窗口（Shift+F4）
- 查找 Java_ 开头的函数（静态注册）
- 查找 JNI_OnLoad 函数

**方法2：搜索字符串**
- 打开 Strings 窗口（Shift+F12）
- 搜索关键词（key、sign、encrypt 等）
- 交叉引用找到使用该字符串的函数

**方法3：搜索导入函数**
- 查看 Imports 窗口
- 关注加密相关函数（如 OpenSSL 的函数）

#### 4. 分析函数逻辑
- 使用 F5 反编译为伪 C 代码
- 分析函数参数和返回值
- 识别加密算法
- 理解业务逻辑

### 6.3 常见 Native 安全问题

#### 1. 密钥硬编码
```c
// 密钥直接写在代码中，容易被提取
const char *SECRET_KEY = "my_secret_key_12345";
```

#### 2. 不校验调用者
```c
// 危险：Native 函数不校验调用者是否为合法应用
// 任何应用加载这个 so 都能调用
jstring Java_com_example_NativeLib_getSign(JNIEnv *env, jobject thiz, jstring input) {
    // 没有校验调用者的签名、包名等
    return encrypt(input, SECRET_KEY);
}
```

#### 3. 缓冲区溢出
```c
// 危险：没有检查输入长度
void process_data(char *input) {
    char buffer[64];
    strcpy(buffer, input);  // 输入过长会溢出
}
```

### 6.4 Native 层 Hook

#### 使用 Frida Hook Native 函数

```javascript
// Hook 导出函数
var nativeFunc = Module.findExportByName("libnative.so", "Java_com_example_NativeLib_getSign");

Interceptor.attach(nativeFunc, {
    onEnter: function(args) {
        // args[0] = JNIEnv*
        // args[1] = jobject
        // args[2] = jstring input
        console.log("[*] getSign 被调用");
        var inputStr = Java.vm.getEnv().getStringUtfChars(args[2], null).readCString();
        console.log("    input: " + inputStr);
    },
    onLeave: function(retval) {
        console.log("    返回值地址: " + retval);
        // 解析返回的 jstring
        var resultStr = Java.vm.getEnv().getStringUtfChars(retval, null).readCString();
        console.log("    返回值: " + resultStr);
    }
});

// Hook 内部函数（通过地址偏移）
var baseAddr = Module.findBaseAddress("libnative.so");
var funcAddr = baseAddr.add(0x1234);  // 函数在 so 中的偏移

Interceptor.attach(funcAddr, {
    onEnter: function(args) {
        console.log("[*] 内部函数被调用");
        console.log("    arg0: " + args[0]);
        console.log("    arg1: " + args[1]);
    },
    onLeave: function(retval) {
        console.log("    return: " + retval);
    }
});
```

---

## 七、脱壳与反调试对抗

### 7.1 加壳原理

#### 整体加固流程

```
加固流程：
原始 APK → 提取 DEX → 加密 DEX → 生成壳程序 → 替换 Application → 打包签名 → 加固后的 APK

运行流程：
启动应用 → 壳 Application 运行 → 解密 DEX → 动态加载 DEX → 切换到真实 Application → 业务代码运行
```

#### 壳的类型

| 类型 | 原理 | 难度 |
|------|------|------|
| 整体壳 | 加密整个 DEX，运行时解密加载 | 较易脱壳 |
| 函数级壳 | 对每个函数单独加密，调用时解密 | 中等 |
| VMP 壳 | 将代码转为自定义虚拟机指令 | 困难 |
| 混淆壳 | 控制流平坦化、指令替换等 | 较难 |

### 7.2 常见壳的识别

#### 识别方法

**1. 查看 APK 结构**：
- classes.dex 很小（壳的 dex）
- assets 目录下有加密的 dex 文件
- lib 目录下有壳的 so 文件

**2. 查看 Application**：
- AndroidManifest.xml 中的 Application 类名是壳的类
- 常见壳的 Application 类名特征

**3. 查看特征文件**：
- 梆梆：libsecexe.so、libsecshell.so
- 爱加密：libexec.so、libexecmain.so
- 360 加固：libjiagu.so、libjiagu_art.so
- 腾讯乐固：libshell-super.2019.so
- 百度加固：libbaiduprotect.so

### 7.3 脱壳方法

#### 方法1：内存 dump 脱壳

**原理**：壳在运行时会将 DEX 解密加载到内存中，直接从内存 dump 出来。

**使用 Frida-DEXDump**：
```bash
# 安装
pip install frida-dexdump

# 使用
frida-dexdump -U -f com.example.app
# 或附加到已运行的进程
frida-dexdump -U -n com.example.app
```

**使用 FART（系统级脱壳）**：
- 基于定制 ROM 的脱壳方案
- 在 ART 层面主动调用所有方法，触发类加载
- 能够脱函数级壳和 VMP 壳

#### 方法2：动态调试脱壳

**原理**：在壳解密完成后下断点，dump 内存中的 dex。

**步骤**：
1. 使用 IDA 附加到应用进程
2. 在 dex 加载完成的位置下断点
3. 断点命中后，从内存中 dump dex 数据
4. 修复 dex 文件结构

#### 方法3：Hook 脱壳

**原理**：Hook 系统加载 dex 的函数，在加载时保存 dex 数据。

**Hook 点**：
- `DexFile::DexFile()`
- `OpenMemory()`
- `CookieToDexFile()`
- `dexFileLoad()`

#### 脱壳工具对比

| 工具 | 原理 | 支持的壳 | 优点 | 缺点 |
|------|------|---------|------|------|
| Frida-DEXDump | 内存搜索 dump | 大部分整体壳 | 使用简单 | 不支持 VMP/函数级壳 |
| FART | 系统级主动调用 | 大部分加固 | 脱壳彻底 | 需要刷定制 ROM |
| Youpk | 系统级脱壳 | 大部分加固 | 脱壳彻底 | 需要特定版本 ROM |
| BlackDex | 内存 dump | 整体壳 | 快速方便 | 不支持复杂壳 |

### 7.4 反调试对抗

#### 常见反调试手段

**1. ptrace 检测**
```c
// 检测是否被 ptrace 附加
if (ptrace(PTRACE_TRACEME, 0, 0, 0) == -1) {
    // 已被调试
    exit(0);
}
```

**2. 读取 /proc/pid/status**
```c
// 查看 TracerPid 字段，非 0 表示被调试
FILE *fp = fopen("/proc/self/status", "r");
// 读取 TracerPid 行
```

**3. 时间差检测**
```c
// 检测代码执行时间，断点会导致时间变长
long start = get_timestamp();
// 执行一段代码
long end = get_timestamp();
if (end - start > THRESHOLD) {
    // 可能被调试
}
```

**4. 检测调试端口**
- 检测 27042 端口（Frida 默认端口）
- 检测 23946 端口（IDA 调试端口）

**5. 检测 Frida**
- 检查 /proc/pid/maps 中是否有 frida 相关的库
- 检查 Java 层是否有 Frida 相关的类

#### 反调试绕过方法

**1. Frida Hook 绕过**
```javascript
// Hook ptrace 函数
var ptrace = Module.findExportByName(null, "ptrace");
Interceptor.replace(ptrace, new NativeCallback(function(request, pid, addr, data) {
    console.log("[*] ptrace 被调用, request=" + request);
    // 假装成功
    return 0;
}, 'int', ['int', 'int', 'pointer', 'pointer']));
```

**2. 修改 Smali/So**
- 静态修改反调试判断逻辑
- 将条件跳转改为无条件跳转或相反

**3. 使用 Magisk 模块**
- 隐藏 Root 状态
- 隐藏调试环境
- 隐藏 Frida

### 7.5 脱壳实战流程

```
1. 识别壳的类型
   ├── 查看 APK 结构
   ├── 查看 Application 类名
   └── 查看 lib 目录下的 so

2. 选择脱壳方案
   ├── 简单整体壳 → Frida-DEXDump / BlackDex
   ├── 函数级壳 → FART / Youpk
   └── VMP 壳 → 手工分析 / 定制方案

3. 执行脱壳
   ├── 运行目标应用
   ├── 触发关键功能（确保代码加载）
   └── 执行脱壳工具

4. 验证结果
   ├── 查看 dump 出的 dex 文件
   ├── 用 JADX 打开验证能否反编译
   └── 检查是否包含目标类和方法

5. 后续分析
   ├── 静态分析反编译后的代码
   ├── 动态调试验证逻辑
   └── 编写 Hook 脚本
```

---

> 提示：逆向分析需要长期积累，建议从简单的应用开始练习，逐步提升难度。多打 CTF 题目、多看优秀的分析文章是快速提升的好方法。
