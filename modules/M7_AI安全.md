# M7 AI 安全 · 详细补充

> **模块编号**：M7
> **所属阶段**：阶段三 · 方向深化
> **建议学习时机**：第 13-18 个月（有安全基础 + Python 编程基础后）
> **前置知识**：M1（Python 熟练）+ M4（Web 安全基础）+ 机器学习基础
> **每日投入**：2 小时（其中实验 ≥ 1.5 小时）
> **信息时效**：2026 年 9 月版（AI 领域迭代快，注意时效性）

---

## 1. 模块定位与前置知识

### 模块定位
AI 安全是 2025-2026 年最热门的安全方向之一。随着大语言模型（LLM）、生成式 AI 在各行各业的大规模落地，AI 带来的新安全问题也日益突出。AI 安全分为两大方向：

1. **AI 自身的安全（Security of AI）**：AI 模型和应用本身的漏洞与防护（如 Prompt 注入、模型窃取、数据投毒）
2. **AI 赋能安全（AI for Security）**：用 AI 技术提升安全能力（如 AI 辅助漏洞挖掘、AI 威胁检测、AI 钓鱼检测）

本模块以 **AI 自身的安全** 为主，兼顾 AI 赋能安全的应用，重点覆盖大语言模型（LLM）安全——这是当前就业需求最大、实战资源最多的方向。

### 前置知识
- **必选前置**：M1（Python 熟练，numpy / pandas 基础）+ M4（Web 安全基础）
- **推荐前置**：机器学习基础（监督学习、神经网络、深度学习概念）
- **数学基础**：线性代数、概率统计基础（不要求精通，但概念要懂）
- **环境要求**：Python + PyTorch / TensorFlow + HuggingFace + 本地 LLM 部署能力
- **硬件建议**：有 GPU 最佳（RTX 3060 以上），没有也可以用 Colab / 云 GPU

### AI 安全能力分级

| 级别 | 能力描述 | 对应阶段 |
|------|---------|---------|
| **L1 入门** | 理解 AI 基本概念、知道常见 AI 安全风险、会用工具做基础检测 | 阶段三中 |
| **L2 实用** | 能做 LLM 安全测试、理解 Prompt 注入等常见攻击、会部署基础防护 | 阶段三末 |
| **L3 熟练** | 能做 AI 红队测试、理解模型层面攻击原理、能设计防御方案 | 阶段四初 |
| **L4 精通** | AI 安全研究、前沿攻击/防御、参与标准制定 | 持续精进 |

---

## 2. 知识图谱

