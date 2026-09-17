/**
 * ============================================================
 * HTTP 安全响应头检测工具 (HTTP Security Header Checker)
 * ============================================================
 *
 * 【原理说明】
 * HTTP 安全响应头是 Web 安全防护的重要组成部分，通过在 HTTP 响应中
 * 设置特定的头部字段，可以有效防止多种 Web 攻击，如 XSS、点击劫持、
 * MIME 嗅探、信息泄露等。
 *
 * 本工具检测以下常见的安全响应头：
 *
 * 1. X-Frame-Options
 *    - 作用：防止点击劫持（Clickjacking）攻击
 *    - 控制页面是否可以被嵌入到 iframe 中
 *    - 可选值：DENY / SAMEORIGIN / ALLOW-FROM uri
 *
 * 2. X-XSS-Protection
 *    - 作用：启用浏览器内置的 XSS 过滤器
 *    - 注意：现代浏览器已逐渐废弃，推荐使用 CSP 替代
 *    - 可选值：0 / 1 / 1; mode=block
 *
 * 3. X-Content-Type-Options
 *    - 作用：防止 MIME 类型嗅探攻击
 *    - 强制浏览器遵循服务器声明的 Content-Type
 *    - 推荐值：nosniff
 *
 * 4. Content-Security-Policy (CSP)
 *    - 作用：内容安全策略，防御 XSS 和数据注入攻击
 *    - 通过白名单机制控制资源加载来源
 *    - 是目前最强大的 XSS 防护手段
 *
 * 5. Strict-Transport-Security (HSTS)
 *    - 作用：强制使用 HTTPS 连接
 *    - 防止协议降级攻击和 Cookie 劫持
 *    - 包含 max-age、includeSubDomains、preload 等指令
 *
 * 6. Referrer-Policy
 *    - 作用：控制 Referer 头信息的发送
 *    - 防止敏感信息通过 URL 泄露
 *    - 推荐值：no-referrer / strict-origin-when-cross-origin
 *
 * 7. Permissions-Policy
 *    - 作用：控制浏览器功能/API 的使用权限
 *    - 如摄像头、麦克风、地理位置、全屏等
 *    - 旧版名为 Feature-Policy
 *
 * 【使用方法】
 *   node http_header_check.js <目标URL>
 *
 * 【参数说明】
 *   目标URL  - 必填，目标网站 URL，例如 https://example.com
 *
 * 【示例】
 *   node http_header_check.js https://www.example.com
 *   node http_header_check.js http://127.0.0.1
 *
 * 【免责声明】
 *   本工具仅供学习和授权测试使用，用于检测自身网站安全配置。
 * ============================================================
 */

const http = require('http');
const https = require('https');

