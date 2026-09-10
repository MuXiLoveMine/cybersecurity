/**
 * 05_object.js - 对象创建、属性访问、遍历、常用方法
 * 
 * 本示例演示 JavaScript 对象的各种操作：
 * - 对象的创建方式
 * - 属性的访问、添加、修改、删除
 * - 对象的遍历
 * - 对象常用方法（keys、values、entries、assign 等）
 * - 解构赋值
 * - 展开运算符
 */

// ========== 1. 对象创建 ==========

console.log("=== 1. 对象创建 ===");

// 方式一：字面量（推荐）
const person = {
    name: "张三",
    age: 25,
    city: "北京",
    isStudent: false
};
console.log("字面量创建:", person);

// 方式二：构造函数
const person2 = new Object();
person2.name = "李四";
person2.age = 30;
console.log("构造函数创建:", person2);

// 方式三：Object.create
const proto = { greet: function() { return "你好！"; } };
const person3 = Object.create(proto);
person3.name = "王五";
console.log("Object.create 创建:", person3);
console.log("person3.greet():", person3.greet());

// 属性名包含特殊字符时需要加引号
const user = {
    "full name": "张三三",
    "user-age": 25
};
console.log("带特殊属性名的对象:", user);

// 计算属性名（ES6）
const key = "email";
const user2 = {
    name: "赵六",
    [key]: "zhaoliu@example.com"
};
console.log("计算属性名:", user2);

// ========== 2. 属性访问 ==========

console.log("\n=== 2. 属性访问 ===");

const student = {
    name: "小明",
    age: 18,
    grade: "高三"
};

// 点语法
console.log("姓名:", student.name);
console.log("年龄:", student.age);

// 方括号语法
console.log("年级:", student["grade"]);

// 方括号语法可以使用变量
const propName = "name";
console.log("动态属性访问:", student[propName]);

// 访问特殊属性名必须用方括号
console.log("full name:", user["full name"]);

// 访问不存在的属性返回 undefined（不会报错）
console.log("不存在的属性:", student.height);

// 可选链操作符（ES2020）- 安全访问嵌套属性
const order = {
    id: 123,
    customer: {
        name: "张三",
        address: {
            city: "北京"
        }
    }
};
// 安全访问：即使中间属性不存在也不会报错
console.log("城市:", order.customer?.address?.city);
console.log("邮编（不存在）:", order.customer?.address?.zipcode);

// ========== 3. 属性增删改 ==========

console.log("\n=== 3. 属性增删改 ===");

let car = {
    brand: "丰田",
    color: "白色"
};
console.log("原始对象:", car);

// 添加属性
car.price = 200000;
car["year"] = 2023;
console.log("添加属性后:", car);

// 修改属性
car.color = "黑色";
console.log("修改颜色后:", car);

// 删除属性
delete car.year;
console.log("删除 year 后:", car);

// 检查属性是否存在
console.log("'brand' in car:", "brand" in car);
console.log("'year' in car:", "year" in car);

// hasOwnProperty - 只检查自身属性（不检查原型链）
console.log("car.hasOwnProperty('brand'):", car.hasOwnProperty('brand'));
console.log("car.hasOwnProperty('toString'):", car.hasOwnProperty('toString'));

// ========== 4. 对象遍历 ==========

console.log("\n=== 4. 对象遍历 ===");

const book = {
    title: "JavaScript 入门",
    author: "张三",
    price: 59.9,
    pages: 300
};

// --- for...in ---
console.log("for...in 遍历:");
for (let key in book) {
    if (book.hasOwnProperty(key)) {
        console.log(`  ${key}: ${book[key]}`);
    }
}

// --- Object.keys ---
console.log("\nObject.keys 获取所有键:");
const keys = Object.keys(book);
console.log("键数组:", keys);
keys.forEach(key => {
    console.log(`  ${key}: ${book[key]}`);
});

// --- Object.values ---
console.log("\nObject.values 获取所有值:");
const values = Object.values(book);
console.log("值数组:", values);

// --- Object.entries ---
console.log("\nObject.entries 获取键值对:");
const entries = Object.entries(book);
console.log("键值对数组:", entries);

for (let [key, value] of entries) {
    console.log(`  ${key}: ${value}`);
}

