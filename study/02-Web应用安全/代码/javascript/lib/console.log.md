# console.log - JavaScript 控制台

> JavaScript 内置的控制台对象，用于输出调试信息、日志记录等。

---

## 一、基本用法

```javascript
// 普通输出
console.log('Hello World');
console.log('值:', 123);

// 格式化输出 (Node.js 和部分浏览器支持)
console.log('Hello %s, you have %d messages', 'Alice', 5);
// %s 字符串, %d 数字, %j JSON, %% 百分号

// 不同级别的日志
console.log('普通信息');
console.info('提示信息');   // 通常与 log 相同
console.warn('警告信息');   // 黄色警告
console.error('错误信息');  // 红色错误
console.debug('调试信息');  // 调试级别
```

---

## 二、常用方法

### 2.1 格式化输出

```javascript
// 字符串替换
console.log('Hello %s!', 'World');  // Hello World!

// 数字格式化
console.log('整数: %d, 浮点数: %f', 42, 3.14);

// JSON 格式化 (Node.js)
const obj = {name: 'test', value: 123};
console.log('%j', obj);  // {"name":"test","value":123}

// CSS 样式 (浏览器)
console.log('%c彩色文字', 'color: red; font-size: 20px;');
console.log('%c红%c绿%c蓝', 
    'color:red', 'color:green', 'color:blue');
```

### 2.2 对象与数组输出

```javascript
// 普通输出（可能被截断）
const arr = [1, 2, 3, 4, 5];
console.log(arr);

const obj = {a: 1, b: {c: 2, d: 3}};
console.log(obj);

// dir - 以树状结构显示对象属性
console.dir(obj);
console.dir(document.body);  // 显示 DOM 对象属性

// table - 以表格形式显示
const users = [
    {name: 'Alice', age: 25, city: 'Beijing'},
    {name: 'Bob', age: 30, city: 'Shanghai'},
    {name: 'Charlie', age: 35, city: 'Guangzhou'}
];
console.table(users);
console.table(users, ['name', 'age']);  // 只显示指定列
```

### 2.3 调试与计时

```javascript
// assert - 断言，条件为假时输出错误
console.assert(1 === 2, '1 不等于 2');
// Assertion failed: 1 不等于 2

// count - 计数调用次数
console.count('点击次数');  // 点击次数: 1
console.count('点击次数');  // 点击次数: 2
console.count('点击次数');  // 点击次数: 3

// 重置计数
console.countReset('点击次数');
console.count('点击次数');  // 点击次数: 1

// time / timeEnd - 计时
console.time('循环耗时');
for (let i = 0; i < 1000000; i++) {
    // 循环体
}
console.timeEnd('循环耗时');  // 循环耗时: 2.345ms

// timeLog - 计时中间点
console.time('整体耗时');
// 步骤1
console.timeLog('整体耗时', '步骤1完成');
// 步骤2
console.timeLog('整体耗时', '步骤2完成');
console.timeEnd('整体耗时');

// group - 分组输出
console.group('用户信息');
console.log('姓名: Alice');
console.log('年龄: 25');
console.group('地址');
console.log('城市: 北京');
console.log('街道: XXX路');
console.groupEnd();
console.groupEnd();

// groupCollapsed - 默认折叠的分组
console.groupCollapsed('详细日志');
console.log('...');
console.groupEnd();
```

### 2.4 其他方法

```javascript
// clear - 清空控制台
console.clear();

// trace - 输出调用栈
function foo() {
    function bar() {
        console.trace('跟踪调用栈');
    }
    bar();
}
foo();
/*
跟踪调用栈
bar @ VM:3
foo @ VM:5
(anonymous) @ VM:7
*/

// profile / profileEnd - 性能分析（浏览器）
console.profile('性能分析');
// ... 代码 ...
console.profileEnd();

// memory - 内存使用（部分浏览器）
console.memory;  // {usedJSHeapSize, totalJSHeapSize, jsHeapSizeLimit}
```

---

## 三、安全相关内容

### 3.1 XSS 风险（控制台输出）

