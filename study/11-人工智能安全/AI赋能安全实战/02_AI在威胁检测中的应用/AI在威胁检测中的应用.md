# AI在威胁检测中的应用

### 2.1 入侵检测/异常检测

#### 2.1.1 基于ML的网络异常检测

传统的网络入侵检测系统（IDS）主要依赖签名规则（如Snort/Suricata规则集），无法检测未知攻击和零日漏洞。机器学习通过学习正常网络流量模式，能够发现偏离基线的异常行为。

```
网络异常检测技术路线:
┌────────────────────────────────────────────────────┐
│              数据采集层                             │
│  NetFlow / PCAP / Zeek日志 / Syslog               │
├────────────────────────────────────────────────────┤
│              特征工程层                             │
│  ├── 流量统计特征: 包数/字节数/持续时间/速率        │
│  ├── 连接特征: 源/目的IP/端口/协议/状态            │
│  ├── 时间特征: 时间窗口/周期性/突发性              │
│  ├── 内容特征: 负载熵/有效载荷特征                  │
│  └── 图特征: 通信拓扑/中心性/社区结构               │
├────────────────────────────────────────────────────┤
│              模型层                                 │
│  ├── 无监督: Isolation Forest / One-Class SVM     │
│  ├── 无监督: Autoencoder / DBSCAN                  │
│  ├── 半监督: DeepSVDD / Deviation Networks        │
│  └── 监督: Random Forest / XGBoost / LSTM         │
├────────────────────────────────────────────────────┤
│              决策层                                 │
│  异常评分 → 阈值判断 → 告警 → 上下文富化           │
└────────────────────────────────────────────────────┘
```

**常用算法对比：**

| 算法 | 类型 | 优势 | 劣势 | 适用场景 |
|------|------|------|------|----------|
| Isolation Forest | 无监督 | 高效、可扩展 | 高维数据性能下降 | 大规模流量异常 |
| One-Class SVM | 无监督 | 理论成熟 | 计算复杂度高 | 中等规模数据 |
| Autoencoder | 无监督 | 可学习复杂特征 | 训练数据需求大 | 流量重建/降维 |
| LSTM | 监督 | 时间序列建模 | 计算开销大 | 时序异常检测 |
| Random Forest | 监督 | 鲁棒性强 | 需要标注数据 | 已知攻击分类 |
| XGBoost | 监督 | 性能优异 | 需要标注数据 | 多分类攻击 |

**基于Isolation Forest的异常检测示例（概念示意）：**

```python
# 网络流量异常检测（概念示意，使用模拟数据）
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

class NetworkAnomalyDetector:
    def __init__(self):
        self.model = IsolationForest(
            n_estimators=200,
            contamination=0.05,  # 预期异常比例
            random_state=42
        )
        self.scaler = StandardScaler()
    
    def extract_features(self, flow_records):
        """从网络流记录中提取特征"""
        features = []
        for flow in flow_records:
            feat = [
                flow['packet_count'],
                flow['byte_count'],
                flow['duration'],
                flow['packet_rate'],
                flow['byte_rate'],
                flow['avg_packet_size'],
                flow['src_port_entropy'],
                flow['dst_port_entropy'],
                flow['tcp_flags_count'],
                flow['retransmission_count'],
            ]
            features.append(feat)
        return np.array(features)
    
    def train(self, normal_flows):
        """使用正常流量训练模型"""
        X = self.extract_features(normal_flows)
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled)
    
    def detect(self, flows):
        """检测异常流量"""
        X = self.extract_features(flows)
        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        scores = self.model.decision_function(X_scaled)
        # -1表示异常，1表示正常
        anomalies = [
            {'flow': f, 'score': s, 'is_anomaly': p == -1}
            for f, p, s in zip(flows, predictions, scores)
        ]
        return anomalies
```

#### 2.1.2 UEBA（用户与实体行为分析）

UEBA利用机器学习建立用户和实体（设备/应用/服务器）的行为基线，检测异常行为：

