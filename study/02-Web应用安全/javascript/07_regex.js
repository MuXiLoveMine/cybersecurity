/**
 * 07_regex.js - 正则表达式创建、test、exec、match、replace、search
 * 
 * 本示例演示 JavaScript 正则表达式的使用：
 * - 正则表达式的创建方式
 * - 修饰符
 * - test 方法
 * - exec 方法
 * - match / matchAll 方法
 * - replace 方法
 * - search 方法
 * - 常用正则模式
 */

// ========== 1. 正则表达式创建 ==========

console.log("=== 1. 正则表达式创建 ===");

// 方式一：字面量（推荐，性能更好）
const regex1 = /abc/;
console.log("字面量:", regex1);

// 方式二：构造函数（适用于动态构建正则）
const regex2 = new RegExp("abc");
console.log("构造函数:", regex2);

// 带修饰符
const regex3 = /abc/gi;
const regex4 = new RegExp("abc", "gi");
console.log("带修饰符:", regex3, regex4);

// 动态构建正则表达式
const keyword = "用户";
const dynamicRegex = new RegExp(keyword, "g");
console.log("动态构建:", dynamicRegex);

// ========== 2. 修饰符 ==========

console.log("\n=== 2. 修饰符 ===");

// g - 全局匹配（查找所有匹配项）
const text = "Hello hello HELLO";
console.log("原始文本:", text);
console.log("不带 g:", text.match(/hello/));
console.log("带 g:", text.match(/hello/g));

// i - 忽略大小写
console.log("不带 i:", text.match(/Hello/g));
console.log("带 i:", text.match(/hello/gi));

// m - 多行模式
const multiText = "第一行\n第二行\n第三行";
console.log("多行匹配 ^:", multiText.match(/^第/gm));

// ========== 3. test 方法 ==========

console.log("\n=== 3. test 方法 ===");

// test() - 测试是否匹配，返回布尔值
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

console.log("test@example.com 是否是邮箱:", emailRegex.test("test@example.com"));
console.log("invalid 是否是邮箱:", emailRegex.test("invalid"));
console.log("@example.com 是否是邮箱:", emailRegex.test("@example.com"));

// 应用：表单验证
function validatePhone(phone) {
    const phoneRegex = /^1[3-9]\d{9}$/;
    return phoneRegex.test(phone);
}

console.log("13812345678 是手机号:", validatePhone("13812345678"));
console.log("12345 是手机号:", validatePhone("12345"));
console.log("12345678901 是手机号:", validatePhone("12345678901"));

// ========== 4. exec 方法 ==========

console.log("\n=== 4. exec 方法 ===");

// exec() - 执行匹配，返回匹配结果数组或 null
const pattern = /(\d+)-(\d+)/g;
const str = "范围：100-200 和 300-400";

console.log("原始字符串:", str);
console.log("正则表达式:", pattern);

// 第一次调用
let match1 = pattern.exec(str);
console.log("第 1 次 exec:", match1);
console.log("  完整匹配:", match1[0]);
console.log("  捕获组 1:", match1[1]);
console.log("  捕获组 2:", match1[2]);
console.log("  匹配索引:", match1.index);

// 第二次调用（带 g 修饰符时，lastIndex 会移动）
let match2 = pattern.exec(str);
console.log("第 2 次 exec:", match2);

// 第三次调用（没有更多匹配，返回 null，lastIndex 重置）
let match3 = pattern.exec(str);
console.log("第 3 次 exec:", match3);

// 循环遍历所有匹配
console.log("\n循环遍历所有匹配:");
pattern.lastIndex = 0;  // 重置 lastIndex
let match;
while ((match = pattern.exec(str)) !== null) {
    console.log(`  找到 ${match[0]}，位置 ${match.index}`);
    console.log(`    组1: ${match[1]}, 组2: ${match[2]}`);
}

// ========== 5. match 方法 ==========

console.log("\n=== 5. match 方法 ===");

const text2 = "Hello World Hello JavaScript";

// 不带 g 修饰符：返回第一个匹配及捕获组、索引等信息
const result1 = text2.match(/Hello/);
console.log("不带 g 的 match:", result1);
console.log("  匹配值:", result1[0]);
console.log("  索引:", result1.index);

// 带 g 修饰符：返回所有匹配的数组
const result2 = text2.match(/Hello/g);
console.log("带 g 的 match:", result2);

// 没有匹配返回 null
const result3 = text2.match(/Bye/g);
console.log("没有匹配:", result3);

// matchAll（ES2020）- 返回迭代器，包含所有匹配的详细信息
console.log("\nmatchAll:");
const text3 = "a1b2c3d4";
const iterator = text3.matchAll(/(\w)(\d)/g);
for (const m of iterator) {
    console.log(`  ${m[0]}: 字母=${m[1]}, 数字=${m[2]}, 位置=${m.index}`);
}

// ========== 6. replace 方法 ==========

console.log("\n=== 6. replace 方法 ===");

const text4 = "Hello World Hello";

// 简单替换（只替换第一个）
console.log("替换第一个:", text4.replace("Hello", "Hi"));

// 正则全局替换
console.log("全局替换:", text4.replace(/Hello/g, "Hi"));

