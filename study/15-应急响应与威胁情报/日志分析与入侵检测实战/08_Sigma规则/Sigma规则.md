# Sigma规则

Sigma是一种通用的签名格式，用于跨SIEM平台的检测规则共享。

```yaml
# Sigma规则示例 - 检测Mimikatz
title: Mimikatz Process Detection
id: f1234567-89ab-cdef-0123-456789abcdef
status: experimental
description: |
  检测Mimikatz凭证提取工具的执行。
  Mimikatz常用于从LSASS内存中提取凭据。
references:
  - https://github.com/gentilkiwi/mimikatz
author: Security Team
date: 2026/09/13
logsource:
  product: windows
  service: security
detection:
  selection_process:
    EventID: 4688
    NewProcessName|endswith: 'mimikatz.exe'
  selection_commandline:
    EventID: 4688
    CommandLine|contains:
      - 'sekurlsa'
      - 'lsadump'
      - 'kerberos'
      - 'privilege::debug'
  condition: selection_process or selection_commandline
falsepositives:
  - 安全研究人员使用
  - 红队演练
level: high
tags:
  - attack.credential_access
  - attack.t1003
  - attack.t1003.001
```

```yaml
# Sigma规则 - 检测可疑PowerShell编码命令
title: PowerShell Encoded Command Execution
id: a1b2c3d4-e5f6-7890-abcd-ef1234567890
status: stable
description: 检测使用编码参数执行PowerShell的恶意行为
references:
  - https://attack.mitre.org/techniques/T1059/001/
author: Security Team
date: 2026/09/13
logsource:
  product: windows
  service: security
detection:
  selection:
    EventID: 4688
    NewProcessName|endswith: '\powershell.exe'
    CommandLine|contains:
      - '-enc '
      - '-encodedcommand '
      - '-e '
      - '/encodedcommand '
  condition: selection
falsepositives:
  - 合法的管理脚本
  - 自动化运维工具
level: high
tags:
  - attack.execution
  - attack.t1059.001
```

```yaml
# Sigma规则 - 检测横向移动(RDP)
title: RDP from Untrusted Source
id: b2c3d4e5-f678-90ab-cdef-123456789abc
status: stable
description: 检测来自非信任网络的RDP连接
author: Security Team
date: 2026/09/13
logsource:
  product: windows
  service: security
detection:
  selection:
    EventID: 4624
    LogonType: 10
  filter_trusted:
    IpAddress|cidr:
      - '10.0.0.0/8'
      - '172.16.0.0/12'
      - '192.168.0.0/16'
  condition: selection and not filter_trusted
falsepositives:
  - VPN连接后RDP
  - 外部管理员访问
level: medium
tags:
  - attack.lateral_movement
  - attack.t1021.001
```

---

> **参考资源**
>
> - MITRE ATT&CK - attack.mitre.org
> - Sigma Project - github.com/SigmaHQ/sigma
> - Splunk SPL Reference - docs.splunk.com/Splex
> - ELK Documentation - elastic.co/guide
> - Windows Security Event IDs - docs.microsoft.com
> - SwiftOnSecurity Sysmon Config - github.com/SwiftOnSecurity

---

## 📋 内容审核与补充建议

> 针对「Sigma规则」部分的内容审核结果：

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

### ⚔️ 攻击技术
- ⚠️ 缺少attack相关内容

---

## 📌 拓展学习资源

### 推荐学习路径
- 理论基础 → 工具实践 → 实战演练 → 深度研究
- 建议搭建本地实验环境进行动手练习

### 相关工具与资源
- 在线实验平台：Hack The Box、TryHackMe、VulnHub
- 技术文档：官方文档、RFC、OWASP 指南
- 社区资源：GitHub、安全论坛、技术博客

---

## 🛠️ 补充：实战拓展

### 一、日志分析常用命令速查（grep/awk/sed）

#### 1. grep 常用命令速查

