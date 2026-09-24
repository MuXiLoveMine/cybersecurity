# Android 渗透测试完整流程

### 2.1 信息收集

```bash
# APK 信息提取
aapt dump badging target.apk | grep -E "package|launchable|permission|sdkVersion"

# 提取 URL 和密钥
apktool d target.apk -o target_decoded
grep -rniE "https?://|api[_-]?key|secret|password|token" target_decoded/

# 检查原生库
find target_decoded/lib -name "*.so"

# 检查资源文件中的敏感信息
find target_decoded/assets -type f | xargs file
```

### 2.2 静态分析（反编译 / 敏感信息 / 硬编码）

```bash
# 使用 jadx 反编译
jadx -d ./jadx_output target.apk

# 搜索硬编码密钥
grep -rniE "AES|DES|RSA|secret|key|password|token|http" jadx_output/sources/

# 检查 AndroidManifest 安全配置
# - 组件导出 (exported="true")
# - debuggable="true"
# - allowBackup="true"
# - usesCleartextTraffic="true"
# - 网络安全配置 (networkSecurityConfig)
```

**敏感信息检查清单**：

| 检查项 | 方法 | 风险等级 |
|--------|------|----------|
| 硬编码密钥 | grep 搜索源码 | 高危 |
| 调试日志 | 搜索 Log.d/Log.v | 中危 |
| 测试接口 | 搜索 test/staging URL | 高危 |
| 密码硬编码 | 搜索 password= | 严重 |
| API Token | 搜索 Bearer/Authorization | 高危 |

### 2.3 动态分析（Frida Hook / 调试 / MITM）

```javascript
// Frida 动态分析模板: 监控所有 HTTP 请求
Java.perform(function() {
    // Hook OkHttp
    var OkHttpClient = Java.use("okhttp3.OkHttpClient");
    OkHttpClient.newCall.implementation = function(request) {
        console.log("[HTTP] " + request.method() + " " + request.url());
        var headers = request.headers();
        for (var i = 0; i < headers.size(); i++) {
            console.log("  " + headers.name(i) + ": " + headers.value(i));
        }
        return this.newCall(request);
    };

    // Hook HttpURLConnection
    var URL = Java.use("java.net.URL");
    URL.openConnection.overload().implementation = function() {
        console.log("[URL] " + this.toString());
        return this.openConnection();
    };
});
```

### 2.4 数据存储安全

```bash
# 1. SharedPrefs 检查
adb shell run-as com.example.app ls -la shared_prefs/
adb shell run-as com.example.app cat shared_prefs/*.xml

# 2. SQLite 检查
adb shell run-as com.example.app ls -la databases/
adb shell run-as com.example.app sqlite3 databases/app.db ".tables"
adb shell run-as com.example.app sqlite3 databases/app.db "SELECT * FROM users;"

# 3. 内部文件检查
adb shell run-as com.example.app ls -laR files/
adb shell run-as com.example.app ls -laR cache/

# 4. 外部存储检查
adb shell ls -la /sdcard/Android/data/com.example.app/
```

**数据存储安全检查表**：

| 存储位置 | 安全要求 | 检查方法 |
|----------|----------|----------|
| SharedPrefs | 敏感数据不存明文 | 检查 xml 文件 |
| SQLite | 敏感数据库需 SQLCipher 加密 | 检查 .db 文件是否可读 |
| 内部文件 | 不存储明文敏感数据 | 检查 files/ 目录 |
| 外部存储 | 不存储敏感数据 | 检查 SD 卡 |
| 备份 | allowBackup="false" | 检查 manifest |

### 2.5 通信安全（HTTPS / SSL Pinning / Certificate）

```bash
# 检查网络安全配置
cat target_decoded/res/xml/network_security_config.xml

# 检查是否允许明文流量
grep -i "usesCleartextTraffic" target_decoded/AndroidManifest.xml

# SSL Pinning 测试
# 使用 Frida 或 objection 绕过
objection -g com.example.app explore
android sslpinning disable

# 如果绕过成功 → 未实现或 Pinning 不完整
# 如果绕过失败 → 实现了较强的 Pinning
```

