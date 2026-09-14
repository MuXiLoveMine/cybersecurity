# 威胁情报生命周期与STIX-TAXII

> 威胁情报的生命周期管理决定了情报从原始数据到可操作防御规则的转化效率。本文档详细讲解威胁情报的完整生命周期、情报来源分类、STIX 2.1标准对象模型与JSON结构、TAXII 2.1传输协议、MISP平台部署与API操作、主流威胁情报平台对比，以及从情报收集到检测规则生成的全流程实战案例，帮助安全学习者掌握威胁情报的标准化建模与自动化消费能力。

---

## 一、威胁情报生命周期

### 1.1 生命周期概述

威胁情报生命周期描述了情报从产生到消亡的完整过程，是威胁情报运营的骨架。

```
┌─────────────────────────────────────────────────────────────┐
│                   威胁情报生命周期                           │
│                                                             │
│   ┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐    │
│   │  收集   │───→│  处理   │───→│  分析   │───→│  传播   │    │
│   │ Collect │    │ Process│    │Analyze │    │Dissem. │    │
│   └────────┘    └────────┘    └────────┘    └────────┘    │
│        ↑                                       │            │
│        │              ┌────────┐               │            │
│        └──────────────│  反馈   │←──────────────┘            │
│                       │Feedback│                            │
│                       └────────┘                            │
│                            │                                 │
│                       ┌────────┐                            │
│                       │  迭代   │                            │
│                       │ Iterate │                            │
│                       └────────┘                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 各阶段详解

#### 1.2.1 收集阶段（Collection）

**目标：** 从多种来源获取原始威胁数据。

| 数据类型 | 来源示例 | 收集方式 |
|----------|----------|----------|
| 恶意IP/域名 | 商业情报源、开源情报、内部检测 | API拉取、手动导入、日志关联 |
| 文件样本 | 沙箱、终端检测、蜜罐 | 自动上传、API提交 |
| 漏洞信息 | NVD、厂商公告、CVE | RSS订阅、API同步 |
| 威胁报告 | 安全博客、厂商报告、APT报告 | 爬虫、手动收集 |
| 暗网数据 | 暗网论坛、Telegram频道 | 爬虫、人工监测 |
| 内部数据 | SIEM、EDR、NDR、防火墙 | 日志查询、告警关联 |

```python
#!/usr/bin/env python3
"""威胁情报多源收集器"""
import requests
import json
import os
from datetime import datetime
from abc import ABC, abstractmethod

