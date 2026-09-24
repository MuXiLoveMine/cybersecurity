
---

## 四、高级实战案例

### 4.1 高级信息收集脚本

综合的信息收集工具，整合多种侦察技术。

```bash
#!/bin/bash
# ===== 高级信息收集工具 =====

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 输出函数
info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERR]${NC} $1"; }

# ===== WHOIS 查询 =====
whois_lookup() {
    local domain=$1
    info "WHOIS 查询: $domain"
    if command -v whois &> /dev/null; then
        whois "$domain" | grep -E "Registrant|Registrar|Creation Date|Expiration Date|Name Server"
    else
        warn "whois 命令未安装"
    fi
}

# ===== DNS 枚举 =====
dns_enum() {
    local domain=$1
    info "DNS 枚举: $domain"
    
    # A 记录
    echo "A 记录:"
    dig +short A "$domain" 2>/dev/null || nslookup "$domain" 2>/dev/null
    
    # MX 记录
    echo -e "\nMX 记录:"
    dig +short MX "$domain" 2>/dev/null
    
    # NS 记录
    echo -e "\nNS 记录:"
    dig +short NS "$domain" 2>/dev/null
    
    # TXT 记录
    echo -e "\nTXT 记录:"
    dig +short TXT "$domain" 2>/dev/null
    
    # 区域传送测试
    echo -e "\n区域传送测试:"
    for ns in $(dig +short NS "$domain"); do
        if dig @"$ns" "$domain" AXFR 2>/dev/null | grep -q "Transfer failed"; then
            echo "  $ns: 拒绝区域传送"
        else
            echo "  $ns: ${RED}可能存在区域传送漏洞!${NC}"
        fi
    done
}

# ===== 子域名爆破 =====
subdomain_brute() {
    local domain=$1
    local wordlist=$2
    info "子域名爆破: $domain"
    
    if [ ! -f "$wordlist" ]; then
        error "字典文件不存在: $wordlist"
        return
    fi
    
    local count=0
    local found=0
    local total=$(wc -l < "$wordlist")
    
    while read -r sub; do
        count=$((count + 1))
        if [ $((count % 100)) -eq 0 ]; then
            info "进度: $count/$total"
        fi
        
        if dig +short "$sub.$domain" &> /dev/null && [ -n "$(dig +short "$sub.$domain" 2>/dev/null)" ]; then
            echo -e "${GREEN}[+]${NC} $sub.$domain -> $(dig +short "$sub.$domain" | head -1)"
            found=$((found + 1))
        fi
    done < "$wordlist"
    
    info "发现 $found 个子域名"
}

# ===== 端口扫描 =====
port_scan() {
    local host=$1
    local start_port=${2:-1}
    local end_port=${3:-1000}
    local timeout=${4:-0.5}
    
    info "端口扫描: $host ($start_port-$end_port)"
    
    local open_ports=()
    
    for port in $(seq "$start_port" "$end_port"); do
        if timeout "$timeout" bash -c "echo > /dev/tcp/$host/$port" 2>/dev/null; then
            echo -e "${GREEN}[+]${NC} 端口 $port 开放"
            open_ports+=("$port")
        fi
    done
    
    info "扫描完成，发现 ${#open_ports[@]} 个开放端口"
}

# ===== 目录爆破 =====
dir_brute() {
    local url=$1
    local wordlist=$2
    info "目录爆破: $url"
    
    if [ ! -f "$wordlist" ]; then
        error "字典文件不存在: $wordlist"
        return
    fi
    
    url="${url%/}"  # 去掉末尾的 /
    
    while read -r path; do
        local status=$(curl -s -o /dev/null -w "%{http_code}" "$url/$path" 2>/dev/null)
        case "$status" in
            200) echo -e "${GREEN}[200]${NC} /$path" ;;
            301|302) echo -e "${YELLOW}[$status]${NC} /$path" ;;
            403) echo -e "${RED}[403]${NC} /$path" ;;
        esac
    done < "$wordlist"
}

# ===== CMS 识别 =====
cms_detect() {
    local url=$1
    info "CMS 识别: $url"
    
    # 下载首页
    local html=$(curl -s "$url" 2>/dev/null)
    
    # WordPress
    if echo "$html" | grep -qi "wordpress\|wp-content\|wp-includes"; then
        echo -e "${GREEN}[+]${NC} WordPress"
        # 检查版本
        local wp_version=$(echo "$html" | grep -oP 'content="WordPress \K[0-9.]+' | head -1)
        [ -n "$wp_version" ] && echo "    版本: $wp_version"
    fi
    
    # Joomla
    if echo "$html" | grep -qi "joomla\|/templates/"; then
        echo -e "${GREEN}[+]${NC} Joomla"
    fi
    
    # Drupal
    if echo "$html" | grep -qi "drupal\|/sites/all/"; then
        echo -e "${GREEN}[+]${NC} Drupal"
    fi
}

# ===== 主函数 =====
main() {
    local target=$1
    local wordlist=${2:-subdomains.txt}
    
    if [ -z "$target" ]; then
        echo "用法: $0 <domain> [wordlist]"
        echo "示例: $0 example.com subdomains.txt"
        exit 1
    fi
    
    echo "========================================"
    echo "  高级信息收集工具"
    echo "  目标: $target"
    echo "========================================"
    echo ""
    
    whois_lookup "$target"
    echo ""
    dns_enum "$target"
    echo ""
    cms_detect "https://$target"
    echo ""
    
    # 端口扫描常见端口
    port_scan "$target" 1 1000 0.3
}

# main "$@"
```