// ============================================================
// 安全头配置定义
// 每个安全头的详细说明、风险等级和修复建议
// ============================================================
const SECURITY_HEADERS = [
  {
    name: 'X-Frame-Options',
    description: '防止点击劫持攻击，控制页面是否可被嵌入 iframe',
    risk: '中',
    recommendations: [
      '推荐设置为 DENY 或 SAMEORIGIN',
      'DENY: 禁止任何页面嵌入',
      'SAMEORIGIN: 仅允许同域名页面嵌入',
      '注意：CSP 的 frame-ancestors 指令优先级更高',
    ],
    validate: (value) => {
      const v = value.toLowerCase().trim();
      if (v === 'deny' || v === 'sameorigin') {
        return { safe: true, message: '配置正确' };
      }
      if (v.startsWith('allow-from')) {
        return { safe: true, message: '使用 ALLOW-FROM 配置（注意浏览器兼容性）' };
      }
      return { safe: false, message: '配置值不正确' };
    },
  },
  {
    name: 'X-XSS-Protection',
    description: '启用浏览器内置 XSS 过滤器',
    risk: '低',
    recommendations: [
      '推荐设置为 1; mode=block',
      '0: 禁用 XSS 过滤（不推荐）',
      '1: 启用 XSS 过滤，发现攻击时清理页面',
      '1; mode=block: 发现攻击时阻止页面渲染',
      '注意：现代浏览器推荐使用 CSP 替代此头',
    ],
    validate: (value) => {
      const v = value.toLowerCase().trim();
      if (v === '1; mode=block' || v === '1;mode=block') {
        return { safe: true, message: '配置正确（最佳实践）' };
      }
      if (v === '1' || v.startsWith('1;')) {
        return { safe: true, message: '已启用，建议使用 mode=block' };
      }
      if (v === '0') {
        return { safe: false, message: '已禁用 XSS 过滤器' };
      }
      return { safe: false, message: '配置值不正确' };
    },
  },
  {
    name: 'X-Content-Type-Options',
    description: '防止 MIME 类型嗅探攻击',
    risk: '中',
    recommendations: [
      '推荐设置为 nosniff',
      '强制浏览器遵循 Content-Type 声明的类型',
      '防止浏览器将非脚本文件当作脚本执行',
    ],
    validate: (value) => {
      const v = value.toLowerCase().trim();
      if (v === 'nosniff') {
        return { safe: true, message: '配置正确' };
      }
      return { safe: false, message: '配置值不正确，应为 nosniff' };
    },
  },
  {
    name: 'Content-Security-Policy',
    description: '内容安全策略，防御 XSS 和数据注入攻击',
    risk: '高',
    recommendations: [
      '配置内容安全策略（CSP）是防御 XSS 的最佳实践',
      '常用指令：',
      '  default-src: 默认资源加载策略',
      "  script-src: 控制脚本来源（'unsafe-inline' 会降低安全性）",
      "  style-src: 控制样式来源",
      '  img-src: 控制图片来源',
      '  frame-ancestors: 控制嵌入权限（替代 X-Frame-Options）',
      '  report-uri / report-to: 违规报告地址',
      "建议避免使用 'unsafe-inline' 和 'unsafe-eval'",
    ],
    validate: (value) => {
      const v = value.toLowerCase().trim();
      const issues = [];
      const warnings = [];

      // 检查是否包含 unsafe-inline
      if (v.includes("'unsafe-inline'")) {
        warnings.push("包含 'unsafe-inline'，会降低 XSS 防护能力");
      }

      // 检查是否包含 unsafe-eval
      if (v.includes("'unsafe-eval'")) {
        warnings.push("包含 'unsafe-eval'，存在代码注入风险");
      }

      // 检查是否有 script-src 指令
      if (!v.includes('script-src') && !v.includes('default-src')) {
        warnings.push('未设置 script-src 或 default-src');
      }

      if (issues.length > 0) {
        return { safe: false, message: issues.join('; ') };
      }
      if (warnings.length > 0) {
        return { safe: true, message: '已配置，警告: ' + warnings.join('; ') };
      }
      return { safe: true, message: '配置良好' };
    },
  },
  {
    name: 'Strict-Transport-Security',
    description: 'HTTP 严格传输安全，强制使用 HTTPS',
    risk: '高',
    recommendations: [
      '强制浏览器使用 HTTPS 访问网站',
      '防止协议降级攻击和 Cookie 劫持',
      '推荐配置：',
      '  max-age=31536000; includeSubDomains',
      '  max-age 单位为秒，建议至少一年（31536000）',
      '  includeSubDomains: 包含所有子域名',
      '  preload: 加入浏览器 HSTS 预加载列表',
      '注意：首次访问需通过 HTTPS 响应此头',
    ],
    validate: (value) => {
      const v = value.toLowerCase().trim();
      const match = v.match(/max-age=(\d+)/);

      if (!match) {
        return { safe: false, message: '缺少 max-age 指令' };
      }

      const maxAge = parseInt(match[1]);
      const warnings = [];

      if (maxAge < 31536000) {
        warnings.push(`max-age (${maxAge}秒) 较短，建议至少一年（31536000秒）`);
      }

      if (!v.includes('includesubdomains')) {
        warnings.push('未包含 includeSubDomains，子域名不受保护');
      }

      if (warnings.length > 0) {
        return { safe: true, message: '已启用，警告: ' + warnings.join('; ') };
      }

      return { safe: true, message: '配置良好' };
    },
  },
  {
    name: 'Referrer-Policy',
    description: '控制 Referer 头信息的发送，保护用户隐私',
    risk: '低',
    recommendations: [
      '控制浏览器发送 Referer 头的策略',
      '推荐值：',
      '  no-referrer: 不发送 Referer 信息',
      '  strict-origin-when-cross-origin: 跨域时只发送 origin',
      '  same-origin: 同域才发送完整 Referer',
      '  no-referrer-when-downgrade: HTTPS->HTTP 不发送',
      '防止 URL 中的敏感信息泄露',
    ],
    validate: (value) => {
      const v = value.toLowerCase().trim();
      const safeValues = [
        'no-referrer',
        'no-referrer-when-downgrade',
        'origin',
        'origin-when-cross-origin',
        'same-origin',
        'strict-origin',
        'strict-origin-when-cross-origin',
        'unsafe-url',
      ];

      if (safeValues.includes(v)) {
        if (v === 'unsafe-url') {
          return { safe: false, message: 'unsafe-url 会泄露完整 URL，不推荐' };
        }
        return { safe: true, message: '配置正确' };
      }
      return { safe: false, message: '配置值不正确' };
    },
  },
  {
    name: 'Permissions-Policy',
    description: '控制浏览器功能和 API 的使用权限',
    risk: '低',
    recommendations: [
      '控制网站可使用的浏览器功能',
      '常用功能：camera, microphone, geolocation, fullscreen 等',
      '推荐禁用不需要的功能：',
      '  Permissions-Policy: camera=(), microphone=(), geolocation=()',
      '旧版名为 Feature-Policy，已重命名为 Permissions-Policy',
    ],
    validate: (value) => {
      if (value && value.trim().length > 0) {
        return { safe: true, message: '已配置' };
      }
      return { safe: false, message: '配置值为空' };
    },
  },
];

