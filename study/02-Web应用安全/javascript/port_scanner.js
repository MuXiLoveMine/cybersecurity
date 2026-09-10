/**
 * ============================================================
 * 端口扫描器 (Port Scanner)
 * ============================================================
 *
 * 【原理说明】
 * 端口扫描是网络安全测试中最基础的步骤之一，用于发现目标主机上开放的服务端口。
 * 本工具使用 TCP 全连接扫描（Full Connect Scan）原理：
 *   - 尝试与目标主机的指定端口建立 TCP 连接
 *   - 如果连接成功（三次握手完成），说明端口开放
 *   - 如果连接被拒绝（RST包）或超时，说明端口关闭或被防火墙过滤
 *
 * 【扫描方式对比】
 *   - TCP全连接扫描：最可靠、最易检测，需要完成完整三次握手
 *   - SYN半开扫描：只发送SYN包，不建立完整连接，更隐蔽（需要原始套接字权限）
 *   - UDP扫描：扫描UDP端口，不可靠且速度慢
 *
 * 【使用方法】
 *   node port_scanner.js <目标IP> [起始端口] [结束端口] [并发数]
 *
 * 【参数说明】
 *   目标IP    - 必填，要扫描的主机IP地址或域名
 *   起始端口  - 可选，扫描范围起始端口，默认 1
 *   结束端口  - 可选，扫描范围结束端口，默认 1024
 *   并发数    - 可选，同时进行的连接数，默认 100
 *
 * 【示例】
 *   node port_scanner.js 127.0.0.1
 *   node port_scanner.js 192.168.1.1 1 65535 200
 *   node port_scanner.js localhost 80 1000 50
 *
 * 【免责声明】
 *   本工具仅供学习和授权测试使用，未经授权扫描他人网络属于违法行为。
 * ============================================================
 */

const net = require('net');     // Node.js 内置 net 模块，用于 TCP 网络操作

// ============================================================
// 常见端口与服务对应表（部分常用端口）
// 参考：IANA 端口分配标准
// ============================================================
const WELL_KNOWN_PORTS = {
  21: 'FTP (文件传输协议)',
  22: 'SSH (安全外壳协议)',
  23: 'Telnet (远程终端协议)',
  25: 'SMTP (简单邮件传输协议)',
  53: 'DNS (域名系统)',
  80: 'HTTP (超文本传输协议)',
  110: 'POP3 (邮局协议v3)',
  111: 'RPC (远程过程调用)',
  135: 'MS RPC (微软远程过程调用)',
  139: 'NetBIOS (网络基本输入输出系统)',
  143: 'IMAP (互联网消息访问协议)',
  443: 'HTTPS (安全超文本传输协议)',
  445: 'SMB (服务器消息块)',
  993: 'IMAPS (安全IMAP)',
  995: 'POP3S (安全POP3)',
  1080: 'SOCKS (代理协议)',
  1433: 'MSSQL (微软SQL Server)',
  1521: 'Oracle DB (Oracle数据库)',
  3306: 'MySQL (MySQL数据库)',
  3389: 'RDP (远程桌面协议)',
  5432: 'PostgreSQL (PostgreSQL数据库)',
  5900: 'VNC (虚拟网络计算)',
  6379: 'Redis (Redis内存数据库)',
  8080: 'HTTP-Proxy (HTTP代理/备用端口)',
  8443: 'HTTPS-Alt (HTTPS备用端口)',
  8888: 'HTTP-Alt (HTTP备用端口)',
  27017: 'MongoDB (MongoDB数据库)',
};

// ============================================================
// 扫描单个端口
// ============================================================
/**
 * 扫描指定主机的单个端口
 * @param {string} host - 目标主机IP或域名
 * @param {number} port - 目标端口号
 * @param {number} timeout - 连接超时时间（毫秒）
 * @returns {Promise<{port: number, open: boolean, service: string, error?: string}>}
 */
function scanPort(host, port, timeout = 2000) {
  return new Promise((resolve) => {
    // 创建 TCP 套接字
    const socket = new net.Socket();

    // 设置连接超时
    socket.setTimeout(timeout);

    // 连接成功事件 - 端口开放
    socket.on('connect', () => {
      socket.destroy(); // 立即关闭连接，避免占用资源
      resolve({
        port,
        open: true,
        service: WELL_KNOWN_PORTS[port] || '未知服务',
      });
    });

    // 连接超时事件 - 端口可能被过滤或关闭
    socket.on('timeout', () => {
      socket.destroy();
      resolve({
        port,
        open: false,
        service: '',
        error: 'timeout',
      });
    });

    // 连接错误事件 - 端口关闭（收到 RST 包）
    socket.on('error', (err) => {
      socket.destroy();
      resolve({
        port,
        open: false,
        service: '',
        error: err.code,
      });
    });

    // 发起连接
    socket.connect(port, host);
  });
}