```
AI 安全知识体系
├── AI 基础（前置知识补齐）
│   ├── 机器学习基础
│   │   ├── 监督学习 / 无监督学习 / 强化学习
│   │   ├── 常见算法：线性回归 / 逻辑回归 / 决策树 / SVM / 聚类
│   │   ├── 模型评估：准确率 / 精确率 / 召回率 / F1 / ROC / AUC
│   │   ├── 过拟合与欠拟合 / 正则化
│   │   └── 训练 / 验证 / 测试集划分
│   ├── 深度学习基础
│   │   ├── 神经网络基础（神经元 / 激活函数 / 反向传播 / 梯度下降）
│   │   ├── CNN 卷积神经网络（图像）
│   │   ├── RNN / LSTM / GRU（序列）
│   │   ├── Transformer 架构 ⭐⭐⭐ 重点
│   │   │   ├── Self-Attention / Multi-Head Attention
│   │   │   ├── Encoder-Decoder 结构
│   │   │   ├── Positional Encoding
│   │   │   └── Transformer 变体
│   │   └── 训练技巧（优化器 / 学习率调度 / Batch Norm / Dropout）
│   ├── 大语言模型（LLM）基础 ⭐⭐⭐ 重中之重
│   │   ├── LLM 发展历程（GPT 系列 / BERT / Llama / Claude / 文心 / 通义）
│   │   ├── 预训练 / 微调 / RLHF / DPO
│   │   ├── Tokenization / 上下文窗口 / 生成原理
│   │   ├── RAG（检索增强生成）
│   │   ├── Agent 与工具调用（Function Calling / Tool Use）
│   │   ├── Prompt Engineering 基础
│   │   └── LLM 部署与推理（vLLM / Ollama / LlamaIndex / LangChain）
│   └── AI 开发工具
│       ├── PyTorch / TensorFlow（框架二选一，推荐 PyTorch）
│       ├── Hugging Face Transformers / Datasets
│       ├── scikit-learn
│       ├── Jupyter Notebook / Lab
│       ├── Ollama（本地大模型部署）
│       ├── LangChain / LlamaIndex（LLM 应用开发）
│       └── Google Colab / Kaggle Notebooks（免费 GPU）
│
├── AI 安全总论
│   ├── AI 安全全景
│   │   ├── AI 安全 vs AI 伦理 vs AI 治理
│   │   ├── NIST AI RMF（AI 风险管理框架）
│   │   ├── ISO/IEC 42001 AI 管理体系
│   │   ├── 国内：《生成式 AI 服务管理暂行办法》
│   │   └── AI 安全威胁模型
│   ├── AI 安全威胁分类
│   │   ├── 数据层面：数据投毒 / 数据泄露 / 隐私泄露
│   │   ├── 模型层面：对抗样本 / 模型窃取 / 模型反转 / 后门攻击
│   │   ├── 应用层面：Prompt 注入 / 越权调用 / 输出滥用
│   │   └── 供应链：模型供应链 / 训练数据污染 / 插件漏洞
│   ├── OWASP Top 10 for LLM ⭐⭐⭐ 重点
│   │   ├── LLM01: Prompt Injection（提示注入）
│   │   ├── LLM02: Insecure Output Handling（不安全输出处理）
│   │   ├── LLM03: Training Data Poisoning（训练数据投毒）
│   │   ├── LLM04: Model Denial of Service（模型拒绝服务）
│   │   ├── LLM05: Supply Chain Vulnerabilities（供应链漏洞）
│   │   ├── LLM06: Sensitive Information Disclosure（敏感信息泄露）
│   │   ├── LLM07: Insecure Plugin Design（不安全的插件设计）
│   │   ├── LLM08: Excessive Agency（过度代理）
│   │   ├── LLM09: Overreliance（过度依赖）
│   │   └── LLM10: Model Theft（模型窃取）
│   └── MITRE ATLAS（Adversarial Threat Landscape for AI Systems）
│
├── LLM 安全（大语言模型安全）⭐⭐⭐ 核心
│   ├── Prompt 注入攻击
│   │   ├── 直接提示注入（Direct Prompt Injection）
│   │   │   ├── 角色扮演绕过（"忽略之前的指令"）
│   │   │   ├── 人格分裂 / DAN（Do Anything Now）
│   │   │   ├── 多语言绕过
│   │   │   ├── 编码绕过（Base64 / Unicode / 混淆）
│   │   │   └── 前缀注入 / 后缀注入
│   │   ├── 间接提示注入（Indirect Prompt Injection）
│   │   │   ├── 通过网页 / 文档 / 邮件注入
│   │   │   ├── RAG 场景下的注入
│   │   │   └── 工具调用返回结果注入
│   │   ├── 进阶注入技巧
│   │   │   ├── 多轮对话注入
│   │   │   ├── 思维链（CoT）注入
│   │   │   ├── 越狱（Jailbreak）技术
│   │   │   ├── 万能越狱（Universal Jailbreak）
│   │   │   └── 多模态注入（图片 / 音频中的隐藏指令）
│   │   └── Prompt 注入检测与防御
│   │       ├── 输入过滤与检测
│   │       ├── 输出过滤与检测
│   │       ├── 系统提示词加固
│   │       ├── Prompt 防火墙
│   │       └── LLM 作为裁判（LLM-as-a-Judge）
│   ├── LLM 数据与隐私安全
│   │   ├── 训练数据泄露（Training Data Leakage）
│   │   │   ├── 成员推理攻击（Membership Inference）
│   │   │   ├── 模型反演 / 数据提取
│   │   │   └── 记忆化攻击（Memorization Attack）
│   │   ├── 对话数据泄露
│   │   │   ├── 提示词泄露（System Prompt Extraction）
│   │   │   ├── 上下文数据泄露
│   │   │   └── 侧信道数据泄露
│   │   ├── 隐私保护技术
│   │   │   ├── 差分隐私（Differential Privacy）
│   │   │   ├── 联邦学习（Federated Learning）
│   │   │   ├── 同态加密（Homomorphic Encryption）
│   │   │   └── 数据脱敏 / 匿名化
│   ├── LLM 代理与工具安全
│   │   ├── Agent 架构与风险
│   │   ├── 工具调用（Function Calling）安全
│   │   │   ├── 越权调用
│   │   │   ├── 参数注入
│   │   │   ├── 命令注入
│   │   │   └── SSRF（通过工具调用访问内网）
│   │   ├── 插件/扩展安全
│   │   │   ├── 插件权限过大
│   │   │   ├── 插件漏洞利用
│   │   │   └── 恶意插件
│   │   ├── RAG 安全
│   │   │   ├── 检索结果投毒
│   │   │   ├── 知识库越权访问
│   │   │   └── 间接 Prompt 注入
│   │   └── 多 Agent 系统安全
│   ├── LLM 输出安全
│   │   ├── 有害内容生成（暴力 / 歧视 / 虚假信息）
│   │   ├── 深度伪造（Deepfake）检测与防范
│   │   ├── 代码生成安全（生成有漏洞的代码）
│   │   ├── 输出过滤与内容审核
│   │   ├── 对齐（Alignment）与 RLHF
│   │   └── 护栏（Guardrails）技术
│   ├── LLM 拒绝服务（DoS）
│   │   ├── 资源消耗攻击（长上下文 / 复杂推理）
│   │   ├── 无限循环攻击
│   │   ├── Prompt 膨胀攻击
│   │   └── API 滥用与成本攻击
│   └── LLM 红队测试
│       ├── LLM 红队方法论
│       ├── 测试维度（安全性 / 鲁棒性 / 公平性 / 隐私）
│       ├── 红队工具（Garak / PromptFoo / Inspect AI）
│       ├── 红队报告模板
│       └── 红蓝对抗（攻击方 vs 防御方）
│
├── 传统 ML 安全（机器学习安全）
│   ├── 对抗样本（Adversarial Examples）
│   │   ├── 对抗样本基本概念
│   │   ├── 白盒攻击 vs 黑盒攻击
│   │   ├── 常见攻击方法
│   │   │   ├── FGSM / BIM / PGD
│   │   │   ├── C&W 攻击
│   │   │   ├── DeepFool
│   │   │   └── 通用对抗扰动（UAP）
│   │   ├── 物理世界对抗样本
│   │   │   ├── 对抗贴纸 / 对抗眼镜
│   │   │   ├── 自动驾驶对抗路标
│   │   │   └── 人脸识别对抗攻击
│   │   └── 防御方法
│   │       ├── 对抗训练（Adversarial Training）
│   │       ├── 防御性蒸馏（Defensive Distillation）
│   │       ├── 输入变换 / 去噪
│   │       ├── 检测与拒绝
│   │       └── 梯度掩码与欺骗
│   ├── 数据投毒（Data Poisoning）
│   │   ├── 标签翻转攻击
│   │   ├── 后门攻击（Backdoor Attack）
│   │   │   ├── 触发器设计
│   │   │   ├── BadNets / Trojan Attack
│   │   │   ├── 清洁标签投毒
│   │   │   └── 后门检测与防御
│   │   └── 投毒防御
│   ├── 模型窃取（Model Stealing / Extraction）
│   │   ├── 模型窃取攻击原理
│   │   ├── 基于查询的模型窃取
│   │   ├── 模型水印与指纹
│   │   └── 防御方法
│   ├── 成员推理攻击
│   │   ├── 攻击原理
│   │   ├── 攻击方法
│   │   └── 防御方法
│   └── 模型反演攻击
│
├── AI 赋能安全（AI for Security）
│   ├── AI 在安全中的应用场景
│   │   ├── AI 辅助漏洞挖掘
│   │   │   ├── AI 代码审计（静态分析增强）
│   │   │   ├── AI Fuzzing（模糊测试增强）
│   │   │   └── AI 漏洞利用生成
│   │   ├── AI 威胁检测
│   │   │   ├── 异常检测（UEBA / 网络异常 / 主机异常）
│   │   │   ├── 恶意代码检测与分类
│   │   │   ├── 钓鱼邮件检测
│   │   │   └── 欺诈检测
│   │   ├── AI 安全运营
│   │   │   ├── AI 告警分诊与降噪
│   │   │   ├── AI 事件调查辅助
│   │   │   ├── AI 报告自动生成
│   │   │   └── AI SOAR 编排
│   │   ├── AI 身份安全
│   │   │   ├── 行为生物识别
│   │   │   ├── 异常登录检测
│   │   │   └── 风控系统
│   │   └── AI 深度伪造检测
│   ├── AI 安全产品与工具
│   │   ├── 商业产品（各大安全厂商的 AI 安全产品）
│   │   ├── 开源工具
│   │   │   ├── Microsoft Security Copilot
│   │   │   ├── Google Chronicle + AI
│   │   │   └── 各种开源 AI 安全项目
│   │   └── LLM 安全产品
│   │       ├── Lakera Guard
│   │       ├── Robust Intelligence
│   │       ├── HiddenLayer
│   │       └── 国内：百度 / 阿里 / 腾讯 / 华为 AI 安全方案
│   └── AI 安全的局限性
│       ├── 对抗攻击对 AI 安全产品的影响
│       ├── 误报与漏报的平衡
│       ├── 可解释性问题
│       └── 合规与隐私问题
│
├── AI 安全合规与治理
│   ├── 国际法规与标准
│   │   ├── 欧盟 AI Act（人工智能法案）
│   │   ├── NIST AI RMF（AI 风险管理框架）
│   │   ├── ISO/IEC 42001 AI 管理体系
│   │   └── OECD AI 原则
│   ├── 国内法规与标准
│   │   ├── 《生成式人工智能服务管理暂行办法》
│   │   ├── 《生成式人工智能服务安全基本要求》
│   │   ├── 《人工智能生成内容标识办法》
│   │   ├── 《个人信息保护法》（AI 数据相关）
│   │   └── 算法推荐管理规定
│   ├── AI 安全评估
│   │   ├── 生成式 AI 服务安全评估
│   │   ├── 算法备案
│   │   ├── 大模型安全评测体系
│   │   └── AI 红队评估服务
│   └── AI 伦理
│       ├── 公平性与偏见
│       ├── 可解释性与透明度
│       ├── 问责制
│       └── 人机协作
│
└── AI 安全工具链
    ├── LLM 安全测试
    │   ├── Garak（LLM 安全扫描框架）
    │   ├── PromptFoo（Prompt 注入测试）
    │   ├── Inspect AI（DeepMind 开源 AI 评估框架）
    │   ├── PyRIT（微软红队工具）
    │   ├── AVID（AI 漏洞数据库）
    │   └── Hugging Face Evaluate
    ├── 传统 ML 安全
    │   ├── Adversarial Robustness Toolbox (ART)（IBM）
    │   ├── TextAttack（NLP 对抗攻击）
    │   ├── Foolbox
    │   ├── CleverHans（已停止维护，了解历史）
    │   ├── Trojai（后门攻击）
    │   └── ModelScan（模型安全扫描）
    ├── LLM 护栏与防护
    │   ├── NVIDIA NeMo Guardrails
    │   ├── Guardrails AI
    │   ├── Lakera Guard
    │   ├── Rebuff（Prompt 注入检测）
    │   └── LangKit（LLM 监控）
    ├── LLM 应用开发
    │   ├── LangChain
    │   ├── LlamaIndex
    │   ├── Ollama（本地部署）
    │   ├── vLLM（推理加速）
    │   └── HuggingFace Transformers
    ├── 隐私计算
    │   ├── PySyft（联邦学习）
    │   ├── Opacus（差分隐私）
    │   └── TenSEAL（同态加密）
    └── AI 安全数据集与基准
        ├── HarmBench / AdvBench
        ├── MMLU / HellaSwag（通用评测）
        ├── TruthfulQA（真实性）
        ├── BBQ / CrowS-Pairs（偏见）
        └── CAIS 安全评测集
```