### 4.2 高级日志分析

Web 日志安全分析脚本，用于检测攻击行为。

```bash
#!/bin/bash
# ===== Web 日志安全分析工具 =====

LOG_FILE=${1:-access.log}

if [ ! -f "$LOG_FILE" ]; then
    echo "日志文件不存在: $LOG_FILE"
    exit 1
fi

echo "===== 日志分析报告 ====="
echo "日志文件: $LOG_FILE"
echo "总请求数: $(wc -l < "$LOG_FILE")"
echo ""

# ===== 1. IP 统计 =====
echo "===== Top 20 IP 访问量 ====="
awk '{print $1}' "$LOG_FILE" | sort | uniq -c | sort -rn | head -20

echo ""

# ===== 2. 状态码统计 =====
echo "===== 状态码分布 ====="
awk '{print $9}' "$LOG_FILE" | sort | uniq -c | sort -rn

echo ""

# ===== 3. 检测 SQL 注入 =====
echo "===== 疑似 SQL 注入 ====="
grep -iE "('|%27|union|select|insert|drop|--|%23|sleep\(|benchmark\(|or 1=1|and 1=1)" "$LOG_FILE" | head -20
echo "共 $(grep -ciE "('|%27|union|select|insert|drop|--|%23)" "$LOG_FILE") 条疑似"

echo ""

# ===== 4. 检测 XSS =====
echo "===== 疑似 XSS 攻击 ====="
grep -iE "(<script|%3Cscript|javascript:|onerror=|onload=|alert\(|%3Cimg)" "$LOG_FILE" | head -20
echo "共 $(grep -ciE "(<script|%3Cscript|javascript:|onerror=|onload=)" "$LOG_FILE") 条疑似"

echo ""

# ===== 5. 检测目录遍历 =====
echo "===== 疑似目录遍历 ====="
grep -E "(\.\./|\.\.%2f|%2e%2e%2f|etc/passwd|boot\.ini)" "$LOG_FILE" | head -20
echo "共 $(grep -cE "(\.\./|\.\.%2f|%2e%2e%2f)" "$LOG_FILE") 条疑似"

echo ""

# ===== 6. 检测暴力破解 =====
echo "===== 登录爆破检测 ====="
grep -i "login\|signin\|wp-login" "$LOG_FILE" | awk '{print $1}' | sort | uniq -c | sort -rn | awk '$1 > 10'
echo "（同一IP登录请求超过10次）"

echo ""

# ===== 7. 扫描器特征 =====
echo "===== 扫描器/爬虫 ====="
grep -iE "(sqlmap|nmap|nikto|acunetix|nessus|burp|scanner|bot|crawler)" "$LOG_FILE" | awk '{print $1}' | sort -u

echo ""

# ===== 8. 404 最多的路径 =====
echo "===== Top 20 404 路径 ====="
awk '$9 == 404 {print $7}' "$LOG_FILE" | sort | uniq -c | sort -rn | head -20

echo ""

# ===== 9. 访问最多的页面 =====
echo "===== Top 20 访问最多页面 ====="
awk '{print $7}' "$LOG_FILE" | sort | uniq -c | sort -rn | head -20

echo ""

# ===== 10. 按小时统计 =====
echo "===== 每小时访问量 ====="
awk '{print substr($4, 14, 2)}' "$LOG_FILE" | sort | uniq -c | sort -k2
```

### 4.3 提权枚举脚本

Linux 提权信息收集脚本，用于寻找提权路径。