```bash
# ========== 基础搜索 ==========

# 简单搜索
grep "pattern" filename

# 不区分大小写
grep -i "error" /var/log/syslog

# 显示行号
grep -n "404" access.log

# 只显示匹配的行数
grep -c "Failed password" /var/log/secure

# 反向匹配（不包含模式的行）
grep -v "200" access.log

# 递归搜索目录
grep -r "pattern" /var/log/
grep -R "pattern" /var/log/  # 跟随符号链接

# 只显示匹配的文件名
grep -l "error" /var/log/*.log

# 只显示不匹配的文件名
grep -L "error" /var/log/*.log

# ========== 高级搜索 ==========

# 扩展正则表达式（等同于 egrep）
grep -E "error|warning|critical" /var/log/syslog

# 匹配整行
grep -x "complete" status.log

# 匹配单词边界
grep -w "root" /var/log/auth.log  # 只匹配"root"单词，不匹配"rootuser"

# Perl正则表达式
grep -P "\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}" access.log

# ========== 输出控制 ==========

# 显示匹配行及其后N行
grep -A 5 "error" app.log      # 显示匹配行和后5行

# 显示匹配行及其前N行
grep -B 3 "error" app.log      # 显示匹配行和前3行

# 显示匹配行及其前后N行
grep -C 3 "error" app.log      # 显示匹配行和前后各3行

# 只输出匹配的部分
grep -o "IP: [0-9.]*" access.log

# 颜色高亮
grep --color=auto "error" app.log

# ========== 常用实战命令 ==========

# 统计IP访问次数
grep -oE "[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+" access.log | sort | uniq -c | sort -rn | head -20

# 查找特定状态码的请求
grep " 404 " access.log | head -20
grep " 500 " access.log | wc -l

# 查找特定时间范围的日志
grep "15/Mar/2026:1[4-7]" access.log  # 14点到17点

# 查找SQL注入特征
grep -iE "union.*select|or 1=1|drop table|-- " access.log

# 查找XSS特征
grep -iE "<script|javascript:|onerror=" access.log

# 搜索暴力破解（SSH登录失败）
grep "Failed password" /var/log/secure | awk '{print $11}' | sort | uniq -c | sort -rn | head -10

# 搜索多个关键词（满足任一）
grep -E "error|fatal|panic|critical" /var/log/syslog

# 搜索必须同时满足的条件（管道）
grep "error" app.log | grep "database" | grep "timeout"
```

#### 2. awk 常用命令速查

```bash
# ========== 基础语法 ==========

# 打印指定列（默认空格分隔）
awk '{print $1}' access.log      # 第1列
awk '{print $1, $9}' access.log  # 第1列和第9列

# 打印最后一列
awk '{print $NF}' access.log

# 打印倒数第二列
awk '{print $(NF-1)}' access.log

# 打印行号
awk '{print NR, $0}' access.log

# 指定字段分隔符
awk -F: '{print $1, $3}' /etc/passwd       # 冒号分隔
awk -F'|' '{print $1, $2}' data.csv        # 竖线分隔
awk -F'[][]' '{print $2}' access.log       # 方括号分隔

# 多个分隔符
awk -F'[ :]' '{print $1, $5}' access.log

# ========== 条件过滤 ==========

# 按列值过滤
awk '$9 == 404 {print $1, $7}' access.log      # 状态码=404
awk '$9 >= 500 {print $0}' access.log          # 5xx错误

# 字符串匹配
awk '$7 ~ /\.php/ {print $0}' access.log       # URL包含.php
awk '$7 !~ /\.css/ {print $0}' access.log      # URL不包含.css

# 正则匹配整行
awk '/error/ {print $0}' app.log

# 多条件
awk '$9 == 200 && $NF > 10000 {print $1, $7, $NF}' access.log

# ========== 统计计算 ==========

# 数值求和
awk '{sum += $NF} END {print "总字节数:", sum}' access.log

# 平均值
awk '{sum += $NF; count++} END {print "平均:", sum/count}' access.log

# 最大值/最小值
awk 'NR==1{max=$NF;min=$NF} {if($NF>max)max=$NF; if($NF<min)min=$NF} END{print "max:",max,"min:",min}' access.log

# 按字段统计次数
awk '{count[$9]++} END {for(code in count) print code, count[code]}' access.log | sort -rn

# 按IP统计访问次数
awk '{count[$1]++} END {for(ip in count) print count[ip], ip}' access.log | sort -rn | head -20

# ========== 字符串处理 ==========

# 字符串长度
awk '{print length($1), $1}' access.log

# 截取子串
awk '{print substr($4, 2, 11)}' access.log    # 从第2字符开始，取11个字符

# 字符串替换
awk '{gsub(/\//, "-", $4); print $4}' access.log  # 将/替换为-

# 转换大小写
awk '{print toupper($1)}' access.log
awk '{print tolower($1)}' access.log

# ========== 数组与循环 ==========

# 按IP+URL统计
awk '{key=$1"|"$7; count[key]++} END {for(k in count) print count[k], k}' access.log | sort -rn | head -10

# ========== 实战场景 ==========

# 统计每个IP的404请求数
awk '$9 == 404 {count[$1]++} END {for(ip in count) print count[ip], ip}' access.log | sort -rn

# 计算平均响应时间（假设第10列是响应时间）
awk '{sum += $10; n++} END {printf "平均响应时间: %.2fms\n", sum/n}' access.log

# 按小时统计请求数
awk -F'[:/]' '{hour=$5; count[hour]++} END {for(h in count) print h, count[h]}' access.log | sort

# 提取所有唯一的URL
awk '{print $7}' access.log | sort -u | wc -l

# 统计每个状态码的流量
awk '{bytes[$9] += $NF; count[$9]++} END {for(code in bytes) print code, count[code], bytes[code]}' access.log
```