---

## 3. 学习顺序与时间表

### 总时长：约 5 个月（300 小时）

| 阶段 | 周次 | 学习内容 | 重点任务 | 实验目标 |
|------|------|---------|---------|---------|
| **AI 基础** | 第 1-3 周 | 机器学习基础 | 监督学习、模型评估、scikit-learn | 完成 3 个经典 ML 项目 |
| | 第 4-6 周 | 深度学习 + Transformer | PyTorch、CNN、Transformer 原理 | 手写简单 Transformer |
| | 第 7-8 周 | LLM 基础与应用开发 | LLM 原理、RAG、Agent、LangChain | 做一个 RAG 应用 |
| **LLM 安全** | 第 9-12 周 | OWASP Top 10 for LLM + Prompt 注入 | 各类 Prompt 注入技术、绕过手法 | Garak / PromptFoo 实战 |
| | 第 13-15 周 | LLM 数据隐私 + 输出安全 | 数据泄露、成员推理、护栏技术 | 部署 Guardrails |
| | 第 16-18 周 | Agent / 工具 / RAG 安全 | 工具调用漏洞、插件安全、RAG 注入 | 搭建有漏洞的 Agent 并攻击 |
| **ML 安全** | 第 19-21 周 | 对抗样本 + 数据投毒 | FGSM/PGD、对抗训练、后门攻击 | ART / TextAttack 实战 |
| **合规与治理** | 第 22-23 周 | AI 合规与标准 | 国内外法规、AI RMF、安全评估 | 完成一份安全评估报告 |
| **综合实战** | 第 24-25 周 | LLM 红队测试综合实战 | 完整 LLM 应用安全评估、报告输出 | 一次完整 LLM 红队项目 |

