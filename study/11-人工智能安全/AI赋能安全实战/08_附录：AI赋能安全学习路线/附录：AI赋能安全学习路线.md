# 附录：AI赋能安全学习路线

### A. 技能矩阵

| 技能领域 | 核心技能 | 学习优先级 |
|----------|----------|-----------|
| 机器学习基础 | 监督/无监督学习、特征工程 | 高 |
| 深度学习 | CNN/RNN/Transformer、PyTorch/TensorFlow | 中 |
| 安全数据分析 | 日志分析、流量分析、特征提取 | 高 |
| 安全运营 | SIEM/SOAR/EDR、事件响应 | 高 |
| LLM应用 | Prompt工程、RAG、Agent | 高 |
| 编程能力 | Python/SQL、数据处理 | 高 |

### B. 推荐学习路径

```
阶段1: 基础建设 (1-2月)
├── 机器学习基础（Coursera/李宏毅）
├── Python数据分析（pandas/numpy/scikit-learn）
├── 网络安全基础（日志格式/协议/工具）
└── 实践: 使用scikit-learn做异常检测

阶段2: 深度学习 (2-3月)
├── 深度学习基础（吴恩达/CS231n）
├── PyTorch/TensorFlow框架
├── NLP基础（BERT/Transformer）
└── 实践: 构建恶意代码分类器

阶段3: 安全应用 (2-3月)
├── AI安全应用专题
├── 威胁检测/漏洞挖掘/安全运营
├── LLM安全应用（RAG/Agent）
└── 实践: 构建AI安全分析管道

阶段4: 进阶研究 (持续)
├── AI安全研究前沿
├── 对抗机器学习
├── AI Agent安全运营
└── 开源贡献/论文阅读
```

### C. 常用数据集

| 数据集 | 类型 | 说明 |
|--------|------|------|
| NSL-KDD | 网络入侵检测 | 经典网络流量数据集 |
| CICIDS2017 | 网络入侵检测 | 现代网络攻击流量 |
| EMBER | 恶意代码检测 | PE文件静态特征 |
| Malimg | 恶意代码检测 | 恶意代码图像分类 |
| Phishing Corpus | 钓鱼检测 | 钓鱼邮件数据集 |
| Alexa/DMOA | 域名分类 | 正常/DGA域名 |
| DARPA TC | 安全运营 | 威胁狩猎数据 |

---

## 🛠️ 补充：实战拓展

### 一、威胁检测工具清单与命令

#### 1. 网络入侵检测

##### Zeek (原 Bro) + ML 分析

```bash
# 安装 Zeek
# Ubuntu/Debian
sudo apt-get install zeek

# 使用 Zeek 分析 PCAP 文件，生成日志
zeek -r sample.pcap local

# 查看生成的日志文件
ls *.log
# conn.log - 连接日志
# dns.log  - DNS 日志
# http.log - HTTP 日志
# files.log - 文件传输日志
```

```python
#!/usr/bin/env python3
"""
使用机器学习进行网络异常检测（基于 Zeek conn.log）
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder, StandardScaler

# 读取 Zeek 连接日志
def load_zeek_conn_log(log_path):
    """加载 Zeek conn.log 文件"""
    columns = [
        "ts", "uid", "id.orig_h", "id.orig_p", "id.resp_h", "id.resp_p",
        "proto", "service", "duration", "orig_bytes", "resp_bytes",
        "conn_state", "local_orig", "local_resp", "missed_bytes",
        "history", "orig_pkts", "orig_ip_bytes", "resp_pkts", "resp_ip_bytes"
    ]
    df = pd.read_csv(log_path, sep="\t", comment="#", names=columns, header=None)
    return df

# 特征工程
def extract_features(df):
    """从连接日志中提取特征"""
    features = pd.DataFrame()

    # 数值特征
    features["duration"] = pd.to_numeric(df["duration"], errors="coerce").fillna(0)
    features["orig_bytes"] = pd.to_numeric(df["orig_bytes"], errors="coerce").fillna(0)
    features["resp_bytes"] = pd.to_numeric(df["resp_bytes"], errors="coerce").fillna(0)
    features["orig_pkts"] = pd.to_numeric(df["orig_pkts"], errors="coerce").fillna(0)
    features["resp_pkts"] = pd.to_numeric(df["resp_pkts"], errors="coerce").fillna(0)

    # 类别特征编码
    le_proto = LabelEncoder()
    features["proto"] = le_proto.fit_transform(df["proto"].fillna("unknown"))

    le_state = LabelEncoder()
    features["conn_state"] = le_state.fit_transform(df["conn_state"].fillna("unknown"))

    # 派生特征
    features["bytes_ratio"] = np.where(
        features["resp_bytes"] > 0,
        features["orig_bytes"] / features["resp_bytes"],
        0
    )
    features["pkt_ratio"] = np.where(
        features["resp_pkts"] > 0,
        features["orig_pkts"] / features["resp_pkts"],
        0
    )

    return features.fillna(0)

# 异常检测
def detect_anomalies(features, contamination=0.01):
    """使用孤立森林检测异常连接"""
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(features)

    model = IsolationForest(
        n_estimators=100,
        contamination=contamination,
        random_state=42,
    )
    predictions = model.fit_predict(X_scaled)

    # -1 表示异常，1 表示正常
    anomalies = predictions == -1
    return anomalies, model

if __name__ == "__main__":
    df = load_zeek_conn_log("conn.log")
    features = extract_features(df)
    anomalies, model = detect_anomalies(features)

    print(f"总连接数: {len(df)}")
    print(f"异常连接数: {sum(anomalies)}")
    print(f"异常比例: {sum(anomalies)/len(df):.2%}")

    # 输出异常连接详情
    if sum(anomalies) > 0:
        print("\n异常连接示例:")
        print(df[anomalies][["id.orig_h", "id.resp_h", "id.resp_p",
                              "proto", "duration", "orig_bytes", "resp_bytes"]].head(10))
```

