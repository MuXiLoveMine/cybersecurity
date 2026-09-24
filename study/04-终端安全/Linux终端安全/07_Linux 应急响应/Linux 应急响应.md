# Linux 应急响应

### 7.1 应急响应准备

**工具准备**

| 类别 | 工具 | 用途 |
|------|------|------|
| 进程分析 | ps、top、htop、lsof、pstree | 进程查看和分析 |
| 网络分析 | netstat、ss、tcpdump、wireshark | 网络连接和流量分析 |
| 文件分析 | file、strings、md5sum、sha256sum | 文件分析和哈希计算 |
| 日志分析 | grep、awk、sed、journalctl | 日志分析 |
| 内存取证 | LiME、Volatility | 内存镜像和分析 |
| 磁盘取证 | dd、FTK Imager、Autopsy | 磁盘镜像和分析 |
| Rootkit 检测 | rkhunter、chkrootkit | Rootkit 检测 |
| 完整性检查 | rpm、dpkg、AIDE | 文件完整性检查 |

### 7.2 事件确认

**常见入侵迹象**

1. **系统异常**：系统变慢、CPU/内存使用率异常、未知进程
2. **网络异常**：异常出站连接、大量流量、未知端口监听
3. **文件异常**：未知文件、文件被篡改、勒索信息
4. **账户异常**：未知账户、异常登录、密码被改
5. **服务异常**：未知服务、服务异常重启
6. **安全告警**：IDS/IPS、HIDS、WAF 告警

**初步信息收集**

```bash
# 系统基本信息
uname -a
cat /etc/os-release
hostname
date

# 当前登录用户
who
w
last
lastb

# 网络连接
netstat -tulnp
ss -tuanp

# 进程列表
ps auxf
ps -ef

# 服务列表
systemctl list-units --type=service --state=running
service --status-all

# 计划任务
crontab -l
ls -la /etc/cron.d/
ls -la /etc/cron.hourly/
ls -la /etc/cron.daily/

# 用户列表
cat /etc/passwd
cat /etc/shadow
```

### 7.3 证据保全

**易失性数据收集**

按照从易失到不易失的顺序收集证据：

```bash
# 1. 网络连接和状态
netstat -tulnp > /evidence/netstat.txt
ss -tuanp > /evidence/ss.txt
arp -a > /evidence/arp.txt
route -n > /evidence/route.txt
iptables -L -n -v > /evidence/iptables.txt

# 2. 进程信息
ps auxf > /evidence/ps.txt
pstree -p > /evidence/pstree.txt
lsof > /evidence/lsof.txt

# 3. 内存镜像
# 使用 LiME (Linux Memory Extractor)
insmod lime.ko "path=/evidence/memory.raw format=raw"
# 或使用 AVML (Azure VM Memory Acquisition)
./avml /evidence/memory.raw

# 4. 文件系统
# 记录文件元数据
find / -type f -exec ls -la {} \; > /evidence/files.txt  # 不推荐，太慢
# 更好的方法：重点目录
ls -laR /etc > /evidence/etc_ls.txt
ls -laR /tmp > /evidence/tmp_ls.txt
ls -laR /var > /evidence/var_ls.txt  # 根据需要选择

# 5. 日志
cp -r /var/log /evidence/logs/
journalctl --no-pager > /evidence/journalctl.log
```

**磁盘镜像**

```bash
# 使用 dd 创建磁盘镜像
dd if=/dev/sda of=/evidence/disk.dd bs=4096 conv=noerror,sync status=progress

# 使用 dc3dd（增强版 dd，带哈希计算）
dc3dd if=/dev/sda of=/evidence/disk.dd hash=sha256 log=/evidence/dc3dd.log

# 使用 FTK Imager（GUI 工具）
```

### 7.4 入侵分析

**账户分析**

```bash
# 查看所有用户
cat /etc/passwd
cat /etc/shadow

# 查看 UID 为 0 的用户（root 权限）
awk -F: '($3 == 0) {print $1}' /etc/passwd

# 查看最近登录
last
lastb  # 失败的登录
lastlog

# 查看 sudo 日志
grep sudo /var/log/auth.log
grep sudo /var/log/secure

# 检查可疑账户
# 1. 没有家目录的用户
awk -F: '{ if ($6 == "") print $0 }' /etc/passwd

# 2. 可登录的系统账户（UID < 1000 但 shell 可登录）
awk -F: '($3 < 1000 && $7 !~ /nologin|false|sync|shutdown|halt/) {print $1, $3, $7}' /etc/passwd
```

**进程分析**

