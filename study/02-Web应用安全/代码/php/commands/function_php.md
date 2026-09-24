# function_php

> **分类**：函数
> **说明**：函数定义与使用

---

## 语法

```php
function funcName($param1, $param2 = default) { ... return $value; }
```

## 特性

- 默认参数
- 可变参数
- 类型声明
- 返回值类型
- 匿名函数
- 箭头函数

## 示例代码

```php
<?php
// 基本函数
function add($a, $b) {
    return $a + $b;
}
echo add(2, 3);  // 5

// 默认参数
function greet($name = "World") {
    return "Hello, $name!";
}
echo greet();         // Hello, World!
echo greet("Alice");  // Hello, Alice!

// 可变参数
function sumAll(...$numbers) {
    return array_sum($numbers);
}
echo sumAll(1, 2, 3, 4);  // 10

// 类型声明（PHP 7+）
function multiply(int $a, int $b): int {
    return $a * $b;
}

// 严格模式（文件开头声明）
// declare(strict_types=1);

// 引用参数
function addOne(int &$n) {
    $n++;
}
$x = 5;
addOne($x);
echo $x;  // 6

// 匿名函数
$double = function($n) {
    return $n * 2;
};
echo $double(5);  // 10

// 箭头函数 (PHP 7.4+)
$triple = fn($n) => $n * 3;
echo $triple(5);  // 15

// use 闭包
$factor = 2;
$multiply = function($n) use ($factor) {
    return $n * $factor;
};

// 可变函数
$funcName = "add";
echo $funcName(2, 3);  // 调用 add 函数

// 递归函数
function factorial($n) {
    if ($n <= 1) return 1;
    return $n * factorial($n - 1);
}
```