// 信息泄露相关的响应头检查（额外检查）
const INFO_LEAK_HEADERS = [
  {
    name: 'Server',
    description: '服务器信息头',
    risk: '低',
    check: (value) => {
      if (value && value.trim()) {
        return {
          leak: true,
          message: `泄露服务器信息: ${value}`,
          suggestion: '建议隐藏或修改 Server 头，避免泄露具体版本信息',
        };
      }
      return { leak: false, message: '未发现（可能已隐藏）' };
    },
  },
  {
    name: 'X-Powered-By',
    description: '技术栈信息头',
    risk: '低',
    check: (value) => {
      if (value && value.trim()) {
        return {
          leak: true,
          message: `泄露技术栈信息: ${value}`,
          suggestion: '建议移除 X-Powered-By 头',
        };
      }
      return { leak: false, message: '未发现（已移除或未设置）' };
    },
  },
  {
    name: 'X-AspNet-Version',
    description: 'ASP.NET 版本信息',
    risk: '低',
    check: (value) => {
      if (value && value.trim()) {
        return {
          leak: true,
          message: `泄露 ASP.NET 版本: ${value}`,
          suggestion: '建议在 web.config 中设置 <httpRuntime enableVersionHeader="false" />',
        };
      }
      return { leak: false, message: '未发现' };
    },
  },
];

// Cookie 安全属性检查
const COOKIE_SECURITY = [
  {
    attribute: 'Secure',
    description: 'Cookie 仅通过 HTTPS 传输',
    check: (cookieStr) => cookieStr.toLowerCase().includes('secure'),
    suggestion: '为 Cookie 添加 Secure 属性，防止在 HTTP 中传输',
  },
  {
    attribute: 'HttpOnly',
    description: '禁止 JavaScript 访问 Cookie',
    check: (cookieStr) => cookieStr.toLowerCase().includes('httponly'),
    suggestion: '为 Cookie 添加 HttpOnly 属性，防御 XSS 窃取 Cookie',
  },
  {
    attribute: 'SameSite',
    description: '防止跨站请求伪造（CSRF）',
    check: (cookieStr) => /samesize\s*=/i.test(cookieStr) || /samesite/i.test(cookieStr),
    suggestion: '为 Cookie 设置 SameSite=Strict 或 SameSite=Lax',
  },
];

// ============================================================
// 发起 HTTP/HTTPS 请求（HEAD 方法，只获取响应头）
// ============================================================
/**
 * 使用 HEAD 方法获取响应头
 * @param {string} targetUrl - 目标 URL
 * @param {number} timeout - 超时时间
 * @returns {Promise<{statusCode: number, headers: Object, cookies: string[]}>}
 */
function requestHeaders(targetUrl, timeout = 10000) {
  return new Promise((resolve, reject) => {
    const parsedUrl = new URL(targetUrl);
    const module = parsedUrl.protocol === 'https:' ? https : http;

    const options = {
      hostname: parsedUrl.hostname,
      port: parsedUrl.port || (parsedUrl.protocol === 'https:' ? 443 : 80),
      path: parsedUrl.pathname + parsedUrl.search,
      method: 'HEAD', // 使用 HEAD 方法，只获取头部，节省带宽
      timeout: timeout,
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      },
    };

    const req = module.request(options, (res) => {
      // 收集所有 Set-Cookie 头
      const cookies = res.headers['set-cookie'] || [];

      resolve({
        statusCode: res.statusCode,
        headers: res.headers,
        cookies: cookies,
      });

      // 不需要接收 body，直接销毁响应
      res.destroy();
    });

    req.on('timeout', () => {
      req.destroy();
      reject(new Error('请求超时'));
    });

    req.on('error', (err) => {
      reject(err);
    });

    req.end();
  });
}

