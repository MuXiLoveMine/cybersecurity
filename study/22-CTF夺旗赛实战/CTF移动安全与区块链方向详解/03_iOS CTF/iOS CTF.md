# iOS CTF

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

---

