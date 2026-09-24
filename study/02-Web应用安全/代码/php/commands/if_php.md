# if_php

> **分类**：条件与循环
> **说明**：条件判断和循环语句

---

## 语法

```php
if/else/elseif/switch/while/for/foreach/do...while
```

## 示例代码

```php
<?php
// if/else
$age = 18;
if ($age >= 18) {
    echo "成年";
} elseif ($age >= 6) {
    echo "少年";
} else {
    echo "儿童";
}

// switch
$day = "Monday";
switch ($day) {
    case "Monday":
        echo "星期一";
        break;
    case "Tuesday":
        echo "星期二";
        break;
    default:
        echo "其他";
}

// match 表达式 (PHP 8+)
$result = match($day) {
    "Monday" => "星期一",
    "Tuesday" => "星期二",
    default => "其他"
};

// for 循环
for ($i = 0; $i < 5; $i++) {
    echo $i;
}

// while 循环
$i = 0;
while ($i < 5) {
    echo $i;
    $i++;
}

// do...while
$i = 0;
do {
    echo $i;
    $i++;
} while ($i < 5);

// foreach
$fruits = ["apple", "banana", "cherry"];
foreach ($fruits as $fruit) {
    echo $fruit;
}

foreach ($person as $key => $value) {
    echo "$key: $value";
}

// break / continue
for ($i = 0; $i < 10; $i++) {
    if ($i == 3) continue;  // 跳过3
    if ($i == 7) break;     // 停止
    echo $i;
}

// 三元运算符
$status = $loggedIn ? "已登录" : "未登录";

// null 合并运算符 (PHP 7+)
$value = $_GET['key'] ?? "默认值";

// null 合并赋值 (PHP 7.4+)
$user['name'] ??= "默认名";

// 太空船运算符 (PHP 7+)
$result = $a <=> $b;  // -1, 0, 或 1
```
