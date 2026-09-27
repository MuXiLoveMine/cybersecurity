# M9 安全开发与 DevSecOps · 详细补充

> **模块编号**：M9
> **所属阶段**：阶段三 · 方向深化
> **建议学习时机**：第 13-18 个月（有编程 + 安全基础后）
> **前置知识**：M1（Python/JS/Go）+ M4（Web 安全深入）+ M8（云原生基础）
> **每日投入**：2 小时（其中编码 ≥ 1.5 小时）
> **信息时效**：2026 年 9 月版

---

## 1. 模块定位与前置知识

### 模块定位
安全开发（Security Development）是从**开发源头**保障软件安全的学科，DevSecOps 是将安全融入 DevOps 流水线的实践方法论。

传统安全是"事后检查"，而安全开发和 DevSecOps 是"安全左移"——在设计、编码、构建、测试阶段就把安全嵌入进去，从源头减少漏洞，降低修复成本。

本模块覆盖 **SDL 安全开发生命周期、代码审计、API 安全、DevSecOps 流水线、安全编码、威胁建模** 六大核心内容。

### 前置知识
- **必选前置**：M1（Python/JS/SQL，至少一门语言熟练）+ M4（Web 安全深入）
- **推荐前置**：M8（云原生基础，DevSecOps 部分需要）
- **编程能力**：至少精通一门后端语言（Java / Python / Go / Node.js 选一）
- **开发经验**：有实际项目开发经验更佳

### 安全开发能力分级

| 级别 | 能力描述 | 对应岗位 |
|------|---------|---------|
| **L1 入门** | 了解安全编码规范、会用 SAST 工具、能发现简单漏洞 | 开发工程师（安全意识） |
| **L2 实用** | 能做代码审计、会写安全代码、能搭建基础 DevSecOps 流水线 | 安全开发工程师 |
| **L3 熟练** | 能设计安全架构、威胁建模、复杂漏洞挖掘、DevSecOps 体系建设 | 高级安全开发 / SDL 工程师 |
| **L4 精通** | 安全架构师、0day 挖掘、安全框架设计、安全团队管理 | 安全架构师 / 安全技术专家 |

---

## 2. 知识图谱

