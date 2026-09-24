# DevSecOps 与 CI/CD 安全

### 4.1 DevSecOps 概述

DevSecOps 是将安全融入 DevOps 流程的理念，在软件开发生命周期（SDLC）的每个阶段都考虑安全。

**安全左移（Shift Left）**：将安全工作从后期（生产环境）提前到早期（设计、开发、测试阶段），更早发现和修复安全问题，降低修复成本。

#### 4.1.1 DevSecOps 工具链

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│    代码提交    │  │   构建阶段    │  │   测试阶段    │  │   部署阶段    │
│  (Commit)    │  │   (Build)    │  │   (Test)     │  │  (Deploy)    │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │                │
       ▼                ▼                ▼                ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  SAST 扫描   │  │  镜像构建    │  │  DAST 测试   │  │  IaC 扫描    │
│  代码静态分析 │  │  镜像扫描    │  │  动态安全测试 │  │  配置合规检查 │
│  密钥检测    │  │  SCA 依赖检查│  │  模糊测试    │  │  准入控制    │
│  依赖检查    │  │  镜像签名    │  │  渗透测试    │  │  运行时监控  │
└─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘
```

### 4.2 CI/CD 流水线安全

#### 4.2.1 CI/CD 流水线安全风险

| 风险 | 说明 |
|------|------|
| 凭证泄露 | CI/CD 配置中的密钥被泄露 |
| 代码投毒 | 攻击者通过 PR 注入恶意代码 |
| 供应链攻击 | 依赖包被篡改 |
| 镜像篡改 | 构建的镜像被篡改 |
| 权限过大 | CI/CD 系统拥有过多部署权限 |
| 流水线注入 | 构建脚本被篡改 |

#### 4.2.2 CI/CD 安全最佳实践

1. **凭证管理**：
   - 使用 CI/CD 系统的 Secrets 管理功能
   - 禁止在代码中硬编码密钥
   - 定期轮换 CI/CD 凭证

2. **代码安全**：
   - 代码审查（Code Review）
   - 静态代码分析（SAST）
   - 依赖漏洞扫描（SCA）
   - 密钥检测（Secret Scanning）

3. **构建安全**：
   - 使用可信的基础镜像
   - 镜像漏洞扫描
   - 镜像签名与验证
   - 最小化镜像（减少攻击面）

4. **部署安全**：
   - 基础设施即代码（IaC）安全扫描
   - 部署前安全门禁
   - 金丝雀发布/蓝绿部署
   - 最小权限的部署账号

#### 4.2.3 GitHub Actions 安全示例

```yaml
name: CI/CD Pipeline

on: [push, pull_request]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # 1. 代码静态分析（SAST）
      - name: Run SAST with SonarQube
        uses: sonarsource/sonarqube-scan-action@master
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}

      # 2. 依赖漏洞扫描（SCA）
      - name: Run SCA with Snyk
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: test --severity-threshold=high

      # 3. 密钥检测
      - name: Secret Scanning
        uses: trufflesecurity/trufflehog@main
        with:
          path: .
          extra_args: --only-verified

      # 4. IaC 扫描
      - name: IaC Scan with Checkov
        uses: bridgecrewio/checkov-action@master
        with:
          directory: terraform/
          framework: terraform

  build-and-scan-image:
    runs-on: ubuntu-latest
    needs: security-scan
    steps:
      - uses: actions/checkout@v4

      # 5. 构建镜像
      - name: Build Docker image
        run: docker build -t my-app:${{ github.sha }} .

      # 6. 镜像漏洞扫描
      - name: Scan image with Trivy
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: my-app:${{ github.sha }}
          format: 'table'
          exit-code: '1'
          ignore-unfixed: true
          severity: 'CRITICAL,HIGH'

      # 7. 镜像签名
      - name: Sign image with Cosign
        run: |
          cosign sign --key ${{ secrets.COSIGN_PRIVATE_KEY }} \
            my-app:${{ github.sha }}
```

### 4.3 安全测试类型

| 测试类型 | 全称 | 阶段 | 说明 |
|----------|------|------|------|
| SAST | Static Application Security Testing | 编码/构建 | 静态代码分析，不运行代码 |
| DAST | Dynamic Application Security Testing | 测试/部署 | 动态测试运行中的应用 |
| SCA | Software Composition Analysis | 构建 | 分析第三方组件和依赖漏洞 |
| IAST | Interactive Application Security Testing | 测试 | 交互式测试，结合 SAST 和 DAST |
| IaC Scanning | Infrastructure as Code Scanning | 构建/部署 | 扫描基础设施配置 |
| Container Scanning | Container Image Scanning | 构建 | 扫描容器镜像漏洞 |

---

---

