# mysqli - PHP 数据库扩展

> PHP 的 MySQL 数据库扩展（MySQL Improved），用于与 MySQL 数据库交互。

---

## 一、安装与连接

### 1.1 两种使用风格

```php
// 面向过程风格
$conn = mysqli_connect('localhost', 'user', 'password', 'database');
if (!$conn) {
    die('连接失败: ' . mysqli_connect_error());
}

// 面向对象风格
$conn = new mysqli('localhost', 'user', 'password', 'database');
if ($conn->connect_error) {
    die('连接失败: ' . $conn->connect_error);
}
```

### 1.2 连接选项

```php
// 连接前设置选项
$conn = mysqli_init();

// 设置字符集
mysqli_options($conn, MYSQLI_SET_CHARSET_NAME, 'utf8mb4');

// 设置连接超时
mysqli_options($conn, MYSQLI_OPT_CONNECT_TIMEOUT, 5);

// 设置 SSL
// mysqli_ssl_set($conn, $key, $cert, $ca, $capath, $cipher);

// 建立连接
mysqli_real_connect($conn, 'localhost', 'user', 'password', 'database', 3306, null);

// 关闭连接
mysqli_close($conn);
```

### 1.3 字符集与数据库选择

```php
// 设置字符集
mysqli_set_charset($conn, 'utf8mb4');  // 推荐 utf8mb4（支持 emoji）
$conn->set_charset('utf8mb4');         // OOP 风格

// 选择数据库
mysqli_select_db($conn, 'new_database');
$conn->select_db('new_database');
```

---

## 二、基本查询

### 2.1 查询 (SELECT)

```php
// 面向过程
$result = mysqli_query($conn, "SELECT * FROM users");

if ($result) {
    // 获取行数
    $num_rows = mysqli_num_rows($result);
    echo "共 {$num_rows} 行\n";
    
    // 逐行获取（关联数组）
    while ($row = mysqli_fetch_assoc($result)) {
        echo $row['id'] . ': ' . $row['username'] . "\n";
    }
    
    // 逐行获取（索引数组）
    // while ($row = mysqli_fetch_row($result)) { ... }
    
    // 逐行获取（对象）
    // while ($row = mysqli_fetch_object($result)) { ... }
    
    // 获取所有行
    $all_rows = mysqli_fetch_all($result, MYSQLI_ASSOC);
    
    // 释放结果
    mysqli_free_result($result);
} else {
    echo '查询失败: ' . mysqli_error($conn);
}

// 面向对象
$result = $conn->query("SELECT * FROM users");
if ($result) {
    while ($row = $result->fetch_assoc()) {
        // ...
    }
    $result->free();
}
```

### 2.2 INSERT / UPDATE / DELETE

```php
// INSERT
$sql = "INSERT INTO users (username, email) VALUES ('john', 'john@example.com')";
if (mysqli_query($conn, $sql)) {
    echo '新记录 ID: ' . mysqli_insert_id($conn);
    echo '影响行数: ' . mysqli_affected_rows($conn);
} else {
    echo '错误: ' . mysqli_error($conn);
}

// UPDATE
$sql = "UPDATE users SET email='new@example.com' WHERE id=1";
mysqli_query($conn, $sql);
echo '更新了 ' . mysqli_affected_rows($conn) . ' 行';

// DELETE
$sql = "DELETE FROM users WHERE id=1";
mysqli_query($conn, $sql);
echo '删除了 ' . mysqli_affected_rows($conn) . ' 行';
```

### 2.3 常用函数

```php
// 获取受影响行数
mysqli_affected_rows($conn);

// 获取自增 ID
mysqli_insert_id($conn);

// 获取错误信息
mysqli_error($conn);
mysqli_errno($conn);  // 错误号

// 转义字符串（不推荐，用预处理语句）
$escaped = mysqli_real_escape_string($conn, $string);

// 查询信息
mysqli_info($conn);  // 最近查询的信息

// 事务相关
mysqli_begin_transaction($conn);  // 开始事务
mysqli_commit($conn);             // 提交
mysqli_rollback($conn);           // 回滚

// 多语句执行
mysqli_multi_query($conn, $sql);

// 获取字段信息
mysqli_fetch_field($result);
mysqli_num_fields($result);
```

