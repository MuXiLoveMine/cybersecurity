# 第9章 OSINT工具箱

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

---

## 📋 内容审核与补充建议

> 针对「第9章 OSINT工具箱」部分的内容审核结果：

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