```javascript
/*
    安全注意：
    console.log 输出用户可控的数据本身不会导致 XSS
    但在某些场景下需要注意：
*/

// 1. Node.js 中输出到日志文件
//    如果日志被前端页面直接展示，可能导致 XSS
const userInput = '<script>alert(1)</script>';
console.log(userInput);  // 控制台输出是安全的
// 但如果把日志内容渲染到 HTML 页面，就需要转义

// 2. 控制台注入（浏览器扩展）
//    恶意扩展可能修改 console 行为

// 3. 敏感信息泄露
//    不要在生产环境输出敏感数据
console.log('用户密码:', password);      // ❌ 泄露密码
console.log('Token:', authToken);        // ❌ 泄露 Token
console.log('用户数据:', userData);      // ❌ 泄露隐私

// 生产环境禁用 console.log
// 方法1: 重写 console.log
if (process.env.NODE_ENV === 'production') {
    console.log = function() {};
    console.warn = function() {};
    // ...
}

// 方法2: 使用构建工具移除（如 terser/webpack）
```

### 3.2 原型污染风险

```javascript
/*
    console 是一个对象，理论上可能被原型污染影响
    但实际中这不是主要的攻击面
*/

// 安全的日志函数
function safeLog(...args) {
    // 生产环境不输出
    if (process.env.NODE_ENV === 'production') return;
    
    // 可以添加脱敏处理
    const sanitized = args.map(arg => {
        if (typeof arg === 'object' && arg !== null) {
            // 移除敏感字段
            const copy = {...arg};
            delete copy.password;
            delete copy.token;
            delete copy.secret;
            return copy;
        }
        return arg;
    });
    
    console.log(...sanitized);
}

// 使用
safeLog('用户登录', {username: 'admin', password: '123456', token: 'xxx'});
// 输出时 password 和 token 会被移除
```

### 3.3 日志最佳实践

```javascript
// ===== 日志级别 =====
const LogLevel = {
    DEBUG: 0,
    INFO: 1,
    WARN: 2,
    ERROR: 3,
    NONE: 4
};

class Logger {
    constructor(level = LogLevel.INFO) {
        this.level = level;
    }
    
    debug(...args) {
        if (this.level <= LogLevel.DEBUG) {
            console.debug('[DEBUG]', ...args);
        }
    }
    
    info(...args) {
        if (this.level <= LogLevel.INFO) {
            console.info('[INFO]', ...args);
        }
    }
    
    warn(...args) {
        if (this.level <= LogLevel.WARN) {
            console.warn('[WARN]', ...args);
        }
    }
    
    error(...args) {
        if (this.level <= LogLevel.ERROR) {
            console.error('[ERROR]', ...args);
        }
    }
}

// 使用
const logger = new Logger(
    process.env.NODE_ENV === 'production' ? LogLevel.ERROR : LogLevel.DEBUG
);

logger.debug('调试信息');   // 生产环境不输出
logger.info('普通信息');
logger.warn('警告信息');
logger.error('错误信息');

// ===== 结构化日志（JSON 格式）=====
function jsonLog(level, message, data = {}) {
    const logEntry = {
        timestamp: new Date().toISOString(),
        level,
        message,
        ...data
    };
    console.log(JSON.stringify(logEntry));
}

jsonLog('info', '用户登录', {userId: 123, ip: '1.2.3.4'});
// {"timestamp":"...","level":"info","message":"用户登录","userId":123,"ip":"1.2.3.4"}
```

---

## 四、Node.js 控制台附加功能

```javascript
// Node.js 特有

// 输出到 stderr
console.error('错误信息');  // 输出到 stderr 流
console.warn('警告信息');    // 输出到 stderr 流

// 自定义控制台
const { Console } = require('console');
const fs = require('fs');

const output = fs.createWriteStream('./stdout.log');
const errorOutput = fs.createWriteStream('./stderr.log');

const logger = new Console({ stdout: output, stderr: errorOutput });
logger.log('写入 stdout.log');
logger.error('写入 stderr.log');
```

---

## 五、注意事项

| 注意点 | 说明 |
|-------|------|
| 生产环境 | 避免输出敏感信息，使用日志框架代替 |
| 性能 | 大量 console.log 会影响性能 |
| 副作用 | console.log 对对象的引用是实时的，展开时才求值 |
| 循环引用 | 包含循环引用的对象可能输出异常 |
| 浏览器兼容性 | 部分方法在旧浏览器中不可用 |
| 输出顺序 | console 输出可能是异步的（取决于实现） |