class IntelCollector(ABC):
    """情报收集器基类"""
    def __init__(self, name):
        self.name = name
        self.collected = []
    
    @abstractmethod
    def collect(self):
        """收集情报"""
        pass
    
    def save(self, output_dir="/tmp/intel"):
        """保存收集结果"""
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(
            output_dir,
            f"{self.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(filepath, 'w') as f:
            json.dump(self.collected, f, indent=2, ensure_ascii=False)
        print(f"[{self.name}] 收集了 {len(self.collected)} 条情报, 保存到 {filepath}")
        return filepath

class AbuseURLCollector(IntelCollector):
    """从urlhaus.abuse.ch收集恶意URL"""
    def __init__(self):
        super().__init__("urlhaus")
    
    def collect(self):
        try:
            resp = requests.get(
                "https://urlhaus.abuse.ch/api/v1/payloads/",
                timeout=30
            )
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get('payloads', [])[:100]:
                    self.collected.append({
                        'source': 'urlhaus',
                        'url': item.get('url'),
                        'first_seen': item.get('firstseen'),
                        'signature': item.get('signature'),
                        'sha256': item.get('sha256'),
                    })
        except Exception as e:
            print(f"[{self.name}] 收集失败: {e}")
        return self.collected

class ThreatFoxCollector(IntelCollector):
    """从ThreatFox收集IOC"""
    def __init__(self):
        super().__init__("threatfox")
    
    def collect(self):
        try:
            resp = requests.get(
                "https://threatfox-api.abuse.ch/api/v1/",
                params={"limit": 100},
                timeout=30
            )
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get('data', [])[:100]:
                    self.collected.append({
                        'source': 'threatfox',
                        'ioc_value': item.get('ioc_value'),
                        'ioc_type': item.get('ioc_type'),
                        'threat_type': item.get('threat_type'),
                        'malware': item.get('malware'),
                        'confidence': item.get('confidence_level'),
                    })
        except Exception as e:
            print(f"[{self.name}] 收集失败: {e}")
        return self.collected

class AlienVaultOTXCollector(IntelCollector):
    """从AlienVault OTX收集情报"""
    def __init__(self, api_key=None):
        super().__init__("alienvault_otx")
        self.api_key = api_key or os.environ.get('OTX_API_KEY', '')
        self.base_url = "https://otx.alienvault.com/api/v1"
    
    def collect(self):
        headers = {'X-OTX-API-KEY': self.api_key}
        try:
            # 获取最近的 pulses
            resp = requests.get(
                f"{self.base_url}/pulses/subscribed",
                headers=headers,
                params={"limit": 50},
                timeout=30
            )
            if resp.status_code == 200:
                data = resp.json()
                for pulse in data.get('results', []):
                    for indicator in pulse.get('indicators', []):
                        self.collected.append({
                            'source': 'alienvault_otx',
                            'pulse_name': pulse.get('name'),
                            'ioc': indicator.get('indicator'),
                            'ioc_type': indicator.get('type'),
                            'description': indicator.get('description'),
                            'created': indicator.get('created'),
                        })
        except Exception as e:
            print(f"[{self.name}] 收集失败: {e}")
        return self.collected

# 使用示例
if __name__ == "__main__":
    collectors = [
        AbuseURLCollector(),
        ThreatFoxCollector(),
        # AlienVaultOTXCollector(api_key="your-api-key"),
    ]
    
    for collector in collectors:
        collector.collect()
        collector.save()
```

#### 1.2.2 处理阶段（Processing）

**目标：** 对原始数据进行标准化、去重、富化。

```
原始数据 → 格式标准化 → 去重 → 数据富化 → 入库
    ↓           ↓          ↓        ↓        ↓
  多格式JSON   STIX格式  哈希比对  VT查询   数据库
  CSV/TSV     统一字段   MD5去重  GeoIP    Elasticsearch
```

```python
#!/usr/bin/env python3
"""威胁情报处理工具"""
import hashlib
from collections import defaultdict
import requests

class IntelProcessor:
    def __init__(self):
        self.processed = []
        self.duplicates_removed = 0
    
    def normalize(self, raw_intel_list):
        """标准化情报数据"""
        normalized = []
        for item in raw_intel_list:
            norm = {
                'value': item.get('ioc') or item.get('ioc_value') or item.get('url'),
                'type': self._detect_type(
                    item.get('ioc_type') or item.get('type') or
                    item.get('url', '')
                ),
                'source': item.get('source', 'unknown'),
                'first_seen': item.get('first_seen') or item.get('created'),
                'confidence': item.get('confidence', 'medium'),
                'tags': self._extract_tags(item),
                'description': item.get('description', ''),
            }
            normalized.append(norm)
        return normalized
    
    def _detect_type(self, value_or_type):
        """自动检测IOC类型"""
        if value_or_type in ('ip', 'ipv4', 'URL', 'url'):
            return value_or_type.lower()
        
        import re
        # IP地址
        if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', str(value_or_type)):
            return 'ipv4'
        # MD5
        if re.match(r'^[a-fA-F0-9]{32}$', str(value_or_type)):
            return 'md5'
        # SHA1
        if re.match(r'^[a-fA-F0-9]{40}$', str(value_or_type)):
            return 'sha1'
        # SHA256
        if re.match(r'^[a-fA-F0-9]{64}$', str(value_or_type)):
            return 'sha256'
        # URL
        if str(value_or_type).startswith(('http://', 'https://')):
            return 'url'
        # 域名
        if re.match(r'^[a-zA-Z0-9][a-zA-Z0-9-]*\.[a-zA-Z]{2,}$', str(value_or_type)):
            return 'domain'
        # 邮箱
        if re.match(r'^[^@]+@[^@]+\.[^@]+$', str(value_or_type)):
            return 'email'
        return 'unknown'
    
    def _extract_tags(self, item):
        """提取标签"""
        tags = []
        if item.get('malware'):
            tags.append(item['malware'].lower())
        if item.get('signature'):
            tags.append(item['signature'].lower())
        if item.get('threat_type'):
            tags.append(item['threat_type'].lower())
        return tags
    
    def deduplicate(self, intel_list):
        """去重"""
        seen = set()
        unique = []
        for item in intel_list:
            key = hashlib.md5(
                f"{item['type']}:{item['value']}".encode()
            ).hexdigest()
            if key not in seen:
                seen.add(key)
                unique.append(item)
            else:
                self.duplicates_removed += 1
        return unique
    
    def enrich(self, intel_list):
        """数据富化"""
        enriched = []
        for item in intel_list:
            if item['type'] == 'ipv4':
                item['geo'] = self._geo_enrich(item['value'])
            if item['type'] in ('md5', 'sha256'):
                item['vt'] = self._vt_enrich(item['value'])
            enriched.append(item)
        return enriched
    
    def _geo_enrich(self, ip):
        """GeoIP富化"""
        try:
            resp = requests.get(
                f"http://ip-api.com/json/{ip}",
                timeout=5
            )
            if resp.status_code == 200:
                data = resp.json()
                return {
                    'country': data.get('countryCode'),
                    'city': data.get('city'),
                    'isp': data.get('isp'),
                    'org': data.get('org'),
                }
        except Exception:
            pass
        return {}
    
    def _vt_enrich(self, hash_value):
        """VirusTotal富化"""
        # 实际使用需要API Key
        return {'status': 'not_configured'}
    
    def process(self, raw_intel_list):
        """完整处理流程"""
        print(f"[处理] 输入 {len(raw_intel_list)} 条原始情报")
        
        # 1. 标准化
        normalized = self.normalize(raw_intel_list)
        print(f"[处理] 标准化完成: {len(normalized)} 条")
        
        # 2. 去重
        deduped = self.deduplicate(normalized)
        print(f"[处理] 去重完成: {len(deduped)} 条 (移除 {self.duplicates_removed} 条重复)")
        
        # 3. 富化
        enriched = self.enrich(deduped)
        print(f"[处理] 富化完成: {len(enriched)} 条")
        
        self.processed = enriched
        return enriched

# 使用
processor = IntelProcessor()
raw_data = [
    {'ioc': '1.2.3.4', 'type': 'ip', 'source': 'test'},
    {'ioc_value': '5.6.7.8', 'ioc_type': 'ip', 'source': 'threatfox'},
    {'url': 'http://malicious.com/payload.exe', 'source': 'urlhaus'},
    {'ioc': '1.2.3.4', 'type': 'ip', 'source': 'test'},  # 重复
]
result = processor.process(raw_data)
import json
print(json.dumps(result, indent=2, ensure_ascii=False))
```

#### 1.2.3 分析阶段（Analysis）

**目标：** 将处理后的数据转化为有上下文的情报。

分析层次：

| 层次 | 输入 | 输出 | 所需技能 |
|------|------|------|----------|
| 战术级 | IOC列表 | 检测规则 | 安全工具配置 |
| 运营级 | IOC + 事件 | 威胁上下文 | 安全运营经验 |
| 战略级 | 多源情报 | 趋势报告 | 威胁分析研究 |

#### 1.2.4 传播阶段（Dissemination）

**目标：** 将情报推送到正确的消费方。

| 消费方 | 情报格式 | 传输方式 |
|--------|----------|----------|
| SIEM/SOC | IOC列表(STIX/TAXII) | API推送 |
| 防火墙/WAF | IP/域名列表 | API同步 |
| EDR | 文件哈希 | 策略下发 |
| 管理层 | 趋势报告 | 邮件/报告 |
| 业务团队 | 风险通告 | 通知公告 |

#### 1.2.5 反馈阶段（Feedback）

**目标：** 收集情报使用效果，指导下一轮收集。

```python
class IntelFeedbackSystem:
    """情报反馈系统"""
    def __init__(self):
        self.feedback = []
    
    def record_feedback(self, intel_id, action_taken, result, effectiveness):
        """记录反馈"""
        self.feedback.append({
            'intel_id': intel_id,
            'action': action_taken,    # 'block', 'detect', 'investigate'
            'result': result,          # 'true_positive', 'false_positive'
            'effectiveness': effectiveness,  # 0-100
            'timestamp': datetime.now().isoformat()
        })
    
    def adjust_collection_priority(self):
        """根据反馈调整收集优先级"""
        source_scores = defaultdict(list)
        for fb in self.feedback:
            if fb['result'] == 'true_positive':
                source_scores[fb['intel_source']].append(fb['effectiveness'])
        
        # 计算各来源的平均有效性
        source_priorities = {}
        for source, scores in source_scores.items():
            source_priorities[source] = sum(scores) / len(scores)
        
        return source_priorities
    
    def detect_ioc_decay(self, ioc_value):
        """检测IOC衰减（过时IOC）"""
        # 如果一个IOC在最近N天内没有产生新的检测结果
        # 标记为可能过时
        recent_hits = [f for f in self.feedback 
                       if f['intel_id'] == ioc_value 
                       and f['result'] == 'true_positive'
                       and (datetime.now() - f['timestamp']).days < 30]
        return len(recent_hits) == 0
```

#### 1.2.6 迭代阶段（Iteration）

情报生命周期是持续迭代的循环。每轮迭代需要：

1. **回顾效果**：上一轮情报的检出率、误报率
2. **调整策略**：增加高价值来源、减少低价值来源
3. **更新规则**：移除过期IOC、更新检测逻辑
4. **优化流程**：自动化处理、缩短响应时间

---

## 二、威胁情报来源分类

### 2.1 来源分类总览

| 类型 | 英文 | 特点 | 代表来源 |
|------|------|------|----------|
| 商业情报 | Commercial | 付费，质量高，有分析支持 | Recorded Future, CrowdStrike, Mandiant |
| 开源情报 | OSINT | 免费，数量多，质量参差 | Abuse.ch, OTX, VirusTotal |
| 共享情报 | Shared | 社区共享，需贡献 | MISP社区, ISAC, CERT |
| 内部情报 | Internal | 自有数据，高度相关 | SIEM日志, EDR告警, 蜜罐 |
| 政府情报 | Government | 权威但受限 | CISA, ENISA, 国家CERT |
| 暗网情报 | Darknet | 数据泄露预警 | 暗网监控, Telegram爬虫 |

### 2.2 开源情报源详情

```yaml
# 开源威胁情报源配置
threat_feeds:
  # === IOC类 ===
  - name: URLhaus
    url: https://urlhaus.abuse.ch/api/
    type: malicious_urls
    update: 实时
    format: JSON
    
  - name: ThreatFox
    url: https://threatfox-api.abuse.ch/api/v1/
    type: iocs
    update: 实时
    format: JSON
    
  - name: PhishTank
    url: https://www.phishtank.com/api/
    type: phishing_urls
    update: 每小时
    format: JSON
    api_key_required: true
    
  - name: AbuseIPDB
    url: https://api.abuseipdb.com/api/v2/
    type: malicious_ips
    update: 实时
    format: JSON
    api_key_required: true
    
  # === 文件样本类 ===
  - name: MalwareBazaar
    url: https://bazaar.abuse.ch/api/
    type: malware_samples
    update: 实时
    format: JSON
    
  - name: VirusTotal
    url: https://www.virustotal.com/api/v3/
    type: file_url_domain_reputation
    update: 实时
    format: JSON
    api_key_required: true
    free_tier: 4_requests_per_minute
    
  # === 漏洞类 ===
  - name: NVD
    url: https://services.nvd.nist.gov/rest/json/
    type: vulnerabilities
    update: 每日
    format: JSON
    
  - name: CISA KEV
    url: https://www.cisa.gov/known-exploited-vulnerabilities
    type: known_exploited_vulns
    update: 不定期
    format: JSON/CSV
    
  # === 威胁报告类 ===
  - name: AlienVault OTX
    url: https://otx.alienvault.com/api/
    type: threat_reports_and_iocs
    update: 实时
    format: JSON
    api_key_required: true
    
  - name: Pulsedive
    url: https://pulsedive.com/api/
    type: ioc_reputation
    update: 实时
    format: JSON
    api_key_required: true
```

### 2.3 内部情报生成

```python
#!/usr/bin/env python3
"""内部情报生成器 - 从安全日志中提取IOC"""
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta

class InternalIntelGenerator:
    def __init__(self):
        self.iocs = defaultdict(list)
    
    def extract_from_dns_logs(self, log_file):
        """从DNS日志中提取可疑域名"""
        dga_patterns = [
            # 长域名（可能是DGA）
            (r'^[a-z0-9]{20,}\.(xyz|top|cn|tk|ml)$', 'dga_long_domain'),
            # 随机字符
            (r'^[a-z]{1}\d{5,}[a-z]{1}\.(xyz|top)$', 'dga_pattern_1'),
            # 高熵域名
            (r'^[bcdfghjklmnpqrstvwxyz]{15,}\.', 'daga_consonant_heavy'),
        ]
        
        with open(log_file) as f:
            for line in f:
                parts = line.split()
                if len(parts) >= 6:
                    query = parts[5].strip('.')
                    for pattern, label in dga_patterns:
                        if re.match(pattern, query):
                            self.iocs['suspicious_domains'].append({
                                'domain': query,
                                'type': label,
                                'source': 'dns_log',
                                'timestamp': parts[0] + ' ' + parts[1]
                            })
    
    def extract_from_proxy_logs(self, log_file):
        """从代理日志中提取可疑URL和IP"""
        suspicious_user_agents = [
            'curl', 'wget', 'python-requests', 'powershell',
            'mozillain', 'mozilla', 'empty'
        ]
        
        with open(log_file) as f:
            for line in f:
                parts = line.split()
                if len(parts) >= 10:
                    dst_ip = parts[6]
                    url = parts[8] if len(parts) > 8 else ''
                    user_agent = parts[11] if len(parts) > 11 else ''
                    
                    # 检测可疑User-Agent
                    for sua in suspicious_user_agents:
                        if sua in user_agent.lower():
                            self.iocs['suspicious_connections'].append({
                                'dst_ip': dst_ip,
                                'url': url,
                                'user_agent': user_agent,
                                'reason': f'suspicious_ua: {sua}',
                                'source': 'proxy_log'
                            })
    
    def extract_from_edr_alerts(self, alert_data):
        """从EDR告警中提取IOC"""
        for alert in alert_data:
            # 提取进程哈希
            if alert.get('process_hash'):
                self.iocs['file_hashes'].append({
                    'hash': alert['process_hash'],
                    'type': 'sha256',
                    'description': alert.get('description', 'EDR alert'),
                    'source': 'edr'
                })
            # 提取网络连接
            if alert.get('network_connection'):
                conn = alert['network_connection']
                self.iocs['network_indicators'].append({
                    'dst_ip': conn.get('dst_ip'),
                    'dst_port': conn.get('dst_port'),
                    'process': alert.get('process_name'),
                    'source': 'edr'
                })
    
    def correlate(self):
        """关联分析"""
        # 找出在多个日志源中出现的IOC
        all_ips = []
        for item in self.iocs['suspicious_connections']:
            all_ips.append(item['dst_ip'])
        for item in self.iocs['network_indicators']:
            all_ips.append(item['dst_ip'])
        
        ip_counts = Counter(all_ips)
        # 出现3次以上的IP视为高置信IOC
        high_confidence = {
            ip: count for ip, count in ip_counts.items() if count >= 3
        }
        return high_confidence
    
    def export_stix(self, output_file):
        """导出为STIX格式"""
        # 后续章节详述STIX格式
        pass
```

---

## 三、STIX 2.1标准详解

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

## 四、TAXII 2.1协议详解

### 4.1 TAXII概述

**TAXII**（Trusted Automated Exchange of Intelligence Information）是用于在网络上传输网络威胁情报信息的协议。TAXII 2.1基于HTTPS RESTful API设计，与STIX 2.1配合使用。

### 4.2 TAXII架构

```
┌──────────────────────────────────────────────────────────┐
│                   TAXII 2.1 架构                          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐                                       │
│  │  Discovery    │  发现服务，返回可用API Root列表        │
│  │  Service      │                                      │
│  └──────┬───────┘                                       │
│         │                                                │
│         ▼                                                │
│  ┌──────────────┐                                       │
│  │  API Root     │  API根目录，包含Collections和Collections│
│  └──────┬───────┘                                       │
│         │                                                │
│    ┌────┴────┐                                          │
│    ▼         ▼                                           │
│ ┌──────┐ ┌──────────┐                                  │
│ │Collections│ │ Collection  │  集合，存储STIX对象的容器    │
│ └──────┘ └──────┬───┘                                  │
│                  │                                      │
│                  ▼                                      │
│            ┌──────────┐                                 │
│            │ Objects  │  STIX对象（Indicator, Malware等）│
│            └──────────┘                                 │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### 4.3 TAXII端点

| 端点 | 方法 | 说明 |
|------|------|------|
| /discovery | GET | 发现服务，返回API Root信息 |
| /{api_root}/ | GET | API Root信息 |
| /{api_root}/collections/ | GET | 列出所有集合 |
| /{api_root}/collections/{id}/ | GET | 获取特定集合信息 |
| /{api_root}/collections/{id}/objects/ | GET | 获取集合中的STIX对象 |
| /{api_root}/collections/{id}/objects/ | POST | 向集合添加STIX对象 |
| /{api_root}/collections/{id}/objects/{object_id}/ | GET | 获取特定对象 |
| /{api_root}/manifest/ | GET | 获取对象清单 |
| /{api_root}/status/{id}/ | GET | 获取操作状态 |

### 4.4 TAXII传输流程

```
客户端                                    TAXII服务器
  │                                            │
  │  1. GET /discovery                          │
  │ ──────────────────────────────────────────→ │
  │                                             │
  │  2. 返回API Root列表                         │
  │ ←──────────────────────────────────────────  │
  │                                             │
  │  3. GET /trust-group1/ (API Root)           │
  │ ──────────────────────────────────────────→ │
  │                                             │
  │  4. 返回API Root信息(标题、描述、集合)       │
  │ ←──────────────────────────────────────────  │
  │                                             │
  │  5. GET /trust-group1/collections/          │
  │ ──────────────────────────────────────────→ │
  │                                             │
  │  6. 返回集合列表                             │
  │ ←──────────────────────────────────────────  │
  │                                             │
  │  7. GET /trust-group1/collections/{id}/     │
  │     /objects?added_after=2024-01-01         │
  │ ──────────────────────────────────────────→ │
  │                                             │
  │  8. 返回STIX对象(Bundle)                    │
  │ ←──────────────────────────────────────────  │
  │                                             │
  │  9. POST /trust-group1/collections/{id}/    │
  │     /objects  (提交新STIX对象)               │
  │ ──────────────────────────────────────────→ │
  │                                             │
  │  10. 返回Status对象(处理状态)               │
  │ ←──────────────────────────────────────────  │
```

### 4.5 TAXII认证与授权

TAXII 2.1支持多种认证方式：

```python
#!/usr/bin/env python3
"""TAXII 2.1客户端实现"""
import requests
import json
from datetime import datetime
from urllib.parse import urljoin

class TAXIIClient:
    """TAXII 2.1客户端"""
    
    def __init__(self, base_url, auth=None, verify_ssl=True):
        self.base_url = base_url.rstrip('/')
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        
        # 认证配置
        if auth:
            if auth.get('type') == 'basic':
                self.session.auth = (auth['user'], auth['password'])
            elif auth.get('type') == 'bearer':
                self.session.headers['Authorization'] = f"Bearer {auth['token']}"
            elif auth.get('type') == 'api_key':
                self.session.headers['X-API-Key'] = auth['key']
        
        self.session.headers.update({
            'Accept': 'application/taxii+json;version=2.1',
            'Content-Type': 'application/taxii+json;version=2.1'
        })
    
    def discover(self):
        """发现服务"""
        url = urljoin(self.base_url + '/', 'discovery')
        resp = self.session.get(url, verify=self.verify_ssl)
        resp.raise_for_status()
        return resp.json()
    
    def get_api_roots(self):
        """获取API Root列表"""
        discovery = self.discover()
        return [root['url'] for root in discovery.get('api_roots', [])]
    
    def get_collections(self, api_root):
        """获取集合列表"""
        url = urljoin(api_root, 'collections/')
        resp = self.session.get(url, verify=self.verify_ssl)
        resp.raise_for_status()
        return resp.json().get('collections', [])
    
    def get_objects(self, api_root, collection_id, 
                    added_after=None, limit=None, 
                    stix_type=None):
        """获取STIX对象"""
        url = urljoin(
            api_root, 
            f'collections/{collection_id}/objects/'
        )
        params = {}
        if added_after:
            params['added_after'] = added_after
        if limit:
            params['limit'] = limit
        if stix_type:
            params['match[type]'] = stix_type
        
        resp = self.session.get(
            url, params=params, verify=self.verify_ssl
        )
        resp.raise_for_status()
        return resp.json()
    
    def add_objects(self, api_root, collection_id, stix_bundle):
        """添加STIX对象"""
        url = urljoin(
            api_root,
            f'collections/{collection_id}/objects/'
        )
        resp = self.session.post(
            url, json=stix_bundle, verify=self.verify_ssl
        )
        resp.raise_for_status()
        return resp.json()
    
    def get_object(self, api_root, collection_id, object_id):
        """获取特定对象"""
        url = urljoin(
            api_root,
            f'collections/{collection_id}/objects/{object_id}/'
        )
        resp = self.session.get(url, verify=self.verify_ssl)
        resp.raise_for_status()
        return resp.json()
    
    def get_manifest(self, api_root, collection_id, 
                     added_after=None, limit=None):
        """获取对象清单"""
        url = urljoin(
            api_root,
            f'collections/{collection_id}/manifest/'
        )
        params = {}
        if added_after:
            params['added_after'] = added_after
        if limit:
            params['limit'] = limit
        
        resp = self.session.get(
            url, params=params, verify=self.verify_ssl
        )
        resp.raise_for_status()
        return resp.json()
    
    def get_status(self, api_root, status_id):
        """获取操作状态"""
        url = urljoin(api_root, f'status/{status_id}/')
        resp = self.session.get(url, verify=self.verify_ssl)
        resp.raise_for_status()
        return resp.json()

# 使用示例
if __name__ == "__main__":
    # 连接TAXII服务器
    client = TAXIIClient(
        base_url="https://cti.example.com",
        auth={
            'type': 'basic',
            'user': 'analyst',
            'password': 'password123'
        },
        verify_ssl=False
    )
    
    # 1. 发现服务
    print("=== Discovery ===")
    discovery = client.discover()
    print(json.dumps(discovery, indent=2))
    
    # 2. 获取API Roots
    print("\n=== API Roots ===")
    roots = client.get_api_roots()
    for root in roots:
        print(f"  {root}")
    
    # 3. 获取集合
    if roots:
        print(f"\n=== Collections ({roots[0]}) ===")
        collections = client.get_collections(roots[0])
        for col in collections:
            print(f"  {col['id']}: {col['title']} ({col.get('description', '')})")
        
        # 4. 获取对象
        if collections:
            col_id = collections[0]['id']
            print(f"\n=== Objects ({col_id}) ===")
            objects = client.get_objects(
                roots[0], col_id,
                added_after="2024-01-01T00:00:00Z",
                limit=10
            )
            for obj in objects.get('objects', []):
                print(f"  [{obj['type']}] {obj.get('name', obj.get('id'))}")
```

---

## 五、MISP平台使用

### 5.1 MISP架构与部署

**MISP**（Malware Information Sharing Platform）是开源的威胁情报共享平台，支持STIX/TAXII、OpenIOC等多种格式。

```
┌────────────────────────────────────────────────────────┐
│                    MISP 架构                            │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │ Web UI   │  │ REST API │  │ Python SDK(PyMISP)│   │
│  └────┬─────┘  └────┬─────┘  └────────┬─────────┘   │
│       │              │                  │              │
│       └──────────────┴──────────────────┘              │
│                        │                               │
│               ┌────────┴────────┐                     │
│               │   MISP Core      │                     │
│               │   (CakePHP)      │                     │
│               └────────┬────────┘                     │
│                        │                               │
│               ┌────────┴────────┐                     │
│               │   MySQL/MariaDB  │                     │
│               │   (数据存储)       │                     │
│               └─────────────────┘                     │
│                                                        │
│  ┌──────────────────────────────────────────────┐     │
│  │            集成模块                            │     │
│  │  STIX/TAXII │ CIRCL │ VirusTotal │ MITRE     │     │
│  └──────────────────────────────────────────────┘     │
│                                                        │
└────────────────────────────────────────────────────────┘
```

**Docker部署：**

```yaml
# docker-compose.yml - MISP部署
version: '3.8'

services:
  misp:
    image: harvarditsecurity/misp:latest
    container_name: misp
    ports:
      - "8080:80"
      - "8443:443"
    environment:
      - MISP_HOSTNAME=misp.local
      - MISP_EMAIL=admin@misp.local
      - MYSQL_ROOT_PASSWORD=misp_db_password
      - MISP_ADMIN_EMAIL=admin@misp.local
      - MISP_ADMIN_PASSPHRASE=AdminPassword123!
      - MISP_ADMIN_KEY=abcdef0123456789abcdef0123456789
    volumes:
      - misp_web:/var/www/MISP
      - misp_db:/var/lib/mysql
    restart: unless-stopped

volumes:
  misp_web:
  misp_db:
```

```bash
# 启动MISP
docker-compose up -d

# 验证服务
docker-compose ps
curl -k https://localhost:8443

# 获取API Key（管理界面: User Settings -> My Profile -> Auth Key）
# 或通过CLI
docker exec misp /var/www/MISP/app/Console/cake Admin getAuthKey admin@admin.test
```

### 5.2 事件管理

MISP中的核心概念是**事件（Event）**，每个事件是一组相关的情报数据。

```python
#!/usr/bin/env python3
"""使用PyMISP管理MISP事件和属性"""
from pymisp import PyMISP, MISPEvent, MISPAttribute
from pymisp import MISPObject, MISPTag
import json

class MISPManager:
    def __init__(self, url, api_key, verify_cert=False):
        self.misp = PyMISP(url, api_key, verify_cert, debug=False)
    
    def create_event(self, info, threat_level=2, analysis=0, 
                     distribution=0, tags=None):
        """创建事件"""
        event = MISPEvent()
        event.info = info
        event.threat_level_id = threat_level  # 1=高, 2=中, 3=低, 4=未知
        event.analysis = analysis  # 0=初始, 1=调查中, 2=完成
        event.distribution = distribution  # 0=仅自己, 1=本组织, 2=社区, 3=全部
        
        if tags:
            for tag_name in tags:
                event.add_tag(tag_name)
        
        result = self.misp.add_event(event)
        return result
    
    def add_attribute(self, event_id, attr_type, attr_value, 
                      category=None, comment=None, to_ids=True):
        """添加属性到事件"""
        event = self.misp.get_event(event_id)
        
        attribute = MISPAttribute()
        attribute.type = attr_type
        attribute.value = attr_value
        if category:
            attribute.category = category  #Payload delivery, Artifacts dropped, etc.
        if comment:
            attribute.comment = comment
        attribute.to_ids = to_ids  # 是否用于IDS检测
        
        result = self.misp.add_attribute(event_id, attribute)
        return result
    
    def add_attributes_batch(self, event_id, attributes):
        """批量添加属性"""
        event = self.misp.get_event(event_id)
        
        for attr in attributes:
            event.add_attribute(
                type=attr['type'],
                value=attr['value'],
                category=attr.get('category'),
                comment=attr.get('comment', ''),
                to_ids=attr.get('to_ids', True)
            )
        
        result = self.misp.update_event(event)
        return result
    
    def search_ioc(self, value=None, type=None, tags=None, 
                   category=None, timestamp=None):
        """搜索IOC"""
        result = self.misp.search(
            value=value,
            type_attribute=type,
            tags=tags,
            category=category,
            timestamp=timestamp
        )
        return result
    
    def add_tag_to_event(self, event_id, tag_name):
        """添加标签到事件"""
        result = self.misp.tag(event_id, tag_name)
        return result
    
    def add_object(self, event_id, template_name, attributes):
        """添加MISP对象（结构化属性集合）"""
        event = self.misp.get_event(event_id)
        
        obj = MISPObject(template_name)
        for attr_name, attr_value in attributes.items():
            obj.add_attribute(attr_name, value=attr_value)
        
        event.add_object(obj)
        result = self.misp.update_event(event)
        return result

# 使用示例
if __name__ == "__main__":
    manager = MISPManager(
        url="https://localhost:8443",
        api_key="abcdef0123456789abcdef0123456789",
        verify_cert=False
    )
    
    # 1. 创建事件
    event = manager.create_event(
        info="APT28 C2基础设施发现",
        threat_level=1,  # 高威胁
        analysis=1,       # 调查中
        distribution=2,   # 社区共享
        tags=["APT28", "C2", "Russia", "tlp:amber"]
    )
    event_id = event['Event']['id']
    print(f"创建事件: {event_id}")
    
    # 2. 添加属性
    attributes = [
        {'type': 'ip-src', 'value': '185.220.101.45', 
         'category': 'Network activity', 'comment': 'APT28 C2服务器'},
        {'type': 'domain', 'value': 'c2.evil.com',
         'category': 'Network activity', 'comment': 'APT28 C2域名'},
        {'type': 'url', 'value': 'http://c2.evil.com/payload.exe',
         'category': 'Payload delivery', 'comment': 'APT28投递URL'},
        {'type': 'sha256', 'value': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
         'category': 'Artifacts dropped', 'comment': 'APT28恶意样本'},
    ]
    manager.add_attributes_batch(event_id, attributes)
    print(f"添加了 {len(attributes)} 个属性")
    
    # 3. 添加标签
    manager.add_tag_to_event(event_id, "mitre-attack:T1566.001")
    
    # 4. 添加MISP对象（文件对象）
    manager.add_object(event_id, "file", {
        'filename': 'payload.exe',
        'size-in-bytes': '24576',
        'sha256': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
        'mimetype': 'application/x-msdownload'
    })
    
    # 5. 搜索IOC
    results = manager.search_ioc(
        value="185.220.101.45",
        type="ip-src"
    )
    print(f"搜索结果: {json.dumps(results, indent=2, ensure_ascii=False)}")
```

### 5.3 MISP与STIX/TAXII集成

```bash
# MISP导出STIX 2.1格式
# 通过API
curl -k -H "Authorization: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -X POST "https://localhost:8443/events/restSearch" \
  -d '{"format":"stix2","tags":["APT28"]}' \
  | jq .

# 通过PyMISP导出
python3 -c "
from pymisp import PyMISP
misp = PyMISP('https://localhost:8443', 'YOUR_API_KEY', False)
events = misp.search(tags=['APT28'], pythonify=True)
stix = misp.stix2_export(events)
print(stix)
"

# MISP作为TAXII服务器
# 启用MISP TAXII扩展
cd /var/www/MISP/app
# 安装cti-taxii-server
pip3 install taxii2-server
# 配置MISP TAXII
cat > /var/www/MISP/taxii_config.json << 'EOF'
{
  "api_root": "https://misp.local/taxii2/api/v21/",
  "collection": "misp",
  "title": "MISP TAXII 2.1 Server",
  "description": "MISP threat intelligence via TAXII 2.1"
}
EOF
```

```python
#!/usr/bin/env python3
"""MISP STIX/TAXII集成工具"""
from pymisp import PyMISP
from stix2 import parse, Bundle
import json
import requests

class MISPSTIXBridge:
    """MISP与STIX/TAXII桥接工具"""
    
    def __init__(self, misp_url, misp_key, verify_cert=False):
        self.misp = PyMISP(misp_url, misp_key, verify_cert)
    
    def misp_to_stix(self, event_id=None, tags=None, 
                     date_from=None, date_to=None):
        """将MISP事件转换为STIX Bundle"""
        # 从MISP获取事件
        if event_id:
            events = [self.misp.get_event(event_id, pythonify=True)]
        else:
            events = self.misp.search(
                tags=tags,
                date_from=date_from,
                date_to=date_to,
                pythonify=True
            )
        
        stix_objects = []
        
        for event in events:
            # 创建Identity
            identity = {
                "type": "identity",
                "spec_version": "2.1",
                "id": f"identity--{event.uuid}",
                "created": event.timestamp.isoformat() + "Z",
                "modified": event.timestamp.isoformat() + "Z",
                "name": event.orgc_id if hasattr(event, 'orgc_id') else "MISP",
                "identity_class": "organization"
            }
            stix_objects.append(identity)
            
            # 转换属性为Indicator
            indicators = []
            for attr in event.attributes:
                indicator = self._attr_to_indicator(attr, event, identity['id'])
                if indicator:
                    stix_objects.append(indicator)
                    indicators.append(indicator)
            
            # 创建Intrusion Set（如果有标签）
            if any(t.name.startswith('APT') for t in event.tags):
                intrusion_set = {
                    "type": "intrusion-set",
                    "spec_version": "2.1",
                    "id": f"intrusion-set--{event.uuid}",
                    "created": event.timestamp.isoformat() + "Z",
                    "modified": event.timestamp.isoformat() + "Z",
                    "name": event.info,
                    "description": event.info,
                    "aliases": [t.name for t in event.tags]
                }
                stix_objects.append(intrusion_set)
                
                # 创建关系
                for ind in indicators:
                    relationship = {
                        "type": "relationship",
                        "spec_version": "2.1",
                        "id": f"relationship--{ind['id'].split('--')[1][:8]}-{event.uuid[:8]}",
                        "created": event.timestamp.isoformat() + "Z",
                        "modified": event.timestamp.isoformat() + "Z",
                        "relationship_type": "indicates",
                        "source_ref": ind['id'],
                        "target_ref": intrusion_set['id']
                    }
                    stix_objects.append(relationship)
        
        bundle = {"type": "bundle", "objects": stix_objects}
        return bundle
    
    def _attr_to_indicator(self, attr, event, identity_id):
        """将MISP属性转换为STIX Indicator"""
        # MISP类型到STIX Pattern的映射
        pattern_map = {
            'ip-src': "ipv4-addr:value = '{}'",
            'ip-dst': "ipv4-addr:value = '{}'",
            'domain': "domain-name:value = '{}'",
            'hostname': "domain-name:value = '{}'",
            'url': "url:value = '{}'",
            'md5': "file:hashes.MD5 = '{}'",
            'sha1': "file:hashes.'SHA-1' = '{}'",
            'sha256': "file:hashes.'SHA-256' = '{}'",
            'email-src': "email-addr:value = '{}'",
            'email-dst': "email-addr:value = '{}'",
        }
        
        stix_type = attr.type
        if stix_type not in pattern_map:
            return None
        
        pattern = f"[{pattern_map[stix_type].format(attr.value)}]"
        
        return {
            "type": "indicator",
            "spec_version": "2.1",
            "id": f"indicator--{attr.uuid}",
            "created": attr.timestamp.isoformat() + "Z" if hasattr(attr, 'timestamp') else event.timestamp.isoformat() + "Z",
            "modified": attr.timestamp.isoformat() + "Z" if hasattr(attr, 'timestamp') else event.timestamp.isoformat() + "Z",
            "name": f"{attr.type}: {attr.value}",
            "description": attr.comment or event.info,
            "pattern": pattern,
            "pattern_type": "stix",
            "valid_from": event.date.isoformat() + "T00:00:00Z" if hasattr(event, 'date') else event.timestamp.isoformat() + "Z",
            "indicator_types": ["malicious-activity"],
            "created_by_ref": identity_id
        }
    
    def push_to_taxii(self, stix_bundle, taxii_url, taxii_auth, 
                      collection_id):
        """将STIX Bundle推送到TAXII服务器"""
        headers = {
            'Accept': 'application/taxii+json;version=2.1',
            'Content-Type': 'application/taxii+json;version=2.1',
            'Authorization': f'Bearer {taxii_auth}'
        }
        
        url = f"{taxii_url}/collections/{collection_id}/objects/"
        resp = requests.post(url, json=stix_bundle, headers=headers)
        return resp.json()

# 使用示例
if __name__ == "__main__":
    bridge = MISPSTIXBridge(
        misp_url="https://localhost:8443",
        misp_key="YOUR_API_KEY",
        verify_cert=False
    )
    
    # MISP -> STIX
    bundle = bridge.misp_to_stix(tags=["APT28"])
    print(f"生成STIX Bundle, 包含 {len(bundle['objects'])} 个对象")
    print(json.dumps(bundle, indent=2, ensure_ascii=False)[:2000])
    
    # 推送到TAXII
    # status = bridge.push_to_taxii(
    #     stix_bundle=bundle,
    #     taxii_url="https://taxii.example.com/api/v21",
    #     taxii_auth="taxii_token",
    #     collection_id="misp-collection"
    # )
    # print(f"TAXII推送状态: {status}")
```

---

## 六、威胁情报平台（TIP）对比

### 6.1 平台功能对比

| 特性 | MISP | OpenCTI | ThreatConnect | Recorded Future |
|------|------|---------|---------------|-----------------|
| 类型 | 开源 | 开源 | 商业 | 商业 |
| 部署方式 | 自建 | 自建/云 | 云/自建 | SaaS |
| STIX/TAXII | 原生支持 | 原生支持 | 支持 | 支持 |
| 数据存储 | MySQL | ElasticSearch | 专有 | 专有 |
| API | REST | GraphQL+REST | REST | REST |
| 可视化 | 基础 | 强大 | 强大 | 极强 |
| MITRE ATT&CK | 标签支持 | 原生集成 | 集成 | 原生集成 |
| 自动化 | 插件 | 内置 | Playbook | AI驱动 |
| 社区共享 | 全球社区 | 本地 | 封闭 | 专有 |
| 成本 | 免费 | 免费 | 付费 | 付费 |
| 适合规模 | 中小到大型 | 中到大型 | 中到大型 | 大型企业 |

### 6.2 OpenCTI部署示例

```yaml
# docker-compose.yml - OpenCTI部署
version: '3.8'

services:
  redis:
    image: redis:7
    restart: always
    
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.12.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    volumes:
      - es_data:/usr/share/elasticsearch/data
    
  minio:
    image: minio/minio:latest
    environment:
      - MINIO_ROOT_PASSWORD=opencti
      - MINIO_ROOT_PASSWORD=opencti
    command: server /data
    volumes:
      - minio_data:/data
    
  rabbitmq:
    image: rabbitmq:3-management
    environment:
      - RABBITMQ_DEFAULT_USER=guest
      - RABBITMQ_DEFAULT_PASS=guest
    
  opencti:
    image: opencti/platform:latest
    environment:
      - NODE_OPTIONS=--max-old-space-size=8096
      - APP__BASE_URL=http://localhost:8080
      - APP__ADMIN__PASSWORD=ChangeMe123!
      - APP__ADMIN__TOKEN=12345678-1234-1234-1234-123456789012
      - REDIS__HOSTNAME=redis
      - ELASTICSEARCH__URL=http://elasticsearch:9200
      - MINIO__ENDPOINT=minio
      - MINIO__ENDPOINT_PORT=9000
      - RABBITMQ__HOSTNAME=rabbitmq
    ports:
      - "8080:8080"
    depends_on:
      - redis
      - elasticsearch
      - minio
      - rabbitmq
    restart: always

volumes:
  es_data:
  minio_data:
```

### 6.3 OpenCTI API使用

```python
#!/usr/bin/env python3
"""OpenCTI Python SDK使用"""
from pycti import OpenCTIApiClient
import json

class OpenCTIManager:
    def __init__(self, url, api_key):
        self.client = OpenCTIApiClient(url, api_key)
    
    def create_threat_actor(self, name, description):
        """创建威胁行为者"""
        actor = self.client.threat_actor.create(
            name=name,
            description=description
        )
        return actor
    
    def create_indicator(self, pattern, name, indicator_type="malicious-activity"):
        """创建指标"""
        indicator = self.client.indicator.create(
            name=name,
            pattern=pattern,
            pattern_type="stix",
            indicator_types=[indicator_type],
            x_opencti_main_observable_type="IPv4-Addr"
        )
        return indicator
    
    def create_malware(self, name, description, malware_types):
        """创建恶意软件"""
        malware = self.client.malware.create(
            name=name,
            description=description,
            malware_types=malware_types
        )
        return malware
    
    def create_relationship(self, from_id, to_id, relationship_type, description=""):
        """创建关系"""
        rel = self.client.stix_core_relationship.create(
            fromId=from_id,
            toId=to_id,
            relationship_type=relationship_type,
            description=description
        )
        return rel
    
    def search_ioc(self, value):
        """搜索IOC"""
        result = self.client.stix_cyber_observable.list(
            filters=[
                {"key": "value", "values": [value]}
            ]
        )
        return result
    
    def get_attack_pattern(self, mitre_id):
        """获取ATT&CK技术"""
        patterns = self.client.attack_pattern.list(
            filters=[
                {"key": "x_mitre_id", "values": [mitre_id]}
            ]
        )
        return patterns

# 使用
if __name__ == "__main__":
    manager = OpenCTIManager(
        url="http://localhost:8080",
        api_key="12345678-1234-1234-1234-123456789012"
    )
    
    # 创建威胁行为者
    actor = manager.create_threat_actor("APT28", "俄罗斯APT组织")
    
    # 创建指标
    indicator = manager.create_indicator(
        pattern="[ipv4-addr:value = '185.220.101.45']",
        name="APT28 C2 IP"
    )
    
    # 创建恶意软件
    malware = manager.create_malware(
        name="Sofacy",
        description="APT28使用的木马",
        malware_types=["trojan", "backdoor"]
    )
    
    # 创建关系
    manager.create_relationship(
        indicator['id'], actor['id'], 'indicates'
    )
    manager.create_relationship(
        actor['id'], malware['id'], 'uses'
    )
    
    print("威胁知识图谱创建完成")
```

---

## 七、威胁情报消费实践

### 7.1 IOC匹配检测

```python
#!/usr/bin/env python3
"""IOC匹配引擎 - 将威胁情报应用于安全日志"""
import re
import ipaddress
import hashlib
from collections import defaultdict
from datetime import datetime

class IOCMatcher:
    """IOC匹配引擎"""
    
    def __init__(self):
        self.iocs = {
            'ip': set(),
            'domain': set(),
            'url': set(),
            'md5': set(),
            'sha1': set(),
            'sha256': set(),
            'email': set(),
        }
        self.ioc_metadata = {}
    
    def load_iocs(self, ioc_list):
        """加载IOC列表"""
        for ioc in ioc_list:
            ioc_type = ioc.get('type', '')
            ioc_value = ioc.get('value', '')
            
            if ioc_type in self.iocs:
                self.iocs[ioc_type].add(ioc_value.lower())
                self.ioc_metadata[ioc_value.lower()] = {
                    'type': ioc_type,
                    'confidence': ioc.get('confidence', 50),
                    'description': ioc.get('description', ''),
                    'tags': ioc.get('tags', []),
                    'source': ioc.get('source', 'unknown')
                }
        
        total = sum(len(v) for v in self.iocs.values())
        print(f"加载了 {total} 条IOC")
    
    def match_log_line(self, line):
        """匹配单行日志"""
        matches = []
        line_lower = line.lower()
        
        # IP匹配
        ip_pattern = r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b'
        for match in re.finditer(ip_pattern, line_lower):
            ip = match.group(1)
            if ip in self.iocs['ip']:
                matches.append({
                    'ioc_type': 'ip',
                    'ioc_value': ip,
                    'metadata': self.ioc_metadata[ip]
                })
        
        # 域名匹配
        domain_pattern = r'\b([a-zA-Z0-9][a-zA-Z0-9-]*\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?)\b'
        for match in re.finditer(domain_pattern, line_lower):
            domain = match.group(1)
            if domain in self.iocs['domain']:
                matches.append({
                    'ioc_type': 'domain',
                    'ioc_value': domain,
                    'metadata': self.ioc_metadata[domain]
                })
        
        # URL匹配
        url_pattern = r'(https?://[^\s<>"\'`]+)'
        for match in re.finditer(url_pattern, line_lower):
            url = match.group(1)
            if url in self.iocs['url']:
                matches.append({
                    'ioc_type': 'url',
                    'ioc_value': url,
                    'metadata': self.ioc_metadata[url]
                })
        
        # 哈希匹配
        for hash_len, hash_type in [(32, 'md5'), (40, 'sha1'), (64, 'sha256')]:
            hash_pattern = rf'\b([a-fA-F0-9]{{{hash_len}}})\b'
            for match in re.finditer(hash_pattern, line_lower):
                h = match.group(1)
                if h in self.iocs[hash_type]:
                    matches.append({
                        'ioc_type': hash_type,
                        'ioc_value': h,
                        'metadata': self.ioc_metadata[h]
                    })
        
        # 邮箱匹配
        email_pattern = r'\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b'
        for match in re.finditer(email_pattern, line_lower):
            email = match.group(1)
            if email in self.iocs['email']:
                matches.append({
                    'ioc_type': 'email',
                    'ioc_value': email,
                    'metadata': self.ioc_metadata[email]
                })
        
        return matches
    
    def match_file(self, file_path):
        """匹配整个日志文件"""
        all_matches = []
        
        with open(file_path, 'r', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                matches = self.match_log_line(line)
                if matches:
                    for m in matches:
                        all_matches.append({
                            'file': file_path,
                            'line_num': line_num,
                            'line': line.strip(),
                            'ioc': m
                        })
        
        return all_matches
    
    def generate_sigma_rule(self, ioc_list):
        """根据IOC生成Sigma检测规则"""
        sigma_rule = {
            'title': 'Threat Intelligence IOC Detection',
            'status': 'experimental',
            'description': 'Detects IOCs from threat intelligence feeds',
            'author': 'Threat Intelligence Team',
            'date': datetime.now().strftime('%Y/%m/%d'),
            'tags': ['attack.command_and_control'],
            'logsource': {
                'product': 'firewall',
                'category': 'network_connection'
            },
            'detection': {
                'selection': {},
                'condition': 'selection'
            },
            'falsepositives': ['Unknown'],
            'level': 'high'
        }
        
        # 按类型分组
        grouped = defaultdict(list)
        for ioc in ioc_list:
            if ioc['type'] in ('ip-src', 'ip-dst'):
                grouped['destinationip'].append(ioc['value'])
            elif ioc['type'] == 'domain':
                grouped['destinationhostname'].append(ioc['value'])
            elif ioc['type'] == 'url':
                grouped['requesturl'].append(ioc['value'])
        
        for field, values in grouped.items():
            sigma_rule['detection']['selection'][field] = values
        
        return sigma_rule

# 使用
if __name__ == "__main__":
    matcher = IOCMatcher()
    
    # 加载IOC
    iocs = [
        {'type': 'ip', 'value': '185.220.101.45', 'confidence': 90, 
         'description': 'APT28 C2', 'tags': ['APT28', 'C2']},
        {'type': 'domain', 'value': 'c2.evil.com', 'confidence': 85,
         'description': 'APT28 C2 domain', 'tags': ['APT28']},
        {'type': 'sha256', 'value': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
         'confidence': 95, 'description': 'APT28 malware sample', 'tags': ['APT28']},
    ]
    matcher.load_iocs(iocs)
    
    # 匹配日志
    matches = matcher.match_log_line(
        "Connection from 10.0.0.5 to 185.220.101.45 on port 443"
    )
    print(f"匹配到 {len(matches)} 个IOC")
    for m in matches:
        print(f"  {m['ioc_type']}: {m['ioc_value']} ({m['metadata']['description']})")
```

### 7.2 APT追踪

```python
#!/usr/bin/env python3
"""APT组织追踪工具 - 基于MITRE ATT&CK映射"""
from collections import defaultdict

class APTTracker:
    """APT组织活动追踪器"""
    
    APT_GROUPS = {
        'APT28': {
            'aliases': ['Fancy Bear', 'Sofacy', 'STRONTIUM'],
            'origin': 'Russia',
            'targets': ['Government', 'Military', 'Energy'],
            'tools': ['Mimikatz', 'PowerShell Empire', 'Zebrocy'],
            'techniques': ['T1566.001', 'T1059.001', 'T1003.001', 'T1071.001'],
            'sectors': ['Defense', 'Government', 'Energy']
        },
        'APT29': {
            'aliases': ['Cozy Bear', 'The Dukes', 'Nobelium'],
            'origin': 'Russia',
            'targets': ['Government', 'Think Tanks', 'Healthcare'],
            'tools': ['SUNBURST', 'EnvyScout', 'FoggyWeb'],
            'techniques': ['T1195.002', 'T1547.001', 'T1078'],
            'sectors': ['Government', 'IT', 'Healthcare']
        },
        'APT41': {
            'aliases': ['Winnti', 'Barium', 'Double Dragon'],
            'origin': 'China',
            'targets': ['Gaming', 'Healthcare', 'Telecom'],
            'tools': ['Winnti', 'PlugX', 'Cobalt Strike'],
            'techniques': ['T1055', 'T1059.003', 'T1543.001'],
            'sectors': ['Gaming', 'Healthcare', 'Telecom']
        },
        'Lazarus': {
            'aliases': ['Hidden Cobra', 'Guardians of Peace'],
            'origin': 'North Korea',
            'targets': ['Financial', 'Defense', 'Media'],
            'tools': ['Manuscrypt', 'BambooDoor', 'MISTPEN'],
            'techniques': ['T1566.002', 'T1059.001', 'T1027'],
            'sectors': ['Financial', 'Defense', 'Cryptocurrency']
        }
    }
    
    def identify_by_technique(self, observed_techniques):
        """通过观察到的ATT&CK技术识别APT组织"""
        scores = defaultdict(int)
        
        for group_name, group_info in self.APT_GROUPS.items():
            overlap = set(observed_techniques) & set(group_info['techniques'])
            score = len(overlap) / len(group_info['techniques']) * 100
            scores[group_name] = {
                'score': round(score, 1),
                'matched': list(overlap),
                'unmatched': list(set(group_info['techniques']) - set(observed_techniques))
            }
        
        return dict(sorted(scores.items(), key=lambda x: x[1]['score'], reverse=True))
    
    def identify_by_tool(self, observed_tools):
        """通过工具识别APT组织"""
        scores = defaultdict(int)
        
        for group_name, group_info in self.APT_GROUPS.items():
            overlap = set(observed_tools) & set(group_info['tools'].lower() for t in group_info['tools'] for t in [t])
            score = len(overlap)
            scores[group_name] = score
        
        return dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))
    
    def generate_threat_report(self, group_name, observed_data=None):
        """生成威胁报告"""
        if group_name not in self.APT_GROUPS:
            return None
        
        info = self.APT_GROUPS[group_name]
        report = {
            'group': group_name,
            'aliases': info['aliases'],
            'origin': info['origin'],
            'target_sectors': info['sectors'],
            'known_tools': info['tools'],
            'attck_techniques': info['techniques'],
            'recommendations': self._generate_recommendations(info)
        }
        
        if observed_data:
            report['observed'] = observed_data
            report['identification'] = self.identify_by_technique(
                observed_data.get('techniques', [])
            )
        
        return report
    
    def _generate_recommendations(self, group_info):
        """根据APT组织特征生成防御建议"""
        recommendations = []
        
        for technique in group_info['techniques']:
            if technique == 'T1566.001':
                recommendations.append('部署邮件安全网关和防钓鱼策略')
            elif technique == 'T1059.001':
                recommendations.append('启用PowerShell脚本日志和约束语言模式')
            elif technique == 'T1003.001':
                recommendations.append('部署LSASS保护(RunAsPPL)和凭据守卫')
            elif technique == 'T1071.001':
                recommendations.append('部署DNS监控和异常域名检测')
            elif technique == 'T1547.001':
                recommendations.append('监控注册表Run键和启动项')
            elif technique == 'T1195.002':
                recommendations.append('实施供应链安全验证')
        
        return list(set(recommendations))

