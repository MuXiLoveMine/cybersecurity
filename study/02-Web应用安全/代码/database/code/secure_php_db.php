<?php
/**
 * secure_php_db.php
 * PHP 安全数据库操作示例
 * 演示如何正确使用 PDO 和参数化查询防止 SQL 注入
 */

// =============================================
// 一、使用 PDO（推荐）
// =============================================

class SecurePDO {
    private $pdo;

    public function __construct($host, $dbname, $username, $password) {
        try {
            $dsn = "mysql:host=$host;dbname=$dbname;charset=utf8mb4";
            $this->pdo = new PDO($dsn, $username, $password, [
                PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,  // 异常模式
                PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,        // 默认关联数组
                PDO::ATTR_EMULATE_PREPARES   => false,                   // 禁用模拟预处理（真预处理）
                PDO::ATTR_PERSISTENT         => false,                   // 非持久连接
            ]);
        } catch (PDOException $e) {
            // 生产环境不要直接输出错误信息
            die("数据库连接失败");
        }
    }

    /**
     * 安全的查询（参数化查询，防 SQL 注入）
     */
    public function getUserById($id) {
        // 使用预处理语句
        $sql = "SELECT id, username, email, role FROM users WHERE id = :id";
        $stmt = $this->pdo->prepare($sql);

        // 绑定参数
        $stmt->bindParam(':id', $id, PDO::PARAM_INT);

        // 执行
        $stmt->execute();

        return $stmt->fetch();
    }

    /**
     * 安全的登录查询
     */
    public function login($username, $password) {
        $sql = "SELECT id, username, role FROM users 
                WHERE username = :username AND password = :password 
                LIMIT 1";

        $stmt = $this->pdo->prepare($sql);
        $stmt->bindParam(':username', $username, PDO::PARAM_STR);
        $stmt->bindParam(':password', md5($password), PDO::PARAM_STR);
        $stmt->execute();

        return $stmt->fetch();
    }

    /**
     * 安全的模糊搜索
     */
    public function searchUsers($keyword) {
        // LIKE 查询需要手动添加 %，然后绑定整个值
        $keyword = "%{$keyword}%";

        $sql = "SELECT id, username, email FROM users 
                WHERE username LIKE :keyword OR email LIKE :keyword";

        $stmt = $this->pdo->prepare($sql);
        $stmt->bindParam(':keyword', $keyword, PDO::PARAM_STR);
        $stmt->execute();

        return $stmt->fetchAll();
    }

    /**
     * 安全的 IN 查询
     */
    public function getUsersByIds(array $ids) {
        // 过滤只保留整数
        $ids = array_filter($ids, 'is_int');

        if (empty($ids)) {
            return [];
        }

        // 生成占位符
        $placeholders = implode(',', array_fill(0, count($ids), '?'));

        $sql = "SELECT id, username, email FROM users WHERE id IN ($placeholders)";
        $stmt = $this->pdo->prepare($sql);
        $stmt->execute($ids);

        return $stmt->fetchAll();
    }

    /**
     * 安全的 ORDER BY（白名单）
     */
    public function getUsers($order = 'id', $sort = 'ASC') {
        // 白名单校验排序字段
        $allowedOrders = ['id', 'username', 'email', 'created_at'];
        $allowedSorts = ['ASC', 'DESC'];

        if (!in_array($order, $allowedOrders)) {
            $order = 'id';
        }
        if (!in_array(strtoupper($sort), $allowedSorts)) {
            $sort = 'ASC';
        }

        // 白名单校验后可以安全拼接
        $sql = "SELECT id, username, email FROM users ORDER BY $order $sort";
        $stmt = $this->pdo->query($sql);

        return $stmt->fetchAll();
    }

    /**
     * 安全的插入
     */
    public function addUser($username, $password, $email) {
        $sql = "INSERT INTO users (username, password, email) 
                VALUES (:username, :password, :email)";

        $stmt = $this->pdo->prepare($sql);
        $stmt->bindParam(':username', $username, PDO::PARAM_STR);
        $stmt->bindParam(':password', password_hash($password, PASSWORD_DEFAULT), PDO::PARAM_STR);
        $stmt->bindParam(':email', $email, PDO::PARAM_STR);

        return $stmt->execute();
    }

