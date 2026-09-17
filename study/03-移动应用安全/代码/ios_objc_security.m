// ============================================================================
// iOS Objective-C安全工具 v1.0
// 深层iOS运行时安全检测与防护工具
//
// 功能模块：
// 1. Method Swizzling检测
// 2. Cycript交互示例
// 3. 运行时Hook检测
// 4. 反调试技术
// 5. 越狱检测方法
//
// 免责声明：仅用于授权的安全测试和防护研究。
// ============================================================================

#import <Foundation/Foundation.h>
#import <objc/runtime.h>
#import <objc/message.h>
#import <Security/Security.h>
#import <dlfcn.h>
#import <sys/sysctl.h>
#import <mach/mach.h>
#import <mach/mach_init.h>
#import <dlfcn.h>
#import <unistd.h>
#import <signal.h>
#import <stdio.h>
#import <stdlib.h>
#import <string.h>
#import <fcntl.h>
#import <sys/stat.h>

// ============================================================================
// 全局定义与工具
// ============================================================================

/// 安全严重程度枚举
typedef NS_ENUM(NSInteger, SecuritySeverity) {
    SecuritySeverityCritical = 0,  // 严重
    SecuritySeverityHigh     = 1,  // 高危
    SecuritySeverityMedium   = 2,  // 中危
    SecuritySeverityLow      = 3,  // 低危
    SecuritySeverityInfo     = 4   // 信息
};

/// 安全发现结果
@interface SecurityFinding : NSObject
@property (nonatomic, assign) SecuritySeverity severity;
@property (nonatomic, copy) NSString *tool;
@property (nonatomic, copy) NSString *title;
@property (nonatomic, copy) NSString *desc;
@property (nonatomic, copy) NSString *recommendation;
@property (nonatomic, copy) NSString *evidence;
@end

@implementation SecurityFinding
@end

/// 结果收集器
@interface ResultCollector : NSObject
@property (nonatomic, strong) NSMutableArray<SecurityFinding *> *findings;
- (void)addFinding:(SecurityFinding *)finding;
- (void)printSummary;
- (void)printDetails;
@end

@implementation ResultCollector

- (instancetype)init {
    self = [super init];
    if (self) {
        _findings = [[NSMutableArray alloc] init];
    }
    return self;
}

- (void)addFinding:(SecurityFinding *)finding {
    [self.findings addObject:finding];
}

- (void)printSummary {
    NSInteger counts[5] = {0};
    for (SecurityFinding *f in self.findings) {
        counts[f.severity]++;
    }
    printf("===========================================================\n");
    printf("  iOS Objective-C安全分析报告\n");
    printf("===========================================================\n");
    printf("  总发现数: %lu\n", (unsigned long)self.findings.count);
    NSArray *labels = @[@"严重", @"高危", @"中危", @"低危", @"信息"];
    for (int i = 0; i < 5; i++) {
        if (counts[i] > 0) {
            printf("  %@: %ld\n", labels[i], (long)counts[i]);
        }
    }
    printf("===========================================================\n");
}

- (void)printDetails {
    NSArray *labels = @[@"严重", @"高危", @"中危", @"低危", @"信息"];
    for (SecurityFinding *f in self.findings) {
        printf("\n[%@] %@\n", labels[f.severity], f.title.UTF8String);
        printf("  工具: %@\n", f.tool.UTF8String);
        printf("  描述: %@\n", f.desc.UTF8String);
        printf("  证据: %@\n", f.evidence.UTF8String);
        printf("  建议: %@\n", f.recommendation.UTF8String);
    }
}

@end

/// 日志输出
static void LogInfo(NSString *msg) {
    printf("[信息] %s\n", msg.UTF8String);
}

static void LogSuccess(NSString *msg) {
    printf("[成功] %s\n", msg.UTF8String);
}

static void LogWarning(NSString *msg) {
    printf("[警告] %s\n", msg.UTF8String);
}

static void LogError(NSString *msg) {
    printf("[错误] %s\n", msg.UTF8String);
}

static void LogVuln(NSString *msg) {
    printf("[漏洞] %s\n", msg.UTF8String);
}

// ============================================================================
// 模块1：Method Swizzling检测
// ============================================================================

/**
 * Method Swizzling检测器
 *
 * Method Swizzling是Objective-C运行时的特性，允许交换两个方法的实现。
 * 攻击者可以利用Swizzling来hook关键方法，如：
 * - 交换登录验证方法
 * - 交换加密方法
 * - 交换网络请求方法
 *
 * 检测方法：
 * - 比较方法实现的地址与原始地址
 * - 检查方法实现的所属类
 * - 检查是否来自可疑模块
 */
@interface MethodSwizzlingDetector : NSObject

/// 检测指定类的方法是否被Swizzle
+ (void)detectSwizzlingForClass:(Class)cls
                        selector:(SEL)selector
                        results:(ResultCollector *)results;

/// 全面检测关键类的方法
+ (void)detectAllSwizzling:(ResultCollector *)results;

/// 获取方法实现信息
+ (NSDictionary *)getMethodInfo:(Method)method;

@end

@implementation MethodSwizzlingDetector

