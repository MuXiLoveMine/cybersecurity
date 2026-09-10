/**
 * ============================================================
 * Web 目录爆破工具 (Directory Brute-force Tool)
 * ============================================================
 *
 * 【原理说明】
 * 目录爆破（也叫目录扫描/路径爆破）是 Web 渗透测试中的常用技术，
 * 通过遍历预设的字典文件，向目标 Web 服务器发起 HTTP 请求，
 * 根据响应状态码和响应长度判断路径是否存在，从而发现隐藏的
 * 目录、文件、备份文件、管理后台等敏感资源。
 *
 * 【判断依据】
 *   - 状态码 200：页面存在（可能是有效路径）
 *   - 状态码 301/302：重定向（通常也表示路径存在）
 *   - 状态码 403：禁止访问（路径存在但无权限）
 *   - 状态码 404：未找到（路径不存在）
 *   - 响应长度：有些网站会自定义404页面，需要结合长度判断
 *
 * 【使用方法】
 *   node dir_brute.js <目标URL> [字典文件] [线程数] [后缀列表]
 *
 * 【参数说明】
 *   目标URL   - 必填，目标网站地址，例如 http://example.com
 *   字典文件  - 可选，自定义字典文件路径，每行一个路径
 *               不提供则使用内置字典
 *   线程数    - 可选，并发请求数，默认 20
 *   后缀列表  - 可选，要追加的文件后缀，用逗号分隔
 *               例如: .php,.html,.bak,.txt
 *
 * 【示例】
 *   node dir_brute.js http://127.0.0.1
 *   node dir_brute.js http://example.com dict.txt 30
 *   node dir_brute.js http://example.com dict.txt 20 .php,.html,.bak
 *
 * 【免责声明】
 *   本工具仅供学习和授权测试使用，未经授权对他人网站进行扫描属于违法行为。
 * ============================================================
 */

const http = require('http');   // Node.js 内置 HTTP 模块
const https = require('https'); // Node.js 内置 HTTPS 模块
const fs = require('fs');       // Node.js 内置文件系统模块
const url = require('url');     // Node.js 内置 URL 处理模块

// ============================================================
// 内置字典 - 常见 Web 目录和文件路径
// 当用户不提供字典文件时使用此内置字典
// ============================================================
const DEFAULT_PATHS = [
  // 常见目录
  '/admin',
  '/admin/login',
  '/admin/index',
  '/administrator',
  '/login',
  '/register',
  '/user',
  '/users',
  '/member',
  '/members',
  '/manage',
  '/manager',
  '/backend',
  '/console',
  '/dashboard',
  '/upload',
  '/uploads',
  '/files',
  '/download',
  '/downloads',
  '/backup',
  '/backups',
  '/bak',
  '/test',
  '/tests',
  '/dev',
  '/debug',
  '/api',
  '/api/v1',
  '/api/v2',
  '/graphql',
  '/phpmyadmin',
  '/pma',
  '/wp-admin',
  '/wp-login',
  '/wp-content',
  '/wp-includes',
  '/drupal',
  '/joomla',
  '/administrator/index.php',
  '/config',
  '/conf',
  '/.git',
  '/.svn',
  '/.env',
  '/.htaccess',
  '/.htpasswd',
  '/robots.txt',
  '/sitemap.xml',
  '/crossdomain.xml',
  '/phpinfo.php',
  '/info.php',
  '/test.php',
  '/index.php',
  '/index.html',
  '/default.html',
  '/home',
  '/about',
  '/contact',
  '/search',
  '/news',
  '/forum',
  '/bbs',
  '/blog',
  '/tmp',
  '/temp',
  '/cache',
  '/data',
  '/database',
  '/install',
  '/setup',
  '/readme',
  '/README',
  '/CHANGELOG',
  '/changelog',
  '/LICENSE',
  '/license',
];

// 常见文件后缀
const DEFAULT_EXTENSIONS = [''];  // 空字符串表示不加后缀（原始路径）

// ============================================================
// 发起 HTTP/HTTPS 请求
// ============================================================
/**
 * 向目标 URL 发起 HTTP 请求，返回响应信息
 * @param {string} targetUrl - 目标 URL
 * @param {number} timeout - 请求超时时间（毫秒）
 * @returns {Promise<{statusCode: number, contentLength: number, url: string}>}
 */
