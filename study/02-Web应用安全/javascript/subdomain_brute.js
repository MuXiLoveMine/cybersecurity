/**
 * ============================================================
 * 子域名爆破工具 (Subdomain Brute-force Tool)
 * ============================================================
 *
 * 【原理说明】
 * 子域名爆破是信息收集中的重要步骤，用于发现目标组织的所有子域名，
 * 从而扩大攻击面，找到更多可能存在漏洞的入口点。
 *
 * 本工具使用 DNS 解析方式进行子域名爆破：
 *   - 遍历子域名字典中的每个前缀
 *   - 拼接目标域名形成完整子域名（如 www.example.com）
 *   - 使用 DNS 解析查询该域名是否存在对应的 IP 地址
 *   - 如果解析成功，说明该子域名存在
 *
 * 【子域名发现方法对比】
 *   - DNS 字典爆破：速度快，但依赖字典质量
 *   - 搜索引擎爬虫：通过搜索引擎发现子域名
 *   - SSL 证书透明度：通过 CT 日志发现子域名
 *   - 区域传送（AXFR）：利用 DNS 服务器配置漏洞
 *   - 内容安全策略（CSP）：从 CSP 报告中发现子域名
 *
 * 【使用方法】
 *   node subdomain_brute.js <目标域名> [字典文件] [并发数]
 *
 * 【参数说明】
 *   目标域名  - 必填，根域名，例如 example.com（不需要加 www）
 *   字典文件  - 可选，自定义子域名字典文件路径，每行一个前缀
 *               不提供则使用内置字典
 *   并发数    - 可选，DNS 查询并发数，默认 50
 *
 * 【示例】
 *   node subdomain_brute.js example.com
 *   node subdomain_brute.js example.com subdomains.txt 100
 *   node subdomain_brute.js baidu.com dict.txt 200
 *
 * 【免责声明】
 *   本工具仅供学习和授权测试使用，用于合法的信息收集。
 * ============================================================
 */

const dns = require('dns');   // Node.js 内置 DNS 模块

