# Docker 安全配置

### 2.1 Docker 安全基线

#### 2.1.1 Docker 守护进程安全

**1. 限制 Docker 守护进程网络访问**

默认情况下，Docker 守护进程监听 Unix socket（/var/run/docker.sock），不应暴露 TCP 端口。

```bash
# 危险配置：暴露 Docker API 到公网（绝对禁止）
dockerd -H tcp://0.0.0.0:2375

# 安全配置：仅监听 Unix socket（默认）
dockerd -H unix:///var/run/docker.sock

# 如需远程访问，使用 TLS 加密
dockerd --tlsverify --tlscacert=ca.pem --tlscert=server-cert.pem --tlskey=server-key.pem -H tcp://0.0.0.0:2376
```

**2. 启用 Docker 内容信任（Content Trust）**

Docker Content Trust (DCT) 用于验证镜像的签名和完整性，防止镜像被篡改。

```bash
# 启用内容信任
export DOCKER_CONTENT_TRUST=1

# 拉取镜像时会自动验证签名
docker pull nginx:latest
```

**3. 启用用户命名空间（User Namespaces）**

用户命名空间可将容器内的 root 用户映射到宿主机的非特权用户，降低容器逃逸后的影响。

```bash
# 修改 /etc/docker/daemon.json
{
    "userns-remap": "default"
}

# 重启 Docker 服务
systemctl restart docker
```

#### 2.1.2 Dockerfile 安全最佳实践

**不安全的 Dockerfile 示例**：
```dockerfile
# 危险 1：使用 latest 标签，不可控
FROM ubuntu:latest

# 危险 2：以 root 用户运行
USER root

# 危险 3：硬编码敏感信息
ENV DB_PASSWORD=supersecret
ENV API_KEY=AKIAIOSFODNN7EXAMPLE

# 危险 4：安装不必要的软件包，增加攻击面
RUN apt-get update && apt-get install -y \
    vim \
    netcat \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# 危险 5：复制整个目录，可能包含敏感文件
COPY . /app

# 危险 6：暴露过多端口
EXPOSE 22 80 443 3306 6379

# 危险 7：使用 root 运行应用
CMD ["python", "app.py"]
```

**安全的 Dockerfile 示例**：
```dockerfile
# 安全 1：使用具体版本的基础镜像，最好是官方镜像
FROM python:3.11-slim-bookworm

# 安全 2：设置非 root 用户
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 安全 3：只安装必要的依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 安全 4：设置工作目录
WORKDIR /app

# 安全 5：先复制依赖文件，利用缓存
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 安全 6：只复制必要的代码文件
COPY src/ ./src/

# 安全 7：切换到非 root 用户
USER appuser

# 安全 8：只暴露必要的端口
EXPOSE 8080

# 安全 9：使用健康检查
HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:8080/health || exit 1

# 安全 10：使用 exec 形式运行，确保信号正确传递
CMD ["python", "src/app.py"]
```

**Dockerfile 安全要点总结**：

| 要点 | 说明 | 实现方式 |
|------|------|----------|
| 使用官方基础镜像 | 减少恶意代码风险 | 从 Docker Hub 官方仓库拉取 |
| 指定具体版本标签 | 可重现构建 | 避免使用 latest |
| 最小化镜像 | 减少攻击面 | 使用 slim/alpine 变体，多阶段构建 |
| 非 root 用户运行 | 降低权限 | USER 指令 |
| 敏感信息不入镜像 | 防止密钥泄露 | 使用环境变量/Secret/构建参数 |
| 最小化复制内容 | 防止意外泄露 | .dockerignore，精确复制 |
| 健康检查 | 运行状态监控 | HEALTHCHECK 指令 |
| 多阶段构建 | 减小最终镜像大小 | FROM ... AS builder + FROM ... |

### 2.2 容器运行时安全配置

#### 2.2.1 危险的运行参数

**绝对禁止的参数**：

| 参数 | 风险 | 说明 |
|------|------|------|
| `--privileged` | 容器逃逸 | 授予容器几乎所有宿主机权限 |
| `--net=host` | 网络监听 | 共享宿主机网络命名空间 |
| `--pid=host` | 进程可见 | 共享宿主机 PID 命名空间 |
| `-v /var/run/docker.sock:/var/run/docker.sock` | 权限提升 | 可控制宿主机 Docker |
| `-v /proc:/proc` | 内核攻击 | 可访问宿主机 proc 文件系统 |
| `-v /sys:/sys` | 系统配置 | 可修改宿主机系统参数 |
| `-v /root:/root` | 数据窃取 | 可访问宿主机 root 目录 |
| `--cap-add=ALL` | 权限过大 | 授予所有 Linux capabilities |