// 使用捕获组
const dateStr = "2024-09-09";
const formatted = dateStr.replace(/(\d{4})-(\d{2})-(\d{2})/, "$1年$2月$3日");
console.log("日期格式化:", formatted);

// 使用函数作为替换参数
const text5 = "hello world";
const result4 = text5.replace(/\b\w/g, function(char) {
    return char.toUpperCase();
});
console.log("首字母大写:", result4);

// 安全应用：敏感词替换
function maskSensitive(text, words) {
    words.forEach(word => {
        const regex = new RegExp(word, "gi");
        text = text.replace(regex, "*".repeat(word.length));
    });
    return text;
}

const sensitiveWords = ["病毒", "攻击", "木马"];
const original = "这个病毒攻击利用了木马程序，非常危险。";
const masked = maskSensitive(original, sensitiveWords);
console.log("\n敏感词替换:");
console.log("  原文:", original);
console.log("  替换:", masked);

// 手机号脱敏
const phone = "13812345678";
const maskedPhone = phone.replace(/(\d{3})\d{4}(\d{4})/, "$1****$2");
console.log("手机号脱敏:", maskedPhone);

// ========== 7. search 方法 ==========

console.log("\n=== 7. search 方法 ===");

// search() - 查找第一个匹配的索引，找不到返回 -1
const text6 = "Hello World";

console.log("search('World'):", text6.search("World"));
console.log("search(/world/i):", text6.search(/world/i));
console.log("search('Bye'):", text6.search("Bye"));

// 与 indexOf 的区别：search 支持正则表达式

// ========== 8. 常用正则模式 ==========

console.log("\n=== 8. 常用正则模式 ===");

// 邮箱验证
const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
console.log("邮箱 test@example.com:", emailPattern.test("test@example.com"));

// 手机号码（中国）
const phonePattern = /^1[3-9]\d{9}$/;
console.log("手机号 13812345678:", phonePattern.test("13812345678"));

// URL
const urlPattern = /^https?:\/\/.+/;
console.log("URL https://example.com:", urlPattern.test("https://example.com"));

// IP 地址（IPv4 简单版）
const ipPattern = /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/;
console.log("IP 192.168.1.1:", ipPattern.test("192.168.1.1"));

// 身份证号
const idCardPattern = /^\d{17}[\dXx]$/;
console.log("身份证 110101199001011234:", idCardPattern.test("110101199001011234"));

// 中文字符
const chinesePattern = /[\u4e00-\u9fa5]/;
console.log("包含中文 '你好world':", chinesePattern.test("你好world"));

// HTML 标签
const htmlPattern = /<[^>]+>/g;
const htmlStr = "<p>Hello <b>World</b></p>";
console.log("HTML 标签提取:", htmlStr.match(htmlPattern));

// 用户名（字母数字下划线，3-20位）
const usernamePattern = /^[a-zA-Z0-9_]{3,20}$/;
console.log("用户名 admin_123:", usernamePattern.test("admin_123"));

// 强密码（至少8位，包含大小写字母和数字）
const passwordPattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/;
console.log("强密码 Abc12345:", passwordPattern.test("Abc12345"));
console.log("弱密码 12345678:", passwordPattern.test("12345678"));

// ========== 9. 安全应用：注入检测 ==========

console.log("\n=== 9. 安全示例：注入检测 ===");

// SQL 注入特征检测
function detectSQLInjection(input) {
    const patterns = [
        /\bunion\b.*\bselect\b/i,
        /\bselect\b.*\bfrom\b/i,
        /\binsert\b.*\binto\b/i,
        /\bdelete\b.*\bfrom\b/i,
        /\bdrop\b.*\btable\b/i,
        /'(\s*or\s*'[^']*'[^']*')/i,
        /;--/,
        /\bexec\b/i,
        /\bxp_cmdshell\b/i
    ];

    for (let i = 0; i < patterns.length; i++) {
        if (patterns[i].test(input)) {
            return {
                detected: true,
                pattern: patterns[i].toString(),
                message: "检测到潜在的 SQL 注入特征"
            };
        }
    }

    return { detected: false, message: "未检测到 SQL 注入特征" };
}

const testInputs = [
    "正常的用户名",
    "' OR '1'='1",
    "1; DROP TABLE users--",
    "union select * from users--",
    "admin"
];

testInputs.forEach(input => {
    const result = detectSQLInjection(input);
    console.log(`  "${input}": ${result.detected ? "可疑" : "安全"}`);
    if (result.detected) {
        console.log(`    匹配模式: ${result.pattern}`);
    }
});

// XSS 特征检测
function detectXSS(input) {
    const patterns = [
        /<script[^>]*>.*<\/script>/i,
        /javascript:/i,
        /on\w+\s*=/i,
        /<iframe[^>]*>/i,
        /eval\s*\(/i
    ];

    return patterns.some(pattern => pattern.test(input));
}

const xssTests = [
    "<script>alert('xss')</script>",
    "<img src=x onerror=alert(1)>",
    "javascript:alert(1)",
    "正常文本",
    '<a href="javascript:alert(1)">点击</a>'
];

console.log("\nXSS 检测:");
xssTests.forEach(input => {
    const isXSS = detectXSS(input);
    console.log(`  "${input.substring(0, 30)}...": ${isXSS ? "可疑" : "安全"}`);
});

console.log("\n=== 示例运行完成 ===");
