# STIX 2.1标准详解

### 3.1 STIX概述

**STIX**（Structured Threat Information eXpression）是一种用于交换网络威胁情报信息的语言和序列化格式。STIX 2.1是当前最新稳定版本（2022年正式发布）。

**STIX 2.1核心特性：**
- 使用JSON格式表示
- 基于对象模型的标准化结构
- 支持丰富的关系建模
- 可扩展的自定义对象
- 与TAXII协议配合使用

### 3.2 STIX对象模型

STIX 2.1定义了四类对象：

```
┌──────────────────────────────────────────────────────────┐
│                  STIX 2.1 对象模型                        │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────┐  ┌──────────────────┐            │
│  │ SDO (域对象)      │  │ SCO (网络对象)     │            │
│  │ Domain Object     │  │ Cyber Observable  │            │
│  │                    │  │ Object             │            │
│  │ - Attack Pattern  │  │ - IP Address      │            │
│  │ - Campaign         │  │ - Domain Name     │            │
│  │ - Course of Action│  │ - File             │            │
│  │ - Identity         │  │ - URL              │            │
│  │ - Indicator        │  │ - Email Address    │            │
│  │ - Intrusion Set    │  │ - Artifact         │            │
│  │ - Malware          │  │ - Process           │            │
│  │ - Observed Data    │  │ - ...              │            │
│  │ - Threat Actor     │  └──────────────────┘            │
│  │ - Tool             │                                   │
│  │ - Vulnerability    │  ┌──────────────────┐            │
│  └──────────────────┘  │ SRO (关系对象)      │            │
│                        │ Relationship Object│            │
│  ┌──────────────────┐  │                    │            │
│  │ SMO (元对象)      │  │ - Relationship    │            │
│  │ Meta Object       │  │ - Sighting        │            │
│  │                    │  └──────────────────┘            │
│  │ - Marking          │                                   │
│  │   Definition      │                                   │
│  │ - Extension        │                                   │
│  │ - Language         │                                   │
│  │   Content          │                                   │
│  └──────────────────┘                                   │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### 3.3 STIX通用属性

所有STIX对象都包含以下通用属性：

| 属性 | 类型 | 必填 | 说明 |
|------|------|------|------|
| type | string | 是 | 对象类型（如"indicator"） |
| spec_version | string | 是 | STIX版本（"2.1"） |
| id | string | 是 | 唯一标识符 (UUID v4 + 类型) |
| created | timestamp | 是 | 创建时间 |
| modified | timestamp | 是 | 最后修改时间 |
| created_by_ref | string | 否 | 创建者引用 |
| revoked | boolean | 否 | 是否撤销 |
| labels | string list | 否 | 标签 |
| confidence | integer | 否 | 置信度(0-100) |
| lang | string | 否 | 语言 |
| object_marking_refs | string list | 否 | 标记定义引用 |
| extensions | object | 否 | 扩展属性 |

### 3.4 核心域对象（SDO）详解

#### 3.4.1 Attack Pattern（攻击模式）

```json
{
  "type": "attack-pattern",
  "spec_version": "2.1",
  "id": "attack-pattern--0d0bf24e-5542-4d5e-a97a-123456789abc",
  "created": "2024-01-15T08:00:00.000Z",
  "modified": "2024-01-15T08:00:00.000Z",
  "name": "Spear Phishing Attachment",
  "description": "攻击者发送带有恶意附件的定向钓鱼邮件",
  "external_references": [
    {
      "source_name": "mitre-attack",
      "external_id": "T1566.001",
      "url": "https://attack.mitre.org/techniques/T1566/001"
    }
  ],
  "kill_chain_phases": [
    {
      "kill_chain_name": "lockheed-martin-cyber-kill-chain",
      "phase_name": "delivery"
    }
  ]
}
```

#### 3.4.2 Campaign（攻击活动）

```json
{
  "type": "campaign",
  "spec_version": "2.1",
  "id": "campaign--a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "created": "2024-01-20T10:00:00.000Z",
  "modified": "2024-01-20T10:00:00.000Z",
  "name": "Operation Night Dragon",
  "description": "针对能源行业的APT攻击活动",
  "first_seen": "2024-01-01T00:00:00Z",
  "last_seen": "2024-01-15T23:59:59Z",
  "objective": "窃取能源行业知识产权",
  "aliases": ["NightDragon", "OperationNA"]
}
```

#### 3.4.3 Course of Action（应对措施）

```json
{
  "type": "course-of-action",
  "spec_version": "2.1",
  "id": "course-of-action--b3c4d5e6-f7a8-9012-bcde-f23456789012",
  "created": "2024-01-15T08:00:00.000Z",
  "modified": "2024-01-15T08:00:00.000Z",
  "name": "Block Phishing Domains",
  "description": "在网络防火墙和邮件网关上封禁已知钓鱼域名",
  "action": "block",
  "external_references": [
    {
      "source_name": "mitre-attack",
      "external_id": "T1566.001"
    }
  ]
}
```

#### 3.4.4 Identity（身份）

```json
{
  "type": "identity",
  "spec_version": "2.1",
  "id": "identity--c5cb6e89-4c4d-4e97-8c1e-123456789abc",
  "created": "2024-01-01T00:00:00.000Z",
  "modified": "2024-01-01T00:00:00.000Z",
  "name": "Security Team Alpha",
  "description": "企业内部安全团队",
  "identity_class": "organization",
  "sectors": ["technology"],
  "contact_information": "security@example.com"
}
```

#### 3.4.5 Indicator（指标）

```json
{
  "type": "indicator",
  "spec_version": "2.1",
  "id": "indicator--d4e5f6a7-b8c9-0123-def0-456789abcdef",
  "created": "2024-01-15T08:00:00.000Z",
  "modified": "2024-01-15T08:00:00.000Z",
  "name": "Malicious IP - Known C2 Server",
  "description": "已知APT组织的C2服务器IP地址",
  "indicator_types": ["malicious-activity"],
  "pattern": "[ipv4-addr:value = '185.220.101.45']",
  "pattern_type": "stix",
  "valid_from": "2024-01-15T08:00:00Z",
  "valid_until": "2024-04-15T08:00:00Z",
  "confidence": 85
}
```

#### 3.4.6 Intrusion Set（入侵集合）

```json
{
  "type": "intrusion-set",
  "spec_version": "2.1",
  "id": "intrusion-set--e5f6a7b8-c9d0-1234-ef01-567890abcdef0",
  "created": "2024-01-01T00:00:00.000Z",
  "modified": "2024-01-15T10:00:00.000Z",
  "name": "APT28",
  "description": "与俄罗斯情报机构相关的APT组织",
  "first_seen": "2007-01-01T00:00:00Z",
  "last_seen": "2024-01-10T00:00:00Z",
  "goals": ["intelligence-collection", "espionage"],
  "primary_motivation": "dominance",
  "secondary_motivations": ["ideology"],
  "aliases": ["Fancy Bear", "Sofacy", "STRONTIUM", "Forest Blizzard"],
  "external_references": [
    {
      "source_name": "mitre-attack",
      "external_id": "G0007",
      "url": "https://attack.mitre.org/groups/G0007"
    }
  ]
}
```

#### 3.4.7 Malware（恶意软件）

```json
{
  "type": "malware",
  "spec_version": "2.1",
  "id": "malware--f6a7b8c9-d0e1-2345-fa01-67890abcdef01",
  "created": "2024-01-10T12:00:00.000Z",
  "modified": "2024-01-10T12:00:00.000Z",
  "name": "Cobalt Strike Beacon",
  "description": "Cobalt Strike框架的信标组件，用于C2通信",
  "malware_types": ["remote-access-trojan", "tool"],
  "is_family": false,
  "first_seen": "2024-01-01T00:00:00Z",
  "last_seen": "2024-01-10T00:00:00Z",
  "operating_system_refs": [],
  "architecture_execution_envs": ["windows-x86", "windows-x64"],
  "implementation_languages": ["C++"],
  "kill_chain_phases": [
    {
      "kill_chain_name": "lockheed-martin-cyber-kill-chain",
      "phase_name": "command-and-control"
    }
  ]
}
```

#### 3.4.8 Observed Data（观测数据）

```json
{
  "type": "observed-data",
  "spec_version": "2.1",
  "id": "observed-data--a7b8c9d0-e1f2-3456-ab01-7890abcdef0123",
  "created": "2024-01-15T14:00:00.000Z",
  "modified": "2024-01-15T14:00:00.000Z",
  "first_observed": "2024-01-15T13:45:00Z",
  "last_observed": "2024-01-15T13:50:00Z",
  "number_observed": 15,
  "objects": {
    "0": {
      "type": "ipv4-addr",
      "value": "192.168.1.100"
    },
    "1": {
      "type": "domain-name",
      "value": "c2.evil.com"
    },
    "2": {
      "type": "file",
      "name": "malware.exe",
      "hashes": {
        "SHA-256": "e3b0c44298fc1c149afbf4c8996fb924..."
      }
    }
  }
}
```

#### 3.4.9 Threat Actor（威胁行为者）

```json
{
  "type": "threat-actor",
  "spec_version": "2.1",
  "id": "threat-actor--b8c9d0e1-f2a3-4567-bc01-890abcdef01234",
  "created": "2024-01-01T00:00:00.000Z",
  "modified": "2024-01-15T12:00:00.000Z",
  "name": "Evil Corp Operator",
  "description": "针对金融机构的勒索软件运营者",
  "threat_actor_types": ["criminal"],
  "first_seen": "2023-06-01T00:00:00Z",
  "last_seen": "2024-01-10T00:00:00Z",
  "goals": ["financial-fraud", "steal-damage"],
  "primary_motivation": "personal-gain",
  "roles": ["malware-author", "operator"],
  "sophistication": "expert",
  "aliases": ["ECOperator"]
}
```

#### 3.4.10 Tool（工具）

```json
{
  "type": "tool",
  "spec_version": "2.1",
  "id": "tool--c9d0e1f2-a3b4-5678-cd01-90abcdef012345",
  "created": "2024-01-01T00:00:00.000Z",
  "modified": "2024-01-01T00:00:00.000Z",
  "name": "Mimikatz",
  "description": "Windows凭据提取工具",
  "tool_types": ["credential-theft", "credential-exploitation"],
  "external_references": [
    {
      "source_name": "mitre-attack",
      "external_id": "S0002",
      "url": "https://attack.mitre.org/software/S0002"
    }
  ],
  "kill_chain_phases": [
    {
      "kill_chain_name": "lockheed-martin-cyber-kill-chain",
      "phase_name": "credential-access"
    }
  ]
}
```

#### 3.4.11 Vulnerability（漏洞）

```json
{
  "type": "vulnerability",
  "spec_version": "2.1",
  "id": "vulnerability--d0e1f2a3-b4c5-6789-de01-0abcdef0123456",
  "created": "2024-01-01T00:00:00.000Z",
  "modified": "2024-01-01T00:00:00.000Z",
  "name": "CVE-2024-12345",
  "description": "远程代码执行漏洞，影响Apache Log4j 2.x",
  "external_references": [
    {
      "source_name": "cve",
      "external_id": "CVE-2024-12345",
      "url": "https://nvd.nist.gov/vuln/detail/CVE-2024-12345"
    }
  ]
}
```

### 3.5 关系对象（SRO）

#### 3.5.1 Relationship（关系）

STIX关系对象描述两个对象之间的语义关系。

```json
{
  "type": "relationship",
  "spec_version": "2.1",
  "id": "relationship--e1f2a3b4-c5d6-7890-ef01-abcdef01234567",
  "created": "2024-01-15T08:00:00.000Z",
  "modified": "2024-01-15T08:00:00.000Z",
  "relationship_type": "indicates",
  "source_ref": "indicator--d4e5f6a7-b8c9-0123-def0-456789abcdef",
  "target_ref": "intrusion-set--e5f6a7b8-c9d0-1234-ef01-567890abcdef0",
  "description": "该IP指标指向APT28组织的C2基础设施"
}
```

**常见关系类型：**

| 关系类型 | 说明 | 示例 |
|----------|------|------|
| indicates | 指向 | Indicator → Intrusion Set |
| uses | 使用 | Intrusion Set → Malware/Tool |
| targets | 目标 | Campaign/Intrusion Set → Identity/Sector |
| exploits | 利用 | Malware → Vulnerability |
| mitigates | 缓解 | Course of Action → Attack Pattern |
| attributed-to | 归因 | Campaign → Threat Actor |
| variant-of | 变体 | Malware → Malware |
| communicates-with | 通信 | Malware → IP/Domain |
| delivers | 投递 | Campaign → Malware |

#### 3.5.2 Sighting（目击）

Sighting对象记录对某个STIX对象的实际观测。

```json
{
  "type": "sighting",
  "spec_version": "2.1",
  "id": "sighting--f2a3b4c5-d6e7-8901-fa01-bcdef012345678",
  "created": "2024-01-16T09:00:00.000Z",
  "modified": "2024-01-16T09:00:00.000Z",
  "first_seen": "2024-01-16T08:30:00Z",
  "last_seen": "2024-01-16T08:45:00Z",
  "sighting_of_ref": "indicator--d4e5f6a7-b8c9-0123-def0-456789abcdef",
  "count": 3,
  "observed_data_refs": [
    "observed-data--a7b8c9d0-e1f2-3456-ab01-7890abcdef0123"
  ],
  "where_sighted_refs": [
    "identity--c5cb6e89-4c4d-4e97-8c1e-123456789abc"
  ],
  "summary": "在内部网络中检测到与APT28关联的C2通信"
}
```

### 3.6 STIX Pattern语言

STIX Pattern用于在Indicator对象中描述检测规则。

```
STIX Pattern语法:
[pattern]