/// 检测单个方法是否被Swizzle
+ (void)detectSwizzlingForClass:(Class)cls
                        selector:(SEL)selector
                        results:(ResultCollector *)results {
    // 获取原始方法
    Method originalMethod = class_getInstanceMethod(cls, selector);
    if (!originalMethod) {
        return;
    }

    // 获取方法实现
    IMP originalIMP = method_getImplementation(originalMethod);

    // 获取方法实现的所属类
    Class implementingClass = class_getImp(cls, selector);

    // 检查实现是否与声明类不同
    if (implementingClass != cls && implementingClass != class_getSuperclass(cls)) {
        SecurityFinding *finding = [[SecurityFinding alloc] init];
        finding.tool = @"Method Swizzling检测器";
        finding.severity = SecuritySeverityHigh;
        finding.title = [NSString stringWithFormat:@"方法可能被Swizzle: %@::%@",
                        NSStringFromClass(cls), NSStringFromSelector(selector)];
        finding.desc = [NSString stringWithFormat:
            @"方法 %@ 的实现来自 %@ 而非 %@，可能被Swizzle",
            NSStringFromSelector(selector),
            NSStringFromClass(implementingClass),
            NSStringFromClass(cls)];
        finding.evidence = [NSString stringWithFormat:
            @"声明类: %@, 实现类: %@",
            NSStringFromClass(cls), NSStringFromClass(implementingClass)];
        finding.recommendation = @"检查方法实现来源，确认是否为预期行为";
        [results addFinding:finding];
        LogVuln(finding.title);
    }

    // 检查方法实现的模块
    Dl_info info;
    if (dladdr((void *)originalIMP, &info)) {
        NSString *implPath = [NSString stringWithUTF8String:info.dli_fname];
        NSString *implName = [NSString stringWithUTF8String:info.dli_sname];

        // 检查是否来自非系统模块
        if (![implPath containsString:@"/usr/lib/"] &&
            ![implPath containsString:@"/System/Library/"]) {
            SecurityFinding *finding = [[SecurityFinding alloc] init];
            finding.tool = @"Method Swizzling检测器";
            finding.severity = SecuritySeverityCritical;
            finding.title = [NSString stringWithFormat:@"方法实现来自非系统模块: %@",
                            NSStringFromSelector(selector)];
            finding.desc = [NSString stringWithFormat:
                @"方法 %@ 的实现来自 %@ (符号: %@)，可能被恶意注入",
                NSStringFromSelector(selector), implPath, implName];
            finding.evidence = [NSString stringWithFormat:@"模块: %@, 符号: %@",
                               implPath, implName];
            finding.recommendation = @"检查dylib注入，使用dyld环境变量限制";
            [results addFinding:finding];
            LogVuln(finding.title);
        }
    }
}

/// 全面检测关键类的方法
+ (void)detectAllSwizzling:(ResultCollector *)results {
    LogInfo(@"开始Method Swizzling全面检测...");

    // 检测关键类的方法
    NSArray *criticalSelectors = @[
        NSStringFromSelector(@selector(viewDidAppear:)),
        NSStringFromSelector(@selector(viewWillAppear:)),
        NSStringFromSelector(@selector(initWithCoder:)),
        NSStringFromSelector(@selector(initWithFrame:)),
    ];

    // 检测UIViewController
    [self detectSwizzlingForClass:[UIViewController class]
                        selector:@selector(viewDidAppear:)
                        results:results];
    [self detectSwizzlingForClass:[UIViewController class]
                        selector:@selector(viewWillAppear:)
                        results:results];

    // 检测NSObject
    [self detectSwizzlingForClass:[NSObject class]
                        selector:@selector(initWithCoder:)
                        results:results];

    // 检测UIView
    [self detectSwizzlingForClass:[UIView class]
                        selector:@selector(initWithFrame:)
                        results:results];

    // 检测UIApplication
    [self detectSwizzlingForClass:[UIApplication class]
                        selector:@selector(sendAction:to:from:forEvent:)
                        results:results];

    // 检测UIDevice
    [self detectSwizzlingForClass:[UIDevice class]
                        selector:@selector(serialNumber)
                        results:results];

    LogInfo(@"Method Swizzling检测完成");
}

/// 获取方法详细信息
+ (NSDictionary *)getMethodInfo:(Method)method {
    NSMutableDictionary *info = [NSMutableDictionary dictionary];

    // 方法类型
    info[@"types"] = [NSString stringWithUTF8String:method_getTypeEncoding(method)];

    // 方法实现地址
    IMP imp = method_getImplementation(method);
    info[@"implementation"] = [NSString stringWithFormat:@"%p", imp];

    // 方法所属模块
    Dl_info dlInfo;
    if (dladdr((void *)imp, &dlInfo)) {
        info[@"module"] = [NSString stringWithUTF8String:dlInfo.dli_fname];
        if (dlInfo.dli_sname) {
            info[@"symbol"] = [NSString stringWithUTF8String:dlInfo.dli_sname];
        }
    }

    return info;
}

@end

// ============================================================================
// 模块2：Cycript交互示例
// ============================================================================

/**
 * Cycript交互工具
 *
 * Cycript是iOS逆向工程中常用的动态分析工具，允许在运行时：
 * - 访问和修改对象的实例变量
 * - 调用任意方法
 * - Hook方法实现
 * - 注入JavaScript代码
 *
 * 本模块提供检测Cycript注入和防御的示例。
 */

// Cycript检测器
@interface CycriptDetector : NSObject

/// 检测Cycript是否正在运行
+ (BOOL)isCycriptRunning:(ResultCollector *)results;

/// 检测Cycript注入的dylib
+ (void)detectCycriptInjection:(ResultCollector *)results;

/// 检测Cycript监听端口
+ (void)detectCycriptPort:(ResultCollector *)results;

@end

@implementation CycriptDetector

