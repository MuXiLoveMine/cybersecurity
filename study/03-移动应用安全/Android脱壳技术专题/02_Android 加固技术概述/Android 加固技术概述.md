# Android 加固技术概述

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

---

## 📋 内容审核与补充建议

> 针对「Android 加固技术概述」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 📖 参考资料
- ⚠️ 缺少参考资料/延伸阅读

---

## 📌 拓展学习资源

### 推荐学习路径
- 理论基础 → 工具实践 → 实战演练 → 深度研究
- 建议搭建本地实验环境进行动手练习

### 相关工具与资源
- 在线实验平台：Hack The Box、TryHackMe、VulnHub
- 技术文档：官方文档、RFC、OWASP 指南
- 社区资源：GitHub、安全论坛、技术博客
