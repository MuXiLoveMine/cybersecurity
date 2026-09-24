# 第六章：PHP 基础

> PHP 详细内容和代码示例请查看 `php/PHP基础.md` 和 `php/` 目录中的示例文件。

### 6.1 PHP 简介

PHP（PHP: Hypertext Preprocessor）是一种广泛使用的开源脚本语言，特别适合 Web 开发，可以嵌入到 HTML 中。

**特点**：
- 语法简单，上手快
- 与 HTML 混编方便
- 数据库支持丰富（MySQL 最佳拍档）
- 跨平台
- 开源免费

### 6.2 PHP 基本语法

```php
<?php
// 这是单行注释
/* 这是多行注释 */

// 输出
echo "Hello, World!";
print "Hello";

// 变量（以 $ 开头）
$name = "张三";
$age = 25;

// 字符串拼接（用点号）
echo "姓名: " . $name . ", 年龄: " . $age;

// 双引号内解析变量
echo "姓名: $name, 年龄: $age";

// 数组
$fruits = array("apple", "banana", "cherry");
$fruits = ["apple", "banana", "cherry"];  // PHP 5.4+

// 关联数组（字典）
$person = [
    "name" => "张三",
    "age" => 25,
    "city" => "北京"
];
echo $person["name"];

// 条件判断
if ($age >= 18) {
    echo "成年";
} elseif ($age >= 13) {
    echo "青少年";
} else {
    echo "儿童";
}

// 循环
for ($i = 0; $i < 5; $i++) {
    echo $i;
}

foreach ($fruits as $fruit) {
    echo $fruit;
}

foreach ($person as $key => $value) {
    echo "$key: $value";
}

// 函数
function add($a, $b) {
    return $a + $b;
}
echo add(3, 5);
?>
```

### 6.3 PHP 与 HTML 混编

```php
<!-- index.php -->
<!DOCTYPE html>
<html>
<head>
    <title>PHP 示例</title>
</head>
<body>
    <h1>欢迎，<?php echo $name; ?>！</h1>
    <p>当前时间：<?php echo date("Y-m-d H:i:s"); ?></p>

    <ul>
        <?php foreach ($fruits as $fruit): ?>
            <li><?php echo $fruit; ?></li>
        <?php endforeach; ?>
    </ul>

    <!-- 短标签（需配置开启） -->
    <p><?= "短输出标签" ?></p>
</body>
</html>
```

### 6.4 PHP 表单处理

```php
<?php
// login.php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $username = $_POST["username"];
    $password = $_POST["password"];

    // 处理登录逻辑...
    echo "用户名: " . htmlspecialchars($username);
}

// GET 参数
$page = $_GET["page"] ?? 1;

// 服务器信息
echo $_SERVER["PHP_SELF"];       // 当前脚本路径
echo $_SERVER["HTTP_USER_AGENT"]; // 用户代理
echo $_SERVER["REMOTE_ADDR"];     // 客户端 IP
?>
```

### 6.5 PHP 操作 MySQL

```php
<?php
// MySQLi 面向过程方式
$conn = mysqli_connect("localhost", "root", "password", "testdb");

if (!$conn) {
    die("连接失败: " . mysqli_connect_error());
}

// 查询
$sql = "SELECT id, name, age FROM users";
$result = mysqli_query($conn, $sql);

if (mysqli_num_rows($result) > 0) {
    while ($row = mysqli_fetch_assoc($result)) {
        echo "id: " . $row["id"] . " 姓名: " . $row["name"] . "<br>";
    }
}

// 插入
$sql = "INSERT INTO users (name, age) VALUES ('张三', 25)";
if (mysqli_query($conn, $sql)) {
    echo "新记录插入成功，ID: " . mysqli_insert_id($conn);
}

// 防止 SQL 注入：预处理语句
$stmt = mysqli_prepare($conn, "INSERT INTO users (name, age) VALUES (?, ?)");
mysqli_stmt_bind_param($stmt, "si", $name, $age);
$name = "李四";
$age = 30;
mysqli_stmt_execute($stmt);

mysqli_close($conn);
?>
```

> **安全提示**：必须使用预处理语句（Prepared Statement）来防止 SQL 注入，绝不能直接拼接用户输入到 SQL 语句中。

### 6.6 PHP 超全局变量

| 超全局变量 | 说明 |
|-----------|------|
| `$GLOBALS` | 全局变量数组 |
| `$_SERVER` | 服务器和环境信息 |
| `$_GET` | GET 请求参数 |
| `$_POST` | POST 请求参数 |
| `$_REQUEST` | GET + POST + Cookie |
| `$_COOKIE` | Cookie 数据 |
| `$_SESSION` | Session 数据 |
| `$_FILES` | 上传的文件信息 |
| `$_ENV` | 环境变量 |

---

---

