# 沙箱与 SELinux

### 6.1 Android 沙箱机制

**核心原理**：每个 Android 应用都分配一个唯一的 UID（用户 ID），运行在独立的进程和虚拟机中，实现应用间的隔离。

#### UID 隔离
- 每个应用安装时被分配唯一的 UID（如 u0_a100）
- 应用进程以该 UID 运行
- 应用数据目录权限设置为仅该 UID 可访问

```bash
# 查看应用的 UID
adb shell dumpsys package com.example.app | grep userId
# 输出：userId=10123

# 查看应用进程
adb shell ps | grep com.example.app
# u0_a123   12345  1234  ...  com.example.app
```

#### 文件系统隔离
```
/data/data/com.example.app/     # 应用私有数据目录（仅应用自身可访问）
    ├── shared_prefs/           # SharedPreferences 存储
    ├── databases/              # SQLite 数据库
    ├── files/                  # 内部存储文件
    ├── cache/                  # 缓存目录
    └── ...

/sdcard/Android/data/com.example.app/   # 外部存储私有目录
    ├── files/
    └── cache/
```

#### 进程隔离
- 每个应用运行在独立的 Linux 进程中
- 每个应用拥有独立的 Dalvik/ART 虚拟机实例
- 应用间不能直接访问对方的内存空间

### 6.2 SELinux 基础

**SELinux**（Security-Enhanced Linux）是 Linux 内核的强制访问控制（MAC）安全模块，Android 从 4.3 开始引入。

#### SELinux 模式
| 模式 | 说明 |
|------|------|
| **Enforcing**（强制模式） | 拒绝违规操作并记录日志（生产环境） |
| **Permissive**（宽容模式） | 只记录日志，不拒绝操作（调试用） |
| **Disabled**（禁用） | 完全关闭 SELinux |

**查看 SELinux 状态**：
```bash
adb shell getenforce
# 输出：Enforcing

adb shell setenforce 0   # 设置为 Permissive（需 root）
adb shell setenforce 1   # 设置为 Enforcing
```

#### SELinux 上下文

每个进程、文件、设备都有 SELinux 上下文，格式为：
```
user:role:type:level
```

**常见上下文示例**：
```
# 进程上下文
u:r:untrusted_app:s0:c123,c256,c512,c768    # 第三方应用
u:r:system_app:s0                           # 系统应用
u:r:shell:s0                                # adb shell
u:r:init:s0                                 # init 进程

# 文件上下文
u:object_r:system_file:s0                   # 系统文件
u:object_r:app_data_file:s0:c123,c256...    # 应用数据
u:object_r:sdcard_file:s0                   # SD卡文件
```

#### SELinux 策略规则

SELinux 规则定义了哪个源类型（进程）可以对哪个目标类型（文件/设备）执行什么操作。

```
allow untrusted_app app_data_file:file { read write create };
```

含义：允许 `untrusted_app` 域的进程对 `app_data_file` 类型的文件执行读、写、创建操作。

#### SELinux 日志与分析

```bash
# 查看 SELinux 拒绝日志
adb shell dmesg | grep "avc: denied"

# 示例日志
# avc: denied { read } for pid=1234 comm="ExampleApp" name="secret.txt"
#     dev="mmcblk0p10" ino=12345 scontext=u:r:untrusted_app:s0:c123
#     tcontext=u:object_r:system_file:s0 tclass=file permissive=0
```

日志解读：
- **scontext**：源上下文（谁在操作）
- **tcontext**：目标上下文（操作什么）
- **tclass**：目标类别（file/dir/socket 等）
- **操作**：read/write/create/open 等
- **permissive=0**：处于 Enforcing 模式，操作被拒绝

### 6.3 沙箱绕过

常见的沙箱绕过手段：
1. **组件导出漏洞**：通过导出组件间接访问其他应用数据
2. **ContentProvider 漏洞**：SQL 注入、路径遍历
3. **符号链接攻击**：利用文件系统的符号链接越权访问
4. **权限提升漏洞**：利用系统漏洞提升到更高权限域
5. **内核漏洞**：利用内核漏洞实现 Root，完全绕过沙箱

---

---

## 📋 内容审核与补充建议

> 针对「沙箱与 SELinux」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

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
