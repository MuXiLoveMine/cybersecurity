/**
 * 06_string.js - 字符串操作、模板字符串、常用方法
 * 
 * 本示例演示 JavaScript 字符串的各种操作：
 * - 字符串创建
 * - 模板字符串
 * - 常用字符串方法（查找、截取、替换、分割等）
 * - 字符串遍历
 * - 字符串与数字转换
 */

// ========== 1. 字符串创建 ==========

console.log("=== 1. 字符串创建 ===");

// 单引号
const str1 = 'Hello, World!';
console.log("单引号:", str1);

// 双引号
const str2 = "你好，世界！";
console.log("双引号:", str2);

// 反引号（模板字符串）
const str3 = `这是模板字符串`;
console.log("模板字符串:", str3);

// 字符串中包含引号
const quote1 = '他说："你好"';
const quote2 = "她说：'再见'";
const quote3 = `他说："我说：'你好'"`;
console.log("嵌套引号:", quote1, quote2, quote3);

// 转义字符
const escaped = '第一行\n第二行\t制表符\\反斜杠\'单引号"双引号';
console.log("转义字符:", escaped);

// ========== 2. 模板字符串 ==========

console.log("\n=== 2. 模板字符串 ===");

const name = "小明";
const age = 20;

// 变量插值
const greeting = `你好，我叫${name}，今年${age}岁。`;
console.log("变量插值:", greeting);

// 表达式计算
const math = `10 + 5 = ${10 + 5}`;
console.log("表达式:", math);

// 调用函数
function toUpper(str) {
    return str.toUpperCase();
}
const funcStr = `转大写：${toUpper("hello")}`;
console.log("函数调用:", funcStr);

// 多行字符串
const multiLine = `
    静夜思
    床前明月光，
    疑是地上霜。
    举头望明月，
    低头思故乡。
`;
console.log("多行字符串:", multiLine);

// 嵌套模板字符串
const isAdmin = true;
const userStatus = `用户状态：${isAdmin ? `管理员（最高权限）` : `普通用户`}`;
console.log("嵌套模板:", userStatus);

// ========== 3. 字符串长度与字符访问 ==========

console.log("\n=== 3. 字符串长度与字符访问 ===");

const str = "Hello, 世界！";

// 长度
console.log("字符串:", str);
console.log("长度:", str.length);

// 访问字符
console.log("第 1 个字符:", str[0]);
console.log("第 7 个字符:", str[6]);

// charAt 方法
console.log("charAt(0):", str.charAt(0));
console.log("charAt(100):", str.charAt(100));  // 越界返回空字符串

// charCodeAt - 获取字符的 Unicode 编码
console.log("charCodeAt(0):", str.charCodeAt(0));  // 72 ('H')

// at 方法（ES2022）- 支持负数索引
console.log("at(-1):", str.at(-1));   // 最后一个字符
console.log("at(-2):", str.at(-2));   // 倒数第二个字符

// ========== 4. 字符串查找 ==========

console.log("\n=== 4. 字符串查找 ===");

const sentence = "The quick brown fox jumps over the lazy dog. The fox is brown.";

// indexOf - 查找第一次出现的位置
console.log("indexOf('fox'):", sentence.indexOf("fox"));          // 16
console.log("indexOf('cat'):", sentence.indexOf("cat"));          // -1（不存在）
console.log("indexOf('the'):", sentence.indexOf("the"));          // 31

// 从指定位置开始查找
console.log("indexOf('The', 10):", sentence.indexOf("The", 10));  // 45

// lastIndexOf - 查找最后一次出现的位置
console.log("lastIndexOf('fox'):", sentence.lastIndexOf("fox"));  // 49
console.log("lastIndexOf('brown'):", sentence.lastIndexOf("brown")); // 56

// includes - 是否包含（ES6）
console.log("includes('fox'):", sentence.includes("fox"));        // true
console.log("includes('cat'):", sentence.includes("cat"));        // false

// startsWith - 是否以...开头（ES6）
console.log("startsWith('The'):", sentence.startsWith("The"));    // true
console.log("startsWith('the'):", sentence.startsWith("the"));    // false

// endsWith - 是否以...结尾（ES6）
console.log("endsWith('.'):", sentence.endsWith("."));            // true
console.log("endsWith('dog'):", sentence.endsWith("dog"));        // false

// ========== 5. 字符串截取 ==========

console.log("\n=== 5. 字符串截取 ===");

const text = "JavaScript 是一门很棒的语言";

// slice - 推荐使用，支持负数
console.log("原始字符串:", text);
console.log("slice(0, 10):", text.slice(0, 10));      // "JavaScript"
console.log("slice(13):", text.slice(13));              // "一门很棒的语言"
console.log("slice(-6):", text.slice(-6));              // "很棒的语言"
console.log("slice(-6, -3):", text.slice(-6, -3));     // "很棒的"

