# 高级OSINT技术与自动化实战

> 适用人群：具有一定OSINT基础的信息安全从业者、渗透测试工程师、社会工程学研究者
> 前置知识：基础网络知识、常用OSINT工具使用、Python编程基础
> 学习目标：掌握高级OSINT侦察技术、自动化工作流构建、企业级情报收集方法论

---

## 第1章 OSINT进阶概述

### 1.1 什么是高级OSINT

OSINT（Open Source Intelligence，开源情报）是指从公开可用的信息源中收集、分析和提炼有价值情报的过程。高级OSINT不仅仅是使用几个工具进行信息收集，而是一套系统化的方法论，涵盖信息聚合、关联分析、模式识别、自动化处理等多个维度。

**高级OSINT的核心特征：**

- **深度关联分析**：将分散在不同平台的碎片化信息进行交叉验证和关联，构建完整的目标画像
- **多源数据融合**：整合社交媒体、泄露数据库、域名系统、代码仓库、文档元数据等多维度信息
- **自动化工作流**：通过脚本和API将重复性操作自动化，提高侦察效率和覆盖范围
- **反侦察意识**：在侦察过程中保持匿名性，避免被目标察觉或追踪
- **情报产品输出**：将原始数据转化为结构化、可行动的情报报告

**高级OSINT与基础OSINT的区别：**

| 维度 | 基础OSINT | 高级OSINT |
|------|-----------|-----------|
| 信息深度 | 表面信息收集 | 深层关联挖掘 |
| 工具使用 | 单一工具 | 工具链编排 |
| 自动化程度 | 手动操作 | 脚本化/流水线 |
| 分析方法 | 线性浏览 | 网络分析、时间线分析 |
| 输出成果 | 信息罗列 | 结构化情报报告 |
| 隐蔽性要求 | 低 | 高（反侦察） |

### 1.2 OSINT与社会工程学的关系

OSINT与社会工程学（Social Engineering）是信息安全领域中紧密相关的两个方向，二者互为补充：

**OSINT为社会工程学提供弹药：**
- 通过OSINT收集目标的个人信息、兴趣爱好、社交关系，为社工攻击提供精准素材
- 了解目标企业的组织架构、员工信息、技术栈，为定向钓鱼攻击提供支撑
- 发现目标的安全弱点和可能的切入点

**社会工程学为OSINT提供手段：**
- 社工技巧可以帮助获取原本不公开的信息
-  pretexting（伪装）技术可以绕过信息访问限制
-  通过社交互动获取内部信息

**典型应用场景：**
1. **鱼叉式钓鱼**：利用OSINT收集的个人信息定制钓鱼邮件内容，提高成功率
2. **伪装身份**：基于目标公司的组织架构信息，伪装成特定角色进行社工攻击
3. **密码猜测**：通过分析目标的社交媒体内容，推断其可能使用的密码模式
4. **物理渗透**：收集目标场所的布局、安保措施、人员作息等信息

### 1.3 OSINT的伦理与法律边界

#### 1.3.1 法律框架

OSINT活动涉及的法律问题因司法管辖区而异，但以下原则具有普遍性：

**中国相关法律法规：**
- 《网络安全法》：对网络数据收集和使用有明确规定
- 《个人信息保护法》：严格规范个人信息的收集、处理和使用
- 《数据安全法》：对数据处理活动进行规范
- 《刑法》：非法获取计算机信息系统数据罪、侵犯公民个人信息罪等

**国际法律参考：**
- GDPR（欧盟通用数据保护条例）
- CFAA（美国计算机欺诈和滥用法案）
- 各国隐私保护法规

#### 1.3.2 伦理原则

OSINT从业者应遵循以下伦理准则：

1. **目的正当性**：仅用于授权的安全测试、研究或合法调查目的
2. **最小必要原则**：只收集完成任务所必需的最少信息
3. **数据保护**：妥善保管收集到的信息，防止二次泄露
4. **不造成伤害**：避免对目标造成不必要的损害或困扰
5. **透明性**：在适当情况下披露调查身份和目的

#### 1.3.3 红线警示

以下行为绝对禁止：
- 未经授权访问非公开系统或数据
- 使用收集的信息进行欺诈、勒索等犯罪活动
- 大规模收集和贩卖个人信息
- 绕过技术保护措施获取信息
- 将OSINT结果用于骚扰、人肉搜索等恶意目的

### 1.4 高级OSINT技能树

```
高级OSINT技能树
├── 基础技能层
│   ├── 网络基础知识（TCP/IP、DNS、HTTP）
│   ├── 搜索引擎高级语法
│   ├── Linux命令行熟练使用
│   └── Python编程基础
├── 工具技能层
│   ├── Maltego高级使用与自定义变换
│   ├── 侦察框架（Recon-ng、SpiderFoot）
│   ├── 社交媒体工具链
│   ├── 图像与人脸分析工具
│   └── 泄露数据查询平台
├── 分析技能层
│   ├── 社交网络分析（SNA）
│   ├── 时间线分析
│   ├── 数据关联与交叉验证
│   ├── 模式识别与行为分析
│   └── 元数据分析
├── 自动化技能层
│   ├── API集成与调用
│   ├── Web爬虫开发
│   ├── 数据清洗与处理
│   ├── 工作流编排
│   └── 报告自动化生成
└── 高阶技能层
    ├── 匿名化与反侦察
    ├── 暗网情报收集
    ├── 企业级OSINT方法论
    ├── 反OSINT与隐私保护
    └── 情报产品设计
```

### 1.5 匿名化与反侦察

在进行高级OSINT活动时，保护自身身份和操作痕迹至关重要。

#### 1.5.1 网络层匿名

**VPN与代理链：**
- 使用可信的VPN服务，注意选择无日志政策的服务商
- 多层代理链（Proxy Chaining）增加溯源难度
- Tor网络用于敏感查询，但需注意出口节点风险

**DNS隐私保护：**
- 使用DoH（DNS over HTTPS）或DoT（DNS over TLS）
- 避免使用ISP提供的DNS服务器
- 推荐：Cloudflare 1.1.1.1、Quad9 9.9.9.9

#### 1.5.2 浏览器指纹防护

**浏览器指纹的组成：**
- User-Agent、屏幕分辨率、时区
- 已安装插件列表、字体列表
- Canvas指纹、WebGL指纹
- AudioContext指纹
- WebRTC本地IP泄露

**防护措施：**
- 使用Tor Browser或Brave浏览器
- 安装隐私保护扩展：uBlock Origin、Privacy Badger、NoScript
- 禁用WebRTC和Canvas读取
- 定期清理Cookie和浏览数据

#### 1.5.3 操作安全（OPSEC）

- 使用独立的侦察环境（虚拟机、专用设备）
- 分离个人身份与侦察身份
- 避免在侦察账号中泄露个人信息
- 使用独立的邮箱和手机号注册工具账号
- 注意操作时间规律，避免形成可识别的行为模式

---

## 第2章 Maltego高级使用

### 2.1 Maltego基础回顾

Maltego是由Paterva开发的可视化链接分析工具，是OSINT从业者的核心工具之一。它以实体（Entity）和变换（Transform）为核心概念，通过图形化方式展示信息之间的关系。

**核心概念回顾：**
- **实体（Entity）**：信息的基本单元，如人、域名、IP地址、邮箱等
- **变换（Transform）**：从一个实体发现相关实体的操作
- **图谱（Graph）**：实体和关系的可视化展示
- **机器（Machine）**：预定义的变换序列，可自动执行

### 2.2 变换（Transform）原理与分类

#### 2.2.1 变换的工作原理

变换本质上是一段程序，它接收一个实体作为输入，查询某个数据源，然后返回一组相关实体。Maltego通过Transform API管理这些变换的调用。

**变换执行流程：**
1. 用户在图谱中选择一个或多个实体
2. 选择要运行的变换
3. Maltego将实体信息发送给变换服务器
4. 变换服务器查询数据源并处理结果
5. 返回新的实体和关系到Maltego客户端
6. 在图谱中可视化展示

#### 2.2.2 变换分类

**按数据源分类：**

| 类别 | 代表变换 | 数据源 |
|------|---------|--------|
| 域名/ DNS | To DNS Name、To IP | 各类DNS服务器 |
| WHOIS | To Registrant、To Registrar | WHOIS数据库 |
| 社交媒体 | To Twitter、To LinkedIn | 社交媒体API |
| 证书透明度 | To SSL Certificate | crt.sh等CT日志 |
| 搜索引擎 | To Site、To URL | Google、Bing API |
| 泄露数据 | To Email (from breach) | Have I Been Pwned等 |
| 地理位置 | To Location、To GPS | 地理信息数据库 |

**按功能分类：**
- **枚举型**：从一个实体发现多个同类或相关实体
- **解析型**：将实体从一种形式转换为另一种形式（如域名转IP）
- ** enrichment型**：为实体添加属性信息
- **关联型**：发现实体之间的关系

### 2.3 变换链设计与优化

#### 2.3.1 变换链设计原则

**1. 广度优先 vs 深度优先**
- 广度优先：先扩大信息面，再逐步深入
- 深度优先：沿着一条线索深入挖掘到底
- 实战中通常采用混合策略

**2. 避免变换循环**
- 域名 → IP → 域名 可能形成循环
- 使用不同层级的变换避免冗余
- 设置实体数量限制防止图谱爆炸

**3. 性能优化策略**
- 批量运行变换，减少往返次数
- 对大型结果集使用过滤器
- 合理使用"Share Transform"减少API调用

#### 2.3.2 常用变换链模式

**域名侦察链：**
```
Domain
├── To DNS Name (正向解析)
├── To IP Address (DNS解析)
│   └── To Domains (反向解析)
├── To DNS Name - MX (邮件服务器)
├── To DNS Name - NS (域名服务器)
├── To SSL Certificate (证书透明度)
│   └── To Domains from Certificate
├── To Subdomains (子域名发现)
├── To WHOIS Information
│   ├── To Registrant Email
│   └── To Registrar
└── To URL (搜索引擎)
    └── To Website Title
```

**个人画像链：**
```
Person (姓名)
├── To Email Address
│   ├── To Social Media Accounts
│   ├── To Breach Data
│   └── To Gravatar
├── To Twitter Account
│   ├── To Followers
│   ├── To Tweets (含关键词)
│   └── To User Location
├── To LinkedIn Account
│   ├── To Company
│   ├── To Skills
│   └── To Connections
└── To Aliases
    └── To Other Platforms
```

### 2.4 常用变换组合模式

#### 2.4.1 企业资产发现组合

**组合1：域名扩展发现**
```
输入：Company Name
1. To Domains [using Search Engine] → 获取公司域名列表
2. 对每个域名运行 To Subdomains [CT Logs]
3. 对每个子域名运行 To IP
4. 对每个IP运行 To Netblock
5. 对每个IP运行 To Ports [Shodan]
```

**组合2：员工信息收集**
```
输入：Company Domain
1. To Email Addresses [Hunter.io]
2. 对每个邮箱运行 To Person
3. 对每个人运行 To LinkedIn
4. 对每个人运行 To Twitter
5. 对每个邮箱运行 To Breach Data
```

#### 2.4.2 社交网络扩展组合

**组合：Twitter社交图谱**
```
输入：Twitter Handle
1. To Followers → 获取关注者列表
2. To Following → 获取关注的人
3. 对关键节点运行 To Tweets with Hashtag
4. 对关键节点运行 To Mentions
5. 使用"Social Network"布局分析中心节点
```

### 2.5 自定义变换开发（Python）

Maltego允许开发者使用Python编写自定义变换，扩展其功能。

#### 2.5.1 开发环境准备

**安装Maltego TRX库：**
```bash
pip install maltego-trx
```

**创建变换项目：**
```bash
# 初始化项目结构
maltego-trx start my_transforms
cd my_transforms
```

项目结构：
```
my_transforms/
├── transforms/          # 变换代码目录
│   ├── __init__.py
│   └── example.py
├── settings.csv         # 配置设置
├── requirements.txt     # 依赖
└── wsgi.py              # 服务器入口
```

#### 2.5.2 编写第一个自定义变换

```python
# transforms/github_repos.py
from maltego_trx.entities import Phrase, URL
from maltego_trx.maltego import MaltegoMsg, MaltegoTransform
from maltego_trx.transform import DiscoverableTransform
import requests

class GithubUserRepos(DiscoverableTransform):
    """
    根据GitHub用户名获取其公开仓库列表
    """
    
    @classmethod
    def create_entities(cls, request: MaltegoMsg, response: MaltegoTransform):
        # 获取输入实体的属性
        username = request.Value
        
        try:
            # 调用GitHub API
            api_url = f"https://api.github.com/users/{username}/repos"
            params = {
                'sort': 'updated',
                'per_page': 30
            }
            
            resp = requests.get(api_url, params=params)
            resp.raise_for_status()
            repos = resp.json()
            
            for repo in repos:
                # 创建仓库实体
                repo_entity = response.addEntity(
                    'maltego.URL', 
                    repo['full_name']
                )
                
                # 添加属性
                repo_entity.addProperty(
                    'url', 
                    value=repo['html_url']
                )
                repo_entity.addProperty(
                    'description', 
                    value=repo['description'] or ''
                )
                repo_entity.addProperty(
                    'language', 
                    value=repo['language'] or ''
                )
                repo_entity.addProperty(
                    'stars', 
                    value=str(repo['stargazers_count'])
                )
                
                # 添加链接关系
                repo_entity.setLinkLabel('contributed to')
                repo_entity.setLinkColor('#6cc644')
                
        except requests.RequestException as e:
            response.addUIMessage(f"API请求失败: {str(e)}", 'FatalError')
```

#### 2.5.3 变换部署与集成

**本地测试：**
```bash
cd my_transforms
python wsgi.py
```

**在Maltego中添加自定义变换：**
1. 打开 Maltego → 管理面板 → 变换管理器
2. 点击 "New Transform"
3. 填写变换名称、描述、输入实体类型
4. 设置变换URL为本地服务地址
5. 配置高级选项（并发数、超时等）

#### 2.5.4 高级变换技巧

**批量处理优化：**
```python
from maltego_trx.maltego import MaltegoTransform
import concurrent.futures

class BatchTransform(DiscoverableTransform):
    @classmethod
    def create_entities(cls, request, response):
        # 获取所有选中的实体
        entities = request.Entities
        
        # 使用线程池并发处理
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(cls.process_entity, ent)
                for ent in entities
            ]
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                # 处理结果...
    
    @classmethod
    def process_entity(cls, entity):
        # 单个实体处理逻辑
        pass
```

### 2.6 Maltego社区版 vs 商业版

| 功能 | 社区版(CE) | 经典版(Classic) | 企业版(Enterprise) |
|------|-----------|-----------------|-------------------|
| 实体数量限制 | 最多12个/图 | 无限制 | 无限制 |
| 内置变换数量 | 有限 | 全部 | 全部 |
| 自定义变换 | 支持 | 支持 | 支持 |
| 协作功能 | 否 | 否 | 支持 |
| 商业数据源集成 | 部分 | 更多 | 全部 |
| 使用场景 | 学习、小型项目 | 专业使用 | 团队/企业 |
| 价格 | 免费 | 订阅制 | 定制报价 |

**社区版使用技巧：**
- 使用多个图谱文件管理不同维度的信息
- 利用导出/导入功能在图谱间传递信息
- 自定义变换弥补内置变换的不足
- 结合其他工具进行数据预处理

### 2.7 实体关系图分析技巧

#### 2.7.1 布局算法选择

Maltego提供多种布局算法，适用于不同的分析场景：

| 布局类型 | 适用场景 | 分析目的 |
|---------|---------|---------|
| 有机布局(Organic) | 通用网络分析 | 发现自然聚类 |
| 圆形布局(Circular) | 中心节点分析 | 观察核心节点连接 |
| 层次布局(Hierarchical) | 组织架构、域名结构 | 理解层级关系 |
| 聚类布局(Clustered) | 社区发现 | 识别群组 |
| 时间布局(Temporal) | 时间线分析 | 观察时间模式 |

#### 2.7.2 关键节点识别

**中心性指标：**
- **度中心性（Degree Centrality）**：连接数最多的节点，通常是关键人物或核心资产
- **介数中心性（Betweenness Centrality）**：位于多条路径之间的节点，起到桥梁作用
- **接近中心性（Closeness Centrality）**：与其他节点距离最近的节点，信息传播最快

**在Maltego中识别关键节点：**
1. 使用"Degree Centrality"变换计算节点重要性
2. 根据中心性数值设置节点大小
3. 使用颜色区分不同重要性等级
4. 过滤低价值节点，聚焦核心节点

#### 2.7.3 路径分析

**寻找最短路径：**
- 用于发现两个实体之间的关联链条
- 在社工场景中找到与目标的共同熟人
- 分析数据泄露的传播路径

**操作方法：**
1. 选中起点和终点实体
2. 右键 → "Find Path Between Selected"
3. 分析路径中的中间节点
4. 评估每个节点的利用价值

### 2.8 大规模数据可视化

#### 2.8.1 处理大数据集

**图谱性能优化：**
- 实体数量控制在500-1000以内保证流畅
- 使用"Hide"而非"Delete"管理实体
- 利用图层(Layer)功能分类显示
- 合理使用过滤器减少视觉噪音

**分层展示策略：**
```
Layer 1: 核心目标（1-5个实体）
Layer 2: 直接关联（10-50个实体）
Layer 3: 扩展关联（50-200个实体）
Layer 4: 外围信息（200+ 个实体）
```

#### 2.8.2 数据导出与外部可视化

**导出格式选择：**
- **GraphML**：用于导入其他网络分析工具（Gephi、Cytoscape）
- **CSV**：用于数据处理和统计分析
- **图片**：用于报告展示
- **PDF**：用于正式报告

**与Gephi联动流程：**
1. Maltego中导出GraphML格式
2. Gephi中打开并应用高级布局算法
3. 使用Gephi的统计功能计算网络指标
4. 生成高质量可视化图表
5. 将关键发现返回Maltego继续分析

---

## 第3章 社交媒体深度挖掘

### 3.1 社交媒体信息聚合工具

#### 3.1.1 主流聚合工具对比

| 工具名称 | 支持平台 | 功能特点 | 开源/商业 |
|---------|---------|---------|-----------|
| Maltego | 多平台 | 可视化关系分析 | 混合 |
| SpiderFoot | 多平台 | 自动化侦察框架 | 开源 |
| Social-Engineer Toolkit | 多平台 | 社工+OSINT集成 | 开源 |
| Sherlock | 300+平台 | 用户名跨平台搜索 | 开源 |
| WhatsMyName | 500+平台 | 用户名枚举 | 开源 |
| OSINT Framework | 多平台 | 资源导航与链接集合 | 开源 |
| Snoop | 多平台 | 社交媒体信息收集 | 开源 |

#### 3.1.2 Sherlock深度使用

Sherlock是最流行的跨平台用户名搜索工具之一。

**基本使用：**
```bash
# 基本搜索
python sherlock.py username

# 搜索多个用户名
python sherlock.py user1 user2 user3

# 只输出找到的结果
python sherlock.py username --print-found

# 指定输出目录
python sherlock.py username --folderoutput ./results

# 使用Tor网络
python sherlock.py username --tor
```

**高级用法——批量处理：**
```python
# batch_sherlock.py
import subprocess
import json
import os

def batch_search(usernames, output_dir="results"):
    os.makedirs(output_dir, exist_ok=True)
    
    results = {}
    for username in usernames:
        print(f"正在搜索: {username}")
        result_file = os.path.join(output_dir, f"{username}.txt")
        
        cmd = [
            "python", "sherlock.py",
            username,
            "--print-found",
            "--output", result_file,
            "--timeout", "10"
        ]
        
        try:
            subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            # 解析结果
            found_sites = []
            if os.path.exists(result_file):
                with open(result_file, 'r') as f:
                    found_sites = [
                        line.strip() for line in f 
                        if line.strip().startswith('[+]')
                    ]
            
            results[username] = {
                'count': len(found_sites),
                'sites': found_sites
            }
            
        except subprocess.TimeoutExpired:
            print(f"  搜索超时: {username}")
            results[username] = {'count': 0, 'sites': [], 'error': 'timeout'}
    
    # 保存汇总结果
    summary_file = os.path.join(output_dir, "summary.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    return results

if __name__ == "__main__":
    usernames = ["john_doe", "johndoe", "john.doe"]
    results = batch_search(usernames)
    
    for user, data in results.items():
        print(f"\n{user}: 发现 {data['count']} 个账号")
```

### 3.2 Twitter/X高级搜索技巧

#### 3.2.1 高级搜索语法

**基础操作符：**
- `"精确短语"`：精确匹配短语
- `关键词1 OR 关键词2`：逻辑或
- `-排除词`：排除包含该词的推文
- `(#hashtag)`：按话题标签搜索
- `(@username)`：提及某用户的推文
- `from:username`：某用户发送的推文
- `to:username`：发送给某用户的推文

**时间和位置过滤：**
- `since:2023-01-01`：从指定日期开始
- `until:2023-12-31`：到指定日期为止
- `near:城市`：指定城市附近
- `within:10km`：指定范围内
- `geocode:纬度,经度,半径`：精确地理范围

**互动和媒体过滤：**
- `min_retweets:100`：最少转发数
- `min_faves:500`：最少点赞数
- `filter:images`：只显示含图片的推文
- `filter:videos`：只显示含视频的推文
- `filter:links`：只显示含链接的推文

#### 3.2.2 高级搜索组合模式

**查找用户的敏感信息泄露：**
```
from:username (密码 OR password OR 账号 OR API key OR secret)
```

**查找某公司员工的抱怨：**
```
(to:公司名 OR @公司名) (吐槽 OR 抱怨 OR 垃圾 OR 问题)
```

**事件时间线重建：**
```
# 事件关键词 + 时间范围
"事件关键词" since:2023-01-01 until:2023-01-31
# 按最早排序观察事件发展
```

**地理位置相关内容：**
```
# 特定区域内的推文
geocode:39.9042,116.4074,5km 关键词

# 带位置标签的推文
"地点名称" filter:images
```

#### 3.2.3 Twitter API数据挖掘

**使用Tweepy库：**
```python
import tweepy
import configparser
import json
from datetime import datetime

class TwitterMiner:
    def __init__(self, api_key, api_secret, access_token, access_secret):
        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_secret)
        self.api = tweepy.API(auth, wait_on_rate_limit=True)
    
    def get_user_profile(self, username):
        """获取用户详细资料"""
        user = self.api.get_user(screen_name=username)
        return {
            'id': user.id_str,
            'name': user.name,
            'screen_name': user.screen_name,
            'location': user.location,
            'description': user.description,
            'followers_count': user.followers_count,
            'friends_count': user.friends_count,
            'created_at': user.created_at.isoformat(),
            'profile_image_url': user.profile_image_url_https,
            'banner_url': user.profile_banner_url if hasattr(user, 'profile_banner_url') else None,
            'url': user.url,
            'verified': user.verified,
            'protected': user.protected
        }
    
    def get_user_tweets(self, username, count=200):
        """获取用户最近的推文"""
        tweets = []
        for tweet in tweepy.Cursor(
            self.api.user_timeline,
            screen_name=username,
            count=200,
            tweet_mode='extended'
        ).items(count):
            tweets.append({
                'id': tweet.id_str,
                'created_at': tweet.created_at.isoformat(),
                'text': tweet.full_text,
                'retweet_count': tweet.retweet_count,
                'favorite_count': tweet.favorite_count,
                'hashtags': [h['text'] for h in tweet.entities.get('hashtags', [])],
                'mentions': [m['screen_name'] for m in tweet.entities.get('user_mentions', [])],
                'urls': [u['expanded_url'] for u in tweet.entities.get('urls', [])],
                'geo': tweet.geo,
                'place': tweet.place.full_name if tweet.place else None,
                'source': tweet.source
            })
        return tweets
    
    def search_tweets(self, keyword, count=100, geocode=None):
        """搜索推文"""
        tweets = []
        query = keyword
        if geocode:
            query += f" geocode:{geocode}"
        
        for tweet in tweepy.Cursor(
            self.api.search_tweets,
            q=query,
            count=100,
            tweet_mode='extended',
            result_type='recent'
        ).items(count):
            tweets.append({
                'id': tweet.id_str,
                'user': tweet.user.screen_name,
                'created_at': tweet.created_at.isoformat(),
                'text': tweet.full_text,
                'location': tweet.user.location,
                'geo': tweet.geo
            })
        return tweets
    
    def get_followers(self, username, limit=500):
        """获取粉丝列表"""
        followers = []
        for follower in tweepy.Cursor(
            self.api.get_followers,
            screen_name=username,
            count=200
        ).items(limit):
            followers.append({
                'id': follower.id_str,
                'screen_name': follower.screen_name,
                'name': follower.name,
                'location': follower.location
            })
        return followers
```