#### 3. sed 常用命令速查

```bash
# ========== 基本替换 ==========

# 替换每行第一个匹配
sed 's/old/new/' filename

# 全局替换（每行所有匹配）
sed 's/old/new/g' filename

# 替换第N个匹配
sed 's/old/new/2' filename

# 不区分大小写（GNU sed）
sed 's/old/new/gi' filename

# 就地修改文件
sed -i 's/old/new/g' filename

# 备份原文件并修改
sed -i.bak 's/old/new/g' filename

# ========== 行操作 ==========

# 删除指定行
sed '5d' filename        # 删除第5行
sed '2,5d' filename      # 删除第2-5行
sed '$d' filename        # 删除最后一行
sed '1,3!d' filename     # 只保留第1-3行

# 删除匹配行
sed '/pattern/d' filename
sed '/error/d' app.log   # 删除包含error的行

# 删除空行
sed '/^$/d' filename
sed '/^\s*$/d' filename  # 包括只有空白字符的行

# 删除首行/尾行
sed '1d' filename
sed '$d' filename

# ========== 插入与追加 ==========

# 在匹配行前插入
sed '/pattern/i\插入的内容' filename

# 在匹配行后追加
sed '/pattern/a\追加的内容' filename

# 在第N行前插入
sed '3i\新的第三行' filename

# 在末尾追加
sed '$a\最后一行内容' filename

# ========== 行替换 ==========

# 替换整行
sed '/pattern/c\替换内容' filename

# 替换第N行
sed '5c\第五行内容' filename

# ========== 打印控制 ==========

# 只打印匹配行（等同grep）
sed -n '/pattern/p' filename

# 打印指定行
sed -n '5p' filename     # 打印第5行
sed -n '2,5p' filename   # 打印第2-5行
sed -n '5,$p' filename   # 打印第5行到末尾

# 打印匹配行及其前后行
sed -n '/pattern/,+3p' filename  # 匹配行和后3行

# 显示行号
sed = filename | sed 'N;s/\n/\t/'

# ========== 正则提取 ==========

# 提取IP地址
sed -n 's/.*\([0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\).*/\1/p' access.log

# 提取日期
sed -n 's/.*\[\(.*?)\).*/\1/p' access.log

# 提取URL
sed -n 's/.*GET \(.*\) HTTP.*/\1/p' access.log

# ========== 实战场景 ==========

# 去除日志中的注释行
sed '/^#/d' config.conf

# 去除重复空行
sed '/^$/{N;/^\n$/d}' filename

# 去除首尾空白字符
sed 's/^[ \t]*//;s/[ \t]*$//' filename

# 转换Windows换行符为Unix
sed -i 's/\r$//' filename

# 处理日志：提取IP和URL，去除状态码200
sed -n 's/^\([0-9.]*\) .* GET \(.*\) HTTP.* 200 .*/\1 \2/p' access.log | grep -v " 200 "

# 批量替换配置文件中的IP
sed -i 's/192\.168\.1\.1/10.0.0.1/g' *.conf
```

