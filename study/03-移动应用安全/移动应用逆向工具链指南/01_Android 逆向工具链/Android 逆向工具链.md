# Android 逆向工具链

### 1.1 jadx — DEX 反编译工具

**jadx** 是目前最流行的 Android 反编译工具，能够将 DEX 字节码反编译为可读的 Java 代码，同时支持 APK/DEX/AXML 解析。

**安装与基本使用**：

```bash
# 方式1：直接下载发布版本
# https://github.com/skylot/jadx/releases
# 下载 jadx-x.x.x.zip 解压即可

# 方式2：源码编译
git clone https://github.com/skylot/jadx.git
cd jadx
./gradlew distZip

# 命令行使用
jadx -d output_dir target.apk           # 反编译APK到指定目录
jadx -d output_dir classes.dex          # 反编译单个DEX文件
jadx --show-bad-code target.apk         # 显示反编译失败的代码
jadx --deobf target.apk                  # 自动重命名混淆的类和方法
jadx -j 4 -d output_dir target.apk      # 使用4线程并行反编译

# GUI 模式
jadx-gui target.apk                      # 打开图形界面
```

**jadx GUI 核心功能**：

| 功能 | 说明 | 快捷键 |
|------|------|--------|
| 搜索文本 | 全局文本搜索 | Ctrl+Shift+F |
| 搜索类名 | 按类名搜索 | Ctrl+N |
| 搜索方法 | 按方法名搜索 | Ctrl+Shift+T |
| 搜索资源 | 搜索资源ID | Ctrl+Shift+R |
| 导出 Gradle 项目 | 导出为可编译的 Gradle 项目 | — |
| 反混淆映射 | 支持 mapping.txt 重命名 | — |

**jadx 高级技巧**：

```bash
# 1. 使用反混淆映射文件（来自 ProGuard/D8 的 mapping.txt）
jadx --deobf-map-file mapping.txt -d output_dir target.apk

# 2. 导出为 Gradle 项目（方便修改和重新编译）
jadx -e --show-bad-code -d output_gradle target.apk

# 3. 批量反编译
for apk in *.apk; do
    jadx -d "output_${apk%.apk}" "$apk"
done

# 4. 提取字符串常量
jadx --no-res --show-bad-code target.apk | grep -i "http\|api\|key\|token\|password"
```

### 1.2 apktool — APK 资源解包工具

**apktool** 主要用于反编译和重打包 APK 的资源文件（AndroidManifest.xml、布局、图片等），以及 Smali 代码修改。

```bash
# 安装
# 需要 Java 环境
# 下载 apktool.jar 和 apktool 脚本

# 反编译（解包资源 + 转 Smali）
apktool d target.apk -o target_decoded

# 反编译选项
apktool d target.apk -o target_decoded -f     # 强制覆盖
apktool d target.apk -o target_decoded -s     # 不反编译DEX（只解包资源）
apktool d target.apk -o target_decoded -r     # 不解包资源（只反编译DEX）

# 重新打包
apktool b target_decoded -o target_modified.apk

# 打包后需要签名才能安装
# 使用 apksigner 签名
keytool -genkey -alias mykey -keyalg RSA -keysize 2048 \
  -validity 10000 -keystore my.keystore
apksigner sign --ks my.keystore --ks-key-alias mykey \
  --out target_signed.apk target_modified.apk

# 验证签名
apksigner verify --verbose target_signed.apk
```

**Smali 代码修改示例**：

```smali
# 修改返回值 - 将方法返回值改为 true
# 原始代码
.method public isVip()Z
    .locals 1
    const/4 v0, 0x0  # 返回 false
    return v0
.end method

# 修改后
.method public isVip()Z
    .locals 1
    const/4 v0, 0x1  # 返回 true
    return v0
.end method
```

### 1.3 Frida 高级用法

Frida 是移动安全领域最重要的动态分析工具，支持 JavaScript 脚本注入和运行时 Hook。

**Frida 环境搭建**：

