# iOS 应用安全检测要点

### 7.1 静态检测

#### 1. 二进制文件检测

| 检测项 | 说明 | 检测方法 |
|--------|------|---------|
| 代码签名 | 签名是否有效 | codesign -vvv |
| 权限配置 | entitlements 是否合理 | codesign -d --entitlements |
| PIE 保护 | 地址空间随机化 | otool -hv |
| Stack Canary | 栈保护 | otool -I \| grep stack_chk |
| ARC | 自动引用计数 | 查看编译标志 |
| 加密标志 | 是否加密（App Store 应用会加密） | otool -l \| grep cryptid |

**检测命令**：
```bash
# 查看 Mach-O 文件头信息（看 PIE）
otool -hv MyApp.app/MyApp

# 查看加密信息
otool -l MyApp.app/MyApp | grep -A 4 LC_ENCRYPTION_INFO

# 查看共享库依赖
otool -L MyApp.app/MyApp

# 查看签名信息
codesign -dvvv MyApp.app/MyApp

# 查看 entitlements
codesign -d --entitlements - MyApp.app/MyApp

# 导出头文件（class-dump）
class-dump MyApp.app/MyApp
```

#### 2. 资源文件检测

| 检测项 | 说明 |
|--------|------|
| Info.plist | 检查 ATS 配置、URL Scheme、权限声明 |
| 配置文件 | 检查是否有敏感配置（URL、密钥等） |
| 证书文件 | 检查是否包含敏感证书/密钥 |
| 数据库文件 | 检查 SQLite 数据库是否有敏感数据 |
| 网页资源 | HTML/JS 文件中是否有敏感信息 |

#### 3. 代码检测

**检测内容**：
- 硬编码的密钥、密码、URL
- 不安全的加密算法（MD5、SHA1、ECB 模式）
- 不安全的随机数生成（arc4random 是安全的，rand 不安全）
- 日志输出（NSLog 打印敏感信息）
- 越狱检测是否完善
- SSL Pinning 实现是否正确
- 数据存储是否使用 Keychain

### 7.2 动态检测

#### 1. 数据存储检测

| 检测项 | 检测方法 |
|--------|---------|
| UserDefaults | 查看 Library/Preferences/ 下的 plist 文件 |
| Keychain | 使用 Keychain 查看工具或 Frida Hook |
| 文件存储 | 浏览 Documents、Library、tmp 目录 |
| 数据库 | 检查 .db、.sqlite 文件 |
| 剪贴板 | 操作应用后检查剪贴板内容 |
| 键盘缓存 | 检查键盘的自动更正缓存 |

#### 2. 通信安全检测

| 检测项 | 检测方法 |
|--------|---------|
| 明文传输 | 使用 Charles/Burp 抓包，查看是否有 HTTP 明文 |
| 证书校验 | 使用自签名证书，看应用是否接受 |
| SSL Pinning | 安装系统 CA 证书，看能否抓包 |
| 弱加密算法 | 查看 TLS 版本和加密套件 |
| 敏感数据加密 | 传输的敏感数据是否额外加密 |

#### 3. 运行时安全检测

| 检测项 | 检测方法 |
|--------|---------|
| 越狱检测 | 在越狱设备上运行，看是否检测 |
| 调试检测 | 尝试用 LLDB 附加调试 |
| 完整性校验 | 修改应用文件，看能否运行 |
| 重签名检测 | 用其他证书重签，看能否正常运行 |
| Hook 检测 | 用 Frida 注入，看是否被检测 |
| 后台截图 | 按 Home 键，检查任务栏截图是否敏感 |

#### 4. 组件安全检测

**URL Scheme 测试**：
```bash
# 列出应用的 URL Scheme
# 查看 Info.plist 中的 CFBundleURLSchemes

# 测试调用
idevice-app-launch -u UDID --scheme myapp://test
```

**Universal Link 测试**：
- 测试 apple-app-site-association 文件
- 测试 Universal Link 的跳转逻辑
- 检查是否存在绕过可能

**App Extension 测试**：
- 检查共享数据容器
- 检查扩展与主应用的通信
- 测试扩展的权限边界

### 7.3 渗透测试工具

| 工具 | 用途 | 平台 |
|------|------|------|
| Frida | 动态插桩、Hook | macOS/Linux/Windows |
| class-dump | 导出头文件 | macOS |
| Hopper | 反汇编、反编译 | macOS |
| IDA Pro | 反汇编、反编译、调试 | 多平台 |
| Ghidra | 开源逆向工具 | 多平台 |
| Cycript | 动态调试 | iOS（Cydia） |
| LLDB | 调试器 | macOS/Xcode |
| Charles | HTTP/HTTPS 抓包 | 多平台 |
| Burp Suite | 抓包与渗透测试 | 多平台 |
| MobSF | 自动化移动安全测试 | 多平台 |
| objection | Frida 封装工具 | 多平台 |
| checkra1n | 越狱工具 | macOS/Linux |
| frida-ios-dump | 砸壳工具 | 多平台 |
| iProxy | 端口转发 | macOS/Linux |

### 7.4 安全测试流程

```
1. 信息收集
   ├── 获取 IPA 文件
   ├── 分析 Info.plist
   ├── 分析 URL Scheme
   ├── 分析 Frameworks
   └── 识别第三方 SDK

2. 静态分析
   ├── class-dump 导出头文件
   ├── Hopper/IDA 反编译
   ├── 搜索敏感字符串
   ├── 分析关键函数
   ├── 检查加密算法
   └── 检查数据存储

3. 动态分析（越狱设备）
   ├── 安装应用
   ├── Frida Hook 关键函数
   ├── 抓包分析通信
   ├── 浏览文件系统
   ├── 查看 Keychain 数据
   ├── 测试越狱检测
   └── 调试关键功能

4. 漏洞验证
   ├── 验证发现的问题
   ├── 构造 PoC
   ├── 评估风险等级
   └── 复现步骤

5. 报告编写
   ├── 漏洞描述
   ├── 风险等级
   ├── 复现步骤
   ├── 修复建议
   └── 证据截图
```

---

> 提示：iOS 安全研究门槛相对较高，需要 macOS 设备和一定的逆向基础。建议从基础的静态分析入手，逐步学习动态调试和漏洞挖掘。

---

## 📋 内容审核与补充建议

> 针对「iOS 应用安全检测要点」部分的内容审核结果：

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

---

## 📌 拓展学习资源

### 推荐学习路径
- 理论基础 → 工具实践 → 实战演练 → 深度研究
- 建议搭建本地实验环境进行动手练习

### 相关工具与资源
- 在线实验平台：Hack The Box、TryHackMe、VulnHub
- 技术文档：官方文档、RFC、OWASP 指南
- 社区资源：GitHub、安全论坛、技术博客
