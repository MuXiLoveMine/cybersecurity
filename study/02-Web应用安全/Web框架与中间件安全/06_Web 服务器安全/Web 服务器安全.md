# Web 服务器安全

### 6.1 Nginx 安全配置

**配置不当导致目录穿越**

```nginx
location /files {
  alias /data/share/;   # 若 location 无尾斜杠而 alias 有，可穿越
}
# 请求 /files../etc/passwd → 读取 /data/share/../etc/passwd
```

加固：`location` 与 `alias` 路径的尾部斜杠必须一致，或使用 `root` 替代。

**CRLF 注入**

Nginx 在 `$uri` 变量中未过滤 `\r\n`，若将 `$uri` 反射到响应头（如重定向 `Location`），攻击者可注入 `%0d%0a` 实现 HTTP 响应拆分。

```nginx
# 危险
return 302 https://example.com$uri;
# 安全：使用 $request_uri（已编码）或显式过滤
return 302 https://example.com/;
```

**Nginx 安全加固清单**
```nginx
server_tokens off;              # 隐藏版本号
client_max_body_size 1m;         # 限制请求体大小
limit_req_zone ... zone=req:10m rate=10r/s;  # 限速防 CC
add_header X-Frame-Options SAMEORIGIN;
add_header X-Content-Type-Options nosniff;
add_header Content-Security-Policy "default-src 'self'";
ssl_protocols TLSv1.2 TLSv1.3;  # 禁用旧版 TLS
```

### 6.2 Apache 安全配置

**.htaccess 滥用**

Apache 允许目录级 `.htaccess` 覆盖主配置。若攻击者能上传 `.htaccess` 文件，可将任意扩展名解析为 PHP 执行：
```
AddType application/x-httpd-php .jpg
```

加固：生产环境 `AllowOverride None` 禁用 `.htaccess`，配置集中在 httpd.conf。

**路径穿越**

Apache 的 `<Directory>` 配置与 `mod_alias` 的 `Alias` 指令路径处理不一致时可导致穿越。

**Apache 安全加固清单**
- 隐藏版本号：`ServerTokens Prod`、`ServerSignature Off`
- 禁用 `.htaccess`：`AllowOverride None`
- 限制 HTTP 方法：仅允许 GET/POST/HEAD
- 关闭目录列表：`Options -Indexes`
- 移除不必要的模块（mod_info、mod_status）

### 6.3 IIS 安全

**短文件名枚举**

IIS 在 NTFS 文件系统上利用 8.3 短文件名机制（如 `SECRET~1.TXT`），攻击者可通过 `~` 通配符逐字符探测，枚举出完整文件名。该漏洞虽不直接泄露内容，但暴露了文件结构信息。

**解析漏洞**

IIS 6.0 存在经典解析漏洞：
- 分号解析：`test.asp;.jpg` → 按 ASP 执行
- 目录解析：`test.asp/test.jpg` → 按 ASP 执行

IIS 7.x 在 `cgi.fix_pathinfo=1`（PHP 配置）时，`test.jpg/.php` 会按 PHP 执行。

加固：升级 IIS 版本；PHP 配置 `cgi.fix_pathinfo=0`；禁止上传目录的执行权限。

---

---

