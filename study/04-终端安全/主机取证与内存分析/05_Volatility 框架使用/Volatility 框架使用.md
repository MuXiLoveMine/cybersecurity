# Volatility 框架使用

### 5.1 安装与基础

```bash
# Volatility 2 (Python 2 - 经典版本)
pip install volatility
# 需要对应的 profile 文件

# Volatility 3 (Python 3 - 推荐版本)
pip install volatility3

# 基本用法 (Volatility 3)
python vol.py -f memory.raw windows.info          # 系统信息
python vol.py -f memory.raw windows.pslist        # 进程列表
python vol.py -f memory.raw windows.netscan       # 网络连接
python vol.py -f memory.raw windows.filescan     # 文件扫描
python vol.py -f memory.raw windows.dumpfiles    # 提取文件
python vol.py -f memory.raw windows.handles      # 句柄
python vol.py -f memory.raw windows.malfind       # 注入检测
python vol.py -f memory.raw windows.registry.*   # 注册表
python vol.py -f memory.raw windows.hashdump     # 密码哈希
python vol.py -f memory.raw windows.cmdline      # 命令行
```

### 5.2 关键命令详解

**（1）imageinfo / 系统信息**

```bash
# Volatility 2
vol.py -f memory.raw --profile=Win10x64_19041 imageinfo

# Volatility 3
python vol.py -f memory.raw windows.info

# 输出示例:
# DTB: 0x1ab000
# Win10x64_19041
# NtBuildNumber: 19041
# KdDebuggerEnabled: False
# CheckedBuild: 0
```

**（2）pslist / 进程列表**

```bash
# 进程列表（按 EPROCESS 链表遍历）
python vol.py -f memory.raw windows.pslist

# 进程树（显示父子关系）
python vol.py -f memory.raw windows.pstree

# 输出示例:
# PID   PPID  ImageFileName      Threads Handles
# 4     0     System              152    0
# 684   4     smss.exe            2      0
# 768   684   csrss.exe           13     0
# 852   768   winlogon.exe        4      0
# ...
# 4520  852   powershell.exe      11     156   ← 可疑进程
# 5644  4520  cmd.exe             1      32    ← PowerShell 子进程

# 检测异常:
# - 进程名与系统进程不符 (如小写的 svchost.exe)
# - PPID 异常 (svchost.exe 父进程不是 services.exe)
# - 无 PPID 的孤儿进程
# - 短暂存在已退出的进程 (psscan 可发现)
```

**（3）psscan / 隐藏进程检测**

```bash
# 扫描内存中所有 EPROCESS 结构（不依赖链表）
# 可发现被 Rootkit 从链表中摘除的隐藏进程

python vol.py -f memory.raw windows.psscan

# 对比 pslist 和 psscan 的差异
# psscan 找到但 pslist 没有的进程 = 隐藏进程
```

**（4）netscan / 网络连接**

```bash
# 提取内存中的网络连接信息
python vol.py -f memory.raw windows.netscan

# 输出示例:
# Offset     Proto  LocalAddr      LocalPort  ForeignAddr  ForeignPort  State     PID
# 0x12345    TCP    0.0.0.0:0     0          10.0.0.5     443          SYN_SENT  4520
# 0x67890    TCP    0.0.0.0:135   0          0.0.0.0:0    0            LISTEN    768
# 0xABCDE    TCP    192.168.1.100:49152  10.8.8.8:443  ESTABLISHED 5644  ← C2连接?

# 可疑指标:
# - 到未知外网IP的ESTABLISHED连接
# - 非常规端口(如非443/80的出站连接)
# - LISTEN端口异常
# - 已知C2 IP地址匹配
```

**（5）malfind / 注入检测**

```bash
# 检测进程内存中的注入代码
python vol.py -f memory.raw windows.malfind -p 4520

# 输出示例:
# Process: powershell.exe (4520)
# Range: 0x1a000000 - 0x1a001000
# Tag: MEM_PRIVATE
# Protection: PAGE_EXECUTE_READWRITE  ← 可执行+可写 = 注入特征
# Disasm:
# 0x1a000000  48 83 ec 28       sub rsp, 0x28
# 0x1a000004  48 8b 05 f0 00 00 mov rax, [rip+0xf0]
# 0x1a00000b  ff d0             call rax  ← shellcode 调用

# 判断标准:
# 1. 内存区域为 PRIVATE (私有分配)
# 2. 保护属性为 RWX (可读可写可执行)
# 3. 包含可执行代码 (非数据)
# 4. 无对应磁盘文件 (内存中独立存在)
```

**（6）hashdump / 凭据提取**

```bash
# 从内存中提取 NTLM 哈希
python vol.py -f memory.raw windows.hashdump --lsa

# 输出示例:
# Administrator:500:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
# Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
# user1:1001:aad3b435b51404eeaad3b435b51404ee:8846f7eaee8fb117ad06bddbb7b06477:::

# 哈希格式: RID:LM_Hash:NT_Hash:::
# 可使用 hashcat/john 离线破解 NTLM 哈希
# hashcat -m 1000 hashes.txt wordlist.txt
```

**（7）文件提取**

```bash
# 扫描内存中的文件对象
python vol.py -f memory.raw windows.filescan | grep -i "temp\|powershell\|malware"

# 提取内存中的文件
python vol.py -f memory.raw windows.dumpfiles --virtaddr 0xFFFFAB001234
python vol.py -f memory.raw windows.dumpfiles --pid 4520

# 提取进程可执行文件
python vol.py -f memory.raw windows.pslist --pid 4520 --dump
```

### 5.3 内存取证实战场景

```
场景1: 恶意代码检测
步骤:
1. pslist + pstree → 查找可疑进程
2. malfind → 检测注入代码
3. dumpfiles → 提取恶意文件
4. netscan → 检查C2连接
5. cmdline → 查看进程命令行
6. handles → 检查打开的文件和资源

场景2: 凭据提取
步骤:
1. hashdump → 提取NTLM哈希
2. lsadump → 提取LSA密钥
3. clipboard → 提取剪贴板内容
4. hashdump --lsa → 提取LSASS中的凭据

场景3: 网络连接恢复
步骤:
1. netscan → 所有TCP/UDP连接
2. 结合进程PID对应到具体进程
3. 检查连接状态(LISTEN/ESTABLISHED)
4. 匹配威胁情报(已知C2 IP/域名)

场景4: 注入检测
步骤:
1. malfind → 扫描所有进程的注入代码
2. 检查 RWX 私有内存区域
3. 提取注入代码进行逆向分析
4. 对比合法DLL加载情况
```

---

---

