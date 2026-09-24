# variable

> **分类**：变量
> **说明**：PHP 变量以 $ 开头，弱类型

---

## 语法

```php
$variableName = value;
```

## 类型

string/integer/float/bool/array/object/null/resource

## 示例代码

```php
<?php
// 变量声明
$name = "Alice";
$age = 25;
$price = 9.99;
$isActive = true;
$nothing = null;

// 变量类型
gettype($var);      // 获取类型
is_string($var);    // 是否字符串
is_int($var);       // 是否整数
is_array($var);     // 是否数组
is_null($var);      // 是否为 null
isset($var);        // 是否设置且不为 null
empty($var);        // 是否为空（0, "", null, false, 空数组等）

// 类型转换
$num = (int)"123";        // 转整数
$str = (string)123;       // 转字符串
$bool = (bool)1;          // 转布尔
$arr = (array)$obj;       // 转数组

// 可变变量
$varName = "age";
$$varName = 25;  // 等于 $age = 25;

// 变量作用域
$globalVar = "全局";
function test() {
    global $globalVar;   // 使用全局变量
    static $count = 0;   // 静态变量（函数调用间保留值）
    $count++;
    echo $count;
}

// 超全局变量
$_GET;      // GET 参数
$_POST;     // POST 参数
$_REQUEST;  // GET + POST + COOKIE
$_SESSION;  // 会话数据
$_COOKIE;   // Cookie
$_SERVER;   // 服务器信息
$_FILES;    // 上传文件
$_ENV;      // 环境变量

// 常量
define("MAX_SIZE", 100);
const MIN_SIZE = 1;
echo MAX_SIZE;

// null合并运算符 (PHP 7+)
$value = $_GET['key'] ?? '默认值';

// 太空船运算符 (PHP 7+)
$result = $a <=> $b;  // -1/0/1
```