    /**
     * 获取 PDO 实例（用于更复杂操作）
     */
    public function getPdo() {
        return $this->pdo;
    }
}

// =============================================
// 二、使用 MySQLi（参数化查询）
// =============================================

class SecureMySQLi {
    private $conn;

    public function __construct($host, $dbname, $username, $password) {
        $this->conn = new mysqli($host, $username, $password, $dbname);

        if ($this->conn->connect_error) {
            die("数据库连接失败");
        }

        $this->conn->set_charset("utf8mb4");
    }

    /**
     * 安全查询
     */
    public function getUserById($id) {
        $sql = "SELECT id, username, email FROM users WHERE id = ?";
        $stmt = $this->conn->prepare($sql);

        // 绑定参数：i=整数, s=字符串, d=双精度, b=blob
        $stmt->bind_param("i", $id);
        $stmt->execute();

        $result = $stmt->get_result();
        return $result->fetch_assoc();
    }

    /**
     * 安全登录
     */
    public function login($username, $password) {
        $sql = "SELECT id, username FROM users WHERE username = ? AND password = ? LIMIT 1";
        $stmt = $this->conn->prepare($sql);

        $hashed_pass = md5($password);
        $stmt->bind_param("ss", $username, $hashed_pass);
        $stmt->execute();

        $result = $stmt->get_result();
        return $result->fetch_assoc();
    }
}

// =============================================
// 三、输入验证与过滤
// =============================================

/**
 * 验证用户名：字母数字下划线，4-20位
 */
function validateUsername($username) {
    return preg_match('/^[a-zA-Z0-9_]{4,20}$/', $username);
}

/**
 * 验证邮箱
 */
function validateEmail($email) {
    return filter_var($email, FILTER_VALIDATE_EMAIL) !== false;
}

/**
 * 验证整数 ID
 */
function validateId($id) {
    return filter_var($id, FILTER_VALIDATE_INT, [
        'options' => ['min_range' => 1]
    ]) !== false;
}

/**
 * 安全输出到 HTML（防 XSS）
 */
function safeOutput($data) {
    return htmlspecialchars($data, ENT_QUOTES, 'UTF-8');
}

// =============================================
// 四、不安全的写法（反面教材，请勿使用！）
// =============================================

/*
// ❌ 危险：直接拼接 SQL（SQL 注入漏洞）
function unsafe_login($username, $password) {
    $sql = "SELECT * FROM users WHERE username = '$username' AND password = '$password'";
    $result = mysqli_query($conn, $sql);
    return mysqli_fetch_assoc($result);
}

// ❌ 危险：直接拼接搜索
function unsafe_search($keyword) {
    $sql = "SELECT * FROM users WHERE username LIKE '%$keyword%'";
    $result = mysqli_query($conn, $sql);
}

// ❌ 危险：直接拼接 ORDER BY
function unsafe_order($order) {
    $sql = "SELECT * FROM users ORDER BY $order";
    $result = mysqli_query($conn, $sql);
}
*/

// =============================================
// 使用示例
// =============================================

// PDO 方式
$db = new SecurePDO('localhost', 'testdb', 'root', 'password');

// 安全查询
$user = $db->getUserById(1);
if ($user) {
    echo "用户名: " . safeOutput($user['username']) . "\n";
    echo "邮箱: " . safeOutput($user['email']) . "\n";
}

// 安全登录
$login_result = $db->login('admin', 'admin123');
if ($login_result) {
    echo "登录成功\n";
} else {
    echo "用户名或密码错误\n";
}

// 安全搜索
$results = $db->searchUsers('a');
foreach ($results as $row) {
    echo safeOutput($row['username']) . "\n";
}

echo "\n安全数据库操作示例完成！\n";
echo "核心原则：永远使用参数化查询，永远不要拼接 SQL！\n";