> **注意**：AI 领域发展极快，学习过程中要持续关注最新论文和安全事件。

---

## 4. 工具链与版本建议

### 4.1 LLM 安全测试工具

| 工具 | 开发者 | 用途 | 优先级 | 费用 |
|------|--------|------|--------|------|
| **Garak** | NVIDIA 开源 | LLM 安全扫描框架，模块化探测器 | ⭐⭐⭐ 必学 | 免费 |
| **PromptFoo** | 开源社区 | Prompt 注入测试 + 红队 + 评估 | ⭐⭐⭐ 必学 | 免费 |
| **PyRIT** | 微软 | Python 红队识别工具包 | ⭐⭐ 重要 | 免费 |
| **Inspect AI** | DeepMind / Google | AI 安全评估框架 | ⭐⭐ 重要 | 免费 |
| **Rebuff** | Protect AI | Prompt 注入检测器 | ⭐⭐ 推荐 | 免费 |
| **Lakera Guard** | Lakera | LLM 安全 API（商业） | ⭐⭐ 推荐 | 免费额度 + 付费 |
| **Guardrails AI** | Guardrails AI | 输出验证与护栏框架 | ⭐⭐ 重要 | 免费 + 付费 |
| **NVIDIA NeMo Guardrails** | NVIDIA | 对话式 AI 护栏 | ⭐⭐ 推荐 | 免费 |
| **LangKit** | WhyLabs | LLM 可观测性与监控 | ⭐ 选学 | 免费 + 付费 |

### 4.2 机器学习安全工具

| 工具 | 开发者 | 用途 | 优先级 |
|------|--------|------|--------|
| **Adversarial Robustness Toolbox (ART)** | IBM / MIT-IBM | ML 安全工具箱（攻击+防御） | ⭐⭐⭐ 必学 |
| **TextAttack** | QData / UVA | NLP 对抗攻击框架 | ⭐⭐⭐ 必学 |
| **Foolbox** | Bethge Lab | 对抗攻击库（PyTorch/TensorFlow） | ⭐⭐ 重要 |
| **ModelScan** | Protect AI | 模型文件安全扫描（检测恶意 pickle 等） | ⭐⭐ 推荐 |
| **TrojanZoo** | 特洛伊动物园 | 后门攻击统一框架 | ⭐⭐ 重要 |
| **BackdoorBox** | 清华大学 | 后门攻击与防御工具箱 | ⭐⭐ 推荐 |
| **Opacus** | Meta / PyTorch | 差分隐私训练库 | ⭐⭐ 重要 |
| **PySyft** | OpenMined | 联邦学习 / 隐私计算 | ⭐ 选学 |

### 4.3 LLM 开发与部署工具

| 工具 | 用途 | 优先级 |
|------|------|--------|
| **PyTorch** | 深度学习框架 | ⭐⭐⭐ 必用 |
| **Hugging Face Transformers** | 预训练模型库 | ⭐⭐⭐ 必用 |
| **Ollama** | 本地大模型一键部署 | ⭐⭐⭐ 必用 |
| **LangChain** | LLM 应用开发框架 | ⭐⭐⭐ 必用 |
| **LlamaIndex** | RAG 应用开发框架 | ⭐⭐ 重要 |
| **vLLM** | LLM 高性能推理 | ⭐⭐ 重要 |
| **Text Generation WebUI (Oobabooga)** | Web UI 本地模型推理 | ⭐⭐ 推荐 |
| **Jupyter Notebook / Lab** | 交互式实验环境 | ⭐⭐⭐ 必用 |

### 4.4 数据集与评测基准

| 数据集 | 用途 | 优先级 |
|--------|------|--------|
| **OWASP Top 10 for LLM** | LLM 安全风险标准 | ⭐⭐⭐ 必读 |
| **HarmBench** | 有害性评测基准 | ⭐⭐ 重要 |
| **AdvBench** | 对抗性提示基准 | ⭐⭐ 重要 |
| **TruthfulQA** | 真实性评测 | ⭐⭐ 重要 |
| **MMLU** | 通用能力评测 | ⭐ 选学 |
| **BBQ / CrowS-Pairs** | 偏见与公平性评测 | ⭐ 选学 |

---

