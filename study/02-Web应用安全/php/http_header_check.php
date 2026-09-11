<?php
/**
 * http_header_check.php
 * HTTP 安全头检测工具 - PHP 安全实战
 *
 * 检测目标网站的 HTTP 安全响应头配置
 * 给出安全评分和修复建议
 *
 * 仅用于安全学习和授权测试
 *
 * 使用方法：
 *   php http_header_check.php https://example.com
 */

$targetUrl = $argv[1] ?? '';

if (empty($targetUrl)) {
    echo "HTTP 安全头检测工具\n\n";
    echo "用法: php http_header_check.php <URL>\n";
    echo "示例: php http_header_check.php https://example.com\n";
    exit(1);
}

echo "========================================\n";
echo "  HTTP 安全头检测工具 (PHP)\n";
echo "  仅用于安全学习和授权测试\n";
echo "========================================\n";
echo "[*] 目标: $targetUrl\n\n";

// 发送请求并获取响应头
function getHeaders($url) {
    $ch = curl_init();
    curl_setopt_array($ch, [
        CURLOPT_URL => $url,
        CURLOPT_HEADER => true,
        CURLOPT_NOBODY => true,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => 15,
        CURLOPT_FOLLOWLOCATION => false,
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_USERAGENT => 'Mozilla/5.0 (Security Scanner)',
    ]);
    $response = curl_exec($ch);
    $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    // 解析响应头
    $headers = [];
    $lines = explode("\r\n", $response);
    foreach ($lines as $line) {
        if (strpos($line, ':') !== false) {
            list($key, $value) = explode(':', $line, 2);
            $key = trim($key);
            $value = trim($value);
            $headers[strtolower($key)] = $value;
        }
    }
    return ['headers' => $headers, 'code' => $code];
}

// 安全头检查清单
$securityHeaders = [
    'x-frame-options' => [
        'score' => 10,
        'risk' => '高',
        'desc' => '防止点击劫持',
        'fix' => 'X-Frame-Options: SAMEORIGIN',
        'validate' => fn($v) => in_array(strtolower($v), ['deny', 'sameorigin']) ? '正确' : '可疑值'
    ],
    'x-content-type-options' => [
        'score' => 10,
        'risk' => '高',
        'desc' => '防止 MIME 嗅探',
        'fix' => 'X-Content-Type-Options: nosniff',
        'validate' => fn($v) => strtolower($v) === 'nosniff' ? '正确' : '可疑值'
    ],
    'x-xss-protection' => [
        'score' => 5,
        'risk' => '中',
        'desc' => '浏览器 XSS 过滤器',
        'fix' => 'X-XSS-Protection: 1; mode=block',
        'validate' => fn($v) => strpos($v, '1') === 0 ? '正确' : '已禁用'
    ],
    'content-security-policy' => [
        'score' => 15,
        'risk' => '高',
        'desc' => '内容安全策略',
        'fix' => 'Content-Security-Policy: default-src \'self\'',
        'validate' => fn($v) => '已配置'
    ],
    'strict-transport-security' => [
        'score' => 10,
        'risk' => '高',
        'desc' => 'HSTS 强制 HTTPS',
        'fix' => 'Strict-Transport-Security: max-age=31536000; includeSubDomains',
        'validate' => fn($v) => '已配置'
    ],
    'referrer-policy' => [
        'score' => 5,
        'risk' => '中',
        'desc' => '控制 Referer 泄露',
        'fix' => 'Referrer-Policy: no-referrer-when-downgrade',
        'validate' => fn($v) => '已配置'
    ],
    'permissions-policy' => [
        'score' => 5,
        'risk' => '低',
        'desc' => '浏览器功能权限控制',
        'fix' => 'Permissions-Policy: geolocation=(), camera=()',
        'validate' => fn($v) => '已配置'
    ],
];

// 信息泄露头
$leakHeaders = ['server', 'x-powered-by', 'x-aspnet-version', 'x-aspnetmvc-version', 'via', 'x-runtime'];

$result = getHeaders($targetUrl);

if ($result['code'] == 0) {
    echo "[!] 请求失败，请检查 URL\n";
    exit(1);
}

echo "[*] HTTP 状态码: {$result['code']}\n\n";

// 安全头检测
echo "===== 安全响应头检查 =====\n";
$totalScore = 0;
$maxScore = 0;
$missing = [];

foreach ($securityHeaders as $headerName => $config) {
    $maxScore += $config['score'];
    $key = strtolower($headerName);

    if (isset($result['headers'][$key])) {
        $value = $result['headers'][$key];
        $validate = $config['validate']($value);
        $totalScore += $config['score'];
        echo "  [+] $headerName : $value ($validate)\n";
    } else {
        echo "  [-] $headerName : 缺失 (风险:{$config['risk']} | {$config['desc']} | 建议:{$config['fix']})\n";
        $missing[] = $config;
    }
}

// 信息泄露检测
echo "\n===== 信息泄露检测 =====\n";
$leakFound = false;
foreach ($leakHeaders as $lh) {
    if (isset($result['headers'][$lh])) {
        echo "  [!] $lh : {$result['headers'][$lh]}\n";
        $leakFound = true;
        $totalScore -= 5;
    }
}
if (!$leakFound) {
    echo "  [+] 未检测到信息泄露头\n";
}

// Cookie 安全检测
echo "\n===== Cookie 安全检测 =====\n";
$setCookie = $result['headers']['set-cookie'] ?? '';
if ($setCookie) {
    $hasSecure = stripos($setCookie, 'secure') !== false;
    $hasHttpOnly = stripos($setCookie, 'httponly') !== false;
    $hasSameSite = stripos($setCookie, 'samesite') !== false;

    if (!$hasSecure) echo "  [-] Cookie 缺少 Secure 属性\n";
    if (!$hasHttpOnly) echo "  [-] Cookie 缺少 HttpOnly 属性\n";
    if (!$hasSameSite) echo "  [-] Cookie 缺少 SameSite 属性\n";
    if ($hasSecure && $hasHttpOnly && $hasSameSite) {
        echo "  [+] Cookie 安全属性完整\n";
    }
} else {
    echo "  [*] 未设置 Cookie\n";
}

// 评分
$percentage = $maxScore > 0 ? floor($totalScore / $maxScore * 100) : 0;
$grade = $percentage >= 90 ? 'A' : ($percentage >= 80 ? 'B' : ($percentage >= 70 ? 'C' : ($percentage >= 60 ? 'D' : 'F')));

echo "\n===== 安全评分 =====\n";
echo "  得分: $totalScore / $maxScore ($percentage%)\n";
echo "  等级: $grade\n";

echo "\n===== 修复建议 =====\n";
if (!empty($missing)) {
    foreach ($missing as $m) {
        echo "  [{$m['risk']}] {$m['fix']}\n";
    }
} else {
    echo "  所有安全头已正确配置！\n";
}
