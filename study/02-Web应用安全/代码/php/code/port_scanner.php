<?php
/**
 * port_scanner.php
 * TCP 端口扫描器 - PHP 安全实战
 *
 * 使用 fsockopen 进行 TCP 全连接端口扫描
 * 支持指定 IP 和端口范围
 *
 * 仅用于安全学习和授权测试，禁止非法用途
 *
 * 使用方法：
 *   php port_scanner.php 192.168.1.1 --start=1 --end=1024
 *   php port_scanner.php 192.168.1.1 --common
 */

$target = $argv[1] ?? '';
$options = getopt('', ['start::', 'end::', 'common', 'timeout::']);

if (empty($target)) {
    echo "TCP 端口扫描器\n\n";
    echo "用法: php port_scanner.php <IP> [options]\n";
    echo "选项:\n";
    echo "  --start=1      起始端口\n";
    echo "  --end=1024     结束端口\n";
    echo "  --common       只扫描常见端口\n";
    echo "  --timeout=2    连接超时（秒）\n";
    echo "示例:\n";
    echo "  php port_scanner.php 192.168.1.1 --start=1 --end=1000\n";
    echo "  php port_scanner.php 192.168.1.1 --common\n";
    exit(1);
}

echo "========================================\n";
echo "  TCP 端口扫描器 (PHP)\n";
echo "  仅用于安全学习和授权测试\n";
echo "========================================\n";

// 常见端口映射
$commonPorts = [
    21 => 'FTP', 22 => 'SSH', 23 => 'Telnet', 25 => 'SMTP',
    53 => 'DNS', 80 => 'HTTP', 110 => 'POP3', 143 => 'IMAP',
    443 => 'HTTPS', 445 => 'SMB', 631 => 'IPP',
    993 => 'IMAPS', 995 => 'POP3S',
    1433 => 'MSSQL', 1521 => 'Oracle',
    3306 => 'MySQL', 3389 => 'RDP',
    5432 => 'PostgreSQL', 5900 => 'VNC',
    6379 => 'Redis', 8080 => 'HTTP-Alt',
    8443 => 'HTTPS-Alt', 9000 => 'PHP-FPM',
    9090 => 'Prometheus', 9200 => 'Elasticsearch',
    11211 => 'Memcached', 27017 => 'MongoDB',
];

$timeout = (float)($options['timeout'] ?? 2.0);

// 确定扫描端口列表
if (isset($options['common'])) {
    $ports = array_keys($commonPorts);
    echo "[*] 扫描常见端口: " . count($ports) . " 个\n";
} else {
    $start = (int)($options['start'] ?? 1);
    $end = (int)($options['end'] ?? 1024);
    $ports = range($start, $end);
    echo "[*] 扫描端口范围: $start-$end (" . count($ports) . " 个)\n";
}

echo "[*] 目标: $target\n";
echo "[*] 超时: {$timeout}s\n";
echo "[*] 开始扫描...\n\n";

$found = [];
$scanned = 0;
$total = count($ports);
$startTime = microtime(true);

foreach ($ports as $port) {
    $scanned++;
    $port = (int)$port;

    // 使用 fsockopen 进行 TCP 连接
    $errno = 0;
    $errstr = '';
    $socket = @fsockopen($target, $port, $errno, $errstr, $timeout);

    if ($socket !== false) {
        // 端口开放
        $service = $commonPorts[$port] ?? 'unknown';
        echo "  [+] $target:$port  OPEN  ($service)\n";
        $found[] = ['port' => $port, 'service' => $service];
        fclose($socket);
    }

    // 进度
    if ($scanned % 10 == 0) {
        $elapsed = microtime(true) - $startTime;
        $rate = round($scanned / $elapsed, 1);
        echo "  [进度] $scanned / $total ($rate ports/s)\r";
    }
}

$elapsed = round(microtime(true) - $startTime, 2);

echo "\n\n===== 扫描结果 =====\n";
echo "目标: $target\n";
echo "扫描端口: $scanned\n";
echo "开放端口: " . count($found) . "\n";
echo "耗时: {$elapsed}s\n";

if (!empty($found)) {
    echo "\n开放端口列表:\n";
    foreach ($found as $f) {
        echo "  {$f['port']}/tcp  {$f['service']}\n";
    }
}