/// 检测Cycript是否正在运行
+ (BOOL)isCycriptRunning:(ResultCollector *)results {
    LogInfo(@"检测Cycript运行状态...");

    // 检测Cycript相关进程
    // 通过检查/proc或使用sysctl检测

    // 方法1: 检测Cycript的dylib是否已加载
    BOOL cycriptFound = NO;

    // 获取已加载的dylib列表
    uint32_t count = _dyld_image_count();
    for (uint32_t i = 0; i < count; i++) {
        const char *name = _dyld_get_image_name(i);
        if (name != NULL) {
            NSString *libName = [NSString stringWithUTF8String:name];
            if ([libName containsString:@"cycript"] ||
                [libName containsString:@"CycriptSubstrate"]) {
                cycriptFound = YES;

                SecurityFinding *finding = [[SecurityFinding alloc] init];
                finding.tool = @"Cycript检测器";
                finding.severity = SecuritySeverityCritical;
                finding.title = @"检测到Cycript dylib注入";
                finding.desc = [NSString stringWithFormat:
                    @"检测到Cycript动态库已加载: %@", libName];
                finding.evidence = libName;
                finding.recommendation = @"检查dyld环境变量，限制dylib注入";
                [results addFinding:finding];
                LogVuln(finding.title);
                break;
            }
        }
    }

    // 方法2: 检测Cycript Server端口（默认2234）
    // 使用CFSocket检测端口是否开放
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock >= 0) {
        struct sockaddr_in addr;
        addr.sin_family = AF_INET;
        addr.sin_port = htons(2234); // Cycript默认端口
        addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);

        if (connect(sock, (struct sockaddr *)&addr, sizeof(addr)) == 0) {
            SecurityFinding *finding = [[SecurityFinding alloc] init];
            finding.tool = @"Cycript检测器";
            finding.severity = SecuritySeverityCritical;
            finding.title = @"Cycript Server端口开放";
            finding.desc = @"检测到端口2234(Cycript默认端口)开放，Cycript Server可能正在运行";
            finding.evidence = @"端口2234可连接";
            finding.recommendation = @"检测到动态分析工具，应用可能正在被调试";
            [results addFinding:finding];
            LogVuln(finding.title);
        }
        close(sock);
    }

    return cycriptFound;
}

/// 检测Cycript注入的dylib
+ (void)detectCycriptInjection:(ResultCollector *)results {
    LogInfo(@"检测Cycript dylib注入...");

    uint32_t count = _dyld_image_count();
    NSMutableArray *suspiciousLibs = [[NSMutableArray alloc] init];

    for (uint32_t i = 0; i < count; i++) {
        const char *name = _dyld_get_image_name(i);
        if (name != NULL) {
            NSString *libName = [NSString stringWithUTF8String:name];
            NSString *libLower = [libName lowercaseString];

            // 检查可疑的动态库
            if ([libLower containsString:@"cycript"] ||
                [libLower containsString:@"substrate"] ||
                [libLower containsString:@"substitute"] ||
                [libLower containsString:@"ellekit"] ||
                [libLower containsString:@"tweak"] ||
                [libLower containsString:@"hook"] ||
                [libLower containsString:@"inject"] ||
                [libLower containsString:@"frida"]) {

                [suspiciousLibs addObject:libName];
            }
        }
    }

    if (suspiciousLibs.count > 0) {
        SecurityFinding *finding = [[SecurityFinding alloc] init];
        finding.tool = @"Cycript检测器";
        finding.severity = SecuritySeverityCritical;
        finding.title = [NSString stringWithFormat:@"检测到 %@ 个可疑动态库注入",
                        @(suspiciousLibs.count)];
        finding.desc = [NSString stringWithFormat:
            @"检测到以下可疑动态库已加载:\n%@",
            [suspiciousLibs componentsJoinedByString:@"\n"]];
        finding.evidence = [suspiciousLibs componentsJoinedByString:@", "];
        finding.recommendation = @"检查DYLD_INSERT_LIBRARIES环境变量，限制动态库注入";
        [results addFinding:finding];
        LogVuln(finding.title);
    } else {
        LogSuccess(@"未检测到可疑动态库注入");
    }
}

/// 检测Cycript监听端口
+ (void)detectCycriptPort:(ResultCollector *)results {
    LogInfo(@"检测Cycript端口...");

    // 检测常见动态分析工具端口
    NSArray *ports = @[
        @2234,  // Cycript
        @27042, // Frida
        @27043, // Frida
        @4444,  // Meterpreter
        @5555,  // ADB
    ];

    for (NSNumber *portNum in ports) {
        int sock = socket(AF_INET, SOCK_STREAM, 0);
        if (sock < 0) continue;

        struct sockaddr_in addr;
        addr.sin_family = AF_INET;
        addr.sin_port = htons(portNum.intValue);
        addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);

        if (connect(sock, (struct sockaddr *)&addr, sizeof(addr)) == 0) {
            SecurityFinding *finding = [[SecurityFinding alloc] init];
            finding.tool = @"Cycript检测器";
            finding.severity = SecuritySeverityHigh;
            finding.title = [NSString stringWithFormat:@"检测到端口 %@ 开放",
                           portNum];
            finding.desc = [NSString stringWithFormat:
                @"端口 %@ 可能被动态分析工具使用", portNum];
            finding.evidence = [NSString stringWithFormat:@"端口 %@ 可连接", portNum];
            finding.recommendation = @"检测到调试端口，应用可能正在被分析";
            [results addFinding:finding];
            LogWarning(finding.title);
        }

        close(sock);
    }
}

@end

// ============================================================================
// 模块3：运行时Hook检测
// ============================================================================

/**
 * 运行时Hook检测器
 *
 * 检测Objective-C运行时的各种Hook技术：
 * - Method Swizzling
 * - Method Exchange
 * - isa Swizzling
 * - IMP Swizzling
 * - dylib注入
 *
 * 通过检查方法实现的地址和来源来判断是否被Hook。
 */
@interface RuntimeHookDetector : NSObject

/// 检测所有关键方法的Hook状态
+ (void)detectAllHooks:(ResultCollector *)results;

/// 检测指定类的方法是否被Hook
+ (BOOL)isMethodHooked:(Class)cls selector:(SEL)sel;

/// 检测isa Swizzling
+ (void)detectIsaSwizzling:(ResultCollector *)results;

/// 获取方法实现的模块路径
+ (NSString *)getImplementationModule:(IMP)imp;

@end

@implementation RuntimeHookDetector

