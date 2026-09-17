# Windows 恶意代码分析基础

### 7.1 PE 文件结构

**PE 文件概述**

PE（Portable Executable）是 Windows 平台的可执行文件格式，包括 .exe、.dll、.sys、.ocx 等。理解 PE 文件结构是恶意代码分析的基础。

**PE 文件结构**

```
┌─────────────────────┐
│    DOS Header       │  ← MZ 签名
├─────────────────────┤
│    DOS Stub         │  ← DOS 下的小程序（通常显示"This program cannot be run in DOS mode"）
├─────────────────────┤
│    NT Header        │  ← PE\0\0 签名 + File Header + Optional Header
│  ├─ Signature       │
│  ├─ File Header     │  ← 机器类型、节数量、时间戳等
│  └─ Optional Header │  ← 入口点、映像基地址、节对齐、数据目录等
├─────────────────────┤
│   Section Table     │  ← 节表，每个节的描述信息
├─────────────────────┤
│     .text 节        │  ← 代码节，存储可执行代码
├─────────────────────┤
│     .data 节        │  ← 数据节，存储初始化的全局变量
├─────────────────────┤
│     .rdata 节       │  ← 只读数据，包括导入表、导出表
├─────────────────────┤
│     .rsrc 节        │  ← 资源节，图标、菜单、对话框等
├─────────────────────┤
│     .reloc 节       │  ← 重定位节
└─────────────────────┘
```

**重要的数据目录**

| 目录 | 说明 |
|------|------|
| Export Table | 导出表，列出该文件导出的函数 |
| Import Table | 导入表，列出该文件导入的函数 |
| Resource Table | 资源表，图标、菜单、字符串等 |
| Exception Table | 异常表，SEH 处理信息 |
| Base Relocation Table | 基址重定位表 |
| TLS Table | 线程局部存储表 |
| Import Address Table | 导入地址表 |
| Delay Import Table | 延迟导入表 |
| COM Descriptor | CLR/.NET 描述符 |

**PE 分析工具**

- CFF Explorer：PE 文件编辑器和分析工具
- PEview：PE 文件结构查看器
- IDA Pro / Ghidra：反汇编和反编译
- x64dbg：动态调试

### 7.2 导入表分析

**导入表的作用**

导入表记录了程序需要从其他 DLL 中导入的函数。分析导入表可以了解程序的功能和行为。

**常见可疑导入函数**

**进程/线程相关**
```
CreateProcess / CreateRemoteThread  → 创建进程/远程线程
OpenProcess / VirtualAllocEx        → 进程注入相关
WriteProcessMemory / ReadProcessMemory → 进程内存读写
CreateThread / QueueUserAPC        → 线程创建/APC 注入
```

**文件操作相关**
```
CreateFile / WriteFile             → 文件创建和写入
FindFirstFile / FindNextFile       → 文件遍历
CopyFile / MoveFile                → 文件复制/移动
DeleteFile                         → 文件删除
```

**注册表相关**
```
RegOpenKeyEx / RegSetValueEx       → 注册表打开/写入
RegCreateKeyEx / RegDeleteKey      → 注册表创建/删除
RegQueryValueEx                    → 注册表查询
```

**网络相关**
```
WSAStartup / socket / connect      → Winsock 初始化/连接
send / recv                        → 网络数据收发
InternetOpen / InternetOpenUrl     → WinINet HTTP 访问
HttpOpenRequest / HttpSendRequest  → HTTP 请求
```

**调试/反调试相关**
```
IsDebuggerPresent                  → 检测调试器
CheckRemoteDebuggerPresent         → 远程调试器检测
OutputDebugString                  → 调试输出
GetTickCount / QueryPerformanceCounter → 时间检测
```

### 7.3 恶意代码常见行为

**持久化行为**

1. 创建注册表启动项
2. 创建系统服务
3. 创建计划任务
4. 修改系统配置
5. 注入到系统进程

**信息窃取行为**

1. 读取浏览器密码和 Cookie
2. 记录键盘输入（键盘记录器）
3. 截取屏幕截图
4. 读取剪贴板内容
5. 窃取文件和文档

**网络行为**

1. 连接 C2 服务器
2. 下载后续 payload
3. 上传窃取的数据
4. 端口扫描
5. 横向移动

**对抗分析行为**

1. 检测调试器
2. 检测虚拟机
3. 检测沙箱
4. 加密/混淆代码
5. 延迟执行

### 7.4 加壳与脱壳

**常见加壳器**

| 加壳器 | 类型 | 说明 |
|--------|------|------|
| UPX | 压缩壳 | 开源，最常见的压缩壳 |
| ASProtect | 加密壳 | 带有反调试、反分析功能 |
| Themida/VMProtect | 虚拟化壳 | 代码虚拟化，强度很高 |
| Enigma Protector | 加密壳 | 功能丰富的保护工具 |
| PECompact | 压缩壳 | 压缩+一些保护功能 |
| MPRESS | 压缩壳 | 免费的压缩壳 |
| Obsidium | 加密壳 | 带授权管理的保护工具 |

**加壳识别方法**

```
1. PEiD / DIE：查壳工具，识别常见加壳器
2. 节区名称：加壳后通常有特殊的节名（UPX0、UPX1、.themida 等）
3. 导入表：加壳后导入表函数很少，通常只有 LoadLibrary 和 GetProcAddress
4. 入口点：入口点不在 .text 节，或在末尾的节中
5. 文件熵：加壳后文件熵值很高（接近8）
```

**UPX 脱壳示例**

```bash
# 使用 UPX 自带的脱壳功能
upx -d malware.exe -o unpacked.exe

# 手动脱壳（ESP 定律）
# 1. 用 x64dbg 打开加壳程序
# 2. 在入口点观察 ESP 寄存器
# 3. 在 ESP 指向的地址下硬件访问断点
# 4. 运行程序，断下后就是 OEP（原始入口点）
# 5. 使用 Scylla 插件转储并修复 IAT
```

---

---

## 📋 内容审核与补充建议

> 针对「Windows 恶意代码分析基础」部分的内容审核结果：

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

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