// ============================================================
// 内置子域名字典（常见子域名前缀）
// 当用户不提供字典文件时使用此内置字典
// ============================================================
const DEFAULT_SUBDOMAINS = [
  // 常见通用前缀
  'www',
  'mail',
  'smtp',
  'pop',
  'pop3',
  'imap',
  'ftp',
  'webmail',
  'admin',
  'administrator',
  'manage',
  'manager',
  'backend',
  'console',
  'dashboard',
  'test',
  'testing',
  'dev',
  'devel',
  'development',
  'stage',
  'staging',
  'prod',
  'production',
  'demo',
  'example',
  'sample',
  'api',
  'api2',
  'api3',
  'api-v1',
  'api-v2',
  'graphql',
  'gateway',
  'gate',
  'proxy',
  'nginx',
  'apache',
  'iis',
  'web',
  'web1',
  'web2',
  'web3',
  'www1',
  'www2',
  'www3',
  'app',
  'apps',
  'application',
  'mobile',
  'm',
  'wap',
  'ios',
  'android',
  'cdn',
  'static',
  'img',
  'images',
  'image',
  'media',
  'video',
  'upload',
  'uploads',
  'download',
  'downloads',
  'files',
  'file',
  'docs',
  'doc',
  'document',
  'blog',
  'news',
  'forum',
  'bbs',
  'community',
  'shop',
  'store',
  'cart',
  'pay',
  'payment',
  'search',
  'cache',
  'redis',
  'db',
  'database',
  'mysql',
  'mssql',
  'oracle',
  'mongodb',
  'es',
  'elasticsearch',
  'mq',
  'rabbitmq',
  'kafka',
  'zookeeper',
  'jenkins',
  'git',
  'gitlab',
  'github',
  'gitee',
  'svn',
  'jira',
  'confluence',
  'wiki',
  'monitor',
  'monitoring',
  'prometheus',
  'grafana',
  'zabbix',
  'nagios',
  'log',
  'logs',
  'elk',
  'kibana',
  'graylog',
  'backup',
  'bak',
  'old',
  'new',
  'test1',
  'test2',
  'test3',
  'dev1',
  'dev2',
  'dev3',
  's1',
  's2',
  's3',
  'node1',
  'node2',
  'node3',
  'server1',
  'server2',
  'master',
  'slave',
  'worker',
  'a',
  'b',
  'c',
  'd',
  'mx',
  'mx1',
  'mx2',
  'ns',
  'ns1',
  'ns2',
  'dns',
  'dns1',
  'dns2',
  'autodiscover',
  'owa',
  'exchange',
  'sharepoint',
  'lync',
  'teams',
  'office',
  'crm',
  'erp',
  'oa',
  'hr',
  'mail2',
  'mail3',
  'secure',
  'ssl',
  'vpn',
  'remote',
  'rdp',
  'ssh',
  'telnet',
  'rsync',
  'ntp',
  'snmp',
  'ldap',
  'radius',
  'sso',
  'auth',
  'login',
  'signin',
  'signup',
  'register',
  'account',
  'user',
  'users',
  'member',
  'members',
  'profile',
  'my',
  'portal',
  'intranet',
  'extranet',
  'support',
  'help',
  'helpdesk',
  'ticket',
  'service',
  'status',
  'health',
  'metrics',
  'stats',
  'analytics',
  'report',
  'reports',
  'panel',
  'cpanel',
  'plesk',
  'directadmin',
  'whm',
  'phpmyadmin',
  'pma',
  'mysqladmin',
  'pgadmin',
  'phpinfo',
  'info',
  'about',
  'contact',
  'feedback',
  'survey',
  'career',
  'jobs',
  'job',
  'hr',
  'recruit',
  'partner',
  'affiliate',
  'reseller',
  'wholesale',
  'distributor',
  'supplier',
  'vendor',
  'b2b',
  'b2c',
  'o2o',
  'p2p',
  'game',
  'games',
  'play',
  'player',
  'video',
  'live',
  'tv',
  'radio',
  'music',
  'audio',
  'podcast',
  'ebook',
  'book',
  'library',
  'download',
  'mirror',
  'mirrors',
  'repo',
  'repository',
  'source',
  'code',
  'coding',
  'project',
  'projects',
  'lab',
  'labs',
  'research',
  'innovation',
  'rnd',
  'beta',
  'alpha',
  'preview',
  'early',
  'next',
  'nextgen',
  'new',
  'legacy',
  'archive',
  'history',
  'old',
  'deprecated',
];

// ============================================================
// 加载字典文件
// ============================================================
/**
 * 从文件加载子域名字典
 * @param {string} filePath - 字典文件路径
 * @returns {string[]} 子域名前缀数组
 */
function loadDict(filePath) {
  const fs = require('fs');
  try {
    const content = fs.readFileSync(filePath, 'utf-8');
    const lines = content.split(/\r?\n/)
      .map(line => line.trim().toLowerCase())
      .filter(line => line && !line.startsWith('#') && !line.includes(' '));
    return lines;
  } catch (err) {
    console.error(`[!] 加载字典文件失败: ${err.message}`);
    process.exit(1);
  }
}

// ============================================================
// DNS 解析函数
// ============================================================
/**
 * 解析域名的 A 记录（IPv4 地址）
 * @param {string} domain - 要解析的域名
 * @param {number} timeout - 超时时间（毫秒）
 * @returns {Promise<{domain: string, exists: boolean, ips: string[]}>}
 */
