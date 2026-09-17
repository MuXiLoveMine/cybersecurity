# APK 文件结构详解

### 4.1 APK 整体结构

APK（Android Package）本质上是一个 ZIP 格式的压缩包，可以直接用解压工具打开。

```
App.apk
├── AndroidManifest.xml      # 清单文件（二进制格式）
├── classes.dex              # Dalvik/ART 字节码（主 dex）
├── classes2.dex             # 多 dex 情况下的其他 dex
├── resources.arsc           # 资源索引表（二进制格式）
├── res/                     # 资源文件
│   ├── drawable/            # 图片资源
│   ├── layout/              # 布局文件（二进制 XML）
│   ├── values/              # 字符串、颜色、尺寸等
│   ├── mipmap-xxxhdpi/      # 图标资源
│   └── ...
├── lib/                     # Native 库
│   ├── armeabi-v7a/         # 32 位 ARM 架构
│   │   ├── libnative.so
│   │   └── libssl.so
│   ├── arm64-v8a/           # 64 位 ARM 架构
│   │   └── libnative.so
│   ├── x86/                 # 32 位 x86 架构
│   └── x86_64/              # 64 位 x86 架构
├── assets/                  # 资产文件（原始文件，不编译）
│   ├── config.json
│   ├── web/
│   └── ...
├── META-INF/                # 签名信息目录
│   ├── MANIFEST.MF          # 文件摘要清单
│   ├── CERT.SF              # 签名文件
│   └── CERT.RSA             # 签名证书（含公钥）
└── Kotlin/                  # Kotlin 元数据（Kotlin 应用才有）
```

### 4.2 各文件详细说明

#### AndroidManifest.xml
- **格式**：二进制 XML（AXML 格式）
- **内容**：应用包名、版本号、权限声明、四大组件声明、SDK 版本要求等
- **分析工具**：Apktool（反编译为文本 XML）、axmlprinter、AndroidManifest.xml 解析器

#### classes.dex
- **格式**：Dalvik Executable 格式
- **内容**：应用的 Java/Kotlin 代码编译后的 Dalvik 字节码
- **特点**：
  - 基于寄存器的虚拟机指令集（与 JVM 基于栈不同）
  - 多 dex 机制：方法数超过 65536 时会分包（classes2.dex、classes3.dex...）
- **分析工具**：JADX、JEB、IDA Pro、baksmali

#### resources.arsc
- **格式**：二进制资源表
- **内容**：所有资源的 ID 映射、字符串池、配置信息等
- **作用**：系统通过资源 ID 快速查找对应资源

#### res/ 目录
- **drawable/**：图片、形状等可绘制资源
- **layout/**：界面布局文件（二进制 XML）
- **values/**：字符串（strings.xml）、颜色（colors.xml）、尺寸（dimens.xml）等
- **mipmap-*/**：应用图标（不同分辨率）
- **xml/**：XML 配置文件（如文件路径配置、网络安全配置）
- **raw/**：原始资源文件（不编译，可通过 R.raw.xxx 访问）

#### lib/ 目录
- 存放不同 CPU 架构的 Native 动态库（.so 文件）
- 常见架构：armeabi-v7a、arm64-v8a、x86、x86_64
- 系统会根据设备架构自动选择对应目录的 so 文件
- 分析工具：IDA Pro、Ghidra、Hopper

#### assets/ 目录
- 存放原始资源文件，保持原样打包
- 不生成资源 ID，通过 AssetManager 访问
- 常用于存放 HTML、字体、配置文件、数据库文件等
- 路径遍历漏洞的高发区

#### META-INF/ 目录
- **MANIFEST.MF**：列出 APK 中所有文件的 SHA-1 摘要
- **CERT.SF**：对 MANIFEST.MF 的签名
- **CERT.RSA**：包含签名证书（公钥）和对 CERT.SF 的数字签名
- 注意：v2/v3 签名信息不在此目录中，而是在 APK 的签名块中

---

---

## 📋 内容审核与补充建议

> 针对「APK 文件结构详解」部分的内容审核结果：

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

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