/// 检测所有关键方法的Hook状态
+ (void)detectAllHooks:(ResultCollector *)results {
    LogInfo(@"开始运行时Hook检测...");

    // 关键类列表
    NSArray *criticalClasses = @[
        @"NSURLSession",
        @"NSURLSessionDataTask",
        @"NSURLRequest",
        @"UIWebView",
        @"WKWebView",
        @"UITextField",
        @"UITextView",
        @"UILabel",
        @"UIViewController",
        @"UIApplication",
        @"UIDevice",
        @"UIScreen",
        @"NSFileManager",
        @"NSUserDefaults",
        @"Keychain"
    ];

    // 检查每个关键类
    for (NSString *className in criticalClasses) {
        Class cls = NSClassFromString(className);
        if (!cls) continue;

        // 获取类的方法列表
        unsigned int methodCount = 0;
        Method *methods = class_copyMethodList(cls, &methodCount);

        for (unsigned int i = 0; i < methodCount; i++) {
            Method method = methods[i];
            SEL selector = method_getName(method);
            IMP imp = method_getImplementation(method);

            // 检查实现是否来自系统模块
            NSString *module = [self getImplementationModule:imp];
            if (module && ![module containsString:@"UIKit"] &&
                ![module containsString:@"Foundation"] &&
                ![module containsString:@"/System/"] &&
                ![module containsString:@"/usr/lib/"]) {

                SecurityFinding *finding = [[SecurityFinding alloc] init];
                finding.tool = @"运行时Hook检测器";
                finding.severity = SecuritySeverityHigh;
                finding.title = [NSString stringWithFormat:
                    @"%@::%@ 可能被Hook",
                    className, NSStringFromSelector(selector)];
                finding.desc = [NSString stringWithFormat:
                    @"方法实现来自非系统模块: %@ (类: %@, 方法: %@)",
                    module, className, NSStringFromSelector(selector)];
                finding.evidence = [NSString stringWithFormat:
                    @"模块: %@, IMP: %p", module, imp];
                finding.recommendation = @"检查方法实现来源，确认是否为预期修改";
                [results addFinding:finding];
            }
        }

        free(methods);
    }

    // 检测isa Swizzling
    [self detectIsaSwizzling:results];

    LogInfo(@"运行时Hook检测完成");
}

/// 检测单个方法是否被Hook
+ (BOOL)isMethodHooked:(Class)cls selector:(SEL)sel {
    Method method = class_getInstanceMethod(cls, sel);
    if (!method) return NO;

    IMP imp = method_getImplementation(method);
    NSString *module = [self getImplementationModule:imp];

    // 如果实现来自非系统模块，可能被Hook
    if (module) {
        if (![module containsString:@"/System/"] &&
            ![module containsString:@"/usr/lib/"]) {
            return YES;
        }
    }

    return NO;
}

/// 检测isa Swizzling
+ (void)detectIsaSwizzling:(ResultCollector *)results {
    LogInfo(@"检测isa Swizzling...");

    // isa Swizzling是一种将对象的isa指针替换为另一个类的技术
    // 常用于KVO实现，但也可被攻击者滥用

    // 检查常见对象的isa
    NSObject *testObj = [[NSObject alloc] init];
    Class originalIsa = object_getClass(testObj);

    // 获取类名
    NSString *className = NSStringFromClass(originalIsa);

    // 如果类名包含不寻常的前缀，可能被Swizzle
    if ([className hasPrefix:@"NSKVONotifying_"] ||
        [className hasPrefix:@"_NSKVONotifying"]) {
        // 这是KVO的isa Swizzling，正常行为
        LogInfo(@"检测到KVO isa Swizzling（正常行为）");
    }

    // 检查是否有非预期的isa Swizzling
    // 遍历关键类检查
    NSArray *keyClasses = @[
        NSStringFromClass([UIApplication class]),
        NSStringFromClass([UIDevice class]),
    ];

    for (NSString *className in keyClasses) {
        Class cls = NSClassFromString(className);
        if (cls) {
            // 获取实例
            id instance = [cls valueForKey:@"sharedInstance"];
            if (instance) {
                Class isa = object_getClass(instance);
                NSString *isaName = NSStringFromClass(isa);

                if (![isaName isEqualToString:className]) {
                    SecurityFinding *finding = [[SecurityFinding alloc] init];
                    finding.tool = @"运行时Hook检测器";
                    finding.severity = SecuritySeverityHigh;
                    finding.title = [NSString stringWithFormat:
                        @"%@ 的isa可能被Swizzle", className];
                    finding.desc = [NSString stringWithFormat:
                        @"对象isa指向 %@ 而非 %@",
                        isaName, className];
                    finding.evidence = [NSString stringWithFormat:
                        @"原始类: %@, isa类: %@",
                        className, isaName];
                    finding.recommendation = @"检查KVO注册和isa Swizzling";
                    [results addFinding:finding];
                }
            }
        }
    }
}

/// 获取方法实现所属的模块路径
+ (NSString *)getImplementationModule:(IMP)imp {
    Dl_info info;
    if (dladdr((void *)imp, &info)) {
        if (info.dli_fname) {
            return [NSString stringWithUTF8String:info.dli_fname];
        }
    }
    return nil;
}

@end

// ============================================================================
// 模块4：反调试技术
// ============================================================================

/**
 * 反调试技术
 *
 * 防止调试器附加到应用进程，包括：
 * - ptrace检测
 * - sysctl检测
 * - 时间检测
 * - 异常处理检测
 *
 * 这些技术可以增加逆向工程的难度。
 */
@interface AntiDebugging : NSObject

/// 检测调试器是否附加
+ (BOOL)isDebuggerAttached;

/// 使用ptrace防止调试
+ (void)preventPtrace;

/// 使用sysctl检测调试
+ (BOOL)detectDebuggerViaSysctl;

/// 使用时间检测调试
+ (BOOL)detectDebuggerViaTiming;

/// 设置异常处理检测
+ (void)setupExceptionHandling;

/// 综合反调试保护
+ (void)applyAllProtections:(ResultCollector *)results;

@end

