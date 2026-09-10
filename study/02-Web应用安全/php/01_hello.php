<?php
// 01_hello.php
// 第一个 PHP 程序

echo "Hello, World!";
echo "<br>";

// 多种输出方式
$name = "张三";
$age = 25;

echo "姓名: " . $name . ", 年龄: " . $age;
echo "<br>";
echo "姓名: $name, 年龄: $age";
echo "<br>";

// print 输出
print "这是 print 输出";
echo "<br>";

// 带 HTML
echo "<h1>PHP 入门</h1>";
echo "<p style='color: red;'>红色文字</p>";
echo "<br>";

// 打印变量信息
$arr = [1, 2, 3];
echo "<pre>";
print_r($arr);
echo "</pre>";

echo "<pre>";
var_dump($name, $age, $arr);
echo "</pre>";
?>
