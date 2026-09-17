# iOS 逆向工具链

### 2.1 砸壳工具

iOS 应用从 App Store 下载后带有 FairPlay DRM 加密，需要砸壳（脱壳）才能进行静态分析。

**frida-ios-dump**：

```bash
# 环境要求：越狱设备 + Frida + USB 连接

# 安装
pip3 install frida-tools
git clone https://github.com/AloneMonkey/frida-ios-dump.git
cd frida-ios-dump
pip3 install -r requirements.txt

# 设备上安装 frida-server（通过 Cydia/Sileo 安装）
# 搜索 frida 并安装

# 查看已安装应用
python3 dump.py -l

# 砸壳指定应用（通过 Bundle ID）
python3 dump.py com.example.app

# 砸壳结果为 .ipa 文件，可直接用 class-dump 或 Hopper 分析
```

**Clutch**：

```bash
# Clutch 是经典的 iOS 砸壳工具
# 通过 Cydia/Sileo 安装

# 列出已安装的加密应用
clutch -i

# 砸壳指定应用
clutch -d com.example.app

# 砸壳结果保存在:
# /var/tmp/clutch/ 或 /private/var/mobile/Documents/Cracked/
```

### 2.2 class-dump — 导出头文件

**class-dump** 从 Mach-O 文件中导出 Objective-C 类的头文件。

```bash
# 安装
# 下载: http://stevenygard.com/projects/class-dump/
# 或使用 Homebrew
brew install class-dump

# 基本使用
class-dump -H TargetApp -o headers/        # 导出所有头文件到目录
class-dump -S TargetApp                     # 输出类和方法列表

# 针对砸壳后的二进制
class-dump -H Payload/TargetApp.app/TargetApp -o headers/

# 导出结果示例：
# @interface LoginManager : NSObject
# - (void)doLoginWithUsername:(NSString *)username password:(NSString *)password;
# - (BOOL)verifyToken:(NSString *)token;
# @end
```

### 2.3 Hopper / IDA Pro 分析 Mach-O

**Hopper Disassembler** 是 macOS 平台的反汇编工具，支持 Mach-O 格式分析：

```
Hopper 分析流程：

1. 打开 Mach-O 二进制文件
   File -> Read Executable -> 选择砸壳后的二进制

2. 搜索 Objective-C 方法
   按类名或方法名搜索（Cmd+Shift+L）
   定位到 -[LoginManager doLoginWithUsername:password:]

3. 阅读汇编代码
   理解参数传递（ARM64: x0-x7）
   分析方法调用和分支跳转

4. 伪代码视图
   切换到 Pseudocode 视图查看类 C 代码

5. 交叉引用
   查看谁调用了这个方法（XREF）
   追踪数据流
```

**IDA Pro 分析 Mach-O**：

```
1. 加载 Mach-O 文件
   IDA 自动识别架构 (ARM64/x86_64)

2. Objective-C 方法分析
   IDA 支持解析 ObjC 方法签名
   Functions 窗口中搜索 sel_ 前缀

3. Swift 方法分析
   Swift 方法名经过 mangle
   使用 swift-demangle 还原名
   或使用 IDA 的 swift 插件

4. 动态调试（需要越狱设备）
   Debugger -> Select debugger -> Remote iOS Debugger
   设置设备 IP 和端口
   在关键函数设置断点
```

### 2.4 Cycript / Frida 动态分析

**Cycript** 是经典的 iOS 动态分析工具（已较少更新），Frida 是更主流的选择。

**Frida iOS Hook 示例**：

