# Vulhub 靶场详解：从搭建到漏洞复现全流程

> **文档定位**：系统介绍 Vulhub 开源漏洞靶场的概念、架构、搭建步骤、使用流程、故障排查与安全合规要求。
>
> **适用对象**：安全初学者 / 渗透测试学习者 / 安全工程师 / 教学讲师
>
> **深度层级**：概念理解 + 操作步骤 + 故障排查
>
> **适用版本**：Vulhub 最新版本（2026 年 GitHub 仓库 master 分支），Docker 24+，Docker Compose v2（内置）
>
> **时效标注**：本文资源链接与版本信息基于 2026 年 9 月验证，请注意时效性。
>
> **安全声明**：本文所有内容仅限测试与教育用途，禁止在生产环境使用。漏洞复现仅限于授权环境。

---

## 目录

1. [Vulhub 是什么](#1-vulhub-是什么)
2. [核心架构与工作原理](#2-核心架构与工作原理)
3. [前置条件](#3-前置条件)
4. [搭建步骤](#4-搭建步骤)
5. [使用流程](#5-使用流程)
6. [Docker Compose 操作速查](#6-docker-compose-操作速查)
7. [常见问题与解决方案](#7-常见问题与解决方案)
8. [安全与合规约束](#8-安全与合规约束)
9. [学习路径建议](#9-学习路径建议)

---

## 1. Vulhub 是什么

### 1.1 定义与定位

Vulhub 是一个开源的**预构建漏洞 Docker 环境集合**（Pre-built Vulnerable Docker Environment Collection）。用户只需一条 `docker compose up -d` 命令即可启动一个完整的漏洞环境，用于安全研究、学习或演示，无需预先具备 Docker 经验。

| 属性 | 说明 |
|---|---|
| **项目名称** | Vulhub |
| **项目类型** | 开源漏洞靶场（Open Source Vulnerability Range） |
| **底层技术** | Docker + Docker Compose |
| **开源协议** | MIT License |
| **官方仓库** | [https://github.com/vulhub/vulhub](https://github.com/vulhub/vulhub) |
| **官方文档** | [https://vulhub.org](https://vulhub.org) |
| **启动方式** | 一条命令启动（Single Command Startup） |
| **目标用户** | 安全研究者、渗透测试学习者、安全工程师、教学讲师 |

> **核心定位**：面向大众的开源漏洞靶场，让安全研究者更加**专注于漏洞原理本身**，而非环境搭建。

### 1.2 收录规模与覆盖范围

Vulhub 当前仓库收录**数百个漏洞环境**，涵盖大量组件与漏洞类型。

**按组件分类的代表性环境**：

| 组件类别 | 代表性漏洞环境 | 漏洞类型 |
|---|---|---|
| **Web 框架** | Spring CVE-2022-22947、Struts2 S2-057、Flask SSTI | RCE / SSTI |
| **中间件** | Tomcat CVE-2017-12615、WebLogic CVE-2017-10271、ActiveMQ CVE-2015-5254 | RCE / 反序列化 |
| **数据库** | PostgreSQL CVE-2019-10164、MongoDB 未授权访问 | RCE / 认证绕过 |
| **CMS 系统** | Drupal CVE-2018-7600、Joomla CVE-2015-8562 | RCE / SQL 注入 |
| **网络服务** | Nginx 路径穿越、Apache CVE-2021-41773 | 路径遍历 / RCE |
| **LLM 应用** | LangChain CVE-2023-36188、Flowise RCE | RCE / SSRF |
| **其他组件** | Django CVE-2017-12794、Node.js 实战环境 | XXE / XSS / SSRF |

**按漏洞类型分类**：

| 漏洞类型 | 英文术语 | 代表性环境示例 |
|---|---|---|
| 远程代码执行 | Remote Code Execution (RCE) | Spring CVE-2022-22947 |
| SQL 注入 | SQL Injection (SQLi) | Drupal CVE-2018-7600 |
| 反序列化 | Deserialization | WebLogic CVE-2017-10271 |
| 路径遍历 | Path Traversal | Nginx 路径穿越 |
| 认证绕过 | Authentication Bypass | Apache ShenYu CVE-2022-23944 |
| 服务端请求伪造 | Server-Side Request Forgery (SSRF) | Flask SSRF 示例 |
| 服务端模板注入 | Server-Side Template Injection (SSTI) | Flask SSTI |
| XML 外部实体 | XML External Entity (XXE) | Apache Solr XXE |
| 跨站脚本 | Cross-Site Scripting (XSS) | Node.js XSS 环境 |

### 1.3 适用场景

| 场景 | 说明 |
|---|---|
| **渗透测试学习** | 在隔离环境中练习 OWASP Top 10 漏洞利用 |
| **漏洞原理研究** | 对照 README 复现 CVE 漏洞，理解漏洞成因与利用链 |
| **安全教学实验** | 课堂教学演示，学生可快速搭建环境进行实验 |
| **漏洞复现演示** | 安全团队内部培训、技术分享会演示 |

### 1.4 与同类靶场对比

| 对比维度 | Vulhub | DVWA | Hack The Box | TryHackMe |
|---|---|---|---|---|
| **部署方式** | Docker Compose 一键启动 | PHP + Web 服务器 | 云端在线平台 | 云端在线平台 |
| **环境隔离** | Docker 容器隔离，互不干扰 | 单一 Web 应用 | 远程虚拟机 | 远程虚拟机 |
| **漏洞数量** | 数百个 CVE 环境 | ~10 类基础漏洞 | 持续更新靶机 | 按主题分类 |
| **目录结构** | 每个环境独立目录 + README | 单一应用 | 无本地结构 | 无本地结构 |
| **网络要求** | 首次拉取镜像需联网 | 离线可用 | 持续在线 | 持续在线 |
| **费用** | 免费开源 | 免费开源 | 部分付费 | 部分付费 |
| **适用阶段** | 初级 → 高级 | 初级 | 中级 → 高级 | 初级 → 中级 |
| **离线能力** | 镜像缓存后可离线使用 | 完全离线 | 不支持离线 | 不支持离线 |

> **Vulhub 核心优势**：基于 Docker Compose 实现"一条命令启动"，环境隔离性好，目录结构清晰，每个漏洞环境配有详细的 README 说明复现步骤。

---

## 2. 核心架构与工作原理

### 2.1 底层依赖：Docker + Docker Compose

Vulhub 的底层依赖关系如下：

```
┌─────────────────────────────────────────────────────┐
│                   Vulhub 仓库                        │
│  （docker-compose.yml + Dockerfile + README.md）     │
└──────────────────────┬──────────────────────────────┘
                       │ 引用
                       ▼
┌─────────────────────────────────────────────────────┐
│              Docker Hub / 自定义镜像                 │
│    （预构建的漏洞镜像，如 vulhub/spring:xxx）          │
└──────────────────────┬──────────────────────────────┘
                       │ 拉取并运行
                       ▼
┌─────────────────────────────────────────────────────┐
│              Docker Engine（容器运行时）              │
│     ┌─────────┐  ┌─────────┐  ┌─────────┐          │
│     │ 容器 1  │  │ 容器 2  │  │ 容器 3  │          │
│     │(漏洞App)│  │(数据库) │  │(辅助服务)│          │
│     └─────────┘  └─────────┘  └─────────┘          │
└──────────────────────┬──────────────────────────────┘
                       │ 端口映射
                       ▼
┌─────────────────────────────────────────────────────┐
│              宿主机网络（Host Network）               │
│         http://your-ip:port → 容器服务               │
└─────────────────────────────────────────────────────┘
```

**关键说明**：

- Vulhub **本身不包含镜像**，而是通过 `docker-compose.yml` 文件引用官方或自定义的漏洞镜像
- 首次启动时 Docker 自动从 Docker Hub 拉取所需镜像
- 后续启动直接使用本地缓存的镜像，无需联网

### 2.2 目录结构

每个漏洞环境存储在独立目录中，路径格式为：

```
vulhub/
├── [应用程序]/
│   ├── [漏洞编号或名称]/
│   │   ├── docker-compose.yml    # Compose 编排文件
│   │   ├── Dockerfile            # 镜像构建定义（部分环境有）
│   │   ├── README.md             # 漏洞说明与复现步骤
│   │   ├── README.zh-cn.md       # 中文说明（部分环境有）
│   │   └── [其他配置文件]         # 如 nginx.conf、application.yml
│   └── ...
├── flask/
│   └── ssti/
│       ├── docker-compose.yml
│       └── README.md
├── spring/
│   └── CVE-2022-22947/
│       ├── docker-compose.yml
│       └── README.md
├── tomcat/
│   └── CVE-2017-12615/
│       ├── docker-compose.yml
│       └── README.md
└── ...
```

**目录结构说明**：

| 文件/目录 | 用途 | 说明 |
|---|---|---|
| `docker-compose.yml` | Compose 编排文件 | 定义服务、端口映射、依赖关系 |
| `Dockerfile` | 镜像构建定义 | 部分环境需要本地构建镜像 |
| `README.md` | 漏洞说明文档 | 包含漏洞描述、影响版本、复现步骤 |
| `README.zh-cn.md` | 中文说明文档 | 部分环境提供中文翻译 |
| 配置文件 | 应用特定配置 | 如 Nginx 配置、应用配置文件 |

### 2.3 启动机制

```
用户执行 docker compose up -d
           │
           ▼
    读取 docker-compose.yml
           │
           ▼
    检查本地是否存在所需镜像
           │
     ┌─────┴─────┐
     │           │
   存在        不存在
     │           │
     │     从 Docker Hub 拉取镜像
     │           │
     └─────┬─────┘
           │
           ▼
    创建并启动容器
           │
           ▼
    按端口映射暴露服务
           │
           ▼
    http://your-ip:port 可访问
```

> **重要提示**：现代 Docker（v20.10+）已内置 `docker compose` 命令，不再需要单独安装 `docker-compose` 二进制文件。如果仍使用旧版 Docker，需单独安装 docker-compose。

### 2.4 docker-compose.yml 示例

以下是一个典型的 Vulhub docker-compose.yml 文件示例：

```yaml
version: '3'
services:
  web:
    image: vulhub/spring:1.0.0    # 漏洞镜像名称
    ports:
      - "8080:8080"               # 端口映射：宿主机端口:容器端口
    # 可选：指定平台（Apple Silicon 需要此配置）
    # platform: linux/amd64
    # 可选：环境变量
    # environment:
    #   - DEBUG=true
    # 可选：数据卷
    # volumes:
    #   - ./data:/app/data
```

**关键字段解读**：

| 字段 | 说明 | 示例 |
|---|---|---|
| `image` | 使用的 Docker 镜像 | `vulhub/spring:1.0.0` |
| `ports` | 端口映射（宿主机:容器） | `"8080:8080"` |
| `platform` | 指定运行平台（ARM 场景） | `linux/amd64` |
| `environment` | 环境变量 | `DEBUG=true` |
| `volumes` | 数据卷挂载 | `./data:/app/data` |
| `depends_on` | 服务依赖顺序 | `db` |

---

## 3. 前置条件

### 3.1 系统与硬件要求

| 要求项 | 最低配置 | 推荐配置 | 说明 |
|---|---|---|---|
| **操作系统** | Linux / macOS / Windows(WSL2) | Ubuntu 22.04+ 或 Kali Linux | WSL2 为 Windows 推荐 |
| **CPU** | 2 核 | 4 核+ | 部分环境资源需求较高 |
| **内存（RAM）** | 1 GB | 4 GB+ | 多容器环境需更多内存 |
| **磁盘空间** | 10 GB | 30 GB+ | Docker 镜像占用空间 |
| **Docker 版本** | 20.10+ | 24.0+ | 内置 docker compose |
| **网络** | 首次需联网拉取镜像 | 可配置镜像加速器 | 后续可离线使用 |

### 3.2 各操作系统安装 Docker

**Ubuntu / Debian**：

```bash
# 方法一：官方一键脚本（推荐）
curl -s https://get.docker.com/ | sh

# 方法二：apt 包管理器
sudo apt update
sudo apt install docker.io -y
```

**CentOS / RHEL**：

```bash
# 方法一：官方一键脚本
curl -s https://get.docker.com/ | sh

# 方法二：yum 包管理器
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install docker-ce docker-ce-cli containerd.io -y
```

**Kali Linux**：

```bash
# Kali 通常已预装 Docker，若未安装：
sudo apt update
sudo apt install docker.io -y
```

**Windows（WSL2）**：

```powershell
# 安装 Docker Desktop（包含 WSL2 后端）
# 从 https://www.docker.com/products/docker-desktop/ 下载安装
# 安装时勾选 "Use WSL 2 based engine"

# 或在 WSL2 Ubuntu 中直接安装：
sudo apt update && sudo apt install docker.io -y
```

> **注意**：Windows 环境推荐使用 WSL2 + Docker Desktop，而非直接在 Windows 宿主上运行 Docker。

### 3.3 Docker 服务管理

```bash
# 启动 Docker 服务
sudo systemctl start docker

# 设置开机自启
sudo systemctl enable docker

# 验证 Docker 安装
sudo docker run hello-world

# 验证 docker compose 可用
docker compose version
```

### 3.4 配置 Docker 镜像加速器（中国大陆网络）

> **背景**：Docker Hub 在中国大陆可能无法直接访问，需配置镜像加速器。

```bash
# 编辑 Docker 配置文件
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": [
    "https://docker.1panel.live",
    "https://hub.rat.dev",
    "https://docker.rainbond.cc"
  ]
}
EOF

# 重启 Docker 服务使配置生效
sudo systemctl daemon-reload
sudo systemctl restart docker

# 验证加速器配置
docker info | grep -A 5 "Registry Mirrors"
```

> **风险提示**：修改 `daemon.json` 后必须重启 Docker 服务，重启期间所有容器将暂停。请在非生产时段操作。

---

## 4. 搭建步骤

### 4.1 搭建流程总览

```
步骤一：安装 Docker
    │
    ▼
步骤二：启动 Docker 服务
    │
    ▼
步骤三：克隆 Vulhub 仓库
    │
    ▼
步骤四：验证安装
    │
    ▼
搭建完成，可开始使用
```

### 4.2 步骤一：安装 Docker

参照 [3.2 各操作系统安装 Docker](#32-各操作系统安装-docker) 章节完成安装。

**安装后验证**：

```bash
docker --version
# 预期输出：Docker version 24.x.x 或更高

docker compose version
# 预期输出：Docker Compose version v2.x.x
```

### 4.3 步骤二：启动 Docker 服务

```bash
# 启动 Docker 服务
sudo systemctl start docker

# 设置开机自启（推荐）
sudo systemctl enable docker

# 检查服务状态
sudo systemctl status docker
# 预期输出：active (running)
```

> **权限提示**：后续 docker 命令如不想每次加 `sudo`，可将当前用户加入 docker 组：
> ```bash
> sudo usermod -aG docker $USER
> # 需注销并重新登录后生效
> ```
> **安全警告**：加入 docker 组等同于授予 root 级别权限，仅限开发/测试环境使用。

### 4.4 步骤三：克隆 Vulhub 仓库

**方法一：Git Clone（推荐）**

```bash
# --depth 1 只拉取最新一次提交，节省空间和时间
git clone --depth 1 https://github.com/vulhub/vulhub.git
```

**方法二：下载 ZIP（网络受限时使用）**

```bash
# 下载压缩包
wget https://github.com/vulhub/vulhub/archive/master.zip -O vulhub-master.zip

# 解压
unzip vulhub-master.zip
mv vulhub-master vulhub
```

**方法三：使用代理或镜像站（中国大陆）**

```bash
# 使用 GitHub 镜像站
git clone --depth 1 https://ghproxy.com/https://github.com/vulhub/vulhub.git

# 或使用 GitHub CLI（如已安装）
gh repo clone vulhub/vulhub
```

### 4.5 步骤四：验证安装

```bash
# 进入 Vulhub 目录
cd vulhub

# 查看漏洞环境列表
ls
# 预期输出：各组件目录名（如 flask、spring、tomcat、weblogic 等）

# 进入任意环境目录查看
ls flask/ssti/
# 预期输出：docker-compose.yml  README.md

# 查看某个环境的 docker-compose.yml 内容
cat flask/ssti/docker-compose.yml
```

**验证检查清单**：

| 检查项 | 命令 | 预期结果 |
|---|---|---|
| Docker 已安装 | `docker --version` | 输出 Docker 版本号 |
| Docker 服务运行 | `sudo systemctl status docker` | active (running) |
| docker compose 可用 | `docker compose version` | 输出 Compose 版本号 |
| Vulhub 仓库已克隆 | `ls vulhub/` | 显示组件目录列表 |
| 环境文件存在 | `ls vulhub/flask/ssti/` | 包含 docker-compose.yml |

---

## 5. 使用流程

### 5.1 使用流程总览

```
选择漏洞环境
    │
    ▼
启动环境（docker compose up -d）
    │
    ▼
检查状态（docker compose ps）
    │
    ▼
访问环境（浏览器/curl 访问映射端口）
    │
    ├──→ 进入容器调试（docker compose exec）
    ├──→ 查看日志（docker compose logs）
    │
    ▼
复现漏洞（按 README 步骤操作）
    │
    ▼
清理环境（docker compose down -v）
```

### 5.2 步骤一：选择漏洞环境

```bash
# 查看所有分类目录
ls vulhub/

# 根据学习目标选择，例如 Spring CVE-2022-22947
cd vulhub/spring/CVE-2022-22947

# 阅读漏洞说明
cat README.md
```

> **提示**：README.md 中包含漏洞描述、影响版本、复现步骤和利用方法说明。部分环境提供中文版 `README.zh-cn.md`。

### 5.3 步骤二：启动环境

```bash
# 后台启动容器（-d 表示 detached 模式，后台运行）
docker compose up -d

# 预期输出：
# [+] Running X/2
#  ✔ Container xxx  Started
#  ✔ Container xxx  Started
```

首次启动时 Docker 会自动拉取镜像，可能需要较长时间（取决于网络速度）。

### 5.4 步骤三：检查状态

```bash
# 查看容器状态和端口映射
docker compose ps

# 预期输出示例：
# NAME                IMAGE               STATUS         PORTS
# spring-web-1       vulhub/spring:1.0    Up 30 seconds  0.0.0.0:8080->8080/tcp
```

**端口映射说明**：

```
0.0.0.0:8080 -> 8080/tcp
    │              │
    │              └── 容器内部端口
    │
    └── 宿主机监听端口（即 your-ip:8080）
```

> **重要提示**：`your-ip` 指宿主机 IP，不是 Docker 容器 IP。如果在本地访问使用 `127.0.0.1` 或 `localhost`，如果在虚拟机中需使用虚拟机 IP。

### 5.5 步骤四：访问环境

```bash
# 使用 curl 测试访问
curl http://127.0.0.1:8080

# 或在浏览器中打开
# http://127.0.0.1:8080
# http://your-server-ip:8080
```

### 5.6 步骤五：进入容器调试

```bash
# 进入容器 Shell（需替换 [容器名称]）
docker compose exec web bash

# 在容器内可执行的调试操作：
ls /app                    # 查看应用文件
cat /app/application.yml   # 查看配置
ps aux                     # 查看运行进程
env                        # 查看环境变量
exit                       # 退出容器
```

> **说明**：`[容器名称]` 可通过 `docker compose ps` 获取，通常格式为 `服务名-数字`（如 `web-1`）。

### 5.7 步骤六：查看日志

```bash
# 实时跟踪所有容器日志（-f 表示 follow）
docker compose logs -f

# 查看特定容器日志
docker compose logs web

# 查看最近 100 行日志
docker compose logs --tail 100 web

# 查看最近 5 分钟的日志
docker compose logs --since 5m web
```

### 5.8 步骤七：复现漏洞

按照 README.md 中的复现步骤，使用渗透测试工具进行漏洞验证：

| 工具 | 用途 | 示例命令 |
|---|---|---|
| **curl** | HTTP 请求测试 | `curl -X POST http://127.0.0.1:8080/api -d 'payload'` |
| **Burp Suite** | HTTP 请求拦截与修改 | 配置浏览器代理至 Burp |
| **sqlmap** | SQL 注入自动化 | `sqlmap -u "http://127.0.0.1:8080/?id=1" --batch` |
| **nmap** | 端口扫描与服务识别 | `nmap -sV -p- 127.0.0.1` |
| **Metasploit** | 漏洞利用框架 | `use exploit/...` |

> **安全警告**：所有漏洞复现操作仅限在隔离的测试环境中进行，严禁对未授权系统使用上述工具。

### 5.9 步骤八：清理环境

```bash
# 停止并删除容器和数据卷（推荐）
docker compose down -v

# 仅停止并删除容器（保留数据卷）
docker compose down

# 清理拉取的镜像（可选，释放磁盘空间）
docker image rm $(docker compose images -q)
```

> **资源管理提示**：学习完成后务必执行 `docker compose down -v` 清理环境，释放系统资源。长期不清理会导致磁盘空间不足。

---

## 6. Docker Compose 操作速查

### 6.1 核心操作速查表

| 操作 | 命令 | 说明 | 使用场景 |
|---|---|---|---|
| 启动环境 | `docker compose up -d` | 后台启动当前目录的漏洞环境 | 首次启动或重启 |
| 停止环境 | `docker compose stop` | 停止容器但不删除 | 暂时暂停 |
| 启动已停止 | `docker compose start` | 重新启动已停止的容器 | 恢复运行 |
| 停止删除 | `docker compose down` | 停止并删除容器 | 简单清理 |
| 清理环境 | `docker compose down -v` | 停止容器并删除数据卷 | 完整清理（推荐） |
| 查看状态 | `docker compose ps` | 显示容器状态和端口映射 | 排查问题 |
| 查看日志 | `docker compose logs -f` | 实时跟踪日志 | 监控行为 |
| 进入容器 | `docker compose exec web bash` | 进入容器 Shell | 调试环境 |
| 重新构建 | `docker compose build` | 重新构建镜像 | Dockerfile 有修改 |
| 重启服务 | `docker compose restart` | 重启所有服务 | 配置更新后 |
| 拉取镜像 | `docker compose pull` | 拉取最新镜像 | 更新环境 |
| 查看配置 | `docker compose config` | 显示解析后的配置 | 验证 yml 语法 |

### 6.2 Docker 通用命令速查

| 操作 | 命令 | 说明 |
|---|---|---|
| 查看所有容器 | `docker ps -a` | 包括已停止的容器 |
| 查看所有镜像 | `docker images` | 列出本地镜像 |
| 删除镜像 | `docker rmi [镜像名]` | 删除指定镜像 |
| 清理悬空资源 | `docker system prune -a` | 清理无用镜像、容器、网络 |
| 查看 Docker 信息 | `docker info` | 系统、存储、网络信息 |
| 查看 Docker 磁盘 | `docker system df` | 磁盘使用统计 |
| 容器资源监控 | `docker stats` | 实时 CPU/内存/网络 |

### 6.3 批量清理命令

```bash
# 停止所有运行中的容器
docker stop $(docker ps -q)

# 删除所有容器
docker rm $(docker ps -aq)

# 删除所有未使用的镜像
docker image prune -a

# 完整清理（谨慎！会删除所有未使用的资源）
docker system prune -a --volumes
```

> **高风险警告**：`docker system prune -a --volumes` 会删除所有未使用的镜像和数据卷，请确认无重要数据后再执行。

---

## 7. 常见问题与解决方案

### 7.1 问题一：Docker 镜像拉取失败

**现象**：

```
Error: Get https://registry-1.docker.io/v2/: net/http: request canceled
```

**原因**：Docker Hub 在中国大陆可能无法直接访问，网络超时或被阻断。

**解决方案**：

```bash
# 方案一：配置镜像加速器（推荐）
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": [
    "https://docker.1panel.live",
    "https://hub.rat.dev",
    "https://docker.rainbond.cc"
  ]
}
EOF
sudo systemctl daemon-reload
sudo systemctl restart docker

# 方案二：使用代理
export HTTP_PROXY=http://your-proxy:port
export HTTPS_PROXY=http://your-proxy:port
docker compose up -d

# 方案三：在境外 VPS / 云服务器上运行 Vulhub
```

### 7.2 问题二：Apple Silicon（M 系列芯片）Mac 启动失败

**现象**：

```
exec format error
or
no matching manifest for linux/arm64/v8
```

**原因**：大多数 Vulhub 环境为 x86（amd64）架构构建，无法在 ARM 架构上原生运行。

**解决方案**：

```bash
# 方案一：设置环境变量（推荐，全局生效）
export DOCKER_DEFAULT_PLATFORM=linux/amd64
docker compose up -d

# 方案二：在 docker-compose.yml 中添加 platform 字段
# 编辑 docker-compose.yml，在服务下添加：
# services:
#   web:
#     platform: linux/amd64
#     image: ...

# 方案三：使用 Docker Desktop 的 Rosetta 模拟
# Docker Desktop → Settings → Features → Use Rosetta for x86/amd64 emulation
```

> **注意**：通过 Rosetta/QEMU 模拟运行 x86 镜像可能有性能损失，部分环境可能存在兼容性问题。

### 7.3 问题三：Kali Linux 启动报错 "too many open files"

**现象**：

```
ERROR: reexec docker... too many open files
```

**原因**：Kali 系统的 `ulimit nofile` 设置过低，Docker 容器打开文件数超限。

**解决方案**：

```bash
# 编辑 Docker 配置文件
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "default-ulimits": {
    "nofile": {
      "Name": "nofile",
      "Hard": 65535,
      "Soft": 65535
    }
  }
}
EOF

# 重启 Docker 服务
sudo systemctl daemon-reload
sudo systemctl restart docker

# 验证配置生效
docker run --rm busybox sh -c "ulimit -n"
# 预期输出：65535
```

### 7.4 问题四：容器启动成功但无法访问

**排查方向**：

| 排查步骤 | 命令 | 说明 |
|---|---|---|
| 1. 检查端口映射 | `docker compose ps` | 确认端口映射是否正确 |
| 2. 检查容器状态 | `docker compose ps` | 确认状态为 running |
| 3. 检查宿主机防火墙 | `sudo ufw status` 或 `sudo iptables -L -n` | 确认端口已放行 |
| 4. 检查容器内服务 | `docker compose exec web ss -tlnp` | 确认服务在容器内监听 |
| 5. 检查 README | `cat README.md` | 确认是否有特殊访问方式 |
| 6. 检查日志 | `docker compose logs` | 查看是否有启动错误 |

**常见修复**：

```bash
# 放行防火墙端口（Ubuntu UFW）
sudo ufw allow 8080/tcp

# 放行防火墙端口（CentOS firewalld）
sudo firewall-cmd --add-port=8080/tcp --permanent
sudo firewall-cmd --reload

# 放行防火墙端口（iptables）
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
```

### 7.5 问题五：权限错误

**现象**：

```
permission denied while trying to connect to the Docker daemon socket
```

**原因**：当前用户无 Docker 操作权限，或对 Vulhub 目录无读写权限。

**解决方案**：

```bash
# 方案一：将用户加入 docker 组（推荐）
sudo usermod -aG docker $USER
# 需注销并重新登录后生效

# 方案二：使用 sudo 运行（临时）
sudo docker compose up -d

# 方案三：修改 Vulhub 目录权限
sudo chown -R $USER:$USER vulhub/
chmod -R 755 vulhub/
```

> **安全警告**：`sudo usermod -aG docker $USER` 等同于授予该用户 root 级别权限，仅限开发/测试环境。生产环境应使用更严格的权限管理方案。

### 7.6 问题六：磁盘空间不足

**现象**：

```
no space left on device
```

**解决方案**：

```bash
# 查看 Docker 磁盘使用情况
docker system df

# 清理未使用的镜像、容器、网络
docker system prune

# 清理未使用的数据卷（谨慎！）
docker system prune -a --volumes

# 删除特定镜像
docker rmi $(docker images -f "dangling=true" -q)
```

### 7.7 问题速查表

| 问题现象 | 可能原因 | 快速解决方案 |
|---|---|---|
| 镜像拉取失败/超时 | 网络限制 | 配置镜像加速器 |
| exec format error | 架构不匹配（ARM vs x86） | 设置 `DOCKER_DEFAULT_PLATFORM=linux/amd64` |
| too many open files | ulimit 限制 | 配置 `daemon.json` 提升 nofile |
| 无法访问端口 | 防火墙/端口未映射 | 检查 `docker compose ps` + 放行端口 |
| permission denied | 用户权限不足 | 加入 docker 组或使用 sudo |
| no space left | 磁盘空间不足 | `docker system prune -a` |
| 容器不断重启 | 应用启动失败 | 查看 `docker compose logs` 排查 |
| 端口冲突 | 宿主机端口被占用 | 修改 yml 中端口映射 |

---

## 8. 安全与合规约束

### 8.1 使用红线

> **以下红线不可逾越，违反可能导致法律责任：**

| 红线 | 说明 | 违反后果 |
|---|---|---|
| **仅限测试与教育** | 所有环境仅用于测试和教育目的 | 用于生产环境可能造成数据泄露 |
| **隔离环境运行** | 必须在虚拟机或隔离网络中运行 | 漏洞环境暴露可能导致被攻击 |
| **授权边界** | 漏洞复现仅限于你拥有或获得明确授权的环境 | 攻击未授权系统属于违法行为 |
| **资源清理** | 学习完成后及时清理环境 | 未清理环境持续消耗资源 |
| **网络隔离** | 建议在无外网访问的隔离网络中运行 | 防止漏洞环境被意外暴露或利用 |

### 8.2 推荐安全架构

```
┌─────────────────────────────────────────┐
│            隔离网络（Host-Only）          │
│                                         │
│   ┌───────────┐    ┌───────────────┐   │
│   │ 攻击者机器 │◄──►│ Vulhub 容器群 │   │
│   │ (Kali VM)  │    │ (漏洞环境)    │   │
│   └───────────┘    └───────────────┘   │
│                                         │
│   ✗ 无外网连接（防止漏洞环境被外部访问）    │
│   ✗ 无共享文件夹（防止宿主机文件泄露）      │
└─────────────────────────────────────────┘
```

### 8.3 安全检查清单

在开始使用 Vulhub 前，请逐项确认：

- [ ] 运行环境为虚拟机或隔离网络（非物理机/生产机）
- [ ] 网络已隔离或限制外网访问
- [ ] 已了解所有操作仅限授权环境
- [ ] 已规划环境清理流程（`docker compose down -v`）
- [ ] 宿主机已安装最新安全补丁
- [ ] Docker 已配置安全限制（如资源限制、网络隔离）
- [ ] 不在 Vulhub 环境中存储敏感数据
- [ ] 学习完成后及时清理容器和镜像

### 8.4 法律法规参考

| 法规 | 相关条款 | 说明 |
|---|---|---|
| 《网络安全法》 | 第二十七条 | 未经授权侵入他人网络系统属违法行为 |
| 《数据安全法》 | 第三十一条 | 不得非法获取、处理他人数据 |
| 《个人信息保护法》 | 第十条 | 不得非法处理他人个人信息 |
| 等保 2.0 | 安全计算环境 | 漏洞环境不得与等保系统混部 |

> **合规声明**：本文档所有内容均从防御和授权测试角度编写，不提供未授权攻击代码。所有操作仅限在用户拥有或获得明确授权的环境中进行。

---

## 9. 学习路径建议

### 9.1 四阶段学习路线图

```
第一阶段：入门（1-2周）
├── 选择简单漏洞环境
├── 熟悉 Vulhub 操作流程
├── 理解 Docker 基本概念
└── 完成首个漏洞复现
        │
        ▼
第二阶段：进阶（2-4周）
├── 结合 PortSwigger Academy
├── 关联漏洞原理与实战场景
├── 学习使用 Burp Suite
└── 完成多个漏洞类型复现
        │
        ▼
第三阶段：系统学习（1-2月）
├── 按组件分类系统学习
│   ├── 中间件漏洞
│   ├── 框架漏洞
│   └── 数据库漏洞
├── 深入理解漏洞利用链
└── 尝试编写 PoC/EXP
        │
        ▼
第四阶段：沉淀（持续）
├── 记录复现笔记
├── 形成个人漏洞知识库
├── 参与漏洞挖掘社区
└── 关注 CVE 最新动态
```

### 9.2 各阶段推荐环境

| 阶段 | 推荐环境 | 漏洞类型 | 学习目标 |
|---|---|---|---|
| **入门** | `flask/ssti` | SSTI | 熟悉操作流程 |
| **入门** | `tomcat/CVE-2017-12615` | RCE | 理解漏洞利用 |
| **入门** | `drupal/CVE-2018-7600` | RCE | CVE 复现流程 |
| **进阶** | `spring/CVE-2022-22947` | RCE | SpEL 注入原理 |
| **进阶** | `weblogic/CVE-2017-10271` | 反序列化 | Java 反序列化 |
| **进阶** | `struts2/s2-057` | RCE | OGNL 注入 |
| **系统** | `activemq/CVE-2015-5254` | 反序列化 | 中间件安全 |
| **系统** | `nginx/CVE-2017-7529` | 路径遍历 | Web 服务器漏洞 |
| **系统** | `django/CVE-2017-12794` | 信息泄露 | 框架安全 |
| **沉淀** | 按个人兴趣选择 | 综合 | 深度研究 |

### 9.3 推荐学习资源（2026 年）

| 资源名称 | 类型 | 链接 | 说明 |
|---|---|---|---|
| **Vulhub 官方仓库** | 文档+代码 | [github.com/vulhub/vulhub](https://github.com/vulhub/vulhub) | 官方源码与 README |
| **Vulhub 官方文档** | 文档 | [vulhub.org](https://vulhub.org) | 在线文档与索引 |
| **PortSwigger Web Security Academy** | 在线实验 | [portswigger.net/web-security](https://portswigger.net/web-security) | 免费 Web 安全实验室 |
| **Hack The Box** | 在线靶场 | [hackthebox.com](https://www.hackthebox.com) | 渗透测试实战平台 |
| **TryHackMe** | 在线教学 | [tryhackme.com](https://tryhackme.com) | 引导式安全学习 |
| **OWASP Top 10** | 标准 | [owasp.org/Top10](https://owasp.org/www-project-top-ten/) | Web 漏洞分类标准 |
| **Docker 官方文档** | 文档 | [docs.docker.com](https://docs.docker.com) | Docker 使用参考 |

### 9.4 推荐学习顺序（按漏洞类型）

```
1. 文件上传漏洞（File Upload）
   └── 理解前端/后端验证绕过

2. SQL 注入（SQL Injection）
   ├── 基础：字符型/数字型
   ├── 进阶：盲注/时间注入
   └── 工具：sqlmap 实战

3. XSS（跨站脚本）
   ├── 反射型 XSS
   ├── 存储型 XSS
   └── DOM 型 XSS

4. SSTI（服务端模板注入）
   ├── Flask/Jinja2 模板注入
   └── 利用链与沙箱逃逸

5. SSRF（服务端请求伪造）
   ├── 基础 SSRF
   └── 协议利用（file://、gopher://）

6. 反序列化漏洞
   ├── Java 反序列化（WebLogic、Fastjson）
   ├── PHP 反序列化
   └── Python 反序列化

7. RCE（远程代码执行）
   ├── 命令注入
   ├── 代码执行
   └── 框架 RCE（Spring、Struts2）

8. 认证与授权漏洞
   ├── 认证绕过
   ├── 权限提升
   └── 会话管理缺陷
```

### 9.5 笔记模板建议

每次漏洞复现建议记录以下内容：

```markdown
## 漏洞名称：[CVE 编号或名称]

### 基本信息
- 漏洞类型：[RCE / SQLi / XSS / ...]
- 影响组件：[组件名称及版本]
- CVSS 评分：[评分]
- CVE 编号：[CVE-XXXX-XXXX]

### 环境信息
- Vulhub 路径：[如 spring/CVE-2022-22947]
- 启动命令：docker compose up -d
- 访问地址：http://127.0.0.1:8080

### 漏洞原理
[描述漏洞成因和技术原理]

### 复现步骤
1. [步骤一]
2. [步骤二]
3. ...

### PoC / Payload
[记录使用的 Payload]

### 修复建议
[官方修复方案和加固建议]

### 学习心得
[个人理解与拓展思考]
```

---

## 附录

### 附录 A：术语对照表

| 中文术语 | 英文术语 | 说明 |
|---|---|---|
| 漏洞靶场 | Vulnerability Range | 用于安全学习与实践的漏洞环境 |
| 容器 | Container | Docker 运行实例 |
| 镜像 | Image | Docker 只读模板 |
| 编排 | Orchestration | 多容器管理（Docker Compose） |
| 端口映射 | Port Mapping | 宿主机端口到容器端口的映射 |
| 数据卷 | Volume | 容器持久化存储 |
| 远程代码执行 | Remote Code Execution (RCE) | 攻击者可远程执行任意代码 |
| SQL 注入 | SQL Injection (SQLi) | 通过注入 SQL 语句攻击数据库 |
| 反序列化 | Deserialization | 将序列化数据还原为对象时的漏洞 |
| 路径遍历 | Path Traversal | 访问预期目录之外的文件 |
| 认证绕过 | Authentication Bypass | 绕过身份验证机制 |
| 服务端请求伪造 | Server-Side Request Forgery (SSRF) | 服务端发起非预期请求 |
| 服务端模板注入 | Server-Side Template Injection (SSTI) | 注入模板引擎表达式 |
| XML 外部实体 | XML External Entity (XXE) | 利用 XML 实体解析攻击 |
| 跨站脚本 | Cross-Site Scripting (XSS) | 注入恶意客户端脚本 |
| 宿主机 | Host Machine | 运行 Docker 的物理机或虚拟机 |
| 漏洞利用 | Exploit | 利用漏洞获取未授权访问 |
| 概念验证 | Proof of Concept (PoC) | 验证漏洞存在的最小化代码 |

### 附录 B：Vulhub 环境分类速查

| 分类 | 目录名 | 代表性漏洞 | 难度 |
|---|---|---|---|
| **Web 框架** | `spring/` | CVE-2022-22947 (SpEL 注入 RCE) | 中 |
| **Web 框架** | `struts2/` | S2-057 (OGNL 注入 RCE) | 中 |
| **Web 框架** | `flask/` | SSTI (模板注入) | 低 |
| **Web 框架** | `django/` | CVE-2017-12794 (信息泄露) | 中 |
| **中间件** | `tomcat/` | CVE-2017-12615 (RCE) | 低 |
| **中间件** | `weblogic/` | CVE-2017-10271 (反序列化) | 高 |
| **中间件** | `activemq/` | CVE-2015-5254 (反序列化) | 中 |
| **中间件** | `nginx/` | CVE-2017-7529 (路径遍历) | 低 |
| **CMS 系统** | `drupal/` | CVE-2018-7600 (RCE) | 中 |
| **CMS 系统** | `joomla/` | CVE-2015-8562 (RCE) | 中 |
| **数据库** | `postgresql/` | CVE-2019-10164 (RCE) | 高 |
| **LLM 应用** | `langchain/` | CVE-2023-36188 (RCE) | 中 |
| **其他** | `node/` | 多种 XSS / 原型链污染 | 低 |

### 附录 C：服务协议类提示词模板

以下模板可用于生成其他靶场或安全工具的系统介绍文档：

```markdown
# 文件名：what-is-[工具名]-prompt.md

# 角色
你是一名资深 [领域] 与 [工具类型] 专家，精通 [核心技术栈] 及 [操作流程]，擅长按层次和操作步骤讲清 [工具] 的搭建与使用方法。

# 任务
请系统介绍 [工具名]，包括：
1. [工具] 是什么（定义、定位、规模、场景、区别）
2. 核心架构与工作原理
3. 前置条件（系统、依赖、网络）
4. 搭建步骤（分步骤、附命令）
5. 使用流程（完整操作链）
6. 常用操作速查（表格）
7. 常见问题与解决方案（原因+方案）
8. 安全与合规约束
9. 学习路径建议

# 输出要求
- Markdown 格式，按大类小类组织
- 关键内容用表格对比
- 重要术语给出中英文
- 每个操作步骤附命令和说明
- 面向：[目标受众]
- 深度：[深度层级]

# 约束
- 不穷举所有环境/功能，按类别列代表性示例
- 命令准确、可执行、可复制
- 高风险操作给出警告
- 引用官方文档和权威来源
```

---

> **文档版本**：v1.0
>
> **最后更新**：2026-09-24
>
> **权威来源**：[Vulhub GitHub 仓库](https://github.com/vulhub/vulhub) | [Vulhub 官方文档](https://vulhub.org)
>
> **免责声明**：本文档仅供学习研究使用，不构成任何安全建议或攻击指导。读者须在合法授权环境下进行所有实验操作。