function request(targetUrl, timeout = 5000) {
  return new Promise((resolve, reject) => {
    // 解析 URL，确定使用 http 还是 https 模块
    const parsedUrl = new URL(targetUrl);
    const module = parsedUrl.protocol === 'https:' ? https : http;

    const options = {
      hostname: parsedUrl.hostname,
      port: parsedUrl.port || (parsedUrl.protocol === 'https:' ? 443 : 80),
      path: parsedUrl.pathname + parsedUrl.search,
      method: 'GET',
      timeout: timeout,
      // 伪造浏览器 User-Agent，避免被简单的WAF拦截
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
      },
    };

    const req = module.request(options, (res) => {
      let data = '';
      // 只接收前 10KB 数据用于计算长度，避免下载大文件
      const maxSize = 10240;

      res.on('data', (chunk) => {
        data += chunk.toString();
        if (data.length > maxSize) {
          // 数据足够时销毁响应，节省带宽
          res.destroy();
        }
      });

      res.on('end', () => {
        resolve({
          statusCode: res.statusCode,
          contentLength: data.length || parseInt(res.headers['content-length']) || 0,
          url: targetUrl,
          redirectUrl: res.headers['location'] || '',
        });
      });

      res.on('close', () => {
        // 响应被提前关闭（数据足够时）
        resolve({
          statusCode: res.statusCode,
          contentLength: data.length || parseInt(res.headers['content-length']) || 0,
          url: targetUrl,
          redirectUrl: res.headers['location'] || '',
        });
      });
    });

    // 请求超时处理
    req.on('timeout', () => {
      req.destroy();
      reject(new Error('timeout'));
    });

    // 请求错误处理（网络错误、DNS失败等）
    req.on('error', (err) => {
      reject(err);
    });

    // 发送请求
    req.end();
  });
}

// ============================================================
// 加载字典文件
// ============================================================
/**
 * 从文件加载字典，每行一个路径
 * @param {string} filePath - 字典文件路径
 * @returns {string[]} 路径数组
 */
function loadDict(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf-8');
    // 按行分割，过滤空行和注释行（以 # 开头）
    const lines = content.split(/\r?\n/)
      .map(line => line.trim())
      .filter(line => line && !line.startsWith('#'));
    return lines;
  } catch (err) {
    console.error(`[!] 加载字典文件失败: ${err.message}`);
    process.exit(1);
  }
}

// ============================================================
// 生成完整路径列表（添加后缀）
// ============================================================
/**
 * 根据基础路径和后缀列表，生成所有要测试的路径
 * @param {string[]} paths - 基础路径列表
 * @param {string[]} extensions - 文件后缀列表
 * @returns {string[]} 完整路径列表
 */
function generatePaths(paths, extensions) {
  const result = [];

  for (const path of paths) {
    for (const ext of extensions) {
      // 确保路径以 / 开头
      let fullPath = path.startsWith('/') ? path : '/' + path;
      // 添加后缀（如果路径已经有后缀则跳过添加新后缀）
      if (ext && !fullPath.endsWith(ext) && !/\.\w+$/.test(fullPath)) {
        fullPath += ext;
      }
      result.push(fullPath);
    }
  }

  // 去重
  return [...new Set(result)];
}

// ============================================================
// 目录爆破主函数（并发控制）
// ============================================================
/**
 * 执行目录爆破
 * @param {string} baseUrl - 目标基础 URL
 * @param {string[]} paths - 要测试的路径列表
 * @param {number} threads - 并发线程数
 * @returns {Promise<Array>} 发现的有效路径
 */
