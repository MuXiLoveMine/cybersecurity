/**
 * 08_file.js - Node.js fs 模块文件读写
 * 
 * 本示例演示 Node.js 中文件操作的各种方法：
 * - fs 模块引入
 * - 文件读取（同步/异步/Promise）
 * - 文件写入（同步/异步/追加）
 * - 目录操作
 * - 文件信息获取
 * - path 模块常用方法
 * 
 * 运行方式：node 08_file.js
 */

const fs = require('fs');
const path = require('path');

// ========== 1. 路径处理（path 模块） ==========

console.log("=== 1. 路径处理（path 模块） ===");

// 当前文件路径
console.log("__dirname:", __dirname);
console.log("__filename:", __filename);

// 拼接路径
const filePath = path.join(__dirname, "test.txt");
console.log("拼接路径:", filePath);

// 解析路径
console.log("basename:", path.basename(filePath));       // test.txt
console.log("basename 去扩展名:", path.basename(filePath, ".txt"));  // test
console.log("dirname:", path.dirname(filePath));         // 目录名
console.log("extname:", path.extname(filePath));         // .txt

// 获取绝对路径
console.log("resolve:", path.resolve("test.txt"));

// 解析路径对象
const parsed = path.parse(filePath);
console.log("parse:", parsed);

// ========== 2. 文件写入 ==========

console.log("\n=== 2. 文件写入 ===");

const testFile = path.join(__dirname, "example.txt");

// --- 异步写入 ---
fs.writeFile(testFile, "Hello, Node.js!\n这是第一行文本。\n", "utf-8", (err) => {
    if (err) {
        console.error("异步写入失败:", err);
        return;
    }
    console.log("异步写入成功:", testFile);
});

// --- 同步写入 ---
try {
    const syncFile = path.join(__dirname, "example_sync.txt");
    fs.writeFileSync(syncFile, "这是同步写入的文件。\n", "utf-8");
    console.log("同步写入成功:", syncFile);
} catch (err) {
    console.error("同步写入失败:", err);
}

// --- 追加写入 ---
const appendFile = path.join(__dirname, "log.txt");

// 异步追加
fs.appendFile(appendFile, `[${new Date().toLocaleString()}] 程序运行了\n`, "utf-8", (err) => {
    if (err) {
        console.error("追加写入失败:", err);
        return;
    }
    console.log("追加写入成功:", appendFile);
});

// ========== 3. 文件读取 ==========

console.log("\n=== 3. 文件读取 ===");

// 先确保有文件可读
fs.writeFileSync(path.join(__dirname, "read_test.txt"), "第一行\n第二行\n第三行\n", "utf-8");

// --- 异步读取 ---
fs.readFile(path.join(__dirname, "read_test.txt"), "utf-8", (err, data) => {
    if (err) {
        console.error("异步读取失败:", err);
        return;
    }
    console.log("异步读取内容:");
    console.log(data);
});

// --- 同步读取 ---
try {
    const data = fs.readFileSync(path.join(__dirname, "read_test.txt"), "utf-8");
    console.log("同步读取内容:");
    console.log(data);
} catch (err) {
    console.error("同步读取失败:", err);
}

// --- Promise 方式（fs.promises）---
async function readWithPromise() {
    try {
        const data = await fs.promises.readFile(
            path.join(__dirname, "read_test.txt"),
            "utf-8"
        );
        console.log("Promise 方式读取成功，长度:", data.length, "字符");
    } catch (err) {
        console.error("Promise 读取失败:", err);
    }
}
readWithPromise();

// ========== 4. 目录操作 ==========

console.log("\n=== 4. 目录操作 ===");

// --- 创建目录 ---
const newDir = path.join(__dirname, "test_dir");
const nestedDir = path.join(__dirname, "test_dir", "sub_dir");

// 递归创建多级目录
fs.mkdir(nestedDir, { recursive: true }, (err) => {
    if (err) {
        console.error("创建目录失败:", err);
        return;
    }
    console.log("目录创建成功:", nestedDir);
});

// --- 读取目录 ---
fs.readdir(__dirname, (err, files) => {
    if (err) {
        console.error("读取目录失败:", err);
        return;
    }
    console.log("当前目录文件数:", files.length);
    console.log("文件列表（前 10 个）:", files.slice(0, 10));
});

// --- 检查文件/目录是否存在 ---
fs.access(testFile, fs.constants.F_OK, (err) => {
    console.log("文件是否存在:", err ? "不存在" : "存在");
});

// ========== 5. 文件信息 ==========

console.log("\n=== 5. 文件信息 ===");

