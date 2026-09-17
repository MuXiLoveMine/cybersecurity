# Linux 主机取证

### 3.1 /proc 文件系统

```
/proc 取证关键文件:

/proc/[pid]/              # 进程信息目录
├── cmdline               # 进程命令行参数
├── environ               # 进程环境变量
├── maps                  # 进程内存映射（检测注入）
├── fd/                   # 文件描述符
├── exe                   # 可执行文件链接
├── status                # 进程状态
├── net/tcp               # TCP连接
├── net/tcp6              # IPv6 TCP连接
└── net/udp               # UDP连接

# 关键系统文件
/proc/loadavg             # 系统负载
/proc/meminfo             # 内存信息
/proc/mounts              # 挂载信息
/proc/net/arp             # ARP表
/proc/net/route           # 路由表
/proc/version             # 内核版本
```

```bash
# Linux 取证采集脚本

# 1. 采集进程信息（包含隐藏进程检测）
echo "=== 进程列表 ==="
ps auxww
echo "=== /proc 进程目录数（检测隐藏进程）==="
ls -d /proc/[0-9]* | wc -l
# 如果 ps 显示的进程数 < /proc 目录数，可能有隐藏进程

# 2. 采集网络连接
echo "=== 网络连接 ==="
ss -tunap
echo "=== 网络接口 ==="
ip addr
echo "=== 路由表 ==="
ip route
echo "=== ARP 表 ==="
arp -a 2>/dev/null || ip neigh

# 3. 采集登录信息
echo "=== 当前登录用户 ==="
w
echo "=== 登录历史 ==="
last -F
echo "=== 失败登录 ==="
lastb -F 2>/dev/null || echo "需root权限"

# 4. 采集计划任务
echo "=== 系统cron ==="
cat /etc/crontab
ls -la /etc/cron.*/
for dir in /etc/cron.*/; do
    echo "--- $dir ---"
    cat "$dir"*
done 2>/dev/null
echo "=== 用户cron ==="
for user in $(cut -d: -f1 /etc/passwd); do
    crontab -l -u "$user" 2>/dev/null && echo "  (用户: $user)"
done
echo "=== at 队列 ==="
atq 2>/dev/null

# 5. 采集自启动项
echo "=== systemd 服务 ==="
systemctl list-units --type=service --state=running
echo "=== systemd 服务文件 ==="
ls -la /etc/systemd/system/*.service
ls -la /lib/systemd/system/*.service
echo "=== rc.local ==="
cat /etc/rc.local 2>/dev/null
echo "=== init.d ==="
ls -la /etc/init.d/
echo "=== profile ==="
cat /etc/profile
cat /etc/bash.bashrc
```

### 3.2 审计日志

```bash
# Linux 关键日志文件
# /var/log/auth.log    - 认证日志（Debian/Ubuntu）
# /var/log/secure      - 认证日志（RHEL/CentOS）
# /var/log/syslog      - 系统日志（Debian/Ubuntu）
# /var/log/messages    - 系统日志（RHEL/CentOS）
# /var/log/audit/      - auditd 审计日志
# /var/log/wtmp        - 登录成功记录（二进制）
# /var/log/btmp        - 登录失败记录（二进制）
# /var/log/lastlog     - 最后登录记录
# ~/.bash_history      - 用户命令历史
# ~/.ssh/authorized_keys  - SSH 授权密钥

# 审计日志分析
# 查找用户创建/删除
ausearch -m ADD_USER,DEL_USER -ts today

# 查找 sudo 执行
ausearch -m USER_CMD -k sudo 2>/dev/null
grep -i "sudo" /var/log/auth.log

# 查找 SSH 登录
grep "sshd" /var/log/auth.log | grep -v "Accepted\|Failed"
grep "Accepted\|Failed" /var/log/auth.log | grep sshd

# 分析 bash 历史记录
for user_home in /home/*; do
    user=$(basename "$user_home")
    echo "=== $user bash_history ==="
    cat "$user_home/.bash_history" 2>/dev/null
done

# 检查 SSH 后门（authorized_keys 中的异常密钥）
for user_home in /root /home/*; do
    echo "=== $user_home authorized_keys ==="
    cat "$user_home/.ssh/authorized_keys" 2>/dev/null
done
```

### 3.3 文件时间线分析

```bash
# 创建文件系统时间线

# 使用 fls (The Sleuth Kit) 提取文件元数据
# 需要有磁盘镜像文件

# 从磁盘镜像创建 body 文件
fls -r -m / disk_image.dd > timeline.body

# 添加已删除文件
fls -r -d -m / disk_image.dd >> timeline.body

# 使用 mactime 生成时间线
mactime -b timeline.body -d > timeline.csv

# 时间线输出格式:
# Date,Size,UID,GID,Mode,File
# 2026-09-10T14:32:00,12345,0,0,r/rr-xr-x,/etc/crontab
# 2026-09-10T14:33:00,5678,0,0,r/rr-xr-x,/tmp/malware.sh
```

```python
# Python 文件时间线异常检测
import os
from datetime import datetime, timedelta

def detect_timeline_anomalies(timeline_csv):
    """
    检测文件时间线中的可疑模式
    """
    anomalies = []
    
    with open(timeline_csv) as f:
        for line in f:
            parts = line.strip().split(',')
            if len(parts) < 6:
                continue
            
            timestamp_str = parts[0]
            filepath = parts[5]
            
            # 异常1: 临时目录中的可执行文件
            if '/tmp/' in filepath and filepath.endswith(('.sh', '.py', '.elf')):
                anomalies.append(f"[临时目录可执行文件] {timestamp_str} {filepath}")
            
            # 异常2: 非工作时间的大量文件修改
            try:
                ts = datetime.fromisoformat(timestamp_str)
                if ts.hour < 6 or ts.hour > 23:
                    if '/etc/' in filepath:
                        anomalies.append(f"[非工作时间修改系统文件] {timestamp_str} {filepath}")
            except:
                pass
            
            # 异常3: timestomp 检测（修改时间 < 创建时间）
            # 需要对比 MACE 时间戳
    
    return anomalies
```

---

---

## 📋 内容审核与补充建议

> 针对「Linux 主机取证」部分的内容审核结果：

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
