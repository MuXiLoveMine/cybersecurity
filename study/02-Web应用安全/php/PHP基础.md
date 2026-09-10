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