```
UEBA分析维度:
├── 用户行为基线
│   ├── 登录时间/频率/位置模式
│   ├── 资源访问模式（文件/数据库/应用）
│   ├── 命令执行模式
│   └── 数据访问量变化
│
├── 实体行为基线
│   ├── 服务器通信模式
│   ├── 设备网络行为
│   ├── 应用API调用模式
│   └── 数据流转模式
│
├── 异常场景
│   ├── 账户被接管（异常登录位置/时间）
│   ├── 内部威胁（数据外传/权限滥用）
│   ├── 横向移动（异常横向连接）
│   ├── 权限提升（异常特权使用）
│   └── 数据泄露（异常数据量传输）
│
└── 风险评分模型
    ├── 多维度行为偏差打分
    ├── 时间衰减加权
    ├── 跨实体关联分析
    └── 动态阈值调整
```

### 2.2 恶意代码检测

#### 2.2.1 静态特征ML分类

静态分析不运行恶意代码，通过提取文件特征进行分类：

```
恶意代码静态特征提取:
├── PE文件特征（Windows可执行文件）
│   ├── 文件头信息: 编译时间/机器类型/子系统
│   ├── 节区信息: 节数/熵值/虚拟大小
│   ├── 导入函数: API调用模式
│   ├── 导出函数
│   ├── 资源信息
│   └── 数字签名状态
│
├── 字节级特征
│   ├── N-gram字节序列
│   ├── 字节熵直方图
│   └── 字节熵方差
│
├── 反汇编特征
│   ├── 指令频率统计
│   ├── 操作码N-gram
│   ├── 控制流图特征
│   └── 函数调用图
│
└── 字符串特征
    ├── API函数名字符串
    ├── URL/IP/域名字符串
    ├── 注册表路径
    └── 加密/混淆特征
```

**分类模型架构：**

```python
# 恶意代码分类器（概念示意）
class MalwareClassifier:
    def __init__(self):
        # 多种特征融合
        self.byte_model = None       # 字节级模型
        self.api_model = None       # API调用模型
        self.header_model = None     # PE头模型
        self.ensemble_model = None  # 融合模型
    
    def extract_byte_features(self, file_path):
        """提取字节级特征"""
        with open(file_path, 'rb') as f:
            byte_data = f.read()
        # 计算字节熵直方图
        hist = np.zeros(256)
        for b in byte_data:
            hist[b] += 1
        hist = hist / len(byte_data)
        # 计算熵
        entropy = -np.sum(hist[hist>0] * np.log2(hist[hist>0]))
        # N-gram特征
        ngrams = self.extract_ngrams(byte_data, n=4)
        return np.concatenate([hist, [entropy], ngrams])
    
    def extract_api_features(self, file_path):
        """提取API调用特征"""
        # 使用静态分析工具提取导入函数
        # 简化示意
        api_list = ['CreateFile', 'WriteFile', 'RegOpenKey', 
                    'InternetOpen', 'socket', 'VirtualAlloc']
        features = np.zeros(len(api_list))
        # 标记API是否被使用
        return features
    
    def classify(self, file_path):
        """融合多特征分类"""
        byte_feat = self.extract_byte_features(file_path)
        api_feat = self.extract_api_features(file_path)
        all_features = np.concatenate([byte_feat, api_feat])
        prediction = self.ensemble_model.predict([all_features])
        return {
            'label': 'malicious' if prediction[0] == 1 else 'benign',
            'confidence': self.ensemble_model.predict_proba([all_features])[0]
        }
```

#### 2.2.2 深度学习恶意软件分类

深度学习能够自动学习特征表示，减少手工特征工程的需求：

```
深度学习恶意代码检测架构:
├── 卷积神经网络(CNN)
│   ├── 输入: 字节序列转图像 / API调用序列
│   ├── 特征: 自动学习空间特征
│   └── 优势: 捕获局部模式
│
├── 循环神经网络(RNN/LSTM/GRU)
│   ├── 输入: API调用序列 / 指令序列
│   ├── 特征: 捕获时序依赖
│   └── 优势: 建模执行流程
│
├── Transformer
│   ├── 输入: 字节/指令序列
│   ├── 特征: 自注意力机制
│   └── 优势: 长序列依赖建模
│
├── 图神经网络(GNN)
│   ├── 输入: 函数调用图 / 控制流图
│   ├── 特征: 图拓扑结构
│   └── 优势: 捕获代码结构关系
│
└── 多模态融合
    ├── 融合: 字节特征 + API特征 + 图特征
    ├── 方法: 多输入神经网络
    └── 优势: 综合多维度信息
```

### 2.3 钓鱼检测

#### 2.3.1 NLP分析钓鱼邮件

钓鱼邮件检测结合自然语言处理和机器学习，从邮件文本内容中识别钓鱼意图：