运算符:
=  等于
!= 不等于
IN 在...范围内
LIKE 模糊匹配
MATCHES 正则匹配

逻辑连接符:
AND, OR, NOT, FOLLOWEDBY

括号:
[ ] 对象分组
( ) 逻辑分组
```

**Pattern示例：**

```
# IP地址指标
[ipv4-addr:value = '185.220.101.45']

# 域名指标
[domain-name:value = 'c2.evil.com']

# 文件哈希
[file:hashes.'SHA-256' = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855']

# URL指标
[url:value = 'http://evil.com/payload.exe']

# 组合指标（IP AND 端口）
([ipv4-addr:value = '185.220.101.45'] AND [network-traffic:dst_port = 443])

# 进程创建指标
[process:name = 'powershell.exe' AND process:command_line LIKE '%-enc%']

# 邮件指标
[email-message:sender = 'attacker@evil.com' AND email-message:subject LIKE '%Invoice%']

# 带时间窗口的关联
([file:name = 'doc.docx'] FOLLOWEDBY [process:name = 'cmd.exe']) WITHIN 300 SECONDS
```

### 3.7 STIX Bundle示例

一个完整的STIX Bundle，包含多个关联对象：

```json
{
  "type": "bundle",
  "id": "bundle--a3b4c5d6-e7f8-9012-ab34-cdef012345678",
  "objects": [
    {
      "type": "identity",
      "spec_version": "2.1",
      "id": "identity--c5cb6e89-4c4d-4e97-8c1e-123456789abc",
      "created": "2024-01-01T00:00:00Z",
      "modified": "2024-01-01T00:00:00Z",
      "name": "Security Team Alpha",
      "identity_class": "organization"
    },
    {
      "type": "intrusion-set",
      "spec_version": "2.1",
      "id": "intrusion-set--e5f6a7b8-c9d0-1234-ef01-567890abcdef0",
      "created": "2024-01-01T00:00:00Z",
      "modified": "2024-01-15T10:00:00Z",
      "name": "APT28",
      "description": "俄罗斯APT组织",
      "aliases": ["Fancy Bear", "Sofacy"]
    },
    {
      "type": "indicator",
      "spec_version": "2.1",
      "id": "indicator--d4e5f6a7-b8c9-0123-def0-456789abcdef",
      "created": "2024-01-15T08:00:00Z",
      "modified": "2024-01-15T08:00:00Z",
      "name": "APT28 C2 IP",
      "pattern": "[ipv4-addr:value = '185.220.101.45']",
      "pattern_type": "stix",
      "indicator_types": ["malicious-activity"],
      "valid_from": "2024-01-15T08:00:00Z",
      "valid_until": "2024-04-15T08:00:00Z"
    },
    {
      "type": "malware",
      "spec_version": "2.1",
      "id": "malware--f6a7b8c9-d0e1-2345-fa01-67890abcdef01",
      "created": "2024-01-10T12:00:00Z",
      "modified": "2024-01-10T12:00:00Z",
      "name": "Sofacy Trojan",
      "malware_types": ["trojan", "backdoor"]
    },
    {
      "type": "relationship",
      "spec_version": "2.1",
      "id": "relationship--e1f2a3b4-c5d6-7890-ef01-abcdef01234567",
      "created": "2024-01-15T08:00:00Z",
      "modified": "2024-01-15T08:00:00Z",
      "relationship_type": "indicates",
      "source_ref": "indicator--d4e5f6a7-b8c9-0123-def0-456789abcdef",
      "target_ref": "intrusion-set--e5f6a7b8-c9d0-1234-ef01-567890abcdef0",
      "description": "C2 IP指向APT28"
    },
    {
      "type": "relationship",
      "spec_version": "2.1",
      "id": "relationship--a3b4c5d6-e7f8-9012-ab34-cdef012345678",
      "created": "2024-01-15T08:00:00Z",
      "modified": "2024-01-15T08:00:00Z",
      "relationship_type": "uses",
      "source_ref": "intrusion-set--e5f6a7b8-c9d0-1234-ef01-567890abcdef0",
      "target_ref": "malware--f6a7b8c9-d0e1-2345-fa01-67890abcdef01",
      "description": "APT28使用Sofacy木马"
    },
    {
      "type": "sighting",
      "spec_version": "2.1",
      "id": "sighting--f2a3b4c5-d6e7-8901-fa01-bcdef012345678",
      "created": "2024-01-16T09:00:00Z",
      "modified": "2024-01-16T09:00:00Z",
      "first_seen": "2024-01-16T08:30:00Z",
      "last_seen": "2024-01-16T08:45:00Z",
      "sighting_of_ref": "indicator--d4e5f6a7-b8c9-0123-def0-456789abcdef",
      "count": 3,
      "where_sighted_refs": ["identity--c5cb6e89-4c4d-4e97-8c1e-123456789abc"]
    }
  ]
}
```

### 3.8 STIX Python库使用

```python
#!/usr/bin/env python3
"""使用stix2库创建和操作STIX对象"""
from stix2 import (
    Indicator, Identity, IntrusionSet, Malware,
    Relationship, Sighting, Bundle, AttackPattern,
    CourseOfAction, Vulnerability, Tool, Campaign,
    ThreatActor, ObservedData, MemoryStore
)
from stix2 import parse, filter_by_type
from datetime import datetime, timezone
import json

# 1. 创建Identity（情报生产者）
identity = Identity(
    name="Security Team Alpha",
    identity_class="organization",
    description="企业内部安全团队"
)

# 2. 创建Indicator
indicator = Indicator(
    name="APT28 C2 IP",
    description="APT28组织的C2服务器IP",
    pattern="[ipv4-addr:value = '185.220.101.45']",
    pattern_type="stix",
    indicator_types=["malicious-activity"],
    valid_from="2024-01-15T08:00:00Z",
    valid_until="2024-04-15T08:00:00Z",
    confidence=85,
    created_by_ref=identity.id
)

# 3. 创建Intrusion Set
intrusion_set = IntrusionSet(
    name="APT28",
    description="俄罗斯APT组织Fancy Bear",
    aliases=["Fancy Bear", "Sofacy", "STRONTIUM"],
    goals=["intelligence-collection", "espionage"],
    primary_motivation="dominance",
    first_seen="2007-01-01T00:00:00Z",
    last_seen="2024-01-15T00:00:00Z"
)

# 4. 创建Malware
malware = Malware(
    name="Sofacy Trojan",
    description="APT28使用的木马程序",
    malware_types=["trojan", "backdoor"],
    is_family=False,
    first_seen="2024-01-01T00:00:00Z",
    operating_system_refs=[]
)

# 5. 创建关系
rel1 = Relationship(
    relationship_type="indicates",
    source_ref=indicator.id,
    target_ref=intrusion_set.id,
    description="该IP指标指向APT28"
)

rel2 = Relationship(
    relationship_type="uses",
    source_ref=intrusion_set.id,
    target_ref=malware.id,
    description="APT28使用Sofacy木马"
)

# 6. 创建Sighting
sighting = Sighting(
    sighting_of_ref=indicator.id,
    first_seen="2024-01-16T08:30:00Z",
    last_seen="2024-01-16T08:45:00Z",
    count=3,
    where_sighted_refs=[identity.id]
)

# 7. 创建Bundle
bundle = Bundle(
    identity, intrusion_set, indicator, malware,
    rel1, rel2, sighting
)

# 序列化为JSON
print("=== STIX Bundle ===")
print(bundle.serialize(pretty=True))

# 8. 使用MemoryStore存储
store = MemoryStore()
store.add(bundle)

# 9. 查询
# 按类型查询
all_indicators = store.query([
    filter("type", "=", "indicator")
])
print(f"\n指标数量: {len(all_indicators)}")

# 按ID查询
retrieved = store.get(indicator.id)
print(f"查询结果: {retrieved.name}")

# 按属性过滤
from stix2 import filter
results = store.query(
    [filter("type", "=", "relationship"),
     filter("relationship_type", "=", "indicates")]
)
for r in results:
    print(f"关系: {r.relationship_type} -> {r.target_ref}")

# 10. 解析JSON为STIX对象
stix_json = bundle.serialize()
parsed = parse(stix_json)
print(f"\n解析对象数量: {len(parsed.objects)}")

# 11. 更新对象
updated_indicator = indicator.set(
    confidence=90,
    modified=datetime.now(timezone.utc)
)
print(f"\n更新后的置信度: {updated_indicator.confidence}")
```

---

---

## 📋 内容审核与补充建议

> 针对「STIX 2.1标准详解」部分的内容审核结果：

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
