# PHP 代码审计

### 2.1 危险函数速查

| 漏洞类型 | 危险函数 |
|----------|----------|
| 代码执行 | `eval()` `assert()` `preg_replace(/e)` `create_function()` |
| 命令执行 | `system()` `exec()` `passthru()` `shell_exec()` `popen()` `proc_open()` `` ` `` |
| 文件包含 | `include()` `require()` `include_once()` `require_once()` |
| 文件读取 | `file_get_contents()` `fread()` `fopen()` `readfile()` `show_source()` |
| 文件写入 | `file_put_contents()` `fwrite()` |
| 反序列化 | `unserialize()` |
| SQL 注入 | `mysql_query()` `mysqli_query()`（拼接 SQL 时） |

### 2.2 文件操作漏洞审计

**文件包含漏洞**

```php
// —— 漏洞代码 ——
$page = $_GET['page'];
include("templates/" . $page . ".php");  // 可包含任意文件
```

```php
// —— 修复代码 ——
$whitelist = ['index', 'about', 'contact'];
$page = $_GET['page'];
if (in_array($page, $whitelist, true)) {
    include "templates/{$page}.php";
} else {
    http_response_code(404);
    exit('非法请求');
}
```

**任意文件读取**

```php
// —— 漏洞代码 ——
echo file_get_contents($_GET['file']);  // 直接读取用户传入路径
```

```php
// —— 修复代码 ——
$base = realpath(__DIR__ . '/uploads/');
$file = realpath($base . '/' . basename($_GET['file']));
if ($file && strpos($file, $base) === 0) {
    echo file_get_contents($file);
}
```

审计要点：追踪 `$_GET/$_POST/$_REQUEST` 是否直接传入文件操作函数，关注路径拼接时是否使用 `realpath()` + 前缀校验。

### 2.3 SQL 注入审计

```php
// —— 漏洞代码：直接拼接 ——
$id = $_GET['id'];
$result = mysqli_query($conn, "SELECT * FROM users WHERE id = $id");

// —— 漏洞代码：预处理误用 ——
$stmt = $conn->prepare("SELECT * FROM users WHERE id = ?");
$stmt->bind_param("s", $_GET['id']);  // bind_param("s", ...) - 这里 bind 的是字符串
$result = $stmt->execute();
// 实际上 bind_param 的 "s" 类型对整数注入防护有限，建议使用 "i"
```

```php
// —— 修复代码：PDO 预处理 ——
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = :id");
$stmt->execute([':id' => $_GET['id']]);
$result = $stmt->fetchAll(PDO::FETCH_ASSOC);
```

审计要点：全局搜索 `query(`、`execute(`，检查 SQL 语句中是否存在变量拼接；预处理语句的参数类型是否匹配预期。

### 2.4 反序列化漏洞审计

```php
// —— 漏洞代码 ——
$data = unserialize($_COOKIE['data']);
// 若存在可利用的魔术方法链，可导致 RCE
```

```php
// —— 危险魔术方法链示例 ——
class Logger {
    public $logFile;
    public $content;
    function __destruct() {
        file_put_contents($this->logFile, $this->content);  // Sink
    }
}
class Cache {
    public $obj;
    function __destruct() {
        $this->obj->flush();  // 触发其他类方法
    }
}
// 攻击者构造 POP 链：Cache -> Logger -> __destruct -> file_put_contents
```

```php
// —— 修复代码 ——
$data = json_decode($_COOKIE['data'], true);  // 使用 JSON 替代序列化
// 或限制反序列化类型
$data = unserialize($_COOKIE['data'], ['allowed_classes' => false]);
```

审计要点：搜索 `unserialize(`，检查参数是否用户可控；梳理 `__wakeup`、`__destruct`、`__toString`、`__call` 等魔术方法是否形成 POP 链。

### 2.5 PHP 框架审计要点

| 框架 | 重点审计位置 |
|------|-------------|
| **ThinkPHP** | 路由参数解析（`$_GET[路由参数]`）、控制器方法名可控、模板渲染函数 |
| **Laravel** | ` unserialize()` 调用、Blade 模板 `{!! !!}` 原始输出、Eloquent 原生查询 `DB::raw()` |

```php
// ThinkPHP 危险模式：方法名可控
// index.php?m=Home&c=Index&a=phpinfo  → 可调用任意公开方法
```

### 2.6 PHP 配置安全

| 配置项 | 安全建议 |
|--------|----------|
| `disable_functions` | 禁用 `exec,system,passthru,shell_exec,proc_open,popen` |
| `open_basedir` | 限制 PHP 文件操作目录范围 |
| `display_errors` | 生产环境设为 `Off` |
| `magic_quotes_gpc` | 已废弃，不应依赖 |
| `allow_url_include` | 设为 `Off`，防止远程文件包含 |

### 2.7 审计实战：模拟审计简化 CMS

以一个简化 CMS 为例，审计流程如下：

```
1. 信息收集：CMS 基于 ThinkPHP 5.0，入口 public/index.php
2. 路由梳理：GET /index/index/hello?name=xxx → Index::hello()
3. 代码审查：
```

```php
// application/index/controller/Index.php
public function hello($name) {
    echo "Hello, " . $name;        // [低危] XSS：未转义直接输出
    $file = input('get.file');
    include($file);                // [高危] 任意文件包含
    $id = input('get.id/d');
    $user = Db::table('users')->where('id', $id)->find();  // [安全] 参数化查询
}
```

```php
// 修复后
public function hello($name) {
    echo "Hello, " . htmlspecialchars($name, ENT_QUOTES);
    $whitelist = ['header', 'footer'];
    $file = input('get.file');
    if (!in_array($file, $whitelist, true)) {
        abort(404);
    }
    include "template/{$file}.php";
    $id = input('get.id/d');
    $user = Db::table('users')->where('id', $id)->find();
}
```

---

---

## 📋 内容审核与补充建议

> 针对「PHP 代码审计」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

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