```javascript
// frida_ios_hook.js
// iOS Objective-C 方法 Hook

function hookObjCMethods() {
    // Hook LoginManager 的 doLoginWithUsername:password: 方法
    var hook = ObjC.classes.LoginManager['- doLoginWithUsername:password:'];
    
    Interceptor.attach(hook.implementation, {
        onEnter: function(args) {
            // args[0] = self, args[1] = _cmd
            // args[2] = username, args[3] = password
            var username = new ObjC.Object(args[2]).toString();
            var password = new ObjC.Object(args[3]).toString();
            console.log('[Hook] doLogin');
            console.log('  用户名: ' + username);
            console.log('  密码: ' + password);
        },
        onLeave: function(retval) {
            console.log('  返回值: ' + retval);
        }
    });
    
    // Hook 通用方法 - 遍历所有 ViewController
    var UIViewController = ObjC.classes.UIViewController;
    var viewDidAppear = UIViewController['- viewDidAppear:'];
    
    Interceptor.attach(viewDidAppear.implementation, {
        onEnter: function(args) {
            var controller = new ObjC.Object(args[0]);
            console.log('[Hook] viewDidAppear: ' + controller.$className);
        }
    });
    
    // Hook NSURLSession 请求
    var NSURLSession = ObjC.classes.NSURLSession;
    var dataTaskWithRequest = NSURLSession['- dataTaskWithRequest:completionHandler:'];
    
    Interceptor.attach(dataTaskWithRequest.implementation, {
        onEnter: function(args) {
            var request = new ObjC.Object(args[2]);
            var url = request.URL().absoluteString().toString();
            var method = request.HTTPMethod().toString();
            console.log('[Network] ' + method + ' ' + url);
            
            // 打印请求头
            var headers = request.allHTTPHeaderFields();
            console.log('  Headers: ' + headers);
            
            // 打印请求体
            var body = request.HTTPBody();
            if (body && !body.isNull()) {
                var nsString = ObjC.classes.NSString.alloc()
                    .initWithData_encoding_(body, 4); // NSUTF8StringEncoding = 4
                console.log('  Body: ' + nsString.toString());
            }
        }
    });
}

// SSL Pinning 绕过（iOS）
function bypassSSLPinning() {
    // Hook SecTrustEvaluate
    var SecTrustEvaluate = Module.findExportByName('Security', 'SecTrustEvaluate');
    if (SecTrustEvaluate) {
        Interceptor.replace(SecTrustEvaluate, new NativeCallback(function(trust, result) {
            // 强制返回验证通过
            result.writeU8(0); // errSecSuccess
            console.log('[Hook] SecTrustEvaluate 强制返回成功');
            return 0;
        }, 'int', ['pointer', 'pointer']));
    }
    
    // Hook AFNetworking SSL Pinning
    try {
        var securityPolicy = ObjC.classes.AFSecurityPolicy;
        if (securityPolicy) {
            var setSSLPinningMode = securityPolicy['- setSSLPinningMode:'];
            Interceptor.attach(setSSLPinningMode.implementation, {
                onEnter: function(args) {
                    // AFSSLPinningModeNone = 0
                    args[2] = ptr(0);
                    console.log('[Hook] AFNetworking SSL Pinning 已禁用');
                }
            });
        }
    } catch (e) {}
}

// 运行: frida -U -f com.example.app -l frida_ios_hook.js
```

### 2.5 LLVM 中间码分析

对于使用 Swift 或底层 C 代码的 iOS 应用，可以分析 LLVM 位码：

```bash
# 检查应用是否包含 LLVM 位码
# 在砸壳后的二进制中搜索 __LLVM 段
otool -l TargetApp | grep -A5 __LLVM

# 使用 llvm-dis 反汇编位码（如果存在）
llvm-dis TargetApp.bc -o TargetApp.ll

# 位码分析适用于：
# - 获取原始的中间表示
# - 分析编译器优化前的逻辑
# - 逆向复杂的控制流
```

---

---

## 📋 内容审核与补充建议

> 针对「iOS 逆向工具链」部分的内容审核结果：

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

---

## 📌 拓展学习资源

### 推荐学习路径
- 理论基础 → 工具实践 → 实战演练 → 深度研究
- 建议搭建本地实验环境进行动手练习

### 相关工具与资源
- 在线实验平台：Hack The Box、TryHackMe、VulnHub
- 技术文档：官方文档、RFC、OWASP 指南
- 社区资源：GitHub、安全论坛、技术博客
