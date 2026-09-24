# Xposed框架概述

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

---

