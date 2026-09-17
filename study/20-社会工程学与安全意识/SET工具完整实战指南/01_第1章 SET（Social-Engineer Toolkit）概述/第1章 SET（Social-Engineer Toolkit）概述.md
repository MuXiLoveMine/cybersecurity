# 第1章 SET（Social-Engineer Toolkit）概述

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

---

## 📋 内容审核与补充建议

> 针对「第1章 SET（Social-Engineer Toolkit）概述」部分的内容审核结果：

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