@implementation AntiDebugging

/// 检测调试器是否附加
+ (BOOL)isDebuggerAttached {
    BOOL attached = NO;

    // 方法1: 使用sysctl检测
    if ([self detectDebuggerViaSysctl]) {
        attached = YES;
    }

    // 方法2: 使用时间检测
    if ([self detectDebuggerViaTiming]) {
        attached = YES;
    }

    // 方法3: 检查getppid()
    // 如果父进程不是launchd(pid=1)，可能被调试
    pid_t parent = getppid();
    if (parent != 1) {
        // 可能被调试器附加
        attached = YES;
    }

    return attached;
}

/// 使用ptrace防止调试
+ (void)preventPtrace {
    // PTRACE_DENY_ATTACH = 31
    // 调用ptrace(PT_DENY_ATTACH, 0, 0, 0)拒绝调试器附加
    // 注意：App Store审核可能拒绝使用ptrace的应用

    typedef int (*ptrace_ptr_t)(int, pid_t, int, int);
    void *handle = dlopen(0, RTLD_GLOBAL | RTLD_NOW);
    if (handle) {
        ptrace_ptr_t ptrace_func = dlsym(handle, "ptrace");
        if (ptrace_func) {
            // PT_DENY_ATTACH = 31
            ptrace_func(31, 0, 0, 0);
        }
        dlclose(handle);
    }
}

/// 使用sysctl检测调试器
+ (BOOL)detectDebuggerViaSysctl {
    // 通过sysctl检查进程的P_TRACED标志
    int mib[4];
    struct kinfo_proc info;
    size_t size = sizeof(info);

    mib[0] = CTL_KERN;
    mib[1] = KERN_PROC;
    mib[2] = KERN_PROC_PID;
    mib[3] = getpid();

    if (sysctl(mib, 4, &info, &size, NULL, 0) == -1) {
        return NO;
    }

    // 检查P_TRACED标志
    return (info.kp_proc.p_flag & P_TRACED) != 0;
}

/// 使用时间检测调试
+ (BOOL)detectDebuggerViaTiming {
    // 调试器会在断点处暂停执行，导致时间异常
    // 通过测量代码执行时间来检测

    const int64_t threshold = 500000; // 500ms（纳秒）

    // 记录开始时间
    mach_time_t start = mach_absolute_time();

    // 执行一些计算
    volatile int sum = 0;
    for (int i = 0; i < 1000; i++) {
        sum += i;
    }

    // 记录结束时间
    mach_time_t end = mach_absolute_time();

    // 计算耗时
    mach_timebase_info_data_t timebase;
    mach_timebase_info(&timebase);

    int64_t elapsed = (end - start) * timebase.numer / timebase.denom;

    // 如果耗时超过阈值，可能有调试器
    if (elapsed > threshold) {
        return YES;
    }

    return NO;
}

/// 设置异常处理检测
+ (void)setupExceptionHandling {
    // 设置信号处理函数
    // 调试器会拦截信号，如果信号被处理说明没有调试器

    signal(SIGTRAP, SIG_IGN);  // 忽略SIGTRAP

    // 恢复信号处理
    signal(SIGTRAP, SIG_DFL);
}

/// 综合反调试保护
+ (void)applyAllProtections:(ResultCollector *)results {
    LogInfo(@"应用反调试保护...");

    // 1. 检测调试器
    BOOL debuggerAttached = [self isDebuggerAttached];

    if (debuggerAttached) {
        SecurityFinding *finding = [[SecurityFinding alloc] init];
        finding.tool = @"反调试保护";
        finding.severity = SecuritySeverityHigh;
        finding.title = @"检测到调试器附加";
        finding.desc = @"应用检测到调试器正在附加，可能正在被逆向分析";
        finding.evidence = @"sysctl或时间检测触发";
        finding.recommendation = @"应用检测到调试，考虑退出或改变行为";
        [results addFinding:finding];
        LogVuln(finding.title);
    } else {
        LogSuccess(@"未检测到调试器");
    }

    // 2. 检测越狱环境（详细检测在越狱检测模块）
    // 这里提供检测框架

    // 3. 检测Frida
    BOOL fridaDetected = [self detectFrida];
    if (fridaDetected) {
        SecurityFinding *finding = [[SecurityFinding alloc] init];
        finding.tool = @"反调试保护";
        finding.severity = SecuritySeverityCritical;
        finding.title = @"检测到Frida";
        finding.desc = @"应用检测到Frida动态注入工具";
        finding.evidence = @"Frida相关dylib或端口检测到";
        finding.recommendation = @"检测到动态分析工具，应用可能正在被分析";
        [results addFinding:finding];
        LogVuln(finding.title);
    }

    LogInfo(@"反调试保护应用完成");
}

/// 检测Frida
+ (BOOL)detectFrida {
    // 方法1: 检查Frida相关dylib
    uint32_t count = _dyld_image_count();
    for (uint32_t i = 0; i < count; i++) {
        const char *name = _dyld_get_image_name(i);
        if (name != NULL) {
            NSString *libName = [NSString stringWithUTF8String:name];
            if ([libName containsString:@"frida"]) {
                return YES;
            }
        }
    }

    // 方法2: 检查Frida端口（默认27042）
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock >= 0) {
        struct sockaddr_in addr;
        addr.sin_family = AF_INET;
        addr.sin_port = htons(27042);
        addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);

        if (connect(sock, (struct sockaddr *)&addr, sizeof(addr)) == 0) {
            close(sock);
            return YES;
        }
        close(sock);
    }

    // 方法3: 检查Frida的异常端口映射
    FILE *fp = fopen("/proc/self/maps", "r");
    if (fp) {
        char line[512];
        while (fgets(line, sizeof(line), fp)) {
            if (strstr(line, "frida") || strstr(line, "gum-js") ||
                strstr(line, "linjector")) {
                fclose(fp);
                return YES;
            }
        }
        fclose(fp);
    }

    return NO;
}

