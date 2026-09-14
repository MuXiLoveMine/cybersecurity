# Xposed与Magisk框架详解

> 本文档深入剖析Xposed框架架构与模块开发、EdXposed/LSPosed在Android 10+的适配、Magisk架构与MagiskHide/Zygisk机制，以及检测与反检测技术的完整知识体系。

---

## 目录

- [一、Xposed框架概述](#一xposed框架概述)
  - [1.1 Xposed简介](#11-xposed简介)
  - [1.2 Xposed技术原理](#12-xposed技术原理)
  - [1.3 Zygote进程与Hook机制](#13-zygote进程与hook机制)
  - [1.4 Xposed框架架构](#14-xposed框架架构)
- [二、Xposed模块开发](#二xposed模块开发)
  - [2.1 开发环境搭建](#21-开发环境搭建)
  - [2.2 Hook方法](#22-hook方法)
  - [2.3 替换资源](#23-替换资源)
  - [2.4 模块开发实战](#24-模块开发实战)
  - [2.5 调试与日志](#25-调试与日志)
- [三、EdXposed与LSPosed](#三edxposed与lsposed)
  - [3.1 EdXposed框架](#31-edxposed框架)
  - [3.2 LSPosed框架](#32-lsposed框架)
  - [3.3 Riru与Zygisk对比](#33-riru与zygisk对比)
- [四、Magisk框架](#四magisk框架)
  - [4.1 Magisk简介](#41-magisk简介)
  - [4.2 Magisk架构](#42-magisk架构)
  - [4.3 Magisk启动流程](#43-magisk启动流程)
  - [4.4 Magisk模块系统](#44-magisk模块系统)
- [五、MagiskHide与Zygisk](#五magiskhide与zygisk)
  - [5.1 MagiskHide原理](#51-magiskhide原理)
  - [5.2 MagiskHide局限与废弃](#52-magiskhide局限与废弃)
  - [5.3 Zygisk机制](#53-zygisk机制)
  - [5.4 DenyList](#54-denylist)
- [六、检测与反检测](#六检测与反检测)
  - [6.1 Root检测技术](#61-root检测技术)
  - [6.2 Xposed检测技术](#62-xposed检测技术)
  - [6.3 Magisk检测技术](#63-magisk检测技术)
  - [6.4 反检测技术](#64-反检测技术)
- [七、实际应用场景](#七实际应用场景)
  - [7.1 安全研究](#71-安全研究)
  - [7.2 隐私保护](#72-隐私保护)
  - [7.3 功能增强](#73-功能增强)

---

## 一、Xposed框架概述

### 1.1 Xposed简介

Xposed是由rovo89开发的Android框架，允许在不修改APK的情况下改变系统和应用的行为。通过Hook机制，Xposed可以在运行时拦截和修改任意Java方法的执行，实现功能增强、安全研究、逆向分析等目的。

Xposed的核心优势：

- **非侵入式**：不需要修改APK文件，通过模块动态注入
- **系统级Hook**：基于Zygote进程，覆盖所有应用
- **灵活强大**：可以Hook任意Java方法、替换资源、修改返回值
- **模块化生态**：大量社区模块可用

### 1.2 Xposed技术原理

Xposed通过替换`/system/bin/app_process`来注入自己的代码到Zygote进程：

```
正常启动流程：
init -> zygote(/system/bin/app_process) -> app_process启动 -> 孵化应用进程

Xposed启动流程：
init -> zygote(Xposed替换的app_process) -> Xposed初始化 -> 注入Hook -> 孵化应用进程
```

Xposed的核心修改：

1. **替换app_process**：将系统的`/system/bin/app_process`替换为Xposed修改版
2. **注入XposedBridge**：在Zygote启动时加载XposedBridge.jar
3. **初始化Hook框架**：注册ART/Dalvik的Hook入口
4. **加载模块**：从Xposed Installer配置中读取已启用模块列表
5. **调用模块初始化**：在应用进程孵化前加载并初始化模块

```
Zygote启动序列
    |
    v
app_process (Xposed修改版)
    |
    +-- 加载XposedBridge.jar
    |       |
    |       +-- IXposedHookLoadPackage接口
    |       +-- IXposedHookZygoteInit接口
    |       +-- XposedHelpers工具类
    |
    +-- 读取启用模块列表
    |       |
    |       +-- 模块A (com.example.moduleA)
    |       +-- 模块B (com.example.moduleB)
    |       +-- ...
    |
    +-- fork应用进程
            |
            +-- 调用模块的handleLoadPackage()
            |       |
            |       +-- Hook目标方法
            |       +-- 修改行为
            |
            +-- 应用正常执行（被Hook的方法行为已改变）
```

### 1.3 Zygote进程与Hook机制

Zygote是Android系统中所有应用进程的父进程。理解Zygote的工作方式对理解Xposed至关重要。

**Zygote启动流程**

```
init进程
  |
  +-> service zygote /system/bin/app_process -Xzygote ...
        |
        +-> AppRuntime.start()
        |     |
        |     +-> 注册Zygote Socket (用于接收启动请求)
        |     +-> 预加载系统资源 (preload classes/resources)
        |     +-> 调用ZygoteInit.main()
        |
        +-> 等待启动请求 (runSelectLoop)
              |
              +-> 接收到启动请求
              +-> fork子进程 (应用进程)
                    |
                    +-> 子进程: 执行ActivityThread.main()
                    +-> 父进程: 继续等待
```

Xposed利用Zygote fork机制实现全局Hook：

- **Zygote Init阶段**：在`fork`之前Hook系统级方法，对所有应用生效
- **Post-fork阶段**：在应用进程fork后执行`handleLoadPackage`，针对特定应用Hook

**ART Hook机制**

Xposed在ART（Android Runtime）上的Hook实现：

```
正常方法调用：
  调用者 -> ArtMethod -> 编译的本地代码 (OAT) -> 执行

Xposed Hook后：
  调用者 -> ArtMethod -> Xposed的trampoline -> Hook处理代码 -> (可选)原始方法
```

Xposed通过修改ArtMethod结构实现Hook：

1. 将目标方法的ArtMethod替换为代理方法的ArtMethod
2. 代理方法跳转到XposedBridge的`handleHookedMethod`
3. `handleHookedMethod`调用注册的`beforeHookedMethod`和`afterHookedMethod`回调
4. 根据回调结果决定是否调用原始方法

### 1.4 Xposed框架架构

```
+----------------------------------+
|        Xposed Installer          |
|  - 模块管理                      |
|  - 框架安装/更新                   |
|  - 日志查看                      |
+----------------------------------+
                |
                v
+----------------------------------+
|        Xposed Framework          |
|  - app_process (替换版)           |
|  - XposedBridge.jar             |
|  - Xposed原生库 (libxposed)      |
+----------------------------------+
                |
        +-------+-------+
        |               |
        v               v
+---------------+   +---------------+
|  IXposedHook  |   | IXposedHook   |
|  LoadPackage  |   | ZygoteInit    |
| (应用级Hook)   |   | (系统级Hook)   |
+---------------+   +---------------+
        |               |
        v               v
+----------------------------------+
|         Xposed Modules           |
|  - 安全研究模块                   |
|  - 隐私保护模块                   |
|  - 功能增强模块                   |
|  - 逆向辅助模块                   |
+----------------------------------+
```

---

## 二、Xposed模块开发

### 2.1 开发环境搭建

**步骤1：创建Android项目**

```gradle
// build.gradle (app模块)
apply plugin: 'com.android.application'

android {
    compileSdkVersion 34
    defaultConfig {
        applicationId "com.example.xposedmodule"
        minSdkVersion 26
        targetSdkVersion 34
        versionCode 1
        versionName "1.0"
    }
}

dependencies {
    // Xposed API - 使用compileOnly，不打包进APK
    compileOnly 'de.robv.android.xposed:api:82'
}
```

如果无法从Maven获取Xposed API，可以手动添加：

```gradle
dependencies {
    compileOnly files('libs/XposedBridgeApi-82.jar')
}
```

**步骤2：配置AndroidManifest.xml**

```xml
<application
    android:label="My Xposed Module"
    android:icon="@mipmap/ic_launcher">

    <!-- 声明为Xposed模块 -->
    <meta-data
        android:name="xposedmodule"
        android:value="true" />

    <!-- 模块描述 -->
    <meta-data
        android:name="xposeddescription"
        android:value="示例Xposed模块 - 演示Hook技术" />

    <!-- 最低版本要求 -->
    <meta-data
        android:name="xposedminversion"
        android:value="82" />

    <!-- 模块作用范围配置页面 (可选) -->
    <meta-data
        android:name="xposedscope"
        android:resource="@array/xposed_scope" />
</application>
```

**步骤3：定义作用范围**

```xml
<!-- res/values/arrays.xml -->
<resources>
    <string-array name="xposed_scope">
        <item>com.android.systemui</item>
        <item>com.example.target</item>
    </string-array>
</resources>
```

**步骤4：创建模块入口**

```java
// src/main/assets/xposed_init
com.example.xposedmodule.MainHook
```

### 2.2 Hook方法

**基础Hook - before/after回调**

```java
package com.example.xposedmodule;

import de.robv.android.xposed.IXposedHookLoadPackage;
import de.robv.android.xposed.XC_MethodHook;
import de.robv.android.xposed.XposedBridge;
import de.robv.android.xposed.XposedHelpers;
import de.robv.android.xposed.callbacks.XC_LoadPackage;

public class MainHook implements IXposedHookLoadPackage {

    private static final String TAG = "MyXposedModule";

    @Override
    public void handleLoadPackage(XC_LoadPackage.LoadPackageParam lpparam) {
        // 只Hook特定应用
        if (!lpparam.packageName.equals("com.example.target")) {
            return;
        }

        XposedBridge.log(TAG + ": Loaded into " + lpparam.packageName);

        hookMethodExample(lpparam);
        hookConstructorExample(lpparam);
        hookAllOverloadsExample(lpparam);
    }

    /**
     * 基本方法Hook示例
     */
    private void hookMethodExample(XC_LoadPackage.LoadPackageParam lpparam) {
        try {
            // Hook String.contains方法
            XposedHelpers.findAndHookMethod(
                "java.lang.String",           // 类名
                lpparam.classLoader,          // 类加载器
                "contains",                   // 方法名
                CharSequence.class,           // 参数类型
                new XC_MethodHook() {
                    @Override
                    protected void beforeHookedMethod(MethodHookParam param) {
                        // 方法执行前调用
                        XposedBridge.log(TAG + ": before contains() called");
                        XposedBridge.log(TAG + ": arg = " + param.args[0]);

                        // 可以修改参数
                        // param.args[0] = "modified_value";

                        // 可以阻止原始方法执行并设置返回值
                        // param.setResult(false);
                    }

                    @Override
                    protected void afterHookedMethod(MethodHookParam param) {
                        // 方法执行后调用
                        XposedBridge.log(TAG + ": after contains() result = " + param.getResult());

                        // 可以修改返回值
                        // param.setResult(true);
                    }
                }
            );
        } catch (Throwable t) {
            XposedBridge.log(TAG + ": Hook failed: " + t.getMessage());
        }
    }

    /**
     * Hook构造函数示例
     */
    private void hookConstructorExample(XC_LoadPackage.LoadPackageParam lpparam) {
        try {
            Class<?> targetClass = XposedHelpers.findClass(
                "com.example.target.User", lpparam.classLoader);

            XposedHelpers.findAndHookConstructor(
                targetClass,
                String.class,   // name参数
                int.class,      // age参数
                new XC_MethodHook() {
                    @Override
                    protected void afterHookedMethod(MethodHookParam param) {
                        XposedBridge.log(TAG + ": User constructor called");
                        XposedBridge.log(TAG + ": name = " + param.args[0]);
                        XposedBridge.log(TAG + ": age = " + param.args[1]);
                    }
                }
            );
        } catch (Throwable t) {
            XposedBridge.log(TAG + ": Constructor hook failed: " + t.getMessage());
        }
    }

    /**
     * Hook所有重载版本
     */
    private void hookAllOverloadsExample(XC_LoadPackage.LoadPackageParam lpparam) {
        try {
            Class<?> targetClass = XposedHelpers.findClass(
                "com.example.target.NetworkClient", lpparam.classLoader);

            // Hook所有名为"sendData"的重载方法
            XposedBridge.hookAllMethods(
                targetClass,
                "sendData",
                new XC_MethodHook() {
                    @Override
                    protected void beforeHookedMethod(MethodHookParam param) {
                        // 记录所有参数
                        StringBuilder sb = new StringBuilder("sendData(");
                        for (int i = 0; i < param.args.length; i++) {
                            if (i > 0) sb.append(", ");
                            sb.append(param.args[i] != null ?
                                param.args[i].toString() : "null");
                        }
                        sb.append(")");
                        XposedBridge.log(TAG + ": " + sb.toString());
                    }
                }
            );
        } catch (Throwable t) {
            XposedBridge.log(TAG + ": Hook all overloads failed: " + t.getMessage());
        }
    }
}
```

**替换方法实现**

```java
private void replaceMethodExample(XC_LoadPackage.LoadPackageParam lpparam) {
    try {
        XposedHelpers.findAndHookMethod(
            "com.example.target.CryptoUtils",
            lpparam.classLoader,
            "encryptPassword",
            String.class,
            new XC_MethodReplacement() {
                @Override
                protected Object replaceHookedMethod(MethodHookParam param) {
                    // 完全替换原始方法
                    String password = (String) param.args[0];
                    XposedBridge.log(TAG + ": Original password: " + password);

                    // 返回自定义结果
                    return "HOOKED_" + password.hashCode();
                }
            }
        );
    } catch (Throwable t) {
        XposedBridge.log(TAG + ": Replace failed: " + t.getMessage());
    }
}
```

### 2.3 替换资源

Xposed可以替换目标应用的资源（布局、字符串、图片等）：

```java
public class ResourceHook implements IXposedHookLoadPackage {

    @Override
    public void handleLoadPackage(XC_LoadPackage.LoadPackageParam lpparam) {
        if (!lpparam.packageName.equals("com.example.target")) return;

        try {
            // 获取目标应用的资源
            String targetPackage = lpparam.packageName;
            Context targetContext = getTargetContext(targetPackage);

            if (targetContext != null) {
                // 替换字符串资源
                String originalString = lpparam.res.getString(
                    lpparam.res.getIdentifier("app_name", "string", targetPackage));
                XposedBridge.log("Original app name: " + originalString);

                // 修改布局
                // 需要在initZygote阶段使用XResources
            }
        } catch (Exception e) {
            XposedBridge.log("Resource hook failed: " + e.getMessage());
        }
    }

    private Context getTargetContext(String packageName) {
        try {
            // 通过ActivityThread获取目标Context
            Class<?> activityThreadClass = Class.forName("android.app.ActivityThread");
            Object activityThread = XposedHelpers.callStaticMethod(
                activityThreadClass, "currentActivityThread");
            // 实现略
            return null;
        } catch (Exception e) {
            return null;
        }
    }
}
```

**使用XResources替换资源（initZygote阶段）**

```java
public class SystemResourceHook implements IXposedHookZygoteInit {

    @Override
    public void initZygote(StartupParam startupParam) {
        // 在Zygote阶段替换系统资源
        XResources res = getXResources();

        // 替换系统UI状态栏布局
        XposedBridge.hookAllMethods(
            XResources.class,
            "getLayout",
            new XC_MethodHook() {
                @Override
                protected void afterHookedMethod(MethodHookParam param) {
                    // 资源替换逻辑
                }
            }
        );
    }

    private XResources getXResources() {
        // 获取XResources实例
        return null; // 实现略
    }
}
```

### 2.4 模块开发实战

**实战1：Hook登录验证**

```java
public class LoginBypassHook implements IXposedHookLoadPackage {

    @Override
    public void handleLoadPackage(XC_LoadPackage.LoadPackageParam lpparam) {
        if (!lpparam.packageName.equals("com.example.secureapp")) return;

        try {
            // Hook登录验证方法
            XposedHelpers.findAndHookMethod(
                "com.example.secureapp.LoginManager",
                lpparam.classLoader,
                "verifyCredentials",
                String.class,  // username
                String.class,  // password
                new XC_MethodHook() {
                    @Override
                    protected void beforeHookedMethod(MethodHookParam param) {
                        String username = (String) param.args[0];
                        String password = (String) param.args[1];
                        XposedBridge.log("Login attempt: " + username + "/" + password);

                        // 绕过验证，直接返回true
                        param.setResult(true);
                    }
                }
            );

            // HookisPremium方法
            XposedHelpers.findAndHookMethod(
                "com.example.secureapp.UserAccount",
                lpparam.classLoader,
                "isPremium",
                new XC_MethodHook() {
                    @Override
                    protected void afterHookedMethod(MethodHookParam param) {
                        param.setResult(true);
                    }
                }
            );
        } catch (Throwable t) {
            XposedBridge.log("Login bypass hook failed: " + t.getMessage());
        }
    }
}
```

**实战2：SSL Pinning绕过**

```java
public class SSLPinningBypassHook implements IXposedHookLoadPackage {

    @Override
    public void handleLoadPackage(XC_LoadPackage.LoadPackageParam lpparam) {
        // 对所有应用生效
        bypassSSL(lpparam);
    }

    private void bypassSSL(XC_LoadPackage.LoadPackageParam lpparam) {
        try {
            // Hook TrustManager验证
            Class<?> trustManagerClass = XposedHelpers.findClass(
                "javax.net.ssl.X509TrustManager", lpparam.classLoader);

            XposedHelpers.findAndHookMethod(
                "javax.net.ssl.X509TrustManager",
                lpparam.classLoader,
                "checkServerTrusted",
                java.security.cert.X509Certificate[].class,
                String.class,
                new XC_MethodHook() {
                    @Override
                    protected void beforeHookedMethod(MethodHookParam param) {
                        // 跳过证书验证
                        param.setResult(null);
                    }
                }
            );

            // Hook OkHttp CertificatePinner
            try {
                XposedHelpers.findAndHookMethod(
                    "okhttp3.CertificatePinner",
                    lpparam.classLoader,
                    "check",
                    String.class,
                    java.util.List.class,
                    new XC_MethodHook() {
                        @Override
                        protected void beforeHookedMethod(MethodHookParam param) {
                            param.setResult(null);
                        }
                    }
                );
            } catch (Throwable ignored) {}

        } catch (Throwable t) {
            // 某些类可能不存在，忽略
        }
    }
}
```

### 2.5 调试与日志

```java
// 使用XposedBridge.log输出日志
XposedBridge.log("Debug message");

// 也可以使用Android Log
android.util.Log.d("XposedModule", "Debug message");

// 查看日志
// adb logcat | grep Xposed
// 或在Xposed Installer中查看Logs
```

---

## 三、EdXposed与LSPosed

### 3.1 EdXposed框架

EdXposed（Enterprise Xposed）是针对Android 8.1+的Xposed替代方案，基于Riru和SandHook/YAHFA。

**EdXposed架构**

```
+-----------------------------+
|     EdXposed Manager        |
+-----------------------------+
              |
              v
+-----------------------------+
|        Riru (Riru模块)      |
|  - 注入Zygote进程             |
|  - 不修改系统分区              |
+-----------------------------+
              |
              v
+-----------------------------+
|    EdXposed Framework      |
|  - EdXposed Bridge          |
|  - SandHook / YAHFA        |
|  - 兼容Xposed API            |
+-----------------------------+
              |
              v
+-----------------------------+
|    Xposed Modules          |
|  (兼容原版Xposed模块)         |
+-----------------------------+
```

**EdXposed特点**

- 支持Android 8.1-10（部分支持11-13）
- 不需要修改/system分区（基于Riru注入Zygote）
- 兼容原版Xposed模块API
- 通过Magisk模块安装
- 已停止维护，被LSPosed取代

### 3.2 LSPosed框架

LSPosed是EdXposed的精神继承者，由LSPosed团队开发，支持Android 8.1+，是目前最活跃的Xposed框架实现。

**LSPosed架构**

```
+-----------------------------+
|     LSPosed Manager         |
|  - 模块管理（含作用域配置）    |
|  - 兼容性检测                 |
|  - 日志查看                  |
+-----------------------------+
              |
              v
+-----------------------------+
|    LSPosed Framework        |
|  - LSPlant (ART Hook引擎)   |
|  - 兼容Xposed API 82+       |
|  - 支持Zygisk和Riru         |
+-----------------------------+
              |
      +-------+-------+
      |               |
      v               v
+-----------+   +-----------+
|  Zygisk   |   |  Riru    |
| (推荐)    |   | (传统)    |
+-----------+   +-----------+
```

**LSPosed核心优势**

- **LSPlant Hook引擎**：自研的ART Hook引擎，支持Android 8.1-14+
- **Zygisk支持**：基于Zygisk，不修改系统分区
- **作用域管理**：精确控制模块作用于哪些应用
- **模块兼容性**：完全兼容原版Xposed模块
- **隐藏能力**：配合Zygisk DenyList隐藏自身
- **持续维护**：活跃的社区和更新

**LSPosed安装**

```
前提条件：
  - 已Root设备（Magisk或KernelSU）
  - Android 8.1+
  - Zygisk已启用（Magisk设置中）

安装步骤：
  1. 下载LSPosed Zygisk模块 (LSPosed-vX.X.X-xxxx-zygisk-release.zip)
  2. 在Magisk中安装模块
  3. 重启设备
  4. 安装LSPosed Manager
  5. 在LSPosed Manager中配置模块作用域
```

### 3.3 Riru与Zygisk对比

| 特性 | Riru | Zygisk |
|------|------|--------|
| 注入方式 | 替换/system/lib/libmemTrack.so | Magisk守护进程注入 |
| 系统修改 | 需要替换系统库 | 不修改系统库 |
| 兼容性 | 较好（但部分ROM不兼容） | 更广泛兼容 |
| 隐藏能力 | 较弱 | 更强（配合DenyList） |
| 性能开销 | 略高 | 较低 |
| 维护状态 | 逐渐被Zygisk取代 | 活跃维护 |

---

## 四、Magisk框架

### 4.1 Magisk简介

Magisk是目前最流行的Android Root解决方案，由topjohnwu开发。Magisk的核心理念是"无系统修改"（Systemless Root），通过在启动时挂载覆盖层来修改系统，不修改系统分区。

Magisk核心功能：

- **Root授权管理**：通过su和MagiskSU提供Root权限
- **无系统修改**：不修改/system分区，通过OverlayFS/mount覆盖
- **MagiskHide/DenyList**：隐藏Root状态
- **模块系统**：通过模块扩展功能
- **Zygisk**：在Zygote中注入代码

### 4.2 Magisk架构

```
+----------------------------------------------------+
|                    Magisk 架构                      |
+----------------------------------------------------+
|                                                    |
|  +-------------+    +-------------+               |
|  | Magisk Daemon|    | MagiskInit  |               |
|  | (守护进程)    |    | (启动初始化)  |               |
|  | - su授权     |    | - 挂载镜像    |               |
|  | - 模块加载   |    | - 初始化Root  |               |
|  | - Hide管理   |    | - Zygisk启动  |               |
|  +-------------+    +-------------+               |
|         |                  |                      |
|         v                  v                      |
|  +-------------+    +-------------+               |
|  | MagiskSU    |    | Magisk Image|               |
|  | (su二进制)   |    | (.img挂载)   |               |
|  +-------------+    +-------------+               |
|         |                  |                      |
|         |          +-------+-------+               |
|         |          |               |               |
|         |          v               v               |
|         |    +-----------+  +-----------+         |
|         |    |  Zygisk   |  |  Modules  |         |
|         |    | (注入引擎) |  | (功能模块) |         |
|         |    +-----------+  +-----------+         |
|         |          |               |              |
|         |          v               v              |
|         |    +-----------+  +-----------+         |
|         |    |DenyList   |  |MagiskHide |         |
|         |    |(隐藏Root)  |  |(已废弃)    |         |
|         |    +-----------+  +-----------+         |
|         |                                           |
|         v                                           |
|    +-----------+                                    |
|    | Magisk    |                                    |
|    | Manager   |                                    |
|    | (管理APP)  |                                    |
|    +-----------+                                    |
|                                                    |
+----------------------------------------------------+
```

### 4.3 Magisk启动流程

```
设备启动流程：

1. 内核启动
   |
2. init进程启动
   |
3. MagiskInit执行 (替换的/init或init.rc注入)
   |   - 挂载magisk.img到 /sbin/.magisk
   |   - 处理启动脚本
   |   - 启动Zygisk (如果启用)
   |
4. Zygote启动
   |   - Magisk通过Zygisk注入Zygote
   |   - DenyList配置生效
   |
5. 系统服务启动
   |   - Magisk Daemon启动
   |   - su二进制就绪
   |
6. 用户解锁
   |   - Magisk Manager可用
   |   - 模块完全加载
```

### 4.4 Magisk模块系统

Magisk模块是一个包含特定文件结构的ZIP包：

```
mymodule.zip
|-- module.prop          # 模块信息
|-- post-fs-data.sh      # post-fs-data阶段脚本
|-- service.sh           # late_start阶段脚本
|-- customize.sh         # 安装时脚本
|-- system/              # 覆盖系统文件
|   `-- ...
|-- system.prop          # 系统属性
|-- sepolicy.rule       # SELinux策略
`-- META-INF/            # 安装脚本
```

**module.prop示例**

```properties
id=my_module
name=My Custom Module
version=v1.0.0
versionCode=10000
author=Developer
description=This is a custom Magisk module
```

**service.sh示例**

```bash
#!/system/bin/sh
# 在late_start service阶段执行
# 网络已可用

# 启动自定义服务
while [ "$(getprop sys.boot_completed)" != "1" ]; do
    sleep 1
done

# 执行自定义逻辑
log -p i -t MyModule "Service started"
```

**创建简单Magisk模块**

```bash
# 创建模块目录结构
mkdir -p mymodule/system/app/MyApp
echo 'id=myapp' > mymodule/module.prop
echo 'name=My App' >> mymodule/module.prop
echo 'version=1.0' >> mymodule/module.prop
echo 'versionCode=1' >> mymodule/module.prop
echo 'author=Me' >> mymodule/module.prop
echo 'description=My custom module' >> mymodule/module.prop

# 添加文件
cp MyApp.apk mymodule/system/app/MyApp/MyApp.apk

# 打包
cd mymodule && zip -r ../mymodule.zip . && cd ..
```

---

## 五、MagiskHide与Zygisk

### 5.1 MagiskHide原理

MagiskHide是Magisk早期版本提供的隐藏Root状态的功能。其工作原理：

```
MagiskHide工作流程：

1. 监控进程启动
   - 通过/proc监控新进程
   - 读取目标应用的AndroidManifest判断是否需要隐藏

2. 解除挂载Magisk覆盖
   - 在目标进程的mount namespace中
   - 卸载magisk.img挂载的所有覆盖
   - 使/system恢复原样

3. 清理Root痕迹
   - 隐藏su二进制
   - 修改/proc/self/maps
   - 隐藏Magisk相关文件
```

**MagiskHide配置**

```
# 在Magisk Manager中配置
Settings -> MagiskHide -> 选择需要隐藏的应用

# 或通过命令行
magisk --hide com.example.app     # 添加到隐藏列表
magisk --hide --rm com.example.app # 从列表移除
magisk --hide --ls                  # 列出隐藏列表
```

### 5.2 MagiskHide局限与废弃

MagiskHide存在以下局限：

- **仅处理mount namespace**：不处理进程内的Root检测
- **性能开销**：需要监控所有新进程
- **容易被检测**：留下的痕迹可被高级检测发现
- **不支持Zygisk**：与Zygisk不兼容

从Magisk 24.0起，MagiskHide被移除，被Zygisk DenyList取代。

### 5.3 Zygisk机制

Zygisk是Magisk 24.0+引入的新机制，在Zygote进程内注入代码，实现更强大的功能。

**Zygisk工作原理**

```
Zygisk启动流程：

1. MagiskInit阶段
   |   - 加载libzygisk.so到Zygote进程
   |   - 注册Zygisk入口点
   |
2. Zygote fork前
   |   - Zygisk初始化
   |   - 加载所有Zygisk模块
   |   - 模块可以Hook系统级方法
   |
3. Zygote fork应用进程
   |   - 检查目标进程是否在DenyList中
   |   - 如果在DenyList中：
   |     - 在fork后立即清理Magisk痕迹
   |     - 卸载所有Magisk挂载
   |     - 隐藏Zygisk自身
   |   - 如果不在DenyList中：
   |     - 正常加载模块
   |     - 模块Hook生效
   |
4. 应用进程运行
       - DenyList应用看不到Root痕迹
       - 普通应用Root和模块正常工作
```

**Zygisk API（模块开发）**

```cpp
// Zygisk模块使用C/C++开发
#include "zygisk.hpp"

class MyModule : public zygisk::Module {
public:
    void onLoad(zygisk::Api *api, JNIEnv *env) override {
        this->api = api;
        this->env = env;
    }

    void preAppSpecialize(const zygisk::AppSpecializeArgs *args) override {
        // 应用进程fork前调用
        // 可以获取包名等信息
        const char *process = env->GetStringUTFChars(args->nice_name, nullptr);
        if (strcmp(process, "com.example.target") == 0) {
            // 对特定应用执行操作
        }
        env->ReleaseStringUTFChars(args->nice_name, process);
    }

    void postAppSpecialize(const zygisk::AppSpecializeArgs *args) override {
        // 应用进程fork后调用
        // 此时可以安全地Hook
    }

private:
    zygisk::Api *api;
    JNIEnv *env;
};

REGISTER_ZYGISK_MODULE(MyModule)
```

### 5.4 DenyList

DenyList是Zygisk时代的隐藏机制，替代了MagiskHide：

**DenyList配置**

```
# Magisk Manager中
Settings -> Zygisk -> Enable
Settings -> Enforce DenyList -> Enable
Configure -> 选择需要隐藏的应用

# 命令行
magisk --denylist add com.example.app
magisk --denylist rm com.example.app
magisk --denylist ls
magisk --denylist enable
magisk --denylist disable
```

**DenyList的作用**

```
DenyList中的进程：
  - Magisk挂载被卸载
  - su不可用
  - Magisk文件不可见
  - Zygisk模块不加载
  - 系统属性恢复默认
  - /proc/self/maps清理

非DenyList中的进程：
  - Root正常可用
  - Zygisk模块正常工作
  - Magisk功能完整
```

**DenyList配置清单**

```
建议添加到DenyList的应用：
  - 银行类：各银行APP
  - 支付类：支付宝、微信支付、Google Pay
  - DRM类：Netflix、Disney+、Prime Video
  - 游戏类：带有反作弊的游戏
  - 企业类：MDM应用、企业邮箱
  - 安全类：Google Play Integrity
```

---

## 六、检测与反检测

### 6.1 Root检测技术

应用使用多种方法检测Root状态：

**方法1：检查su二进制**

```java
public class RootDetector {
    private static final String[] SU_PATHS = {
        "/system/bin/su",
        "/system/xbin/su",
        "/sbin/su",
        "/su/bin/su",
        "/system/sbin/su",
        "/system/bin/.su",
        "/system/xbin/.su",
        "/data/local/xbin/su",
        "/data/local/bin/su",
        "/data/local/su",
        "/magisk/.core/bin/su",
        "/system/sd/xbin/su",
        "/dev/com.koushikdutta.superuser.daemon/"
    };

    public static boolean checkSuBinary() {
        for (String path : SU_PATHS) {
            if (new File(path).exists()) {
                return true;
            }
        }
        // 检查which命令
        try {
            Process process = Runtime.getRuntime().exec(new String[]{"which", "su"});
            BufferedReader reader = new BufferedReader(
                new InputStreamReader(process.getInputStream()));
            String line = reader.readLine();
            if (line != null && !line.isEmpty()) {
                return true;
            }
        } catch (Exception e) {
            // 忽略
        }
        return false;
    }
}
```

**方法2：检查Magisk文件**

```java
public static boolean checkMagiskFiles() {
    String[] magiskPaths = {
        "/sbin/.magisk",
        "/data/adb/magisk",
        "/data/adb/modules",
        "/cache/.magisk",
        "/dev/.magisk.unmount",
        "/sbin/.magisk.unblock",
        "/init.magisk.rc",
        "/data/adb/magisk.db",
        "/data/adb/magisk.img"
    };
    for (String path : magiskPaths) {
        if (new File(path).exists()) {
            return true;
        }
    }
    return false;
}
```

**方法3：检查系统属性**

```java
public static boolean checkSystemProperties() {
    String[] props = {
        "ro.build.selinux",
        "ro.debuggable",
        "service.adb.root",
        "ro.secure",
        "ro.boot.verifiedbootstate",
        "ro.boot.flash.locked",
        "ro.boot.vbmeta.device_state",
        "ro.boot.warranty_bit",
        "ro.warranty_bit",
        "ro.build.type",
        "ro.boot.veritymode"
    };

    for (String prop : props) {
        try {
            Class<?> cls = Class.forName("android.os.SystemProperties");
            Method get = cls.getMethod("get", String.class);
            String value = (String) get.invoke(null, prop);
            if (value != null) {
                if (prop.equals("ro.debuggable") && value.equals("1")) return true;
                if (prop.equals("ro.secure") && value.equals("0")) return true;
                if (prop.equals("ro.boot.verifiedbootstate") && value.equals("orange")) return true;
                if (prop.equals("ro.boot.flash.locked") && value.equals("0")) return true;
            }
        } catch (Exception e) {}
    }
    return false;
}
```

**方法4：检查挂载点**

```java
public static boolean checkMounts() {
    try {
        BufferedReader reader = new BufferedReader(
            new FileReader("/proc/self/mounts"));
        String line;
        while ((line = reader.readLine()) != null) {
            if (line.contains("magisk") || line.contains("MagiskManager") ||
                line.contains("/sbin/.core/mirror") || line.contains("/sbin/.magisk")) {
                return true;
            }
        }
        reader.close();
    } catch (Exception e) {}
    return false;
}
```

### 6.2 Xposed检测技术

**方法1：检查Xposed包名**

```java
public static boolean checkXposedPackage(Context context) {
    PackageManager pm = context.getPackageManager();
    try {
        pm.getPackageInfo("de.robv.android.xposed.installer",
            PackageManager.GET_ACTIVITIES);
        return true;
    } catch (PackageManager.NameNotFoundException e) {
        // Xposed Installer不存在
    }

    // 检查EdXposed
    try {
        pm.getPackageInfo("org.meowcat.edxposed.manager",
            PackageManager.GET_ACTIVITIES);
        return true;
    } catch (PackageManager.NameNotFoundException e) {}

    // 检查LSPosed
    try {
        pm.getPackageInfo("org.lsposed.manager",
            PackageManager.GET_ACTIVITIES);
        return true;
    } catch (PackageManager.NameNotFoundException e) {}

    return false;
}
```

**方法2：检查Xposed类**

```java
public static boolean checkXposedClasses() {
    try {
        Class.forName("de.robv.android.xposed.XposedBridge");
        return true;
    } catch (ClassNotFoundException e) {
        // 正常
    }

    try {
        Class.forName("de.robv.android.xposed.XC_MethodHook");
        return true;
    } catch (ClassNotFoundException e) {}

    return false;
}
```

**方法3：检查调用栈**

```java
public static boolean checkStackTrace() {
    try {
        throw new Exception("stack trace check");
    } catch (Exception e) {
        for (StackTraceElement element : e.getStackTrace()) {
            if (element.getClassName().contains("de.robv.android.xposed") ||
                element.getClassName().contains("org.lsposed") ||
                element.getClassName().contains("org.meowcat.edxposed")) {
                return true;
            }
            if (element.getClassName().contains("XposedBridge") ||
                element.getClassName().contains("XposedHelpers")) {
                return true;
            }
        }
    }
    return false;
}
```

**方法4：检查native库**

```java
public static boolean checkNativeLibs() {
    try {
        BufferedReader reader = new BufferedReader(
            new FileReader("/proc/self/maps"));
        String line;
        while ((line = reader.readLine()) != null) {
            if (line.contains("xposed") || line.contains("XposedBridge") ||
                line.contains("libxposed_art") || line.contains("riru") ||
                line.contains("zygisk")) {
                return true;
            }
        }
        reader.close();
    } catch (Exception e) {}
    return false;
}
```

### 6.3 Magisk检测技术

**方法1：SafetyNet / Play Integrity API**

```java
// Google Play Integrity API检测（SafetyNet的替代）
// 需要Google Play服务支持
public void checkPlayIntegrity(Context context) {
    IntegrityManager manager = IntegrityManagerFactory.create(context);
    IntegrityTokenRequest request = IntegrityTokenRequest.builder()
        .setNonce("nonce")
        .build();

    manager.requestIntegrityToken(request)
        .addOnSuccessListener(response -> {
            // 发送token到服务器验证
            verifyTokenOnServer(response.token());
        })
        .addOnFailureListener(e -> {
            // Play服务不可用或设备不合规
            handleNonCompliantDevice();
        });
}
```

**方法2：检测Magisk环境**

```java
public static boolean detectMagisk() {
    // 检查magisk数据库
    File magiskDb = new File("/data/adb/magisk.db");
    if (magiskDb.exists()) return true;

    // 检查magisk socket
    File magiskSocket = new File("/dev/socket/magisk");
    if (magiskSocket.exists()) return true;

    // 检查magisk属性
    try {
        Class<?> cls = Class.forName("android.os.SystemProperties");
        Method get = cls.getMethod("get", String.class);
        String magiskVer = (String) get.invoke(null, "ro.magisk.version");
        if (magiskVer != null && !magiskVer.isEmpty()) return true;
    } catch (Exception e) {}

    // 检查zygisk
    try {
        BufferedReader reader = new BufferedReader(
            new FileReader("/proc/self/maps"));
        String line;
        while ((line = reader.readLine()) != null) {
            if (line.contains("libzygisk") || line.contains("zygisk")) {
                return true;
            }
        }
        reader.close();
    } catch (Exception e) {}

    return false;
}
```

### 6.4 反检测技术

**Magisk隐藏配置**

```
1. 启用Zygisk
   Magisk Manager -> Settings -> Zygisk -> Enable

2. 配置DenyList
   Magisk Manager -> Settings -> Enforce DenyList -> Enable
   Configure -> 勾选需要隐藏的应用

3. 隐藏Magisk Manager
   Magisk Manager -> Settings -> Hide Magisk Manager
   (将Magisk Manager重新打包为随机包名)

4. 配置随机包名
   Magisk Manager -> Settings -> Restore Magisk Manager (隐藏后)

5. 使用Shamiko模块（更强大的隐藏）
   安装Shamiko Magisk模块
   配置白名单模式或黑名单模式
```

**Shamiko模块**

Shamiko是一个基于Zygisk的高级隐藏模块，提供比DenyList更强的隐藏：

```
Shamiko配置：
  - 白名单模式：DenyList中的应用被隐藏
  - 黑名单模式：DenyList中的应用不隐藏，其他全部隐藏

安装：
  1. 下载Shamiko-vX.X.X-release.zip
  2. Magisk Manager -> Modules -> Install from storage
  3. 选择Shamiko ZIP文件
  4. 重启设备
```

**反Xposed检测 - Hook检测函数**

```java
// 使用Xposed Hook掉检测函数
public class AntiDetectionHook implements IXposedHookLoadPackage {
    @Override
    public void handleLoadPackage(XC_LoadPackage.LoadPackageParam lpparam) {
        // Hook RootDetector使其返回false
        XposedHelpers.findAndHookMethod(
            "com.example.app.RootDetector",
            lpparam.classLoader,
            "checkSuBinary",
            XC_MethodReplacement.returnConstant(false)
        );

        // Hook Xposed检测
        XposedHelpers.findAndHookMethod(
            "com.example.app.SecurityChecker",
            lpparam.classLoader,
            "checkXposedClasses",
            XC_MethodReplacement.returnConstant(false)
        );

        // Hook PackageManager隐藏Xposed包
        XposedHelpers.findAndHookMethod(
            "android.app.ApplicationPackageManager",
            lpparam.classLoader,
            "getPackageInfo",
            String.class, int.class,
            new XC_MethodHook() {
                @Override
                protected void beforeHookedMethod(MethodHookParam param) {
                    String pkg = (String) param.args[0];
                    if (pkg.contains("xposed") || pkg.contains("lsposed") ||
                        pkg.contains("edxposed") || pkg.contains("magisk")) {
                        param.setThrowable(
                            new PackageManager.NameNotFoundException());
                    }
                }
            }
        );
    }
}
```

---

## 七、实际应用场景

### 7.1 安全研究

**应用漏洞挖掘**

```java
// Hook加密方法查看明文
public class CryptoAnalysisHook implements IXposedHookLoadPackage {
    @Override
    public void handleLoadPackage(XC_LoadPackage.LoadPackageParam lpparam) {
        // Hook AES加密方法
        try {
            XposedHelpers.findAndHookMethod(
                "javax.crypto.Cipher",
                lpparam.classLoader,
                "doFinal",
                byte[].class,
                new XC_MethodHook() {
                    @Override
                    protected void afterHookedMethod(MethodHookParam param) {
                        byte[] input = (byte[]) param.args[0];
                        byte[] output = (byte[]) param.getResult();
                        XposedBridge.log("AES Input: " + bytesToHex(input));
                        XposedBridge.log("AES Output: " + bytesToHex(output));
                    }
                }
            );
        } catch (Throwable t) {}

        // HookSharedPreferences查看存储数据
        try {
            XposedHelpers.findAndHookMethod(
                "android.app.SharedPreferencesImpl",
                lpparam.classLoader,
                "getAll",
                new XC_MethodHook() {
                    @Override
                    protected void afterHookedMethod(MethodHookParam param) {
                        Map<String, ?> map = (Map<String, ?>) param.getResult();
                        for (Map.Entry<String, ?> entry : map.entrySet()) {
                            XposedBridge.log(
                                "SharedPref: " + entry.getKey() +
                                " = " + entry.getValue());
                        }
                    }
                }
            );
        } catch (Throwable t) {}
    }
}
```

**网络流量分析**

```java
// Hook网络请求查看数据
public class NetworkAnalysisHook implements IXposedHookLoadPackage {
    @Override
    public void handleLoadPackage(XC_LoadPackage.LoadPackageParam lpparam) {
        // Hook HttpURLConnection
        try {
            XposedHelpers.findAndHookMethod(
                "java.net.URL",
                lpparam.classLoader,
                "openConnection",
                new XC_MethodHook() {
                    @Override
                    protected void afterHookedMethod(MethodHookParam param) {
                        URL url = (URL) param.thisObject;
                        XposedBridge.log("HTTP Request: " + url.toString());
                    }
                }
            );
        } catch (Throwable t) {}

        // Hook OkHttp
        try {
            XposedHelpers.findAndHookMethod(
                "okhttp3.RealCall",
                lpparam.classLoader,
                "execute",
                new XC_MethodHook() {
                    @Override
                    protected void beforeHookedMethod(MethodHookParam param) {
                        Object request = XposedHelpers.callMethod(
                            param.thisObject, "request");
                        String url = XposedHelpers.callMethod(
                            XposedHelpers.callMethod(request, "url"),
                            "toString").toString();
                        XposedBridge.log("OkHttp Request: " + url);
                    }
                }
            );
        } catch (Throwable t) {}
    }
}
```

### 7.2 隐私保护

```java
// 隐私保护模块 - 阻止应用获取真实信息
public class PrivacyGuardHook implements IXposedHookLoadPackage {
    @Override
    public void handleLoadPackage(XC_LoadPackage.LoadPackageParam lpparam) {
        // 拦截设备ID获取
        try {
            XposedHelpers.findAndHookMethod(
                "android.provider.Settings$Secure",
                lpparam.classLoader,
                "getString",
                ContentResolver.class, String.class,
                new XC_MethodHook() {
                    @Override
                    protected void afterHookedMethod(MethodHookParam param) {
                        if (param.args[1].equals("android_id")) {
                            param.setResult("0000000000000000"); // 伪造ID
                        }
                    }
                }
            );
        } catch (Throwable t) {}

        // 拦截位置信息
        try {
            XposedHelpers.findAndHookMethod(
                "android.location.Location",
                lpparam.classLoader,
                "getLatitude",
                new XC_MethodHook() {
                    @Override
                    protected void afterHookedMethod(MethodHookParam param) {
                        param.setResult(0.0); // 伪造纬度
                    }
                }
            );
            XposedHelpers.findAndHookMethod(
                "android.location.Location",
                lpparam.classLoader,
                "getLongitude",
                new XC_MethodHook() {
                    @Override
                    protected void afterHookedMethod(MethodHookParam param) {
                        param.setResult(0.0); // 伪造经度
                    }
                }
            );
        } catch (Throwable t) {}

        // 拦截通讯录读取
        try {
            XposedHelpers.findAndHookMethod(
                "android.content.ContentResolver",
                lpparam.classLoader,
                "query",
                Uri.class, String[].class, String.class,
                String[].class, String.class,
                new XC_MethodHook() {
                    @Override
                    protected void beforeHookedMethod(MethodHookParam param) {
                        Uri uri = (Uri) param.args[0];
                        if (uri.toString().contains("contacts")) {
                            // 返回空Cursor
                            param.setResult(null);
                        }
                    }
                }
            );
        } catch (Throwable t) {}
    }
}
```

### 7.3 功能增强

```java
// 功能增强模块 - 解锁高级功能
public class FeatureUnlockHook implements IXposedHookLoadPackage {
    @Override
    public void handleLoadPackage(XC_LoadPackage.LoadPackageParam lpparam) {
        if (!lpparam.packageName.equals("com.example.app")) return;

        // 解锁Pro功能
        try {
            XposedHelpers.findAndHookMethod(
                "com.example.app.LicenseManager",
                lpparam.classLoader,
                "isProUser",
                XC_MethodReplacement.returnConstant(true)
            );
        } catch (Throwable t) {}

        // 移除广告
        try {
            XposedHelpers.findAndHookMethod(
                "com.example.app.AdManager",
                lpparam.classLoader,
                "showAd",
                XC_MethodReplacement.returnConstant(null)
            );
        } catch (Throwable t) {}
    }
}
```

---

> **参考资源**
>
> - Xposed Framework - github.com/rovo89/Xposed
> - LSPosed Framework - github.com/LSPosed/LSPosed
> - Magisk - github.com/topjohnwu/Magisk
> - LSPlant (ART Hook引擎) - github.com/LSPosed/LSPlant
> - Shamiko (Zygisk隐藏模块) - github.com/LSPosed/LSPosed.github.io
> - Google Play Integrity API - developer.android.com
