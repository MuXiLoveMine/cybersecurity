# MITRE ATT&CK 框架

### 2.1 ATT&CK 概述

**ATT&CK 定义**
- MITRE ATT&CK 是一个全球可访问的对抗性战术和技术知识库
- 基于真实观察到的攻击行为
- 包含战术（Tactics）、技术（Techniques）、程序（Procedures）

**ATT&CK 矩阵**
```
1. 侦察 (Reconnaissance)
2. 资源开发 (Resource Development)
3. 初始访问 (Initial Access)
4. 执行 (Execution)
5. 持久化 (Persistence)
6. 权限提升 (Privilege Escalation)
7. 防御绕过 (Defense Evasion)
8. 凭据访问 (Credential Access)
9. 发现 (Discovery)
10. 横向移动 (Lateral Movement)
11. 收集 (Collection)
12. 命令与控制 (Command and Control)
13. 数据外传 (Exfiltration)
14. 影响 (Impact)
```

### 2.2 ATT&CK 在红蓝对抗中的应用

**红队使用 ATT&CK**
- 攻击链设计：选择 ATT&CK 技术点组成攻击链
- TTPs 映射：将攻击行为映射到 ATT&CK 技术
- 覆盖率评估：评估攻击技术多样性

**蓝队使用 ATT&CK**
- 检测覆盖评估：评估每项 ATT&CK 技术的检测能力
- 规则开发：基于 ATT&CK 技术开发检测规则
- 威胁狩猎：基于 ATT&CK 框架进行威胁狩猎
- 差距分析：发现检测覆盖缺口

---

---