#### 2.2.2 安全的容器启动参数

**推荐的安全启动命令**：

```bash
docker run -d \
    --name my-app \
    --read-only \                    # 只读根文件系统
    --tmpfs /tmp \                    # /tmp 使用 tmpfs
    --tmpfs /run \                    # /run 使用 tmpfs
    --memory=512m \                   # 内存限制
    --cpus=1 \                        # CPU 限制
    --pids-limit=100 \                # 进程数限制
    --user 1000:1000 \                # 非 root 用户
    --cap-drop=ALL \                  # 丢弃所有 capabilities
    --cap-add=NET_BIND_SERVICE \      # 只添加必要的 capability
    --security-opt=no-new-privileges \ # 禁止获取新权限
    --security-opt seccomp=default \  # seccomp 过滤
    --restart=on-failure:5 \          # 重启策略
    --network=my-network \            # 自定义网络
    -p 8080:8080 \                    # 只映射必要端口
    my-app:latest
```

#### 2.2.3 Linux Capabilities 详解

Capabilities 是 Linux 内核提供的权限细分机制，将 root 权限分解为多个独立的权限。

**常用 Capabilities**：

| Capability | 权限 | 是否通常需要 |
|------------|------|-------------|
| NET_BIND_SERVICE | 绑定小于 1024 的端口 | Web 服务可能需要 |
| NET_RAW | 使用 RAW 和 PACKET 套接字 | 通常不需要 |
| SYS_ADMIN | 系统管理权限（非常强大） | 几乎不需要 |
| SYS_PTRACE | 跟踪进程（ptrace） | 通常不需要 |
| DAC_OVERRIDE | 绕过文件读写权限检查 | 通常不需要 |

**最佳实践**：
- 默认使用 `--cap-drop=ALL` 丢弃所有 capabilities
- 只添加应用实际需要的 capability
- 优先使用非 root 用户替代 capabilities

### 2.3 Docker 网络安全

#### 2.3.1 Docker 网络模式

| 网络模式 | 说明 | 安全性 |
|----------|------|--------|
| bridge | 默认桥接网络，容器间可互通 | 中 |
| host | 共享宿主机网络 | 低 |
| none | 无网络 | 最高 |
| container | 共享另一个容器的网络 | 中 |
| 自定义网络 | 用户自定义的 bridge 网络 | 高 |

#### 2.3.2 网络安全最佳实践

1. **使用自定义网络**：
```bash
# 创建自定义网络
docker network create --driver bridge my-app-network

# 启动容器时指定网络
docker run -d --network my-app-network --name web nginx
docker run -d --network my-app-network --name db mysql
```

2. **避免使用 host 网络模式**

3. **使用网络别名而非 --link**

4. **限制容器间通信**：
```bash
# 创建禁用 ICC（容器间通信）的网络
docker network create --driver bridge --opt com.docker.network.bridge.enable_icc=false secure-network
```

### 2.4 Docker 安全审计工具

#### 2.4.1 Docker Bench for Security

Docker Bench for Security 是官方的 Docker 安全审计脚本，基于 CIS Docker Benchmark。

**使用方法**：
```bash
# 克隆仓库
git clone https://github.com/docker/docker-bench-security.git
cd docker-bench-security

# 运行审计
sh docker-bench-security.sh
```

**审计内容**：
- 主机配置
- Docker 守护进程配置
- Docker 守护进程文件权限
- 容器镜像和构建文件
- 容器运行时配置
- Docker 安全操作

#### 2.4.2 容器镜像扫描工具

| 工具 | 说明 | 特点 |
|------|------|------|
| Trivy | Aqua Security 开源 | 速度快、漏洞库全、支持多类型扫描 |
| Clair | CoreOS 开源 | 可与镜像仓库集成 |
| Anchore | 开源/商业 | 策略驱动的镜像分析 |
| Docker Scout | Docker 官方 | 与 Docker Hub 集成 |

**Trivy 使用示例**：
```bash
# 安装 Trivy
# 扫描镜像漏洞
trivy image nginx:latest

# 扫描结果输出为 JSON
trivy image -f json -o result.json nginx:latest

# 只显示高危和严重漏洞
trivy image --severity HIGH,CRITICAL nginx:latest

# 扫描 Dockerfile
trivy config Dockerfile

# 扫描文件系统（包含 IaC）
trivy fs .
```

---

---

## 📋 内容审核与补充建议

> 针对「Docker 安全配置」部分的内容审核结果：

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

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
