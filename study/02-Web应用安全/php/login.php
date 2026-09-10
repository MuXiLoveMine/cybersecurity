<?php
// login.php
// 简单登录示例

session_start();

// 如果已登录，跳转到首页
if (isset($_SESSION["user_id"])) {
    header("Location: index.php");
    exit;
}

$error = "";

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $username = trim($_POST["username"] ?? "");
    $password = $_POST["password"] ?? "";

    // 模拟验证（实际应用中查数据库 + password_verify）
    $valid_users = [
        "admin" => "123456",
        "test" => "test123"
    ];

    if (isset($valid_users[$username]) && $valid_users[$username] === $password) {
        // 登录成功
        $_SESSION["user_id"] = 1;
        $_SESSION["username"] = $username;
        $_SESSION["login_time"] = time();

        // 重新生成 Session ID，防止会话固定攻击
        session_regenerate_id(true);

        header("Location: index.php");
        exit;
    } else {
        $error = "用户名或密码错误";
    }
}
?>
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>登录</title>
    <style>
        body { font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; background: #f5f5f5; }
        .login-box { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); width: 300px; }
        h2 { text-align: center; margin-top: 0; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; color: #666; }
        input { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        button { width: 100%; padding: 10px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
        .error { color: #dc3545; background: #f8d7da; padding: 10px; border-radius: 4px; margin-bottom: 15px; }
        .tip { color: #666; font-size: 12px; margin-top: 10px; text-align: center; }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>用户登录</h2>

        <?php if ($error): ?>
            <div class="error"><?php echo htmlspecialchars($error); ?></div>
        <?php endif; ?>

        <form method="POST">
            <div class="form-group">
                <label>用户名</label>
                <input type="text" name="username" value="<?php echo htmlspecialchars($username ?? ''); ?>" required>
            </div>

            <div class="form-group">
                <label>密码</label>
                <input type="password" name="password" required>
            </div>

            <button type="submit">登 录</button>
        </form>

        <p class="tip">测试账号: admin / 123456</p>
    </div>
</body>
</html>
