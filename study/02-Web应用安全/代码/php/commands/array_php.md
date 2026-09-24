# array_php

> **分类**：数组
> **说明**：PHP 数组功能强大，既是数组也是字典

---

## 语法

```php
$arr = [key => value, ...]; 或 array(...)
```

## 常用函数

- count
- push
- pop
- shift
- unshift
- slice
- splice
- merge
- keys
- values
- sort
- rsort
- asort
- ksort
- array_filter
- array_map
- array_reduce
- in_array
- array_search

## 示例代码

```php
<?php
// 索引数组
$fruits = ["apple", "banana", "cherry"];
echo $fruits[0];  // "apple"

// 关联数组
$person = [
    "name" => "Alice",
    "age" => 25,
    "city" => "Beijing"
];
echo $person["name"];  // "Alice"

// 多维数组
$matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
];
echo $matrix[1][2];  // 6

// 常用函数
count($arr);                // 元素个数
array_push($arr, "new");    // 末尾添加
array_pop($arr);            // 末尾弹出
array_unshift($arr, "x");   // 开头添加
array_shift($arr);          // 开头弹出

// 数组操作
$keys = array_keys($arr);     // 所有键
$values = array_values($arr); // 所有值
$merged = array_merge($a, $b); // 合并
$slice = array_slice($arr, 1, 2); // 切片
array_splice($arr, 1, 2, $replacement); // 替换

// 查找
in_array("apple", $fruits);     // 是否包含
array_search("apple", $fruits); // 查找键
array_key_exists("name", $person); // 键是否存在

// 排序
sort($arr);       // 升序（索引重排）
rsort($arr);      // 降序
asort($arr);      // 升序（保留键关联）
arsort($arr);     // 降序
ksort($arr);      // 按键升序
krsort($arr);     // 按键降序
usort($arr, $cmpFunc); // 自定义排序

// 过滤与映射
$evens = array_filter($nums, fn($n) => $n % 2 == 0);
$squares = array_map(fn($n) => $n * $n, $nums);
$sum = array_reduce($nums, fn($acc, $n) => $acc + $n, 0);

// 遍历
foreach ($fruits as $fruit) {
    echo $fruit;
}

foreach ($person as $key => $value) {
    echo "$key: $value";
}

// 数组合并运算符 (PHP 7.4+)
$combined = $a + $b;  // 键相同则保留 $a 的

// 展开运算符 (PHP 7.4+)
$arr1 = [1, 2, 3];
$arr2 = [...$arr1, 4, 5];  // [1, 2, 3, 4, 5]

// 数组解构
[$a, $b, $c] = [1, 2, 3];
["name" => $name, "age" => $age] = $person;
```
