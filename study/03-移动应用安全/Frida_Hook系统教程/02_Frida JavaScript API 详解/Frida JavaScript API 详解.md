# Frida JavaScript API 详解

### 2.1 Process / Module / Pointer API

```javascript
// Process: 获取进程信息
console.log("进程名:", Process.id);
console.log("架构:", Process.arch);        // arm64 / x64
console.log("平台:", Process.platform);    // linux / darwin

// Module: 枚举已加载模块
Process.enumerateModules().forEach(function(m) {
    console.log(m.name, m.base, m.size);
});

// 查找特定模块
var lib = Process.findModuleByName("libnative.so");
console.log("基址:", lib.base, "大小:", lib.size);

// 查找导出函数地址
var addr = Module.findExportByName("libnative.so", "Java_com_example_nativeFunc");
console.log("函数地址:", addr);

// Pointer: 指针操作
var ptr1 = ptr("0x12345678");
var ptr2 = ptr(lib.base).add(0x1000);
console.log(ptr2);
```

### 2.2 Interceptor（函数 Hook 基础）

Interceptor 是 Frida 最核心的 API，用于在函数入口/出口插入自定义逻辑。

```javascript
// Hook Native 函数
var funcAddr = Module.findExportByName("libc.so", "open");
Interceptor.attach(funcAddr, {
    onEnter: function(args) {
        // args[0] = 第一个参数
        // this 上下文可保存数据传递到 onLeave
        this.filename = args[0].readUtf8String();
        console.log("[open] 文件:", this.filename);
    },
    onLeave: function(retval) {
        // retval = 返回值
        console.log("[open] 返回值:", retval.toInt32());
        // 修改返回值
        // retval.replace(0);
    }
});

// Hook 地址（偏移方式）
var base = Module.findBaseAddress("libnative.so");
Interceptor.attach(base.add(0x1234), {
    onEnter: function(args) { /* ... */ },
    onLeave: function(retval) { /* ... */ }
});
```

### 2.3 Memory（内存读写搜索）

```javascript
// 读取内存
var data = Memory.readByteArray(ptr("0x12345678"), 64);
console.log(hexdump(data));

// 写入内存
Memory.writeByteArray(ptr("0x12345678"), [0x90, 0x90, 0x90, 0x90]);

// 读取字符串
var str = Memory.readUtf8String(ptr("0x12345678"));
var wstr = Memory.readUtf16String(ptr("0x12345678"));

// 内存搜索
Memory.scan(base, size, "48 8b ?? ?? 00 00", {
    onMatch: function(address, size) {
        console.log("匹配地址:", address);
    },
    onComplete: function() {
        console.log("搜索完成");
    }
});

// 内存保护修改（用于修改代码段）
Memory.protect(ptr("0x12345678"), 4096, 'rwx');

// 分配内存
var buf = Memory.alloc(256);
Memory.writeUtf8String(buf, "hello frida");
```

### 2.4 Java.perform（Android Java 层 Hook）

```javascript
Java.perform(function() {
    // Hook 静态方法
    var Log = Java.use("android.util.Log");
    Log.e.overload('java.lang.String', 'java.lang.String').implementation = function(tag, msg) {
        console.log("[Log.e]", tag, msg);
        return this.e(tag, msg);
    };

    // Hook 构造函数
    var String = Java.use("java.lang.String");
    String.$init.overload('[B', 'java.lang.String').implementation = function(bytes, charset) {
        console.log("[String 构造] bytes:", bytes);
        return this.$init(bytes, charset);
    };

    // Hook 内部类
    var InnerClass = Java.use("com.example.MainActivity$InnerTask");
    InnerClass.doTask.implementation = function() {
        console.log("[InnerTask.doTask] 被调用");
        return this.doTask();
    };

    // 主动调用
    var instance = String.$new("hello");
    console.log(instance.length());
});
```

### 2.5 ObjC（iOS Objective-C Hook）

```javascript
// Hook Objective-C 方法
var hook = ObjC.classes.UIViewController["- viewDidAppear:"];
Interceptor.attach(hook.implementation, {
    onEnter: function(args) {
        var self = new ObjC.Object(args[0]);
        console.log("[viewDidAppear]", self.$className);
    }
});

// Hook 类方法
var className = "NSString";
var methodName = "+ stringWithUTF8String:";
var method = ObjC.classes[className][methodName];
if (method) {
    Interceptor.attach(method.implementation, {
        onEnter: function(args) {
            console.log("NSString stringWithUTF8String 调用");
        }
    });
}

// 遍历所有类
for (var name in ObjC.classes) {
    if (name.indexOf("Target") !== -1) {
        console.log(name);
    }
}
```

### 2.6 NativeFunction / NativeCallback

```javascript
// NativeFunction: 创建对 Native 函数的调用句柄
var openPtr = Module.findExportByName("libc.so", "open");
var openFunc = new NativeFunction(openPtr, 'int', ['pointer', 'int']);
var fd = openFunc(Memory.allocUtf8String("/etc/hosts"), 0); // O_RDONLY
console.log("文件描述符:", fd);

// NativeCallback: 创建 C 回调函数传给 Native
var callback = new NativeCallback(function(result) {
    console.log("回调被调用, 结果:", result);
}, 'void', ['int']);
```

### 2.7 RPC（远程调用）

```javascript
// JS 端定义导出函数
rpc.exports = {
    getpid: function() {
        return Process.id;
    },
    readmemory: function(addr, len) {
        return Memory.readByteArray(ptr(addr), len);
    }
};

// Python 端调用
# import frida
# session = frida.get_usb_device().attach("com.example.app")
# script = session.create_script(js_code)
# script.load()
# pid = script.exports.getpid()
# data = script.exports.read_memory("0x12345678", 64)
```

---

---

## 📋 内容审核与补充建议

> 针对「Frida JavaScript API 详解」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

### ⚔️ 攻击技术
- ⚠️ 缺少attack相关内容

### 📖 参考资料
- ⚠️ 缺少参考资料/延伸阅读

---

## 📌 拓展学习资源

### 推荐学习路径
- 理论基础 → 工具实践 → 实战演练 → 深度研究
- 建议搭建本地实验环境进行动手练习

### 相关工具与资源
- 在线实验平台：Hack The Box、TryHackMe、VulnHub
- 技术文档：官方文档、RFC、OWASP 指南
- 社区资源：GitHub、安全论坛、技术博客
