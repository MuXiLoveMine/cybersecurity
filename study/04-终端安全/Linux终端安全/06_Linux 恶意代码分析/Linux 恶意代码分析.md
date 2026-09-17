# Linux 恶意代码分析

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

---

## 📋 内容审核与补充建议

> 针对「Linux 恶意代码分析」部分的内容审核结果：

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

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
