# WiFi 安全

### 3.1 WiFi 加密体系

WiFi 安全经历了从 WEP 到 WPA3 的演进过程：

```
WiFi 安全协议演进：

WEP (1997)
├── 使用 RC4 流密码
├── 40/104 位密钥
├── 严重安全漏洞，几分钟内可破解
└── 已被废弃，但仍可见于老旧设备

WPA (2003)
├── 临时方案，兼容 WEP 硬件
├── 使用 TKIP 加密
├── 引入了 MIC 防篡改
└── 存在 TKIP 注入漏洞

WPA2 (2004)
├── 使用 AES-CCMP 加密
├── 四次握手认证
├── KRACK 攻击暴露协议缺陷
└── 当前最广泛部署的协议

WPA3 (2018)
├── 使用 SAE 替代 PSK
├── 前向保密
├── 抗离线字典攻击
└── 分为 Personal 和 Enterprise 版本
```

### 3.2 认证流程

WiFi 认证流程涉及多个阶段：

```
WiFi 连接完整流程：

1. 扫描阶段
   ├── 主动扫描：Station 发送 Probe Request
   └── 被动扫描：Station 监听 Beacon 帧

2. 认证阶段（Open System / Shared Key）
   ├── Station -> AP: Authentication Request
   └── AP -> Station: Authentication Response

3. 关联阶段
   ├── Station -> AP: Association Request
   └── AP -> Station: Association Response

4. 密钥协商阶段（WPA/WPA2/WPA3）
   ├── WPA2: 四次握手（4-Way Handshake）
   └── WPA3: SAE 握手

5. 数据传输阶段
   └── 使用协商的密钥加密数据帧
```

---

---

## 📋 内容审核与补充建议

> 针对「WiFi 安全」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

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