#### 3.2.4 第三方Twitter分析工具

- **Twlets**：Chrome扩展，一键导出Twitter数据
- **TweetDeck**：官方多栏监控工具
- **Followerwonk**：Twitter粉丝分析工具
- **Tweepsmap**：地理位置可视化
- **Social Bearing**：Twitter用户分析

### 3.3 LinkedIn信息挖掘

#### 3.3.1 LinkedIn高级搜索

**搜索过滤器：**
- **公司过滤**：`company:"公司名称"`
- **职位过滤**：`title:"职位名称"`
- **地点过滤**：`location:"地点"`
- **学校过滤**：`school:"学校名称"`
- **组合使用**：`company:"Google" title:"Security Engineer" location:"Mountain View"`

**Boolean搜索语法：**
```
# AND逻辑
"Security" AND "Engineer"

# OR逻辑
"Python" OR "Java"

# NOT逻辑
"Manager" NOT "Senior"

# 括号组合
("Security" OR "安全") AND ("Engineer" OR "工程师")
```

#### 3.3.2 组织架构图重建

**方法1：通过公司页面浏览**
1. 进入目标公司LinkedIn页面
2. 点击"员工"标签
3. 按部门、职位筛选
4. 记录关键人物及其汇报关系

**方法2：通过搜索批量发现**
```
# 搜索某公司的安全团队成员
company:"目标公司" AND (title:"安全" OR title:"Security" OR title:"渗透" OR title:"攻防")

# 搜索某公司的IT部门
company:"目标公司" AND (title:"IT" OR title:"信息技术" OR title:"系统" OR title:"网络")
```

**方法3：使用LinkedIn Sales Navigator**
- 更强大的筛选功能
- 可保存搜索和自动监控
- 查看扩展档案信息

#### 3.3.3 LinkedIn数据提取工具

**LinkedIn API（官方）：**
- People API：获取用户公开资料
- Company API：获取公司信息
- Jobs API：获取职位信息
- 需要申请开发者账号和相应权限

**第三方工具：**
- **PhantomBuster**：LinkedIn自动化工具，支持批量资料导出
- **Dux-Soup**：LinkedIn自动化扩展
- **SalesQL**：邮箱查找工具
- **Lusha**：联系方式获取

**注意事项：**
- 违反LinkedIn用户协议可能导致账号封禁
- 大量自动化操作容易被检测
- 建议使用专门的侦察账号
- 控制请求频率，模拟人工操作

### 3.4 Facebook/Instagram图片元数据与位置信息

#### 3.4.1 Facebook信息收集

**Facebook搜索技巧：**
- `site:facebook.com "关键词"`：通过搜索引擎发现公开内容
- 搜索"公开帖子"：查找所有人可见的帖子
- 地点搜索：搜索在特定地点签到的帖子
- 照片搜索：通过照片标签发现关联人物

**Facebook Graph Search（部分地区可用）：**
```
# 喜欢某页面的人
People who like [页面名称]

# 住在某地的人
People who live in [城市名]

# 在某公司工作的人
People who work at [公司名]

# 组合搜索
People who work at [公司] and live in [城市]
```

#### 3.4.2 Instagram信息挖掘

**Instagram搜索语法：**
- 按标签搜索：`#标签名`
- 按位置搜索：位置标签
- 按用户搜索：@用户名

**Instagram工具：**
- **ImgInn**：匿名查看Instagram帖子和故事
- **Picuki**：在线Instagram查看器
- **SmiHub**：匿名查看工具
- **Instaloader**：开源Instagram下载工具（Python）

**使用Instaloader：**
```python
import instaloader
import json

class InstagramMiner:
    def __init__(self):
        self.L = instaloader.Instaloader(
            download_pictures=False,
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=True,
            download_comments=True,
            save_metadata=True,
            compress_json=False
        )
    
    def get_profile_info(self, username):
        """获取用户资料"""
        profile = instaloader.Profile.from_username(self.L.context, username)
        return {
            'username': profile.username,
            'full_name': profile.full_name,
            'biography': profile.biography,
            'followers': profile.followers,
            'followees': profile.followees,
            'mediacount': profile.mediacount,
            'profile_pic_url': profile.profile_pic_url,
            'external_url': profile.external_url,
            'is_private': profile.is_private,
            'is_verified': profile.is_verified
        }
    
    def get_posts_with_location(self, username, max_count=100):
        """获取带位置信息的帖子"""
        profile = instaloader.Profile.from_username(self.L.context, username)
        posts_with_location = []
        
        for post in profile.get_posts():
            if len(posts_with_location) >= max_count:
                break
            
            if post.location:
                posts_with_location.append({
                    'shortcode': post.shortcode,
                    'date_utc': post.date_utc.isoformat(),
                    'caption': post.caption,
                    'likes': post.likes,
                    'location': {
                        'name': post.location.name,
                        'lat': post.location.lat,
                        'lng': post.location.lng
                    },
                    'url': f"https://www.instagram.com/p/{post.shortcode}/"
                })
        
        return posts_with_location
    
    def analyze_location_patterns(self, posts_with_location):
        """分析位置模式"""
        from collections import Counter
        
        locations = [p['location']['name'] for p in posts_with_location]
        location_counts = Counter(locations)
        
        # 按时间分析位置
        timeline = sorted(posts_with_location, key=lambda x: x['date_utc'])
        
        return {
            'unique_locations': len(set(locations)),
            'top_locations': location_counts.most_common(10),
            'timeline_sample': [
                (p['date_utc'][:10], p['location']['name'])
                for p in timeline[:20]
            ]
        }
```

#### 3.4.3 图片EXIF数据提取

虽然大多数社交平台会剥离EXIF数据，但在某些情况下仍可能获取到：

- 用户通过其他渠道分享的原图
- 早期上传的图片
- 某些平台的特定上传方式

**EXIF提取工具：**
- **ExifTool**：最强大的元数据读取工具
- **Jeffrey's Image Metadata Viewer**：在线工具
- **Metapicz**：在线EXIF查看器

```python
# 使用Python提取EXIF
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import os

def extract_exif(image_path):
    """提取图片EXIF信息"""
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        
        if not exif_data:
            return None
        
        result = {}
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            
            if tag == 'GPSInfo':
                gps_data = {}
                for gps_tag_id, gps_value in value.items():
                    gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                    gps_data[gps_tag] = gps_value
                result['GPSInfo'] = gps_data
            else:
                result[tag] = str(value)
        
        return result
    except Exception as e:
        print(f"提取EXIF失败: {e}")
        return None

def gps_to_decimal(coords, ref):
    """将GPS坐标转换为十进制度"""
    degrees = coords[0]
    minutes = coords[1]
    seconds = coords[2]
    
    decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
    
    if ref in ['S', 'W']:
        decimal = -decimal
    
    return decimal
```

### 3.5 微博/微信等中文平台OSINT

#### 3.5.1 微博信息挖掘

**微博高级搜索：**
- 按关键词搜索：支持时间、类型（原创/转发）、地点筛选
- 按用户搜索：昵称、手机号、学校、公司等字段
- 高级筛选：包含图片、包含视频、包含音乐等

**微博数据分析工具：**
- **微博搜索高级版**：官方高级搜索功能
- **第三方数据平台**：如新榜、清博大数据等
- **Python爬虫**：可通过模拟登录获取更多数据

**微博信息收集要点：**
1. **用户资料分析**：昵称、简介、所在地、学校、公司
2. **时间线分析**：作息规律、兴趣话题、社交圈
3. **地理位置信息**：微博定位、签到记录
4. **关系网络**：关注列表、粉丝列表、互动频繁的账号
5. **图片分析**：原图EXIF、背景环境、拍摄地点推测

#### 3.5.2 微信相关信息收集

微信本身是封闭平台，但可以通过以下途径获取信息：

**公开信息源：**
- **微信公众号**：通过搜狗微信搜索查找公开文章
- **微信小程序**：部分小程序数据可通过搜索引擎发现
- **微信群二维码**：公开渠道分享的群二维码
- **微信视频号**：公开的视频内容和评论

**搜狗微信搜索技巧：**
- `site:weixin.sogou.com 关键词`：搜索微信公众号文章
- 按公众号搜索：查找特定机构或个人的公众号
- 按文章搜索：全网微信文章搜索

#### 3.5.3 其他中文平台

| 平台 | OSINT价值 | 收集方法 |
|------|----------|---------|
| 知乎 | 职业信息、兴趣领域、知识结构 | 用户主页、回答历史、关注列表 |
| B站 | 兴趣爱好、观看偏好、评论内容 | 用户空间、投稿视频、弹幕分析 |
| 豆瓣 | 阅读/观影/音乐偏好、小组归属 | 个人主页、书影音记录、小组发言 |
| 小红书 | 消费偏好、生活方式、地理位置 | 笔记内容、定位信息、评论 |
| 脉脉 | 职场信息、公司评价、人脉关系 | 公司主页、员工动态、匿名点评 |
| QQ空间 | 个人动态、好友关系、相册 | 公开内容查看、说说分析 |

### 3.6 社交媒体时间线分析

#### 3.6.1 时间线分析的价值

- **作息规律分析**：推断目标的工作时间、生活习惯
- **事件时间线重建**：还原特定事件的发展过程
- **行为模式识别**：发现异常行为或规律性行为
- **地点轨迹推断**：结合时间和位置信息推断移动轨迹
- **心理状态评估**：通过发文内容和频率变化分析情绪变化

#### 3.6.2 时间线分析方法

**数据收集步骤：**
1. 收集目标在各平台的所有公开帖子
2. 统一时间格式（转为UTC或本地时间）
3. 按时间排序构建完整时间线
4. 标注重要事件节点
5. 分析时间分布规律

**Python时间线分析示例：**
```python
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from datetime import datetime, timedelta

class TimelineAnalyzer:
    def __init__(self, posts_data):
        """
        posts_data: 列表，每个元素包含 'timestamp', 'platform', 'content', 'location'
        """
        self.df = pd.DataFrame(posts_data)
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
        self.df['date'] = self.df['timestamp'].dt.date
        self.df['hour'] = self.df['timestamp'].dt.hour
        self.df['weekday'] = self.df['timestamp'].dt.weekday
    
    def posting_frequency(self):
        """分析发帖频率"""
        daily_counts = self.df.groupby('date').size()
        
        return {
            'total_posts': len(self.df),
            'date_range': {
                'start': str(self.df['date'].min()),
                'end': str(self.df['date'].max())
            },
            'avg_per_day': round(daily_counts.mean(), 2),
            'max_per_day': daily_counts.max(),
            'most_active_day': str(daily_counts.idxmax()),
            'active_days_count': len(daily_counts)
        }
    
    def hourly_pattern(self):
        """分析24小时发帖分布"""
        hourly_counts = self.df.groupby('hour').size()
        
        # 找出最活跃的时段
        peak_hours = hourly_counts.nlargest(3).index.tolist()
        quiet_hours = hourly_counts.nsmallest(3).index.tolist()
        
        return {
            'hourly_distribution': hourly_counts.to_dict(),
            'peak_hours': peak_hours,
            'quiet_hours': quiet_hours
        }
    
    def weekday_pattern(self):
        """分析工作日/周末发帖规律"""
        weekday_counts = self.df.groupby('weekday').size()
        weekday_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        
        weekday_data = {}
        for i, name in enumerate(weekday_names):
            weekday_data[name] = weekday_counts.get(i, 0)
        
        # 工作日 vs 周末
        weekday_total = sum(weekday_counts.get(i, 0) for i in range(5))
        weekend_total = sum(weekday_counts.get(i, 0) for i in range(5, 7))
        
        return {
            'weekday_distribution': weekday_data,
            'weekday_avg': round(weekday_total / 5, 2),
            'weekend_avg': round(weekend_total / 2, 2),
            'weekend_ratio': round(weekend_total / (weekday_total + weekend_total) * 100, 1)
        }
    
    def activity_bursts(self, threshold=3):
        """发现发帖高峰（异常活跃时段）"""
        # 按小时统计发帖数
        hourly = self.df.set_index('timestamp').resample('H').size()
        
        # 找出超过平均值threshold倍的时段
        avg = hourly.mean()
        bursts = hourly[hourly > avg * threshold]
        
        return {
            'avg_per_hour': round(avg, 2),
            'burst_threshold': threshold,
            'burst_count': len(bursts),
            'burst_periods': [
                {
                    'time': str(idx),
                    'count': int(count)
                }
                for idx, count in bursts.items()
            ]
        }
    
    def generate_timeline_report(self):
        """生成完整的时间线分析报告"""
        return {
            'frequency': self.posting_frequency(),
            'hourly_pattern': self.hourly_pattern(),
            'weekday_pattern': self.weekday_pattern(),
            'bursts': self.activity_bursts()
        }
```

### 3.7 社交关系网络分析

#### 3.7.1 社交网络分析基础

**核心概念：**
- **节点（Node）**：社交网络中的个体（用户账号）
- **边（Edge）**：节点之间的关系（关注、好友、互动等）
- **度（Degree）**：一个节点拥有的连接数
- **聚类系数（Clustering Coefficient）**：节点邻居之间也相互连接的程度
- **社区（Community）**：内部连接紧密、外部连接稀疏的节点组

#### 3.7.2 网络构建方法

**数据来源：**
- 关注/粉丝列表
- 互动数据（点赞、评论、转发）
- 共同好友/关注
- 地理位置重合
- 话题标签重合

**构建步骤：**
1. 确定目标中心节点
2. 获取一跳邻居（直接关联）
3. 获取二跳邻居（邻居的邻居，可选）
4. 定义边的权重（互动次数、关系类型）
5. 构建网络数据结构（邻接表或邻接矩阵）

#### 3.7.3 网络分析工具

**Gephi：**
- 开源的网络分析和可视化软件
- 支持多种布局算法
- 丰富的统计指标计算
- 可导入GraphML格式数据

**Cytoscape：**
- 生物信息学领域常用，也适用于社交网络
- 强大的可视化定制能力
- 丰富的插件生态

**Python库：**
- **NetworkX**：最常用的网络分析库
- **igraph**：高性能网络分析
- **PyVis**：交互式网络可视化

```python
# NetworkX社交网络分析示例
import networkx as nx
import json

class SocialNetworkAnalyzer:
    def __init__(self):
        self.G = nx.Graph()
    
    def build_network(self, connections):
        """
        构建社交网络
        connections: 列表，每个元素为 (user1, user2, weight)
        """
        for u1, u2, weight in connections:
            self.G.add_edge(u1, u2, weight=weight)
    
    def basic_metrics(self):
        """基础网络指标"""
        return {
            'node_count': self.G.number_of_nodes(),
            'edge_count': self.G.number_of_edges(),
            'density': round(nx.density(self.G), 4),
            'avg_degree': round(
                sum(dict(self.G.degree()).values()) / self.G.number_of_nodes(), 
                2
            ),
            'is_connected': nx.is_connected(self.G),
            'components': nx.number_connected_components(self.G)
        }
    
    def find_influential_nodes(self, top_n=10):
        """找出有影响力的节点"""
        # 度中心性
        degree_centrality = nx.degree_centrality(self.G)
        
        # 介数中心性
        betweenness_centrality = nx.betweenness_centrality(self.G)
        
        # 接近中心性
        closeness_centrality = nx.closeness_centrality(self.G)
        
        # PageRank
        pagerank = nx.pagerank(self.G)
        
        top_degree = sorted(
            degree_centrality.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:top_n]
        
        top_betweenness = sorted(
            betweenness_centrality.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:top_n]
        
        return {
            'top_by_degree': top_degree,
            'top_by_betweenness': top_betweenness,
            'top_by_pagerank': sorted(
                pagerank.items(), key=lambda x: x[1], reverse=True
            )[:top_n]
        }
    
    def detect_communities(self):
        """社区检测"""
        try:
            from networkx.algorithms.community import greedy_modularity_communities
            
            communities = list(greedy_modularity_communities(self.G))
            
            return {
                'community_count': len(communities),
                'communities': [
                    {
                        'size': len(c),
                        'members': sorted(list(c))[:10]  # 只显示前10个
                    }
                    for c in sorted(communities, key=len, reverse=True)
                ]
            }
        except ImportError:
            return {'error': '需要安装networkx社区检测模块'}
    
    def shortest_path(self, source, target):
        """查找最短路径"""
        try:
            path = nx.shortest_path(self.G, source, target)
            return {
                'path': path,
                'length': len(path) - 1
            }
        except nx.NetworkXNoPath:
            return {'error': '两节点之间无连接路径'}
```

### 3.8 删帖内容恢复与缓存利用

#### 3.8.1 网页缓存与存档服务

**主要缓存服务：**

| 服务 | 特点 | 网址 |
|------|------|------|
| Wayback Machine | 最全面的网页存档 | web.archive.org |
| Google Cache | Google搜索结果缓存 | 搜索结果中点击"缓存" |
| Bing Cache | Bing搜索结果缓存 | 类似Google |
| Archive.is | 手动存档服务 | archive.is |
| WebCite | 学术引用存档 | webcitation.org |

#### 3.8.2 Wayback Machine使用技巧

**基本搜索：**
- 直接访问 `web.archive.org` 输入URL
- 查看时间线上所有存档版本
- 对比不同时间点的页面变化

**高级用法：**
```
# 查看某个特定时间的存档
https://web.archive.org/web/20230101000000/https://example.com

# 查看最早的存档
https://web.archive.org/web/0/https://example.com

# 查看最新的存档
https://web.archive.org/web/2/https://example.com
```

**CDX API查询：**
```python
import requests
import json

class WaybackMachine:
    def __init__(self):
        self.base_url = "https://web.archive.org"
        self.cdx_api = "https://web.archive.org/cdx/search/cdx"
    
    def get_snapshots(self, url, from_date=None, to_date=None, limit=100):
        """获取某个URL的存档列表"""
        params = {
            'url': url,
            'output': 'json',
            'limit': limit,
            'fl': 'timestamp,original,statuscode,mimetype,digest,length'
        }
        
        if from_date:
            params['from'] = from_date
        if to_date:
            params['to'] = to_date
        
        try:
            response = requests.get(self.cdx_api, params=params)
            data = response.json()
            
            if len(data) <= 1:
                return []
            
            # 第一行是表头
            headers = data[0]
            results = []
            
            for row in data[1:]:
                snapshot = dict(zip(headers, row))
                snapshot['archive_url'] = (
                    f"{self.base_url}/web/{snapshot['timestamp']}/"
                    f"{snapshot['original']}"
                )
                results.append(snapshot)
            
            return results
            
        except Exception as e:
            print(f"查询Wayback Machine失败: {e}")
            return []
    
    def get_page_content(self, timestamp, url):
        """获取存档页面内容"""
        archive_url = f"{self.base_url}/web/{timestamp}/{url}"
        
        try:
            response = requests.get(archive_url)
            return response.text
        except Exception as e:
            print(f"获取存档内容失败: {e}")
            return None
    
    def find_deleted_content(self, url, keyword):
        """查找已删除的内容（包含特定关键词的存档）"""
        snapshots = self.get_snapshots(url, limit=1000)
        
        matching_snapshots = []
        for snap in snapshots:
            if snap['statuscode'] == '200':
                content = self.get_page_content(snap['timestamp'], url)
                if content and keyword.lower() in content.lower():
                    matching_snapshots.append(snap)
        
        return matching_snapshots
```

#### 3.8.3 社交媒体删帖恢复

**Twitter删帖恢复：**
- Wayback Machine存档的推文页面
- 第三方存档服务（如Wayback Machine的Twitter存档）
- 其他用户的截图和引用
- 推讯（Pushshift）等第三方数据存档

**微博删帖恢复：**
- 微博的"编辑记录"功能（部分可见）
- 搜索引擎缓存
- 第三方截图和转发
- Wayback Machine的微博存档

**注意事项：**
- 缓存服务可能不包含登录后才能看到的内容
- 社交媒体的动态内容可能无法完整存档
- 图片和视频的存档率通常低于文字内容
- 隐私内容不应通过缓存服务非法获取

---

## 第4章 人脸与图像反向搜索

### 4.1 反向图像搜索引擎

#### 4.1.1 主流反向图像搜索平台对比

| 搜索引擎 | 特点 | 优势领域 | 访问方式 |
|---------|------|---------|---------|
| Google 反向图片搜索 | 最大的索引库，结果最全面 | 通用图片搜索、网页溯源 | images.google.com |
| Bing 视觉搜索 | 微软旗下，与Bing索引整合 | 商品识别、相似图片 | bing.com/images |
| Yandex 图片搜索 | 俄罗斯引擎，人脸匹配强 | 人脸搜索、东欧地区资源 | yandex.com/images |
| PimEyes | 专门的人脸反向搜索引擎 | 跨平台人脸匹配、深网搜索 | pimeyes.com |
| TinEye | 最早的反向图片搜索之一 | 图片溯源、版本追踪 | tineye.com |
| Berify | 专注图片版权追踪 | 版权保护、全网追踪 | berify.com |

#### 4.1.2 Google反向图片搜索高级技巧

**搜索语法组合：**
- 上传图片 + 关键词：限定搜索范围
- `site:域名`：限定在特定网站内搜索
- `filetype:jpg`：限定文件类型
- `-词`：排除特定结果

**多引擎并行搜索策略：**
不同搜索引擎的索引库和算法不同，并行使用多个引擎可以提高发现率。建议的组合：
1. Google（最全面）
2. Yandex（人脸最强）
3. Bing（补充结果）
4. PimEyes（专门人脸）

#### 4.1.3 PimEyes深度使用

PimEyes是一款专门的人脸搜索引擎，其核心优势在于人脸识别而非简单的图片匹配。

**功能特点：**
- 人脸特征向量匹配，而非图像哈希
- 支持上传多张照片建立人脸模型
- 可搜索数百万个网站的公开图片
- 提供深度搜索（Deep Search）功能
- 支持按时间过滤结果

**搜索策略：**
1. 使用多张不同角度、不同光线的照片构建人脸模型
2. 先进行快速搜索，再对可疑结果进行深度搜索
3. 利用过滤功能缩小范围（时间、网站类型）
4. 注意区分长相相似的不同人

**局限性：**
- 付费版功能更强大，免费版搜索次数有限
- 可能返回长相相似的无关人员
- 无法搜索社交媒体的私密内容
- 存在误报，需要人工验证

### 4.2 人脸搜索引擎与技术原理

#### 4.2.1 人脸识别技术基础

**人脸识别的基本流程：**

```
人脸检测 → 人脸对齐 → 特征提取 → 特征比对 → 结果输出
```

**关键技术点：**

1. **人脸检测（Face Detection）**
   - Viola-Jones算法（经典方法）
   - MTCNN（多任务级联卷积网络）
   - YOLO系列（实时检测）
   - RetinaFace（高精度检测）

2. **人脸对齐（Face Alignment）**
   - 检测人脸关键点（ landmarks）
   - 常见关键点数量：5点、68点、106点
   - 将人脸归一化到标准姿态

3. **特征提取（Feature Extraction）**
   - 将人脸图像转换为特征向量（通常128维或512维）
   - 同一人的不同照片特征向量距离近
   - 不同人的特征向量距离远
   - 主流模型：FaceNet、ArcFace、CosFace

4. **特征比对（Feature Matching）**
   - 计算特征向量之间的距离（余弦距离、欧氏距离）
   - 设定阈值判断是否为同一人
   - 大规模人脸库使用向量数据库加速检索

#### 4.2.2 常用人脸搜索引擎

| 平台 | 技术特点 | 数据来源 | 适用场景 |
|------|---------|---------|---------|
| PimEyes | 深度学习人脸匹配 | 公开网页图片 | 跨平台人脸搜索 |
| FaceCheck.ID | FBI级别面部识别 | 社交媒体、新闻网站 | 身份验证 |
| Social Catfish | 反钓鱼身份验证 | 多平台数据整合 | 网恋诈骗识别 |
| TruePeopleSearch | 人脸+个人信息 | 公开记录 | 美国人信息查询 |
| FindFace | 俄罗斯人脸搜索 | VK等社交平台 | 俄语地区搜索 |

#### 4.2.3 自建人脸搜索系统

对于有编程能力的研究者，可以使用开源库构建自己的人脸搜索系统。