# 使用
if __name__ == "__main__":
    tracker = APTTracker()
    
    # 通过技术识别APT
    observed = ['T1566.001', 'T1059.001', 'T1003.001', 'T1071.001']
    scores = tracker.identify_by_technique(observed)
    print("=== APT识别结果 ===")
    for group, info in scores.items():
        if info['score'] > 0:
            print(f"  {group}: {info['score']}% (匹配: {info['matched']})")
    
    # 生成威胁报告
    report = tracker.generate_threat_report('APT28')
    import json
    print("\n=== 威胁报告 ===")
    print(json.dumps(report, indent=2, ensure_ascii=False))
```

### 7.3 漏洞优先级排序

```python
#!/usr/bin/env python3
"""基于威胁情报的漏洞优先级排序"""
import requests
from datetime import datetime

class VulnPrioritizer:
    """漏洞优先级排序工具"""
    
    def __init__(self):
        self.kev_catalog = []  # CISA KEV已知利用漏洞
        self.load_kev()
    
    def load_kev(self):
        """加载CISA KEV目录"""
        try:
            resp = requests.get(
                "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json",
                timeout=30
            )
            if resp.status_code == 200:
                data = resp.json()
                self.kev_catalog = data.get('vulnerabilities', [])
                print(f"加载了 {len(self.kev_catalog)} 条已知利用漏洞")
        except Exception as e:
            print(f"加载KEV失败: {e}")
    
    def prioritize(self, vuln_list):
        """对漏洞列表进行优先级排序"""
        prioritized = []
        
        for vuln in vuln_list:
            cve_id = vuln.get('cve_id', '')
            cvss = vuln.get('cvss_score', 0)
            is_exploited = any(
                v.get('cveID') == cve_id for v in self.kev_catalog
            )
            has_exploit = vuln.get('public_exploit', False)
            asset_criticality = vuln.get('asset_criticality', 'medium')
            internet_facing = vuln.get('internet_facing', False)
            
            # 计算综合优先级分数
            score = 0
            
            # CVSS分数 (0-10) -> 权重40%
            score += cvss * 4
            
            # 已知利用 -> 权重30%
            if is_exploited:
                score += 30
            
            # 公开PoC -> 权重15%
            if has_exploit:
                score += 15
            
            # 资产重要性 -> 权重10%
            criticality_scores = {'critical': 10, 'high': 7, 'medium': 5, 'low': 2}
            score += criticality_scores.get(asset_criticality, 5)
            
            # 互联网暴露 -> 权重5%
            if internet_facing:
                score += 5
            
            # 确定优先级级别
            if score >= 70:
                priority = 'P0-紧急'
                sla = '24小时'
            elif score >= 50:
                priority = 'P1-高'
                sla = '7天'
            elif score >= 30:
                priority = 'P2-中'
                sla = '30天'
            else:
                priority = 'P3-低'
                sla = '90天'
            
            prioritized.append({
                'cve_id': cve_id,
                'cvss': cvss,
                'known_exploited': is_exploited,
                'has_exploit': has_exploit,
                'asset_criticality': asset_criticality,
                'internet_facing': internet_facing,
                'score': round(score, 1),
                'priority': priority,
                'sla': sla
            })
        
        return sorted(prioritized, key=lambda x: x['score'], reverse=True)