@end

// ============================================================================
// 模块5：越狱检测方法
// ============================================================================

/**
 * 越狱检测器
 *
 * 多维度检测iOS设备是否越狱：
 * - 文件系统检测（越狱文件/目录）
 * - URL Scheme检测（Cydia/Sileo）
 * - 系统文件访问检测
 * - 沙盒完整性检测
 * - 动态库注入检测
 * - Fork/SSH检测
 */
@interface JailbreakDetector : NSObject

/// 综合越狱检测
+ (BOOL)isJailbroken:(ResultCollector *)results;

/// 检测越狱文件
+ (BOOL)checkJailbreakFiles:(ResultCollector *)results;

/// 检测URL Scheme
+ (BOOL)checkURLSchemes:(ResultCollector *)results;

/// 检测系统文件访问
+ (BOOL)checkSystemFileAccess:(ResultCollector *)results;

/// 检测沙盒完整性
+ (BOOL)checkSandboxIntegrity:(ResultCollector *)results;

/// 检测动态库注入
+ (BOOL)checkDylibInjection:(ResultCollector *)results;

/// 检测SSH/Fork
+ (BOOL)checkSSHAndFork:(ResultCollector *)results;

@end

@implementation JailbreakDetector

/// 综合越狱检测
+ (BOOL)isJailbroken:(ResultCollector *)results {
    LogInfo(@"开始综合越狱检测...");

    BOOL jailbroken = NO;

    if ([self checkJailbreakFiles:results]) jailbroken = YES;
    if ([self checkURLSchemes:results]) jailbroken = YES;
    if ([self checkSystemFileAccess:results]) jailbroken = YES;
    if ([self checkSandboxIntegrity:results]) jailbroken = YES;
    if ([self checkDylibInjection:results]) jailbroken = YES;
    if ([self checkSSHAndFork:results]) jailbroken = YES;

    if (jailbroken) {
        SecurityFinding *finding = [[SecurityFinding alloc] init];
        finding.tool = @"越狱检测器";
        finding.severity = SecuritySeverityCritical;
        finding.title = @"设备已越狱";
        finding.desc = @"综合检测表明当前设备已越狱，存在安全风险";
        finding.evidence = @"多个越狱指示器触发";
        finding.recommendation = @"在越狱设备上应增加额外防护或拒绝运行敏感功能";
        [results addFinding:finding];
        LogVuln(@"设备已越狱!");
    } else {
        LogSuccess(@"设备未越狱");
    }

    LogInfo(@"越狱检测完成");
    return jailbroken;
}

/// 检测越狱文件
+ (BOOL)checkJailbreakFiles:(ResultCollector *)results {
    LogInfo(@"检测越狱文件...");

    // 越狱相关文件和目录
    NSArray *jailbreakPaths = @[
        @"/Applications/Cydia.app",
        @"/Applications/Sileo.app",
        @"/Applications/Zebra.app",
        @"/Applications/Installer.app",
        @"/Applications/SSH.app",
        @"/Applications/SSHTerm.app",
        @"/Applications/M terminal.app",
        @"/Library/MobileSubstrate/MobileSubstrate.dylib",
        @"/Library/MobileSubstrate/DynamicLibraries",
        @"/bin/bash",
        @"/bin/sh",
        @"/usr/bin/bash",
        @"/usr/bin/sh",
        @"/usr/sbin/sshd",
        @"/usr/bin/ssh",
        @"/usr/bin/sshd",
        @"/etc/apt",
        @"/etc/ssh/sshd_config",
        @"/private/var/lib/apt",
        @"/private/var/lib/cydia",
        @"/private/var/lib/silevo",
        @"/private/var/stash",
        @"/private/var/tmp/cydia.log",
        @"/private/var/cache/apt",
        @"/private/etc/apt/sources.list",
        @"/usr/lib/sbsettings",
        @"/usr/libexec/cydia",
        @"/usr/libexec/sftp-server",
        @"/usr/sbin/inject",
        @"/usr/sbin/sshd",
        @"/var/cache/apt",
        @"/var/lib/cydia",
        @"/var/log/syslog",
        @"/var/tmp/cydia.log",
        @"/sbin/su",
        @"/bin/su",
        @"/usr/bin/su",
        @"/usr/bin/vi",
        @"/usr/bin/nano",
        @"/var/bin/su",
        @"/var/bin/killall",
        @"/usr/bin/killall",
        @"/private/var/mobile/Library/SBSettings/Themes",
        @"/Library/MobileSubstrate/CydiaSubstrate.dylib",
        @"/usr/lib/TweakInject",
        @"/.bootstrapped_electra",
        @"/.installed_unc0ver",
    ];

    NSFileManager *fm = [NSFileManager defaultManager];
    NSMutableArray *foundPaths = [[NSMutableArray alloc] init];

    for (NSString *path in jailbreakPaths) {
        if ([fm fileExistsAtPath:path]) {
            [foundPaths addObject:path];
        }
    }

    // 额外检查：尝试写入沙盒外路径
    NSString *testPath = @"/private/jailbreak_test_file";
    [@@"test" writeToFile:testPath atomically:YES encoding:NSUTF8StringEncoding error:nil];
    if ([fm fileExistsAtPath:testPath]) {
        [foundPaths addObject:@"可写入沙盒外路径"];
        [fm removeItemAtPath:testPath error:nil];
    }

    // 检查符号链接
    NSArray *symlinks = @[
        @"/Applications",
        @"/Library/Ringtones",
        @"/Library/Wallpaper",
        @"/usr/include",
        @"/usr/libexec",
        @"/usr/share",
    ];

    for (NSString *path in symlinks) {
        NSDictionary *attrs = [fm attributesOfItemAtPath:path error:nil];
        if (attrs) {
            NSString *fileType = attrs[NSFileType];
            if ([fileType isEqualToString:NSFileTypeSymbolicLink]) {
                [foundPaths addObject:[NSString stringWithFormat:@"符号链接: %@", path]];
            }
        }
    }

    if (foundPaths.count > 0) {
        SecurityFinding *finding = [[SecurityFinding alloc] init];
        finding.tool = @"越狱检测器";
        finding.severity = SecuritySeverityCritical;
        finding.title = [NSString stringWithFormat:@"发现 %lu 个越狱文件",
                        (unsigned long)foundPaths.count];
        finding.desc = [NSString stringWithFormat:
            @"发现以下越狱相关文件:\n%@",
            [foundPaths componentsJoinedByString:@"\n"]];
        finding.evidence = [foundPaths componentsJoinedByString:@", "];
        finding.recommendation = @"设备已越狱，存在安全风险";
        [results addFinding:finding];
        return YES;
    }

    return NO;
}