#### 2. 恶意代码检测

##### EMBER 数据集 + LightGBM

```bash
# 安装依赖
pip install ember lightgbm pefile

# 下载 EMBER 数据集
# https://github.com/elastic/ember
```

```python
#!/usr/bin/env python3
"""
基于 EMBER 特征的恶意代码检测
"""
import ember
import lightgbm as lgb
import numpy as np

# 训练模型（使用 EMBER 数据集）
def train_ember_model(ember_dir, output_model_path):
    """训练 EMBER 恶意代码检测模型"""
    # 加载特征
    X_train, y_train, X_test, y_test = ember.read_vectorized_features(ember_dir)

    # 过滤掉未标注的样本（label == -1）
    train_mask = y_train != -1
    test_mask = y_test != -1

    X_train_clean = X_train[train_mask]
    y_train_clean = y_train[train_mask]
    X_test_clean = X_test[test_mask]
    y_test_clean = y_test[test_mask]

    # 创建 LightGBM 数据集
    lgb_train = lgb.Dataset(X_train_clean, y_train_clean)
    lgb_test = lgb.Dataset(X_test_clean, y_test_clean, reference=lgb_train)

    # 模型参数
    params = {
        "boosting_type": "gbdt",
        "objective": "binary",
        "metric": "auc",
        "num_leaves": 1024,
        "learning_rate": 0.05,
        "feature_fraction": 0.8,
        "bagging_fraction": 0.8,
        "bagging_freq": 5,
        "verbose": 1,
    }

    # 训练
    model = lgb.train(
        params,
        lgb_train,
        num_boost_round=1000,
        valid_sets=[lgb_test],
        callbacks=[lgb.early_stopping(50)],
    )

    # 保存模型
    model.save_model(output_model_path)
    print(f"模型已保存到 {output_model_path}")
    return model

# 预测单个 PE 文件
def predict_pe_file(model, pe_path):
    """预测单个 PE 文件是否为恶意代码"""
    import pefile

    # 使用 ember 提取特征
    extractor = ember.PEFeatureExtractor()
    with open(pe_path, "rb") as f:
        bytez = f.read()

    try:
        features = extractor.feature_vector(bytez)
        score = model.predict([features])[0]
        return score  # 接近 1 表示恶意，接近 0 表示良性
    except Exception as e:
        print(f"提取特征失败: {e}")
        return None

if __name__ == "__main__":
    # 批量扫描目录下的 PE 文件
    import os

    model = lgb.Booster(model_file="ember_model.txt")
    scan_dir = "./scan_targets"

    results = []
    for root, dirs, files in os.walk(scan_dir):
        for fname in files:
            fpath = os.path.join(root, fname)
            score = predict_pe_file(model, fpath)
            if score is not None:
                is_malicious = score > 0.8  # 阈值可调
                results.append({"file": fpath, "score": score, "malicious": is_malicious})

    # 输出结果
    results.sort(key=lambda x: x["score"], reverse=True)
    print("\n扫描结果:")
    print("-" * 60)
    for r in results[:20]:  # 前 20 个最高风险
        flag = "[恶意]" if r["malicious"] else "[正常]"
        print(f"{flag} {r['score']:.4f} {r['file']}")
```

