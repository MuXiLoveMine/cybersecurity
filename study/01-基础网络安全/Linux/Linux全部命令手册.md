# Linux 全部命令手册

> 本手册收录 Linux 系统中常用的全部命令，按使用频率从高到低排列。常用和基础命令放在最前面，方便快速查阅。

---

## 目录

- [第一部分：常用基础命令（最高频）](#第一部分常用基础命令最高频)
- [第二部分：文件与目录管理](#第二部分文件与目录管理)
- [第三部分：文件内容查看与编辑](#第三部分文件内容查看与编辑)
- [第四部分：文件查找与定位](#第四部分文件查找与定位)
- [第五部分：文件权限与所有者](#第五部分文件权限与所有者)
- [第六部分：用户与组管理](#第六部分用户与组管理)
- [第七部分：进程管理](#第七部分进程管理)
- [第八部分：系统信息与监控](#第八部分系统信息与监控)
- [第九部分：网络命令](#第九部分网络命令)
- [第十部分：磁盘与文件系统](#第十部分磁盘与文件系统)
- [第十一部分：压缩与归档](#第十一部分压缩与归档)
- [第十二部分：软件包管理](#第十二部分软件包管理)
- [第十三部分：文本处理工具](#第十三部分文本处理工具)
- [第十四部分：定时任务](#第十四部分定时任务)
- [第十五部分：服务管理](#第十五部分服务管理)
- [第十六部分：Shell 与脚本相关](#第十六部分shell-与脚本相关)
- [第十七部分：安全与防火墙](#第十七部分安全与防火墙)
- [第十八部分：其他实用命令](#第十八部分其他实用命令)

---

## 第一部分：常用基础命令（最高频）

### 1.1 目录与文件操作

| 命令 | 说明 | 常用示例 |
|------|------|----------|
| `ls` | 列出目录内容 | `ls -la` 显示所有文件（含隐藏文件）的详细信息 |
| `cd` | 切换目录 | `cd /home` 切换到 /home 目录；`cd ~` 回到用户主目录 |
| `pwd` | 显示当前工作目录 | `pwd` 输出当前绝对路径 |
| `mkdir` | 创建目录 | `mkdir -p a/b/c` 递归创建多级目录 |
| `rmdir` | 删除空目录 | `rmdir dirname` 删除空目录 |
| `rm` | 删除文件或目录 | `rm -rf dirname` 递归强制删除目录及内容 |
| `cp` | 复制文件或目录 | `cp -r src dst` 递归复制目录 |
| `mv` | 移动/重命名文件 | `mv old.txt new.txt` 重命名文件 |
| `touch` | 创建空文件或更新时间戳 | `touch file.txt` 创建空文件 |
| `ln` | 创建链接 | `ln -s /path/to/file linkname` 创建软链接 |
| `tree` | 树形显示目录结构 | `tree -L 2` 显示两层目录结构 |

### 1.2 文件查看

| 命令 | 说明 | 常用示例 |
|------|------|----------|
| `cat` | 查看文件内容 | `cat file.txt` 输出文件全部内容 |
| `less` | 分页查看文件 | `less file.txt` 支持上下翻页搜索 |
| `more` | 分页查看文件 | `more file.txt` 向下翻页查看 |
| `head` | 查看文件开头 | `head -n 20 file.txt` 查看前20行 |
| `tail` | 查看文件末尾 | `tail -f log.txt` 实时追踪日志文件 |
| `wc` | 统计行/词/字节数 | `wc -l file.txt` 统计行数 |

### 1.3 帮助与信息

| 命令 | 说明 | 常用示例 |
|------|------|----------|
| `man` | 查看命令手册 | `man ls` 查看 ls 命令帮助 |
| `info` | 查看命令信息 | `info coreutils` 查看 info 文档 |
| `help` | 查看内置命令帮助 | `help cd` 查看 cd 帮助 |
| `--help` | 查看命令帮助 | `ls --help` 查看 ls 快速帮助 |
| `whatis` | 显示命令简短描述 | `whatis ls` 显示 ls 的一行描述 |
| `whereis` | 查找命令位置 | `whereis python` 查找 python 路径 |
| `which` | 查找可执行文件路径 | `which bash` 显示 bash 路径 |
| `type` | 查看命令类型 | `type cd` 显示 cd 是内置命令 |
| `alias` | 设置命令别名 | `alias ll='ls -la'` 设置别名 |
| `unalias` | 取消别名 | `unalias ll` 取消 ll 别名 |
| `history` | 查看历史命令 | `history 50` 查看最近50条命令 |

### 1.4 通用基础

| 命令 | 说明 | 常用示例 |
|------|------|----------|
| `echo` | 输出文本 | `echo $PATH` 输出环境变量 |
| `printf` | 格式化输出 | `printf "%s\n" "hello"` 格式化打印 |
| `clear` | 清屏 | `clear` 清空终端 |
| `date` | 显示/设置日期时间 | `date "+%Y-%m-%d %H:%M:%S"` 格式化输出 |
| `cal` | 显示日历 | `cal 2026` 显示2026年日历 |
| `whoami` | 显示当前用户名 | `whoami` 输出当前用户 |
| `who` | 显示登录用户 | `who` 查看所有登录用户 |
| `w` | 显示用户活动 | `w` 查看用户登录及活动信息 |
| `uptime` | 显示系统运行时间 | `uptime` 查看系统运行时长和负载 |
| `exit` | 退出终端 | `exit` 退出当前 Shell |
| `logout` | 注销登录 | `logout` 注销当前会话 |
| `reboot` | 重启系统 | `reboot` 立即重启 |
| `shutdown` | 关机 | `shutdown -h now` 立即关机 |
| `poweroff` | 关机 | `poweroff` 关闭电源 |

---

## 第二部分：文件与目录管理

| 命令 | 说明 | 常用示例 |
|------|------|----------|
| `stat` | 显示文件状态信息 | `stat file.txt` 查看文件详细元数据 |
| `file` | 查看文件类型 | `file file.txt` 检测文件类型 |
| `basename` | 提取文件名 | `basename /a/b/c.txt` 输出 c.txt |
| `dirname` | 提取目录名 | `dirname /a/b/c.txt` 输出 /a/b |
| `realpath` | 显示绝对路径 | `realpath file.txt` 输出真实路径 |
| `readlink` | 查看符号链接目标 | `readlink -f link` 显示链接指向的真实路径 |
| `install` | 复制文件并设置属性 | `install -m 755 src dst` 复制并设置权限 |
| `truncate` | 缩减/扩展文件大小 | `truncate -s 0 file.txt` 清空文件内容 |
| `mktemp` | 创建临时文件 | `mktemp` 创建唯一临时文件 |
| `updatedb` | 更新文件数据库 | `sudo updatedb` 更新 locate 数据库 |
| `basename` | 获取文件名 | `basename /path/to/file.txt .txt` 输出 file |
| `shred` | 安全删除文件 | `shred -u file.txt` 安全覆盖后删除 |
| `cmp` | 比较两个文件 | `cmp file1 file2` 逐字节比较 |
| `comm` | 比较排序后的文件 | `comm file1 file2` 比较两个排序文件 |
| `shuf` | 随机打乱行 | `shuf file.txt` 随机重排文件行 |
| `rename` | 批量重命名 | `rename 's/.txt/.md/' *.txt` 批量改扩展名 |
| `watch` | 定时执行命令 | `watch -n 2 ls` 每2秒执行一次 ls |

---

## 第三部分：文件内容查看与编辑

| 命令 | 说明 | 常用示例 |
|------|------|----------|
| `vi` / `vim` | 文本编辑器 | `vim file.txt` 用 Vim 编辑文件 |
| `nano` | 简单文本编辑器 | `nano file.txt` 用 nano 编辑文件 |
| `gedit` | 图形文本编辑器 | `gedit file.txt` 用 gedit 编辑 |
| `emacs` | 文本编辑器 | `emacs file.txt` 用 Emacs 编辑 |
| `sed` | 流编辑器 | `sed 's/old/new/g' file` 全局替换文本 |
| `cut` | 按列截取 | `cut -d: -f1 /etc/passwd` 截取第一列 |
| `paste` | 合并文件行 | `paste file1 file2` 按行合并 |
| `column` | 格式化为列 | `column -t file.txt` 对齐为表格 |
| `fold` | 折叠长行 | `fold -w 80 file.txt` 每行80字符换行 |
| `fmt` | 格式化段落 | `fmt -w 72 file.txt` 设置段落宽度 |
| `pr` | 格式化打印 | `pr -n file.txt` 带行号格式化输出 |
| `nl` | 添加行号 | `nl file.txt` 给文件加行号 |
| `tac` | 反向输出 | `tac file.txt` 从最后一行开始输出 |
| `rev` | 反转每行字符 | `rev file.txt` 每行字符顺序反转 |
| `expand` | 制表符转空格 | `expand -t 4 file.txt` Tab 转4个空格 |
| `unexpand` | 空格转制表符 | `unexpand -a file.txt` 空格转 Tab |
| `strings` | 提取可打印字符串 | `strings binary_file` 提取二进制中的文本 |
| `xxd` | 十六进制转储 | `xxd file.txt` 以十六进制显示文件 |
| `hexdump` | 十六进制转储 | `hexdump -C file.txt` 带ASCII的十六进制显示 |
| `od` | 八进制转储 | `od -c file.txt` 以字符方式显示 |

---

## 第四部分：文件查找与定位

| 命令 | 说明 | 常用示例 |
|------|------|----------|
| `find` | 查找文件 | `find / -name "*.conf"` 按名称查找文件 |
| `locate` | 快速查找文件 | `locate nginx.conf` 从数据库查找 |
| `which` | 查找命令路径 | `which python3` 查找 python3 路径 |
| `whereis` | 查找命令相关文件 | `whereis nginx` 查找 nginx 相关文件 |
| `grep` | 文本搜索 | `grep -rn "keyword" /path` 递归搜索关键词 |
| `egrep` | 扩展正则搜索 | `egrep "a\|b" file` 匹配 a 或 b |
| `fgrep` | 固定字符串搜索 | `fgrep "literal" file` 搜索固定字符串 |
| `rg` | ripgrep 快速搜索 | `rg "pattern" /path` 比 grep 更快 |
| `ag` | silver searcher 搜索 | `ag "pattern" /path` 快速代码搜索 |
| `ack` | 代码搜索工具 | `ack "pattern"` 面向程序员的搜索 |
| `fd` | 现代版 find | `fd "\.conf$"` 快速查找文件 |
| `fzf` | 模糊查找器 | `fzf` 交互式模糊搜索 |

---

## 第五部分：文件权限与所有者

| 命令 | 说明 | 常用示例 |
|------|------|----------|
| `chmod` | 修改文件权限 | `chmod 755 file` 设置 rwxr-xr-x 权限 |
| `chown` | 修改文件所有者 | `chown user:group file` 修改所有者和组 |
| `chgrp` | 修改文件所属组 | `chgrp groupname file` 修改所属组 |
| `umask` | 设置默认权限掩码 | `umask 022` 设置默认权限 |
| `chattr` | 修改文件扩展属性 | `chattr +i file` 设置不可变属性 |
| `lsattr` | 查看文件扩展属性 | `lsattr file` 查看扩展属性 |
| `getfacl` | 查看 ACL 权限 | `getfacl file` 查看访问控制列表 |
| `setfacl` | 设置 ACL 权限 | `setfacl -m u:user:rwx file` 为用户设置权限 |
| `sudo` | 以管理员执行 | `sudo apt update` 以 root 权限执行 |
| `su` | 切换用户 | `su - root` 切换到 root 用户 |
| `newgrp` | 切换到新组 | `newgrp docker` 切换到 docker 组 |
| `id` | 显示用户ID信息 | `id username` 显示 UID/GID 信息 |

---

## 第六部分：用户与组管理

| 命令 | 说明 | 常用示例 |
|------|------|----------|
| `useradd` | 添加用户 | `useradd -m -s /bin/bash user` 创建用户并建主目录 |
| `userdel` | 删除用户 | `userdel -r user` 删除用户及主目录 |
| `usermod` | 修改用户属性 | `usermod -aG sudo user` 将用户加入 sudo 组 |
| `adduser` | 交互式添加用户 | `adduser username` 交互式创建用户 |
| `deluser` | 交互式删除用户 | `deluser username` 交互式删除用户 |
| `groupadd` | 添加用户组 | `groupadd groupname` 创建新组 |
| `groupdel` | 删除用户组 | `groupdel groupname` 删除组 |
| `groupmod` | 修改组属性 | `groupmod -n newname oldname` 重命名组 |
| `gpasswd` | 管理组密码和成员 | `gpasswd -a user group` 将用户加入组 |
| `passwd` | 修改用户密码 | `passwd username` 修改密码 |
| `chpasswd` | 批量修改密码 | `echo "user:pass" \| chpasswd` 批量设置密码 |
| `chage` | 修改密码策略 | `chage -M 90 user` 设置密码90天过期 |
| `chfn` | 修改用户信息 | `chfn -f "Full Name" user` 修改全名 |
| `chsh` | 修改登录 Shell | `chsh -s /bin/zsh` 修改默认 Shell |
| `groups` | 查看用户所属组 | `groups username` 显示用户所属组 |
| `getent` | 查询系统数据库 | `getent passwd user` 查询用户信息 |
| `vipw` | 编辑 passwd 文件 | `vipw` 安全编辑 /etc/passwd |
| `vigr` | 编辑 group 文件 | `vigr` 安全编辑 /etc/group |
| `last` | 查看登录记录 | `last` 显示用户登录历史 |
| `lastlog` | 查看最后登录 | `lastlog` 显示所有用户最后登录时间 |
| `finger` | 查看用户信息 | `finger username` 显示用户详细信息 |

---

## 第七部分：进程管理

| 命令 | 说明 | 常用示例 |
|------|------|----------|
| `ps` | 查看进程 | `ps aux` 查看所有进程 |
| `top` | 实时进程监控 | `top` 实时显示进程和资源使用 |
| `htop` | 增强版进程监控 | `htop` 彩色交互式进程查看 |
| `btop` | 现代化系统监控 | `btop` 美观的系统资源监控 |
| `kill` | 终止进程 | `kill -9 PID` 强制杀死进程 |
| `killall` | 按名称终止进程 | `killall nginx` 杀死所有 nginx 进程 |
| `pkill` | 按名称终止进程 | `pkill -f "python script.py"` 按命令行匹配 |
| `pgrep` | 按名称查找进程 | `pgrep -l nginx` 查找 nginx 进程 |
| `jobs` | 查看后台任务 | `jobs -l` 列出后台任务及 PID |
| `bg` | 后台运行任务 | `bg %1` 将任务1放到后台 |
| `fg` | 前台运行任务 | `fg %1` 将任务1调到前台 |
| `nohup` | 忽略挂断运行 | `nohup command &` 后台运行不随终端退出 |
| `disown` | 从作业表移除 | `disown %1` 将任务脱离终端 |
| `nice` | 设置进程优先级 | `nice -n 10 command` 降低优先级运行 |
| `renice` | 修改进程优先级 | `renice -n 5 -p PID` 修改运行中进程优先级 |
| `pidof` | 查找进程 PID | `pidof nginx` 获取 nginx 的 PID |
| `pstree` | 树形显示进程 | `pstree -p` 以树形显示进程及 PID |
| `atop` | 高级系统监控 | `atop` 记录和显示系统活动 |
| `glances` | 系统监控工具 | `glances` 全面的系统监控 |
| `free` | 查看内存使用 | `free -h` 人性化显示内存 |
| `vmstat` | 虚拟内存统计 | `vmstat 1` 每秒报告一次系统状态 |
| `strace` | 追踪系统调用 | `strace -p PID` 追踪进程的系统调用 |
| `ltrace` | 追踪库调用 | `ltrace command` 追踪动态库调用 |
| `timeout` | 限时运行命令 | `timeout 10 command` 10秒后自动终止 |
| `wait` | 等待进程结束 | `wait $PID` 等待指定进程完成 |

---

## 第八部分：系统信息与监控

| 命令 | 说明 | 常用示例 |
|------|------|----------|
| `uname` | 显示系统信息 | `uname -a` 显示所有系统信息 |
| `hostname` | 显示/设置主机名 | `hostname` 显示主机名 |
| `hostnamectl` | 管理主机名 | `hostnamectl set-hostname name` 设置主机名 |
| `dmesg` | 查看内核日志 | `dmesg \| tail` 查看最近的内核消息 |
| `lscpu` | 查看 CPU 信息 | `lscpu` 显示 CPU 架构信息 |
| `lsmem` | 查看内存信息 | `lsmem` 显示内存范围信息 |
| `lsblk` | 查看块设备 | `lsblk` 列出块设备树 |
| `lspci` | 查看 PCI 设备 | `lspci -v` 详细显示 PCI 设备 |
| `lsusb` | 查看 USB 设备 | `lsusb` 列出 USB 设备 |
| `lsdev` | 查看设备信息 | `lsdev` 显示设备信息 |
| `lshw` | 查看硬件信息 | `lshw -short` 简洁显示硬件列表 |
| `dmidecode` | 查看 DMI 信息 | `dmidecode -t memory` 查看内存信息 |
| `inxi` | 系统信息工具 | `inxi -F` 显示完整系统信息 |
| `neofetch` | 系统信息展示 | `neofetch` 美观显示系统信息 |
| `screenfetch` | 系统信息展示 | `screenfetch` 带logo的系统信息 |
| `time` | 命令计时 | `time command` 测量命令执行时间 |
| `arch` | 显示系统架构 | `arch` 输出如 x86_64 |
| `nproc` | 显示 CPU 核数 | `nproc` 输出逻辑 CPU 数量 |
| `lsof` | 查看打开的文件 | `lsof -i:80` 查看占用80端口的进程 |
| `fuser` | 查看文件使用者 | `fuser -k 80/tcp` 杀死占用80端口的进程 |
| `iostat` | I/O 统计 | `iostat -x 1` 每秒显示扩展 I/O 统计 |
| `iotop` | I/O 监控 | `iotop` 监控进程 I/O 使用 |
| `sar` | 系统活动报告 | `sar -u 1 3` 每秒报告3次CPU使用率 |
| `mpstat` | 多核 CPU 统计 | `mpstat -P ALL` 显示所有CPU核心状态 |
| `watch` | 定时刷新命令 | `watch -n 1 nvidia-smi` 每秒刷新GPU状态 |

---

## 第九部分：网络命令

| 命令 | 说明 | 常用示例 |
|------|------|----------|
| `ping` | 测试网络连通性 | `ping -c 4 google.com` 发送4个测试包 |
| `ifconfig` | 查看/配置网卡 | `ifconfig eth0 up` 启用网卡 |
| `ip` | 网络配置工具 | `ip addr show` 查看所有网络接口 |
| `route` | 查看/管理路由表 | `route -n` 查看路由表 |
| `traceroute` | 路由追踪 | `traceroute google.com` 追踪路由路径 |
| `tracepath` | 路径追踪 | `tracepath google.com` 追踪MTU路径 |
| `mtr` | 网络诊断工具 | `mtr google.com` 结合 ping 和 traceroute |
| `netstat` | 查看网络状态 | `netstat -tlnp` 查看监听端口 |
| `ss` | 查看套接字 | `ss -tlnp` 替代 netstat 查看端口 |
| `curl` | HTTP 请求工具 | `curl -O url` 下载文件 |
| `wget` | 文件下载 | `wget -c url` 断点续传下载 |
| `ssh` | 远程登录 | `ssh user@host` SSH 远程连接 |
| `scp` | 安全复制文件 | `scp file user@host:/path` 远程复制文件 |
| `rsync` | 远程同步 | `rsync -avz src/ dst/` 增量同步目录 |
| `sftp` | 安全文件传输 | `sftp user@host` 交互式文件传输 |
| `nc` / `netcat` | 网络工具 | `nc -l 8080` 监听8080端口 |
| `nmap` | 网络扫描 | `nmap -sS 192.168.1.0/24` 扫描网段 |
| `dig` | DNS 查询 | `dig example.com` 查询 DNS 记录 |
| `nslookup` | DNS 查询 | `nslookup example.com` 查询域名解析 |
| `host` | DNS 查询 | `host example.com` 简单 DNS 查询 |
| `arp` | ARP 缓存管理 | `arp -a` 查看 ARP 缓存表 |
| `hostname` | 主机名管理 | `hostname -I` 显示本机 IP |
| `tcpdump` | 抓包工具 | `tcpdump -i eth0 port 80` 抓取80端口流量 |
| `tshark` | 终端抓包 | `tshark -i eth0` Wireshark 命令行版 |
| `telnet` | 远程登录/测试 | `telnet host 80` 测试端口连通性 |
| `ftp` | 文件传输 | `ftp host` 连接 FTP 服务器 |
| `mail` | 邮件客户端 | `mail -s "subject" user` 发送邮件 |
| `iptables` | 防火墙规则 | `iptables -L` 查看防火墙规则 |
| `ufw` | 简化防火墙 | `ufw allow 80` 允许80端口 |
| `firewalld` | 动态防火墙 | `firewall-cmd --list-all` 查看防火墙 |
| `nmcli` | NetworkManager CLI | `nmcli device status` 查看网络设备状态 |
| `ifup` / `ifdown` | 启停网卡 | `ifup eth0` 启用 eth0 网卡 |
| `ethtool` | 网卡配置工具 | `ethtool eth0` 查看网卡详细信息 |
| `iwconfig` | 无线网卡配置 | `iwconfig wlan0` 查看无线网卡 |
| `iw` | 无线网络工具 | `iw dev` 查看无线设备 |

---

## 第十部分：磁盘与文件系统

| 命令 | 说明 | 常用示例 |
|------|------|----------|
| `df` | 查看磁盘使用 | `df -h` 人性化显示磁盘空间 |
| `du` | 查看目录大小 | `du -sh /path` 显示目录总大小 |
| `fdisk` | 磁盘分区工具 | `fdisk -l` 列出所有磁盘分区 |
| `parted` | 分区工具 | `parted /dev/sda print` 显示分区表 |
| `cfdisk` | 交互式分区 | `cfdisk /dev/sda` 图形化分区 |
| `mkfs` | 创建文件系统 | `mkfs.ext4 /dev/sda1` 格式化为 ext4 |
| `mke2fs` | 创建 ext 文件系统 | `mke2fs -t ext4 /dev/sda1` 创建 ext4 |
| `mount` | 挂载文件系统 | `mount /dev/sda1 /mnt` 挂载分区 |
| `umount` | 卸载文件系统 | `umount /mnt` 卸载挂载点 |
| `fsck` | 文件系统检查 | `fsck /dev/sda1` 检查并修复文件系统 |
| `e2fsck` | ext 文件系统检查 | `e2fsck -f /dev/sda1` 强制检查 ext |
| `tune2fs` | 调整 ext 参数 | `tune2fs -l /dev/sda1` 查看文件系统信息 |
| `dumpe2fs` | 查看 ext 信息 | `dumpe2fs /dev/sda1` 显示文件系统详情 |
| `blkid` | 查看块设备标识 | `blkid` 显示设备 UUID 和类型 |
| `findmnt` | 查看挂载信息 | `findmnt` 以树形显示挂载点 |
| `lsblk` | 查看块设备 | `lsblk -f` 显示设备文件系统 |
| `partprobe` | 更新分区表 | `partprobe /dev/sda` 通知内核重新读取分区 |
| `dd` | 数据复制工具 | `dd if=/dev/sda of=image.iso` 制作磁盘镜像 |
| `hdparm` | 硬盘参数设置 | `hdparm -tT /dev/sda` 测试磁盘速度 |
| `smartctl` | 硬盘健康检测 | `smartctl -a /dev/sda` 查看 S.M.A.R.T 信息 |
| `badblocks` | 检查坏块 | `badblocks -v /dev/sda1` 检查磁盘坏块 |
| `mdadm` | RAID 管理 | `mdadm --detail /dev/md0` 查看 RAID 信息 |
| `lvdisplay` | 查看 LVM 逻辑卷 | `lvdisplay` 显示逻辑卷信息 |
| `pvdisplay` | 查看 LVM 物理卷 | `pvdisplay` 显示物理卷信息 |
| `vgdisplay` | 查看 LVM 卷组 | `vgdisplay` 显示卷组信息 |
| `lvcreate` | 创建逻辑卷 | `lvcreate -L 10G -n lv1 vg0` 创建10G逻辑卷 |
| `lvextend` | 扩展逻辑卷 | `lvextend -L +5G /dev/vg0/lv1` 扩容5G |
| `xfs_growfs` | 扩展 XFS 文件系统 | `xfs_growfs /mnt` 在线扩展 XFS |
| `resize2fs` | 扩展 ext 文件系统 | `resize2fs /dev/vg0/lv1` 在线扩展 ext4 |
| `fstrim` | SSD TRIM 操作 | `fstrim /` 回收 SSD 未使用块 |
| `duf` | 现代版 df | `duf` 美观显示磁盘使用情况 |
| `ncdu` | 交互式 du | `ncdu /path` 交互式查看目录大小 |

---

## 第十一部分：压缩与归档

| 命令 | 说明 | 常用示例 |
|------|------|----------|
| `tar` | 归档工具 | `tar -czvf archive.tar.gz dir/` 压缩目录为 tar.gz |
| `gzip` | gzip 压缩 | `gzip file` 压缩为 .gz 文件 |
| `gunzip` | gzip 解压 | `gunzip file.gz` 解压 .gz 文件 |
| `bzip2` | bzip2 压缩 | `bzip2 file` 压缩为 .bz2（压缩率高） |
| `bunzip2` | bzip2 解压 | `bunzip2 file.bz2` 解压 .bz2 文件 |
| `xz` | xz 压缩 | `xz file` 压缩为 .xz（压缩率最高） |
| `unxz` | xz 解压 | `unxz file.xz` 解压 .xz 文件 |
| `zip` | zip 压缩 | `zip -r archive.zip dir/` 压缩为 zip |
| `unzip` | zip 解压 | `unzip archive.zip` 解压 zip 文件 |
| `7z` | 7zip 压缩 | `7z a archive.7z dir/` 压缩为 7z |
| `rar` | rar 压缩 | `rar a archive.rar dir/` 压缩为 rar |
| `unrar` | rar 解压 | `unrar x archive.rar` 解压 rar 文件 |
| `zcat` | 查看压缩文件 | `zcat file.gz` 不解压查看 .gz 内容 |
| `zgrep` | 搜索压缩文件 | `zgrep "keyword" file.gz` 在 .gz 中搜索 |
| `zless` | 分页查看压缩文件 | `zless file.gz` 分页查看 .gz |
| `compress` | 旧式压缩 | `compress file` 压缩为 .Z |
| `uncompress` | 旧式解压 | `uncompress file.Z` 解压 .Z 文件 |
| `ar` | 归档工具 | `ar rcs lib.a *.o` 创建静态库 |
| `cpio` | 归档工具 | `find . \| cpio -ov > archive.cpio` 创建归档 |
| `zstd` | Zstandard 压缩 | `zstd file` 快速压缩为 .zst |

---

## 第十二部分：软件包管理

### 12.1 Debian/Ubuntu 系（apt/dpkg）

| 命令 | 说明 | 常用示例 |
|------|------|----------|
| `apt` | 高级包管理 | `apt install nginx` 安装软件包 |
| `apt-get` | 包管理工具 | `apt-get update` 更新包索引 |
| `apt-cache` | 包查询 | `apt-cache search nginx` 搜索软件包 |
| `dpkg` | 底层包管理 | `dpkg -i package.deb` 安装 deb 包 |
| `aptitude` | 交互式包管理 | `aptitude install nginx` 安装软件 |
| `snap` | Snap 包管理 | `snap install package` 安装 snap 包 |
| `flatpak` | Flatpak 管理 | `flatpak install package` 安装 flatpak |
| `tasksel` | 任务安装 | `tasksel install lamp-server` 安装任务组 |
| `gdebi` | 安装 deb 及依赖 | `gdebi package.deb` 安装并自动处理依赖 |
| `add-apt-repository` | 添加 PPA | `add-apt-repository ppa:name` 添加 PPA 源 |

### 12.2 RHEL/CentOS 系（yum/dnf/rpm）

| 命令 | 说明 | 常用示例 |
|------|------|----------|
| `dnf` | 新版包管理 | `dnf install nginx` 安装软件包 |
| `yum` | 包管理工具 | `yum install nginx` 安装软件包 |
| `rpm` | RPM 包管理 | `rpm -ivh package.rpm` 安装 rpm 包 |
| `dnf group` | 组安装 | `dnf groupinstall "Dev Tools"` 安装开发工具组 |

### 12.3 Arch 系（pacman）

| 命令 | 说明 | 常用示例 |
|------|------|----------|
| `pacman` | Arch 包管理 | `pacman -S nginx` 安装软件包 |
| `yay` | AUR 助手 | `yay -S package` 安装 AUR 包 |

### 12.4 通用

| 命令 | 说明 | 常用示例 |
|------|------|----------|
| `pip` | Python 包管理 | `pip install package` 安装 Python 包 |
| `pip3` | Python3 包管理 | `pip3 install package` 安装 Python3 包 |
| `conda` | Conda 包管理 | `conda install package` 安装 Conda 包 |
| `npm` | Node 包管理 | `npm install package` 安装 Node 包 |
| `yarn` | Node 包管理 | `yarn add package` 安装 Node 包 |
| `gem` | Ruby 包管理 | `gem install package` 安装 Ruby 包 |
| `composer` | PHP 包管理 | `composer require package` 安装 PHP 包 |
| `cargo` | Rust 包管理 | `cargo install crate` 安装 Rust 包 |
| `go` | Go 包管理 | `go get package` 安装 Go 包 |
| `brew` | Homebrew 管理 | `brew install package` 安装软件 |
| `make` | 编译工具 | `make && make install` 编译安装 |
| `cmake` | 构建工具 | `cmake .` 生成 Makefile |
| `configure` | 配置编译 | `./configure --prefix=/usr/local` 配置安装路径 |

---

## 第十三部分：文本处理工具

| 命令 | 说明 | 常用示例 |
|------|------|----------|
| `grep` | 文本搜索 | `grep -i "error" log.txt` 不区分大小写搜索 |
| `sed` | 流编辑器 | `sed -i 's/old/new/g' file` 原地替换 |
| `awk` | 文本处理语言 | `awk '{print $1}' file` 打印第一列 |
| `gawk` | GNU awk | `gawk -F: '{print $1}' /etc/passwd` 处理 |
| `sort` | 排序 | `sort -rn file` 按数字逆序排序 |
| `uniq` | 去重 | `sort file \| uniq -c` 排序并统计重复行 |
| `tr` | 字符转换 | `tr 'a-z' 'A-Z'` 小写转大写 |
| `cut` | 截取列 | `cut -d',' -f2 file` 截取第2列 |
| `paste` | 合并文件 | `paste -d',' file1 file2` 按逗号合并 |
| `join` | 关联合并 | `join file1 file2` 按公共字段合并 |
| `split` | 分割文件 | `split -l 1000 file prefix` 每千行分割 |
| `csplit` | 按模式分割 | `csplit file /pattern/` 按模式分割 |
| `tee` | 双向输出 | `command \| tee file` 输出到终端和文件 |
| `xargs` | 参数传递 | `find . -name "*.log" \| xargs rm` 批量删除 |
| `diff` | 文件比较 | `diff file1 file2` 比较两个文件差异 |
| `patch` | 打补丁 | `patch -p1 < file.patch` 应用补丁 |
| `col` | 过滤控制字符 | `man ls \| col -b > ls.txt` 去除格式字符 |
| `column` | 列格式化 | `column -t -s',' file.csv` CSV对齐显示 |
| `jq` | JSON 处理 | `jq '.key' file.json` 提取 JSON 字段 |
| `yq` | YAML 处理 | `yq '.key' file.yaml` 提取 YAML 字段 |
| `xmlstarlet` | XML 处理 | `xmlstarlet sel -t -v "//node" file.xml` 解析 XML |
| `iconv` | 编码转换 | `iconv -f GBK -t UTF-8 file` 转换编码 |
| `enca` | 检测编码 | `enca file` 检测文件编码 |
| `dos2unix` | 换行符转换 | `dos2unix file` Windows转Unix换行 |
| `unix2dos` | 换行符转换 | `unix2dos file` Unix转Windows换行 |
| `figlet` | ASCII 艺术字 | `figlet "Hello"` 生成大字标题 |
| `toilet` | 彩色 ASCII 字 | `toilet -f mono "Hello"` 彩色大字 |
| `boxes` | 文字边框 | `echo "hi" \| boxes` 给文字加边框 |
| `cowsay` | 牛说话 | `cowsay "Hello"` ASCII 牛说话 |
| `lolcat` | 彩虹色输出 | `echo "hi" \| lolcat` 彩虹色显示 |
| `asciinema` | 终端录制 | `asciinema rec` 录制终端操作 |

---

## 第十四部分：定时任务

| 命令 | 说明 | 常用示例 |
|------|------|----------|
| `crontab` | 定时任务管理 | `crontab -e` 编辑定时任务 |
| `at` | 一次性定时任务 | `echo "cmd" \| at 10:00` 10点执行一次 |
| `atq` | 查看待执行任务 | `atq` 列出 at 队列 |
| `atrm` | 删除 at 任务 | `atrm 1` 删除编号1的任务 |
| `batch` | 系统空闲时执行 | `batch` 系统负载低时执行 |
| `systemctl` | 管理定时服务 | `systemctl status cron` 查看 cron 状态 |
| `anacron` | 非实时定时任务 | 配置 /etc/anacrontab 补执行漏掉的任务 |

---

## 第十五部分：服务管理

| 命令 | 说明 | 常用示例 |
|------|------|----------|
| `systemctl` | systemd 服务管理 | `systemctl start nginx` 启动服务 |
| `service` | SysV 服务管理 | `service nginx start` 启动服务 |
| `journalctl` | 查看系统日志 | `journalctl -u nginx -f` 追踪 nginx 日志 |
| `chkconfig` | 服务开机自启 | `chkconfig nginx on` 设置开机启动 |
| `init` | 切换运行级别 | `init 3` 切换到命令行模式 |
| `telinit` | 切换运行级别 | `telinit 6` 重启系统 |
| `runlevel` | 查看运行级别 | `runlevel` 显示当前运行级别 |
| `tput` | 终端控制 | `tput setaf 1` 设置前景色为红色 |
| `stty` | 终端设置 | `stty -a` 查看终端设置 |

---

## 第十六部分：Shell 与脚本相关

| 命令 | 说明 | 常用示例 |
|------|------|----------|
| `bash` | Bash Shell | `bash script.sh` 执行 Bash 脚本 |
| `sh` | POSIX Shell | `sh script.sh` 执行 Shell 脚本 |
| `zsh` | Z Shell | `zsh` 启动 Zsh |
| `fish` | Friendly Shell | `fish` 启动 Fish Shell |
| `source` / `.` | 执行脚本 | `source ~/.bashrc` 重新加载配置 |
| `export` | 导出环境变量 | `export PATH=$PATH:/new/path` 设置 PATH |
| `env` | 查看环境变量 | `env` 显示所有环境变量 |
| `printenv` | 打印环境变量 | `printenv PATH` 输出 PATH 变量 |
| `set` | 查看/设置 Shell 变量 | `set` 显示所有变量 |
| `unset` | 删除变量 | `unset VARNAME` 删除变量 |
| `declare` | 声明变量 | `declare -r CONST=1` 声明只读变量 |
| `readonly` | 设置只读变量 | `readonly VAR` 设置变量为只读 |
| `read` | 读取输入 | `read -p "Name: " name` 交互式读取 |
| `test` / `[ ]` | 条件测试 | `test -f file` 测试文件是否存在 |
| `expr` | 整数运算 | `expr 1 + 2` 计算加法 |
| `bc` | 计算器 | `echo "scale=2; 10/3" \| bc` 浮点运算 |
| `seq` | 生成序列 | `seq 1 10` 生成1到10的序列 |
| `yes` | 重复输出 | `yes \| rm *.tmp` 自动回答 yes |
| `sleep` | 延时 | `sleep 5` 暂停5秒 |
| `cron` | 定时任务守护 | `crond` cron 守护进程 |
| `eval` | 执行命令字符串 | `eval "$cmd"` 执行变量中的命令 |
| `exec` | 替换当前进程 | `exec command` 替换当前 Shell |
| `trap` | 捕获信号 | `trap 'echo bye' EXIT` 退出时执行 |
| `getopts` | 解析选项 | Shell 脚本中解析命令行参数 |
| `shift` | 移动位置参数 | `shift` 左移参数列表 |
| `xargs` | 构造参数列表 | `echo "a b c" \| xargs mkdir` 批量创建目录 |
| `basename` | 取文件名 | `basename $0` 获取脚本名 |
| `dirname` | 取目录名 | `dirname $0` 获取脚本所在目录 |
| `logger` | 记录系统日志 | `logger "message"` 写入 syslog |

---

## 第十七部分：安全与防火墙

| 命令 | 说明 | 常用示例 |
|------|------|----------|
| `sudo` | 以管理员权限执行 | `sudo command` 以 root 执行命令 |
| `su` | 切换用户 | `su -` 切换到 root |
| `passwd` | 修改密码 | `passwd user` 修改用户密码 |
| `gpg` | GPG 加密 | `gpg -c file` 对称加密文件 |
| `openssl` | SSL/TLS 工具 | `openssl enc -aes-256-cbc -in file -out enc` 加密 |
| `ssh-keygen` | 生成 SSH 密钥 | `ssh-keygen -t rsa -b 4096` 生成 RSA 密钥 |
| `ssh-copy-id` | 复制公钥 | `ssh-copy-id user@host` 安装公钥到远程 |
| `ssh-agent` | SSH 代理 | `eval $(ssh-agent)` 启动 SSH 代理 |
| `ssh-add` | 添加密钥到代理 | `ssh-add ~/.ssh/id_rsa` 添加密钥 |
| `iptables` | 防火墙规则 | `iptables -A INPUT -p tcp --dport 22 -j ACCEPT` |
| `ip6tables` | IPv6 防火墙 | `ip6tables -L` 查看 IPv6 规则 |
| `ufw` | 简化防火墙 | `ufw enable` 启用防火墙 |
| `firewall-cmd` | firewalld 命令 | `firewall-cmd --add-port=80/tcp` 开放端口 |
| `fail2ban-client` | 入侵防护 | `fail2ban-client status` 查看 ban 状态 |
| `tcpdump` | 网络抓包 | `tcpdump -i eth0 -w capture.pcap` 抓包保存 |
| `nmap` | 端口扫描 | `nmap -sV -p 1-1000 host` 扫描端口和服务 |
| `nikto` | Web 漏洞扫描 | `nikto -h http://target` 扫描 Web 漏洞 |
| `john` | 密码破解 | `john hashfile` 破解密码哈希 |
| `hashcat` | GPU 密码破解 | `hashcat -m 0 hash.txt wordlist` 破解哈希 |
| `aircrack-ng` | 无线安全工具 | `aircrack-ng capture.cap` 破解 WiFi |
| `hydra` | 暴力破解 | `hydra -l user -P passlist ssh://host` 破解 SSH |
| `selinux` | SELinux 管理 | `getenforce` 查看 SELinux 状态 |
| `getenforce` | 查看 SELinux 模式 | `getenforce` 输出 Enforcing/Permissive |
| `setenforce` | 设置 SELinux 模式 | `setenforce 0` 设置为宽容模式 |
| `chcon` | 修改 SELinux 上下文 | `chcon -t httpd_sys_content_t file` |
| `restorecon` | 恢复 SELinux 上下文 | `restorecon -R /var/www` 恢复默认上下文 |
| `auditctl` | 审计规则管理 | `auditctl -l` 列出审计规则 |
| `ausearch` | 搜索审计日志 | `ausearch -m USER_LOGIN` 搜索登录事件 |
| `aureport` | 审计报告 | `aureport --summary` 生成审计摘要 |
| `chroot` | 改变根目录 | `chroot /newroot /bin/bash` 切换根环境 |
| `apparmor` | AppArmor 管理 | `aa-status` 查看 AppArmor 状态 |
| `rkhunter` | Rootkit 检测 | `rkhunter --check` 检查 Rootkit |
| `clamscan` | 病毒扫描 | `clamscan -r /home` 递归扫描病毒 |
| `lynis` | 安全审计 | `lynis audit system` 系统安全审计 |

---

## 第十八部分：其他实用命令

| 命令 | 说明 | 常用示例 |
|------|------|----------|
| `git` | 版本控制 | `git clone url` 克隆仓库 |
| `docker` | 容器管理 | `docker run -it ubuntu bash` 运行容器 |
| `docker-compose` | 容器编排 | `docker-compose up -d` 启动服务栈 |
| `kubectl` | K8s 管理 | `kubectl get pods` 查看 Pod |
| `screen` | 终端复用器 | `screen -S name` 创建命名会话 |
| `tmux` | 终端复用器 | `tmux new -s name` 创建新会话 |
| `byobu` | 增强终端复用 | `byobu` 启动 Byobu |
| `tldr` | 简化版 man | `tldr tar` 查看 tar 简明示例 |
| `cheat` | 命令速查 | `cheat tar` 查看 tar 常用示例 |
| `entr` | 文件变化触发 | `ls *.py \| entr python test.py` 文件变化自动运行 |
| `fzf` | 模糊查找 | `find . \| fzf` 交互式文件选择 |
| `ripgrep` | 快速搜索 | `rg "pattern" --type py` 在 Python 文件中搜索 |
| `bat` | 增强版 cat | `bat file.py` 带语法高亮查看 |
| `exa` / `eza` | 增强版 ls | `exa -la --git` 带Git状态显示 |
| `delta` | 增强版 diff | `git diff \| delta` 美观显示差异 |
| `dust` | 增强版 du | `dust /path` 可视化磁盘使用 |
| `procs` | 增强版 ps | `procs` 彩色进程列表 |
| `bottom` | 增强版 top | `btm` 图形化系统监控 |
| `gdu` | 快速 du | `gdu /path` 快速磁盘分析 |
| `sd` | 增强版 sed | `sd 'old' 'new' file` 更易用的替换 |
| `hyperfine` | 基准测试 | `hyperfine 'cmd1' 'cmd2'` 比较命令性能 |
| `zoxide` | 智能 cd | `z dirname` 快速跳转常用目录 |
| `mcfly` | 智能 history | 搜索历史命令 |
| `starship` | Shell 提示符 | 跨 Shell 的美观提示符 |
| `lazygit` | Git TUI | `lazygit` 终端 Git 图形界面 |
| `lazydocker` | Docker TUI | `lazydocker` 终端 Docker 管理 |
| `ncdu` | 磁盘使用分析 | `ncdu /` 交互式磁盘分析 |
| `glow` | Markdown 渲染 | `glow README.md` 终端渲染 Markdown |
| `mdcat` | Markdown 渲染 | `mdcat file.md` 终端显示 Markdown |
| `chafa` | 终端图片显示 | `chafa image.png` 终端中显示图片 |
| `pv` | 管道进度条 | `pv bigfile \| tar -cz` 显示传输进度 |
| `progress` | 显示进度 | `progress -m` 监控 cp/mv 等进度 |
| `dialog` | 终端对话框 | `dialog --msgbox "Hello" 10 30` 显示对话框 |
| `whiptail` | 交互式对话框 | `whiptail --yesno "Continue?" 10 30` |
| `expect` | 自动交互 | 自动化 SSH 登录等交互操作 |
| `parallel` | 并行执行 | `parallel command ::: arg1 arg2` 并行运行 |
| `cron` | 定时任务守护 | 系统定时任务服务 |
| `atop` | 高级监控 | `atop 1` 每秒更新系统状态 |
| `slurm` | 网络流量监控 | `slurm -i eth0` 可视化网卡流量 |
| `speedtest-cli` | 网速测试 | `speedtest-cli` 测试网络速度 |
| `ffmpeg` | 音视频处理 | `ffmpeg -i input.mp4 output.avi` 格式转换 |
| `imagemagick` | 图片处理 | `convert input.png output.jpg` 格式转换 |
| `pandoc` | 文档转换 | `pandoc input.md -o output.pdf` 格式转换 |
| `cron` | 定时守护进程 | 系统计划任务服务 |
| `wall` | 广播消息 | `wall "System reboot in 5 min"` 向所有用户广播 |
| `write` | 发送消息 | `write username tty` 向指定用户发消息 |
| `mesg` | 消息开关 | `mesg n` 拒绝接收消息 |
| `talk` | 聊天 | `talk username` 与用户聊天 |
| `banner` | 大字横幅 | `banner "Hello"` 打印大字 |
| `factor` | 因数分解 | `factor 100` 分解质因数 |
| `units` | 单位转换 | `units` 交互式单位转换 |
| `calendar` | 日历提醒 | `calendar` 查看今日日历提醒 |
| `fortune` | 随机格言 | `fortune` 输出随机名言 |
| `sl` | 蒸汽火车 | `sl` 趣味命令（ls的纠错彩蛋） |
| `cmatrix` | 矩阵雨 | `cmatrix` 黑客帝国效果 |
| `neofetch` | 系统信息 | `neofetch` 美观显示系统信息 |

---

## 附录：命令速查表

### 常用快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl + C` | 终止当前命令 |
| `Ctrl + Z` | 挂起当前命令（可用 fg 恢复） |
| `Ctrl + D` | 退出当前 Shell（EOF） |
| `Ctrl + A` | 光标移到行首 |
| `Ctrl + E` | 光标移到行尾 |
| `Ctrl + U` | 删除光标到行首的内容 |
| `Ctrl + K` | 删除光标到行尾的内容 |
| `Ctrl + W` | 删除光标前一个单词 |
| `Ctrl + R` | 搜索历史命令 |
| `Ctrl + L` | 清屏（等同于 clear） |
| `Tab` | 自动补全 |
| `!!` | 执行上一条命令 |
| `!$` | 上一条命令的最后一个参数 |
| `Alt + .` | 插入上一条命令的最后一个参数 |

### 文件权限说明

```
rwx rwx rwx
 |   |   |
 |   |   └── 其他用户权限 (Others)
 |   └────── 组权限 (Group)
 └────────── 所有者权限 (Owner)

r = 4 (读)
w = 2 (写)
x = 1 (执行)

755 = rwxr-xr-x (所有者全部权限，其他用户读和执行)
644 = rw-r--r-- (所有者读写，其他用户只读)
600 = rw------- (仅所有者读写)
```

### 常用信号

| 信号 | 编号 | 说明 |
|------|------|------|
| `SIGHUP` | 1 | 挂起信号，常用于重载配置 |
| `SIGINT` | 2 | 中断信号（Ctrl+C） |
| `SIGQUIT` | 3 | 退出信号（Ctrl+\） |
| `SIGKILL` | 9 | 强制终止信号（不可忽略） |
| `SIGTERM` | 15 | 优雅终止信号（默认） |
| `SIGSTOP` | 19 | 暂停信号（不可忽略） |
| `SIGCONT` | 18 | 继续执行信号 |
| `SIGTSTP` | 20 | 终端停止信号（Ctrl+Z） |

### 运行级别

| 级别 | 说明 |
|------|------|
| 0 | 关机 |
| 1 | 单用户模式（维护模式） |
| 2 | 多用户模式（无网络，Debian 默认） |
| 3 | 完全多用户模式（命令行） |
| 4 | 保留未使用 |
| 5 | 图形界面模式 |
| 6 | 重启 |

---

> **说明**：本手册涵盖了 Linux 系统中最常用的命令。部分命令可能需要安装额外的软件包才能使用。使用 `man 命令名` 可以查看每个命令的详细用法和完整参数说明。
>
> 生成日期：2026-08-13