```
安全开发与 DevSecOps 知识体系
├── SDL 安全开发生命周期
│   ├── SDL 基础
│   │   ├── 什么是 SDL（Security Development Lifecycle）
│   │   ├── 微软 SDL 七大阶段
│   │   ├── OWASP SAMM（软件保障成熟度模型）
│   │   ├── BSIMM（构建安全成熟度模型）
│   │   └── DevSecOps 与 SDL 的关系
│   ├── 需求阶段
│   │   ├── 安全需求分析
│   │   ├── 安全用例 / 滥用用例
│   │   ├── 合规要求（等保 / 个保法 / GDPR）
│   │   └── 隐私设计（Privacy by Design）
│   ├── 设计阶段
│   │   ├── 威胁建模（Threat Modeling）⭐⭐⭐ 重点
│   │   │   ├── STRIDE 模型
│   │   │   ├── DREAD 风险评级
│   │   │   ├── 攻击树（Attack Tree）
│   │   │   ├── PASTA 方法论
│   │   │   └── 威胁建模工具（Microsoft Threat Modeling Tool / OWASP Threat Dragon）
│   │   ├── 安全设计原则
│   │   │   ├── 最小权限原则
│   │   │   ├── 纵深防御
│   │   │   ├── 失败安全（Fail Secure）
│   │   │   ├── 不信任外部输入
│   │   │   ├── 安全的默认配置
│   │   │   └── 单点失效（避免单点）
│   │   └── 安全架构设计
│   ├── 开发阶段
│   │   ├── 安全编码规范
│   │   ├── 代码安全评审（Code Review）
│   │   ├── SAST 静态分析
│   │   └── 安全编码培训
│   ├── 测试阶段
│   │   ├── DAST 动态测试
│   │   ├── 渗透测试
│   │   ├── 模糊测试（Fuzzing）
│   │   └── 安全测试用例
│   ├── 部署阶段
│   │   ├── 配置安全
│   │   ├── 密钥与凭证管理
│   │   ├── 部署流程安全
│   │   └── 镜像安全（容器）
│   └── 运维阶段
│       ├── 漏洞管理
│       ├── 安全监控
│       ├── 应急响应
│       └── 安全更新与补丁
│
├── 安全编码
│   ├── 安全编码原则
│   │   ├── 输入验证（白名单 > 黑名单）
│   │   ├── 输出编码
│   │   ├── 错误处理（不泄露敏感信息）
│   │   ├── 日志安全（不记录敏感数据）
│   │   ├── 加密与哈希（正确使用加密算法）
│   │   ├── 安全的随机数（CSPRNG）
│   │   └── 资源管理（内存 / 文件 / 连接）
│   ├── 各语言安全编码
│   │   ├── Python 安全编码
│   │   │   ├── 注入防御（SQL / 命令 / 代码）
│   │   │   ├── pickle / yaml 反序列化安全
│   │   │   ├── Jinja2 SSTI 防御
│   │   │   ├── Django / Flask 安全配置
│   │   │   └── requests / urllib 安全使用
│   │   ├── Java 安全编码
│   │   │   ├── SQL 注入防御（PreparedStatement / MyBatis）
│   │   │   ├── 反序列化漏洞防御
│   │   │   ├── Spring Security
│   │   │   ├── Shiro 安全配置
│   │   │   └── Fastjson / Jackson 安全
│   │   ├── JavaScript / Node.js 安全编码
│   │   │   ├── XSS 防御
│   │   │   ├── 原型链污染
│   │   │   ├── eval / Function 危险函数
│   │   │   ├── Express / Koa 安全配置
│   │   │   └── NPM 依赖安全
│   │   ├── Go 安全编码
│   │   │   ├── 模板注入防御
│   │   │   ├── SQL 注入防御
│   │   │   ├── Gin / Echo 安全配置
│   │   │   └── Go 模块安全
│   │   └── C/C++ 安全编码（选学）
│   │       ├── 缓冲区溢出防御
│   │       ├── 格式化字符串
│   │       ├── 内存安全
│   │       └── 编译器安全选项
│   └── OWASP Top 10 防御编码实践
│       ├── 注入防御（SQL / 命令 / 代码）
│       ├── 认证失效防御
│       ├── 敏感数据泄露防御
│       ├── XSS 防御
│       ├── 访问控制失效防御
│       ├── 安全配置错误防御
│       ├── 不安全的反序列化防御
│       ├── 已知漏洞组件防御
│       ├── 日志与监控不足防御
│       └── 服务端请求伪造（SSRF）防御
│
├── 代码审计（白盒测试）
│   ├── 代码审计基础
│   │   ├── 什么是代码审计
│   │   ├── 代码审计方法论
│   │   ├── 审计流程（准备 → 分析 → 验证 → 报告）
│   │   └── 审计策略（正向追踪 / 逆向追溯 / 危险函数搜索）
│   ├── 自动化审计工具（SAST）
│   │   ├── SonarQube
│   │   ├── Semgrep ⭐⭐⭐ 重点
│   │   ├── Fortify SCA
│   │   ├── Checkmarx
│   │   ├── CodeQL
│   │   ├── FindSecBugs（Java）
│   │   ├── Bandit（Python）
│   │   ├── ESLint + 安全规则（JS）
│   │   ├── Gosec（Go）
│   │   └── 工具选型与对比
│   ├── 手工代码审计
│   │   ├── 危险函数与关键字
│   │   ├── 入口点分析（路由 / 控制器 / API）
│   │   ├── 数据流追踪（Source → Sink）
│   │   ├── 漏洞模式识别
│   │   └── 业务逻辑漏洞审计
│   ├── 各语言代码审计
│   │   ├── PHP 代码审计（经典 CMS / 框架）
│   │   ├── Java 代码审计（Spring / Struts2 / 中间件）
│   │   ├── Python 代码审计（Django / Flask）
│   │   ├── Node.js 代码审计（Express / Koa）
│   │   └── .NET 代码审计
│   ├── 框架与组件审计
│   │   ├── 常见框架漏洞模式
│   │   ├── 第三方组件审计
│   │   └── 供应链安全
│   └── 代码审计报告
│       ├── 漏洞分级（严重/高危/中危/低危）
│       ├── 漏洞描述 + 代码位置 + 复现步骤
│       ├── 修复建议（含代码示例）
│       └── 审计总结
│
├── API 安全
│   ├── API 基础
│   │   ├── REST API / GraphQL / gRPC / WebSocket
│   │   ├── API 版本控制
│   │   ├── API 文档（Swagger / OpenAPI）
│   │   └── API 网关
│   ├── OWASP API Security Top 10 ⭐⭐⭐ 重点
│   │   ├── API01: 授权失效（Broken Object Level Authorization）
│   │   ├── API02: 认证失效（Broken Authentication）
│   │   ├── API03: 对象属性暴露（Broken Object Property Level Authorization）
│   │   ├── API04: 无节制资源消耗（Unrestricted Resource Consumption）
│   │   ├── API05: 功能权限缺失（Broken Function Level Authorization）
│   │   ├── API06: 批量分配（Mass Assignment）
│   │   ├── API07: 安全配置错误（Security Misconfiguration）
│   │   ├── API08: 2023 库存缺失（Missing Inventory）
│   │   ├── API09: 资产管理不当（Improper Assets Management）
│   │   └── API10: 消费端数据不安全（Unsafe Consumption of APIs）
│   ├── API 认证与授权
│   │   ├── API Key
│   │   ├── OAuth 2.0（授权码 / 客户端凭证 / 隐式 / 密码模式）
│   │   ├── OIDC（OpenID Connect）
│   │   ├── JWT 安全（签名验证 / 算法混淆 / 密钥管理）
│   │   ├── HMAC 签名
│   │   └── mTLS 双向认证
│   ├── API 常见漏洞与防御
│   │   ├── 越权访问（水平 / 垂直）
│   │   ├── 注入（SQL / NoSQL / 命令）
│   │   ├── 批量分配 /  Mass Assignment
│   │   ├── 速率限制缺失（暴力破解 / 短信轰炸）
│   │   ├── API 信息泄露（Swagger / 调试信息 / 堆栈）
│   │   ├── GraphQL 安全（查询深度 / 内省 / 注入）
│   │   ├── WebSocket 安全
│   │   └── SSRF（通过 API 调用内网）
│   ├── API 安全测试
│   │   ├── Postman / Bruno（API 测试工具）
│   │   ├── Burp Suite API 测试
│   │   ├── OWASP ZAP API 扫描
│   │   ├── API 模糊测试
│   │   └── Postman 安全测试集合
│   └── API 安全防护
│       ├── API 网关安全策略
│       ├── WAF / API 安全网关
│       ├── 速率限制 / 流控
│       ├── API 审计日志
│       └── API 安全标准（OAuth / OIDC / FAPI）
│
├── DevSecOps
│   ├── DevOps 基础
│   │   ├── DevOps 文化与原则
│   │   ├── CI/CD 概念与流程
│   │   ├── 版本控制（Git 工作流）
│   │   ├── 持续集成 / 持续交付 / 持续部署
│   │   └── 常见 CI/CD 工具（Jenkins / GitLab CI / GitHub Actions）
│   ├── DevSecOps 基础
│   │   ├── 什么是 DevSecOps
│   │   ├── 安全左移（Shift Left）
│   │   ├── 安全右移（Shift Right - 运行时安全）
│   │   ├── DevSecOps 文化与组织
│   │   └── DevSecOps 成熟度模型
│   ├── CI/CD 流水线安全
│   │   ├── 代码提交阶段
│   │   │   ├── Pre-commit hooks
│   │   │   ├── 代码规范检查
│   │   │   ├── 密钥检测（Git hooks）
│   │   │   └── 本地 SAST
│   │   ├── 代码合并阶段（MR / PR）
│   │   │   ├── 代码评审（Code Review）
│   │   │   ├── SAST 扫描
│   │   │   ├── SCA 依赖扫描
│   │   │   ├── IaC 安全扫描
│   │   │   └── 质量门禁
│   │   ├── 构建阶段
│   │   │   ├── 构建环境安全
│   │   │   ├── 容器镜像扫描
│   │   │   ├── 镜像签名（Sigstore / Cosign）
│   │   │   └── SBOM 生成
│   │   ├── 测试阶段
│   │   │   ├── DAST 扫描
│   │   │   ├── API 安全测试
│   │   │   ├── 模糊测试
│   │   │   └── 渗透测试（自动化）
│   │   ├── 部署阶段
│   │   │   ├── 部署前准入检查
│   │   │   ├── 配置安全扫描
│   │   │   ├── 密钥与凭证管理
│   │   │   └── GitOps 安全
│   │   └── 运行阶段
│   │       ├── 运行时安全监控
│   │       ├── 漏洞管理与修复
│   │       └── 安全遥测与反馈
│   ├── CI/CD 系统自身安全
│   │   ├── 代码仓库安全（GitHub / GitLab）
│   │   ├── CI/CD Runner / Agent 安全
│   │   ├── 凭证管理（Secrets Management）
│   │   ├── 流水线注入攻击
│   │   ├── 供应链投毒（依赖混淆 / 恶意包）
│   │   └── 构建安全（供应链攻击）
│   ├── 工具链集成
│   │   ├── Jenkins 安全流水线
│   │   ├── GitLab CI/CD 安全流水线
│   │   ├── GitHub Actions 安全流水线
│   │   ├── SonarQube 集成
│   │   ├── Snyk 集成
│   │   ├── OWASP ZAP 集成
│   │   └── 各工具 API 调用
│   └── 安全度量与运营
│       ├── DevSecOps 指标（MTTD / 修复时长 / 漏洞密度）
│       ├── 安全质量门禁
│       ├── 开发者赋能与培训
│       └── 持续改进
│
├── 软件供应链安全
│   ├── 供应链安全基础
│   │   ├── 什么是软件供应链安全
│   │   ├── 典型事件（SolarWinds / Log4j / xz-utils / Codecov）
│   │   ├── 供应链攻击面
│   │   └── 供应链安全框架
│   ├── SBOM（软件物料清单）
│   │   ├── SBOM 格式（SPDX / CycloneDX / SWID）
│   │   ├── SBOM 生成工具（Syft / Trivy / SPDX tools）
│   │   ├── SBOM 管理与共享
│   │   └── VEX（漏洞可利用性交换）
│   ├── 依赖安全（SCA）
│   │   ├── 依赖管理
│   │   ├── 已知漏洞检测（SCA 工具）
│   │   ├── 依赖混淆攻击（Dependency Confusion）
│   │   ├── 恶意包检测
│   │   └── 依赖更新策略（Dependabot / Renovate）
│   ├── 构建安全
│   │   ├── 构建环境隔离
│   │   ├── 复现构建（Reproducible Builds）
│   │   ├── 构建日志与审计
│   │   └── hermetic builds（密封构建）
│   ├── 签名与验证
│   │   ├── 代码签名
│   │   ├── 容器镜像签名（Cosign / Sigstore）
│   │   ├── Git 提交签名（GPG / SSH）
│   │   └── in-toto 框架
│   ├── SLSA 框架
│   │   ├── SLSA 是什么（Supply-chain Levels for Software Artifacts）
│   │   ├── SLSA 1-4 级要求
│   │   ├── SLSA 实现路径
│   │   └── SLSA 工具
│   └── 国内供应链安全标准
│       ├── GB/T 41479 信息安全技术 网络产品和服务安全通用要求
│       ├── 等保 2.0 供应链安全要求
│       └── 《网络产品安全漏洞管理规定》
│
└── 安全工具开发
    ├── 安全工具开发基础
    │   ├── 工具设计原则
    │   ├── 性能与并发
    │   ├── 可扩展性与插件化
    │   └── 输出与报告
    ├── 常见安全工具开发
    │   ├── 漏洞扫描器
    │   ├── 信息收集工具
    │   ├── 渗透测试框架
    │   ├── 日志分析工具
    │   └── 检测规则引擎
    ├── 安全自动化
    │   ├── 漏洞管理自动化
    │   ├── 安全运营自动化（SOAR）
    │   ├── 报告自动生成
    │   └── API 驱动的安全工作流
    └── 开源安全项目贡献
        ├── 如何参与开源安全项目
        ├── 代码贡献 / 文档贡献
        └── 个人项目开源
```

