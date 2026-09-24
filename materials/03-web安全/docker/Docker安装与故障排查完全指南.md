# Docker 安装与故障排查完全指南

> **文档定位**：系统介绍 Linux 环境下 Docker Engine 的安装方式、分发行版步骤、安装后验证、常见问题排查与生产环境加固。
>
> **适用对象**：系统管理员 / DevOps 工程师 / 容器运维工程师 / 安全工程师
>
> **深度层级**：操作参考 + 原理理解 + 故障排查 + 安全加固
>
> **适用版本**：Docker Engine 29.x（2026 年最新稳定版），Ubuntu 22.04/24.04，Debian 12，CentOS 7（EOL），Rocky Linux 9，AlmaLinux 9，RHEL 8/9/10
>
> **时效标注**：本文基于 2026 年 9 月 Docker 官方文档验证，请注意时效性。
>
> **安全声明**：本文所有操作仅限授权测试与开发环境。生产环境操作前请确认维护窗口与回滚方案。

---

## 目录

1. [安装前检查](#1-安装前检查)
2. [安装方式对比](#2-安装方式对比)
3. [分发行版安装步骤](#3-分发行版安装步骤)
4. [安装后验证](#4-安装后验证)
5. [常见问题与解决方案](#5-常见问题与解决方案)
6. [生产环境建议](#6-生产环境建议)
7. [卸载与回滚](#7-卸载与回滚)
8. [一键排查清单](#8-一键排查清单)

---

## 1. 安装前检查

### 1.1 系统版本与内核检查

安装 Docker 前需确认操作系统版本、内核版本和系统架构满足要求。

| 检查项 | 最低要求 | 推荐版本 | 检查命令 |
|---|---|---|---|
| **操作系统** | 64-bit Linux | Ubuntu 22.04+ / RHEL 9+ | `cat /etc/os-release` |
| **内核版本** | 3.10+ | 5.15+（推荐 5.4 LTS+） | `uname -r` |
| **系统架构** | x86_64 / arm64 | x86_64 | `uname -m` |
| **systemd** | 已安装并运行 | systemd 240+ | `systemctl --version` |
| **内存** | 2 GB | 4 GB+ | `free -h` |
| **磁盘空间** | 10 GB | 50 GB+（含镜像） | `df -h /` |

```bash
# === 综合检查命令（一键执行） ===
cat /etc/os-release          # 查看发行版信息
uname -r                     # 查看内核版本
uname -m                     # 查看系统架构
systemctl --version          # 查看 systemd 版本
free -h                      # 查看内存
df -h /                      # 查看根分区磁盘空间
lscpu | grep "Virtualization"  # 检查虚拟化支持（可选）
```

**各发行版官方支持矩阵**：

| 发行版 | 支持版本 | 备注 |
|---|---|---|
| Ubuntu | 22.04 (Jammy), 24.04 (Noble), 26.04 (Resolute) | 官方首选支持 |
| Debian | 12 (Bookworm), 13 (Trixie) | 官方支持 |
| RHEL | 8, 9, 10 | 官方支持 |
| Rocky Linux | 8, 9 | 使用 RHEL 仓库 |
| AlmaLinux | 8, 9 | 使用 RHEL 仓库 |
| CentOS | 7 (EOL 2024-06-30) | 已停止维护，建议迁移 |

> **警告**：CentOS 7 已于 2024 年 6 月 30 日 EOL（End of Life），不再接收安全更新。如仍在使用，建议迁移至 Rocky Linux 9 或 AlmaLinux 9。

### 1.2 旧版 Docker / Podman / containerd 检查

Docker 官方包与发行版自带的非官方包（`docker.io`、`podman`、`runc`）可能冲突，安装前必须清理。

```bash
# === Ubuntu / Debian 系：检查旧版包 ===
dpkg --get-selections | grep -E 'docker|containerd|runc|podman'

# === RHEL / Rocky / AlmaLinux 系：检查旧版包 ===
rpm -qa | grep -E 'docker|containerd|runc|podman'

# === 通用：检查已安装的 Docker 相关二进制 ===
which docker dockerd containerd runc podman 2>/dev/null

# === 检查是否有残留的 Docker 服务 ===
systemctl list-unit-files | grep -E 'docker|containerd'
```

**需要清理的冲突包列表**：

| 包名 | 说明 | 清理命令（Ubuntu/Debian） | 清理命令（RHEL 系） |
|---|---|---|---|
| `docker.io` | 发行版自带 Docker | `sudo apt remove docker.io` | — |
| `docker-compose` | 旧版 Compose v1 | `sudo apt remove docker-compose` | `sudo dnf remove docker-compose` |
| `docker-compose-v2` | 发行版打包的 Compose v2 | `sudo apt remove docker-compose-v2` | — |
| `docker-doc` | Docker 文档包 | `sudo apt remove docker-doc` | — |
| `docker-buildx` | 发行版打包的 BuildKit | `sudo apt remove docker-buildx` | — |
| `podman-docker` | Podman 的 Docker 兼容层 | `sudo apt remove podman-docker` | `sudo dnf remove podman-docker` |
| `runc` | 独立安装的 runc | `sudo apt remove runc` | `sudo dnf remove runc` |
| `containerd` | 独立安装的 containerd | `sudo apt remove containerd` | `sudo dnf remove containerd` |
| `docker-engine` | 旧版 Docker Engine（RHEL 系） | — | `sudo dnf remove docker-engine` |

### 1.3 磁盘、内存、cgroup 与安全模块检查

```bash
# === 磁盘空间检查（Docker 默认数据目录 /var/lib/docker） ===
df -h /var/lib/docker 2>/dev/null || df -h /

# === 内存检查 ===
free -h

# === cgroup 版本检查 ===
# cgroup v2 是现代推荐版本，Docker 20.10+ 完整支持
stat -fc %T /sys/fs/cgroup/
# 输出 cgroup2fs 表示 cgroup v2
# 输出 tmpfs 表示 cgroup v1

# === cgroup 挂载点检查 ===
mount | grep cgroup

# === SELinux 状态检查（RHEL / Rocky / AlmaLinux） ===
getenforce                    # 输出 Enforcing / Permissive / Disabled
sestatus                      # 详细 SELinux 状态

# === AppArmor 状态检查（Ubuntu / Debian） ===
aa-status 2>/dev/null || echo "AppArmor not installed"

# === iptables / nftables 检查 ===
iptables --version            # 查看 iptables 版本
nft --version 2>/dev/null     # 查看 nftables 版本
update-alternatives --display iptables 2>/dev/null  # Ubuntu/Debian 查看 iptables 后端

# === 防火墙状态检查 ===
ufw status 2>/dev/null                     # Ubuntu UFW
firewall-cmd --state 2>/dev/null           # RHEL 系 firewalld
systemctl is-active firewalld 2>/dev/null  # firewalld 服务状态
```

> **注意**：Docker 仅兼容 `iptables-nft` 和 `iptables-legacy`。如果你的系统使用原生 `nft` 规则集（非 iptables 兼容层），Docker 的网络功能可能异常。

---

## 2. 安装方式对比

### 2.1 四种安装方式总览

| 安装方式 | 英文术语 | 推荐度 | 适用场景 | 优点 | 缺点 |
|---|---|---|---|---|---|
| **官方仓库** | Official Repository | ★★★★★ | 生产/开发/测试 | 版本最新，可自动更新，GPG 验签 | 需配置仓库源 |
| **官方脚本** | Convenience Script | ★★★☆☆ | 快速测试/临时环境 | 一行命令完成，自动检测发行版 | 不可定制参数，不适合生产，不适合升级 |
| **发行版仓库** | Distribution Repository | ★★☆☆☆ | 受限环境/稳定性优先 | 无需添加第三方源 | 版本滞后，可能缺少插件 |
| **离线安装** | Offline / Air-gapped | ★★★★☆ | 内网/无外网/合规要求 | 无需联网，版本可控 | 升级需手动下载，维护成本高 |

### 2.2 推荐方案

| 场景 | 推荐方式 | 原因 |
|---|---|---|
| **生产环境** | 官方仓库 | 版本最新，安全补丁及时，支持自动更新 |
| **开发测试** | 官方仓库 | 与生产保持一致，便于复现问题 |
| **快速验证** | 官方脚本 | 最快上手，适合一次性环境 |
| **内网/离线** | 离线安装（deb/rpm） | 无外网环境唯一可行方案 |
| **合规要求严格** | 离线安装 + 内部仓库 | 可审计、可追溯，避免外部依赖 |

> **推荐**：对于你的开发测试环境，推荐使用 **官方仓库安装**，版本最新且便于后续升级。如需快速验证，可使用官方脚本。

---

## 3. 分发行版安装步骤

### 3.1 Ubuntu / Debian 系

#### 3.1.1 卸载旧版本

```bash
# 卸载可能冲突的旧版包（需要 sudo/root）
sudo apt remove $(dpkg --get-selections docker.io docker-compose docker-compose-v2 docker-doc docker-buildx podman-docker containerd runc 2>/dev/null | cut -f1)
```

#### 3.1.2 方式一：官方仓库安装（推荐）

```bash
# ============================================================
# 步骤 1：安装依赖包
# ============================================================
sudo apt update
sudo apt install -y ca-certificates curl

# ============================================================
# 步骤 2：添加 Docker 官方 GPG 密钥
# ============================================================
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# ============================================================
# 步骤 3：添加 Docker apt 仓库
# ============================================================
# --- Ubuntu 用 ---
echo \
  "Types: deb\n\
URIs: https://download.docker.com/linux/ubuntu\n\
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")\n\
Components: stable\n\
Architectures: $(dpkg --print-architecture)\n\
Signed-By: /etc/apt/keyrings/docker.asc" | \
  sudo tee /etc/apt/sources.list.d/docker.sources > /dev/null

# --- Debian 用（将 ubuntu 替换为 debian） ---
# echo \
#   "Types: deb\n\
# URIs: https://download.docker.com/linux/debian\n\
# Suites: $(. /etc/os-release && echo "$VERSION_CODENAME")\n\
# Components: stable\n\
# Architectures: $(dpkg --print-architecture)\n\
# Signed-By: /etc/apt/keyrings/docker.asc" | \
#   sudo tee /etc/apt/sources.list.d/docker.sources > /dev/null

# ============================================================
# 步骤 4：更新 apt 索引并安装 Docker
# ============================================================
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io \
  docker-buildx-plugin docker-compose-plugin

# ============================================================
# 步骤 5：启动并设置开机自启
# ============================================================
sudo systemctl enable --now docker
```

> **GPG 密钥指纹验证**：Docker 官方 GPG 密钥指纹为 `060A 61C5 1B55 8A7F 742B 77AA C52F EB6B 621E 9F35`，可通过 `gpg --show-keys /etc/apt/keyrings/docker.asc` 验证。

#### 3.1.3 方式二：官方脚本安装（快速测试）

```bash
# 下载脚本（先审查再执行）
curl -fsSL https://get.docker.com -o get-docker.sh

# 预览脚本将执行的步骤（不实际安装）
sudo sh get-docker.sh --dry-run

# 确认无误后执行安装
sudo sh get-docker.sh
```

> **警告**：官方脚本不适合生产环境，且不支持通过脚本升级已有 Docker 安装。脚本会自动检测发行版并配置仓库，但不可自定义安装参数。

#### 3.1.4 方式三：离线安装（deb 包）

```bash
# 步骤 1：在有网机器上下载 deb 包
# 访问 https://download.docker.com/linux/ubuntu/dists/ 选择对应版本
# 进入 pool/stable/amd64/ 下载以下包：
#   - containerd.io_<version>_amd64.deb
#   - docker-ce_<version>_amd64.deb
#   - docker-ce-cli_<version>_amd64.deb
#   - docker-buildx-plugin_<version>_amd64.deb
#   - docker-compose-plugin_<version>_amd64.deb

# 步骤 2：将包拷贝到目标机器后安装
sudo dpkg -i ./containerd.io_*.deb \
  ./docker-ce_*.deb \
  ./docker-ce-cli_*.deb \
  ./docker-buildx-plugin_*.deb \
  ./docker-compose-plugin_*.deb

# 步骤 3：启动服务
sudo systemctl enable --now docker
```

---

### 3.2 RHEL / CentOS / Rocky / AlmaLinux 系

#### 3.2.1 卸载旧版本

```bash
# 卸载可能冲突的旧版包（需要 sudo/root）
sudo dnf remove -y docker \
  docker-client \
  docker-client-latest \
  docker-common \
  docker-latest \
  docker-latest-logrotate \
  docker-logrotate \
  docker-engine \
  podman \
  runc
```

> **注意**：CentOS 7 使用 `yum` 而非 `dnf`。以下命令中 `dnf` 在 CentOS 7 上替换为 `yum`。

#### 3.2.2 方式一：官方仓库安装（推荐）

```bash
# ============================================================
# 步骤 1：安装 dnf 插件包
# ============================================================
sudo dnf install -y dnf-plugins-core

# ============================================================
# 步骤 2：添加 Docker 官方仓库
# ============================================================
# --- RHEL / Rocky / AlmaLinux 9 用 ---
sudo dnf config-manager --add-repo https://download.docker.com/linux/rhel/docker-ce.repo

# --- CentOS 7 用（使用 centos 仓库） ---
# sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# ============================================================
# 步骤 3：安装 Docker Engine + 插件
# ============================================================
sudo dnf install -y docker-ce docker-ce-cli containerd.io \
  docker-buildx-plugin docker-compose-plugin

# 如果提示 GPG 密钥，验证指纹后接受：
# 指纹：060A 61C5 1B55 8A7F 742B 77AA C52F EB6B 621E 9F35

# ============================================================
# 步骤 4：启动并设置开机自启
# ============================================================
sudo systemctl enable --now docker
```

> **注意**：RHEL 系安装后 Docker 不会自动启动，需手动执行 `systemctl enable --now docker`。

#### 3.2.3 方式二：官方脚本安装（快速测试）

```bash
# 与 Ubuntu/Debian 完全相同
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# RHEL 系安装后需手动启动
sudo systemctl enable --now docker
```

#### 3.2.4 方式三：离线安装（rpm 包）

```bash
# 步骤 1：在有网机器上下载 rpm 包
# 访问 https://download.docker.com/linux/rhel/ 选择对应版本
# 进入对应架构/stable/Packages/ 下载以下包：
#   - containerd.io-<version>.<arch>.rpm
#   - docker-ce-<version>.<arch>.rpm
#   - docker-ce-cli-<version>.<arch>.rpm
#   - docker-buildx-plugin-<version>.<arch>.rpm
#   - docker-compose-plugin-<version>.<arch>.rpm

# 步骤 2：将包拷贝到目标机器后安装
sudo dnf install -y ./containerd.io-*.rpm \
  ./docker-ce-*.rpm \
  ./docker-ce-cli-*.rpm \
  ./docker-buildx-plugin-*.rpm \
  ./docker-compose-plugin-*.rpm

# 步骤 3：启动服务
sudo systemctl enable --now docker
```

---

### 3.3 安装后立即配置（所有发行版通用）

```bash
# ============================================================
# 将当前用户加入 docker 组（免 sudo 运行 docker 命令）
# ============================================================
sudo usermod -aG docker $USER

# 需要注销并重新登录，或执行以下命令立即生效：
newgrp docker

# ============================================================
# 配置 daemon.json（镜像加速 + 日志限制 + 存储驱动）
# ============================================================
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json << 'EOF'
{
  "registry-mirrors": [
    "https://docker.1ms.run",
    "https://docker.xuanyuan.me"
  ],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  },
  "storage-driver": "overlay2",
  "live-restore": true,
  "default-address-pools": [
    {"base": "172.17.0.0/16", "size": 24}
  ]
}
EOF

# 重新加载配置并重启 Docker
sudo systemctl daemon-reload
sudo systemctl restart docker
```

> **警告**：修改 `daemon.json` 后必须执行 `systemctl daemon-reload && systemctl restart docker`。配置文件 JSON 格式错误会导致 Docker 启动失败。

---

## 4. 安装后验证

### 4.1 版本验证

```bash
# 查看 Docker 客户端和服务端版本
docker version

# 预期输出示例：
# Client: Docker Engine - Community
#  Version:           29.x.x
#  ...
# Server: Docker Engine - Community
#  Version:           29.x.x
#  ...
```

### 4.2 系统信息验证

```bash
# 查看 Docker 系统详细信息
docker info

# 关注以下关键字段：
#  Server Version: 29.x.x
#  Storage Driver: overlay2          ← 存储驱动
#  Cgroup Driver: systemd            ← cgroup 驱动
#  Cgroup Version: 2                 ← cgroup 版本
#  Docker Root Dir: /var/lib/docker  ← 数据目录
#  Registry Mirrors: https://...     ← 镜像加速
#  Live Restore Enabled: true        ← 热恢复
```

### 4.3 服务状态验证

```bash
# 检查 Docker 服务状态
sudo systemctl status docker

# 检查是否开机自启
systemctl is-enabled docker

# 检查 containerd 服务状态
sudo systemctl status containerd
```

### 4.4 运行测试容器

```bash
# 拉取并运行 hello-world 测试镜像
docker run hello-world

# 预期输出：
# Hello from Docker!
# This message shows that your installation appears to be working correctly.
# ...

# 运行 Ubuntu 容器测试交互能力
docker run -it ubuntu bash
# 在容器内执行：
#   cat /etc/os-release
#   exit
```

### 4.5 验证清单

| 验证项 | 命令 | 预期结果 | 异常处理 |
|---|---|---|---|
| 客户端版本 | `docker version` | 显示 Client + Server 版本 | 无 Server → 检查 dockerd 是否启动 |
| 系统信息 | `docker info` | 无报错，显示完整信息 | 报错 → 检查 daemon.json 格式 |
| 服务状态 | `systemctl status docker` | active (running) | failed → 查看 journalctl 日志 |
| 开机自启 | `systemctl is-enabled docker` | enabled | disabled → `systemctl enable docker` |
| 容器运行 | `docker run hello-world` | 正常输出问候信息 | 拉取失败 → 检查网络/镜像加速 |
| Compose 插件 | `docker compose version` | 显示 Compose v2 版本 | 未安装 → 安装 docker-compose-plugin |
| BuildKit 插件 | `docker buildx version` | 显示 BuildKit 版本 | 未安装 → 安装 docker-buildx-plugin |

---

## 5. 常见问题与解决方案

### 5.1 网络与仓库问题

#### 5.1.1 无法连接 download.docker.com / 超时

**现象**：`curl` 或 `apt update` 连接 `download.docker.com` 超时或被拒绝。

**原因**：网络不通、DNS 解析失败、防火墙拦截、公司代理限制。

**解决方案**：

```bash
# === 诊断 ===
# 测试连通性
curl -v https://download.docker.com/linux/ubuntu/gpg 2>&1 | head -20

# 检查 DNS 解析
nslookup download.docker.com
dig download.docker.com +short

# === 方案 1：使用国内镜像源替代官方源 ===
# Ubuntu/Debian 系：将 download.docker.com 替换为 mirrors.aliyun.com/docker-ce
sudo sed -i 's|https://download.docker.com|https://mirrors.aliyun.com/docker-ce|g' \
  /etc/apt/sources.list.d/docker.sources
sudo apt update

# RHEL 系：将 download.docker.com 替换为 mirrors.aliyun.com/docker-ce
sudo sed -i 's|https://download.docker.com|https://mirrors.aliyun.com/docker-ce|g' \
  /etc/yum.repos.d/docker-ce.repo
sudo dnf makecache

# === 方案 2：配置系统代理 ===
# 临时配置（当前会话生效）
export http_proxy="http://proxy.example.com:3128"
export https_proxy="http://proxy.example.com:3128"
export no_proxy="localhost,127.0.0.1,.internal.example.com"

# 永久配置 apt 代理（Ubuntu/Debian）
sudo tee /etc/apt/apt.conf.d/99proxy << 'EOF'
Acquire::http::Proxy "http://proxy.example.com:3128";
Acquire::https::Proxy "http://proxy.example.com:3128";
EOF

# 永久配置 dnf/yum 代理（RHEL 系）
sudo tee /etc/dnf/dnf.conf.d/proxy.conf << 'EOF'
proxy=http://proxy.example.com:3128
EOF
# CentOS 7 用 yum：
# sudo tee /etc/yum.conf << 'EOF'
# [main]
# proxy=http://proxy.example.com:3128
# EOF

# === 方案 3：使用官方脚本（自动检测可用源） ===
curl -fsSL https://get.docker.com -o get-docker.sh
# 可设置镜像源
sudo sh get-docker.sh --mirror Aliyun
```

#### 5.1.2 GPG 密钥错误

**现象**：`apt update` 报 `NO_PUBKEY` 或 `GPG error`；`dnf install` 报 `GPG check FAILED`。

**原因**：GPG 密钥未正确导入、密钥过期、密钥文件权限错误。

**解决方案**：

```bash
# === Ubuntu/Debian：重新导入 GPG 密钥 ===
sudo rm -f /etc/apt/keyrings/docker.asc
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
sudo apt update

# 验证密钥指纹
gpg --show-keys /etc/apt/keyrings/docker.asc
# 预期指纹：060A 61C5 1B55 8A7F 742B 77AA C52F EB6B 621E 9F35

# === RHEL 系：导入 GPG 密钥 ===
sudo rpm --import https://download.docker.com/linux/rhel/gpg
# 验证
rpm -qa gpg-pubkey --qf '%{NAME}-%{VERSION}-%{RELEASE}\t%{SUMMARY}\n' | grep -i docker
```

#### 5.1.3 apt/yum/dnf 源冲突

**现象**：安装时提示依赖冲突、版本不匹配。

**原因**：系统中存在多个 Docker 源（官方源 + 发行版源 + 第三方源）。

**解决方案**：

```bash
# === Ubuntu/Debian：检查并清理多余源 ===
# 查看所有 Docker 相关源
grep -r docker /etc/apt/sources.list /etc/apt/sources.list.d/

# 删除发行版自带的 docker.io 源（如果存在）
sudo apt remove -y docker.io docker-compose docker-compose-v2
sudo apt autoremove -y

# 仅保留官方源
ls -la /etc/apt/sources.list.d/docker*
# 确认只有 docker.sources 一个文件

# === RHEL 系：检查并清理多余源 ===
ls -la /etc/yum.repos.d/*docker*
# 删除非官方源
sudo rm -f /etc/yum.repos.d/docker-ce-old.repo
# 清理缓存
sudo dnf clean all
sudo dnf makecache
```

---

### 5.2 Docker 服务问题

#### 5.2.1 docker 服务启动失败

**现象**：`systemctl start docker` 失败，`systemctl status docker` 显示 `failed`。

**排查步骤**：

```bash
# 步骤 1：查看详细错误日志
sudo journalctl -u docker --no-pager -n 50

# 步骤 2：手动启动 dockerd 查看详细输出
sudo dockerd --debug 2>&1 | head -50

# 步骤 3：检查 daemon.json 格式
sudo cat /etc/docker/daemon.json
# 用 python 验证 JSON 格式
python3 -c "import json; json.load(open('/etc/docker/daemon.json'))" && echo "JSON OK" || echo "JSON ERROR"
```

**常见原因与解决方案**：

| 原因 | 现象 | 解决方案 |
|---|---|---|
| daemon.json JSON 格式错误 | `failed to start daemon: error loading config file` | 用 `python3 -m json.tool /etc/docker/daemon.json` 验证并修复 |
| 存储驱动不兼容 | `failed to start daemon: error initializing graphdriver` | 修改 `storage-driver` 或清理 `/var/lib/docker` |
| 端口被占用 | `bind: address already in use` | `ss -tlnp \| grep 2375` 查找占用进程 |
| iptables 不可用 | `iptables: command not found` | 安装 `iptables` 或 `iptables-nft` |
| cgroup 挂载异常 | `cgroup mountpoint does not exist` | 重新挂载 cgroup（见 5.7 节） |
| /var/lib/docker 损坏 | `failed to start daemon: containerd: containerd not running` | 停止服务后清理并重启（见下方） |
| SELinux 拒绝 | `avc: denied` 相关日志 | 设置 SELinux 为 Permissive 排查（见 5.8 节） |

```bash
# === 修复 /var/lib/docker 损坏 ===
# ⚠️ 警告：此操作会删除所有容器、镜像和卷，请先备份！
sudo systemctl stop docker
sudo mv /var/lib/docker /var/lib/docker.bak
sudo mkdir /var/lib/docker
sudo systemctl start docker
```

> **警告**：删除 `/var/lib/docker` 会丢失所有 Docker 数据（镜像、容器、卷）。仅在确认数据可丢弃或已备份时执行。

#### 5.2.2 daemon.json 配置错误

**现象**：修改 `daemon.json` 后 Docker 无法启动。

**常见配置错误与修复**：

```bash
# === 错误 1：JSON 语法错误（尾随逗号、缺少引号等） ===
# 检查命令
python3 -m json.tool /etc/docker/daemon.json

# === 错误 2：hosts 选项与 systemd 冲突 ===
# daemon.json 中配置了 "hosts" 但 systemd 也配置了 -H
# 解决：删除 daemon.json 中的 "hosts" 配置，改用 systemd drop-in
sudo mkdir -p /etc/systemd/system/docker.service.d
sudo tee /etc/systemd/system/docker.service.d/override.conf << 'EOF'
[Service]
ExecStart=
ExecStart=/usr/bin/dockerd
EOF
sudo systemctl daemon-reload
sudo systemctl restart docker

# === 错误 3：registry-mirrors URL 格式错误 ===
# 正确格式：带协议但不带路径
# ✅ 正确： "https://docker.1ms.run"
# ❌ 错误： "docker.1ms.run"（缺协议）
# ❌ 错误： "https://docker.1ms.run/v2/"（多了路径）

# === 临时绕过：备份并使用空配置启动 ===
sudo cp /etc/docker/daemon.json /etc/docker/daemon.json.bak
echo '{}' | sudo tee /etc/docker/daemon.json
sudo systemctl restart docker
```

---

### 5.3 权限问题

#### 5.3.1 Permission denied /var/run/docker.sock

**现象**：非 root 用户执行 `docker ps` 报 `permission denied while trying to connect to the Docker daemon socket`。

**原因**：当前用户不在 `docker` 组中。

**解决方案**：

```bash
# 方案 1：将用户加入 docker 组（推荐）
sudo usermod -aG docker $USER

# 需要重新登录或执行以下命令立即生效
newgrp docker

# 验证
docker ps  # 不再报错

# 方案 2：临时使用 sudo
sudo docker ps

# 方案 3：修改 sock 权限（不推荐，安全风险高）
# sudo chmod 666 /var/run/docker.sock
```

> **安全警告**：将用户加入 `docker` 组等同于赋予该用户 root 级别权限，因为可以通过容器挂载宿主机文件系统提权。仅在受信任的环境中使用。

---

### 5.4 镜像与网络问题

#### 5.4.1 镜像拉取失败 / 超时

**现象**：`docker pull` 报 `timeout`、`connection refused`、`i/o timeout`。

**排查与解决**：

```bash
# === 诊断 ===
# 测试与 Docker Hub 的连通性
curl -v https://registry-1.docker.io/v2/ 2>&1 | head -20

# 检查 DNS 解析
nslookup registry-1.docker.io

# === 方案 1：配置镜像加速器 ===
# 编辑 daemon.json 添加 registry-mirrors
sudo tee /etc/docker/daemon.json << 'EOF'
{
  "registry-mirrors": [
    "https://docker.1ms.run",
    "https://docker.xuanyuan.me",
    "https://docker.registry.cyou",
    "https://docker-cf.registry.cyou"
  ]
}
EOF
sudo systemctl restart docker

# 验证加速器是否生效
docker info | grep -A 5 "Registry Mirrors"

# === 方案 2：配置 Docker 守护进程代理 ===
# 编辑 daemon.json 添加 proxy 配置
sudo tee /etc/docker/daemon.json << 'EOF'
{
  "proxies": {
    "http-proxy": "http://proxy.example.com:3128",
    "https-proxy": "http://proxy.example.com:3128",
    "no-proxy": "localhost,127.0.0.1,.internal.example.com"
  }
}
EOF
sudo systemctl restart docker

# === 方案 3：为 docker pull 指定完整镜像路径 ===
# 使用镜像加速站的完整路径
docker pull docker.1ms.run/library/ubuntu:22.04
# 然后重新打标签
docker tag docker.1ms.run/library/ubuntu:22.04 ubuntu:22.04

# === 方案 4：离线导入镜像 ===
# 在有网机器上导出
docker save -o ubuntu.tar ubuntu:22.04
# 拷贝到目标机器后导入
docker load -i ubuntu.tar
```

#### 5.4.2 DNS 问题导致容器无法联网

**现象**：容器内无法解析域名，`ping` IP 正常但 `ping` 域名失败。

**原因**：容器使用的 DNS 服务器不可达或配置错误。

**解决方案**：

```bash
# === 方案 1：在 daemon.json 中全局配置 DNS ===
sudo tee /etc/docker/daemon.json << 'EOF'
{
  "dns": ["8.8.8.8", "8.8.4.4", "114.114.114.114"]
}
EOF
sudo systemctl restart docker

# === 方案 2：单容器指定 DNS ===
docker run --dns 8.8.8.8 --dns 114.114.114.114 -it ubuntu bash

# === 方案 3：检查宿主机 DNS 配置 ===
cat /etc/resolv.conf
# 确保 nameserver 指向可达的 DNS 服务器

# === 方案 4：检查 iptables 是否拦截了 DNS 流量 ===
sudo iptables -L -n -v | grep 53
```

#### 5.4.3 公司代理环境问题

**现象**：公司网络要求通过代理上网，Docker 拉取镜像失败。

**解决方案**：

```bash
# === 步骤 1：配置 Docker 守护进程代理（daemon.json） ===
# 见 5.4.1 方案 2

# === 步骤 2：配置 systemd 服务代理 ===
sudo mkdir -p /etc/systemd/system/docker.service.d
sudo tee /etc/systemd/system/docker.service.d/proxy.conf << 'EOF'
[Service]
Environment="HTTP_PROXY=http://proxy.example.com:3128"
Environment="HTTPS_PROXY=http://proxy.example.com:3128"
Environment="NO_PROXY=localhost,127.0.0.1,.internal.example.com"
EOF
sudo systemctl daemon-reload
sudo systemctl restart docker

# 验证代理配置
systemctl show --property=Environment docker

# === 步骤 3：配置容器内代理（docker build 时使用） ===
# 通过 ~/.docker/config.json 配置（客户端级别）
mkdir -p ~/.docker
tee ~/.docker/config.json << 'EOF'
{
  "proxies": {
    "default": {
      "httpProxy": "http://proxy.example.com:3128",
      "httpsProxy": "http://proxy.example.com:3128",
      "noProxy": "localhost,127.0.0.1,.internal.example.com"
    }
  }
}
EOF
```

---

### 5.5 防火墙与网络冲突

#### 5.5.1 iptables / nftables 冲突

**现象**：容器网络不通、端口映射失效、`docker run -p` 后外部无法访问。

**原因**：Docker 依赖 `iptables` 管理 NAT 和网络隔离，与 `nftables` 原生规则或 `firewalld` 冲突。

| 问题 | 原因 | 解决方案 |
|---|---|---|
| 容器间无法通信 | iptables FORWARD 链策略为 DROP | 添加 `iptables -P FORWARD ACCEPT` 或配置 daemon.json |
| 端口映射外部不可达 | firewalld/ufw 覆盖了 Docker 的 iptables 规则 | 配置防火墙放行或使用 DOCKER-USER 链 |
| nftables 规则丢失 | Docker 使用 iptables-nft 但系统用原生 nft | 统一使用 iptables-nft 或禁用 Docker 的 iptables 管理 |
| 容器启动报 iptables 错误 | iptables 缺失或版本不兼容 | 安装 `iptables-nft` 包 |

**解决方案**：

```bash
# === 方案 1：Ubuntu/Debian 确保 iptables 使用 nft 后端 ===
sudo update-alternatives --set iptables /usr/sbin/iptables-nft
sudo update-alternatives --set ip6tables /usr/sbin/ip6tables-nft

# === 方案 2：配置 daemon.json 中的 iptables 选项 ===
# 在 daemon.json 中添加（不推荐禁用 iptables，仅排查时临时使用）
{
  "iptables": true
}
# ⚠️ 警告：设置 "iptables": false 会导致容器网络完全失效！

# === 方案 3：firewalld 与 Docker 共存（RHEL 系） ===
# 添加 Docker 信任接口
sudo firewall-cmd --permanent --zone=trusted --add-interface=docker0
sudo firewall-cmd --permanent --zone=trusted --add-source=172.17.0.0/16
sudo firewall-cmd --reload
sudo systemctl restart docker

# === 方案 4：UFW 与 Docker 共存（Ubuntu） ===
# 编辑 /etc/default/ufw 修改转发策略
sudo sed -i 's/DEFAULT_FORWARD_POLICY="DROP"/DEFAULT_FORWARD_POLICY="ACCEPT"/' /etc/default/ufw
sudo ufw reload
# 或在 UFW 规则中放行 Docker 网络
sudo ufw route allow in on docker0
sudo ufw route allow out on docker0
```

> **重要**：Docker 的端口映射（`-p`）会直接操作 iptables，绕过 UFW 和 firewalld 的规则。这意味着即使 UFW 未放行某端口，Docker 映射的端口仍然可从外部访问。详见 [Docker 与防火墙交互](https://docs.docker.com/engine/network/packet-filtering-firewalls/) [$TRAE_REF](https://docs.docker.com/engine/network/packet-filtering-firewalls/)。

#### 5.5.2 Docker 网络子网冲突

**现象**：Docker 创建网络时报 `Pool overlaps with other one on this address space`，或容器网络与宿主机局域网 IP 段冲突。

**解决方案**：

```bash
# 查看所有 Docker 网络
docker network ls
docker network inspect bridge | grep Subnet

# 在 daemon.json 中自定义默认地址池
sudo tee /etc/docker/daemon.json << 'EOF'
{
  "default-address-pools": [
    {"base": "172.17.0.0/16", "size": 24},
    {"base": "172.18.0.0/16", "size": 24},
    {"base": "172.19.0.0/16", "size": 24},
    {"base": "172.20.0.0/16", "size": 24},
    {"base": "10.250.0.0/16", "size": 24}
  ]
}
EOF
sudo systemctl restart docker
```

---

### 5.6 存储驱动问题

#### 5.6.1 overlay2 存储驱动问题

**现象**：`docker info` 显示存储驱动非 overlay2，或容器启动报 `level=error msg="overlayfs: ..."`。

**原因**：内核不支持 overlay、文件系统不兼容、旧版存储驱动残留。

**解决方案**：

```bash
# 检查内核是否支持 overlay
grep -i overlay /proc/filesystems
# 预期输出：nodev  overlay

# 检查当前存储驱动
docker info | grep "Storage Driver"

# === 强制使用 overlay2 ===
# 在 daemon.json 中指定
sudo tee /etc/docker/daemon.json << 'EOF'
{
  "storage-driver": "overlay2"
}
EOF

# ⚠️ 警告：切换存储驱动需要清理旧数据！
sudo systemctl stop docker
sudo rm -rf /var/lib/docker/*
sudo systemctl start docker
```

> **警告**：切换存储驱动会删除所有镜像和容器数据。切换前务必备份或确认数据可丢弃。

#### 5.6.2 磁盘空间不足

**现象**：`docker pull` 报 `no space left on device`，或容器写入失败。

**排查与解决**：

```bash
# === 诊断 ===
df -h /var/lib/docker
docker system df

# === 清理无用数据 ===
# 清理停止的容器、无用网络、悬空镜像、悬空卷
docker system prune

# 彻底清理（包括未被引用的卷）
docker system prune -a --volumes
# ⚠️ 警告：--volumes 会删除所有未被容器引用的卷，谨慎使用！

# === 清理构建缓存 ===
docker builder prune -a -f

# === 查看占用空间的镜像和容器 ===
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | sort -k 3 -h
docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Size}}" | sort -k 3 -h

# === 迁移 Docker 数据目录（见 6.3 节） ===
```

---

### 5.7 cgroup 与 systemd 驱动问题

#### 5.7.1 cgroup v1/v2 兼容性

**现象**：容器内存/CPU 限制不生效，或 `docker info` 显示 cgroup driver 为 `cgroupfs` 而非 `systemd`。

**原因**：Docker 默认使用 `cgroupfs` 驱动，而 systemd 推荐 `systemd` 驱动。Kubernetes 环境下二者必须一致。

**检查与修复**：

```bash
# === 检查 cgroup 版本 ===
stat -fc %T /sys/fs/cgroup/
# cgroup2fs → cgroup v2
# tmpfs → cgroup v1

# === 检查 Docker cgroup 驱动 ===
docker info | grep -i cgroup

# === 配置 systemd cgroup driver（推荐） ===
sudo tee /etc/docker/daemon.json << 'EOF'
{
  "exec-opts": ["native.cgroupdriver=systemd"]
}
EOF
sudo systemctl restart docker

# 验证
docker info | grep "Cgroup Driver"
# 预期：Cgroup Driver: systemd
```

> **注意**：在 Kubernetes 环境中，Docker（或 containerd）的 cgroup driver 必须与 kubelet 一致，推荐统一使用 `systemd`。

#### 5.7.2 cgroup 挂载异常

**现象**：Docker 启动报 `cgroup mountpoint does not exist` 或 `failed to initialize cgroup`。

**解决方案**：

```bash
# 检查 cgroup 挂载
mount | grep cgroup
ls /sys/fs/cgroup/

# === 修复 cgroup v2 挂载 ===
sudo mount -t cgroup2 none /sys/fs/cgroup

# === WSL2 环境下可能需要额外配置 ===
# 编辑 /etc/wsl.conf（WSL2 专用）
sudo tee /etc/wsl.conf << 'EOF'
[boot]
systemd=true
EOF
# 然后在 Windows PowerShell 中执行：
# wsl --shutdown
# 重新打开 WSL
```

---

### 5.8 SELinux / AppArmor 拒绝

#### 5.8.1 SELinux 拒绝（RHEL / Rocky / AlmaLinux）

**现象**：容器无法访问挂载的卷、日志中出现 `avc: denied` 消息。

**排查与解决**：

```bash
# === 诊断 ===
# 查看当前 SELinux 模式
getenforce

# 查看 SELinux 拒绝日志
sudo ausearch -m AVC -ts recent 2>/dev/null | tail -20
# 或
sudo grep denied /var/log/audit/audit.log | tail -20

# === 方案 1：临时设为 Permissive 模式排查 ===
sudo setenforce 0
# 测试 Docker 是否正常
docker run -v /tmp/test:/data busybox ls /data
# 测试完成后恢复
sudo setenforce 1

# === 方案 2：为容器卷添加正确的 SELinux 标签 ===
# 使用 :z（共享标签）或 :Z（私有标签）后缀
docker run -v /host/path:/container/path:z busybox ls /container/path
docker run -v /host/path:/container/path:Z busybox ls /container/path

# === 方案 3：安装 SELinux 管理工具并生成策略 ===
sudo dnf install -y policycoreutils-python-utils
sudo grep denied /var/log/audit/audit.log | audit2allow -M mydocker
sudo semodule -i mydocker.pp

# === 方案 4：在 daemon.json 中启用 SELinux ===
sudo tee /etc/docker/daemon.json << 'EOF'
{
  "selinux-enabled": true
}
EOF
sudo systemctl restart docker
```

> **注意**：不推荐直接将 SELinux 设为 `Disabled`。应使用 `Permissive` 模式排查问题，再通过正确的标签或策略规则修复。

#### 5.8.2 AppArmor 拒绝（Ubuntu / Debian）

**现象**：容器启动失败，日志中出现 `apparmor=DENIED`。

**排查与解决**：

```bash
# === 诊断 ===
# 查看 AppArmor 状态
aa-status

# 查看 AppArmor 拒绝日志
sudo dmesg | grep -i apparmor | tail -20
# 或
sudo journalctl -k | grep -i apparmor | tail -20

# === 方案 1：临时禁用 Docker 的 AppArmor 配置文件 ===
sudo apparmor_parser -R /etc/apparmor.d/docker
# 测试完成后重新加载
sudo apparmor_parser -r /etc/apparmor.d/docker

# === 方案 2：为容器指定自定义 AppArmor 配置文件 ===
docker run --security-opt apparmor=docker-default busybox

# === 方案 3：完全禁用容器 AppArmor（不推荐） ===
docker run --security-opt apparmor=unconfined busybox
```

---

### 5.9 Docker 与 containerd / Podman 冲突

#### 5.9.1 containerd 版本冲突

**现象**：Docker 启动报 `containerd: containerd not running` 或版本不匹配。

**解决方案**：

```bash
# === 检查 containerd 状态 ===
sudo systemctl status containerd
containerd --version

# === 重启 containerd ===
sudo systemctl restart containerd
sudo systemctl restart docker

# === 如果 containerd 版本与 Docker 不匹配 ===
# 卸载独立安装的 containerd，使用 Docker 捆绑的 containerd.io
# Ubuntu/Debian
sudo apt remove -y containerd
sudo apt install -y containerd.io

# RHEL 系
sudo dnf remove -y containerd
sudo dnf install -y containerd.io

# 重新启动
sudo systemctl restart docker
```

#### 5.9.2 Podman 冲突

**现象**：`podman-docker` 包安装后 `docker` 命令行为异常。

**原因**：`podman-docker` 包将 `docker` 命令别名为 `podman`，与 Docker Engine 冲突。

**解决方案**：

```bash
# 卸载 podman-docker 兼容层
# Ubuntu/Debian
sudo apt remove -y podman-docker

# RHEL 系
sudo dnf remove -y podman-docker

# 验证 docker 命令指向正确的二进制
which docker
docker --version
# 确认输出 Docker Engine 而非 podman
```

---

### 5.10 特殊环境问题

#### 5.10.1 WSL2 环境问题

**现象**：WSL2 中 Docker 启动失败、systemd 不支持、网络异常。

**解决方案**：

```bash
# === 前提条件：确保 WSL2 启用了 systemd ===
# 在 /etc/wsl.conf 中配置
sudo tee /etc/wsl.conf << 'EOF'
[boot]
systemd=true

[network]
generateResolvConf=true
EOF

# 在 Windows PowerShell 中重启 WSL
# wsl --shutdown
# 重新打开 WSL

# === 验证 systemd 运行 ===
ps -p 1 -o comm=
# 预期输出：systemd（如果是 init 或其他则未启用）

# === WSL2 网络 DNS 问题 ===
# 如果容器内 DNS 解析失败
sudo tee /etc/docker/daemon.json << 'EOF'
{
  "dns": ["8.8.8.8", "8.8.4.4"]
}
EOF
sudo systemctl restart docker

# === 推荐方案：使用 Docker Desktop for Windows ===
# 对于 WSL2 环境，也可安装 Docker Desktop 并启用 WSL2 集成
# 这会自动处理大部分兼容性问题
```

#### 5.10.2 远程服务器失联风险

> **警告**：在远程服务器上修改网络配置（iptables、firewalld、网卡）可能导致 SSH 连接断开，务必保持至少一个已建立的管理会话。

```bash
# 安全操作建议：
# 1. 修改防火墙前先在 tmux/screen 中操作
tmux new -s docker-setup

# 2. 预设一个"安全网"定时任务，5 分钟后自动恢复防火墙
sudo sh -c 'echo "iptables -F; systemctl restart firewalld" | at now + 5 minutes' 2>/dev/null

# 3. 修改完成后确认 SSH 仍可连接
# 在另一个终端测试：ssh user@server

# 4. 确认无误后取消定时任务
atq  # 查看任务
atrm <job_id>  # 删除任务
```

---

## 6. 生产环境建议

### 6.1 用户权限管理

| 策略 | 说明 | 配置方式 |
|---|---|---|
| **限制 docker 组成员** | 仅将受信任用户加入 docker 组 | `sudo usermod -aG docker <user>` |
| **使用 Rootless 模式** | 非 root 运行 Docker 守护进程 | `dockerd-rootless-setuptool.sh install` |
| **禁用特权容器** | 避免使用 `--privileged` | 使用 `--cap-add` 精确授予能力 |
| **使用只读根文件系统** | 防止容器内篡改 | `docker run --read-only` |
| **启用用户命名空间映射** | 容器内 root 映射为宿主普通用户 | daemon.json 配置 `userns-remap` |

```bash
# === 启用用户命名空间映射（推荐生产环境） ===
sudo tee /etc/docker/daemon.json << 'EOF'
{
  "userns-remap": "default"
}
EOF
sudo systemctl restart docker

# 验证
docker info | grep "Username"
```

### 6.2 日志限制

```bash
# === 在 daemon.json 中配置全局日志限制 ===
sudo tee /etc/docker/daemon.json << 'EOF'
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  }
}
EOF
sudo systemctl restart docker

# === 单容器指定日志限制 ===
docker run \
  --log-driver json-file \
  --log-opt max-size=50m \
  --log-opt max-file=5 \
  myapp:latest
```

> **重要**：不限制日志大小可能导致磁盘被日志填满，引发服务中断。生产环境必须配置日志限制。

### 6.3 数据目录迁移

```bash
# === 将 Docker 数据目录从 /var/lib/docker 迁移到大磁盘 ===
# 步骤 1：停止 Docker
sudo systemctl stop docker

# 步骤 2：创建新数据目录
sudo mkdir -p /data/docker

# 步骤 3：复制数据（保留权限）
sudo rsync -aP /var/lib/docker/ /data/docker/

# 步骤 4：备份旧目录
sudo mv /var/lib/docker /var/lib/docker.bak

# 步骤 5：配置 daemon.json 指向新路径
sudo tee /etc/docker/daemon.json << 'EOF'
{
  "data-root": "/data/docker"
}
EOF

# 步骤 6：启动 Docker
sudo systemctl start docker

# 步骤 7：验证
docker info | grep "Docker Root Dir"
# 预期：Docker Root Dir: /data/docker

# 步骤 8：确认无误后删除旧目录
sudo rm -rf /var/lib/docker.bak
```

> **警告**：迁移前确保新磁盘有足够空间。迁移过程中 Docker 服务不可用，需在维护窗口内操作。

### 6.4 镜像加速与私有仓库

```bash
# === 配置镜像加速 + 私有仓库信任 ===
sudo tee /etc/docker/daemon.json << 'EOF'
{
  "registry-mirrors": [
    "https://docker.1ms.run",
    "https://docker.xuanyuan.me"
  ],
  "insecure-registries": [
    "registry.internal.example.com:5000"
  ]
}
EOF
sudo systemctl restart docker

# === 配置私有仓库认证 ===
# 登录私有仓库
docker login registry.internal.example.com:5000
# 凭证存储在 ~/.docker/config.json

# === 配置日志限制 + 镜像加速 + 安全选项（完整生产配置） ===
sudo tee /etc/docker/daemon.json << 'EOF'
{
  "data-root": "/data/docker",
  "registry-mirrors": [
    "https://docker.1ms.run",
    "https://docker.xuanyuan.me"
  ],
  "insecure-registries": [],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  },
  "storage-driver": "overlay2",
  "exec-opts": ["native.cgroupdriver=systemd"],
  "live-restore": true,
  "userland-proxy": false,
  "max-concurrent-downloads": 10,
  "max-concurrent-uploads": 5,
  "default-address-pools": [
    {"base": "172.17.0.0/16", "size": 24}
  ]
}
EOF
sudo systemctl restart docker
```

### 6.5 安全加固清单

| 加固项 | 说明 | 优先级 | 配置方式 |
|---|---|---|---|
| 限制 docker 组 | 仅受信任用户可操作 Docker | 高 | 审计 `getent group docker` |
| 禁用特权容器 | 避免 `--privileged` | 高 | 使用 `--cap-add` 精确授权 |
| 启用内容信任 | 验证镜像签名 | 高 | `export DOCKER_CONTENT_TRUST=1` |
| 限制容器资源 | CPU/内存限制 | 高 | `docker run --memory=512m --cpus=1.0` |
| 日志限制 | 防止磁盘耗尽 | 高 | daemon.json 配置 log-opts |
| 网络隔离 | 使用自定义网络 | 中 | `docker network create --internal` |
| 只读文件系统 | 防止篡改 | 中 | `docker run --read-only` |
| 启用 user namespace | 容器 root 映射 | 中 | daemon.json 配置 userns-remap |
| 禁用旧 API | 限制 Docker API 版本 | 低 | daemon.json 配置 `api-cors-header` |
| 定期清理 | 清理无用镜像和容器 | 低 | cron 定时执行 `docker system prune` |
| 启用 audit | 审计 Docker 命令执行 | 低 | 配置 auditd 规则 |

```bash
# === 启用 Docker 内容信任（Content Trust） ===
# 全局启用
export DOCKER_CONTENT_TRUST=1
# 永久配置
echo 'export DOCKER_CONTENT_TRUST=1' >> ~/.bashrc

# === 配置 auditd 审计 Docker ===
sudo tee /etc/audit/rules.d/docker.rules << 'EOF'
-w /usr/bin/docker -p wa -k docker
-w /var/lib/docker -p wa -k docker
-w /etc/docker/daemon.json -p wa -k docker
-w /etc/systemd/system/docker.service -p wa -k docker
EOF
sudo systemctl restart auditd
```

---

## 7. 卸载与回滚

### 7.1 卸载步骤（Ubuntu / Debian 系）

```bash
# 步骤 1：停止 Docker 服务
sudo systemctl stop docker
sudo systemctl stop docker.socket
sudo systemctl stop containerd

# 步骤 2：禁用开机自启
sudo systemctl disable docker
sudo systemctl disable containerd

# 步骤 3：卸载软件包
sudo apt purge -y docker-ce docker-ce-cli containerd.io \
  docker-buildx-plugin docker-compose-plugin docker-ce-rootless-extras

# 步骤 4：清理依赖
sudo apt autoremove -y

# 步骤 5：删除残留目录
# ⚠️ 警告：以下命令会删除所有镜像、容器和卷数据！
sudo rm -rf /var/lib/docker
sudo rm -rf /var/lib/containerd

# 步骤 6：删除配置文件
sudo rm -f /etc/docker/daemon.json
sudo rm -rf /etc/docker
sudo rm -f /etc/apt/sources.list.d/docker.sources
sudo rm -f /etc/apt/keyrings/docker.asc

# 步骤 7：删除 systemd drop-in（如有）
sudo rm -rf /etc/systemd/system/docker.service.d
sudo systemctl daemon-reload

# 步骤 8：删除 docker 用户组（如不再需要）
sudo groupdel docker 2>/dev/null

# 步骤 9：验证卸载完成
dpkg --get-selections | grep docker  # 应无输出
which docker  # 应无输出
```

### 7.2 卸载步骤（RHEL / Rocky / AlmaLinux 系）

```bash
# 步骤 1：停止 Docker 服务
sudo systemctl stop docker
sudo systemctl stop docker.socket
sudo systemctl stop containerd

# 步骤 2：禁用开机自启
sudo systemctl disable docker
sudo systemctl disable containerd

# 步骤 3：卸载软件包
sudo dnf remove -y docker-ce docker-ce-cli containerd.io \
  docker-buildx-plugin docker-compose-plugin docker-ce-rootless-extras

# 步骤 4：清理依赖
sudo dnf autoremove -y

# 步骤 5：删除残留目录
# ⚠️ 警告：以下命令会删除所有镜像、容器和卷数据！
sudo rm -rf /var/lib/docker
sudo rm -rf /var/lib/containerd

# 步骤 6：删除配置文件
sudo rm -f /etc/docker/daemon.json
sudo rm -rf /etc/docker
sudo rm -f /etc/yum.repos.d/docker-ce.repo

# 步骤 7：删除 systemd drop-in（如有）
sudo rm -rf /etc/systemd/system/docker.service.d
sudo systemctl daemon-reload

# 步骤 8：删除 docker 用户组
sudo groupdel docker 2>/dev/null

# 步骤 9：验证卸载完成
rpm -qa | grep docker  # 应无输出
which docker  # 应无输出
```

### 7.3 回滚方案

如需从新版本回滚到旧版本：

```bash
# === Ubuntu/Debian 回滚 ===
# 查看可用版本
apt list --all-versions docker-ce

# 安装指定版本
sudo apt install -y docker-ce=5:<version>~ubuntu.<distro> docker-ce-cli=5:<version>~ubuntu.<distro> containerd.io

# === RHEL 系回滚 ===
# 查看可用版本
dnf list docker-ce --showduplicates | sort -r

# 安装指定版本
sudo dnf install -y docker-ce-<version> docker-ce-cli-<version> containerd.io

# 重新启动
sudo systemctl restart docker
```

> **警告**：降级前务必备份 `/etc/docker/daemon.json` 和 `/var/lib/docker`。跨大版本降级可能导致数据不兼容。

---

## 8. 一键排查清单

当 Docker 出现问题时，按以下顺序执行排查命令：

```bash
#!/bin/bash
# ============================================================
# Docker 一键排查脚本
# 用法：sudo bash docker-troubleshoot.sh
# ============================================================

echo "=========================================="
echo "1. 系统基本信息"
echo "=========================================="
cat /etc/os-release | head -4
echo "内核: $(uname -r)"
echo "架构: $(uname -m)"
echo ""

echo "=========================================="
echo "2. Docker 版本信息"
echo "=========================================="
docker version 2>&1
echo ""

echo "=========================================="
echo "3. Docker 系统信息"
echo "=========================================="
docker info 2>&1 | grep -E "Server Version|Storage Driver|Cgroup Driver|Cgroup Version|Docker Root Dir|Registry Mirrors|Live Restore"
echo ""

echo "=========================================="
echo "4. Docker 服务状态"
echo "=========================================="
systemctl status docker --no-pager 2>&1 | head -15
echo ""

echo "=========================================="
echo "5. containerd 服务状态"
echo "=========================================="
systemctl status containerd --no-pager 2>&1 | head -10
echo ""

echo "=========================================="
echo "6. Docker 日志（最近 30 行）"
echo "=========================================="
journalctl -u docker --no-pager -n 30 2>&1
echo ""

echo "=========================================="
echo "7. daemon.json 配置"
echo "=========================================="
if [ -f /etc/docker/daemon.json ]; then
    echo "文件存在，内容："
    python3 -m json.tool /etc/docker/daemon.json 2>&1
else
    echo "daemon.json 不存在（使用默认配置）"
fi
echo ""

echo "=========================================="
echo "8. 磁盘空间"
echo "=========================================="
df -h /var/lib/docker 2>/dev/null || df -h /
echo ""

echo "=========================================="
echo "9. Docker 磁盘使用"
echo "=========================================="
docker system df 2>&1
echo ""

echo "=========================================="
echo "10. 内存与 cgroup"
echo "=========================================="
free -h
echo "cgroup 版本: $(stat -fc %T /sys/fs/cgroup/)"
echo ""

echo "=========================================="
echo "11. 防火墙状态"
echo "=========================================="
echo "--- UFW ---"
ufw status 2>/dev/null || echo "UFW 未安装"
echo "--- firewalld ---"
firewall-cmd --state 2>/dev/null || echo "firewalld 未安装"
echo ""

echo "=========================================="
echo "12. SELinux / AppArmor"
echo "=========================================="
echo "--- SELinux ---"
getenforce 2>/dev/null || echo "SELinux 未安装"
echo "--- AppArmor ---"
aa-status 2>/dev/null | head -5 || echo "AppArmor 未安装"
echo ""

echo "=========================================="
echo "13. iptables / 网络"
echo "=========================================="
echo "--- iptables 版本 ---"
iptables --version 2>&1
echo "--- Docker iptables 规则 ---"
sudo iptables -t nat -L -n 2>&1 | head -20
echo ""

echo "=========================================="
echo "14. Docker 网络"
echo "=========================================="
docker network ls 2>&1
echo ""

echo "=========================================="
echo "15. 运行中的容器"
echo "=========================================="
docker ps -a 2>&1
echo ""

echo "=========================================="
echo "排查完成"
echo "=========================================="
```

**使用方式**：

```bash
# 保存为脚本并执行
sudo bash docker-troubleshoot.sh > docker-diagnosis.txt 2>&1
# 查看结果
cat docker-diagnosis.txt
```

---

## 附录：核心术语中英文对照

| 中文术语 | 英文术语 | 说明 |
|---|---|---|
| 容器引擎 | Container Engine | Docker Engine / containerd / CRI-O |
| 容器运行时 | Container Runtime | runc / crun / kata |
| 存储驱动 | Storage Driver | overlay2 / devicemapper / vfs |
| 镜像 | Image | 只读模板，用于创建容器 |
| 容器 | Container | 镜像的运行实例 |
| 卷 | Volume | 持久化数据存储 |
| 镜像加速器 | Registry Mirror | 加速镜像拉取的代理服务 |
| 内容信任 | Content Trust | 镜像签名验证机制（Notary） |
| 控制组 | cgroup (Control Group) | 限制和隔离进程资源 |
| 命名空间 | Namespace | 隔离进程视图（PID/网络/挂载等） |
| 用户命名空间 | User Namespace | 容器内 root 映射为宿主普通用户 |
| 无根模式 | Rootless Mode | 非 root 用户运行 Docker 守护进程 |
| 热恢复 | Live Restore | 升级守护进程时不中断运行中的容器 |
| 构建工具 | BuildKit / buildx | 镜像构建引擎 |
| 编排工具 | Docker Compose | 多容器定义与编排 |
| 安全模块 | Security Module | SELinux / AppArmor |
| 防火墙 | Firewall | iptables / nftables / firewalld / UFW |

---

## 附录：daemon.json 完整生产配置模板

```json
{
  "data-root": "/data/docker",
  "registry-mirrors": [
    "https://docker.1ms.run",
    "https://docker.xuanyuan.me"
  ],
  "insecure-registries": [],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  },
  "storage-driver": "overlay2",
  "exec-opts": ["native.cgroupdriver=systemd"],
  "live-restore": true,
  "userland-proxy": false,
  "max-concurrent-downloads": 10,
  "max-concurrent-uploads": 5,
  "default-address-pools": [
    {"base": "172.17.0.0/16", "size": 24}
  ],
  "dns": ["8.8.8.8", "8.8.4.4"],
  "userns-remap": "default",
  "icc": false,
  "no-new-privileges": true,
  "default-ulimits": {
    "nofile": {"Hard": 64000, "Soft": 64000},
    "nproc": {"Hard": 64000, "Soft": 64000}
  }
}
```

> **注意**：`"icc": false` 会禁用容器间默认通信，仅允许通过 `--link` 或自定义网络通信。根据实际需求决定是否启用。

---

> **参考文档**：
> - Docker 官方安装指南（Ubuntu）：https://docs.docker.com/engine/install/ubuntu/ [$TRAE_REF](https://docs.docker.com/engine/install/ubuntu/)
> - Docker 官方安装指南（RHEL）：https://docs.docker.com/engine/install/rhel/ [$TRAE_REF](https://docs.docker.com/engine/install/rhel/)
> - Docker 安装后配置：https://docs.docker.com/engine/install/linux-postinstall/ [$TRAE_REF](https://docs.docker.com/engine/install/linux-postinstall/)
> - Docker 守护进程代理配置：https://docs.docker.com/engine/daemon/proxy/ [$TRAE_REF](https://docs.docker.com/engine/daemon/proxy/)
> - Docker 守护进程故障排查：https://docs.docker.com/engine/daemon/troubleshoot [$TRAE_REF](https://docs.docker.com/engine/daemon/troubleshoot)
> - Docker 与防火墙交互：https://docs.docker.com/engine/network/packet-filtering-firewalls/ [$TRAE_REF](https://docs.docker.com/engine/network/packet-filtering-firewalls/)
> - Docker 安全：https://docs.docker.com/engine/security/ [$TRAE_REF](https://docs.docker.com/engine/security/)