#### 4. 其他日志分析常用命令

```bash
# ========== 排序与去重 ==========

# 按数值倒序排序
sort -rn access.log

# 按指定列排序
sort -k9 -n access.log    # 按第9列数值排序
sort -k1,1 -k2,2 file     # 先按第1列，再按第2列

# 去重
sort filename | uniq
sort -u filename          # 同上

# 统计重复次数
sort filename | uniq -c
sort filename | uniq -c | sort -rn

# 只显示重复行
sort filename | uniq -d

# 只显示唯一行
sort filename | uniq -u

# ========== 查看文件 ==========

# 查看前N行
head -n 20 filename
head -20 filename

# 查看后N行
tail -n 20 filename
tail -20 filename

# 实时查看
tail -f filename
tail -F filename          # 文件重建后继续跟踪

# 查看中间部分
sed -n '100,200p' filename
head -200 filename | tail -100

# ========== 切割与合并 ==========

# 提取列
cut -d' ' -f1,7 access.log       # 空格分隔
cut -d':' -f1,3 /etc/passwd      # 冒号分隔

# 合并两个文件（按列）
paste file1.txt file2.txt

# 合并两个文件（按行）
cat file1.txt file2.txt > combined.txt

# ========== 日志统计 ==========

# 统计行数
wc -l access.log

# 统计字节数
wc -c access.log

# 统计单词数
wc -w access.log

# ========== xargs 批量处理 ==========

# 批量搜索文件
find /var/log -name "*.log" | xargs grep "error"

# 批量处理
cat ioc_list.txt | xargs -I {} grep {} access.log

# ========== 组合命令实战 ==========

# 统计访问量TOP10的IP
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -10

# 统计访问量TOP10的URL
awk '{print $7}' access.log | sort | uniq -c | sort -rn | head -10

# 找出状态码分布
awk '{print $9}' access.log | sort | uniq -c | sort -rn

# 按小时统计访问量
awk -F'[:]' '{print $2":"$3}' access.log | cut -d: -f1,2 | sort | uniq -c

# 找出攻击特征：同一IP短时间内大量请求
awk '{print $1, substr($4, 2, 14)}' access.log | sort | uniq -c | sort -rn | head -20
```

### 二、日志分析工具速查表

#### 1. 命令行日志分析工具

| 工具 | 平台 | 用途 | 常用命令 |
|------|------|------|---------|
| **grep/egrep** | Linux/Unix | 文本搜索 | `grep -r "pattern" /path` |
| **awk** | Linux/Unix | 文本处理 | `awk '{print $1}' file` |
| **sed** | Linux/Unix | 文本编辑 | `sed 's/old/new/g' file` |
| **sort** | Linux/Unix | 排序 | `sort -rn file` |
| **uniq** | Linux/Unix | 去重统计 | `sort file \| uniq -c` |
| **wc** | Linux/Unix | 统计 | `wc -l file` |
| **find** | Linux/Unix | 文件查找 | `find / -mtime -1 -type f` |
| **xargs** | Linux/Unix | 批量处理 | `find . -name *.log \| xargs grep error` |
| **jq** | 跨平台 | JSON处理 | `jq '.key' file.json` |
| **gron** | 跨平台 | JSON扁平化 | `gron file.json \| grep key` |
| **lnav** | Linux | 日志查看器 | `lnav /var/log/syslog` |
| **multitail** | Linux | 多文件tail | `multitail file1 file2` |
| **ccze** | Linux | 日志着色 | `tail -f app.log \| ccze` |
| **logrotate** | Linux | 日志轮转 | `logrotate /etc/logrotate.conf` |

#### 2. 图形化日志分析工具

