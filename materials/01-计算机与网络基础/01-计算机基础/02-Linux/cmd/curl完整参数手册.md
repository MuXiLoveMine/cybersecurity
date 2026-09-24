# curl 完整参数手册（8.x 基准）

> **文档定位**：系统覆盖 `curl` 8.x 全部命令行参数，按功能分类详解，附实战示例、退出码、安全建议与排错清单。
>
> **适用对象**：系统管理员 / 运维工程师 / 安全工程师 / 后端开发工程师
>
> **深度层级**：操作参考 + 原理理解 + 故障排查 + 安全加固
>
> **适用版本**：curl 8.x（以 8.22.1 为基准），同时标注与 7.x 的差异
>
> **时效标注**：本文基于 2026 年 9 月 curl 官方文档验证，请注意时效性。
>
> **安全声明**：本文所有操作仅限授权测试与开发环境。涉及凭据、Token 的示例使用占位符，禁止在生产命令中明文写入敏感信息。

---

## 目录

1. [curl 是什么](#1-curl-是什么)
2. [基本语法](#2-基本语法)
3. [URL 语法与多 URL 用法](#3-url-语法与多-url-用法)
4. [全部参数总览表](#4-全部参数总览表)
5. [分类详解](#5-分类详解)
6. [每个参数的标准说明格式](#6-每个参数的标准说明格式)
7. [使用方式与实战示例](#7-使用方式与实战示例)
8. [退出码](#8-退出码)
9. [安全建议](#9-安全建议)
10. [常见错误与排错清单](#10-常见错误与排错清单)
11. [按字母索引](#11-按字母索引)

---

## 1. curl 是什么

### 1.1 定义与定位

`curl`（Client URL）是一个开源的**命令行 URL 数据传输工具**，由 Daniel Stenberg 于 1998 年创建，底层由 `libcurl` 库驱动。它支持 20 余种网络协议，是系统管理员、开发者和安全工程师最常用的网络工具之一。

| 属性 | 说明 |
|---|---|
| **全称** | Client URL |
| **底层引擎** | libcurl |
| **开源协议** | MIT/X derivate license |
| **官方站点** | https://curl.se |
| **官方文档** | https://curl.se/docs/manpage.html |
| **当前版本** | 8.22.1（2026 年） |
| **支持协议** | DICT, FILE, FTP, FTPS, GOPHER, GOPHERS, HTTP, HTTPS, IMAP, IMAPS, LDAP, LDAPS, MQTT, MQTTS, POP3, POP3S, RTSP, SCP, SFTP, SMTP, SMTPS, TELNET, TFTP, WS, WSS |
| **命令行选项数** | 259+（8.x 系列） |

### 1.2 curl 7.x 与 8.x 主要差异

| 变化项 | curl 7.x | curl 8.x | 说明 |
|---|---|---|---|
| **版本号体系** | 7.x.x | 8.x.x | 2023-03-15 起跳版至 8.0.0，无实质性破坏变更 |
| **HTTP/3 支持** | 实验性（`--http3`） | 稳定（`--http3`） | 8.x 起默认编译可包含 HTTP/3 |
| **变量支持** | 不支持 | `--variable`（8.3.0+） | 命令行变量与展开 |
| **`--json`** | 不支持（7.82 前） | 原生支持（7.82+，8.x 稳定） | JSON 请求快捷方式 |
| **`--help all`** | 不支持 | 支持（8.0+） | 显示全部选项 |
| **`--help` 适配终端** | 固定宽度 | 自适应终端宽度（8.8+） | |
| **ECH（Encrypted Client Hello）** | 不支持 | `--ech`（8.8+，实验性） | 加密 ClientHello |
| **`--trace-config`** | 不支持 | 支持（8.3+） | 细粒度 trace 配置 |
| **`--create-dirs`** | 长选项 `--create-dirs` | 同 | 无变化 |
| **WebSockets** | 实验性 | 稳定（`ws://` / `wss://`） | 8.x 起为正式协议 |
| **`--parallel-max-host`** | 不支持 | 支持（8.x） | 每主机最大并发数 |
| **长选项 `=` 传值** | 不支持 | 支持（8.16.0+） | `--url=https://example.com` |

### 1.3 安装与版本检查

```bash
# 查看版本与编译特性
curl --version

# 预期输出示例：
# curl 8.22.1 (x86_64-pc-linux-gnu) libcurl/8.22.1 OpenSSL/3.0.13 zlib/1.3 ...
# Release-Date: 2026-xx-xx
# Protocols: dict file ftp ftps gopher gophers http https imap imaps ...
# Features: alt-svc AsynchDNS brotli GSS-API HSTS HTTP2 HTTP3 ...

# 查看全部帮助
curl --help all

# 查看 man 手册
man curl
```

---

## 2. 基本语法

### 2.1 命令格式

```bash
curl [选项] [URL ...]
```

- 选项（Options）以单破折号（`-`）或双破折号（`--`）开头
- URL 可以有一个或多个，按顺序依次处理
- 选项和 URL 可以混合排列
- 非选项参数被视为 URL

### 2.2 选项书写规则

| 规则 | 说明 | 示例 |
|---|---|---|
| 短选项带空格 | 短选项与值之间可有空格 | `-d 'data'` 或 `-d'data'` |
| 长选项必须有空格 | 长选项与值之间必须有空格 | `--data 'data'` |
| 长选项等号传值（8.16+） | 可用 `=` 直接传值 | `--url=https://example.com` |
| 布尔选项取反 | 使用 `--no-` 前缀 | `--no-keepalive` |
| 短选项合并 | 无值短选项可连写 | `-OLv` 等同 `-O -L -v` |
| `--` 终止选项 | `--` 后的参数均视为 URL | `curl -- -d` |
| 全局选项 | 不受 `--next` 重置影响 | `--verbose`, `--parallel` 等 |

### 2.3 布尔选项取反

大多数布尔选项可通过添加 `--no-` 前缀来取反。例如 `--keepalive` 对应 `--no-keepalive`。

---

## 3. URL 语法与多 URL 用法

### 3.1 URL 基本语法

curl 遵循 [RFC 3986](https://www.ietf.org/rfc/rfc3986.txt) URL 语法：

```
scheme://[user:password@]host[:port]/path?query#fragment
```

| 组成部分 | 说明 | 示例 |
|---|---|---|
| **scheme** | 协议 | `http`, `https`, `ftp`, `sftp`, `scp` |
| **user:password** | 认证凭据（不推荐明文） | `admin:secret@` |
| **host** | 主机名或 IP | `example.com`, `192.168.1.1` |
| **port** | 端口 | `:8080`, `:443` |
| **path** | 路径 | `/api/v1/users` |
| **query** | 查询参数 | `?page=1&size=20` |

> **安全警告**：URL 中嵌入 `user:password` 会被 `ps` 等进程查看工具暴露，强烈建议使用 `-u` 选项或 `--netrc-file` 代替。

### 3.2 协议自动推断

如果 URL 不带 `scheme://` 前缀，curl 会自动推断：

| URL 前缀 | 推断协议 |
|---|---|
| 无前缀 | HTTP（默认） |
| `ftp.` 开头 | FTP |
| `dict.` 开头 | DICT |
| `ldap.` 开头 | LDAP |
| `imap.` 开头 | IMAP |

### 3.3 Globbing（通配符批量 URL）

curl 支持在 URL 中使用通配符（Globbing）来批量匹配多个 URL：

| 语法 | 说明 | 示例 |
|---|---|---|
| `{a,b,c}` | 列举匹配 | `https://example.com/{one,two,three}.jpg` |
| `[1-100]` | 数字范围 | `https://example.com/file[1-100].txt` |
| `[001-100]` | 带前导零 | `https://example.com/file[001-100].txt` |
| `[a-z]` | 字母范围 | `https://example.com/file[a-z].txt` |
| `[1-100:10]` | 步长 | `https://example.com/file[1-100:10].txt`（每 10 个取一次） |
| `<name>...` | 命名通配（8.21+） | `https://example.com/{<num>one,two}.jpg` |

```bash
# 下载 file1.txt 到 file100.txt
curl -O https://example.com/file[1-100].txt

# 带命名通配符（8.21+），在 -o 中引用
curl -o "file_#<num>.txt" https://example.com/file[<num>1-100].txt

# 禁用通配符（按字面量处理大括号/方括号）
curl -g https://example.com/{literal}.txt
```

### 3.4 多 URL 与连接复用

```bash
# 顺序获取多个 URL
curl https://example.com/api/1 https://example.com/api/2

# 并行获取多个 URL（--parallel）
curl --parallel https://example.com/api/1 https://example.com/api/2

# 使用 --next 分组（每组独立选项）
curl -d "data1" https://example.com/api/1 --next -d "data2" https://example.com/api/2
```

curl 会自动对同一主机的多个 URL 复用 TCP 连接，减少握手开销。

### 3.5 变量与展开（8.3.0+）

```bash
# 定义变量
curl --variable name=value https://example.com/api

# 从文件读取变量
curl --variable secret@$HOME/.token --expand-url "https://example.com/api?key={{secret}}"

# 从环境变量导入
curl --variable '%API_KEY' --expand-header "Authorization: Bearer {{API_KEY}}" https://example.com/api

# 变量函数：trim / json / url / b64 / 64dec
curl --variable payload@$FILE --expand-data "{{payload:trim:json}}" https://example.com/api
```

---

## 4. 全部参数总览表

> 下表按字母顺序列出 curl 8.x 全部命令行选项。标有 `[G]` 的为全局选项（不受 `--next` 影响）。

### 4.1 短选项总览

| 短选项 | 长选项 | 参数类型 | 说明 |
|---|---|---|---|
| `-a` | `--append` | 无 | FTP/SFTP 上传时追加到文件末尾 |
| `-b` | `--cookie` | `<data\|file>` | 发送 Cookie |
| `-c` | `--cookie-jar` | `<file>` | 将响应 Cookie 保存到文件 |
| `-C` | `--continue-at` | `<offset>` | 断点续传 |
| `-d` | `--data` | `<data>` | 发送 POST 数据（application/x-www-form-urlencoded） |
| `-D` | `--dump-header` | `<file>` | 将响应头写入文件 |
| `-e` | `--referer` | `<url>` | 设置 Referer 头 |
| `-E` | `--cert` | `<cert[:passwd]>` | 客户端证书 |
| `-f` | `--fail` | 无 | HTTP 错误时快速失败（不输出错误页面） |
| `-F` | `--form` | `<name=content>` | multipart 表单上传 |
| `-g` | `--globoff` | 无 | 禁用 URL 通配符 |
| `-G` | `--get` | 无 | 将 POST 数据转为 GET 查询参数 |
| `-h` | `--help` | `[subject]` | 显示帮助 |
| `-H` | `--header` | `<header>` | 添加自定义请求头 |
| `-i` | `--include` | 无 | 输出中包含响应头 |
| `-I` | `--head` | 无 | 只获取响应头（HEAD 请求） |
| `-j` | `--junk-session-cookies` | 无 | 忽略会话 Cookie |
| `-J` | `--remote-header-name` | 无 | 使用 Content-Disposition 中的文件名保存 |
| `-k` | `--insecure` | 无 | 跳过 TLS 证书验证 |
| `-K` | `--config` | `<file>` | 从文件读取配置 |
| `-l` | `--list-only` | 无 | FTP 只列出目录名 |
| `-L` | `--location` | 无 | 跟随重定向 |
| `-m` | `--max-time` | `<seconds>` | 总超时时间 |
| `-M` | `--manual` | 无 | 显示完整手册 |
| `-n` | `--netrc` | 无 | 从 ~/.netrc 读取凭据 |
| `-N` | `--no-buffer` | 无 | 禁用输出缓冲 |
| `-o` | `--output` | `<file>` | 输出到文件 |
| `-O` | `--remote-name` | 无 | 按 URL 原文件名保存 |
| `-p` | `--proxytunnel` | 无 | 通过 HTTP 代理隧道（非 HTTP 请求） |
| `-P` | `--ftp-port` | `<address>` | FTP 主动模式端口 |
| `-q` | — | 无 | 禁用 curlrc 配置文件（必须第一个） |
| `-Q` | `--quote` | `<command>` | FTP/SFTP 传输前执行命令 |
| `-r` | `--range` | `<range>` | 请求字节范围 |
| `-R` | `--remote-time` | 无 | 保存文件时使用服务器时间戳 |
| `-s` | `--silent` | 无 | 静默模式 |
| `-S` | `--show-error` | 无 | 静默模式下仍显示错误 |
| `-t` | `--telnet-option` | `<opt=val>` | Telnet 选项 |
| `-T` | `--upload-file` | `<file>` | 上传文件 |
| `-u` | `--user` | `<user:pass>` | 认证凭据 |
| `-U` | `--proxy-user` | `<user:pass>` | 代理认证凭据 |
| `-v` | `--verbose` `[G]` | 无 | 详细输出 |
| `-V` | `--version` | 无 | 显示版本信息 |
| `-w` | `--write-out` | `<format>` | 输出自定义格式信息 |
| `-x` | `--proxy` | `[protocol://]host[:port]` | 使用代理 |
| `-X` | `--request` | `<method>` | 自定义请求方法 |
| `-Y` | `--speed-limit` | `<speed>` | 最低速度限制 |
| `-y` | `--speed-time` | `<seconds>` | 速度限制时间窗口 |
| `-z` | `--time-cond` | `<time>` | 基于时间的条件请求 |
| `-Z` | `--parallel` `[G]` | 无 | 并行传输 |
| — | `--abstract-unix-socket` | `<path>` | 抽象 Unix Socket |
| — | `--alt-svc` | `<filename>` | Alt-Svc 缓存 |
| — | `--anyauth` | 无 | 自动选择最安全的认证方式 |
| — | `--append` | 无 | 同 `-a` |

### 4.2 仅长选项的参数总览

| 长选项 | 参数类型 | 说明 |
|---|---|---|
| `--aws-sigv4` | `<provider1[:...]>` | AWS V4 签名认证 |
| `--basic` | 无 | HTTP Basic 认证 |
| `--ca-native` | 无 | 使用系统原生 CA 存储 |
| `--cacert` | `<file>` | CA 证书 |
| `--capath` | `<dir>` | CA 证书目录 |
| `--cert-status` | 无 | 证书 OCSP stapling 验证 |
| `--cert-type` | `<type>` | 证书类型（PEM/DER/ENG/P12） |
| `--ciphers` | `<list>` | TLS 密码套件 |
| `--compressed` | 无 | 请求压缩响应（gzip/deflate/br/zstd） |
| `--compressed-ssh` | 无 | SSH 压缩 |
| `--config` | `<file>` | 同 `-K` |
| `--connect-timeout` | `<seconds>` | 连接超时 |
| `--connect-to` | `<host1:port1:host2:port2>` | 连接重定向 |
| `--continue-at` | `<offset>` | 同 `-C` |
| `--cookie` | `<data\|file>` | 同 `-b` |
| `--cookie-jar` | `<file>` | 同 `-c` |
| `--create-dirs` | 无 | 创建本地目录结构 |
| `--create-file-mode` | `<mode>` | 创建文件的权限模式（8.x） |
| `--crlf` | 无 | 上传时 LF 转 CRLF |
| `--crlfile` | `<file>` | CRL（证书吊销列表）文件 |
| `--curves` | `<curves>` | TLS 椭圆曲线 |
| `--data` | `<data>` | 同 `-d` |
| `--data-ascii` | `<data>` | 同 `--data` |
| `--data-binary` | `<data>` | 发送二进制 POST 数据 |
| `--data-raw` | `<data>` | 发送原始数据（不解析 `@`） |
| `--data-urlencode` | `<data>` | URL 编码后发送 |
| `--delegation` | `<level>` | GSS-API 委托级别 |
| `--digest` | 无 | HTTP Digest 认证 |
| `--disable-eprt` | 无 | 禁用 EPRT/PORT（FTP） |
| `--disable-epsv` | 无 | 禁用 EPSV（FTP） |
| `--disallow-username-in-url` | 无 | 禁止 URL 中含用户名 |
| `--dns-interface` | `<interface>` | DNS 使用的网络接口 |
| `--dns-ipv4-addr` | `<addr>` | DNS 绑定 IPv4 地址 |
| `--dns-ipv6-addr` | `<addr>` | DNS 绑定 IPv6 地址 |
| `--dns-servers` | `<addr>` | 自定义 DNS 服务器 |
| `--doas-auth` | 无 | doas 认证（SSH） |
| `--dump-ca-embed` | `<file>` | 导出嵌入的 CA 证书 |
| `--dump-header` | `<file>` | 同 `-D` |
| `--ech` | `<config>` | 加密 ClientHello（实验性，8.8+） |
| `--egd-file` | `<file>` | EGD 随机数套接字 |
| `--engine` | `<name>` | 加密引擎 |
| `--etag-compare` | `<file>` | 从文件加载 ETag 做条件请求 |
| `--etag-save` | `<file>` | 保存响应 ETag 到文件 |
| `--expect100-timeout` | `<seconds>` | Expect: 100-continue 超时 |
| `--fail` | 无 | 同 `-f` |
| `--fail-with-body` | 无 | 失败时仍输出响应体 |
| `--fail-early` | 无 `[G]` | 第一个错误即退出 |
| `--false-start` | 无 | TLS False Start |
| `--form` | `<name=content>` | 同 `-F` |
| `--form-escape` | 无 | 表单字段反斜杠转义 |
| `--form-string` | `<name=string>` | 表单字段（纯字符串） |
| `--ftp-account` | `<data>` | FTP ACCOUNT 命令 |
| `--ftp-alternative-to-user` | `<cmd>` | FTP 替代 USER 命令 |
| `--ftp-create-dirs` | 无 | FTP 远程创建目录 |
| `--ftp-method` | `<method>` | FTP 传输方法 |
| `--ftp-pasv` | 无 | FTP 被动模式 |
| `--ftp-port` | `<address>` | 同 `-P` |
| `--ftp-pret` | 无 | FTP PASV 前 PRET 命令 |
| `--ftp-skip-pasv-ip` | 无 | 忽略 PASV 返回的 IP |
| `--ftp-ssl-ccc` | 无 | FTP CCC 关闭 TLS 通道 |
| `--ftp-ssl-ccc-mode` | `<mode>` | CCC 模式 |
| `--ftp-ssl-control` | 无 | FTP 控制通道加密 |
| `--get` | 无 | 同 `-G` |
| `--globoff` | 无 | 同 `-g` |
| `--happy-eyeballs-timeout-ms` | `<ms>` | Happy Eyeballs 超时 |
| `--haproxy-clientip` | `<ip>` | HAProxy PROXY 协议客户端 IP |
| `--haproxy-protocol` | 无 | HAProxy PROXY 协议 |
| `--head` | 无 | 同 `-I` |
| `--header` | `<header>` | 同 `-H` |
| `--help` | `[subject]` | 同 `-h` |
| `--hostpubmd5` | `<md5>` | SSH 主机公钥 MD5 |
| `--hostpubsha256` | `<sha256>` | SSH 主机公钥 SHA256 |
| `--hsts` | `<file>` | HSTS 缓存文件 |
| `--http0.9` | 无 | 允许 HTTP 0.9 响应 |
| `--http1.0` | 无 | 使用 HTTP 1.0 |
| `--http1.1` | 无 | 使用 HTTP 1.1 |
| `--http2` | 无 | 使用 HTTP/2 |
| `--http2-prior-knowledge` | 无 | 直接使用 HTTP/2（不协商） |
| `--http3` | 无 | 使用 HTTP/3（仅 QUIC） |
| `--http3-only` | 无 | 仅使用 HTTP/3 |
| `--ignore-content-length` | 无 | 忽略 Content-Length |
| `--insecure` | 无 | 同 `-k` |
| `--interface` | `<name>` | 绑定网络接口 |
| `--ip-tos` | `<value>` | IP TOS 字段 |
| `--ipv4` | 无 | 仅解析 IPv4 |
| `--ipv6` | 无 | 仅解析 IPv6 |
| `--json` | `<data>` | 发送 JSON 请求 |
| `--junk-session-cookies` | 无 | 同 `-j` |
| `--keepalive` | 无 | 启用 TCP keepalive（默认） |
| `--keepalive-time` | `<seconds>` | keepalive 间隔 |
| `--key` | `<key>` | 私钥文件 |
| `--key-type` | `<type>` | 私钥类型 |
| `--krb` | `<level>` | Kerberos 安全级别 |
| `--libcurl` | `<file>` `[G]` | 输出 libcurl 等效 C 代码 |
| `--limit-rate` | `<speed>` | 限速 |
| `--list-only` | 无 | 同 `-l` |
| `--local-port` | `<port[-end]>` | 绑定本地端口 |
| `--location` | 无 | 同 `-L` |
| `--location-trusted` | 无 | 跟随重定向并信任凭据 |
| `--login-options` | `<options>` | 登录选项（IMAP/POP3/SMTP） |
| `--mail-auth` | `<addr>` | SMTP AUTH 地址 |
| `--mail-from` | `<addr>` | SMTP 发件人 |
| `--mail-rcpt` | `<addr>` | SMTP 收件人 |
| `--mail-rcpt-allowfails` | 无 | SMTP 部分收件人失败不中止 |
| `--manual` | 无 | 同 `-M` |
| `--max-filesize` | `<bytes>` | 最大下载文件大小 |
| `--max-redirs` | `<num>` | 最大重定向次数 |
| `--max-time` | `<seconds>` | 同 `-m` |
| `--metalink` | 无 | Metalink 处理（已弃用） |
| `--negotiate` | 无 | HTTP Negotiate (SPNEGO) 认证 |
| `--netrc` | 无 | 同 `-n` |
| `--netrc-file` | `<file>` | 指定 netrc 文件 |
| `--netrc-optional` | 无 | 可选 netrc |
| `--next` | 无 | 分隔下一组选项 |
| `--no-alpn` | 无 | 禁用 ALPN |
| `--no-buffer` | 无 | 同 `-N` |
| `--no-clobber` | 无 | 不覆盖已存在的文件 |
| `--no-keepalive` | 无 | 禁用 TCP keepalive |
| `--no-npn` | 无 | 禁用 NPN |
| `--no-progress-meter` | 无 | 禁用进度条（不静默） |
| `--no-sessionid` | 无 | 禁用 SSL Session ID 复用 |
| `--noproxy` | `<no-proxy-list>` | 不使用代理的主机列表 |
| `--nping` | 无 | — |
| `--ntlm` | 无 | HTTP NTLM 认证 |
| `--ntlm-wb` | 无 | NTLM WinBridger 认证 |
| `--oauth2-bearer` | `<token>` | OAuth 2.0 Bearer Token |
| `--output` | `<file>` | 同 `-o` |
| `--output-dir` | `<dir>` | 输出目录 |
| `--parallel` | 无 `[G]` | 同 `-Z` |
| `--parallel-immediate` | 无 `[G]` | 并行立即开始 |
| `--parallel-max` | `<num>` `[G]` | 最大并行连接数 |
| `--parallel-max-host` | `<num>` `[G]` | 每主机最大并行数 |
| `--parallel-progress` | `<method>` `[G]` | 并行进度显示方式 |
| `--parted-load` | — | — |
| `--pass` | `<phrase>` | 私钥密码短语 |
| `--path-as-is` | 无 | 路径原样发送（不合并 `..`） |
| `--pinnedpubkey` | `<hashes>` | 公钥指纹锁定 |
| `--pipelining` | 无 | HTTP 流水线（已弃用） |
| `--post301` | 无 | 301 重定向后保持 POST |
| `--post302` | 无 | 302 重定向后保持 POST |
| `--post303` | 无 | 303 重定向后保持 POST |
| `--preproxy` | `[protocol://]host[:port]` | 预代理（代理链） |
| `--progress-bar` | 无 `[G]` | 进度条显示 |
| `--proto` | `<protocols>` | 启用/禁用协议 |
| `--proto-default` | `<protocol>` | 默认协议 |
| `--proto-redir` | `<protocols>` | 重定向后允许的协议 |
| `--proxy` | `[protocol://]host[:port]` | 同 `-x` |
| `--proxy-anyauth` | 无 | 代理自动选择认证 |
| `--proxy-basic` | 无 | 代理 Basic 认证 |
| `--proxy-ca-native` | 无 | 代理使用原生 CA |
| `--proxy-cacert` | `<file>` | 代理 CA 证书 |
| `--proxy-capath` | `<dir>` | 代理 CA 目录 |
| `--proxy-cert` | `<cert[:passwd]>` | 代理客户端证书 |
| `--proxy-cert-type` | `<type>` | 代理证书类型 |
| `--proxy-ciphers` | `<list>` | 代理 TLS 密码套件 |
| `--proxy-crlfile` | `<file>` | 代理 CRL 文件 |
| `--proxy-digest` | 无 | 代理 Digest 认证 |
| `--proxy-header` | `<header>` | 代理请求头 |
| `--proxy-http2` | 无 | 代理使用 HTTP/2 |
| `--proxy-insecure` | 无 | 代理跳过证书验证 |
| `--proxy-key` | `<key>` | 代理私钥 |
| `--proxy-key-type` | `<type>` | 代理私钥类型 |
| `--proxy-negotiate` | 无 | 代理 Negotiate 认证 |
| `--proxy-ntlm` | 无 | 代理 NTLM 认证 |
| `--proxy-pass` | `<phrase>` | 代理私钥密码短语 |
| `--proxy-pinnedpubkey` | `<hashes>` | 代理公钥指纹锁定 |
| `--proxy-service-name` | `<name>` | 代理 SPNEGO 服务名 |
| `--proxy-ssl-allow-beast` | 无 | 代理允许 BEAST 攻击缓解 |
| `--proxy-ssl-auto-client-cert` | 无 | 代理自动客户端证书 |
| `--proxy-tls13-ciphers` | `<list>` | 代理 TLS 1.3 密码套件 |
| `--proxy-tlsauthtype` | `<type>` | 代理 TLS 认证类型 |
| `--proxy-tlspassword` | `<pwd>` | 代理 TLS 密码 |
| `--proxy-tlsuser` | `<user>` | 代理 TLS 用户名 |
| `--proxy-tlsv1` | 无 | 代理使用 TLS 1.x |
| `--proxy-user` | `<user:pass>` | 同 `-U` |
| `--proxy1.0` | `<host[:port]>` | 使用 HTTP/1.0 代理 |
| `--proxytunnel` | 无 | 同 `-p` |
| `--pubkey` | `<key>` | SSH 公钥 |
| `--quote` | `<command>` | 同 `-Q` |
| `--random-file` | `<file>` | 随机数源文件 |
| `--range` | `<range>` | 同 `-r` |
| `--rate` | `<max request rate>` `[G]` | 请求速率限制 |
| `--raw` | 无 | 禁用 HTTP 内容编码传输 |
| `--referer` | `<url>` | 同 `-e` |
| `--remote-header-name` | 无 | 同 `-J` |
| `--remote-name` | 无 | 同 `-O` |
| `--remote-name-all` | 无 | 所有 URL 使用 -O |
| `--remote-time` | 无 | 同 `-R` |
| `--remove-on-error` | 无 | 失败时删除输出文件 |
| `--request` | `<method>` | 同 `-X` |
| `--request-target` | `<target>` | 自定义请求目标 |
| `--resolve` | `<[+]host:port:addr[,addr]...>` | 自定义 DNS 解析 |
| `--retry` | `<num>` | 重试次数 |
| `--retry-all-errors` | 无 | 所有错误都重试 |
| `--retry-connrefused` | 无 | 连接拒绝也重试 |
| `--retry-delay` | `<seconds>` | 重试间隔 |
| `--retry-max-time` | `<seconds>` | 最大重试总时长 |
| `--sasl-authzid` | `<identity>` | SASL 授权身份 |
| `--sasl-ir` | 无 | SASL 初始响应 |
| `--service-name` | `<name>` | SPNEGO 服务名 |
| `--sessionid` | 无 | 启用 SSL Session ID（默认） |
| `--show-error` | 无 `[G]` | 同 `-S` |
| `--silent` | 无 | 同 `-s` |
| `--socks4` | `<host[:port]>` | SOCKS4 代理 |
| `--socks4a` | `<host[:port]>` | SOCKS4a 代理 |
| `--socks5` | `<host[:port]>` | SOCKS5 代理 |
| `--socks5-basic` | 无 | SOCKS5 用户名/密码认证 |
| `--socks5-gssapi` | 无 | SOCKS5 GSS-API 认证 |
| `--socks5-gssapi-nec` | 无 | SOCKS5 GSS-API NEC 模式 |
| `--socks5-gssapi-service` | `<name>` | SOCKS5 GSS-API 服务名 |
| `--socks5-hostname` | `<host[:port]>` | SOCKS5 远程 DNS |
| `--speed-limit` | `<speed>` | 同 `-Y` |
| `--speed-time` | `<seconds>` | 同 `-y` |
| `--ssl` | 无 | 启用 SSL/TLS（FTP/IMAP/POP3/SMTP） |
| `--ssl-allow-beast` | 无 | 允许 BEAST 缓解 |
| `--ssl-auto-client-cert` | 无 | 自动客户端证书 |
| `--ssl-no-revoke` | 无 | 禁用 CRL 检查 |
| `--ssl-reqd` | 无 | 要求 SSL/TLS |
| `--ssl-revoke-best-effort` | 无 | 尽力 CRL 检查 |
| `--sslv2` | 无 | SSLv2（已移除） |
| `--sslv3` | 无 | SSLv3（已移除） |
| `--stderr` | `<file>` `[G]` | 重定向 stderr |
| `--styled-output` | 无 `[G]` | 带颜色的终端输出 |
| `--suppress-connect-headers` | 无 | 抑制代理 CONNECT 响应头 |
| `--tcp-fastopen` | 无 | TCP Fast Open |
| `--tcp-nodelay` | 无 | TCP_NODELAY（禁用 Nagle） |
| `--telnet-option` | `<opt=val>` | 同 `-t` |
| `--test-event` | 无 | 事件测试（内部） |
| `--tftp-blksize` | `<value>` | TFTP 块大小 |
| `--tftp-no-options` | 无 | TFTP 不发送选项 |
| `--time-cond` | `<time>` | 同 `-z` |
| `--tls-earlydata` | 无 | TLS 0-RTT 数据 |
| `--tls-max` | `<VERSION>` | 最大 TLS 版本 |
| `--tls13-ciphers` | `<list>` | TLS 1.3 密码套件 |
| `--tlsauthtype` | `<type>` | TLS 认证类型 |
| `--tlspassword` | `<pwd>` | TLS 密码 |
| `--tlsuser` | `<user>` | TLS 用户名 |
| `--tlsv1` | 无 | TLS 1.x |
| `--tlsv1.0` | 无 | TLS 1.0 |
| `--tlsv1.1` | 无 | TLS 1.1 |
| `--tlsv1.2` | 无 | TLS 1.2 |
| `--tlsv1.3` | 无 | TLS 1.3 |
| `--tr-encoding` | 无 | 请求传输编码 |
| `--trace` | `<file>` `[G]` | 详细 trace（含数据） |
| `--trace-ascii` | `<file>` `[G]` | 详细 trace（ASCII） |
| `--trace-config` | `<string>` `[G]` | trace 配置（8.3+） |
| `--trace-ids` | 无 `[G]` | trace 中包含传输 ID |
| `--trace-time` | 无 `[G]` | trace 中包含时间戳 |
| `--unix-socket` | `<path>` | Unix Socket |
| `--upload-file` | `<file>` | 同 `-T` |
| `--url` | `<url>` | 指定 URL |
| `--url-query` | `<data>` | URL 查询参数（8.x） |
| `--use-ascii` | 无 | 同 `-B`（FTP ASCII 模式） |
| `--user` | `<user:pass>` | 同 `-u` |
| `--user-agent` | `<name>` | 同 `-A` |
| `--variable` | `<[%]name=text@file>` | 变量定义（8.3+） |
| `--verbose` | 无 `[G]` | 同 `-v` |
| `--version` | 无 | 同 `-V` |
| `--vlan-priority` | `<value>` | VLAN 优先级 |
| `--write-out` | `<format>` | 同 `-w` |
| `--ws-options` | `<options>` | WebSocket 选项 |
| `--xattr` | 无 | 文件扩展属性存储元数据 |

---

## 5. 分类详解

### 5.1 请求方法与协议控制

### `-X, --request <method>`

- 作用：指定 HTTP 请求方法（GET/POST/PUT/DELETE/PATCH/HEAD/OPTIONS 等）
- 语法：`curl -X <method> <url>` 或 `curl --request <method> <url>`
- 示例：
```bash
curl -X DELETE https://$HOST/api/users/$ID
curl -X PUT -H "Content-Type: application/json" -d '{"name":"test"}' https://$HOST/api/users/$ID
curl -X PATCH -d '{"email":"new@example.com"}' https://$HOST/api/users/$ID
```
- 版本要求：7.x+
- 平台/协议限制：HTTP/FTP/SMTP/IMAP/POP3 等协议均可使用
- 注意事项：`-d` 隐含 POST、`-I` 隐含 HEAD，不需要额外指定 `-X`。`-X` 仅改变方法名，不自动设置 Content-Type

### `--request-target <target>`

- 作用：自定义 HTTP 请求行中的请求目标（通常用于 HTTP/2 或特殊场景）
- 语法：`curl --request-target <target> <url>`
- 示例：
```bash
curl --request-target "*" -X OPTIONS https://$HOST/api
```
- 版本要求：7.55.0+
- 平台/协议限制：HTTP
- 注意事项：一般不需要修改，主要用于 HTTP/2 协议测试

### `-G, --get`

- 作用：将 `-d` 提供的数据转为 URL 查询参数，并使用 GET 方法发送
- 语法：`curl -G -d "<data>" <url>` 或 `curl --get --data "<data>" <url>`
- 示例：
```bash
curl -G -d "q=curl" -d "page=2" https://$HOST/api/search
# 等效于：curl "https://$HOST/api/search?q=curl&page=2"
```
- 版本要求：7.x+
- 平台/协议限制：HTTP
- 注意事项：多个 `-d` 会被 `&` 连接。与 `-X GET` 不同，`-G` 会将数据移到 URL 中

### `--url <url>`

- 作用：显式指定 URL（用于配置文件或多 URL 场景）
- 语法：`curl --url <url>`
- 示例：
```bash
curl --url https://$HOST/api/v1 --url https://$HOST/api/v2
```
- 版本要求：7.x+
- 平台/协议限制：所有协议
- 注意事项：通常不需要，直接写 URL 即可

### `--url-query <data>`

- 作用：向 URL 添加查询参数（8.x 新增）
- 语法：`curl --url-query "<data>" <url>`
- 示例：
```bash
curl --url-query "q=curl" --url-query "page=2" https://$HOST/api/search
```
- 版本要求：8.x
- 平台/协议限制：HTTP
- 注意事项：与 `-G -d` 不同，`--url-query` 不改变请求方法，直接在 URL 上附加查询参数

### `--http0.9`

- 作用：允许接收 HTTP 0.9 格式的响应（仅状态行，无头）
- 语法：`curl --http0.9 <url>`
- 示例：
```bash
curl --http0.9 http://$HOST/legacy
```
- 版本要求：7.66.0+（默认禁用 HTTP/0.9）
- 平台/协议限制：HTTP
- 注意事项：HTTP 0.9 极其古老，仅用于兼容老服务器，存在安全隐患

### `--http1.0`

- 作用：强制使用 HTTP 1.0
- 语法：`curl --http1.0 <url>`
- 示例：
```bash
curl --http1.0 http://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：HTTP
- 注意事项：HTTP 1.0 不支持 keepalive、分块传输等特性

### `--http1.1`

- 作用：强制使用 HTTP 1.1
- 语法：`curl --http1.1 <url>`
- 示例：
```bash
curl --http1.1 https://$HOST/api
```
- 版本要求：7.33.0+
- 平台/协议限制：HTTP
- 注意事项：在默认使用 HTTP/2 的环境中降级到 1.1

### `--http2`

- 作用：使用 HTTP/2（通过 ALPN 协商）
- 语法：`curl --http2 <url>`
- 示例：
```bash
curl --http2 https://$HOST/api
```
- 版本要求：7.33.0+（需要 nghttp2 编译支持）
- 平台/协议限制：HTTPS；取决于编译选项
- 注意事项：8.x 默认对 HTTPS 启用 HTTP/2

### `--http2-prior-knowledge`

- 作用：直接使用 HTTP/2，不经过 ALPN 协商（h2c）
- 语法：`curl --http2-prior-knowledge <url>`
- 示例：
```bash
curl --http2-prior-knowledge http://$HOST/api
```
- 版本要求：7.49.0+
- 平台/协议限制：HTTP（明文 HTTP/2）
- 注意事项：如果服务器不支持 HTTP/2 会直接失败

### `--http3`

- 作用：使用 HTTP/3（通过 Alt-Svc 或直接 QUIC）
- 语法：`curl --http3 <url>`
- 示例：
```bash
curl --http3 https://$HOST/api
```
- 版本要求：7.66.0+（实验性），8.x 稳定
- 平台/协议限制：HTTPS；取决于编译选项（需要 QUIC 库：quiche/ngtcp2/openssl3）
- 注意事项：如果服务器不支持 HTTP/3 会回退到 HTTP/2 或 HTTP/1.1

### `--http3-only`

- 作用：仅使用 HTTP/3，不回退
- 语法：`curl --http3-only <url>`
- 示例：
```bash
curl --http3-only https://$HOST/api
```
- 版本要求：7.66.0+
- 平台/协议限制：HTTPS；取决于编译选项
- 注意事项：服务器不支持时直接失败

### `--proto <protocols>`

- 作用：启用或禁用特定协议
- 语法：`curl --proto <[+|-]protocol[,protocol...]> <url>`
- 示例：
```bash
# 只允许 HTTP(S)
curl --proto -all,+http,https https://$HOST/

# 禁用 FILE 协议
curl --proto -file https://$HOST/
```
- 版本要求：7.47.0+
- 平台/协议限制：全局
- 注意事项：`-all,+http` 表示禁用全部再启用 HTTP。安全加固建议限制可用协议

### `--proto-default <protocol>`

- 作用：设置无 scheme 时的默认协议
- 语法：`curl --proto-default <protocol> <url>`
- 示例：
```bash
curl --proto-default https $HOST/api
```
- 版本要求：7.45.0+
- 平台/协议限制：全局
- 注意事项：比 `curl http://...` 默认 HTTP 更安全

### `--proto-redir <protocols>`

- 作用：设置重定向后允许的协议
- 语法：`curl --proto-redir <[+|-]protocol[,protocol...]> -L <url>`
- 示例：
```bash
# 重定向后只允许 HTTP(S)
curl --proto-redir -all,+http,https -L https://$HOST/redirect
```
- 版本要求：7.47.0+
- 平台/协议限制：HTTP
- 注意事项：防止从 HTTPS 重定向到 FILE/FTP 等危险协议

### `--ignore-content-length`

- 作用：忽略 Content-Length 头
- 语法：`curl --ignore-content-length <url>`
- 示例：
```bash
curl --ignore-content-length https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：HTTP/FTP
- 注意事项：某些服务器返回错误的 Content-Length 导致下载截断

### `--raw`

- 作用：禁用 HTTP 内容编码传输（不发送 Accept-Encoding）
- 语法：`curl --raw <url>`
- 示例：
```bash
curl --raw https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：HTTP
- 注意事项：与 `--compressed` 相反

### `--tr-encoding`

- 作用：请求传输编码（Transfer-Encoding: chunked）
- 语法：`curl --tr-encoding <url>`
- 示例：
```bash
curl --tr-encoding --compressed https://$HOST/api
```
- 版本要求：7.21.5+
- 平台/协议限制：HTTP
- 注意事项：通常与 `--compressed` 配合使用

### `--no-alpn`

- 作用：禁用 TLS ALPN（Application-Layer Protocol Negotiation）
- 语法：`curl --no-alpn <url>`
- 示例：
```bash
curl --no-alpn https://$HOST/api
```
- 版本要求：7.36.0+
- 平台/协议限制：HTTPS
- 注意事项：ALPN 是 HTTP/2 协商的标准方式，禁用后无法通过 ALPN 使用 HTTP/2

### `--no-npn`

- 作用：禁用 TLS NPN（Next Protocol Negotiation）
- 语法：`curl --no-npn <url>`
- 示例：
```bash
curl --no-npn https://$HOST/api
```
- 版本要求：7.36.0+
- 平台/协议限制：HTTPS
- 注意事项：NPN 已被 ALPN 取代，大多数实现不再支持

---

### 5.2 请求头与响应头

### `-H, --header <header>`

- 作用：添加或替换 HTTP 请求头
- 语法：`curl -H "<Header: value>" <url>`
- 示例：
```bash
curl -H "X-Custom-Header: value" https://$HOST/api
curl -H "Authorization: Bearer $TOKEN" https://$HOST/api
# 删除头（冒号后无空格）
curl -H "X-Unneeded:" https://$HOST/api
# 添加空值头
curl -H "X-Empty;" https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：HTTP/WS/WSS
- 注意事项：同一个头多次出现会全部发送。`-H "Header:"` 会删除该头

### `-A, --user-agent <name>`

- 作用：设置 User-Agent 请求头
- 语法：`curl -A "<agent string>" <url>`
- 示例：
```bash
curl -A "MyApp/1.0" https://$HOST/api
curl -A "" https://$HOST/api  # 空 User-Agent
```
- 版本要求：7.x+
- 平台/协议限制：HTTP
- 注意事项：默认为 `curl/x.y.z`。某些 API 根据 UA 返回不同内容

### `-e, --referer <url>`

- 作用：设置 Referer 请求头
- 语法：`curl -e "<referer url>" <url>`
- 示例：
```bash
curl -e "https://$HOST/login" https://$HOST/dashboard
# 自动设置 Referer 为来源页面
curl -e ";auto" -L https://$HOST/redirect
```
- 版本要求：7.x+
- 平台/协议限制：HTTP
- 注意事项：`;auto` 表示跟随重定向时自动设置 Referer

### `-D, --dump-header <file>`

- 作用：将响应头写入文件
- 语法：`curl -D <file> <url>`
- 示例：
```bash
curl -D headers.txt https://$HOST/api
# 输出到 stdout
curl -D - -o /dev/null https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：HTTP/FTP
- 注意事项：`-D -` 输出到 stdout，配合 `-o /dev/null` 可只看头

### `-i, --include`

- 作用：在输出中包含响应头
- 语法：`curl -i <url>`
- 示例：
```bash
curl -i https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：HTTP/FTP
- 注意事项：与 `-D` 不同，`-i` 将头和体混合输出到 stdout

### `-I, --head`

- 作用：只发送 HEAD 请求（只获取响应头）
- 语法：`curl -I <url>`
- 示例：
```bash
curl -I https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：HTTP/FTP/FILE
- 注意事项：HEAD 请求的响应没有响应体

### `--suppress-connect-headers`

- 作用：抑制通过代理 CONNECT 时返回的响应头
- 语法：`curl --suppress-connect-headers -x $PROXY https://$HOST/`
- 示例：
```bash
curl --suppress-connect-headers -x http://$PROXY:8080 https://$HOST/api
```
- 版本要求：8.9.0+
- 平台/协议限制：HTTP（代理场景）
- 注意事项：仅在使用 HTTP 代理连接 HTTPS 时有意义

---

### 5.3 发送数据

### `-d, --data <data>`

- 作用：发送 POST 请求体（Content-Type: application/x-www-form-urlencoded）
- 语法：`curl -d "<data>" <url>`
- 示例：
```bash
curl -d "name=test&email=test@example.com" https://$HOST/api/users
# 从文件读取
curl -d "@data.txt" https://$HOST/api/users
# 从 stdin 读取
echo '{"key":"value"}' | curl -d "@-" https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：HTTP/SMTP
- 注意事项：`-d` 会移除换行符。`@file` 从文件读取。多次 `-d` 用 `&` 连接

### `--data-raw <data>`

- 作用：发送原始 POST 数据（不解析 `@` 前缀）
- 语法：`curl --data-raw "<data>" <url>`
- 示例：
```bash
curl --data-raw "@username" https://$HOST/api  # 发送字面量 @username
```
- 版本要求：7.77.0+
- 平台/协议限制：HTTP
- 注意事项：当数据以 `@` 开头但不是文件引用时使用

### `--data-binary <data>`

- 作用：发送二进制 POST 数据（保留换行符，不做任何处理）
- 语法：`curl --data-binary "<data>" <url>`
- 示例：
```bash
curl --data-binary "@binary.dat" https://$HOST/api/upload
curl --data-binary '{"json":"data\nwith\nnewlines"}' https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：HTTP
- 注意事项：与 `-d` 不同，`--data-binary` 不会移除换行符

### `--data-ascii <data>`

- 作用：同 `--data`，发送 ASCII POST 数据
- 语法：`curl --data-ascii "<data>" <url>`
- 示例：
```bash
curl --data-ascii "name=test" https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：HTTP
- 注意事项：`--data-ascii` 是 `--data` 的别名

### `--data-urlencode <data>`

- 作用：对 POST 数据进行 URL 编码后发送
- 语法：`curl --data-urlencode "<data>" <url>`
- 示例：
```bash
# 全部编码
curl --data-urlencode "name=张三" https://$HOST/api
# 只编码值
curl --data-urlencode "name=张三" https://$HOST/api
# 从文件读取并编码
curl --data-urlencode "data=@file.txt" https://$HOST/api
# 编码已存在的查询字符串
curl --data-urlencode "=name=张三&email=test" https://$HOST/api
```
- 版本要求：7.18.0+
- 平台/协议限制：HTTP
- 注意事项：`name=value` 只编码 value 部分；`=value` 编码全部；`@file` 从文件读取

### `--json <data>`

- 作用：发送 JSON 请求（设置 Content-Type: application/json，Accept: application/json）
- 语法：`curl --json "<json string>" <url>`
- 示例：
```bash
curl --json '{"name":"test","email":"test@example.com"}' https://$HOST/api/users
# 从文件读取
curl --json "@payload.json" https://$HOST/api/users
# 从 stdin
cat data.json | curl --json "@-" https://$HOST/api/users
```
- 版本要求：7.82.0+（8.x 稳定）
- 平台/协议限制：HTTP
- 注意事项：`--json` 等同于 `-H "Content-Type: application/json" -H "Accept: application/json" --data`。`@file` 从文件读取

---

### 5.4 表单与文件上传

### `-F, --form <name=content>`

- 作用：发送 multipart/form-data 表单（支持文件上传）
- 语法：`curl -F "<name>=<content>" <url>`
- 示例：
```bash
# 普通字段
curl -F "name=test" -F "age=30" https://$HOST/api/upload

# 上传文件
curl -F "file=@$FILE" https://$HOST/api/upload

# 指定文件名和 Content-Type
curl -F "file=@$FILE;filename=custom.csv;type=text/csv" https://$HOST/api/upload

# 多文件上传
curl -F "files[]=@file1.txt" -F "files[]=@file2.txt" https://$HOST/api/upload

# 从 stdin 读取
echo "content" | curl -F "file=@-" https://$HOST/api/upload
```
- 版本要求：7.x+
- 平台/协议限制：HTTP/SMTP
- 注意事项：`@` 表示文件，`<` 表示从文件读取内容作为文本字段。安全提醒：`@file` 可能意外读取敏感文件

### `--form-string <name=string>`

- 作用：发送纯字符串表单字段（不以 `@` 开头的文件引用）
- 语法：`curl --form-string "<name>=<string>" <url>`
- 示例：
```bash
curl --form-string "filename=@special" https://$HOST/api/upload
```
- 版本要求：7.x+
- 平台/协议限制：HTTP/SMTP
- 注意事项：当字段值以 `@` 开头但不是文件引用时使用

### `--form-escape`

- 作用：在 multipart 表单中对字段名和文件名进行反斜杠转义
- 语法：`curl --form-escape -F "name=value" <url>`
- 示例：
```bash
curl --form-escape -F 'file=@C:\path\to\file.txt' https://$HOST/api/upload
```
- 版本要求：7.81.0+
- 平台/协议限制：HTTP
- 注意事项：Windows 路径中的反斜杠可能被误解为转义字符

### `-T, --upload-file <file>`

- 作用：上传文件（使用 PUT 方法或 FTP/SCP/SFTP 协议）
- 语法：`curl -T <file> <url>`
- 示例：
```bash
# HTTP PUT 上传
curl -T $FILE https://$HOST/api/upload

# FTP 上传
curl -T $FILE ftp://$HOST/upload/

# 从 stdin 上传
curl -T - https://$HOST/api/upload < data.txt

# 批量上传（通配符）
curl -T "{file1,file2}" ftp://$HOST/upload/
```
- 版本要求：7.x+
- 平台/协议限制：HTTP/FTP/FTPS/SCP/SFTP
- 注意事项：HTTP 默认使用 PUT 方法。`-T -` 从 stdin 读取。`-T` 与 `-F` 不同：`-T` 上传整个请求体

---

### 5.5 下载与输出

### `-o, --output <file>`

- 作用：将响应保存到文件
- 语法：`curl -o <file> <url>`
- 示例：
```bash
curl -o output.txt https://$HOST/file.txt
# 通配符引用
curl -o "file_#1.txt" https://$HOST/file[1-5].txt
# 输出到 /dev/null（只测速/测连通性）
curl -o /dev/null -s -w "%{http_code}" https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：所有协议
- 注意事项：`#1` 引用 URL 通配符的第一个匹配组

### `-O, --remote-name`

- 作用：使用 URL 中的文件名保存到当前目录
- 语法：`curl -O <url>`
- 示例：
```bash
curl -O https://$HOST/file.txt  # 保存为 file.txt
curl -O https://$HOST/file[1-10].txt  # 下载 10 个文件
```
- 版本要求：7.x+
- 平台/协议限制：所有协议
- 注意事项：URL 末尾无文件名时此选项无效

### `-O, --remote-name-all`

- 作用：对所有 URL 使用 `-O` 行为
- 语法：`curl --remote-name-all <url1> <url2>`
- 示例：
```bash
curl --remote-name-all https://$HOST/file1.txt https://$HOST/file2.txt
```
- 版本要求：7.x+
- 平台/协议限制：所有协议
- 注意事项：不需要为每个 URL 单独指定 `-O`

### `-J, --remote-header-name`

- 作用：使用响应头中的 Content-Disposition 文件名保存
- 语法：`curl -OJ <url>`
- 示例：
```bash
curl -OJ https://$HOST/download
# 服务器返回：Content-Disposition: attachment; filename="report.pdf"
# 文件保存为 report.pdf
```
- 版本要求：7.x+
- 平台/协议限制：HTTP
- 注意事项：需要与 `-O` 配合使用。文件名可能包含恶意路径，存在路径穿越风险

### `-C, --continue-at <offset>`

- 作用：断点续传（从指定偏移开始下载）
- 语法：`curl -C <offset> -o <file> <url>` 或 `curl -C - -o <file> <url>`
- 示例：
```bash
# 自动检测续传位置
curl -C - -o largefile.zip https://$HOST/largefile.zip

# 手动指定偏移
curl -C 1000 -o file.txt https://$HOST/file.txt

# 上传续传
curl -C - -T largefile.zip ftp://$HOST/upload/
```
- 版本要求：7.x+
- 平台/协议限制：HTTP/FTP/SFTP/SCP
- 注意事项：`-C -` 让 curl 自动检测已下载大小。服务器必须支持 Range 请求

### `--create-dirs`

- 作用：配合 `-o` 自动创建本地目录结构
- 语法：`curl --create-dirs -o <path/file> <url>`
- 示例：
```bash
curl --create-dirs -o /tmp/download/sub/file.txt https://$HOST/file.txt
```
- 版本要求：7.x+
- 平台/协议限制：所有协议
- 注意事项：仅创建 `-o` 路径中不存在的目录

### `--output-dir <dir>`

- 作用：指定 `-O`/`-o` 的输出目录
- 语法：`curl --output-dir <dir> -O <url>`
- 示例：
```bash
curl --output-dir /tmp/downloads -O https://$HOST/file1.txt -O https://$HOST/file2.txt
```
- 版本要求：7.73.0+
- 平台/协议限制：所有协议
- 注意事项：目录必须已存在（不自动创建，除非配合 `--create-dirs`）

### `--no-clobber`

- 作用：不覆盖已存在的本地文件
- 语法：`curl --no-clobber -O <url>`
- 示例：
```bash
curl --no-clobber -O https://$HOST/file[1-5].txt
```
- 版本要求：8.4.0+
- 平台/协议限制：所有协议
- 注意事项：与 `-o` 配合使用时，如果文件已存在则报错

### `--remove-on-error`

- 作用：传输失败时删除已创建的输出文件
- 语法：`curl --remove-on-error -o <file> <url>`
- 示例：
```bash
curl --remove-on-error -o output.txt https://$HOST/file.txt
```
- 版本要求：8.x
- 平台/协议限制：所有协议
- 注意事项：避免留下不完整的下载文件

### `-R, --remote-time`

- 作用：保存文件时使用服务器返回的时间戳
- 语法：`curl -RO <url>`
- 示例：
```bash
curl -RO https://$HOST/file.txt
# 文件修改时间 = 服务器 Last-Modified 时间
```
- 版本要求：7.x+
- 平台/协议限制：HTTP/FTP
- 注意事项：与 `-O` 或 `-o` 配合使用

### `--max-filesize <bytes>`

- 作用：限制最大下载文件大小
- 语法：`curl --max-filesize <bytes> <url>`
- 示例：
```bash
curl --max-filesize 1000000 -O https://$HOST/file.zip  # 最大 1MB
```
- 版本要求：7.x+
- 平台/协议限制：HTTP/FTP
- 注意事项：仅对有 Content-Length 的响应有效。超过限制时返回退出码 63

### `-r, --range <range>`

- 作用：请求指定字节范围
- 语法：`curl -r <start-end> <url>`
- 示例：
```bash
# 下载前 1024 字节
curl -r 0-1023 -o part1.bin https://$HOST/largefile.bin

# 从 1024 字节到末尾
curl -r 1024- -o part2.bin https://$HOST/largefile.bin

# 最后 512 字节
curl -r -512 -o tail.bin https://$HOST/largefile.bin
```
- 版本要求：7.x+
- 平台/协议限制：HTTP/FTP/FILE/SFTP
- 注意事项：服务器必须支持 Range 请求（HTTP 206 Partial Content）

### `-N, --no-buffer`

- 作用：禁用输出缓冲，实时输出数据
- 语法：`curl -N <url>`
- 示例：
```bash
curl -N https://$HOST/stream  # 实时输出流数据
```
- 版本要求：7.x+
- 平台/协议限制：所有协议
- 注意事项：对流式数据（SSE/streaming API）有用

### `--xattr`

- 作用：将下载文件的 URL 和 Content-Type 存入文件扩展属性
- 语法：`curl --xattr -O <url>`
- 示例：
```bash
curl --xattr -O https://$HOST/file.txt
# 查看扩展属性
getfattr -d file.txt
```
- 版本要求：7.x+
- 平台/协议限制：Linux/macOS（文件系统需支持 xattr）
- 注意事项：URL 中可能包含敏感信息（Token/凭据）

---

### 5.6 认证与凭据

### `-u, --user <user:password>`

- 作用：设置服务器认证凭据
- 语法：`curl -u <user:password> <url>`
- 示例：
```bash
curl -u admin:secret https://$HOST/api
# 只输入用户名，密码交互式输入
curl -u admin https://$HOST/api
# 从 netrc 读取（不在此指定）
curl -n https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：HTTP/FTP/SCP/SFTP/SMTP/IMAP/POP3/LDAP
- 注意事项：**安全警告**：密码会出现在 `ps` 输出和 shell 历史中。建议使用 `--netrc-file` 或 `-u user` 交互输入

### `--oauth2-bearer <token>`

- 作用：设置 OAuth 2.0 Bearer Token 认证
- 语法：`curl --oauth2-bearer "<token>" <url>`
- 示例：
```bash
curl --oauth2-bearer "$TOKEN" https://$HOST/api/protected
```
- 版本要求：7.33.0+
- 平台/协议限制：HTTP/IMAP/POP3/SMTP
- 注意事项：等效于 `-H "Authorization: Bearer <token>"`。**安全警告**：Token 会出现在进程列表中

### `--basic`

- 作用：使用 HTTP Basic 认证（默认）
- 语法：`curl --basic -u <user:pass> <url>`
- 示例：
```bash
curl --basic -u admin:secret https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：HTTP
- 注意事项：Basic 认证以 Base64 编码发送凭据，非加密。仅在 HTTPS 下使用

### `--digest`

- 作用：使用 HTTP Digest 认证
- 语法：`curl --digest -u <user:pass> <url>`
- 示例：
```bash
curl --digest -u admin:secret https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：HTTP
- 注意事项：比 Basic 更安全，不直接发送密码

### `--ntlm`

- 作用：使用 HTTP NTLM 认证
- 语法：`curl --ntlm -u <user:pass> <url>`
- 示例：
```bash
curl --ntlm -u 'DOMAIN\user:pass' https://$HOST/api
```
- 版本要求：7.x+（需要 OpenSSL 编译支持）
- 平台/协议限制：HTTP
- 注意事项：NTLM 用于 Windows 域环境

### `--ntlm-wb`

- 作用：NTLM WinBridger 认证（使用外部助手程序）
- 语法：`curl --ntlm-wb -u <user:pass> <url>`
- 示例：
```bash
curl --ntlm-wb -u 'DOMAIN\user:pass' https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：HTTP
- 注意事项：用于通过 Samba/Winbind 进行 NTLM 认证

### `--negotiate`

- 作用：使用 HTTP Negotiate (SPNEGO) 认证
- 语法：`curl --negotiate -u : <url>`
- 示例：
```bash
curl --negotiate -u : https://$HOST/api
```
- 版本要求：7.x+（需要 GSS-API 编译支持）
- 平台/协议限制：HTTP
- 注意事项：用于 Kerberos/SPNEGO 环境

### `--anyauth`

- 作用：自动选择最安全的认证方式
- 语法：`curl --anyauth -u <user:pass> <url>`
- 示例：
```bash
curl --anyauth -u admin:secret https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：HTTP
- 注意事项：会先发送无认证请求，再根据 401 响应选择认证方式

### `--aws-sigv4 <provider1[:provider2[:region[:service]]]>`

- 作用：使用 AWS Signature V4 认证
- 语法：`curl --aws-sigv4 "<provider:region:service>" --user "<key:secret>" <url>`
- 示例：
```bash
curl --aws-sigv4 "aws:amz:us-east-1:s3" --user "$ACCESS_KEY:$SECRET_KEY" \
  https://s3.amazonaws.com/my-bucket/object
```
- 版本要求：7.75.0+
- 平台/协议限制：HTTP
- 注意事项：用于 AWS API 访问

### `-n, --netrc`

- 作用：从 `~/.netrc` 文件读取认证凭据
- 语法：`curl -n <url>`
- 示例：
```bash
# ~/.netrc 文件格式：
# machine example.com login admin password secret

curl -n https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：HTTP/FTP
- 注意事项：**安全警告**：`~/.netrc` 包含明文密码，需设置 `chmod 600 ~/.netrc`

### `--netrc-file <file>`

- 作用：指定自定义 netrc 文件
- 语法：`curl --netrc-file <file> <url>`
- 示例：
```bash
curl --netrc-file ~/.netrc-custom https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：HTTP/FTP
- 注意事项：比 `-n` 更灵活，可指定非默认位置

### `--netrc-optional`

- 作用：可选地读取 netrc（文件不存在不报错）
- 语法：`curl --netrc-optional <url>`
- 示例：
```bash
curl --netrc-optional https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：HTTP/FTP
- 注意事项：与 `--netrc-file` 配合使用

### `--sasl-authzid <identity>`

- 作用：设置 SASL 授权身份
- 语法：`curl --sasl-authzid "<identity>" <url>`
- 示例：
```bash
curl --sasl-authzid "authzid@realm" -u "authcid:pass" imap://$HOST/
```
- 版本要求：8.3.0+
- 平台/协议限制：IMAP/SMTP/POP3/LDAP
- 注意事项：用于 SASL 认证中的代理授权

### `--sasl-ir`

- 作用：启用 SASL 初始响应（Initial Response）
- 语法：`curl --sasl-ir <url>`
- 示例：
```bash
curl --sasl-ir -u user:pass imap://$HOST/
```
- 版本要求：7.x+
- 平台/协议限制：IMAP/SMTP/POP3/LDAP
- 注意事项：减少认证往返

### `--service-name <name>`

- 作用：设置 SPNEGO 认证的服务名
- 语法：`curl --service-name "<name>" --negotiate <url>`
- 示例：
```bash
curl --service-name "HTTP/$HOST" --negotiate -u : https://$HOST/api
```
- 版本要求：7.43.0+
- 平台/协议限制：HTTP
- 注意事项：默认服务名为 `HTTP/<host>`

---

### 5.7 Cookie 与会话

### `-b, --cookie <data|file>`

- 作用：发送 Cookie
- 语法：`curl -b "<cookie data>" <url>` 或 `curl -b <cookie_file> <url>`
- 示例：
```bash
# 直接指定 Cookie
curl -b "session=abc123; user=test" https://$HOST/api

# 从文件读取 Cookie
curl -b cookies.txt https://$HOST/api

# 从 `-c` 保存的文件读取
curl -c cookies.txt -L https://$HOST/login
curl -b cookies.txt https://$HOST/dashboard
```
- 版本要求：7.x+
- 平台/协议限制：HTTP
- 注意事项：`-b` 接收文件时，文件格式应为 Netscape/Mozilla cookies.txt 格式

### `-c, --cookie-jar <file>`

- 作用：将响应中的 Cookie 保存到文件
- 语法：`curl -c <file> <url>`
- 示例：
```bash
# 登录并保存 Cookie
curl -c cookies.txt -d "user=admin&pass=secret" -L https://$HOST/login

# 使用保存的 Cookie
curl -b cookies.txt https://$HOST/dashboard

# 输出到 stdout
curl -c - -o /dev/null https://$HOST/
```
- 版本要求：7.x+
- 平台/协议限制：HTTP
- 注意事项：`-c -` 输出到 stdout

### `-j, --junk-session-cookies`

- 作用：忽略会话 Cookie（过期时间为 0 的 Cookie）
- 语法：`curl -j -b <file> <url>`
- 示例：
```bash
curl -j -b cookies.txt https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：HTTP
- 注意事项：用于只加载持久 Cookie，忽略会话 Cookie

---

### 5.8 代理

### `-x, --proxy [protocol://]host[:port]`

- 作用：使用指定代理服务器
- 语法：`curl -x "[protocol://]host[:port]" <url>`
- 示例：
```bash
# HTTP 代理
curl -x http://proxy.example.com:8080 https://$HOST/api

# SOCKS5 代理
curl -x socks5://proxy.example.com:1080 https://$HOST/api

# SOCKS5 远程 DNS
curl -x socks5h://proxy.example.com:1080 https://$HOST/api

# 使用环境变量代理
curl --proxy http://$PROXY_HOST:$PROXY_PORT https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：所有协议
- 注意事项：支持的代理协议：http, https, socks4, socks4a, socks5, socks5h。`socks5h` 表示 DNS 在代理端解析

### `-U, --proxy-user <user:password>`

- 作用：设置代理认证凭据
- 语法：`curl -U <user:password> -x <proxy> <url>`
- 示例：
```bash
curl -U proxyuser:proxypass -x http://proxy.example.com:8080 https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：所有协议
- 注意事项：**安全警告**：同 `-u`，密码会出现在进程列表中

### `--proxy-header <header>`

- 作用：添加代理请求头（只发送给代理，不发送给目标服务器）
- 语法：`curl --proxy-header "<Header: value>" -x <proxy> <url>`
- 示例：
```bash
curl --proxy-header "Proxy-Authorization: Bearer $TOKEN" -x http://proxy:8080 https://$HOST/api
```
- 版本要求：7.37.0+
- 平台/协议限制：HTTP
- 注意事项：与 `-H` 不同，`--proxy-header` 只影响到代理的请求

### `--noproxy <no-proxy-list>`

- 作用：指定不使用代理的主机列表
- 语法：`curl --noproxy "<host1,host2,..." <url>`
- 示例：
```bash
curl --noproxy "localhost,127.0.0.1,.internal.example.com" -x http://proxy:8080 https://$HOST/api
# 禁用所有代理
curl --noproxy "*" https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：所有协议
- 注意事项：也影响 `http_proxy`/`https_proxy` 环境变量

### `--proxy1.0 <host[:port]>`

- 作用：使用 HTTP/1.0 代理
- 语法：`curl --proxy1.0 <host[:port]> <url>`
- 示例：
```bash
curl --proxy1.0 proxy.example.com:8080 https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：HTTP
- 注意事项：某些老代理不支持 HTTP/1.1

### `--preproxy [protocol://]host[:port]`

- 作用：设置预代理（代理链：先连预代理，再连目标代理）
- 语法：`curl --preproxy "[protocol://]host[:port]" -x <proxy> <url>`
- 示例：
```bash
curl --preproxy socks5://pre-proxy:1080 -x http://proxy:8080 https://$HOST/api
```
- 版本要求：7.52.0+
- 平台/协议限制：所有协议
- 注意事项：用于多层代理场景

### `-p, --proxytunnel`

- 作用：通过 HTTP 代理创建隧道（用于非 HTTP 协议通过 HTTP 代理）
- 语法：`curl -p -x <proxy> <url>`
- 示例：
```bash
curl -p -x http://proxy:8080 ftp://$HOST/file.txt
```
- 版本要求：7.x+
- 平台/协议限制：所有协议
- 注意事项：HTTPS 默认使用 CONNECT 隧道，非 HTTP 协议需要 `-p`

### `--proxy-anyauth`

- 作用：代理自动选择认证方式
- 语法：`curl --proxy-anyauth -U <user:pass> -x <proxy> <url>`
- 示例：
```bash
curl --proxy-anyauth -U admin:secret -x http://proxy:8080 https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：HTTP
- 注意事项：同 `--anyauth`，但用于代理认证

### `--proxy-basic`

- 作用：代理使用 Basic 认证
- 语法：`curl --proxy-basic -U <user:pass> -x <proxy> <url>`
- 示例：
```bash
curl --proxy-basic -U admin:secret -x http://proxy:8080 https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：HTTP

### `--proxy-digest`

- 作用：代理使用 Digest 认证
- 语法：`curl --proxy-digest -U <user:pass> -x <proxy> <url>`
- 示例：
```bash
curl --proxy-digest -U admin:secret -x http://proxy:8080 https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：HTTP

### `--proxy-negotiate`

- 作用：代理使用 Negotiate (SPNEGO) 认证
- 语法：`curl --proxy-negotiate -U <user:pass> -x <proxy> <url>`
- 示例：
```bash
curl --proxy-negotiate -U : -x http://proxy:8080 https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：HTTP

### `--proxy-ntlm`

- 作用：代理使用 NTLM 认证
- 语法：`curl --proxy-ntlm -U <user:pass> -x <proxy> <url>`
- 示例：
```bash
curl --proxy-ntlm -U 'DOMAIN\user:pass' -x http://proxy:8080 https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：HTTP

### `--proxy-http2`

- 作用：代理使用 HTTP/2
- 语法：`curl --proxy-http2 -x <proxy> <url>`
- 示例：
```bash
curl --proxy-http2 -x http://proxy:8080 https://$HOST/api
```
- 版本要求：8.1.0+
- 平台/协议限制：HTTP
- 注意事项：需要代理支持 HTTP/2

### `--proxy-insecure`

- 作用：代理跳过 TLS 证书验证
- 语法：`curl --proxy-insecure -x https://proxy:8443 <url>`
- 示例：
```bash
curl --proxy-insecure -x https://proxy.example.com:8443 https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：HTTPS 代理
- 注意事项：**安全警告**：同 `-k`，存在中间人攻击风险

### `--proxy-ca-native`

- 作用：代理使用系统原生 CA 存储
- 语法：`curl --proxy-ca-native -x https://proxy:8443 <url>`
- 示例：
```bash
curl --proxy-ca-native -x https://proxy:8443 https://$HOST/api
```
- 版本要求：8.2.0+
- 平台/协议限制：HTTPS 代理

### `--proxy-cacert <file>`

- 作用：设置代理 CA 证书
- 语法：`curl --proxy-cacert <file> -x https://proxy:8443 <url>`
- 示例：
```bash
curl --proxy-cacert /etc/ssl/certs/proxy-ca.pem -x https://proxy:8443 https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：HTTPS 代理

### `--proxy-capath <dir>`

- 作用：设置代理 CA 证书目录
- 语法：`curl --proxy-capath <dir> -x https://proxy:8443 <url>`
- 示例：
```bash
curl --proxy-capath /etc/ssl/certs -x https://proxy:8443 https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：HTTPS 代理

### `--proxy-cert <cert[:passwd]>`

- 作用：设置代理客户端证书
- 语法：`curl --proxy-cert <file> -x https://proxy:8443 <url>`
- 示例：
```bash
curl --proxy-cert client.pem -x https://proxy:8443 https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：HTTPS 代理

### `--proxy-cert-type <type>`

- 作用：设置代理证书类型（PEM/DER/ENG/P12）
- 语法：`curl --proxy-cert-type PEM --proxy-cert <file> -x https://proxy:8443 <url>`
- 示例：
```bash
curl --proxy-cert-type DER --proxy-cert client.der -x https://proxy:8443 https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：HTTPS 代理

### `--proxy-ciphers <list>`

- 作用：设置代理 TLS 密码套件
- 语法：`curl --proxy-ciphers "<list>" -x https://proxy:8443 <url>`
- 示例：
```bash
curl --proxy-ciphers "HIGH:!aNULL" -x https://proxy:8443 https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：HTTPS 代理

### `--proxy-crlfile <file>`

- 作用：设置代理 CRL（证书吊销列表）文件
- 语法：`curl --proxy-crlfile <file> -x https://proxy:8443 <url>`
- 示例：
```bash
curl --proxy-crlfile crl.pem -x https://proxy:8443 https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：HTTPS 代理

### `--proxy-key <key>`

- 作用：设置代理客户端私钥
- 语法：`curl --proxy-key <file> --proxy-cert <cert> -x https://proxy:8443 <url>`
- 示例：
```bash
curl --proxy-key client.key --proxy-cert client.pem -x https://proxy:8443 https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：HTTPS 代理

### `--proxy-key-type <type>`

- 作用：设置代理私钥类型（PEM/DER/ENG）
- 语法：`curl --proxy-key-type PEM --proxy-key <file> -x https://proxy:8443 <url>`
- 示例：
```bash
curl --proxy-key-type DER --proxy-key client.der -x https://proxy:8443 https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：HTTPS 代理

### `--proxy-pass <phrase>`

- 作用：设置代理私钥密码短语
- 语法：`curl --proxy-pass "<passphrase>" --proxy-key <file> -x https://proxy:8443 <url>`
- 示例：
```bash
curl --proxy-pass "secret" --proxy-key client.key -x https://proxy:8443 https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：HTTPS 代理

### `--proxy-pinnedpubkey <hashes>`

- 作用：锁定代理公钥指纹
- 语法：`curl --proxy-pinnedpubkey "<hashes>" -x https://proxy:8443 <url>`
- 示例：
```bash
curl --proxy-pinnedpubkey "sha256//base64==" -x https://proxy:8443 https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：HTTPS 代理

### `--proxy-ssl-allow-beast`

- 作用：代理允许 BEAST 攻击缓解（不进行某些 TLS 修复）
- 语法：`curl --proxy-ssl-allow-beast -x https://proxy:8443 <url>`
- 示例：
```bash
curl --proxy-ssl-allow-beast -x https://proxy:8443 https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：HTTPS 代理
- 注意事项：不建议使用，存在安全风险

### `--proxy-ssl-auto-client-cert`

- 作用：代理自动选择客户端证书
- 语法：`curl --proxy-ssl-auto-client-cert -x https://proxy:8443 <url>`
- 示例：
```bash
curl --proxy-ssl-auto-client-cert -x https://proxy:8443 https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：HTTPS 代理（Schannel）

### `--proxy-tls13-ciphers <list>`

- 作用：设置代理 TLS 1.3 密码套件
- 语法：`curl --proxy-tls13-ciphers "<list>" -x https://proxy:8443 <url>`
- 示例：
```bash
curl --proxy-tls13-ciphers "TLS_AES_256_GCM_SHA384" -x https://proxy:8443 https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：HTTPS 代理

### `--proxy-tlsauthtype <type>`

- 作用：设置代理 TLS 认证类型（SRP）
- 语法：`curl --proxy-tlsauthtype SRP --proxy-tlsuser <user> -x https://proxy:8443 <url>`
- 示例：
```bash
curl --proxy-tlsauthtype SRP --proxy-tlsuser user --proxy-tlspassword pass -x https://proxy:8443 https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：HTTPS 代理

### `--proxy-tlsuser <user>`

- 作用：设置代理 TLS 用户名
- 语法：`curl --proxy-tlsuser <user> -x https://proxy:8443 <url>`
- 示例：
```bash
curl --proxy-tlsuser user --proxy-tlspassword pass --proxy-tlsauthtype SRP -x https://proxy:8443 https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：HTTPS 代理

### `--proxy-tlspassword <pwd>`

- 作用：设置代理 TLS 密码
- 语法：`curl --proxy-tlspassword <pwd> -x https://proxy:8443 <url>`
- 示例：
```bash
curl --proxy-tlspassword pass --proxy-tlsuser user --proxy-tlsauthtype SRP -x https://proxy:8443 https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：HTTPS 代理

### `--proxy-tlsv1`

- 作用：代理使用 TLS 1.x
- 语法：`curl --proxy-tlsv1 -x https://proxy:8443 <url>`
- 示例：
```bash
curl --proxy-tlsv1 -x https://proxy:8443 https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：HTTPS 代理

### `--proxy-service-name <name>`

- 作用：设置代理 SPNEGO 服务名
- 语法：`curl --proxy-service-name "<name>" --proxy-negotiate -x <proxy> <url>`
- 示例：
```bash
curl --proxy-service-name "HTTP/proxy" --proxy-negotiate -U : -x http://proxy:8080 https://$HOST/api
```
- 版本要求：7.43.0+
- 平台/协议限制：HTTP 代理

### `--socks4 <host[:port]>`

- 作用：使用 SOCKS4 代理
- 语法：`curl --socks4 <host[:port]> <url>`
- 示例：
```bash
curl --socks4 proxy.example.com:1080 https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：所有协议
- 注意事项：SOCKS4 不支持认证和远程 DNS

### `--socks4a <host[:port]>`

- 作用：使用 SOCKS4a 代理（远程 DNS 解析）
- 语法：`curl --socks4a <host[:port]> <url>`
- 示例：
```bash
curl --socks4a proxy.example.com:1080 https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：所有协议
- 注意事项：SOCKS4a 在 SOCKS4 基础上支持远程 DNS

### `--socks5 <host[:port]>`

- 作用：使用 SOCKS5 代理（本地 DNS）
- 语法：`curl --socks5 <host[:port]> <url>`
- 示例：
```bash
curl --socks5 proxy.example.com:1080 https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：所有协议
- 注意事项：SOCKS5 本地解析 DNS

### `--socks5-hostname <host[:port]>`

- 作用：使用 SOCKS5 代理（远程 DNS 解析）
- 语法：`curl --socks5-hostname <host[:port]> <url>`
- 示例：
```bash
curl --socks5-hostname proxy.example.com:1080 https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：所有协议
- 注意事项：等效于 `socks5h://` scheme

### `--socks5-basic`

- 作用：SOCKS5 使用用户名/密码认证
- 语法：`curl --socks5-basic --socks5 <host[:port]> <url>`
- 示例：
```bash
curl --socks5-basic -U user:pass --socks5 proxy:1080 https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：SOCKS5

### `--socks5-gssapi`

- 作用：SOCKS5 使用 GSS-API 认证
- 语法：`curl --socks5-gssapi --socks5 <host[:port]> <url>`
- 示例：
```bash
curl --socks5-gssapi --socks5 proxy:1080 https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：SOCKS5

### `--socks5-gssapi-nec`

- 作用：SOCKS5 GSS-API NEC 模式
- 语法：`curl --socks5-gssapi-nec --socks5-gssapi --socks5 <host[:port]> <url>`
- 示例：
```bash
curl --socks5-gssapi-nec --socks5-gssapi --socks5 proxy:1080 https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：SOCKS5

### `--socks5-gssapi-service <name>`

- 作用：SOCKS5 GSS-API 服务名
- 语法：`curl --socks5-gssapi-service "<name>" --socks5-gssapi --socks5 <host[:port]> <url>`
- 示例：
```bash
curl --socks5-gssapi-service "rcmd/proxy" --socks5-gssapi --socks5 proxy:1080 https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：SOCKS5

---

### 5.9 TLS/SSL/证书

### `-k, --insecure`

- 作用：跳过 TLS 证书验证
- 语法：`curl -k <url>` 或 `curl --insecure <url>`
- 示例：
```bash
curl -k https://self-signed.example.com/api
```
- 版本要求：7.x+
- 平台/协议限制：HTTPS/FTPS/IMAPS/POP3S/SMTPS
- 注意事项：**安全警告**：跳过证书验证会导致中间人攻击风险。仅在测试环境使用

### `--cacert <file>`

- 作用：指定 CA 证书文件
- 语法：`curl --cacert <file> <url>`
- 示例：
```bash
curl --cacert /etc/ssl/certs/ca-certificates.crt https://$HOST/api
curl --cacert custom-ca.pem https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：TLS
- 注意事项：替代系统默认 CA 证书

### `--capath <dir>`

- 作用：指定 CA 证书目录
- 语法：`curl --capath <dir> <url>`
- 示例：
```bash
curl --capath /etc/ssl/certs https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：TLS
- 注意事项：目录中需有哈希命名的证书文件（c_rehash 生成）

### `--ca-native`

- 作用：使用操作系统原生 CA 存储
- 语法：`curl --ca-native <url>`
- 示例：
```bash
curl --ca-native https://$HOST/api
```
- 版本要求：8.2.0+
- 平台/协议限制：TLS；取决于操作系统和编译选项
- 注意事项：使用系统自带的 CA 证书（如 Windows 证书存储、macOS Keychain）

### `--cert-status`

- 作用：验证服务器证书状态（OCSP Stapling）
- 语法：`curl --cert-status <url>`
- 示例：
```bash
curl --cert-status https://$HOST/api
```
- 版本要求：7.41.0+
- 平台/协议限制：HTTPS（OpenSSL/GnuTLS/Schannel）
- 注意事项：要求服务器支持 OCSP Stapling

### `-E, --cert <cert[:passwd]>`

- 作用：指定客户端证书
- 语法：`curl -E <file> <url>` 或 `curl --cert <file> <url>`
- 示例：
```bash
curl -E client.pem https://$HOST/api
curl -E client.p12:password https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：TLS
- 注意事项：需与 `--key` 配合使用

### `--cert-type <type>`

- 作用：指定证书类型
- 语法：`curl --cert-type <type> --cert <file> <url>`
- 示例：
```bash
curl --cert-type PEM --cert client.pem https://$HOST/api
curl --cert-type P12 --cert client.p12 https://$HOST/api
curl --cert-type DER --cert client.der https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：TLS
- 注意事项：支持 PEM/DER/ENG/P12

### `--key <key>`

- 作用：指定私钥文件
- 语法：`curl --key <file> --cert <file> <url>`
- 示例：
```bash
curl --key client.key --cert client.pem https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：TLS

### `--key-type <type>`

- 作用：指定私钥类型
- 语法：`curl --key-type <type> --key <file> <url>`
- 示例：
```bash
curl --key-type PEM --key client.key https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：TLS

### `--pass <phrase>`

- 作用：指定私钥密码短语
- 语法：`curl --pass "<passphrase>" --key <file> <url>`
- 示例：
```bash
curl --pass "secret" --key client.key --cert client.pem https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：TLS
- 注意事项：**安全警告**：密码短语会出现在进程列表中

### `--ciphers <list>`

- 作用：指定 TLS 密码套件
- 语法：`curl --ciphers "<list>" <url>`
- 示例：
```bash
curl --ciphers "HIGH:!aNULL:!eNULL:!EXPORT:!DES:!MD5:!PSK:!RC4" https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：TLS
- 注意事项：密码套件语法取决于 TLS 后端（OpenSSL/GnuTLS 等）

### `--tls13-ciphers <list>`

- 作用：指定 TLS 1.3 密码套件
- 语法：`curl --tls13-ciphers "<list>" <url>`
- 示例：
```bash
curl --tls13-ciphers "TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256" https://$HOST/api
```
- 版本要求：7.61.0+
- 平台/协议限制：TLS 1.3

### `--curves <curves>`

- 作用：指定 TLS 椭圆曲线
- 语法：`curl --curves "<curves>" <url>`
- 示例：
```bash
curl --curves "X25519:P-256:P-384" https://$HOST/api
```
- 版本要求：7.73.0+
- 平台/协议限制：TLS（OpenSSL）

### `--crlfile <file>`

- 作用：指定 CRL（证书吊销列表）文件
- 语法：`curl --crlfile <file> <url>`
- 示例：
```bash
curl --crlfile crl.pem https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：TLS

### `--ssl-allow-beast`

- 作用：允许 BEAST 攻击缓解（不进行 1/n-1 记录分割）
- 语法：`curl --ssl-allow-beast <url>`
- 示例：
```bash
curl --ssl-allow-beast https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：TLS
- 注意事项：不建议使用

### `--ssl-no-revoke`

- 作用：禁用 CRL 检查
- 语法：`curl --ssl-no-revoke <url>`
- 示例：
```bash
curl --ssl-no-revoke https://$HOST/api
```
- 版本要求：7.44.0+
- 平台/协议限制：Schannel（Windows）

### `--ssl-revoke-best-effort`

- 作用：尽力进行 CRL 检查（失败不中止）
- 语法：`curl --ssl-revoke-best-effort <url>`
- 示例：
```bash
curl --ssl-revoke-best-effort https://$HOST/api
```
- 版本要求：7.69.0+
- 平台/协议限制：Schannel（Windows）

### `--ssl-auto-client-cert`

- 作用：自动使用系统证书存储中的客户端证书
- 语法：`curl --ssl-auto-client-cert <url>`
- 示例：
```bash
curl --ssl-auto-client-cert https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：Schannel（Windows）

### `--pinnedpubkey <hashes>`

- 作用：锁定服务器公钥指纹
- 语法：`curl --pinnedpubkey "<hashes>" <url>`
- 示例：
```bash
curl --pinnedpubkey "sha256//base64==" https://$HOST/api
# 多个指纹（任一匹配即可）
curl --pinnedpubkey "sha256//hash1;sha256//hash2" https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：TLS
- 注意事项：用于证书锁定（HPKP），防止 CA 被攻破后的中间人攻击

### `--false-start`

- 作用：启用 TLS False Start
- 语法：`curl --false-start <url>`
- 示例：
```bash
curl --false-start https://$HOST/api
```
- 版本要求：7.42.0+
- 平台/协议限制：TLS
- 注意事项：减少 TLS 握手往返，但需确保安全性

### `--tls-earlydata`

- 作用：启用 TLS 0-RTT 数据
- 语法：`curl --tls-earlydata <url>`
- 示例：
```bash
curl --tls-earlydata https://$HOST/api
```
- 版本要求：8.3.0+
- 平台/协议限制：TLS 1.3
- 注意事项：0-RTT 数据存在重放攻击风险

### `--tls-max <VERSION>`

- 作用：设置最大 TLS 版本
- 语法：`curl --tls-max <VERSION> <url>`
- 示例：
```bash
curl --tls-max 1.2 https://$HOST/api
```
- 版本要求：7.54.0+
- 平台/协议限制：TLS
- 注意事项：支持 1.0/1.1/1.2/1.3

### `--tlsv1`

- 作用：使用 TLS 1.x（至少 1.0）
- 语法：`curl --tlsv1 <url>`
- 示例：
```bash
curl --tlsv1 https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：TLS

### `--tlsv1.0`

- 作用：使用 TLS 1.0
- 语法：`curl --tlsv1.0 <url>`
- 示例：
```bash
curl --tlsv1.0 https://$HOST/api
```
- 版本要求：7.34.0+
- 平台/协议限制：TLS 1.0

### `--tlsv1.1`

- 作用：使用 TLS 1.1
- 语法：`curl --tlsv1.1 <url>`
- 示例：
```bash
curl --tlsv1.1 https://$HOST/api
```
- 版本要求：7.34.0+
- 平台/协议限制：TLS 1.1

### `--tlsv1.2`

- 作用：使用 TLS 1.2
- 语法：`curl --tlsv1.2 <url>`
- 示例：
```bash
curl --tlsv1.2 https://$HOST/api
```
- 版本要求：7.34.0+
- 平台/协议限制：TLS 1.2

### `--tlsv1.3`

- 作用：使用 TLS 1.3
- 语法：`curl --tlsv1.3 <url>`
- 示例：
```bash
curl --tlsv1.3 https://$HOST/api
```
- 版本要求：7.52.0+
- 平台/协议限制：TLS 1.3

### `--tlsauthtype <type>`

- 作用：TLS 认证类型（SRP）
- 语法：`curl --tlsauthtype SRP --tlsuser <user> --tlspassword <pwd> <url>`
- 示例：
```bash
curl --tlsauthtype SRP --tlsuser user --tlspassword pass https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：TLS（OpenSSL TLS-SRP）

### `--tlsuser <user>`

- 作用：TLS SRP 用户名
- 语法：`curl --tlsuser <user> --tlsauthtype SRP <url>`
- 示例：
```bash
curl --tlsuser user --tlspassword pass --tlsauthtype SRP https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：TLS-SRP

### `--tlspassword <pwd>`

- 作用：TLS SRP 密码
- 语法：`curl --tlspassword <pwd> --tlsauthtype SRP <url>`
- 示例：
```bash
curl --tlspassword pass --tlsuser user --tlsauthtype SRP https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：TLS-SRP

### `--no-sessionid`

- 作用：禁用 SSL Session ID 复用
- 语法：`curl --no-sessionid <url>`
- 示例：
```bash
curl --no-sessionid https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：TLS

### `--sessionid`

- 作用：启用 SSL Session ID 复用（默认）
- 语法：`curl --sessionid <url>`
- 示例：
```bash
curl --sessionid https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：TLS
- 注意事项：默认已启用，通常不需要显式指定

### `--ech <config>`

- 作用：配置 ECH（Encrypted Client Hello）
- 语法：`curl --ech "<config>" <url>`
- 示例：
```bash
curl --ech "true" https://$HOST/api
curl --ech "false" https://$HOST/api
curl --ech "grease" https://$HOST/api
```
- 版本要求：8.8.0+（实验性）
- 平台/协议限制：TLS；取决于编译选项
- 注意事项：ECH 加密 SNI，防止中间人看到目标域名

### `--crlf`

- 作用：上传时将 LF 转换为 CRLF
- 语法：`curl --crlf -T <file> <url>`
- 示例：
```bash
curl --crlf -T file.txt ftp://$HOST/upload/
```
- 版本要求：7.x+
- 平台/协议限制：FTP

### `--engine <name>`

- 作用：指定加密引擎
- 语法：`curl --engine <name> <url>`
- 示例：
```bash
curl --engine rdrand https://$HOST/api
# 列出可用引擎
curl --engine list
```
- 版本要求：7.x+
- 平台/协议限制：TLS（OpenSSL）

### `--egd-file <file>`

- 作用：指定 EGD（Entropy Gathering Daemon）套接字路径
- 语法：`curl --egd-file <file> <url>`
- 示例：
```bash
curl --egd-file /var/run/egd-pool https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：TLS
- 注意事项：现代系统通常不需要 EGD

### `--random-file <file>`

- 作用：指定随机数源文件
- 语法：`curl --random-file <file> <url>`
- 示例：
```bash
curl --random-file /dev/urandom https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：TLS
- 注意事项：现代系统通常不需要

### `--compressed`

- 作用：请求压缩响应（自动解压）
- 语法：`curl --compressed <url>`
- 示例：
```bash
curl --compressed https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：HTTP
- 注意事项：发送 `Accept-Encoding: gzip, deflate, br`，自动解压响应

### `--compressed-ssh`

- 作用：启用 SSH 压缩
- 语法：`curl --compressed-ssh sftp://$HOST/file`
- 示例：
```bash
curl --compressed-ssh sftp://$HOST/file.txt
```
- 版本要求：7.x+
- 平台/协议限制：SCP/SFTP

---

### 5.10 重定向与跳转

### `-L, --location`

- 作用：跟随 HTTP 重定向（3xx 响应）
- 语法：`curl -L <url>`
- 示例：
```bash
curl -L https://$HOST/redirect-to-api
```
- 版本要求：7.x+
- 平台/协议限制：HTTP
- 注意事项：默认最多跟随 50 次。GET 重定向安全，POST 301/302 会变 GET

### `--location-trusted`

- 作用：跟随重定向并将凭据发送给重定向目标
- 语法：`curl --location-trusted -u <user:pass> <url>`
- 示例：
```bash
curl --location-trusted -u user:pass https://$HOST/redirect
```
- 版本要求：7.x+
- 平台/协议限制：HTTP
- 注意事项：**安全警告**：`-L` 默认不向重定向目标发送凭据，`--location-trusted` 会发送。仅在信任重定向目标时使用

### `--max-redirs <num>`

- 作用：设置最大重定向次数
- 语法：`curl --max-redirs <num> -L <url>`
- 示例：
```bash
curl --max-redirs 5 -L https://$HOST/redirect
curl --max-redirs -1 -L https://$HOST/redirect  # 不限次数
```
- 版本要求：7.x+
- 平台/协议限制：HTTP
- 注意事项：默认 50。`-1` 表示无限

### `--post301`

- 作用：301 重定向后保持 POST 方法
- 语法：`curl --post301 -L -d "data" <url>`
- 示例：
```bash
curl --post301 -L -d "name=value" https://$HOST/redirect
```
- 版本要求：7.x+
- 平台/协议限制：HTTP
- 注意事项：默认 301 会将 POST 变为 GET

### `--post302`

- 作用：302 重定向后保持 POST 方法
- 语法：`curl --post302 -L -d "data" <url>`
- 示例：
```bash
curl --post302 -L -d "name=value" https://$HOST/redirect
```
- 版本要求：7.x+
- 平台/协议限制：HTTP

### `--post303`

- 作用：303 重定向后保持 POST 方法
- 语法：`curl --post303 -L -d "data" <url>`
- 示例：
```bash
curl --post303 -L -d "name=value" https://$HOST/redirect
```
- 版本要求：7.x+
- 平台/协议限制：HTTP
- 注意事项：按 RFC 7231，303 应将 POST 变为 GET

### `--proto-redir <protocols>`

- 作用：重定向后允许的协议
- 语法：`curl --proto-redir <[+|-]protocols> -L <url>`
- 示例：
```bash
curl --proto-redir -all,+http,https -L https://$HOST/redirect
```
- 版本要求：7.47.0+
- 平台/协议限制：HTTP
- 注意事项：防止重定向到危险协议（如 file://）

---

### 5.11 超时、重试、限速

### `--connect-timeout <seconds>`

- 作用：设置连接超时（仅 TCP 连接阶段）
- 语法：`curl --connect-timeout <seconds> <url>`
- 示例：
```bash
curl --connect-timeout 10 https://$HOST/api  # 10 秒连接超时
curl --connect-timeout 3.5 https://$HOST/api  # 3.5 秒（小数支持）
```
- 版本要求：7.x+
- 平台/协议限制：所有协议
- 注意事项：仅限制连接阶段，不包括数据传输

### `-m, --max-time <seconds>`

- 作用：设置总超时（整个操作）
- 语法：`curl -m <seconds> <url>` 或 `curl --max-time <seconds> <url>`
- 示例：
```bash
curl -m 30 https://$HOST/api  # 30 秒总超时
curl --max-time 120 -O https://$HOST/largefile.zip  # 2 分钟总超时
```
- 版本要求：7.x+
- 平台/协议限制：所有协议
- 注意事项：超过总超时后 curl 返回退出码 28

### `--retry <num>`

- 作用：失败时自动重试
- 语法：`curl --retry <num> <url>`
- 示例：
```bash
curl --retry 3 https://$HOST/api  # 最多重试 3 次
curl --retry 5 --retry-delay 2 --retry-connrefused https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：所有协议
- 注意事项：默认仅对临时错误（超时、5xx）重试。使用 `--retry-all-errors` 对所有错误重试

### `--retry-delay <seconds>`

- 作用：设置重试间隔
- 语法：`curl --retry <num> --retry-delay <seconds> <url>`
- 示例：
```bash
curl --retry 5 --retry-delay 3 https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：所有协议

### `--retry-max-time <seconds>`

- 作用：设置重试总时长上限
- 语法：`curl --retry <num> --retry-max-time <seconds> <url>`
- 示例：
```bash
curl --retry 10 --retry-max-time 60 https://$HOST/api  # 总计不超过 60 秒
```
- 版本要求：7.x+
- 平台/协议限制：所有协议

### `--retry-all-errors`

- 作用：对所有错误都重试（包括 4xx）
- 语法：`curl --retry <num> --retry-all-errors <url>`
- 示例：
```bash
curl --retry 3 --retry-all-errors https://$HOST/api
```
- 版本要求：7.71.0+
- 平台/协议限制：所有协议

### `--retry-connrefused`

- 作用：连接拒绝也重试
- 语法：`curl --retry <num> --retry-connrefused <url>`
- 示例：
```bash
curl --retry 5 --retry-connrefused --retry-delay 2 https://$HOST/api
```
- 版本要求：7.52.0+
- 平台/协议限制：所有协议

### `--limit-rate <speed>`

- 作用：限速下载/上传
- 语法：`curl --limit-rate <speed> <url>`
- 示例：
```bash
curl --limit-rate 100K -O https://$HOST/largefile.zip  # 限速 100KB/s
curl --limit-rate 1M -O https://$HOST/largefile.zip    # 限速 1MB/s
curl --limit-rate 500k -T $FILE ftp://$HOST/upload/    # 上传限速
```
- 版本要求：7.x+
- 平台/协议限制：所有协议
- 注意事项：单位 K/M/G 基于 1024

### `-Y, --speed-limit <speed>`

- 作用：最低速度限制（低于此速度则中止）
- 语法：`curl -Y <speed> -y <seconds> <url>`
- 示例：
```bash
curl -Y 1000 -y 30 -O https://$HOST/largefile.zip  # 30秒内低于1000B/s则中止
```
- 版本要求：7.x+
- 平台/协议限制：所有协议
- 注意事项：需与 `-y` 配合使用

### `-y, --speed-time <seconds>`

- 作用：速度限制的时间窗口
- 语法：`curl -y <seconds> -Y <speed> <url>`
- 示例：
```bash
curl -y 60 -Y 5000 -O https://$HOST/largefile.zip  # 60秒内低于5000B/s则中止
```
- 版本要求：7.x+
- 平台/协议限制：所有协议

### `--expect100-timeout <seconds>`

- 作用：Expect: 100-continue 超时
- 语法：`curl --expect100-timeout <seconds> <url>`
- 示例：
```bash
curl --expect100-timeout 2 -d "@large.json" https://$HOST/api/upload
```
- 版本要求：7.47.0+
- 平台/协议限制：HTTP
- 注意事项：curl 发送大 POST 数据前先发 Expect: 100-continue，等待服务器确认

### `--happy-eyeballs-timeout-ms <ms>`

- 作用：Happy Eyeballs 算法超时（IPv4/IPv6 并行连接）
- 语法：`curl --happy-eyeballs-timeout-ms <ms> <url>`
- 示例：
```bash
curl --happy-eyeballs-timeout-ms 200 https://$HOST/api
```
- 版本要求：7.59.0+
- 平台/协议限制：所有协议
- 注意事项：默认 200ms，控制 IPv6 连接失败后多久尝试 IPv4

### `--max-filesize <bytes>`

- 作用：最大下载文件大小限制
- 语法：`curl --max-filesize <bytes> <url>`
- 示例：
```bash
curl --max-filesize 10485760 -O https://$HOST/file.zip  # 最大 10MB
```
- 版本要求：7.x+
- 平台/协议限制：HTTP/FTP
- 注意事项：超过限制返回退出码 63

### `--rate <max request rate>`

- 作用：请求速率限制
- 语法：`curl --rate "<count>/<time>" <url>`
- 示例：
```bash
# 每秒最多 10 个请求
curl --rate 10/s https://$HOST/api/[1-100]
# 每分钟最多 5 个请求
curl --rate 5/m https://$HOST/api/[1-100]
```
- 版本要求：7.84.0+
- 平台/协议限制：所有协议
- 注意事项：全局选项，对多 URL 并行传输有效

---

### 5.12 连接控制

### `--keepalive`

- 作用：启用 TCP keepalive（默认已启用）
- 语法：`curl --keepalive <url>`
- 示例：
```bash
curl --keepalive https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：所有 TCP 协议

### `--no-keepalive`

- 作用：禁用 TCP keepalive
- 语法：`curl --no-keepalive <url>`
- 示例：
```bash
curl --no-keepalive https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：所有 TCP 协议

### `--keepalive-time <seconds>`

- 作用：设置 TCP keepalive 间隔
- 语法：`curl --keepalive-time <seconds> <url>`
- 示例：
```bash
curl --keepalive-time 30 https://$HOST/api  # 30 秒间隔
```
- 版本要求：7.x+
- 平台/协议限制：所有 TCP 协议
- 注意事项：默认 60 秒

### `--connect-to <host1:port1:host2:port2>`

- 作用：将指定主机端口的连接重定向到另一主机端口
- 语法：`curl --connect-to <host1:port1:host2:port2> <url>`
- 示例：
```bash
# 连接 example.com:443 实际连到 127.0.0.1:8443
curl --connect-to example.com:443:127.0.0.1:8443 https://example.com/api

# 多个重定向
curl --connect-to ::127.0.0.1: https://$HOST/api  # 所有端口重定向
```
- 版本要求：7.36.0+
- 平台/协议限制：所有协议
- 注意事项：与 `--resolve` 不同，`--connect-to` 不修改 Host 头

### `--interface <name>`

- 作用：绑定到指定网络接口
- 语法：`curl --interface <name> <url>`
- 示例：
```bash
curl --interface eth0 https://$HOST/api
curl --interface 192.168.1.100 https://$HOST/api
curl --interface tun0 https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：所有协议
- 注意事项：可指定接口名或 IP 地址

### `--local-port <port[-end]>`

- 作用：绑定本地端口范围
- 语法：`curl --local-port <port[-end]> <url>`
- 示例：
```bash
curl --local-port 5000-5100 https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：所有协议
- 注意事项：用于防火墙需要指定源端口的场景

### `--tcp-nodelay`

- 作用：设置 TCP_NODELAY（禁用 Nagle 算法）
- 语法：`curl --tcp-nodelay <url>`
- 示例：
```bash
curl --tcp-nodelay https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：TCP

### `--tcp-fastopen`

- 作用：启用 TCP Fast Open
- 语法：`curl --tcp-fastopen <url>`
- 示例：
```bash
curl --tcp-fastopen https://$HOST/api
```
- 版本要求：7.49.0+
- 平台/协议限制：TCP；需要操作系统支持

### `--ip-tos <value>`

- 作用：设置 IP TOS（Type of Service）字段
- 语法：`curl --ip-tos <value> <url>`
- 示例：
```bash
curl --ip-tos 0x10 https://$HOST/api
```
- 版本要求：7.46.0+
- 平台/协议限制：IP

### `--vlan-priority <value>`

- 作用：设置 VLAN 优先级
- 语法：`curl --vlan-priority <value> <url>`
- 示例：
```bash
curl --vlan-priority 5 https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：Linux

### `--abstract-unix-socket <path>`

- 作用：通过抽象 Unix Socket 连接
- 语法：`curl --abstract-unix-socket <path> <url>`
- 示例：
```bash
curl --abstract-unix-socket socketpath https://localhost/api
```
- 版本要求：7.53.0+
- 平台/协议限制：Linux
- 注意事项：抽象 socket 路径不以 `@` 开头

### `--unix-socket <path>`

- 作用：通过 Unix Socket 连接
- 语法：`curl --unix-socket <path> <url>`
- 示例：
```bash
# 连接 Docker daemon
curl --unix-socket /var/run/docker.sock http://localhost/containers/json

# 连接 Nginx
curl --unix-socket /run/nginx.sock http://localhost/status
```
- 版本要求：7.40.0+
- 平台/协议限制：Unix/Linux
- 注意事项：URL 中 host 通常使用 `localhost`

### `--haproxy-protocol`

- 作用：发送 HAProxy PROXY 协议头
- 语法：`curl --haproxy-protocol <url>`
- 示例：
```bash
curl --haproxy-protocol http://$HOST/api
```
- 版本要求：7.60.0+
- 平台/协议限制：HTTP
- 注意事项：用于代理服务器需要客户端 IP 的场景

### `--haproxy-clientip <ip>`

- 作用：在 HAProxy PROXY 协议头中指定客户端 IP
- 语法：`curl --haproxy-clientip <ip> --haproxy-protocol <url>`
- 示例：
```bash
curl --haproxy-clientip 192.168.1.100 --haproxy-protocol http://$HOST/api
```
- 版本要求：8.2.0+
- 平台/协议限制：HTTP

---

### 5.13 DNS 与解析

### `--resolve <[+]host:port:addr[,addr]...>`

- 作用：自定义 DNS 解析（不查询 DNS 服务器）
- 语法：`curl --resolve <host:port:addr> <url>`
- 示例：
```bash
# 将 example.com:443 解析到 127.0.0.1
curl --resolve example.com:443:127.0.0.1 https://example.com/api

# 多个解析
curl --resolve example.com:443:127.0.0.1 --resolve api.example.com:443:10.0.0.1 https://example.com/api

# IPv6
curl --resolve example.com:443:[::1] https://example.com/api

# 使用 + 前缀添加（不覆盖已有解析）
curl --resolve +example.com:443:10.0.0.1 https://example.com/api
```
- 版本要求：7.21.3+
- 平台/协议限制：所有协议
- 注意事项：与 `--connect-to` 不同，`--resolve` 修改 DNS 解析但保留 Host 头

### `--dns-servers <addresses>`

- 作用：指定自定义 DNS 服务器
- 语法：`curl --dns-servers <addr1,addr2,...> <url>`
- 示例：
```bash
curl --dns-servers 8.8.8.8,8.8.4.4 https://$HOST/api
curl --dns-servers 1.1.1.1 https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：需要 c-ares 编译支持（`curl --version` 查看 `AsynchDNS`）
- 注意事项：不影响系统 DNS，仅 curl 内部使用

### `--dns-interface <interface>`

- 作用：DNS 查询使用的网络接口
- 语法：`curl --dns-interface <interface> <url>`
- 示例：
```bash
curl --dns-interface eth0 https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：需要 c-ares 编译支持

### `--dns-ipv4-addr <addr>`

- 作用：DNS 查询绑定的 IPv4 地址
- 语法：`curl --dns-ipv4-addr <addr> <url>`
- 示例：
```bash
curl --dns-ipv4-addr 192.168.1.100 https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：需要 c-ares 编译支持

### `--dns-ipv6-addr <addr>`

- 作用：DNS 查询绑定的 IPv6 地址
- 语法：`curl --dns-ipv6-addr <addr> <url>`
- 示例：
```bash
curl --dns-ipv6-addr fe80::1 https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：需要 c-ares 编译支持

### `--alt-svc <filename>`

- 作用：启用 Alt-Svc（替代服务）缓存
- 语法：`curl --alt-svc <filename> <url>`
- 示例：
```bash
curl --alt-svc altsvc.cache https://$HOST/api
# 仅内存缓存
curl --alt-svc "" https://$HOST/api
```
- 版本要求：7.47.0+（8.x 对 HTTP/3 更重要）
- 平台/协议限制：HTTPS
- 注意事项：Alt-Svc 允许服务器告知客户端可使用替代协议（如 HTTP/3）

### `--doas-auth`

- 作用：使用 doas 认证（SSH）
- 语法：`curl --doas-auth sftp://$HOST/file`
- 示例：
```bash
curl --doas-auth sftp://$HOST/file
```
- 版本要求：8.x
- 平台/协议限制：SCP/SFTP

---

### 5.14 HTTP/2、HTTP/3、WebSocket

### `--http2`

- 作用：使用 HTTP/2
- 语法：`curl --http2 <url>`
- 示例：
```bash
curl --http2 https://$HOST/api
```
- 版本要求：7.33.0+（需要 nghttp2）
- 平台/协议限制：HTTPS
- 注意事项：8.x 对 HTTPS 默认尝试 HTTP/2

### `--http2-prior-knowledge`

- 作用：直接使用 HTTP/2，不协商
- 语法：`curl --http2-prior-knowledge <url>`
- 示例：
```bash
curl --http2-prior-knowledge http://$HOST/api
```
- 版本要求：7.49.0+
- 平台/协议限制：HTTP（明文 HTTP/2）

### `--http3`

- 作用：使用 HTTP/3（QUIC）
- 语法：`curl --http3 <url>`
- 示例：
```bash
curl --http3 https://$HOST/api
```
- 版本要求：7.66.0+（8.x 稳定）
- 平台/协议限制：HTTPS；取决于编译选项
- 注意事项：查看 `curl --version` 输出中是否有 `HTTP3`

### `--http3-only`

- 作用：仅使用 HTTP/3，不回退
- 语法：`curl --http3-only <url>`
- 示例：
```bash
curl --http3-only https://$HOST/api
```
- 版本要求：7.66.0+
- 平台/协议限制：HTTPS；取决于编译选项

### `--ws-options <options>`

- 作用：WebSocket 选项
- 语法：`curl --ws-options <options> ws://<url>`
- 示例：
```bash
curl --ws-options "mask" ws://$HOST/ws
```
- 版本要求：8.x
- 平台/协议限制：WS/WSS

### `--hsts <file>`

- 作用：HSTS（HTTP Strict Transport Security）缓存文件
- 语法：`curl --hsts <file> <url>`
- 示例：
```bash
curl --hsts ~/.curl-hsts https://$HOST/api
```
- 版本要求：7.74.0+
- 平台/协议限制：HTTPS

---

### 5.15 调试、日志、trace

### `-v, --verbose`

- 作用：详细输出（显示请求和响应的详细信息）
- 语法：`curl -v <url>`
- 示例：
```bash
curl -v https://$HOST/api 2>&1 | head -30
# 只看详细输出，不输出响应体
curl -v -o /dev/null https://$HOST/api 2>&1
```
- 版本要求：7.x+；全局选项
- 平台/协议限制：所有协议
- 注意事项：详细输出到 stderr，响应体到 stdout

### `--trace <file>`

- 作用：输出完整 trace（包含二进制数据）
- 语法：`curl --trace <file> <url>`
- 示例：
```bash
curl --trace trace.log https://$HOST/api
# 输出到 stderr
curl --trace - -o /dev/null https://$HOST/api
```
- 版本要求：7.x+；全局选项
- 平台/协议限制：所有协议
- 注意事项：比 `-v` 更详细，包含所有传输数据

### `--trace-ascii <file>`

- 作用：输出 ASCII trace（非打印字符用 `.` 表示）
- 语法：`curl --trace-ascii <file> <url>`
- 示例：
```bash
curl --trace-ascii trace.txt https://$HOST/api
```
- 版本要求：7.x+；全局选项
- 平台/协议限制：所有协议

### `--trace-config <string>`

- 作用：细粒度 trace 配置
- 语法：`curl --trace-config <string> <url>`
- 示例：
```bash
curl --trace-config "http/2,ssl" https://$HOST/api
curl --trace-config "all" https://$HOST/api
```
- 版本要求：8.3.0+；全局选项
- 平台/协议限制：所有协议

### `--trace-ids`

- 作用：trace 中包含传输 ID
- 语法：`curl --trace-ids --trace-ascii - <url>`
- 示例：
```bash
curl --trace-ids --trace-ascii - -o /dev/null https://$HOST/api
```
- 版本要求：8.2.0+；全局选项
- 平台/协议限制：所有协议

### `--trace-time`

- 作用：trace 中包含时间戳
- 语法：`curl --trace-time -v <url>`
- 示例：
```bash
curl --trace-time -v https://$HOST/api 2>&1
```
- 版本要求：7.x+；全局选项
- 平台/协议限制：所有协议

### `--libcurl <file>`

- 作用：输出等效的 libcurl C 代码
- 语法：`curl --libcurl <file> <url>`
- 示例：
```bash
curl --libcurl code.c -d "name=value" https://$HOST/api
cat code.c
```
- 版本要求：7.x+；全局选项
- 平台/协议限制：所有协议
- 注意事项：用于将命令行 curl 转为 C 代码

### `--fail-early`

- 作用：第一个错误即退出（不继续后续 URL）
- 语法：`curl --fail-early <url1> <url2>`
- 示例：
```bash
curl --fail-early https://$HOST/api/1 https://$HOST/api/2
```
- 版本要求：7.x+；全局选项
- 平台/协议限制：所有协议

### `--test-event`

- 作用：内部事件测试
- 语法：`curl --test-event <url>`
- 示例：
```bash
curl --test-event https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：内部使用

---

### 5.16 输出格式与 `-w` / `--write-out`

### `-w, --write-out <format>`

- 作用：在传输完成后输出自定义格式信息
- 语法：`curl -w "<format>" <url>`
- 示例：
```bash
# 输出 HTTP 状态码
curl -s -o /dev/null -w "%{http_code}" https://$HOST/api

# 输出 JSON 格式信息
curl -s -o /dev/null -w '{"status":%{http_code},"time":%{time_total}}\n' https://$HOST/api

# 输出详细计时
curl -s -o /dev/null -w "DNS:%{time_namelookup} Connect:%{time_connect} TLS:%{time_appconnect} TTFB:%{time_starttransfer} Total:%{time_total}\n" https://$HOST/api

# 使用 @file 读取格式
echo '%{http_code} %{time_total}' > format.txt
curl -s -o /dev/null -w "@format.txt" https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：所有协议
- 注意事项：`%{variable}` 语法输出变量。`@file` 从文件读取格式

**`-w` 可用变量总览**：

| 变量 | 说明 |
|---|---|
| `%{url}` | 最终 URL（含重定向后的地址） |
| `%{url_effective}` | 同 `%{url}` |
| `%{http_code}` | HTTP 状态码（如 200、404） |
| `%{http_version}` | HTTP 版本（如 1.1、2、3） |
| `%{response_code}` | 同 `%{http_code}` |
| `%{scheme}` | URL scheme（http/https） |
| `%{content_type}` | 响应 Content-Type |
| `%{size_download}` | 下载数据大小（字节） |
| `%{size_upload}` | 上传数据大小（字节） |
| `%{size_header}` | 响应头大小（字节） |
| `%{size_request}` | 请求大小（字节） |
| `%{num_headers}` | 响应头数量 |
| `%{time_namelookup}` | DNS 解析耗时（秒） |
| `%{time_connect}` | TCP 连接耗时（秒） |
| `%{time_appconnect}` | TLS 握手耗时（秒） |
| `%{time_pretransfer}` | 传输前准备耗时（秒） |
| `%{time_starttransfer}` | 首字节到达时间 TTFB（秒） |
| `%{time_total}` | 总耗时（秒） |
| `%{speed_download}` | 平均下载速度（字节/秒） |
| `%{speed_upload}` | 平均上传速度（字节/秒） |
| `%{header_json}` | 所有响应头 JSON 格式（8.3+） |
| `%{remote_ip}` | 远程服务器 IP |
| `%{remote_port}` | 远程服务器端口 |
| `%{local_ip}` | 本地 IP |
| `%{local_port}` | 本地端口 |
| `%{ssl_verify_result}` | SSL 验证结果（0=成功） |
| `%{filename_effective}` | 最终保存的文件名 |
| `%{ftp_entry_path}` | FTP 初始路径 |
| `%{redirect_url}` | 重定向目标 URL（未跟随时） |
| `%{num_redirects}` | 重定向次数 |
| `%{exitcode}` | 退出码 |
| `%{errormsg}` | 错误消息 |

---

### 5.17 配置文件与变量

### `-K, --config <file>`

- 作用：从文件读取 curl 配置（选项和 URL）
- 语法：`curl -K <file> <url>` 或 `curl --config <file>`
- 示例：
```bash
# 创建配置文件
cat > curl-config.txt << 'EOF'
# 注释行
--user-agent "MyApp/1.0"
--compressed
--connect-timeout 10
--max-time 30
--retry 3
url = "https://$HOST/api"
EOF

curl -K curl-config.txt

# 从 stdin 读取配置
echo "url = https://$HOST/api" | curl -K -
```
- 版本要求：7.x+
- 平台/协议限制：所有协议
- 注意事项：配置文件中每行一个选项，`#` 开头为注释。默认读取 `~/.curlrc`

### `--variable <[%]name=text@file>`

- 作用：定义命令行变量（8.3.0+）
- 语法：`curl --variable <name=value>` 或 `curl --variable <name@file>` 或 `curl --variable %<envvar>`
- 示例：
```bash
# 直接赋值
curl --variable user=alice --expand-url "https://$HOST/api/{{user}}"

# 从文件读取
curl --variable payload@$FILE --expand-data "{{payload}}" https://$HOST/api

# 从环境变量导入
curl --variable '%API_KEY' --expand-header "X-API-Key: {{API_KEY}}" https://$HOST/api

# 环境变量带默认值
curl --variable '%API_KEY=fallback' --expand-url "https://$HOST/api?key={{API_KEY}}"

# 变量函数：trim / json / url / b64 / 64dec
curl --variable raw@$HOME/.token --expand-header "Authorization: Bearer {{raw:trim}}" https://$HOST/api
```
- 版本要求：8.3.0+
- 平台/协议限制：所有协议
- 注意事项：`--expand-*` 前缀的选项支持 `{{name}}` 变量展开。函数链用冒号分隔

### `--expand-url <url>`

- 作用：支持变量展开的 URL
- 语法：`curl --variable <name=value> --expand-url "https://...{{name}}..."`
- 示例：
```bash
curl --variable host=api.example.com --expand-url "https://{{host}}/v1/users"
```
- 版本要求：8.3.0+
- 平台/协议限制：所有协议

### `--expand-header <header>`

- 作用：支持变量展开的请求头
- 语法：`curl --variable <name=value> --expand-header "X-Custom: {{name}}"`
- 示例：
```bash
curl --variable '%TOKEN' --expand-header "Authorization: Bearer {{TOKEN}}" https://$HOST/api
```
- 版本要求：8.3.0+
- 平台/协议限制：HTTP

### `--expand-data <data>`

- 作用：支持变量展开的 POST 数据
- 语法：`curl --variable <name=value> --expand-data "{{name}}"`
- 示例：
```bash
curl --variable payload=@$FILE --expand-data "{{payload:json}}" https://$HOST/api
```
- 版本要求：8.3.0+
- 平台/协议限制：HTTP

### `--expand-form <name=content>`

- 作用：支持变量展开的表单字段
- 语法：`curl --variable <name=value> --expand-form "field={{name}}"`
- 示例：
```bash
curl --variable user=alice --expand-form "username={{user}}" https://$HOST/api/upload
```
- 版本要求：8.3.0+
- 平台/协议限制：HTTP

### `--expand-variable <name=content>`

- 作用：在变量展开中使用变量
- 语法：`curl --expand-variable <name@{{other_var}}/file>`
- 示例：
```bash
curl --variable %HOME --expand-variable config@"{{HOME}}/.config" --expand-data "{{config}}" https://$HOST/api
```
- 版本要求：8.3.0+
- 平台/协议限制：所有协议

### `-q`

- 作用：禁用 curlrc 配置文件（必须为第一个参数）
- 语法：`curl -q <url>`
- 示例：
```bash
curl -q https://$HOST/api  # 不读取 ~/.curlrc
```
- 版本要求：7.x+
- 平台/协议限制：所有协议
- 注意事项：必须在命令行第一个参数位置

---

### 5.18 进度条与静默

### `-s, --silent`

- 作用：静默模式（不显示进度和错误信息）
- 语法：`curl -s <url>`
- 示例：
```bash
curl -s https://$HOST/api  # 只输出响应体
curl -s -o /dev/null -w "%{http_code}" https://$HOST/api  # 只输出状态码
```
- 版本要求：7.x+
- 平台/协议限制：所有协议
- 注意事项：`-s` 会同时隐藏错误信息，建议与 `-S` 配合使用

### `-S, --show-error`

- 作用：在静默模式下仍显示错误信息
- 语法：`curl -sS <url>`
- 示例：
```bash
curl -sS https://$HOST/api  # 静默但显示错误
```
- 版本要求：7.x+；全局选项
- 平台/协议限制：所有协议
- 注意事项：需与 `-s` 配合使用

### `--progress-bar`

- 作用：使用进度条显示（替代默认进度表）
- 语法：`curl --progress-bar -O <url>`
- 示例：
```bash
curl --progress-bar -O https://$HOST/largefile.zip
```
- 版本要求：7.x+；全局选项
- 平台/协议限制：所有协议

### `--no-progress-meter`

- 作用：禁用进度表（但不静默，错误信息仍输出）
- 语法：`curl --no-progress-meter <url>`
- 示例：
```bash
curl --no-progress-meter https://$HOST/api
```
- 版本要求：7.67.0+
- 平台/协议限制：所有协议
- 注意事项：与 `-s` 不同，`--no-progress-meter` 不影响错误输出

### `--styled-output`

- 作用：终端输出带颜色
- 语法：`curl --styled-output <url>`
- 示例：
```bash
curl --styled-output -v https://$HOST/api
```
- 版本要求：7.61.0+；全局选项
- 平台/协议限制：终端
- 注意事项：需要终端支持 ANSI 颜色

### `--stderr <file>`

- 作用：重定向 stderr 到文件
- 语法：`curl --stderr <file> <url>`
- 示例：
```bash
curl --stderr errors.log -v https://$HOST/api
# 重定向到 stdout
curl --stderr - https://$HOST/api
```
- 版本要求：7.x+；全局选项
- 平台/协议限制：所有协议

---

### 5.19 邮件、FTP、SFTP、LDAP、MQTT 等协议专用参数

### `-a, --append`

- 作用：FTP/SFTP 上传时追加到文件末尾
- 语法：`curl --append -T <file> ftp://<url>`
- 示例：
```bash
curl --append -T logfile.txt ftp://$HOST/upload/logfile.txt
```
- 版本要求：7.x+
- 平台/协议限制：FTP/SFTP

### `-l, --list-only`

- 作用：FTP 只列出目录名（不显示详情）
- 语法：`curl -l ftp://<url>`
- 示例：
```bash
curl -l ftp://$HOST/upload/
```
- 版本要求：7.x+
- 平台/协议限制：FTP

### `-P, --ftp-port <address>`

- 作用：FTP 主动模式指定数据连接端口
- 语法：`curl -P <address> ftp://<url>`
- 示例：
```bash
curl -P - ftp://$HOST/file.txt        # 使用默认地址
curl -P 192.168.1.100 ftp://$HOST/    # 指定 IP
curl -P 192.168.1.100,2048-3210 ftp://$HOST/  # 指定 IP 和端口范围
```
- 版本要求：7.x+
- 平台/协议限制：FTP

### `--ftp-pasv`

- 作用：FTP 被动模式（默认）
- 语法：`curl --ftp-pasv ftp://<url>`
- 示例：
```bash
curl --ftp-pasv ftp://$HOST/file.txt
```
- 版本要求：7.x+
- 平台/协议限制：FTP

### `--ftp-method <method>`

- 作用：FTP 传输方法
- 语法：`curl --ftp-method <method> ftp://<url>`
- 示例：
```bash
curl --ftp-method multicwd ftp://$HOST/path/to/file.txt
curl --ftp-method nocwd ftp://$HOST/path/to/file.txt
curl --ftp-method singlecwd ftp://$HOST/path/to/file.txt
```
- 版本要求：7.x+
- 平台/协议限制：FTP
- 注意事项：`multicwd`（默认）逐级 CWD，`nocwd` 直接 URL 路径，`singlecwd` 单次 CWD

### `--ftp-account <data>`

- 作用：FTP ACCOUNT 命令
- 语法：`curl --ftp-account "<account>" ftp://<url>`
- 示例：
```bash
curl --ftp-account "myaccount" ftp://$HOST/file.txt
```
- 版本要求：7.x+
- 平台/协议限制：FTP

### `--ftp-alternative-to-user <cmd>`

- 作用：FTP 替代 USER 命令
- 语法：`curl --ftp-alternative-to-user "<cmd>" ftp://<url>`
- 示例：
```bash
curl --ftp-alternative-to-user "SITE AUTH" ftp://$HOST/file.txt
```
- 版本要求：7.x+
- 平台/协议限制：FTP

### `--ftp-create-dirs`

- 作用：FTP 远程创建目录
- 语法：`curl --ftp-create-dirs -T <file> ftp://<url>`
- 示例：
```bash
curl --ftp-create-dirs -T file.txt ftp://$HOST/new/dir/file.txt
```
- 版本要求：7.x+
- 平台/协议限制：FTP

### `--ftp-pret`

- 作用：PASV 前发送 PRET 命令
- 语法：`curl --ftp-pret ftp://<url>`
- 示例：
```bash
curl --ftp-pret ftp://$HOST/file.txt
```
- 版本要求：7.x+
- 平台/协议限制：FTP

### `--ftp-skip-pasv-ip`

- 作用：忽略 PASV 返回的 IP，使用控制连接的 IP
- 语法：`curl --ftp-skip-pasv-ip ftp://<url>`
- 示例：
```bash
curl --ftp-skip-pasv-ip ftp://$HOST/file.txt
```
- 版本要求：7.x+
- 平台/协议限制：FTP

### `--ftp-ssl-ccc`

- 作用：FTP 发送 CCC 命令关闭 TLS 通道
- 语法：`curl --ftp-ssl-ccc ftps://<url>`
- 示例：
```bash
curl --ftp-ssl-ccc ftps://$HOST/file.txt
```
- 版本要求：7.x+
- 平台/协议限制：FTPS

### `--ftp-ssl-ccc-mode <mode>`

- 作用：CCC 模式（active/passive）
- 语法：`curl --ftp-ssl-ccc-mode <mode> --ftp-ssl-ccc ftps://<url>`
- 示例：
```bash
curl --ftp-ssl-ccc-mode passive --ftp-ssl-ccc ftps://$HOST/file.txt
```
- 版本要求：7.x+
- 平台/协议限制：FTPS

### `--ftp-ssl-control`

- 作用：FTP 只加密控制通道
- 语法：`curl --ftp-ssl-control ftp://<url>`
- 示例：
```bash
curl --ftp-ssl-control ftp://$HOST/file.txt
```
- 版本要求：7.x+
- 平台/协议限制：FTP

### `--disable-eprt`

- 作用：禁用 EPRT/PORT 命令（FTP）
- 语法：`curl --disable-eprt ftp://<url>`
- 示例：
```bash
curl --disable-eprt ftp://$HOST/file.txt
```
- 版本要求：7.x+
- 平台/协议限制：FTP

### `--disable-epsv`

- 作用：禁用 EPSV 命令（FTP）
- 语法：`curl --disable-epsv ftp://<url>`
- 示例：
```bash
curl --disable-epsv ftp://$HOST/file.txt
```
- 版本要求：7.x+
- 平台/协议限制：FTP

### `--krb <level>`

- 作用：Kerberos 安全级别
- 语法：`curl --krb <level> ftp://<url>`
- 示例：
```bash
curl --krb clear ftp://$HOST/file.txt
curl --krb private ftp://$HOST/file.txt
```
- 版本要求：7.x+
- 平台/协议限制：FTP；需要 Kerberos 编译支持
- 注意事项：级别：clear / safe / confidential / private

### `-Q, --quote <command>`

- 作用：传输前执行 FTP/SFTP 命令
- 语法：`curl -Q "<command>" ftp://<url>`
- 示例：
```bash
# FTP 命令
curl -Q "DELE oldfile.txt" -T newfile.txt ftp://$HOST/upload/
curl -Q "CWD /pub" -O ftp://$HOST/file.txt

# SFTP 命令
curl -Q "rm /tmp/oldfile" sftp://$HOST/file.txt

# 传输后命令（-Q -）
curl -Q "-DELE temp.txt" -T data.txt ftp://$HOST/
```
- 版本要求：7.x+
- 平台/协议限制：FTP/SFTP
- 注意事项：`-Q -` 前缀表示传输后执行

### `--mail-from <addr>`

- 作用：SMTP 发件人地址
- 语法：`curl --mail-from <addr> smtp://<url>`
- 示例：
```bash
curl --mail-from sender@example.com --mail-rcpt recipient@example.com \
  smtp://$HOST --upload-file email.txt
```
- 版本要求：7.x+
- 平台/协议限制：SMTP

### `--mail-rcpt <addr>`

- 作用：SMTP 收件人地址
- 语法：`curl --mail-rcpt <addr> smtp://<url>`
- 示例：
```bash
curl --mail-from sender@example.com \
  --mail-rcpt recipient1@example.com \
  --mail-rcpt recipient2@example.com \
  smtp://$HOST -T email.txt
```
- 版本要求：7.x+
- 平台/协议限制：SMTP

### `--mail-rcpt-allowfails`

- 作用：部分收件人失败不中止发送
- 语法：`curl --mail-rcpt-allowfails --mail-rcpt <addr> smtp://<url>`
- 示例：
```bash
curl --mail-rcpt-allowfails \
  --mail-from sender@example.com \
  --mail-rcpt good@example.com \
  --mail-rcpt bad@example.com \
  smtp://$HOST -T email.txt
```
- 版本要求：7.x+
- 平台/协议限制：SMTP

### `--mail-auth <addr>`

- 作用：SMTP AUTH 地址
- 语法：`curl --mail-auth <addr> smtp://<url>`
- 示例：
```bash
curl --mail-auth auth@example.com --mail-from sender@example.com \
  --mail-rcpt recipient@example.com smtp://$HOST -T email.txt
```
- 版本要求：7.x+
- 平台/协议限制：SMTP

### `--login-options <options>`

- 作用：登录选项（IMAP/POP3/SMTP）
- 语法：`curl --login-options "<options>" <url>`
- 示例：
```bash
curl --login-options "AUTH=PLAIN" imap://$HOST/INBOX
```
- 版本要求：7.x+
- 平台/协议限制：IMAP/POP3/SMTP

### `--ssl`

- 作用：启用 SSL/TLS（FTP/IMAP/POP3/SMTP）
- 语法：`curl --ssl <url>`
- 示例：
```bash
curl --ssl ftp://$HOST/file.txt
curl --ssl imap://$HOST/INBOX
```
- 版本要求：7.x+
- 平台/协议限制：FTP/IMAP/POP3/SMTP
- 注意事项：TLS 可选，服务器不支持 TLS 时不报错

### `--ssl-reqd`

- 作用：要求 SSL/TLS
- 语法：`curl --ssl-reqd <url>`
- 示例：
```bash
curl --ssl-reqd ftp://$HOST/file.txt
```
- 版本要求：7.x+
- 平台/协议限制：FTP/IMAP/POP3/SMTP
- 注意事项：服务器不支持 TLS 时直接失败

### `-t, --telnet-option <opt=val>`

- 作用：Telnet 选项
- 语法：`curl -t <opt=val> telnet://<url>`
- 示例：
```bash
curl -t TTYPE=vt100 telnet://$HOST
```
- 版本要求：7.x+
- 平台/协议限制：TELNET

### `--tftp-blksize <value>`

- 作用：TFTP 块大小
- 语法：`curl --tftp-blksize <value> tftp://<url>`
- 示例：
```bash
curl --tftp-blksize 1428 -O tftp://$HOST/file.txt
```
- 版本要求：7.x+
- 平台/协议限制：TFTP

### `--tftp-no-options`

- 作用：TFTP 不发送选项
- 语法：`curl --tftp-no-options tftp://<url>`
- 示例：
```bash
curl --tftp-no-options -O tftp://$HOST/file.txt
```
- 版本要求：7.x+
- 平台/协议限制：TFTP

### `--pubkey <key>`

- 作用：SSH 公钥文件
- 语法：`curl --pubkey <file> sftp://<url>`
- 示例：
```bash
curl --pubkey ~/.ssh/id_rsa.pub sftp://$HOST/file.txt
```
- 版本要求：7.x+
- 平台/协议限制：SCP/SFTP

### `--hostpubmd5 <md5>`

- 作用：SSH 主机公钥 MD5 指纹
- 语法：`curl --hostpubmd5 "<md5>" sftp://<url>`
- 示例：
```bash
curl --hostpubmd5 "a1b2c3d4e5f6..." sftp://$HOST/file.txt
```
- 版本要求：7.x+
- 平台/协议限制：SCP/SFTP

### `--hostpubsha256 <sha256>`

- 作用：SSH 主机公钥 SHA256 指纹
- 语法：`curl --hostpubsha256 "<sha256>" sftp://<url>`
- 示例：
```bash
curl --hostpubsha256 "sha256://base64==" sftp://$HOST/file.txt
```
- 版本要求：7.x+
- 平台/协议限制：SCP/SFTP

### `--delegation <level>`

- 作用：GSS-API 委托级别
- 语法：`curl --delegation <level> <url>`
- 示例：
```bash
curl --delegation none --negotiate https://$HOST/api
curl --delegation always --negotiate https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：GSS-API
- 注意事项：级别：none / policy / always

---

### 5.20 实验性/高级参数

### `--etag-compare <file>`

- 作用：从文件加载 ETag，发送条件请求（If-None-Match）
- 语法：`curl --etag-compare <file> <url>`
- 示例：
```bash
# 首次下载保存 ETag
curl --etag-save etag.txt -O https://$HOST/file.txt

# 后续检查是否有更新
curl --etag-compare etag.txt -O https://$HOST/file.txt
# 如果 ETag 匹配，返回 304，不下载
```
- 版本要求：7.x+
- 平台/协议限制：HTTP

### `--etag-save <file>`

- 作用：保存响应 ETag 到文件
- 语法：`curl --etag-save <file> <url>`
- 示例：
```bash
curl --etag-save etag.txt -O https://$HOST/file.txt
```
- 版本要求：7.x+
- 平台/协议限制：HTTP

### `-z, --time-cond <time>`

- 作用：基于时间的条件请求（If-Modified-Since / If-Unmodified-Since）
- 语法：`curl -z "<time>" <url>`
- 示例：
```bash
# 如果文件在指定时间后修改过才下载
curl -z "1 Dec 2025 12:00:00" -O https://$HOST/file.txt

# 使用本地文件的时间戳
curl -z file.txt -O https://$HOST/file.txt

# 反向（如果文件在指定时间前修改过）
curl -z "-1 Dec 2025 12:00:00" -O https://$HOST/file.txt
```
- 版本要求：7.x+
- 平台/协议限制：HTTP/FTP
- 注意事项：支持多种日期格式。`-` 前缀反转条件

### `--create-file-mode <mode>`

- 作用：创建文件的权限模式
- 语法：`curl --create-file-mode <mode> <url>`
- 示例：
```bash
curl --create-file-mode 0644 -O https://$HOST/file.txt
```
- 版本要求：8.x
- 平台/协议限制：所有协议

### `--path-as-is`

- 作用：URL 路径原样发送（不合并 `..` 和 `.`）
- 语法：`curl --path-as-is <url>`
- 示例：
```bash
curl --path-as-is https://$HOST/api/../v1/users
# 原样发送 /api/../v1/users，而非 /v1/users
```
- 版本要求：7.42.0+
- 平台/协议限制：HTTP
- 注意事项：**安全提醒**：路径穿越测试时需要此选项

### `--disallow-username-in-url`

- 作用：禁止 URL 中包含用户名
- 语法：`curl --disallow-username-in-url <url>`
- 示例：
```bash
curl --disallow-username-in-url https://user@example.com/api
# 返回错误，因为 URL 中含用户名
```
- 版本要求：8.7.0+
- 平台/协议限制：所有协议
- 注意事项：安全加固选项，防止 URL 中泄露凭据

### `--next`

- 作用：分隔多组选项（每组独立配置）
- 语法：`curl [options1] <url1> --next [options2] <url2>`
- 示例：
```bash
curl -d "data1" https://$HOST/api/1 --next -H "X-Custom: val" https://$HOST/api/2
```
- 版本要求：7.x+
- 平台/协议限制：所有协议
- 注意事项：全局选项不受 `--next` 影响

### `--parallel`

- 作用：并行传输多个 URL
- 语法：`curl --parallel <url1> <url2>`
- 示例：
```bash
curl --parallel https://$HOST/api/1 https://$HOST/api/2 https://$HOST/api/3
# 简写
curl -Z https://$HOST/api/1 https://$HOST/api/2
```
- 版本要求：7.x+；全局选项
- 平台/协议限制：所有协议

### `--parallel-immediate`

- 作用：并行立即开始（不等连接复用）
- 语法：`curl --parallel-immediate --parallel <url1> <url2>`
- 示例：
```bash
curl --parallel --parallel-immediate https://$HOST/api/1 https://$HOST/api/2
```
- 版本要求：8.7.0+；全局选项
- 平台/协议限制：所有协议

### `--parallel-max <num>`

- 作用：最大并行连接数
- 语法：`curl --parallel --parallel-max <num> <url1> <url2>`
- 示例：
```bash
curl --parallel --parallel-max 10 https://$HOST/api/[1-50]
```
- 版本要求：7.x+；全局选项
- 平台/协议限制：所有协议
- 注意事项：默认 50

### `--parallel-max-host <num>`

- 作用：每主机最大并行连接数
- 语法：`curl --parallel --parallel-max-host <num> <url1> <url2>`
- 示例：
```bash
curl --parallel --parallel-max-host 4 https://$HOST/api/[1-50]
```
- 版本要求：8.x；全局选项
- 平台/协议限制：所有协议

### `--parallel-progress <method>`

- 作用：并行传输进度显示方式
- 语法：`curl --parallel --parallel-progress <method> <url1> <url2>`
- 示例：
```bash
curl --parallel --parallel-progress bar https://$HOST/api/1 https://$HOST/api/2
```
- 版本要求：8.x；全局选项
- 平台/协议限制：所有协议

### `--dump-ca-embed <file>`

- 作用：导出 curl 内嵌的 CA 证书
- 语法：`curl --dump-ca-embed <file>`
- 示例：
```bash
curl --dump-ca-embed ca-bundle.pem
```
- 版本要求：8.x
- 平台/协议限制：需要编译时内嵌 CA 证书

### `--metalink`

- 作用：处理 Metalink 文件（已弃用）
- 语法：`curl --metalink <file>`
- 示例：
```bash
curl --metalink file.metalink
```
- 版本要求：7.x（已弃用）
- 平台/协议限制：所有协议
- 注意事项：从 7.88.0 起弃用

### `--pipelining`

- 作用：HTTP 流水线（已弃用）
- 语法：`curl --pipelining <url>`
- 示例：
```bash
curl --pipelining https://$HOST/api
```
- 版本要求：7.x（已弃用）
- 平台/协议限制：HTTP
- 注意事项：HTTP/1.1 流水线已被 HTTP/2 多路复用取代

---

### 5.21 其他剩余参数

### `-B, --use-ascii`

- 作用：FTP 使用 ASCII 模式
- 语法：`curl -B ftp://<url>`
- 示例：
```bash
curl -B ftp://$HOST/file.txt
```
- 版本要求：7.x+
- 平台/协议限制：FTP

### `--ipv4`

- 作用：仅解析 IPv4 地址
- 语法：`curl --ipv4 <url>`
- 示例：
```bash
curl --ipv4 https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：所有协议

### `--ipv6`

- 作用：仅解析 IPv6 地址
- 语法：`curl --ipv6 <url>`
- 示例：
```bash
curl --ipv6 https://$HOST/api
```
- 版本要求：7.x+
- 平台/协议限制：所有协议

### `-f, --fail`

- 作用：HTTP 错误时快速失败（不输出错误页面）
- 语法：`curl -f <url>`
- 示例：
```bash
curl -f https://$HOST/api  # 404 时返回退出码 22，不输出 HTML 错误页
```
- 版本要求：7.x+
- 平台/协议限制：HTTP
- 注意事项：仅对 400+ 响应有效

### `--fail-with-body`

- 作用：HTTP 错误时返回非零退出码但仍输出响应体
- 语法：`curl --fail-with-body <url>`
- 示例：
```bash
curl --fail-with-body https://$HOST/api  # 404 时仍输出错误页面，但退出码非零
```
- 版本要求：7.x+
- 平台/协议限制：HTTP
- 注意事项：与 `-f` 不同，`--fail-with-body` 会输出错误页面内容

### `-V, --version`

- 作用：显示版本信息和编译特性
- 语法：`curl --version`
- 示例：
```bash
curl --version
# 输出示例：
# curl 8.22.1 (x86_64-pc-linux-gnu) libcurl/8.22.1 OpenSSL/3.0.13 ...
# Protocols: dict file ftp ftps gopher gophers http https imap imaps ...
# Features: alt-svc AsynchDNS brotli GSS-API HSTS HTTP2 HTTP3 ...
```
- 版本要求：7.x+
- 平台/协议限制：所有协议
- 注意事项：检查是否支持 HTTP/2/3、WebSocket 等特性

### `-M, --manual`

- 作用：显示完整 man 手册
- 语法：`curl --manual`
- 示例：
```bash
curl --manual | less
```
- 版本要求：7.x+
- 平台/协议限制：所有协议

### `-h, --help [subject]`

- 作用：显示帮助信息
- 语法：`curl --help` 或 `curl --help all` 或 `curl --help <subject>`
- 示例：
```bash
curl --help          # 基本帮助
curl --help all      # 显示全部选项
curl --help http     # 只显示 HTTP 相关选项
curl --help ftp      # 只显示 FTP 相关选项
```
- 版本要求：7.x+（`--help all` 和 `--help <subject>` 为 8.x+）
- 平台/协议限制：所有协议

---

## 6. 每个参数的标准说明格式

本文档第 5 章的分类详解中，每个参数均采用以下标准格式：

```markdown
### `短选项, 长选项 <参数类型>`

- 作用：参数的核心功能描述
- 语法：完整使用语法
- 示例：bash 代码块，使用 $URL、$TOKEN 等占位符
- 版本要求：引入版本
- 平台/协议限制：适用的协议、操作系统、编译选项
- 注意事项：安全提醒、使用限制、与其他参数的关系
```

**格式说明**：
- 短选项和长选项都标注（如 `-d, --data`）
- 带值参数标注参数类型（如 `<url>`、`<file>`、`<seconds>`）
- 示例统一使用 `bash` 代码块
- 示例中使用变量占位符（`$URL`、`$TOKEN`、`$FILE`、`$HOST`）
- 危险参数标注 **安全警告**
- 全局选项标注 `[G]`

---

## 7. 使用方式与实战示例

### 7.1 GET 请求

```bash
curl https://$HOST/api/users
```
- 参数解释：无额外参数，默认 GET 请求
- 预期结果：输出响应体到 stdout
- 常见坑：响应体直接输出到终端，大数据量时会刷屏，建议加 `-o` 保存

### 7.2 POST JSON

```bash
curl --json '{"name":"test","email":"test@example.com"}' https://$HOST/api/users
```
- 参数解释：`--json` 自动设置 Content-Type 和 Accept 为 application/json
- 预期结果：服务器收到 JSON 格式请求体
- 常见坑：JSON 字符串中的引号需正确转义；从文件读取更安全 `--json "@payload.json"`

### 7.3 POST 表单

```bash
# application/x-www-form-urlencoded
curl -d "name=test&email=test@example.com" https://$HOST/api/users

# multipart/form-data
curl -F "name=test" -F "email=test@example.com" https://$HOST/api/users
```
- 参数解释：`-d` 发送 URL 编码表单，`-F` 发送 multipart 表单
- 预期结果：服务器收到对应格式的表单数据
- 常见坑：`-d` 的 `&` 在 shell 中需要引号包裹

### 7.4 PUT / PATCH / DELETE

```bash
# PUT
curl -X PUT -H "Content-Type: application/json" \
  -d '{"name":"updated"}' https://$HOST/api/users/$ID

# PATCH
curl -X PATCH -d '{"email":"new@example.com"}' https://$HOST/api/users/$ID

# DELETE
curl -X DELETE https://$HOST/api/users/$ID
```
- 参数解释：`-X` 指定 HTTP 方法
- 预期结果：服务器执行对应操作
- 常见坑：`-d` 已隐含 POST，配合 `-X PUT` 时需显式指定

### 7.5 添加请求头

```bash
curl -H "X-Custom-Header: value" \
     -H "X-Another-Header: another" \
     https://$HOST/api
```
- 参数解释：`-H` 添加自定义请求头，可多次使用
- 预期结果：服务器收到所有自定义头
- 常见坑：`-H "Header:"` 会删除该头（冒号后无空格）

### 7.6 携带 Bearer Token

```bash
curl -H "Authorization: Bearer $TOKEN" https://$HOST/api/protected
# 或使用 --oauth2-bearer
curl --oauth2-bearer "$TOKEN" https://$HOST/api/protected
```
- 参数解释：`-H` 或 `--oauth2-bearer` 设置 Bearer Token
- 预期结果：服务器验证 Token 并授权
- 常见坑：**Token 会出现在 `ps` 输出和 shell 历史中**，建议使用 `--variable` 或配置文件

### 7.7 Basic 认证

```bash
# 命令行指定（不安全）
curl -u admin:secret https://$HOST/api

# 交互式输入密码（更安全）
curl -u admin https://$HOST/api

# 使用 netrc 文件（最安全）
echo "machine $HOST login admin password secret" > ~/.netrc
chmod 600 ~/.netrc
curl -n https://$HOST/api
```
- 参数解释：`-u` 设置 Basic 认证凭据，`-n` 从 netrc 读取
- 预期结果：服务器返回认证后的数据
- 常见坑：**密码出现在进程列表中**，生产环境必须使用 netrc

### 7.8 使用 Cookie

```bash
# 登录并保存 Cookie
curl -c cookies.txt -d "user=admin&pass=secret" -L https://$HOST/login

# 使用保存的 Cookie
curl -b cookies.txt https://$HOST/dashboard

# 直接指定 Cookie
curl -b "session=abc123; user=admin" https://$HOST/dashboard
```
- 参数解释：`-c` 保存 Cookie，`-b` 发送 Cookie
- 预期结果：维持会话状态
- 常见坑：`-c` 和 `-b` 配合使用实现会话保持

### 7.9 上传文件

```bash
# multipart 上传
curl -F "file=@$FILE" https://$HOST/api/upload

# PUT 上传
curl -T $FILE https://$HOST/api/upload

# FTP 上传
curl -T $FILE ftp://$USER:$PASS@$HOST/upload/
```
- 参数解释：`-F` 表单上传，`-T` PUT/FTP 上传
- 预期结果：文件上传到服务器
- 常见坑：`@file` 是文件引用，如果文件名以 `@` 开头需用 `--form-string`

### 7.10 下载文件

```bash
# 按原文件名保存
curl -O https://$HOST/file.zip

# 指定文件名保存
curl -o output.zip https://$HOST/file.zip

# 使用 Content-Disposition 文件名
curl -OJ https://$HOST/download
```
- 参数解释：`-O` 原文件名，`-o` 指定文件名，`-J` 使用 Content-Disposition
- 预期结果：文件保存到当前目录
- 常见坑：`-J` 的文件名可能含恶意路径

### 7.11 断点续传

```bash
# 自动检测续传位置
curl -C - -o largefile.zip https://$HOST/largefile.zip

# 手动指定偏移
curl -C 1048576 -o largefile.zip https://$HOST/largefile.zip
```
- 参数解释：`-C -` 自动检测已下载大小并续传
- 预期结果：从中断处继续下载
- 常见坑：服务器必须支持 Range 请求

### 7.12 限速下载

```bash
curl --limit-rate 1M -O https://$HOST/largefile.zip
```
- 参数解释：`--limit-rate` 限制传输速度
- 预期结果：下载速度不超过 1MB/s
- 常见坑：单位 K/M/G 基于 1024

### 7.13 使用代理

```bash
# HTTP 代理
curl -x http://proxy.example.com:8080 https://$HOST/api

# SOCKS5 代理（远程 DNS）
curl -x socks5h://proxy.example.com:1080 https://$HOST/api

# 代理认证
curl -x http://proxy.example.com:8080 -U proxyuser:proxypass https://$HOST/api
```
- 参数解释：`-x` 指定代理，`-U` 代理认证
- 预期结果：通过代理访问目标
- 常见坑：`socks5://` 本地 DNS，`socks5h://` 远程 DNS

### 7.14 忽略自签证书

```bash
curl -k https://self-signed.example.com/api
# 或指定 CA 证书（更安全）
curl --cacert custom-ca.pem https://$HOST/api
```
- 参数解释：`-k` 跳过证书验证，`--cacert` 指定自定义 CA
- 预期结果：成功连接自签名证书服务器
- 常见坑：**`-k` 存在中间人攻击风险**，仅限测试环境。生产环境应使用 `--cacert`

### 7.15 只看响应头

```bash
# HEAD 请求
curl -I https://$HOST/api

# 将响应头输出到 stdout
curl -D - -o /dev/null https://$HOST/api

# 包含响应头和响应体
curl -i https://$HOST/api
```
- 参数解释：`-I` HEAD 请求，`-D -` 响应头到 stdout
- 预期结果：只看到响应头
- 常见坑：`-I` 发送 HEAD 请求，某些服务器对 HEAD 和 GET 返回不同

### 7.16 输出 HTTP 状态码与耗时

```bash
# 状态码
curl -s -o /dev/null -w "%{http_code}\n" https://$HOST/api

# 状态码 + 总耗时
curl -s -o /dev/null -w "HTTP %{http_code} | Time: %{time_total}s\n" https://$HOST/api

# 详细计时
curl -s -o /dev/null -w \
  "DNS:%{time_namelookup} Connect:%{time_connect} TLS:%{time_appconnect} TTFB:%{time_starttransfer} Total:%{time_total}\n" \
  https://$HOST/api

# JSON 格式输出
curl -s -o /dev/null -w \
  '{"http_code":%{http_code},"time_total":%{time_total},"remote_ip":"%{remote_ip}"}\n' \
  https://$HOST/api
```
- 参数解释：`-w` 自定义输出格式，`-s -o /dev/null` 隐藏其他输出
- 预期结果：只输出状态码和计时信息
- 常见坑：`-w` 的输出在响应体之后，需配合 `-o /dev/null` 分离

### 7.17 失败自动重试

```bash
curl --retry 5 --retry-delay 2 --retry-connrefused \
  -f -o output.txt https://$HOST/api
```
- 参数解释：`--retry` 重试次数，`--retry-delay` 间隔，`--retry-connrefused` 连接拒绝也重试
- 预期结果：临时失败时自动重试
- 常见坑：默认不对 4xx 重试，需 `--retry-all-errors`

### 7.18 设置连接超时与总超时

```bash
curl --connect-timeout 10 --max-time 30 https://$HOST/api
```
- 参数解释：`--connect-timeout` 连接阶段超时，`--max-time` 总超时
- 预期结果：连接超过 10 秒或总操作超过 30 秒自动中止
- 常见坑：`--max-time` 包含连接时间，应大于 `--connect-timeout`

### 7.19 跟随重定向

```bash
curl -L --max-redirs 5 https://$HOST/redirect
```
- 参数解释：`-L` 跟随重定向，`--max-redirs` 限制次数
- 预期结果：自动跳转到最终页面
- 常见坑：POST 301/302 默认变 GET；使用 `--post301`/`--post302` 保持 POST

### 7.20 使用配置文件

```bash
cat > ~/.curlrc << 'EOF'
# 默认选项
--compressed
--connect-timeout 10
--max-time 60
--retry 3
--user-agent "MyApp/1.0"
EOF

# 使用默认配置文件
curl https://$HOST/api

# 指定配置文件
curl -K custom-config.txt https://$HOST/api
```
- 参数解释：`~/.curlrc` 默认配置文件，`-K` 指定配置文件
- 预期结果：自动应用配置文件中的选项
- 常见坑：`~/.curlrc` 中的选项会被命令行选项覆盖

### 7.21 多 URL 与并发

```bash
# 顺序获取多个 URL
curl -O https://$HOST/file[1-10].txt

# 并行获取
curl --parallel --parallel-max 5 -O https://$HOST/file[1-50].txt

# 多 URL 不同选项
curl -d "data1" https://$HOST/api/1 \
  --next -d "data2" https://$HOST/api/2

# 速率限制
curl --rate 10/s -O https://$HOST/file[1-100].txt
```
- 参数解释：`--parallel` 并行传输，`--next` 分组，`--rate` 限速
- 预期结果：高效批量获取
- 常见坑：并行数过高可能导致服务器拒绝连接

### 7.22 调试 TLS / DNS / 代理问题

```bash
# TLS 调试
curl -v https://$HOST/api 2>&1 | grep -E "SSL|TLS|certificate"

# 完整 TLS trace
curl --trace-ascii - -o /dev/null https://$HOST/api 2>&1 | grep -i "ssl\|tls"

# DNS 调试
curl -v https://$HOST/api 2>&1 | grep -i "resolve\|dns\|connect"

# 自定义 DNS 解析
curl --resolve $HOST:443:10.0.0.1 https://$HOST/api

# 使用指定 DNS 服务器
curl --dns-servers 8.8.8.8 https://$HOST/api

# 代理调试
curl -v -x http://proxy:8080 https://$HOST/api 2>&1 | grep -i "proxy\|connect"

# 查看协商的 HTTP 版本
curl -sI -o /dev/null -w "%{http_version}\n" https://$HOST/api

# 查看远程 IP 和端口
curl -s -o /dev/null -w "IP:%{remote_ip} Port:%{remote_port}\n" https://$HOST/api
```
- 参数解释：`-v` 详细输出，`--trace-ascii` 完整 trace，`--resolve` 自定义 DNS
- 预期结果：显示 TLS 握手、DNS 解析、代理连接的详细信息
- 常见坑：`-v` 输出到 stderr，需 `2>&1` 重定向

---

## 8. 退出码

| 退出码 | 常量名 | 说明 |
|---|---|---|
| `0` | `CURLE_OK` | 操作成功 |
| `1` | `CURLE_UNSUPPORTED_PROTOCOL` | 不支持的协议 |
| `2` | `CURLE_FAILED_INIT` | 初始化失败 |
| `3` | `CURLE_URL_MALFORMAT` | URL 格式错误 |
| `4` | `CURLE_NOT_BUILT_IN` | 功能未编译 |
| `5` | `CURLE_COULDNT_RESOLVE_PROXY` | 无法解析代理 |
| `6` | `CURLE_COULDNT_RESOLVE_HOST` | 无法解析主机（DNS 失败） |
| `7` | `CURLE_COULDNT_CONNECT` | 无法连接服务器 |
| `8` | `CURLE_WEIRD_SERVER_REPLY` | 服务器回复异常 |
| `9` | `CURLE_REMOTE_ACCESS_DENIED` | 远程访问被拒绝 |
| `10` | `CURLE_FTP_ACCEPT_FAILED` | FTP ACCEPT 失败 |
| `11` | `CURLE_FTP_WEIRD_PASS_REPLY` | FTP PASS 回复异常 |
| `12` | `CURLE_FTP_ACCEPT_TIMEOUT` | FTP ACCEPT 超时 |
| `13` | `CURLE_FTP_WEIRD_PASV_REPLY` | FTP PASV 回复异常 |
| `14` | `CURLE_FTP_WEIRD_227_FORMAT` | FTP 227 格式异常 |
| `15` | `CURLE_FTP_CANT_GET_HOST` | FTP 无法获取主机 |
| `16` | `CURLE_HTTP2` | HTTP/2 错误 |
| `17` | `CURLE_FTP_COULDNT_SET_TYPE` | FTP 设置类型失败 |
| `18` | `CURLE_PARTIAL_FILE` | 传输不完整 |
| `19` | `CURLE_FTP_COULDNT_RETR_FILE` | FTP 无法获取文件 |
| `20` | — | （未使用） |
| `21` | `CURLE_QUOTE_ERROR` | FTP QUOTE 命令错误 |
| `22` | `CURLE_HTTP_RETURNED_ERROR` | HTTP 返回错误（≥400，配合 `-f`） |
| `23` | `CURLE_WRITE_ERROR` | 写入错误 |
| `24` | `CURLE_UPLOAD_FAILED` | 上传失败 |
| `25` | `CURLE_READ_ERROR` | 读取错误 |
| `26` | `CURLE_OUT_OF_MEMORY` | 内存不足 |
| `27` | `CURLE_OPERATION_TIMEDOUT` | 操作超时 |
| `28` | — | （同 27，历史遗留） |
| `30` | `CURLE_FTP_PORT_FAILED` | FTP PORT 失败 |
| `31` | `CURLE_FTP_COULDNT_USE_REST` | FTP REST 失败 |
| `33` | `CURLE_RANGE_ERROR` | Range 不支持 |
| `34` | `CURLE_HTTP_POST_ERROR` | HTTP POST 错误 |
| `35` | `CURLE_SSL_CONNECT_ERROR` | SSL/TLS 连接错误 |
| `36` | `CURLE_BAD_DOWNLOAD_RESUME` | 断点续传失败 |
| `37` | `CURLE_FILE_COULDNT_READ_FILE` | 文件无法读取 |
| `38` | `CURLE_LDAP_CANNOT_BIND` | LDAP 绑定失败 |
| `39` | `CURLE_LDAP_SEARCH_FAILED` | LDAP 搜索失败 |
| `41` | `CURLE_FUNCTION_NOT_FOUND` | 函数未找到 |
| `42` | `CURLE_ABORTED_BY_CALLBACK` | 回调中止 |
| `43` | `CURLE_BAD_FUNCTION_ARGUMENT` | 参数错误 |
| `45` | `CURLE_INTERFACE_FAILED` | 接口绑定失败 |
| `47` | `CURLE_TOO_MANY_REDIRECTS` | 重定向次数过多 |
| `48` | `CURLE_UNKNOWN_OPTION` | 未知选项 |
| `49` | `CURLE_SETOPT_OPTION_SYNTAX` | 选项语法错误 |
| `52` | `CURLE_GOT_NOTHING` | 服务器无响应 |
| `53` | `CURLE_SSL_ENGINE_NOTFOUND` | SSL 引擎未找到 |
| `54` | `CURLE_SSL_ENGINE_SETFAILED` | SSL 引擎设置失败 |
| `55` | `CURLE_SEND_ERROR` | 发送错误 |
| `56` | `CURLE_RECV_ERROR` | 接收错误 |
| `58` | `CURLE_SSL_CERTPROBLEM` | 证书问题 |
| `59` | `CURLE_SSL_CIPHER` | SSL 密码套件错误 |
| `60` | `CURLE_PEER_FAILED_VERIFICATION` | 证书验证失败 |
| `61` | `CURLE_BAD_CONTENT_ENCODING` | 内容编码错误 |
| `62` | `CURLE_OBSOLETE` | （已废弃） |
| `63` | `CURLE_FILESIZE_EXCEEDED` | 文件大小超限 |
| `64` | `CURLE_USE_SSL_FAILED` | SSL 使用失败 |
| `65` | `CURLE_SEND_FAIL_REWIND` | 发送失败需回退 |
| `66` | `CURLE_SSL_ENGINE_INITFAILED` | SSL 引擎初始化失败 |
| `67` | `CURLE_LOGIN_DENIED` | 登录被拒绝 |
| `68` | `CURLE_TFTP_NOTFOUND` | TFTP 文件未找到 |
| `69` | `CURLE_TFTP_PERM` | TFTP 权限错误 |
| `70` | `CURLE_REMOTE_DISK_FULL` | 远程磁盘满 |
| `71` | `CURLE_TFTP_ILLEGAL` | TFTP 非法操作 |
| `72` | `CURLE_TFTP_UNKNOWNID` | TFTP 未知 ID |
| `73` | `CURLE_REMOTE_FILE_EXISTS` | 远程文件已存在 |
| `74` | `CURLE_TFTP_NOSUCHUSER` | TFTP 无此用户 |
| `75` | `CURLE_CONV_FAILED` | 字符转换失败 |
| `76` | `CURLE_CONV_REQD` | 需要字符转换 |
| `77` | `CURLE_SSL_CACERT_BADFILE` | CA 证书文件错误 |
| `78` | `CURLE_REMOTE_FILE_NOT_FOUND` | 远程文件未找到 |
| `79` | `CURLE_SSH` | SSH 错误 |
| `80` | `CURLE_SSL_SHUTDOWN_FAILED` | SSL 关闭失败 |
| `81` | `CURLE_AGAIN` | 需重试 |
| `82` | `CURLE_SSL_CRL_BADFILE` | CRL 文件错误 |
| `83` | `CURLE_SSL_ISSUER_ERROR` | 证书颁发者错误 |
| `84` | `CURLE_FTP_PRET_FAILED` | FTP PRET 失败 |
| `85` | `CURLE_RTSP_CSEQ_ERROR` | RTSP CSeq 错误 |
| `86` | `CURLE_RTSP_SESSION_ERROR` | RTSP 会话错误 |
| `87` | `CURLE_FTP_BAD_FILE_LIST` | FTP 文件列表错误 |
| `88` | `CURLE_CHUNK_FAILED` | 分块回调失败 |
| `89` | `CURLE_NO_CONNECTION_AVAILABLE` | 无可用连接 |
| `90` | `CURLE_SSL_PINNEDPUBKEYNOTMATCH` | 公钥锁定不匹配 |
| `91` | `CURLE_SSL_INVALIDCERTSTATUS` | 证书状态无效 |
| `92` | `CURLE_HTTP2_STREAM` | HTTP/2 流错误 |
| `93` | `CURLE_RECURSIVE_API_CALL` | 递归 API 调用 |
| `94` | `CURLE_AUTH_ERROR` | 认证错误 |
| `95` | `CURLE_HTTP3` | HTTP/3 错误 |
| `96` | `CURLE_QUIC_CONNECT_ERROR` | QUIC 连接错误 |
| `97` | `CURLE_PROXY` | 代理错误 |
| `98` | `CURLE_SSL_CLIENTCERT` | 客户端证书错误 |

---

## 9. 安全建议

### 9.1 不要明文写密码

```bash
# ❌ 危险：密码出现在 ps 和 shell 历史中
curl -u admin:secret https://$HOST/api
curl https://admin:secret@$HOST/api

# ✅ 安全：交互式输入密码
curl -u admin https://$HOST/api

# ✅ 更安全：使用 netrc 文件
echo "machine $HOST login admin password secret" > ~/.netrc
chmod 600 ~/.netrc
curl -n https://$HOST/api

# ✅ 8.x 推荐：使用变量从环境读取
curl --variable '%API_PASS' --expand-user "admin:{{API_PASS}}" https://$HOST/api
```

### 9.2 `-k/--insecure` 的风险

`-k` 跳过 TLS 证书验证，使连接容易受到中间人攻击。**仅在测试环境使用**。

```bash
# ❌ 不安全：生产环境跳过证书验证
curl -k https://$HOST/api

# ✅ 安全：指定自定义 CA 证书
curl --cacert custom-ca.pem https://$HOST/api

# ✅ 安全：锁定公钥指纹
curl --pinnedpubkey "sha256//base64==" https://$HOST/api
```

### 9.3 `-u user:pass` 的泄露风险

`-u` 指定的凭据会出现在：
- `ps aux` 进程列表
- Shell 历史文件（`~/.bash_history`、`~/.zsh_history`）
- 系统审计日志

**替代方案**：使用 `--netrc-file`、`--variable`（8.x）或 `-u user`（交互输入）。

### 9.4 `@file` 读取敏感文件风险

```bash
# ❌ 危险：如果用户输入被注入到 -d 参数
curl -d "@$USER_INPUT" https://$HOST/api
# 攻击者输入 "@/etc/passwd" 即可读取敏感文件

# ✅ 安全：使用 --data-raw 避免文件引用解析
curl --data-raw "$USER_INPUT" https://$HOST/api
```

### 9.5 代理与重定向风险

```bash
# ❌ 危险：跟随重定向并携带凭据
curl -L --location-trusted -u user:pass https://$HOST/redirect
# 凭据可能发送给恶意重定向目标

# ✅ 安全：默认 -L 不携带凭据
curl -L -u user:pass https://$HOST/redirect

# ✅ 安全：限制重定向协议
curl -L --proto-redir -all,+https https://$HOST/redirect

# ✅ 安全：限制重定向次数
curl -L --max-redirs 5 https://$HOST/redirect
```

### 9.6 Token 泄露风险

```bash
# ❌ 危险：Token 出现在进程列表
curl -H "Authorization: Bearer eyJhb..." https://$HOST/api

# ✅ 安全：从环境变量读取
TOKEN=$(cat ~/.token)
curl -H "Authorization: Bearer $TOKEN" https://$HOST/api

# ✅ 更安全：使用配置文件
echo '-H "Authorization: Bearer '"$TOKEN"'"' > ~/.curlrc.api
chmod 600 ~/.curlrc.api
curl -K ~/.curlrc.api https://$HOST/api

# ✅ 8.x 推荐：使用变量
curl --variable '%TOKEN' --expand-header "Authorization: Bearer {{TOKEN}}" https://$HOST/api
```

### 9.7 安全加固速查表

| 安全建议 | 实现方式 |
|---|---|
| 不在命令行明文写密码 | 使用 `--netrc-file` 或 `--variable` |
| 不跳过证书验证 | 使用 `--cacert` 代替 `-k` |
| 限制协议 | `--proto -all,+https` |
| 限制重定向协议 | `--proto-redir -all,+https` |
| 限制重定向次数 | `--max-redirs 5` |
| 不在 URL 中嵌入凭据 | 使用 `-u` 或 netrc |
| 使用配置文件权限 | `chmod 600 ~/.curlrc` |
| 清理 shell 历史 | `history -d <line>` 或 `HISTCONTROL=ignorespace`（命令前加空格） |
| 锁定公钥 | `--pinnedpubkey` |
| 禁用 URL 用户名 | `--disallow-username-in-url`（8.7+） |

---

## 10. 常见错误与排错清单

### 10.1 DNS 失败

| 现象 | 退出码 | 排查 | 解决 |
|---|---|---|---|
| Could not resolve host | 6 | `nslookup $HOST` | 检查 DNS 配置 / 使用 `--resolve` 或 `--dns-servers` |
| 解析到错误 IP | — | `dig $HOST` | 使用 `--resolve` 指定正确 IP |
| IPv6 解析失败 | 6 | `curl -v https://$HOST 2>&1 \| grep resolve` | 使用 `--ipv4` 强制 IPv4 |

### 10.2 TLS 证书错误

| 现象 | 退出码 | 排查 | 解决 |
|---|---|---|---|
| 证书验证失败 | 60 | `curl -v https://$HOST 2>&1 \| grep -i cert` | 使用 `--cacert` 指定正确 CA |
| 自签名证书 | 60 | 同上 | 测试环境用 `-k`，生产用 `--cacert` |
| 证书过期 | 60 | `echo \| openssl s_client -connect $HOST:443` | 更新证书 |
| 证书域名不匹配 | 51 | 检查证书 SAN | 使用 `--resolve` 指定正确域名 |
| CRL 检查失败 | 35 | — | `--ssl-no-revoke`（Schannel）或更新 CRL |

### 10.3 连接超时

| 现象 | 退出码 | 排查 | 解决 |
|---|---|---|---|
| 连接超时 | 28 | `telnet $HOST 443` | 检查防火墙 / 网络 |
| 连接被拒绝 | 7 | `nc -zv $HOST 443` | 检查服务是否运行 |
| 连接重置 | 56 | `curl -v https://$HOST` | 检查 MTU / 防火墙规则 |

### 10.4 代理错误

| 现象 | 退出码 | 排查 | 解决 |
|---|---|---|---|
| 代理连接失败 | 5 | `curl -v -x $PROXY https://$HOST 2>&1 \| head` | 检查代理地址和端口 |
| 代理认证失败 | 97 | `curl -v -U user:pass -x $PROXY ...` | 检查代理凭据 |
| 代理不支持 HTTPS 隧道 | — | `curl -v -p -x $PROXY ...` | 使用 `-p` 启用 CONNECT 隧道 |

### 10.5 重定向循环

| 现象 | 退出码 | 排查 | 解决 |
|---|---|---|---|
| Too many redirects | 47 | `curl -v -L https://$HOST 2>&1 \| grep Location` | 检查 Cookie / 限制 `--max-redirs` |
| 重定向到错误协议 | — | `curl -v -L https://$HOST` | `--proto-redir -all,+https` |

### 10.6 HTTP 4xx / 5xx

| 状态码 | 含义 | curl 退出码（配合 `-f`） | 排查 |
|---|---|---|---|
| 400 | Bad Request | 22 | 检查请求格式 / 请求体 |
| 401 | Unauthorized | 22 | 检查认证凭据 |
| 403 | Forbidden | 22 | 检查权限 / Token / Cookie |
| 404 | Not Found | 22 | 检查 URL |
| 429 | Too Many Requests | 22 | 降低频率 / 添加 `--retry` |
| 500 | Internal Server Error | 22 | 检查服务器日志 |
| 502/503/504 | Gateway/Service errors | 22 | 检查上游服务 / 添加 `--retry` |

### 10.7 上传/下载中断

| 现象 | 退出码 | 排查 | 解决 |
|---|---|---|---|
| 下载不完整 | 18 | 检查 Content-Length | 使用 `-C -` 断点续传 |
| 上传中断 | 25 | 检查磁盘空间 / 网络 | 使用 `--retry` 自动重试 |
| 传输速度过慢 | — | `--limit-rate` 检查 | 使用 `-Y -y` 设置最低速度 |

### 10.8 HTTP/2 / HTTP/3 协商失败

| 现象 | 退出码 | 排查 | 解决 |
|---|---|---|---|
| HTTP/2 不可用 | — | `curl --version \| grep HTTP2` | 安装 nghttp2 重新编译 |
| HTTP/3 不可用 | — | `curl --version \| grep HTTP3` | 安装 QUIC 库重新编译 |
| HTTP/2 流错误 | 92 | `curl -v --http2 ...` | 检查服务器 HTTP/2 实现 |
| HTTP/3 连接失败 | 96 | `curl -v --http3 ...` | 检查 UDP/QUIC 防火墙规则 |

### 10.9 退出码排查

```bash
# 捕获退出码
curl -f https://$HOST/api
EXIT_CODE=$?
echo "Exit code: $EXIT_CODE"

# 常见退出码快速排查
case $EXIT_CODE in
  0)   echo "成功" ;;
  6)   echo "DNS 解析失败" ;;
  7)   echo "连接被拒绝" ;;
  22)  echo "HTTP 错误（≥400）" ;;
  28)  echo "操作超时" ;;
  35)  echo "SSL/TLS 连接错误" ;;
  47)  echo "重定向次数过多" ;;
  60)  echo "证书验证失败" ;;
  *)   echo "其他错误：$EXIT_CODE" ;;
esac
```

---

## 11. 按字母索引

| 字母 | 参数 |
|---|---|
| **A** | `--abstract-unix-socket`, `--alt-svc`, `--anyauth`, `-a/--append`, `--aws-sigv4` |
| **B** | `-B/--use-ascii`, `--basic`, `-b/--cookie`, `--ca-native`, `--cacert`, `--capath` |
| **C** | `-E/--cert`, `--cert-status`, `--cert-type`, `-c/--cookie-jar`, `--ciphers`, `--compressed`, `--compressed-ssh`, `-K/--config`, `--connect-timeout`, `--connect-to`, `-C/--continue-at`, `--create-dirs`, `--create-file-mode`, `--crlf`, `--crlfile`, `--curves` |
| **D** | `-d/--data`, `--data-ascii`, `--data-binary`, `--data-raw`, `--data-urlencode`, `--delegation`, `--digest`, `--disable-eprt`, `--disable-epsv`, `--disallow-username-in-url`, `--dns-interface`, `--dns-ipv4-addr`, `--dns-ipv6-addr`, `--dns-servers`, `--doas-auth`, `--dump-ca-embed`, `-D/--dump-header` |
| **E** | `--ech`, `--egd-file`, `--engine`, `--etag-compare`, `--etag-save`, `--expect100-timeout`, `-e/--referer` |
| **F** | `-f/--fail`, `--fail-with-body`, `--fail-early`, `--false-start`, `-F/--form`, `--form-escape`, `--form-string`, `--ftp-account`, `--ftp-alternative-to-user`, `--ftp-create-dirs`, `--ftp-method`, `--ftp-pasv`, `-P/--ftp-port`, `--ftp-pret`, `--ftp-skip-pasv-ip`, `--ftp-ssl-ccc`, `--ftp-ssl-ccc-mode`, `--ftp-ssl-control` |
| **G** | `-G/--get`, `-g/--globoff` |
| **H** | `--haproxy-clientip`, `--haproxy-protocol`, `--happy-eyeballs-timeout-ms`, `--head`, `-H/--header`, `--help`, `--hostpubmd5`, `--hostpubsha256`, `--hsts`, `--http0.9`, `--http1.0`, `--http1.1`, `--http2`, `--http2-prior-knowledge`, `--http3`, `--http3-only` |
| **I** | `--ignore-content-length`, `-i/--include`, `--insecure`, `--interface`, `--ip-tos`, `--ipv4`, `--ipv6` |
| **J** | `-j/--junk-session-cookies`, `--json`, `-J/--remote-header-name` |
| **K** | `--keepalive`, `--keepalive-time`, `--key`, `--key-type`, `--krb` |
| **L** | `--libcurl`, `--limit-rate`, `-l/--list-only`, `--local-port`, `-L/--location`, `--location-trusted`, `--login-options` |
| **M** | `--mail-auth`, `--mail-from`, `--mail-rcpt`, `--mail-rcpt-allowfails`, `--manual`, `--max-filesize`, `--max-redirs`, `-m/--max-time`, `--metalink` |
| **N** | `--negotiate`, `-n/--netrc`, `--netrc-file`, `--netrc-optional`, `--next`, `--no-alpn`, `-N/--no-buffer`, `--no-clobber`, `--no-keepalive`, `--no-npn`, `--no-progress-meter`, `--no-sessionid`, `--noproxy`, `--ntlm`, `--ntlm-wb` |
| **O** | `--oauth2-bearer`, `-o/--output`, `--output-dir` |
| **P** | `--parallel`, `--parallel-immediate`, `--parallel-max`, `--parallel-max-host`, `--parallel-progress`, `--pass`, `--path-as-is`, `--pinnedpubkey`, `--pipelining`, `--post301`, `--post302`, `--post303`, `--preproxy`, `--progress-bar`, `--proto`, `--proto-default`, `--proto-redir`, `--proxy`, `--proxy-anyauth`, `--proxy-basic`, `--proxy-ca-native`, `--proxy-cacert`, `--proxy-capath`, `--proxy-cert`, `--proxy-cert-type`, `--proxy-ciphers`, `--proxy-crlfile`, `--proxy-digest`, `--proxy-header`, `--proxy-http2`, `--proxy-insecure`, `--proxy-key`, `--proxy-key-type`, `--proxy-negotiate`, `--proxy-ntlm`, `--proxy-pass`, `--proxy-pinnedpubkey`, `--proxy-service-name`, `--proxy-ssl-allow-beast`, `--proxy-ssl-auto-client-cert`, `--proxy-tls13-ciphers`, `--proxy-tlsauthtype`, `--proxy-tlspassword`, `--proxy-tlsuser`, `--proxy-tlsv1`, `--proxy-user`, `--proxy1.0`, `-p/--proxytunnel`, `--pubkey` |
| **Q** | `-q`, `-Q/--quote` |
| **R** | `--random-file`, `-r/--range`, `--rate`, `--raw`, `-e/--referer`, `--remote-header-name`, `--remote-name`, `--remote-name-all`, `-R/--remote-time`, `--remove-on-error`, `-X/--request`, `--request-target`, `--resolve`, `--retry`, `--retry-all-errors`, `--retry-connrefused`, `--retry-delay`, `--retry-max-time` |
| **S** | `--sasl-authzid`, `--sasl-ir`, `--service-name`, `--sessionid`, `-S/--show-error`, `-s/--silent`, `--socks4`, `--socks4a`, `--socks5`, `--socks5-basic`, `--socks5-gssapi`, `--socks5-gssapi-nec`, `--socks5-gssapi-service`, `--socks5-hostname`, `-Y/--speed-limit`, `-y/--speed-time`, `--ssl`, `--ssl-allow-beast`, `--ssl-auto-client-cert`, `--ssl-no-revoke`, `--ssl-reqd`, `--ssl-revoke-best-effort`, `--stderr`, `--styled-output`, `--suppress-connect-headers` |
| **T** | `--tcp-fastopen`, `--tcp-nodelay`, `-t/--telnet-option`, `--test-event`, `--tftp-blksize`, `--tftp-no-options`, `-z/--time-cond`, `--tls-earlydata`, `--tls-max`, `--tls13-ciphers`, `--tlsauthtype`, `--tlspassword`, `--tlsuser`, `--tlsv1`, `--tlsv1.0`, `--tlsv1.1`, `--tlsv1.2`, `--tlsv1.3`, `--trace`, `--trace-ascii`, `--trace-config`, `--trace-ids`, `--trace-time`, `--tr-encoding`, `-T/--upload-file` |
| **U** | `--unix-socket`, `--url`, `--url-query`, `--user`, `--user-agent` |
| **V** | `--variable`, `-v/--verbose`, `-V/--version`, `--vlan-priority` |
| **W** | `--ws-options`, `-w/--write-out` |
| **X** | `-x/--proxy`, `--xattr` |
| **Z** | `-Z/--parallel` |

---

## 附录：核心术语中英文对照

| 中文术语 | 英文术语 | 说明 |
|---|---|---|
| 统一资源定位符 | URL (Uniform Resource Locator) | 网络资源地址 |
| 传输层安全 | TLS (Transport Layer Security) | 加密传输协议 |
| 超文本传输协议 | HTTP (HyperText Transfer Protocol) | Web 传输协议 |
| 快速 UDP 网络连接 | QUIC (Quick UDP Internet Connections) | HTTP/3 底层传输 |
| 代理服务器 | Proxy Server | 中转服务器 |
| 套接字安全 | SOCKS (Socket Secure) | 代理协议 |
| 域名系统 | DNS (Domain Name System) | 域名解析 |
| 内容分发 | Content-Disposition | 附件文件名头 |
| 证书颁发机构 | CA (Certificate Authority) | 签发证书 |
| 证书吊销列表 | CRL (Certificate Revocation List) | 已吊销证书列表 |
| 在线证书状态协议 | OCSP (Online Certificate Status Protocol) | 证书状态查询 |
| 加密客户端问候 | ECH (Encrypted Client Hello) | 加密 SNI |
| HTTP 严格传输安全 | HSTS (HTTP Strict Transport Security) | 强制 HTTPS |
| 替代服务 | Alt-Svc (Alternative Service) | 协议升级提示 |
| 应用层协议协商 | ALPN (Application-Layer Protocol Negotiation) | TLS 内协议协商 |
| 首字节时间 | TTFB (Time To First Byte) | 服务器响应首字节耗时 |
| 简单认证安全层 | SASL (Simple Authentication and Security Layer) | 认证框架 |
| 协商认证 | SPNEGO (Simple and Protected GSSAPI Negotiation) | Kerberos 认证 |
| OAuth 2.0 持有者令牌 | OAuth 2.0 Bearer Token | API 认证令牌 |
| AWS 签名版本 4 | AWS Signature V4 | AWS API 认证 |

---

> **参考文档**：
> - curl 官方手册页：https://curl.se/docs/manpage.html [$TRAE_REF](https://curl.se/docs/manpage.html)
> - curl 官方教程：https://curl.se/docs/tutorial.html [$TRAE_REF](https://curl.se/docs/tutorial.html)
> - curl HTTP 脚本指南：https://curl.se/docs/httpscripting.html [$TRAE_REF](https://curl.se/docs/httpscripting.html)
> - curl 选项添加历史：https://curl.se/docs/optionswhen.html [$TRAE_REF](https://curl.se/docs/optionswhen.html)
> - curl 变更日志：https://curl.se/changes.html [$TRAE_REF](https://curl.se/changes.html)
> - RFC 3986（URL 语法）：https://www.ietf.org/rfc/rfc3986.txt [$TRAE_REF](https://www.ietf.org/rfc/rfc3986.txt)