```python
# 使用face_recognition库构建简单人脸搜索
import face_recognition
import os
import json
import numpy as np
from PIL import Image

class FaceSearchEngine:
    def __init__(self, face_db_path="face_database"):
        self.face_db_path = face_db_path
        os.makedirs(face_db_path, exist_ok=True)
        self.known_encodings = []
        self.known_names = []
        self.known_sources = []
        self._load_database()
    
    def _load_database(self):
        """加载人脸数据库"""
        index_file = os.path.join(self.face_db_path, "index.json")
        if os.path.exists(index_file):
            with open(index_file, 'r') as f:
                data = json.load(f)
            
            for entry in data:
                encoding_file = os.path.join(
                    self.face_db_path, 
                    entry['encoding_file']
                )
                if os.path.exists(encoding_file):
                    encoding = np.load(encoding_file)
                    self.known_encodings.append(encoding)
                    self.known_names.append(entry['name'])
                    self.known_sources.append(entry.get('source', ''))
    
    def add_face(self, image_path, name, source=""):
        """添加人脸到数据库"""
        # 加载图片并提取人脸编码
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)
        
        if len(encodings) == 0:
            return False, "未检测到人脸"
        
        # 取第一张人脸
        encoding = encodings[0]
        
        # 保存编码
        encoding_filename = f"{name}_{len(self.known_encodings)}.npy"
        encoding_path = os.path.join(self.face_db_path, encoding_filename)
        np.save(encoding_path, encoding)
        
        # 更新索引
        self.known_encodings.append(encoding)
        self.known_names.append(name)
        self.known_sources.append(source)
        
        # 保存索引文件
        self._save_index()
        
        return True, f"已添加 {name} 的人脸数据"
    
    def _save_index(self):
        """保存索引文件"""
        index_data = []
        for i, (name, source) in enumerate(
            zip(self.known_names, self.known_sources)
        ):
            index_data.append({
                'name': name,
                'source': source,
                'encoding_file': f"{name}_{i}.npy"
            })
        
        index_file = os.path.join(self.face_db_path, "index.json")
        with open(index_file, 'w') as f:
            json.dump(index_data, f, indent=2)
    
    def search_face(self, image_path, tolerance=0.6, top_k=5):
        """搜索相似人脸
        
        Args:
            image_path: 待搜索的图片路径
            tolerance: 匹配阈值，越小越严格
            top_k: 返回前K个结果
        """
        # 加载待搜索图片
        unknown_image = face_recognition.load_image_file(image_path)
        unknown_encodings = face_recognition.face_encodings(unknown_image)
        
        if len(unknown_encodings) == 0:
            return [], "未检测到人脸"
        
        results = []
        for unknown_encoding in unknown_encodings:
            # 计算与所有已知人脸的距离
            if len(self.known_encodings) > 0:
                distances = face_recognition.face_distance(
                    self.known_encodings, 
                    unknown_encoding
                )
                
                # 按距离排序
                sorted_indices = np.argsort(distances)
                
                face_results = []
                for idx in sorted_indices[:top_k]:
                    if distances[idx] <= tolerance:
                        face_results.append({
                            'name': self.known_names[idx],
                            'source': self.known_sources[idx],
                            'distance': float(distances[idx]),
                            'similarity': round(
                                (1 - distances[idx]) * 100, 2
                            )
                        })
                
                results.append(face_results)
            else:
                results.append([])
        
        return results, f"检测到 {len(results)} 张人脸"
    
    def batch_search_directory(self, directory_path, tolerance=0.6):
        """批量搜索目录中的图片"""
        results = {}
        
        for filename in os.listdir(directory_path):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                filepath = os.path.join(directory_path, filename)
                face_results, message = self.search_face(
                    filepath, tolerance
                )
                
                if face_results and face_results[0]:
                    results[filename] = face_results[0]
        
        return results
```

### 4.3 图片元数据分析（EXIF、GPS坐标）

#### 4.3.1 EXIF数据详解

EXIF（Exchangeable image file format）是数码相机和智能手机拍摄照片时嵌入的元数据标准。

**EXIF包含的主要信息：**

| 类别 | 字段 | 说明 |
|------|------|------|
| 拍摄设备 | Make、Model | 相机/手机品牌和型号 |
| 拍摄参数 | DateTimeOriginal | 拍摄时间（精确到秒） |
| | ExposureTime | 曝光时间 |
| | FNumber | 光圈值 |
| | ISOSpeedRatings | ISO感光度 |
| | FocalLength | 焦距 |
| | Flash | 闪光灯状态 |
| 位置信息 | GPSLatitude/Longitude | GPS坐标 |
| | GPSAltitude | 海拔高度 |
| | GPSTimeStamp | GPS时间戳 |
| 图像信息 | ImageWidth/Height | 图像尺寸 |
| | Orientation | 拍摄方向 |
| | Software | 处理软件 |
| 作者信息 | Artist | 作者 |
| | Copyright | 版权信息 |

#### 4.3.2 使用ExifTool深度分析

ExifTool是最强大的元数据读取工具，支持几乎所有的元数据格式。

**基本命令：**
```bash
# 查看所有元数据
exiftool photo.jpg

# 查看GPS信息
exiftool -gps:* photo.jpg

# 导出为JSON格式
exiftool -json photo.jpg > metadata.json

# 批量提取目录中的GPS信息
exiftool -gpslatitude -gpslongitude -csv *.jpg > gps_coords.csv

# 查看拍摄时间序列
exiftool -datetimeoriginal -T -d "%Y-%m-%d %H:%M:%S" *.jpg | sort
```

**高级用法——追踪设备：**
```bash
# 通过序列号识别设备
exiftool -serialnumber -model *.jpg

# 查找同一设备拍摄的照片
exiftool -FileName -Model -SerialNumber -csv *.jpg | grep "设备型号"
```

#### 4.3.3 GPS坐标地图可视化

```python
# GPS坐标提取与地图可视化
import exifread
import os
import json
import folium
from folium.plugins import MarkerCluster

class GPSAnalyzer:
    def __init__(self):
        self.photos_with_gps = []
    
    def extract_gps_from_photo(self, image_path):
        """从照片中提取GPS坐标"""
        try:
            with open(image_path, 'rb') as f:
                tags = exifread.process_file(f)
            
            if 'GPS GPSLatitude' in tags and 'GPS GPSLongitude' in tags:
                lat = self._convert_to_degrees(tags['GPS GPSLatitude'])
                lon = self._convert_to_degrees(tags['GPS GPSLongitude'])
                
                # 判断方向
                lat_ref = str(tags.get('GPS GPSLatitudeRef', 'N'))
                lon_ref = str(tags.get('GPS GPSLongitudeRef', 'E'))
                
                if lat_ref == 'S':
                    lat = -lat
                if lon_ref == 'W':
                    lon = -lon
                
                # 提取时间
                datetime_original = None
                if 'EXIF DateTimeOriginal' in tags:
                    datetime_original = str(tags['EXIF DateTimeOriginal'])
                
                return {
                    'file': os.path.basename(image_path),
                    'path': image_path,
                    'latitude': lat,
                    'longitude': lon,
                    'datetime': datetime_original
                }
        except Exception as e:
            print(f"处理 {image_path} 失败: {e}")
        
        return None
    
    def _convert_to_degrees(self, value):
        """将度分秒格式转换为十进制度"""
        d = float(value.values[0].num) / float(value.values[0].den)
        m = float(value.values[1].num) / float(value.values[1].den)
        s = float(value.values[2].num) / float(value.values[2].den)
        
        return d + (m / 60.0) + (s / 3600.0)
    
    def scan_directory(self, directory):
        """扫描目录中的所有图片"""
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.tiff')):
                    filepath = os.path.join(root, file)
                    gps_data = self.extract_gps_from_photo(filepath)
                    if gps_data:
                        self.photos_with_gps.append(gps_data)
        
        return self.photos_with_gps
    
    def generate_map(self, output_file="gps_map.html"):
        """生成交互式地图"""
        if not self.photos_with_gps:
            return None
        
        # 计算中心点
        avg_lat = sum(p['latitude'] for p in self.photos_with_gps) / len(self.photos_with_gps)
        avg_lon = sum(p['longitude'] for p in self.photos_with_gps) / len(self.photos_with_gps)
        
        # 创建地图
        m = folium.Map(location=[avg_lat, avg_lon], zoom_start=12)
        
        # 添加标记聚类
        marker_cluster = MarkerCluster().add_to(m)
        
        for photo in self.photos_with_gps:
            popup_html = f"""
            <strong>{photo['file']}</strong><br>
            时间: {photo.get('datetime', '未知')}<br>
            坐标: {photo['latitude']:.6f}, {photo['longitude']:.6f}
            """
            
            folium.Marker(
                location=[photo['latitude'], photo['longitude']],
                popup=popup_html,
                icon=folium.Icon(color='red', icon='camera')
            ).add_to(marker_cluster)
        
        # 按时间连线（如果有时间信息）
        timed_photos = [p for p in self.photos_with_gps if p.get('datetime')]
        if len(timed_photos) > 1:
            timed_photos.sort(key=lambda x: x['datetime'])
            path_coords = [
                [p['latitude'], p['longitude']] 
                for p in timed_photos
            ]
            folium.PolyLine(
                path_coords,
                color='blue',
                weight=2,
                opacity=0.7,
                popup='移动轨迹'
            ).add_to(m)
        
        m.save(output_file)
        return output_file
    
    def analyze_location_patterns(self):
        """分析位置模式"""
        if not self.photos_with_gps:
            return None
        
        # 按地理位置聚类（简化版：按坐标精度到小数点后2位分组）
        location_groups = {}
        for photo in self.photos_with_gps:
            # 粗略坐标（约1km范围）
            rough_coord = (
                round(photo['latitude'], 2),
                round(photo['longitude'], 2)
            )
            
            if rough_coord not in location_groups:
                location_groups[rough_coord] = []
            location_groups[rough_coord].append(photo)
        
        # 找出拍照最多的地点
        sorted_locations = sorted(
            location_groups.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )
        
        return {
            'total_photos': len(self.photos_with_gps),
            'unique_locations': len(location_groups),
            'top_locations': [
                {
                    'coordinates': loc[0],
                    'photo_count': len(loc[1]),
                    'photos': [p['file'] for p in loc[1][:5]]
                }
                for loc in sorted_locations[:10]
            ]
        }
```

### 4.4 图片真实性鉴定

#### 4.4.1 图片篡改检测

**常见篡改手法：**
- **拼接（Splicing）**：将不同图片的部分组合在一起
- **复制-移动（Copy-Move）**：复制图片中的一部分并移动到另一位置
- **移除（Removal）**：删除图片中的某些元素
- **增强（Enhancement）**：调整亮度、对比度等进行美化

**检测方法：**

1. **ELA（Error Level Analysis）误差水平分析**
   - 原理：JPEG压缩的不均匀性
   - 篡改区域的压缩误差与原图不同
   - 工具：fotoforensics.com

2. **元数据分析**
   - 检查EXIF信息是否一致
   - 软件编辑痕迹
   - 时间戳异常

3. **光照和阴影分析**
   - 检查光线方向是否一致
   - 阴影是否合理
   - 反射是否符合物理规律

4. **噪点分析**
   - 不同来源的图片噪点模式不同
   - 拼接边缘噪点不连续

#### 4.4.2 AI生成图片检测

随着AI生成图片技术的发展，鉴别真实图片和AI生成图片变得越来越重要。

**AI生成图片的常见特征：**
- 手指数量异常（多一根或少一根）
- 牙齿不自然
- 背景细节混乱
- 文字模糊不清
- 对称性异常
- 光照和阴影不合理

**检测工具：**

| 工具 | 特点 | 网址 |
|------|------|------|
| GPTZero | 文本+图像检测 | gptzero.me |
| Originality.ai | AI内容检测 | originality.ai |
| Illuminarty | AI图像检测 | illuminarty.com |
| Sensity | 深度伪造检测 | sensity.ai |
| FakeApp | 深度伪造检测工具 | 开源工具 |

**检测API集成示例：**
```python
import requests
import base64

class AIImageDetector:
    def __init__(self, api_key=None):
        self.api_key = api_key
    
    def detect_with_sightengine(self, image_path):
        """使用SightEngine API检测AI生成图片"""
        # 注意：需要注册获取API密钥
        if not self.api_key:
            return {'error': '需要API密钥'}
        
        api_user = 'api_user'  # 替换为实际用户
        api_secret = self.api_key
        
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode()
        
        params = {
            'models': 'genai',
            'api_user': api_user,
            'api_secret': api_secret
        }
        
        files = {
            'media': (image_path, open(image_path, 'rb'))
        }
        
        try:
            response = requests.post(
                'https://api.sightengine.com/1.0/check.json',
                files=files,
                data=params
            )
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    def basic_artifact_check(self, image_path):
        """基础AI生成特征检查（启发式）"""
        from PIL import Image
        import numpy as np
        
        try:
            img = Image.open(image_path)
            img_array = np.array(img)
            
            findings = []
            
            # 检查1：图像尺寸是否为典型的AI生成尺寸
            width, height = img.size
            ai_sizes = [
                (512, 512), (768, 768), (1024, 1024),
                (512, 768), (768, 512), (1024, 1536)
            ]
            if (width, height) in ai_sizes:
                findings.append({
                    'type': 'size_pattern',
                    'confidence': 0.3,
                    'detail': f'图像尺寸 {width}x{height} 是常见的AI生成尺寸'
                })
            
            # 检查2：颜色分布是否过于平滑
            # 计算相邻像素差异
            diff_h = np.mean(np.abs(np.diff(img_array, axis=0)))
            diff_v = np.mean(np.abs(np.diff(img_array, axis=1)))
            avg_diff = (diff_h + diff_v) / 2
            
            if avg_diff < 10:  # 阈值需根据经验调整
                findings.append({
                    'type': 'over_smoothing',
                    'confidence': 0.2,
                    'detail': '图像过于平滑，可能是AI生成'
                })
            
            # 计算总体概率（简化版）
            probability = min(
                sum(f['confidence'] for f in findings), 
                0.9
            )
            
            return {
                'ai_generated_probability': round(probability * 100, 2),
                'findings': findings,
                'note': '此为基础启发式检测，仅供参考'
            }
            
        except Exception as e:
            return {'error': str(e)}
```

### 4.5 跨平台人脸匹配

#### 4.5.1 跨平台匹配策略

**匹配流程：**
```
1. 收集目标在已知平台的照片
   ↓
2. 提取人脸特征向量，建立人脸模型
   ↓
3. 在其他平台收集疑似照片
   ↓
4. 批量进行人脸比对
   ↓
5. 人工验证高置信度匹配
   ↓
6. 交叉验证关联信息
```

**提高准确率的方法：**
- 使用多张照片建立人脸模型（不同角度、表情、光线）
- 设置合理的匹配阈值（宁可不匹配，不要误匹配）
- 结合其他信息验证（用户名、位置、时间）
- 对高风险结果进行人工复核

#### 4.5.2 多平台照片收集

**各平台照片获取方法：**

| 平台 | 头像获取 | 相册获取 | 工具/方法 |
|------|---------|---------|-----------|
| Twitter | 直接URL | 推文配图 | Tweepy API |
| Instagram | 公开可见 | 公开帖子 | Instaloader |
| LinkedIn | 公开可见 | 有限 | 官方API/爬虫 |
| Facebook | 公开可见 | 取决于隐私设置 | 手动/第三方工具 |
| 微博 | 公开可见 | 公开相册 | 爬虫/第三方工具 |
| GitHub | 直接URL | 无 | 简单HTTP请求 |

### 4.6 以图搜人实战流程

#### 4.6.1 标准操作流程（SOP）

**阶段1：图片预处理**
1. 获取原始图片，确保质量
2. 裁剪出人脸区域（减少干扰）
3. 如有必要，进行图像增强（调整亮度、对比度）
4. 提取并记录EXIF信息

**阶段2：多引擎搜索**
1. Google反向图片搜索
2. Yandex图片搜索
3. PimEyes人脸搜索
4. TinEye溯源搜索
5. 记录所有引擎的结果

**阶段3：结果分析与验证**
1. 汇总各引擎结果，去重
2. 按置信度排序
3. 对高置信度结果进行人工验证
4. 交叉验证其他信息（用户名、位置、时间）
5. 排除误报（长相相似的不同人）

**阶段4：扩展挖掘**
1. 对确认匹配的账号进行深度信息收集
2. 发现更多关联账号
3. 构建完整的人物画像

#### 4.6.2 实战注意事项

- **隐私边界**：仅搜索公开信息，不要尝试获取隐私内容
- **误报处理**：人脸识别可能有误，必须结合其他信息验证
- **法律合规**：遵守当地法律法规，不要用于非法目的
- **道德准则**：尊重他人隐私，不进行人肉搜索等恶意行为
- **数据保护**：妥善保管收集到的图片和信息

---

## 第5章 泄露数据查询与利用

### 5.1 数据泄露事件与数据库

#### 5.1.1 重大数据泄露事件回顾

| 事件 | 时间 | 影响用户数 | 泄露内容 |
|------|------|-----------|---------|
| Yahoo | 2013-2014 | 30亿+ | 姓名、邮箱、密码、安全问题 |
| Facebook | 2019 | 5.33亿 | 手机号、姓名、位置、邮箱 |
| LinkedIn | 2021 | 7亿 | 职业信息、联系方式 |
| Twitter | 2022 | 2.35亿 | 邮箱、手机号、用户名 |
| 新浪微博 | 2020 | 5.38亿 | 手机号、用户名 |
| TikTok | 2022 | 20亿+（有争议） | 用户资料 |
| Marriott酒店 | 2018 | 5亿 | 房客信息、护照号、信用卡 |
| Equifax | 2017 | 1.47亿 | 社保号、信用信息 |

#### 5.1.2 泄露数据的类型

**按数据类型分类：**
- **身份信息**：姓名、身份证号、手机号、邮箱、地址
- **账号凭证**：用户名、密码哈希、安全问题答案
- **行为数据**：浏览记录、购物记录、社交关系
- **金融信息**：银行卡号、交易记录、信用信息
- **位置数据**：GPS轨迹、签到记录
- **企业数据**：员工信息、客户数据、内部文档

**按泄露程度分类：**
- **明文泄露**：数据以原始形式泄露，风险最高
- **哈希泄露**：密码经过哈希处理，需要破解
- **部分泄露**：只泄露部分字段，需与其他数据组合
- **脱敏数据**：经过脱敏处理，但仍可能被反推

### 5.2 Have I Been Pwned使用

#### 5.2.1 功能介绍

Have I Been Pwned（HIBP）是最知名的泄露数据查询平台，由安全研究员Troy Hunt创建。

**主要功能：**
- 邮箱/手机号是否在泄露数据库中
- 查询涉及哪些泄露事件
- 密码是否曾被泄露（k-anonymity保护隐私）
- 域名监测（企业版）
- API接口供开发者集成

#### 5.2.2 高级使用技巧

**密码泄露查询（k-anonymity）：**
HIBP使用k-匿名性算法保护用户密码隐私：
1. 计算密码的SHA-1哈希
2. 只发送哈希的前5位
3. 服务端返回匹配前5位的所有哈希后缀
4. 本地比对完整哈希，判断是否泄露

```python
import hashlib
import requests

class HIBPChecker:
    def __init__(self):
        self.base_url = "https://api.pwnedpasswords.com/range/"
        self.breach_url = "https://haveibeenpwned.com/api/v3/"
        # 注意：v3 API需要API密钥
        self.api_key = None  # 填入你的API密钥
    
    def check_password(self, password):
        """检查密码是否泄露（k-anonymity方式，无需API密钥）"""
        # 计算SHA-1哈希
        sha1_hash = hashlib.sha1(
            password.encode('utf-8')
        ).hexdigest().upper()
        
        prefix = sha1_hash[:5]
        suffix = sha1_hash[5:]
        
        # 查询API
        url = f"{self.base_url}{prefix}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            # 解析结果
            hashes = response.text.splitlines()
            
            for line in hashes:
                hash_suffix, count = line.split(':')
                if hash_suffix == suffix:
                    return {
                        'pwned': True,
                        'count': int(count),
                        'message': f'密码已泄露 {count} 次'
                    }
            
            return {
                'pwned': False,
                'count': 0,
                'message': '密码未在泄露数据库中发现'
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def check_email_breaches(self, email):
        """查询邮箱涉及的泄露事件（需要API密钥）"""
        if not self.api_key:
            return {'error': '需要HIBP API密钥'}
        
        url = f"{self.breach_url}breachedaccount/{email}"
        headers = {
            'hibp-api-key': self.api_key,
            'User-Agent': 'OSINT-Tool'
        }
        params = {
            'truncateResponse': 'false'
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 404:
                return {
                    'breached': False,
                    'breaches': []
                }
            
            response.raise_for_status()
            breaches = response.json()
            
            return {
                'breached': True,
                'breach_count': len(breaches),
                'breaches': [
                    {
                        'name': b['Name'],
                        'title': b['Title'],
                        'domain': b['Domain'],
                        'breach_date': b['BreachDate'],
                        'pwn_count': b['PwnCount'],
                        'data_classes': b['DataClasses'],
                        'is_verified': b['IsVerified']
                    }
                    for b in breaches
                ]
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def check_password_strength_vs_breaches(self, password):
        """综合评估密码强度和泄露情况"""
        result = self.check_password(password)
        
        # 基础强度评估
        length = len(password)
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)
        
        strength_score = 0
        if length >= 8:
            strength_score += 1
        if length >= 12:
            strength_score += 1
        if has_upper and has_lower:
            strength_score += 1
        if has_digit:
            strength_score += 1
        if has_special:
            strength_score += 1
        
        strength_levels = ['极弱', '弱', '一般', '较强', '强', '极强']
        strength = strength_levels[min(strength_score, len(strength_levels) - 1)]
        
        return {
            'password': '***',  # 不返回明文
            'length': length,
            'pwned': result.get('pwned', False),
            'pwned_count': result.get('count', 0),
            'strength': strength,
            'strength_score': strength_score,
            'recommendation': self._get_recommendation(result, strength_score)
        }
    
    def _get_recommendation(self, pwned_result, strength_score):
        """生成密码改进建议"""
        recommendations = []
        
        if pwned_result.get('pwned'):
            recommendations.append(
                '此密码已在数据泄露中出现，立即更换！'
            )
        
        if strength_score < 3:
            recommendations.append(
                '建议密码长度至少12位，包含大小写字母、数字和特殊字符'
            )
        
        if not recommendations:
            recommendations.append('密码强度良好，继续保持')
        
        return recommendations
```

### 5.3 DeHashed、LeakCheck等平台

#### 5.3.1 DeHashed

DeHashed是一个综合的泄露数据查询平台，提供比HIBP更详细的信息。

**特点：**
- 包含数十亿条泄露记录
- 支持多种查询方式（邮箱、用户名、IP、域名、手机号等）
- 提供密码明文（部分数据）
- API接口完善
- 付费查询

**查询字段：**
- email: 邮箱地址
- username: 用户名
- password: 密码
- hashed_password: 哈希密码
- ip_address: IP地址
- phone: 电话号码
- name: 姓名
- domain: 域名
- address: 地址

#### 5.3.2 LeakCheck

LeakCheck是另一个流行的泄露数据查询服务。

**特点：**
- 免费层有限查询
- 支持邮箱、用户名、IP、域名查询
- 提供泄露来源信息
- 定期更新数据库

#### 5.3.3 其他泄露数据平台

| 平台 | 特点 | 价格 |
|------|------|------|
| DeHashed | 数据量大，字段全 | 付费 |
| LeakCheck | 免费版可用 | 免费/付费 |
| IntelX | 暗网+明网数据 | 免费/付费 |
| Snusbase | 历史泄露数据库 | 付费 |
| BreachDirectory | 综合泄露查询 | 免费/付费 |
| Firefox Monitor | Mozilla出品，基于HIBP | 免费 |

### 5.4 泄露数据组合利用

#### 5.4.1 数据关联分析

**单源数据 vs 多源关联：**
- 单源数据只能提供有限信息
- 多源数据关联可以构建完整画像
- 不同泄露事件中的同一邮箱/手机号是关联关键

**关联维度：**
- 身份标识：邮箱、手机号、用户名
- 行为模式：注册时间、密码习惯
- 社交关系：共同联系人、好友关系
- 地理位置：IP地址、注册地点

#### 5.4.2 密码复用分析

密码复用是最大的安全风险之一。通过分析泄露数据中的密码，可以：
- 发现目标的密码模式
- 推测其他账号的可能密码
- 评估目标的安全意识水平