---

## 三、预处理语句（防 SQL 注入）

### 3.1 基本用法

```php
// ===== 不安全的写法（SQL 注入风险）=====
$username = $_POST['username'];
$sql = "SELECT * FROM users WHERE username = '$username'";
$result = mysqli_query($conn, $sql);  // ❌ 危险！

// ===== 安全的写法（预处理语句）=====

// 1. 准备语句
$stmt = mysqli_prepare($conn, "SELECT * FROM users WHERE username = ?");

// 2. 绑定参数
// 类型说明符:
//   i - integer
//   d - double
//   s - string
//   b - blob
$username = $_POST['username'];
mysqli_stmt_bind_param($stmt, "s", $username);

// 3. 执行
mysqli_stmt_execute($stmt);

// 4. 获取结果
$result = mysqli_stmt_get_result($stmt);
while ($row = mysqli_fetch_assoc($result)) {
    // 处理数据
}

// 5. 关闭语句
mysqli_stmt_close($stmt);
```

### 3.2 各种类型参数绑定

```php
// 多个参数
$stmt = mysqli_prepare($conn, 
    "INSERT INTO users (name, age, salary, bio) VALUES (?, ?, ?, ?)");

// s = string, i = int, d = double, b = blob
mysqli_stmt_bind_param($stmt, "sids", $name, $age, $salary, $bio);

$name = "John";
$age = 30;
$salary = 50000.50;
$bio = "some text...";

mysqli_stmt_execute($stmt);

// 获取 INSERT 的自增 ID
echo "新用户 ID: " . mysqli_stmt_insert_id($stmt);
```

### 3.3 SELECT 预处理

```php
// 方法1: 使用 get_result（推荐，需要 mysqlnd 驱动）
$stmt = mysqli_prepare($conn, "SELECT id, name, email FROM users WHERE id > ?");
mysqli_stmt_bind_param($stmt, "i", $min_id);

$min_id = 10;
mysqli_stmt_execute($stmt);

$result = mysqli_stmt_get_result($stmt);
while ($row = mysqli_fetch_assoc($result)) {
    echo $row['id'] . ': ' . $row['name'] . "\n";
}

// 方法2: 使用 bind_result（绑定变量）
$stmt = mysqli_prepare($conn, "SELECT id, name, email FROM users WHERE id = ?");
mysqli_stmt_bind_param($stmt, "i", $id);
mysqli_stmt_bind_result($stmt, $out_id, $out_name, $out_email);

$id = 1;
mysqli_stmt_execute($stmt);

while (mysqli_stmt_fetch($stmt)) {
    echo "ID: $out_id, Name: $out_name, Email: $out_email\n";
}
```

### 3.4 LIKE 模糊查询

```php
// LIKE 查询需要先构造好带通配符的字符串
$search = "%{$_GET['keyword']}%";  // 这里已经绑定了，所以安全

$stmt = mysqli_prepare($conn, "SELECT * FROM users WHERE name LIKE ?");
mysqli_stmt_bind_param($stmt, "s", $search);
mysqli_stmt_execute($stmt);

$result = mysqli_stmt_get_result($stmt);
```

### 3.5 IN 子句的处理

```php
// IN (?, ?, ?) 需要动态构造
$ids = [1, 2, 3, 4, 5];
$placeholders = implode(',', array_fill(0, count($ids), '?'));
$types = str_repeat('i', count($ids));

$stmt = mysqli_prepare($conn, "SELECT * FROM users WHERE id IN ($placeholders)");

// 动态绑定参数（使用引用）
$params = array();
$params[] = &$stmt;
$params[] = &$types;
foreach ($ids as &$id) {
    $params[] = &$id;
}

call_user_func_array('mysqli_stmt_bind_param', $params);

mysqli_stmt_execute($stmt);
$result = mysqli_stmt_get_result($stmt);
```