```bash
# 安装 Frida 工具链
pip install frida-tools

# 下载对应架构的 frida-server
# https://github.com/frida/frida/releases
# 选择与设备架构匹配的版本 (arm64/arm)

# 推送到设备并运行
adb push frida-server-arm64 /data/local/tmp/frida-server
adb shell "chmod +x /data/local/tmp/frida-server"
adb shell "su -c '/data/local/tmp/frida-server &'"

# 验证连接
frida-ps -U              # 列出设备上所有进程
frida-ps -Uai            # 列出已安装的应用
frida-ps -Ua             # 列出正在运行的应用
```

**（1）Hook SSL Pinning**

```javascript
// frida_ssl_bypass.js
// 通用 SSL Pinning 绕过脚本

setTimeout(function() {
    Java.perform(function() {
        console.log('[*] SSL Pinning 绕过脚本启动...');

        // OkHttp3 CertificatePinner
        try {
            var certPinner = Java.use('okhttp3.CertificatePinner');
            certPinner.check.overload('java.lang.String', 'java.util.List')
                .implementation = function(host, list) {
                console.log('[+] 绕过 OkHttp3 Pinning: ' + host);
                return;
            };
        } catch (e) {}

        // TrustManager（自定义实现）
        try {
            var X509TrustManager = Java.use('javax.net.ssl.X509TrustManager');
            var SSLContext = Java.use('javax.net.ssl.SSLContext');
            var TrustManager = Java.registerClass({
                name: 'org.wooyun.TrustAllManager',
                implements: [X509TrustManager],
                methods: {
                    checkClientTrusted: function(chain, authType) {},
                    checkServerTrusted: function(chain, authType) {},
                    getAcceptedIssuers: function() {
                        return [];
                    }
                }
            });
            var TrustManagers = [TrustManager.$new()];
            var initSSL = SSLContext.init.overload(
                '[Ljavax.net.ssl.KeyManager;',
                '[Ljavax.net.ssl.TrustManager;',
                'java.security.SecureRandom'
            );
            initSSL.implementation = function(km, tm, sr) {
                console.log('[+] 替换 TrustManager');
                initSSL.call(this, km, TrustManagers, sr);
            };
        } catch (e) {}

        // Conscrypt (Android 8+)
        try {
            var TrustManagerImpl = Java.use('com.android.org.conscrypt.TrustManagerImpl');
            TrustManagerImpl.verifyChain.implementation = function(untrustedChain, trustAnchorChain, host, clientAuth, ocspData, tlsSrpData) {
                console.log('[+] 绕过 Conscrypt: ' + host);
                return Java.use('java.util.ArrayList').$new();
            };
        } catch (e) {}

        // WebView SSL Error 处理
        try {
            var WebViewClient = Java.use('android.webkit.WebViewClient');
            WebViewClient.onReceivedSslError.implementation = function(view, handler, error) {
                console.log('[+] 绕过 WebView SSL 错误');
                handler.proceed();
            };
        } catch (e) {}
    });
}, 0);

// 运行: frida -U -f com.example.app -l frida_ssl_bypass.js
```

**（2）Hook 加密函数**

