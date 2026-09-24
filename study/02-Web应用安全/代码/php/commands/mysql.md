# mysql

> **分类**：数据库
> **说明**：MySQLi 和 PDO 数据库操作

---

## 语法

```php
MySQLi: $conn = new mysqli(host, user, pass, dbname);\nPDO: $pdo = new PDO("mysql:host=...;dbname=...", user, pass);
```

## ⚠️ 注意

⚠️ 永远不要使用 mysql_ 系列函数（已废弃），使用 MySQLi 或 PDO

## 示例代码

```php
<?php
// ===== MySQLi (面向对象) =====
$conn = new mysqli("localhost", "username", "password", "database");

if ($conn->connect_error) {
    die("连接失败: " . $conn->connect_error);
}

// 查询（有 SQL 注入风险！）
$sql = "SELECT * FROM users WHERE id = $id";
$result = $conn->query($sql);

if ($result->num_rows > 0) {
    while ($row = $result->fetch_assoc()) {
        echo $row["name"];
    }
}

// ===== 预处理语句（防止 SQL 注入，推荐！）=====
$stmt = $conn->prepare("SELECT * FROM users WHERE id = ? AND status = ?");
$stmt->bind_param("is", $id, $status);  // i=整数, s=字符串
$stmt->execute();
$result = $stmt->get_result();

while ($row = $result->fetch_assoc()) {
    // 处理结果
}

$stmt->close();
$conn->close();

// ===== PDO（推荐，跨数据库）=====
try {
    $pdo = new PDO(
        "mysql:host=localhost;dbname=mydb;charset=utf8mb4",
        "username",
        "password",
        [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]
    );

    // 预处理
    $stmt = $pdo->prepare("SELECT * FROM users WHERE id = :id");
    $stmt->execute(["id" => $id]);

    // 获取结果
    $row = $stmt->fetch(PDO::FETCH_ASSOC);  // 一行
    $rows = $stmt->fetchAll(PDO::FETCH_ASSOC);  // 所有行

    // 插入
    $stmt = $pdo->prepare("INSERT INTO users (name, email) VALUES (:name, :email)");
    $stmt->execute(["name" => "Alice", "email" => "a@test.com"]);
    $lastId = $pdo->lastInsertId();

    // 事务
    $pdo->beginTransaction();
    try {
        $pdo->exec("INSERT ...");
        $pdo->exec("UPDATE ...");
        $pdo->commit();
    } catch (Exception $e) {
        $pdo->rollBack();
        throw $e;
    }

} catch (PDOException $e) {
    die("数据库错误: " . $e->getMessage());
}
```
