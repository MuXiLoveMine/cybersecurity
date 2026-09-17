# APK 反编译流程

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

---

## 📋 内容审核与补充建议

> 针对「APK 反编译流程」部分的内容审核结果：

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

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
