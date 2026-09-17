# OWASP Testing Guide v4.2 详解

### 7.1 OWASP WSTG 分类体系

OWASP Web Security Testing Guide v4.2 将测试分为以下类别：

```
WSTG 分类（OTG = OWASP Testing Guide）：

OTG-INFO: 信息收集与侦察
  OTG-INFO-01: 搜索引擎信息收集
  OTG-INFO-02: Web 服务器指纹识别
  OTG-INFO-03: 应用程序技术栈识别
  OTG-INFO-04: 错误页面分析
  OTG-INFO-05: 应用入口点映射
  OTG-INFO-06: 应用执行路径映射
  OTG-INFO-07: 应用架构映射
  OTG-INFO-08: 指纹识别 Web 应用框架
  OTG-INFO-09: 指纹识别 Web 应用程序
  OTG-INFO-10: 测试 Google Hacking

OTG-CONF: 配置与部署管理测试
  OTG-CONF-01: 网络基础设施配置
  OTG-CONF-02: 应用平台配置
  OTG-CONF-03: 文件扩展名处理
  OTG-CONF-04: 旧备份和引用文件
  OTG-CONF-05: 管理接口
  OTG-CONF-06: HTTP 方法
  OTG-CONF-07: HSTS
  OTG-CONF-08: RIA 策略文件
  OTG-CONF-09: CORS

OTG-IDNT: 身份认证测试
  OTG-IDNT-01: 凭据传输加密
  OTG-IDNT-02: 默认凭据
  OTG-IDNT-03: 弱锁定机制
  OTG-IDNT-04: 绕过认证
  OTG-IDNT-05: 弱密码策略
  OTG-IDNT-06: 弱安全问答

OTG-ATHN: 授权测试
  OTG-ATHN-01: 路径遍历
  OTG-ATHN-02: 越权访问

OTG-SESS: 会话管理测试
  OTG-SESS-01: 会话管理架构
  OTG-SESS-02: Cookie 属性
  OTG-SESS-03: 会话固定
  OTG-SESS-04: 会话变量暴露
  OTG-SESS-05: CSRF
  OTG-SESS-06: 注销功能

OTG-INPV: 输入验证测试
  OTG-INPV-01: 反射型 XSS
  OTG-INPV-02: 存储型 XSS
  OTG-INPV-03: DOM 型 XSS
  OTG-INPV-04: SQL 注入
  OTG-INPV-05: ORM 注入
  OTG-INPV-06: 代码注入
  OTG-INPV-07: 命令注入
  OTG-INPV-08: 缓冲区溢出
  OTG-INPV-09: 堆栈溢出
  OTG-INPV-10: 整数溢出
  OTG-INPV-11: LFI/RFI
  OTG-INPV-12: XXE
  OTG-INPV-13: SSRF
  OTG-INPV-14: HTTP 请求走私
  OTG-INPV-15: HTTP 分割

OTG-ERRH: 错误处理测试
  OTG-ERRH-01: 错误处理
  OTG-ERRH-02: 堆栈追踪
```

### 7.2 OWASP 测试执行清单

```
针对每个测试类别，执行清单：

[ ] 信息收集：被动/主动信息收集
[ ] 配置管理：服务器配置、管理接口、备份文件
[ ] 认证：弱密码、锁定机制、会话固定
[ ] 授权：水平/垂直越权
[ ] 会话：Cookie 安全、CSRF
[ ] 输入验证：XSS、SQLi、RCE、LFI、XXE、SSRF
[ ] 业务逻辑：价格篡改、竞态条件、工作流绕过
[ ] 客户端：DOM XSS、点击劫持、CORS
[ ] API：认证、授权、限流、注入
```

---

---

## 📋 内容审核与补充建议

> 针对「OWASP Testing Guide v4.2 详解」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

### ⚔️ 攻击技术
- ⚠️ 缺少attack相关内容

---

## 📌 拓展学习资源

### 推荐学习路径
- 理论基础 → 工具实践 → 实战演练 → 深度研究
- 建议搭建本地实验环境进行动手练习

### 相关工具与资源
- 在线实验平台：Hack The Box、TryHackMe、VulnHub
- 技术文档：官方文档、RFC、OWASP 指南
- 社区资源：GitHub、安全论坛、技术博客
