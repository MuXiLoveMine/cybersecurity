/**
 * security_cases.js —— JavaScript 安全案例集（防御/学习视角）
 *
 * 涵盖 4 个安全案例：
 *   1. XSS 输入检测与净化 —— 检测恶意脚本、HTML 转义、URL 净化
 *   2. CSRF Token 生成与验证 —— Token 生成、验证机制
 *   3. 前端加密逻辑分析 —— 哈希、Base64、常见混淆模式识别
 *   4. 输入验证与安全工具集 —— 邮箱/IP/URL 验证、正则安全检测
 *
 * 运行方式:
 *   node security_cases.js              # 运行所有演示
 *   node security_cases.js --help       # 查看帮助
 *   node security_cases.js xss          # XSS 检测与净化
 *   node security_cases.js csrf         # CSRF Token 演示
 *   node security_cases.js crypto       # 前端加密分析
 *   node security_cases.js validate     # 输入验证工具集
 *
 * 注意：
 *   - 所有工具仅限在授权的环境中学习和使用
 *   - 本脚本为防御和学习目的，不包含可直接利用的攻击代码
 *   - 生产环境请使用成熟的安全库（如 DOMPurify）
 */

"use strict";

// ============================================================
// 辅助函数
// ============================================================

const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const OUTPUT_DIR = path.join(__dirname, "output");

function info(msg)    { console.log("\x1b[36m[INFO]\x1b[0m  " + msg); }
function success(msg) { console.log("\x1b[32m[OK]\x1b[0m    " + msg); }
function warn(msg)    { console.log("\x1b[33m[WARN]\x1b[0m  " + msg); }
function error(msg)   { console.log("\x1b[31m[ERROR]\x1b[0m " + msg); }
function section(title) { console.log("\n\x1b[35m=== " + title + " ===\x1b[0m\n"); }

function ensureOutputDir() {
    if (!fs.existsSync(OUTPUT_DIR)) {
        fs.mkdirSync(OUTPUT_DIR, { recursive: true });
    }
}

function getTimestamp() {
    const d = new Date();
    return d.getFullYear().toString() +
        String(d.getMonth() + 1).padStart(2, "0") +
        String(d.getDate()).padStart(2, "0") + "_" +
        String(d.getHours()).padStart(2, "0") +
        String(d.getMinutes()).padStart(2, "0") +
        String(d.getSeconds()).padStart(2, "0");
}

// ============================================================
// 帮助信息
// ============================================================
function showHelp() {
    console.log("");
    console.log("JavaScript 安全案例集 - 使用帮助");
    console.log("==================================");
    console.log("");
    console.log("用法: node security_cases.js [模式]");
    console.log("");
    console.log("模式:");
    console.log("  all        运行所有案例（默认）");
    console.log("  xss        XSS 输入检测与净化");
    console.log("  csrf       CSRF Token 生成与验证");
    console.log("  crypto     前端加密逻辑分析");
    console.log("  validate   输入验证与安全工具集");
    console.log("  help       显示此帮助");
    console.log("");
    console.log("注意事项:");
    console.log("  - 所有案例仅供学习和研究使用");
    console.log("  - 生产环境请使用成熟的安全库（DOMPurify 等）");
    console.log("  - 仅限授权环境下进行安全测试");
    console.log("");
}

// ============================================================
// 案例 1：XSS 输入检测与净化
// ============================================================

