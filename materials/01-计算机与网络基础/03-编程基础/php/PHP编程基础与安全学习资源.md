# PHP 编程基础与安全学习资源

> 本文系统介绍 PHP 编程基础与 Web 安全领域应用：PHP 在安全中的定位、编程基础（安全视角）、PHP 安全核心用法（常见漏洞与防御）、常用工具与扩展、2026 年免费学习资源、推荐 GitHub 项目，以及两个可运行的示例程序（basics.php 和 security_cases.php）。面向 Web 安全工程师与代码审计人员，全部内容从防御、漏洞分析和安全研究的正向角度出发。

---

## 目录

- [一、PHP 在网络安全中的定位](#一php-在网络安全中的定位)
- [二、PHP 编程基础（安全视角）](#二php-编程基础安全视角)
- [三、PHP 安全核心用法](#三php-安全核心用法)
- [四、常用工具与扩展](#四常用工具与扩展)
- [五、2026 年免费学习资源](#五2026-年免费学习资源)
- [六、2026 年推荐 GitHub 项目](#六2026-年推荐-github-项目)
- [七、示例代码文件](#七示例代码文件)
- [附：PHP 安全编码检查清单](#附php-安全编码检查清单)

---

## 一、PHP 在网络安全中的定位

### 1.1 PHP 与 Web 安全

PHP 是 Web 开发领域使用最广泛的语言之一。从 WordPress、Drupal、Discuz! 到各类电商系统、CMS 框架，PHP 几乎占据了 Web 应用的半壁江山。**正因为应用广泛，PHP 也成为 Web 安全漏洞的重灾区**。

| 特点 | 说明 | 安全意义 |
|------|------|---------|
| **入门门槛低** | 语法简单，初学者容易上手 | 低质量代码多，漏洞频发 |
| **弱类型语言** | 自动类型转换，灵活方便 | 类型混淆漏洞（MD5 比较、switch 绕过等） |
| **内置大量函数** | 字符串、数组、数据库、文件操作一应俱全 | 危险函数多（eval、system、exec 等） |
| **与 Web 天然集成** | 超全局变量、Session、Cookie 开箱即用 | 输入处理不当直接导致漏洞 |
| **生态庞大** | WordPress、Drupal、ThinkPHP、Laravel 等 | CMS 漏洞影响面极广 |
| **历史遗留多** | PHP 4/5/7/8 各版本差异大 | 不同版本漏洞利用方式不同 |

> **安全视角的重要性**：
> - 作为**Web 渗透测试工程师**：理解 PHP 漏洞原理才能更好地发现和利用
> - 作为**代码审计人员**：PHP 是代码审计最常见的目标语言之一
> - 作为**CMS 安全分析师**：WordPress、Drupal 等都是 PHP 写的
> - 作为**PHP 开发者**：理解常见漏洞才能写出安全的代码

### 1.2 安全领域的应用方向

| 方向 | PHP 的作用 | 典型场景 |
|------|-----------|---------|
| **Web 渗透测试** | 理解 PHP 漏洞原理，编写 PoC | SQL 注入、XSS、文件包含、文件上传 |
| **PHP 代码审计** | 审计 PHP 源码发现漏洞 | 危险函数审计、输入验证审计、业务逻辑漏洞 |
| **CMS 安全分析** | 分析主流 CMS 的漏洞 | WordPress 插件漏洞、ThinkPHP 框架漏洞 |
| **漏洞复现与研究** | 复现 PHP 相关 CVE | 反序列化漏洞、RCE 漏洞分析 |
| **安全工具开发** | 用 PHP 编写安全扫描脚本 | 漏洞扫描器、PoC 验证脚本 |
| **红蓝对抗** | PHP WebShell、内网渗透 | 一句话木马、免杀、提权 |
| **安全加固** | PHP 安全配置、代码加固 | php.ini 安全配置、WAF 规则、代码修复 |

### 1.3 PHP 版本演进与安全变化

| 版本 | 时间 | 安全相关变化 |
|------|------|-------------|
| PHP 4 | 2000 | register_globals 默认开启（极不安全） |
| PHP 5.2 | 2006 | filter 扩展、安全模式、open_basedir |
| PHP 5.3 | 2009 | magic_quotes_gpc 废弃、匿名函数 |
| PHP 5.4 | 2012 | magic_quotes 移除、安全模式移除 |
| PHP 5.6 | 2014 | 常量标量表达式、密码哈希 API |
| PHP 7.0 | 2015 | 巨大性能提升、标量类型声明、null 合并运算符 |
| PHP 7.4 | 2019 | 类型属性、预加载、箭头函数 |
| PHP 8.0 | 2020 | JIT 编译、命名参数、联合类型、match 表达式 |
| PHP 8.1 | 2021 | Fibers、枚举、只读属性 |
| PHP 8.2 | 2022 | 只读类、敏感参数模糊化 |
| PHP 8.3 | 2023 | 类型化类常量、json_validate |

> **注意**：PHP 5.x 已经停止维护，PHP 7.x 也已 EOL。生产环境应使用 PHP 8.x。但大量遗留系统仍在使用旧版本，安全研究中经常需要考虑不同版本的差异。

---

## 二、PHP 编程基础（安全视角）

### 2.1 环境搭建

典型的 PHP 开发环境组合：

| 组合 | 说明 | 适用场景 |
|------|------|---------|
| **LAMP** | Linux + Apache + MySQL + PHP | 经典组合，最广泛使用 |
| **LNMP** | Linux + Nginx + MySQL + PHP | 高性能，Nginx + PHP-FPM |
| **WAMP** | Windows + Apache + MySQL + PHP | Windows 开发环境 |
| **XAMPP** | 跨平台集成环境 | 快速搭建，开发测试用 |
| **Docker** | 容器化部署 | 现代开发、生产部署 |

```bash
# Ubuntu/Debian 安装 PHP
sudo apt install php php-fpm php-mysql php-mbstring php-xml php-curl

# 查看 PHP 版本和配置
php -v
php -i            # 查看所有配置（等价于 phpinfo()）
php -m            # 查看已加载的扩展
php --ini         # 查看 php.ini 位置

# 运行 PHP 内置开发服务器（学习用）
php -S 127.0.0.1:8000
```

### 2.2 基础语法

```php
<?php
// 单行注释
/* 多行注释 */

// 变量：以 $ 开头，弱类型
$name = "Alice";
$age = 25;
$height = 1.68;
$is_student = true;

// 数据类型
$int = 42;           // integer
$float = 3.14;       // float (double)
$str = "hello";      // string
$bool = true;        // boolean
$arr = [1, 2, 3];    // array
$null = null;        // NULL
$obj = new stdClass(); // object

// 类型查看
var_dump($name);     // 输出类型和值
gettype($age);       // 返回类型字符串
is_int($age);        // 判断是否为整数
is_string($name);    // 判断是否为字符串
is_array($arr);      // 判断是否为数组
is_null($null);      // 判断是否为 NULL

// 常量
define("PI", 3.14159);
const MAX_SIZE = 100;

echo PI;        // 3.14159
echo MAX_SIZE;  // 100

// 运算符
$a = 10;
$b = 3;
$a + $b;    // 13
$a - $b;    // 7
$a * $b;    // 30
$a / $b;    // 3.333...
$a % $b;    // 1（取余）
$a ** $b;   // 1000（幂运算，PHP 5.6+）

// 比较运算符
$a == $b;    // 等于（值相等，自动类型转换）⚠️
$a === $b;   // 全等于（类型和值都相等）✅ 推荐
$a != $b;    // 不等于
$a !== $b;   // 不全等于
$a < $b;
$a > $b;
$a <= $b;
$a >= $b;

// 逻辑运算符
true && false;   // false
true || false;   // true
!true;           // false
true and false;  // and 优先级低
true or false;   // or 优先级低
```

> **安全要点**：
> - PHP 是弱类型语言，`==` 比较会自动类型转换，可能导致类型混淆漏洞
> - 例如：`"admin" == 0` 的结果是 `true`（字符串转数字是 0）
> - **永远使用 `===` 进行比较**，除非你明确知道自己在做什么
> - 经典漏洞：MD5 比较绕过（`0e12345 == 0e67890` 为 true，因为都被当 0）

### 2.3 流程控制

```php
// if-else
$score = 85;
if ($score >= 90) {
    echo "优秀";
} elseif ($score >= 80) {
    echo "良好";
} elseif ($score >= 60) {
    echo "及格";
} else {
    echo "不及格";
}

// switch
$day = "Monday";
switch ($day) {
    case "Monday":
        echo "星期一";
        break;
    case "Friday":
        echo "星期五";
        break;
    default:
        echo "其他";
}

// for 循环
for ($i = 0; $i < 10; $i++) {
    echo $i;
}

// while 循环
$i = 0;
while ($i < 10) {
    echo $i;
    $i++;
}

// do-while
$i = 0;
do {
    echo $i;
    $i++;
} while ($i < 10);

// foreach（数组遍历，最常用）
$fruits = ["apple", "banana", "orange"];
foreach ($fruits as $fruit) {
    echo $fruit;
}

// 带键的 foreach
$user = ["name" => "Alice", "age" => 25];
foreach ($user as $key => $value) {
    echo "$key: $value";
}
```

> **安全要点**：switch 使用松散比较（`==`），如果 case 是数字而 switch 表达式是字符串，可能出现意外匹配。例如 `switch("1abc") { case 1: echo "匹配了"; }` 会匹配成功。

### 2.4 函数

```php
// 基本函数
function add($a, $b) {
    return $a + $b;
}
echo add(3, 5);  // 8

// 默认参数
function greet($name = "World") {
    return "Hello, " . $name . "!";
}
echo greet();        // Hello, World!
echo greet("Alice"); // Hello, Alice!

// 类型声明（PHP 7+）
function multiply(int $a, int $b): int {
    return $a * $b;
}

// 可变参数
function sum(...$numbers) {
    $total = 0;
    foreach ($numbers as $n) {
        $total += $n;
    }
    return $total;
}
echo sum(1, 2, 3, 4, 5);  // 15

// 匿名函数（闭包）
$double = function($n) {
    return $n * 2;
};
echo $double(5);  // 10

// 箭头函数（PHP 7.4+）
$triple = fn($n) => $n * 3;
echo $triple(5);  // 15
```

### 2.5 数组

PHP 的数组是非常强大的哈希表（字典 + 数组混合体）。

```php
// 索引数组
$nums = [1, 2, 3, 4, 5];
echo $nums[0];  // 1

// 关联数组（键值对）
$user = [
    "name" => "Alice",
    "age" => 25,
    "email" => "alice@example.com"
];
echo $user["name"];  // Alice

// 多维数组
$users = [
    ["name" => "Alice", "age" => 25],
    ["name" => "Bob", "age" => 30]
];
echo $users[0]["name"];  // Alice

// 常用数组函数
count($nums);                // 数组长度
array_push($nums, 6);        // 末尾添加
array_pop($nums);            // 末尾删除
array_unshift($nums, 0);     // 开头添加
array_shift($nums);          // 开头删除
array_merge($a, $b);         // 合并数组
in_array("Alice", $user);    // 检查值是否存在
array_key_exists("name", $user); // 检查键是否存在
array_search("Alice", $user);    // 搜索值，返回键
sort($nums);                 // 排序
ksort($user);                // 按键排序
array_slice($nums, 0, 3);    // 截取子数组
array_map(function($n) { return $n * 2; }, $nums);  // 映射
array_filter($nums, function($n) { return $n > 2; }); // 过滤
```

> **安全要点**：
> - `in_array()` 默认使用松散比较（`==`），第三个参数设为 `true` 才是严格比较
> - `array_search()` 同样有松散比较问题
> - 用户可控的数组键可能导致覆盖变量（`$$` 变量覆盖、`extract()` 漏洞）

### 2.6 字符串操作

```php
$str = "Hello, World!";

// 基本操作
strlen($str);                  // 字符串长度
strpos($str, "World");         // 查找子串位置（从 0 开始）
str_replace("World", "PHP", $str); // 替换
substr($str, 0, 5);            // 截取子串
strtolower($str);              // 转小写
strtoupper($str);              // 转大写
trim($str);                    // 去除首尾空白
explode(",", "a,b,c");         // 分割为数组
implode("-", [1, 2, 3]);       // 数组合并为字符串
sprintf("%s is %d years old", "Alice", 25); // 格式化字符串

// 字符串拼接
$name = "Alice";
echo "Hello, $name!";          // 双引号内解析变量
echo 'Hello, ' . $name . '!';  // 单引号拼接（推荐，性能更好）
```

### 2.7 表单处理

```php
<?php
// 获取 GET 参数
$name = $_GET["name"] ?? "默认值";  // PHP 7+ null 合并运算符
$id = isset($_GET["id"]) ? $_GET["id"] : 0; // 旧写法

// 获取 POST 参数
$username = $_POST["username"] ?? "";
$password = $_POST["password"] ?? "";

// 获取请求参数（GET + POST + Cookie）
$action = $_REQUEST["action"] ?? "";  // ⚠️ 不推荐，来源不明确

// 文件上传
$uploaded_file = $_FILES["avatar"];
// $uploaded_file["name"]     文件名
// $uploaded_file["type"]     MIME 类型
// $uploaded_file["size"]     文件大小
// $uploaded_file["tmp_name"] 临时文件路径
// $uploaded_file["error"]    错误码

// 超全局变量汇总
$_GET;       // URL 查询参数
$_POST;      // POST 表单数据
$_REQUEST;   // GET + POST + Cookie（不推荐）
$_FILES;     // 上传的文件
$_SERVER;    // 服务器和执行环境信息
$_SESSION;   // Session 数据
$_COOKIE;    // Cookie 数据
$_ENV;       // 环境变量
$GLOBALS;    // 全局变量
```

> **安全要点**：
> - **永远不要信任用户输入**，所有 `$_GET`、`$_POST`、`$_COOKIE`、`$_SERVER` 等都可能被篡改
> - 输入必须验证和过滤
> - `$_REQUEST` 来源不明确，不推荐使用
> - 文件上传是高危操作，必须严格校验（见安全案例）

### 2.8 会话管理

```php
<?php
// 开启 Session（必须在输出之前调用）
session_start();

// 设置 Session 变量
$_SESSION["user_id"] = 123;
$_SESSION["username"] = "alice";
$_SESSION["is_login"] = true;

// 读取 Session
if (isset($_SESSION["is_login"]) && $_SESSION["is_login"]) {
    echo "欢迎, " . $_SESSION["username"];
} else {
    echo "请先登录";
}

// 销毁 Session
session_destroy();

// Cookie 操作
// 设置 Cookie（有效期 1 小时）
setcookie("remember_me", "1", time() + 3600, "/", "", true, true);
// 参数：名称、值、过期时间、路径、域、安全(HTTPS)、HttpOnly

// 读取 Cookie
$remember = $_COOKIE["remember_me"] ?? "0";

// 删除 Cookie（设置过期时间为过去）
setcookie("remember_me", "", time() - 3600, "/");
```

> **安全要点**：
> - Session 数据存在服务器端，相对安全，但 Session ID 如果被窃取就会导致会话劫持
> - Cookie 安全配置：`httponly`（防 XSS 窃取）、`secure`（仅 HTTPS 传输）、`SameSite`（防 CSRF）
> - 使用 `session_regenerate_id()` 防止会话固定攻击
> - 重要操作（修改密码、转账）需要二次验证

### 2.9 数据库操作

#### 危险方式：直接拼接 SQL（已废弃，仅用于理解漏洞）

```php
<?php
// ⚠️ 危险！SQL 注入漏洞
$conn = mysqli_connect("localhost", "user", "pass", "db");
$username = $_GET["username"];
$sql = "SELECT * FROM users WHERE username = '$username'";
$result = mysqli_query($conn, $sql);
// 攻击者输入: ' OR '1'='1 就能绕过登录
```

#### 安全方式 1：PDO 参数化查询（推荐）

```php
<?php
try {
    $pdo = new PDO(
        "mysql:host=localhost;dbname=mydb;charset=utf8mb4",
        "username",
        "password",
        [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_EMULATE_PREPARES => false, // 禁用模拟预处理，使用真正的预处理
        ]
    );

    // 参数化查询
    $stmt = $pdo->prepare("SELECT * FROM users WHERE id = :id");
    $stmt->execute(["id" => $_GET["id"] ?? 0]);
    $user = $stmt->fetch();

    // 查询多条
    $stmt = $pdo->prepare("SELECT * FROM users WHERE age > :age");
    $stmt->execute(["age" => 18]);
    $users = $stmt->fetchAll();

    // 插入
    $stmt = $pdo->prepare(
        "INSERT INTO users (username, email, age) VALUES (:username, :email, :age)"
    );
    $stmt->execute([
        "username" => "alice",
        "email" => "alice@example.com",
        "age" => 25
    ]);
    $new_id = $pdo->lastInsertId();

} catch (PDOException $e) {
    // 生产环境不要输出详细错误信息
    error_log("数据库错误: " . $e->getMessage());
    die("数据库错误，请稍后重试");
}
```

#### 安全方式 2：MySQLi 预处理

```php
<?php
$conn = new mysqli("localhost", "user", "pass", "db");
if ($conn->connect_error) {
    die("连接失败");
}

$stmt = $conn->prepare("SELECT * FROM users WHERE username = ? AND age > ?");
$stmt->bind_param("si", $username, $age);  // s=string, i=int

$username = $_GET["username"] ?? "";
$age = intval($_GET["age"] ?? 0);

$stmt->execute();
$result = $stmt->get_result();
while ($row = $result->fetch_assoc()) {
    // 处理每一行
}

$stmt->close();
$conn->close();
```

> **安全要点**：
> - **永远使用参数化查询（Prepared Statements）**，不要拼接 SQL
> - PDO 是更好的选择，跨数据库、API 更友好
> - 设置 `ATTR_EMULATE_PREPARES => false` 确保真正的预处理
> - 生产环境不要显示详细的数据库错误信息
> - 数据库账号使用最小权限原则

### 2.10 文件操作

```php
<?php
// 文件读取
$content = file_get_contents("data.txt");  // 整个文件读入字符串
$lines = file("data.txt");                 // 按行读入数组

// fopen 方式（更灵活）
$fp = fopen("data.txt", "r");
if ($fp) {
    while (($line = fgets($fp)) !== false) {
        echo $line;
    }
    fclose($fp);
}

// 文件写入
file_put_contents("data.txt", "Hello, World!");  // 覆盖写入
file_put_contents("data.txt", "追加内容\n", FILE_APPEND);  // 追加

// 检查文件
file_exists("data.txt");    // 文件是否存在
is_file("data.txt");        // 是否为文件
is_dir("data");             // 是否为目录
filesize("data.txt");       // 文件大小
filemtime("data.txt");      // 最后修改时间

// 目录操作
$files = scandir("./");     // 列出目录内容
mkdir("new_dir");           // 创建目录
rmdir("empty_dir");         // 删除空目录
unlink("file.txt");         // 删除文件

// ⚠️ 文件包含（危险函数！）
// include "header.php";     // 包含，失败警告
// require "header.php";     // 包含，失败致命错误
// include_once "lib.php";   // 只包含一次
// require_once "config.php";// 只包含一次
```

> **安全要点**：
> - 文件包含是 PHP 经典高危漏洞：如果包含路径可控，可能导致 RCE
> - `allow_url_include = Off` 禁止远程文件包含
> - 包含文件使用固定路径，不要用用户输入拼接

---

## 三、PHP 安全核心用法

### 3.1 常见 PHP 漏洞类型

| 漏洞类型 | 严重程度 | 典型成因 | 防御方法 |
|---------|---------|---------|---------|
| **SQL 注入** | 🔴 极高 | 拼接 SQL 语句 | 参数化查询 |
| **XSS（跨站脚本）** | 🔴 高 | 输出未转义 | 输出编码、CSP |
| **文件包含** | 🔴 极高 | 包含路径可控 | 白名单、固定路径 |
| **文件上传** | 🔴 极高 | 上传校验不严 | 白名单、重命名、随机路径 |
| **命令执行** | 🔴 极高 | 危险函数 + 可控参数 | 避免使用、escapeshellarg |
| **反序列化** | 🔴 极高 | 反序列化不可信数据 | 避免反序列化用户输入 |
| **CSRF** | 🟠 中 | 无 Token 验证 | CSRF Token |
| **SSRF** | 🟠 中 | 请求地址可控 | 白名单、协议限制 |
| **变量覆盖** | 🟡 中 | extract()、$$ | 避免使用 extract |
| **弱类型比较** | 🟡 中 | == 松散比较 | 使用 === |
| **XXE** | 🟠 中 | XML 解析未禁用外部实体 | 禁用外部实体 |

### 3.2 危险函数清单

#### 命令执行类

| 函数 | 说明 | 危险等级 |
|------|------|---------|
| `eval()` | 执行字符串作为 PHP 代码 | 🔴 极高 |
| `assert()` | 断言（PHP 7.2 前可执行代码） | 🔴 高 |
| `system()` | 执行系统命令并输出 | 🔴 极高 |
| `exec()` | 执行系统命令，返回最后一行 | 🔴 极高 |
| `shell_exec()` | 执行命令，返回全部输出 | 🔴 极高 |
| `passthru()` | 执行命令并直接输出原始输出 | 🔴 极高 |
| `popen()` / `proc_open()` | 打开进程 | 🔴 极高 |
| `` `...` ``（反引号） | 同 shell_exec | 🔴 极高 |
| `pcntl_exec()` | 执行指定程序 | 🔴 高 |

#### 文件包含类

| 函数 | 说明 | 危险等级 |
|------|------|---------|
| `include()` | 包含文件 | 🔴 极高 |
| `require()` | 包含文件（失败报错） | 🔴 极高 |
| `include_once()` | 包含一次 | 🔴 高 |
| `require_once()` | 包含一次 | 🔴 高 |

#### 文件操作类

| 函数 | 说明 | 危险等级 |
|------|------|---------|
| `file_get_contents()` | 读取文件内容 | 🟠 中 |
| `readfile()` | 读取并输出文件 | 🟠 中 |
| `fopen()` | 打开文件 | 🟠 中 |
| `file_put_contents()` | 写入文件 | 🟠 中 |
| `unlink()` | 删除文件 | 🟠 中 |
| `move_uploaded_file()` | 移动上传文件 | 🔴 高（配合上传漏洞） |

#### 其他危险函数

| 函数 | 说明 | 危险等级 |
|------|------|---------|
| `unserialize()` | 反序列化 | 🔴 极高 |
| `extract()` | 导入数组为变量 | 🟠 中（变量覆盖） |
| `parse_str()` | 解析字符串为变量 | 🟠 中（变量覆盖） |
| `$$`（可变变量） | 动态变量名 | 🟠 中（变量覆盖） |
| `call_user_func()` | 调用回调函数 | 🔴 高 |
| `call_user_func_array()` | 调用回调函数（数组参数） | 🔴 高 |
| `preg_replace()` /e 修饰符 | 替换时执行 PHP 代码 | 🔴 极高（PHP 7.0 移除） |

### 3.3 SQL 注入防护

```php
<?php
// ✅ 正确做法：PDO 参数化查询
$pdo = new PDO("mysql:host=localhost;dbname=test;charset=utf8mb4", "user", "pass", [
    PDO::ATTR_EMULATE_PREPARES => false,  // 禁用模拟预处理
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
]);

$stmt = $pdo->prepare("SELECT * FROM users WHERE id = ?");
$stmt->execute([$_GET["id"] ?? 0]);
$user = $stmt->fetch();

// ✅ 正确做法：整数类型强制转换
$id = intval($_GET["id"] ?? 0);
$sql = "SELECT * FROM users WHERE id = $id";  // 整数可以拼接（但还是推荐参数化）

// ✅ 正确做法：LIKE 查询也要参数化
$keyword = "%" . $_GET["keyword"] . "%";
$stmt = $pdo->prepare("SELECT * FROM users WHERE username LIKE ?");
$stmt->execute([$keyword]);

// ❌ 错误做法：直接拼接
// $sql = "SELECT * FROM users WHERE username = '" . $_GET["username"] . "'";
```

### 3.4 XSS 防护

```php
<?php
// ✅ 输出到 HTML 时用 htmlspecialchars 转义
$username = $_GET["name"] ?? "";
echo "欢迎, " . htmlspecialchars($username, ENT_QUOTES, "UTF-8");

// ✅ 封装成函数更方便
function e($str): string {
    return htmlspecialchars($str, ENT_QUOTES, "UTF-8");
}

// 模板中使用
// <h1>欢迎, <?= e($username) ?></h1>

// ✅ 输出到 JavaScript 时用 json_encode
$user_data = ["name" => $username, "age" => 25];
echo "<script>var user = " . json_encode($user_data) . ";</script>";

// ✅ 输出到 URL 时用 urlencode
$url = "/search?q=" . urlencode($keyword);

// ✅ HTTP 安全头
header("Content-Security-Policy: default-src 'self'; script-src 'self'");
header("X-Content-Type-Options: nosniff");
header("X-Frame-Options: DENY");
header("X-XSS-Protection: 1; mode=block");
```

### 3.5 文件上传防护

```php
<?php
function safe_upload(array $file): string|false {
    // 1. 检查上传错误
    if ($file["error"] !== UPLOAD_ERR_OK) {
        return false;
    }

    // 2. 检查文件大小
    $max_size = 2 * 1024 * 1024;  // 2MB
    if ($file["size"] > $max_size) {
        return false;
    }

    // 3. 白名单校验扩展名
    $allowed_ext = ["jpg", "jpeg", "png", "gif"];
    $ext = strtolower(pathinfo($file["name"], PATHINFO_EXTENSION));
    if (!in_array($ext, $allowed_ext, true)) {
        return false;
    }

    // 4. 检查 MIME 类型（辅助校验，不可单独依赖）
    $finfo = new Finfo(FILEINFO_MIME_TYPE);
    $mime_type = $finfo->file($file["tmp_name"]);
    $allowed_mime = ["image/jpeg", "image/png", "image/gif"];
    if (!in_array($mime_type, $allowed_mime, true)) {
        return false;
    }

    // 5. 检查文件头（图片文件的魔术字节）
    // 对图片可以用 getimagesize 验证
    $image_info = @getimagesize($file["tmp_name"]);
    if (!$image_info) {
        return false;
    }

    // 6. 随机文件名，避免覆盖和路径遍历
    $new_filename = uniqid() . "." . $ext;
    $upload_dir = __DIR__ . "/uploads/";

    // 7. 上传目录不能在 Web 可执行路径，或禁止脚本执行
    $dest = $upload_dir . $new_filename;
    if (move_uploaded_file($file["tmp_name"], $dest)) {
        return $new_filename;
    }

    return false;
}
```

### 3.6 反序列化防护

```php
<?php
// ⚠️ 反序列化用户输入是极度危险的！
// unserialize($_GET["data"]);  // 绝对不要这么做！

// ✅ 安全替代方案：使用 JSON
$data = json_decode($_GET["data"] ?? "{}", true);
// JSON 只能解析数据，不会执行代码或实例化对象

// ✅ 如果必须使用序列化（不推荐），使用白名单限制类
// PHP 7+ 支持 allowed_classes
$data = unserialize(
    $_GET["data"] ?? "",
    ["allowed_classes" => ["User", "Product"]]  // 只允许这些类
);

// ✅ 更好的做法：完全避免反序列化不可信数据
// 使用 JSON、XML（禁用外部实体）、Protobuf 等数据格式
```

> **PHP 反序列化漏洞原理**：当 `unserialize()` 接受用户可控的输入时，攻击者可以构造特定的序列化数据，实例化任意类。如果类中有 `__wakeup()`、`__destruct()`、`__toString()` 等魔术方法，并且这些方法中包含危险操作，就可能导致远程代码执行。这就是所谓的 **POP 链（Property-Oriented Programming）**。

### 3.7 命令执行防护

```php
<?php
// ❌ 危险：直接把用户输入拼接到命令中
// system("ping " . $_GET["ip"]);  // 攻击者注入 ; rm -rf /

// ✅ 安全做法 1：完全避免执行系统命令
// 用 PHP 内置函数替代

// ✅ 安全做法 2：如果必须执行，严格白名单
$allowed_commands = ["ls", "pwd", "whoami"];
$cmd = $_GET["cmd"] ?? "";
if (in_array($cmd, $allowed_commands, true)) {
    system($cmd);
}

// ✅ 安全做法 3：参数用 escapeshellarg 转义
$ip = $_GET["ip"] ?? "";
if (filter_var($ip, FILTER_VALIDATE_IP)) {  // 先验证格式
    $safe_ip = escapeshellarg($ip);
    system("ping -c 1 " . $safe_ip);
}

// ✅ 安全做法 4：用 escapeshellcmd 转义整个命令（弱一些）
$command = escapeshellcmd($_GET["cmd"] ?? "");
system($command);
```

### 3.8 PHP 安全配置（php.ini）

```ini
; 安全模式（PHP 5.4 已移除，仅作历史参考）
safe_mode = Off

; 禁止远程文件包含（必须关）
allow_url_include = Off
allow_url_fopen = On  ; 按需，一般开着就行

; 禁用危险函数（按需配置）
disable_functions = eval,assert,system,exec,shell_exec,passthru,popen,proc_open

; 隐藏 PHP 版本
expose_php = Off

; 错误显示（生产环境关闭）
display_errors = Off
log_errors = On
error_log = /var/log/php/error.log

; 打开 basedir 限制（限制 PHP 只能访问指定目录）
open_basedir = /var/www/html/:/tmp/

; Session 安全
session.cookie_httponly = On
session.cookie_secure = On   ; HTTPS 网站开启
session.cookie_samesite = "Strict"
session.use_strict_mode = On

; 文件上传限制
file_uploads = On
upload_max_filesize = 2M
max_file_uploads = 20
```

---

## 四、常用工具与扩展

### 4.1 调试与开发

| 工具 | 用途 | 说明 |
|------|------|------|
| **Xdebug** | PHP 调试扩展 | 断点调试、性能分析，IDE 集成 |
| **PhpStorm** | IDE | JetBrains 出品，功能强大（商业） |
| **VS Code + PHP Intelephense** | 编辑器 + 插件 | 免费、轻量 |

### 4.2 静态分析与代码质量

| 工具 | 用途 | 说明 |
|------|------|------|
| **PHPStan** | 静态分析 | 发现代码中的潜在问题，支持自定义规则 |
| **Psalm** | 静态分析 | 另一个优秀的 PHP 静态分析工具 |
| **PHP_CodeSniffer** | 代码规范检查 | 检查代码是否符合 PSR 等规范 |
| **RIPS** | PHP 安全静态分析 | 专业的 PHP 漏洞静态扫描（开源版可用） |
| **Semgrep** | 通用静态分析 | 支持 PHP，有很多安全规则集 |
| **PHPCS Security Audit** | 安全审计规则 | PHP_CodeSniffer 的安全规则集 |

```bash
# PHPStan
composer require --dev phpstan/phpstan
vendor/bin/phpstan analyse src/ --level=max

# Psalm
composer require --dev vimeo/psalm
vendor/bin/psalm

# PHP_CodeSniffer
composer require --dev squizlabs/php_codesniffer
vendor/bin/phpcs --standard=PSR12 src/
```

### 4.3 依赖管理

| 工具 | 用途 | 说明 |
|------|------|------|
| **Composer** | PHP 依赖管理 | PHP 标准包管理器，类似 npm/pip |
| **Packagist** | PHP 包仓库 | 官方 Composer 包仓库 |
| **composer audit** | 漏洞检查 | 检查依赖中的已知漏洞 |
| **SensioLabs Security Checker** | 安全检查 | 检查 Composer 依赖的安全公告 |

```bash
# 初始化项目
composer init

# 安装依赖
composer require monolog/monolog
composer require --dev phpunit/phpunit

# 更新依赖
composer update

# 检查依赖漏洞
composer audit
```

### 4.4 测试工具

| 工具 | 用途 | 说明 |
|------|------|------|
| **PHPUnit** | 单元测试 | PHP 标准测试框架 |
| **Laravel Dusk** | 浏览器测试 | Laravel 生态 |
| **PHP-SecLib** | 安全库 | 加密、SSH、SFTP 等安全功能 |

---

## 五、2026 年免费学习资源

| 资源 | 类型 | 说明 | 链接/获取方式 |
|------|------|------|--------------|
| **国家高等教育智慧教育平台 PHP 课程** | 在线课程 | PHP 动态 Web 开发课程，系统讲解动态 Web 项目开发流程 | 智慧教育平台搜索 "PHP" |
| **Educative — PHP Tutorial** | 在线教程 | 从零开始学习 PHP，交互式免费课程 | Educative 官网搜索 PHP |
| **Simplilearn — Free PHP Course** | 视频课程 | 7 小时自定进度视频，90 天访问权 | Simplilearn 官网 |
| **PHP 官方手册** | 参考文档 | 最权威的 PHP 参考，中文翻译完善 | [php.net/manual/zh/](https://www.php.net/manual/zh/) |
| **W3Schools PHP Tutorial** | 入门教程 | 经典入门教程，有在线编辑器 | [w3schools.com/php](https://www.w3schools.com/php/) |
| **PHP: The Right Way** | 最佳实践 | PHP 最佳实践指南，中文化 | [laravel-china.github.io/php-the-right-way](https://laravel-china.github.io/php-the-right-way/) |
| **Codecademy PHP Course** | 交互式课程 | 交互式学习 PHP 基础 | Codecademy 官网 |
| **OWASP PHP Security Cheat Sheet** | 安全速查 | PHP 安全编码速查表 | OWASP 官网 |

> **2026 年时效性标注**：PHP 8.x 是当前主流版本，PHP 7 已停止维护。学习资源以 PHP 8 为主，但安全研究中仍需了解 PHP 5/7 的特性（大量遗留系统仍在使用）。

---

## 六、2026 年推荐 GitHub 项目

| 项目 | Stars（约） | 说明 | 适用场景 |
|------|------------|------|---------|
| **SrikantAich/PHP** | 学习级 | PHP 编程基础学习仓库，涵盖变量、数组、控制结构等核心概念 | PHP 入门练习 |
| **hexlet-basics/exercises-php** | 数百+ | 免费 PHP 课程练习，Hexlet 出品 | PHP 基础练习 |
| **EbookFoundation/free-programming-books** | 30万+ | 免费编程书籍大全，含 PHP 资源 | 资源索引 |
| **laravel/framework** | 数万+ | 最流行的 PHP Web 框架 | Web 开发、框架学习 |
| **symfony/symfony** | 数万+ | 另一个优秀的 PHP 框架，组件化 | 企业级开发 |
| **WordPress/WordPress** | 数万+ | WordPress 源码 | CMS 安全研究、代码审计 |
| **kaloz/webshell** | 数千级 | WebShell 收集与分析（学习研究用） | WebShell 分析研究 |
| **Firebasky/PHP_disable_functions** | 数百+ | PHP disable_functions 绕过研究 | 安全研究、提权 |
| **snoopysecurity/awesome-php-security** | 数千+ | PHP 安全资源大全 | 资源索引 |

> **⚠️ 免责声明**：以上 GitHub 项目仅供学习研究使用。漏洞利用相关内容**仅限在完全授权的测试环境中使用**。未经授权对任何系统进行测试可能违反法律。学习者应重点关注漏洞原理和防御方法，以及如何编写安全的代码。

---

## 七、示例代码文件

`code/` 目录下包含两个 PHP 示例程序：

| 文件 | 内容 | 运行方式 |
|------|------|---------|
| `basics.php` | PHP 基础语法示例：变量、数据类型、流程控制、函数、数组、表单处理、Session、数据库操作 | `php basics.php` 或浏览器访问 |
| `security_cases.php` | 安全案例集：SQL 注入防御、XSS 输入净化、文件上传白名单校验、反序列化安全、CSRF 防护 | `php security_cases.php` 或浏览器访问 |

### 7.1 basics.php 内容概览

- 变量与数据类型（弱类型特点与安全注意）
- 运算符与比较（`==` vs `===` 的区别）
- 流程控制（if/switch/for/foreach/while）
- 函数（普通函数、默认参数、类型声明、可变参数）
- 数组（索引数组、关联数组、常用函数）
- 字符串操作
- 表单处理（GET/POST/文件上传）
- Session 与 Cookie
- 数据库操作（PDO 参数化查询）

### 7.2 security_cases.php 内容概览

| 案例 | 功能 | 说明 |
|------|------|------|
| **SQL 注入防御** | PDO 参数化查询 + 危险版本对比 | 理解 SQL 注入原理，掌握参数化查询 |
| **XSS 防护** | 输出编码 + 输入验证 + CSP 头 | 理解 XSS 原理，掌握转义和安全头配置 |
| **文件上传安全** | 白名单扩展名 + MIME 校验 + 文件头检查 + 随机文件名 | 理解上传漏洞，掌握多层校验 |
| **反序列化安全** | JSON 替代 + 白名单类限制 | 理解反序列化漏洞，掌握安全替代方案 |
| **CSRF 防护** | Token 验证机制 | 理解 CSRF 原理，掌握 Token 防护 |

> **运行注意**：
> - 需要 PHP 7.4+ 环境（推荐 PHP 8.x）
> - 命令行运行：`php basics.php`
> - 浏览器访问：`php -S 127.0.0.1:8000` 然后访问 `http://127.0.0.1:8000/security_cases.php`
> - 数据库案例需要配置数据库连接（默认为演示模式）

---

## 附：PHP 安全编码检查清单

### 输入验证

- [ ] 所有外部输入都进行验证（`$_GET`、`$_POST`、`$_COOKIE`、`$_SERVER`、上传文件）
- [ ] 使用白名单验证，而非黑名单
- [ ] 验证数据类型、长度、范围、格式
- [ ] 整数使用 `intval()` 或类型声明
- [ ] 邮箱使用 `filter_var($email, FILTER_VALIDATE_EMAIL)`
- [ ] URL 使用 `filter_var($url, FILTER_VALIDATE_URL)`
- [ ] IP 使用 `filter_var($ip, FILTER_VALIDATE_IP)`

### 数据库安全

- [ ] 所有数据库查询使用参数化查询（PDO prepared statements）
- [ ] 禁用模拟预处理（`ATTR_EMULATE_PREPARES => false`）
- [ ] 数据库账号使用最小权限
- [ ] 生产环境不显示数据库错误信息
- [ ] 敏感数据加密存储（密码用 password_hash）

### 输出安全

- [ ] 输出到 HTML 使用 `htmlspecialchars()` 转义
- [ ] 输出到 JavaScript 使用 `json_encode()`
- [ ] 输出到 URL 使用 `urlencode()`
- [ ] 设置正确的 Content-Type 和 charset
- [ ] 配置 CSP（Content-Security-Policy）响应头

### 文件上传安全

- [ ] 白名单校验扩展名
- [ ] 校验 MIME 类型（辅助）
- [ ] 校验文件内容/文件头
- [ ] 文件大小限制
- [ ] 随机生成文件名
- [ ] 上传目录禁止脚本执行
- [ ] 上传目录不在 Web 根目录内更好

### 会话安全

- [ ] 使用 `session_start()` 开启会话
- [ ] 登录后调用 `session_regenerate_id()`
- [ ] Cookie 设置 `httponly`
- [ ] HTTPS 站点设置 `secure`
- [ ] 设置 `SameSite` 属性
- [ ] 会话超时机制
- [ ] 重要操作二次验证

### 其他安全配置

- [ ] `expose_php = Off` 隐藏 PHP 版本
- [ ] `display_errors = Off` 生产环境关闭错误显示
- [ ] `allow_url_include = Off` 禁止远程文件包含
- [ ] `disable_functions` 禁用不必要的危险函数
- [ ] `open_basedir` 限制文件访问范围
- [ ] Composer 依赖定期更新并检查漏洞
- [ ] PHP 版本保持更新，使用受支持的版本

---

> **免责声明**：本文档所有内容仅用于学习、研究和授权环境下的安全测试与防御实践。任何未经授权的测试或攻击行为均属违法。读者应遵守所在地区法律法规，对自己的行为负责。