// ============================================================
// 安全头检测主函数
// ============================================================
/**
 * 检测目标 URL 的 HTTP 安全响应头配置
 * @param {string} urlStr - 目标 URL
 */
async function checkSecurityHeaders(urlStr) {
  console.log('\n' + '='.repeat(60));
  console.log('[*] HTTP 安全响应头检测工具');
  console.log('='.repeat(60));
  console.log(`[*] 目标 URL: ${urlStr}`);

  let result;
  try {
    result = await requestHeaders(urlStr);
  } catch (err) {
    console.log(`[!] 请求失败: ${err.message}`);
    console.log('[*] 尝试使用 GET 方法重试...');

    // 如果 HEAD 失败，尝试 GET 方法
    try {
      result = await requestWithGet(urlStr);
    } catch (err2) {
      console.error(`[!] 请求仍然失败: ${err2.message}`);
      process.exit(1);
    }
  }

  console.log(`[*] 响应状态码: ${result.statusCode}`);
  console.log('='.repeat(60));

  const headers = result.headers;
  const missingHeaders = [];
  const weakHeaders = [];
  const goodHeaders = [];

  // ============================================================
  // 1. 检查安全响应头
  // ============================================================
  console.log('\n[*] 一、安全响应头检查');
  console.log('-'.repeat(50));

  for (const headerConfig of SECURITY_HEADERS) {
    const headerName = headerConfig.name;
    // HTTP 头不区分大小写，统一转小写比较
    const headerValue = headers[headerName.toLowerCase()] || headers[headerName] || null;

    if (headerValue === null || headerValue === undefined) {
      // 缺少该安全头
      missingHeaders.push(headerConfig);
      console.log(`  [缺失] ${headerName}`);
      console.log(`         风险等级: ${headerConfig.risk}`);
      console.log(`         说明: ${headerConfig.description}`);
    } else {
      // 验证配置是否合理
      const validation = headerConfig.validate(headerValue);
      if (validation.safe) {
        goodHeaders.push({ name: headerName, value: headerValue, message: validation.message });
        console.log(`  [正常] ${headerName}`);
        console.log(`         值: ${headerValue.substring(0, 80)}${headerValue.length > 80 ? '...' : ''}`);
        console.log(`         状态: ${validation.message}`);
      } else {
        weakHeaders.push({ name: headerName, value: headerValue, message: validation.message });
        console.log(`  [较弱] ${headerName}`);
        console.log(`         值: ${headerValue}`);
        console.log(`         问题: ${validation.message}`);
      }
    }
  }

  // ============================================================
  // 2. 检查信息泄露头
  // ============================================================
  console.log('\n[*] 二、信息泄露头检查');
  console.log('-'.repeat(50));

  const leakingHeaders = [];
  for (const headerConfig of INFO_LEAK_HEADERS) {
    const headerValue = headers[headerConfig.name.toLowerCase()] || null;
    const checkResult = headerConfig.check(headerValue);

    if (checkResult.leak) {
      leakingHeaders.push({ name: headerConfig.name, ...checkResult });
      console.log(`  [泄露] ${headerConfig.name}`);
      console.log(`         ${checkResult.message}`);
      console.log(`         建议: ${checkResult.suggestion}`);
    } else {
      console.log(`  [正常] ${headerConfig.name}`);
      console.log(`         ${checkResult.message}`);
    }
  }

  // ============================================================
  // 3. 检查 Cookie 安全属性
  // ============================================================
  console.log('\n[*] 三、Cookie 安全属性检查');
  console.log('-'.repeat(50));

  if (result.cookies.length === 0) {
    console.log('  [-] 未设置 Cookie（无 Set-Cookie 头）');
  } else {
    console.log(`  [*] 发现 ${result.cookies.length} 个 Cookie：`);
    result.cookies.forEach((cookie, index) => {
      const cookieName = cookie.split('=')[0];
      console.log(`\n    Cookie [${index + 1}]: ${cookieName}`);

      for (const sec of COOKIE_SECURITY) {
        const hasAttr = sec.check(cookie);
        if (hasAttr) {
          console.log(`      [✓] ${sec.attribute}`);
        } else {
          console.log(`      [✗] 缺少 ${sec.attribute}`);
          console.log(`          说明: ${sec.description}`);
          console.log(`          建议: ${sec.suggestion}`);
        }
      }
    });
  }

  // ============================================================
  // 4. 输出风险评估和修复建议汇总
  // ============================================================
  console.log('\n' + '='.repeat(60));
  console.log('[*] 四、风险评估与修复建议');
  console.log('='.repeat(60));

  const highRiskMissing = missingHeaders.filter(h => h.risk === '高');
  const midRiskMissing = missingHeaders.filter(h => h.risk === '中');
  const lowRiskMissing = missingHeaders.filter(h => h.risk === '低');

  // 计算安全评分（百分制）
  let score = 100;
  score -= highRiskMissing.length * 15;  // 每个高风险缺失扣15分
  score -= midRiskMissing.length * 10;   // 每个中风险缺失扣10分
  score -= lowRiskMissing.length * 5;    // 每个低风险缺失扣5分
  score -= weakHeaders.length * 5;       // 每个配置较弱扣5分
  score -= leakingHeaders.length * 3;    // 每个信息泄露扣3分
  score = Math.max(0, score);

  // 安全评级
  let grade, gradeColor;
  if (score >= 90) {
    grade = 'A (优秀)';
  } else if (score >= 75) {
    grade = 'B (良好)';
  } else if (score >= 60) {
    grade = 'C (一般)';
  } else if (score >= 40) {
    grade = 'D (较差)';
  } else {
    grade = 'F (危险)';
  }

  console.log(`\n  安全评分: ${score}/100`);
  console.log(`  安全等级: ${grade}`);
  console.log(`\n  缺失安全头: ${missingHeaders.length} 个`);
  console.log(`    - 高风险: ${highRiskMissing.length} 个`);
  console.log(`    - 中风险: ${midRiskMissing.length} 个`);
  console.log(`    - 低风险: ${lowRiskMissing.length} 个`);
  console.log(`  配置较弱: ${weakHeaders.length} 个`);
  console.log(`  信息泄露: ${leakingHeaders.length} 个`);

  // 详细修复建议
  if (missingHeaders.length > 0) {
    console.log('\n  修复建议（按优先级）:');
    console.log('  ' + '-'.repeat(40));

    let priority = 1;
    const sortedMissing = [...missingHeaders].sort((a, b) => {
      const riskOrder = { '高': 0, '中': 1, '低': 2 };
      return riskOrder[a.risk] - riskOrder[b.risk];
    });

    for (const header of sortedMissing) {
      console.log(`\n  [${priority}] ${header.name} (${header.risk}风险)`);
      console.log(`      作用: ${header.description}`);
      console.log(`      建议:`);
      header.recommendations.forEach(rec => {
        console.log(`        ${rec}`);
      });
      priority++;
    }
  }

  console.log('\n' + '='.repeat(60));
  console.log('[*] 检测完成');
  console.log('='.repeat(60));

  return {
    score,
    grade,
    missingHeaders: missingHeaders.map(h => h.name),
    weakHeaders: weakHeaders.map(h => h.name),
    leakingHeaders: leakingHeaders.map(h => h.name),
  };
}

