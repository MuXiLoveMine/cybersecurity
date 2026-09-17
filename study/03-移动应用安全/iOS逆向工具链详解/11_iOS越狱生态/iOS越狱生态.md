# iOS越狱生态

### 10.1 越狱工具

```bash
# checkra1n
# 基于checkm8漏洞的硬件级越狱
# 支持A7-A11芯片设备（iPhone 5s - iPhone X）
# 特点：tethered/semi-tethered，需要USB连接引导

# unc0ver
# 基于内核漏洞的越狱
# 支持iOS 11.0 - 14.3
# 特点：untethered，重启后保持越狱

# Taurine
# 吥德赛团队开发的越狱
# 支持iOS 14.0 - 14.3
# 特点：基于CVE-2021-1782内核漏洞

# Fugu
# 开源越狱工具
# 支持A12-A14设备
# 特点：基于CVE-2021-1782

# Palera1n
# 最新越狱工具
# 支持checkm8设备（A7-A11）
# 支持iOS 15+

# 越狱后安装常用工具
# Cydia/Sileo中安装：
# - OpenSSH (SSH连接)
# - Frida (动态分析)
# - Cycript (运行时分析)
# - adv-cmds (高级命令行工具)
# - wget/curl
# - vim/nano
# - class-dump (头文件提取)
# - Clutch (应用脱壳)
# - AppSync (安装未签名IPA)
# - AFC2 (文件系统访问)
# - Frida (动态注入)
```

### 10.2 包管理器

```
# Cydia - 经典越狱包管理器
# 由Saurik开发，是最早的越狱包管理器
# 软件源（常用）：
# - BigBoss (http://apt.bigboss.org)
# - ModMyi (http://apt.modmyi.com)
# - Saurik's Cydia (http://apt.saurik.com)

# Sileo - 新一代包管理器
# 由CoolStar团队开发
# 更快的包管理速度
# 支持现代iOS版本
# 软件源与Cydia兼容

# Zebra - 轻量级包管理器
# 开源项目
# 支持Cydia和Sileo源
# 更好的性能

# 安装Tweak
# 1. 在包管理器中搜索Tweak
# 2. 点击安装
# 3. 注销（Respring）或重启SpringBoard
# 4. Tweak自动加载

# 常用Tweak源
# - https://repo.chariz.com (Chariz)
# - https://repo.dynastic.co (Dynastic)
# - https://apt.bingner.com (Bingner)
# - https://repo.packix.com (Packix)

# Tweak管理
# 使用iCleaner Pro管理已安装Tweak
# 排查冲突时选择性禁用Tweak
```

---

---

## 📋 内容审核与补充建议

> 针对「iOS越狱生态」部分的内容审核结果：

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
