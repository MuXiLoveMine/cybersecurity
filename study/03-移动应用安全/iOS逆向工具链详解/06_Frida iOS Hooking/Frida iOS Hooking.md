# Frida iOS Hooking

### 5.1 ObjC Hook

```javascript
// frida-ios-hook.js
// ObjC方法Hook示例

// Hook类方法
if (ObjC.available) {
    // Hook登录验证方法
    var LoginManager = ObjC.classes.LoginManager;
    Interceptor.attach(LoginManager['- verifyPassword:'].implementation, {
        onEnter: function(args) {
            // args[0] = self, args[1] = selector, args[2] = 第一个参数
            var password = ObjC.Object(args[2]);
            console.log("[Hook] verifyPassword called with: " + password.toString());
        },
        onLeave: function(retval) {
            console.log("[Hook] verifyPassword returned: " + retval);
            // 修改返回值，绕过验证
            retval.replace(1); // 返回YES
        }
    });

    // Hook所有ObjC方法
    var className = "SecretViewController";
    var hook = ObjC.classes[className];
    var methods = hook.$ownMethods;
    methods.forEach(function(method) {
        console.log("Hooking: " + className + " " + method);
        Interceptor.attach(hook[method].implementation, {
            onEnter: function(args) {
                console.log("[+] Called: " + className + " " + method);
            }
        });
    });

    // Hook NSURLSession
    var NSURLSession = ObjC.classes.NSURLSession;
    Interceptor.attach(NSURLSession['- dataTaskWithRequest:completionHandler:'].implementation, {
        onEnter: function(args) {
            var request = ObjC.Object(args[2]);
            console.log("[URL] " + request.URL().absoluteString().toString());
            console.log("[Method] " + request.HTTPMethod().toString());
            var body = request.HTTPBody();
            if (body) {
                console.log("[Body] " + ObjC.classes.NSString.alloc().initWithData_encoding_(body, 4).toString());
            }
        }
    });

    // HookKeychain操作
    var SecItemAdd = Module.findExportByName("Security", "SecItemAdd");
    Interceptor.attach(SecItemAdd, {
        onEnter: function(args) {
            var query = ObjC.Object(args[0]);
            console.log("[Keychain Add] " + query.toString());
        }
    });

    var SecItemCopyMatching = Module.findExportByName("Security", "SecItemCopyMatching");
    Interceptor.attach(SecItemCopyMatching, {
        onEnter: function(args) {
            var query = ObjC.Object(args[0]);
            console.log("[Keychain Query] " + query.toString());
        },
        onLeave: function(retval) {
            console.log("[Keychain Result] " + retval);
        }
    });
}
```

### 5.2 Swift Hook

```javascript
// Swift方法Hook需要特殊处理
// Swift方法名会被mangle

// 查找Swift类
if (ObjC.available) {
    // 列出所有Swift类
    for (var name in ObjC.classes) {
        if (name.indexOf("Swift") !== -1) {
            console.log("Swift class: " + name);
        }
    }
}

// Hook Swift方法（通过mangled name）
var className = "AppName.LoginManager";
var methodName = "loginWithUsername(_:password:)";

// 使用Swift Interop
if (Swift.available) {
    var loginManager = Swift.classes.LoginManager;
    // Hook Swift方法
}

// 通过符号名Hook
var sym = "_$s9AppName13LoginManagerC5login9username8passwordSS_SStF";
var addr = Module.findExportByName(null, sym);
if (addr) {
    Interceptor.attach(addr, {
        onEnter: function(args) {
            console.log("[Swift Hook] login called");
        }
    });
}
```

### 5.3 Native Hook

```javascript
// Native C/C++函数Hook

// Hook OpenSSL加密函数
var EVP_EncryptInit_ex = Module.findExportByName("libcrypto", "EVP_EncryptInit_ex");
if (EVP_EncryptInit_ex) {
    Interceptor.attach(EVP_EncryptInit_ex, {
        onEnter: function(args) {
            // args[2] = key, args[3] = iv
            console.log("[Crypto] Encryption init");
            var key = args[2];
            if (!key.isNull()) {
                console.log("[Crypto] Key: " + hexdump(key, {length: 32}));
            }
        }
    });
}

// Hook malloc/free跟踪内存分配
var malloc = Module.findExportByName(null, "malloc");
Interceptor.attach(malloc, {
    onEnter: function(args) {
        this.size = args[0].toInt32();
        this.ret = null;
    },
    onLeave: function(retval) {
        if (this.size > 1024 * 1024) {
            console.log("[Memory] Large allocation: " + this.size + " bytes at " + retval);
        }
    }
});

// Hook文件操作
var fopen = Module.findExportByName(null, "fopen");
Interceptor.attach(fopen, {
    onEnter: function(args) {
        var path = args[0].readUtf8String();
        if (path && (path.indexOf("secret") !== -1 || path.indexOf("password") !== -1)) {
            console.log("[File] Opening sensitive file: " + path);
        }
    }
});

// Hook ptrace防止反调试
var ptrace = Module.findExportByName(null, "ptrace");
Interceptor.replace(ptrace, new NativeCallback(function(request, pid, addr, data) {
    console.log("[Anti-Debug] ptrace called, returning 0");
    return 0;
}, 'long', ['int', 'int', 'pointer', 'int']));

// 运行: frida -U -f com.example.app -l frida-ios-hook.js
```

---

---

## 📋 内容审核与补充建议

> 针对「Frida iOS Hooking」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

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
