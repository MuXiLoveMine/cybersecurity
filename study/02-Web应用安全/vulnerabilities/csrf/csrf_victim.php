<?php
/**
 * csrf_victim.php
 * CSRF 漏洞 - 受害者站点（仅用于学习，禁止非法用途）
 *
 * 漏洞成因：修改密码等敏感操作没有 CSRF Token 验证
 * 利用方式：诱导已登录用户访问攻击者的恶意页面
 */

session_start();

// 模拟用户数据
if (!isset($_SESSION['user'])) {
    $_SESSION['user'] = [
        'username' => 'admin',
        'password' => '123456',
        'email' => 'admin@example.com'
    ];
}

// 处理修改密码
$message = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['new_password'])) {
    $new_password = $_POST['new_password'];
    // 漏洞：没有验证 CSRF Token，也没有验证原密码
    $_SESSION['user']['password'] = $new_password;
    $message = "密码修改成功！新密码：" . $new_password;
}
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>CSRF 漏洞示例 - 修改密码</title>
</head>
<body>
    <h1>个人中心</h1>

    <p>当前用户：<?php echo $_SESSION['user']['username']; ?></p>
    <p>当前密码：<?php echo $_SESSION['user']['password']; ?></p>

    <?php if ($message): ?>
        <p style="color: green;"><?php echo $message; ?></p>
    <?php endif; ?>

    <h2>修改密码</h2>
    <!-- 漏洞：没有 CSRF Token -->
    <form method="POST" action="">
        <p>
            新密码：<input type="text" name="new_password">
        </p>
        <button type="submit">确认修改</button>
    </form>

    <hr>
    <h3>漏洞说明：</h3>
    <p>这个修改密码的表单没有 CSRF 防护，攻击者可以构造恶意页面，</p>
    <p>诱导已登录的用户访问，从而修改用户的密码。</p>

    <hr>
    <h3>修复方法：</h3>
    <ol>
        <li>在表单中加入随机 CSRF Token</li>
        <li>服务端验证 Token</li>
        <li>敏感操作增加二次验证（输入原密码、验证码等）</li>
        <li>Cookie 设置 SameSite 属性</li>
    </ol>
</body>
</html>