# 使用
if __name__ == "__main__":
    prioritizer = VulnPrioritizer()
    
    # 模拟漏洞列表
    vulns = [
        {'cve_id': 'CVE-2024-12345', 'cvss_score': 9.8, 
         'public_exploit': True, 'asset_criticality': 'critical', 
         'internet_facing': True},
        {'cve_id': 'CVE-2024-67890', 'cvss_score': 7.5,
         'public_exploit': False, 'asset_criticality': 'medium',
         'internet_facing': False},
        {'cve_id': 'CVE-2024-11111', 'cvss_score': 6.5,
         'public_exploit': True, 'asset_criticality': 'high',
         'internet_facing': True},
    ]
    
    results = prioritizer.prioritize(vulns)
    print("\n=== 漏洞优先级排序 ===")
    for r in results:
        print(f"  {r['cve_id']} | CVSS:{r['cvss']} | 分数:{r['score']} | {r['priority']} | SLA:{r['sla']}")
        print(f"    已知利用:{r['known_exploited']} | 公开PoC:{r['has_exploit']} | 暴露:{r['internet_facing']}")
```

---

## 八、实战案例: 从情报收集到检测规则生成全流程

### 8.1 案例背景

> **场景**: 安全团队收到情报，APT29组织正在利用新型恶意软件进行钓鱼攻击，目标为政府机构和医疗机构。需要从情报收集开始，完成处理、分析、STIX建模、TAXII传输，最终生成可部署的检测规则。

### 8.2 全流程实施

**步骤1: 情报收集**

```python
#!/usr/bin/env python3
"""Step 1: 情报收集"""
import requests
import json