---

## 四、安全相关内容

### 4.1 SQL 注入攻击与防御

```php
// ===== 注入演示 =====

// 危险示例：直接拼接用户输入
$id = $_GET['id'];
$sql = "SELECT * FROM users WHERE id = $id";
// 攻击: ?id=1 OR 1=1
// 结果: SELECT * FROM users WHERE id = 1 OR 1=1 (返回所有用户)

// 攻击: ?id=1; DROP TABLE users;--
// 结果: 删除 users 表（mysqli 默认不允许多语句，但有风险）

// ===== 防御方法 =====

// ✅ 方法1：预处理语句（最推荐）
$stmt = mysqli_prepare($conn, "SELECT * FROM users WHERE id = ?");
mysqli_stmt_bind_param($stmt, "i", $_GET['id']);
mysqli_stmt_execute($stmt);
$result = mysqli_stmt_get_result($stmt);

// ✅ 方法2：类型强制转换（数字型参数）
$id = (int)$_GET['id'];  // 强制转为整数
$sql = "SELECT * FROM users WHERE id = $id";

// ✅ 方法3：白名单验证（表名/列名等无法参数化的部分）
$allowed_columns = ['id', 'name', 'email', 'created_at'];
$sort = $_GET['sort'] ?? 'id';

if (!in_array($sort, $allowed_columns)) {
    $sort = 'id';  // 默认值
}
$sql = "SELECT * FROM users ORDER BY $sort";

// ❌ 不推荐：mysqli_real_escape_string
// 可以绕过，且容易出错
$name = mysqli_real_escape_string($conn, $_GET['name']);
$sql = "SELECT * FROM users WHERE name = '$name'";
```

### 4.2 事务处理

```php
// 开始事务
mysqli_begin_transaction($conn);

try {
    // 操作1：扣钱
    $sql1 = "UPDATE accounts SET balance = balance - 100 WHERE id = 1";
    if (!mysqli_query($conn, $sql1)) {
        throw new Exception("扣款失败: " . mysqli_error($conn));
    }
    
    if (mysqli_affected_rows($conn) == 0) {
        throw new Exception("余额不足");
    }
    
    // 操作2：加钱
    $sql2 = "UPDATE accounts SET balance = balance + 100 WHERE id = 2";
    if (!mysqli_query($conn, $sql2)) {
        throw new Exception("加钱失败: " . mysqli_error($conn));
    }
    
    // 提交事务
    mysqli_commit($conn);
    echo "转账成功";
    
} catch (Exception $e) {
    // 回滚
    mysqli_rollback($conn);
    echo "转账失败: " . $e->getMessage();
}
```

### 4.3 数据库连接安全

```php
// ===== 安全配置 =====

// 1. 不要硬编码密码（使用环境变量或配置文件）
$host = getenv('DB_HOST') ?: 'localhost';
$user = getenv('DB_USER') ?: 'root';
$pass = getenv('DB_PASS') ?: '';
$db   = getenv('DB_NAME') ?: 'database';

$conn = mysqli_connect($host, $user, $pass, $db);

// 2. 配置文件放在 Web 目录外
// config.php 放在 /var/www/../config/ 目录下
// 而不是 /var/www/html/config.php

// 3. 使用最小权限的数据库账号
// 应用账号不应有 DROP, ALTER, FILE 等权限

// 4. 禁止显示详细错误信息（生产环境）
ini_set('display_errors', 0);
mysqli_report(MYSQLI_REPORT_OFF);

// 5. 安全错误处理
function db_query($conn, $sql) {
    $result = mysqli_query($conn, $sql);
    if (!$result) {
        // 记录详细错误到日志
        error_log('DB Error: ' . mysqli_error($conn) . ' SQL: ' . $sql);
        // 给用户返回模糊的错误
        throw new Exception('数据库操作失败，请稍后重试');
    }
    return $result;
}

// 6. 使用 SSL 连接（远程数据库时）
$conn = mysqli_init();
mysqli_ssl_set($conn, NULL, NULL, '/path/to/ca.pem', NULL, NULL);
mysqli_real_connect($conn, $host, $user, $pass, $db, 3306, NULL, MYSQLI_CLIENT_SSL);
```

