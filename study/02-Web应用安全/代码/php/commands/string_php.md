# string_php

> **分类**：字符串
> **说明**：常用字符串处理函数

---

## 语法

```php
strlen/strpos/substr/str_replace/trim/explode/implode/strtolower/strtoupper/htmlspecialchars/md5/sha1
```

## 示例代码

```php
<?php
// 长度
$len = strlen("Hello");  // 5

// 查找
$pos = strpos("Hello World", "World");  // 6
$pos = strrpos("Hello World", "o");     // 7（最后一个）

// 截取
$sub = substr("Hello World", 0, 5);    // "Hello"
$sub = substr("Hello World", 6);       // "World"

// 替换
$str = str_replace("World", "PHP", "Hello World");  // "Hello PHP"

// 大小写
strtolower("Hello");   // "hello"
strtoupper("Hello");   // "HELLO"
ucfirst("hello");      // "Hello"
ucwords("hello world");// "Hello World"

// 去除空白
trim("  hello  ");     // "hello"
ltrim("  hello");      // "hello"
rtrim("hello  ");      // "hello"

// 分割与连接
$parts = explode(",", "a,b,c");        // ["a", "b", "c"]
$str = implode("-", ["a", "b", "c"]);  // "a-b-c"

// HTML 转义（防 XSS）
$safe = htmlspecialchars($userInput);
$safe = htmlentities($userInput);

// URL 编码
$encoded = urlencode("hello world");    // "hello+world"
$decoded = urldecode($encoded);

// 哈希
$md5 = md5($string);
$sha1 = sha1($string);

// 密码哈希（安全）
$hash = password_hash($password, PASSWORD_DEFAULT);
if (password_verify($password, $hash)) {
    // 密码正确
}

// 格式化
$num = number_format(1234.56, 2);  // "1,234.56"
$text = sprintf("%s 今年 %d 岁", "小明", 18);

// 正则匹配
if (preg_match("/\d+/", $string, $matches)) {
    echo $matches[0];
}

// 正则替换
$result = preg_replace("/\s+/", " ", $string);
```