# 1. 从开源情报源收集IOC
print("=== Step 1: 情报收集 ===")

# 收集URLhaus恶意URL
resp = requests.get("https://urlhaus.abuse.ch/api/v1/payloads/", timeout=30)
urlhaus_data = resp.json()
print(f"URLhaus: 收集到 {len(urlhaus_data.get('payloads', []))} 条")

# 收集ThreatFox IOC
resp = requests.get("https://threatfox-api.abuse.ch/api/v1/", params={"limit": 50}, timeout=30)
threatfox_data = resp.json()
print(f"ThreatFox: 收集到 {len(threatfox_data.get('data', []))} 条")

# 内部情报（来自EDR告警）
internal_iocs = [
    {"type": "ip", "value": "193.29.188.5", "source": "edr_alert", "confidence": 90,
     "description": "APT29疑似C2服务器"},
    {"type": "domain", "value": "secure-doc-share.com", "source": "edr_alert", "confidence": 85,
     "description": "APT29钓鱼域名"},
    {"type": "sha256", "value": "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef1234",
     "source": "edr_alert", "confidence": 95, "description": "APT29新型恶意样本"},
    {"type": "url", "value": "https://secure-doc-share.com/view.php?id=12345",
     "source": "edr_alert", "confidence": 88, "description": "APT29钓鱼链接"},
]
print(f"内部情报: 收集到 {len(internal_iocs)} 条")
```

**步骤2: 数据处理与富化**

```python
# Step 2: 数据处理
print("\n=== Step 2: 数据处理 ===")