## 5. 编程 / 脚本练习

### 5.1 Python + PyTorch 基础

```python
# 练习 1：用 PyTorch 实现一个简单的线性回归
# 练习 2：用 PyTorch 实现一个简单的 CNN（图像分类）
# 练习 3：用 HuggingFace Transformers 加载预训练模型做文本分类
# 练习 4：用 scikit-learn 训练一个分类器，评估准确率/精确率/召回率/F1
```

### 5.2 LLM 安全脚本练习

```python
# 练习 5：简单的 Prompt 注入检测
# - 基于关键词匹配
# - 基于相似度检测
# - 基于 LLM 自检测

def detect_prompt_injection(prompt: str) -> bool:
    """基础的 Prompt 注入检测（演示用，实际远不够）"""
    suspicious_patterns = [
        "ignore previous instructions",
        "ignore all previous",
        "forget everything",
        "you are now",
        "DAN",
        "do anything now",
        "system prompt",
        "reveal your instructions",
    ]
    for pattern in suspicious_patterns:
        if pattern.lower() in prompt.lower():
            return True
    return False

# 练习 6：用 Garak 扫描一个 LLM 应用，分析扫描结果
# 练习 7：用 PromptFoo 进行 Prompt 注入红队测试
# 练习 8：实现一个简单的输出过滤器（检测并过滤有害内容）
# 练习 9：用 LangChain + Guardrails 构建一个带安全护栏的应用
# 练习 10：写一个脚本，自动化测试一个 RAG 应用的间接注入漏洞
```

### 5.3 对抗样本练习

```python
# 练习 11：用 ART 库实现 FGSM 对抗攻击（图像分类模型）
from art.attacks.evasion import FastGradientMethod
from art.estimators.classification import PyTorchClassifier
# （具体代码见 ART 官方文档）

# 练习 12：用 TextAttack 对文本分类模型做对抗攻击
# 练习 13：实现简单的对抗训练，对比前后模型鲁棒性
# 练习 14：实现一个简单的成员推理攻击
# 练习 15：用 ModelScan 扫描模型文件的安全风险
```

### 5.4 LLM 红队工具开发

```python
# 练习 16：写一个 Prompt 注入 Fuzzer
# - 自动生成各种变体的注入 Prompt
# - 测试 LLM 的越狱成功率
# - 输出测试报告

# 练习 17：写一个 LLM 输出安全评估工具
# - 评估维度：有害性 / 偏见 / 隐私泄露 / 幻觉
# - 支持批量测试
# - 生成评估报告

# 练习 18：写一个简单的 LLM 代理安全扫描器
# - 检测工具调用中的注入风险
# - 检测权限过度问题
# - 生成安全建议
```

---

## 6. 靶场与实验环境

### 6.1 LLM 安全实验环境

#### 本地 LLM 部署（必做！）
```
工具：Ollama
安装：一条命令安装
部署模型：
  - llama3.1:8b（Llama 3.1 8B，适合入门）
  - qwen2.5:7b（通义千问 2.5 7B，中文好）
  - mistral:7b（Mistral 7B，英文好）
  - gemma:7b（Google Gemma 7B）

验证：curl http://localhost:11434/api/generate -d '{
  "model": "llama3.1:8b",
  "prompt": "Hello, who are you?"
}'
```

#### LLM 应用实验环境
```
工具：LangChain + FastAPI + Streamlit
搭建一个有漏洞的 LLM 应用：
  1. 简单的聊天机器人（有 Prompt 注入漏洞）
  2. RAG 知识库问答（有间接注入漏洞）
  3. Agent 工具调用应用（有越权调用漏洞）
  4. 代码助手（有代码生成安全问题）

攻击目标：
  - 提取 System Prompt
  - 越狱生成有害内容
  - 通过 RAG 注入恶意指令
  - 通过工具调用执行命令 / SSRF
```

### 6.2 在线 LLM 安全靶场

| 平台 / 资源 | 特点 | 费用 |
|------------|------|------|
| **Garak 官方示例** | LLM 安全扫描框架，自带大量探测器 | 免费 |
| **PromptFoo Academy** | Prompt 注入学习与练习 | 免费 + 付费 |
| **OWASP Top 10 for LLM Labs** | OWASP 官方 LLM 安全实验室 | 免费 |
| **Gandalf（Lakera）** | 经典的 Prompt 注入闯关游戏 | 免费 |
| **AI Village CTFs** | DEFCON AI 安全 CTF | 免费 |
| **Hack The Box - AI Track** | HTB 上的 AI/ML 安全挑战 | 免费 + 付费 |
| **Adversarial ML Threat Matrix** | ATT&CK 风格的 ML 安全矩阵 | 免费 |
| **LLM CTF 合集（GitHub）** | 各种 LLM CTF 题目收集 | 免费 |

### 6.3 机器学习安全靶场

| 平台 | 特点 | 费用 |
|------|------|------|
| **ART Notebooks** | IBM ART 官方教程笔记本 | 免费 |
| **TextAttack 教程** | TextAttack 官方文档和教程 | 免费 |
| **Adversarial ML 101** | 入门级对抗 ML 教程 | 免费 |
| **Kaggle 竞赛** | 有 ML 安全相关竞赛 | 免费 |
| **Google AI 安全入门** | Google 官方 AI 安全课程 | 免费 |

### 6.4 CTF 与比赛