/// 检测URL Scheme
+ (BOOL)checkURLSchemes:(ResultCollector *)results {
    LogInfo(@"检测URL Scheme...");

    // 检查越狱应用URL Scheme
    NSArray *schemes = @[
        @"cydia://",           // Cydia
        @"sileo://",           // Sileo
        @"zebra://",           // Zebra
        @"undecimus://",       // unc0ver
        @"filza://",           // Filza
        @"activator://",       // Activator
        @"appsanum://",        // Appsanum
    ];

    NSMutableArray *foundSchemes = [[NSMutableArray alloc] init];

    for (NSString *scheme in schemes) {
        NSURL *url = [NSURL URLWithString:scheme];
        if ([[UIApplication sharedApplication] canOpenURL:url]) {
            [foundSchemes addObject:scheme];
        }
    }

    if (foundSchemes.count > 0) {
        SecurityFinding *finding = [[SecurityFinding alloc] init];
        finding.tool = @"越狱检测器";
        finding.severity = SecuritySeverityHigh;
        finding.title = [NSString stringWithFormat:@"发现 %lu 个越狱URL Scheme",
                        (unsigned long)foundSchemes.count];
        finding.desc = [NSString stringWithFormat:
            @"发现以下越狱应用URL Scheme:\n%@",
            [foundSchemes componentsJoinedByString:@"\n"]];
        finding.evidence = [foundSchemes componentsJoinedByString:@", "];
        finding.recommendation = @"设备安装了越狱应用管理器";
        [results addFinding:finding];
        return YES;
    }

    return NO;
}

/// 检测系统文件访问
+ (BOOL)checkSystemFileAccess:(ResultCollector *)results {
    LogInfo(@"检测系统文件访问...");

    // 在非越狱设备上，沙盒应阻止访问系统文件
    NSArray *systemFiles = @[
        @"/etc/passwd",
        @"/etc/master.passwd",
        @"/etc/sudoers",
        @"/etc/fstab",
        @"/private/etc/passwd",
        @"/private/etc/master.passwd",
        @"/private/var/log/syslog",
        @"/private/var/log/asl/",
        @"/var/log/syslog",
    ];

    NSMutableArray *accessibleFiles = [[NSMutableArray alloc] init];

    for (NSString *path in systemFiles) {
        if ([[NSFileManager defaultManager] isReadableFileAtPath:path]) {
            [accessibleFiles addObject:path];
        }
    }

    if (accessibleFiles.count > 0) {
        SecurityFinding *finding = [[SecurityFinding alloc] init];
        finding.tool = @"越狱检测器";
        finding.severity = SecuritySeverityHigh;
        finding.title = @"沙盒被绕过，可访问系统文件";
        finding.desc = [NSString stringWithFormat:
            @"应用可以读取以下系统文件:\n%@",
            [accessibleFiles componentsJoinedByString:@"\n"]];
        finding.evidence = [accessibleFiles componentsJoinedByString:@", "];
        finding.recommendation = @"沙盒完整性被破坏，设备可能越狱";
        [results addFinding:finding];
        return YES;
    }

    return NO;
}

/// 检测沙盒完整性
+ (BOOL)checkSandboxIntegrity:(ResultCollector *)results {
    LogInfo(@"检测沙盒完整性...");

    // 尝试访问沙盒外的目录
    NSString *home = NSHomeDirectory();

    // 检查是否能访问其他应用的数据目录
    NSString *otherAppPath = @"/private/var/mobile/Containers/Data/Application";
    NSFileManager *fm = [NSFileManager defaultManager];

    if ([fm fileExistsAtPath:otherAppPath]) {
        // 尝试列举目录
        NSArray *contents = [fm contentsOfDirectoryAtPath:otherAppPath error:nil];
        if (contents && contents.count > 0) {
            SecurityFinding *finding = [[SecurityFinding alloc] init];
            finding.tool = @"越狱检测器";
            finding.severity = SecuritySeverityHigh;
            finding.title = @"沙盒完整性被破坏";
            finding.desc = [NSString stringWithFormat:
                @"可以列举其他应用的容器目录: %@ (%lu 个条目)",
                otherAppPath, (unsigned long)contents.count];
            finding.evidence = otherAppPath;
            finding.recommendation = @"沙盒应阻止跨应用目录访问";
            [results addFinding:finding];
            return YES;
        }
    }

    // 检查fork()是否可用
    // 非越狱设备上fork()应返回-1
    pid_t pid = fork();
    if (pid >= 0) {
        if (pid == 0) {
            // 子进程
            exit(0);
        } else {
            // 父进程
            int status;
            waitpid(pid, &status, 0);

            SecurityFinding *finding = [[SecurityFinding alloc] init];
            finding.tool = @"越狱检测器";
            finding.severity = SecuritySeverityHigh;
            finding.title = @"fork()可执行";
            finding.desc = @"应用可以调用fork()创建子进程，沙盒限制被绕过";
            finding.evidence = @"fork()成功返回";
            finding.recommendation = @"非越狱设备上fork()应被阻止";
            [results addFinding:finding];
            return YES;
        }
    }

    return NO;
}