# 标准化、去重、富化
all_iocs = []
# ... 合并各来源IOC ...

# 使用前面定义的IntelProcessor处理
processed_iocs = internal_iocs  # 简化示例
print(f"处理后IOC数量: {len(processed_iocs)}")

# 富化：查询VirusTotal
for ioc in processed_iocs:
    if ioc['type'] == 'sha256':
        # 查询VT（简化示例）
        ioc['vt_detection'] = "45/72"
        ioc['vt_tags'] = ['apt', 'trojan', 'cozybear']
    elif ioc['type'] == 'ip':
        ioc['geo'] = {'country': 'RU', 'isp': 'Unknown'}
    elif ioc['type'] == 'domain':
        ioc['dns'] = {'resolved_ip': '193.29.188.5', 'registrar': 'Njalla'}
```

**步骤3: STIX建模**

```python
# Step 3: STIX建模
print("\n=== Step 3: STIX建模 ===")

stix_bundle = {
    "type": "bundle",
    "id": "bundle--apt29-campaign-2024-001",
    "objects": [
        # Identity
        {
            "type": "identity",
            "spec_version": "2.1",
            "id": "identity--sec-team-alpha-001",
            "created": "2024-09-11T08:00:00.000Z",
            "modified": "2024-09-11T08:00:00.000Z",
            "name": "Security Team Alpha",
            "identity_class": "organization"
        },
        # Intrusion Set (APT29)
        {
            "type": "intrusion-set",
            "spec_version": "2.1",
            "id": "intrusion-set--apt29-2024",
            "created": "2024-09-11T08:00:00.000Z",
            "modified": "2024-09-11T08:00:00.000Z",
            "name": "APT29",
            "description": "俄罗斯APT组织Cozy Bear",
            "aliases": ["Cozy Bear", "The Dukes", "Nobelium"],
            "goals": ["intelligence-collection", "espionage"],
            "primary_motivation": "dominance"
        },
        # Indicators
        {
            "type": "indicator",
            "spec_version": "2.1",
            "id": "indicator--apt29-ip-001",
            "created": "2024-09-11T08:00:00.000Z",
            "modified": "2024-09-11T08:00:00.000Z",
            "name": "APT29 C2 IP",
            "pattern": "[ipv4-addr:value = '193.29.188.5']",
            "pattern_type": "stix",
            "indicator_types": ["malicious-activity"],
            "valid_from": "2024-09-11T08:00:00Z",
            "valid_until": "2024-12-11T08:00:00Z",
            "confidence": 90
        },
        {
            "type": "indicator",
            "spec_version": "2.1",
            "id": "indicator--apt29-domain-001",
            "created": "2024-09-11T08:00:00.000Z",
            "modified": "2024-09-11T08:00:00.000Z",
            "name": "APT29 Phishing Domain",
            "pattern": "[domain-name:value = 'secure-doc-share.com']",
            "pattern_type": "stix",
            "indicator_types": ["malicious-activity"],
            "valid_from": "2024-09-11T08:00:00Z",
            "valid_until": "2024-12-11T08:00:00Z",
            "confidence": 85
        },
        {
            "type": "indicator",
            "spec_version": "2.1",
            "id": "indicator--apt29-hash-001",
            "created": "2024-09-11T08:00:00.000Z",
            "modified": "2024-09-11T08:00:00.000Z",
            "name": "APT29 Malware Sample",
            "pattern": "[file:hashes.'SHA-256' = 'a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef1234']",
            "pattern_type": "stix",
            "indicator_types": ["malicious-activity"],
            "valid_from": "2024-09-11T08:00:00Z",
            "valid_until": "2024-12-11T08:00:00Z",
            "confidence": 95
        },
        # Relationships
        {
            "type": "relationship",
            "spec_version": "2.1",
            "id": "relationship--apt29-rel-001",
            "created": "2024-09-11T08:00:00.000Z",
            "modified": "2024-09-11T08:00:00.000Z",
            "relationship_type": "indicates",
            "source_ref": "indicator--apt29-ip-001",
            "target_ref": "intrusion-set--apt29-2024"
        },
        {
            "type": "relationship",
            "spec_version": "2.1",
            "id": "relationship--apt29-rel-002",
            "created": "2024-09-11T08:00:00.000Z",
            "modified": "2024-09-11T08:00:00.000Z",
            "relationship_type": "indicates",
            "source_ref": "indicator--apt29-domain-001",
            "target_ref": "intrusion-set--apt29-2024"
        },
        {
            "type": "relationship",
            "spec_version": "2.1",
            "id": "relationship--apt29-rel-003",
            "created": "2024-09-11T08:00:00.000Z",
            "modified": "2024-09-11T08:00:00.000Z",
            "relationship_type": "indicates",
            "source_ref": "indicator--apt29-hash-001",
            "target_ref": "intrusion-set--apt29-2024"
        }
    ]
}

