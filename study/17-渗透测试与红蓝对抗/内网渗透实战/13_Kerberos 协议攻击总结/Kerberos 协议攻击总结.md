# Kerberos 协议攻击总结

| 攻击名称 | 攻击阶段 | 所需条件 | 效果 |
|---------|---------|---------|------|
| AS-REP Roasting | AS 阶段 | 用户不需要预认证 | 离线破解用户密码 |
| Kerberoasting | TGS 阶段 | 任何域用户 | 离线破解服务账户密码 |
| Golden Ticket | 票据伪造 | krbtgt Hash | 伪造任意用户 TGT |
| Silver Ticket | 票据伪造 | 服务账户 Hash | 伪造特定服务 TGS |
| Pass the Key | AS 阶段 | 用户 AES Key | 获取 TGT |
| Overpass the Hash | AS 阶段 | NTLM Hash | 获取 TGT |
| DCSync | 模拟复制 | DS-Replication 权限 | 导出所有用户 Hash |
| ZeroLogon | Netlogon | 网络可达域控 | 置空域控密码 |

---

---

## 🚀 实战拓展

### 💻 常用工具
Nmap、Burp Suite、Wireshark、Metasploit、sqlmap、Python

### ⌨️ 关键命令
常用Linux命令、网络工具命令、脚本语言基础

### 🎯 练习建议
靶场练习、CTF比赛、SRC漏洞挖掘、自建实验环境

### 🛡️ 防御要点
安全意识、最小权限、纵深防御、持续监控、定期审计

### 📖 延伸阅读
相关技术文档、官方指南、安全博客、技术社区

---