```javascript
// frida_crypto_hook.js
// Hook 常见加密函数，输出明文和密钥

Java.perform(function() {
    // Hook javax.crypto.Cipher
    var Cipher = Java.use('javax.crypto.Cipher');
    
    // Hook init 方法获取密钥和算法
    Cipher.init.overload('int', 'java.security.Key').implementation = function(mode, key) {
        var modeStr = (mode === 1) ? 'ENCRYPT' : 'DECRYPT';
        var algorithm = this.getAlgorithm();
        var keyBytes = key.getEncoded();
        var keyHex = '';
        if (keyBytes) {
            for (var i = 0; i < keyBytes.length; i++) {
                keyHex += ('00' + (keyBytes[i] & 0xFF).toString(16)).slice(-2);
            }
        }
        console.log('[Crypto] init()');
        console.log('  模式: ' + modeStr);
        console.log('  算法: ' + algorithm);
        console.log('  密钥: ' + keyHex);
        return this.init(mode, key);
    };
    
    // Hook doFinal 获取加密/解密数据
    Cipher.doFinal.overload('[B').implementation = function(input) {
        var result = this.doFinal(input);
        var inputStr = '';
        for (var i = 0; i < input.length; i++) {
            inputStr += ('00' + (input[i] & 0xFF).toString(16)).slice(-2);
        }
        var resultStr = '';
        for (var i = 0; i < result.length; i++) {
            resultStr += ('00' + (result[i] & 0xFF).toString(16)).slice(-2);
        }
        console.log('[Crypto] doFinal()');
        console.log('  输入: ' + inputStr);
        console.log('  输出: ' + resultStr);
        return result;
    };
    
    // Hook MessageDigest (MD5/SHA)
    var MessageDigest = Java.use('java.security.MessageDigest');
    MessageDigest.digest.overload().implementation = function() {
        var result = this.digest();
        var algorithm = this.getAlgorithm();
        var hashHex = '';
        for (var i = 0; i < result.length; i++) {
            hashHex += ('00' + (result[i] & 0xFF).toString(16)).slice(-2);
        }
        console.log('[Hash] ' + algorithm + ' = ' + hashHex);
        return result;
    };
    
    // Hook Base64
    var Base64 = Java.use('android.util.Base64');
    Base64.encodeToString.overload('[B', 'int').implementation = function(input, flags) {
        var result = this.encodeToString(input, flags);
        var inputStr = '';
        for (var i = 0; i < input.length; i++) {
            inputStr += String.fromCharCode(input[i] & 0xFF);
        }
        console.log('[Base64] 编码: ' + inputStr + ' -> ' + result);
        return result;
    };
});
```

**（3）动态修改返回值**

```javascript
// frida_modify_return.js
// 修改方法返回值，实现功能解锁或绕过校验

Java.perform(function() {
    // 修改 isVip 返回值
    var UserManager = Java.use('com.example.app.UserManager');
    UserManager.isVip.implementation = function() {
        console.log('[Hook] isVip() 原始返回值可能为 false，强制返回 true');
        return true;  // 强制返回 VIP
    };
    
    // 修改签名校验
    var SecurityCheck = Java.use('com.example.app.SecurityCheck');
    SecurityCheck.verifySignature.implementation = function(signature) {
        console.log('[Hook] verifySignature() 被调用，签名: ' + signature);
        console.log('[Hook] 强制返回 true（签名验证通过）');
        return true;
    };
    
    // 修改过期为永久有效
    var LicenseManager = Java.use('com.example.app.LicenseManager');
    LicenseManager.isExpired.implementation = function() {
        console.log('[Hook] isExpired() 强制返回 false');
        return false;
    };
    
    // 修改字符串常量（拦截 getString）
    var context = Java.use('android.content.Context');
    context.getString.overload('int').implementation = function(resId) {
        var result = this.getString(resId);
        if (result === 'Trial Version') {
            console.log('[Hook] getString() 替换 "Trial Version" -> "Pro Version"');
            return 'Pro Version';
        }
        return result;
    };
});
```

### 1.4 objection — 自动化测试框架

**objection** 是基于 Frida 构建的自动化移动安全测试框架，提供交互式命令行界面。

```bash
# 安装
pip install objection

# 附加到运行中的应用
objection -g com.example.app explore

# 启动应用并附加
objection -g com.example.app explore --startup-command "android sslpinning disable"

# 常用命令

# === Android 命令 ===

# SSL Pinning 绕过
android sslpinning disable

# Root 检测绕过
android root disable

# 列出 Activities
android hooking list activities

# 列出 Services
android hooking list services

# 搜索类
android hooking search classes keyword

# Hook 类的所有方法
android hooking watch class com.example.app.LoginManager

# Hook 特定方法
android hooking watch class_method com.example.app.LoginManager.login \
  --dump-args --dump-return --dump-backtrace

# 切换方法返回值
android hooking set return_value com.example.app.UserManager.isVip true

# 列出可 Hook 的方法
android hooking list class_methods com.example.app.LoginManager

# Keystore 操作
android keystore list
android keystore clear

# 环境信息
android env
android shell_exec whoami

# === iOS 命令 ===
# ios sslpinning disable
# ios cookies get
# ios pasteboard monitor
# ios keychain dump
```

### 1.5 Magisk + LSPosed — Hook 框架

**Magisk** 提供 Root 权限管理，**LSPosed** 是基于 Riru 的 Xposed 框架替代品，支持系统级 Hook。