---

## 3. 学习顺序与时间表

### 总时长：约 5 个月（300 小时）

| 阶段 | 周次 | 学习内容 | 重点任务 | 实验目标 |
|------|------|---------|---------|---------|
| **SDL 与安全编码** | 第 1-3 周 | SDL 方法论 + 威胁建模 | SDL 各阶段、STRIDE/DREAD、Threat Dragon | 完成一次威胁建模 |
| | 第 4-6 周 | 安全编码实践 | OWASP Top 10 防御编码、安全编码规范 | 安全重构一个有漏洞的项目 |
| **代码审计** | 第 7-10 周 | SAST 工具 + 手工审计 | Semgrep / SonarQube、手工审计方法 | 审计 2 个开源项目 |
| | 第 11-13 周 | 代码审计深入 | 框架审计、业务逻辑漏洞、供应链审计 | 发现并报告 3+ 个真实漏洞 |
| **API 安全** | 第 14-16 周 | API 安全 | OWASP API Top 10、JWT/OAuth、GraphQL 安全 | API 安全测试 + 加固 |
| **DevSecOps** | 第 17-20 周 | CI/CD 安全 + DevSecOps 流水线 | 多阶段安全检查、工具集成 | 搭建完整 DevSecOps 流水线 |
| **供应链安全** | 第 21-23 周 | 软件供应链安全 | SBOM / SCA / SLSA / 签名验证 | 供应链安全项目实践 |
| **综合实战** | 第 24-25 周 | 综合实战 + 安全工具开发 | SDL 全流程落地 + 自研安全工具 | 安全工具开发项目 |

---

## 4. 工具链与版本建议

### 4.1 SAST（静态应用安全测试）

