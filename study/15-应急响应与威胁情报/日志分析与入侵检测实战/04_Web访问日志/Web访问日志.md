# Web访问日志

### 4.1 Apache/Nginx日志

```bash
# Apache/Nginx访问日志分析

# 统计IP访问频率(暴力破解/扫描检测)
awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -20

# 检测SQL注入
grep -i "union\|select\|drop\|insert\|update\|delete.*from" /var/log/nginx/access.log

# 检测XSS
grep -i "<script\|javascript:\|onerror\|onload\|alert\|document.cookie" /var/log/nginx/access.log

# 检测路径遍历
grep -i "\.\./\|\.\\.\|\.\.%2f\|%2e%2e%2f" /var/log/nginx/access.log

# 检测命令注入
grep -i "; cat\|; ls\|; id\|; whoami\|\$\(.*\)\|`.*`" /var/log/nginx/access.log

# 检测Web Shell
grep -i "eval(\|assert(\|system(\|exec(\|shell_exec\|passthru\|base64_decode" /var/log/nginx/access.log

# 检测文件包含
grep -i "php://\|data://\|expect://\|file://\|include=" /var/log/nginx/access.log

# 检测SSRF
grep -i "127.0.0.1\|localhost\|169.254.169.254\|0.0.0.0\|file://" /var/log/nginx/access.log

# 统计HTTP状态码
awk '{print $9}' /var/log/nginx/access.log | sort | uniq -c | sort -rn

# 404分析(目录爆破检测)
awk '$9==404 {print $7}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -20

# User-Agent分析
awk -F'"' '{print $6}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -20
```

### 4.2 攻击特征识别

```
常见攻击日志特征:

SQL注入:
  /page?id=1' OR '1'='1
  /page?id=1 UNION SELECT 1,2,3--
  /page?id=1;DROP TABLE users--
  /search?q=' UNION SELECT user(),version(),3--

XSS:
  /search?q=<script>alert(1)</script>
  /search?q=<img src=x onerror=alert(1)>
  /search?q="><script>document.cookie</script>

路径遍历:
  /file?name=../../../etc/passwd
  /file?name=..%2f..%2f..%2fetc%2fpasswd
  /file?name=/etc/passwd

命令注入:
  /ping?host=127.0.0.1;cat /etc/passwd
  /ping?host=127.0.0.1|id
  /ping?host=$(whoami)

Web Shell:
  POST /uploads/shell.php?cmd=whoami
  POST /images/config.php HTTP/1.1
  GET /tmp/.hidden.php HTTP/1.1

目录爆破:
  大量404响应
  /admin, /phpmyadmin, /.git, /.env, /backup.zip
```

---

---

