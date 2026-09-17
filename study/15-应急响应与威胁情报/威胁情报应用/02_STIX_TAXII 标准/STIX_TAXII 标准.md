# STIX/TAXII 标准

### 2.1 为什么需要标准化

**问题：**
- 威胁情报格式不统一
- 不同厂商的情报格式不同
- 难以在不同系统间交换情报
- 集成成本高

**解决方案：标准化**
- STIX：结构化威胁信息表达（数据格式标准）
- TAXII：威胁情报自动交换（传输协议标准）
- 两者配合，实现威胁情报的标准化生产和交换

### 2.2 STIX 详解

#### 2.2.1 STIX 概述

**STIX**（Structured Threat Information Expression）是一种标准化的语言，用于表示和交换威胁情报信息。

**STIX 的目标：**
- 标准化威胁情报的表示方式
- 实现不同系统间的情报交换
- 支持自动化处理和分析
- 社区协作开发

**STIX 版本：**
- STIX 1.x：基于 XML
- STIX 2.x：基于 JSON（更现代，更易用）
- 当前主流版本：STIX 2.1

#### 2.2.2 STIX 核心对象

STIX 2 定义了多种 SDO（STIX Domain Object，STIX 域对象）：

| 对象类型 | 名称 | 说明 |
|----------|------|------|
| **Attack Pattern** | 攻击模式 | 描述攻击的技术和方法（对应 ATT&CK 技术） |
| **Campaign** | 战役 | 描述一组有组织的攻击活动 |
| **Course of Action** | 行动方案 | 描述防御和响应措施 |
| **Identity** | 身份 | 描述个人、组织、系统等身份 |
| **Indicator** | 指标 | IOC，用于检测攻击的模式 |
| **Infrastructure** | 基础设施 | 攻击者使用的基础设施（IP、域名、服务器等） |
| **Intrusion Set** | 入侵集 | 攻击者组织及其活动（对应 APT 组织） |
| **Malware** | 恶意软件 | 描述恶意软件家族 |
| **Malware Analysis** | 恶意软件分析 | 恶意软件分析结果 |
| **Observed Data** | 观测数据 | 观察到的数据和统计 |
| **Report** | 报告 | 威胁情报报告 |
| **Threat Actor** | 威胁行为体 | 攻击者/组织 |
| **Tool** | 工具 | 攻击工具（包括恶意和合法工具） |
| **Vulnerability** | 漏洞 | 安全漏洞 |
| **Location** | 位置 | 地理位置 |
| **Opinion** | 观点 | 对情报的评估和观点 |
| **Note** | 注释 | 附加说明和注释 |

#### 2.2.3 STIX 关系（SRO）

除了域对象，STIX 还有 SRO（STIX Relationship Object，STIX 关系对象），用于描述对象之间的关系。

**常见关系类型：**
- `indicates`：指示（指标 → 攻击模式/恶意软件/威胁行为体）
- `uses`：使用（威胁行为体/入侵集 → 攻击模式/工具/恶意软件/基础设施）
- `targets`：针对（威胁行为体/入侵集/恶意软件 → 身份/漏洞）
- `mitigates`：缓解（行动方案 → 攻击模式/漏洞/恶意软件）
- `attributed-to`：归因于（入侵集 → 威胁行为体）
- `compromises`：攻陷（基础设施 → 身份）
- `delivers`：投递（基础设施 → 恶意软件）
- `has`：拥有（威胁行为体 → 基础设施）
- `variants-of`：变种（恶意软件 → 恶意软件）

#### 2.2.4 STIX 示例

一个简单的 STIX 2 Indicator 对象示例：

```json
{
  "type": "indicator",
  "spec_version": "2.1",
  "id": "indicator--8e2e2d2b-17d4-4cbf-938f-98ee46b3cd3f",
  "created": "2024-01-01T00:00:00.000Z",
  "modified": "2024-01-01T00:00:00.000Z",
  "name": "恶意 IP 指示器",
  "description": "已知的 C2 服务器 IP 地址",
  "pattern": "[ipv4-addr:value = '192.168.1.100']",
  "pattern_type": "stix",
  "pattern_version": "2.1",
  "valid_from": "2024-01-01T00:00:00.000Z",
  "valid_until": "2024-03-01T00:00:00.000Z",
  "labels": ["malicious-activity", "c2"]
}
```