##### YARA 规则 + AI 辅助生成

```bash
# 安装 yara-python
pip install yara-python

# 安装 yara-gen (AI 辅助生成 YARA 规则)
pip install yara-gen
```

---

### 二、日志分析工具与命令

#### 1. ELK + ML 异常检测

```bash
# 使用 Docker 快速启动 ELK
docker pull docker.elastic.co/elasticsearch/elasticsearch:8.11.0
docker pull docker.elastic.co/kibana/kibana:8.11.0
docker pull docker.elastic.co/logstash/logstash:8.11.0

# 启动 Elasticsearch
docker run -d --name elasticsearch \
  -p 9200:9200 -p 9300:9300 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  docker.elastic.co/elasticsearch/elasticsearch:8.11.0

# 启动 Kibana
docker run -d --name kibana \
  -p 5601:5601 \
  --link elasticsearch:elasticsearch \
  docker.elastic.co/kibana/kibana:8.11.0
```

#### 2. Python 日志异常检测脚本

```python
#!/usr/bin/env python3
"""
安全日志异常检测：基于模板提取 + 异常检测
适用于检测 Web 日志、系统日志中的异常模式
"""
import re
import pandas as pd
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
import numpy as np

# Nginx 日志解析
def parse_nginx_log(log_path):
    """解析 Nginx access.log"""
    pattern = re.compile(
        r'(\d+\.\d+\.\d+\.\d+) - - \[(.*?)\] "(.*?)" (\d+) (\d+) "(.*?)" "(.*?)"'
    )

    records = []
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            m = pattern.match(line)
            if m:
                records.append({
                    "ip": m.group(1),
                    "time": m.group(2),
                    "request": m.group(3),
                    "status": int(m.group(4)),
                    "size": int(m.group(5)),
                    "referer": m.group(6),
                    "user_agent": m.group(7),
                })
    return pd.DataFrame(records)

# SQL 注入检测（基于关键词 + 特征）
def detect_sql_injection(requests):
    """简单的 SQL 注入请求检测"""
    sql_patterns = [
        r"(\bunion\b.*\bselect\b)",
        r"(\bselect\b.*\bfrom\b)",
        r"(\bor\b\s+['\"]?\d+['\"]?\s*=\s*['\"]?\d+)",
        r"(--\s|/\*|\*/)",
        r"(\bdrop\b.*\btable\b)",
        r"(\binsert\b.*\binto\b)",
        r"(\bupdate\b.*\bset\b)",
        r"(\bdelete\b.*\bfrom\b)",
        r"('\s+or\s+'1'='1)",
        r"(\bsleep\s*\(\s*\d+\s*\))",
    ]

    results = []
    for req in requests:
        score = 0
        matched = []
        for pat in sql_patterns:
            if re.search(pat, req, re.IGNORECASE):
                score += 1
                matched.append(pat)
        results.append({"request": req, "score": score, "matched": matched})

    return results

# 异常 IP 检测
def detect_anomalous_ips(df, top_n=10):
    """检测异常访问 IP（高频访问、高错误率）"""
    ip_stats = df.groupby("ip").agg(
        request_count=("request", "count"),
        error_rate=("status", lambda x: (x >= 400).mean()),
        unique_paths=("request", "nunique"),
    ).reset_index()

    # 综合评分
    ip_stats["risk_score"] = (
        ip_stats["request_count"].rank(pct=True) * 0.4
        + ip_stats["error_rate"].rank(pct=True) * 0.4
        + ip_stats["unique_paths"].rank(pct=True) * 0.2
    )

    return ip_stats.sort_values("risk_score", ascending=False).head(top_n)

# 使用聚类发现异常请求
def cluster_requests(requests, eps=0.5, min_samples=5):
    """使用 DBSCAN 聚类发现异常请求模式"""
    vectorizer = TfidfVectorizer(analyzer="char", ngram_range=(2, 4), max_features=1000)
    X = vectorizer.fit_transform(requests)

    clustering = DBSCAN(eps=eps, min_samples=min_samples, metric="cosine")
    labels = clustering.fit_predict(X)

    # -1 表示噪声点（异常）
    anomaly_indices = np.where(labels == -1)[0]
    return labels, anomaly_indices, vectorizer

if __name__ == "__main__":
    # 解析日志
    df = parse_nginx_log("access.log")
    print(f"共解析 {len(df)} 条日志")

    # SQL 注入检测
    sql_results = detect_sql_injection(df["request"].tolist())
    high_risk = [r for r in sql_results if r["score"] >= 2]
    print(f"\nSQL 注入高风险请求: {len(high_risk)} 条")
    for r in high_risk[:10]:
        print(f"  [得分{r['score']}] {r['request'][:80]}")

    # 异常 IP 检测
    risky_ips = detect_anomalous_ips(df)
    print("\n高风险 IP:")
    for _, row in risky_ips.iterrows():
        print(
            f"  {row['ip']:15s} 请求数:{row['request_count']:5d} "
            f"错误率:{row['error_rate']:.1%} 风险分:{row['risk_score']:.3f}"
        )
```

