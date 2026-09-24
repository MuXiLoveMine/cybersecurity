# Linux 入侵排查

### 3.1 排查思路

Linux 入侵排查与 Windows 类似，但工具和方法有所不同。

**排查思路：**
1. 整体状态检查（系统资源、进程、网络）
2. 用户和权限检查
3. 历史命令和日志检查
4. 持久化机制检查（计划任务、服务、启动项）
5. 文件系统检查（Webshell、后门、Rootkit）
6. 深入分析和取证

### 3.2 进程排查

#### 3.2.1 查看进程

```bash
# 查看所有进程
ps aux
ps -ef

# 按 CPU 排序
ps aux --sort=-%cpu | head -20

# 按内存排序
ps aux --sort=-%rss | head -20

# 查看进程树
pstree -p

# 实时监控进程
top
htop
```

#### 3.2.2 排查可疑进程

**异常特征：**
- CPU/内存占用异常高（可能是挖矿程序）
- 进程名可疑（随机字符串、伪装系统进程）
- 进程路径异常（/tmp、/dev/shm、/var/tmp 等）
- 进程的父进程异常
- 隐藏进程（ps 看不到但 top 能看到，或反之）

```bash
# 查看进程的可执行文件路径
ls -la /proc/PID/exe

# 查看进程的命令行参数
cat /proc/PID/cmdline | tr '\0' ' '

# 查看进程打开的文件
ls -la /proc/PID/fd/

# 查看进程的环境变量
cat /proc/PID/environ | tr '\0' '\n'

# 查看进程的当前工作目录
ls -la /proc/PID/cwd

# 查看进程的内存映射
cat /proc/PID/maps
```

#### 3.2.3 隐藏进程检测

```bash
# 对比 ps 和 /proc 目录的进程
ps -e | awk '{print $1}' | sort -n > /tmp/ps.txt
ls /proc | grep -E '^[0-9]+$' | sort -n > /tmp/proc.txt
diff /tmp/ps.txt /tmp/proc.txt

# 使用 unhide 工具检测隐藏进程
unhide proc
unhide sys
unhide brute
```

### 3.3 网络连接排查

#### 3.3.1 查看网络连接

```bash
# 查看所有网络连接和监听端口
netstat -tulnp
ss -tulnp

# 查看所有连接（包括 TIME_WAIT 等）
netstat -an
ss -an

# 查看建立的连接
netstat -an | grep ESTABLISHED
ss -an | grep ESTAB

# 查看 UDP 连接
netstat -ulnp
ss -ulnp

# 查看 Unix 域套接字
netstat -x
ss -x
```

#### 3.3.2 查看进程与端口对应关系

```bash
# 查看指定端口的进程
lsof -i :22
lsof -i :80
lsof -i :443

# 查看指定进程的网络连接
lsof -p PID -i

# 查看所有网络连接（带进程）
lsof -i
```

#### 3.3.3 网络流量监控

```bash
# 实时网络流量监控
iftop
nload
vnstat

# 抓包分析
tcpdump -i eth0 -w /tmp/capture.pcap
tcpdump -i eth0 port 80 -w /tmp/http.pcap
```

#### 3.3.4 可疑网络连接特征

- 连接到境外 IP 的进程
- 连接到高位随机端口
- 异常的对外连接（特别是到 445、139、22 等端口的横向移动）
- 非标准端口的监听
- 系统进程的异常网络连接

### 3.4 用户排查

#### 3.4.1 查看用户

```bash
# 查看所有用户
cat /etc/passwd

# 查看可登录的用户
grep -E "(/bin/bash|/bin/sh|/bin/zsh)" /etc/passwd

# 查看 UID 为 0 的用户（root 权限）
awk -F: '$3==0 {print $1}' /etc/passwd

# 查看最近登录的用户
last
last -a
last -f /var/log/wtmp

# 查看登录失败记录
lastb
lastb -f /var/log/btmp

# 查看当前登录用户
who
w
users
```

#### 3.4.2 排查可疑用户

- UID 为 0 的非 root 用户
- 陌生的用户账号
- 用户 shell 为可交互 shell 的系统用户
- 最近新增的用户
- 用户家目录中有可疑文件

```bash
# 查看 /etc/passwd 文件修改时间
ls -la /etc/passwd

# 查看用户组
cat /etc/group
cat /etc/gshadow

# 查看 sudo 权限用户
cat /etc/sudoers
ls -la /etc/sudoers.d/
```

### 3.5 日志排查

#### 3.5.1 常见日志文件