一个威胁行为体对象示例：

```json
{
  "type": "threat-actor",
  "spec_version": "2.1",
  "id": "threat-actor--8e2e2d2b-17d4-4cbf-938f-98ee46b3cd3f",
  "created": "2024-01-01T00:00:00.000Z",
  "modified": "2024-01-01T00:00:00.000Z",
  "name": "APT-XX",
  "description": "APT-XX 是一个国家级攻击组织，主要针对政府和国防工业目标",
  "threat_actor_types": ["nation-state"],
  "aliases": ["Group X", "Advanced Panda"],
  "first_seen": "2015-01-01T00:00:00.000Z",
  "last_seen": "2024-01-15T00:00:00.000Z",
  "roles": ["attacker", "sponsor"],
  "goals": ["窃取机密信息", "获取军事技术"],
  "sophistication": "expert",
  "resource_level": "government",
  "primary_motivation": "espionage",
  "labels": ["nation-state", "apt"]
}
```

### 2.3 TAXII 详解

#### 2.3.1 TAXII 概述

**TAXII**（Trusted Automated Exchange of Intelligence Information）是一种应用层协议，用于在组织之间安全地自动交换威胁情报。

**TAXII 的作用：**
- 定义威胁情报的传输方式
- 支持安全的情报共享
- 支持推送和拉取两种模式
- 与 STIX 配合使用（TAXII 传输 STIX 数据）

**TAXII 版本：**
- TAXII 1.x：基于 XML/HTTP
- TAXII 2.x：基于 REST/JSON（更现代）
- 当前主流：TAXII 2.1

#### 2.3.2 TAXII 核心概念

| 概念 | 说明 |
|------|------|
| **TAXII Server** | TAXII 服务器，提供情报共享服务 |
| **TAXII Client** | TAXII 客户端，连接服务器获取情报 |
| **API Root** | API 根路径，一个服务器可以有多个 API Root |
| **Collection** | 集合，一组相关的情报对象 |
| **Channel** | 通道（TAXII 2.1 新增，用于发布/订阅） |

#### 2.3.3 TAXII 服务类型

**1. 集合（Collections）**
- 服务器管理多个情报集合
- 客户端可以浏览和查询集合
- 类似图书馆的分类

**2. 发现（Discovery）**
- 客户端发现服务器的能力
- 获取 API Root 列表
- 获取可用集合列表

**3. 轮询（Polling）**
- 客户端从服务器拉取情报
- 支持增量拉取（只获取新的/修改的）
- 支持过滤（按类型、时间、标签等）

**4. 收件箱（Inbox）**
- 客户端向服务器推送情报
- 支持提交新的情报
- 类似邮件收件箱

#### 2.3.4 TAXII 2.x API 示例

```
# 发现 API Root
GET /taxii2/

# 获取集合列表
GET /api-root/collections/

# 获取集合中的对象
GET /api-root/collections/{collection_id}/objects/

# 获取单个对象
GET /api-root/collections/{collection_id}/objects/{object_id}

# 添加对象
POST /api-root/collections/{collection_id}/objects/

# 按时间范围查询
GET /api-root/collections/{collection_id}/objects/?added_after=2024-01-01T00:00:00.000Z

# 按类型过滤
GET /api-root/collections/{collection_id}/objects/?match[type]=indicator
```

### 2.4 STIX/TAXII 的意义

1. **互操作性**
   - 不同厂商的产品可以互相交换情报
   - 降低集成成本
   - 用户可以自由选择产品

2. **自动化**
   - 机器可读，支持自动化处理
   - 情报可以自动导入检测设备
   - 减少人工操作

3. **标准化**
   - 统一的概念和术语
   - 便于交流和共享
   - 促进行业发展

4. **生态系统**
   - 促进威胁情报生态系统的发展
   - 更多的参与者
   - 更多的情报源和工具

---

---

## 📋 内容审核与补充建议

> 针对「STIX/TAXII 标准」部分的内容审核结果：

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
