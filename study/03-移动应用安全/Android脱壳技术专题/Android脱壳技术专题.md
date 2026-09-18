# Android 脱壳技术专题

> 本文档系统讲解 Android 应用加固与脱壳技术，覆盖加固原理、脱壳方法、实战流程及反调试对抗，适用于安全研究与教学场景。

---

## 目录

1. [Android 加固技术概述](#1-android-加固技术概述)
2. [脱壳原理](#2-脱壳原理)
3. [常见脱壳方法](#3-常见脱壳方法)
4. [实战脱壳流程](#4-实战脱壳流程)
5. [函数抽取壳处理](#5-函数抽取壳处理)
6. [VMP 壳分析入门](#6-vmp-壳分析入门)
7. [反调试与绕过](#7-反调试与绕过)
8. [脱壳注意事项](#8-脱壳注意事项)

---

## 1. Android 加固技术概述

### 1.1 APK 文件结构（DEX / 资源 / 签名）

APK 本质上是一个 ZIP 压缩包，解压后包含以下核心结构：

```
app.apk
├── AndroidManifest.xml     # 编译后的二进制清单文件
├── classes.dex             # Dalvik 可执行文件（应用代码）
├── classes2.dex            # 多 DEX 支持（方法数超过 65535 时）
├── resources.arsc          # 编译后的资源索引表
├── res/                    # 资源文件（图片/布局等）
├── lib/                    # Native 库（.so 文件，按架构分目录）
│   ├── arm64-v8a/
│   ├── armeabi-v7a/
│   └── x86_64/
├── assets/                 # 原始资源（不编译，原样打包）
├── META-INF/               # 签名信息
│   ├── MANIFEST.MF
│   ├── CERT.SF
│   └── CERT.RSA
└── META-INF/CERT.RSA       # 签名证书
```

加固后的 APK 通常会修改 `classes.dex`，将其替换为壳的入口 DEX，真正的业务 DEX 则被加密存储在 assets 或 SO 库中。

### 1.2 DEX 文件格式详解

DEX（Dalvik Executable）是 Android 虚拟机（Dalvik/ART）的可执行格式。理解 DEX 格式是脱壳的基础。

```
DEX 文件结构:
┌──────────────────────────┐
│ Header (0x70 bytes)       │  ← magic: "dex\n035\0" (或 036/037/038/039)
│  - checksum              │
│  - signature (SHA-1)     │
│  - file_size, header_size│
│  - 各数据区起始偏移与大小  │
├──────────────────────────┤
│ String IDs (字符串索引)    │
├──────────────────────────┤
│ Type IDs (类型索引)        │
├──────────────────────────┤
│ Proto IDs (方法原型索引)   │
├──────────────────────────┤
│ Field IDs (字段索引)       │
├──────────────────────────┤
│ Method IDs (方法索引)      │
├──────────────────────────┤
│ Class Defs (类定义)        │
├──────────────────────────┤
│ Data (实际数据区)          │  ← CodeItem 存储在此区域
├──────────────────────────┤
│ Link Data (链接数据)       │
└──────────────────────────┘
```

关键概念：
- **CodeItem**：每个 Java 方法的字节码都封装在 CodeItem 结构中，包含寄存器列表、Dalvik 指令集。函数抽取壳的核心就是剥离 CodeItem。
- **magic header**：`dex\n035\0`（8 字节），这是内存中识别 DEX 的核心特征。
- **DEX 校验**：checksum（Adler32）和 signature（SHA-1），脱壳后需修复。

### 1.3 加固原理

Android 加固的核心思路是将原始 DEX 加密隐藏，运行时动态解密加载到内存中执行。

| 加固类型 | 原理 | 保护层级 |
|----------|------|----------|
| **DEX 整体加密（一代壳）** | 将 classes.dex 加密存储，壳 DEX 负责解密并加载 | 整体保护 |
| **函数抽取（二代壳）** | DEX 结构保留，但 CodeItem 被抽空，运行时逐函数还原 | 方法级保护 |
| **VMP 虚拟化（三代壳）** | 将 Dalvik 指令转为自定义虚拟指令集，由解释器执行 | 指令级保护 |
| **DEX 隐藏（四代壳）** | 利用 ART 的类加载机制，在不修改原 DEX 的前提下动态加载隐藏 DEX | 动态加载保护 |

### 1.4 主流加固厂商特征

| 厂商 | 特征文件/关键词 | 加固类型 |
|------|----------------|----------|
| 腾讯乐固 | `libshell.so`、`libshella.so`、`com.tencent.StubShell.TxAppEntry` | DEX 整体加密 + 函数抽取 |
| 360 加固保 | `libjiagu.so`、`libjiagu_aosp.so`、`com.stub.StubApp` | DEX 整体加密 |
| 爱加密 | `libencauth.so`、`libencore.so`、`ijiami.dat` | DEX 整体加密 + 函数抽取 |
| 梆梆安全 | `libsecexe.so`、`libsecmain.so`、`libSecShell.so` | 函数抽取 + VMP |
| 阿里聚安全 | `libsgmainso-6.4.xx.so`、`libsg intrusionso` | DEX 加密 |
| 百度安全 | `libbaiduprotect.so` | DEX 加密 |

---

## 2. 脱壳原理

### 2.1 内存中 DEX 文件特征

无论加固方案多么复杂，最终 DEX 都需要被加载到内存中由 ART 虚拟机执行。因此内存中必然存在完整或部分完整的 DEX 数据。

核心特征：
- **magic header**：`64 65 78 0A 30 33 35 00`（`dex\n035\0`）
- **string_data** 区域包含类名、方法名等字符串
- 完整的 DEX 在内存中通常以 4KB 对齐

### 2.2 脱壳时机选择

脱壳效果取决于脱壳时机：

| 时机 | 方法 | 效果 |
|------|------|------|
| **App 刚启动** | attach 时 dump | 可能只拿到壳 DEX，真正 DEX 尚未加载 |
| **类加载后** | dexopt/dex2oat 阶段 | DEX 已解密，但函数抽取壳可能未还原 |
| **关键方法调用后** | 运行中 dump | 适合函数抽取壳，需主动触发各方法 |
| **全量执行后** | 深度主动调用后 | 效果最好，覆盖面最广 |

### 2.3 主动调用 vs 被动 Dump

| 方式 | 原理 | 优势 | 劣势 |
|------|------|------|------|
| **被动 Dump** | 在内存中搜索 DEX 特征并直接提取 | 实现简单 | 函数抽取壳只能拿到空壳 |
| **主动调用** | 主动调用每个方法，触发 CodeItem 还原后 Dump | 能还原函数抽取壳 | 覆盖率依赖调用范围 |

### 2.4 加固代际演进

```
一代壳（整体加密DEX）
  │  原理: classes.dex 加密 → 壳解密 → 加载到内存
  │  脱壳: 内存搜索 magic header 即可
  │  难度: ★☆☆☆☆
  ▼
二代壳（函数抽取）
  │  原理: DEX 结构完整，CodeItem 被抽空 → 运行时逐方法还原
  │  脱壳: 需主动调用每个方法触发还原 + FART 等自动化工具
  │  难度: ★★★☆☆
  ▼
三代壳（VMP 虚拟化）
  │  原理: 核心方法转为虚拟指令集 → 自定义解释器执行
  │  脱壳: 需逆向虚拟指令集映射表，难度极高
  │  难度: ★★★★★
  ▼
四代壳（DEX隐藏/动态加载）
  │  原理: 利用 ClassLoader 机制，隐藏 DEX 不落盘
  │  脱壳: 需 Hook 类加载器，枚举所有加载的 DEX
  │  难度: ★★★★☆
```

---

## 3. 常见脱壳方法

### 3.1 DexExtractor 原理与使用

**原理**：通过 Hook `DexFile` 构造函数或 `openDexFile` 方法，在 DEX 被加载时拦截并 dump。

```
流程:
1. Hook art::DexFile::OpenMemory (ART 虚拟机内部接口)
2. 当壳 DEX 加载真正的 DEX 时，该方法被调用
3. 拦截参数中的 DEX 数据指针和大小
4. 将数据写入文件
```

**使用**：
```bash
# 需要定制 ROM 或使用 Frida 注入
# 对 ART 虚拟机有版本依赖
```

### 3.2 DexHound 原理

**原理**：基于 Frida，在运行时遍历 ART 内部结构 `DexFile` 对象链表，枚举所有已加载的 DEX 文件并导出。

与直接搜索 magic header 不同，DexHound 直接从 ART 的内部数据结构中获取 DEX 列表，更精确。

```
ART 内部结构:
ClassLinker
  └── dex_caches_ (数组)
        └── DexCache
              └── dex_file (指针) → DEX 数据在内存中的地址
```

### 3.3 FRIDA-DEXDump 原理与使用

**原理**：基于 Frida，在目标进程内存中扫描 DEX magic header（`dex\n035`），找到后根据 header 中的 `file_size` 字段确定 DEX 大小并完整导出。

```bash
# 安装
pip install frida-dexdump

# 使用（需要 root + frida-server）
# 方式1: attach 到运行中的进程
frida-dexdump -U -p <pid>

# 方式2: spawn 模式启动
frida-dexdump -U -f com.example.app -o ./output/

# 输出目录中会包含所有 dump 出的 DEX 文件
```

**优势**：
- 无需定制 ROM
- 支持一代壳和部分二代壳
- 可导出多个 DEX 文件

**局限**：
- 函数抽取壳只能导出部分 DEX（空 CodeItem）
- 无法自动修复被修改的 header

### 3.4 BlackDex 原理与使用

**原理**：利用 ART 虚拟机的类加载机制，创建独立进程，通过 Hook `DexFile` 加载流程拦截 DEX 数据。

BlackDex 的核心创新在于使用 **双进程模型**：
- 进程 A：运行壳代码，触发 DEX 解密
- 进程 B：通过内存映射读取进程 A 中已解密的 DEX

```bash
# 使用 BlackDex
# 1. 安装 BlackDex APK
# 2. 选择目标应用
# 3. 点击 "Unpack"
# 4. 输出 DEX 到 /sdcard/Android/data/com.blackdex/files/

# 也可通过 Frida 使用核心逻辑
```

### 3.5 Youpk 原理

**原理**：基于定制 ART 虚拟机的脱壳方案。修改 AOSP 中 ART 的源码，在 `ClassLinker::DefineClass` 和方法编译流程中插入 dump 逻辑。

核心机制：
1. 在 ART 中添加**调用链追踪**
2. 当每个 Java 方法被**首次调用**时，自动 dump 对应的 CodeItem
3. 通过**全量主动调用**保证所有方法被触发
4. 最终合成完整 DEX

### 3.6 FART（自动化脱壳）原理

**原理**：FART（Firm Analyze and Reverse Tool）通过**修改 AOSP 源码**，在 ART 虚拟机的类加载和方法编译阶段插入主动调用和 dump 逻辑。

核心机制分为三步：

```
步骤1: 类枚举
  ├─ 修改 DexFile 解析流程，获取所有类列表
  └─ 对每个类执行 Class.forname() 触发加载

步骤2: 主动调用
  ├─ 获取每个类的所有方法
  ├─ 逐个构造参数并主动调用
  └─ 确保 CodeItem 被还原到内存中

步骤3: CodeItem Dump
  ├─ 在 ART 方法编译入口插入 dump 逻辑
  ├─ 每个方法被调用时 dump 对应的 CodeItem
  └─ 最终合成完整 DEX
```

FART 是目前对付函数抽取壳最有效的工具之一。

### 3.7 各方法对比表

| 工具/方法 | 适用壳类型 | Root 要求 | 需定制 ROM | 成功率 | 操作难度 |
|-----------|-----------|-----------|-----------|--------|----------|
| FRIDA-DEXDump | 一代壳 | 需要 | 否 | 高 | 低 |
| BlackDex | 一代壳 | 需要 | 否 | 中高 | 低 |
| DexExtractor | 一代壳 | 需要 | 否 | 中 | 中 |
| DexHound | 一代/二代壳 | 需要 | 否 | 中 | 中 |
| FART | 一代/二代壳 | 需要 | 是 | 高 | 中高 |
| Youpk | 一代/二代壳 | 需要 | 是 | 极高 | 高 |
| 手动 IDA 分析 | 全部 | 否 | 否 | 视壳复杂度 | 极高 |

---

## 4. 实战脱壳流程

### 4.1 判断加固类型

```bash
# 1. 解压 APK
unzip target.apk -d target_app

# 2. 检查 APK 中是否有加固特征文件
find target_app -name "*.so" | grep -E "shell|jiagu|sec|enc"
# 示例输出:
# target_app/lib/arm64-v8a/libshell.so        → 腾讯乐固
# target_app/lib/arm64-v8a/libjiagu.so         → 360加固保
# target_app/lib/arm64-v8a/libsecmain.so       → 梆梆安全
# target_app/assets/ijiami.dat                → 爱加密

# 3. 检查 AndroidManifest.xml 中的 Application 类
# 反编译 AndroidManifest:
java -jar apktool.jar d target.apk -o target_decoded
# 查看 application android:name 属性
# 例: android:name="com.tencent.StubShell.TxAppEntry" → 腾讯乐固
# 例: android:name="com.stub.StubApp"                  → 360加固保

# 4. 检查 classes.dex 的方法数
# 如果 classes.dex 只包含壳的少量类，说明是整体加密壳
# 如果 classes.dex 结构完整但方法体为空，说明是函数抽取壳
```

### 4.2 选择脱壳方法

```
判断流程:

APK 加固特征分析
  │
  ├── 一代壳（DEX 整体加密）
  │     └── 选择: FRIDA-DEXDump / BlackDex
  │         └── 成功率高，操作简单
  │
  ├── 二代壳（函数抽取）
  │     └── 选择: FART / Youpk
  │         └── 需定制 ROM，但效果最好
  │
  ├── 三代壳（VMP）
  │     └── 选择: IDA 逆向 + 手动分析
  │         └── 无通用工具，需个案分析
  │
  └── 四代壳（DEX 隐藏）
        └── 选择: BlackDex / FRIDA-DEXDump + ClassLoader Hook
            └── 需 Hook 枚举所有 ClassLoader
```

### 4.3 内存 Dump DEX

以 FRIDA-DEXDump 为例：

```bash
# 1. 启动 frida-server
adb shell "su -c '/data/local/tmp/frida-server &'"

# 2. 启动目标应用
adb shell am start -n com.example.app/.MainActivity

# 3. 等待应用完全加载
sleep 5

# 4. 执行脱壳
frida-dexdump -U -f com.example.app -o ./dex_output/

# 5. 查看导出的 DEX
ls -la ./dex_output/
# 输出:
# classes.dex   classes02.dex   classes03.dex ...
```

### 4.4 DEX 修复（Header 修复 / CodeItem 对齐）

Dump 出的 DEX 可能存在以下问题，需要修复：

```
常见问题:
1. Header 中的 checksum 和 signature 不匹配
   → 重新计算 Adler32 checksum 和 SHA-1 signature

2. DEX 数据不完整（截断）
   → 通过 header 中的 file_size 判断完整性

3. CodeItem 对齐问题（函数抽取壳）
   → 需将 dump 出的 CodeItem 写回 DEX 对应位置

4. multi-dex 合并
   → 多个 DEX 需要合并或分别处理
```

修复脚本示例：

```python
import struct
import zlib
import hashlib

def fix_dex_header(dex_data):
    """修复 DEX 文件头部 checksum 和 signature"""
    # 1. 重新计算 SHA-1 signature
    sha1 = hashlib.sha1(dex_data[32:]).digest()
    dex_data = dex_data[:12] + sha1 + dex_data[32:]

    # 2. 重新计算 Adler32 checksum
    checksum = zlib.adler32(dex_data[12:])
    dex_data = dex_data[:8] + struct.pack('<I', checksum) + dex_data[12:]

    return dex_data

# 使用
with open('dumped.dex', 'rb') as f:
    data = bytearray(f.read())

fixed = fix_dex_header(data)

with open('fixed.dex', 'wb') as f:
    f.write(fixed)
```

### 4.5 反编译验证（jadx / JADX-GUI）

```bash
# 使用 jadx 反编译修复后的 DEX
jadx -d ./jadx_output fixed.dex

# 或使用图形界面
jadx-gui fixed.dex

# 验证脱壳效果:
# 1. 检查关键类是否存在（如 com.example.app.MainActivity）
# 2. 检查方法体是否完整（非抽象方法应有字节码）
# 3. 检查字符串资源是否可读
# 4. 如果反编译出大量 "Code" 或空方法体 → 函数抽取壳未完全还原
```

---

## 5. 函数抽取壳处理

### 5.1 函数抽取原理

函数抽取壳的核心原理：

```
原始 DEX:
  方法A: 有完整 CodeItem (Dalvik 指令)
  方法B: 有完整 CodeItem
  方法C: 有完整 CodeItem

加固后 DEX:
  方法A: CodeItem 被抽空 (保留方法定义，方法体为空)
  方法B: CodeItem 被抽空
  方法C: CodeItem 被抽空
  
  加密的 CodeItem 数据 → 存储在 SO 库或 assets 中

运行时:
  方法A 被调用 → 壳从加密数据中解密 CodeItemA → 写回内存 → 执行
  方法B 被调用 → 壳从加密数据中解密 CodeItemB → 写回内存 → 执行
  ...
```

关键点：
- DEX 文件结构（类定义、方法定义）保持完整
- 只是 CodeItem（方法体）被抽空
- 运行时按需还原，还原后方法体存在内存中
- 如果在方法被调用前 dump，只能得到空壳

### 5.2 主动调用触发

```javascript
// Frida 主动调用脚本: 遍历所有类的方法并主动调用
Java.perform(function() {
    var dexClassLoader = Java.use("dalvik.system.DexClassLoader");
    // 获取目标应用的所有已加载类

    Java.enumerateLoadedClasses({
        onMatch: function(className) {
            try {
                var cls = Java.use(className);
                var methods = cls.class.getDeclaredMethods();
                methods.forEach(function(method) {
                    var methodName = method.getName();
                    try {
                        // 构造空参数调用
                        var params = method.getParameterTypes();
                        var args = params.map(function(p) {
                            var name = p.getName();
                            if (name === "int" || name === "long") return 0;
                            if (name === "boolean") return false;
                            return null;
                        });
                        // 注意: 主动调用可能触发异常，需 try-catch
                        cls[methodName].apply(cls.$new(), args);
                    } catch(e) {
                        // 调用失败是正常的，关键是触发 CodeItem 还原
                    }
                });
            } catch(e) {}
        },
        onComplete: function() {
            console.log("主动调用完成");
        }
    });
});
```

### 5.3 FART 自动还原

FART 的主动调用逻辑（核心思路）：

```
FART 主动调用流程:
1. 枚举 DEX 中的所有类定义
2. 对每个类执行 Class.forName() 触发类加载
3. 获取类的所有方法
4. 逐个方法主动调用（即使会抛异常也没关系，重点是触发还原）
5. 在 ART 内部 hook 方法编译入口
6. 当方法被触发时，dump 对应的 CodeItem 到文件
7. 后处理：将 CodeItem 写回 DEX 对应位置
```

### 5.4 CodeItem 定位与提取

CodeItem 在 DEX 文件中的定位：

```
方法定位流程:
1. 从 MethodIds 数组中找到目标方法
2. 从 ClassDefs 中找到方法所在的类
3. ClassDefs 中有 class_data_off 指向类数据
4. 类数据中包含每个方法的 code_off
5. code_off 直接指向 CodeItem 在 DEX 中的偏移

CodeItem 结构:
┌──────────────────────────┐
│ code_off (4 bytes)       │ ← 在 DEX 文件中的偏移量
├──────────────────────────┤
│ registers_size (2 bytes) │ ← 寄存器数量
│ ins_size (2 bytes)       │ ← 参数寄存器数量
│ outs_size (2 bytes)      │ ← 调用其他方法所需寄存器
│ tries_size (2 bytes)     │ ← try/catch 块数量
├──────────────────────────┤
│ debug_info_off (4 bytes) │
│ insns_size (4 bytes)     │ ← 指令数量（2字节为单位）
├──────────────────────────┤
│ insns[] (insns_size*2)   │ ← Dalvik 字节码指令
├──────────────────────────┤
│ padding (可选)            │
│ try_items[]              │
│ handlers[]               │
└──────────────────────────┘
```

---

## 6. VMP 壳分析入门

### 6.1 VMP 原理（指令虚拟化）

VMP（Virtual Machine Protection）将原始的 Dalvik 字节码转换为自定义的虚拟指令集，由壳内置的虚拟机解释器执行。

```
原始流程:
  Java方法 → Dalvik字节码 → ART虚拟机执行

VMP 保护后:
  Java方法 → Dalvik字节码 → 加密存储
              ↓
  运行时: 加密指令 → 自定义解释器 → 执行
  
  自定义指令集 → 与 Dalvik 指令完全不同
  解释器 → 在 SO 库中实现
```

### 6.2 VMP 还原难度

VMP 是目前最难脱壳的加固方案：

| 挑战 | 说明 |
|------|------|
| 指令映射表未知 | 每个壳的自定义指令集不同，需逆向映射表 |
| 解释器混淆 | SO 库中的解释器代码经过 OLLVM 混淆 |
| 无标准 DEX 可 Dump | 代码以虚拟指令存在，不是标准 Dalvik 指令 |
| 上下文相关 | 部分虚拟指令依赖运行时状态，难以静态还原 |

### 6.3 部分还原方法

```
VMP 部分还原思路:

1. 定位解释器入口
   ├─ 在 SO 库中找到指令 dispatch 循环
   └─ 通常是一个大的 switch-case 结构

2. 分析指令映射
   ├─ 逐个 case 分析虚拟指令的语义
   ├─ 建立 虚拟指令 → Dalvik指令 映射表
   └─ 利用已知的执行行为辅助验证

3. 动态跟踪验证
   ├─ 使用 Frida Stalker 跟踪解释器执行流
   ├─ 对比原始方法逻辑与虚拟执行结果
   └─ 确认映射关系正确性

4. 有限还原
   ├─ 对于简单方法（算术运算/条件跳转）可完整还原
   └─ 对于复杂方法（多分支/异常处理）可能只能部分还原

注意: VMP 还原通常需要数周甚至数月的逆向工作，且每个壳需要单独分析。
```

---

## 7. 反调试与绕过

### 7.1 ptrace 检测

```c
// APP 中的反调试代码（C层）
void anti_debug() {
    // 方法1: 自己 ptrace 自己
    // ptrace 返回 0 说明已经在被调试
    if (ptrace(PTRACE_TRACE, 0, 0, 0) < 0) {
        exit(0); // 正在被调试，退出
    }
}
```

```javascript
// Frida 绕过 ptrace 检测
var ptrace = Module.findExportByName("libc.so", "ptrace");
Interceptor.replace(ptrace, new NativeCallback(function(pid, req, addr, data) {
    console.log("[ptrace] 被调用，返回0绕过");
    return 0;
}, 'long', ['int', 'int', 'pointer', 'pointer']));
```

### 7.2 /proc/self/status 检测

```c
// 检测 TracerPid 字段是否非零
void check_tracer_pid() {
    FILE *f = fopen("/proc/self/status", "r");
    char line[256];
    while (fgets(line, sizeof(line), f)) {
        if (strncmp(line, "TracerPid:", 10) == 0) {
            int pid = atoi(line + 10);
            if (pid != 0) {
                exit(0); // 正在被调试
            }
        }
    }
}
```

```javascript
// Frida 绕过 TracerPid 检测
var fopen = Module.findExportByName("libc.so", "fopen");
var fgets = Module.findExportByName("libc.so", "fgets");

Interceptor.attach(fopen, {
    onEnter: function(args) {
        var path = args[0].readUtf8String();
        if (path && path.indexOf("/proc/") !== -1 && path.indexOf("status") !== -1) {
            this.isStatusFile = true;
        }
    }
});

Interceptor.attach(fgets, {
    onLeave: function(retval) {
        if (retval && !retval.isNull()) {
            var line = retval.readUtf8String();
            if (line && line.indexOf("TracerPid:") !== -1) {
                // 将 TracerPid 改为 0
                var modified = "TracerPid:\t0\n";
                retval.writeUtf8String(modified);
            }
        }
    }
});
```

### 7.3 SO 层反调试

常见 SO 层反调试手段：

| 检测方法 | 原理 | 绕过方式 |
|----------|------|----------|
| 检测调试器端口 | 扫描 /proc/net/tcp 查找调试器端口 | Hook 文件读取返回假数据 |
| 检测 frida 线程 | 遍历 /proc/self/task 查找 frida 线程名 | Hook open/read 对该路径返回假数据 |
| 检测 inotify | 通过 inotify 监控关键文件被读取 | Hook inotify_add_watch |
| 时间检测 | 检测函数执行时间异常（被 Hook 后变慢） | 优化 Hook 逻辑减少耗时 |
| 信号检测 | 发送 SIGTRAP 信号检测调试器 | Hook kill/sigaction |

### 7.4 Frida 检测与绕过

```javascript
// 绕过 Frida 检测的综合脚本

// 1. 绕过端口检测 (27042)
var read = Module.findExportByName("libc.so", "read");
Interceptor.attach(read, {
    onLeave: function(retval) {
        // 如果是读取 /proc/net/tcp 的结果
        // 过滤掉包含 27042 的行
    }
});

// 2. 绕过线程名检测 (gmain, gdbus, frida)
var pthread_getname = Module.findExportByName("libc.so", "pthread_getname_np");
Interceptor.replace(pthread_getname, new NativeCallback(function(thread, buf, len) {
    // 返回假线程名
    Memory.writeUtf8String(buf, "app_thread");
    return 0;
}, 'int', ['pointer', 'pointer', 'size_t']));

// 3. 绕过内存特征扫描 (搜索 "frida" "gadget" 字符串)
var memcmp = Module.findExportByName("libc.so", "memcmp");
Interceptor.attach(memcmp, {
    onEnter: function(args) {
        var data = args[1].readUtf8String(6);
        if (data === "frida-" || data === "gadget") {
            // 修改比较结果使其不匹配
            this.bypass = true;
        }
    },
    onLeave: function(retval) {
        if (this.bypass) {
            retval.replace(1); // 不匹配
        }
    }
});

// 4. 使用 frida-gadget 替代 frida-server（减少检测特征）
// 将 libfrida-gadget.so 打包进 APK 或使用 LD_PRELOAD

// 5. 修改 frida-server 监听端口
// adb shell "/data/local/tmp/frida-server -l 0.0.0.0:8888 &"
// frida -H 127.0.0.1:8888 -n com.example.app
```

---

## 8. 脱壳注意事项

### 8.1 法律合规边界

```
合法场景:
  ✓ 安全研究（个人学习/学术研究）
  ✓ 渗透测试（获得明确授权）
  ✓ 漏洞挖掘（安全应急响应）
  ✓ CTF 竞赛

非法场景:
  ✗ 未授权破解商业APP
  ✗ 去除付费验证逻辑
  ✗ 窃取/泄露商业代码
  ✗ 修改APP用于欺诈
```

### 8.2 脱壳环境搭建

推荐环境配置：

```
系统环境:
  - 脱壳专用 Android 设备（避免污染日常设备）
  - 推荐机型: Google Pixel 系列（AOSP 支持好）
  - Android 版本: 8.0 - 11（兼容性最佳）
  - 需 Root (Magisk)

工具链:
  - frida-server (对应 frida-tools 版本)
  - Python 3.8+ (frida-tools, frida-dexdump)
  - jadx / jadx-gui (反编译验证)
  - apktool (APK 解包)
  - IDA Pro (SO 库逆向，可选)
  - FART 定制 ROM (函数抽取壳)
  - BlackDex (一键脱壳)
```

### 8.3 实用工具清单

| 工具 | 用途 | 获取方式 |
|------|------|----------|
| **FRIDA-DEXDump** | 一代壳 DEX Dump | `pip install frida-dexdump` |
| **BlackDex** | 一代壳脱壳 | GitHub: AsLdf/BlackDex |
| **FART** | 函数抽取壳脱壳 | 需自行编译 AOSP 定制 ROM |
| **Youpk** | 高级脱壳 | GitHub: Youlor/Youpk |
| **DexExtractor** | 内存 DEX 提取 | 需 Frida 注入 |
| **jadx** | DEX 反编译 | `pip install jadx` |
| **apktool** | APK 解包/重打包 | `pip install apktool` |
| **Frida** | 动态 Hook | `pip install frida-tools` |
| **objection** | Frida 封装框架 | `pip install objection` |
| **IDA Pro** | SO 库逆向分析 | 商业软件 |
| **Ghidra** | SO 库逆向（免费替代） | NSA 开源 |
| **MT 管理器** | APK 编辑（移动端） | Android APK |

---

## 结语

Android 脱壳是移动安全研究中极具挑战性的领域。从一代壳的简单内存搜索到三代 VMP 的虚拟指令还原，难度呈指数级增长。实际工作中，建议按以下顺序提升能力：

1. 熟练使用 FRIDA-DEXDump / BlackDex 处理一代壳
2. 学习 FART 原理，理解函数抽取壳的主动调用策略
3. 深入理解 DEX 文件格式和 ART 虚拟机类加载机制
4. 尝试修改 AOSP 源码实现自定义脱壳方案
5. 面向 VMP 壳，积累 SO 库逆向经验

> **安全声明**：本文档仅供安全研究与教学使用。脱壳行为请在合法授权范围内进行，切勿用于未授权的商业逆向、破解付费功能或窃取知识产权。
