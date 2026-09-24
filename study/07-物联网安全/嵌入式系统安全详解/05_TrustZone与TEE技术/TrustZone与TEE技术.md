# TrustZone与TEE技术

### 5.1 TrustZone工作原理

```
TrustZone安全隔离:

┌──────────────────────────────────────────────────────────┐
│                  硬件隔离层                                │
│                                                           │
│  ┌─────────────────────┐  ┌─────────────────────────┐    │
│  │   正常世界          │  │   安全世界               │    │
│  │                     │  │                         │    │
│  │  ┌──────────┐      │  │  ┌──────────┐           │    │
│  │  │ REE OS   │      │  │  │ TEE OS   │           │    │
│  │  │ (Linux)  │      │  │  │ (OP-TEE)│           │    │
│  │  └──────────┘      │  │  └──────────┘           │    │
│  │  ┌──────────┐      │  │  ┌──────────┐           │    │
│  │  │ Apps     │      │  │  │ TA       │           │    │
│  │  │          │      │  │  │ (可信应用)│           │    │
│  │  └──────────┘      │  │  └──────────┘           │    │
│  │                     │  │                         │    │
│  │  非安全内存         │  │  安全内存                │    │
│  │  非安全外设         │  │  安全外设                │    │
│  │  非安全中断         │  │  安全中断                │    │
│  └─────────────────────┘  └─────────────────────────┘    │
│                                                           │
│           NS (Non-Secure) bit: 0=Secure, 1=Non-Secure    │
│                                                           │
│  ┌─────────────────────────────────────────────────┐     │
│  │              安全监控 (Secure Monitor)           │     │
│  │              EL3 / Monitor Mode                  │     │
│  │  - 世界切换                                    │     │
│  │  - 上下文保存/恢复                              │     │
│  │  - 安全中断路由                                │     │
│  └─────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────┘
```

### 5.2 OP-TEE架构

```
OP-TEE (Open Portable Trusted Execution Environment):

┌───────────────────────────────────────────────────────┐
│              用户空间 (User Space)                     │
│                                                        │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐        │
│  │ CA        │  │ CA        │  │ CA        │        │
│  │ (Client   │  │ (Client   │  │ (Client   │        │
│  │  App)     │  │  App)     │  │  App)     │        │
│  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘        │
│        │              │              │               │
│        └──────────────┼──────────────┘               │
│                       │                              │
│            ┌──────────┴──────────┐                   │
│            │ libteec (TEE Client │                   │
│            │  Library)           │                   │
│            └──────────┬──────────┘                   │
├────────────────────────┼──────────────────────────────┤
│              内核空间 (Kernel Space)                   │
│            ┌──────────┴──────────┐                   │
│            │ OP-TEE Driver        │                   │
│            │ (Linux Kernel Module)│                   │
│            └──────────┬──────────┘                   │
│                       │ SMC                            │
├────────────────────────┼──────────────────────────────┤
│           安全世界 (Secure World)                      │
│            ┌──────────┴──────────┐                   │
│            │ OP-TEE OS            │                   │
│            │ (Trusted OS)        │                   │
│            └──────────┬──────────┘                   │
│                       │                              │
│         ┌─────────────┼─────────────┐               │
│         │             │             │               │
│  ┌──────┴──────┐ ┌────┴─────┐ ┌────┴──────┐        │
│  │ TA          │ │ TA       │ │ TA        │        │
│  │ (Trusted    │ │ (Trusted │ │ (Trusted  │        │
│  │  App)       │ │  App)    │ │  App)     │        │
│  └─────────────┘ └──────────┘ └───────────┘        │
└───────────────────────────────────────────────────────┘
```

### 5.3 可信应用 (TA) 开发