// substring - 不支持负数，参数会自动交换
console.log("substring(0, 10):", text.substring(0, 10));  // "JavaScript"
console.log("substring(10, 0):", text.substring(10, 0));  // "JavaScript"（自动交换）

// substr - 已弃用，第二个参数是长度
console.log("substr(0, 10):", text.substr(0, 10));        // "JavaScript"

// ========== 6. 大小写转换 ==========

console.log("\n=== 6. 大小写转换 ===");

const caseStr = "Hello World";

console.log("原始:", caseStr);
console.log("toUpperCase:", caseStr.toUpperCase());  // "HELLO WORLD"
console.log("toLowerCase:", caseStr.toLowerCase());  // "hello world"

// ========== 7. 去除空白 ==========

console.log("\n=== 7. 去除空白 ===");

const spaceStr = "   Hello World   ";

console.log("原始:", `[${spaceStr}]`);
console.log("trim():", `[${spaceStr.trim()}]`);              // 去除两端
console.log("trimStart():", `[${spaceStr.trimStart()}]`);    // 去除开头
console.log("trimEnd():", `[${spaceStr.trimEnd()}]`);        // 去除结尾

// ========== 8. 字符串替换 ==========

console.log("\n=== 8. 字符串替换 ===");

const replaceStr = "Hello World, Hello JavaScript";

// replace - 只替换第一个匹配
console.log("替换第一个 Hello:", replaceStr.replace("Hello", "Hi"));

// 正则全局替换
console.log("全局替换 Hello:", replaceStr.replace(/Hello/g, "Hi"));

// 忽略大小写替换
console.log("忽略大小写:", replaceStr.replace(/hello/gi, "Hi"));

// 使用函数作为替换参数
const result = replaceStr.replace(/Hello/g, function(match, index) {
    return `[${match}@${index}]`;
});
console.log("函数替换:", result);

// replaceAll - 全部替换（ES2021）
console.log("replaceAll:", replaceStr.replaceAll("Hello", "Hi"));

// ========== 9. 字符串分割与拼接 ==========

console.log("\n=== 9. 字符串分割与拼接 ===");

// split - 分割成数组
const csv = "苹果,香蕉,橙子,葡萄";
const fruits = csv.split(",");
console.log("split 分割:", fruits);

// 限制分割数量
const limited = csv.split(",", 2);
console.log("限制分割 2 个:", limited);

// 分割每个字符
const chars = "hello".split("");
console.log("分割每个字符:", chars);

// join - 数组拼接成字符串
const joined = fruits.join(" - ");
console.log("join 拼接:", joined);

// concat - 字符串拼接
const concatStr = "Hello".concat(" ", "World", "!");
console.log("concat:", concatStr);

// ========== 10. 其他方法 ==========

console.log("\n=== 10. 其他字符串方法 ===");

// repeat - 重复
console.log("'ab'.repeat(3):", "ab".repeat(3));  // "ababab"

// padStart / padEnd - 填充
console.log("'5'.padStart(3, '0'):", "5".padStart(3, "0"));     // "005"
console.log("'5'.padEnd(3, '0'):", "5".padEnd(3, "0"));         // "500"

// 应用：格式化日期
const month = "9";
const day = "5";
console.log("格式化日期:", `2024-${month.padStart(2, '0')}-${day.padStart(2, '0')}`);

// ========== 11. 字符串遍历 ==========

console.log("\n=== 11. 字符串遍历 ===");

const helloStr = "Hello";

// for 循环
console.log("for 循环:");
for (let i = 0; i < helloStr.length; i++) {
    console.log(" ", helloStr[i]);
}

// for...of
console.log("for...of:");
for (let char of helloStr) {
    console.log(" ", char);
}

// ========== 12. 安全应用：输入处理 ==========

console.log("\n=== 12. 安全示例：输入处理 ===");

// 去除首尾空白
function sanitizeInput(input) {
    if (typeof input !== "string") {
        return "";
    }
    return input.trim();
}

console.log("去除空白:", `[${sanitizeInput("  用户名  ")}]`);

// 防止 XSS 的 HTML 转义
function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

// 由于在 Node.js 环境中没有 document，这里手动实现
function escapeHtmlNode(text) {
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}

const userInput = '<script>alert("XSS攻击")</script>';
console.log("用户输入:", userInput);
console.log("HTML 转义后:", escapeHtmlNode(userInput));

// SQL 注入简单检测
function detectSQLInjection(input) {
    const patterns = [
        /(\b(union|select|insert|update|delete|drop|alter)\b)/i,
        /'(\s*or\s*'[^']*'[^']*')/i,
        /;--/,
        /\bexec\b/i
    ];
    return patterns.some(pattern => pattern.test(input));
}

console.log("SQL 注入检测 'admin' OR '1'='1':", detectSQLInjection("' OR '1'='1"));
console.log("SQL 注入检测 '正常输入':", detectSQLInjection("正常输入"));

console.log("\n=== 示例运行完成 ===");