| 比赛 | 类型 | 说明 |
|------|------|------|
| **DEFCON AI Village CTF** | AI/ML 安全 CTF | 最知名的 AI 安全 CTF |
| **Hack-a-Sat** | 卫星安全 + AI | 含 ML 相关题目 |
| **国内 CTF（AI 赛道）** | 国内比赛 | 强网杯 / 铁人赛 / 网鼎杯等有 AI 方向 |
| **Kaggle 竞赛** | 数据科学竞赛 | 有安全相关主题 |
| **MITRE ATLAS Challenges** | AI 威胁矩阵挑战 | 实战导向 |

---

## 7. 推荐资料

### 📚 书籍

| 书名 | 难度 | 备注 |
|------|------|------|
| **《机器学习》（西瓜书）** | ⭐⭐⭐ 基础 | 周志华著，中文 ML 经典 |
| **《深度学习》（花书）** | ⭐⭐⭐⭐ 进阶 | Goodfellow 著，深度学习圣经 |
| **《动手学深度学习》**第 2 版 | ⭐⭐ 入门 | 李沐著，代码+理论，实战性强 |
| **《大语言模型：原理与实践》** | ⭐⭐⭐ 进阶 | LLM 系统学习 |
| **《AI 安全：原理与实践》** | ⭐⭐⭐ 进阶 | AI 安全综合教材 |
| **《对抗机器学习》** | ⭐⭐⭐⭐ 进阶 | 对抗样本专业书籍 |
| **《Trustworthy Machine Learning》** | ⭐⭐⭐⭐ 进阶 | 可信机器学习，英文 |
| **《Building Secure and Reliable Systems》** | ⭐⭐⭐ 进阶 | Google SRE + 安全，含 ML 安全 |

### 🌐 在线课程与文档

| 资源 | 关键词 | 特点 |
|------|--------|------|
| **OWASP Top 10 for LLM** | owasp.org/www-project-top-10-for-large-language-model-applications | LLM 安全必读标准 |
| **MITRE ATLAS** | atlas.mitre.org | AI 系统对抗威胁矩阵 |
| **NIST AI RMF** | nist.gov/itl/ai-risk-management-framework | AI 风险管理框架 |
| **Hugging Face Course** | huggingface.co/learn | 免费 NLP / 深度学习课程 |
| **DeepLearning.AI** | deeplearning.ai | Andrew Ng 的课程系列（含 AI 安全专题） |
| **Fast.ai** | fast.ai | 实战派深度学习课程 |
| **Google AI Safety Fundamentals** | safety.google | AI 安全基础课程 |
| **Red Team AI** | redteamai.com | AI 红队资源 |
| **AI Village** | aivillage.org | DEFCON AI Village 资源 |

### 🎥 视频与创作者

| 创作者 / 频道 | 平台 | 特点 |
|-------------|------|------|
| **3Blue1Brown** | YouTube / B 站 | 神经网络/深度学习可视化讲解 |
| **李沐** | B 站 / YouTube | 动手学深度学习系列 |
| **Stanford CS229 / CS230 / CS231n** | YouTube / B 站 | 斯坦福经典 AI 课程 |
| **Andrej Karpathy** | YouTube | 前 Tesla AI 总监，Neural Networks Zero to Hero |
| **Yannic Kilcher** | YouTube | 最新 AI 论文解读 |
| **Two Minute Papers** | YouTube | AI 论文快速解读 |
| **AI Explained** | YouTube | AI 技术与安全科普 |

### 📝 论文与研究资源

| 资源 | 用途 |
|------|------|
| **arXiv** | AI 安全最新论文（搜索 prompt injection / adversarial 等关键词） |
| **Google Scholar** | 学术搜索 |
| **Papers With Code** | 论文 + 代码 |
| **Hugging Face Papers** | 每日最新论文 |
| **AI Security Papers（GitHub 收集）** | AI 安全论文精选列表 |

### 🏢 厂商与研究机构

| 机构 | 方向 |
|------|------|
| **OpenAI Safety** | OpenAI 安全团队 |
| **DeepMind Safety** | Google DeepMind 安全研究 |
| **Anthropic Safety** | Anthropic 安全研究（Constitutional AI） |
| **MIT-IBM Watson AI Lab** | ART 等安全工具 |
| **微软安全 AI 团队** | PyRIT 等工具 |
| **NVIDIA AI Security** | Garak / NeMo Guardrails |
| **国内：智源 / 阿里 / 腾讯 / 百度安全实验室** | 国内 AI 安全研究 |

---

## 8. 实战项目

### 项目一：LLM 安全检测工具

**目标**：开发一个 LLM 安全检测工具，覆盖 OWASP Top 10 for LLM 的主要风险项。

**功能模块**：
1. **Prompt 注入检测模块**
   - 直接注入检测（基于关键词 + 语义 + LLM 裁判）
   - 间接注入检测（RAG 场景）
   - 越狱检测（Jailbreak）
2. **输出安全检测模块**
   - 有害内容检测
   - 敏感信息泄露检测
   - 幻觉检测（事实一致性）
3. **Agent 安全检测模块**
   - 工具调用权限检查
   - 参数注入检测
   - SSRF 风险检测
4. **数据隐私检测模块**
   - PII（个人身份信息）检测
   - 训练数据泄露检测
5. **报告生成模块**
   - 风险等级评估
   - 详细检测结果
   - 修复建议
   - OWASP Top 10 for LLM 映射

**技术栈**：Python + LangChain + Streamlit（Web UI）
**预计耗时**：40 小时
**产出物**：LLM 安全检测工具 + 使用文档 + 测试报告

---

### 项目二：LLM 红队评估实战

**目标**：对一个 LLM 应用进行完整的红队评估，输出专业评估报告。

**评估目标**：一个自建的 LLM 应用（如带 RAG 的客服机器人 + 工具调用功能）

