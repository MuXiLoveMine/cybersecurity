<?php
/**
 * sqli_login.php
 * SQL 注入登录绕过示例（仅用于学习，禁止非法用途）
 *
 * 漏洞成因：用户名和密码直接拼接到 SQL 语句中
 * 利用方式：在用户名输入注入语句绕过登录
 */

// 模拟数据库
$users = [
    ['id' => 1, 'username' => 'admin', 'password' => 'admin123', 'role' => 'admin'],
    ['id' => 2, 'username' => 'zhangsan', 'password' => '123456', 'role' => 'user'],
    ['id' => 3, 'username' => 'lisi', 'password' => '123456', 'role' => 'user'],
];

$message = '';
$login_user = null;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = $_POST['username'];
    $password = $_POST['password'];

    // 漏洞：直接拼接 SQL（这里用数组模拟数据库查询，效果一样）
    // 真实环境的 SQL 类似：SELECT * FROM users WHERE username='$username' AND password='$password'
    $found = null;
    foreach ($users as $user) {
        // 模拟 SQL 注入的效果
        // 实际场景中是数据库执行了被注入的 SQL
        if ($user['username'] === $username && $user['password'] === $password) {
            $found = $user;
            break;
        }
    }

    // 为了演示注入效果，我们手动处理几个经典的注入 payload
    // 真实的 SQL 注入是在数据库层面发生的
    if (!$found) {
        // 模拟 ' OR 1=1 --  这种万能密码
        if (strpos($username, "' OR '1'='1") !== false ||
            strpos($username, "admin' --") !== false ||
            strpos($username, "' OR 1=1 #") !== false) {
            $found = $users[0];  // 返回 admin 用户
        }
    }

    if ($found) {
        $message = "登录成功！欢迎 " . $found['username'] . "（角色：" . $found['role'] . "）";
        $login_user = $found;
    } else {
        $message = "用户名或密码错误！";
    }
}
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>SQL 注入登录绕过示例</title>
</head>
<body>
    <h1>用户登录</h1>

    <?php if ($message): ?>
        <p style="color: <?php echo $login_user ? 'green' : 'red'; ?>;">
            <?php echo $message; ?>
        </p>
    <?php endif; ?>

    <form method="POST" action="">
        <p>
            用户名：<input type="text" name="username">
        </p>
        <p>
            密码：<input type="password" name="password">
        </p>
        <button type="submit">登录</button>
    </form>

    <hr>
    <h3>测试 Payload（在用户名输入框中输入）：</h3>
    <ul>
        <li><code>admin' --</code> （注释掉密码校验）</li>
        <li><code>' OR '1'='1</code> （万能密码，密码任意）</li>
        <li><code>' OR 1=1 #</code> （同上，另一种注释方式）</li>
        <li><code>admin' AND 1=1 #</code> （判断用户名是否存在）</li>
    </ul>

    <h3>真实 SQL 执行过程：</h3>
    <p>正常登录的 SQL：</p>
    <pre>SELECT * FROM users WHERE username='admin' AND password='123456'</pre>

    <p>注入后的 SQL（用户名输入 <code>admin' --</code>）：</p>
    <pre>SELECT * FROM users WHERE username='admin' -- ' AND password='xxx'</pre>
    <p>-- 后面的内容被注释掉了，只校验用户名，直接登录成功</p>

    <p>注入后的 SQL（用户名输入 <code>' OR 1=1 #</code>）：</p>
    <pre>SELECT * FROM users WHERE username='' OR 1=1 #' AND password='xxx'</pre>
    <p>OR 1=1 永远为真，返回第一条用户记录</p>

    <hr>
    <h3>修复方法：</h3>
    <ol>
        <li>使用预处理语句（PDO / MySQLi Prepared Statement）</li>
        <li>使用 ORM 框架</li>
        <li>输入验证和过滤</li>
        <li>最小权限原则</li>
    </ol>
</body>
</html>
