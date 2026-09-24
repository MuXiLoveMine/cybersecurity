# Android Hook 实战

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

---