| 工具 | 平台 | 类型 | 特点 |
|------|------|------|------|
| **ELK Stack** | 跨平台 | 开源 | Elasticsearch+Logstash+Kibana，最流行的日志分析平台 |
| **Splunk** | 跨平台 | 商业 | 功能强大，搜索语言SPL，企业级首选 |
| **Graylog** | 跨平台 | 开源 | 轻量级，GELF协议，易部署 |
| **Grafana Loki** | 跨平台 | 开源 | 云原生，轻量索引，与Grafana集成 |
| **Fluentd/Fluent Bit** | 跨平台 | 开源 | 日志收集与转发，CNCF项目 |
| **Apache Flume** | 跨平台 | 开源 | 分布式日志收集，Hadoop生态 |
| **Logstash** | 跨平台 | 开源 | 日志收集处理管道，ELK组件之一 |
| **NXLog** | 跨平台 | 开源/商业 | 多平台日志收集，高性能 |

#### 3. Windows 日志分析工具

| 工具 | 用途 | 说明 |
|------|------|------|
| **Event Viewer** | 事件查看器 | 系统自带，图形化查看事件日志 |
| **wevtutil** | 命令行日志工具 | 系统自带，查询、导出、清除日志 |
| **Log Parser** | 日志查询工具 | 微软官方，支持SQL语法查询多种日志 |
| **Event Log Explorer** | 事件日志分析 | 第三方工具，支持过滤、排序、导出 |
| **WinLogBeat** | 日志收集 | Elastic出品，Windows日志转发到ELK |
| **NXLog Community** | 日志转发 | 开源，支持Windows日志收集 |
| **Sysmon** | 系统监控 | Sysinternals工具，增强进程/网络/文件监控 |

**Log Parser 常用命令：**

```cmd
:: 查询安全日志中的登录事件
LogParser "SELECT TimeGenerated,EventID,Message FROM Security WHERE EventID=4624" -i:EVT

:: 查询最近24小时的登录失败
LogParser "SELECT TimeGenerated,EXTRACT_TOKEN(Strings,5,'|') AS UserName,EXTRACT_TOKEN(Strings,18,'|') AS IP FROM Security WHERE EventID=4625 AND TimeGenerated > SUB(SYSTEM_TIMESTAMP(), TIMESTAMP('24','h'))" -i:EVT

:: 导出IIS日志统计
LogParser "SELECT cs-uri-stem, COUNT(*) AS Hits INTO results.csv FROM u_ex*.log GROUP BY cs-uri-stem ORDER BY Hits DESC" -i:IISW3C -o:CSV

:: 按IP统计访问量
LogParser "SELECT c-ip, COUNT(*) AS Hits FROM u_ex*.log GROUP BY c-ip ORDER BY Hits DESC" -i:IISW3C
```

#### 4. Web 日志分析工具

| 工具 | 平台 | 特点 | 常用命令 |
|------|------|------|---------|
| **GoAccess** | Linux | 实时，终端UI | `goaccess access.log -c` |
| **AWStats** | 跨平台 | 老牌，功能全 | `perl awstats.pl -config=site -update` |
| **Webalizer** | Linux | 轻量，快速 | `webalizer access.log` |
| **HTTPry** | Linux | 实时HTTP流量 | `httpry -i eth0` |
| **HTTPie** | 跨平台 | HTTP客户端 | `http https://example.com` |

**GoAccess 常用命令：**

```bash
# 终端实时查看
goaccess access.log

# 指定日志格式
goaccess access.log --log-format=COMBINED

# 生成HTML报告
goaccess access.log -o report.html --log-format=COMBINED

# 实时生成HTML报告
goaccess access.log -o report.html --real-time-html --log-format=COMBINED

# 多文件分析
goaccess access.log access.log.1 -o report.html --log-format=COMBINED

# 过滤指定IP范围
goaccess access.log --ignore-panel=OS --ignore-panel=BROWSERS
```

#### 5. 日志聚合与SIEM工具

| 工具 | 类型 | 核心功能 | 适用场景 |
|------|------|---------|---------|
| **Splunk Enterprise** | 商业 | 日志收集、搜索、可视化、告警 | 大型企业 |
| **ELK Stack** | 开源 | Elasticsearch存储、Logstash收集、Kibana展示 | 中大型企业 |
| **Wazuh** | 开源 | HIDS+SIEM一体化，集成OSSEC | 中小企业 |
| **Security Onion** | 开源 | 网络安全监控平台，集成ELK/Suricata等 | 安全运营中心 |
| **AlienVault OSSIM** | 开源/商业 | 开源SIEM，集成多种安全工具 | 中小企业 |
| **QRadar** | 商业 | IBM企业级SIEM | 大型企业 |
| **ArcSight** | 商业 | Micro Focus企业级SIEM | 大型企业 |
| **LogRhythm** | 商业 | 下一代SIEM平台 | 中大型企业 |