---

### 三、AI 安全运营工具清单

#### 1. 威胁情报分析

```python
#!/usr/bin/env python3
"""
AI 辅助威胁情报分析：IOC 提取与关联分析
"""
import re
from collections import defaultdict

# IOC (Indicator of Compromise) 提取
def extract_iocs(text):
    """从文本中提取 IOC"""
    iocs = {
        "ipv4": [],
        "domains": [],
        "urls": [],
        "md5": [],
        "sha256": [],
        "emails": [],
    }

    # IPv4 地址
    ipv4_pattern = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
    iocs["ipv4"] = re.findall(ipv4_pattern, text)

    # 域名
    domain_pattern = r"\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b"
    iocs["domains"] = re.findall(domain_pattern, text)

    # URL
    url_pattern = r"https?://[^\s<>\"']+"
    iocs["urls"] = re.findall(url_pattern, text)

    # MD5
    md5_pattern = r"\b[a-fA-F0-9]{32}\b"
    iocs["md5"] = re.findall(md5_pattern, text)

    # SHA256
    sha256_pattern = r"\b[a-fA-F0-9]{64}\b"
    iocs["sha256"] = re.findall(sha256_pattern, text)

    # Email
    email_pattern = r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"
    iocs["emails"] = re.findall(email_pattern, text)

    # 去重
    for key in iocs:
        iocs[key] = list(set(iocs[key]))

    return iocs

# MITRE ATT&CK 映射（简化版）
def map_to_mitre(tactics_keywords):
    """将攻击行为关键词映射到 MITRE ATT&CK 战术"""
    mitre_mapping = {
        "初始访问": ["phishing", "钓鱼", "exploit", "漏洞利用", "brute force", "暴力破解"],
        "执行": ["execute", "执行", "malware", "恶意代码", "script", "脚本"],
        "持久化": ["persistence", "持久化", "registry", "注册表", "service", "服务"],
        "权限提升": ["privilege escalation", "提权", "uac", "bypass", "绕过"],
        "防御规避": ["evasion", "规避", "obfuscate", "混淆", "antivirus", "杀软"],
        "凭证访问": ["credential", "凭证", "password", "密码", "hash", "哈希"],
        "发现": ["discovery", "发现", "scan", "扫描", "recon", "侦察"],
        "横向移动": ["lateral", "横向", "psexec", "wmi", "smb"],
        "数据收集": ["collect", "收集", "exfiltrate", "窃取"],
        "指挥控制": ["c2", "command", "control", "beacon", "回连"],
        "数据窃取": ["exfiltration", "数据泄露", "transfer", "传输"],
        "影响": ["impact", "破坏", "ransomware", "勒索", "dos", "拒绝服务"],
    }

    matched_tactics = []
    for tactic, keywords in mitre_mapping.items():
        for kw in keywords:
            if kw.lower() in " ".join(tactics_keywords).lower():
                matched_tactics.append(tactic)
                break

    return matched_tactics
```

#### 2. 安全编排自动化 (SOAR) 脚本模板