**Magisk 核心**：

```
Magisk 架构
├── magiskinit     # 初始化（替换 ramdisk）
├── magiskd        # 守护进程（提供 Root 授权）
├── magiskboot     # Boot 镜像修补工具
├── magiskpolicy   # SELinux 策略修补
├── MagiskHide / Zygisk DenyList  # 隐藏 Root
└── Module 系统    # 模块化扩展
```

**Magisk 隐藏 Root（绕过 Root 检测）**：

```
# 启用 Zygisk
Magisk Settings -> Zygisk -> Enable

# 配置 DenyList（隐藏 Root）
Magisk Settings -> Enforce DenyList -> Enable
Configure -> 勾选需要隐藏的应用

# 或使用 Shamiko 模块（更强大的隐藏）
# 下载 Shamiko 模块 zip
# Magisk -> Modules -> Install from storage -> 选择 zip
```

**LSPosed 模块开发示例**：

```java
// Xposed 模块 - Hook 特定方法
package com.example.hookmodule;

import de.robv.android.xposed.IXposedHookLoadPackage;
import de.robv.android.xposed.XC_MethodHook;
import de.robv.android.xposed.XposedBridge;
import de.robv.android.xposed.XposedHelpers;
import de.robv.android.xposed.callbacks.XC_LoadPackage.LoadPackageParam;

public class MainHook implements IXposedHookLoadPackage {
    @Override
    public void handleLoadPackage(LoadPackageParam lpparam) {
        // 只 Hook 目标应用
        if (!lpparam.packageName.equals("com.example.app")) return;
        
        // Hook isVip 方法
        XposedHelpers.findAndHookMethod(
            "com.example.app.UserManager",
            lpparam.classLoader,
            "isVip",
            new XC_MethodHook() {
                @Override
                protected void afterHookedMethod(MethodHookParam param) {
                    // 强制修改返回值
                    param.setResult(true);
                    XposedBridge.log("isVip() 返回值已修改为 true");
                }
            }
        );
        
        // Hook 登录验证
        XposedHelpers.findAndHookMethod(
            "com.example.app.SecurityCheck",
            lpparam.classLoader,
            "verifySignature",
            String.class,
            new XC_MethodHook() {
                @Override
                protected void beforeHookedMethod(MethodHookParam param) {
                    String signature = (String) param.args[0];
                    XposedBridge.log("verifySignature 输入: " + signature);
                }
                @Override
                protected void afterHookedMethod(MethodHookParam param) {
                    param.setResult(true);
                    XposedBridge.log("verifySignature 强制返回 true");
                }
            }
        );
    }
}
```

### 1.6 Native 逆向（SO 库分析）

当核心逻辑在 Native 层（C/C++ 编译的 SO 库）时，需要使用 IDA Pro 或 Ghidra 进行分析。

**IDA Pro 分析流程**：

```
1. 加载 SO 库
   File -> Open -> 选择 libnative.so
   选择 ARM64 / ARM 处理器架构

2. 定位关键函数
   - 通过 JNI 函数名搜索（Java_com_example_app_*）
   - 通过字符串引用定位
   - 通过导出函数表查找

3. 分析 JNI 函数
   __int64 Java_com_example_app_NativeHelper_encrypt(
       JNIEnv *env,    # 参数1: JNIEnv 指针
       jobject thiz,   # 参数2: 对象/类
       jbyteArray input # 参数3: Java 传入的数据
   )

4. 交叉引用分析
   - 查看 XREF（交叉引用）追踪数据流
   - 分析函数调用链

5. 动态调试
   - 使用 IDA 的 Android Debugger
   - 在关键函数设置断点
   - 查看寄存器和内存
```

**Ghidra 分析（免费替代方案）**：

```bash
# 启动 Ghidra
# 导入 SO 文件
# File -> Import File -> 选择 libnative.so
# 设置语言: AARCH64:LE:64:v8A (ARM64)
# 或 ARM:LE:32:v7 (ARM32)

# Ghidra 脚本 - 自动定位 JNI 函数
# @category Analysis
import ghidra.app.script.GhidraScript;
import ghidra.program.model.symbol.*;

public class FindJNIFunctions extends GhidraScript {
    @Override
    public void run() throws Exception {
        SymbolTable symTable = currentProgram.getSymbolTable();
        for (Symbol sym : symTable.getSymbols()) {
            if (sym.getName().startsWith("Java_")) {
                println("JNI 函数: " + sym.getName() + 
                        " 地址: " + sym.getAddress());
            }
        }
    }
}
```

