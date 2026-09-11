<?php
/**
 * dir_brute.php
 * Web 目录爆破工具 - PHP 安全实战
 *
 * 基于 cURL 的目录/文件扫描工具
 * 内置常见路径字典，支持自定义字典和扩展名
 *
 * 仅用于安全学习和授权测试，禁止非法用途
 *
 * 使用方法：
 *   php dir_brute.php http://example.com
 *   php dir_brute.php http://example.com --ext=php,bak,html --threads=20
 */

$url = $argv[1] ?? '';
$options = getopt('', ['ext::', 'threads::', 'wordlist::', 'quiet']);

if (empty($url)) {
    echo "Web 目录爆破工具\n\n";
    echo "用法: php dir_brute.php <URL> [options]\n";
    echo "选项:\n";
    echo "  --ext=php,html,bak    追加文件后缀\n";
    echo "  --threads=20         并发线程数（实际用 cURL multi）\n";
    echo "  --wordlist=file.txt   自定义字典文件\n";
    echo "  --quiet               只显示发现的结果\n";
    echo "示例:\n";
    echo "  php dir_brute.php http://example.com\n";
    echo "  php dir_brute.php http://example.com --ext=php,bak\n";
    exit(1);
}

echo "========================================\n";
echo "  Web 目录爆破工具 (PHP)\n";
echo "  仅用于安全学习和授权测试\n";
echo "========================================\n";

// 内置字典
$builtinDict = [
    'admin', 'administrator', 'login', 'manage', 'manager', 'backend',
    'backup', 'config', 'test', 'debug', 'tmp', 'temp', 'old', 'new',
    'api', 'v1', 'v2', 'swagger', 'graphql', 'rest',
    '.git', '.svn', '.env', '.htaccess', 'web.config', 'robots.txt',
    'phpinfo', 'phpmyadmin', 'pma', 'adminer', 'wp-admin',
    'upload', 'uploads', 'files', 'download', 'data',
    'shell', 'cmd', 'system', 'database', 'db', 'sql',
    'logs', 'access.log', 'error.log', 'sitemap.xml',
    'README', 'CHANGELOG', 'LICENSE', 'install', 'setup',
    'include', 'includes', 'lib', 'src', 'static', 'public',
    'assets', 'js', 'css', 'images', 'img', 'fonts',
    'dev', 'stage', 'staging', 'test', 'demo', 'beta',
    'backup.zip', 'backup.sql', 'dump.sql', 'db.sql',
    'shell.php', 'shell.php.bak', 'c99.php', 'c100.php',
    'index.php.bak', 'config.php.bak', 'config.php.old',
    'phpinfo.php', 'info.php', 'test.php',
    '.DS_Store', '.gitignore', '.idea', '.vscode',
    'vendor', 'node_modules', 'composer.json', 'package.json',
    'Dockerfile', 'docker-compose.yml', '.dockerignore',
];

// 加载字典
if (!empty($options['wordlist']) && file_exists($options['wordlist'])) {
    $dict = file($options['wordlist'], FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    $dict = array_filter($dict, fn($l) => substr($l, 0, 1) !== '#');
    echo "[*] 加载自定义字典: " . count($dict) . " 条\n";
} else {
    $dict = $builtinDict;
    echo "[*] 使用内置字典: " . count($dict) . " 条\n";
}

// 扩展名
$extensions = [''];
if (!empty($options['ext'])) {
    $exts = explode(',', $options['ext']);
    foreach ($exts as $e) {
        $extensions[] = '.' . trim($e);
    }
}

// 构建完整路径列表
$paths = [];
foreach ($dict as $word) {
    foreach ($extensions as $ext) {
        $paths[] = $word . $ext;
    }
}

$baseUrl = rtrim($url, '/');
$quiet = isset($options['quiet']);
$threads = (int)($options['threads'] ?? 10);
$threads = min($threads, 20); // 限制最大并发

echo "[*] 目标: $baseUrl\n";
echo "[*] 路径数: " . count($paths) . "\n";
echo "[*] 并发: $threads\n";
echo "[*] 开始扫描...\n\n";

// cURL 多线程并发
$mh = curl_multi_init();
$activeHandles = [];
$found = [];
$queue = array_values($paths);
$processed = 0;
$total = count($queue);

// 初始化批处理
function initBatch(&$mh, &$activeHandles, &$queue, $baseUrl, $batchSize) {
    for ($i = 0; $i < $batchSize && !empty($queue); $i++) {
        $path = array_shift($queue);
        $ch = curl_init();
        curl_setopt_array($ch, [
            CURLOPT_URL => $baseUrl . '/' . $path,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT => 10,
            CURLOPT_NOBODY => true,
            CURLOPT_FOLLOWLOCATION => false,
            CURLOPT_SSL_VERIFYPEER => false,
            CURLOPT_USERAGENT => 'Mozilla/5.0 (Security Scanner)',
        ]);
        curl_setopt($ch, CURLOPT_PRIVATE, $path);
        curl_multi_add_handle($mh, $ch);
        $activeHandles[] = $ch;
    }
}

initBatch($mh, $activeHandles, $queue, $baseUrl, $threads);

// 主循环
do {
    $status = curl_multi_exec($mh, $active);
    while ($info = curl_multi_info_read($mh)) {
        $ch = $info['handle'];
        $path = curl_getinfo($ch, CURLINFO_PRIVATE);
        $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $size = curl_getinfo($ch, CURLINFO_CONTENT_LENGTH_DOWNLOAD);

        $processed++;

        // 200/301/302/401/403 是有意义的响应
        if (in_array($code, [200, 301, 302, 401, 403, 500])) {
            $statusColor = match($code) {
                200 => '200 OK',
                301, 302 => "$code Redirect",
                401 => '401 Unauthorized',
                403 => '403 Forbidden',
                500 => '500 Error',
                default => "$code"
            };
            echo "  [$code] /$path" . ($size > 0 ? "  ($size bytes)" : "") . "\n";
            $found[] = ['path' => $path, 'code' => $code, 'size' => $size];
        } elseif (!$quiet) {
            // 不显示 404
        }

        // 进度
        if ($processed % 50 == 0) {
            $progress = floor($processed / $total * 100);
            echo "  [进度] $processed / $total ($progress%)\r";
        }

        curl_multi_remove_handle($mh, $ch);
        curl_close($ch);

        // 从队列补充新请求
        if (!empty($queue)) {
            $newPath = array_shift($queue);
            $newCh = curl_init();
            curl_setopt_array($newCh, [
                CURLOPT_URL => $baseUrl . '/' . $newPath,
                CURLOPT_RETURNTRANSFER => true,
                CURLOPT_TIMEOUT => 10,
                CURLOPT_NOBODY => true,
                CURLOPT_FOLLOWLOCATION => false,
                CURLOPT_SSL_VERIFYPEER => false,
                CURLOPT_USERAGENT => 'Mozilla/5.0 (Security Scanner)',
            ]);
            curl_setopt($newCh, CURLOPT_PRIVATE, $newPath);
            curl_multi_add_handle($mh, $newCh);
            $activeHandles[] = $newCh;
        }
    }

    if ($active > 0) {
        curl_multi_select($mh, 1.0);
    }
} while ($active > 0 || !empty($queue));

curl_multi_close($mh);

echo "\n\n===== 扫描结果 =====\n";
echo "总请求数: $processed\n";
echo "发现路径: " . count($found) . "\n";

if (!empty($found)) {
    echo "\n发现的路径:\n";
    foreach ($found as $f) {
        echo "  [{$f['code']}] /{$f['path']}\n";
    }
}