/**
 * 使用 GET 方法作为备选（有些服务器不支持 HEAD）
 */
function requestWithGet(targetUrl, timeout = 10000) {
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
      },
    };

    const req = module.request(options, (res) => {
      const cookies = res.headers['set-cookie'] || [];
      let body = '';

      res.on('data', (chunk) => {
        body += chunk.toString();
        if (body.length > 1024) res.destroy(); // 只需要头
      });

      res.on('end', () => {
        resolve({ statusCode: res.statusCode, headers: res.headers, cookies });
      });

      res.on('close', () => {
        resolve({ statusCode: res.statusCode, headers: res.headers, cookies });
      });
    });

    req.on('timeout', () => { req.destroy(); reject(new Error('请求超时')); });
    req.on('error', (err) => { reject(err); });
    req.end();
  });
}

// ============================================================
// 主程序入口
// ============================================================
function main() {
  const args = process.argv.slice(2);

  if (args.length < 1) {
    console.log('用法: node http_header_check.js <目标URL>');
    console.log('示例: node http_header_check.js https://www.example.com');
    process.exit(1);
  }

  let targetUrl = args[0];

  // 自动补全 URL 协议
  if (!targetUrl.startsWith('http://') && !targetUrl.startsWith('https://')) {
    targetUrl = 'https://' + targetUrl;
    console.log(`[*] 自动补全协议: ${targetUrl}`);
  }

  // 验证 URL 格式
  try {
    new URL(targetUrl);
  } catch (err) {
    console.error('[!] 错误：URL 格式无效');
    process.exit(1);
  }

  // 执行检测
  checkSecurityHeaders(targetUrl)
    .catch((err) => {
      console.error('\n[!] 检测出错:', err.message);
      process.exit(1);
    });
}

// 运行主程序
main();
