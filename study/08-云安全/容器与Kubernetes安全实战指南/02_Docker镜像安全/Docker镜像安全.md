# Docker镜像安全

### 2.1 镜像构建安全

#### 2.1.1 最小化基础镜像选择

| 基础镜像 | 大小 | 包含 Shell | 包含包管理器 | 安全性 |
|----------|------|-----------|-------------|--------|
| ubuntu:22.04 | ~77MB | 是 | apt | 中 |
| alpine:3.18 | ~7MB | 是 | apk | 中（musl libc 兼容性问题） |
| distroless | ~2-20MB | **否** | **否** | **高** |
| scratch | 0MB | 否 | 否 | 最高（需静态编译） |

**推荐**：生产环境使用 distroless 或 Alpine，最小化攻击面。

#### 2.1.2 多阶段构建减少攻击面

```dockerfile
# 阶段1：构建阶段（包含编译工具，不进入最终镜像）
FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o myapp -ldflags="-s -w" main.go

# 阶段2：最终镜像（最小化，不含编译工具链）
FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=builder /app/myapp /myapp
USER nonroot:nonroot
ENTRYPOINT ["/myapp"]
```

#### 2.1.3 安全的Dockerfile编写规范

```dockerfile
# 基础镜像：使用固定版本标签，禁止用 latest
FROM python:3.12-slim AS base

# 设置工作目录
WORKDIR /app

# 创建非root用户
RUN groupadd -r appuser && useradd -r -g appuser -s /sbin/nologin appuser

# 仅复制必要文件，使用 .dockerignore 排除 .git/credentials
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    rm -rf /root/.cache /tmp/*

# 切换为非root用户
USER appuser

# 暴露端口
EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

CMD ["python", "app.py"]
```

### 2.2 镜像漏洞扫描

#### 2.2.1 Trivy使用实战

```bash
# 扫描镜像漏洞
trivy image python:3.12-slim

# 仅显示高危和严重漏洞
trivy image --severity HIGH,CRITICAL python:3.12-slim

# 输出JSON格式，便于CI/CD集成
trivy image --format json -o results.json python:3.12-slim

# 扫描时跳过已修复的漏洞
trivy image --ignore-unfixed python:3.12-slim

# 使用 Trivy 内置策略检查 Dockerfile
trivy config Dockerfile
```

#### 2.2.2 Grype扫描

```bash
# 安装并扫描
grype python:3.12-slim

# 仅显示固定版本可修复的漏洞
grype python:3.12-slim --only-fixed
```

#### 2.2.3 镜像签名（Cosign）

```bash
# 生成密钥对
cosign generate-key-pair

# 对镜像签名
cosign sign --key cosign.key myregistry.com/myapp:v1.0

# 验证签名
cosign verify --key cosign.pub myregistry.com/myapp:v1.0

# 在K8s准入策略中强制验证签名（详见第四章准入控制器部分）
```

### 2.3 镜像仓库安全

#### 2.3.1 Harbor私有仓库

Harbor 是企业级私有镜像仓库，提供镜像扫描、签名验证、访问控制等能力。核心安全配置：

```yaml
# Harbor 安全配置要点
# 1. 启用漏洞扫描：每次 push 后自动扫描
# 2. 启用镜像签名：集成 Notary/Cosign
# 3. 配置机器人账户：CI/CD 使用受限 token
# 4. 配置副本与存储加密

# Harbor docker-compose 中的核心服务
core:
  environment:
    - CONFIG_PATH=/etc/core/app.conf
    - NOTARY_URL=https://notary.harbor.local
    -clair_url=http://clair:6060
    # 启用 OIDC 认证
    - OIDC_NAME=SSO
    - OIDC_ENDPOINT=https://keycloak.local/auth/realms/main
    - OIDC_CLIENTID=harbor
    - OIDC_CLIENTSECRET=<secret>
```

---

---