| 工具 | 语言 | 用途 | 优先级 | 费用 |
|------|------|------|--------|------|
| **Semgrep** | 多语言 | 轻量级静态代码扫描，自定义规则 | ⭐⭐⭐ 必学 | 开源免费 + 商业版 |
| **SonarQube** | 多语言 | 代码质量 + 安全分析平台 | ⭐⭐⭐ 必学 | 社区版免费 + 商业版 |
| **CodeQL** | 多语言 | GitHub 代码查询引擎，像查数据库一样查代码 | ⭐⭐⭐ 必学 | 开源免费 |
| **Bandit** | Python | Python 安全扫描器 | ⭐⭐ 重要 | 免费 |
| **FindSecBugs** | Java | Java 静态安全分析（SpotBugs 插件） | ⭐⭐ 重要 | 免费 |
| **Gosec** | Go | Go 语言安全扫描器 | ⭐⭐ 重要 | 免费 |
| **ESLint + security 插件** | JavaScript | JS/TS 安全规则 | ⭐⭐ 重要 | 免费 |
| **Brakeman** | Ruby | Rails 安全扫描器 | ⭐ 选学 | 免费 |
| **Fortify SCA** | 多语言 | 商业 SAST 工具，功能强大 | ⭐ 选学 | 付费（贵） |
| **Checkmarx** | 多语言 | 商业 SAST 工具 | ⭐ 选学 | 付费（贵） |

### 4.2 DAST / API 安全测试

| 工具 | 用途 | 优先级 | 费用 |
|------|------|--------|------|
| **Burp Suite Pro** | Web / API 渗透测试 | ⭐⭐⭐ 必用 | 付费 |
| **OWASP ZAP** | 开源 DAST 扫描器 | ⭐⭐⭐ 必学 | 免费 |
| **Postman / Bruno** | API 测试与调试 | ⭐⭐⭐ 必用 | 免费 + 付费 |
| **k6** | 性能测试（也用于速率限制测试） | ⭐⭐ 推荐 | 免费 |
| **42Crunch / APISec** | API 安全专项测试 | ⭐ 选学 | 付费 |
| **GraphQL Cop / InQL** | GraphQL 安全测试 | ⭐⭐ 重要 | 免费 |
| **wfuzz / ffuf** | API / Web Fuzzing | ⭐⭐⭐ 必用 | 免费 |

### 4.3 SCA 与供应链安全

| 工具 | 用途 | 优先级 | 费用 |
|------|------|--------|------|
| **Snyk** | SCA + 容器 + IaC + 代码 | ⭐⭐⭐ 推荐 | 免费版 + 付费 |
| **OWASP Dependency-Check** | SCA 依赖漏洞扫描 | ⭐⭐⭐ 必学 | 免费 |
| **Trivy** | 容器 + 文件系统 + 依赖扫描 | ⭐⭐⭐ 必学 | 免费 |
| **Dependabot / Renovate** | 自动依赖更新 | ⭐⭐ 重要 | 免费 |
| **Syft** | SBOM 生成 | ⭐⭐ 重要 | 免费 |
| **Grype** | 漏洞扫描（与 Syft 配合） | ⭐⭐ 重要 | 免费 |
| **Cosign / Sigstore** | 镜像 / 代码签名验证 | ⭐⭐ 重要 | 免费 |
| **Gitleaks / TruffleHog** | Git 密钥检测 | ⭐⭐⭐ 必用 | 免费 |
| **OWASP Dependency-Track** | 软件成分分析平台 | ⭐⭐ 推荐 | 免费 |
| **SLSA 工具集** | SLSA 合规工具链 | ⭐ 选学 | 免费 |

### 4.4 IaC 安全

| 工具 | 用途 | 优先级 |
|------|------|--------|
| **Checkov** | IaC 安全扫描（多框架） | ⭐⭐⭐ 必学 |
| **tfsec** | Terraform 安全扫描 | ⭐⭐ 重要 |
| **Terrascan** | IaC 安全扫描（Accurics） | ⭐⭐ 推荐 |
| **Kics** | IaC 安全扫描（Checkmarx） | ⭐⭐ 推荐 |
| **OPA / Rego** | 策略即代码 | ⭐⭐ 重要 |
| **Sentinel** | HashiCorp 策略语言 | ⭐ 选学 |

### 4.5 CI/CD 平台

| 平台 | 用途 | 优先级 |
|------|------|--------|
| **GitHub Actions** | GitHub 原生 CI/CD | ⭐⭐⭐ 必学 |
| **GitLab CI/CD** | GitLab 原生 CI/CD | ⭐⭐⭐ 必学 |
| **Jenkins** | 老牌 CI/CD 工具 | ⭐⭐ 重要 |
| **Argo CD** | GitOps 持续部署（K8s） | ⭐⭐ 推荐 |
| **Flux CD** | GitOps 工具 | ⭐ 选学 |

### 4.6 威胁建模工具

| 工具 | 用途 | 优先级 |
|------|------|--------|
| **OWASP Threat Dragon** | 开源威胁建模工具 | ⭐⭐⭐ 必用 |
| **Microsoft Threat Modeling Tool** | 微软官方威胁建模工具 | ⭐⭐ 推荐 |
| **IriusRisk** | 商业威胁建模平台 | ⭐ 选学 |
| **draw.io / Excalidraw** | 通用绘图（画架构图 / 攻击树） | ⭐⭐⭐ 必用 |

---

## 5. 编程 / 脚本练习

### 5.1 安全编码练习

```python
# 练习 1：安全的用户登录函数
# 修复 SQL 注入、XSS、弱密码、明文传输等问题
# 使用参数化查询 + 密码哈希（bcrypt）+ 输入验证

import bcrypt
import sqlite3

def safe_login(username: str, password: str) -> bool:
    """安全的登录验证"""
    # 输入验证
    if not username or not password:
        return False
    if len(username) > 50 or len(password) > 100:
        return False
    
    # 参数化查询防 SQL 注入
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        # 防止用户名枚举（统一错误信息）
        bcrypt.checkpw(password.encode(), b'$2b$12$dummyhashvaluexxxxxxxxxxxxxxxxxxxxxx')
        return False
    
    # bcrypt 验证密码
    return bcrypt.checkpw(password.encode(), result[0].encode())

# 练习 2：安全的文件上传处理（白名单 + 随机文件名 + 路径限制）
# 练习 3：安全的命令执行（避免命令注入，使用参数列表而非字符串拼接）
# 练习 4：安全的反序列化（避免 pickle / yaml 反序列化不可信数据）
# 练习 5：安全的 JWT 处理（验证签名 + 过期时间 + 算法白名单）
# 练习 6：XSS 防御（输出编码 + CSP + HttpOnly Cookie）
# 练习 7：安全的随机数 / Token 生成（使用 secrets 模块，不用 random）
```