```python
from collections import Counter
import re

class PasswordPatternAnalyzer:
    def __init__(self, passwords):
        """
        passwords: 已知的目标密码列表（从泄露数据中获取）
        """
        self.passwords = passwords
    
    def analyze_patterns(self):
        """分析密码模式"""
        if not self.passwords:
            return None
        
        patterns = {
            'total_count': len(self.passwords),
            'unique_count': len(set(self.passwords)),
            'reuse_rate': round(
                (1 - len(set(self.passwords)) / len(self.passwords)) * 100, 
                2
            ),
        }
        
        # 长度分析
        lengths = [len(p) for p in self.passwords]
        patterns['length_stats'] = {
            'min': min(lengths),
            'max': max(lengths),
            'avg': round(sum(lengths) / len(lengths), 2),
            'most_common': Counter(lengths).most_common(3)
        }
        
        # 字符类型分析
        patterns['char_types'] = self._analyze_char_types()
        
        # 常见模式检测
        patterns['common_patterns'] = self._detect_patterns()
        
        # 词根分析（提取密码中的有意义部分）
        patterns['root_words'] = self._extract_roots()
        
        return patterns
    
    def _analyze_char_types(self):
        """分析字符类型分布"""
        all_lower = sum(1 for p in self.passwords if p.islower())
        all_upper = sum(1 for p in self.passwords if p.isupper())
        has_number = sum(1 for p in self.passwords if any(c.isdigit() for c in p))
        has_special = sum(1 for p in self.passwords if any(not c.isalnum() for c in p))
        first_cap = sum(1 for p in self.passwords if p and p[0].isupper() and p[1:].islower())
        
        total = len(self.passwords)
        
        return {
            'all_lowercase': f"{round(all_lower/total*100, 1)}%",
            'all_uppercase': f"{round(all_upper/total*100, 1)}%",
            'first_letter_capital': f"{round(first_cap/total*100, 1)}%",
            'contains_number': f"{round(has_number/total*100, 1)}%",
            'contains_special': f"{round(has_special/total*100, 1)}%",
        }
    
    def _detect_patterns(self):
        """检测常见密码模式"""
        pattern_counts = Counter()
        
        for password in self.passwords:
            # 姓名+数字模式
            if re.match(r'^[a-zA-Z]+\d+$', password):
                pattern_counts['word+numbers'] += 1
            
            # 纯数字模式
            if password.isdigit():
                pattern_counts['all_numbers'] += 1
            
            # 纯字母模式
            if password.isalpha():
                pattern_counts['all_letters'] += 1
            
            # 键盘连续模式（简化检测）
            keyboard_rows = ['qwertyuiop', 'asdfghjkl', 'zxcvbnm']
            for row in keyboard_rows:
                for i in range(len(row) - 3):
                    if row[i:i+4] in password.lower():
                        pattern_counts['keyboard_sequence'] += 1
                        break
            
            # 日期模式
            if re.search(r'\d{6,8}', password):
                num_part = re.search(r'\d{6,8}', password).group()
                if len(num_part) in [6, 8]:
                    # 可能是生日
                    pattern_counts['date_pattern'] += 1
        
        return dict(pattern_counts.most_common())
    
    def _extract_roots(self):
        """提取密码词根"""
        # 移除数字和特殊字符，提取字母部分
        roots = []
        for p in self.passwords:
            letters = re.sub(r'[^a-zA-Z]', '', p)
            if len(letters) >= 3:
                roots.append(letters.lower())
        
        # 统计最常见的词根
        return Counter(roots).most_common(10)
    
    def predict_passwords(self, target_info=None):
        """基于模式预测可能的密码
        
        target_info: 目标个人信息字典，如姓名、生日等
        """
        predictions = []
        
        # 如果有个人信息，生成基于个人信息的密码变体
        if target_info:
            predictions.extend(
                self._generate_personal_variants(target_info)
            )
        
        # 基于已有密码模式生成变体
        predictions.extend(self._generate_pattern_variants())
        
        # 去重
        seen = set()
        unique_predictions = []
        for p in predictions:
            if p not in seen:
                seen.add(p)
                unique_predictions.append(p)
        
        return unique_predictions[:100]  # 返回前100个
    
    def _generate_personal_variants(self, info):
        """基于个人信息生成密码变体"""
        variants = []
        
        name = info.get('name', '')
        birthday = info.get('birthday', '')  # YYYY-MM-DD
        nickname = info.get('nickname', '')
        pet_name = info.get('pet_name', '')
        
        base_words = [name, nickname, pet_name]
        base_words = [w for w in base_words if w]
        
        # 常见后缀
        common_suffixes = ['123', '123456', '!', '@', '#', '1', '12', '1234']
        
        if birthday:
            parts = birthday.split('-')
            year = parts[0] if len(parts) > 0 else ''
            short_year = year[2:] if year else ''
            month_day = ''.join(parts[1:]) if len(parts) > 2 else ''
            
            common_suffixes.extend([year, short_year, month_day])
        
        for word in base_words:
            # 首字母大写 + 后缀
            cap_word = word.capitalize()
            for suffix in common_suffixes:
                variants.append(cap_word + suffix)
                variants.append(word + suffix)
            
            # 全大写 + 后缀
            upper_word = word.upper()
            variants.append(upper_word + '123')
        
        return variants
    
    def _generate_pattern_variants(self):
        """基于已有密码模式生成变体"""
        # 简化实现：对已有密码做常见变换
        variants = []
        for password in set(self.passwords):
            # 大小写变换
            variants.append(password.lower())
            variants.append(password.upper())
            variants.append(password.capitalize())
            
            # 数字递增/递减
            numbers = re.findall(r'\d+', password)
            if numbers:
                for num_str in numbers:
                    try:
                        num = int(num_str)
                        for delta in [1, -1, 2, -2]:
                            new_num = str(num + delta)
                            variants.append(
                                password.replace(num_str, new_num, 1)
                            )
                    except ValueError:
                        pass
        
        return variants
```

### 5.5 密码泄露分析与密码习惯研究

#### 5.5.1 常见密码统计

根据历年泄露数据库的统计分析，最常见的密码包括：
- `123456`、`password`、`12345678`、`qwerty`、`123456789`
- `12345`、`1234`、`111111`、`1234567`、`dragon`
- 中国人常用：`123456`、`password`、`123456789`、`qwerty`、`12345678`
- 生日模式：YYYYMMDD、MMDDYYYY

#### 5.5.2 密码习惯地域差异

不同国家和地区的用户有不同的密码设置习惯：
- **英语国家**：偏好英文单词+数字
- **中国用户**：偏好拼音+数字、纯数字、手机号
- **日韩用户**：罗马音+数字、纪念日

### 5.6 暗网泄露数据获取（合法渠道）

#### 5.6.1 暗网情报概述

暗网（Dark Web）是指使用Tor等匿名技术访问的网络，其中存在大量数据泄露交易。

**注意：访问暗网和获取泄露数据涉及法律和道德问题，请确保：**
- 仅用于合法的安全研究和企业防护目的
- 遵守当地法律法规
- 不下载或传播非法获取的数据
- 通过合法渠道获取情报

#### 5.6.2 合法暗网情报来源

**商业情报服务：**
- **Flashpoint**：专业暗网情报服务商
- **Recorded Future**：威胁情报平台，含暗网数据
- **Intel 471**：犯罪网络情报
- **DarkOwl**：暗网数据搜索引擎

**开源情报工具：**
- **IntelX**：提供暗网数据搜索，有免费层
- **OnionScan**：暗网网站扫描工具
- **Dark Web News Monitoring**：监控暗网论坛

#### 5.6.3 企业泄露监测方法

**主动监测：**
1. 监控暗网论坛和市场
2. 设置关键词告警（公司名、域名、产品名）
3. 定期搜索员工邮箱是否泄露
4. 监控代码仓库和文件分享平台

**被动监测：**
1. 订阅威胁情报服务
2. 使用Have I Been Pwned的域名监测功能
3. 监控安全媒体和漏洞披露平台

### 5.7 企业泄露监测

#### 5.7.1 监测范围

- **员工凭证泄露**：员工邮箱、密码是否出现在泄露数据库中
- **客户数据泄露**：客户信息是否被泄露或售卖
- **源代码泄露**：公司代码是否出现在公开平台
- **内部文档泄露**：机密文档是否被泄露
- **凭据售卖**：公司账号是否在暗网售卖

#### 5.7.2 自动化监测方案

```python
import requests
import json
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta

class BreachMonitor:
    def __init__(self, config):
        self.config = config
        self.domains = config.get('domains', [])
        self.monitored_emails = config.get('monitored_emails', [])
        self.alert_email = config.get('alert_email')
        self.hibp_api_key = config.get('hibp_api_key')
        
        # 存储已知的泄露记录，避免重复告警
        self.known_breaches_file = 'known_breaches.json'
        self.known_breaches = self._load_known_breaches()
    
    def _load_known_breaches(self):
        """加载已知的泄露记录"""
        try:
            with open(self.known_breaches_file, 'r') as f:
                return set(json.load(f))
        except FileNotFoundError:
            return set()
    
    def _save_known_breaches(self):
        """保存已知的泄露记录"""
        with open(self.known_breaches_file, 'w') as f:
            json.dump(list(self.known_breaches), f)
    
    def check_domain_breaches(self, domain):
        """检查域名相关的泄露"""
        # 使用HIBP API
        url = f"https://haveibeenpwned.com/api/v3/breaches?domain={domain}"
        headers = {
            'hibp-api-key': self.hibp_api_key,
            'User-Agent': 'BreachMonitor'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"检查域名 {domain} 失败: {e}")
            return []
    
    def check_email_breach(self, email):
        """检查单个邮箱是否泄露"""
        url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
        headers = {
            'hibp-api-key': self.hibp_api_key,
            'User-Agent': 'BreachMonitor'
        }
        params = {'truncateResponse': 'true'}
        
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 404:
                return []
            response.raise_for_status()
            return [b['Name'] for b in response.json()]
        except Exception as e:
            print(f"检查邮箱 {email} 失败: {e}")
            return []
    
    def run_monitoring(self):
        """执行监测任务"""
        new_breaches = []
        
        # 检查域名泄露
        for domain in self.domains:
            print(f"检查域名: {domain}")
            breaches = self.check_domain_breaches(domain)
            
            for breach in breaches:
                breach_id = f"domain:{domain}:{breach['Name']}"
                if breach_id not in self.known_breaches:
                    new_breaches.append({
                        'type': 'domain_breach',
                        'domain': domain,
                        'breach_name': breach['Name'],
                        'breach_title': breach['Title'],
                        'breach_date': breach['BreachDate'],
                        'pwn_count': breach['PwnCount'],
                        'data_classes': breach['DataClasses']
                    })
                    self.known_breaches.add(breach_id)
        
        # 检查特定邮箱泄露
        for email in self.monitored_emails:
            print(f"检查邮箱: {email}")
            breaches = self.check_email_breach(email)
            
            for breach_name in breaches:
                breach_id = f"email:{email}:{breach_name}"
                if breach_id not in self.known_breaches:
                    new_breaches.append({
                        'type': 'email_breach',
                        'email': email,
                        'breach_name': breach_name
                    })
                    self.known_breaches.add(breach_id)
        
        # 保存已知泄露记录
        self._save_known_breaches()
        
        # 如果有新泄露，发送告警
        if new_breaches:
            self._send_alert(new_breaches)
        
        return new_breaches
    
    def _send_alert(self, new_breaches):
        """发送告警邮件"""
        if not self.alert_email:
            print("未配置告警邮箱")
            return
        
        subject = f"【泄露告警】发现 {len(new_breaches)} 条新的泄露记录"
        
        body = "监测到以下新的数据泄露：\n\n"
        for i, breach in enumerate(new_breaches, 1):
            if breach['type'] == 'domain_breach':
                body += f"{i}. 域名泄露: {breach['domain']}\n"
                body += f"   泄露事件: {breach['breach_title']}\n"
                body += f"   泄露日期: {breach['breach_date']}\n"
                body += f"   影响账号数: {breach['pwn_count']}\n"
                body += f"   泄露数据类型: {', '.join(breach['data_classes'])}\n\n"
            elif breach['type'] == 'email_breach':
                body += f"{i}. 邮箱泄露: {breach['email']}\n"
                body += f"   出现在: {breach['breach_name']}\n\n"
        
        print(f"发送告警: {subject}")
        # 实际环境中需要配置SMTP服务器
        print(body)
```

---

## 第6章 企业OSINT高级技巧

### 6.1 企业组织架构图重建

#### 6.1.1 信息收集维度

重建企业组织架构需要从多个维度收集信息：

**公开来源：**
- LinkedIn公司页面和员工档案
- 公司官网的"关于我们"、"团队"页面
- 新闻报道和采访
- 招聘信息（职位层级、部门划分）
- 内部演讲和技术分享
- 员工社交媒体信息

**推断方法：**
- 职位名称推断层级
- 汇报关系推断（LinkedIn关系、会议出席）
- 部门命名规律推断组织架构
- 员工数量和增长趋势推断

#### 6.1.2 组织架构重建步骤

**步骤1：确定组织规模和层级**
- 员工总数（LinkedIn显示、招聘信息推断）
- 管理层级：从CEO到基层员工有几层
- 部门划分：按职能/产品/地域

**步骤2：识别关键人物**
- 高管层：CEO、CTO、CFO、VP等
- 中层管理者：各部门负责人
- 技术骨干：安全负责人、架构师等
- 信息安全相关岗位

**步骤3：填充部门结构**
- 按部门分类收集员工信息
- 确定各部门的负责人
- 标注部门间的汇报关系

**步骤4：验证和细化**
- 交叉验证不同来源的信息
- 通过会议、演讲等信息确认汇报关系
- 标注信息的可信度

#### 6.1.3 自动化工具实现

```python
import json
import re
from collections import defaultdict

class OrgChartReconstructor:
    def __init__(self):
        self.employees = []
        self.departments = defaultdict(list)
    
    def add_employee(self, name, title, department=None, 
                     manager=None, source=None, confidence=0.5):
        """添加员工信息"""
        employee = {
            'name': name,
            'title': title,
            'department': department,
            'manager': manager,
            'source': source,
            'confidence': confidence,
            'level': self._estimate_level(title)
        }
        self.employees.append(employee)
        
        if department:
            self.departments[department].append(employee)
        
        return employee
    
    def _estimate_level(self, title):
        """根据职位名称估计层级"""
        title_lower = title.lower()
        
        # C级高管
        if any(x in title_lower for x in ['ceo', 'cto', 'cfo', 'coo', 'chief']):
            return 'C-level'
        
        # VP级别
        if any(x in title_lower for x in ['vice president', 'vp', '副总裁']):
            return 'VP'
        
        # 总监级别
        if any(x in title_lower for x in ['director', '总监']):
            return 'Director'
        
        # 经理级别
        if any(x in title_lower for x in ['manager', '经理', '主管', 'leader']):
            return 'Manager'
        
        # 高级工程师
        if any(x in title_lower for x in ['senior', '高级', '资深', 'lead']):
            return 'Senior'
        
        # 普通员工
        return 'Individual Contributor'
    
    def analyze_structure(self):
        """分析组织架构"""
        # 按层级统计
        level_counts = defaultdict(int)
        for emp in self.employees:
            level_counts[emp['level']] += 1
        
        # 按部门统计
        dept_stats = {}
        for dept, members in self.departments.items():
            levels = defaultdict(int)
            for m in members:
                levels[m['level']] += 1
            dept_stats[dept] = {
                'total': len(members),
                'levels': dict(levels)
            }
        
        return {
            'total_employees': len(self.employees),
            'level_distribution': dict(level_counts),
            'department_stats': dept_stats,
            'estimated_depth': self._estimate_depth()
        }
    
    def _estimate_depth(self):
        """估计组织深度（层级数）"""
        levels_order = [
            'C-level', 'VP', 'Director', 
            'Manager', 'Senior', 'Individual Contributor'
        ]
        existing_levels = set(emp['level'] for emp in self.employees)
        
        depth = 0
        for level in levels_order:
            if level in existing_levels:
                depth += 1
        
        return depth
    
    def find_security_team(self):
        """识别安全团队成员"""
        security_keywords = [
            'security', '安全', '渗透', '攻防', 'vulnerability',
            '漏洞', 'sdl', 'devsecops', 'soc', 'siem', 'ciso'
        ]
        
        security_team = []
        for emp in self.employees:
            title_lower = emp['title'].lower()
            if any(kw in title_lower for kw in security_keywords):
                security_team.append(emp)
        
        return security_team
    
    def generate_org_chart(self):
        """生成组织架构图数据（可用于可视化）"""
        # 按层级和部门组织
        chart = {
            'nodes': [],
            'edges': []
        }
        
        # 添加节点
        for emp in self.employees:
            chart['nodes'].append({
                'id': emp['name'],
                'label': f"{emp['name']}\n{emp['title']}",
                'level': emp['level'],
                'department': emp['department'],
                'confidence': emp['confidence']
            })
        
        # 添加边（汇报关系，如果已知manager）
        for emp in self.employees:
            if emp.get('manager'):
                chart['edges'].append({
                    'from': emp['manager'],
                    'to': emp['name'],
                    'relation': 'reports_to'
                })
        
        return chart
```

### 6.2 员工邮箱枚举与验证

#### 6.2.1 邮箱格式推断

**常见企业邮箱格式：**

| 格式 | 示例 | 常见程度 |
|------|------|---------|
| first.last@domain | john.smith@company.com | 非常常见 |
| firstlast@domain | johnsmith@company.com | 常见 |
| flast@domain | jsmith@company.com | 常见 |
| first@domain | john@company.com | 小公司 |
| lastf@domain | smithj@company.com | 较少 |
| 工号@domain | 12345@company.com | 大企业 |

**推断方法：**
1. 收集已知的员工邮箱（从LinkedIn、论文、会议等）
2. 分析邮箱命名规律
3. 生成可能的邮箱列表
4. 验证邮箱是否存在

#### 6.2.2 邮箱发现方法

**主动发现：**
- Hunter.io、Snov.io等邮箱查找工具
- LinkedIn邮箱导出工具
- 公司官网员工页面
- 域名WHOIS信息
- SSL证书信息

**被动发现：**
- Google搜索：`@company.com email`
- 代码仓库中的提交记录
- 文档元数据（PDF、Office文档）
- 公开的邮件列表存档
- 泄露数据库查询

#### 6.2.3 邮箱验证技术

**验证方法：**

1. **SMTP验证**
   - 连接目标邮件服务器
   - 使用VRFY或RCPT TO命令
   - 检查服务器响应
   - 注意：可能触发安全告警

2. **语法验证**
   - 检查邮箱格式是否正确
   - 验证域名是否存在MX记录
   - 不能确认邮箱是否真实存在

3. **基于行为的验证**
   - 密码找回功能
   - 注册功能（提示邮箱已注册）
   - 登录功能的错误提示差异

```python
import dns.resolver
import smtplib
import re
import requests

class EmailValidator:
    def __init__(self):
        self.results = {}
    
    def validate_format(self, email):
        """验证邮箱格式"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def check_mx_records(self, domain):
        """检查域名的MX记录"""
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            return [
                {
                    'priority': r.preference,
                    'exchange': str(r.exchange)
                }
                for r in mx_records
            ]
        except Exception as e:
            print(f"MX查询失败: {e}")
            return []
    
    def smtp_verify(self, email, from_email='test@example.com'):
        """通过SMTP验证邮箱是否存在
        
        注意：此方法可能触发目标服务器的安全检测
        """
        domain = email.split('@')[1]
        mx_records = self.check_mx_records(domain)
        
        if not mx_records:
            return {'valid': False, 'reason': '无MX记录'}
        
        # 使用优先级最高的MX服务器
        mx_server = mx_records[0]['exchange']
        
        try:
            server = smtplib.SMTP(timeout=10)
            server.connect(mx_server, 25)
            server.helo()
            server.mail(from_email)
            code, message = server.rcpt(email)
            server.quit()
            
            if code == 250:
                return {'valid': True, 'confidence': 0.8}
            elif code == 550:
                return {'valid': False, 'confidence': 0.9}
            else:
                return {
                    'valid': 'unknown', 
                    'code': code,
                    'message': message.decode('utf-8', errors='ignore')
                }
                
        except Exception as e:
            return {'valid': 'unknown', 'error': str(e)}
    
    def generate_email_variants(self, first_name, last_name, domain):
        """生成可能的邮箱变体"""
        variants = []
        f = first_name.lower()
        l = last_name.lower()
        fi = first_name[0].lower()
        li = last_name[0].lower()
        
        # 常见格式
        patterns = [
            f"{f}.{l}",          # john.smith
            f"{f}{l}",           # johnsmith
            f"{fi}{l}",          # jsmith
            f"{f}{li}",          # johns
            f"{f}",              # john
            f"{l}",              # smith
            f"{f}-{l}",          # john-smith
            f"{fi}.{l}",         # j.smith
            f"{l}{fi}",          # smithj
            f"{f}_{l}",          # john_smith
        ]
        
        for pattern in patterns:
            variants.append(f"{pattern}@{domain}")
        
        return variants
    
    def batch_validate(self, emails):
        """批量验证邮箱"""
        results = {}
        
        for email in emails:
            if not self.validate_format(email):
                results[email] = {'valid': False, 'reason': '格式错误'}
                continue
            
            # 检查MX记录
            domain = email.split('@')[1]
            mx = self.check_mx_records(domain)
            if not mx:
                results[email] = {'valid': False, 'reason': '无MX记录'}
                continue
            
            # SMTP验证（谨慎使用）
            # result = self.smtp_verify(email)
            # results[email] = result
            
            # 仅验证域名和格式
            results[email] = {
                'valid': 'possible',
                'format_valid': True,
                'mx_valid': True,
                'confidence': 0.3
            }
        
        return results
```

### 6.3 子域名与IP资产发现

#### 6.3.1 子域名发现方法

**被动发现：**
- 搜索引擎（site:domain.com）
- 证书透明度日志（crt.sh）
- DNS记录聚合服务（SecurityTrails、PassiveTotal）
- Wayback Machine存档
- VirusTotal子域名信息
- Threat Intelligence平台

**主动发现：**
- 字典爆破（subfinder、amass、gobuster）
- 通配符DNS检测
- DNS区域传输（如果配置错误）
- 证书SAN字段提取
- 递归发现（子域名的子域名）

#### 6.3.2 资产发现工具链

**工具组合：**
```
子域名发现 → 存活检测 → 端口扫描 → 服务识别 → 技术栈识别
   ↓            ↓           ↓           ↓           ↓
subfinder     httpx       nmap       whatweb    wappalyzer
amass        httprobe    masscan    nikto      builtwith
assetfinder  katana      naabu      gobuster   wfuzz
```

**自动化流程：**
```python
import subprocess
import os
import json

class SubdomainDiscovery:
    def __init__(self, domain, output_dir="results"):
        self.domain = domain
        self.output_dir = os.path.join(output_dir, domain)
        os.makedirs(self.output_dir, exist_ok=True)
    
    def run_subfinder(self):
        """使用subfinder发现子域名"""
        output_file = os.path.join(self.output_dir, "subfinder.txt")
        
        cmd = [
            "subfinder",
            "-d", self.domain,
            "-o", output_file,
            "-silent"
        ]
        
        try:
            subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            with open(output_file, 'r') as f:
                subdomains = [line.strip() for line in f if line.strip()]
            
            return subdomains
        except Exception as e:
            print(f"subfinder执行失败: {e}")
            return []
    
    def run_amass(self):
        """使用amass发现子域名（更全面但更慢）"""
        output_file = os.path.join(self.output_dir, "amass.txt")
        
        cmd = [
            "amass", "enum",
            "-d", self.domain,
            "-o", output_file,
            "-silent"
        ]
        
        try:
            subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            with open(output_file, 'r') as f:
                subdomains = [line.strip() for line in f if line.strip()]
            
            return subdomains
        except Exception as e:
            print(f"amass执行失败: {e}")
            return []
    
    def run_crtsh(self):
        """通过crt.sh证书透明度发现子域名"""
        import requests
        
        url = f"https://crt.sh/?q=%25.{self.domain}&output=json"
        
        try:
            response = requests.get(url, timeout=30)
            data = response.json()
            
            subdomains = set()
            for entry in data:
                name = entry.get('name_value', '')
                for n in name.split('\n'):
                    n = n.strip()
                    if n.endswith(self.domain) and '*' not in n:
                        subdomains.add(n)
            
            return list(subdomains)
        except Exception as e:
            print(f"crt.sh查询失败: {e}")
            return []
    
    def merge_results(self, *subdomain_lists):
        """合并多个工具的结果并去重"""
        all_subdomains = set()
        for lst in subdomain_lists:
            all_subdomains.update(lst)
        
        # 过滤无效结果
        valid = [
            s for s in all_subdomains 
            if s and s.endswith(self.domain) and '*' not in s
        ]
        
        # 保存合并结果
        output_file = os.path.join(self.output_dir, "all_subdomains.txt")
        with open(output_file, 'w') as f:
            f.write('\n'.join(sorted(valid)))
        
        return sorted(valid)
    
    def check_alive(self, subdomains):
        """使用httpx检测存活主机"""
        input_file = os.path.join(self.output_dir, "all_subdomains.txt")
        output_file = os.path.join(self.output_dir, "alive.txt")
        
        with open(input_file, 'w') as f:
            f.write('\n'.join(subdomains))
        
        cmd = [
            "httpx",
            "-l", input_file,
            "-o", output_file,
            "-silent",
            "-status-code",
            "-title",
            "-tech-detect"
        ]
        
        try:
            subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            alive_hosts = []
            if os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            alive_hosts.append(line)
            
            return alive_hosts
        except Exception as e:
            print(f"httpx执行失败: {e}")
            return []
    
    def full_discovery(self):
        """执行完整的子域名发现流程"""
        print(f"开始发现 {self.domain} 的子域名...")
        
        # 1. 多工具发现
        print("  运行subfinder...")
        subfinder_results = self.run_subfinder()
        print(f"    发现 {len(subfinder_results)} 个")
        
        print("  查询crt.sh...")
        crtsh_results = self.run_crtsh()
        print(f"    发现 {len(crtsh_results)} 个")
        
        # 2. 合并去重
        print("  合并结果...")
        all_subdomains = self.merge_results(
            subfinder_results,
            crtsh_results
        )
        print(f"    共 {len(all_subdomains)} 个唯一子域名")
        
        # 3. 存活检测
        print("  检测存活主机...")
        alive = self.check_alive(all_subdomains)
        print(f"    存活 {len(alive)} 个")
        
        return {
            'total_discovered': len(all_subdomains),
            'alive_count': len(alive),
            'all_subdomains': all_subdomains,
            'alive_hosts': alive
        }
```

