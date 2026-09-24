# session_cookie

> **分类**：会话与Cookie
> **说明**：Session 和 Cookie 操作

---

## 语法

```php
session_start(); $_SESSION["key"] = value;\nsetcookie(name, value, expire);
```

## 示例代码

```php
<?php
// ===== Cookie =====

// 设置 Cookie
setcookie("user", "Alice", time() + 3600, "/");  // 1小时过期

// 读取 Cookie
if (isset($_COOKIE["user"])) {
    echo $_COOKIE["user"];
}

// 删除 Cookie（设为过期时间）
setcookie("user", "", time() - 3600, "/");

// ===== Session =====

// 开始会话（必须在任何输出之前）
session_start();

// 设置 Session 变量
$_SESSION["username"] = "Alice";
$_SESSION["user_id"] = 123;
$_SESSION["logged_in"] = true;

// 读取
if (isset($_SESSION["username"])) {
    echo "欢迎, " . $_SESSION["username"];
}

// 删除单个
unset($_SESSION["user_id"]);

// 销毁所有
session_destroy();

// 安全配置（php.ini 或 ini_set）
ini_set("session.cookie_httponly", 1);    // HttpOnly
ini_set("session.cookie_secure", 1);      // 仅 HTTPS
ini_set("session.cookie_samesite", "Strict"); // SameSite
ini_set("session.use_strict_mode", 1);    // 严格模式

// 防止会话固定
session_regenerate_id();  // 登录后重新生成会话ID

// ===== 安全建议 =====
// 1. Session 数据存储在服务器，比 Cookie 安全
// 2. 重要操作前重新验证密码
// 3. 设置合理的过期时间
// 4. 使用 HTTPS 传输
// 5. 开启 HttpOnly 防止 XSS 窃取
// 6. 开启 SameSite 防止 CSRF
```
