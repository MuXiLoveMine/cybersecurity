# Dobby框架

### 6.1 Dobby简介

Dobby是一个跨架构的Inline Hook框架，支持ARM/ARM64/x86/x86_64架构。与xHook/bHook的PLT/GOT Hook不同，Dobby使用Inline Hook技术，可以Hook任意函数（包括内部函数），功能更强大。

**项目地址：** https://github.com/jmpews/Dobby

**核心特性：**
- **Inline Hook**：直接修改函数入口指令，可Hook任意函数
- **跨架构支持**：ARM/Thumb/ARM64/x86/x86_64
- **指令重定位**：内置完整的指令重定位引擎
- **Near Trampoline**：支持近距离跳转，减少跳转开销
- **Function Inline Hook**：支持完全内联Hook
- **兼容性好**：可与Frida、xHook等框架共存

### 6.2 Dobby API

```c
#include "dobby.h"

// Hook函数（核心API）
// param 1: 目标函数地址
// param 2: 新函数地址
// param 3: 输出原始函数地址（用于调用原始逻辑）
int DobbyHook(void *address,
              void *replace_call,
              void **origin_call);

// 取消Hook
int DobbyUnHook(void *address);

// 获取指令地址（用于Hook函数中间）
void *DobbyInstructionAddress(void *address);

// 注册调试回调
void DobbyDebugCallback(void (*callback)(void *address, const char *info));
```

### 6.3 使用示例

**Hook Native加密函数：**

```c
#include <stdio.h>
#include <string.h>
#include <android/log.h>
#include "dobby.h"

#define TAG "DobbyDemo"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, TAG, __VA_ARGS__)

// 假设这是目标应用中的加密函数
// 签名: int encrypt_data(const char *input, int input_len, char *output, int *output_len)
typedef int (*encrypt_data_t)(const char *, int, char *, int *);

static encrypt_data_t orig_encrypt = NULL;

// Hook函数
static int hook_encrypt_data(const char *input, int input_len,
                              char *output, int *output_len) {
    LOGI("[Hook] encrypt_data called");
    LOGI("[Hook] input_len=%d", input_len);

    // 打印输入数据
    if (input && input_len > 0) {
        char hex_buf[1024] = {0};
        for (int i = 0; i < input_len && i < 512; i++) {
            sprintf(hex_buf + i * 2, "%02x", (unsigned char)input[i]);
        }
        LOGI("[Hook] input(hex): %s", hex_buf);
    }

    // 调用原始函数
    int ret = orig_encrypt(input, input_len, output, output_len);

    // 打印输出数据
    if (output && output_len && *output_len > 0) {
        char hex_buf[1024] = {0};
        for (int i = 0; i < *output_len && i < 512; i++) {
            sprintf(hex_buf + i * 2, "%02x", (unsigned char)output[i]);
        }
        LOGI("[Hook] output(hex): %s", hex_buf);
    }
    LOGI("[Hook] encrypt_data returned %d", ret);

    return ret;
}

// 通过JNI获取目标函数地址并Hook
JNIEXPORT void JNICALL
Java_com_example_security_NativeHook_initDobby(JNIEnv *env, jobject thiz,
                                                jlong target_addr) {
    LOGI("Target function address: 0x%llx", target_addr);

    int ret = DobbyHook((void *)target_addr,
                        (void *)hook_encrypt_data,
                        (void **)&orig_encrypt);

    if (ret == 0) {
        LOGI("Dobby hook success!");
    } else {
        LOGI("Dobby hook failed! ret=%d", ret);
    }
}
```

**通过符号名Hook（需dlsym）：**

```c
#include <dlfcn.h>

// 通过符号名Hook
void hook_by_symbol(const char *lib_name, const char *symbol) {
    void *handle = dlopen(lib_name, RTLD_NOW);
    if (!handle) {
        LOGI("Failed to open %s: %s", lib_name, dlerror());
        return;
    }

    void *target = dlsym(handle, symbol);
    if (!target) {
        LOGI("Symbol %s not found", symbol);
        return;
    }

    LOGI("Found %s at %p", symbol, target);

    // 使用Dobby Hook
    int ret = DobbyHook(target,
                        (void *)hook_encrypt_data,
                        (void **)&orig_encrypt);

    LOGI("Dobby hook %s: %s", symbol, ret == 0 ? "success" : "failed");
}
```

**Hook libc的syscall wrapper：**

```c
// Hook ptrace（反调试）
typedef long (*orig_ptrace_t)(int request, pid_t pid,
                               void *addr, void *data);
static orig_ptrace_t orig_ptrace = NULL;

static long hook_ptrace(int request, pid_t pid,
                         void *addr, void *data) {
    LOGI("[Anti-Debug] ptrace(%d, %d) intercepted!", request, pid);
    // 返回0表示成功，欺骗反调试检测
    return 0;
}

void init_anti_debug_bypass() {
    void *ptrace_addr = dlsym(RTLD_DEFAULT, "ptrace");
    if (ptrace_addr) {
        DobbyHook(ptrace_addr,
                  (void *)hook_ptrace,
                  (void **)&orig_ptrace);
        LOGI("ptrace hooked at %p", ptrace_addr);
    }
}
```

### 6.4 Dobby编译集成

**CMakeLists.txt：**
```cmake
cmake_minimum_required(VERSION 3.4.1)

# 添加Dobby子模块
add_subdirectory(Dobby)

# 你的库
add_library(native_hook SHARED
    native_hook.cpp)

# 链接Dobby
target_link_libraries(native_hook
    dobby
    log
    dl)
```

---

---

## 📋 内容审核与补充建议

> 针对「Dobby框架」部分的内容审核结果：

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
