# 第2章 BeEF环境搭建

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

---