### 5.2 Semgrep 规则编写

```yaml
# 练习 8：编写 Semgrep 规则检测 SQL 注入
rules:
  - id: python-sql-injection
    patterns:
      - pattern-either:
          - pattern: $CURSOR.execute("..." + $USER_INPUT, ...)
          - pattern: $CURSOR.execute(f"...{$USER_INPUT}...", ...)
          - pattern: $CURSOR.execute("%s" % $USER_INPUT, ...)
      - metavariable-regex:
          metavariable: $USER_INPUT
          regex: (request|input|param|data)
    message: "Potential SQL injection: user input used directly in query"
    languages: [python]
    severity: ERROR

# 练习 9：编写 Semgrep 规则检测危险函数使用（eval / exec / system 等）
# 练习 10：编写 Semgrep 规则检测硬编码密码 / API Key
# 练习 11：编写 Semgrep 规则检测不安全的随机数（用 random 代替 secrets）
# 练习 12：编写 Semgrep 规则检测 CORS 配置错误（Access-Control-Allow-Origin: *）
```

### 5.3 DevSecOps 流水线脚本

```python
# 练习 13：CI/CD 安全质量门禁脚本
# - 调用 SAST 扫描
# - 调用 SCA 扫描
# - 调用容器镜像扫描
# - 汇总结果
# - 根据阈值决定是否阻断流水线

# 练习 14：自动化漏洞修复建议生成器
# - 输入：漏洞描述 + 代码片段
# - 输出：修复建议 + 修复后的代码示例
# - 可选：集成 LLM 生成修复建议

# 练习 15：安全代码评审机器人
# - 监听 PR / MR
# - 自动运行 SAST / SCA 扫描
# - 评论扫描结果
# - 标记需要人工评审的高危问题
```

---

## 6. 靶场与实验环境

### 6.1 代码审计靶场

| 靶场 / 项目 | 特点 | 费用 |
|------------|------|------|
| **OWASP WebGoat** | Java 编写的漏洞教学应用，代码可审计 | 免费 |
| **OWASP Juice Shop** | Node.js 编写的现代靶场，有源码可审计 | 免费 |
| **DVWA** | PHP 经典靶场，适合 PHP 代码审计入门 | 免费 |
| **VulnHub 代码审计靶机** | 各种 CMS / 框架的代码审计环境 | 免费 |
| **SecLists** | 安全测试用的各种字典和 Payload | 免费 |
| **Damn Vulnerable NodeJS Application** | Node.js 漏洞应用 | 免费 |
| **VulnApp** | 各种语言的漏洞应用集合 | 免费 |
| **GitHub 上的真实漏洞项目** | 找历史上有已知漏洞的开源项目做审计 | 免费 |

### 6.2 API 安全靶场

| 靶场 | 特点 | 费用 |
|------|------|------|
| **OWASP API Security Top 10 Labs** | OWASP 官方 API 安全实验室 | 免费 |
| **vAPI** | 漏洞 API 靶场（OWASP 项目） | 免费 |
| **crAPI** | 完全糟糕的 API 靶场 | 免费 |
| **GraphQL Damn Vulnerable** | GraphQL 漏洞靶场 | 免费 |
| **Postman 公共工作区** | API 测试集合 | 免费 |
| **HTB API 相关靶机** | HTB 上的 API 漏洞靶机 | 免费 + 付费 |
| **TryHackMe API 专题房间** | API 安全学习路径 | 免费 + 付费 |

### 6.3 DevSecOps 实验环境

```
本地 DevSecOps 实验环境：
  ├── Git 服务器（Gitea / GitLab CE）
  ├── CI/CD（GitLab Runner / Jenkins / GitHub Actions 自托管）
  ├── 代码质量（SonarQube Community）
  ├── 镜像仓库（Harbor / Registry）
  ├── K8s 集群（minikube / kind）
  ├── 示例应用（DVWA / Juice Shop / 自己的项目）
  └── 安全工具链（Semgrep / Trivy / OWASP ZAP / Gitleaks）

流水线实验：
  代码提交 → Pre-commit（密钥检测 + 格式检查）
       ↓
  CI 构建 → SAST + SCA + 密钥检测 + 单元测试
       ↓
  镜像构建 → Dockerfile 扫描 + 镜像漏洞扫描 + SBOM 生成
       ↓
  部署测试 → DAST 扫描 + IaC 安全扫描 + 安全门禁
       ↓
  生产部署 → 运行时监控 + 漏洞管理
```

### 6.4 CTF 与竞赛

| 比赛 / 平台 | 类型 | 说明 |
|------------|------|------|
| **代码审计类 CTF** | CTF | 国内 CTF 常考代码审计 |
| **Real World CTF** | CTF | 真实世界漏洞，难度高 |
| **HTB 企业靶场** | 企业级 | 接近真实环境的代码审计 |
| **HackerOne / 补天** | 漏洞赏金 | 真实项目漏洞挖掘 |
| **Snyk Code Challenges** | 代码安全挑战 | Snyk 官方安全挑战 |

---

## 7. 推荐资料

### 📚 书籍

| 书名 | 难度 | 备注 |
|------|------|------|
| **《代码审计：企业级 Web 安全架构》** | ⭐⭐⭐ 进阶 | 国内代码审计经典 |
| **《Web 安全深度剖析》** | ⭐⭐ 入门 | 张炳帅著，含代码审计 |
| **《白帽子讲 Web 安全》**第 2 版 | ⭐⭐ 入门 | 吴翰清著，安全思维 |
| **《Building Secure & Reliable Systems》** | ⭐⭐⭐ 进阶 | Google SRE + 安全，英文 |
| **《Threat Modeling》** | ⭐⭐ 入门 | 威胁建模设计安全 |
| **《OWASP Top 10 中文版》** | ⭐⭐ 入门 | OWASP 官方文档 |
| **《DevOps 安全实战》** | ⭐⭐ 入门 | DevSecOps 实践 |
| **《Securing DevOps》** | ⭐⭐⭐ 进阶 | Manning 出版，DevSecOps 经典，英文 |
| **《软件供应链安全》** | ⭐⭐⭐ 进阶 | 供应链安全专题 |
| **《API 安全实战》** | ⭐⭐ 入门 | API 安全实战 |