| 日志文件 | 说明 |
|----------|------|
| `/var/log/messages` | 系统日志（通用） |
| `/var/log/syslog` | 系统日志（Debian/Ubuntu） |
| `/var/log/secure` | 安全日志（CentOS/RHEL） |
| `/var/log/auth.log` | 认证日志（Debian/Ubuntu） |
| `/var/log/cron` | 计划任务日志 |
| `/var/log/maillog` | 邮件日志 |
| `/var/log/kern.log` | 内核日志 |
| `/var/log/btmp` | 登录失败记录（二进制） |
| `/var/log/wtmp` | 登录记录（二进制） |
| `/var/log/utmp` | 当前登录用户（二进制） |
| `/var/log/nginx/` | Nginx 日志 |
| `/var/log/apache2/` | Apache 日志 |
| `/var/log/httpd/` | HTTPD 日志 |
| `/var/log/audit/audit.log` | 审计日志 |

#### 3.5.2 登录日志分析

```bash
# 查看登录成功记录
last
last | head -50

# 查看登录失败记录
lastb
lastb | head -50

# 查看登录失败的 IP 统计
lastb | awk '{print $3}' | sort | uniq -c | sort -rn | head -20

# 查看 SSH 登录日志
grep "Accepted" /var/log/secure
grep "Failed" /var/log/secure
grep "sshd" /var/log/auth.log

# 查看暴力破解尝试
grep "Failed password" /var/log/secure | awk '{print $11}' | sort | uniq -c | sort -rn | head -20
```

#### 3.5.3 命令历史分析

```bash
# 查看当前用户的命令历史
history
cat ~/.bash_history

# 查看所有用户的命令历史
cat /home/*/.bash_history
cat /root/.bash_history

# 查看最近执行的命令
grep -E "(rm|wget|curl|chmod|chown|passwd|useradd)" ~/.bash_history
```

**注意：**
- 攻击者可能会清除命令历史
- 可以通过 `HISTFILE` 环境变量查看历史文件位置
- 可以检查 `~/.bash_logout` 是否有清除历史的命令

#### 3.5.4 sudo 日志分析

```bash
# 查看 sudo 操作记录
grep "sudo" /var/log/secure
grep "sudo" /var/log/auth.log

# 查看 sudo 失败记录
grep "NOT in sudoers" /var/log/secure
```

### 3.6 计划任务排查

#### 3.6.1 查看计划任务

```bash
# 查看当前用户的 crontab
crontab -l

# 查看所有用户的 crontab
ls -la /var/spool/cron/
ls -la /var/spool/cron/crontabs/

# 查看系统级计划任务
cat /etc/crontab
ls -la /etc/cron.d/
ls -la /etc/cron.daily/
ls -la /etc/cron.hourly/
ls -la /etc/cron.weekly/
ls -la /etc/cron.monthly/
```

#### 3.6.2 排查重点

- 可疑的计划任务（执行恶意脚本或命令）
- 未知用户的 crontab
- 计划任务执行的脚本路径异常
- 计划任务中包含反弹 shell、下载执行等恶意命令

```bash
# 查找所有 crontab 中的可疑内容
grep -rE "(wget|curl|bash|nc|python|perl|ruby)" /var/spool/cron/
grep -rE "(wget|curl|bash|nc|python|perl|ruby)" /etc/cron*
```

### 3.7 服务与自启动排查

#### 3.7.1 Systemd 服务

```bash
# 查看所有服务
systemctl list-unit-files --type=service

# 查看运行中的服务
systemctl list-units --type=service --state=running

# 查看服务详情
systemctl status 服务名
cat /etc/systemd/system/服务名.service
cat /usr/lib/systemd/system/服务名.service

# 查看服务启动的命令
systemctl show -p ExecStart 服务名
```

#### 3.7.2 init.d 服务

```bash
# 查看 init.d 服务
ls -la /etc/init.d/

# 查看各运行级别的服务
ls -la /etc/rc.d/
ls -la /etc/rc3.d/
ls -la /etc/rc5.d/
```

#### 3.7.3 其他自启动位置

```bash
# rc.local
cat /etc/rc.local
cat /etc/rc.d/rc.local

# 环境变量配置文件
cat /etc/profile
cat /etc/bashrc
cat ~/.bashrc
cat ~/.bash_profile
cat ~/.profile

# SSH 配置和密钥
cat /etc/ssh/sshd_config
ls -la ~/.ssh/
cat ~/.ssh/authorized_keys
```

### 3.8 文件系统排查

#### 3.8.1 最近修改的文件