```c
// OP-TEE Trusted Application 示例
// 文件: secure_storage_ta.c

#include <tee.h>
#include <tee_internal_api.h>
#include <tee_internal_api_extensions.h>

#define TA_NAME "secure_storage_ta"
#define STORAGE_ID 0x42535400  // BST0

// TA全局变量
typedef struct {
    TEE_ObjectHandle secure_object;
    uint32_t object_size;
} TA_Context;

static TA_Context ctx;

// TA创建时调用
TEE_Result TA_CreateEntryPoint(void) {
    memset(&ctx, 0, sizeof(ctx));
    return TEE_SUCCESS;
}

// TA销毁时调用
void TA_DestroyEntryPoint(void) {
    if (ctx.secure_object != TEE_HANDLE_NULL) {
        TEE_CloseAndPersistsObject(ctx.secure_object);
    }
}

// 开启会话
TEE_Result TA_OpenSessionEntryPoint(uint32_t param_types,
        TEE_Param params[4], void **sess_ctx) {
    return TEE_SUCCESS;
}

// 关闭会话
void TA_CloseSessionEntryPoint(void *sess_ctx) {
}

// 调用命令
TEE_Result TA_InvokeCommandEntryPoint(void *sess_ctx,
        uint32_t cmd_id, uint32_t param_types,
        TEE_Param params[4]) {
    
    switch (cmd_id) {
        case 1:  // 存储数据
            return store_secure_data(param_types, params);
        case 2:  // 读取数据
            return read_secure_data(param_types, params);
        case 3:  // 删除数据
            return delete_secure_data(param_types, params);
        case 4:  // 加密数据
            return encrypt_data(param_types, params);
        default:
            return TEE_ERROR_BAD_PARAMETERS;
    }
}

// 安全存储数据
static TEE_Result store_secure_data(uint32_t param_types,
        TEE_Param params[4]) {
    TEE_Result res;
    
    // 验证参数
    if (param_types != TEE_PARAM_TYPES(
            TEE_PARAM_TYPE_MEMREF_INPUT,
            TEE_PARAM_TYPE_NONE,
            TEE_PARAM_TYPE_NONE,
            TEE_PARAM_TYPE_NONE)) {
        return TEE_ERROR_BAD_PARAMETERS;
    }
    
    // 创建持久化对象
    res = TEE_CreatePersistentObject(
        TEE_STORAGE_PRIVATE,    // 存储类型
        &STORAGE_ID,            // 对象ID
        sizeof(STORAGE_ID),
        TEE_DATA_FLAG_ACCESS_READ | 
        TEE_DATA_FLAG_ACCESS_WRITE |
        TEE_DATA_FLAG_OVERWRITE,
        TEE_HANDLE_NULL,        // 属性
        params[0].memref.buffer, // 初始数据
        params[0].memref.size,   // 数据大小
        &ctx.secure_object       // 对象句柄
    );
    
    if (res != TEE_SUCCESS) {
        EMSG("Failed to create persistent object: 0x%x", res);
        return res;
    }
    
    ctx.object_size = params[0].memref.size;
    return TEE_SUCCESS;
}

// 加密数据 (使用硬件加速)
static TEE_Result encrypt_data(uint32_t param_types,
        TEE_Param params[4]) {
    TEE_OperationHandle op = TEE_HANDLE_NULL;
    TEE_Result res;
    
    // 分配加密操作 (AES-GCM)
    res = TEE_AllocateOperation(&op, TEE_ALG_AES_GCM,
                                 TEE_MODE_ENCRYPT, 256);
    if (res != TEE_SUCCESS) {
        return res;
    }
    
    // 设置密钥 (应从安全存储中获取)
    TEE_ObjectHandle key_handle;
    res = TEE_AllocateTransientObject(TEE_TYPE_AES, 256, &key_handle);
    if (res != TEE_SUCCESS) {
        TEE_FreeOperation(op);
        return res;
    }
    
    // ... 设置密钥和加密 ...
    
    TEE_FreeOperation(op);
    TEE_CloseObject(key_handle);
    
    return TEE_SUCCESS;
}
```

---

---