### 2.6 组件安全（Activity / Service / Receiver / Provider）

```bash
# 使用 Drozer 进行组件安全测试（详见第5节）

# Activity 导出测试
drozer console connect -c "run app.activity.info -a com.example.app"
drozer console connect -c "run app.activity.start --component com.example.app com.example.app.MainActivity"

# Service 导出测试
drozer console connect -c "run app.service.info -a com.example.app"
drozer console connect -c "run app.service.start --component com.example.app com.example.app.ExportService"

# Content Provider 导出测试
drozer console connect -c "run app.provider.info -a com.example.app"
drozer console connect -c "run app.provider.query content://com.example.app/users"

# Broadcast Receiver 导出测试
drozer console connect -c "run app.broadcast.info -a com.example.app"
drozer console connect -c "run app.broadcast.send --action com.example.app.SENSITIVE_ACTION"
```

### 2.7 WebView 安全

```javascript
// WebView 安全检查项
// 1. JavaScript 是否启用
// 2. 是否允许 file 访问
// 3. 是否有 JS 桥接接口
// 4. 是否允许混合内容

// Frida Hook WebView 检查
Java.perform(function() {
    var WebView = Java.use("android.webkit.WebView");

    WebView.settings.getJavaScriptEnabled.implementation = function() {
        var result = this.getJavaScriptEnabled();
        console.log("[WebView] JavaScript Enabled:", result);
        return result;
    };

    WebView.addJavascriptInterface.implementation = function(obj, name) {
        console.log("[WebView] JS Interface:", name, "对象:", obj.$className);
        return this.addJavascriptInterface(obj, name);
    };

    WebView.loadUrl.overload('java.lang.String').implementation = function(url) {
        console.log("[WebView] 加载URL:", url);
        return this.loadUrl(url);
    };
});
```

**WebView 安全检查清单**：

| 检查项 | 安全配置 | 风险 |
|--------|----------|------|
| JavaScript | 仅在需要时启用 | XSS |
| setAllowFileAccess | 应设为 false | 本地文件泄露 |
| setAllowUniversalAccessFromFileURLs | 应设为 false | 跨域文件访问 |
| JsBridge | 检查暴露的方法 | 远程代码执行 |
| 密码保存 | setSavePassword(false) | 凭据泄露 |

### 2.8 第三方 SDK 安全

```bash
# 列出 APK 中集成的第三方 SDK
find target_decoded/lib -name "*.so"  # 原生库
grep -r "com.google\|com.facebook\|com.tencent\|cn.jpush\|com.umeng" jadx_output/sources/ | head -50

# 检查 SDK 版本是否存在已知漏洞
# 参考: National Vulnerability Database (NVD)
```

### 2.9 Root 检测与绕过

详见《Frida Hook 系统教程》第 3.6 节，核心绕过方法：
- 修改 `Build.TAGS` 为 `release-keys`
- Hook `File.exists()` 过滤 su/busybox 路径
- Hook `Runtime.exec()` 拦截 `su` 命令检测
- 使用 MagiskHide / Zygisk 隐藏 root

### 2.10 完整性校验与绕过

```javascript
// 绕过签名校验
Java.perform(function() {
    var PackageManager = Java.use("android.app.ApplicationPackageManager");
    PackageManager.getPackageInfo.overload('int').implementation = function(flags) {
        var info = this.getPackageInfo(flags);
        // 如果应用检查 signatures 字段，需要伪造
        if ((flags & 0x40) !== 0) { // GET_SIGNATURES
            console.log("[签名校验] 被触发");
            // 返回原始签名信息
        }
        return info;
    };

    // 绕过 CRC/MD5 文件完整性校验
    var ZipFile = Java.use("java.util.zip.ZipFile");
    ZipFile.getEntry.implementation = function(name) {
        var entry = this.getEntry(name);
        if (entry !== null) {
            console.log("[完整性校验] 检查文件:", name);
        }
        return entry;
    };
});
```

---

---

