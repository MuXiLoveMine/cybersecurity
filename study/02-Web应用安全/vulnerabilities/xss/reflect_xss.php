<?php
/**
 * reflect_xss.php
 * 反射型 XSS 漏洞示例（仅用于学习，禁止非法用途）
 *
 * 漏洞成因：用户输入未经转义直接输出到 HTML
 * 利用方式：?keyword=<script>alert(1)</script>
 */

// 获取搜索关键词（用户可控）
$keyword = isset($_GET['keyword']) ? $_GET['keyword'] : '';

// 模拟搜索结果
$results = [];
if (!empty($keyword)) {
    $results = [
        ['title' => $keyword . ' 相关结果 1', 'desc' => '这是关于 ' . $keyword . ' 的搜索结果'],
        ['title' => $keyword . ' 相关结果 2', 'desc' => '另一个 ' . $keyword . ' 相关的内容'],
    ];
}
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>反射型 XSS 示例</title>
</head>
<body>
    <h1>搜索</h1>

    <form method="GET" action="">
        <input type="text" name="keyword" placeholder="输入关键词" value="<?php echo $keyword; ?>">
        <button type="submit">搜索</button>
    </form>

    <?php if (!empty($keyword)): ?>
        <!-- 漏洞点：关键词直接输出到页面 -->
        <p>搜索关键词：<?php echo $keyword; ?></p>
        <p>找到 <?php echo count($results); ?> 个结果</p>

        <div class="results">
            <?php foreach ($results as $result): ?>
                <div class="item">
                    <h3><?php echo $result['title']; ?></h3>
                    <p><?php echo $result['desc']; ?></p>
                </div>
            <?php endforeach; ?>
        </div>
    <?php endif; ?>

    <hr>
    <h3>测试 Payload：</h3>
    <ul>
        <li><code>?keyword=&lt;script&gt;alert(1)&lt;/script&gt;</code></li>
        <li><code>?keyword=&lt;img src=x onerror=alert(document.cookie)&gt;</code></li>
        <li><code>?keyword=&lt;svg onload=alert('XSS')&gt;</code></li>
    </ul>

    <hr>
    <h3>安全的写法（修复后）：</h3>
    <p>使用 htmlspecialchars() 转义输出：</p>
    <pre>echo htmlspecialchars($keyword, ENT_QUOTES, 'UTF-8');</pre>
</body>
</html>