// ============================================================
// 并发端口扫描（异步并发控制）
// ============================================================
/**
 * 使用异步并发方式扫描端口范围
 * @param {string} host - 目标主机
 * @param {number} startPort - 起始端口
 * @param {number} endPort - 结束端口
 * @param {number} concurrency - 并发数
 * @param {number} timeout - 超时时间
 * @returns {Promise<Array>} 开放端口列表
 */
async function portScan(host, startPort, endPort, concurrency = 100, timeout = 2000) {
  const totalPorts = endPort - startPort + 1;
  const openPorts = [];    // 存储开放的端口
  let currentIndex = 0;    // 当前扫描到的端口索引
  let scannedCount = 0;    // 已扫描的端口数量

  console.log(`\n[*] 开始扫描目标: ${host}`);
  console.log(`[*] 端口范围: ${startPort} - ${endPort} (共 ${totalPorts} 个端口)`);
  console.log(`[*] 并发数: ${concurrency}`);
  console.log(`[*] 超时时间: ${timeout}ms`);
  console.log('='.repeat(60));

  const startTime = Date.now();

  // ============================================================
  // 并发控制核心逻辑：工作线程模式
  // 启动 concurrency 个"工作线程"，每个线程不断取下一个端口扫描
  // 直到所有端口扫描完毕
  // ============================================================
  async function worker() {
    while (currentIndex <= endPort - startPort) {
      // 原子性获取当前端口索引（JS单线程，这里不需要锁）
      const port = startPort + currentIndex;
      currentIndex++;

      // 扫描当前端口
      const result = await scanPort(host, port, timeout);
      scannedCount++;

      // 如果端口开放，记录并打印
      if (result.open) {
        openPorts.push(result);
        console.log(`[+] 端口 ${result.port} 开放 - ${result.service}`);
      }

      // 每扫描100个端口打印一次进度
      if (scannedCount % 100 === 0 || scannedCount === totalPorts) {
        const progress = ((scannedCount / totalPorts) * 100).toFixed(1);
        process.stdout.write(`\r[*] 扫描进度: ${scannedCount}/${totalPorts} (${progress}%)`);
      }
    }
  }

  // 启动指定数量的并发工作者
  const workers = [];
  for (let i = 0; i < concurrency; i++) {
    workers.push(worker());
  }

  // 等待所有工作者完成
  await Promise.all(workers);

  const endTime = Date.now();
  const duration = ((endTime - startTime) / 1000).toFixed(2);

  // ============================================================
  // 输出扫描结果汇总
  // ============================================================
  console.log('\n' + '='.repeat(60));
  console.log(`[*] 扫描完成！耗时: ${duration} 秒`);
  console.log(`[*] 扫描端口总数: ${totalPorts}`);
  console.log(`[+] 发现开放端口: ${openPorts.length} 个`);

  if (openPorts.length > 0) {
    console.log('\n[*] 开放端口列表:');
    console.log('-'.repeat(40));
    // 按端口号排序
    openPorts.sort((a, b) => a.port - b.port);
    openPorts.forEach((p) => {
      console.log(`  ${p.port}/tcp\t开放\t${p.service}`);
    });
  }

  return openPorts;
}

// ============================================================
// 命令行参数解析与主程序入口
// ============================================================
function main() {
  // 解析命令行参数
  // process.argv[0] = node 路径
  // process.argv[1] = 脚本路径
  // process.argv[2] = 目标IP
  // process.argv[3] = 起始端口
  // process.argv[4] = 结束端口
  // process.argv[5] = 并发数
  const args = process.argv.slice(2);

  if (args.length < 1) {
    console.log('用法: node port_scanner.js <目标IP> [起始端口] [结束端口] [并发数]');
    console.log('示例: node port_scanner.js 127.0.0.1 1 1024 100');
    process.exit(1);
  }

  const host = args[0];
  const startPort = parseInt(args[1]) || 1;
  const endPort = parseInt(args[2]) || 1024;
  const concurrency = parseInt(args[3]) || 100;

  // 参数合法性检查
  if (startPort < 1 || endPort > 65535 || startPort > endPort) {
    console.error('[!] 错误：端口范围无效，请输入 1-65535 范围内的有效端口');
    process.exit(1);
  }

  if (concurrency < 1 || concurrency > 1000) {
    console.error('[!] 错误：并发数应在 1-1000 之间');
    process.exit(1);
  }

  // 执行扫描
  portScan(host, startPort, endPort, concurrency)
    .catch((err) => {
      console.error('\n[!] 扫描出错:', err.message);
      process.exit(1);
    });
}

// 运行主程序
main();