// ========== 5. 对象常用方法 ==========

console.log("\n=== 5. 对象常用方法 ===");

// --- Object.assign - 合并/复制对象 ---
const target = { a: 1, b: 2 };
const source1 = { b: 3, c: 4 };
const source2 = { d: 5 };

const merged = Object.assign({}, target, source1, source2);
console.log("Object.assign 合并:", merged);
// 后面的属性会覆盖前面的

// --- 展开运算符（ES6）---
const merged2 = { ...target, ...source1, ...source2 };
console.log("展开运算符合并:", merged2);

// 浅拷贝对象
const copy = { ...book };
console.log("浅拷贝:", copy);
copy.title = "修改后的标题";
console.log("原对象标题不变:", book.title);

// --- Object.freeze - 冻结对象 ---
const frozen = Object.freeze({ x: 1, y: 2 });
// frozen.x = 10;  // 严格模式下报错，非严格模式下静默失败
console.log("冻结对象:", frozen);
console.log("是否冻结:", Object.isFrozen(frozen));

// --- Object.seal - 密封对象 ---
const sealed = Object.seal({ m: 10, n: 20 });
sealed.m = 100;     // 可以修改
// sealed.p = 30;   // 不能添加
// delete sealed.n; // 不能删除
console.log("密封对象:", sealed);
console.log("是否密封:", Object.isSealed(sealed));

// ========== 6. 解构赋值 ==========

console.log("\n=== 6. 解构赋值（ES6） ===");

const personInfo = {
    name: "小红",
    age: 22,
    city: "上海",
    job: "工程师"
};

// 基本解构
const { name, age } = personInfo;
console.log("解构:", name, age);

// 重命名
const { name: personName, age: personAge } = personInfo;
console.log("重命名解构:", personName, personAge);

// 默认值
const { name: n, gender = "未知" } = personInfo;
console.log("带默认值:", n, gender);

// 嵌套解构
const company = {
    name: "科技公司",
    address: {
        city: "北京",
        street: "中关村大街"
    },
    employees: 1000
};

const { address: { city, street } } = company;
console.log("嵌套解构:", city, street);

// ========== 7. 对象方法 ==========

console.log("\n=== 7. 对象方法 ===");

const calculator = {
    // 属性
    result: 0,

    // 方法（传统写法）
    add: function(x) {
        this.result += x;
        return this;  // 返回 this 支持链式调用
    },

    // 方法（ES6 简写）
    subtract(x) {
        this.result -= x;
        return this;
    },

    multiply(x) {
        this.result *= x;
        return this;
    },

    getResult() {
        return this.result;
    },

    reset() {
        this.result = 0;
        return this;
    }
};

// 链式调用
const calcResult = calculator.reset().add(10).multiply(2).subtract(5).getResult();
console.log("链式调用结果 (0 + 10) * 2 - 5 =", calcResult);

// ========== 8. 安全应用：用户对象安全处理 ==========

console.log("\n=== 8. 安全示例：用户信息脱敏 ===");

function maskUserInfo(user) {
    // 创建副本，避免修改原对象
    const masked = { ...user };

    // 手机号脱敏
    if (masked.phone) {
        masked.phone = masked.phone.replace(/(\d{3})\d{4}(\d{4})/, "$1****$2");
    }

    // 身份证号脱敏
    if (masked.idCard) {
        masked.idCard = masked.idCard.replace(/(\d{6})\d{8}(\d{4})/, "$1********$2");
    }

    // 邮箱脱敏
    if (masked.email) {
        const [username, domain] = masked.email.split("@");
        if (username.length > 2) {
            masked.email = username[0] + "***" + username[username.length - 1] + "@" + domain;
        }
    }

    // 移除敏感字段（如密码）
    delete masked.password;
    delete masked.token;

    return masked;
}

const userInfo = {
    id: 1,
    username: "admin",
    phone: "13812345678",
    email: "admin@example.com",
    idCard: "110101199001011234",
    password: "abc123",
    token: "xyz789"
};

console.log("原始用户信息:", userInfo);
console.log("脱敏后:", maskUserInfo(userInfo));

console.log("\n=== 示例运行完成 ===");