async function dirBrute(baseUrl, paths, threads = 20) {
  const foundPaths = [];       // 存储发现的有效路径
  let currentIndex = 0;        // 当前扫描索引
  let scannedCount = 0;        // 已扫描数量
  let errorCount = 0;          // 错误计数
  const totalPaths = paths.length;

  // 确保基础 URL 不以 / 结尾
  const base = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;

  console.log(`\n[*] 目标: ${base}`);
  console.log(`[*] 路径总数: ${totalPaths}`);
  console.log(`[*] 线程数: ${threads}`);
  console.log('='.repeat(60));

  const startTime = Date.now();

  // ============================================================
  // 并发工作者函数
  // ============================================================
  async function worker() {
    while (currentIndex < totalPaths) {
      const index = currentIndex;
      currentIndex++;
      const path = paths[index];
      const targetUrl = base + path;

      try {
        const result = await request(targetUrl);
        scannedCount++;

        // 根据状态码判断路径是否存在
        const statusCode = result.statusCode;

        // 状态码分类：
        // 2xx - 成功（路径存在）
        // 3xx - 重定向（路径通常存在）
        // 403 - 禁止访问（路径存在但无权限）
        // 404 - 未找到（路径不存在）
        // 5xx - 服务器错误（路径可能存在但有问题）
        if (statusCode === 200) {
          foundPaths.push({ path, statusCode, length: result.contentLength, type: '存在' });
          console.log(`\n[+] [200] ${path} (长度: ${result.contentLength})`);
        } else if (statusCode === 403) {
          foundPaths.push({ path, statusCode, length: result.contentLength, type: '禁止访问' });
          console.log(`\n[*] [403] ${path} (禁止访问)`);
        } else if (statusCode >= 300 && statusCode < 400) {
          foundPaths.push({
            path,
            statusCode,
            length: result.contentLength,
            type: '重定向',
            redirect: result.redirectUrl,
          });
          console.log(`\n[*] [${statusCode}] ${path} -> ${result.redirectUrl || '未知'}`);
        }

      } catch (err) {
        scannedCount++;
        errorCount++;
      }

      // 实时进度更新（使用 \r 回车符实现同一行刷新）
      if (scannedCount % 10 === 0 || scannedCount === totalPaths) {
        const progress = ((scannedCount / totalPaths) * 100).toFixed(1);
        process.stdout.write(`\r[*] 进度: ${scannedCount}/${totalPaths} (${progress}%)  错误: ${errorCount}`);
      }
    }
  }

  // 启动指定数量的工作线程
  const workers = [];
  for (let i = 0; i < threads; i++) {
    workers.push(worker());
  }

  // 等待所有线程完成
  await Promise.all(workers);

  const endTime = Date.now();
  const duration = ((endTime - startTime) / 1000).toFixed(2);

  // ============================================================
  // 输出结果汇总
  // ============================================================
  console.log('\n' + '='.repeat(60));
  console.log(`[*] 扫描完成！耗时: ${duration} 秒`);
  console.log(`[*] 总请求数: ${totalPaths}`);
  console.log(`[*] 错误数: ${errorCount}`);
  console.log(`[+] 发现路径: ${foundPaths.length} 个`);

  if (foundPaths.length > 0) {
    console.log('\n[*] 发现的路径:');
    console.log('-'.repeat(50));
    foundPaths.sort((a, b) => a.statusCode - b.statusCode);
    foundPaths.forEach((item) => {
      console.log(`  [${item.statusCode}] ${item.path}\t${item.type}`);
    });
  }

  return foundPaths;
}

// ============================================================
// 主程序入口
// ============================================================
function main() {
  const args = process.argv.slice(2);

  if (args.length < 1) {
    console.log('用法: node dir_brute.js <目标URL> [字典文件] [线程数] [后缀列表]');
    console.log('示例: node dir_brute.js http://127.0.0.1 dict.txt 20 .php,.html,.bak');
    process.exit(1);
  }

  const targetUrl = args[0];
  const dictFile = args[1] || null;
  const threads = parseInt(args[2]) || 20;
  const extInput = args[3] || '';

  // 加载字典
  let paths;
  if (dictFile) {
    paths = loadDict(dictFile);
    console.log(`[*] 使用自定义字典: ${dictFile} (${paths.length} 条)`);
  } else {
    paths = DEFAULT_PATHS;
    console.log(`[*] 使用内置字典 (${paths.length} 条)`);
  }

  // 解析后缀列表
  let extensions = [...DEFAULT_EXTENSIONS];
  if (extInput) {
    const exts = extInput.split(',').map(e => e.trim()).filter(e => e);
    extensions = extensions.concat(exts);
    console.log(`[*] 文件后缀: ${exts.join(', ')}`);
  }

  // 生成完整路径列表
  const allPaths = generatePaths(paths, extensions);

  // 参数检查
  if (threads < 1 || threads > 200) {
    console.error('[!] 错误：线程数应在 1-200 之间');
    process.exit(1);
  }

  // 验证 URL 格式
  try {
    new URL(targetUrl);
  } catch (err) {
    console.error('[!] 错误：URL 格式无效，请包含 http:// 或 https://');
    process.exit(1);
  }

  // 执行目录爆破
  dirBrute(targetUrl, allPaths, threads)
    .catch((err) => {
      console.error('\n[!] 扫描出错:', err.message);
      process.exit(1);
    });
}

// 运行主程序
main();
