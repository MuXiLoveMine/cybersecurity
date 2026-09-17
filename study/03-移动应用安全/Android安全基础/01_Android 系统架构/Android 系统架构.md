# Android 系统架构

### 1.1 四层架构详解

Android 系统采用分层架构设计，从上到下分为四层：

```
┌─────────────────────────────────────────┐
│           应用层 (Applications)          │  ← 系统应用 + 第三方应用
├─────────────────────────────────────────┤
│       应用框架层 (Application Framework) │  ← Java API 框架
├─────────────────────────────────────────┤
│        系统运行库层 (Libraries)          │  ← Native 库 + Android Runtime
├─────────────────────────────────────────┤
│         Linux 内核层 (Linux Kernel)      │  ← 驱动 + 核心服务
└─────────────────────────────────────────┘
```

#### 第一层：应用层 (Applications)
- **位置**：最顶层
- **内容**：系统自带应用（电话、短信、通讯录、浏览器等）和用户安装的第三方应用
- **运行环境**：每个应用运行在独立的 Dalvik/ART 虚拟机实例中
- **安全意义**：应用层是用户直接交互的层面，也是漏洞最集中的层面

#### 第二层：应用框架层 (Application Framework)
- **位置**：应用层之下
- **核心组件**：
  - **Activity Manager**：管理 Activity 生命周期和任务栈
  - **Window Manager**：管理窗口系统
  - **Content Providers**：跨应用数据共享
  - **View System**：UI 控件体系
  - **Package Manager**：应用包管理
  - **Telephony Manager**：电话相关服务
  - **Resource Manager**：资源管理
  - **Location Manager**：位置服务
  - **Notification Manager**：通知管理
- **安全意义**：框架层提供了应用间通信的机制，也是权限控制的核心层

#### 第三层：系统运行库层 (Libraries)
- **位置**：框架层之下，分为两部分：

**Native C/C++ 库**：
- **Surface Manager**：显示系统管理
- **Media Framework**：多媒体框架（基于 PacketVideo）
- **SQLite**：轻量级数据库
- **OpenGL ES**：3D 图形渲染
- **FreeType**：字体渲染
- **WebKit**：浏览器引擎
- **SGL**：2D 图形引擎
- **SSL**：安全套接层
- **libc**：标准 C 库

**Android Runtime (ART)**：
- 核心库（Core Libraries）：提供 Java 核心 API
- ART 虚拟机：执行 DEX 字节码，采用 AOT（预编译）+ JIT（即时编译）混合模式
- 取代了旧版的 Dalvik 虚拟机（Android 5.0 之前）

**安全意义**：Native 层漏洞（如缓冲区溢出）可能导致权限提升

#### 第四层：Linux 内核层 (Linux Kernel)
- **位置**：最底层
- **核心功能**：
  - **进程管理**：基于 Linux 的进程模型
  - **内存管理**：虚拟内存、内存映射
  - **文件系统**：ext4、F2FS 等
  - **设备驱动**：显示驱动、摄像头驱动、音频驱动、蓝牙驱动、WiFi 驱动、Binder 驱动等
  - **网络协议栈**：TCP/IP 协议栈
  - **安全机制**：SELinux、权限隔离

**安全意义**：内核漏洞是权限提升和 Root 的关键

### 1.2 系统启动流程

```
Boot ROM → Bootloader → Kernel → init → Zygote → SystemServer → 系统应用 → Launcher
```

各阶段安全要点：
- **Bootloader**：负责验证内核镜像完整性，防止刷机攻击
- **Kernel**：启动 SELinux、加载驱动、挂载文件系统
- **Zygote**：孵化所有应用进程的母体进程，初始化 ART 虚拟机
- **SystemServer**：启动所有系统服务（ActivityManagerService、PackageManagerService 等）

---

---

## 📋 内容审核与补充建议

> 针对「Android 系统架构」部分的内容审核结果：

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
