# SIP（系统完整性保护）

### 4.1 SIP 原理与保护范围

SIP（System Integrity Protection），又称 rootless，首次引入于 OS X 10.11（El Capitan）。其核心设计是即使拥有 root 权限，也无法修改受保护系统目录，从架构上限制 root 的能力。

**SIP 保护范围**

| 保护对象 | 路径 | 保护内容 |
|----------|------|----------|
| 系统目录 | /System | 系统二进制和框架不可修改 |
| 系统二进制 | /usr, /bin, /sbin | 命令行工具不可替换 |
| 预启动分区 | Preboot、Recovery | 启动相关文件不可修改 |
| Apple 品牌 | /Applications 中 Apple 应用 | 系统自带应用不可修改 |
| APFS 系统卷 | readonly (SSV) | 只读系统卷，整个系统签名验证 |
| 内核扩展 | /Library/Extensions | 仅签名 KEXT 可加载 |
| NVRAM | 特定变量 | 受保护的 NVRAM 变量不可修改 |
| DTrace | 受限 | 无法追踪受保护进程 |

**验证 SIP 保护**

```bash
# 查看 SIP 状态
csrutil status
# 输出：System Integrity Protection status: enabled.

# 查看 SIP 详细配置
csrutil status --verbose

# 尝试修改受保护目录（SIP 启用时会被拒绝）
sudo touch /System/test
# 错误：Read-only file system

sudo touch /usr/local/test
# /usr/local 不在 SIP 保护范围（可写）
```

### 4.2 SIP 对安全的影响

**正面影响**

- 防止恶意软件修改系统二进制文件进行持久化
- 阻止 rootkit 替换核心系统命令
- 保护内核扩展不被篡改
- 配合 SSV（Signed System Volume）实现全系统完整性校验
- 限制 DTrace 对受保护进程的追踪

**负面影响**

| 负面影响 | 说明 |
|----------|------|
| 调试受限 | 无法附加调试器到受保护进程 |
| 系统定制受限 | 无法修改系统级 UI 行为 |
| 取证工具受限 | 部分取证工具无法读取内核内存 |
| 合法工具被阻 | 某些系统管理工具无法操作受保护路径 |
| 安全研究受限 | 安全研究人员需禁用 SIP 才能进行内核研究 |

### 4.3 SIP 绕过技术

**禁用 SIP（需要恢复模式）**

```bash
# 步骤1: 重启进入恢复模式（Intel: Cmd+R；Apple Silicon: 长按电源键）

# 步骤2: 在恢复模式的终端中
csrutil disable
# 输出：Successfully disabled System Integrity Protection.

# 步骤3: 重启
reboot

# 步骤4: 验证（正常模式下）
csrutil status
# 输出：System Integrity Protection status: disabled.

# 重新启用 SIP（恢复模式）
csrutil enable

# 部分启用 SIP（高级配置）
# csrutil enable --without fs --without dtrace --without debug
# 可选参数：
#   --without fs      禁用文件系统保护
#   --without dtrace   禁用 DTrace 限制
#   --without debug    禁用调试限制
#   --without nvram   禁用 NVRAM 保护
#   --without kext     禁用 KEXT 验证
```

**SIP-less 环境风险**

在 SIP 禁用的环境中，攻击者可以：

```
1. 替换系统二进制文件 → 实现持久化后门
   sudo cp /tmp/evil_binary /usr/bin/sudo

2. 修改系统框架 → 注入恶意代码
   sudo cp /tmp/evil.dylib /System/Library/Frameworks/...

3. 加载未签名 KEXT → 内核级 rootkit
   sudo kextload /tmp/evil.kext

4. 修改 NVRAM → 启动级持久化
   sudo nvram boot-args="..."

5. 使用 DTrace 追踪凭据 → 窃取密码
   sudo dtrace -n 'syscall::read:entry /pid==$target/ { ... }'
```

### 4.4 SIP 配置与定制化

**Apple Silicon 的安全策略层级**

```
macOS 安全启动链（Apple Silicon）：
┌──────────────────────────────────┐
│  Secure Enclave ROM              │  ← 硬件信任根
├──────────────────────────────────┤
│  iBoot Bootloader                │  ← 验证下一阶段签名
├──────────────────────────────────┤
│  macOS Kernel (kernelcache)      │  ← 签名验证
├──────────────────────────────────┤
│  Signed System Volume (SSV)      │  ← APFS 快照 + 加密
├──────────────────────────────────┤
│  System Integrity Protection     │  ← 运行时保护
├──────────────────────────────────┤
│  App Sandbox + TCC               │  ← 应用层隔离
└──────────────────────────────────┘

安全策略层级（Per-OS Security Level）：
  完全安全（Full Security）— 默认，最严格
   ↓ 可降低
  中等安全（Reduced Security）— 允许旧版内核扩展
   ↓ 可降低
  不安全（Permissive Security）— 允许未签名代码，禁用 SIP
```

**Apple Silicon 下管理 SIP**

```bash
# 在恢复模式中查看启动策略
csrutil status

# 设置启动磁盘安全策略（恢复模式）
# 降低安全策略（安装旧版 KEXT）
csrutil authenticated-root disable

# 完全安全策略（恢复后恢复默认）
csrutil authenticated-root enable

# 手动挂载系统卷为可写（需要 SSV 禁用，不推荐）
sudo mount -uw /
# 注意：此操作在 Apple Silicon + SSV 启用时无效
```

---

---

