# Windows动态调试

### 2.1 x64dbg/WinDbg使用

**x64dbg** 是当前最流行的开源 Windows 用户态调试器，是 OllyDbg 的现代继任者，支持 x86/x64。它集成反汇编、内存查看、堆栈跟踪、脚本引擎等功能。

x64dbg 的基本操作流程：

```
1. File → Open / Attach       打开或附加目标程序
2. F9      运行               程序全速执行
3. F8      Step Over          单步步过（不进入函数）
4. F7      Step Into           单步步入（进入函数）
5. F2      Toggle Breakpoint  在当前指令设置/取消断点
6. Ctrl+F9 Execute till Return 运行到函数返回
```

**WinDbg** 既支持用户态也支持内核态调试，是调试 Windows 内核和驱动的首选工具。常用命令：

```
!process 0 0              // 列出所有进程（内核模式）
!devnode 0 1              // 设备树
bp nt!NtCreateFile        // 在内核函数设断点
!process 0 7 /m image.exe // 查看指定进程详细信息
.reload /f                // 强制重新加载符号
!analyze -v               // 自动分析崩溃
dt nt!_EPROCESS           // 显示结构体
```

### 2.2 断点类型

断点是动态调试的核心机制，不同类型的断点适用于不同场景。

**软件断点（INT3 Breakpoint）**：将目标指令首字节替换为 `0xCC`（INT3），CPU 执行到此处触发异常，调试器捕获。

```
原始指令:  55              push ebp
断点设置后:CC              int 3   ← 首字节被替换为0xCC
```

- 优点：数量不限、设置简单。
- 缺点：修改内存，容易被反调试检测（CRC 自校验）。

**硬件断点（Hardware Breakpoint）**：使用 CPU 的调试寄存器（DR0-DR3）设置断点，不修改内存。

```
DR0-DR3: 断点地址（最多4个硬件断点）
DR7:     控制寄存器（断点类型/长度/启用）
```

x64dbg 设置硬件断点：
```
bphws 0x00401000        // 硬件执行断点
bphws 0x00405000,r,1    // 硬件读取断点，长度1字节
bphws 0x00405000,w,4    // 硬件写入断点，长度4字节
```

- 优点：不修改内存、速度快、可设内存访问断点。
- 缺点：最多4个。

**内存断点（Memory Breakpoint）**：设置页面保护属性，访问触发异常。

```
bpm 0x00401000,1,a      // 内存访问断点
bpm 0x00401000,1,w      // 内存写入断点
```

**条件断点**：满足条件才中断，避免频繁断下。

```
bp 0x00401000
bpcnd 0x00401000,"[eax]==0x1234"     // 条件断点：内存[eax]等于0x1234时断下
bp 0x00402000,"eax>0x100 && ecx==0"  // 多条件组合
bp 0x00403000,"[esp+4]=="password""  // 检查参数
```

### 2.3 调试事件

Windows 调试器通过调试事件循环接收目标进程的状态通知。主要事件类型：

| 事件 | 触发时机 | 调试用途 |
|------|----------|----------|
| CREATE_PROCESS_DEBUG_EVENT | 进程创建 | 初始化断点、读取PE头 |
| LOAD_DLL_DEBUG_EVENT | DLL加载 | 在特定DLL加载后设断点 |
| EXCEPTION_DEBUG_EVENT | 异常发生 | 断点命中、访问违例、除零 |
| EXIT_PROCESS_DEBUG_EVENT | 进程退出 | 清理、分析结束 |
| RIP_EVENT | 调试器内部错误 | 诊断 |

```
调试事件循环（伪代码）：
while (WaitForDebugEvent(&de, INFINITE)) {
    switch (de.dwDebugEventCode) {
        case EXCEPTION_DEBUG_EVENT:
            if (de.Exception.ExceptionRecord.ExceptionCode == EXCEPTION_BREAKPOINT)
                // INT3断点命中
            else if (de.Exception.ExceptionRecord.ExceptionCode == EXCEPTION_SINGLE_STEP)
                // 单步或硬件断点命中
            else if (de.Exception.ExceptionRecord.ExceptionCode == EXCEPTION_ACCESS_VIOLATION)
                // 内存访问违例
            break;
        case LOAD_DLL_DEBUG_EVENT:
            if ( strstr(de.LoadDll.lpImageName, "user32.dll") )
                // user32.dll加载完成
            break;
    }
    ContinueDebugEvent(...);
}
```