### 🌐 在线资源

| 资源 | 关键词 | 特点 |
|------|--------|------|
| **OWASP 官网** | owasp.org | OWASP 项目大全，必收藏 |
| **OWASP Cheat Sheet Series** | cheatsheetseries.owasp.org | 各种安全主题速查表 |
| **OWASP SAMM** | owasp.org/www-project-samm | 软件保障成熟度模型 |
| **OWASP API Security Top 10** | owasp.org/www-project-api-security | API 安全 Top 10 |
| **OWASP Dependency-Check** | owasp.org/www-project-dependency-check | SCA 工具 |
| **Semgrep 官方文档** | semgrep.dev/docs | Semgrep 使用与规则编写 |
| **SLSA 官网** | slsa.dev | 供应链安全等级框架 |
| **NIST SSDF** | nist.gov/ssdf | 安全软件开发框架 |
| **Microsoft SDL** | microsoft.com/security/sdl | 微软 SDL 方法论 |
| **安全编码规范（CERT）** | cert.org/secure-coding | CERT 安全编码标准 |
| **HackTricks - Source Code Review** | book.hacktricks.xyz/generic-methodologies-and-resources | 代码审计技巧 |

### 🎥 视频与创作者

| 创作者 / 课程 | 平台 | 特点 |
|-------------|------|------|
| **代码审计系列** | B 站（多位 UP 主） | 中文代码审计教程 |
| **IppSec** | YouTube | 偶尔有代码审计视频 |
| **LiveOverflow** | YouTube | 深入的漏洞分析 |
| **Gynvael Coldwind** | YouTube | 安全与代码审计 |
| **OWASP 官方频道** | YouTube | OWASP 官方视频 |
| **SonarSource** | YouTube | SonarQube 与代码质量 |
| **SnykLearn** | YouTube / snyk.io | Snyk 安全课程 |
| **DevSecOps 系列** | B 站 / 各大厂商 | 中文 DevSecOps 实战 |

### 📝 社区与博客

| 平台 | 用途 |
|------|------|
| **先知社区 / FreeBuf** | 国内代码审计 / 安全开发文章 |
| **安全客** | 安全技术 |
| **Seebug 漏洞平台** | 知道创宇漏洞平台 |
| **Reddit r/netsec / r/devsecops** | 国际社区 |
| **Dev.to - Security** | 开发者安全社区 |
| **Troy Hunt Blog** | 安全名人博客 |
| **PortSwigger Research** | Burp 团队研究博客 |
| **Snyk Blog** | 漏洞与供应链安全博客 |

---

## 8. 实战项目

### 项目一：代码审计实战

**目标**：对 2-3 个开源项目进行完整的代码审计，发现漏洞并输出审计报告。

**审计对象**（建议难度递进）：
1. **简单项目**：DVWA / BWAPP（已知漏洞，练手）
2. **中等项目**：某个小型 CMS 或博客系统（选有已知 CVE 的）
3. **真实项目**：选一个 GitHub 上 Star 不多但真实的项目

**审计内容**：
1. **准备阶段**
   - 搭建运行环境
   - 了解项目架构和功能
   - 梳理入口点（路由 / 控制器 / API）
2. **自动化扫描**
   - Semgrep 扫描（自定义规则 + 社区规则）
   - SonarQube 扫描
   - SCA 依赖扫描
   - 记录所有发现，分类整理
3. **手工审计**
   - 危险函数搜索（eval / system / exec / unserialize 等）
   - 数据流追踪（用户输入 → 危险函数）
   - 认证授权审计
   - 业务逻辑审计
   - 配置安全审计
4. **漏洞验证**
   - 每个疑似漏洞都要实际验证
   - 构造 PoC / EXP
   - 确认漏洞真实存在
5. **报告撰写**
   - 漏洞清单（按严重程度排序）
   - 每个漏洞：描述 / 风险等级 / 代码位置 / 复现步骤 / 修复建议
   - 整体安全评估
   - 改进建议

**预计耗时**：40 小时
**产出物**：代码审计报告（3 份以上，每份 20+ 页）

---

### 项目二：安全重构——把有漏洞的项目变安全

**目标**：拿一个有漏洞的 Web 应用（如 DVWA / 自己写的有漏洞的博客），逐个修复所有漏洞，输出安全重构前后的对比。

**漏洞修复清单**：
1. **SQL 注入** → 全部改为预编译语句（PreparedStatement / ORM 参数化）
2. **XSS** → 输出编码 + CSP 头 + HttpOnly Cookie
3. **CSRF** → 添加 CSRF Token 验证
4. **文件上传** → 白名单后缀 + 随机文件名 + 独立存储域 + MIME 验证
5. **命令注入** → 禁止拼接命令字符串，使用参数数组
6. **反序列化** → 禁止反序列化不可信数据，改用 JSON
7. **密码安全** → bcrypt / Argon2 哈希 + 强度策略
8. **认证安全** → 登录失败次数限制 + MFA + Session 安全
9. **授权安全** → 每个接口做权限校验，防止越权
10. **错误处理** → 生产环境不显示详细错误信息和堆栈
11. **日志安全** → 不记录敏感数据（密码 / Token / 身份证号）
12. **安全头** → 配置完整的 HTTP 安全响应头
13. **依赖安全** → 升级所有有已知漏洞的依赖
14. **配置安全** → 移除默认配置、关闭调试模式

**交付物**：
- 修复后的完整代码
- 每个漏洞的修复说明（漏洞 → 原因 → 修复方案 → 代码对比）
- 安全编码规范文档
- 重新扫描验证报告（SAST + DAST 验证漏洞已修复）

**预计耗时**：35 小时
**产出物**：安全重构后的项目 + 修复手册 + 验证报告

---

### 项目三：DevSecOps 流水线建设

