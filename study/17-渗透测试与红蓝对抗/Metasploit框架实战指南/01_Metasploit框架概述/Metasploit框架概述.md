# Metasploit框架概述

### 1.1 MSF架构

Metasploit 采用模块化架构，各组件协同工作形成完整的渗透测试流程：

```
Metasploit 架构:
├── 模块（Modules）       → 核心，各种漏洞利用和功能实现
├── 插件（Plugins）       → 扩展功能（如 Nessus/OpenVAS 集成）
├── 接口（Interfaces）    → msfconsole / msfweb / msf rpc
├── 工具集（Tools）       → msfvenom / msfdb / msfrpc
├── 数据库（Database）    → PostgreSQL 存储工作区/主机/凭据
└── 库（Libraries）      → Rex（基础库）/ Msf::Core / Msf::Base
```

### 1.2 模块类型详解

| 模块类型 | 路径前缀 | 功能说明 |
|----------|----------|----------|
| exploit | exploit/ | 漏洞利用模块，组合漏洞利用代码和载荷 |
| auxiliary | auxiliary/ | 辅助模块，扫描/嗅探/Fuzz/信息收集 |
| post | post/ | 后渗透模块，已获取 Shell 后的操作 |
| payload | payload/ | 载荷模块，执行在目标上的代码（Shellcode） |
| encoder | encoder/ | 编码器，对载荷编码以规避检测 |
| evasion | evasion/ | 规避模块，生成绕过杀软的载荷 |
| nop | nop/ | NOP 空指令生成器，填充载荷保持稳定性 |

### 1.3 环境配置与更新

```bash
# Kali Linux 中 MSF 已预装，更新方式:
apt update && apt install metasploit-framework

# 初始化数据库:
msfdb init

# 启动 MSF 并连接数据库:
msfconsole
msf6 > db_status    # 检查数据库连接

# 常用配置:
# ~/.msf4/ 目录下存放用户配置
# /usr/share/metasploit-framework/ 为安装目录
```

---

---

