# iOS逆向工具链详解

> 本文档系统性地介绍iOS逆向工程的完整工具链，涵盖逆向环境搭建、头文件提取、动态分析、反汇编、Frida Hook、自动化测试、静态分析、应用脱壳、Tweak开发及越狱生态。

---

## 目录

- [1. iOS逆向环境搭建](#1-ios逆向环境搭建)
  - [1.1 Ubuntu逆向环境](#11-ubuntu逆向环境)
  - [1.2 Theos越狱开发框架](#12-theos越狱开发框架)
  - [1.3 SDK与工具链配置](#13-sdk与工具链配置)
- [2. class-dump与头文件提取](#2-class-dump与头文件提取)
  - [2.1 class-dump基础](#21-class-dump基础)
  - [2.2 头文件分析技巧](#22-头文件分析技巧)
- [3. Cycript动态分析](#3-cycript动态分析)
  - [3.1 Cycript基础语法](#31-cycript基础语法)
  - [3.2 实例变量与方法Hook](#32-实例变量与方法hook)
  - [3.3 消息转发分析](#33-消息转发分析)
- [4. Hopper与IDA Pro逆向](#4-hopper与ida-pro逆向)
  - [4.1 Hopper Disassembler](#41-hopper-disassembler)
  - [4.2 IDA Pro iOS逆向](#42-ida-pro-ios逆向)
- [5. Frida iOS Hooking](#5-frida-ios-hooking)
  - [5.1 ObjC Hook](#51-objc-hook)
  - [5.2 Swift Hook](#52-swift-hook)
  - [5.3 Native Hook](#53-native-hook)
- [6. objection自动化](#6-objection自动化)
  - [6.1 越狱检测绕过](#61-越狱检测绕过)
  - [6.2 SSL Pinning绕过](#62-ssl-pinning绕过)
  - [6.3 Keychain Dump](#63-keychain-dump)
- [7. LLVM Pass与静态分析](#7-llvm-pass与静态分析)
- [8. iOS应用脱壳](#8-ios应用脱壳)
  - [8.1 frida-ios-dump](#81-frida-ios-dump)
  - [8.2 Clutch](#82-clutch)
  - [8.3 其他脱壳工具](#83-其他脱壳工具)
- [9. Tweak开发](#9-tweak开发)
  - [9.1 Theos项目创建](#91-theos项目创建)
  - [9.2 Logos语法](#92-logos语法)
  - [9.3 Cydia Substrate](#93-cydia-substrate)
- [10. iOS越狱生态](#10-ios越狱生态)
  - [10.1 越狱工具](#101-越狱工具)
  - [10.2 包管理器](#102-包管理器)

---

## 1. iOS逆向环境搭建

### 1.1 Ubuntu逆向环境

在Ubuntu上搭建iOS逆向环境，安装核心工具链：

```bash
# 安装基础依赖
sudo apt update
sudo apt install -y build-essential git python3 python3-pip curl wget
sudo apt install -y libssl-dev libusb-dev libplist-utils

# 安装SDK工具
# 从已越狱设备提取SDK
# 将SDK文件放置到/opt/iOS-SDKs/

# 安装ldid（用于签名iOS二进制文件）
git clone https://github.com/daemontuss/ldid.git
cd ldid
./make.sh
sudo cp ldid /usr/local/bin/

# 安装dpkg-deb（用于创建deb包）
sudo apt install -y dpkg-dev

# 安装USB工具
sudo apt install -y libimobiledevice-dev ifuse usbmuxd

# 安装class-dump（通过Swift编译）
# 需要安装Swift工具链
sudo apt install -y swift
```

### 1.2 Theos越狱开发框架

Theos是iOS越狱插件（Tweak）开发的核心框架：

```bash
# 安装Theos
export THEOS=/opt/theos
sudo git clone --recursive https://github.com/theos/theos.git $THEOS

# 配置环境变量
echo 'export THEOS=/opt/theos' >> ~/.bashrc
echo 'export PATH=$THEOS/bin:$PATH' >> ~/.bashrc
source ~/.bashrc

# 安装iOS SDK
# 方法1：从Xcode提取
# 将iPhoneOS.sdk复制到$THEOS/sdks/

# 方法2：从越狱设备提取
# SSH到越狱设备，复制/System/Library/PrivateFrameworks
# 和/usr/lib到本地SDK目录

# 安装dpkg
sudo apt install -y dpkg

# 验证安装
theos --version
```

### 1.3 SDK与工具链配置

```bash
# 配置iOS SDK路径
# 将SDK放置到Theos的sdks目录
mkdir -p $THEOS/sdks
cp -r /path/to/iPhoneOS16.5.sdk $THEOS/sdks/

# 配置工具链
# Theos默认使用Clang
echo 'export THEOS_CHAIN=clang' >> ~/.bashrc

# 安装ldid用于签名
# ldid用于为iOS二进制文件进行伪签名

# 配置dpkg-deb路径
echo 'export PATH=/usr/bin:$PATH' >> ~/.bashrc

# 配置ssh到越狱设备
ssh-keygen -t rsa -b 4096
ssh-copy-id root@<iOS_DEVICE_IP>

# 配置SSH密码（默认alpine）
# 越狱设备默认root密码为alpine，务必修改
# 在设备上执行passwd修改密码

# 验证Theos配置
# 创建测试Tweak验证环境
```

---

## 2. class-dump与头文件提取

### 2.1 class-dump基础

class-dump用于从Mach-O二进制文件中提取Objective-C类接口定义：

```bash
# 安装class-dump
# 从https://github.com/steve228uk/class-dump下载

# 基本用法
class-dump -H /path/to/App -o /output/dir/

# 提取所有头文件
class-dump -H MyApp.app/MyApp -o headers/

# 指定架构
class-dump -H --arch arm64 MyApp.app/MyApp -o headers/

# 提取特定类
class-dump --arch arm64 -o headers/ --classes MyClass MyApp.app/MyApp

# 生成可读性更好的输出
class-dump -H --sdk-root /path/to/sdk MyApp.app/MyApp -o headers/

# 使用class-dump-z（支持Swift）
# class-dump-z是class-dump的改进版
class-dump-z MyApp.app/MyApp -o headers/
```

### 2.2 头文件分析技巧

```bash
# 分析提取的头文件
# 找出继承自UIViewController的类
grep -r ': UIViewController' headers/

# 找出包含关键方法的类
grep -r 'login\|auth\|token\|verify' headers/ -l

# 找出使用URLSession的类
grep -r 'NSURLSession\|URLSession' headers/ -l

# 找出使用Keychain的类
grep -r 'Keychain\|SecItemAdd\|SecItemCopy' headers/ -l

# 找出使用加密的类
grep -r 'CC_SHA\|CCCrypt\|AES\|RSA\|encrypt\|decrypt' headers/ -l

# 找出包含敏感字符串的类
grep -r 'password\|secret\|api_key\|token' headers/ -l

# 分析协议定义
grep -r '@protocol' headers/ -l

# 分析Block使用
grep -r 'block\|Block' headers/ -l
```

---

## 3. Cycript动态分析

### 3.1 Cycript基础语法

Cycript允许在运行时与Objective-C对象交互：

```javascript
// 连接到进程
cycript -p SpringBoard

// 获取当前应用的keyWindow
UIWindow *keyWindow = (UIWindow *)[[UIApplication sharedApplication] keyWindow];

// 获取rootViewController
UIViewController *rootVC = [keyWindow rootViewController];
console.log([rootVC description]);

// 列出所有视图
[rootVC.view.subviews enumerateObjectsUsingBlock:^(UIView *view, NSUInteger idx, BOOL *stop) {
    console.log([view description]);
}];

// 获取当前显示的视图控制器
UIViewController *visibleVC = rootVC;
while ([visibleVC presentedViewController]) {
    visibleVC = [visibleVC presentedViewController];
}
console.log([visibleVC description]);
```

### 3.2 实例变量与方法Hook

```javascript
// 获取类实例变量
#import "<头文件名>"
MyClass *instance = [MyClass new];

// 查看实例变量
MyClass *obj = [[MyClass alloc] init];
console.log([obj ivarList]);

// Hook方法实现
%hook MyClass
- (void)sensitiveMethod:(NSString *)param {
    console.log(@"调用了sensitiveMethod: %@", param);
    %orig; // 调用原始实现
}
%end

// 动态修改实例变量值
MyClass *obj = [someInstance];
[obj setValue:@"hacked" forKey:@"secretValue"];

// 遍历当前所有对象
// 使用objc_getClassList获取所有类
unsigned int count = 0;
Class *classes = objc_copyClassList(&count);
for (int i = 0; i < count; i++) {
    console.log(class_getName(classes[i]));
}
```

### 3.3 消息转发分析

```javascript
// 分析消息转发机制
// Hook forwardingTargetForSelector:
%hook NSObject
- (id)forwardingTargetForSelector:(SEL)sel {
    console.log(@"forwardingTargetForSelector: %@", NSStringFromSelector(sel));
    return %orig;
}
%end

// Hook methodSignatureForSelector:
%hook NSObject
- (NSMethodSignature *)methodSignatureForSelector:(SEL)sel {
    console.log(@"methodSignatureForSelector: %@", NSStringFromSelector(sel));
    return %orig;
}
%end

// Hook forwardInvocation:
%hook NSObject
- (void)forwardInvocation:(NSInvocation *)invocation {
    console.log(@"forwardInvocation: %@", NSStringFromSelector([invocation selector]));
    %orig;
}
%end
```

---

## 4. Hopper与IDA Pro逆向

### 4.1 Hopper Disassembler

Hopper是macOS/Linux上的逆向工程工具，支持Mach-O文件分析：

```
# 基本操作流程
1. 打开Mach-O二进制文件
2. 等待自动分析完成
3. 使用导航条浏览代码段
4. 双击函数查看反汇编
5. 使用Ctrl+D查看伪代码
6. 使用标记功能标注关键函数

# 常用快捷键
- N: 重命名符号
- X: 查看交叉引用
- D: 转换为数据
- C: 转换为代码
- A: 转换为ASCII
- G: 跳转到地址
- :: 添加注释

# 分析技巧
1. 搜索字符串: 使用Search -> Strings
2. 搜索函数名: 使用Search -> Labels
3. 查找入口点: 查找_start符号
4. 分析ObjC方法: 搜索objc_msgSend
5. 分析Swift方法: 搜索swift_前缀
```

### 4.2 IDA Pro iOS逆向

IDA Pro是业界标准的反汇编工具，支持iOS二进制分析：

```
# iOS逆向分析流程

1. 加载Mach-O文件
   - File -> Open -> 选择Mach-O文件
   - 选择ARM64架构
   - 等待自动分析完成

2. 常用分析功能
   - View -> Open subviews -> Strings: 字符串窗口
   - View -> Open subviews -> Functions: 函数列表
   - View -> Open subviews -> Imports: 导入表
   - View -> Open subviews -> Exports: 导出表
   - View -> Open subviews -> Structs: 结构体定义

3. ObjC方法分析
   - 查找objc_msgSend调用
   - 分析SEL参数引用
   - 跟踪方法调用链
   - 使用Shift+F1查看类型库

4. 脚本自动化
   # IDAPython脚本示例
   import idautils
   import idc

   # 查找所有objc_msgSend调用
   for seg in idautils.Segments():
       for func in idautils.Functions(idc.get_segm_start(seg), idc.get_segm_end(seg)):
           name = idc.get_func_name(func)
           if name and 'objc_msgSend' in name:
               print(f"Found at: 0x{func:x}")

5. 加密算法识别
   - 使用FindCrypt插件识别加密常量
   - 分析AES/SHA/RSA相关函数
   - 查找硬编码密钥
```

---

## 5. Frida iOS Hooking

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

## 6. objection自动化

### 6.1 越狱检测绕过

```bash
# 使用objection绕过越狱检测
objection -g com.example.app explore

# 自动绕过越狱检测
ios jailbreak disable

# 手动Hook越狱检测方法
# 在objection中执行
ios hooking search classes Jailbreak
ios hooking watch class JailbreakDetector

# 查看方法列表
ios hooking list class JailbreakDetector

# 替换方法返回值
ios hooking set return_value "-[JailbreakDetector isJailbroken]" false
```

### 6.2 SSL Pinning绕过

```bash
# 在objection中绕过SSL Pinning
ios sslpinning disable

# 查看HTTP请求
ios hooking watch class_method "-[NSURLSession dataTaskWithRequest:completionHandler:]" --dump-args --dump-return

# 拦截所有HTTP请求
android hooking watch class_method okhttp3.OkHttpClient$Builder.build
ios hooking watch class_method "*[* HTTPRequest]"
```

### 6.3 Keychain Dump

```bash
# 导出Keychain数据
ios keychain dump

# 导出并按格式化输出
ios keychain dump --json

# 导出NSUserDefaults
ios nsuserdefaults get

# 导出文件系统
ls /var/mobile/Containers/Data/Application/

# 查看应用沙盒
env
cd /var/mobile/Containers/Data/Application/<UUID>/

# 导出所有Cookie
ios cookies get
```

---

## 7. LLVM Pass与静态分析

```python
# LLVM Pass用于静态分析iOS二进制文件
# 可以分析Mach-O文件中的安全漏洞

# 编写自定义LLVM Pass
# MyAnalysisPass.cpp
'''
#include "llvm/Pass.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/Module.h"
#include "llvm/Support/raw_ostream.h"

using namespace llvm;

struct SecurityAnalysisPass : public ModulePass {
    static char ID;
    SecurityAnalysisPass() : ModulePass(ID) {}

    bool runOnModule(Module &M) override {
        for (auto &F : M) {
            // 检查危险函数调用
            if (F.getName().contains("system")) {
                errs() << "[!] Found system() call in: " << F.getName() << "\n";
            }
            if (F.getName().contains("exec")) {
                errs() << "[!] Found exec() call in: " << F.getName() << "\n";
            }
            if (F.getName().contains("sprintf")) {
                errs() << "[!] Found sprintf() (buffer overflow risk) in: " << F.getName() << "\n";
            }
        }
        return false;
    }
};
'''

# 使用静态分析工具
# 使用otool分析Mach-O
otool -L MyApp              # 查看链接库
otool -ov MyApp              # 查看ObjC类信息
otool -IV MyApp             # 查看符号表
otool -tv MyApp              # 反汇编text段

# 使用nm查看符号
nm -g MyApp                  # 全局符号
nm -m MyApp                  # Mach-O格式符号

# 使用strings提取字符串
strings -n 8 MyApp | grep -i 'password\|secret\|key\|token\|api'
strings -n 8 MyApp | grep -i 'http'
strings -n 8 MyApp | grep -i 'AES\|SHA\|RSA\|encrypt'

# 使用MachOView可视化分析
# 1. 加载二进制文件
# 2. 浏览Mach-O头部
# 3. 查看Load Commands
# 4. 分析段和节
# 5. 查看符号表
# 6. 分析动态绑定信息
```

---

## 8. iOS应用脱壳

### 8.1 frida-ios-dump

```bash
# frida-ios-dump是最常用的iOS脱壳工具
# 需要越狱设备和USB连接

# 安装
git clone https://github.com/AloneMonkey/frida-ios-dump.git
cd frida-ios-dump
pip3 install -r requirements.txt

# 列出已安装应用
python3 dump.py -l

# 脱壳指定应用
python3 dump.py com.example.app

# 脱壳并输出到指定目录
python3 dump.py com.example.app -o /path/to/output/

# 脱壳原理
# 1. 通过Frida连接到目标应用
# 2. Hook dlopen/dlsym获取解密后的内存
# 3. 从内存中dump出解密的Mach-O文件
# 4. 重签名生成可分析的IPA
```

### 8.2 Clutch

```bash
# Clutch是经典的iOS脱壳工具
# 需要在越狱设备上运行

# 安装Clutch
# 通过Cydia/Sileo添加源安装
# 或从GitHub下载deb包安装

# 基本用法
Clutch -i                  # 列出已安装应用
Clutch -d com.example.app  # 脱壳指定应用
Clutch -d 2                # 按编号脱壳

# Clutch脱壳原理
# 1. 找到目标应用的Mach-O文件
# 2. 创建新的进程
# 3. 等待dyld完成解密
# 4. 从内存dump解密后的二进制
# 5. 保存到/var/root/Documents/
```

### 8.3 其他脱壳工具

```bash
# Cracknix（适用于较新iOS版本）
# 在越狱设备上运行
cracknix dump com.example.app

# flexdecrypt
# 通过Cydia安装
flexdecrypt /var/containers/Bundle/Application/<UUID>/MyApp.app/MyApp

# bagbak（基于Node.js）
npm install -g bagbak
bagbak com.example.app

# 手动脱壳方法
# 1. SSH到越狱设备
# 2. 找到应用路径
# 3. 使用gdb/lldb附加到进程
# 4. 获取解密后的内存
# 5. dump内存到文件

# 手动脱壳示例
# SSH到设备
ssh root@<device_ip>

# 找到应用路径
find /var/containers/Bundle/Application -name "MyApp"

# 使用LLDB脱壳
lldb -p <pid>
(lldb) image list MyApp
(lldb) memory read --size 1 --format x --count <size> <decrypt_addr> > dumped.bin
```

---

## 9. Tweak开发

### 9.1 Theos项目创建

```bash
# 创建Theos Tweak项目
nic.pl
# 选择tweak模板
# 输入项目名称、包名、作者等

# 项目结构
# TweakName/
# ├── Makefile
# ├── TweakName.plist     # 注入配置
# ├── Tweak.x             # Tweak代码（Logos语法）
# └── TweakNamePrefs/      # 偏好设置bundle（可选）

# Makefile配置
export THEOS_DEVICE_IP = 192.168.1.100
export THEOS_DEVICE_PORT = 22

TARGET := iphone:clang:16.5:14.0
INSTALL_TARGET_PROCESSES = SpringBoard

include $(THEOS)/makefiles/common.mk

TWEAK_NAME = MyTweak

MyTweak_FILES = Tweak.x
MyTweak_CFLAGS = -fobjc-arc
MyTweak_FRAMEWORKS = UIKit Security

include $(THEOS_MAKE_PATH)/tweak.mk
```

### 9.2 Logos语法

```objc
// Tweak.x - Logos语法示例

// Hook指定类的方法
%hook MyClass

// Hook实例方法
- (void)viewDidLoad {
    %orig; // 调用原始实现
    NSLog(@"MyClass viewDidLoad called");
}

// Hook带参数的方法
- (BOOL)verifyPassword:(NSString *)password {
    NSLog(@"Original password: %@", password);
    // 修改参数
    // NSString *newPassword = @"bypass";
    // return %orig(newPassword);
    // 直接返回YES绕过验证
    return YES;
}

// Hook类方法
+ (instancetype)sharedInstance {
    NSLog(@"sharedInstance called");
    return %orig;
}

// 添加新方法到类
%new
- (void)myNewMethod {
    NSLog(@"This is a new method added by Tweak");
}

// 添加属性
%new
- (NSString *)myProperty {
    return @"custom value";
}

%new
- (void)setMyProperty:(NSString *)value {
    NSLog(@"Setting myProperty to: %@", value);
}

%end // 结束Hook

// Hook多个类
%hook AnotherClass
- (void)someMethod {
    %orig;
}
%end

// 在特定时机执行代码
%ctor {
    NSLog(@"Tweak loaded!");
    // 初始化代码
}

%dtor {
    NSLog(@"Tweak unloaded!");
}
```

### 9.3 Cydia Substrate

```objc
// Cydia Substrate (MobileSubstrate) 是Tweak的底层框架
// 提供方法Hook和函数Hook能力

// 使用MSHookFunction Hook C函数
#import <substrate.h>

// 定义函数指针
static void (*orig_CC_SHA1)(const void *data, CC_LONG len, unsigned char *md);

// 替换函数
static void my_CC_SHA1(const void *data, CC_LONG len, unsigned char *md) {
    NSLog(@"CC_SHA1 called, data length: %lu", len);
    orig_CC_SHA1(data, len, md);
    NSLog(@"SHA1 result: %s", md);
}

// 在%ctor中安装Hook
%ctor {
    MSHookFunction(CC_SHA1, (void *)my_CC_SHA1, (void **)&orig_CC_SHA1);
}

// 使用MSHookMessageEx Hook ObjC方法
// Logos的%hook底层就是使用MSHookMessageEx
#import <objc/runtime.h>

static void (*orig_viewDidLoad)(id self, SEL _cmd);

static void my_viewDidLoad(id self, SEL _cmd) {
    NSLog(@"viewDidLoad: %@", [self class]);
    orig_viewDidLoad(self, _cmd);
}

%ctor {
    MSHookMessageEx(objc_getClass("UIViewController"),
                    @selector(viewDidLoad),
                    (void *)my_viewDidLoad,
                    (void **)&orig_viewDidLoad);
}
```

---

## 10. iOS越狱生态

### 10.1 越狱工具

```bash
# checkra1n
# 基于checkm8漏洞的硬件级越狱
# 支持A7-A11芯片设备（iPhone 5s - iPhone X）
# 特点：tethered/semi-tethered，需要USB连接引导

# unc0ver
# 基于内核漏洞的越狱
# 支持iOS 11.0 - 14.3
# 特点：untethered，重启后保持越狱

# Taurine
# 吥德赛团队开发的越狱
# 支持iOS 14.0 - 14.3
# 特点：基于CVE-2021-1782内核漏洞

# Fugu
# 开源越狱工具
# 支持A12-A14设备
# 特点：基于CVE-2021-1782

# Palera1n
# 最新越狱工具
# 支持checkm8设备（A7-A11）
# 支持iOS 15+

# 越狱后安装常用工具
# Cydia/Sileo中安装：
# - OpenSSH (SSH连接)
# - Frida (动态分析)
# - Cycript (运行时分析)
# - adv-cmds (高级命令行工具)
# - wget/curl
# - vim/nano
# - class-dump (头文件提取)
# - Clutch (应用脱壳)
# - AppSync (安装未签名IPA)
# - AFC2 (文件系统访问)
# - Frida (动态注入)
```

### 10.2 包管理器

```
# Cydia - 经典越狱包管理器
# 由Saurik开发，是最早的越狱包管理器
# 软件源（常用）：
# - BigBoss (http://apt.bigboss.org)
# - ModMyi (http://apt.modmyi.com)
# - Saurik's Cydia (http://apt.saurik.com)

# Sileo - 新一代包管理器
# 由CoolStar团队开发
# 更快的包管理速度
# 支持现代iOS版本
# 软件源与Cydia兼容

# Zebra - 轻量级包管理器
# 开源项目
# 支持Cydia和Sileo源
# 更好的性能

# 安装Tweak
# 1. 在包管理器中搜索Tweak
# 2. 点击安装
# 3. 注销（Respring）或重启SpringBoard
# 4. Tweak自动加载

# 常用Tweak源
# - https://repo.chariz.com (Chariz)
# - https://repo.dynastic.co (Dynastic)
# - https://apt.bingner.com (Bingner)
# - https://repo.packix.com (Packix)

# Tweak管理
# 使用iCleaner Pro管理已安装Tweak
# 排查冲突时选择性禁用Tweak
```

---

## 总结

本文档系统性地介绍了iOS逆向工程的完整工具链，包括环境搭建、class-dump头文件提取、Cycript动态分析、Hopper/IDA Pro反汇编、Frida Hook（ObjC/Swift/Native）、objection自动化测试、LLVM Pass静态分析、应用脱壳（frida-ios-dump/Clutch）、Tweak开发（Theos/Logos/Substrate）以及越狱生态（checkra1n/unc0ver/Sileo/Zebra）。

> **免责声明**：本文档仅用于安全学习和研究目的。在使用这些技术时请确保获得适当授权，遵守相关法律法规。未经授权分析他人应用属于违法行为。
