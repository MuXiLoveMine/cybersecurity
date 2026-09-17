# Linux日志

### 3.1 auth.log分析

```bash
# 查看认证日志
cat /var/log/auth.log

# SSH暴力破解检测
grep "Failed password" /var/log/auth.log | \
    awk '{print $(NF-3)}' | \
    sort | uniq -c | sort -rn | head -20

# 成功SSH登录
grep "Accepted" /var/log/auth.log

# 检测sudo使用
grep "sudo" /var/log/auth.log

# 检测新用户创建
grep "useradd" /var/log/auth.log

# 检测密码修改
grep "passwd" /var/log/auth.log

# 检测用户切换
grep "su:" /var/log/auth.log
```

### 3.2 syslog分析

```bash
# 查看系统日志
cat /var/log/syslog

# 检测服务异常
grep -i "fail\|error\|critical" /var/log/syslog | tail -50

# 检测内核模块加载(rootkit)
grep "module" /var/log/syslog

# 检测cron任务执行
grep CRON /var/log/syslog
```

### 3.3 auditd审计

```bash
# 安装和配置auditd
apt install auditd

# 审计规则
# /etc/audit/audit.rules

# 监控关键文件
-a always,exit -F path=/etc/passwd -F perm=wa -k identity
-a always,exit -F path=/etc/shadow -F perm=wa -k identity
-a always,exit -F path=/etc/sudoers -F perm=wa -k identity

# 监控命令执行
-a always,exit -F arch=b64 -S execve -k cmd_exec

# 查看审计日志
ausearch -k identity  # 查看标识文件访问
ausearch -k cmd_exec  # 查看命令执行
ausearch -m USER_LOGIN -sv no  # 查看登录失败

# 实时监控
tail -f /var/log/audit/audit.log
```

---

---

## 📋 内容审核与补充建议

> 针对「Linux日志」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

### ⚔️ 攻击技术
- ⚠️ 缺少attack相关内容

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