```bash
# 查找最近 24 小时修改的文件
find / -mtime -1 -type f 2>/dev/null

# 查找最近 1 小时修改的文件
find / -mmin -60 -type f 2>/dev/null

# 查找最近 7 天新增的可执行文件
find / -mtime -7 -name "*.sh" -type f 2>/dev/null
find / -mtime -7 -perm -u+x -type f 2>/dev/null

# 查找 SETUID/SETGID 文件（可能是提权工具）
find / -perm -4000 -type f 2>/dev/null
find / -perm -2000 -type f 2>/dev/null
```

#### 3.8.2 临时目录排查

```bash
# 检查 /tmp 目录
ls -la /tmp/
find /tmp -type f -executable 2>/dev/null

# 检查 /dev/shm 目录（内存文件系统，重启后消失）
ls -la /dev/shm/

# 检查 /var/tmp 目录
ls -la /var/tmp/
```

#### 3.8.3 Webshell 检测

```bash
# 查找 PHP Webshell 特征
grep -r "eval(" /var/www/html/ --include="*.php" 2>/dev/null
grep -r "assert(" /var/www/html/ --include="*.php" 2>/dev/null
grep -r "base64_decode" /var/www/html/ --include="*.php" 2>/dev/null
grep -r "system(" /var/www/html/ --include="*.php" 2>/dev/null
grep -r "shell_exec" /var/www/html/ --include="*.php" 2>/dev/null

# 查找 JSP Webshell 特征
grep -r "Runtime.getRuntime()" /var/www/html/ --include="*.jsp" 2>/dev/null

# 查找一句话木马
grep -rE "eval\s*\(\s*(\$_POST|\$_GET|\$_REQUEST)" /var/www/html/ --include="*.php" 2>/dev/null
```

#### 3.8.4 文件完整性检查

```bash
# 使用 AIDE 检查文件完整性（需预先安装并初始化）
aide --check

# 验证 RPM 包完整性（CentOS/RHEL）
rpm -Va

# 验证 DEB 包完整性（Debian/Ubuntu）
debsums -c
```

### 3.9 Rootkit 检测

```bash
# 使用 chkrootkit 检测
chkrootkit

# 使用 rkhunter 检测
rkhunter --check
rkhunter --update

# 检查内核模块
lsmod
cat /proc/modules

# 检查系统调用是否被 hook
# 对比系统调用表（需要专业工具）
```

### 3.10 其他排查项

#### 3.10.1 SSH 密钥排查

```bash
# 查看所有用户的 authorized_keys
cat /home/*/.ssh/authorized_keys 2>/dev/null
cat /root/.ssh/authorized_keys 2>/dev/null

# 查看 SSH 配置
cat /etc/ssh/sshd_config | grep -E "(PermitRootLogin|PasswordAuthentication|PubkeyAuthentication)"
```

#### 3.10.2 后门排查

```bash
# 查看 alias 是否有恶意别名
alias
cat ~/.bashrc | grep alias

# 查看 PATH 环境变量是否有异常
echo $PATH

# 检查系统命令是否被替换
which ls
which ps
which netstat
file /bin/ls
file /bin/ps
file /usr/bin/netstat

# 检查共享库
cat /etc/ld.so.preload
cat /etc/ld.so.conf
```

#### 3.10.3 数据库排查

```bash
# MySQL/MariaDB
mysql -u root -p -e "SELECT user, host FROM mysql.user;"
mysql -u root -p -e "SHOW PROCESSLIST;"

# PostgreSQL
psql -U postgres -c "\du"
psql -U postgres -c "SELECT * FROM pg_stat_activity;"
```

### 3.11 Linux 入侵排查清单

**快速排查清单（15分钟内）：**

- [ ] 查看异常进程（ps aux / top）
- [ ] 查看异常网络连接（netstat -tulnp / ss）
- [ ] 查看异常用户（cat /etc/passwd / last）
- [ ] 查看计划任务（crontab -l / /etc/cron*）
- [ ] 查看系统服务（systemctl / init.d）
- [ ] 查看 SSH 密钥和配置
- [ ] 查看命令历史（history / .bash_history）
- [ ] 查看最近修改的文件（find / -mtime -1）
- [ ] 检查临时目录（/tmp / /dev/shm）
- [ ] 查看系统日志（/var/log/secure / /var/log/auth.log）

**深入排查清单：**

- [ ] Rootkit 检测（chkrootkit / rkhunter）
- [ ] 隐藏进程检测（unhide）
- [ ] 文件完整性检查（AIDE / rpm -Va）
- [ ] 内存取证（Volatility）
- [ ] 磁盘镜像分析
- [ ] 完整日志分析
- [ ] 流量分析（tcpdump / Wireshark）
- [ ] Webshell 全面检测
- [ ] 后门检测（ld.so.preload / 系统命令替换）
- [ ] 内核模块检测

---

---

