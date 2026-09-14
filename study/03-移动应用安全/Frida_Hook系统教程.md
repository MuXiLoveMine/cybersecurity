# Frida 动态插桩系统教程

> 本教程系统讲解 Frida 动态插桩框架的原理、API、Android/iOS 实战技巧与高级用法，适用于移动安全研究与渗透测试场景。

---

## 目录

1. [Frida 概述](#1-frida-概述)
2. [Frida JavaScript API 详解](#2-frida-javascript-api-详解)
3. [Android Hook 实战](#3-android-hook-实战)
4. [iOS Hook 实战](#4-ios-hook-实战)
5. [高级技巧](#5-高级技巧)
6. [常用 Frida 脚本集合](#6-常用-frida-脚本集合)

---

## 1. Frida 概述

### 1.1 动态插桩技术原理

动态插桩（Dynamic Instrumentation）是指在程序运行时，将额外代码注入目标进程，从而实现对函数调用、内存读写、执行流的监控与修改。其核心思想是：在目标函数的入口处插入跳转指令，使 CPU 跳转到自定义的处理逻辑，处理完成后再返回原函数继续执行。

与静态分析（反编译）相比，动态插桩有如下优势：

- 不需要理解全部反编译代码，可直接观察运行时行为
- 能获取加密前的明文数据（如加解密函数的入参和返回值）
- 能修改函数逻辑（如绕过检测、修改返回值）

### 1.2 Frida 架构（Agent / Server / Gum Stalker）

Frida 采用 **Client-Server** 架构，主要由以下组件组成：

```
┌─────────────┐        ┌──────────────────────────┐
│  Frida CLI  │        │      Target Process       │
│  (Python)   │◄─────►│  ┌──────────────────────┐  │
│  frida -tools│  USB/  │  │   frida-agent (JS)   │  │
│             │  TCP   │  │   ┌────────────────┐ │  │
└─────────────┘        │  │   │  Gum/Stalker   │ │  │
                       │  │   └────────────────┘ │  │
                       │  └──────────────────────┘  │
                       │         ▲                   │
                       │  ┌──────┴───────┐           │
                       │  │ frida-server │           │
                       │  │ (native daemon)│          │
                       │  └──────────────┘           │
                       └──────────────────────────────┘
```

| 组件 | 说明 |
|------|------|
| **frida-server** | 运行在目标设备（Android/iOS）上的守护进程，负责进程注入与通信 |
| **frida-agent** | 被注入目标进程的 JS 运行时，通过 V8/QuickJS 执行用户脚本 |
| **Gum** | Frida 的核心引擎，提供 Interceptor、Memory、Stalker 等底层能力 |
| **Stalker** | Gum 中的代码执行跟踪引擎，可记录每条指令的执行路径 |
| **frida-tools** | PC 端 Python 工具包（frida、frida-trace、frida-ps 等） |

### 1.3 Frida vs Xposed 对比

| 特性 | Frida | Xposed |
|------|-------|--------|
| 工作层级 | Native + Java + ObjC | 仅 Java 层 |
| 注入时机 | 运行时动态注入（无需重启） | Zygote 启动时全局注入（需重启） |
| 脚本语言 | JavaScript/TypeScript | Java（需编译为模块） |
| 环境依赖 | frida-server + Python | Xposed Framework（需刷机） |
| iOS 支持 | 支持 | 不支持 |
| 隐蔽性 | 较低（易被检测） | 较高（系统级注入） |
| 开发效率 | 高（热重载） | 中（需编译部署） |
| 适用场景 | 快速分析、逆向、调试 | 持久化 Hook 模块、自动化测试 |

### 1.4 环境搭建

#### PC 端安装

```bash
# 安装 Python frida-tools
pip install frida-tools

# 验证版本
frida --version
```

#### Android 端 frida-server 部署

```bash
# 1. 确认设备架构
adb shell getprop ro.product.cpu.abi
# 输出如: arm64-v8a

# 2. 下载对应版本 frida-server
# https://github.com/frida/frida/releases
# 选择 frida-server-{version}-android-arm64.xz

# 3. 解压并推送
xz -d frida-server-17.0.0-android-arm64.xz
adb push frida-server-17.0.0-android-arm64 /data/local/tmp/frida-server
adb shell "chmod 755 /data/local/tmp/frida-server"

# 4. 启动（需要 root）
adb shell "su -c '/data/local/tmp/frida-server &'"

# 5. PC 端验证连接
frida-ps -U          # 列出设备进程
frida-ps -Ua         # 列出运行中的前台应用
```

#### iOS 端部署

```bash
# 越狱设备上通过 Cydia/Sileo 安装
# 添加源: https://build.frida.re
# 安装: Frida

# PC 端连接验证（USB）
frida-ps -U
```

---

## 2. Frida JavaScript API 详解

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

## 3. Android Hook 实战

### 3.1 Hook Java 方法（重载方法、构造函数、内部类）

```javascript
Java.perform(function() {
    var MainActivity = Java.use("com.example.app.MainActivity");

    // Hook 重载方法 - 通过 overload 指定参数类型
    MainActivity.login.overload('java.lang.String', 'java.lang.String').implementation = function(user, pass) {
        console.log("[login] 用户名:", user, "密码:", pass);
        var ret = this.login(user, pass);
        console.log("[login] 返回:", ret);
        return ret;
    };

    // Hook 所有重载
    MainActivity.login.overloads.forEach(function(overload) {
        overload.implementation = function() {
            console.log("[login] 参数:", JSON.stringify(arguments));
            return this.login.apply(this, arguments);
        };
    });

    // Hook 内部类 (类名用 $ 连接)
    var InnerTask = Java.use("com.example.app.MainActivity$InnerTask");
    InnerTask.run.implementation = function() {
        console.log("[InnerTask.run] 被触发");
        return this.run();
    };

    // Hook 动态加载的 Dex 类
    Java.enumerateClassLoaders().forEach(function(loader) {
        try {
            var factory = Java.ClassFactory.get(loader);
            var dynClass = factory.use("com.protected.DynamicClass");
            console.log("找到动态类:", dynClass);
        } catch(e) {}
    });
});
```

### 3.2 Hook Native 函数（JNI 函数、SO 库函数）

```javascript
// Hook JNI 注册的函数（JNI_OnLoad 动态注册）
var RegisterNatives = Module.findExportByName("libart.so", "art::JNI::RegisterNatives");
if (RegisterNatives) {
    Interceptor.attach(RegisterNatives, {
        onEnter: function(args) {
            var classObj = args[1];
            var methods = args[2];
            var count = args[3].toInt32();
            for (var i = 0; i < count; i++) {
                var name = Memory.readUtf8String(methods.add(i * Process.pointerSize * 3).readPointer());
                var sig  = Memory.readUtf8String(methods.add(i * Process.pointerSize * 3 + Process.pointerSize).readPointer());
                var fnPtr= methods.add(i * Process.pointerSize * 3 + Process.pointerSize * 2).readPointer();
                console.log("[RegisterNatives]", name, sig, fnPtr);
            }
        }
    });
}

// Hook SO 库导出函数
var nativeFunc = Module.findExportByName("libnative.so", "Java_com_example_NativeLib_decrypt");
Interceptor.attach(nativeFunc, {
    onEnter: function(args) {
        // JNI 函数: args[0]=JNIEnv, args[1]=jobject, args[2+]=实际参数
        var input = Java.vm.getEnv().getStringUtfChars(args[2], null).readUtf8String();
        console.log("[decrypt] 输入:", input);
        this.input = input;
    },
    onLeave: function(retval) {
        var output = Java.vm.getEnv().getStringUtfChars(retval, null).readUtf8String();
        console.log("[decrypt] 输出:", output);
    }
});

// Hook 未导出函数（IDA 分析偏移）
var base = Module.findBaseAddress("libnative.so");
Interceptor.attach(base.add(0x1A3C), {
    onEnter: function(args) {
        console.log("sub_1A3C 调用, 参数0:", args[0]);
    }
});
```

### 3.3 主动调用方法

```javascript
Java.perform(function() {
    // 获取已存在的实例
    Java.choose("com.example.app.CryptoUtil", {
        onMatch: function(instance) {
            console.log("找到实例:", instance);
            // 主动调用方法
            var result = instance.encrypt("test_data");
            console.log("加密结果:", result);
        },
        onComplete: function() {
            console.log("搜索完成");
        }
    });

    // 创建新实例调用
    var CryptoUtil = Java.use("com.example.app.CryptoUtil");
    var instance = CryptoUtil.$new();
    var result = instance.encrypt("test_data");
    console.log("结果:", result);
});
```

### 3.4 内存搜索与修改

```javascript
// 搜索内存中的特征值（如搜索金币数值 999999）
var ranges = Process.enumerateRanges('rw-');
var found = false;
ranges.forEach(function(range) {
    if (found) return;
    Memory.scan(range.base, range.size, "3F 42 0F 00", {  // 999999 的小端序
        onMatch: function(address) {
            console.log("找到金币地址:", address);
            // 修改为 9999999
            Memory.writeInt(address, 9999999);
            found = true;
        },
        onComplete: function() {}
    });
});
```

### 3.5 SSL Pinning 绕过

```javascript
// 通用 SSL Pinning 绕过脚本
Java.perform(function() {
    // TrustManager 绕过
    var X509TrustManager = Java.use('javax.net.ssl.X509TrustManager');
    var SSLContext = Java.use('javax.net.ssl.SSLContext');
    var TrustManager = Java.registerClass({
        name: 'com.frida.TrustManager',
        superClass: X509TrustManager,
        methods: {
            checkClientTrusted: function(chain, authType) {},
            checkServerTrusted: function(chain, authType) {},
            getAcceptedIssuers: function() { return []; }
        }
    });
    var TrustManagers = [TrustManager.$new()];
    var ctx = SSLContext.getInstance("TLS");
    ctx.init(null, TrustManagers, null);
    SSLContext.setDefault(ctx);

    // OkHttp CertificatePinner 绕过
    try {
        var CertificatePinner = Java.use('okhttp3.CertificatePinner');
        CertificatePinner.check.overload('java.lang.String', 'java.util.List').implementation = function() {};
    } catch(e) {}

    // Conscrypt 绕过
    try {
        var Conscrypt = Java.use('com.android.org.conscrypt.TrustManagerImpl');
        Conscrypt.verifyChain.implementation = function(untrustedChain, trustAnchorChain, host, clientAuth, ocspData, tlsSctData) {
            return untrustedChain;
        };
    } catch(e) {}
});
```

### 3.6 Root 检测绕过

```javascript
Java.perform(function() {
    // 绕过 Build.TAGS 检测
    var Build = Java.use("android.os.Build");
    Build.TAGS.value = "release-keys";

    // 绕过文件检测 (su, busybox)
    var File = Java.use("java.io.File");
    File.exists.implementation = function() {
        var path = this.getAbsolutePath();
        if (path.indexOf("su") !== -1 || path.indexOf("busybox") !== -1 || path.indexOf("magisk") !== -1) {
            console.log("[Root检测] 拦截文件检查:", path);
            return false;
        }
        return this.exists();
    };

    // 绕过 Runtime.exec("su") 检测
    var Runtime = Java.use("java.lang.Runtime");
    Runtime.exec.overload('java.lang.String').implementation = function(cmd) {
        if (cmd === "su" || cmd.indexOf("which su") !== -1) {
            console.log("[Root检测] 拦截 exec:", cmd);
            throw Java.use("java.io.IOException").$new("su not found");
        }
        return this.exec(cmd);
    };
});
```

### 3.7 Frida 自身反调试绕过

```javascript
// 检测 frida-server 是否在运行，并绕过
Java.perform(function() {
    // 绕过 /proc/net/tcp 检测（检测 27042 端口）
    var BufferedReader = Java.use("java.io.BufferedReader");
    BufferedReader.readLine.implementation = function() {
        var line = this.readLine();
        if (line !== null && line.indexOf("27042") !== -1) {
            console.log("[反Frida] 拦截端口检测");
            return this.readLine(); // 跳过包含端口的行
        }
        return line;
    };

    // 绕过 ptrace 反调试
    var ptrace = Module.findExportByName("libc.so", "ptrace");
    Interceptor.replace(ptrace, new NativeCallback(function(pid, req, addr, data) {
        console.log("[ptrace] 被调用, 返回0");
        return 0;
    }, 'long', ['int', 'int', 'pointer', 'pointer']));

    // 绕过 /proc/self/status TracerPid 检测
    var fopen = Module.findExportByName("libc.so", "fopen");
    Interceptor.attach(fopen, {
        onEnter: function(args) {
            var path = args[0].readUtf8String();
            if (path && path.indexOf("/proc/") !== -1 && path.indexOf("status") !== -1) {
                this.isStatus = true;
            }
        },
        onLeave: function(retval) {
            if (this.isStatus) {
                // 后续读取会获取 TracerPid，需进一步处理
            }
        }
    });
});
```

### 3.8 完整示例：分析加固 APP 登录流程

```javascript
/*
 * 完整示例：分析加固APP登录流程
 * 目标：获取登录时传给服务端的加密参数
 */

setTimeout(function() {
    Java.perform(function() {
        console.log("=== 登录流程分析开始 ===");

        // 1. Hook 登录按钮点击
        var MainActivity = Java.use("com.example.app.MainActivity");
        MainActivity.onClick.implementation = function(view) {
            console.log("[点击] 触发登录");
            this.onClick(view);
        };

        // 2. Hook 加密函数
        var CryptoUtil = Java.use("com.example.app.utils.CryptoUtil");
        CryptoUtil.encryptAES.overload('java.lang.String', 'java.lang.String').implementation = function(data, key) {
            console.log("[AES加密] 明文:", data);
            console.log("[AES加密] 密钥:", key);
            var encrypted = this.encryptAES(data, key);
            console.log("[AES加密] 密文:", encrypted);
            return encrypted;
        };

        // 3. Hook 网络请求
        var OkHttpClient = Java.use("okhttp3.OkHttpClient");
        OkHttpClient.newCall.implementation = function(request) {
            var url = request.url().toString();
            console.log("[HTTP请求] URL:", url);
            var body = request.body();
            if (body !== null) {
                var buffer = Java.use("okio.Buffer").$new();
                body.writeTo(buffer);
                console.log("[HTTP请求] Body:", buffer.readUtf8());
            }
            return this.newCall(request);
        };

        // 4. Hook 登录响应解析
        var LoginResponse = Java.use("com.example.app.model.LoginResponse");
        LoginResponse.$init.overload('java.lang.String').implementation = function(json) {
            console.log("[登录响应] JSON:", json);
            return this.$init(json);
        };

        console.log("=== Hook 部署完成，请操作APP登录 ===");
    });
}, 3000);
```

---

## 4. iOS Hook 实战

### 4.1 Hook Objective-C 方法

```javascript
// Hook 实例方法
var hook = ObjC.classes.SensitiveManager["- checkPassword:"];
Interceptor.attach(hook.implementation, {
    onEnter: function(args) {
        // args[0] = self, args[1] = selector, args[2] = 第一个参数
        var password = new ObjC.Object(args[2]);
        console.log("[checkPassword] 输入:", password.toString());
    },
    onLeave: function(retval) {
        console.log("[checkPassword] 返回:", retval);
        // 绕过密码验证
        retval.replace(1); // YES
    }
});

// Hook Block 回调
var block = ObjC.blocks.Block;
// 需根据实际 block 结构进行 Hook
```

### 4.2 Hook Swift 方法

```javascript
// Swift 方法名会被 mangle，需通过符号查找
var swiftMethod = Module.findExportByName(null, "$s8MyAppApp22ViewControllerC15verifyToken5tokenSbSS_tF");
if (swiftMethod) {
    Interceptor.attach(swiftMethod, {
        onEnter: function(args) {
            // Swift 调用约定: args[0] = self, args[1]+ = 参数
            console.log("[Swift verifyToken] 被调用");
        }
    });
}

// 通过 Objective-C 桥接（Swift 类继承 NSObject）
var swiftClass = ObjC.classes.MySwiftClass;
if (swiftClass) {
    var method = swiftClass["- myMethod:"];
    Interceptor.attach(method.implementation, {
        onEnter: function(args) { console.log("Swift方法调用"); }
    });
}
```

### 4.3 iOS Keychain 操作

```javascript
// Hook Keychain 读取
var SecItemCopyMatching = Module.findExportByName("Security", "SecItemCopyMatching");
Interceptor.attach(SecItemCopyMatching, {
    onEnter: function(args) {
        console.log("[Keychain] SecItemCopyMatching 查询");
        var query = new ObjC.Object(args[0]);
        console.log("查询条件:", query.toString());
    },
    onLeave: function(retval) {
        console.log("返回状态:", retval);
    }
});

// Hook Keychain 写入
var SecItemAdd = Module.findExportByName("Security", "SecItemAdd");
Interceptor.attach(SecItemAdd, {
    onEnter: function(args) {
        var attributes = new ObjC.Object(args[0]);
        console.log("[Keychain] SecItemAdd:", attributes.toString());
    }
});
```

### 4.4 SSL Pinning 绕过（iOS）

```javascript
// iOS SSL Pinning 绕过
var pinningMethods = [
    // NSURLSession
    ["__NSURLSessionDelegate", "URLSession:didReceiveChallenge:completionHandler:"],
    // AFNetworking
    ["AFSecurityPolicy", "evaluateServerTrust:forDomain:"],
    // TrustKit
    ["TSKPinningValidator", "validateTrust:"],
];

pinningMethods.forEach(function(item) {
    var cls = item[0], sel = item[1];
    if (ObjC.classes[cls] && ObjC.classes[cls][sel]) {
        var method = ObjC.classes[cls][sel];
        Interceptor.attach(method.implementation, {
            onLeave: function(retval) {
                console.log("[SSL Pinning] 绕过:", cls, sel);
                retval.replace(1); // YES / 0 (success)
            }
        });
    }
});

// 底层 SSL 绕过
var sslVerify = Module.findExportByName("libboringssl.dylib", "SSL_CTX_set_verify");
if (sslVerify) {
    Interceptor.attach(sslVerify, {
        onEnter: function(args) {
            // 将 mode 设为 SSL_VERIFY_NONE = 0
            args[1] = ptr(0);
        }
    });
}
```

### 4.5 越狱检测绕过

```javascript
// 绕过文件路径检测
var stat = Module.findExportByName("libSystem.B.dylib", "stat");
Interceptor.attach(stat, {
    onEnter: function(args) {
        var path = args[0].readUtf8String();
        if (path && (path.indexOf("/Applications/Cydia.app") !== -1 ||
                     path.indexOf("/Library/MobileSubstrate") !== -1 ||
                     path.indexOf("/bin/bash") !== -1 ||
                     path.indexOf("/usr/sbin/sshd") !== -1)) {
            console.log("[越狱检测] 拦截:", path);
            this.bypass = true;
        }
    },
    onLeave: function(retval) {
        if (this.bypass) {
            retval.replace(-1); // 文件不存在
        }
    }
});

// 绕过 fork 检测（越狱环境下 fork 返回值 > 0）
var fork = Module.findExportByName("libSystem.B.dylib", "fork");
Interceptor.attach(fork, {
    onLeave: function(retval) {
        if (retval.toInt32() > 0) {
            retval.replace(0); // 伪装为非越狱
        }
    }
});
```

---

## 5. 高级技巧

### 5.1 Frida 脚本混淆与加密

```javascript
// 使用 JavaScript 混淆防止脚本被检测
// 方法1: 动态拼接函数名（避免静态特征检测）
var funcName = ["ch", "ec", "k"].join("");
var TargetClass = Java.use("com.example.app." + "Security" + funcName);

// 方法2: 使用 eval 执行脚本（避免静态扫描）
var encoded = "ZXZhbCgndmFy..." // Base64 编码的脚本
var decoded = Java.use("android.util.Base64").decode(encoded, 0);
eval(Memory.readUtf8String(decoded));

// 方法3: 字符串加密
function decrypt(encrypted, key) {
    var result = "";
    for (var i = 0; i < encrypted.length; i++) {
        result += String.fromCharCode(encrypted.charCodeAt(i) ^ key);
    }
    return result;
}
```

### 5.2 Gum Stalker 代码跟踪

```javascript
// Stalker: 跟踪特定线程的执行流
var tid = Process.mainThread.id;
Stalker.follow(tid, {
    events: {
        call: true,    // 函数调用
        ret: false,    // 函数返回
        exec: false,   // 指令执行（数据量极大，慎用）
        block: true     // 基本块
    },
    onCallSummary: function(summary) {
        // summary: { "0x1234": 调用次数, ... }
        for (var addr in summary) {
            var sym = DebugSymbol.fromAddress(ptr(addr));
            console.log("调用:", sym, "次数:", summary[addr]);
        }
    },
    onBlockTraceRecords: function(records) {
        records.forEach(function(r) {
            console.log("Block @", r.begin, "->", r.end);
        });
    }
});

// 跟踪指定函数范围内的执行
Interceptor.attach(targetFunc, {
    onEnter: function(args) {
        this.tid = Process.getCurrentThreadId();
        Stalker.follow(this.tid, {
            events: { exec: true },
            onReceive: function(events) {
                var calls = Stalker.parse(events, { stringify: false, annotate: true });
                calls.forEach(function(c) {
                    console.log("执行:", c[1] ? c[1].name : c[0]);
                });
            }
        });
    },
    onLeave: function() {
        Stalker.unfollow(this.tid);
    }
});
```

### 5.3 Frida 编译自定义 Agent

```bash
# 1. 克隆 Frida 源码
git clone --recursive https://github.com/frida/frida.git
cd frida

# 2. 配置编译环境（需要 Node.js, Python 3, Make）
make

# 3. 自定义 frida-agent（修改 frida-agent/src/ 下的源码）
# 4. 重新编译
make agent

# 5. 编译自定义 frida-server
make frida-server-android-arm64
```

### 5.4 Hook 绕过 Frida 检测的方法

```javascript
// 1. 修改 frida-server 名称和端口
// 启动时: frida-server -l 0.0.0.0:8888
// 连接时: frida -H 127.0.0.1:8888 -n com.example.app

// 2. frida-gadget 注入（不需要 frida-server）
// 将 libfrida-gadget.so 重打包进 APK 或使用 LD_PRELOAD

// 3. 绕过内存特征扫描
// 检测: 在内存中搜索 "frida" "gadget" "frida-agent" 字符串
// 绕过: 编译时去除特征字符串

// 4. 绕过线程名检测
// 检测: 遍历 /proc/self/task/*/comm 查找 "gmain" "gdbus" 等 Frida 线程名
// 绕过: Hook fopen/open 对该路径返回假数据

// 5. 使用 frida-gadget + 配置文件实现持久化注入
// frida-gadget config.json:
```
```json
{
    "interaction": {
        "type": "script",
        "path": "/data/local/tmp/hook.js"
    }
}
```

### 5.5 群控/批量 Hook 框架

```python
# Python 群控脚本示例
import frida
import threading

devices = frida.enumerate_devices()
usb_device = [d for d in devices if d.type == 'usb'][0]

# 批量设备 Hook
def hook_device(device_id, app_name, script_code):
    try:
        device = frida.get_device(device_id)
        session = device.attach(app_name)
        script = session.create_script(script_code)
        script.on('message', lambda msg, data: print(f"[{device_id}]", msg))
        script.load()
        print(f"[{device_id}] Hook 成功")
    except Exception as e:
        print(f"[{device_id}] 错误:", e)

# 多设备并发
script_code = open("hook.js").read()
threads = []
for dev in usb_device:
    t = threading.Thread(target=hook_device, args=(dev.id, "com.example.app", script_code))
    threads.append(t)
    t.start()

for t in threads:
    t.join()
```

---

## 6. 常用 Frida 脚本集合

### 6.1 常用 Hook 模板

```javascript
// ========== 模板1: 日志记录（打印所有参数和返回值）==========
function logHook(className, methodName) {
    var cls = Java.use(className);
    cls[methodName].overloads.forEach(function(overload) {
        overload.implementation = function() {
            console.log("[" + className + "." + methodName + "] 参数:", JSON.stringify(Array.prototype.slice.call(arguments)));
            var ret = this[methodName].apply(this, arguments);
            console.log("[" + className + "." + methodName + "] 返回:", ret);
            return ret;
        };
    });
}

// 使用: logHook("com.example.app.CryptoUtil", "encrypt")

// ========== 模板2: 修改返回值 ==========
function modifyReturn(className, methodName, newReturn) {
    var cls = Java.use(className);
    cls[methodName].overloads.forEach(function(overload) {
        overload.implementation = function() {
            this[methodName].apply(this, arguments);
            console.log("[修改返回值] " + className + "." + methodName + " -> " + newReturn);
            return newReturn;
        };
    });
}

// ========== 模板3: 修改参数 ==========
function modifyArgs(className, methodName, argIndex, newValue) {
    var cls = Java.use(className);
    cls[methodName].overload('java.lang.String').implementation = function() {
        arguments[argIndex] = newValue;
        console.log("[修改参数] arg" + argIndex + " -> " + newValue);
        return this[methodName].apply(this, arguments);
    };
}

// ========== 模板4: 暴力枚举所有类的所有方法 ==========
function traceAllMethods(className) {
    Java.perform(function() {
        var cls = Java.use(className);
        var methods = cls.class.getDeclaredMethods();
        methods.forEach(function(method) {
            var methodName = method.getName();
            if (cls[methodName]) {
                try {
                    cls[methodName].overloads.forEach(function(overload) {
                        overload.implementation = function() {
                            console.log("[" + className + "." + methodName + "]");
                            return this[methodName].apply(this, arguments);
                        };
                    });
                } catch(e) {}
            }
        });
    });
}
```

### 6.2 工具推荐

| 工具 | 用途 | 说明 |
|------|------|------|
| **frida-trace** | 自动化函数追踪 | `frida-trace -U -i "encrypt*" -f com.example.app` |
| **objection** | Frida 封装框架 | 提供交互式 REPL，快速进行 SSL Pinning 绕过、类枚举等 |
| **Jaider** | Frida 脚本管理 | 图形化管理 Frida 脚本 |
| **frida-dexdump** | Android 脱壳 | 基于 Frida 的 DEX 内存 Dump 工具 |
| **rpc-fingerprint** | 指纹识别 | 基于 Frida 的移动应用指纹识别 |

#### frida-trace 快速使用

```bash
# 跟踪所有匹配的 Native 函数
frida-trace -U -i "Java_*" -f com.example.app

# 跟踪指定 SO 库的所有函数
frida-trace -U -i "libnative.so!*encrypt*" com.example.app

# 跟踪 Objective-C 方法
frida-trace -U -m "-[UIViewController viewDidAppear:]" -f com.example.app
```

#### objection 快速使用

```bash
# 启动 objection
objection -g com.example.app explore

# 常用命令
android sslpinning disable              # SSL Pinning 绕过
android root disable                    # Root 检测绕过
android hooking list classes            # 列出所有类
android hooking watch class ClassName   # 监控类的所有方法
android hooking watch class_method ClassName.method --dump-args --dump-return
ios keychain dump                       # iOS Keychain 导出
ios nsuserdefaults dump                 # iOS UserDefaults 导出
```

---

## 结语

Frida 作为当今最强大的动态插桩工具，贯穿了移动安全研究的各个环节——从逆向分析、渗透测试到脱壳研究，都离不开它的身影。掌握 Frida 的核心 API 与实战技巧，是移动安全工程师的基本功。建议结合实际目标（在合法授权范围内）反复练习，从简单的 Hook 模板开始，逐步深入到 Stalker 代码跟踪与反检测对抗。

> **安全声明**：本文档仅供安全研究与教学使用，请确保在合法授权范围内使用 Frida，切勿用于未授权的商业逆向或破坏行为。