### 2.4 跟踪操作

```
Step Into (F7)        步入：进入CALL调用的函数内部
Step Over (F8)        步过：执行CALL但不进入函数
Step Out  (Ctrl+F9)  步出：运行到当前函数返回
Run to Cursor         运行到光标位置
Trace Into            跟踪步入：自动单步并记录每条指令
Trace Over            跟踪步过：自动单步步过并记录
```

运行跟踪（Run Trace）会记录每一步执行的寄存器状态和内存变化，用于事后分析复杂算法：

```
x64dbg 跟踪命令：
TraceIntoConditional 0x00401000     // 跟踪到条件满足
TraceIntoConditional "eax==0x1234"  // 跟踪到eax为指定值
TraceCount 1000                      // 跟踪指定步数
```

### 2.5 调试窗口与运行跟踪

x64dbg 提供多种调试窗口用于观察程序状态：

- **反汇编窗口**：显示当前位置的反汇编代码，可滚动查看。
- **寄存器窗口**：实时显示通用寄存器、标志位、段寄存器值，变化时高亮。
- **内存窗口**：以十六进制+ASCII 形式显示指定地址的内存内容，可同时打开多个。
- **堆栈窗口**：显示当前 ESP/RSP 指向的栈内容，自动标注返回地址和参数。
- **日志窗口**：输出调试器脚本和插件的日志信息。
- **引用窗口**：查找指令、字符串、常量的引用。

运行跟踪日志：开启后，每条执行指令的寄存器状态都会记录到日志文件，便于事后分析。配置在 `Options → Preferences → Events`。

### 2.6 脚本调试

x64dbg 内置脚本引擎，支持变量、条件、循环，用于自动化调试任务。

**x64dbg 脚本示例 - 在 API 设断点并打印参数：**

```
// 设置API断点
bp VirtualAlloc
// 运行到断点
run
// 循环打印每次调用的参数
loop:
    log "VirtualAlloc: lpAddress={?,[esp+4]}, size={?,[esp+8]}, allocType={?,[esp+12]}, protect={?,[esp+16]}"
    run
    cmp eip, VirtualAlloc
    jne done
    jmp loop
done:
    msg "跟踪结束"
```

**WinDbg 脚本示例 - 命令脚本块：**

```
$$ 遍历所有堆块并检查
.foreach (chunk {!heap -h 0 -all}) {
    .printf "Chunk: %p\n", chunk
}
```

### 2.7 插件开发

x64dbg 提供完整的插件 SDK（C++），开发者可以编写插件扩展功能。核心 API：

```cpp
// 插件回调：菜单点击
PLUG_CB_MENUENTRY {
    int hEntry = callbackInfo->hEntry;
    if (hEntry == MENU_TEST) {
        // 读取当前EIP
        duint eip = 0;
        RegGetValue(EIP, &eip);
        _plugin_logprintf("Current EIP: 0x%p\n", eip);

        // 在EIP处设断点
        DbgCmdExec("bp eip");
    }
}

// 注册插件
extern "C" __declspec(dllexport) bool pluginit(PLUG_INITSTRUCT* initStruct) {
    initStruct->pluginVersion = 1;
    initStruct->sdkVersion = 1;
    strcpy_s(initStruct->pluginName, "MyPlugin");
    return true;
}
```

常用插件功能接口：
```
DbgCmdExec()           执行调试器命令
DbgMemRead()           读取目标进程内存
DbgMemWrite()          写入目标进程内存
DbgSetBreakpoint()     设置断点
PluginMenuAddEntry     添加菜单项
```

---

---

## 📋 内容审核与补充建议

> 针对「Windows动态调试」部分的内容审核结果：

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

### ⚔️ 攻击技术
- ⚠️ 缺少attack相关内容

---

## 📌 拓展学习资源

### 推荐学习路径
- 理论基础 → 工具实践 → 实战演练 → 深度研究
- 建议搭建本地实验环境进行动手练习

### 相关工具与资源
- 在线实验平台：Hack The Box、TryHackMe、VulnHub
- 技术文档：官方文档、RFC、OWASP 指南
- 社区资源：GitHub、安全论坛、技术博客
