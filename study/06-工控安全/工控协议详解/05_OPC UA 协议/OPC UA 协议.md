# OPC UA 协议

### 5.1 OPC UA 概述

OPC UA（Open Platform Communications Unified Architecture，开放平台通信统一架构）是 OPC 基金会推出的新一代工业通信标准，是 OPC 经典（DA/AE/HDA）的继承者。

**与经典 OPC 的区别：**

| 特性 | 经典 OPC (DA/AE/HDA) | OPC UA |
|------|----------------------|--------|
| 平台依赖 | Windows 平台（依赖 COM/DCOM） | 跨平台（Windows/Linux/嵌入式） |
| 安全机制 | 依赖 DCOM 安全，很弱 | 内置安全机制（认证/加密/签名） |
| 数据模型 | 简单的标签-值模型 | 丰富的面向对象模型 |
| 通信方式 | COM/DCOM | TCP/HTTP/HTTPS 多种传输 |
| 防火墙友好 | 不友好（DCOM 端口动态） | 友好（固定端口） |
| 互操作性 | 较差 | 标准化程度高 |

**OPC UA 的核心优势：**
- 平台无关性
- 内置安全机制
- 统一的数据模型
- 支持多种传输协议
- 面向服务的架构

### 5.2 OPC UA 架构

```
┌─────────────────────────────────────────┐
│           OPC UA 应用层                 │
│  数据访问 / 报警事件 / 历史数据 / 方法  │
├─────────────────────────────────────────┤
│           OPC UA 服务层                 │
│  会话服务 / 节点管理 / 订阅服务         │
├─────────────────────────────────────────┤
│           OPC UA 通信层                 │
│  UA TCP / UA HTTPS / UA WebSocket      │
├─────────────────────────────────────────┤
│           传输层 (TCP / HTTPS)          │
└─────────────────────────────────────────┘
```

### 5.3 OPC UA 安全模型

OPC UA 定义了完整的安全模型，包括：

**安全策略（Security Policy）：**
| 安全策略 | 说明 |
|----------|------|
| None | 无安全（明文，无认证） |
| Basic128Rsa15 | 基本安全（RSA-15 密钥，128位加密） |
| Basic256 | 256位加密 |
| Basic256Sha256 | SHA-256 哈希 + 256位加密 |
| Aes128_Sha256_RsaOaep | AES-128 + SHA-256 + RSA-OAEP |
| Aes256_Sha256_RsaPss | AES-256 + SHA-256 + RSA-PSS |

**安全模式（Security Mode）：**
- `None`：无安全
- `Sign`：仅签名（验证完整性和身份）
- `SignAndEncrypt`：签名并加密（最安全）

**用户认证方式：**
- 匿名（Anonymous）
- 用户名/密码（Username/Password）
- X.509 证书
- 颁发的令牌（如 JWT）

### 5.4 OPC UA 地址空间模型

OPC UA 使用节点（Node）和引用（Reference）构建地址空间：

```
对象 (Object)
  ├── 变量 (Variable) → 数据值
  ├── 方法 (Method)   → 可调用的函数
  ├── 对象 (Object)   → 子对象
  └── ...

节点属性：
  - NodeId: 节点唯一标识
  - NodeClass: 节点类型（对象/变量/方法/视图等）
  - BrowseName: 浏览名称
  - DisplayName: 显示名称
  - Description: 描述
  - Value: 值（仅变量节点）
  - DataType: 数据类型
```

### 5.5 OPC UA 服务

OPC UA 定义了丰富的服务集：

| 服务集 | 主要服务 | 说明 |
|--------|---------|------|
| 发现服务 | FindServers, GetEndpoints | 发现服务器和端点 |
| 会话服务 | CreateSession, ActivateSession | 创建和激活会话 |
| 节点管理 | Browse, Read, Write | 浏览和读写节点 |
| 订阅服务 | CreateSubscription, Publish | 数据订阅和发布 |
| 监控项 | CreateMonitoredItems | 监控数据变化 |
| 方法服务 | Call | 调用方法 |
| 历史数据 | HistoryRead, HistoryUpdate | 读写历史数据 |
| 报警事件 | EventSubscription, Condition | 事件和报警 |

### 5.6 OPC UA 安全风险

**1. 配置不当风险**
- 很多部署使用默认配置（无安全模式）
- 管理员安全意识不足
- 证书管理不当

**2. 匿名访问风险**
- 启用匿名访问
- 攻击者可直接读取所有数据
- 可调用敏感方法

**3. 证书漏洞**
- 自签名证书未验证
- 过期证书继续使用
- 私钥泄露

**4. 已知漏洞**
- OPC UA 实现库的漏洞
- 栈溢出、空指针引用
- 认证绕过漏洞

**5. 横向移动风险**
- OPC UA 服务器连接多个 PLC
- 攻破 OPC UA 服务器即可控制大量设备
- 作为横向移动的跳板

---

---

## 📋 内容审核与补充建议

> 针对「OPC UA 协议」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

---

## 📌 拓展学习资源

### 推荐学习路径
- 理论基础 → 工具实践 → 实战演练 → 深度研究
- 建议搭建本地实验环境进行动手练习

### 相关工具与资源
- 在线实验平台：Hack The Box、TryHackMe、VulnHub
- 技术文档：官方文档、RFC、OWASP 指南
- 社区资源：GitHub、安全论坛、技术博客
