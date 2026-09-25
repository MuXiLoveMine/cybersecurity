# Windows 文件架构详解

> 本文系统介绍 Windows 操作系统的文件架构，从文件系统类型、NTFS 核心结构、系统目录结构，到安全相关目录与物理/逻辑架构。面向系统管理员与安全工程师，深度覆盖操作参考与安全加固。示例优先 Windows 10/11 与 Windows Server 2019/2022。

---

## 目录

- [一、文件系统类型](#一文件系统类型)
- [二、NTFS 核心结构](#二ntfs-核心结构)
- [三、Windows 系统目录结构](#三windows-系统目录结构)
- [四、安全相关目录与文件](#四安全相关目录与文件)
- [五、物理架构与逻辑架构](#五物理架构与逻辑架构)
- [附：优化后的提示词模板](#附优化后的提示词模板)

---

## 一、文件系统类型

### 1.1 四大文件系统对比

| 特性 | **NTFS** | **ReFS** | **FAT32** | **exFAT** |
|------|----------|----------|-----------|-----------|
| **全称** | New Technology File System | Resilient File System | File Allocation Table 32 | Extended File Allocation Table |
| **引入版本** | Windows NT 3.1 (1993) | Windows Server 2012 | Windows 95 OSR2 | Windows CE 6.0 / Vista SP1 |
| **最大单文件** | 16 EB（理论）<br>256 TB（实际） | 16 EB | 4 GB | 16 EB |
| **最大卷大小** | 256 TB | 1 YB（理论）<br>35 PB（实际） | 2 TB（标准）<br>16 TB（64KB簇） | 128 PB |
| **默认簇大小** | 4 KB（< 2 TB） | 4 KB / 64 KB | 4 KB - 32 KB | 4 KB - 32 MB |
| **文件名长度** | 255 字符（Unicode） | 255 字符 | 255 字符（长文件名） | 255 字符 |
| **权限（ACL）** | ✅ 完整支持 | ✅ 完整支持 | ❌ 不支持 | ❌ 不支持 |
| **日志（Journaling）** | ✅ 元数据日志 | ✅ 分配写入元数据 | ❌ 无 | ❌ 无 |
| **文件压缩** | ✅ NTFS 压缩 | ❌ 不支持 | ❌ 不支持 | ❌ 不支持 |
| **文件加密（EFS）** | ✅ 透明加密 | ❌ 不支持 | ❌ 不支持 | ❌ 不支持 |
| **配额（Quota）** | ✅ 支持 | ❌ 不支持 | ❌ 不支持 | ❌ 不支持 |
| **硬链接** | ✅ 同卷内 | ❌ 不支持 | ❌ 不支持 | ❌ 不支持 |
| **符号链接** | ✅ 支持 | ✅ 支持 | ❌ 不支持 | ❌ 不支持 |
| **重解析点** | ✅ 支持 | ✅ 部分支持 | ❌ 不支持 | ❌ 不支持 |
| **稀疏文件** | ✅ 支持 | ✅ 支持 | ❌ 不支持 | ❌ 不支持 |
| **快照/卷影副本** | ✅ VSS | ✅ 内置快照 | ❌ 不支持 | ❌ 不支持 |
| **数据完整性校验** | ❌ 元数据无校验 | ✅ 校验和 + 自动修复 | ❌ 无 | ❌ 无 |
| **跨平台兼容** | Windows 主要<br>Linux 只读（NTFS-3G） | Windows 仅 | 全平台通用 | 全平台通用 |
| **适用场景** | 系统盘、数据盘、权限管理 | 大文件存储、备份、虚拟化 | U盘、SD卡、多系统交换 | 大容量U盘、移动硬盘 |

### 1.2 各文件系统优缺点

#### NTFS

```
优点：
  ✓ 权限管理完善（ACL），企业安全必备
  ✓ 日志保证崩溃后数据一致性
  ✓ 压缩/加密/配额/硬链接 等高级特性
  ✓ 卷影副本（VSS）支持备份和恢复
  ✓ 成熟稳定，Windows 默认系统盘格式

缺点：
  ✗ 元数据无校验和，静默损坏无法检测
  ✗ 元数据开销较大，小文件浪费空间
  ✗ 跨平台兼容性差（Linux 需 NTFS-3G）
  ✗ 不适合闪存优化（无 TRIM 直通优化）
```

#### ReFS

```
优点：
  ✓ 内置校验和，自动检测和修复损坏
  ✓ 基于分配写入（Allocate-on-write），抗损坏
  ✓ 支持块克隆（Block Cloning），虚拟机高效
  ✓ 支持镜像加速奇偶校验（镜像层+奇偶层）
  ✓ 大文件/大卷性能优异

缺点：
  ✗ 不支持文件压缩、EFS 加密、磁盘配额
  ✗ 不支持硬链接
  ✗ 不能作为系统盘（引导盘）
  ✗ 社区工具和取证工具支持较少
```

> **版本差异**：Windows Server 2019 起 ReFS 支持实时层级优化；Windows Server 2022 增强了压缩和去重。Windows 10/11 Pro for Workstations 版本支持 ReFS 格式化。

#### FAT32

```
优点：
  ✓ 几乎所有设备/系统都能读取
  ✓ 结构简单，实现成本低
  ✓ 小文件存储效率高

缺点：
  ✗ 单文件最大 4 GB（最常见痛点）
  ✗ 无权限、无日志、无加密
  ✗ 大卷下簇浪费严重
  ✗ 文件名长度有限（短文件名 8.3 格式）
```

#### exFAT

```
优点：
  ✓ 突破 4 GB 文件限制，最大 16 EB
  ✓ 全平台兼容（Windows/macOS/Linux）
  ✓ 专为闪存设计，磨损均衡友好
  ✓ 支持大簇大小，大文件效率高

缺点：
  ✗ 无权限、无日志、无加密
  ✗ 专利问题（微软持有，Linux 需 fuse-exfat）
  ✗ 不支持硬链接
```

### 1.3 选择建议

| 场景 | 推荐文件系统 | 理由 |
|------|-------------|------|
| **系统盘（C:）** | NTFS | 必须支持引导、权限、压缩 |
| **数据盘（企业）** | NTFS 或 ReFS | NTFS 功能全；ReFS 数据完整性好 |
| **备份盘** | ReFS | 校验和 + 自动修复，防静默损坏 |
| **U盘（< 32 GB）** | FAT32 | 兼容性最好 |
| **U盘（> 32 GB）** | exFAT | 支持大文件 + 兼容性 |
| **双系统共享分区** | exFAT 或 NTFS | exFAT 无日志写入更安全 |
| **虚拟机磁盘存储** | ReFS | 块克隆 + 快照性能优异 |
| **服务器文件共享** | NTFS | ACL 权限管理完善 |

---

## 二、NTFS 核心结构

### 2.1 NTFS 卷整体布局

```
磁盘分区（NTFS 卷）

┌────────────┬──────────────────────────────────────────┬──────────┐
│ 分区引导扇区│           MFT 区域（元数据）                │  文件数据  │
│  (16 扇区)  │  ┌──────────────────────────────────┐    │          │
│            │  │  $MFT（主文件表，含自身记录）       │    │          │
│  Boot Sector│  │  $MFTMirr（MFT 前几条记录镜像）    │    │  文件数据  │
│  BPB 参数   │  │  $LogFile（事务日志文件）          │    │          │
│            │  │  $Volume（卷信息）                  │    │  空闲空间  │
│            │  │  $AttrDef（属性定义表）             │    │          │
│            │  │  .（根目录）                        │    │          │
│            │  │  $Bitmap（簇位图）                  │    │          │
│            │  │  $Boot（引导扇区副本）              │    │          │
│            │  │  $BadClus（坏簇列表）               │    │          │
│            │  │  $Secure（安全描述符表）            │    │          │
│            │  │  $UpCase（Unicode 大小写表）        │    │          │
│            │  │  $Extend（扩展元数据目录）          │    │          │
│            │  └──────────────────────────────────┘    │          │
└────────────┴──────────────────────────────────────────┴──────────┘
```

### 2.2 主引导记录（MBR）与引导扇区

#### （1）分区方式：MBR vs GPT

| 特性 | MBR | GPT（GUID Partition Table） |
|------|-----|----------------------------|
| **最大分区数** | 4 个主分区（或 3 主 + 扩展） | 128 个（Windows 默认） |
| **最大磁盘容量** | 2 TB | 18 EB（9.4 ZB 理论） |
| **引导记录备份** | 无 | 头部和尾部各一份 |
| **校验** | 无 | CRC32 校验 |
| **UEFI 支持** | 需 Legacy BIOS 模式 | 原生支持 |
| **安全启动** | 不支持 | 支持（Secure Boot） |
| **适用系统** | 旧系统、BIOS 主板 | Windows 10/11 默认、新主板 |

> **安全提示**：GPT + UEFI + Secure Boot 是现代 Windows 安全启动的标配，可防止 Bootkit 类攻击。

#### （2）NTFS 引导扇区（Boot Sector）

NTFS 卷的第一个扇区（512 字节）是引导扇区，也叫 VBR（Volume Boot Record）。

```
引导扇区结构（前 36 字节为 BPB）：

偏移   大小    含义
0x00   3       跳转指令（EB 52 90）
0x03   8       OEM ID（"NTFS    "）
0x0B   25      BPB（BIOS 参数块）
         - 每扇区字节数（512）
         - 每簇扇区数（8 = 4KB 簇）
         - 保留扇区数
         - 总扇区数
         - MFT 起始簇号
         - MFTMirr 起始簇号
         - 每 MFT 记录簇数
         - ...
0x24   48      扩展 BPB
0x54   426     引导代码
0x1FE  2       签名 0x55AA
```

**安全风险**：引导扇区被篡改会导致系统无法启动，Bootkit 病毒常修改此处。

### 2.3 主文件表（MFT）

MFT（Master File Table）是 NTFS 的核心，是一个数据库表，卷上的每个文件/目录在 MFT 中都有一条记录。

#### （1）MFT 记录

```
每个 MFT 记录 = 1024 字节（1 KB），也可以是 4 KB

MFT 记录结构：

┌──────────────────────────────────┐
│  FILE 签名（4 字节）               │
├──────────────────────────────────┤
│  更新序列号偏移 + 大小             │
├──────────────────────────────────┤
│  日志文件序列号（LSN）             │
├──────────────────────────────────┤
│  序列号、硬链接数                  │
├──────────────────────────────────┤
│  第一个属性偏移                    │
│  ↓                                 │
│  属性列表（按类型排序）             │
│  ┌─────────────────────────────┐ │
│  │ $STANDARD_INFORMATION       │ │
│  ├─────────────────────────────┤ │
│  │ $FILE_NAME                  │ │
│  ├─────────────────────────────┤ │
│  │ $DATA                       │ │
│  ├─────────────────────────────┤ │
│  │ $SECURITY_DESCRIPTOR        │ │
│  ├─────────────────────────────┤ │
│  │ ... 更多属性                 │ │
│  └─────────────────────────────┘ │
│  ↓                                 │
│  属性结束标记（0xFFFFFFFF）         │
└──────────────────────────────────┘
```

> **非常小的文件**：如果文件数据能放在 MFT 记录的剩余空间里，数据直接存在 MFT 记录中（称为"常驻属性" Resident Attribute），这就是 NTFS 小文件效率高的原因。

#### （2）MFT 前 16 条记录（元数据文件）

| 记录号 | 文件名 | 说明 | 安全相关性 |
|--------|--------|------|-----------|
| 0 | **$MFT** | MFT 自身 | MFT 被破坏 = 卷上所有文件丢失 |
| 1 | **$MFTMirr** | MFT 前几条记录的镜像 | MFT 损坏时的恢复入口 |
| 2 | **$LogFile** | 事务日志文件 | 用于崩溃恢复，可用于取证（文件操作痕迹） |
| 3 | **$Volume** | 卷信息（卷标、版本、标志） | — |
| 4 | **$AttrDef** | 属性定义表 | 定义 NTFS 支持的所有属性类型 |
| 5 | **.**（根目录） | 根目录索引 | — |
| 6 | **$Bitmap** | 簇位图（哪些簇被占用） | 取证时可发现隐藏数据 |
| 7 | **$Boot** | 引导扇区副本 | — |
| 8 | **$BadClus** | 坏簇列表 | 可被用于隐藏数据（将正常簇标记为坏） |
| 9 | **$Secure** | 安全描述符表（$SDS / $SDH / $SII） | ACL 集中存储，减少重复 |
| 10 | **$UpCase** | Unicode 大小写转换表 | — |
| 11 | **$Extended** | 扩展元数据目录 | 含 $ObjId、$Quota、$Reparse 等 |
| 12 - 15 | 保留 | 预留记录 | — |

#### （3）MFT 镜像（$MFTMirr）

```
$MFTMirr 位置：通常在卷中间位置

作用：
  - 备份 MFT 的前 4 条记录（$MFT, $MFTMirr, $LogFile, $Volume）
  - 如果 MFT 开头损坏，可以通过 $MFTMirr 找到 MFT 其余部分
  - 大小：通常 4 个 MFT 记录 = 4 KB

安全提示：
  - 数据恢复工具通过搜索 MFT 镜像来重建文件列表
  - 彻底擦除数据需要同时处理 MFT 和 MFT 镜像
```

### 2.4 NTFS 关键属性

每个 MFT 记录由多个属性（Attribute）组成，每个属性有类型编号、名称和数据。

| 属性 | 类型号 | 常驻/非常驻 | 说明 |
|------|--------|------------|------|
| **$STANDARD_INFORMATION** | 0x10 | 常驻 | 标准信息：创建时间、修改时间、MFT 变更时间、访问时间、属性标志（只读/隐藏/系统/存档）、硬链接数 |
| **$ATTRIBUTE_LIST** | 0x20 | 可变 | 属性列表：当属性太多一条记录装不下时，列出所有属性的位置 |
| **$FILE_NAME** | 0x30 | 常驻 | 文件名：父目录 MFT 引用、文件名（Unicode）、文件大小、时间戳、DOS 名称（8.3） |
| **$OBJECT_ID** | 0x40 | 常驻 | 对象 ID：16 字节 GUID，用于分布式链接跟踪 |
| **$SECURITY_DESCRIPTOR** | 0x50 | 非常驻 | 安全描述符：DACL/SACL/所有者 SID（实际存储在 $Secure 中） |
| **$VOLUME_NAME** | 0x60 | 常驻 | 卷标名 |
| **$VOLUME_INFORMATION** | 0x70 | 常驻 | 卷版本号、标志（如：标记为脏） |
| **$DATA** | 0x80 | 两者皆可 | 文件数据：小文件常驻，大文件非常驻（指向数据簇） |
| **$INDEX_ROOT** | 0x90 | 常驻 | 索引根：目录 B-Tree 的根节点 |
| **$INDEX_ALLOCATION** | 0xA0 | 非常驻 | 索引分配：目录索引的其他节点 |
| **$BITMAP** | 0xB0 | 非常驻 | 索引位图：索引节点的使用情况 |
| **$REPARSE_POINT** | 0xC0 | 常驻 | 重解析点：符号链接、挂载点、目录交接点 |
| **$EA_INFORMATION** | 0xD0 | 常驻 | 扩展属性信息 |
| **$EA** | 0xE0 | 可变 | 扩展属性数据 |
| **$LOGGED_UTILITY_STREAM** | 0x100 | 非常驻 | 日志化工具流：EFS 加密密钥等 |

**属性标志（File Attributes）**：

| 标志位 | 值 | 含义 | 安全用途 |
|--------|----|------|---------|
| **只读** | 0x0001 | 不能被修改/删除 | 保护关键文件 |
| **隐藏** | 0x0002 | 默认不显示 | 恶意软件隐藏自身 |
| **系统** | 0x0004 | 系统文件，受保护 | 系统关键文件标记 |
| **存档** | 0x0020 | 文件已修改，需备份 | 增量备份依据 |
| **目录** | 0x0010 | 是目录 | — |
| **压缩** | 0x0800 | 文件被压缩 | — |
| **加密** | 0x4000 | EFS 加密 | 数据保护 |
| **稀疏** | 0x0200 | 稀疏文件 | — |
| **重解析点** | 0x0400 | 含重解析点 | 符号链接/挂载点 |

> **取证提示**：时间戳（$STANDARD_INFORMATION 中的四个时间）是取证分析的关键，但可被轻易篡改。$FILE_NAME 属性中也有一套时间戳，两者不一致时可能是伪造痕迹。

### 2.5 B-Tree 目录索引

NTFS 使用 B+ 树（B-Tree 变体）管理目录，使文件查找效率为 O(log n)。

```
目录索引结构：

一个目录 = $INDEX_ROOT + $INDEX_ALLOCATION + $BITMAP

$INDEX_ROOT（B-Tree 根节点，常驻 MFT）
  ├── 索引条目 1（文件名 1 → MFT 记录号）
  ├── 索引条目 2（文件名 2 → MFT 记录号）
  └── ...

$INDEX_ALLOCATION（索引缓冲区，非常驻）
  ├── 索引块 1（4 KB 大小）
  │     ├── 索引条目 A
  │     └── 索引条目 B
  ├── 索引块 2
  └── ...

$BITMAP（索引节点位图）
  标记哪些索引块被使用
```

**查找过程**：

```
查找 C:\Users\Alice\Documents\report.docx

1. 从根目录（MFT 记录 5）的 $INDEX_ROOT 开始
2. 在索引中找到 "Users" → 对应 MFT 记录号 X
3. 读取 MFT 记录 X 的 $INDEX_ROOT
4. 在索引中找到 "Alice" → 对应 MFT 记录号 Y
5. 读取 MFT 记录 Y 的 $INDEX_ROOT
6. 在索引中找到 "Documents" → 对应 MFT 记录号 Z
7. 读取 MFT 记录 Z 的 $INDEX_ROOT
8. 在索引中找到 "report.docx" → 对应 MFT 记录号 W
9. 读取 MFT 记录 W，获取 $DATA 属性 → 文件内容
```

### 2.6 NTFS 高级特性

#### （1）日志（USN 日志 + $LogFile）

| 日志 | 位置 | 用途 | 安全相关性 |
|------|------|------|-----------|
| **$LogFile** | NTFS 元数据 | 事务日志，保证元数据操作原子性 | 崩溃恢复，取证价值有限 |
| **USN 日志** | $Extend\$UsnJrnl | 变更日志，记录文件增删改 | **取证关键**：可追溯文件操作历史 |

```
USN 日志（Update Sequence Number Journal）：

  记录内容：
    - 文件名
    - 操作类型（创建/删除/修改/重命名/安全更改）
    - 时间戳
    - 文件引用号（MFT 记录号）

  查看命令：
    fsutil usn queryJournal C:
    fsutil usn readJournal C:

  安全用途：
    ✓ 取证分析：追踪攻击者操作过的文件
    ✓ 监控：检测敏感文件被访问/修改
    ✓ 备份：增量备份判断哪些文件变更
```

#### （2）NTFS 压缩

```
压缩方式：
  - 按压缩单元（Compression Unit）压缩
  - 压缩单元 = 16 个簇（默认 64 KB）
  - 稀疏文件零块不占用磁盘空间

  启用方式：
    右键 → 属性 → 高级 → 压缩内容以节省磁盘空间
    compact /c file.txt
    compact /c /s:C:\folder

  适用：
    ✓ 很少访问的大文件（日志、备份）
    ✗ 频繁修改的文件（每次写入都要解压/压缩）
    ✗ 系统文件（引导文件不能压缩）
```

#### （3）EFS 加密（Encrypting File System）

```
工作原理：
  1. 文件用 FEK（文件加密密钥，随机对称密钥）加密
  2. FEK 用用户公钥加密，存在 $EFS 属性中
  3. 用户用私钥解密 FEK，再用 FEK 解密文件
  4. 私钥受 DPAPI 保护，存储在用户配置文件中

  启用方式：
    右键 → 属性 → 高级 → 加密内容以保护数据
    cipher /e file.txt
    cipher /e /s:C:\folder

  安全注意：
    - 必须备份 EFS 证书（.pfx），否则重装系统后无法解密
    - 攻击者拿到用户配置文件 + 密码可解密
    - EFS 不防内存窃取（文件在内存中是明文）
```

#### （4）硬链接 vs 符号链接 vs 交接点

| 类型 | 英文 | 跨卷 | 指向目录 | 命令 | 安全风险 |
|------|------|------|---------|------|---------|
| **硬链接** | Hard Link | ❌ | ❌（仅文件） | `mklink /H` | 多个入口，难追踪 |
| **符号链接** | Symbolic Link | ✅ | ✅ | `mklink /D`（目录）<br>`mklink`（文件） | 路径欺骗、提权 |
| **目录交接点** | Junction Point | ❌ | ✅ | `mklink /J` | 路径欺骗、权限绕过 |
| **挂载点** | Mount Point | — | ✅（卷） | `diskmgmt.msc` | — |

```
硬链接示例：
  mklink /H link.txt target.txt
  - link.txt 和 target.txt 指向同一个 MFT 记录
  - 删除任何一个都不影响另一个
  - 硬链接计数记录在 $STANDARD_INFORMATION 中

符号链接示例：
  mklink link.txt target.txt
  - link.txt 是一个重解析点，存储目标路径
  - 删除 target.txt，link.txt 变成死链接
  - 可指向网络路径（UNC）
```

> **安全风险**：符号链接和交接点可被用于路径欺骗攻击。例如，攻击者在可写目录创建符号链接指向系统目录，结合某些服务的文件操作可能导致权限提升。

---

## 三、Windows 系统目录结构

### 3.1 C:\ 根目录典型结构

```
C:\
├── $Recycle.Bin          回收站（每个用户一个子目录，以 SID 命名）
├── Boot                  启动配置数据库（BCD）
├── Documents and Settings  指向 Users 的交接点（兼容旧程序）
├── MSOCache               Microsoft Office 安装缓存
├── pagefile.sys           页面文件（虚拟内存）
├── PerfLogs               性能日志
├── Program Files          64 位程序
├── Program Files (x86)    32 位程序
├── ProgramData            所有用户共用的程序数据
├── Recovery               恢复分区（WinRE）
├── System Volume Information  系统卷信息（还原点、索引）
├── Users                  用户配置文件目录
├── Windows                操作系统目录（%SystemRoot%）
├── hiberfil.sys           休眠文件（大小 = 内存大小）
└── swapfile.sys           交换文件（UWP 应用用）
```

| 目录/文件 | 说明 | 风险点 | 安全建议 |
|----------|------|--------|---------|
| **$Recycle.Bin** | 回收站，按用户 SID 分子目录 | 被删除文件可能仍含敏感数据 | 定期清空，用 `cipher /w` 擦除空闲空间 |
| **pagefile.sys** | 虚拟内存页面文件 | 内存数据可能被写入磁盘，含敏感信息 | 关机时清空页面文件（组策略） |
| **hiberfil.sys** | 休眠文件，保存内存快照 | 含完整内存镜像，凭据等敏感数据 | 不需要休眠则禁用：`powercfg /h off` |
| **System Volume Information** | 系统还原点、卷影副本 | 旧版本文件可能被利用 | 限制还原点使用空间 |
| **ProgramData** | 公共程序数据 | 弱权限目录可能被写入恶意 DLL | 检查权限，确保仅管理员可写 |

### 3.2 %SystemRoot%（C:\Windows）

```
C:\Windows ( %SystemRoot% )
├── System32                64 位系统文件（核心）
│   ├── config              注册表配置单元
│   ├── drivers             驱动程序（.sys）
│   │   └── etc             hosts、services、protocol 等
│   ├── spool               打印队列
│   ├── Logs                系统日志
│   ├── winevt              事件日志（.evtx）
│   ├── Tasks               计划任务
│   ├── GroupPolicy         组策略缓存
│   └── ... 大量 .exe / .dll
│
├── SysWOW64                32 位系统文件（Wow64 兼容层）
│   ├── config              32 位注册表视图
│   └── ... 32 位 DLL
│
├── SystemApps              系统应用（UWP，如设置、计算器）
├── WinSxS                   Windows 组件存储（WinSxS，side-by-side）
├── Fonts                    字体文件
├── inf                      驱动安装信息文件（.inf）
├── assembly                 GAC（全局程序集缓存，.NET）
├── Boot                     启动相关文件
├── Prefetch                 预读取缓存（应用启动加速）
├── Temp                     系统临时目录
├── Microsoft.NET            .NET Framework
├── Resources                系统资源（主题、壁纸等）
├── ShellExperiences         Shell 体验包
├── ImmersiveControlPanel    沉浸式控制面板
└── Panther                  安装日志
```

### 3.3 System32 与 SysWOW64

这是 Windows 64 位系统中最容易混淆的目录。

| 目录 | 位数 | 说明 |
|------|------|------|
| **System32** | 64 位 | 64 位系统文件和 DLL |
| **SysWOW64** | 32 位 | 32 位系统文件和 DLL（WOW64 = Windows on Windows 64） |

```
为什么名字反直觉？
  - 历史原因：32 位 Windows 时代，系统目录叫 System32
  - 升级到 64 位时，为了兼容大量硬编码 System32 的程序
  - 64 位程序继续用 System32
  - 32 位程序的系统目录改名为 SysWOW64

文件系统重定向（File System Redirector）：
  32 位程序访问 C:\Windows\System32
    → 自动重定向到 C:\Windows\SysWOW64

  32 位程序想访问真正的 64 位 System32
    → 使用 C:\Windows\SysNative  （虚拟路径）
```

**关键安全差异**：

| 配置 | 32 位程序路径 | 64 位程序路径 |
|------|--------------|--------------|
| 系统目录 | C:\Windows\SysWOW64 | C:\Windows\System32 |
| 注册表 | HKLM\SOFTWARE\Wow6432Node | HKLM\SOFTWARE |
| Program Files | C:\Program Files (x86) | C:\Program Files |
| hosts 文件 | C:\Windows\SysWOW64\drivers\etc\hosts | C:\Windows\System32\drivers\etc\hosts |

> ⚠️ **安全警告**：32 位/64 位有两套独立的 hosts 文件、注册表和 DLL 搜索路径。排查问题或加固时必须同时检查两边，否则可能漏掉恶意条目。

### 3.4 Program Files 与 Program Files (x86)

```
C:\Program Files              64 位程序
  ├── WindowsApps             UWP 应用（受保护）
  ├── Microsoft Office        Office 64 位
  ├── Windows Defender        杀毒软件
  ├── IIS                     Internet Information Services
  └── ... 其他 64 位程序

C:\Program Files (x86)        32 位程序
  ├── Common Files            共享组件
  ├── Internet Explorer       32 位 IE
  └── ... 其他 32 位程序
```

| 目录 | 位数 | 默认权限 | 安全提示 |
|------|------|---------|---------|
| **Program Files** | 64 位 | 管理员可写，用户只读 | 权限较严，恶意程序不易写入 |
| **Program Files (x86)** | 32 位 | 同上 | 注意 32 位浏览器、办公软件可能有更多漏洞 |
| **ProgramData** | 共用 | 用户可写（部分子目录） | 常见持久化和 DLL 劫持位置 |
| **Program Files\WindowsApps** | UWP | TrustedInstaller 所有 | 受保护的 UWP 应用目录 |

### 3.5 Users 目录

```
C:\Users
├── Default                 默认用户配置模板（新用户从这里复制）
├── Default User            指向 Default 的交接点
├── Public                  公共用户文件（所有用户可访问）
│   ├── Documents           公共文档
│   ├── Downloads           公共下载
│   └── Desktop             公共桌面
│
├── <UserName>              用户配置目录（%USERPROFILE%）
│   ├── AppData
│   │   ├── Local           本地数据（不同步，%LOCALAPPDATA%）
│   │   │   ├── Temp        用户临时目录
│   │   │   ├── Microsoft\Windows\History  IE 历史
│   │   │   └── Packages    UWP 应用数据
│   │   ├── LocalLow        低完整性级别数据（如浏览器沙箱）
│   │   └── Roaming         漫游数据（域环境同步，%APPDATA%）
│   │       ├── Microsoft\Windows\Recent   最近打开的文件
│   │       ├── Microsoft\Windows\Start Menu  开始菜单
│   │       └── Microsoft\Credentials  凭据管理器
│   ├── Contacts            联系人
│   ├── Desktop             桌面
│   ├── Documents           文档
│   ├── Downloads           下载
│   ├── Favorites           收藏夹
│   ├── Links               链接
│   ├── Music               音乐
│   ├── Pictures            图片
│   ├── Videos              视频
│   ├── Searches            保存的搜索
│   ├── NTUSER.DAT          用户注册表 Hive 文件（HKCU）
│   ├── NTUSER.DAT.LOG      注册表日志
│   └── ntuser.ini          用户配置初始化
│
└── All Users               指向 ProgramData 的交接点
```

| 目录 | 说明 | 安全相关性 |
|------|------|-----------|
| **AppData\Local\Temp** | 用户临时文件 | 恶意软件常用落地点，权限宽松 |
| **AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup** | 用户启动目录 | 用户级持久化位置，登录时自动运行 |
| **NTUSER.DAT** | 用户注册表 Hive | 含用户配置、密码哈希（DPAPI）、最近运行记录 |
| **AppData\Local\Microsoft\Windows\History** | IE/Edge 历史 | 浏览痕迹取证 |
| **AppData\Roaming\Microsoft\Windows\Recent** | 最近文件 | 取证分析用户操作 |
| **AppData\LocalLow** | 低完整性数据 | 浏览器沙箱数据，安全边界 |

### 3.6 ProgramData 与 PerfLogs

```
C:\ProgramData  ( %ProgramData% )
  ├── Microsoft
  │   ├── Windows\Start Menu  所有用户开始菜单
  │   ├── Windows\Start Menu\Programs\Startup  全局启动目录
  │   ├── Crypto\RSA\MachineKeys  机器级密钥存储
  │   ├── Windows\WER  错误报告
  │   └── Windows Defender  杀毒软件数据
  ├── {GUID} 目录           各应用公共数据
  └── 其他应用数据目录

C:\PerfLogs
  ├── Admin                 管理员性能日志
  ├── Diagnostic            诊断日志
  └── System                系统性能日志
```

> **安全提示**：`ProgramData\Microsoft\Windows\Start Menu\Programs\Startup` 是全局启动目录，所有用户登录时都会执行其中的程序。恶意软件常在此处放快捷方式实现持久化。

### 3.7 驱动程序位置

```
驱动程序存储位置：

C:\Windows\System32\drivers\
  ├── *.sys                  内核驱动文件
  ├── etc\
  │   ├── hosts              主机名解析
  │   ├── services           服务名与端口映射
  │   ├── protocol           协议号
  │   └── networks           网络名
  └── DriverStore\           驱动存储库
       └── FileRepository\   驱动包（.inf + .sys + .dll）

驱动信息存储：
  注册表：HKLM\SYSTEM\CurrentControlSet\Services\<驱动名>
  类型：1 = 内核驱动, 2 = 文件系统驱动, 4 = 适配器驱动
```

> **安全检查**：用 `driverquery /v` 或 `sc query type= driver` 查看所有已加载驱动，识别可疑驱动。Rootkit 常通过安装恶意驱动隐藏自身。

### 3.8 重要 DLL 位置

| DLL | 位置 | 功能 | 安全相关性 |
|-----|------|------|-----------|
| **ntdll.dll** | System32 | 系统调用桩、Native API | 用户态与内核态边界 |
| **kernel32.dll** | System32 | 核心 Win32 API（进程/内存/文件） | 最常用 API 库 |
| **user32.dll** | System32 | 窗口、消息、GUI | 消息钩子、注入点 |
| **gdi32.dll** | System32 | 图形设备接口 | GDI+ 漏洞历史多 |
| **advapi32.dll** | System32 | 高级 API（注册表、安全、服务） | 安全相关 API |
| **ws2_32.dll** | System32 | Winsock 网络 | 网络通信 |
| **rpcrt4.dll** | System32 | RPC 运行时 | RPC 漏洞（如 MS08-067） |
| **win32k.sys** | 内核驱动 | 内核图形/窗口 | 内核漏洞高发区 |
| **ntoskrnl.exe** | System32 | 内核执行体 | 内核核心 |
| **hal.dll** | System32 | 硬件抽象层 | 硬件差异隔离 |

---

## 四、安全相关目录与文件

### 4.1 注册表配置单元（Hive 文件）

| Hive 文件 | 对应根键 | 路径 | 安全重要性 |
|-----------|---------|------|-----------|
| **SAM** | HKLM\SAM | `C:\Windows\System32\config\SAM` | ★★★★★ 用户密码哈希 |
| **SECURITY** | HKLM\SECURITY | `C:\Windows\System32\config\SECURITY` | ★★★★ 安全策略、缓存域凭据 |
| **SYSTEM** | HKLM\SYSTEM | `C:\Windows\System32\config\SYSTEM` | ★★★★ 引导配置、服务配置、加密密钥（Syskey/开机密钥） |
| **SOFTWARE** | HKLM\SOFTWARE | `C:\Windows\System32\config\SOFTWARE` | ★★★ 软件配置、持久化点 |
| **DEFAULT** | HKU\.DEFAULT | `C:\Windows\System32\config\DEFAULT` | ★★ 默认用户配置 |
| **COMPONENTS** | HKLM\COMPONENTS | `C:\Windows\System32\config\COMPONENTS` | ★ 组件存储 |
| **NTUSER.DAT** | HKCU | `C:\Users\<user>\NTUSER.DAT` | ★★★★ 用户配置、Run 键、MRU |
| **UsrClass.dat** | HKCU\Software\Classes | `C:\Users\<user>\AppData\Local\Microsoft\Windows\UsrClass.dat` | ★★ COM 类注册、Shell 扩展 |

> ⚠️ **高风险提示**：SAM 和 SYSTEM 配合可提取本地用户密码哈希。SECURITY 中可能有缓存的域凭据（MS Cache）。这些文件在系统运行时被锁定，但可以通过以下方式获取：
> - 卷影副本（VSS）
> - 注册表保存命令：`reg save HKLM\SAM sam.hive`
> - 物理访问 / 启动盘

### 4.2 日志与审计目录

```
事件日志位置：
  C:\Windows\System32\winevt\Logs\
    ├── Security.evtx        安全日志（登录/登出/权限使用）
    ├── System.evtx          系统日志（驱动/服务/BSOD）
    ├── Application.evtx     应用日志（应用事件）
    ├── Setup.evtx           安装日志
    ├── ForwardedEvents.evtx 转发事件
    └── ... 其他自定义日志

其他安全相关日志：
  C:\Windows\System32\LogFiles\
    ├── W3SVC\               IIS 日志（Web 攻击痕迹）
    ├── HTTPERR\             HTTP 错误日志
    └── Firewall\            防火墙日志

  C:\Windows\Prefetch\       预读取缓存（可分析最近运行程序）
    ├── *.pf                 程序启动记录（含文件名、运行次数、时间）

  C:\Windows\Tasks\           计划任务（XML 格式）
    └── *.job / *.xml
```

| 日志 | 位置 | 用途 | 安全建议 |
|------|------|------|---------|
| **Security.evtx** | winevt\Logs | 登录审计、权限使用、对象访问 | 启用成功+失败审核，集中转发 |
| **System.evtx** | winevt\Logs | 服务启停、驱动加载、BSOD | 监控异常驱动和服务 |
| **Prefetch** | Prefetch\ | 程序执行痕迹取证 | 攻击者常删除此目录隐藏痕迹 |
| **USN 日志** | NTFS 元数据 | 文件增删改记录 | 启用，取证关键 |
| **IIS 日志** | LogFiles\W3SVC | Web 攻击检测 | 开启，集中收集分析 |
| **防火墙日志** | LogFiles\Firewall | 网络连接审计 | 开启日志记录 |

### 4.3 缓存与临时目录

| 目录 | 说明 | 安全风险 |
|------|------|---------|
| **C:\Windows\Temp** | 系统临时目录 | 恶意软件常在此释放载荷，权限宽松 |
| **C:\Users\<user>\AppData\Local\Temp** | 用户临时目录 | 同上，用户级落地点 |
| **C:\ProgramData\** | 公共程序数据 | DLL 劫持、持久化 |
| **C:\Windows\Prefetch\** | 预读取缓存 | 泄露程序使用历史 |
| **C:\Windows\Recent** | 最近文件 | 取证分析用户行为 |
| **C:\Users\<user>\AppData\Local\Microsoft\Windows\INetCache** | IE/Edge 缓存 | 浏览器痕迹、恶意脚本缓存 |
| **C:\Users\<user>\AppData\Roaming\Microsoft\Windows\Recent** | 最近使用的文件 | 取证分析 |
| **C:\System Volume Information** | 卷影副本 | 旧版本文件可被利用，含历史凭据 |
| **C:\$Recycle.Bin** | 回收站 | 被删文件仍可恢复 |

### 4.4 常见攻击面

#### （1）持久化位置

```
高风险持久化位置（按优先级）：

1. 注册表 Run 键
   HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
   HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
   HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce

2. 启动目录
   C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup
   C:\Users\<user>\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup

3. 服务
   HKLM\SYSTEM\CurrentControlSet\Services\
   sc query type= service

4. 计划任务
   C:\Windows\System32\Tasks\
   schtasks /query /fo LIST /v

5. 映像劫持（IFEO）
   HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\

6. Winlogon
   HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon\Userinit
   HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon\Shell

7. WMI 事件订阅
   命名空间 root\subscription 下的 __EventFilter / __FilterToConsumerBinding

8. 浏览器扩展 / 插件
   各浏览器扩展目录

9. COM 劫持
   HKCR\CLSID\ 下的 COM 类
   HKCU\Software\Classes\CLSID\
```

#### （2）提权常见位置

```
提权关注点：

1. 服务配置错误
   - 服务路径未加引号（Unquoted Service Path）
   - 服务权限过宽（普通用户可修改服务配置）
   - 服务可执行文件权限过宽（普通用户可替换）

2. 注册表权限
   - HKLM\SYSTEM\CurrentControlSet\Services 下的子键权限
   - 普通用户可写的注册表启动项

3. 计划任务
   - 以高权限运行的任务，其程序/脚本可被普通用户修改

4. DLL 劫持
   - 程序加载顺序中存在可写目录
   - 缺少签名验证的 DLL

5. 令牌权限
   - SeDebugPrivilege：可调试任意进程
   - SeImpersonatePrivilege：模拟令牌（JuicyPotato 等）
   - SeBackupPrivilege：备份权限（可读 SAM/SECURITY）
```

#### （3）凭据存储位置

```
Windows 凭据存储位置：

1. SAM 数据库
   路径：C:\Windows\System32\config\SAM
   内容：本地用户 NTLM 哈希
   获取：需要 SYSTEM 权限，或从 VSS 复制

2. LSASS 进程内存
   内容：登录用户的明文/哈希/票据
   获取：mimikatz sekurlsa::logonpasswords

3. 凭据管理器（Credential Manager）
   路径：%AppData%\Microsoft\Credentials
   内容：保存的网站密码、远程桌面密码、共享凭据
   获取：cmdkey /list 或 mimikatz dpapi::cred

4. 域缓存凭据（MS Cache）
   路径：HKLM\SECURITY\Cache
   内容：缓存的域用户密码哈希（可脱机登录）
   获取：mimikatz lsadump::cache

5. DPAPI 主密钥
   路径：%AppData%\Microsoft\Protect\<SID>\
   用途：加密凭据管理器、EFS、浏览器密码等
   获取：需用户密码或 SYSTEM 权限

6. WiFi 密码
   命令：netsh wlan show profiles name="SSID" key=clear
   存储：WLAN 配置文件
```

### 4.5 安全加固建议

#### （1）系统目录加固

```powershell
# 1. 启用内核驱动签名强制
# 确保只有签名驱动可加载
# 设置 → 更新和安全 → Windows 安全 → 设备安全 → 内核隔离

# 2. 配置 UAC 到最高级别
# 用户账户控制：以管理员批准模式运行所有管理员
secpol.msc → 本地策略 → 安全选项 → 用户账户控制

# 3. 限制对 SAM 的访问
# Windows 10 1809+ 已默认限制，确认以下注册表值为 1
reg query "HKLM\SYSTEM\CurrentControlSet\Control\Lsa" /v RestrictRemoteSAM

# 4. 启用 Credential Guard
# 虚拟化安全保护 LSASS，防止内存读取
# 需 UEFI + Secure Boot + TPM 2.0

# 5. 禁用 LM 哈希（仅存储 NTLMv2）
# 组策略：网络安全：LAN 管理器身份验证级别 → 仅发送 NTLMv2 响应
secpol.msc → 本地策略 → 安全选项 → 网络安全: LAN 管理器身份验证级别

# 6. 启用 LSA 保护
# 防止未签名插件注入 LSASS
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Lsa" /v RunAsPPL /t REG_DWORD /d 1 /f
```

#### （2）审计与日志加固

```powershell
# 1. 启用安全日志审计
# 组策略 → 计算机配置 → Windows 设置 → 安全设置 → 本地策略 → 审核策略
#   审核登录事件：成功 + 失败
#   审核对象访问：成功 + 失败
#   审核进程追踪：成功

# 2. 增加安全日志大小
wevtutil sl Security /ms:419430400  # 设置为 400 MB

# 3. 启用 Sysmon（增强进程/网络/文件审计）
# 下载 Sysmon，导入配置
Sysmon64.exe -i sysmonconfig.xml

# 4. 启用 Windows 防火墙日志
netsh advfirewall set currentprofile logging filename "C:\Windows\System32\LogFiles\Firewall\pfirewall.log"
netsh advfirewall set currentprofile logging maxfilesize 4096
netsh advfirewall set currentprofile logging droppedconnections enable
```

#### （3）临时目录与回收站

```powershell
# 1. 定期清理临时目录
# 用磁盘清理工具
cleanmgr /sagerun:1

# 2. 关机时清空页面文件（防止内存数据泄露）
# 组策略：关机：清除虚拟内存页面文件
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management" /v ClearPageFileAtShutdown /t REG_DWORD /d 1 /f

# 3. 禁用休眠（删除 hiberfil.sys）
powercfg /h off

# 4. 擦除空闲空间（删除文件后擦除）
cipher /w:C:\folder
# ⚠️ 注意：会在空闲空间写入随机数据，耗时长，影响 SSD 寿命
```

#### （4）关键文件备份建议

```
备份清单（系统修复与取证）：

1. 注册表配置单元备份
   reg save HKLM\SAM sam_backup.hive
   reg save HKLM\SYSTEM system_backup.hive
   reg save HKLM\SECURITY security_backup.hive
   ⚠️ 加密存储，防止泄露

2. 系统状态备份
   wbadmin start systemstatebackup -backuptarget:D:

3. 卷影副本
   vssadmin create shadow /for=C:
   ⚠️ 攻击者也可能利用 VSS，需控制访问权限

4. EFS 证书备份
   certmgr.msc → 个人 → 证书 → 导出（含私钥，.pfx 格式）
   ⚠️ 设置强密码，离线存储

⚠️ 修改系统目录/文件前的通用原则：
  1. 先做系统还原点
  2. 重要文件先备份
  3. 优先使用组策略/官方工具修改
  4. 不要直接手动删除系统目录下的文件
  5. 测试环境验证后再上生产
```

---

## 五、物理架构与逻辑架构

### 5.1 从磁盘到文件的层次

```
物理层 ←————————————————————→ 逻辑层

  物理磁盘（Disk）
      │
      ↓  分区（Partition）
  MBR / GPT 分区表
      │
      ↓  卷（Volume）
  逻辑磁盘（C:, D:, ...）
      │
      ↓  文件系统（File System）
  NTFS / ReFS / FAT32
      │
      ↓  目录与文件
  C:\Users\Alice\Documents\report.docx
```

| 层次 | 概念 | 说明 | 工具 |
|------|------|------|------|
| **物理磁盘** | Physical Disk | 真实硬件 | diskmgmt.msc, `wmic diskdrive` |
| **分区** | Partition | 磁盘上的逻辑划分 | diskpart, fdisk |
| **卷** | Volume | 格式化后的分区，有盘符 | `mountvol`, diskmgmt.msc |
| **文件系统** | File System | 组织文件的方式 | format, `fsutil fsinfo` |
| **目录/文件** | Directory/File | 用户可见的数据组织 | 资源管理器, dir |

### 5.2 逻辑路径与物理扇区的关系

```
文件路径：C:\Users\Alice\doc.txt
    │
    ↓  路径解析
  NTFS 目录索引（B-Tree 查找）
    │
    ↓  找到文件 MFT 记录号
  MFT 记录（读取 $DATA 属性）
    │
    ↓  获取数据簇号（VCN → LCN）
  数据簇（Cluster）
    │
    ↓  簇 = N 个扇区
  逻辑扇区（LBA, Logical Block Address）
    │
    ↓  磁盘控制器翻译
  物理扇区（柱面/磁头/扇区 → LBA）
```

**关键术语**：

| 术语 | 英文 | 说明 | 典型大小 |
|------|------|------|---------|
| **扇区** | Sector | 磁盘最小读写单位 | 512 字节（传统）/ 4 KB（Advanced Format） |
| **簇** | Cluster | 文件系统最小分配单位 | 4 KB（NTFS 默认） |
| **VCN** | Virtual Cluster Number | 虚拟簇号（文件内的偏移） | — |
| **LCN** | Logical Cluster Number | 逻辑簇号（卷上的绝对位置） | — |
| **LBA** | Logical Block Address | 逻辑块地址（扇区级地址） | — |

### 5.3 Windows 引导流程

#### （1）UEFI 引导（现代系统）

```
1. 上电 → UEFI BIOS 初始化
     ↓
2. UEFI 读取 GPT 分区表
     ↓
3. 找到 EFI 系统分区（ESP，通常 100-500 MB，FAT32 格式）
     ↓
4. 加载 ESP:\EFI\Microsoft\Boot\bootmgfw.efi
     ↓
5. Windows Boot Manager 读取 BCD（引导配置数据）
   位置：ESP:\EFI\Microsoft\Boot\BCD
     ↓
6. 选择启动项 → 加载 Windows 启动加载器
   winload.efi（位于 C:\Windows\System32\winload.efi）
     ↓
7. winload.efi 加载内核
   - NTOSKRNL.EXE（内核执行体）
   - HAL.DLL（硬件抽象层）
   - 启动类型的驱动
     ↓
8. 内核初始化（Phase 0 + Phase 1）
     ↓
9. 启动会话管理器（smss.exe）
     ↓
10. 启动 Winlogon.exe → 用户登录
     ↓
11. 启动 explorer.exe → Shell 就绪
```

#### （2）BIOS + MBR 引导（传统系统）

```
1. 上电 → BIOS 自检（POST）
     ↓
2. BIOS 读取 MBR（磁盘 0 号扇区，512 字节）
     ↓
3. MBR 引导代码查找活动分区
     ↓
4. 加载活动分区的引导扇区（VBR）
     ↓
5. VBR 加载 bootmgr（Windows 启动管理器）
     ↓
6. bootmgr 读取 BCD（C:\Boot\BCD）
     ↓
7. 选择启动项 → 加载 winload.exe
     ↓
8. 后续同 UEFI 流程（步骤 7-11）
```

### 5.4 引导相关文件位置

| 文件 | UEFI 路径 | BIOS 路径 | 说明 |
|------|----------|----------|------|
| **bootmgfw.efi / bootmgr** | ESP:\EFI\Microsoft\Boot\ | C:\bootmgr | Windows 启动管理器 |
| **BCD** | ESP:\EFI\Microsoft\Boot\BCD | C:\Boot\BCD | 引导配置数据库 |
| **winload.efi / winload.exe** | C:\Windows\System32\winload.efi | C:\Windows\System32\winload.exe | 内核加载器 |
| **ntoskrnl.exe** | C:\Windows\System32\ntoskrnl.exe | 同左 | 内核执行体 |
| **hal.dll** | C:\Windows\System32\hal.dll | 同左 | 硬件抽象层 |
| **EFI 分区** | ESP（FAT32，100MB+） | — | UEFI 系统分区 |
| **恢复分区** | WinRE 分区（NTFS） | 同左 | Windows 恢复环境 |

### 5.5 物理磁盘到文件的完整映射示例

```
示例：读取 C:\Users\Alice\test.txt

物理磁盘（500 GB SSD）
  │
  ├── GPT 分区表
  │   ├── 分区 1：恢复分区（500 MB，NTFS）
  │   ├── 分区 2：EFI 系统分区（100 MB，FAT32）
  │   └── 分区 3：C: 盘（~498 GB，NTFS） ← 我们的目标
  │
  C: 盘（NTFS 卷）
    │
    ├── 引导扇区（LBA 0）
    │     └── MFT 起始簇号 = 786432
    │
    ├── MFT（簇 786432 起始）
    │     ├── MFT 记录 0：$MFT
    │     ├── MFT 记录 5：根目录（.）
    │     │     └── $INDEX_ROOT → 根目录索引
    │     │           查找 "Users" → MFT 记录 12345
    │     │
    │     ├── MFT 记录 12345：Users 目录
    │     │     └── $INDEX_ROOT → Users 目录索引
    │     │           查找 "Alice" → MFT 记录 23456
    │     │
    │     ├── MFT 记录 23456：Alice 目录
    │     │     └── $INDEX_ROOT → Alice 目录索引
    │     │           查找 "test.txt" → MFT 记录 34567
    │     │
    │     └── MFT 记录 34567：test.txt 文件
    │           ├── $STANDARD_INFORMATION（时间戳、属性）
    │           ├── $FILE_NAME（文件名 test.txt）
    │           └── $DATA → 数据运行列表：
    │                   VCN 0 → LCN 1234567（长度 2 簇 = 8 KB）
    │
    └── 数据区（LCN 1234567 开始的 2 个簇）
          └── test.txt 的实际内容（8 KB 数据）
```

---

## 附：优化后的提示词模板

以下是可复用的文件架构知识查询提示词模板：

```markdown
# 角色
你是一名资深【操作系统/平台】文件系统专家，精通【平台】的文件系统类型、
磁盘结构、系统目录与安全目录，擅长按层次和分类讲清复杂概念。

# 任务
请系统介绍【操作系统/平台】的文件架构，包括：
1. 文件系统类型（主流文件系统的区别、优缺点、适用场景）
2. 核心文件系统结构（引导扇区、元数据表、关键属性、目录索引）
3. 系统目录结构（根目录、系统目录、程序目录、用户目录）
4. 安全相关目录与文件（凭据存储、日志审计、攻击面与加固）
5. 物理架构与逻辑架构（磁盘→分区→卷→文件系统→文件的层次关系）

# 输出要求
- 使用 Markdown
- 按大类、小类组织
- 关键内容用表格对比
- 重要术语给出中英文
- 每个目录或结构说明用途、风险点、安全建议
- 面向：【系统管理员 + 安全工程师】
- 深度：【操作参考 + 安全加固】
- 示例标注适用版本：【当前主流版本】

# 约束
- 不要罗列所有文件，只列核心和关键目录
- 路径必须准确
- 修改系统目录或文件前必须提示备份
- 区分 32 位与 64 位系统差异
- 对高风险操作给出警告
- 文件架构需同时覆盖物理结构和逻辑结构
- 用 ASCII 图展示架构与流程
- 最后附"优化后的提示词模板"
```

**使用说明**：将【操作系统/平台】替换为"Linux""macOS""Android"等，将【当前主流版本】替换为对应系统的版本号，即可生成同等深度的文件架构知识文档。

---

> **总结**：Windows 文件架构是一个从物理磁盘到逻辑文件的多层体系。理解 NTFS 的 MFT/属性/B-Tree 索引，掌握系统目录的结构与功能，熟悉安全相关的 Hive 文件/日志/凭据存储位置，以及物理到逻辑的映射关系，是系统管理员和安全工程师的必备基础。本文从文件系统类型到物理架构再到安全加固，提供了完整的知识地图和操作参考。
