# xHook框架

### 4.1 xHook简介

xHook是爱奇艺开源的PLT/GOT Hook框架，专注于Android平台Native层函数Hook。它通过修改ELF文件的PLT/GOT表实现函数拦截，具有轻量、稳定、易用的特点。

**项目地址：** https://github.com/iqiyi/xHook

**核心特性：**
- 纯C实现，无依赖
- 支持ARM/ARM64/x86/x86_64架构
- 基于PLT/GOT修改，稳定性高
- 提供简洁的API接口
- 支持批量注册和取消Hook

### 4.2 API详解

```c
// xHook核心API

// 注册Hook
// param 1: 被Hook库名的正则表达式（匹配.so文件名）
// param 2: 被Hook的函数名
// param 3: 新函数地址
// param 4: 输出原始函数地址
int xhook_register(const char *pathname_regex_str,
                    const char *symbol,
                    void *new_func,
                    void **proto_func);

// 取消Hook
int xhook_unregister(const char *pathname_regex_str,
                     const char *symbol);

// 取消所有Hook
int xhook_unregister_all();

// 刷新Hook（重新扫描已加载的库）
int xhook_refresh(int async);

// 清除缓存
void xhook_clear();

// 启用/禁用调试日志
void xhook_enable_debug(int flag);

// 启用/禁用签名校验
void xhook_enable_sigsegv_protect(int flag);
```

### 4.3 使用方法

**CMakeLists.txt配置：**
```cmake
cmake_minimum_required(VERSION 3.4.1)

# 添加xHook源码
add_library(xhook SHARED
    src/xh_core.c
    src/xh_core.h
    src/xh_iter.c
    src/xh_iter.h
    src/xh_elf.c
    src/xh_elf.h
    src/xh_log.c
    src/xh_log.h
    src/xh_util.c
    src/xh_util.h
    src/xh_version.h
)

# 链接依赖库
target_link_libraries(xhook log)
```

**Android.mk配置：**
```makefile
LOCAL_PATH := $(call my-dir)

include $(CLEAR_VARS)
LOCAL_MODULE := xhook
LOCAL_SRC_FILES := \
    xhook/src/xh_core.c \
    xhook/src/xh_iter.c \
    xhook/src/xh_elf.c \
    xhook/src/xh_util.c \
    xhook/src/xh_log.c
LOCAL_C_INCLUDES := $(LOCAL_PATH)/xhook/src
LOCAL_EXPORT_C_INCLUDES := $(LOCAL_PATH)/xhook/src
LOCAL_LDLIBS := -llog
include $(BUILD_SHARED_LIBRARY)
```

**实战示例 - Hook libc的open函数：**

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdarg.h>
#include "xhook.h"

// 原始函数指针
static int (*orig_open)(const char *pathname, int flags, ...) = NULL;

// Hook函数
static int hook_open(const char *pathname, int flags, ...) {
    // 提取可变参数
    mode_t mode = 0;
    if (flags & O_CREAT) {
        va_list args;
        va_start(args, flags);
        mode = va_arg(args, mode_t);
        va_end(args);
    }

    // 记录调用信息
    __android_log_print(ANDROID_LOG_INFO, "XhookDemo",
                        "open(%s, %d, %d)", pathname, flags, mode);

    // 调用原始函数
    int fd = orig_open ? orig_open(pathname, flags, mode)
                       : open(pathname, flags, mode);

    __android_log_print(ANDROID_LOG_INFO, "XhookDemo",
                        "open() returned fd=%d", fd);

    return fd;
}

// 初始化Hook
void init_hooks() {
    // Hook所有.so中的open函数
    if (xhook_register(".*/lib\\.so$", "open",
                        (void *)hook_open, (void **)&orig_open) != 0) {
        __android_log_print(ANDROID_LOG_ERROR, "XhookDemo",
                            "Failed to hook open()");
    }

    // 刷新
    xhook_refresh(0);
}

// JNI接口供Java层调用
JNIEXPORT void JNICALL
Java_com_example_security_NativeHook_initXHook(JNIEnv *env, jobject thiz) {
    init_hooks();
}
```

**Hook多个函数的批量示例：**

```c
// Hook libc中的多个文件操作函数
static int (*orig_open)(const char *, int, ...) = NULL;
static int (*orig_close)(int) = NULL;
static ssize_t (*orig_read)(int, void *, size_t) = NULL;
static ssize_t (*orig_write)(int, const void *, size_t) = NULL;

static int hook_open(const char *pathname, int flags, ...) {
    __android_log_print(ANDROID_LOG_INFO, "FileMonitor",
                        "[CALL] open(%s)", pathname);
    mode_t mode = 0;
    if (flags & O_CREAT) {
        va_list args;
        va_start(args, flags);
        mode = va_arg(args, mode_t);
        va_end(args);
    }
    return orig_open(pathname, flags, mode);
}

static int hook_close(int fd) {
    __android_log_print(ANDROID_LOG_INFO, "FileMonitor",
                        "[CALL] close(%d)", fd);
    return orig_close(fd);
}

static ssize_t hook_read(int fd, void *buf, size_t count) {
    ssize_t ret = orig_read(fd, buf, count);
    __android_log_print(ANDROID_LOG_INFO, "FileMonitor",
                        "[CALL] read(fd=%d, count=%zu) = %zd",
                        fd, count, ret);
    return ret;
}

static ssize_t hook_write(int fd, const void *buf, size_t count) {
    __android_log_print(ANDROID_LOG_INFO, "FileMonitor",
                        "[CALL] write(fd=%d, count=%zu)", fd, count);
    return orig_write(fd, buf, count);
}

void init_file_monitor() {
    xhook_register(".+\\.so$", "open",  (void *)hook_open,  (void **)&orig_open);
    xhook_register(".+\\.so$", "close", (void *)hook_close, (void **)&orig_close);
    xhook_register(".+\\.so$", "read",  (void *)hook_read,  (void **)&orig_read);
    xhook_register(".+\\.so$", "write", (void *)hook_write, (void **)&orig_write);
    xhook_refresh(0);
}
```

### 4.4 xHook使用注意事项

1. **符号匹配范围**：`pathname_regex_str`使用POSIX正则，需精确匹配库名
2. **线程安全**：Hook初始化应在程序启动早期完成，避免多线程竞争
3. **Hook顺序**：多次Hook同一符号时，需注意Hook链的顺序
4. **dlopen延迟加载**：对于运行时动态加载的库，需要调用`xhook_refresh()`重新扫描
5. **ART虚拟机内部函数**：xHook无法HookART内部函数（非PLT调用）

---

---

## 📋 内容审核与补充建议

> 针对「xHook框架」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

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