### 三、日志分析实战场景

#### 场景1：暴力破解检测

```bash
# SSH暴力破解检测
grep "Failed password" /var/log/secure | \
    awk '{print $11}' | \
    sort | \
    uniq -c | \
    sort -rn | \
    awk '$1 > 10 {print $0}'

# 按用户统计失败次数
grep "Failed password" /var/log/secure | \
    awk '{for(i=1;i<=NF;i++) if($i=="for") {print $(i+1); break}}' | \
    sort | uniq -c | sort -rn

# Windows RDP暴力破解
wevtutil qe Security /q:"*[System/EventID=4625]" /c:100 /f:text /rd:true | \
    findstr /c:"Account Name" /c:"Source Network Address"
```

#### 场景2：Web攻击检测

```bash
# SQL注入检测
grep -iE "(union.*select|or 1=1|-- |information_schema|sleep\(|benchmark\()|%27|%22" access.log

# XSS攻击检测
grep -iE "(<script|javascript:|onerror=|onload=|alert\(|%3Cscript)" access.log

# 路径遍历检测
grep -E "(\.\./|%2e%2e%2f|%2e%2e/|\.\.%2f)" access.log

# 命令注入检测
grep -iE "(;|&&|\|\|).*(ls|cat|id|whoami|uname|wget|curl)" access.log

# 扫描器特征检测
grep -iE "(nikto|nmap|sqlmap|acunetix|nessus|dirbuster)" access.log

# 找出异常请求（URL超长或包含异常字符）
awk '{if(length($7) > 200) print $1, length($7), $7}' access.log | head -20
```

#### 场景3：异常流量分析

```bash
# 找出短时间内大量请求的IP
awk '{
    minute = substr($4, 2, 16)
    key = $1 "|" minute
    count[key]++
}
END {
    for(k in count) {
        if(count[k] > 100) {
            print count[k], k
        }
    }
}' access.log | sort -rn | head -20

# 统计每个IP的平均请求间隔（检测爬虫）
awk '{
    ip = $1
    time = mktime(substr($4, 2, 4) " " substr($4, 6, 2) " " substr($4, 9, 2) " " substr($4, 12, 2) " " substr($4, 15, 2) " " substr($4, 18, 2))
    if(last[ip] != 0) {
        diff[ip] += (time - last[ip])
        count[ip]++
    }
    last[ip] = time
}
END {
    for(ip in count) {
        avg = diff[ip] / count[ip]
        if(avg < 1 && count[ip] > 50) {
            printf "%-20s 平均间隔: %.2f秒 请求数: %d\n", ip, avg, count[ip]
        }
    }
}' access.log
```

#### 场景4：日志取证时间线构建

```bash
#!/bin/bash
# 日志时间线合并工具
# 合并多种日志源，按时间排序

LOG_DIR="/var/log"
OUTPUT_FILE="/tmp/timeline.txt"

# 收集认证日志
grep -h "Accepted\|Failed\|session" $LOG_DIR/secure* | \
    awk '{print $1, $2, $3, "[AUTH]", $0}' > /tmp/auth_timeline.txt

# 收集系统日志
grep -h "error\|warning\|critical" $LOG_DIR/messages* | \
    awk '{print $1, $2, $3, "[SYS]", $0}' > /tmp/sys_timeline.txt

# 收集Web日志（转换时间格式）
awk '{
    # 提取时间 [15/Mar/2026:14:30:22 +0800]
    time_str = substr($4, 2, 20)
    print time_str, "[WEB]", $0
}' $LOG_DIR/nginx/access.log* > /tmp/web_timeline.txt

# 合并并排序
cat /tmp/auth_timeline.txt /tmp/sys_timeline.txt /tmp/web_timeline.txt | \
    sort > $OUTPUT_FILE

echo "时间线已生成: $OUTPUT_FILE"
echo "总行数: $(wc -l < $OUTPUT_FILE)"
```