```
钓鱼邮件检测特征体系:
├── 文本内容特征
│   ├── 紧迫性语言: "立即"/"紧急"/"24小时内"
│   ├── 威胁性语言: "关闭账户"/"法律行动"
│   ├── 利益诱导: "中奖"/"退款"/"免费"
│   ├── 权威伪装: 冒充银行/政府/上级
│   ├── 语法错误: 非母语攻击者特征
│   └── 文本相似度: 与已知钓鱼邮件比对
│
├── URL特征
│   ├── 域名年龄/注册时间
│   ├── 域名相似度（与合法域名）
│   ├── URL长度/深度/特殊字符
│   ├── IP地址URL（无域名）
│   ├── URL重定向链
│   └── 证书信息
│
├── 邮件头特征
│   ├── SPF/DKIM/DMARC验证结果
│   ├── 发件域信誉
│   ├── 邮件路径异常
│   └── 回复地址不一致
│
└── 行为特征
    ├── 发送时间异常（非工作时间批量发送）
    ├── 发送模式异常（大规模群发）
    └── 收件人模式（跨组织发送）
```

**NLP钓鱼检测流程：**

```python
# 钓鱼邮件NLP检测（概念示意）
from transformers import pipeline
import re

class PhishingEmailDetector:
    def __init__(self):
        # 使用预训练模型进行文本分类
        self.classifier = pipeline(
            "text-classification",
            model="bert-base-uncased",  # 示意
        )
        # 钓鱼关键词模式
        self.urgency_patterns = [
            r'(?i)(urgent|immediate|24 hours|account.*suspended)',
            r'(?i)(verify.*identity|confirm.*password|update.*information)',
            r'(?i)(click.*here|login.*immediately|security alert)',
        ]
    
    def extract_features(self, email_text, email_headers):
        """提取多维度特征"""
        features = {
            'urgency_score': self._urgency_score(email_text),
            'url_count': len(re.findall(r'https?://\S+', email_text)),
            'has_ip_url': self._has_ip_url(email_text),
            'sender_mismatch': self._check_sender(email_headers),
            'text_sentiment': self._sentiment_analysis(email_text),
            'grammar_errors': self._count_grammar_errors(email_text),
        }
        return features
    
    def detect(self, email_text, email_headers=None):
        """综合检测钓鱼邮件"""
        features = self.extract_features(email_text, email_headers)
        # NLP分类
        nlp_score = self.classifier(email_text[:512])
        # 综合评分
        risk_score = self._calculate_risk(features, nlp_score)
        return {
            'is_phishing': risk_score > 0.7,
            'risk_score': risk_score,
            'features': features,
            'indicators': self._get_indicators(features)
        }
```

#### 2.3.2 URL特征分类

```python
# URL钓鱼检测（概念示意）
class URLPhishingDetector:
    def __init__(self):
        self.features = [
            'url_length', 'domain_age', 'has_ip', 'has_at_symbol',
            'redirect_count', 'https_valid', 'subdomain_count',
            'tld_suspicious', 'shortening_service', 'page_rank',
        ]
    
    def extract_url_features(self, url):
        """提取URL特征"""
        features = {}
        features['url_length'] = len(url)
        features['has_ip'] = bool(re.match(
            r'https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', url
        ))
        features['has_at_symbol'] = '@' in url
        features['subdomain_count'] = url.count('.')
        features['has_dash'] = '-' in url.split('/')[2] if '/' in url else False
        # 域名年龄查询等
        return features
    
    def classify(self, url):
        features = self.extract_url_features(url)
        # 基于规则+ML的分类
        return self.model.predict([list(features.values())])
```

### 2.4 欺诈检测

```
欺诈检测AI应用:
├── 交易异常检测
│   ├── 基于规则的过滤（金额/频率/地点）
│   ├── 基于ML的异常评分（隔离森林/自编码器）
│   ├── 时序模式分析（LSTM建模交易序列）
│   └── 图分析（资金流转网络）
│
├── 行为生物特征
│   ├── 鼠标移动模式分析
│   ├── 键盘输入节奏（击键间隔/持续时间）
│   ├── 触摸屏行为模式
│   ├── 设备指纹（硬件/软件特征）
│   └── 地理位置一致性
│
└── 关联分析
    ├── 多账户关联检测
    ├── 设备聚集分析
    └── 资金流网络分析
```

---

---

