# 常用 Frida 脚本集合

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

---

