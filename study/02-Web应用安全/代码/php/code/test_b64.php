<?php
/**
 * ==============================================================================
 *   TCP 端口扫描器 - port_scanner.php
 * ==============================================================================
 *   功能说明：
 *     本脚本使用 fsockopen 函数实现 TCP 端口扫描，支持端口范围扫描，
 *     用于安全研究和授权测试。
 *
 *   功能特性：
 *     1. 单端口扫描
 *     2. 端口范围扫描
 *     3. 常见端口快捷扫描
 *     4. 可配置超时时间
 *     5. 端口服务名称识别
 *
 *   使用方法：
 *     php port_scanner.php <目标IP> [起始端口] [结束端口] [超时秒数]
 *
 *   示例：
 *     // 扫描单个端口
 *     php port_scanner.php 127.0.0.1 80
 *
 *     // 扫描端口范围
 *     php port_scanner.php 127.0.0.1 1 1000
 *
 *     // 快速扫描常见端口（只传 IP）
 *     php port_scanner.php 127.0.0.1
 *
 *     // 自定义超时时间
 *     php port_scanner.php 192.168.1.1 1 1000 2
 *
 *   免责声明：
 *     本脚本仅供安全学习和授权测试使用。
 *     未经授权扫描他人网络或系统属于违法行为。
 *     使用者需对使用本脚本产生的一切后果自行承担责任。
 *     请遵守当地法律法规，仅在获得明确授权的情况下使用。
 * ==============================================================================
 */

// ============================================================
// 常见端口与服务名称映射
// ============================================================
$commonPorts = [
    21    => 'FTP (文件传输协议)',
    22    => 'SSH (安全外壳)',
    23    => 'Telnet (远程终端)',
    25    => 'SMTP (邮件发送)',
    53    => 'DNS (域名系统)',
    80    => 'HTTP (网页服务)',
    110   => 'POP3 (邮件接收)',
    111   => 'RPC (远程过程调用)',
    135   => 'MSRPC (微软RPC)',
    139   => 'NetBIOS (网络基本输入输出)',
    143   => 'IMAP (邮件访问)',
    443   => 'HTTPS (安全网页服务)',
    445   => 'SMB (服务器消息块)',
    465   => 'SMTPS (安全邮件发送)',
    993   => 'IMAPS (安全邮件访问)',
    995   => 'POP3S (安全邮件接收)',
    1080  => 'SOCKS (代理服务)',
    1433  => 'MSSQL (微软SQL Server)',
    1521  => 'Oracle (Oracle数据库)',
    1723  => 'PPTP (点对点隧道)',
    3306  => 'MySQL (MySQL数据库)',
    3389  => 'RDP (远程桌面)',
    5432  => 'PostgreSQL (PostgreSQL数据库)',
    5900  => 'VNC (虚拟网络计算)',
    6379  => 'Redis (Redis缓存)',
    8080  => 'HTTP-Proxy (HTTP代理/备用)',
    8443  => 'HTTPS-Alt (HTTPS备用)',
    8888  => 'HTTP-Alt (HTTP备用)',
    27017 => 'MongoDB (MongoDB数据库)',
];

// ============================================================
// 打印帮助信息
// ============================================================
function printHelp()
{
    echo "================================================================\n";
    echo "  TCP 端口扫描器 - 安全研究用\n";
    echo "================================================================\n\n";
    echo "用法: php port_scanner.php <目标IP> [起始端口] [结束端口] [超时]\n\n";
    echo "参数说明:\n";
    echo "  目标IP    目标主机IP地址或域名（必需）\n";
    echo "  起始端口  扫描起始端口（默认扫描常见端口）\n";
    echo "  结束端口  扫描结束端口（省略则扫描单个端口）\n";
    echo "  超时      连接超时秒数（默认 1 秒）\n\n";
    echo "示例:\n";
    echo "  php port_scanner.php 127.0.0.1\n";
    echo "  php port_scanner.php 127.0.0.1 80\n";
    echo "  php port_scanner.php 127.0.0.1 1 1000\n";
    echo "  php port_scanner.php 192.168.1.1 1 65535 2\n";
    echo "================================================================\n";
}

// ============================================================
// 扫描单个端口
// 使用 fsockopen 建立 TCP 连接，通过连接是否成功判断端口状态
// 参数：
//   $host    - 目标主机
//   $port    - 端口号
//   $timeout - 超时时间（秒）
// 返回：true（开放）/ false（关闭/过滤）
// ============================================================
function scanPort($host, $port, $timeout = 1)
{
    // 创建 socket 连接
    // fsockopen 会建立 TCP 连接，连接成功返回文件指针
    $socket = @fsockopen($host, $port, $errno, $errstr, $timeout);

    if ($socket) {
        // 连接成功，端口开放
        fclose($socket);
        return true;
    }

    // 连接失败，端口关闭或被过滤
    return false;
}

