# iOS Hook 实战

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

---

