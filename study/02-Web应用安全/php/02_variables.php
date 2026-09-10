<?php
// 02_variables.php
// 变量与数据类型

$name = "张三";
$age = 25;
$height = 1.75;
$is_student = true;

echo "<h2>变量定义</h2>";
echo "姓名: $name<br>";
echo "年龄: $age<br>";
echo "身高: $height<br>";
echo "是否学生: ";
var_dump($is_student);
echo "<br>";

// 可变变量
$foo = "bar";
$$foo = "hello";
echo "可变变量: ";
echo '$bar = ' . $bar . "<br>";

echo "<h2>常量</h2>";
define("PI", 3.14159);
echo "PI = " . PI . "<br>";

const MAX_SIZE = 1024;
echo "MAX_SIZE = " . MAX_SIZE . "<br>";

echo "<h2>运算符</h2>";
$x = 10;
$y = 3;
echo "x = $x, y = $y<br>";
echo "加法: " . ($x + $y) . "<br>";
echo "减法: " . ($x - $y) . "<br>";
echo "乘法: " . ($x * $y) . "<br>";
echo "除法: " . ($x / $y) . "<br>";
echo "取余: " . ($x % $y) . "<br>";

echo "<h3>比较运算</h3>";
echo '5 == "5": ';
var_dump(5 == "5");
echo "<br>";
echo '5 === "5": ';
var_dump(5 === "5");
echo "<br>";
echo '0 == "abc": ';
var_dump(0 == "abc");
echo "<br>";
?>
