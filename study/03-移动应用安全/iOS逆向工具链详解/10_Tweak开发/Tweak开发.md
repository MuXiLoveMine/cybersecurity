# Tweak开发

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

---

## 📋 内容审核与补充建议

> 针对「Tweak开发」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

### ⚔️ 攻击技术
- ⚠️ 缺少attack相关内容

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