**评估维度**：
1. **Prompt 注入测试**
   - 直接注入（20 种以上 Payload）
   - 间接注入（通过 RAG 文档注入）
   - 多轮对话注入
   - 编码/混淆绕过
   - 多语言绕过
2. **输出安全测试**
   - 有害内容生成测试
   - 敏感信息泄露测试
   - 幻觉测试
3. **数据隐私测试**
   - System Prompt 提取
   - 训练数据记忆化测试
   - PII 泄露测试
4. **Agent / 工具安全测试**
   - 工具越权调用
   - 参数注入
   - SSRF 测试
5. **拒绝服务测试**
   - 资源消耗攻击
   - Prompt 膨胀攻击

**输出报告**：
- 执行摘要
- 评估范围与方法
- 漏洞详情（描述 / 风险等级 / 复现步骤 / 修复建议）
- OWASP Top 10 for LLM 映射
- 风险评级矩阵
- 整改建议与优先级

**预计耗时**：35 小时
**产出物**：LLM 红队评估报告（30+ 页）+ 测试用例库 + PoC 脚本

---

### 项目三：带安全防护的 LLM 应用

**目标**：开发一个有安全防护的 LLM 应用，从各个层面保障安全。

**应用场景**：企业内部知识库问答机器人（RAG + Agent）

**安全防护措施**：
1. **输入层防护**
   - Prompt 注入检测（Garak + 自定义规则）
   - 输入内容审核
   - 速率限制与配额
2. **模型层防护**
   - System Prompt 加固
   - 输出格式约束
   - 温度与随机性控制
3. **工具调用防护**
   - 最小权限原则
   - 参数校验与白名单
   - 人工确认（高风险操作）
4. **输出层防护**
   - 内容安全审核
   - 敏感信息脱敏
   - 引用溯源（RAG 场景）
5. **监控与审计**
   - 完整对话日志
   - 安全事件告警
   - 使用行为分析
6. **RAG 安全**
   - 知识库访问权限控制
   - 文档注入防护
   - 检索结果过滤

**技术栈**：LangChain + FastAPI + PostgreSQL + Redis + Guardrails
**预计耗时**：40 小时
**产出物**：带安全防护的 LLM 应用 + 安全设计文档 + 攻防测试报告

---

### 项目四：对抗样本攻击与防御实验

**目标**：深入理解对抗样本攻击与防御原理，动手实现并验证。

**实验内容**：
1. **图像分类模型对抗攻击**
   - 用 ResNet / VGG 等预训练模型
   - 实现 FGSM / PGD / C&W 攻击
   - 对比不同攻击的成功率和扰动大小
   - 物理世界对抗样本（可选，打印对抗贴纸）
2. **文本分类模型对抗攻击**
   - 用 BERT 做情感分类
   - 用 TextAttack 进行对抗攻击
   - 分析攻击成功的样本特征
3. **防御方法对比**
   - 对抗训练
   - 输入去噪 / 变换
   - 检测 + 拒绝
   - 防御性蒸馏（可选）
   - 对比不同防御方法的效果和代价
4. **评估指标**
   - 干净准确率
   - 对抗准确率
   - 鲁棒性准确率
   - 计算开销

**预计耗时**：30 小时
**产出物**：对抗样本攻防实验报告 + 代码仓库

---

## 9. 常见误区

### ❌ 误区 1：觉得 AI 安全是"纯算法"，安全背景没用
**现象**：觉得 AI 安全都是数学和算法，自己是安全背景搞不定。
**纠正**：AI 安全是"AI + 安全"的交叉领域，安全思维和攻防方法论非常重要。比如 Prompt 注入本质上就是 Web 安全里的注入攻击在 LLM 场景下的变体，Agent 工具调用漏洞和 Web 安全的越权、命令注入思路一样。安全背景反而是优势。

### ❌ 误区 2：只学攻击，不学防御和合规
**现象**：只研究怎么越狱、怎么注入，对护栏、合规、治理一窍不通。
**纠正**：企业真正需要的是"既能攻又能防"的人才。尤其是 AI 安全岗位，很大一部分工作是合规评估、安全加固、防护体系建设。只懂攻击不懂防御，就业面会窄很多。

### ❌ 误区 3：沉迷"大模型"，忽视传统 ML 安全
**现象**：觉得只有大模型安全才算 AI 安全，传统 ML 安全过时了。
**纠正**：传统 ML 安全（对抗样本、数据投毒、模型窃取等）是 AI 安全的基础。大模型安全中的很多问题（如数据投毒、后门攻击）本质上还是传统 ML 安全问题在更大规模模型上的体现。基础打牢了，大模型安全才能深入。

### ❌ 误区 4：追新猎奇，每个新模型都要玩一遍
**现象**：每天追新模型，GPT-4o 出来了试一下，Llama 3.1 出来了试一下，但一个都没深入。
**纠正**：工具和模型只是载体，核心是理解安全原理。选定 1-2 个模型深入研究其安全特性，比浅尝辄止 10 个模型有用得多。原理是通用的。

### ❌ 误区 5：觉得 AI 安全 = Prompt 注入
**现象**：觉得 AI 安全就是 Prompt 注入，学几个 Payload 就完事了。
**纠正**：Prompt 注入只是 LLM 安全的冰山一角。LLM 安全有 10 大类风险（OWASP Top 10），更别说还有传统 ML 安全、数据隐私、供应链安全、合规治理等方向。视野要开阔。

### ❌ 误区 6：忽视 AI 安全的伦理和社会影响
**现象**：只研究技术，不考虑伦理和社会影响。
**纠正**：AI 安全和伦理、治理、法规是紧密结合的。企业里做 AI 安全，很大一部分工作是合规和治理。了解《生成式 AI 服务管理暂行办法》等法规，理解 AI 伦理原则，是 AI 安全从业者的必备素养。