const XSSTool = (function() {
    // 常见 XSS 攻击向量特征（仅用于检测，不是完整防护）
    const xssPatterns = [
        { name: "script 标签", pattern: /<script[\s>]/i, severity: "高" },
        { name: "事件处理器", pattern: /on\w+\s*=/i, severity: "高" },
        { name: "javascript 伪协议", pattern: /javascript\s*:/i, severity: "高" },
        { name: "vbscript 伪协议", pattern: /vbscript\s*:/i, severity: "中" },
        { name: "data URI 脚本", pattern: /data\s*:\s*text\/html/i, severity: "中" },
        { name: "iframe 标签", pattern: /<iframe[\s>]/i, severity: "中" },
        { name: "img 标签(可能 onerror)", pattern: /<img[\s>].*onerror/i, severity: "高" },
        { name: "svg 标签", pattern: /<svg[\s>]/i, severity: "中" },
        { name: "eval 调用", pattern: /eval\s*\(/i, severity: "高" },
        { name: "document.write", pattern: /document\.write\s*\(/i, severity: "中" },
        { name: "innerHTML 赋值", pattern: /\.innerHTML\s*=/i, severity: "中" },
        { name: "HTML 注释+脚本", pattern: /<!--.*<script/i, severity: "中" }
    ];

    /**
     * HTML 转义（防止 XSS 的基础方法）
     * 注意：这只是基础转义，生产环境请用 DOMPurify
     */
    function escapeHtml(str) {
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#39;")
            .replace(/\//g, "&#47;");
    }

    /**
     * 检测输入中的 XSS 特征
     * @param {string} input - 待检测的输入
     * @returns {Object} 检测结果
     */
    function detectXSS(input) {
        const findings = [];
        const inputStr = String(input);

        for (const rule of xssPatterns) {
            if (rule.pattern.test(inputStr)) {
                findings.push({
                    rule: rule.name,
                    severity: rule.severity,
                    matched: inputStr.match(rule.pattern)?.[0] || ""
                });
            }
        }

        return {
            safe: findings.length === 0,
            findings: findings,
            riskLevel: findings.length === 0 ? "无" :
                findings.some(f => f.severity === "高") ? "高" :
                findings.some(f => f.severity === "中") ? "中" : "低"
        };
    }

    /**
     * URL 净化（防止 javascript: 等危险协议）
     */
    function sanitizeUrl(url) {
        if (!url) return "";
        const urlStr = String(url).trim();

        // 只允许 http/https/ftp/mailto 等安全协议
        const safeProtocols = ["http:", "https:", "ftp:", "ftps:", "mailto:"];

        try {
            const parsed = new URL(urlStr, "http://localhost");
            if (safeProtocols.includes(parsed.protocol)) {
                return urlStr;
            }
            return "";  // 危险协议，返回空
        } catch {
            // 不是合法 URL，检查是否是相对路径
            if (urlStr.startsWith("/") || urlStr.startsWith("./") || urlStr.startsWith("../")) {
                return urlStr;
            }
            return "";
        }
    }

    /**
     * 安全的 innerHTML 替代方案（用 textContent）
     * 在浏览器环境中使用，这里演示原理
     */
    function safeSetText(element, text) {
        // 浏览器中：element.textContent = text;
        // 这是最安全的方式，不会解析 HTML
        return { element: element, content: String(text), method: "textContent" };
    }

    return {
        detectXSS,
        escapeHtml,
        sanitizeUrl,
        safeSetText,
        xssPatterns
    };
})();

function runXSSCase() {
    section("案例 1：XSS 输入检测与净化");

    // 1.1 XSS 检测
    info("【1.1 XSS 特征检测】");
    console.log("");

    const testInputs = [
        "Hello, world!",
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert(1)>",
        "<a href='javascript:alert(1)'>click me</a>",
        "<div onmouseover='alert(1)'>hover</div>",
        "<svg onload=alert('XSS')>",
        "正常的用户输入，没有恶意内容",
        "<iframe src='https://evil.com'>",
        "eval(window.location.hash)"
    ];

    console.log("  测试输入检测结果:");
    console.log("  " + "-".repeat(70));

    const results = [];
    for (const input of testInputs) {
        const result = XSSTool.detectXSS(input);
        const shortInput = input.length > 50 ? input.slice(0, 47) + "..." : input;
        const status = result.safe ? "\x1b[32m✅ 安全\x1b[0m" : `\x1b[31m⚠️  ${result.riskLevel}危\x1b[0m`;

        console.log(`  输入: ${shortInput}`);
        console.log(`  状态: ${status}`);

        if (result.findings.length > 0) {
            console.log(`  发现问题: ${result.findings.map(f => `${f.rule}(${f.severity})`).join(", ")}`);
        }
        console.log("");

        results.push({
            input: input,
            safe: result.safe,
            riskLevel: result.riskLevel,
            findings: result.findings.map(f => f.rule).join("; ")
        });
    }

    // 1.2 HTML 转义
    info("【1.2 HTML 转义（基础 XSS 防护）】");
    console.log("");

    const xssPayload = "<script>alert('XSS')</script><img src=x onerror=alert(1)>";
    const escaped = XSSTool.escapeHtml(xssPayload);

    console.log("  原始输入（危险）:");
    console.log("    " + xssPayload);
    console.log("");
    console.log("  转义后（安全）:");
    console.log("    " + escaped);
    console.log("");
    console.log("  💡 转义后，所有 HTML 特殊字符都变成了实体");
    console.log("     浏览器会把它们当作文本显示，而不是解析为标签");
    console.log("");

    // 1.3 URL 净化
    info("【1.3 URL 净化（防止 javascript: 伪协议）】");
    console.log("");

    const testUrls = [
        "https://example.com/page",
        "javascript:alert(document.cookie)",
        "http://test.org/path?q=1",
        "vbscript:msgbox('XSS')",
        "/relative/path",
        "data:text/html,<script>alert(1)</script>",
        "mailto:user@example.com"
    ];

    console.log("  URL 净化测试:");
    console.log("  " + "-".repeat(70));
    for (const url of testUrls) {
        const sanitized = XSSTool.sanitizeUrl(url);
        const safe = sanitized !== "";
        const status = safe ? "\x1b[32m✅ 安全\x1b[0m" : "\x1b[31m❌ 危险（已移除）\x1b[0m";
        console.log(`  原始: ${url}`);
        console.log(`  状态: ${status}`);
        if (safe && sanitized !== url) {
            console.log(`  净化后: ${sanitized}`);
        }
        console.log("");
    }

    // 1.4 防御建议
    info("【1.4 XSS 防御层次建议】");
    console.log("");
    const defenses = [
        ["输入验证", "服务端白名单验证", "第一道防线"],
        ["输出编码", "根据上下文正确转义（HTML/JS/CSS/URL）", "核心防御"],
        ["CSP", "内容安全策略，限制脚本来源", "纵深防御"],
        ["HttpOnly", "Cookie 设置 HttpOnly 属性", "保护 Cookie"],
        ["安全 API", "使用 textContent 代替 innerHTML", "前端最佳实践"],
        ["WAF", "Web 应用防火墙", "额外防护层"]
    ];

    console.log("  " + "层级".padEnd(10) + "措施".padEnd(30) + "说明");
    console.log("  " + "-".repeat(65));
    for (const [level, measure, desc] of defenses) {
        console.log("  " + level.padEnd(10) + measure.padEnd(30) + desc);
    }
    console.log("");

    warn("注意：以上检测和净化仅为基础演示，生产环境请使用成熟的安全库如 DOMPurify");
    console.log("");

    // 导出结果
    ensureOutputDir();
    const reportFile = path.join(OUTPUT_DIR, `xss_detection_${getTimestamp()}.json`);
    fs.writeFileSync(reportFile, JSON.stringify(results, null, 2), "utf8");
    success(`XSS 检测报告已导出: ${reportFile}`);
    console.log("");
}

// ============================================================
// 案例 2：CSRF Token 生成与验证
// ============================================================

const CSRFTool = (function() {
    /**
     * 生成安全的随机 Token
     * 使用 crypto 模块的安全随机数
     */
    function generateToken(length = 32) {
        return crypto.randomBytes(length).toString("hex");
    }

    /**
     * 生成带时间戳的 CSRF Token（可选过期机制）
     */
    function generateTimedToken(ttlSeconds = 3600) {
        const token = generateToken(32);
        const timestamp = Date.now();
        const expiresAt = timestamp + ttlSeconds * 1000;

        // 实际场景中，Token 会存储在 session 中
        // 这里返回 Token 及其元数据
        return {
            token: token,
            issuedAt: timestamp,
            expiresAt: expiresAt,
            ttl: ttlSeconds
        };
    }

    /**
     * 验证 CSRF Token（恒定时间比较，防止时序攻击）
     */
    function verifyToken(token, expectedToken, issuedAt = null, ttlSeconds = 3600) {
        // 1. 基本格式检查
        if (!token || !expectedToken) {
            return { valid: false, reason: "Token 不能为空" };
        }

        // 2. 恒定时间比较（防止时序攻击）
        // crypto.timingSafeEqual 需要 Buffer
        try {
            const tokenBuf = Buffer.from(token);
            const expectedBuf = Buffer.from(expectedToken);

            if (tokenBuf.length !== expectedBuf.length) {
                return { valid: false, reason: "Token 长度不匹配" };
            }

            const matches = crypto.timingSafeEqual(tokenBuf, expectedBuf);

            if (!matches) {
                return { valid: false, reason: "Token 不匹配" };
            }
        } catch (e) {
            return { valid: false, reason: "Token 验证异常" };
        }

        // 3. 过期时间检查
        if (issuedAt) {
            const now = Date.now();
            if (now > issuedAt + ttlSeconds * 1000) {
                return { valid: false, reason: "Token 已过期" };
            }
        }

        return { valid: true, reason: "验证通过" };
    }

    /**
     * 生成 HMAC 签名的 Token（服务端可验证，无需存储）
     * 类似 JWT 的思路，但更简单
     */
    function generateHmacToken(secret, sessionId) {
        const timestamp = Date.now();
        const payload = `${sessionId}.${timestamp}`;
        const signature = crypto
            .createHmac("sha256", secret)
            .update(payload)
            .digest("hex");
        return `${payload}.${signature}`;
    }

    function verifyHmacToken(token, secret, sessionId, ttlSeconds = 3600) {
        try {
            const parts = token.split(".");
            if (parts.length !== 3) {
                return { valid: false, reason: "Token 格式错误" };
            }

            const [sid, tsStr, signature] = parts;
            const timestamp = parseInt(tsStr, 10);

            // 验证 sessionId
            if (sid !== sessionId) {
                return { valid: false, reason: "Session 不匹配" };
            }

            // 验证过期
            if (Date.now() > timestamp + ttlSeconds * 1000) {
                return { valid: false, reason: "Token 已过期" };
            }

            // 验证签名
            const payload = `${sid}.${tsStr}`;
            const expectedSig = crypto
                .createHmac("sha256", secret)
                .update(payload)
                .digest("hex");

            const sigBuf = Buffer.from(signature);
            const expectedBuf = Buffer.from(expectedSig);

            if (sigBuf.length !== expectedBuf.length) {
                return { valid: false, reason: "签名长度不匹配" };
            }

            const valid = crypto.timingSafeEqual(sigBuf, expectedBuf);
            return {
                valid: valid,
                reason: valid ? "验证通过" : "签名不匹配"
            };
        } catch (e) {
            return { valid: false, reason: "验证异常: " + e.message };
        }
    }

    return {
        generateToken,
        generateTimedToken,
        verifyToken,
        generateHmacToken,
        verifyHmacToken
    };
})();

function runCSRFCase() {
    section("案例 2：CSRF Token 生成与验证");

    // 2.1 基本 Token 生成
    info("【2.1 基本 CSRF Token 生成】");
    console.log("");

    const token1 = CSRFTool.generateToken();
    const token2 = CSRFTool.generateToken();

    console.log("  Token 1:", token1);
    console.log("  Token 2:", token2);
    console.log("  长度: ", token1.length, "个十六进制字符（", token1.length / 2, "字节）");
    console.log("  两个 Token 相同吗？", token1 === token2 ? "是（异常）" : "否（正常，每次都不同）");
    console.log("");
    console.log("  💡 CSRF Token 必须是密码学安全的随机数");
    console.log("     不能使用可预测的值（如时间戳、自增ID）");
    console.log("");

    // 2.2 Token 验证
    info("【2.2 Token 验证（恒定时间比较）】");
    console.log("");

    const validToken = CSRFTool.generateToken();
    const correctInput = validToken;
    const wrongInput = "00000000000000000000000000000000";

    const result1 = CSRFTool.verifyToken(correctInput, validToken);
    const result2 = CSRFTool.verifyToken(wrongInput, validToken);
    const result3 = CSRFTool.verifyToken("", validToken);

    console.log("  正确 Token 验证:", result1.valid ? "✅ 通过" : "❌ 失败", "-", result1.reason);
    console.log("  错误 Token 验证:", result2.valid ? "✅ 通过" : "❌ 失败", "-", result2.reason);
    console.log("  空 Token 验证:  ", result3.valid ? "✅ 通过" : "❌ 失败", "-", result3.reason);
    console.log("");
    console.log("  💡 使用恒定时间比较（timingSafeEqual）防止时序攻击");
    console.log("     普通的 === 比较可能因字符逐一比较而泄露信息");
    console.log("");

    // 2.3 带过期时间的 Token
    info("【2.3 带过期时间的 Token】");
    console.log("");

    const timedToken = CSRFTool.generateTimedToken(3600);  // 1 小时有效期
    console.log("  Token:     ", timedToken.token.slice(0, 20) + "...");
    console.log("  签发时间:   ", new Date(timedToken.issuedAt).toLocaleString());
    console.log("  过期时间:   ", new Date(timedToken.expiresAt).toLocaleString());
    console.log("  有效期:     ", timedToken.ttl, "秒（", timedToken.ttl / 3600, "小时）");
    console.log("");

    // 验证（带时间检查）
    const verifyTimed = CSRFTool.verifyToken(
        timedToken.token,
        timedToken.token,
        timedToken.issuedAt,
        timedToken.ttl
    );
    console.log("  验证结果:", verifyTimed.valid ? "✅ 有效" : "❌ 无效", "-", verifyTimed.reason);
    console.log("");

    // 2.4 HMAC Token（无状态）
    info("【2.4 HMAC Token（服务端无状态验证）】");
    console.log("");

    const serverSecret = "server-secret-key-" + crypto.randomBytes(16).toString("hex");
    const userSessionId = "user-session-" + crypto.randomBytes(8).toString("hex");

    console.log("  服务端密钥: ", serverSecret.slice(0, 20) + "...");
    console.log("  用户会话ID: ", userSessionId);
    console.log("");

    const hmacToken = CSRFTool.generateHmacToken(serverSecret, userSessionId);
    console.log("  HMAC Token:");
    console.log("    " + hmacToken.slice(0, 60) + "...");
    console.log("");

    // 验证
    const hmacResult = CSRFTool.verifyHmacToken(hmacToken, serverSecret, userSessionId, 3600);
    console.log("  正确验证:", hmacResult.valid ? "✅ 通过" : "❌ 失败", "-", hmacResult.reason);

    const wrongSessionResult = CSRFTool.verifyHmacToken(hmacToken, serverSecret, "other-session-id", 3600);
    console.log("  错误会话:", wrongSessionResult.valid ? "✅ 通过" : "❌ 失败", "-", wrongSessionResult.reason);

    const tamperedToken = hmacToken.replace(/.$/, "X");  // 篡改最后一个字符
    const tamperedResult = CSRFTool.verifyHmacToken(tamperedToken, serverSecret, userSessionId, 3600);
    console.log("  篡改 Token:", tamperedResult.valid ? "✅ 通过" : "❌ 失败", "-", tamperedResult.reason);
    console.log("");

    // 2.5 CSRF 防御总结
    info("【2.5 CSRF 防御方法总结】");
    console.log("");

    const csrfDefenses = [
        ["CSRF Token", "每个请求携带随机 Token，服务端验证", "最常用，有效"],
        ["SameSite Cookie", "Cookie 设置 SameSite=Strict/Lax", "现代浏览器支持"],
        ["双重提交 Cookie", "Cookie 和请求参数中各放一个 Token", "无状态方案"],
        ["验证 Referer/Origin", "检查请求来源", "可被绕过，辅助手段"],
        ["验证码", "关键操作需要验证码", "有效但影响体验"],
        ["重新认证", "敏感操作重新输入密码", "最安全但最繁琐"]
    ];

    console.log("  " + "方法".padEnd(16) + "原理".padEnd(30) + "有效性");
    console.log("  " + "-".repeat(65));
    for (const [method, principle, effectiveness] of csrfDefenses) {
        console.log("  " + method.padEnd(16) + principle.padEnd(30) + effectiveness);
    }
    console.log("");

    success("CSRF Token 案例演示完成");
    console.log("");
}

// ============================================================
// 案例 3：前端加密逻辑分析
// ============================================================

const CryptoTool = (function() {
    /**
     * 计算 MD5 哈希（仅用于学习，不推荐用于安全场景）
     */
    function md5(data) {
        return crypto.createHash("md5").update(data).digest("hex");
    }

    /**
     * 计算 SHA-1 哈希（仅用于学习，不推荐用于安全场景）
     */
    function sha1(data) {
        return crypto.createHash("sha1").update(data).digest("hex");
    }

    /**
     * 计算 SHA-256 哈希（安全推荐）
     */
    function sha256(data) {
        return crypto.createHash("sha256").update(data).digest("hex");
    }

    /**
     * 计算 SHA-512 哈希
     */
    function sha512(data) {
        return crypto.createHash("sha512").update(data).digest("hex");
    }

    /**
     * HMAC-SHA256
     */
    function hmacSha256(key, data) {
        return crypto.createHmac("sha256", key).update(data).digest("hex");
    }

    /**
     * Base64 编码
     */
    function base64Encode(str) {
        return Buffer.from(str, "utf8").toString("base64");
    }

    /**
     * Base64 解码
     */
    function base64Decode(str) {
        return Buffer.from(str, "base64").toString("utf8");
    }

    /**
     * AES-256-CBC 加密
     * 注意：前端加密仅用于混淆，密钥不能保密
     */
    function aesEncrypt(text, key, iv) {
        const keyBuf = Buffer.from(key, "hex");
        const ivBuf = Buffer.from(iv, "hex");
        const cipher = crypto.createCipheriv("aes-256-cbc", keyBuf, ivBuf);
        let encrypted = cipher.update(text, "utf8", "hex");
        encrypted += cipher.final("hex");
        return encrypted;
    }

    function aesDecrypt(encrypted, key, iv) {
        const keyBuf = Buffer.from(key, "hex");
        const ivBuf = Buffer.from(iv, "hex");
        const decipher = crypto.createDecipheriv("aes-256-cbc", keyBuf, ivBuf);
        let decrypted = decipher.update(encrypted, "hex", "utf8");
        decrypted += decipher.final("utf8");
        return decrypted;
    }

    /**
     * 识别常见的编码类型
     */
    function detectEncoding(str) {
        const detections = [];

        // Base64 检测
        if (/^[A-Za-z0-9+/]+=*$/.test(str) && str.length % 4 === 0 && str.length > 8) {
            try {
                const decoded = base64Decode(str);
                // 检查解码后是否为可打印字符
                if (/^[\x20-\x7e\s]+$/.test(decoded)) {
                    detections.push({
                        type: "Base64",
                        confidence: "高",
                        decoded: decoded
                    });
                } else {
                    detections.push({
                        type: "Base64 (二进制数据)",
                        confidence: "中",
                        decoded: decoded.slice(0, 50) + "..."
                    });
                }
            } catch (e) {
                // 不是有效的 Base64
            }
        }

        // Hex 编码检测
        if (/^[0-9a-fA-F]+$/.test(str) && str.length % 2 === 0 && str.length > 6) {
            try {
                const decoded = Buffer.from(str, "hex").toString("utf8");
                if (/^[\x20-\x7e\s]+$/.test(decoded)) {
                    detections.push({
                        type: "Hex (十六进制)",
                        confidence: "中",
                        decoded: decoded
                    });
                }
            } catch (e) {
                // 忽略
            }
        }

        // URL 编码检测
        if (/%[0-9a-fA-F]{2}/.test(str)) {
            try {
                const decoded = decodeURIComponent(str);
                if (decoded !== str) {
                    detections.push({
                        type: "URL 编码",
                        confidence: "高",
                        decoded: decoded
                    });
                }
            } catch (e) {
                // 忽略
            }
        }

        // MD5 哈希检测（32 位十六进制）
        if (/^[0-9a-f]{32}$/.test(str)) {
            detections.push({
                type: "可能是 MD5 哈希",
                confidence: "中",
                decoded: "哈希不可逆，需查彩虹表"
            });
        }

        // SHA-256 哈希检测（64 位十六进制）
        if (/^[0-9a-f]{64}$/.test(str)) {
            detections.push({
                type: "可能是 SHA-256 哈希",
                confidence: "高",
                decoded: "哈希不可逆，需查彩虹表"
            });
        }

        return detections;
    }

    return {
        md5,
        sha1,
        sha256,
        sha512,
        hmacSha256,
        base64Encode,
        base64Decode,
        aesEncrypt,
        aesDecrypt,
        detectEncoding
    };
})();

function runCryptoCase() {
    section("案例 3：前端加密逻辑分析");

    // 3.1 哈希算法对比
    info("【3.1 常见哈希算法对比】");
    console.log("");

    const testData = "password123";
    console.log("  测试数据:", testData);
    console.log("");

    const hashes = [
        ["MD5", CryptoTool.md5(testData), "❌ 不安全（已破解）"],
        ["SHA-1", CryptoTool.sha1(testData), "⚠️  不安全（已碰撞）"],
        ["SHA-256", CryptoTool.sha256(testData), "✅ 安全推荐"],
        ["SHA-512", CryptoTool.sha512(testData), "✅ 安全"]
    ];

    console.log("  " + "算法".padEnd(10) + "哈希值".padEnd(40) + "安全性");
    console.log("  " + "-".repeat(70));
    for (const [algo, hash, security] of hashes) {
        const shortHash = hash.slice(0, 36) + "...";
        console.log("  " + algo.padEnd(10) + shortHash.padEnd(40) + security);
    }
    console.log("");
    console.log("  💡 密码存储应该用 bcrypt / scrypt / Argon2 等慢哈希算法");
    console.log("     普通哈希（即使是 SHA-256）也容易被彩虹表破解");
    console.log("");

    // 3.2 HMAC 演示
    info("【3.2 HMAC 消息认证码】");
    console.log("");

    const secretKey = "my-secret-key-12345";
    const message = "user_id=123&role=user";
    const hmac = CryptoTool.hmacSha256(secretKey, message);

    console.log("  密钥:", secretKey);
    console.log("  消息:", message);
    console.log("  HMAC-SHA256:", hmac);
    console.log("");
    console.log("  💡 HMAC 可以验证消息的完整性和来源");
    console.log("     只有持有密钥的人才能生成正确的 HMAC");
    console.log("");

    // 3.3 Base64 编解码
    info("【3.3 Base64 编解码】");
    console.log("");

    const originalText = "Hello, World! 这是一段测试文本";
    const encoded = CryptoTool.base64Encode(originalText);
    const decoded = CryptoTool.base64Decode(encoded);

    console.log("  原始文本:", originalText);
    console.log("  Base64 编码:", encoded);
    console.log("  Base64 解码:", decoded);
    console.log("");
    console.log("  💡 Base64 不是加密！只是编码，可以直接解码还原");
    console.log("     前端常见于：简单混淆、数据传输、图片编码");
    console.log("");

    // 3.4 AES 对称加密演示
    info("【3.4 AES 对称加密演示】");
    console.log("");

    const aesKey = crypto.randomBytes(32).toString("hex");  // 256 位密钥
    const aesIV = crypto.randomBytes(16).toString("hex");   // 128 位 IV
    const plainText = "敏感数据: 用户密码 = admin123";

    console.log("  密钥 (256位):", aesKey.slice(0, 20) + "...");
    console.log("  IV (128位):  ", aesIV.slice(0, 20) + "...");
    console.log("  明文:        ", plainText);
    console.log("");

    const encrypted = CryptoTool.aesEncrypt(plainText, aesKey, aesIV);
    console.log("  密文 (hex):  ", encrypted.slice(0, 50) + "...");
    console.log("  密文长度:    ", encrypted.length, "个十六进制字符（", encrypted.length / 2, "字节）");
    console.log("");

    const decrypted = CryptoTool.aesDecrypt(encrypted, aesKey, aesIV);
    console.log("  解密结果:    ", decrypted);
    console.log("  解密正确吗？  ", decrypted === plainText ? "✅ 是" : "❌ 否");
    console.log("");

    console.log("  ⚠️  前端加密的局限性:");
    console.log("    1. 密钥无法保密（JS 代码可以被查看）");
    console.log("    2. 不能替代 HTTPS（中间人可以修改 JS）");
    console.log("    3. 主要用于：简单混淆、本地存储加密、数据传输辅助");
    console.log("    4. 真正的安全必须依赖服务端和 TLS 传输");
    console.log("");

    // 3.5 编码识别
    info("【3.5 编码类型自动识别】");
    console.log("");

    const testStrings = [
        "SGVsbG8sIFdvcmxkIQ==",
        "482c811da5d5b4bc6d497ffa98491e38",
        "Hello%20World%21",
        "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8",
        "68656c6c6f"
    ];

    console.log("  编码识别测试:");
    console.log("  " + "-".repeat(70));
    for (const str of testStrings) {
        console.log("  输入:", str.slice(0, 50) + (str.length > 50 ? "..." : ""));
        const detections = CryptoTool.detectEncoding(str);
        if (detections.length > 0) {
            for (const d of detections) {
                console.log("    ", d.type, "(" + d.confidence + "):", d.decoded.slice(0, 50));
            }
        } else {
            console.log("    未识别出常见编码");
        }
        console.log("");
    }

    success("前端加密逻辑分析案例演示完成");
    console.log("");
}

// ============================================================
// 案例 4：输入验证与安全工具集
// ============================================================

const ValidationTool = (function() {
    /**
     * 邮箱格式验证
     */
    function validateEmail(email) {
        if (!email || typeof email !== "string") {
            return { valid: false, reason: "输入不能为空" };
        }
        // 实用的邮箱验证正则（不追求完美，但能过滤大部分错误）
        const re = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        if (!re.test(email)) {
            return { valid: false, reason: "邮箱格式不正确" };
        }
        if (email.length > 254) {
            return { valid: false, reason: "邮箱长度超过限制" };
        }
        return { valid: true, reason: "验证通过" };
    }

    /**
     * IPv4 地址验证
     */
    function validateIPv4(ip) {
        if (!ip || typeof ip !== "string") {
            return { valid: false, reason: "输入不能为空" };
        }
        const re = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
        if (!re.test(ip)) {
            return { valid: false, reason: "IPv4 格式不正确" };
        }
        return { valid: true, reason: "验证通过" };
    }

    /**
     * URL 安全验证
     */
    function validateSafeURL(url) {
        if (!url || typeof url !== "string") {
            return { valid: false, reason: "输入不能为空" };
        }

        const safeProtocols = ["http:", "https:"];

        try {
            const parsed = new URL(url);

            if (!safeProtocols.includes(parsed.protocol)) {
                return { valid: false, reason: "不允许的协议: " + parsed.protocol };
            }

            return {
                valid: true,
                reason: "验证通过",
                protocol: parsed.protocol,
                hostname: parsed.hostname,
                port: parsed.port,
                pathname: parsed.pathname
            };
        } catch (e) {
            return { valid: false, reason: "URL 格式不正确" };
        }
    }

    /**
     * 密码强度检测
     * 返回强度等级和建议
     */
    function checkPasswordStrength(password) {
        if (!password || typeof password !== "string") {
            return { score: 0, level: "无", reasons: ["密码不能为空"] };
        }

        let score = 0;
        const reasons = [];

        // 长度
        if (password.length < 6) {
            reasons.push("密码太短（至少 8 位）");
        } else if (password.length >= 8 && password.length < 12) {
            score += 1;
        } else if (password.length >= 12 && password.length < 16) {
            score += 2;
        } else {
            score += 3;
        }

        // 字符种类
        let typeCount = 0;
        if (/[a-z]/.test(password)) typeCount++;
        if (/[A-Z]/.test(password)) typeCount++;
        if (/[0-9]/.test(password)) typeCount++;
        if (/[^a-zA-Z0-9]/.test(password)) typeCount++;

        if (typeCount >= 4) {
            score += 3;
        } else if (typeCount === 3) {
            score += 2;
        } else if (typeCount === 2) {
            score += 1;
        } else {
            reasons.push("字符类型太单一");
        }

        // 常见弱密码检查
        const weakPasswords = ["password", "123456", "12345678", "qwerty", "abc123", "admin", "letmein"];
        if (weakPasswords.includes(password.toLowerCase())) {
            score = 0;
            reasons.push("这是常见的弱密码");
        }

        // 重复字符
        if (/(.)\1{2,}/.test(password)) {
            reasons.push("包含连续重复字符");
            score = Math.max(0, score - 1);
        }

        // 连续数字/字母
        if (/(012|123|234|345|456|567|678|789|abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)/i.test(password)) {
            reasons.push("包含连续序列");
            score = Math.max(0, score - 1);
        }

        // 评级
        let level;
        if (score <= 1) level = "弱";
        else if (score <= 3) level = "中";
        else if (score <= 5) level = "强";
        else level = "非常强";

        // 建议
        const suggestions = [];
        if (password.length < 12) suggestions.push("增加密码长度到 12 位以上");
        if (typeCount < 4) suggestions.push("混合大小写字母、数字和特殊字符");
        if (weakPasswords.includes(password.toLowerCase())) suggestions.push("避免使用常见弱密码");

        return {
            score: Math.min(score, 6),
            maxScore: 6,
            level: level,
            reasons: reasons,
            suggestions: suggestions,
            length: password.length,
            typeCount: typeCount
        };
    }

    /**
     * 检测正则表达式的 ReDoS 风险（基础版）
     */
    function checkReDoSRisk(pattern) {
        const risks = [];

        // 嵌套量词（如 (a+)+, (a*)+ 等）
        if (/\([^)]*[+*?]\)[+*?]/.test(pattern)) {
            risks.push({
                type: "嵌套量词",
                severity: "高",
                description: "存在嵌套的量词，可能导致指数级回溯"
            });
        }

        // 多个重叠的量词
        if (/\[.*\][+*].*\[.*\][+*]/.test(pattern)) {
            risks.push({
                type: "重叠量词",
                severity: "中",
                description: "多个可重叠的量词可能导致大量回溯"
            });
        }

        // .* 开头或结尾（可能匹配过多）
        if (/^\.\*.*\.\*$/.test(pattern)) {
            risks.push({
                type: "双重 .*",
                severity: "中",
                description: "前后都是 .* 可能匹配大量文本"
            });
        }

        return {
            risky: risks.length > 0,
            risks: risks,
            riskLevel: risks.length === 0 ? "低" :
                risks.some(r => r.severity === "高") ? "高" : "中"
        };
    }

    return {
        validateEmail,
        validateIPv4,
        validateSafeURL,
        checkPasswordStrength,
        checkReDoSRisk
    };
})();

function runValidationCase() {
    section("案例 4：输入验证与安全工具集");

    // 4.1 邮箱验证
    info("【4.1 邮箱格式验证】");
    console.log("");

    const testEmails = [
        "user@example.com",
        "user.name+tag@domain.co.uk",
        "invalid@",
        "@nodomain.com",
        "user@.com",
        "user@domain",
        "a@b.c"
    ];

    console.log("  邮箱验证测试:");
    console.log("  " + "-".repeat(60));
    for (const email of testEmails) {
        const result = ValidationTool.validateEmail(email);
        const status = result.valid ? "\x1b[32m✅\x1b[0m" : "\x1b[31m❌\x1b[0m";
        console.log(`  ${status} ${email.padEnd(30)} ${result.reason}`);
    }
    console.log("");

    // 4.2 IP 验证
    info("【4.2 IPv4 地址验证】");
    console.log("");

    const testIPs = [
        "192.168.1.1",
        "10.0.0.1",
        "255.255.255.0",
        "256.1.1.1",
        "192.168.1",
        "abc.def.ghi.jkl",
        "0.0.0.0"
    ];

    console.log("  IP 验证测试:");
    console.log("  " + "-".repeat(60));
    for (const ip of testIPs) {
        const result = ValidationTool.validateIPv4(ip);
        const status = result.valid ? "\x1b[32m✅\x1b[0m" : "\x1b[31m❌\x1b[0m";
        console.log(`  ${status} ${ip.padEnd(20)} ${result.reason}`);
    }
    console.log("");

    // 4.3 URL 安全验证
    info("【4.3 URL 安全验证】");
    console.log("");

    const testURLs = [
        "https://example.com/page",
        "http://test.org/path?query=1",
        "javascript:alert(1)",
        "ftp://files.example.com",
        "https://evil.com/redirect?url=http://attacker.com",
        "not-a-url"
    ];

    console.log("  URL 安全验证（仅允许 http/https）:");
    console.log("  " + "-".repeat(60));
    for (const url of testURLs) {
        const result = ValidationTool.validateSafeURL(url);
        const status = result.valid ? "\x1b[32m✅\x1b[0m" : "\x1b[31m❌\x1b[0m";
        console.log(`  ${status} ${url.slice(0, 40).padEnd(42)} ${result.reason}`);
    }
    console.log("");

    // 4.4 密码强度检测
    info("【4.4 密码强度检测】");
    console.log("");

    const testPasswords = [
        "123456",
        "password",
        "abc123",
        "Password1",
        "P@ssw0rd",
        "MyStr0ng!Pass#2024",
        "Tr0ub4dor&3-horse-staple"
    ];

    console.log("  密码强度测试:");
    console.log("  " + "-".repeat(70));
    for (const pwd of testPasswords) {
        const result = ValidationTool.checkPasswordStrength(pwd);
        const stars = "★".repeat(result.score) + "☆".repeat(result.maxScore - result.score);
        const levelColor = result.level === "弱" ? "\x1b[31m" :
                          result.level === "中" ? "\x1b[33m" :
                          result.level === "强" ? "\x1b[32m" : "\x1b[36m";
        const displayPwd = pwd.length > 20 ? pwd.slice(0, 17) + "..." : pwd;
        console.log(`  ${displayPwd.padEnd(22)} ${stars} ${levelColor}${result.level}\x1b[0m`);
        if (result.suggestions.length > 0) {
            result.suggestions.forEach(s => console.log(`    💡 ${s}`));
        }
    }
    console.log("");

    // 4.5 ReDoS 风险检测
    info("【4.5 正则表达式 ReDoS 风险检测】");
    console.log("");

    const testRegexes = [
        ["^[a-z]+$", "简单匹配"],
        ["(a+)+$", "嵌套量词（危险）"],
        ["^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$", "邮箱正则"],
        ["(a|aa)+$", "重叠分支（危险）"],
        ["^.*=.*$", "双重匹配"]
    ];

    console.log("  ReDoS 风险检测:");
    console.log("  " + "-".repeat(70));
    for (const [pattern, desc] of testRegexes) {
        const result = ValidationTool.checkReDoSRisk(pattern);
        const riskColor = result.riskLevel === "高" ? "\x1b[31m" :
                         result.riskLevel === "中" ? "\x1b[33m" : "\x1b[32m";
        console.log(`  正则: ${pattern.slice(0, 40).padEnd(42)} ${riskColor}${result.riskLevel}危\x1b[0m (${desc})`);
        if (result.risks.length > 0) {
            result.risks.forEach(r => console.log(`    ⚠️  ${r.type}: ${r.description}`));
        }
    }
    console.log("");

    console.log("  💡 ReDoS（正则拒绝服务）防护建议:");
    console.log("    1. 避免使用嵌套量词（如 (a+)+）");
    console.log("    2. 限制输入字符串长度");
    console.log("    3. 设置正则匹配超时");
    console.log("    4. 使用 RE2 等安全的正则引擎");
    console.log("    5. 对用户提供的正则表达式进行审计");
    console.log("");

    success("输入验证与安全工具集案例演示完成");
    console.log("");
}

// ============================================================
// 主程序入口
// ============================================================

const args = process.argv.slice(2);
const mode = args[0] || "all";

console.log("");
console.log("=".repeat(60));
console.log("  JavaScript 安全案例集");
console.log("  Security Cases for JavaScript");
console.log("=".repeat(60));
console.log("");

info("输出目录: " + OUTPUT_DIR);
info("运行模式: " + mode);
console.log("");

switch (mode) {
    case "help":
        showHelp();
        break;
    case "xss":
        runXSSCase();
        break;
    case "csrf":
        runCSRFCase();
        break;
    case "crypto":
        runCryptoCase();
        break;
    case "validate":
        runValidationCase();
        break;
    case "all":
        info("运行所有安全案例...");
        console.log("");

        runXSSCase();
        runCSRFCase();
        runCryptoCase();
        runValidationCase();

        section("全部案例执行完毕");
        success("所有安全案例已运行完成");
        info("输出文件保存在: " + OUTPUT_DIR);
        console.log("");
        break;
    default:
        error("未知模式: " + mode);
        showHelp();
        process.exit(1);
}

console.log("");
console.log("=".repeat(60));
console.log("  免责声明");
console.log("=".repeat(60));
console.log("");
console.log("  本脚本仅供学习、研究和授权环境下的安全运维使用。");
console.log("  任何未经授权的测试或攻击行为均属违法。");
console.log("  使用者应遵守所在地区法律法规，对自己的行为负责。");
console.log("");