fs.stat(__filename, (err, stats) => {
    if (err) {
        console.error("获取文件信息失败:", err);
        return;
    }
    console.log("文件信息:");
    console.log("  是文件:", stats.isFile());
    console.log("  是目录:", stats.isDirectory());
    console.log("  文件大小:", stats.size, "字节");
    console.log("  创建时间:", stats.birthtime.toLocaleString());
    console.log("  修改时间:", stats.mtime.toLocaleString());
});

// ========== 6. 删除文件和目录 ==========

console.log("\n=== 6. 删除文件和目录 ===");

// 删除文件
const deleteFile = path.join(__dirname, "to_delete.txt");
fs.writeFileSync(deleteFile, "将要被删除的文件", "utf-8");
console.log("创建待删除文件:", deleteFile);

fs.unlink(deleteFile, (err) => {
    if (err) {
        console.error("删除文件失败:", err);
        return;
    }
    console.log("文件已删除:", deleteFile);
});

// 删除空目录
const emptyDir = path.join(__dirname, "empty_dir");
fs.mkdirSync(emptyDir);
console.log("创建空目录:", emptyDir);

fs.rmdir(emptyDir, (err) => {
    if (err) {
        console.error("删除目录失败:", err);
        return;
    }
    console.log("目录已删除:", emptyDir);
});

// ========== 7. 流式读写（大文件） ==========

console.log("\n=== 7. 流式读写 ===");

// 创建可读流
const readStream = fs.createReadStream(path.join(__dirname, "read_test.txt"), "utf-8");

let content = "";
readStream.on("data", (chunk) => {
    content += chunk;
    console.log("  读取到一块数据，大小:", chunk.length);
});

readStream.on("end", () => {
    console.log("流式读取完成，总长度:", content.length);
});

readStream.on("error", (err) => {
    console.error("流式读取错误:", err);
});

// ========== 8. 安全应用：安全文件处理 ==========

console.log("\n=== 8. 安全示例：安全文件处理 ===");

// 路径遍历检测（防止目录遍历攻击）
function isPathSafe(baseDir, targetPath) {
    const resolvedBase = path.resolve(baseDir);
    const resolvedTarget = path.resolve(targetPath);
    return resolvedTarget.startsWith(resolvedBase);
}

const baseDir = path.join(__dirname, "safe_dir");
const safePath = path.join(baseDir, "file.txt");
const unsafePath = path.join(baseDir, "../etc/passwd");

console.log("基础目录:", baseDir);
console.log("安全路径是否安全:", isPathSafe(baseDir, safePath));
console.log("危险路径是否安全:", isPathSafe(baseDir, unsafePath));

// 安全读取文件（检查路径）
function safeReadFile(baseDir, relativePath, callback) {
    const fullPath = path.join(baseDir, relativePath);

    if (!isPathSafe(baseDir, fullPath)) {
        callback(new Error("非法路径：检测到目录遍历攻击"), null);
        return;
    }

    fs.readFile(fullPath, "utf-8", callback);
}

// 演示
const safeDir = path.join(__dirname, "safe_dir");
if (!fs.existsSync(safeDir)) {
    fs.mkdirSync(safeDir);
}
fs.writeFileSync(path.join(safeDir, "test.txt"), "安全文件内容", "utf-8");

// 正常读取
safeReadFile(safeDir, "test.txt", (err, data) => {
    if (err) {
        console.log("正常读取错误:", err.message);
    } else {
        console.log("正常读取成功:", data);
    }
});

// 尝试目录遍历攻击
safeReadFile(safeDir, "../example.txt", (err, data) => {
    if (err) {
        console.log("路径遍历攻击被阻止:", err.message);
    } else {
        console.log("读取到数据:", data);
    }
});

// 清理临时文件（延迟执行，确保前面的异步操作完成）
setTimeout(() => {
    console.log("\n=== 清理临时文件 ===");
    const tempFiles = [
        "example.txt",
        "example_sync.txt",
        "log.txt",
        "read_test.txt",
        "test_dir"
    ];

    tempFiles.forEach(file => {
        const fullPath = path.join(__dirname, file);
        try {
            const stats = fs.statSync(fullPath);
            if (stats.isDirectory()) {
                // 递归删除目录
                fs.rmSync(fullPath, { recursive: true, force: true });
                console.log("删除目录:", file);
            } else {
                fs.unlinkSync(fullPath);
                console.log("删除文件:", file);
            }
        } catch (err) {
            // 文件不存在则忽略
        }
    });

    // 删除 safe_dir
    try {
        fs.rmSync(safeDir, { recursive: true, force: true });
        console.log("删除目录: safe_dir");
    } catch (err) {}

    console.log("\n=== 示例运行完成 ===");
}, 1000);
