# 威胁情报平台（TIP）

### 1.1 TIP 概述

**威胁情报平台（Threat Intelligence Platform，TIP）** 是用于收集、处理、分析、管理和分发威胁情报的软件平台。

**TIP 的核心功能：**
- 情报收集：从多种来源收集威胁情报
- 情报处理：标准化、去重、丰富化
- 情报分析：关联分析、聚类分析、归因分析
- 情报管理：存储、检索、分类、标签
- 情报分发：API、导出、推送
- 情报应用：与其他安全工具集成

### 1.2 TIP 的核心能力

#### 1.2.1 多源情报汇聚
- 支持多种情报格式（STIX、OpenIOC、CSV、JSON 等）
- 支持多种情报来源（商业、开源、政府、内部）
- 自动采集和手动导入
- 情报源管理和质量评估

#### 1.2.2 情报处理与丰富化
- 数据标准化（统一格式和字段）
- 去重合并（同一指标多个来源）
- 数据丰富化（补充上下文信息）
- 置信度评分
- 过期管理（IOC 生命周期管理）

#### 1.2.3 情报分析
- IOC 关联分析
- TTP 分析
- 攻击者画像
- 攻击活动追踪
- 趋势分析
- 可视化分析

#### 1.2.4 情报共享与协作
- 情报共享（组织内部、行业间）
- 协作分析（多人协作）
- 情报社区
- 工作流管理

#### 1.2.5 集成与分发
- RESTful API
- 与 SIEM/EDR/SOAR 集成
- 多种格式导出
- 告警和通知

### 1.3 常见 TIP 产品

#### 1.3.1 开源 TIP

| 产品 | 开发者 | 特点 |
|------|--------|------|
| **MISP** | MISP Project | 最流行的开源威胁情报平台，功能强大，社区活跃 |
| **OpenCTI** | Filigran | 现代化的开源威胁情报平台，图形化好，支持 STIX 2 |
| **YETI** | CERT Polska | 你的日常威胁情报平台，轻量级 |
| **Cortex** | TheHive Project | 可观测性分析引擎，与 TheHive 配合 |
| **TheHive** | TheHive Project | 安全事件响应平台，与 MISP 集成 |

#### 1.3.2 商业 TIP

| 产品 | 厂商 | 特点 |
|------|------|------|
| **微步在线 TIP** | 微步在线 | 国内领先的威胁情报平台 |
| **奇安信威胁情报平台** | 奇安信 | 国内主流威胁情报平台 |
| **Recorded Future** | Recorded Future | 国际领先，AI 驱动 |
| **ThreatConnect** | ThreatConnect | 综合威胁情报平台 |
| **Anomali ThreatStream** | Anomali | 威胁情报管理平台 |
| **LookingGlass** | LookingGlass | 威胁情报解决方案 |
| **Flashpoint** | Flashpoint | 商业情报和暗网监控 |
| **Digital Shadows** | Digital Shadows | 数字风险保护 |
| **IBM X-Force Exchange** | IBM | IBM 威胁情报平台 |

### 1.4 MISP 实战入门

MISP（Malware Information Sharing Platform）是最流行的开源威胁情报平台。

#### 1.4.1 MISP 核心概念

| 概念 | 说明 |
|------|------|
| **Event（事件）** | 情报事件，包含一组相关的属性和对象 |
| **Attribute（属性）** | 单个 IOC 指标（IP、域名、哈希等） |
| **Object（对象）** | 一组相关的属性（如文件对象包含文件名、哈希、大小等） |
| **Tag（标签）** | 用于分类和标记（如 tlp:white, malware:botnet） |
| **Taxonomy（分类法）** | 标准化的标签体系（如 TLP、MITRE ATT&CK） |
| **Galaxy（星系）** | 知识库（如攻击者、攻击工具、漏洞等） |
| **Feed（源）** | 情报来源，可以订阅 |

#### 1.4.2 MISP 基本操作

**1. 创建事件**
```
事件信息：
- 信息（Info）：事件标题/描述
- 分布（Distribution）：共享范围
  - 你的组织仅
  - 此社区仅
  - 连接社区
  - 所有社区
- 威胁级别（Threat Level）：
  - 低
  - 中
  - 高
  - 未定义
- 分析（Analysis）：
  - 初始
  - 进行中
  - 完成
- TLP 标签：TLP:WHITE / TLP:GREEN / TLP:AMBER / TLP:RED
```

**2. 添加属性**
```
属性类型：
- ip-dst / ip-src：目的/源 IP
- domain / hostname：域名/主机名
- url：URL
- md5 / sha1 / sha256：文件哈希
- filename：文件名
- regkey：注册表键
- mutex：互斥量
- email-src / email-dst：邮件地址
- etc.

属性类别：
- 内部参考
- 目标
- 恶意工件
- 其他
- 攻击者工具
- 攻击模式
- 受害者身份
- 支持基础设施
- 社会工程
```

**3. 使用标签**
```
常用标签体系：
- TLP（Traffic Light Protocol）：流量灯协议，控制共享范围
  - TLP:WHITE - 无限共享
  - TLP:GREEN - 社区内共享
  - TLP:AMBER - 受限共享
  - TLP:RED - 不能共享
- MITRE ATT&CK：攻击技术标签
- 恶意软件家族标签
- 攻击者标签
- 行业标签
```

#### 1.4.3 MISP 情报共享

**共享方式：**
1. **同步（Synchronisation）**
   - 两个 MISP 实例之间互相同步
   - 推/拉模式
   - 支持过滤（按标签、组织等）

2. **Feeds（情报源）**
   - 订阅外部情报源
   - 支持 MISP 格式、Freetext、CSV 等
   - 定期自动拉取

3. **导出**
   - 导出为多种格式：STIX、JSON、CSV、OpenIOC 等
   - API 接口
   - 自定义导出模板

### 1.5 TIP 部署建议

#### 1.5.1 小型组织
- 使用 MISP 或 OpenCTI 开源平台
- 接入 2-3 个开源情报源
- 1-2 人负责维护
- 重点关注 IOC 类情报

#### 1.5.2 中型组织
- 开源 TIP + 商业情报源
- 或直接使用商业 TIP
- 专门的威胁情报团队
- 与 SIEM/EDR 集成
- 覆盖 IOC、TTP 等多种情报

#### 1.5.3 大型组织
- 商业 TIP 平台
- 多种商业情报源
- 完整的威胁情报团队
- 情报驱动安全运营
- 参与情报共享社区
- 威胁狩猎和深度分析

---

---