// ============================================================
// 获取端口服务名称
// ============================================================
function getServiceName($port)
{
    global $commonPorts;
    return isset($commonPorts[$port]) ? $commonPorts[$port] : '未知服务';
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

    $host = $argv[1];
    $startPort = 0;
    $endPort = 0;
    $timeout = 1;
    $scanCommon = false;

    // 解析参数
    if ($argc >= 3) {
        $startPort = intval($argv[2]);
        if ($argc >= 4) {
            $endPort = intval($argv[3]);
        }
        if ($argc >= 5) {
            $timeout = floatval($argv[4]);
        }
    } else {
        // 只传了 IP，扫描常见端口
        $scanCommon = true;
    }

    // 验证端口
    if (!$scanCommon) {
        if ($startPort < 1 || $startPort > 65535) {
            echo "[错误] 起始端口必须在 1-65535 之间\n";
            return;
        }
        if ($endPort == 0) {
            // 单个端口
            $endPort = $startPort;
        }
        if ($endPort < 1 || $endPort > 65535) {
            echo "[错误] 结束端口必须在 1-65535 之间\n";
            return;
        }
        if ($startPort > $endPort) {
            echo "[错误] 起始端口不能大于结束端口\n";
            return;
        }
    }

    // 验证超时
    if ($timeout <= 0) {
        echo "[错误] 超时时间必须大于 0\n";
        return;
    }

    echo "\n";
    echo "================================================================\n";
    echo "  TCP 端口扫描器\n";
    echo "================================================================\n\n";

    // 解析目标地址
    echo "[信息] 目标地址: $host\n";
    $ip = gethostbyname($host);
    if ($ip != $host) {
        echo "[信息] 解析结果: $ip\n";
    }
    echo "[信息] 超时时间: {$timeout} 秒\n";

    // 构建端口列表
    $portList = [];
    if ($scanCommon) {
        global $commonPorts;
        $portList = array_keys($commonPorts);
        sort($portList);
        echo "[信息] 扫描模式: 常见端口 (" . count($portList) . " 个)\n";
    } else {
        $portList = range($startPort, $endPort);
        echo "[信息] 扫描范围: {$startPort} - {$endPort} (" . count($portList) . " 个端口)\n";
    }

    echo "\n";
    echo "----------------------------------------------------------------\n";
    echo "  开始扫描...\n";
    echo "----------------------------------------------------------------\n\n";

    // 执行扫描
    $openPorts = [];
    $total = count($portList);
    $count = 0;
    $startTime = microtime(true);

    foreach ($portList as $port) {
        $count++;

        // 扫描端口
        $isOpen = scanPort($host, $port, $timeout);

        // 显示进度（每 100 个端口更新一次）
        if ($count % 100 == 0 || $count == $total) {
            $progress = round(($count / $total) * 100, 1);
            echo "\r[进度] {$progress}% ({$count}/{$total})";
        }

        if ($isOpen) {
            $service = getServiceName($port);
            echo "\n[开放] 端口 {$port} - {$service}\n";
            $openPorts[] = [
                'port' => $port,
                'service' => $service,
            ];
        }
    }

    echo "\n";

    $endTime = microtime(true);
    $duration = round($endTime - $startTime, 2);

    // 输出结果汇总
    echo "\n";
    echo "================================================================\n";
    echo "  扫描结果汇总\n";
    echo "================================================================\n\n";
    echo "  目标地址:   {$host}\n";
    echo "  扫描端口数: {$total}\n";
    echo "  开放端口数: " . count($openPorts) . "\n";
    echo "  扫描耗时:   {$duration} 秒\n";
    echo "\n";

    if (count($openPorts) > 0) {
        echo "  开放端口列表:\n";
        echo "  " . str_repeat("-", 56) . "\n";
        echo "  " . str_pad("端口", 10) . str_pad("服务名称", 46) . "\n";
        echo "  " . str_repeat("-", 56) . "\n";

        foreach ($openPorts as $item) {
            echo "  " . str_pad($item['port'], 10) . str_pad($item['service'], 46) . "\n";
        }
    } else {
        echo "  未发现开放端口\n";
    }

    echo "\n";
    echo "================================================================\n";
}

// 运行主程序
main($argc, $argv);