```bash
#!/bin/bash
# ===== Linux 提权枚举脚本 =====

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info() { echo -e "${GREEN}[+]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
vuln() { echo -e "${RED}[VULN]${NC} $1"; }

echo "=================================="
echo "  Linux 提权枚举脚本"
echo "=================================="
echo ""

# ===== 1. 系统信息 =====
echo "===== 系统信息 ====="
info "主机名: $(hostname)"
info "内核版本: $(uname -r)"
info "发行版: $(cat /etc/os-release 2>/dev/null | grep PRETTY_NAME | cut -d'"' -f2)"
info "架构: $(uname -m)"
info "当前用户: $(whoami) ($(id))"
info "当前路径: $(pwd)"
echo ""

# ===== 2. 用户信息 =====
echo "===== 用户信息 ====="
info "UID: $(id -u), GID: $(id -g)"
info "所属组: $(id -Gn)"
info "是否 root: $( [ $(id -u) -eq 0 ] && echo '是' || echo '否' )"
echo ""
info "可登录用户:"
grep -E ":/bin/(bash|sh|zsh)" /etc/passwd
echo ""

# ===== 3. Sudo 权限 =====
echo "===== Sudo 权限 ====="
if sudo -n -l 2>/dev/null; then
    warn "可以无密码使用 sudo"
    sudo -l 2>/dev/null | grep -E "NOPASSWD|ALL" | while read line; do
        vuln "sudo 命令: $line"
    done
else
    info "需要密码才能使用 sudo"
fi
echo ""

# ===== 4. SUID/SGID 文件 =====
echo "===== SUID 文件 ====="
suid_files=$(find / -perm -4000 -type f 2>/dev/null)
if [ -n "$suid_files" ]; then
    echo "$suid_files"
    # 检查可利用的 SUID
    for bin in nmap vim find bash python perl ruby; do
        if echo "$suid_files" | grep -q "$bin"; then
            vuln "可利用的 SUID: $bin"
        fi
    done
else
    info "未找到 SUID 文件（或无权限）"
fi
echo ""

# ===== 5. 可写文件 =====
echo "===== 可写的敏感文件 ====="
for file in /etc/passwd /etc/shadow /etc/sudoers /etc/crontab; do
    if [ -w "$file" ]; then
        vuln "$file 可写!"
    fi
done
echo ""

# ===== 6. 定时任务 =====
echo "===== 定时任务 ====="
if [ -r /etc/crontab ]; then
    cat /etc/crontab 2>/dev/null
fi
echo ""
ls -la /etc/cron.* 2>/dev/null
echo ""
ls -la /var/spool/cron/ 2>/dev/null
echo ""

# ===== 7. 内核漏洞 =====
echo "===== 内核版本检查 ====="
kernel_version=$(uname -r)
info "内核版本: $kernel_version"

# 检查一些著名的内核漏洞
major=$(echo "$kernel_version" | cut -d. -f1)
minor=$(echo "$kernel_version" | cut -d. -f2)

if [ "$major" -eq 2 ] && [ "$minor" -lt 6 ]; then
    warn "可能存在多个内核漏洞"
fi
echo ""

# ===== 8. 正在运行的服务 =====
echo "===== 监听端口 ====="
netstat -tulnp 2>/dev/null || ss -tulnp 2>/dev/null
echo ""

# ===== 9. 环境变量 =====
echo "===== 环境变量 ====="
env | grep -iE "path|ld_preload|ld_library_path"
echo ""

# ===== 10. 密码信息 =====
echo "===== 密码哈希可读性 ====="
if [ -r /etc/shadow ]; then
    vuln "/etc/shadow 可读！"
    head -5 /etc/shadow
else
    info "/etc/shadow 不可读"
fi
echo ""

# ===== 11. 已知的提权程序 =====
echo "===== 检查 GTFOBins 候选 ====="
for cmd in python perl ruby lua find nmap vim bash less more; do
    if command -v "$cmd" &> /dev/null; then
        info "$cmd 可用"
    fi
done

echo ""
echo "枚举完成！"
```

---

## 五、进阶学习资源

### 5.1 Shell 脚本高级技巧

- **Bash Hackers Wiki**：https://wiki.bash-hackers.org/ — Bash 高级技巧
- **Advanced Bash-Scripting Guide**：https://tldp.org/LDP/abs/html/ — 高级 Bash 脚本指南
- **Shellcheck**：https://www.shellcheck.net/ — Shell 脚本静态检查工具
- **Explainshell**：https://explainshell.com/ — 解析复杂 Shell 命令