print(f"STIX Bundle: {len(stix_bundle['objects'])} 个对象")
print(f"  - 1 Identity")
print(f"  - 1 Intrusion Set (APT29)")
print(f"  - 3 Indicators (IP, Domain, Hash)")
print(f"  - 3 Relationships")
```

**步骤4: TAXII传输**

```python
# Step 4: 通过TAXII传输
print("\n=== Step 4: TAXII传输 ===")

# 使用前面定义的TAXIIClient
# client = TAXIIClient(
#     base_url="https://taxii.internal.corp",
#     auth={'type': 'bearer', 'token': 'taxii_token'}
# )
# 
# # 推送到TAXII服务器
# status = client.add_objects(
#     api_root="https://taxii.internal.corp/trust-group1",
#     collection_id="apt-intelligence",
#     stix_bundle=stix_bundle
# )
# print(f"TAXII推送状态: {status}")

print("STIX Bundle已推送到TAXII服务器")
print("下游SIEM、防火墙、EDR将自动拉取最新情报")
```

**步骤5: 检测规则生成**

```python
# Step 5: 生成检测规则
print("\n=== Step 5: 检测规则生成 ===")

# Sigma规则
sigma_rule = {
    "title": "APT29 Infrastructure Detection",
    "status": "experimental",
    "description": "Detects network connections to known APT29 infrastructure",
    "author": "Threat Intelligence Team",
    "date": "2024-09-11",
    "tags": ["attack.command_and_control", "attack.t1071.001"],
    "logsource": {
        "product": "firewall",
        "category": "network_connection"
    },
    "detection": {
        "selection_ip": {
            "destinationip": ["193.29.188.5"]
        },
        "selection_domain": {
            "destinationhostname": ["secure-doc-share.com"]
        },
        "selection_url": {
            "requesturl|contains": ["secure-doc-share.com"]
        },
        "condition": "selection_ip or selection_domain or selection_url"
    },
    "falsepositives": ["Unknown"],
    "level": "critical"
}