```bash
# 1. 查看所有进程
ps auxf
ps -efH

# 2. 查看 CPU/内存占用最高的进程
top -b -n 1 | head -20
ps aux --sort=-%cpu | head -10
ps aux --sort=-%mem | head -10

# 3. 查看进程打开的文件
lsof -p <pid>
lsof | grep -i deleted  # 已删除但仍在运行的文件（可疑）

# 4. 查看进程的可执行文件路径
ls -la /proc/<pid>/exe
readlink /proc/<pid>/exe

# 5. 查看进程的命令行
cat /proc/<pid>/cmdline | tr '\0' ' '
echo

# 6. 查看进程的环境变量
cat /proc/<pid>/environ | tr '\0' '\n'

# 7. 检查隐藏进程
# 对比 ps 输出和 /proc 目录
```

**网络分析**

```bash
# 1. 查看所有网络连接
netstat -tulnp
ss -tuanp
lsof -i -P -n

# 2. 查看监听端口
netstat -tulnp | grep LISTEN
ss -tlnp

# 3. 查看已建立的连接
netstat -tanp | grep ESTABLISHED
ss -tanp | grep ESTAB

# 4. 抓包分析
tcpdump -i eth0 -w /evidence/capture.pcap -s 0
tcpdump -i eth0 -n -c 100  # 实时查看 100 个包

# 5. 检查可疑连接
# 连接到已知恶意 IP 的连接
# 连接到非标准端口的连接
# 大量出站连接（可能是 C2 或扫描）
```

**文件分析**

```bash
# 1. 查找最近修改的文件
find / -mtime -1 -type f 2>/dev/null  # 最近 1 天
find / -mmin -60 -type f 2>/dev/null  # 最近 60 分钟

# 2. 查找隐藏文件
find / -name ".*" -type f 2>/dev/null
find /tmp -name ".*" -type f 2>/dev/null

# 3. 查找 SUID/SGID 文件
find / -perm -4000 -type f 2>/dev/null
find / -perm -2000 -type f 2>/dev/null

# 4. 查找无属主文件
find / -nouser -o -nogroup 2>/dev/null

# 5. 计算文件哈希
md5sum /path/to/file
sha256sum /path/to/file

# 6. 查看文件字符串
strings /path/to/file | head -50

# 7. 检查系统文件完整性
rpm -Va  # CentOS/RHEL
dpkg -V  # Debian/Ubuntu
```

**日志分析**

```bash
# 认证日志
tail -100 /var/log/auth.log  # Debian/Ubuntu
tail -100 /var/log/secure    # CentOS/RHEL

# 系统日志
tail -100 /var/log/syslog    # Debian/Ubuntu
tail -100 /var/log/messages  # CentOS/RHEL

# 系统 journal
journalctl -u sshd --since "2024-09-01" --until "2024-09-11"
journalctl -p err..alert --since yesterday

# 登录失败日志
grep "Failed password" /var/log/auth.log
grep "authentication failure" /var/log/auth.log
lastb

# sudo 日志
grep "sudo" /var/log/auth.log
grep "COMMAND=" /var/log/auth.log

# 防火墙日志
grep -i "iptables\|firewall\|ufw" /var/log/syslog
grep -i "iptables\|firewalld" /var/log/messages

# 审计日志
ausearch -m avc -ts today
ausearch -k time_change -ts today
```

### 7.5 遏制与根除

**遏制措施**

1. **网络隔离**：断开受感染主机的网络连接
   ```bash
   # 禁用网络接口
   ifdown eth0
   ip link set eth0 down
   # 或使用防火墙阻断所有入站/出站
   iptables -P INPUT DROP
   iptables -P OUTPUT DROP
   iptables -F
   ```

2. **账户禁用**：禁用被攻陷的账户
   ```bash
   passwd -l username  # 锁定账户
   usermod -s /sbin/nologin username  # 修改 shell
   ```

3. **终止恶意进程**
   ```bash
   kill <pid>
   kill -9 <pid>  # 强制终止
   pkill process_name
   killall process_name
   ```

4. **停止恶意服务**
   ```bash
   systemctl stop malicious.service
   service malicious stop
   ```

**根除措施**

1. **删除恶意文件**
2. **清理持久化机制**（cron、服务、SSH 密钥等）
3. **恢复被篡改的系统文件**
4. **重置所有凭据**（密码、密钥、token 等）
5. **修复被利用的漏洞**

### 7.6 恢复与总结

**恢复步骤**

1. 从干净备份恢复系统（优先选择）
2. 或在确认清除恶意代码后重新接入网络
3. 加强监控，观察是否有复发迹象
4. 修复被利用的漏洞和弱点

**事件报告**

```
应急响应报告应包含：
1. 事件概述：时间、影响范围、严重程度
2. 入侵路径：攻击者是如何进入的
3. 攻击链：攻击者做了什么（时间线）
4. 影响评估：数据泄露、系统破坏、业务影响
5. 处置措施：采取了哪些遏制和根除措施
6. IOC 指标：IP、域名、文件哈希、进程名等
7. 改进建议：如何防止类似事件再次发生
```

---

---