function resolveDomain(domain, timeout = 5000) {
  return new Promise((resolve) => {
    // 设置超时定时器
    const timer = setTimeout(() => {
      // 超时，认为域名不存在或 DNS 服务器无响应
      resolve({
        domain,
        exists: false,
        ips: [],
        error: 'timeout',
      });
    }, timeout);

    // 使用 dns.resolve4 查询 A 记录
    dns.resolve4(domain, (err, addresses) => {
      clearTimeout(timer);

      if (err) {
        // 常见错误码：
        // ENOTFOUND - 域名不存在（NXDOMAIN）
        // ETIMEOUT  - 查询超时
        // ESERVFAIL - 服务器失败
        if (err.code === 'ENOTFOUND' || err.code === 'ENODATA') {
          resolve({
            domain,
            exists: false,
            ips: [],
            error: err.code,
          });
        } else {
          // 其他错误（超时、服务器错误等）也视为不存在
          resolve({
            domain,
            exists: false,
            ips: [],
            error: err.code,
          });
        }
      } else {
        // 解析成功，域名存在
        resolve({
          domain,
          exists: true,
          ips: addresses,
        });
      }
    });
  });
}

/**
 * 同时解析 A 记录和 CNAME 记录，获取更全面的信息
 * @param {string} domain - 要解析的域名
 * @param {number} timeout - 超时时间
 * @returns {Promise<{domain: string, exists: boolean, ips: string[], cname: string}>}
 */
async function resolveDomainDetailed(domain, timeout = 5000) {
  const result = await resolveDomain(domain, timeout);

  if (result.exists) {
    // 尝试获取 CNAME 记录
    try {
      const cnameResult = await new Promise((resolve) => {
        dns.resolveCname(domain, (err, addresses) => {
          if (err) {
            resolve(null);
          } else {
            resolve(addresses[0] || null);
          }
        });
      });
      if (cnameResult) {
        result.cname = cnameResult;
      }
    } catch (e) {
      // CNAME 查询失败不影响主结果
    }
  }

  return result;
}

// ============================================================
// 子域名爆破主函数（并发控制）
// ============================================================
/**
 * 执行子域名爆破
 * @param {string} rootDomain - 根域名
 * @param {string[]} subdomains - 子域名前缀列表
 * @param {number} concurrency - 并发数
 * @returns {Promise<Array>} 发现的子域名列表
 */
async function subdomainBrute(rootDomain, subdomains, concurrency = 50) {
  const foundSubdomains = [];  // 存储发现的子域名
  let currentIndex = 0;        // 当前扫描索引
  let scannedCount = 0;        // 已扫描数量
  const total = subdomains.length;

  console.log(`\n[*] 目标根域名: ${rootDomain}`);
  console.log(`[*] 子域名数量: ${total}`);
  console.log(`[*] 并发数: ${concurrency}`);
  console.log('='.repeat(60));

  const startTime = Date.now();

  // ============================================================
  // 并发工作者函数
  // 每个工作者不断取下一个子域名进行解析
  // ============================================================
  async function worker() {
    while (currentIndex < total) {
      const index = currentIndex;
      currentIndex++;
      const prefix = subdomains[index];
      const fullDomain = `${prefix}.${rootDomain}`;

      // 执行 DNS 解析
      const result = await resolveDomain(fullDomain);
      scannedCount++;

      // 如果域名存在，记录并打印
      if (result.exists) {
        foundSubdomains.push({
          domain: fullDomain,
          ips: result.ips,
          cname: result.cname || '',
        });
        const ipStr = result.ips.length > 0 ? result.ips.join(', ') : '未知IP';
        console.log(`\n[+] ${fullDomain} -> ${ipStr}`);
      }

      // 进度更新
      if (scannedCount % 50 === 0 || scannedCount === total) {
        const progress = ((scannedCount / total) * 100).toFixed(1);
        process.stdout.write(`\r[*] 进度: ${scannedCount}/${total} (${progress}%)  发现: ${foundSubdomains.length}`);
      }
    }
  }

  // 启动并发工作者
  const workers = [];
  for (let i = 0; i < concurrency; i++) {
    workers.push(worker());
  }

  // 等待所有工作者完成
  await Promise.all(workers);

  const endTime = Date.now();
  const duration = ((endTime - startTime) / 1000).toFixed(2);

  // ============================================================
  // 输出结果汇总
  // ============================================================
  console.log('\n' + '='.repeat(60));
  console.log(`[*] 扫描完成！耗时: ${duration} 秒`);
  console.log(`[*] 扫描子域名总数: ${total}`);
  console.log(`[+] 发现有效子域名: ${foundSubdomains.length} 个`);

  if (foundSubdomains.length > 0) {
    console.log('\n[*] 发现的子域名列表:');
    console.log('-'.repeat(60));

    // 按子域名字母顺序排序
    foundSubdomains.sort((a, b) => a.domain.localeCompare(b.domain));

    foundSubdomains.forEach((item, index) => {
      const ipStr = item.ips.length > 0 ? item.ips.join(', ') : '未知';
      console.log(`  [${index + 1}] ${item.domain}`);
      console.log(`      IP: ${ipStr}`);
      if (item.cname) {
        console.log(`      CNAME: ${item.cname}`);
      }
    });
  }

  return foundSubdomains;
}

