# echo

> **分类**：输出
> **说明**：输出一个或多个字符串

---

## 语法

```php
echo(string ...$expressions): void
```

## 区别对比

echo - 语言结构，无返回值，快\nprint - 语言结构，返回1\nprint_r - 打印变量（数组等）\nvar_dump - 打印变量详细信息（类型+值）

## 示例代码

```php
<?php
// 基本输出
echo "Hello, World!";
echo "Hello", " ", "World!";  // 多个参数

// 变量输出
$name = "Alice";
echo "你好, $name!";         // 双引号内解析变量
echo '你好, ' . $name . '!';  // 字符串拼接

// HTML 输出
echo "<h1>标题</h1>";
echo "<p>段落</p>";

// 数组输出（调试用）
$arr = [1, 2, 3];
print_r($arr);    // 简单输出
var_dump($arr);   // 详细信息（类型+长度+值）
var_export($arr); // 可执行的 PHP 代码格式

// 条件输出
$loggedIn = true;
echo $loggedIn ? "已登录" : "未登录";

// 短标签（需启用 short_open_tag）
// <?= $variable ?>
```