### 5.2 渗透测试 Shell 脚本

- **LinEnum**：https://github.com/rebootuser/LinEnum — Linux 提权枚举脚本
- **linux-exploit-suggester**：https://github.com/mzet-/linux-exploit-suggester — 内核漏洞检测
- **LinPEAS / WinPEAS**：https://github.com/carlospolop/PEASS-ng — 权限提升枚举
- **pspy**：https://github.com/DominicBreuker/pspy — 无需 root 监控进程
- **Linux Smart Enumeration**：https://github.com/diego-treitos/linux-smart-enumeration

### 5.3 提权与后渗透

- **GTFOBins**：https://gtfobins.github.io/ — Unix 二进制提权
- **LOLBAS**：https://lolbas-project.github.io/ — Windows 内置工具利用
- **WADComs**：https://wadcoms.github.io/ — AD 攻击命令
- **PayloadsAllTheThings**：https://github.com/swisskyrepo/PayloadsAllTheThings
- **Reverse Shell Generator**：https://www.revshells.com/ — 反弹 Shell 生成器

### 5.4 网络工具与分析

- **tcpdump**：经典网络抓包工具
- **Wireshark / tshark**：网络协议分析
- **nmap**：网络扫描器
- **masscan**：高速端口扫描
- **netcat / ncat / socat**：网络瑞士军刀
- **hping3**：网络数据包组装/分析
- **aircrack-ng**：无线网络安全工具

### 5.5 日志分析与取证

- **日志分析工具**：
  - grep / awk / sed — 命令行文本处理三件套
  - goaccess — 实时 Web 日志分析
  - awstats — Web 日志统计
  - ELK Stack — 日志分析平台

- **取证工具**：
  - autopsy / sleuthkit — 数字取证工具
  - volatility — 内存取证
  - foremost — 文件 carving
  - binwalk — 固件分析

### 5.6 CTF 与练习平台

- **OverTheWire**：https://overthewire.org/wargames/ — 经典 wargame
- **Bandit**：https://overthewire.org/wargames/bandit/ — 适合初学者
- **Natas**：https://overthewire.org/wargames/natas/ — Web 安全
- **Krypton**：https://overthewire.org/wargames/krypton/ — 密码学
- **VulnHub**：https://www.vulnhub.com/ — 漏洞靶机
- **Hack The Box**：https://www.hackthebox.com/
- **TryHackMe**：https://tryhackme.com/
- **Bugku**：https://ctf.bugku.com/

### 5.7 推荐书籍

- **Shell 脚本**：
  - 《Linux Shell 脚本攻略》
  - 《Bash 脚本学习指南》
  - 《高级 Bash 脚本编程指南》

- **网络安全**：
  - 《Wireshark 网络分析实战》
  - 《TCP/IP 详解》
  - 《网络安全监测与分析》

- **渗透测试**：
  - 《Kali Linux 高级渗透测试》
  - 《Metasploit 魔鬼训练营》
  - 《高级渗透测试》

- **系统底层**：
  - 《鸟哥的 Linux 私房菜》
  - 《Linux 内核设计与实现》
  - 《UNIX 环境高级编程》

### 5.8 社区与博客

- **Exploit-DB**：https://www.exploit-db.com/
- **Packet Storm**：https://packetstormsecurity.com/
- **FreeBuf**：https://www.freebuf.com/
- **安全客**：https://www.anquanke.com/
- **先知社区**：https://xz.aliyun.com/
- **看雪学院**：https://www.kanxue.com/

### 5.9 进阶学习路线

**第 1 阶段：Shell 脚本精通（1-2月）**
- 掌握 bash 高级语法（数组、关联数组、正则）
- 熟练使用 awk/sed/grep 文本处理三剑客
- 学习编写复杂脚本和工具

**第 2 阶段：Linux 系统深入（2-3月）**
- 深入理解 Linux 文件系统、权限、进程
- 学习系统调用和内核基础知识
- 掌握 Linux 常用服务配置与安全

**第 3 阶段：网络安全工具（2-3月）**
- nmap 高级扫描技术
- tcpdump/Wireshark 流量分析
- 各种网络协议深入理解

**第 4 阶段：渗透测试与提权（3-4月）**
- 信息收集与侦察技术
- 漏洞利用与提权方法
- 后渗透与内网横向移动

**第 5 阶段：实战与 CTF（持续）**
- 参加 CTF 比赛
- 打靶机练手（VulnHub/HTB）
- 开发自己的工具脚本
- 研究新的攻击技术