### ❌ 误区 7：觉得没有 GPU 就学不了 AI 安全
**现象**：自己电脑没有好显卡，觉得学不了 AI。
**纠正**：
- LLM 安全的大部分内容（Prompt 注入、Agent 安全、输出安全）不需要训练模型，用 API 或本地小模型就能练
- 免费 GPU 资源很多：Google Colab、Kaggle Notebooks、阿里云 / 腾讯云免费额度
- 传统 ML 安全用 CPU 也能跑很多实验（小模型 + 小数据集）

---

## 10. 自测题与产出物

### 10.1 基础理论题

1. 什么是 Transformer？简述 Self-Attention 的工作原理。
2. 大语言模型的训练流程是什么？预训练、微调、RLHF、DPO 分别是什么？
3. OWASP Top 10 for LLM 有哪些？选 3 个详细说明其原理和危害。
4. 什么是 Prompt 注入？直接注入和间接注入有什么区别？
5. 常见的 Prompt 注入绕过手法有哪些？（至少说 8 种）
6. 什么是 RAG？RAG 有哪些安全风险？
7. 什么是 Agent / Function Calling？有哪些安全风险？
8. 什么是成员推理攻击？什么是模型反演攻击？
9. 什么是对抗样本？白盒攻击和黑盒攻击的区别？
10. 什么是数据投毒？什么是后门攻击？
11. 什么是差分隐私？什么是联邦学习？它们分别解决什么问题？
12. NIST AI RMF 是什么？它的核心功能有哪些？
13. 国内有哪些关于生成式 AI 的法规？核心要求是什么？
14. 什么是 AI 红队？它和传统渗透测试有什么异同？
15. LLM 安全护栏（Guardrails）有哪些实现方式？各有什么优缺点？

### 10.2 实操题

1. 用 Ollama 在本地部署一个大模型（如 Llama 3.1 8B），并写一个简单的 Python 脚本调用它。
2. 用 LangChain 搭建一个简单的 RAG 应用（用自己的文档做知识库）。
3. 对一个 LLM 应用进行 Prompt 注入测试，至少成功实现 5 种不同的注入手法，并写出测试报告。
4. 用 Garak 扫描一个 LLM 应用，分析扫描结果，找出高危风险项，并给出修复建议。
5. 用 PromptFoo 做一次系统化的 Prompt 红队测试，生成评估报告。
6. 搭建一个带工具调用的 LLM Agent，然后找出并利用其中的安全漏洞（如 SSRF、命令注入、越权调用）。
7. 用 ART 库实现 FGSM 和 PGD 对抗攻击，在 MNIST / CIFAR-10 数据集上测试攻击成功率。
8. 用 TextAttack 对一个文本分类模型进行对抗攻击，分析攻击效果。
9. 实现一个简单的 Prompt 注入检测系统（输入过滤 + 输出过滤 + LLM 裁判），并测试其检测率和误报率。
10. 完成一次完整的 LLM 应用安全评估，输出专业的评估报告（参照 OWASP 标准）。

### 10.3 阶段产出物清单

完成本模块后，你应该拥有以下产出物：

- [ ] **AI 基础**
  - [ ] 机器学习经典算法实现（5+ 个）
  - [ ] PyTorch 深度学习项目（3+ 个）
  - [ ] Transformer 原理笔记 + 代码实现
- [ ] **LLM 开发**
  - [ ] 本地 LLM 部署环境（Ollama + 3+ 个模型）
  - [ ] RAG 应用项目（1 个完整项目）
  - [ ] Agent 工具调用应用（1 个）
  - [ ] LangChain / LlamaIndex 实战项目
- [ ] **LLM 安全**
  - [ ] Prompt 注入 Payload 库（50+ 个，按类型分类）
  - [ ] LLM 安全检测工具（自研或基于开源改造）
  - [ ] LLM 红队评估报告（2 份以上）
  - [ ] OWASP Top 10 for LLM 详解笔记
  - [ ] 越狱技术与防御总结
- [ ] **ML 安全**
  - [ ] 对抗样本攻防实验报告
  - [ ] 数据投毒 / 后门攻击实验
  - [ ] ART / TextAttack 工具使用笔记
  - [ ] ML 安全论文阅读笔记（10+ 篇）
- [ ] **合规与治理**
  - [ ] 国内外 AI 安全法规梳理
  - [ ] NIST AI RMF 学习笔记
  - [ ] AI 安全评估模板
  - [ ] 生成式 AI 备案 / 评估指南
- [ ] **实战经验**
  - [ ] 参加 1-2 次 AI 安全 CTF 比赛
  - [ ] 提交过 AI 相关漏洞（SRC / 漏洞平台）
  - [ ] AI 安全技术博客 10+ 篇
- [ ] **GitHub 项目**
  - [ ] LLM 安全检测工具
  - [ ] LLM 红队测试工具集
  - [ ] AI 安全学习笔记仓库

---

> **下一步建议**：完成 M7 后，你已经掌握了前沿的 AI 安全能力。接下来：
> - 想深耕 AI 安全 → 关注最新论文、参加 AI 安全 CTF、贡献开源项目
> - 想做云安全 → 进入 **M8 云原生安全**（云上 AI 安全是结合点）
> - 想做安全开发 → 进入 **M9 安全开发与 DevSecOps**（AI 应用安全开发）
> - 想就业 → 进入 **M10 认证与就业**，准备 CISP-AISS 等 AI 安全认证