### 6.4 技术栈识别与漏洞关联

#### 6.4.1 技术栈识别方法

**Web技术栈识别：**
- HTTP响应头（Server、X-Powered-By）
- Cookie命名（PHPSESSID、JSESSIONID、csrftoken）
- URL模式（.php、.aspx、.jsp）
- 页面特征（favicon、CSS类名、JS函数）
- 指纹库匹配（Wappalyzer、WhatWeb）

**基础设施识别：**
- CDN检测（Cloudflare、Akamai、AWS CloudFront）
- 云服务识别（AWS、Azure、GCP）
- WAF检测（ModSecurity、Cloudflare WAF、阿里云WAF）
- 邮件服务（Google Workspace、Office 365、自建邮件服务器）

#### 6.4.2 漏洞关联思路

```
技术栈识别 → 版本号提取 → 漏洞数据库查询 → 风险评估
     ↓            ↓             ↓              ↓
  Wappalyzer   响应头       CVE详情      CVSS评分
  WhatWeb     页面特征     Exploit-DB    利用难度
  BuiltWith   指纹匹配     NVD           影响范围
```

### 6.5 代码托管平台信息泄露

#### 6.5.1 GitHub Dorking高级技巧

GitHub Dorking是指使用GitHub的高级搜索语法来发现敏感信息。

**基础搜索语法：**
- `关键词`：搜索包含关键词的代码
- `user:用户名`：限定用户
- `org:组织名`：限定组织
- `repo:仓库名`：限定仓库
- `filename:文件名`：按文件名搜索
- `extension:扩展名`：按文件扩展名搜索
- `path:路径`：按路径搜索
- `language:语言`：按编程语言搜索

**敏感信息搜索Dorks：**

| 目标 | Dork示例 |
|------|---------|
| API密钥 | `filename:.env api_key` |
| AWS密钥 | `AKIA extension:py` |
| 数据库密码 | `password extension:yml database` |
| SSH私钥 | `BEGIN RSA PRIVATE KEY extension:pem` |
| Slack Token | `xoxb- extension:js` |
| 私钥文件 | `filename:id_rsa` |
| 配置文件密码 | `password filename:config.php` |
| 内部文档 | `confidential extension:pdf` |

**高级搜索技巧：**
```
# 搜索某组织内的密码
org:company_name password

# 搜索特定类型文件中的API密钥
extension:py "api_key" OR "secret_key"

# 搜索提交历史中的敏感信息
"removed password" type:commit

# 搜索被删除的敏感文件
filename:.env org:company_name is:deleted

# 搜索包含特定关键词的Issue
"security vulnerability" type:issue org:company_name
```

#### 6.5.2 敏感信息搜索实战

```python
import requests
import json
import time
from datetime import datetime, timedelta

class GitHubDorker:
    def __init__(self, token=None):
        self.base_url = "https://api.github.com"
        self.token = token
        self.headers = {
            'Accept': 'application/vnd.github.v3+json'
        }
        if token:
            self.headers['Authorization'] = f'token {token}'
    
    def search_code(self, query, per_page=30, page=1):
        """搜索代码"""
        url = f"{self.base_url}/search/code"
        params = {
            'q': query,
            'per_page': per_page,
            'page': page
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 403:
                # 速率限制
                reset_time = response.headers.get('X-RateLimit-Reset')
                if reset_time:
                    wait_time = int(reset_time) - time.time() + 1
                    print(f"速率限制，等待 {wait_time:.0f} 秒")
                    time.sleep(max(wait_time, 0))
                    return self.search_code(query, per_page, page)
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            print(f"搜索失败: {e}")
            return None
    
    def search_sensitive_info(self, org_or_user, is_org=True):
        """搜索敏感信息"""
        prefix = 'org' if is_org else 'user'
        
        dorks = {
            'api_keys': [
                f'{prefix}:{org_or_user} "api_key" extension:py',
                f'{prefix}:{org_or_user} "secret_key" extension:js',
                f'{prefix}:{org_or_user} "AKIA" extension:py',
                f'{prefix}:{org_or_user} "access_token" extension:json',
            ],
            'passwords': [
                f'{prefix}:{org_or_user} "password" filename:.env',
                f'{prefix}:{org_or_user} "DB_PASSWORD" extension:yml',
                f'{prefix}:{org_or_user} "root:" filename:config.php',
            ],
            'private_keys': [
                f'{prefix}:{org_or_user} "BEGIN RSA PRIVATE KEY"',
                f'{prefix}:{org_or_user} filename:id_rsa',
                f'{prefix}:{org_or_user} filename:.pem',
            ],
            'config_files': [
                f'{prefix}:{org_or_user} filename:config.php password',
                f'{prefix}:{org_or_user} filename:database.yml password',
                f'{prefix}:{org_or_user} filename:web.config "connectionString"',
            ],
            'internal_docs': [
                f'{prefix}:{org_or_user} "内部" extension:pdf',
                f'{prefix}:{org_or_user} "confidential" extension:docx',
            ]
        }
        
        results = {}
        
        for category, queries in dorks.items():
            print(f"搜索 {category}...")
            category_results = []
            
            for query in queries:
                data = self.search_code(query, per_page=30)
                if data and 'items' in data:
                    for item in data['items']:
                        category_results.append({
                            'file': item['name'],
                            'path': item['path'],
                            'repo': item['repository']['full_name'],
                            'url': item['html_url'],
                            'query': query
                        })
                
                # 避免触发速率限制
                time.sleep(2)
            
            results[category] = category_results
            print(f"  发现 {len(category_results)} 个结果")
        
        return results
    
    def get_commit_history(self, repo, filepath, since=None):
        """获取文件的提交历史"""
        url = f"{self.base_url}/repos/{repo}/commits"
        params = {'path': filepath}
        if since:
            params['since'] = since
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            commits = response.json()
            
            return [
                {
                    'sha': c['sha'],
                    'message': c['commit']['message'],
                    'author': c['commit']['author']['name'],
                    'date': c['commit']['author']['date'],
                    'url': c['html_url']
                }
                for c in commits
            ]
        except Exception as e:
            print(f"获取提交历史失败: {e}")
            return []
    
    def list_repos(self, org_or_user, is_org=True):
        """列出组织或用户的所有仓库"""
        if is_org:
            url = f"{self.base_url}/orgs/{org_or_user}/repos"
        else:
            url = f"{self.base_url}/users/{org_or_user}/repos"
        
        params = {
            'per_page': 100,
            'type': 'all'
        }
        
        all_repos = []
        page = 1
        
        while True:
            params['page'] = page
            try:
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                repos = response.json()
                
                if not repos:
                    break
                
                all_repos.extend([
                    {
                        'name': r['name'],
                        'full_name': r['full_name'],
                        'description': r['description'],
                        'language': r['language'],
                        'stars': r['stargazers_count'],
                        'forks': r['forks_count'],
                        'is_fork': r['fork'],
                        'created_at': r['created_at'],
                        'updated_at': r['updated_at'],
                        'url': r['html_url']
                    }
                    for r in repos
                ])
                
                page += 1
                
                if len(repos) < 100:
                    break
                    
            except Exception as e:
                print(f"获取仓库列表失败: {e}")
                break
        
        return all_repos
```

#### 6.5.3 提交历史与删除文件恢复

**Git历史中的敏感信息：**
- 开发者不小心提交了敏感文件，然后删除了
- 但提交历史中仍然保留
- 使用git log和git show可以查看

**发现方法：**
1. 搜索包含敏感关键词的commit message
2. 检查大的删除提交（可能是删除敏感文件）
3. 使用truffleHog、gitleaks等工具扫描历史

**恢复被删除的文件：**
```bash
# 查找删除文件的commit
git log --diff-filter=D --summary -- "*.pem"

# 从特定commit恢复文件
git show <commit_sha>:path/to/file > recovered_file
```

### 6.6 文档元数据挖掘

#### 6.6.1 可挖掘的文档类型

| 文档类型 | 扩展名 | 元数据价值 |
|---------|--------|-----------|
| PDF | .pdf | 作者、创建工具、修改历史、嵌入对象 |
| Word | .docx/.doc | 作者、公司、修订记录、批注 |
| Excel | .xlsx/.xls | 作者、公式、隐藏工作表、外部链接 |
| PPT | .pptx/.ppt | 作者、演讲者备注、隐藏幻灯片 |
| 图片 | .jpg/.png | EXIF信息、GPS坐标（见第4章） |

#### 6.6.2 文档元数据提取工具

**ExifTool：** 支持几乎所有文件格式的元数据读取
```bash
# 提取PDF元数据
exiftool document.pdf

# 提取Office文档元数据
exiftool document.docx

# 导出所有元数据为JSON
exiftool -json -a -u *.pdf > metadata.json
```

**PDF元数据深度挖掘：**
```python
import PyPDF2
import subprocess
import json
import os

class DocumentMetadataMiner:
    def extract_pdf_metadata(self, pdf_path):
        """提取PDF元数据"""
        try:
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                
                info = reader.metadata
                metadata = {
                    'title': info.title if info else None,
                    'author': info.author if info else None,
                    'subject': info.subject if info else None,
                    'creator': info.creator if info else None,
                    'producer': info.producer if info else None,
                    'creation_date': str(info.creation_date) if info and info.creation_date else None,
                    'modification_date': str(info.modification_date) if info and info.modification_date else None,
                    'pages': len(reader.pages),
                    'encrypted': reader.is_encrypted
                }
                
                # 提取文本内容（用于关键词搜索）
                text_content = ""
                for page in reader.pages:
                    text_content += page.extract_text() + "\n"
                
                metadata['text_length'] = len(text_content)
                metadata['text_preview'] = text_content[:500]
                
                return metadata
        except Exception as e:
            return {'error': str(e)}
    
    def extract_office_metadata(self, file_path):
        """提取Office文档元数据（使用exiftool）"""
        try:
            result = subprocess.run(
                ['exiftool', '-json', file_path],
                capture_output=True, text=True
            )
            data = json.loads(result.stdout)
            if data:
                return data[0]
        except Exception as e:
            return {'error': str(e)}
    
    def scan_directory_for_docs(self, directory):
        """扫描目录中的文档并提取元数据"""
        results = []
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                ext = file.lower().split('.')[-1]
                
                if ext in ['pdf', 'docx', 'xlsx', 'pptx', 'doc', 'xls', 'ppt']:
                    filepath = os.path.join(root, file)
                    
                    if ext == 'pdf':
                        metadata = self.extract_pdf_metadata(filepath)
                    else:
                        metadata = self.extract_office_metadata(filepath)
                    
                    results.append({
                        'file': file,
                        'path': filepath,
                        'type': ext,
                        'metadata': metadata
                    })
        
        return results
    
    def find_sensitive_keywords(self, text, keywords=None):
        """在文本中查找敏感关键词"""
        if keywords is None:
            keywords = [
                '密码', 'password', 'secret', '密钥', 'API Key',
                '内部', '机密', 'confidential', 'internal',
                '用户名', 'username', '账号', 'account'
            ]
        
        found = {}
        text_lower = text.lower()
        
        for kw in keywords:
            count = text_lower.count(kw.lower())
            if count > 0:
                found[kw] = count
        
        return found
```

---

## 第7章 OSINT自动化工作流

### 7.1 Python OSINT编程基础

#### 7.1.1 为什么选择Python

Python是OSINT自动化的首选编程语言，原因包括：
- 丰富的第三方库生态
- 简洁易读的语法，快速原型开发
- 强大的网络编程能力
- 数据处理和分析库（pandas、numpy）
- 大量安全工具使用Python开发
- 跨平台兼容性

#### 7.1.2 必备Python库

| 类别 | 库名 | 用途 |
|------|------|------|
| 网络请求 | requests | HTTP请求 |
| | httpx | 异步HTTP |
| | aiohttp | 异步HTTP客户端 |
| 网页解析 | BeautifulSoup | HTML/XML解析 |
| | lxml | 高性能XML/HTML解析 |
| | parsel | 基于lxml的解析器 |
| 浏览器自动化 | selenium | 浏览器自动化 |
| | playwright | 现代浏览器自动化 |
| 数据处理 | pandas | 数据分析与处理 |
| | json | JSON处理 |
| | csv | CSV处理 |
| 网络工具 | dnspython | DNS查询 |
| | python-whois | WHOIS查询 |
| | shodan | Shodan API |
| 可视化 | matplotlib | 数据可视化 |
| | folium | 地图可视化 |
| | networkx | 网络分析与可视化 |

#### 7.1.3 开发环境配置

```python
# requirements.txt 推荐配置
requests>=2.28.0
beautifulsoup4>=4.11.0
lxml>=4.9.0
selenium>=4.8.0
pandas>=1.5.0
dnspython>=2.3.0
python-whois>=0.8.0
shodan>=1.28.0
folium>=0.14.0
networkx>=3.0.0
exifread>=3.0.0
PyPDF2>=3.0.0
```

### 7.2 requests、BeautifulSoup、selenium在OSINT中的应用

#### 7.2.1 requests库高级用法

**会话管理：**
```python
import requests

class SessionManager:
    def __init__(self):
        self.session = requests.Session()
        self._setup_headers()
    
    def _setup_headers(self):
        """设置请求头，模拟真实浏览器"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;'
                      'q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def set_proxy(self, proxy_url):
        """设置代理"""
        self.session.proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
    
    def get_with_retry(self, url, max_retries=3, timeout=10):
        """带重试的GET请求"""
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=timeout)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    raise
                wait_time = 2 ** attempt  # 指数退避
                print(f"请求失败，{wait_time}秒后重试: {e}")
                import time
                time.sleep(wait_time)
    
    def post_with_retry(self, url, data=None, json=None, max_retries=3, timeout=10):
        """带重试的POST请求"""
        for attempt in range(max_retries):
            try:
                response = self.session.post(
                    url, data=data, json=json, timeout=timeout
                )
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    raise
                wait_time = 2 ** attempt
                print(f"请求失败，{wait_time}秒后重试: {e}")
                import time
                time.sleep(wait_time)
```

#### 7.2.2 BeautifulSoup网页解析

```python
from bs4 import BeautifulSoup
import requests

class WebParser:
    def __init__(self, html_content):
        self.soup = BeautifulSoup(html_content, 'lxml')
    
    def extract_all_links(self):
        """提取所有链接"""
        links = []
        for link in self.soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text(strip=True)
            if href.startswith('http'):
                links.append({'url': href, 'text': text})
        return links
    
    def extract_emails(self):
        """提取页面中的邮箱地址"""
        import re
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        
        # 从文本中提取
        text = self.soup.get_text()
        emails = re.findall(email_pattern, text)
        
        # 从mailto链接中提取
        for link in self.soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('mailto:'):
                email = href[7:].split('?')[0]
                emails.append(email)
        
        return list(set(emails))
    
    def extract_phone_numbers(self):
        """提取电话号码（中国格式）"""
        import re
        text = self.soup.get_text()
        
        # 手机号
        mobile_pattern = r'1[3-9]\d{9}'
        # 固定电话
        landline_pattern = r'0\d{2,3}-?\d{7,8}'
        
        mobiles = re.findall(mobile_pattern, text)
        landlines = re.findall(landline_pattern, text)
        
        return {
            'mobiles': list(set(mobiles)),
            'landlines': list(set(landlines))
        }
    
    def extract_meta_tags(self):
        """提取meta标签信息"""
        meta_info = {}
        
        for meta in self.soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            if name and content:
                meta_info[name] = content
        
        return meta_info
    
    def extract_tables(self):
        """提取页面中的表格数据"""
        tables = []
        
        for table in self.soup.find_all('table'):
            table_data = []
            rows = table.find_all('tr')
            
            for row in rows:
                cells = row.find_all(['th', 'td'])
                row_data = [cell.get_text(strip=True) for cell in cells]
                table_data.append(row_data)
            
            if table_data:
                tables.append(table_data)
        
        return tables
```

#### 7.2.3 Selenium动态页面爬取

对于JavaScript渲染的动态页面，需要使用Selenium等浏览器自动化工具。

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

