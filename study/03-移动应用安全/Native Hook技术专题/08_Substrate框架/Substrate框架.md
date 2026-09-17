# Substrate框架

### 7.1 Cydia Substrate简介

Cydia Substrate（原名MobileSubstrate）是最早的移动平台Hook框架之一，最初为iOS越狱开发，后来推出了Android版本（Substrate for Android）。它提供了系统级的Hook能力，包括Java层和Native层。

**核心组件：**
- **Substrate**：核心Hook引擎
- **SubstrateBootstrap**：Zygote注入器
- **MSHookFunction**：Native层Inline Hook API
- **MS.hookMethod**：Java层Hook API

### 7.2 MSHookFunction

`MSHookFunction`是Substrate的Native层Hook核心API，使用Inline Hook技术：

```c
#include <substrate.h>

// MSHookFunction函数签名
// param 1: 目标函数地址
// param 2: 替换函数地址
// param 3: 输出原始函数指针
void MSHookFunction(void *symbol, void *replace, void **result);

// 示例：Hook libc的open函数
static int (*orig_open)(const char *pathname, int flags, ...) = NULL;

static int my_open(const char *pathname, int flags, ...) {
    // 获取可变参数
    mode_t mode = 0;
    if (flags & O_CREAT) {
        va_list args;
        va_start(args, flags);
        mode = va_arg(args, mode_t);
        va_end(args);
    }

    LOGI("Substrate: open(%s, %d, %d)", pathname, flags, mode);

    return orig_open(pathname, flags, mode);
}

// 初始化
void init_substrate_hook() {
    void *open_addr = dlsym(RTLD_DEFAULT, "open");
    MSHookFunction(open_addr,
                   (void *)my_open,
                   (void **)&orig_open);
}
```

### 7.3 Substrate for Android

在Android上使用Substrate需要Root权限和Substrate框架的安装：

**AndroidManifest.xml配置：**
```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.substratehook">

    <!-- 声明为Substrate扩展 -->
    <application>
        <meta-data android:name="com.saurik.substrate.meta"
                   android:value="com.example.substratehook.MainHook"/>
    </application>

    <!-- 需要注入的目标应用 -->
    <meta-data android:name="com.saurik.substrate.appid"
               android:value="com.target.app"/>
</manifest>
```

**Hook入口类：**
```java
package com.example.substratehook;

import com.saurik.substrate.MS;

public class MainHook {
    public static void initialize() {
        // Java层Hook
        MS.hookClassLoad("android.telephony.TelephonyManager",
            new MS.ClassLoadHook() {
                @Override
                public void classLoaded(Class<?> telephonyClass) {
                    // Hook getDeviceId
                    MS.hookMethod(telephonyClass,
                        "getDeviceId",
                        new MS.MethodAlterer() {
                        @Override
                        public Object invoked(Object obj,
                                               Object... args)
                                               throws Throwable {
                            // 返回自定义IMEI
                            return "123456789012345";
                        }
                    });
                }
            });
    }
}
```

### 7.4 Substrate与现代框架对比

| 特性 | Substrate | Frida | Dobby |
|------|-----------|-------|-------|
| 工作模式 | 需要框架安装 | 动态注入 | 库集成 |
| Root要求 | 需要 | 需要或Frida Server | 不需要 |
| 架构支持 | ARM/ARM64 | 全架构 | ARM/ARM64/x86 |
| Native Hook | MSHookFunction | Interceptor | DobbyHook |
| Java Hook | MS.hookMethod | Java API | 无 |
| 热重载 | 不支持 | 支持 | 不支持 |
| 跨平台 | iOS/Android | 全平台 | Android/iOS |
| 维护状态 | 停止维护 | 活跃 | 活跃 |

> 注意：Substrate目前已基本停止维护，在现代Android版本（Android 10+）上兼容性较差。建议优先使用Frida、Dobby或bHook等活跃维护的框架。

---

---

## 📋 内容审核与补充建议

> 针对「Substrate框架」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

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