### 4.4 密码存储安全

```php
// ===== 密码哈希 =====

// ❌ 错误：使用 MD5/SHA1（太快，易暴力破解）
$hash = md5($password);
$hash = sha1($password);

// ❌ 不推荐：直接 SHA256 + 盐（还是太快）
$hash = hash('sha256', $salt . $password);

// ✅ 正确：使用 password_hash()（bcrypt）
$hash = password_hash($password, PASSWORD_DEFAULT);
// 自动生成随机盐，存储在哈希中
// 结果类似: $2y$10$...

// 验证密码
if (password_verify($password, $stored_hash)) {
    echo '密码正确';
} else {
    echo '密码错误';
}

// 检查是否需要重新哈希（算法/成本变化时）
if (password_needs_rehash($stored_hash, PASSWORD_DEFAULT)) {
    $new_hash = password_hash($password, PASSWORD_DEFAULT);
    // 更新数据库中的哈希
}

// 自定义成本（默认为 10，值越大越慢越安全）
$options = ['cost' => 12];
$hash = password_hash($password, PASSWORD_BCRYPT, $options);

// ===== SQL 中的密码验证 =====
// 不要在 SQL 中比较密码，而是取出哈希用 password_verify 比较

// 正确做法
$stmt = mysqli_prepare($conn, "SELECT password_hash FROM users WHERE username = ?");
mysqli_stmt_bind_param($stmt, "s", $username);
mysqli_stmt_execute($stmt);
$result = mysqli_stmt_get_result($stmt);
$user = mysqli_fetch_assoc($result);

if ($user && password_verify($password, $user['password_hash'])) {
    // 登录成功
}
```

---

## 五、性能优化

```php
// 1. 使用索引（数据库层面）
// CREATE INDEX idx_username ON users(username);

// 2. 只取需要的列
// 好: SELECT id, name FROM users
// 不好: SELECT * FROM users

// 3. LIMIT 分页
$sql = "SELECT * FROM users ORDER BY id LIMIT 10 OFFSET 0";  // 第1页

// 4. 复用连接（连接池或单例）
class DB {
    private static $conn = null;
    
    public static function getConnection() {
        if (self::$conn === null) {
            self::$conn = mysqli_connect('host', 'user', 'pass', 'db');
        }
        return self::$conn;
    }
}

// 5. 使用持久连接（p: 前缀）
$conn = mysqli_connect('p:localhost', 'user', 'pass', 'db');

// 6. 批量插入
$values = [];
foreach ($data as $row) {
    $name = mysqli_real_escape_string($conn, $row['name']);
    $values[] = "('$name')";
}
$sql = "INSERT INTO users (name) VALUES " . implode(',', $values);
mysqli_query($conn, $sql);
```

---

## 六、常见错误

| 错误 | 原因 |
|------|------|
| `mysqli_connect(): Access denied` | 用户名/密码错误，或权限不足 |
| `Unknown database 'xxx'` | 数据库不存在 |
| `Table 'xxx' doesn't exist` | 表不存在 |
| `Unknown column 'xxx'` | 列名错误 |
| `You have an error in your SQL syntax` | SQL 语法错误 |
| `Commands out of sync` | 未释放前一个结果集 |
| `Prepared statement needs to be re-prepared` | 表结构变化了 |
| `Number of variables doesn't match` | 绑定参数数量不匹配 |