# Suricata规则
suricata_rules = [
    'alert tcp $HOME_NET any -> $EXTERNAL_NET any '
    '(msg:"APT29 C2 Communication"; '
    'ip:dst_host; content:"193.29.188.5"; '
    'sid:2024091101; rev:1; '
    'classtype:trojan-activity; priority:1; '
    'metadata:source "threat_intel", tag "APT29", tag "C2";)',
    
    'alert tls $HOME_NET any -> $EXTERNAL_NET any '
    '(msg:"APT29 Phishing Domain"; '
    'tls.sni; content:"secure-doc-share.com"; '
    'sid:2024091102; rev:1; '
    'classtype:trojan-activity; priority:1; '
    'metadata:source "threat_intel", tag "APT29", tag "phishing";)',
]

# YARA规则
yara_rule = '''
rule APT29_Malware_Sample {
    meta:
        description = "APT29 new malware sample"
        author = "Threat Intelligence Team"
        date = "2024-09-11"
        hash = "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef1234"
        tags = ["APT29", "CozyBear", "trojan"]
    
    strings:
        $hash_sha256 = "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef1234"
        $suspicious_api1 = "InternetOpenA"
        $suspicious_api2 = "CreateProcessA"
        $suspicious_api3 = "VirtualAllocEx"
        $c2_pattern = /https?:\/\/secure-doc-share\.com[^\s]*/
    
    condition:
        uint16(0) == 0x5A4D and
        (
            $hash_sha256 or
            3 of ($suspicious_api*) or
            $c2_pattern
        )
}
'''

print("生成的检测规则:")
print(f"\n1. Sigma规则:\n{json.dumps(sigma_rule, indent=2)}")
print(f"\n2. Suricata规则 ({len(suricata_rules)} 条):")
for rule in suricata_rules:
    print(f"  {rule[:100]}...")
print(f"\n3. YARA规则:\n{yara_rule[:200]}...")
```

**步骤6: 部署与监控**

```python
# Step 6: 部署到安全设备
print("\n=== Step 6: 部署与监控 ===")

# 部署检查清单
deployment_checklist = {
    "SIEM (Splunk/Elastic)": {
        "status": "已部署",
        "rules": ["Sigma规则导入", "IOC自动匹配lookup表更新"],
        "auto_alert": True
    },
    "防火墙 (Palo Alto)": {
        "status": "已部署",
        "rules": ["IP封锁: 193.29.188.5", "域名封锁: secure-doc-share.com"],
        "auto_block": True
    },
    "EDR (CrowdStrike/Defender)": {
        "status": "已部署",
        "rules": ["SHA256检测规则", "行为检测规则"],
        "auto_quarantine": True
    },
    "IDS/IPS (Suricata)": {
        "status": "已部署",
        "rules": [f"{len(suricata_rules)}条Suricata规则"],
        "auto_alert": True
    },
    "邮件网关 (Proofpoint)": {
        "status": "已部署",
        "rules": ["钓鱼URL阻断", "发件人域名阻断"],
        "auto_quarantine": True
    }
}

print("部署状态:")
for device, config in deployment_checklist.items():
    print(f"  [{config['status']}] {device}")
    for rule in config['rules']:
        print(f"    - {rule}")

print("\n监控指标:")
print("  - SIEM告警阈值: P0级告警 -> 立即通知SOC")
print("  - 防火墙命中频率: 每日检查阻断统计")
print("  - EDR检出次数: 每日检查检测统计")
print("  - 情报有效期: 90天后自动过期")
print("  - IOC衰减检查: 30天无命中 -> 评估是否下线")
```

### 8.3 完整流程图

```
┌──────────────────────────────────────────────────────────────────┐
│              从情报收集到检测规则生成全流程                        │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [收集]                                                          │
│  ├── 开源情报 (URLhaus, ThreatFox, OTX)                          │
│  ├── 内部情报 (EDR告警, SIEM日志, 蜜罐)                          │
│  └── 商业情报 (VirusTotal, 商业TIP)                              │
│       │                                                          │
│       ▼                                                          │
│  [处理]                                                          │
│  ├── 标准化 (统一格式, 类型检测)                                  │
│  ├── 去重 (哈希去重)                                             │
│  └── 富化 (GeoIP, VT, DNS)                                       │
│       │                                                          │
│       ▼                                                          │
│  [分析]                                                          │
│  ├── APT归属分析 (ATT&CK映射)                                    │
│  ├── 关联分析 (IP-域名-样本关联)                                  │
│  └── 置信度评估                                                  │
│       │                                                          │
│       ▼                                                          │
│  [STIX建模]                                                      │
│  ├── Identity (情报生产者)                                        │
│  ├── Intrusion Set (APT29)                                       │
│  ├── Indicator (IP, Domain, Hash, URL)                           │
│  └── Relationship (indicates关系)                                 │
│       │                                                          │
│       ▼                                                          │
│  [TAXII传输]                                                     │
│  └── 推送到TAXII服务器 → 下游自动拉取                             │
│       │                                                          │
│       ▼                                                          │
│  [规则生成]                                                      │
│  ├── Sigma规则 (SIEM检测)                                        │
│  ├── Suricata规则 (NIDS检测)                                     │
│  ├── YARA规则 (EDR/文件检测)                                     │
│  └── 防火墙策略 (IP/域名阻断)                                     │
│       │                                                          │
│       ▼                                                          │
│  [部署监控]                                                      │
│  ├── SIEM自动告警                                                │
│  ├── 防火墙自动阻断                                               │
│  ├── EDR自动检测                                                 │
│  ├── IDS自动告警                                                 │
│  └── 邮件网关自动隔离                                             │
│       │                                                          │
│       ▼                                                          │
│  [反馈迭代]                                                      │
│  ├── 命中率监控                                                  │
│  ├── 误报率分析                                                  │
│  ├── IOC衰减检测                                                 │
│  └── 情报源优先级调整                                             │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### 8.4 关键经验总结

| 环节 | 关键经验 | 注意事项 |
|------|----------|----------|
| 收集 | 多源交叉验证，单一来源容易误判 | 控制API调用频率，避免限额耗尽 |
| 处理 | 去重是最重要的步骤，避免重复告警 | 自动化处理流程，减少人工 |
| 分析 | ATT&CK映射帮助识别APT组织 | 保持分析人员的专业能力 |
| 建模 | STIX关系建模是核心价值 | 保持版本一致(STIX 2.1) |
| 传输 | TAXII实现自动化分发 | 确保传输加密和认证 |
| 规则 | 多格式规则覆盖不同设备 | 规则需要定期更新和衰减 |
| 部署 | 自动化部署减少响应时间 | 灰度发布，避免误报影响业务 |
| 反馈 | 持续迭代优化情报质量 | 建立IOC生命周期管理机制 |

---

## 附录: 常用工具与资源

### 威胁情报源

| 名称 | 类型 | URL |
|------|------|-----|
| URLhaus | 恶意URL | https://urlhaus.abuse.ch |
| ThreatFox | IOC | https://threatfox.abuse.ch |
| MalwareBazaar | 恶意样本 | https://bazaar.abuse.ch |
| AbuseIPDB | 恶意IP | https://www.abuseipdb.com |
| PhishTank | 钓鱼URL | https://www.phishtank.com |
| AlienVault OTX | 综合情报 | https://otx.alienvault.com |
| VirusTotal | 综合查询 | https://www.virustotal.com |
| CISA KEV | 已知漏洞 | https://www.cisa.gov/kev |
| MITRE ATT&CK | 攻击技术 | https://attack.mitre.org |

### 标准与协议

| 标准 | 说明 | 官方URL |
|------|------|---------|
| STIX 2.1 | 情报结构化表达 | https://oasis-open.github.io/cti-documentation |
| TAXII 2.1 | 情报传输协议 | https://taxii.mitre.org |
| OpenIOC | 开放指标格式 | https://www.openioc.org |
| CybOX | 网络可观测对象 | https://cyboxproject.github.io |
| MAEC | 恶意软件行为编码 | https://maecproject.github.io |
| VERIS | 事件记录框架 | https://verisframework.org |

### Python库

```bash
# STIX/TAXII库
pip install stix2          # STIX 2.1库
pip install taxii2-client # TAXII 2.1客户端
pip install taxii2-server # TAXII 2.1服务器

# MISP库
pip install pymisp        # MISP Python SDK

# OpenCTI库
pip install pycti         # OpenCTI Python SDK

# 情报查询库
pip install vt-py         # VirusTotal SDK
pip install shodan        # Shodan SDK
pip install censys        # Censys SDK
```