**目标**：为一个示例项目搭建完整的 DevSecOps 流水线，从代码提交到部署全流程嵌入安全检查。

**项目选择**：一个包含前后端的 Web 应用（如 Node.js + React 或 Python + Vue）

**流水线设计**：

```
代码提交阶段（本地 Pre-commit）
  ├── 代码格式检查（Prettier / Black / ESLint）
  ├── 密钥检测（Gitleaks pre-commit hook）
  └── 本地单元测试
        ↓
PR / MR 阶段（CI）
  ├── SAST 扫描（Semgrep + SonarQube）
  ├── SCA 依赖扫描（Dependency-Check / Snyk）
  ├── 代码覆盖率检查
  ├── 质量门禁（阻断高危漏洞）
  └── 人工 Code Review（高危变更强制）
        ↓
合并到主分支
  ├── 构建应用
  ├── 构建 Docker 镜像
  ├── Dockerfile 安全扫描（Hadolint）
  ├── 镜像漏洞扫描（Trivy）
  ├── 镜像签名（Cosign）
  ├── SBOM 生成（Syft）
  └── 推送到私有镜像仓库
        ↓
部署到测试环境
  ├── IaC 安全扫描（Checkov / tfsec）
  ├── DAST 扫描（OWASP ZAP）
  ├── API 安全测试
  └── 集成测试 + 安全测试
        ↓
部署到生产环境
  ├── 灰度发布 / 蓝绿部署
  ├── 运行时安全监控（Falco / Wazuh）
  ├── 漏洞持续监控
  └── 安全告警接入 SOC
```

**技术栈**：GitHub Actions / GitLab CI + SonarQube + Trivy + OWASP ZAP + Checkov
**预计耗时**：40 小时
**产出物**：完整的 DevSecOps 流水线 + 示例项目 + 流水线设计文档

---

### 项目四：威胁建模与安全设计

**目标**：为一个中等复杂度的系统做完整的威胁建模，并输出安全设计方案。

**系统选择**：一个在线电商系统（或博客 / 社交平台）

**任务清单**：
1. **系统设计**
   - 画出系统架构图（前端 / 后端 / 数据库 / 缓存 / 消息队列 / 第三方服务）
   - 定义数据流向
   - 定义信任边界
   - 列出所有用户角色和权限
2. **威胁识别（STRIDE 模型）**
   - 每个组件和数据流都用 STRIDE 分析
   - Spoofing（仿冒）
   - Tampering（篡改）
   - Repudiation（抵赖）
   - Information Disclosure（信息泄露）
   - Denial of Service（拒绝服务）
   - Elevation of Privilege（权限提升）
3. **风险评级（DREAD）**
   - 每个威胁按 DREAD 评分
   - Damage（潜在损害）
   - Reproducibility（复现难度）
   - Exploitability（利用难度）
   - Affected Users（受影响用户数）
   - Discoverability（发现难度）
4. **安全设计与缓解措施**
   - 每个威胁对应的缓解方案
   - 安全设计原则的应用
   - 安全技术选型（WAF / IDS / 加密 / 认证等）
5. **攻击树（Attack Tree）**
   - 选择 2-3 个关键威胁，画攻击树
   - 根节点（攻击目标）→ 中间节点（攻击方法）→ 叶节点（具体步骤）
6. **输出威胁建模报告**
   - 系统描述与架构图
   - 信任边界与数据流
   - 威胁清单（STRIDE + DREAD）
   - 缓解措施与优先级
   - 攻击树
   - 安全设计建议

**工具**：OWASP Threat Dragon / Microsoft Threat Modeling Tool / draw.io
**预计耗时**：25 小时
**产出物**：威胁建模报告 + 安全设计方案 + 攻击树

---

## 9. 常见误区

### ❌ 误区 1：安全开发就是"加个 WAF"
**现象**：觉得代码有漏洞没关系，上线加个 WAF 就能防住。
**纠正**：WAF 只是防御的一环，不能替代安全编码。WAF 有绕过方法，而且很多业务逻辑漏洞 WAF 根本防不住。安全必须从源头做起，代码层的安全才是根本。

### ❌ 误区 2：代码审计就是跑个 SAST 工具
**现象**：用 SAST 工具扫一遍，把报告改完就觉得代码审计做完了。
**纠正**：自动化工具只能发现"已知模式"的漏洞，而且误报率不低。业务逻辑漏洞、复杂的权限问题、架构层面的问题，自动化工具根本发现不了。代码审计 = 工具扫描 + 人工审计，人工才是核心。

### ❌ 误区 3：安全开发就是"背安全编码规范"
**现象**：背了一堆安全编码规范，但写代码时还是会出漏洞。
**纠正**：安全编码不是靠背诵，而是靠理解漏洞原理。理解了为什么会产生漏洞，自然就知道怎么写才安全。配合代码评审、自动化扫描、安全培训等机制，形成体系化保障。

### ❌ 误区 4：DevSecOps 就是"在流水线里加几个安全工具"
**现象**：在 CI 里加了 SAST 和 SCA 扫描，就说自己做了 DevSecOps。
**纠正**：DevSecOps 是文化、流程、工具的结合。工具只是最表层的，更重要的是安全左移的理念、开发者的安全意识、流程的嵌入、度量与持续改进。只加工具不做运营，最后扫描器堆了一堆，漏洞还是照样出。

### ❌ 误区 5：安全和开发是对立的
**现象**：觉得安全就是"给开发找事"、"拖慢进度"，开发也觉得安全部门没事找事。
**纠正**：安全和开发的目标是一致的——交付高质量的产品。安全开发的目标是让安全成为开发的助力而不是阻力。通过自动化工具、安全左移、开发者赋能，让安全在不影响效率的前提下落地。

### ❌ 误区 6：只关注代码，不关注供应链
**现象**：自己的代码写得很安全，但依赖包里全是漏洞也不管。
**纠正**：现代软件 90% 以上的代码来自第三方依赖。供应链安全已经成为最大的安全风险之一。Log4j、xz-utils 这些事件还历历在目。SCA、依赖管理、SBOM 都是安全开发的必备技能。

