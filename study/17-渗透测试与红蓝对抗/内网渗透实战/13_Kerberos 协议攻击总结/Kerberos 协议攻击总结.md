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

## 📋 内容审核与补充建议

> 针对「Kerberos 协议攻击总结」部分的内容审核结果：

### 💻 代码示例
- ⚠️ 缺少code相关内容

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

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