```python
#!/usr/bin/env python3
"""
AI 辅助安全事件响应自动化脚本模板
"""
import json
from datetime import datetime

class SecurityIncident:
    """安全事件类"""
    def __init__(self, event_data):
        self.id = event_data.get("event_id", "")
        self.type = event_data.get("event_type", "")
        self.severity = event_data.get("severity", "low")
        self.source_ip = event_data.get("source_ip", "")
        self.target_ip = event_data.get("target_ip", "")
        self.timestamp = event_data.get("timestamp", datetime.now().isoformat())
        self.raw_data = event_data

    def analyze(self):
        """AI 分析事件严重程度"""
        score = 0

        # 基于事件类型评分
        severity_map = {
            "malware": 80,
            "ransomware": 100,
            "sql_injection": 60,
            "brute_force": 40,
            "phishing": 50,
            "data_exfiltration": 90,
        }
        score += severity_map.get(self.type, 30)

        # 基于资产重要性（示例）
        critical_assets = ["192.168.1.100", "10.0.0.50"]
        if self.target_ip in critical_assets:
            score += 20

        # 自动定级
        if score >= 80:
            self.severity = "critical"
        elif score >= 60:
            self.severity = "high"
        elif score >= 40:
            self.severity = "medium"
        else:
            self.severity = "low"

        return score

    def auto_response(self):
        """自动响应动作"""
        responses = []

        if self.severity == "critical":
            responses.extend([
                "立即隔离受影响主机",
                "启动应急响应流程",
                "通知安全团队负责人",
                "保全现场证据",
            ])
        elif self.severity == "high":
            responses.extend([
                "阻断源 IP 访问",
                "深度扫描受影响系统",
                "通知安全分析师",
            ])
        elif self.severity == "medium":
            responses.extend([
                "增加监控频率",
                "人工复核告警",
            ])
        else:
            responses.append("记录日志，持续观察")

        return responses

# 使用示例
if __name__ == "__main__":
    event = {
        "event_id": "INC-2024-001",
        "event_type": "ransomware",
        "source_ip": "192.168.1.50",
        "target_ip": "192.168.1.100",
        "severity": "high",
    }

    incident = SecurityIncident(event)
    score = incident.analyze()
    responses = incident.auto_response()

    print(f"事件 ID: {incident.id}")
    print(f"风险评分: {score}")
    print(f"严重等级: {incident.severity}")
    print("建议响应动作:")
    for i, action in enumerate(responses, 1):
        print(f"  {i}. {action}")
```

---

### 四、AI 安全工具速查表

| 分类 | 工具 | 用途 | 安装命令 |
|------|------|------|---------|
| 威胁检测 | Zeek | 网络流量分析 | `apt install zeek` |
| 威胁检测 | Suricata | IDS/IPS | `apt install suricata` |
| 恶意代码 | EMBER | PE 恶意代码检测 | `pip install ember` |
| 恶意代码 | YARA | 规则匹配检测 | `pip install yara-python` |
| 日志分析 | ELK Stack | 日志收集分析 | Docker 部署 |
| 日志分析 | Splunk |  SIEM 平台 | 商业软件 |
| 异常检测 | scikit-learn | ML 算法库 | `pip install scikit-learn` |
| 异常检测 | PyOD | 异常检测库 | `pip install pyod` |
| 威胁情报 | MISP | 威胁情报平台 | Docker 部署 |
| 威胁情报 | OpenCTI | CTI 平台 | Docker 部署 |
| 漏洞挖掘 | CodeLlama | AI 代码审计 | `pip install transformers` |
| 漏洞挖掘 | Semgrep | 静态代码分析 | `pip install semgrep` |
| SOAR | Shuffle | 开源 SOAR | Docker 部署 |
| 安全运营 | DFIR-IRIS | 事件响应平台 | Docker 部署 |

---

### 五、环境搭建一键脚本

```bash
#!/bin/bash
# AI 安全实战环境搭建脚本

# 创建 conda 环境
conda create -n ai-sec python=3.10 -y
conda activate ai-sec

# 核心机器学习库
pip install numpy pandas scikit-learn matplotlib seaborn jupyter

# 深度学习框架
pip install torch torchvision transformers

# 安全分析库
pip install pefile yara-python scapy

# 异常检测
pip install pyod imbalanced-learn

# 网络安全工具
pip install requests beautifulsoup4

# 可视化
pip install plotly networkx

# 验证安装
python -c "
import numpy, pandas, sklearn, torch
import pefile, yara
print('✓ 核心库安装成功')
print(f'  NumPy: {numpy.__version__}')
print(f'  scikit-learn: {sklearn.__version__}')
print(f'  PyTorch: {torch.__version__}')
"
```

---

> **免责声明：** 本文档所有技术内容仅用于安全研究、防御能力建设和授权安全测试。AI安全技术的应用应遵守相关法律法规和伦理准则。在使用LLM分析漏洞和生成利用代码时，请确保拥有合法授权并遵守负责任披露原则。

---

## 📋 内容审核与补充建议

> 针对「附录：AI赋能安全学习路线」部分的内容审核结果：已补充实战拓展内容

### ✅ 已补充
- ⌨️ 威胁检测工具（Zeek/EMBER/YARA）安装与使用命令
- 💻 网络入侵检测 ML 脚本（孤立森林）
- 💻 恶意代码检测完整示例（EMBER + LightGBM）
- 💻 安全日志异常检测脚本（Nginx 日志解析 + SQL注入检测 + IP 异常分析）
- 💻 IOC 提取与 MITRE ATT&CK 映射脚本
- 💻 安全事件自动响应（SOAR）模板
- 📊 AI 安全工具分类速查表
- 🛠️ 环境搭建一键脚本