class SeleniumScraper:
    def __init__(self, headless=True):
        self.options = Options()
        
        if headless:
            self.options.add_argument('--headless')
        
        # 反检测配置
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.set_page_load_timeout(30)
        self.wait = WebDriverWait(self.driver, 10)
        
        # 注入JavaScript隐藏自动化特征
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            '''
        })
    
    def get_page(self, url, wait_for_element=None):
        """获取页面内容"""
        self.driver.get(url)
        
        if wait_for_element:
            try:
                self.wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, wait_for_element)
                    )
                )
            except Exception:
                pass
        
        # 模拟滚动以加载更多内容
        self._scroll_page()
        
        return self.driver.page_source
    
    def _scroll_page(self):
        """模拟页面滚动"""
        for i in range(3):
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            time.sleep(1)
    
    def extract_text_by_selector(self, css_selector):
        """通过CSS选择器提取文本"""
        try:
            elements = self.driver.find_elements(By.CSS_SELECTOR, css_selector)
            return [elem.text.strip() for elem in elements if elem.text.strip()]
        except Exception as e:
            print(f"提取失败: {e}")
            return []
    
    def extract_links(self):
        """提取所有链接"""
        links = self.driver.find_elements(By.TAG_NAME, 'a')
        result = []
        for link in links:
            href = link.get_attribute('href')
            text = link.text.strip()
            if href and href.startswith('http'):
                result.append({'url': href, 'text': text})
        return result
    
    def take_screenshot(self, filename):
        """截图"""
        self.driver.save_screenshot(filename)
    
    def close(self):
        """关闭浏览器"""
        self.driver.quit()
```

### 7.3 API集成（Shodan、Censys、Hunter.io、HIBP）

#### 7.3.1 Shodan API集成

Shodan是互联网连接设备搜索引擎，OSINT中用于发现目标的网络资产。

```python
import shodan
import json

class ShodanScanner:
    def __init__(self, api_key):
        self.api = shodan.Shodan(api_key)
    
    def host_lookup(self, ip):
        """查询IP的详细信息"""
        try:
            host = self.api.host(ip)
            
            return {
                'ip': host.get('ip_str'),
                'org': host.get('org'),
                'os': host.get('os'),
                'country': host.get('country_name'),
                'city': host.get('city'),
                'ports': host.get('ports', []),
                'vulns': host.get('vulns', []),
                'last_update': host.get('last_update'),
                'services': [
                    {
                        'port': s['port'],
                        'transport': s['transport'],
                        'product': s.get('product', ''),
                        'version': s.get('version', ''),
                        'data': s.get('data', '')[:200]
                    }
                    for s in host.get('data', [])
                ]
            }
        except shodan.APIError as e:
            return {'error': str(e)}
    
    def search_by_query(self, query, limit=100):
        """按关键词搜索"""
        try:
            results = self.api.search(query, limit=limit)
            
            return {
                'total': results['total'],
                'matches': [
                    {
                        'ip': m['ip_str'],
                        'port': m['port'],
                        'org': m.get('org', ''),
                        'location': f"{m.get('country_name', '')}, {m.get('city', '')}",
                        'product': m.get('product', ''),
                        'version': m.get('version', ''),
                        'data': m.get('data', '')[:300]
                    }
                    for m in results['matches']
                ]
            }
        except shodan.APIError as e:
            return {'error': str(e)}
    
    def search_by_domain(self, domain):
        """搜索域名相关的主机"""
        query = f"hostname:{domain}"
        return self.search_by_query(query)
    
    def get_exploits(self, query):
        """搜索漏洞利用代码"""
        try:
            results = self.api.exploits.search(query)
            return {
                'total': results['total'],
                'exploits': results['matches'][:10]
            }
        except shodan.APIError as e:
            return {'error': str(e)}
    
    def scan_ip(self, ip):
        """请求扫描一个IP（需要积分）"""
        try:
            result = self.api.scan(ip)
            return result
        except shodan.APIError as e:
            return {'error': str(e)}
```

#### 7.3.2 Hunter.io集成

Hunter.io用于发现和验证企业邮箱地址。

```python
import requests

class HunterIOClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.hunter.io/v2"
    
    def domain_search(self, domain, limit=100):
        """搜索域名下的所有邮箱"""
        url = f"{self.base_url}/domain-search"
        params = {
            'domain': domain,
            'api_key': self.api_key,
            'limit': limit
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('data'):
                result = data['data']
                return {
                    'domain': result.get('domain'),
                    'disposable': result.get('disposable'),
                    'webmail': result.get('webmail'),
                    'pattern': result.get('pattern'),
                    'organization': result.get('organization'),
                    'emails': [
                        {
                            'value': e['value'],
                            'type': e.get('type', ''),
                            'confidence': e.get('confidence', 0),
                            'first_name': e.get('first_name', ''),
                            'last_name': e.get('last_name', ''),
                            'position': e.get('position', ''),
                            'department': e.get('department', ''),
                            'linkedin': e.get('linkedin', ''),
                            'phone_number': e.get('phone_number', '')
                        }
                        for e in result.get('emails', [])
                    ]
                }
            return None
        except Exception as e:
            return {'error': str(e)}
    
    def email_finder(self, domain, first_name, last_name):
        """根据姓名查找邮箱"""
        url = f"{self.base_url}/email-finder"
        params = {
            'domain': domain,
            'first_name': first_name,
            'last_name': last_name,
            'api_key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('data'):
                result = data['data']
                return {
                    'email': result.get('email'),
                    'score': result.get('score'),
                    'sources': result.get('sources', [])
                }
            return None
        except Exception as e:
            return {'error': str(e)}
    
    def email_verifier(self, email):
        """验证邮箱是否存在"""
        url = f"{self.base_url}/email-verifier"
        params = {
            'email': email,
            'api_key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('data'):
                result = data['data']
                return {
                    'result': result.get('result'),  # deliverable, undeliverable, risky
                    'score': result.get('score'),
                    'regexp': result.get('regexp'),
                    'gibberish': result.get('gibberish'),
                    'disposable': result.get('disposable'),
                    'webmail': result.get('webmail'),
                    'mx_records': result.get('mx_records'),
                    'smtp_server': result.get('smtp_server'),
                    'smtp_check': result.get('smtp_check'),
                    'accept_all': result.get('accept_all'),
                    'block': result.get('block')
                }
            return None
        except Exception as e:
            return {'error': str(e)}
```

#### 7.3.3 Censys API集成

Censys是另一个互联网资产搜索引擎，与Shodan互补。

```python
import requests

class CensysClient:
    def __init__(self, api_id, api_secret):
        self.api_id = api_id
        self.api_secret = api_secret
        self.base_url = "https://search.censys.io/api/v2"
        self.auth = (api_id, api_secret)
    
    def search_hosts(self, query, per_page=25, page=1):
        """搜索主机"""
        url = f"{self.base_url}/hosts/search"
        params = {
            'q': query,
            'per_page': per_page,
            'page': page
        }
        
        try:
            response = requests.get(url, auth=self.auth, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    def get_host(self, ip):
        """获取主机详情"""
        url = f"{self.base_url}/hosts/{ip}"
        
        try:
            response = requests.get(url, auth=self.auth)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    def search_certificates(self, query, per_page=25):
        """搜索证书"""
        url = f"{self.base_url}/certificates/search"
        params = {
            'q': query,
            'per_page': per_page
        }
        
        try:
            response = requests.get(url, auth=self.auth, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
```

### 7.4 自动化信息收集脚本开发

#### 7.4.1 域名信息收集脚本

```python
import dns.resolver
import whois
import requests
import json
import subprocess
from datetime import datetime

class DomainIntelligence:
    def __init__(self, domain):
        self.domain = domain
        self.results = {
            'domain': domain,
            'scan_date': datetime.now().isoformat()
        }
    
    def whois_lookup(self):
        """WHOIS查询"""
        try:
            w = whois.whois(self.domain)
            self.results['whois'] = {
                'registrar': w.registrar,
                'creation_date': str(w.creation_date) if w.creation_date else None,
                'expiration_date': str(w.expiration_date) if w.expiration_date else None,
                'updated_date': str(w.updated_date) if w.updated_date else None,
                'registrant': w.get('registrant', ''),
                'registrant_org': w.get('org', ''),
                'registrant_country': w.get('country', ''),
                'nameservers': w.name_servers if w.name_servers else [],
                'status': w.status if w.status else []
            }
        except Exception as e:
            self.results['whois'] = {'error': str(e)}
        
        return self.results['whois']
    
    def dns_enumeration(self):
        """DNS记录枚举"""
        dns_records = {}
        
        record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA', 'SPF']
        
        for record_type in record_types:
            try:
                answers = dns.resolver.resolve(self.domain, record_type)
                records = []
                for rdata in answers:
                    if record_type == 'A':
                        records.append(rdata.address)
                    elif record_type == 'AAAA':
                        records.append(rdata.address)
                    elif record_type == 'MX':
                        records.append({
                            'priority': rdata.preference,
                            'exchange': str(rdata.exchange)
                        })
                    elif record_type == 'NS':
                        records.append(str(rdata.target))
                    elif record_type == 'TXT':
                        records.append(str(rdata))
                    elif record_type == 'CNAME':
                        records.append(str(rdata.target))
                    elif record_type == 'SOA':
                        records.append({
                            'mname': str(rdata.mname),
                            'rname': str(rdata.rname),
                            'serial': rdata.serial
                        })
                    else:
                        records.append(str(rdata))
                
                dns_records[record_type.lower()] = records
            except Exception as e:
                dns_records[record_type.lower()] = []
        
        self.results['dns'] = dns_records
        return dns_records
    
    def subdomain_discovery(self):
        """子域名发现（使用多种方法）"""
        subdomains = set()
        
        # 方法1: Certificate Transparency
        try:
            url = f"https://crt.sh/?q=%25.{self.domain}&output=json"
            response = requests.get(url, timeout=30)
            data = response.json()
            
            for entry in data:
                name = entry.get('name_value', '')
                for n in name.split('\n'):
                    n = n.strip()
                    if n.endswith(self.domain) and '*' not in n:
                        subdomains.add(n)
        except Exception as e:
            print(f"crt.sh查询失败: {e}")
        
        self.results['subdomains'] = sorted(list(subdomains))
        return sorted(list(subdomains))
    
    def web_tech_detect(self):
        """Web技术检测（简化版）"""
        try:
            url = f"https://{self.domain}"
            response = requests.get(url, timeout=10, allow_redirects=True)
            
            tech_stack = {
                'server': response.headers.get('Server', ''),
                'x_powered_by': response.headers.get('X-Powered-By', ''),
                'x_frame_options': response.headers.get('X-Frame-Options', ''),
                'x_content_type_options': response.headers.get('X-Content-Type-Options', ''),
                'content_security_policy': response.headers.get('Content-Security-Policy', ''),
                'cookies': list(response.cookies.keys())
            }
            
            # 检测常见CMS和框架
            content = response.text.lower()
            
            detections = []
            if 'wordpress' in content or 'wp-content' in content:
                detections.append('WordPress')
            if 'drupal' in content or 'sites/default' in content:
                detections.append('Drupal')
            if 'joomla' in content:
                detections.append('Joomla')
            if 'react' in content:
                detections.append('React')
            if 'vue' in content:
                detections.append('Vue.js')
            if 'jquery' in content:
                detections.append('jQuery')
            if 'bootstrap' in content:
                detections.append('Bootstrap')
            if 'cloudflare' in response.headers.get('server', '').lower():
                detections.append('Cloudflare')
            
            tech_stack['detected_tech'] = detections
            tech_stack['status_code'] = response.status_code
            tech_stack['final_url'] = response.url
            
            self.results['web_tech'] = tech_stack
            return tech_stack
            
        except Exception as e:
            self.results['web_tech'] = {'error': str(e)}
            return {'error': str(e)}
    
    def full_scan(self):
        """执行完整扫描"""
        print(f"开始扫描域名: {self.domain}")
        
        print("  [1/5] WHOIS查询...")
        self.whois_lookup()
        
        print("  [2/5] DNS记录枚举...")
        self.dns_enumeration()
        
        print("  [3/5] 子域名发现...")
        subdomains = self.subdomain_discovery()
        print(f"    发现 {len(subdomains)} 个子域名")
        
        print("  [4/5] Web技术检测...")
        self.web_tech_detect()
        
        print("  [5/5] 生成报告...")
        
        return self.results
    
    def save_report(self, output_file=None):
        """保存扫描报告"""
        if output_file is None:
            output_file = f"{self.domain}_osint_report.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        return output_file
```

#### 7.4.2 社交媒体账号收集脚本

```python
import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

class SocialMediaEnumerator:
    def __init__(self, username):
        self.username = username
        self.results = []
        
        # 预定义的社交媒体平台列表（简化版）
        self.platforms = [
            {'name': 'Twitter', 'url': 'https://twitter.com/{username}', 'method': 'status'},
            {'name': 'Instagram', 'url': 'https://www.instagram.com/{username}/', 'method': 'status'},
            {'name': 'GitHub', 'url': 'https://github.com/{username}', 'method': 'status'},
            {'name': 'YouTube', 'url': 'https://www.youtube.com/@{username}', 'method': 'status'},
            {'name': 'Reddit', 'url': 'https://www.reddit.com/user/{username}/', 'method': 'status'},
            {'name': 'Medium', 'url': 'https://medium.com/@{username}', 'method': 'status'},
            {'name': 'Dev.to', 'url': 'https://dev.to/{username}', 'method': 'status'},
            {'name': 'Pinterest', 'url': 'https://www.pinterest.com/{username}/', 'method': 'status'},
            {'name': 'SoundCloud', 'url': 'https://soundcloud.com/{username}', 'method': 'status'},
            {'name': 'Steam', 'url': 'https://steamcommunity.com/id/{username}', 'method': 'status'},
        ]
    
    def check_platform(self, platform):
        """检查单个平台"""
        url = platform['url'].format(username=self.username)
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
            
            # 简单的状态码检测
            if response.status_code == 200:
                # 进一步验证（检查页面内容是否包含用户名）
                if self.username.lower() in response.text.lower():
                    return {
                        'platform': platform['name'],
                        'url': url,
                        'found': True,
                        'confidence': 0.7,
                        'status_code': response.status_code
                    }
            
            return {
                'platform': platform['name'],
                'url': url,
                'found': False,
                'confidence': 0,
                'status_code': response.status_code
            }
            
        except Exception as e:
            return {
                'platform': platform['name'],
                'url': url,
                'found': False,
                'error': str(e)
            }
    
    def enumerate(self, max_workers=5):
        """枚举所有平台"""
        print(f"正在搜索用户名: {self.username}")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.check_platform, platform): platform
                for platform in self.platforms
            }
            
            for future in as_completed(futures):
                result = future.result()
                self.results.append(result)
                
                if result.get('found'):
                    print(f"  [+] {result['platform']}: {result['url']}")
        
        # 按平台名称排序
        self.results.sort(key=lambda x: x['platform'])
        
        return self.results
    
    def get_found_accounts(self):
        """获取已发现的账号"""
        return [r for r in self.results if r.get('found')]
    
    def save_results(self, output_file=None):
        """保存结果"""
        if output_file is None:
            output_file = f"{self.username}_social_media.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'username': self.username,
                'total_platforms': len(self.platforms),
                'found_count': len(self.get_found_accounts()),
                'results': self.results
            }, f, ensure_ascii=False, indent=2)
        
        return output_file
```

### 7.5 OSINT工具链编排

#### 7.5.1 工具链设计原则

1. **输入标准化**：统一各工具的输入输出格式
2. **模块化设计**：每个工具作为独立模块，便于替换和升级
3. **数据流转**：前一个工具的输出作为后一个工具的输入
4. **错误处理**：单个工具失败不影响整体流程
5. **结果聚合**：统一汇总多工具的结果，去重和关联

#### 7.5.2 企业侦察工具链示例

```python
import json
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

class OSINTPipeline:
    def __init__(self, target, output_dir="osint_results"):
        self.target = target
        self.output_dir = os.path.join(output_dir, target)
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.results = {
            'target': target,
            'start_time': datetime.now().isoformat(),
            'phases': {}
        }
    
    def phase1_domain_intel(self):
        """阶段1：域名基础信息收集"""
        print("=" * 50)
        print("阶段1：域名基础信息收集")
        print("=" * 50)
        
        domain_intel = DomainIntelligence(self.target)
        result = domain_intel.full_scan()
        
        self.results['phases']['domain_intel'] = result
        domain_intel.save_report(
            os.path.join(self.output_dir, "domain_intel.json")
        )
        
        return result
    
    def phase2_subdomain_enum(self):
        """阶段2：子域名枚举"""
        print("\n" + "=" * 50)
        print("阶段2：子域名枚举")
        print("=" * 50)
        
        subdomain_enum = SubdomainDiscovery(
            self.target, 
            output_dir=self.output_dir
        )
        result = subdomain_enum.full_discovery()
        
        self.results['phases']['subdomains'] = result
        
        return result
    
    def phase3_web_tech(self):
        """阶段3：Web技术栈识别"""
        print("\n" + "=" * 50)
        print("阶段3：Web技术栈识别")
        print("=" * 50)
        
        # 对存活的子域名进行技术检测
        subdomains = self.results['phases'].get('subdomains', {}).get('alive_hosts', [])
        tech_results = {}
        
        for host in subdomains[:5]:  # 只检测前5个作为示例
            url = host if host.startswith('http') else f"https://{host}"
            try:
                response = requests.get(url, timeout=10, verify=False)
                tech_results[host] = {
                    'status': response.status_code,
                    'server': response.headers.get('Server', ''),
                    'x_powered_by': response.headers.get('X-Powered-By', '')
                }
            except Exception as e:
                tech_results[host] = {'error': str(e)}
        
        self.results['phases']['web_tech'] = tech_results
        print(f"  检测了 {len(tech_results)} 个主机")
        
        return tech_results
    
    def phase4_employee_enum(self):
        """阶段4：员工信息收集"""
        print("\n" + "=" * 50)
        print("阶段4：员工信息收集")
        print("=" * 50)
        
        # 使用Hunter.io（需要API密钥）
        # hunter = HunterIOClient(api_key="your_api_key")
        # result = hunter.domain_search(self.target)
        
        # 模拟结果
        result = {
            'note': '需要配置Hunter.io API密钥以启用此功能',
            'estimated_emails': []
        }
        
        self.results['phases']['employees'] = result
        print("  跳过（未配置API密钥）")
        
        return result
    
    def phase5_breach_check(self):
        """阶段5：泄露数据检查"""
        print("\n" + "=" * 50)
        print("阶段5：泄露数据检查")
        print("=" * 50)
        
        # 检查域名是否出现在已知泄露中
        checker = HIBPChecker()
        # 注意：完整功能需要API密钥
        # 这里只做密码泄露检查示例
        
        result = {
            'note': '完整泄露检查需要HIBP API密钥',
            'password_breach_check': '可用 check_password() 方法检查单个密码'
        }
        
        self.results['phases']['breach_check'] = result
        print("  基础检查完成")
        
        return result
    
    def run_full_pipeline(self):
        """运行完整的OSINT流水线"""
        print(f"\n开始OSINT侦察: {self.target}")
        print(f"输出目录: {self.output_dir}\n")
        
        try:
            self.phase1_domain_intel()
        except Exception as e:
            print(f"阶段1失败: {e}")
        
        try:
            self.phase2_subdomain_enum()
        except Exception as e:
            print(f"阶段2失败: {e}")
        
        try:
            self.phase3_web_tech()
        except Exception as e:
            print(f"阶段3失败: {e}")
        
        try:
            self.phase4_employee_enum()
        except Exception as e:
            print(f"阶段4失败: {e}")
        
        try:
            self.phase5_breach_check()
        except Exception as e:
            print(f"阶段5失败: {e}")
        
        # 生成最终报告
        self.results['end_time'] = datetime.now().isoformat()
        self._generate_summary()
        self._save_full_report()
        
        print("\n" + "=" * 50)
        print("侦察完成！")
        print(f"报告保存在: {self.output_dir}")
        print("=" * 50)
        
        return self.results
    
    def _generate_summary(self):
        """生成摘要"""
        summary = {
            'target': self.target,
            'subdomain_count': len(
                self.results['phases'].get('subdomains', {}).get('all_subdomains', [])
            ),
            'alive_count': len(
                self.results['phases'].get('subdomains', {}).get('alive_hosts', [])
            ),
        }
        self.results['summary'] = summary
    
    def _save_full_report(self):
        """保存完整报告"""
        report_file = os.path.join(self.output_dir, "full_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        return report_file
```

### 7.6 数据清洗与关联分析

#### 7.6.1 数据清洗的重要性

OSINT收集的原始数据往往存在以下问题：
- 重复数据
- 格式不统一
- 无效或过期信息
- 噪音数据
- 数据缺失

**清洗步骤：**
1. **去重**：移除重复记录
2. **格式标准化**：统一日期、电话号码、姓名等格式
3. **有效性验证**：验证邮箱、域名、URL等是否有效
4. **噪音过滤**：移除无关或错误信息
5. **数据补全**：补充缺失的关键字段

#### 7.6.2 数据关联分析方法

**关联维度：**
- **身份关联**：同一人在不同平台的账号关联
- **时间关联**：事件发生的时间顺序和模式
- **地点关联**：地理位置信息的关联
- **关系关联**：社交关系、组织关系
- **行为关联**：行为模式的相似性

```python
import pandas as pd
from fuzzywuzzy import fuzz
from datetime import datetime

class OSINTDataProcessor:
    def __init__(self):
        pass
    
    def deduplicate_emails(self, email_list):
        """邮箱去重"""
        # 转小写、去空格
        normalized = [
            email.strip().lower() 
            for email in email_list 
            if email and '@' in email
        ]
        
        # 移除重复
        unique = list(set(normalized))
        
        return {
            'original_count': len(email_list),
            'unique_count': len(unique),
            'unique_emails': sorted(unique)
        }
    
    def normalize_phone(self, phone):
        """标准化电话号码（中国）"""
        # 移除空格、横线、括号等
        digits = ''.join(c for c in phone if c.isdigit())
        
        if digits.startswith('86'):
            digits = digits[2:]
        elif digits.startswith('+86'):
            digits = digits[3:]
        
        if len(digits) == 11 and digits.startswith('1'):
            return f"{digits[:3]}****{digits[7:]}"  # 脱敏显示
        elif len(digits) == 11:
            return digits
        
        return digits
    
    def fuzzy_match_names(self, name, name_list, threshold=80):
        """模糊匹配姓名"""
        matches = []
        
        for candidate in name_list:
            # 计算相似度
            ratio = fuzz.ratio(name, candidate)
            partial_ratio = fuzz.partial_ratio(name, candidate)
            token_sort_ratio = fuzz.token_sort_ratio(name, candidate)
            
            # 综合得分
            score = max(ratio, partial_ratio, token_sort_ratio)
            
            if score >= threshold:
                matches.append({
                    'name': candidate,
                    'score': score,
                    'ratio': ratio,
                    'partial_ratio': partial_ratio
                })
        
        return sorted(matches, key=lambda x: x['score'], reverse=True)
    
    def merge_data_sources(self, *data_frames, on='email'):
        """合并多个数据源"""
        if not data_frames:
            return None
        
        result = data_frames[0]
        
        for df in data_frames[1:]:
            result = pd.merge(
                result, df, 
                on=on, 
                how='outer',
                suffixes=('_left', '_right')
            )
        
        return result
    
    def analyze_timeline(self, events, time_field='timestamp'):
        """时间线分析"""
        df = pd.DataFrame(events)
        df[time_field] = pd.to_datetime(df[time_field])
        df = df.sort_values(time_field)
        
        # 时间间隔分析
        df['time_diff'] = df[time_field].diff()
        
        # 按天统计
        df['date'] = df[time_field].dt.date
        daily_counts = df.groupby('date').size()
        
        return {
            'total_events': len(df),
            'date_range': {
                'start': str(df[time_field].min()),
                'end': str(df[time_field].max())
            },
            'avg_interval': str(df['time_diff'].mean()),
            'daily_stats': daily_counts.to_dict(),
            'busiest_day': str(daily_counts.idxmax()),
            'busiest_count': daily_counts.max()
        }
    
    def find_connections(self, data, key_fields):
        """发现数据间的关联"""
        connections = []
        
        # 基于关键字段匹配
        for i, item1 in enumerate(data):
            for j, item2 in enumerate(data[i+1:], i+1):
                shared_fields = []
                for field in key_fields:
                    val1 = item1.get(field)
                    val2 = item2.get(field)
                    if val1 and val2 and val1 == val2:
                        shared_fields.append(field)
                
                if shared_fields:
                    connections.append({
                        'source': i,
                        'target': j,
                        'shared_fields': shared_fields,
                        'strength': len(shared_fields)
                    })
        
        return sorted(connections, key=lambda x: x['strength'], reverse=True)
```

### 7.7 自动化报告生成

#### 7.7.1 报告结构设计

一份好的OSINT报告应包含以下部分：

1. **执行摘要**：关键发现和结论
2. **目标概述**：侦察目标和范围
3. **方法说明**：使用的工具和方法
4. **详细发现**：各维度的详细信息
5. **风险评估**：发现的安全风险
6. **建议措施**：改进建议
7. **附录**：原始数据和参考资料

#### 7.7.2 报告生成工具

```python
import json
import os
from datetime import datetime
from jinja2 import Template

class OSINTReportGenerator:
    def __init__(self, template_dir="templates"):
        self.template_dir = template_dir
    
    def generate_markdown_report(self, data, output_file):
        """生成Markdown格式报告"""
        report = []
        
        # 标题
        report.append(f"# OSINT侦察报告 - {data.get('target', '未知目标')}")
        report.append("")
        report.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**扫描时间**: {data.get('start_time', '未知')} ~ {data.get('end_time', '未知')}")
        report.append("")
        
        # 执行摘要
        report.append("## 执行摘要")
        report.append("")
        summary = data.get('summary', {})
        report.append(f"- **目标**: {data.get('target', '')}")
        report.append(f"- **发现子域名**: {summary.get('subdomain_count', 0)} 个")
        report.append(f"- **存活主机**: {summary.get('alive_count', 0)} 个")
        report.append("")
        
        # 详细发现
        phases = data.get('phases', {})
        
        if 'domain_intel' in phases:
            report.append("## 1. 域名信息")
            report.append("")
            domain_info = phases['domain_intel']
            
            if 'whois' in domain_info and 'error' not in domain_info['whois']:
                whois = domain_info['whois']
                report.append("### 1.1 WHOIS信息")
                report.append("")
                report.append(f"- **注册商**: {whois.get('registrar', 'N/A')}")
                report.append(f"- **注册时间**: {whois.get('creation_date', 'N/A')}")
                report.append(f"- **到期时间**: {whois.get('expiration_date', 'N/A')}")
                report.append(f"- **注册人组织**: {whois.get('registrant_org', 'N/A')}")
                report.append(f"- **注册人国家**: {whois.get('registrant_country', 'N/A')}")
                report.append("")
            
            if 'dns' in domain_info:
                dns = domain_info['dns']
                report.append("### 1.2 DNS记录")
                report.append("")
                for record_type, records in dns.items():
                    if records:
                        report.append(f"**{record_type.upper()}记录**:")
                        if isinstance(records, list):
                            for r in records[:10]:  # 只显示前10条
                                if isinstance(r, dict):
                                    report.append(f"- {r}")
                                else:
                                    report.append(f"- {r}")
                        report.append("")
        
        if 'subdomains' in phases:
            report.append("## 2. 子域名")
            report.append("")
            subdomains = phases['subdomains']
            report.append(f"共发现 **{subdomains.get('total_discovered', 0)}** 个子域名，"
                         f"其中存活 **{subdomains.get('alive_count', 0)}** 个。")
            report.append("")
            
            alive = subdomains.get('alive_hosts', [])
            if alive:
                report.append("### 2.1 存活主机")
                report.append("")
                for host in alive[:20]:  # 只显示前20个
                    report.append(f"- {host}")
                if len(alive) > 20:
                    report.append(f"... 共 {len(alive)} 个")
                report.append("")
        
        # 风险评估
        report.append("## 3. 风险评估")
        report.append("")
        report.append("### 3.1 识别的风险")
        report.append("")
        report.append("- 待根据实际发现填充风险评估内容")
        report.append("")
        
        # 建议
        report.append("## 4. 建议措施")
        report.append("")
        report.append("1. 定期进行OSINT自查，了解公开暴露面")
        report.append("2. 及时清理不必要的公开信息")
        report.append("3. 加强员工安全意识培训")
        report.append("4. 建立信息泄露监测机制")
        report.append("")
        
        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
        
        return output_file
    
    def generate_html_report(self, data, output_file):
        """生成HTML格式报告（使用模板）"""
        # 简化版HTML生成
        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OSINT报告 - {data.get('target', '')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        h3 {{ color: #7f8c8d; }}
        .summary {{ background: #ecf0f1; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        .risk-high {{ color: #e74c3c; }}
        .risk-medium {{ color: #f39c12; }}
        .risk-low {{ color: #27ae60; }}
        table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
        th {{ background: #3498db; color: white; }}
        tr:nth-child(even) {{ background: #f8f9fa; }}
        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #7f8c8d; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>OSINT侦察报告</h1>
        <p><strong>目标:</strong> {data.get('target', '')}</p>
        <p><strong>生成时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <div class="summary">
            <h2>执行摘要</h2>
            <p>发现子域名: <strong>{data.get('summary', {}).get('subdomain_count', 0)}</strong> 个</p>
            <p>存活主机: <strong>{data.get('summary', {}).get('alive_count', 0)}</strong> 个</p>
        </div>
        
        <h2>详细发现</h2>
        <p>（详细内容请参考JSON数据文件）</p>
        
        <div class="footer">
            <p>本报告由OSINT自动化工具生成，仅供参考。</p>
        </div>
    </div>
</body>
</html>
        """
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return output_file
```

---

## 第8章 实战案例

### 8.1 案例1：企业全面OSINT侦察（从域名到员工到技术栈）

#### 8.1.1 背景

**目标企业**：某科技公司（示例：example-tech.com）
**侦察目的**：授权的安全测试前的信息收集
**时间限制**：3个工作日
**输出要求**：完整的企业OSINT报告

#### 8.1.2 侦察计划

**Day 1：基础设施侦察**
- 域名WHOIS和DNS信息收集
- 子域名发现与存活检测
- IP资产和网络范围识别
- 技术栈初步识别

**Day 2：组织与人脉侦察**
- 公司组织架构重建
- 员工邮箱枚举
- 关键人物识别（技术、安全岗位）
- 社交媒体关联分析

**Day 3：深度分析与报告**
- 代码仓库敏感信息检查
- 泄露数据查询
- 文档元数据挖掘
- 风险评估与报告生成

#### 8.1.3 执行过程

**步骤1：域名信息收集**
```python
# 初始化侦察流水线
pipeline = OSINTPipeline("example-tech.com")
result = pipeline.run_full_pipeline()
```

**步骤2：子域名发现**
```
发现的关键子域名：
- admin.example-tech.com → 管理后台（需进一步确认）
- api.example-tech.com → API服务
- dev.example-tech.com → 开发环境
- mail.example-tech.com → 邮件服务器
- staging.example-tech.com → 预发布环境
- wiki.example-tech.com → 内部Wiki（可能公开访问）
```

**步骤3：员工信息收集**
- 使用Hunter.io发现50+员工邮箱
- 邮箱格式：`first.last@example-tech.com`
- 识别出CTO、安全负责人、运维工程师等关键角色
- 在LinkedIn上确认组织架构：技术部约20人，安全团队3人

**步骤4：技术栈分析**
```
主要技术栈：
- 前端：React + TypeScript
- 后端：Node.js + Python (FastAPI)
- 数据库：PostgreSQL + Redis
- 云平台：AWS
- CDN：Cloudflare
- CI/CD：GitHub Actions
- 容器：Docker + Kubernetes
```

**步骤5：代码仓库检查**
- 发现公司GitHub组织有15个公开仓库
- 其中一个仓库的历史提交中包含AWS密钥（已删除但历史仍在）
- 发现内部文档仓库包含架构图和接口文档

**步骤6：泄露数据检查**
- 3个员工邮箱出现在LinkedIn 2021泄露事件中
- 1个邮箱出现在其他小型泄露中
- 未发现公司核心系统的直接泄露

#### 8.1.4 关键发现与风险

**高风险：**
1. GitHub仓库历史提交中包含AWS访问密钥
2. 预发布环境（staging）配置较弱，可能存在漏洞
3. Wiki系统公开访问，包含内部技术文档

**中风险：**
1. 多名员工邮箱密码曾泄露，存在被撞库风险
2. 子域名暴露了较多内部系统
3. 部分员工在社交媒体上泄露工作细节

**低风险：**
1. 域名WHOIS信息保护不完整
2. 部分旧版本技术栈存在已知漏洞

#### 8.1.5 建议措施

1. **立即行动**：轮换泄露的AWS密钥，审计密钥使用情况
2. **短期措施**：限制公开仓库数量，清理Git历史中的敏感信息
3. **中期措施**：建立代码审查机制，防止敏感信息提交
4. **长期措施**：建立持续的OSINT监测机制，定期自查

### 8.2 案例2：个人目标深度画像（社交媒体+泄露数据+人脸搜索）

#### 8.2.1 背景

**目标**：某安全研究员（授权测试用例）
**已知信息**：姓名、Twitter账号
**目标**：构建完整的个人OSINT画像

#### 8.2.2 信息收集过程

**阶段1：Twitter深度挖掘**
- 收集2000+条历史推文
- 提取发布时间规律：工作日10:00-18:00为主，周末较少
- 分析兴趣话题：安全研究、CTF、开源项目、科技新闻
- 提取互动频繁的账号：识别出同事、朋友、同行
- 发现地理位置线索：多次提到某城市的安全会议

**阶段2：跨平台账号发现**
```
使用Sherlock搜索用户名，发现以下平台账号：
- GitHub: github.com/username (确认)
- LinkedIn: linkedin.com/in/username (确认)
- Twitter: @username (已知)
- Medium: medium.com/@username (确认)
- 知乎: zhihu.com/people/username (疑似)
- GitHub: 多个仓库，主要语言为Python和Go
```

**阶段3：人脸搜索验证**
- 从Twitter头像提取人脸
- 使用PimEyes搜索，找到在Instagram的账号（非公开）
- 在安全会议照片中确认身份
- 交叉验证：多个平台照片匹配成功，置信度>95%

**阶段4：泄露数据查询**
- HIBP查询：邮箱出现在2个泄露事件中
  - LinkedIn 2021泄露：职业信息
  - 某论坛泄露：包含密码哈希
- 密码分析：密码模式为"姓名+年份+特殊字符"

**阶段5：职业与技能画像**
```
从LinkedIn和GitHub分析：
- 职位：安全研究员
- 工作经验：5年+
- 技能：渗透测试、漏洞研究、Python/Go开发、逆向工程
- 参与项目：多个开源安全工具
- CTF经历：多次获奖，主攻Web和Pwn
- 教育背景：某大学计算机科学专业
```

#### 8.2.3 社工攻击面分析

**可能的攻击向量：**
1. **鱼叉钓鱼**：使用安全会议、CTF相关话题作为诱饵
2. **恶意文件**：发送伪造的安全研究论文或工具
3. **社交工程**：伪装成同行进行技术交流
4. **账号盗用**：利用泄露的密码尝试登录其他平台

**防御建议：**
1. 启用所有账号的双因素认证
2. 使用密码管理器，避免密码复用
3. 谨慎对待陌生的技术交流请求
4. 定期检查个人信息泄露情况
5. 限制社交媒体上的工作信息披露

### 8.3 案例3：GitHub敏感信息发现与溯源

#### 8.3.1 背景

**目标组织**：某互联网公司的GitHub组织
**目的**：授权的安全评估，发现并修复代码中的敏感信息泄露

#### 8.3.2 发现过程

**步骤1：仓库枚举**
- 发现该组织共有47个公开仓库
- 主要语言：Java、Python、JavaScript、Go
- 包含前端、后端、移动端、运维工具等项目

**步骤2：敏感信息扫描**

使用GitHub API + 自定义Dork搜索：
```
发现的敏感信息：
1. AWS访问密钥
   - 位置：config/credentials.yml (已删除文件)
   - 状态：在提交历史中仍然存在
   - 提交者：某位开发工程师
   - 时间：8个月前

2. 数据库密码
   - 位置：db/init.sql
   - 内容：root用户密码为弱密码
   - 状态：当前版本仍存在（测试环境配置）

3. API密钥
   - 位置：src/config/api-keys.js
   - 内容：第三方服务API密钥
   - 状态：注释中标注为"测试用"，但实际可使用

4. SSH私钥
   - 位置：deploy/id_rsa
   - 状态：在某个测试仓库中
   - 风险：可能用于部署服务器

5. 内部文档
   - 位置：docs/internal/
   - 内容：架构图、接口文档、部署指南
   - 风险：暴露内部系统架构
```

**步骤3：提交历史溯源**
```
对包含敏感信息的文件进行历史追溯：

AWS密钥泄露溯源：
- 首次出现：2023-03-15，提交ID: a1b2c3d
- 提交信息："添加AWS配置"
- 提交者：张三
- 首次删除：2023-05-20，提交ID: e4f5g6h
- 删除信息："移除敏感信息"
- 问题：仅删除了文件，未清理Git历史

数据库密码溯源：
- 首次出现：2022-11-01
- 一直保留至今
- 说明：开发人员误以为是测试环境无所谓
```

**步骤4：影响评估**
```
风险评估：
1. AWS密钥泄露 - 高风险
   - 密钥权限：S3读写权限
   - 可能影响：数据泄露、服务篡改
   - 建议：立即轮换密钥，审计S3访问日志

2. 数据库密码 - 中风险
   - 密码强度：弱密码
   - 适用环境：测试环境
   - 建议：更换强密码，测试环境也不应使用弱密码

3. API密钥 - 中风险
   - 服务：第三方短信服务
   - 可能影响：费用损失、账号滥用
   - 建议：轮换密钥，设置使用限制

4. SSH私钥 - 高风险
   - 用途：部署服务器
   - 可能影响：服务器被入侵
   - 建议：立即更换密钥，审计服务器登录日志
```

#### 8.3.3 修复建议

**立即修复：**
1. 轮换所有泄露的密钥和密码
2. 审计泄露密钥的使用情况
3. 清理Git历史中的敏感信息（使用git filter-repo或BFG Repo-Cleaner）
4. 将敏感仓库设为私有

**长期改进：**
1. 实施pre-commit钩子，阻止敏感信息提交
2. 使用git-secrets或truffleHog定期扫描
3. 建立敏感信息管理规范
4. 加强开发人员安全培训
5. 使用密钥管理服务（如HashiCorp Vault）

### 8.4 案例4：自动化OSINT侦察脚本开发实战

#### 8.4.1 需求分析

**客户需求**：
- 对指定域名进行自动化OSINT侦察
- 输出结构化的JSON报告
- 支持批量目标处理
- 可配置的侦察模块
- 结果可视化展示

**功能模块设计：**
1. 域名信息模块（WHOIS、DNS）
2. 子域名发现模块
3. 端口服务扫描模块
4. 技术栈识别模块
5. 员工信息模块
6. 泄露数据模块
7. 报告生成模块

#### 8.4.2 脚本架构设计

```
osint_tool/
├── main.py                 # 主入口
├── config.py               # 配置文件
├── modules/
│   ├── __init__.py
│   ├── domain.py           # 域名信息
│   ├── subdomain.py        # 子域名发现
│   ├── portscan.py         # 端口扫描
│   ├── webtech.py          # Web技术识别
│   ├── employee.py         # 员工信息
│   └── breach.py           # 泄露数据
├── utils/
│   ├── __init__.py
│   ├── http_client.py      # HTTP客户端
│   ├── dns_utils.py        # DNS工具
│   ├── data_processor.py   # 数据处理
│   └── report_generator.py # 报告生成
└── output/                 # 输出目录
```

#### 8.4.3 核心代码实现

**主程序入口：**
```python
#!/usr/bin/env python3
"""
自动化OSINT侦察工具
用法: python main.py example.com
"""

import argparse
import json
import sys
import os
from datetime import datetime
from modules.domain import DomainModule
from modules.subdomain import SubdomainModule
from modules.webtech import WebTechModule
from modules.breach import BreachModule
from utils.report_generator import ReportGenerator

class OSINTTool:
    def __init__(self, target, config=None):
        self.target = target
        self.config = config or self._default_config()
        self.results = {
            'target': target,
            'start_time': datetime.now().isoformat(),
            'modules': {}
        }
        self.output_dir = os.path.join('output', target)
        os.makedirs(self.output_dir, exist_ok=True)
    
    def _default_config(self):
        return {
            'modules': {
                'domain': {'enabled': True},
                'subdomain': {'enabled': True, 'max_results': 500},
                'webtech': {'enabled': True},
                'employee': {'enabled': False, 'api_key': ''},
                'breach': {'enabled': True, 'api_key': ''}
            },
            'output': {
                'format': ['json', 'markdown'],
                'directory': 'output'
            }
        }
    
    def run_module(self, module_name, module_class):
        """运行单个模块"""
        if not self.config['modules'].get(module_name, {}).get('enabled', False):
            print(f"  [跳过] {module_name} 模块未启用")
            return None
        
        print(f"  [运行] {module_name} 模块...")
        try:
            module = module_class(self.target, self.config['modules'][module_name])
            result = module.run()
            self.results['modules'][module_name] = result
            print(f"  [完成] {module_name} 模块")
            return result
        except Exception as e:
            print(f"  [错误] {module_name} 模块失败: {e}")
            self.results['modules'][module_name] = {'error': str(e)}
            return None
    
    def run_all(self):
        """运行所有启用的模块"""
        print(f"\n{'='*60}")
        print(f"OSINT侦察开始 - 目标: {self.target}")
        print(f"{'='*60}\n")
        
        # 按顺序运行模块
        self.run_module('domain', DomainModule)
        self.run_module('subdomain', SubdomainModule)
        self.run_module('webtech', WebTechModule)
        self.run_module('breach', BreachModule)
        
        # 生成报告
        print("\n  [生成] 生成报告...")
        self.results['end_time'] = datetime.now().isoformat()
        self._generate_reports()
        
        print(f"\n{'='*60}")
        print("侦察完成！")
        print(f"报告目录: {self.output_dir}")
        print(f"{'='*60}\n")
        
        return self.results
    
    def _generate_reports(self):
        """生成各种格式的报告"""
        generator = ReportGenerator(self.results, self.output_dir)
        
        # JSON报告
        json_file = generator.generate_json()
        print(f"    JSON报告: {json_file}")
        
        # Markdown报告
        md_file = generator.generate_markdown()
        print(f"    Markdown报告: {md_file}")


def main():
    parser = argparse.ArgumentParser(description='自动化OSINT侦察工具')
    parser.add_argument('target', help='目标域名')
    parser.add_argument('-c', '--config', help='配置文件路径')
    parser.add_argument('-o', '--output', help='输出目录', default='output')
    parser.add_argument('--modules', nargs='+', 
                       help='指定运行的模块',
                       default=['domain', 'subdomain', 'webtech', 'breach'])
    
    args = parser.parse_args()
    
    # 加载配置
    config = None
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r') as f:
            config = json.load(f)
    
    # 运行工具
    tool = OSINTTool(args.target, config)
    results = tool.run_all()
    
    # 打印摘要
    print("\n侦察摘要:")
    print(f"  目标: {results['target']}")
    for module_name, module_result in results['modules'].items():
        if 'error' not in module_result:
            print(f"  {module_name}: 成功")
        else:
            print(f"  {module_name}: 失败 - {module_result['error']}")


if __name__ == '__main__':
    main()
```

**模块基类：**
```python
# modules/__init__.py
from abc import ABC, abstractmethod

class BaseModule(ABC):
    def __init__(self, target, config=None):
        self.target = target
        self.config = config or {}
    
    @abstractmethod
    def run(self):
        """运行模块，返回结果字典"""
        pass
```

**子域名模块示例：**
```python
# modules/subdomain.py
from . import BaseModule
import requests
import subprocess
import os

class SubdomainModule(BaseModule):
    def run(self):
        results = {
            'subdomains': [],
            'alive_hosts': [],
            'sources': {}
        }
        
        # 方法1: crt.sh
        print("    - 查询crt.sh...")
        crtsh_results = self._crtsh_lookup()
        results['sources']['crtsh'] = len(crtsh_results)
        results['subdomains'].extend(crtsh_results)
        
        # 方法2: 调用subfinder（如果已安装）
        print("    - 运行subfinder...")
        subfinder_results = self._run_subfinder()
        if subfinder_results:
            results['sources']['subfinder'] = len(subfinder_results)
            results['subdomains'].extend(subfinder_results)
        
        # 去重
        results['subdomains'] = sorted(list(set(results['subdomains'])))
        results['total_count'] = len(results['subdomains'])
        
        # 存活检测
        print("    - 存活检测...")
        results['alive_hosts'] = self._check_alive(results['subdomains'][:100])
        results['alive_count'] = len(results['alive_hosts'])
        
        return results
    
    def _crtsh_lookup(self):
        """通过crt.sh发现子域名"""
        try:
            url = f"https://crt.sh/?q=%25.{self.target}&output=json"
            response = requests.get(url, timeout=30)
            data = response.json()
            
            subdomains = set()
            for entry in data:
                name = entry.get('name_value', '')
                for n in name.split('\n'):
                    n = n.strip()
                    if n.endswith(self.target) and '*' not in n:
                        subdomains.add(n)
            
            return list(subdomains)
        except Exception as e:
            print(f"      crt.sh查询失败: {e}")
            return []
    
    def _run_subfinder(self):
        """调用subfinder工具"""
        try:
            result = subprocess.run(
                ['subfinder', '-d', self.target, '-silent'],
                capture_output=True, text=True, timeout=120
            )
            if result.returncode == 0:
                return [line.strip() for line in result.stdout.split('\n') if line.strip()]
        except Exception as e:
            print(f"      subfinder调用失败: {e}")
        return []
    
    def _check_alive(self, subdomains):
        """简单存活检测"""
        alive = []
        for sub in subdomains[:50]:  # 只检测前50个
            try:
                url = f"https://{sub}"
                response = requests.get(url, timeout=5, verify=False)
                alive.append(f"{sub} [{response.status_code}]")
            except:
                try:
                    url = f"http://{sub}"
                    response = requests.get(url, timeout=5)
                    alive.append(f"{sub} [{response.status_code}]")
                except:
                    pass
        return alive
```

#### 8.4.4 使用效果

**运行示例：**
```bash
python main.py example.com
```

**输出：**
```
============================================================
OSINT侦察开始 - 目标: example.com
============================================================

  [运行] domain 模块...
  [完成] domain 模块
  [运行] subdomain 模块...
    - 查询crt.sh...
    - 运行subfinder...
    - 存活检测...
  [完成] subdomain 模块
  [运行] webtech 模块...
  [完成] webtech 模块
  [运行] breach 模块...
  [完成] breach 模块

  [生成] 生成报告...
    JSON报告: output/example.com/full_report.json
    Markdown报告: output/example.com/report.md

============================================================
侦察完成！
报告目录: output/example.com
============================================================

侦察摘要:
  目标: example.com
  domain: 成功
  subdomain: 成功
  webtech: 成功
  breach: 成功
```

---

## 第9章 OSINT工具箱

### 9.1 侦察框架

#### 9.1.1 Recon-ng

**简介**：Recon-ng是一个用Python编写的全功能Web侦察框架，模块化设计，类似Metasploit的交互界面。

**核心特点：**
- 模块化架构，支持数百个模块
- 数据库存储结果，便于查询和分析
- 支持API密钥管理
- 报告生成功能
- 命令行交互界面

**主要模块分类：**
- **Discovery**：发现模块（DNS、WHOIS、搜索引擎等）
- **Recon**：侦察模块（域名、主机、联系人等）
- **Reporting**：报告模块（HTML、CSV、JSON等）
- **Import**：导入模块

**常用命令：**
```bash
# 启动Recon-ng
recon-ng

# 添加工作区
workspaces create target_name

# 添加域名
add domains target.com

# 搜索模块
marketplace search subdomain

# 安装模块
marketplace install recon/domains-hosts/baidu_site

# 加载模块
modules load recon/domains-hosts/baidu_site

# 设置选项
options set SOURCE target.com

# 运行模块
run

# 查看结果
show hosts

# 生成报告
modules load reporting/html
run
```

**常用模块列表：**

| 模块路径 | 功能 | 数据源 |
|---------|------|--------|
| recon/domains-hosts/baidu_site | 百度子域名搜索 | 百度 |
| recon/domains-hosts/bing_domain_web | Bing子域名搜索 | Bing |
| recon/domains-hosts/google_site_web | Google子域名搜索 | Google |
| recon/domains-hosts/netcraft | Netcraft子域名 | Netcraft |
| recon/domains-hosts/certificate_transparency | 证书透明度 | crt.sh |
| recon/hosts-hosts/resolve | 解析IP | DNS |
| recon/hosts-hosts/reverse_resolve | 反向解析 | DNS |
| recon/hosts-ports/shodan_ip | 端口扫描 | Shodan |
| recon/contacts-contacts/namechk | 用户名搜索 | Namechk |
| recon/companies-multi/whois_miner | WHOIS信息 | WHOIS |

#### 9.1.2 theHarvester

**简介**：theHarvester是一个简单但强大的电子邮件、子域名和人名收集工具。

**功能：**
- 电子邮件收集
- 子域名发现
- 虚拟主机发现
- 员工姓名收集
- 开放端口检测

**使用方法：**
```bash
# 基本使用
theHarvester -d example.com -l 100 -b all

# 指定数据源
theHarvester -d example.com -b google,bing,linkedin

# DNS枚举
theHarvester -d example.com -b all -c

# 虚拟主机检测
theHarvester -d example.com -b all -v

# 保存结果
theHarvester -d example.com -b all -f result.html
```

**支持的数据源：**
- baidu、bing、bingapi、censys、certspotter
- crtsh、dnsdumpster、dogpile、duckduckgo
- google、google-plus、google-profiles
- hackerTarget、hunter、intelx
- linkedin、netcraft、otx、securityTrails
- shodan、spyse、threatcrowd、trello
- twitter、urlscan、virustotal、yahoo

#### 9.1.3 SpiderFoot

**简介**：SpiderFoot是一个自动化OSINT收集工具，支持超过200个模块，可以自动进行目标的信息收集和关联分析。

**核心特点：**
- 基于Python开发
- Web界面或命令行界面
- 自动关联发现的信息
- 支持目标类型：IP、域名、邮箱、人名等
- 丰富的模块生态
- 结果可视化

**主要模块类型：**
- **Footprint**：基础信息收集
- **Crawling**：网页爬取
- **Passive DNS**：被动DNS查询
- **Dark Web**：暗网搜索
- **Social Media**：社交媒体搜索
- **Threat Intelligence**：威胁情报

**使用场景：**
- 攻击面评估
- 威胁情报收集
- 资产发现
- 个人信息泄露检测

### 9.2 域名/IP工具

#### 9.2.1 Amass

**简介**：Amass是OWASP项目的子域名枚举工具，集成了多种被动和主动发现技术。

**核心功能：**
- 被动子域名发现（30+数据源）
- 主动子域名爆破
- DNS解析和验证
- 网络基础设施映射
- 子域名劫持检测
- ASN和CIDR发现

**常用命令：**
```bash
# 基本枚举
amass enum -d example.com

# 被动枚举（不主动扫描）
amass enum -passive -d example.com

# 主动枚举（含爆破）
amass enum -active -d example.com

# 指定输出目录
amass enum -d example.com -o results/

# 使用配置文件
amass enum -config config.ini -d example.com

# 显示详细信息
amass enum -v -d example.com

# 枚举多个域名
amass enum -d example1.com -d example2.com

# 图形界面查看结果
amass viz -d3 -d example.com
```

**数据来源：**
- AlienVault OTX、ArchiveIt、Arquivo
- Ask、Baidu、Bing、Censys
- CertSpotter、CommonCrawl、Crtsh
- DNSDB、DNSDumpster、Digitorus
- DuckDuckGo、GitHub、Google
- HackerTarget、IPv4Info
- LinkedIn、Mnemonic、Netcraft
- Pastebin、PTRarchive
- RADb、RapidDNS、Reddit
- SecurityTrails、ShadowServer
- Shodan、Spyse、ThreatCrowd
- Twitter、Umbrella、URLScan
- VirusTotal、Wayback、Yahoo

#### 9.2.2 subfinder

**简介**：subfinder是一个用Go编写的快速子域名发现工具，专为速度和效率设计。

**特点：**
- 快速、轻量
- 25+个被动数据源
- 简单的CLI界面
- 支持多种输出格式
- 易于集成到工作流中

**使用方法：**
```bash
# 基本使用
subfinder -d example.com

# 多个域名
subfinder -d example.com -d example2.com

# 从文件读取域名
subfinder -dL domains.txt

# 静默模式（只输出结果）
subfinder -silent -d example.com

# 保存结果到文件
subfinder -d example.com -o subdomains.txt

# 使用所有可用源
subfinder -d example.com -all

# 递归发现
subfinder -d example.com -recursive

# 显示来源
subfinder -d example.com -v
```

**支持的数据源：**
- ArchiveToday、Arquivo、Ask、BGPView
- Baidu、BufferOver、C99、Censys
- CertSpotter、Chaos、Chinaz、CommonCrawl
- Crtsh、DnsDB、DNSRepo、DNSDumpster
- DuckDuckGo、FullHunt、GitHub
- HackerTarget、Hunter、IntelX
- LeakIX、PassiveTotal、Quake
- Riddler、SecurityTrails、Shodan
- Sitedossier、ThreatBook
- URLScan、VirusTotal、WayBack
- WhoisXMLAPI、Yahoo、ZoomEye

#### 9.2.3 httpx

**简介**：httpx是一个快速的多用途HTTP工具包，用于探测存活主机、获取网页标题、技术栈识别等。

**核心功能：**
- HTTP/HTTPS存活探测
- 状态码检测
- 网页标题获取
- 技术栈检测（Wappalyzer集成）
- 内容长度检测
- 重定向跟随
- favicon哈希计算
- WebSocket检测

**常用命令：**
```bash
# 基本存活检测
cat subdomains.txt | httpx

# 显示状态码和标题
cat subdomains.txt | httpx -status-code -title

# 技术栈检测
cat subdomains.txt | httpx -tech-detect

# 从文件读取
httpx -l subdomains.txt

# 输出到文件
httpx -l subdomains.txt -o alive.txt

# 自定义端口
httpx -l subdomains.txt -ports 80,443,8080,8443

# 跟随重定向
httpx -l subdomains.txt -follow-redirects

# 截图（需要额外配置）
httpx -l subdomains.txt -screenshot

# 批量并发
httpx -l subdomains.txt -threads 100

# JSON输出
httpx -l subdomains.txt -json -o results.json
```

#### 9.2.4 其他域名/IP工具

| 工具名 | 功能 | 特点 |
|-------|------|------|
| massdns | 高速DNS解析器 | C编写，百万级QPS |
| puredns | DNS子域名爆破 | 准确、快速 |
| shuffledns | 子域名枚举 | 基于massdns |
| dnsx | DNS查询工具 | 多功能DNS工具箱 |
| naabu | 端口扫描 | Go编写，快速 |
| masscan | 大规模端口扫描 | 超快，号称5分钟扫全网 |
| nmap | 经典端口扫描 | 功能最全，深度扫描 |
| whatweb | Web技术识别 | 1000+插件 |
| wappalyzer | 技术栈检测 | 浏览器扩展+CLI |
| gobuster | 目录/文件爆破 | Go编写，快速 |
| ffuf | 模糊测试工具 | 快速、灵活 |
| dirsearch | 目录扫描 | Python编写 |

### 9.3 社交媒体工具

#### 9.3.1 用户名枚举工具

| 工具名 | 支持平台数 | 语言 | 特点 |
|-------|-----------|------|------|
| Sherlock | 300+ | Python | 最流行，活跃维护 |
| WhatsMyName | 500+ | 多格式 | 数据集丰富 |
| Namechk | 100+ | Web服务 | 在线工具 |
| KnowEm | 500+ | 商业服务 | 品牌保护 |
| Social Searcher | - | Web服务 | 社交媒体搜索 |
| Snoop | 100+ | Python | 多平台搜索 |

**Sherlock安装与使用：**
```bash
# 安装
pip install sherlock-project

# 或从源码安装
git clone https://github.com/sherlock-project/sherlock.git
cd sherlock
pip install -r requirements.txt

# 使用
python sherlock.py username

# 多用户搜索
python sherlock.py user1 user2 user3

# 只显示找到的
python sherlock.py username --print-found

# 使用Tor
python sherlock.py username --tor

# 指定输出目录
python sherlock.py username --folderoutput results/
```

#### 9.3.2 Twitter/X工具

| 工具 | 功能 | 类型 |
|------|------|------|
| Tweepy | Twitter API Python库 | 库 |
| Twint | Twitter抓取工具（无需API） | 工具 |
| TweetDeck | 多栏监控 | 官方工具 |
| Followerwonk | 粉丝分析 | 商业服务 |
| Twlets | 数据导出 | 浏览器扩展 |
| Twitter Analytics | 官方分析 | 官方功能 |

**Twint使用：**
```bash
# 安装
pip install twint

# 搜索用户推文
twint -u username

# 搜索关键词
twint -s "关键词"

# 搜索包含链接的推文
twint -s "关键词" --links

# 导出为CSV
twint -u username -o output.csv --csv

# 获取粉丝列表
twint -u username --followers

# 获取关注列表
twint -u username --following

# 按时间范围
twint -u username --since 2023-01-01 --until 2023-12-31

# 地理定位
twint -g="39.9042,116.4074,5km"
```

#### 9.3.3 LinkedIn工具

| 工具 | 功能 | 类型 |
|------|------|------|
| LinkedIn Sales Navigator | 高级搜索 | 官方商业服务 |
| PhantomBuster | 自动化数据导出 | SaaS服务 |
| Dux-Soup | 自动化工具 | 浏览器扩展 |
| Lusha | 联系方式查找 | 浏览器扩展 |
| SalesQL | 邮箱查找 | 浏览器扩展 |
| ContactOut | 联系方式查找 | 浏览器扩展 |
| RocketReach | 联系方式查找 | SaaS服务 |

#### 9.3.4 Instagram工具

| 工具 | 功能 | 类型 |
|------|------|------|
| Instaloader | 数据下载/分析 | Python库/CLI |
| ImgInn | 匿名查看 | 在线工具 |
| Picuki | 匿名查看 | 在线工具 |
| SmiHub | 匿名查看 | 在线工具 |
| Greatfon | 匿名查看器 | 在线工具 |

**Instaloader使用：**
```bash
# 安装
pip install instaloader

# 下载用户所有帖子
instaloader profile username

# 下载带位置信息
instaloader --geotags profile username

# 下载特定标签的帖子
instaloader "#hashtag"

# 下载故事
instaloader --stories profile username

# 只下载元数据
instaloader --no-pictures profile username
```

### 9.4 人脸/图像工具

#### 9.4.1 反向图像搜索

| 工具 | 特点 | 网址 |
|------|------|------|
| Google Images | 最大索引库 | images.google.com |
| Yandex Images | 人脸搜索强 | yandex.com/images |
| Bing Visual Search | 微软必应 | bing.com/images |
| PimEyes | 专业人脸搜索 | pimeyes.com |
| TinEye | 最早的反向搜索 | tineye.com |
| Berify | 版权追踪 | berify.com |
| Social Catfish | 身份验证 | socialcatfish.com |
| FaceCheck.ID | 人脸搜索 | facecheck.id |

#### 9.4.2 元数据工具

| 工具 | 功能 | 平台 |
|------|------|------|
| ExifTool | 最强大的元数据工具 | 跨平台（Perl） |
| exifread | Python EXIF读取 | Python库 |
| Pillow | Python图像处理 | Python库 |
| Metadata2Go | 在线元数据查看 | 在线工具 |
| Jeffrey's Viewer | 在线EXIF查看器 | 在线工具 |
| Metapicz | 在线EXIF查看 | 在线工具 |
| FotoForensics | 图像取证分析 | 在线工具 |
| Ghiro | 图像取证分析 | 开源工具 |

**ExifTool常用命令：**
```bash
# 查看所有元数据
exiftool photo.jpg

# 查看GPS信息
exiftool -gps:* photo.jpg

# 递归提取目录
exiftool -r -csv *.jpg > metadata.csv

# 提取特定标签
exiftool -DateTimeOriginal -Make -Model -GPSPosition photo.jpg

# 批量清理元数据
exiftool -all= *.jpg

# 导出为JSON
exiftool -json -a -u photo.jpg > metadata.json

# 查看文件类型和MIME类型
exiftool -FileType -MIMEType photo.jpg
```

#### 9.4.3 人脸分析开源库

| 库名 | 语言 | 功能 |
|------|------|------|
| face_recognition | Python | 人脸识别（基于dlib） |
| OpenCV | C++/Python | 计算机视觉库 |
| dlib | C++/Python | 机器学习/人脸识别 |
| MTCNN | Python | 人脸检测 |
| InsightFace | Python | 人脸分析（ArcFace） |
| DeepFace | Python | 深度学习人脸识别 |
| FaceNet | Python/TensorFlow | 人脸识别算法 |
| MediaPipe | Python/C++ | Google的多媒体框架 |

### 9.5 泄露数据查询平台

#### 9.5.1 主要平台对比

| 平台 | 数据量 | 查询方式 | 价格 | 特点 |
|------|--------|---------|------|------|
| Have I Been Pwned | 120亿+ | 邮箱/域名/密码 | 免费/付费API | 最知名，k-anonymity |
| DeHashed | 数十亿 | 多字段搜索 | 付费 | 数据最全 |
| LeakCheck | 数十亿 | 邮箱/IP/域名 | 免费/付费 | 免费版可用 |
| IntelX | - | 多源搜索 | 免费/付费 | 暗网+明网 |
| Snusbase | 数亿 | 多字段搜索 | 付费 | 历史泄露数据 |
| BreachDirectory | - | 邮箱/手机号 | 免费/付费 | 多语言支持 |
| Firefox Monitor | 基于HIBP | 邮箱 | 免费 | Mozilla出品 |
| SpyCloud | - | 企业级监测 | 商业服务 | 企业防护 |

#### 9.5.2 暗网情报平台

| 平台 | 类型 | 特点 |
|------|------|------|
| Flashpoint | 商业服务 | 专业暗网情报 |
| Recorded Future | 商业服务 | 威胁情报平台 |
| Intel 471 | 商业服务 | 犯罪网络情报 |
| DarkOwl | 商业服务 | 暗网数据搜索 |
| Terbium Labs | 商业服务 | 暗网监测 |
| Sixgill | 商业服务 | 暗网威胁情报 |
| IntelX | 免费/付费 | 暗网+明网搜索 |
| OnionScan | 开源工具 | 暗网网站扫描 |

### 9.6 Python OSINT库

#### 9.6.1 核心库

| 库名 | 用途 | 安装 |
|------|------|------|
| requests | HTTP请求 | `pip install requests` |
| beautifulsoup4 | HTML解析 | `pip install beautifulsoup4` |
| lxml | XML/HTML解析 | `pip install lxml` |
| selenium | 浏览器自动化 | `pip install selenium` |
| pandas | 数据处理 | `pip install pandas` |
| dnspython | DNS查询 | `pip install dnspython` |
| python-whois | WHOIS查询 | `pip install python-whois` |
| shodan | Shodan API | `pip install shodan` |
| tweepy | Twitter API | `pip install tweepy` |
| PyPDF2 | PDF处理 | `pip install PyPDF2` |
| exifread | EXIF读取 | `pip install exifread` |
| Pillow | 图像处理 | `pip install Pillow` |
| networkx | 网络分析 | `pip install networkx` |
| folium | 地图可视化 | `pip install folium` |
| matplotlib | 数据可视化 | `pip install matplotlib` |

#### 9.6.2 专业OSINT库

| 库名 | 用途 | 说明 |
|------|------|------|
| Phunter | Hunter.io API封装 | 邮箱查找 |
| pwnedpasswords | HIBP密码检查 | 密码泄露查询 |
| censys | Censys API客户端 | 互联网扫描数据 |
| instagrapi | Instagram私有API | Instagram数据获取 |
| facebook-scraper | Facebook抓取 | Facebook数据获取 |
| sherlock | 用户名枚举 | 跨平台用户名搜索 |
| social-analyzer | 社交媒体分析 | 多平台分析 |
| osintgram | Instagram OSINT工具 | Instagram侦察 |
| blackbird | 用户名搜索 | 类似Sherlock |
| maigret | 用户名搜索 | 1000+网站 |
| holehe | 邮箱注册检测 | 邮箱账号发现 |

#### 9.6.3 数据处理库

| 库名 | 用途 | 适用场景 |
|------|------|---------|
| pandas | 表格数据处理 | 大规模数据分析 |
| numpy | 数值计算 | 统计分析 |
| json | JSON处理 | 数据交换格式 |
| csv | CSV处理 | 表格数据导入导出 |
| re | 正则表达式 | 模式匹配、信息提取 |
| fuzzywuzzy | 模糊字符串匹配 | 姓名匹配、去重 |
| jellyfish | 字符串相似度 | 模糊匹配 |
| networkx | 图/网络分析 | 社交网络分析 |
| matplotlib | 静态可视化 | 图表生成 |
| plotly | 交互式可视化 | 交互式图表 |
| seaborn | 统计可视化 | 统计图 |

### 9.7 浏览器扩展与插件

#### 9.7.1 信息收集扩展

| 扩展名称 | 功能 | 浏览器 |
|---------|------|--------|
| Wappalyzer | 技术栈识别 | Chrome/Firefox |
| BuiltWith | 技术栈分析 | Chrome/Firefox |
| Web Developer | Web开发工具 | Chrome/Firefox |
| User-Agent Switcher | UA切换 | Chrome/Firefox |
| FoxyProxy | 代理管理 | Chrome/Firefox |
| EditThisCookie | Cookie编辑 | Chrome/Firefox |
| JSON Viewer | JSON格式化 | Chrome/Firefox |

#### 9.7.2 OSINT专用扩展

| 扩展名称 | 功能 | 说明 |
|---------|------|------|
| OSINT Framework | OSINT资源导航 | 分类整理各类OSINT资源 |
| Bellingcat | OSINT工具箱 | 调查记者工具集 |
| Social Searcher | 社交媒体搜索 | 多平台社交搜索 |
| Lusha | 联系方式查找 | LinkedIn邮箱电话 |
| Hunter.io | 邮箱查找 | 网页上的邮箱发现 |
| SimilarWeb | 网站流量分析 | 网站排名和流量数据 |
| Wayback Machine | 网页存档 | 查看历史版本 |
| Domain Hunter Plus | 过期域名发现 | 域名侦察 |

#### 9.7.3 隐私保护扩展

| 扩展名称 | 功能 | 用途 |
|---------|------|------|
| uBlock Origin | 广告/追踪器拦截 | 防止被追踪 |
| Privacy Badger | 隐私保护 | EFF出品的隐私工具 |
| NoScript | 脚本控制 | 阻止恶意脚本 |
| HTTPS Everywhere | HTTPS强制 | 加密连接 |
| Cookie AutoDelete | 自动清理Cookie | 减少追踪 |
| Decentraleyes | 本地CDN | 防止CDN追踪 |
| Multi-Account Containers | 账号隔离 | Firefox多容器 |
| ClearURLs | URL清理 | 移除追踪参数 |

---

## 第10章 反OSINT与隐私保护

### 10.1 个人数字足迹清理

#### 10.1.1 数字足迹评估

**第一步：了解你的数字足迹**

在清理之前，首先需要了解自己在互联网上留下了多少信息。

**自我审计方法：**
1. **搜索引擎自查**
   - Google搜索你的姓名、邮箱、手机号
   - 使用引号精确匹配：`"你的姓名"`
   - 搜索你的用户名：`site:github.com username`
   - 图片搜索：Google反向图片搜索你的头像

2. **泄露数据检查**
   - Have I Been Pwned查询你的邮箱
   - 检查密码是否泄露
   - 检查手机号是否泄露

3. **社交媒体审计**
   - 列出你使用的所有社交平台
   - 检查每个平台的隐私设置
   - 审查历史发布内容

4. **数据经纪人搜索**
   - 在PeopleFinder、TruthFinder等网站搜索自己
   - 申请删除个人信息

#### 10.1.2 社交媒体清理

**各平台清理要点：**

**Twitter/X：**
- 检查并更新隐私设置
- 审核历史推文，删除敏感内容
- 检查关注和粉丝列表
- 清理旧的直接消息
- 撤销不必要的应用授权

**Facebook：**
- 将个人资料设为好友可见
- 限制旧帖子的可见性
- 关闭面部识别
- 关闭位置历史记录
- 清理应用和网站授权
- 限制广告偏好

**LinkedIn：**
- 审查个人资料中的信息披露
- 调整隐私设置（谁能查看你的资料、 connections）
- 关闭公开个人资料（可选）
- 控制谁能看到你的好友列表
- 管理公司和职位信息的可见性

**Instagram：**
- 设为私密账号（可选）
- 关闭位置标签
- 清理关注的账号和粉丝
- 审查历史帖子和故事
- 关闭同步通讯录

**微博/微信：**
- 微博：限制可见范围、关闭位置、清理旧微博
- 微信：设置好友验证、关闭陌生人查看、清理朋友圈

**清理工具：**
- **TweetDelete**：批量删除旧推文
- **Redact**：多平台批量删除内容
- **DeleteMe**：专业数据删除服务
- **JustDeleteMe**：删除账号指南网站

#### 10.1.3 个人信息删除

**数据经纪人删除：**
很多数据经纪人网站会收集和售卖个人信息，需要主动申请删除。

**主要数据经纪人：**
- Spokeo
- PeopleFinder
- TruthFinder
- Intelius
- BeenVerified
- Whitepages
- Instant Checkmate
- US Search

**删除步骤：**
1. 在每个网站上搜索自己的信息
2. 找到opt-out或删除页面
3. 按照流程提交删除请求
4. 验证身份（通常需要邮箱验证）
5. 定期复查，确认已删除

**简化方法：**
- 使用DeleteMe等付费服务
- 使用PrivacyDuck等隐私管理服务
- 使用自动删除脚本（需谨慎）

### 10.2 隐私保护工具与方法

#### 10.2.1 身份保护

**邮件隐私：**
- 使用邮件别名服务（SimpleLogin、AnonAddy）
- 不同网站使用不同邮箱
- 启用邮箱双因素认证
- 谨慎公开主邮箱

**手机号保护：**
- 使用虚拟手机号（Google Voice、阿里小号等）
- 不同场景使用不同号码
- 不要随意填写手机号
- 关闭手机号登录公开账号

**身份信息保护：**
- 身份证号加密存储
- 不要在网上随意上传身份证照片
- 使用身份证水印
- 定期检查身份证是否被冒用

#### 10.2.2 密码安全

**密码最佳实践：**
1. **使用密码管理器**
   - 推荐：1Password、Bitwarden、KeePass
   - 每个账号使用独立密码
   - 主密码设置强密码

2. **启用双因素认证（2FA）**
   - 优先使用硬件密钥（YubiKey等）
   - 其次使用认证器应用（Authy、Google Authenticator）
   - 最后才考虑短信验证码

3. **定期更换关键账号密码**
   - 邮箱、银行、社交主账号
   - 发现泄露立即更换

**密码强度评估：**
```
弱密码特征：
- 长度小于8位
- 纯数字或纯字母
- 常见单词或姓名
- 生日、手机号等个人信息
- 键盘连续字符

强密码特征：
- 长度12位以上
- 包含大小写字母、数字、特殊字符
- 随机生成
- 不包含个人信息
- 每个账号唯一
```

#### 10.2.3 网络隐私工具

**VPN服务：**
- **Mullvad**：隐私保护最佳，匿名支付
- **ProtonVPN**：瑞士隐私法保护
- **NordVPN**：功能丰富
- **Surfshark**：性价比高

**选择VPN的要点：**
- 无日志政策（已审计验证）
- 位于隐私友好的司法管辖区
- 支持匿名支付（加密货币）
- 不收集个人信息
- 使用安全协议（WireGuard、OpenVPN）

**浏览器选择与配置：**

| 浏览器 | 隐私等级 | 特点 |
|--------|---------|------|
| Tor Browser | 最高 | 基于Firefox，Tor网络集成 |
| Brave | 高 | 内置广告拦截和隐私保护 |
| Firefox | 中高 | 可高度自定义隐私设置 |
| Librewolf | 高 | Firefox隐私强化分支 |
| Chrome | 低 | Google生态，隐私较差 |

**浏览器隐私配置建议：**
- 设置为不跟踪（Do Not Track）
- 阻止第三方Cookie
- 关闭密码自动填充
- 关闭位置服务
- 关闭自动同步
- 定期清理浏览数据
- 使用隐私搜索引繁（DuckDuckGo、Startpage）

#### 10.2.4 移动端隐私保护

**Android隐私：**
- 使用GrapheneOS或LineageOS（高级用户）
- 限制应用权限
- 使用F-Droid替代Google Play
- 启用隐私模式浏览
- 关闭广告ID
- 使用AppOps精细化权限管理

**iOS隐私：**
- 启用"要求应用不跟踪"
- 限制广告跟踪
- 使用"隐藏邮件地址"
- 精确位置关闭（使用大致位置）
- 启用iCloud Private Relay
- 定期审查应用权限

**通讯隐私：**
- 使用Signal替代普通短信
- 使用ProtonMail/Tutanota等加密邮件
- 避免使用云同步通讯录
- 使用端到端加密的聊天工具

### 10.3 企业反OSINT措施

#### 10.3.1 信息暴露面评估

**企业OSINT自查清单：**

**域名和网络资产：**
- [ ] 所有子域名是否必要且已知
- [ ] 测试/开发环境是否公开可访问
- [ ] 管理后台是否暴露在公网
- [ ] 是否有遗忘的旧系统仍在运行
- [ ] DNS记录是否泄露内部信息
- [ ] WHOIS信息是否已保护

**员工信息：**
- [ ] 员工邮箱格式是否容易被推断
- [ ] 员工LinkedIn是否泄露过多内部信息
- [ ] 是否有员工在社交媒体上发布敏感信息
- [ ] 员工邮箱是否出现在泄露数据库中
- [ ] 组织架构信息是否过度暴露

**代码和文档：**
- [ ] GitHub/GitLab上是否有敏感信息
- [ ] 公开仓库是否包含密钥、密码
- [ ] Git历史中是否有已删除的敏感文件
- [ ] 公开文档是否包含内部信息
- [ ] 文档元数据是否清理

**技术信息：**
- [ ] 技术栈是否过度暴露
- [ ] 错误页面是否泄露技术细节
- [ ] HTTP头是否泄露服务器信息
- [ ] 默认账号/密码是否已修改
- [ ] 已知漏洞是否已修复

#### 10.3.2 企业信息保护策略

**1. 代码安全策略**
- 实施代码审查制度
- 使用pre-commit钩子检测敏感信息
- 定期扫描代码仓库
- 密钥使用专用管理服务
- 敏感仓库设为私有

**2. 员工隐私培训**
- OSINT和社工攻击认知培训
- 社交媒体使用规范
- 个人信息保护意识
- 钓鱼攻击识别训练
- 密码安全培训

**3. 技术防护措施**
- WAF部署
- CDN隐藏真实IP
- 错误信息脱敏
- HTTP头安全配置
- 漏洞扫描和修复

**4. 监测与响应**
- 定期OSINT自查
- 泄露数据监测
- 暗网监测
- 品牌保护监测
- 事件响应流程

#### 10.3.3 数据最小化原则

**核心思想：**
只收集和暴露完成业务所必需的最少信息。

**实施方法：**
- 网站注册只收集必要信息
- 员工公开资料只显示必要内容
- 错误页面不显示技术细节
- 文档发布前脱敏处理
- 定期清理不需要的公开信息
- 旧系统和账号及时关闭

### 10.4 OPSEC（操作安全）基础

#### 10.4.1 OPSEC概念

OPSEC（Operations Security，操作安全）是一个源自军事的概念，指通过保护敏感信息来防止对手获得关键情报的过程。

**OPSEC五步流程：**
1. **识别关键信息**：确定需要保护的核心信息
2. **分析威胁**：识别潜在的对手和他们的能力
3. **分析漏洞**：评估信息暴露的薄弱环节
4. **评估风险**：根据威胁和漏洞评估风险等级
5. **实施对策**：采取措施降低风险

#### 10.4.2 OSINT活动中的OPSEC

**身份隔离：**
- 使用独立的侦察账号
- 侦察身份与真实身份完全分离
- 使用独立的邮箱、手机号
- 不同平台使用不同用户名
- 避免在侦察账号中泄露个人特征

**网络匿名：**
- 使用VPN或Tor网络
- 轮换IP地址
- 使用代理链
- 保护DNS查询隐私
- 避免使用真实网络环境

**浏览器指纹防护：**
- 使用Tor Browser或Brave
- 禁用WebRTC
- 限制Canvas读取
- 定期清理Cookie和存储
- 使用反指纹扩展

**行为模式伪装：**
- 避免固定的操作时间
- 模拟真实用户的浏览行为
- 控制请求频率
- 避免形成可识别的模式
- 使用不同的User-Agent

#### 10.4.3 个人OPSEC实践

**日常生活中的OPSEC：**

1. **社交媒体管理**
   - 限制个人信息公开程度
   - 不发布实时位置
   - 不发布工作内容细节
   - 定期清理旧内容
   - 谨慎接受好友请求

2. **通讯安全**
   - 敏感话题使用加密通讯
   - 不在公共WiFi进行敏感操作
   - 注意周围环境（肩窥）
   - 不随意透露个人信息

3. **物理安全**
   - 注意摄像头和麦克风
   - 重要文件物理上锁
   - 设备设置锁屏密码
   - 不在公共场所讨论敏感话题
   - 注意被跟踪或监视的迹象

4. **信息共享控制**
   - 了解你分享的信息的受众
   - 思考信息可能被如何利用
   - 遵循"需要知道"原则
   - 避免过度分享个人生活

#### 10.4.4 OPSEC常见错误

**常见失误：**
- 在多个平台使用相同用户名
- 使用包含个人信息的邮箱
- 头像照片可以反向搜索到其他账号
- 社交媒体上发布真实位置
- 工作和个人账号混用
- 在公共设备上登录敏感账号
- 忽略隐私设置，使用默认配置
- 密码复用或使用弱密码
- 随意授权第三方应用
- 不及时更新软件和系统

**改进方法：**
- 定期进行自我OSINT审计
- 建立隐私检查清单
- 关注新的隐私威胁和工具
- 持续学习和调整策略
- 将隐私保护融入日常习惯

---

## 附录：学习资源推荐

### 书籍
- 《开源情报(OSINT)方法与实践》
- 《Open Source Intelligence Techniques》- Michael Bazzell
- 《Social Engineering: The Art of Human Hacking》
- 《The Art of Memory Forensics》
- 《蓝队手册》

### 网站与博客
- OSINT Framework (osintframework.com)
- Bellingcat (bellingcat.com)
- IntelTechniques (inteltechniques.com)
- 开源情报网
- 安全客、FreeBuf等安全媒体

### 播客与视频
- The Privacy, Security, and OSINT Show
- Darknet Diaries
- Bellingcat Podcast
- YouTube各类OSINT教程

### 社区与论坛
- Reddit: r/OSINT、r/privacy
- Twitter OSINT社区
- 国内安全社区：先知社区、看雪论坛等
- Discord OSINT服务器

---

> **免责声明**：本文档仅用于教育和研究目的。读者应确保在法律允许的范围内使用所学知识，尊重他人隐私，遵守相关法律法规。未经授权的信息收集和使用可能构成违法行为。