### ❌ 误区 7：威胁建模是"架构师的事"，和开发没关系
**现象**：觉得威胁建模是架构师和安全专家的工作，开发人员不用管。
**纠正**：威胁建模不只是高层设计阶段的事，也不是只有专家才能做。简单的威胁建模（如 STRIDE）开发人员也能做，而且越早做越好，越早在设计阶段发现问题，修复成本越低。

---

## 10. 自测题与产出物

### 10.1 基础理论题

1. 什么是 SDL？简述 SDL 的主要阶段。
2. 什么是威胁建模？STRIDE 和 DREAD 分别是什么？
3. 安全设计原则有哪些？（至少说 8 个，并解释含义）
4. 什么是 SAST / DAST / IAST / SCA？各自的优缺点和适用场景？
5. 代码审计的方法论有哪些？正向追踪和逆向追溯的区别？
6. OWASP API Security Top 10 有哪些？选 3 个详细说明。
7. JWT 安全问题有哪些？（至少 5 种）如何防御？
8. OAuth 2.0 有几种授权模式？各自的适用场景和安全风险？
9. 什么是 DevSecOps？安全左移和安全右移分别是什么意思？
10. CI/CD 流水线中，哪些阶段可以嵌入安全检查？各检查什么？
11. 什么是软件供应链安全？常见的供应链攻击类型有哪些？
12. 什么是 SBOM？常见的 SBOM 格式有哪些？SBOM 有什么用？
13. 什么是 SLSA 框架？它有几个级别？每个级别的核心要求是什么？
14. 什么是依赖混淆攻击（Dependency Confusion）？原理和防御方法？
15. 什么是 Cosign / Sigstore？它们解决什么问题？
16. 什么是安全的编码原则？输入验证为什么要用白名单而不是黑名单？
17. 常见的密码存储方式有哪些？为什么不能用 MD5 / SHA1 存密码？
18. XSS 的防御方法有哪些？输出编码和 CSP 分别是什么原理？
19. SQL 注入的防御方法有哪些？预编译为什么能防注入？
20. 什么是 Mass Assignment（批量赋值）漏洞？如何防御？
21. 什么是 GraphQL 安全？GraphQL 常见的安全问题有哪些？
22. 什么是安全质量门禁（Quality Gate）？在 DevSecOps 中如何落地？
23. 什么是 Secrets Management？CI/CD 中的密钥应该如何管理？
24. CI/CD 系统自身有哪些安全风险？如何防护？
25. 什么是 GitOps？GitOps 的安全风险和最佳实践有哪些？

### 10.2 实操题

1. 用 Semgrep 编写 10 条自定义安全规则（覆盖 SQL 注入、XSS、命令注入、硬编码密码等），并在一个真实项目上测试效果。
2. 对一个开源项目进行完整的代码审计，至少发现 5 个真实漏洞，输出专业的代码审计报告。
3. 拿一个有漏洞的 Web 应用（如 DVWA），修复所有高危漏洞，并通过 SAST + DAST 扫描验证修复效果。
4. 搭建一个完整的 DevSecOps 流水线（至少包含 SAST / SCA / 镜像扫描 / DAST 四个阶段），并配置质量门禁。
5. 用 OWASP Threat Dragon 对一个系统（如电商 / 博客）做完整的威胁建模，输出威胁建模报告。
6. 对一个 API 应用进行完整的安全测试，覆盖 OWASP API Top 10 的主要风险项，输出 API 安全测试报告。
7. 为一个项目生成 SBOM，并扫描 SBOM 中的漏洞，输出供应链安全报告。
8. 配置 Git 预提交钩子（pre-commit hook），实现提交前自动密钥检测和代码安全检查。
9. 用 CodeQL 查询一个代码仓库，找出其中的安全漏洞（如 SQL 注入、XSS 等）。
10. 模拟一次供应链攻击（如依赖混淆攻击），然后说明防御方法并实际部署防护措施。

### 10.3 阶段产出物清单

完成本模块后，你应该拥有以下产出物：

- [ ] **安全编码**
  - [ ] 安全编码规范文档（自己的语言栈）
  - [ ] OWASP Top 10 防御代码示例库
  - [ ] 安全重构项目（漏洞修复前后对比）
  - [ ] 常见漏洞修复 Cheat Sheet
- [ ] **代码审计**
  - [ ] 代码审计报告（3 份以上）
  - [ ] Semgrep 自定义规则集（20+ 条）
  - [ ] 危险函数速查表（各语言）
  - [ ] 代码审计方法论笔记
- [ ] **API 安全**
  - [ ] API 安全测试报告（2 份以上）
  - [ ] OWASP API Top 10 详解 + 防御代码
  - [ ] JWT 安全最佳实践
  - [ ] API 安全测试 Playbook
- [ ] **DevSecOps**
  - [ ] 完整的 DevSecOps 流水线项目
  - [ ] CI/CD 安全检查清单
  - [ ] 质量门禁配置
  - [ ] 流水线即代码（Pipeline as Code）
- [ ] **供应链安全**
  - [ ] SBOM 生成与管理实践
  - [ ] 供应链安全评估报告
  - [ ] 依赖更新策略与自动化
  - [ ] 镜像签名与验证实践
- [ ] **威胁建模与设计**
  - [ ] 威胁建模报告（2 份以上）
  - [ ] STRIDE / DREAD 模板
  - [ ] 攻击树示例
  - [ ] 安全设计原则手册
- [ ] **工具与自动化**
  - [ ] 自研安全工具（至少 1 个有价值的项目）
  - [ ] 安全自动化脚本集合
  - [ ] 安全工具集成方案
- [ ] **知识输出**
  - [ ] 安全开发技术博客 15+ 篇
  - [ ] GitHub 安全项目获得 Star
  - [ ] 提交过的漏洞 / PR（开源项目）

---

> **下一步建议**：完成 M9 后，你已经具备了安全开发的全流程能力。接下来：
> - 想做安全架构 → 继续深入研究零信任、云原生安全架构
> - - 想就业 → 进入 **M10 认证与就业**，准备 OSWE / CSSLP 等安全开发相关认证
> - 想做红队 → 回到 **M5 渗透测试与红队**，用代码审计能力挖 0day
> - 想做云安全 → 回到 **M8 云原生安全**，深化 DevSecOps 在云原生环境的落地
