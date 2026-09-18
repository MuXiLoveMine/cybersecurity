# JTAG/SWD调试安全

### 9.1 调试接口风险

```
调试接口安全风险:

┌──────────────────────────────────────────────────────────┐
│ JTAG (Joint Test Action Group):                           │
│  - 4/5线接口: TCK, TMS, TDI, TDO, (TRST)                │
│  - 可读写所有内存                                         │
│  - 可注入并执行任意代码                                   │
│  - 可绕过安全启动                                         │
│  - 可读取加密密钥                                         │
├──────────────────────────────────────────────────────────┤
│ SWD (Serial Wire Debug):                                 │
│  - 2线接口: SWCLK, SWDIO                                 │
│  - 功能类似JTAG但引脚更少                                │
│  - 同样可完全控制设备                                     │
├──────────────────────────────────────────────────────────┤
│ UART (串口调试):                                          │
│  - TX, RX, GND                                           │
│  - 可能暴露调试Shell                                      │
│  - 可能输出敏感信息                                       │
└──────────────────────────────────────────────────────────┘

攻击场景:
1. 通过JTAG读取Flash内容 (固件提取)
2. 通过SWD注入代码 (代码执行)
3. 通过JTAG修改eFuse (绕过安全启动)
4. 通过UART获取Root Shell
5. 通过JTAG提取加密密钥
```

### 9.2 调试接口保护方案

```c
// ARM调试接口保护配置

// 1. eFuse/OTP保护 (硬件级, 不可逆)
// 在芯片生产时烧写eFuse
// - DBG_AP: 禁用调试端口
// - DBG_DP: 禁用调试端口 (数据)
// - SID: 设置安全ID
// - SEC: 启用安全启动

// 2. 运行时调试保护 (软件级)
// 通过时钟控制禁用调试
#include "stm32h7xx_hal.h"

void disable_debug_interface(void) {
    // STM32 HAL: 禁用调试接口
    // 注意: 禁用后可能无法再通过调试器连接!
    
    // 选项1: 完全禁用
    // HAL_DBGMCU_DisableDBGTamper();
    
    // 选项2: 仅在生产模式禁用
    FLASH_OBProgramInitTypeDef ob;
    
    HAL_FLASHEx_OBGetConfig(&ob);
    
    // 设置调试选项字节
    ob.RDPLevel = OB_RDP_LEVEL_1;  // 读保护级别1
    // ob.RDPLevel = OB_RDP_LEVEL_2; // 级别2: 永久禁用调试 (不可逆!)
    
    HAL_FLASH_OB_Unlock();
    HAL_FLASHEx_OBProgram(&ob);
    HAL_FLASH_OB_Lock();
    HAL_FLASH_OB_Launch();  // 重载选项字节
}

// 3. 调试接口认证
// 需要密码才能启用调试
#define DEBUG_PASSWORD 0xDEADBEEF

volatile uint32_t debug_unlock = 0;
volatile uint32_t debug_attempts = 0;

void Debug_Auth_Handler(void) {
    if (debug_attempts++ > 3) {
        // 超过3次尝试, 永久禁用调试
        disable_debug_interface();
        return;
    }
    
    if (debug_unlock == DEBUG_PASSWORD) {
        // 密码正确, 临时启用调试
        DBGMCU->CR |= DBGMCU_CR_DBG_STOP;
    }
}

// 4. 调试检测
// 检测调试器是否连接
bool is_debugger_attached(void) {
    // 方法1: 检查调试状态寄存器
    if (CoreDebug->DHCSR & CoreDebug_DHCSR_C_DEBUGEN_Msk) {
        return true;
    }
    
    // 方法2: 检查周期时间 (调试暂停会延长时间)
    uint32_t start = DWT->CYCCNT;
    __NOP();
    __NOP();
    __NOP();
    uint32_t elapsed = DWT->CYCCNT - start;
    
    if (elapsed > 100) {  // 正常应小于100个时钟周期
        return true;  // 可能在调试
    }
    
    return false;
}

// 5. 调试响应动作
void security_check(void) {
    if (is_debugger_attached()) {
        // 清除敏感数据
        memset(sensitive_buffer, 0, sizeof(sensitive_buffer));
        
        // 锁定安全功能
        lock_security_features();
        
        // 可选: 触发安全状态
        enter_safe_mode();
        
        // 可选: 记录事件
        log_security_event("DEBUG_DETECTED");
    }
}
```

### 9.3 UART安全

```bash
# UART安全加固

# 1. 禁用UART调试Shell
# 在bootloader中禁用:
# U-Boot环境变量
setenv bootdelay 0        # 无启动延迟
setenv bootstop off        # 禁止按键中断
setenv autostart yes       # 自动启动
saveenv

# 2. 禁用内核控制台
# 内核命令行参数
# console=ttyS0,115200 -> 移除console参数
# 或使用 console=/dev/null

# 3. 限制UART输出
# 在设备树中禁用UART
&uart1 {
    status = "disabled";
};

// 4. 串口密码保护
// 需要密码才能访问串口Shell
void serial_shell_init(void) {
    char password[32];
    printf("Serial Shell Access\n");
    printf("Password: ");
    
    if (!read_password(password, sizeof(password))) {
        printf("\nAuthentication failed\n");
        return;
    }
    
    if (verify_password(password)) {
        printf("\nWelcome\n");
        start_shell();
    } else {
        printf("\nAccess denied\n");
        delay_ms(3000);  // 延迟防止暴力
    }
}
```

---

---

## 📋 内容审核与补充建议

> 针对「JTAG/SWD调试安全」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

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