**Native 层 Frida Hook（JNI 函数 Hook）**

```javascript
// frida_native_hook.js
// Hook Native 层 JNI 函数

// 方式1：通过 Java 层声明 native 方法后 Hook
Java.perform(function() {
    var nativeLib = Java.use('com.example.app.NativeHelper');
    
    // Hook native 方法（需要在 Java 层有声明）
    nativeLib.encrypt.implementation = function(input) {
        console.log('[Native] encrypt 输入: ' + input);
        var result = this.encrypt(input);
        console.log('[Native] encrypt 输出: ' + result);
        return result;
    };
});

// 方式2：直接 Hook Native 函数地址
function hookNativeFunction() {
    var moduleName = 'libnative.so';
    var module = Process.getModuleByName(moduleName);
    
    // 通过导出函数名查找
    var funcAddr = Module.findExportByName(moduleName, 'Java_com_example_app_NativeHelper_encrypt');
    
    if (funcAddr) {
        Interceptor.attach(funcAddr, {
            onEnter: function(args) {
                // args[0] = JNIEnv*, args[1] = jobject, args[2] = 输入参数
                console.log('[Native] encrypt() 被调用');
                this.input = args[2];
            },
            onLeave: function(retval) {
                console.log('[Native] encrypt() 返回值: ' + retval);
            }
        });
    }
    
    // 通过偏移地址查找（未导出的内部函数）
    var baseAddr = module.base;
    var targetOffset = 0x1234;  // 从 IDA/Ghidra 获取的偏移
    var targetAddr = baseAddr.add(targetOffset);
    
    Interceptor.attach(targetAddr, {
        onEnter: function(args) {
            console.log('[Native] 内部函数 @0x1234 被调用');
            console.log('  参数1: ' + args[0]);
            console.log('  参数2: ' + args[1]);
        },
        onLeave: function(retval) {
            console.log('  返回值: ' + retval);
        }
    });
}
```

### 1.7 脱壳工具

加壳应用（如加固保、爱加密、梆梆安全等）的 DEX 被加密，需要脱壳后才能反编译。

**FRIDA-DEXDump**：

```bash
# 安装
pip install frida-tools
git clone https://github.com/hluwa/FRIDA-DEXDump.git

# 使用
# 方式1：通过 objection 插件
objection -g com.example.app explore
plugin load /path/to/FRIDA-DEXDump

# 方式2：直接运行脚本
python FRIDA-DEXDump/frida_dexdump.py -U -f com.example.app

# 方式3：Frida 脚本方式
frida -U -f com.example.app -l frida_dexdump.js --no-pause

# 脱壳后的 DEX 文件会被保存到当前目录
# 使用 jadx 反编译脱壳后的 DEX
jadx -d output_dir *.dex
```

**BlackDex**：

```bash
# BlackDex 是一个脱壳工具，支持多种壳
# 下载: https://github.com/CodingGay/BlackDex/releases

# 安装 BlackDex APK
adb install BlackDex.apk

# 打开 BlackDex，选择目标应用
# 点击脱壳按钮
# 脱壳后的 DEX 保存在:
# /sdcard/Android/data/com.googlecode.android/BlackDex/packagename/

# 拉取脱壳结果
adb pull /sdcard/Android/data/com.googlecode.android/BlackDex/com.example.app/ ./
```

**脱壳工具对比**：

| 工具 | 原理 | 支持壳 | 需要 Root |
|------|------|--------|-----------|
| FRIDA-DEXDump | 内存中搜索 DEX 特征 | 大部分壳 | 是 |
| BlackDex | ART 运行时 dump | 部分壳 | 否 |
| Dexlib | 直接从内存 dump | 有限 | 是 |
| Youpk | 整体脱壳框架 | 较多 | 是(定制ROM) |

---

---