// ============================================================
// 通配符 DNS 检测
// （有些域名配置了泛解析，所有子域名都会解析到同一个IP）
// ============================================================
/**
 * 检测目标域名是否启用了通配符解析（泛解析）
 * 如果存在通配符，爆破结果将不准确
 * @param {string} rootDomain - 根域名
 * @returns {Promise<{wildcard: boolean, ips: string[]}>}
 */
async function checkWildcard(rootDomain) {
  // 生成一个极不可能存在的随机子域名
  const randomSub = `xxxtest-not-exist-${Date.now()}-${Math.random().toString(36).substr(2, 8)}`;
  const testDomain = `${randomSub}.${rootDomain}`;

  console.log(`[*] 检测通配符 DNS...`);

  const result = await resolveDomain(testDomain, 5000);

  if (result.exists) {
    console.log(`[!] 警告：检测到通配符 DNS 解析（泛解析）`);
    console.log(`[!] 随机域名 ${testDomain} 解析到了 IP: ${result.ips.join(', ')}`);
    console.log(`[!] 这意味着爆破结果可能包含大量假阳性`);
    console.log(`[!] 建议使用其他手段（如搜索引擎、SSL证书）辅助验证`);
    return { wildcard: true, ips: result.ips };
  } else {
    console.log(`[*] 未检测到通配符 DNS`);
    return { wildcard: false, ips: [] };
  }
}

// ============================================================
// 主程序入口
// ============================================================
function main() {
  const args = process.argv.slice(2);

  if (args.length < 1) {
    console.log('用法: node subdomain_brute.js <目标域名> [字典文件] [并发数]');
    console.log('示例: node subdomain_brute.js example.com');
    console.log('      node subdomain_brute.js example.com subdomains.txt 100');
    process.exit(1);
  }

  const rootDomain = args[0];
  const dictFile = args[1] || null;
  const concurrency = parseInt(args[2]) || 50;

  // 参数检查
  if (concurrency < 1 || concurrency > 500) {
    console.error('[!] 错误：并发数应在 1-500 之间');
    process.exit(1);
  }

  // 简单验证域名格式
  if (!/^[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+$/.test(rootDomain)) {
    console.error('[!] 错误：域名格式无效');
    process.exit(1);
  }

  // 加载字典
  let subdomains;
  if (dictFile) {
    subdomains = loadDict(dictFile);
    console.log(`[*] 使用自定义字典: ${dictFile} (${subdomains.length} 条)`);
  } else {
    subdomains = DEFAULT_SUBDOMAINS;
    console.log(`[*] 使用内置字典 (${subdomains.length} 条)`);
  }

  // 去重
  subdomains = [...new Set(subdomains)];

  console.log('\n[*] 子域名爆破工具');
  console.log('[*] ' + '='.repeat(50));

  // 先检测通配符 DNS
  checkWildcard(rootDomain)
    .then(() => {
      // 执行子域名爆破
      return subdomainBrute(rootDomain, subdomains, concurrency);
    })
    .catch((err) => {
      console.error('\n[!] 扫描出错:', err.message);
      process.exit(1);
    });
}

// 运行主程序
main();
