# bhook框架

### 5.1 bhook简介

bhook（ByteHook）是字节跳动开源的Android PLT Hook框架，是xHook的继任者。相比xHook，bhook在性能、稳定性和功能上都有显著提升。

**项目地址：** https://github.com/bytedance/bhook

**核心特性：**
- **异步Hook**：支持异步刷新，不阻塞主线程
- **高性能**：优化了ELF解析算法，Hook速度更快
- **高稳定性**：完善的错误处理和回退机制
- **支持Hook链**：允许多个Hook同时作用于一个函数
- **线程安全**：内置线程安全机制
- **全面架构支持**：ARM/ARM64/x86/x86_64

### 5.2 bHook与xHook对比

| 特性 | xHook | bHook |
|------|-------|-------|
| 异步Hook | 不支持 | 支持 |
| Hook链 | 不支持 | 支持 |
| 稳定性 | 一般 | 更高（错误回退） |
| 性能 | 一般 | 更快 |
| 内存管理 | 手动 | 自动 |
| 架构支持 | ARM/ARM64/x86 | ARM/ARM64/x86/x86_64 |
| 维护状态 | 维护减少 | 活跃维护 |

### 5.3 bHook API详解

```c
#include "bytehook.h"

// 注册Hook（单个符号）
// param 1: 被Hook库的路径正则（NULL匹配所有）
// param 2: 被Hook函数名
// param 3: Hook回调函数
// param 4: 调用者地址（用于Hook链标识）
bytehook_stub_t bytehook_hook_single(
    const char *caller_path_regex,
    const char *callee_func_name,
    void *hook_func,
    void *arg);

// 注册Hook（所有匹配的符号）
bytehook_stub_t bytehook_hook_all(
    const char *caller_path_regex,
    const char *callee_func_name,
    void *hook_func,
    void *arg);

// 取消Hook
int bytehook_unhook(bytehook_stub_t stub);

// 取消所有Hook
int bytehook_unhook_all();

// 刷新（扫描新加载的库）
int bytehook_refresh(int async);

// 获取原始函数地址（用于Hook链中调用）
void *bytehook_get_orig(void *func, int *status);
```

### 5.4 使用示例

**Hook libc的malloc/free进行内存监控：**

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <malloc.h>
#include <android/log.h>
#include "bytehook.h"

#define TAG "BhookDemo"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, TAG, __VA_ARGS__)

// 全局统计
static size_t total_alloc = 0;
static size_t total_free = 0;
static int alloc_count = 0;

// Hook malloc
static void *hook_malloc(size_t size, void *arg) {
    // 获取原始函数并调用
    void *ptr = malloc(size);

    // 统计
    __sync_fetch_and_add(&total_alloc, size);
    __sync_fetch_and_add(&alloc_count, 1);

    // 大内存分配告警
    if (size > 1024 * 1024) {
        LOGI("[LargeAlloc] malloc(%zu) = %p", size, ptr);
    }

    return ptr;
}

// Hook free
static void hook_free(void *ptr, void *arg) {
    if (ptr) {
        __sync_fetch_and_add(&total_free, 1);
    }
    free(ptr);
}

// Hook calloc
static void *hook_calloc(size_t nmemb, size_t size, void *arg) {
    void *ptr = calloc(nmemb, size);
    __sync_fetch_and_add(&total_alloc, nmemb * size);
    LOGI("[calloc] nmemb=%zu, size=%zu, ptr=%p", nmemb, size, ptr);
    return ptr;
}

// 初始化内存监控
void init_memory_monitor() {
    // Hook所有库中的malloc
    bytehook_hook_single(NULL, "malloc",
                         (void *)hook_malloc, NULL);
    bytehook_hook_single(NULL, "free",
                         (void *)hook_free, NULL);
    bytehook_hook_single(NULL, "calloc",
                         (void *)hook_calloc, NULL);

    LOGI("Memory monitor initialized");
}

// 获取统计报告
void get_memory_report() {
    LOGI("=== Memory Monitor Report ===");
    LOGI("Total allocated: %zu bytes", total_alloc);
    LOGI("Total freed: %zu", total_free);
    LOGI("Alloc count: %d", alloc_count);
}
```

**使用Hook链进行多重Hook：**

```c
// 第一个Hook：记录调用
static void *hook_malloc_log(size_t size, void *arg) {
    LOGI("[Hook1] malloc(%zu)", size);
    // 调用Hook链中的下一个函数
    void *(*orig)(size_t) = bytehook_get_orig(
        (void *)hook_malloc_log, NULL);
    return orig ? orig(size) : malloc(size);
}

// 第二个Hook：大小限制
static void *hook_malloc_limit(size_t size, void *arg) {
    if (size > 100 * 1024 * 1024) {  // 限制100MB
        LOGI("[Hook2] Blocked large malloc(%zu)", size);
        return NULL;
    }
    void *(*orig)(size_t) = bytehook_get_orig(
        (void *)hook_malloc_limit, NULL);
    return orig ? orig(size) : malloc(size);
}

// 注册Hook链
void init_chained_hook() {
    // 先注册的Hook在外层
    bytehook_hook_single(NULL, "malloc",
                         (void *)hook_malloc_log, NULL);
    bytehook_hook_single(NULL, "malloc",
                         (void *)hook_malloc_limit, NULL);
}
```

### 5.5 异步Hook

bHook支持异步刷新机制，适用于需要Hook大量库的场景：

```c
// 异步刷新回调
static void on_refresh_done(int status, void *arg) {
    LOGI("Async refresh done, status=%d", status);
}

void init_async_hook() {
    // 注册Hook
    bytehook_hook_all(".*/libnative\\.so$", "open",
                      (void *)hook_open, NULL);

    // 异步刷新
    bytehook_refresh(1);  // 1 = async

    // 注册刷新完成回调
    bytehook_register_refresh_callback(on_refresh_done, NULL);
}
```

---

---

## 📋 内容审核与补充建议

> 针对「bhook框架」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

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