/// 检测动态库注入
+ (BOOL)checkDylibInjection:(ResultCollector *)results {
    LogInfo(@"检测动态库注入...");

    uint32_t count = _dyld_image_count();
    NSMutableArray *suspiciousLibs = [[NSMutableArray alloc] init];

    for (uint32_t i = 0; i < count; i++) {
        const char *name = _dyld_get_image_name(i);
        if (name != NULL) {
            NSString *libName = [NSString stringWithUTF8String:name];
            NSString *libLower = [libName lowercaseString];

            // 检查可疑动态库
            if ([libLower containsString:@"substrate"] ||
                [libLower containsString:@"substitute"] ||
                [libLower containsString:@"ellekit"] ||
                [libLower containsString:@"tweakinject"] ||
                [libLower containsString:@"mobilesubstrate"] ||
                [libLower containsString:@"cycript"] ||
                [libLower containsString:@"frida"] ||
                [libLower containsString:@"gum"] ||
                [libLower containsString:@"inject"] ||
                [libLower containsString:@"hook"]) {
                [suspiciousLibs addObject:libName];
            }
        }
    }

    if (suspiciousLibs.count > 0) {
        SecurityFinding *finding = [[SecurityFinding alloc] init];
        finding.tool = @"越狱检测器";
        finding.severity = SecuritySeverityCritical;
        finding.title = [NSString stringWithFormat:@"检测到 %lu 个注入动态库",
                        (unsigned long)suspiciousLibs.count];
        finding.desc = [NSString stringWithFormat:
            @"检测到以下注入的动态库:\n%@",
            [suspiciousLibs componentsJoinedByString:@"\n"]];
        finding.evidence = [suspiciousLibs componentsJoinedByString:@", "];
        finding.recommendation = @"检查DYLD_INSERT_LIBRARIES环境变量";
        [results addFinding:finding];
        return YES;
    }

    return NO;
}

/// 检测SSH和Fork
+ (BOOL)checkSSHAndFork:(ResultCollector *)results {
    LogInfo(@"检测SSH和Fork...");

    BOOL detected = NO;

    // 检测SSH端口（22）
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock >= 0) {
        struct sockaddr_in addr;
        addr.sin_family = AF_INET;
        addr.sin_port = htons(22);
        addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);

        // 设置非阻塞
        int flags = fcntl(sock, F_GETFL, 0);
        fcntl(sock, F_SETFL, flags | O_NONBLOCK);

        connect(sock, (struct sockaddr *)&addr, sizeof(addr));

        fd_set fdset;
        FD_ZERO(&fdset);
        FD_SET(sock, &fdset);

        struct timeval timeout;
        timeout.tv_sec = 1;
        timeout.tv_usec = 0;

        int result = select(sock + 1, NULL, &fdset, NULL, &timeout);
        if (result > 0) {
            int so_error;
            socklen_t len = sizeof(so_error);
            getsockopt(sock, SOL_SOCKET, SO_ERROR, &so_error, &len);
            if (so_error == 0) {
                SecurityFinding *finding = [[SecurityFinding alloc] init];
                finding.tool = @"越狱检测器";
                finding.severity = SecuritySeverityHigh;
                finding.title = @"SSH端口开放";
                finding.desc = @"检测到本地端口22(SSH)开放，设备可能越狱";
                finding.evidence = @"端口22可连接";
                finding.recommendation = @"越狱设备通常安装SSH服务";
                [results addFinding:finding];
                detected = YES;
            }
        }
        close(sock);
    }

    // 检测SSH相关文件
    NSArray *sshPaths = @[
        @"/usr/sbin/sshd",
        @"/etc/ssh/sshd_config",
        @"/etc/ssh/ssh_config",
        @"/var/root/.ssh",
    ];

    for (NSString *path in sshPaths) {
        if ([[NSFileManager defaultManager] fileExistsAtPath:path]) {
            SecurityFinding *finding = [[SecurityFinding alloc] init];
            finding.tool = @"越狱检测器";
            finding.severity = SecuritySeverityHigh;
            finding.title = [NSString stringWithFormat:@"发现SSH文件: %@", path];
            finding.desc = [NSString stringWithFormat:@"SSH相关文件存在: %@", path];
            finding.evidence = path;
            finding.recommendation = @"SSH通常在越狱设备上安装";
            [results addFinding:finding];
            detected = YES;
        }
    }

    return detected;
}

@end

// ============================================================================
// 主函数
// ============================================================================

int main(int argc, const char *argv[]) {
    @autoreleasepool {
        printf("===========================================================\n");
        printf("  iOS Objective-C安全工具 v1.0\n");
        printf("  深层运行时安全检测与防护\n");
        printf("===========================================================\n\n");

        ResultCollector *results = [[ResultCollector alloc] init];

        // 1. Method Swizzling检测
        printf("[1] Method Swizzling检测\n");
        [MethodSwizzlingDetector detectAllSwizzling:results];

        // 2. Cycript检测
        printf("\n[2] Cycript检测\n");
        [CycriptDetector isCycriptRunning:results];
        [CycriptDetector detectCycriptInjection:results];
        [CycriptDetector detectCycriptPort:results];

        // 3. 运行时Hook检测
        printf("\n[3] 运行时Hook检测\n");
        [RuntimeHookDetector detectAllHooks:results];

        // 4. 反调试保护
        printf("\n[4] 反调试保护\n");
        [AntiDebugging applyAllProtections:results];

        // 5. 越狱检测
        printf("\n[5] 越狱检测\n");
        [JailbreakDetector isJailbroken:results];

        // 打印结果
        printf("\n");
        [results printSummary];
        printf("\n");
        [results printDetails];

        printf("\n===========================================================\n");
        printf("  免责声明: 仅用于授权的安全测试！\n");
        printf("===========================================================\n");
    }
    return 0;
}
