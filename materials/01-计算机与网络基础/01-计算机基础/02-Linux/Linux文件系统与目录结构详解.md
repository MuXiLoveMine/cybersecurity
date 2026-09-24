# Linux 文件系统与目录结构详解

> 本文系统介绍 Linux 文件系统与目录结构，从文件系统基础、磁盘分区与挂载、FHS 目录结构、inode 原理、权限与属性、核心操作命令，到安全加固与故障排查。面向系统管理员、运维工程师和安全工程师，深度覆盖操作参考 + 原理理解 + 安全加固。示例覆盖 Ubuntu/Debian、CentOS/RHEL、Arch 等主流发行版。

---

## 目录

- [一、文件系统基础](#一文件系统基础)
- [二、磁盘、分区与挂载](#二磁盘分区与挂载)
- [三、FHS 目录结构](#三fhs-目录结构)
- [四、inode 与文件元数据](#四inode-与文件元数据)
- [五、权限与属性](#五权限与属性)
- [六、文件与目录操作核心命令](#六文件与目录操作核心命令)
- [七、安全与故障排查](#七安全与故障排查)
- [附：优化后的提示词模板](#附优化后的提示词模板)

---

## 一、文件系统基础

### 1.1 什么是文件系统

文件系统（File System）是操作系统中**组织和存储数据的方式**，负责管理文件的存储、检索、命名、权限和元数据。它定义了数据在磁盘上的组织格式，使应用程序可以通过路径和文件名访问数据，而无需关心物理存储细节。

```
应用程序
   │ open() / read() / write()
   ↓
C 库（glibc）— 系统调用封装
   │ syscall
   ↓
VFS（虚拟文件系统）← Linux 内核的统一抽象层
   │
   ├── 本地磁盘文件系统：ext4、XFS、Btrfs、ZFS
   ├── 伪文件系统：procfs、sysfs、tmpfs、devtmpfs
   ├── 网络文件系统：NFS、CIFS、9p
   └── 集群/分布式文件系统：Ceph、GlusterFS
   ↓
块设备层（磁盘/SSD/RAID/LVM）
```

### 1.2 VFS 虚拟文件系统

VFS（Virtual File System）是 Linux 内核中的**文件系统抽象层**，它定义了所有文件系统必须实现的统一接口，使得：

| VFS 的价值 | 说明 |
|-----------|------|
| **统一接口** | 应用用同一套系统调用（open/read/write）访问不同文件系统 |
| **多种实现** | 同一目录树可以挂载多种文件系统 |
| **目录树统一** | 所有文件系统挂载到同一棵目录树上 |
| **缓存机制** | 统一的 page cache、dentry cache、inode cache |

```
VFS 四个核心对象：

1. 超级块（Superblock）
   代表整个文件系统，存储文件系统元数据
   - 文件系统类型、大小、状态
   - inode 总数、空闲数
   - 块大小

2. inode（索引节点）
   代表一个文件，存储文件元数据
   - 权限、所有者、大小、时间戳
   - 数据块指针
   - 每个 inode 有唯一的 inode 号

3. 目录项（Dentry）
   代表路径中的一个分量，是文件名到 inode 的映射
   - 加速路径解析
   - dentry cache 缓存最近使用的目录项

4. 文件对象（File）
   代表一个打开的文件
   - 文件位置（偏移量）
   - 打开模式
   - 每个进程打开的文件在 fd 表中有一个条目
```

### 1.3 常见文件系统对比

#### （1）本地磁盘文件系统

| 文件系统 | 全称/类型 | 最大单文件 | 最大卷 | 日志/CoW | 突出特性 | 适用场景 |
|---------|----------|-----------|--------|---------|---------|---------|
| **ext4** | Fourth Extended | 16 TB | 1 EB | 日志（ordered） | 稳定、成熟、兼容性好 | 通用服务器、系统盘 |
| **XFS** | X File System | 8 EB | 8 EB | 日志（元数据） | 高性能、大文件、延迟分配 | 数据库、大文件存储、RHEL 默认 |
| **Btrfs** | B-tree FS | 16 EB | 16 EB | CoW（写时复制） | 子卷、快照、校验、压缩、RAID | 桌面、备份、Fedora 默认 |
| **ZFS** | Zettabyte FS | 16 EB | 256 ZB | CoW | 企业级、RAID-Z、快照、数据完整性 | 文件服务器、NAS、存储集群 |
| **F2FS** | Flash-Friendly FS | 4 TB（4KB簇） | 16 TB | 日志 | 专为闪存设计、磨损均衡 | 手机、SSD、嵌入式 |

**ext4 vs XFS vs Btrfs 详细对比**：

| 维度 | ext4 | XFS | Btrfs |
|------|------|-----|-------|
| **成熟度** | ★★★★★ 最高 | ★★★★ 高 | ★★★ 中（但在快速发展） |
| **大文件性能** | ★★★★ | ★★★★★ | ★★★★ |
| **小文件性能** | ★★★★ | ★★★ | ★★★ |
| **数据完整性** | ★★★（仅元数据日志） | ★★★（仅元数据日志） | ★★★★★（校验+CoW） |
| **快照** | ❌ 不支持 | ❌ 不支持 | ✅ 原生支持（高效） |
| **子卷** | ❌ 不支持 | ❌ 不支持 | ✅ 支持 |
| **内置 RAID** | ❌ 不支持 | ❌ 不支持 | ✅ RAID 0/1/10/5/6 |
| **压缩** | 弱（文件级） | ❌ 不支持 | ✅ zstd/zlib/lzo |
| **在线增长** | ✅ 支持 | ✅ 支持 | ✅ 支持 |
| **在线缩小** | ✅ 支持（需卸载） | ❌ 不支持 | ✅ 支持 |
| **恢复工具** | e2fsck、debugfs | xfs_repair | btrfs check |
| **默认发行版** | Ubuntu/Debian | RHEL/CentOS/SUSE | Fedora/OpenSUSE |

#### （2）伪文件系统

伪文件系统（Pseudo File System）不存储实际数据，而是提供内核数据结构的文件接口。

| 文件系统 | 挂载点 | 用途 | 特点 |
|---------|--------|------|------|
| **procfs** | `/proc` | 进程信息、内核参数、系统状态 | 内存生成，不占磁盘 |
| **sysfs** | `/sys` | 设备、驱动、总线信息 | 比 proc 更结构化 |
| **devtmpfs** | `/dev` | 设备文件（自动创建） | udev 管理 |
| **tmpfs** | `/tmp`、`/run` | 内存文件系统 | 断电丢失，速度极快 |
| **devpts** | `/dev/pts` | 伪终端设备 | 终端模拟 |
| **cgroup2** | `/sys/fs/cgroup` | 控制组（资源限制） | 容器基础 |
| **debugfs** | `/sys/kernel/debug` | 内核调试信息 | 调试用 |
| **securityfs** | `/sys/kernel/security** | 安全子系统 | LSM 等 |

```bash
# 查看当前挂载的所有文件系统类型
findmnt -o TARGET,FSTYPE
df -T
```

#### （3）网络文件系统

| 文件系统 | 协议/端口 | 特点 | 适用场景 |
|---------|----------|------|---------|
| **NFS** | TCP/UDP 2049 | Unix 标准、性能好、简单 | Unix/Linux 环境文件共享 |
| **CIFS/SMB** | TCP 445 | Windows 兼容、权限丰富 | 跨平台共享、Windows 环境 |
| **9p** | 9P 协议 | 轻量、虚拟化用 | QEMU/KVM 虚拟机共享 |
| **GlusterFS** | TCP 24007 | 分布式、可扩展 | 集群存储 |
| **CephFS** | TCP 6789+ | 分布式、高可用 | 云存储、大规模集群 |

### 1.4 文件系统选择建议

| 场景 | 推荐 | 理由 |
|------|------|------|
| **系统盘（通用）** | ext4 或 XFS | 成熟稳定，工具完善 |
| **数据库（MySQL/PostgreSQL）** | XFS | 大文件性能好，RHEL 推荐 |
| **大文件存储（视频/备份）** | XFS 或 ZFS | 高吞吐、数据完整性 |
| **桌面/工作站** | ext4 或 Btrfs | ext4 兼容好；Btrfs 快照方便 |
| **SSD / 闪存** | F2FS 或 ext4 | F2FS 专为闪存优化 |
| **临时文件 / 缓存** | tmpfs | 内存文件系统，速度极快 |
| **NAS / 文件服务器** | ZFS 或 Btrfs | 快照、校验、数据完整性 |
| **容器存储** | overlay2 + ext4/xfs | Docker 默认 |
| **U 盘 / 移动硬盘** | exFAT 或 ext4 | exFAT 跨平台；ext4 权限完整 |

---

## 二、磁盘、分区与挂载

### 2.1 物理到逻辑的层次

```
物理磁盘（HDD/SSD/NVMe）
  │
  ├── 分区表（MBR / GPT）
  │     ├── 分区 1（/boot）
  │     ├── 分区 2（/）
  │     └── 分区 3（swap）
  │
  ├── LVM（可选）
  │     ├── 物理卷（PV）
  │     ├── 卷组（VG）
  │     └── 逻辑卷（LV）→ 格式化 → 挂载
  │
  └── RAID（可选）
        ├── RAID 0（条带化）
        ├── RAID 1（镜像）
        ├── RAID 5（校验）
        └── RAID 10（镜像+条带）
```

### 2.2 MBR vs GPT 分区表

| 特性 | MBR（BIOS） | GPT（UEFI） |
|------|-------------|-------------|
| **全称** | Master Boot Record | GUID Partition Table |
| **最大分区数** | 4 个主分区（扩展分区可更多） | 128 个（默认） |
| **最大磁盘容量** | 2 TB | 9.4 ZB（18 EB 可用） |
| **备份** | 无单一备份点 | 头部和尾部各一份 |
| **校验** | 无 | CRC32 校验 |
| **安全启动** | 不支持 | 支持（Secure Boot） |
| **引导代码** | 446 字节在 MBR 中 | 独立 EFI 系统分区 |
| **适用场景** | 旧系统、BIOS 主板 | 现代系统、UEFI 主板 |
| **分区类型** | 用代码标识（如 0x83=Linux） | 用 GUID 标识 |

```bash
# 查看分区表类型
parted /dev/sda print | grep "Partition Table"
gdisk -l /dev/sda | grep "GPT"
```

### 2.3 常用磁盘命令

| 命令 | 用途 | 示例 |
|------|------|------|
| **lsblk** | 列出块设备树 | `lsblk`、`lsblk -f`（含文件系统） |
| **blkid** | 块设备信息（UUID/类型） | `blkid`、`blkid /dev/sda1` |
| **fdisk** | MBR 分区工具 | `fdisk /dev/sda` |
| **parted** | 通用分区工具 | `parted /dev/sda` |
| **gdisk** | GPT 分区工具 | `gdisk /dev/sda` |
| **mkfs** | 格式化（创建文件系统） | `mkfs.ext4 /dev/sda1` |
| **mount** | 挂载 | `mount /dev/sda1 /mnt` |
| **umount** | 卸载 | `umount /mnt` |
| **df** | 磁盘空间 | `df -h`、`df -i` |
| **du** | 目录大小 | `du -sh /dir`、`du -h --max-depth=1` |
| **fsck** | 文件系统检查/修复 | `fsck /dev/sda1` |
| **tune2fs** | 调整 ext2/3/4 参数 | `tune2fs -l /dev/sda1` |
| **xfs_info** | XFS 信息 | `xfs_info /dev/sda1` |
| **btrfs** | Btrfs 管理 | `btrfs filesystem df /` |

#### （1）lsblk / blkid

```bash
# 查看块设备树状结构
lsblk

# 显示文件系统类型和 LABEL/UUID
lsblk -f

# 查看所有块设备的 UUID 和类型
blkid
blkid /dev/sda1
```

#### （2）fdisk / parted / gdisk — 分区工具

```bash
# fdisk：MBR 分区
fdisk /dev/sdb
# 交互命令：n=新建分区, d=删除, p=打印, w=写入, q=退出

# parted：通用（支持 MBR 和 GPT）
parted /dev/sdb
# (parted) mklabel gpt        创建 GPT 分区表
# (parted) mkpart primary 0% 100%  创建使用全部空间的分区
# (parted) print              打印分区表
# (parted) quit               退出

# gdisk：GPT 专用（类 fdisk 界面）
gdisk /dev/sdb
# ? 查看帮助，n 新建分区，w 写入，q 退出
```

> ⚠️ **极高风险**：分区操作会直接修改磁盘分区表，操作错误可能导致数据丢失。操作前务必备份重要数据。先用 `p`（print）确认当前状态，确认无误后再 `w`（write）。生产环境操作前建议先在测试机演练。

#### （3）mkfs — 格式化

```bash
# 格式化为 ext4
mkfs.ext4 /dev/sdb1
mkfs.ext4 -L mydata /dev/sdb1      # 指定卷标

# 格式化为 XFS
mkfs.xfs /dev/sdb1
mkfs.xfs -L mydata /dev/sdb1

# 格式化为 Btrfs
mkfs.btrfs /dev/sdb1

# 格式化为 swap
mkswap /dev/sdb2
swapon /dev/sdb2   # 启用 swap
```

> ⚠️ **极高风险**：`mkfs` 会**删除分区上的所有数据**。操作前务必确认目标分区正确，重要数据已备份。可以先用 `blkid` 或 `mount` 确认分区是否已挂载或有数据。

### 2.4 挂载与卸载

#### （1）mount / umount

```bash
# 挂载分区
mount /dev/sdb1 /data

# 指定文件系统类型
mount -t ext4 /dev/sdb1 /data

# 指定挂载选项
mount -o noatime,nodiratime /dev/sdb1 /data

# 挂载 ISO 镜像（回环设备）
mount -o loop /path/to/image.iso /mnt/iso

# 挂载 NFS 共享
mount -t nfs server:/share /mnt/share

# 挂载 SMB/CIFS 共享
mount -t cifs //server/share /mnt -o username=user,password=pass

# 卸载
umount /data
umount /dev/sdb1

# 强制卸载（占用时，慎用）
umount -f /data

# 懒惰卸载（等不忙了再卸载）
umount -l /data

# 查看挂载信息
mount          # 查看所有挂载
findmnt        # 树状查看（更清晰）
cat /proc/mounts
```

#### （2）挂载选项

| 选项 | 说明 | 安全用途 |
|------|------|---------|
| **defaults** | 默认选项（rw, suid, dev, exec, auto, nouser, async） | — |
| **ro** | 只读挂载 | 数据防篡改、备份盘 |
| **noexec** | 不允许执行二进制文件 | /tmp、/var/tmp 加固 |
| **nosuid** | 忽略 SUID/SGID 位 | 所有非系统分区加固 |
| **nodev** | 不解释设备文件 | 所有非系统分区加固 |
| **noatime** | 不更新访问时间 | 性能优化，减少写入 |
| **nodiratime** | 不更新目录访问时间 | 性能优化 |
| **relatime** | 相对访问时间（折中方案） | 性能+兼容 |
| **sync** | 同步写入（立即刷盘） | 数据安全但慢 |
| **async** | 异步写入（默认） | 性能好但断电可能丢数据 |
| **remount** | 重新挂载（不改挂载点） | 单用户模式改 ro 为 rw |
| **user** | 允许普通用户挂载 | 可移动设备 |
| **users** | 任何用户都可以挂载/卸载 | 共享环境 |
| **_netdev** | 网络文件系统（等网络启动后挂载） | NFS/CIFS |

> **安全加固建议**：
> - `/tmp`、`/var/tmp` 应挂载为 `nodev,nosuid,noexec`
> - `/home` 应挂载为 `nodev,nosuid`
> - 数据分区应挂载为 `nodev,nosuid`
> - 备份盘可挂载为 `ro`（只读）防篡改

#### （3）/etc/fstab — 永久挂载

fstab（file systems table）定义了系统启动时自动挂载的文件系统。

```
fstab 格式（6 个字段，空格/制表符分隔）：

# <设备>        <挂载点>    <类型>    <选项>                   <dump> <pass>
UUID=xxxx-xxxx   /boot      vfat      defaults,noatime         0      2
UUID=xxxxxxxx    /          ext4      errors=remount-ro        0      1
UUID=xxxxxxxx    none       swap      sw                       0      0
UUID=xxxxxxxx    /data      xfs       defaults,noatime,nosuid,nodev  0  0
tmpfs            /tmp       tmpfs     defaults,noatime,nosuid,nodev,size=2G  0 0
```

| 字段 | 说明 |
|------|------|
| **设备** | 可以是 `/dev/sda1`、`UUID=xxx`、`LABEL=xxx` |
| **挂载点** | 挂载到哪个目录 |
| **类型** | 文件系统类型（ext4/xfs/swap/tmpfs/nfs 等） |
| **选项** | 挂载选项（逗号分隔） |
| **dump** | 0=不备份，1=备份（dump 工具用，基本不用了） |
| **pass** | fsck 检查顺序：0=不检查，1=最先（根分区），2=其他 |

**设备标识方式对比**：

| 方式 | 示例 | 优点 | 缺点 |
|------|------|------|------|
| **设备路径** | `/dev/sda1` | 简单直观 | 磁盘顺序变化会变（如插拔后） |
| **UUID** | `UUID=a1b2c3...` | 唯一，不会变 | 长，不好记 |
| **LABEL** | `LABEL=root` | 可读的名称 | 可能重复（需确保唯一） |
| **PARTUUID** | `PARTUUID=xxx` | GPT 分区唯一标识 | 更底层，分区表级 |

```bash
# 获取 UUID / LABEL
blkid
lsblk -f

# 修改 fstab 后测试（不重启）🔑
mount -a    # 挂载 fstab 中所有未挂载的
# 如果有错误会提示，但不会导致系统无法启动

# 查看 fstab 中某行是否正确
findmnt /data    # 能查到就是挂载了
```

> ⚠️ **重要警告**：修改 `/etc/fstab` 前务必备份！如果 fstab 配置错误，系统可能无法启动。修改后先执行 `mount -a` 测试，确认无错误再重启。如果系统因 fstab 无法启动，进入单用户模式或救援模式修复。

### 2.5 LVM 逻辑卷管理

LVM（Logical Volume Manager）是 Linux 的逻辑卷管理系统，在物理磁盘和文件系统之间增加了一个抽象层，支持灵活的空间调整。

```
物理磁盘 / 分区（PV）
   │
   └── 卷组（VG）
         │
         ├── 逻辑卷 1（LV） → 格式化 → 挂载点 /
         ├── 逻辑卷 2（LV） → 格式化 → 挂载点 /home
         ├── 逻辑卷 3（LV） → 格式化 → swap
         └── ...
```

| 概念 | 英文 | 说明 |
|------|------|------|
| **PV** | Physical Volume | 物理卷（磁盘/分区） |
| **VG** | Volume Group | 卷组（多个 PV 组成的存储池） |
| **LV** | Logical Volume | 逻辑卷（从 VG 中划分） |
| **PE** | Physical Extent | 物理块（VG 的最小分配单位，默认 4MB） |
| **LE** | Logical Extent | 逻辑块（对应 PE） |

```bash
# ========== 创建 LVM ==========

# 1. 创建物理卷（PV）🔑
pvcreate /dev/sdb1 /dev/sdc1
pvscan                    # 扫描所有 PV
pvdisplay                 # 查看 PV 详情

# 2. 创建卷组（VG）🔑
vgcreate myvg /dev/sdb1 /dev/sdc1
vgs                       # 查看 VG 概览
vgdisplay myvg            # 查看 VG 详情

# 3. 创建逻辑卷（LV）🔑
lvcreate -L 10G -n mylv myvg    # 创建 10GB 的 LV
lvcreate -l 100%FREE -n data myvg  # 使用全部剩余空间
lvs                       # 查看 LV 概览
lvdisplay /dev/myvg/mylv  # 查看 LV 详情

# 4. 格式化并挂载
mkfs.ext4 /dev/myvg/mylv
mount /dev/myvg/mylv /data


# ========== 扩展 LVM ==========

# 方案 A：添加新磁盘
pvcreate /dev/sdd1
vgextend myvg /dev/sdd1    # 扩展 VG
lvextend -L +5G /dev/myvg/mylv   # 扩展 LV（加 5G）
resize2fs /dev/myvg/mylv   # ext4：调整文件系统大小
# xfs_growfs /data         # XFS：调整文件系统大小（需挂载）

# 方案 B：扩展现有 PV（分区变大后）
pvresize /dev/sdb1
lvextend -r -L +5G /dev/myvg/mylv   # -r 自动调整文件系统
```

### 2.6 RAID

RAID（Redundant Array of Independent Disks）将多块磁盘组合成逻辑磁盘，提供性能提升或冗余保护。

| RAID 级别 | 最小磁盘数 | 可用容量 | 冗余 | 读性能 | 写性能 | 适用场景 |
|----------|-----------|---------|------|--------|--------|---------|
| **RAID 0** | 2 | 100% | ❌ 无 | ↑↑ 高 | ↑↑ 高 | 临时数据、缓存（追求性能） |
| **RAID 1** | 2 | 50% | ✅ 1 块 | ↑ 中 | ↓ 中 | 系统盘、重要数据（追求安全） |
| **RAID 5** | 3 | (n-1)/n | ✅ 1 块 | ↑ 高 | ↓↓ 低 | 读多写少的大容量存储 |
| **RAID 6** | 4 | (n-2)/n | ✅ 2 块 | ↑ 中 | ↓↓↓ 很低 | 大阵列、高可靠要求 |
| **RAID 10** | 4 | 50% | ✅ 每组 1 块 | ↑↑ 高 | ↑ 高 | 数据库、高性能+高可用 |

```bash
# mdadm 创建 RAID 1
mdadm --create /dev/md0 --level=1 --raid-devices=2 /dev/sdb1 /dev/sdc1

# 查看 RAID 状态
cat /proc/mdstat
mdadm --detail /dev/md0

# 标记磁盘故障
mdadm /dev/md0 --fail /dev/sdb1

# 移除故障盘
mdadm /dev/md0 --remove /dev/sdb1

# 添加新盘（重建）
mdadm /dev/md0 --add /dev/sdd1
```

---

## 三、FHS 目录结构

FHS（Filesystem Hierarchy Standard）定义了 Linux 目录结构的标准，使不同发行版保持一致性。

### 3.1 根目录一级结构

```
/                               根目录
├── bin/                        基本命令二进制（所有用户）→ /usr/bin 的软链（现代系统）
├── sbin/                       系统管理二进制（root 用）→ /usr/sbin 的软链
├── lib/                        基本共享库 → /usr/lib 的软链
├── lib64/                      64 位共享库 → /usr/lib64 的软链
├── boot/                       引导加载文件
├── dev/                        设备文件
├── etc/                        系统配置文件
├── home/                       用户主目录
├── root/                       root 用户主目录
├── mnt/                        临时挂载点
├── media/                      可移动媒体挂载点
├── opt/                        可选软件包
├── srv/                        服务数据
├── tmp/                        临时文件
├── usr/                        Unix Software Resources（用户程序/库/文档）
├── var/                        可变数据（日志/缓存/邮件/打印队列）
├── proc/                       进程与内核信息（procfs）
├── sys/                        系统设备信息（sysfs）
└── run/                        运行时数据（tmpfs）
```

### 3.2 各目录详解

#### （1）核心系统目录

| 目录 | 用途 | 典型内容 | 安全关注点 |
|------|------|---------|-----------|
| **/bin** | 所有用户可用的基本命令 | ls, cat, cp, bash 等 | 现代系统通常是 /usr/bin 的符号链接 |
| **/sbin** | 系统管理命令（root 用） | mount, umount, fdisk, ifconfig 等 | 现代系统通常是 /usr/sbin 的符号链接 |
| **/lib** | 基本共享库和内核模块 | libc.so, ld-linux.so 等 | 现代系统通常是 /usr/lib 的符号链接 |
| **/lib64** | 64 位共享库 | 64 位版本的库文件 | 同上 |
| **/boot** | 引导加载文件 | vmlinuz（内核）、initrd、GRUB 配置 | 🔐 限制写权限；内核镜像完整性检查 |
| **/dev** | 设备文件（devtmpfs） | null, zero, sda, tty, random, urandom | 🔐 /dev 下有很多敏感设备；普通用户不应能直接访问磁盘设备 |

**/dev 关键设备文件**：

| 设备 | 类型 | 用途 |
|------|------|------|
| `/dev/null` | 字符 | 空设备（写入被丢弃，读取返回 EOF） |
| `/dev/zero` | 字符 | 零设备（返回无限个 0 字节） |
| `/dev/random` | 字符 | 随机数设备（阻塞，高熵） |
| `/dev/urandom` | 字符 | 随机数设备（非阻塞） |
| `/dev/sda` | 块 | 第一块 SCSI/SATA 磁盘 |
| `/dev/sda1` | 块 | 第一块磁盘的第一个分区 |
| `/dev/tty` | 字符 | 当前终端 |
| `/dev/pts/0` | 字符 | 第一个伪终端 |
| `/dev/shm` | tmpfs | 共享内存 |

#### （2）配置与数据目录

| 目录 | 用途 | 典型内容 | 安全关注点 |
|------|------|---------|-----------|
| **/etc** | 系统配置文件（hosts, passwd, shadow, fstab, ssh, sysconfig 等） | 见下方详解 | 🔐 敏感文件（shadow、密码、密钥）权限必须严格；审计修改 |
| **/home** | 用户主目录 | /home/alice、/home/bob | 🔐 用户私密数据；umask 影响默认权限 |
| **/root** | root 用户主目录 | root 的配置和文件 | 🔐 仅 root 可访问（权限 700） |
| **/var** | 可变数据（日志、缓存、邮件、打印队列等） | 见下方详解 | 🔐 /var/log 含敏感日志；/var/tmp 需加固（nosuid,noexec） |
| **/usr** | Unix Software Resources（用户程序/库/文档/头文件） | bin, sbin, lib, include, share, local | 🔐 /usr/bin 和 /usr/sbin 的文件完整性很重要；SUID 审计 |
| **/opt** | 可选软件包（第三方大型软件） | 如 /opt/google/chrome | 权限通常较宽松，注意路径中是否有可写目录 |
| **/srv** | 服务数据（www, ftp, git 等） | /srv/www, /srv/ftp | Web 根目录权限控制 |

#### （3）临时与运行时目录

| 目录 | 用途 | 典型内容 | 安全关注点 |
|------|------|---------|-----------|
| **/tmp** | 临时文件（所有用户可写） | 临时文件、脚本、socket | 🔐 高风险目录！应挂载 nodev,nosuid,noexec；定期清理 |
| **/var/tmp** | 重启保留的临时文件 | 跨重启的临时数据 | 🔐 同 /tmp 加固要求 |
| **/run** | 运行时数据（tmpfs，重启清空） | pid 文件、socket、锁文件 | 系统进程使用 |
| **/proc** | 进程与内核信息（procfs，内存生成） | cpuinfo, meminfo, sys, <pid>/ | 🔐 /proc/sys 可调整内核参数；部分路径需限制 |
| **/sys** | 设备/驱动/总线信息（sysfs） | block, bus, class, dev, kernel, module | 内核参数调整入口 |
| **/mnt** | 临时挂载点 | 管理员手动挂载用 | — |
| **/media** | 可移动媒体自动挂载点 | cdrom, usb | 用户插入 U 盘自动挂载在此 |

#### （4）/etc 核心文件

```
/etc/
├── passwd                    用户账户信息（不含密码哈希）
├── shadow                    用户密码哈希（root 只读）
├── group                     组信息
├── gshadow                   组密码
├── hosts                     主机名→IP 映射
├── hostname                  主机名
├── resolv.conf               DNS 配置（可能是 symlink）
├── nsswitch.conf             名称服务切换
├── fstab                     文件系统挂载表
├── crontab                   全局定时任务
├── cron.d/                   cron 任务目录
├── profile                   全局 Shell 配置（登录时）
├── bash.bashrc               全局 bashrc（交互式）
├── environment               全局环境变量
├── sudoers                   sudo 配置（用 visudo 编辑）
├── shells                    可用 Shell 列表
├── login.defs                登录默认配置
├── adduser.conf              添加用户默认配置
├── default/                  默认配置目录
│   └── useradd               useradd 默认值
├── skel/                     新用户模板文件（.bashrc .profile 等）
├── sysctl.conf               内核参数
├── sysctl.d/                 内核参数片段
├── ssh/                      SSH 配置
│   ├── sshd_config           服务端配置
│   └── ssh_config            客户端配置
├── apt/                      APT 配置（Debian/Ubuntu）
│   ├── sources.list          软件源
│   └── sources.list.d/       第三方源
├── yum/                      YUM 配置（RHEL/CentOS）
│   └── yum.conf
├── yum.repos.d/              YUM 仓库配置
├── network/                  网络配置（旧 Debian）
├── sysconfig/                系统配置（RHEL 系）
│   ├── network-scripts/      网络接口配置
│   └── selinux               SELinux 配置
├── services                  服务名→端口映射
├── protocols                 协议号映射
├── rpc                       RPC 程序号映射
├── security/                 安全配置
│   ├── access.conf           访问控制
│   └── limits.conf           资源限制（ulimit）
├── pam.d/                    PAM 配置
├── logrotate.d/              日志轮转配置
├── systemd/                  systemd 配置
│   ├── system/               系统级 unit
│   └── journald.conf         日志配置
├── audit/                    auditd 配置
├── rsyslog.conf              syslog 配置
└── udev/                     udev 规则
```

**/etc 关键安全文件**：

| 文件 | 权限 | 说明 | 风险等级 |
|------|------|------|---------|
| `/etc/shadow` | 640, root:shadow | 用户密码哈希 | ★★★★★ |
| `/etc/sudoers` | 440, root:root | sudo 配置 | ★★★★ |
| `/etc/passwd` | 644, root:root | 用户信息 | ★★ |
| `/etc/ssh/sshd_config` | 644, root:root | SSH 服务端配置 | ★★★ |
| `/etc/fstab` | 644, root:root | 挂载表 | ★★★ |
| `/etc/hosts` | 644, root:root | 主机名解析 | ★★ |

#### （5）/var 核心目录

```
/var/
├── log/                      系统日志
│   ├── syslog                系统日志（Debian）
│   ├── messages              系统日志（RHEL）
│   ├── auth.log              认证日志（Debian）
│   ├── secure                安全日志（RHEL）
│   ├── kern.log              内核日志
│   ├── cron                  cron 日志
│   ├── dpkg.log              包管理日志（Debian）
│   ├── yum.log               包管理日志（RHEL）
│   ├── nginx/                Nginx 日志
│   └── audit/                审计日志
├── spool/                    脱机数据
│   ├── mail/                 邮件队列
│   ├── cron/                 cron 任务
│   └── cups/                 打印队列
├── cache/                    缓存数据
│   └── apt/                  APT 包缓存
├── lib/                      应用状态数据
│   ├── dpkg/                 dpkg 数据库
│   ├── rpm/                  RPM 数据库
│   └── systemd/              systemd 状态
├── tmp/                      重启保留的临时文件
├── run/                      → /run（软链接）
├── lock/                     锁文件
└── www/                      Web 根目录（有的系统）
```

#### （6）/usr 核心目录

```
/usr/
├── bin/                      用户命令二进制
├── sbin/                     系统管理命令
├── lib/                      共享库和内核模块
├── lib64/                    64 位共享库
├── local/                    本地安装的软件（管理员手动安装）
│   ├── bin/
│   ├── sbin/
│   ├── lib/
│   └── etc/
├── include/                  C/C++ 头文件
├── share/                    架构无关的共享数据
│   ├── man/                  man 手册
│   ├── doc/                  文档
│   ├── zoneinfo/             时区数据
│   ├── dict/                 字典
│   └── locale/               本地化数据
└── src/                      内核源代码（可选）
```

### 3.3 用户目录结构

```
~（用户主目录）
├── .bashrc                   bash 交互式配置
├── .bash_profile             bash 登录配置
├── .bash_logout              bash 退出时执行
├── .profile                  Shell 通用登录配置
├── .bash_history             命令历史
├── .ssh/                     SSH 密钥和配置
│   ├── id_rsa                RSA 私钥（600）
│   ├── id_rsa.pub            RSA 公钥（644）
│   ├── authorized_keys       授权公钥（600）
│   └── config                SSH 客户端配置
├── .local/                   用户本地数据
├── .config/                  应用配置（XDG 规范）
├── .cache/                   缓存
├── Desktop/                  桌面
├── Documents/                文档
├── Downloads/                下载
├── Pictures/                 图片
└── ...
```

> 🔐 **安全提示**：`~/.ssh/` 目录和其中的私钥文件权限必须严格（目录 700，私钥 600），否则 SSH 会拒绝使用。`authorized_keys` 权限 600，否则公钥认证可能不生效。

---

## 四、inode 与文件元数据

### 4.1 inode 是什么

inode（index node，索引节点）是 Unix/Linux 文件系统中**存储文件元数据的数据结构**。每个文件对应一个 inode，每个 inode 有唯一的 inode 号。

```
inode 包含的内容：
  ✓ 文件类型（普通文件/目录/符号链接/设备/FIFO/套接字）
  ✓ 权限位（mode）
  ✓ 所有者 UID / 所属组 GID
  ✓ 文件大小（字节）
  ✓ 硬链接数
  ✓ 时间戳：
      - atime：访问时间（Access Time）
      - mtime：修改时间（Modification Time，内容修改）
      - ctime：变更时间（Change Time，元数据修改）
  ✓ 数据块指针（直接/间接/双重间接/三重间接）

✗ inode 不包含：
  文件名（文件名存在目录项 dentry 中）
```

**文件的完整定位流程**：

```
路径：/home/alice/doc.txt

1. 根目录 inode（已知 inode 号，通常是 2）
   ↓ 读取根目录数据块
2. 找到 "home" 目录项 → inode 号 X
   ↓ 读取 inode X
3. 读取 home 目录的数据块
   ↓ 找到 "alice" 目录项 → inode 号 Y
4. 读取 inode Y
   ↓ 读取 alice 目录的数据块
5. 找到 "doc.txt" 目录项 → inode 号 Z
   ↓ 读取 inode Z
6. 从 inode Z 的数据块指针找到数据块
   ↓
7. 读取文件内容
```

### 4.2 超级块、目录项、数据块

| 概念 | 英文 | 说明 |
|------|------|------|
| **超级块** | Superblock | 存储文件系统整体信息（大小、inode 数、块大小等） |
| **inode 表** | inode Table | 所有 inode 的集合 |
| **目录项** | Directory Entry | 目录中的条目，包含文件名和 inode 号 |
| **数据块** | Data Block | 存储实际文件内容的块 |
| **块组** | Block Group | ext4 中将磁盘分成多个块组，每个组有独立的 superblock/inode 表/数据块 |

```
ext4 块组结构：

┌─────────────────────────────────────────────────────────┐
│                    块组 n                                │
├──────┬──────┬───────┬──────┬───────┬──────┬────────────┤
│ 超级  │ GDT  │ 块位图 │ inode│ inode │ 块位图│  数据块    │
│ 块    │      │       │ 位图  │ 表    │      │            │
└──────┴──────┴───────┴──────┴───────┴──────┴────────────┘

每个块组有：
  - 超级块副本（部分组有）
  - 组描述符表
  - 块位图（标记哪些块已用）
  - inode 位图（标记哪些 inode 已用）
  - inode 表
  - 数据块
```

### 4.3 硬链接与软链接

| 特性 | 硬链接（Hard Link） | 软链接/符号链接（Symbolic Link） |
|------|-------------------|------------------------------|
| **本质** | 多个文件名指向同一个 inode | 独立文件，内容是目标路径 |
| **inode 号** | 相同 | 不同 |
| **跨文件系统** | ❌ 不可以 | ✅ 可以 |
| **目录链接** | ❌ 不可以（防止环） | ✅ 可以 |
| **目标删除后** | 文件仍存在（链接数-1） | 链接失效（死链接） |
| **相对路径** | — | 支持（相对链接） |
| **大小** | 不占用额外 inode 和数据块 | 占用一个 inode + 少量数据 |
| **命令** | `ln` | `ln -s` |
| **文件类型** | 普通文件（-） | 符号链接（l） |

```bash
# 创建硬链接
ln /path/to/source /path/to/link

# 创建软链接（符号链接）
ln -s /path/to/source /path/to/link
ln -s ../relative/path /path/to/link   # 相对路径软链接

# 查看 inode 号
ls -li filename

# 查看文件的硬链接数
ls -l filename
# 第二个字段就是硬链接数
```

### 4.4 inode 相关命令

```bash
# 查看文件 inode 号
ls -li filename

# 查看文件详细元数据
stat filename
stat -f /path    # 查看文件系统信息（不是单个文件）

# 查看 inode 使用情况（inode 空间）
df -i
# Filesystem      Inodes   IUsed   IFree IUse% Mounted on
# /dev/sda1      3276800  123456 3153344    4% /

# 查看文件系统 inode 总数（ext4）
tune2fs -l /dev/sda1 | grep "Inode count"

# 通过 inode 号查找文件
find /path -inum <inode-number>
```

### 4.5 inode 耗尽问题

```
什么是 inode 耗尽：
  文件系统创建时就确定了 inode 总数（默认按块数比例）
  如果大量小文件（每个占一个 inode），可能空间还没用完
  但 inode 已经用完了，无法创建新文件

排查方法：
  1. df -i 检查 inode 使用率
  2. 如果 IUse% 接近 100%，就是 inode 耗尽

定位哪个目录小文件多：
  for d in /*/; do echo "$d: $(find $d -xdev -type f | wc -l)"; done
  # 逐层深入，找到小文件集中的目录

解决方法：
  1. 删除无用的小文件
  2. 重新格式化（创建时指定更多 inode）
     mkfs.ext4 -N 10000000 /dev/sdb1  # 指定 inode 数
  3. 使用其他文件系统（XFS/Btrfs inode 是动态的）
```

---

## 五、权限与属性

### 5.1 基础权限位（rwx）

```
ls -l 输出的 10 位权限：

-rwxr-xr--  1 user group  size date filename
││││││││││
│││││││││└── 其他用户（Other）：只读
││││││││└─── 其他用户执行位
│││││││└──── 其他用户写位
││││││└───── 其他用户读位
│││││└────── 所属组（Group）：读+执行
││││└─────── 组执行位
│││└──────── 组写位
││└───────── 组读位
│└────────── 所有者（Owner/User）：读+写+执行
└─────────── 文件类型（-普通 d目录 l符号链接 b块设备 c字符设备 p管道 s套接字）
```

**数字表示法**：

| 权限 | 读（r） | 写（w） | 执行（x） |
|------|--------|--------|----------|
| **值** | 4 | 2 | 1 |

```
rwx = 4+2+1 = 7
rw- = 4+2+0 = 6
r-x = 4+0+1 = 5
r-- = 4+0+0 = 4
--- = 0+0+0 = 0

常见组合：
  755 = rwxr-xr-x   所有者全控，其他读+执行（可执行文件/目录）
  644 = rw-r--r--   所有者读写，其他只读（普通文件）
  600 = rw-------   仅所有者读写（私密文件，如 SSH 私钥）
  700 = rwx------   仅所有者全控（私密目录，如 ~/.ssh）
  775 = rwxrwxr-x   所有者+组全控，其他读执行（共享目录）
  777 = rwxrwxrwx   ⚠️ 完全开放（尽量不用）
```

### 5.2 umask

umask（user file-creation mask）定义了**新建文件/目录时默认去掉哪些权限**。

| umask 值 | 文件默认权限 | 目录默认权限 | 说明 |
|---------|------------|------------|------|
| **022** | 644 (rw-r--r--) | 755 (rwxr-xr-x) | 系统默认（root 和普通用户） |
| **027** | 640 (rw-r-----) | 750 (rwxr-x---) | 更严格，其他用户无权限 |
| **077** | 600 (rw-------) | 700 (rwx------) | 最严格，仅所有者 |
| **002** | 664 (rw-rw-r--) | 775 (rwxrwxr-x) | 组内协作（同组用户可写） |

```bash
# 查看当前 umask
umask
umask -S    # 符号形式显示

# 临时设置 umask
umask 027

# 永久设置（全局）
# 在 /etc/profile 或 /etc/bashrc 中添加：
umask 027

# 用户级：~/.bashrc 或 ~/.profile
```

### 5.3 特殊权限位

| 权限 | 文件上的作用 | 目录上的作用 | 数字表示 | 字母表示 |
|------|-------------|-------------|---------|---------|
| **SUID** (Set UID) | 执行时获得文件**所有者**的权限 | 无意义 | 4000 | s（所有者 x 位） |
| **SGID** (Set GID) | 执行时获得文件**所属组**的权限 | 新建文件继承目录的**所属组** | 2000 | s（组 x 位） |
| **Sticky Bit** | 无意义 | 只有文件所有者/root 能删除自己的文件 | 1000 | t（其他 x 位） |

```bash
# 设置 SUID
chmod u+s /path/to/program
chmod 4755 /path/to/program

# 设置 SGID（目录）
chmod g+s /data/shared
chmod 2775 /data/shared

# 设置 Sticky Bit
chmod +t /tmp
chmod 1777 /tmp

# 查找 SUID 文件（提权审计）
find / -perm -4000 -type f 2>/dev/null

# 查找 SGID 文件
find / -perm -2000 -type f 2>/dev/null

# 查找有 Sticky Bit 的目录
find / -perm -1000 -type d 2>/dev/null
```

> ⚠️ **安全提示**：SUID 程序是提权的常见途径。有漏洞的 SUID 程序可被用来获得 root 权限。应定期审计系统中的 SUID/SGID 文件，移除不必要的。

### 5.4 ACL（访问控制列表）

ACL 提供比传统 rwx 更细粒度的权限控制，可以为**单个用户或单个组**设置权限。

```bash
# 安装 ACL 工具
# Debian/Ubuntu
apt install acl
# RHEL/CentOS
yum install acl

# 文件系统需要挂载 acl 选项（现代系统默认支持）
# /etc/fstab 中加 acl 选项
# UUID=xxx /data ext4 defaults,acl 0 0

# ========== 查看 ACL ==========
getfacl filename

# ========== 设置 ACL ==========

# 给用户 alice 读写执行权限
setfacl -m u:alice:rwx filename

# 给组 developers 读权限
setfacl -m g:developers:r filename

# 给其他用户设置只读
setfacl -m o::r filename

# 设置默认 ACL（目录内新建的文件自动继承）
setfacl -m d:u:alice:rwx /data/shared
setfacl -m d:g:developers:rwx /data/shared

# 递归设置
setfacl -R -m u:alice:rwx /data/

# ========== 删除 ACL ==========

# 删除单个用户的 ACL
setfacl -x u:alice filename

# 删除所有 ACL
setfacl -b filename

# 删除默认 ACL
setfacl -k /dir
```

### 5.5 文件属性（chattr / lsattr）

ext2/3/4 和其他一些文件系统支持额外的文件属性（attributes），比 ACL 更底层。

| 属性 | 说明 | 安全用途 |
|------|------|---------|
| **a** (append) | 只能追加写入，不能修改/删除已有内容 | 日志文件防篡改 |
| **i** (immutable) | 不可变：不能修改/删除/重命名/链接 | 关键配置文件保护 |
| **d** (no dump) | dump 备份时忽略 | — |
| **s** (secure deletion) | 删除时用 0 覆盖数据块 | 安全删除 |
| **u** (undeletable) | 删除后可恢复 | 防误删 |
| **c** (compressed) | 自动压缩 | 节省空间 |
| **e** (extent) | 使用 extent 映射（ext4 默认） | — |
| **j** (journaled data) | 数据也记录日志 | 数据安全 |

```bash
# 查看文件属性
lsattr filename
lsattr -d /dir        # 查看目录属性
lsattr -R /dir        # 递归查看

# 设置不可变属性（需 root）🔑
chattr +i /etc/sudoers
chattr +i /etc/shadow

# 取消不可变属性
chattr -i /etc/sudoers

# 设置只能追加
chattr +a /var/log/secure.log

# 取消追加属性
chattr -a /var/log/secure.log
```

> 🔐 **安全提示**：`chattr +i` 设置的文件即使 root 也不能修改/删除，是保护关键配置文件的好方法。但也要注意：攻击者入侵后可能用 `chattr +i` 锁定恶意文件，使其难以删除。排查入侵时注意检查异常的 immutable 文件。

### 5.6 chmod / chown / chgrp

```bash
# ========== chmod 修改权限 ==========

# 数字方式
chmod 755 filename
chmod 644 filename
chmod 600 ~/.ssh/id_rsa

# 符号方式
chmod u+x filename           # 所有者加执行权限
chmod g-w filename           # 组减写权限
chmod o-rwx filename         # 其他用户去掉所有权限
chmod a+r filename           # 所有人加读权限
chmod ug=rw filename         # 所有者和组设为读写
chmod -R 644 /path/to/dir    # 递归修改

# ========== chown 修改所有者 ==========
# 需 root 权限🔑

chown user filename                  # 修改所有者
chown user:group filename           # 同时修改所有者和组
chown user: filename                # 组设为用户主组
chown :group filename               # 只改组
chown -R user:group /dir            # 递归修改

# ========== chgrp 修改组 ==========

chgrp groupname filename
chgrp -R groupname /dir
```

> ⚠️ **风险提示**：`chmod -R 777` 会给所有文件加执行权限，极其危险。`chown -R` 递归修改前确认路径正确。

---

## 六、文件与目录操作核心命令

### 6.1 基本操作

| 命令 | 用途 | 核心参数/用法 |
|------|------|--------------|
| **ls** | 列出目录内容 | `-l` 详细、`-a` 隐藏、`-h` 人类可读、`-R` 递归、`-i` inode、`-t` 按时间排序、`-S` 按大小排序 |
| **cd** | 切换目录 | `~` 回家、`-` 回上次、`..` 上一级、`/` 根目录 |
| **pwd** | 显示当前路径 | `-P` 物理路径（解引用符号链接） |
| **mkdir** | 创建目录 | `-p` 创建多级、`-m` 指定权限 |
| **rmdir** | 删除空目录 | `-p` 删除多级空目录 |
| **cp** | 复制 | `-r` 递归、`-a` 归档（保留权限/时间/所有者）、`-i` 交互提示、`-u` 仅更新 |
| **mv** | 移动/重命名 | `-i` 交互、`-f` 强制、`-u` 仅更新 |
| **rm** | 删除 | `-r` 递归、`-f` 强制、`-i` 交互 |
| **touch** | 创建文件/改时间 | `-a` 仅改访问时间、`-m` 仅改修改时间、`-t` 指定时间 |
| **file** | 识别文件类型 | `-b` 仅输出类型、`-i` MIME 类型 |
| **stat** | 文件详细信息 | `stat file`、`stat -f /path`（文件系统信息） |
| **tree** | 树形显示目录 | `-d` 仅目录、`-L N` 深度、`-I pattern` 排除 |

```bash
# ls 常用组合
ls -la             # 详细列表 + 隐藏文件
ls -lh             # 人类可读大小
ls -ltr            # 按时间排序（最新在底部）
ls -lS             # 按大小排序（大的在前）
ls -li             # 显示 inode 号
ls -R              # 递归列出

# mkdir 创建多级目录
mkdir -p a/b/c/d

# cp 归档复制（保留所有属性）
cp -a source/ dest/

# 安全删除（交互模式）
rm -i file.txt

# ⚠️ 强制递归删除（危险！）
rm -rf /path/to/dir

# touch 创建多个文件
touch file1.txt file2.txt file3.txt

# 查看文件类型
file /bin/bash
file image.png

# 树状查看目录结构
tree -L 2 /etc
```

> ⚠️ **最高风险警告**：`rm -rf /` 会删除整个系统的所有文件！`rm -rf /path/*` 前务必确认路径正确，建议先 `ls /path/*` 确认。生产环境中可以给 `rm` 加别名或安装 `trash-cli` 替代。

### 6.2 查找命令

| 命令 | 用途 | 核心参数 |
|------|------|---------|
| **find** | 高级文件查找（递归、多条件） | 见下方详解 |
| **locate** | 快速文件名查找（基于数据库） | `-i` 忽略大小写、`-r` 正则、`-b` 只匹配 basename |
| **which** | 查找可执行文件路径 | `-a` 显示所有匹配 |
| **whereis** | 查找二进制/源码/man 手册 | `-b` 仅二进制、`-m` 仅 man |
| **type** | 显示命令类型（别名/内置/外部） | `-a` 所有位置、`-p` 路径 |

#### find 命令详解

```
find 语法：
  find [路径] [选项] [表达式] [操作]

常用测试条件：
  -name "pattern"      按文件名（支持通配符）
  -iname "pattern"     不区分大小写
  -type f/d/l/b/c/s/p  按类型（文件/目录/链接/块/字符/套接字/管道）
  -size +10M           大小大于 10M（+大于 -小于 无符号=等于）
  -mtime -7            7 天内修改（天）
  -mmin -60            60 分钟内修改（分钟）
  -atime -7            7 天内访问
  -ctime -7            7 天内元数据变更
  -newer file          比 file 更新的文件
  -user username       指定所有者
  -group groupname     指定组
  -uid UID             指定 UID
  -perm 755            权限精确等于 755
  -perm -4000          有 SUID 位（至少有这些位）
  -perm /u+x           所有者有执行权限（有任意一位即可）
  -maxdepth N          最大深度
  -mindepth N          最小深度
  -empty               空文件/空目录
  -path "pattern"      路径匹配
  -regex "pattern"     正则匹配

常用操作：
  -print               打印（默认）
  -delete              删除（危险！）
  -exec command {} \;  对每个文件执行命令
  -ok command {} \;    执行前确认
  -ls                  类似 ls -l 的输出
```

```bash
# 按名称查找
find /etc -name "*.conf"
find /etc -iname "host*"

# 按类型查找
find / -type l -ls 2>/dev/null         # 所有符号链接
find /var/log -type f -name "*.log"   # 所有 .log 文件

# 按大小查找
find / -size +100M -type f 2>/dev/null   # 大于 100MB 的文件
find /tmp -size -1k -type f              # 小于 1KB 的文件

# 按时间查找
find /var/log -mtime -7 -type f     # 7 天内修改过的文件
find / -mmin -120 -type f 2>/dev/null  # 2 小时内修改的文件
find / -atime +30 -type f 2>/dev/null   # 30 天未访问的文件

# 按权限查找（安全审计）
find / -perm -4000 -type f 2>/dev/null    # SUID 文件
find / -perm -2000 -type f 2>/dev/null    # SGID 文件
find / -perm /6000 -type f 2>/dev/null    # SUID 或 SGID
find /tmp -perm -o+w -type d 2>/dev/null  # 其他用户可写的目录

# 按所有者查找
find /home -user alice -type f
find / -nouser -type f 2>/dev/null    # 无有效所有者的文件（孤儿文件）

# 组合条件
find /var -type f -name "*.log" -size +10M -mtime +30

# 限制深度
find /etc -maxdepth 2 -name "*.conf"

# 对找到的文件执行操作
find /tmp -name "*.tmp" -delete                   # 删除（危险！）
find . -name "*.txt" -exec cp {} /backup/ \;     # 复制到备份目录
find / -perm -4000 -ls 2>/dev/null               # 列出 SUID 文件详情
find . -name "*.bak" -ok rm {} \;                # 确认后删除
```

> ⚠️ **风险提示**：`find ... -delete` 会直接删除匹配的文件，不可恢复。使用前先用不带 `-delete` 的命令确认匹配结果正确。

```bash
# locate 快速查找（基于 updatedb 数据库）
locate filename
locate -i filename        # 不区分大小写
locate -r "\.conf$"       # 正则匹配
updatedb                  # 更新数据库（需 root）🔑

# which 查找可执行文件
which python3
which -a python3          # 所有匹配

# whereis 查找二进制+源码+man
whereis python3
whereis -b python3        # 仅二进制

# type 查看命令类型
type ls
type cd
type -a python3
```

### 6.3 链接与文件信息

```bash
# 创建硬链接
ln /path/to/source /path/to/hardlink

# 创建软链接（符号链接）
ln -s /path/to/source /path/to/symlink
ln -s ../relative/path /path/to/symlink    # 相对路径

# 查看 inode
ls -li filename
stat filename

# 查看文件类型
file filename
file -i filename          # MIME 类型

# 查看文件系统信息
stat -f /
df -T

# 树形显示目录
tree -L 2 /
tree -d -L 3 /etc          # 仅目录，3 层深度
```

---

## 七、安全与故障排查

### 7.1 权限配置错误排查

```
常见权限问题与排查：

1. 无法访问文件
   → 检查文件本身权限：ls -l filename
   → 检查每一级目录权限：namei -l /path/to/file
   → 检查 ACL：getfacl filename
   → 检查文件属性：lsattr filename
   → 检查 SELinux：ls -Z filename / audit2why

2. 无法执行程序
   → 检查 x 权限
   → 检查是否为 noexec 挂载
   → 检查 ELF 架构（32/64 位）
   → 检查动态链接库：ldd program

3. 应用无法写文件
   → 检查目录是否有 w 权限（创建文件）
   → 检查文件是否有 w 权限（修改文件）
   → 检查磁盘空间：df -h
   → 检查 inode：df -i
   → 检查 SELinux / AppArmor 日志

4. suid 程序不工作
   → 检查是否在 nosuid 挂载的分区
   → 检查程序是否为脚本（脚本 SUID 无效）
   → 检查文件系统是否支持 SUID
```

```bash
# 检查路径上每一级的权限
namei -l /home/alice/documents/report.txt

# 检查文件系统挂载选项
findmnt /tmp
mount | grep /tmp

# 检查 SELinux 上下文
ls -Z /var/www/html/
ps -eZ | grep httpd

# 查看 SELinux 拒绝
ausearch -m avc -ts recent
```

### 7.2 挂载选项安全加固

**推荐的安全挂载选项**：

| 分区 | 推荐选项 | 理由 |
|------|---------|------|
| **/tmp** | `nodev,nosuid,noexec` | 临时目录最危险，攻击者常在此放恶意程序 |
| **/var/tmp** | `nodev,nosuid,noexec` | 同 /tmp，且重启保留 |
| **/dev/shm** | `nodev,nosuid,noexec,size=2G` | 共享内存，限制大小和权限 |
| **/home** | `nodev,nosuid` | 用户目录不应有设备文件和 SUID |
| **/var** | `nodev,nosuid` | 可变数据区 |
| **数据分区** | `nodev,nosuid` | 数据分区不应有特殊权限 |
| **备份分区** | `ro`（只读挂载时） | 防篡改 |
| **/boot** | `nodev,nosuid,noexec` | 引导分区 |

> 注意：根分区 `/` 不能加 noexec、nodev、nosuid，否则系统无法正常工作。

```bash
# 临时测试加固选项
mount -o remount,noexec,nosuid,nodev /tmp

# 永久修改（/etc/fstab）
# UUID=xxx /tmp tmpfs defaults,noexec,nosuid,nodev,size=2G 0 0
```

### 7.3 高风险操作汇总

| 操作 | 风险等级 | 说明 | 安全建议 |
|------|---------|------|---------|
| `rm -rf /` | ★★★★★ | 删除整个系统 | 永远不要执行！用 `trash-cli` 替代 rm |
| `rm -rf /path/*` | ★★★★ | 路径错误会删错 | 先 `ls /path/*` 确认，再删除 |
| `mkfs` | ★★★★ | 格式化会清除所有数据 | 先确认目标设备正确，重要数据备份 |
| `fdisk / parted` | ★★★★ | 分区表修改错误会丢失数据 | 操作前打印确认，测试环境演练 |
| `dd` | ★★★★ | 直接写磁盘，写错位置就完蛋 | 输入输出确认清楚，先 dry-run |
| `chmod -R 777` | ★★★ | 所有文件可执行，安全隐患极大 | 不要用 777，用精确权限 |
| `chown -R` | ★★★ | 递归改所有者，路径错了影响很大 | 先确认路径和用户 |
| `find -delete` | ★★★★ | 误匹配会删除意外文件 | 先不带 -delete 确认结果 |
| `echo > file` | ★★★ | 会清空文件内容 | 用 `>>` 追加，或先备份 |
| `> file` | ★★★ | 清空文件 | 同上 |
| 修改 `/etc/fstab` | ★★★★ | 错误会导致系统无法启动 | 修改前备份，改后 mount -a 测试 |
| 修改 `/etc/sudoers` | ★★★ | 语法错误导致 sudo 不可用 | 必须用 `visudo` 编辑 |

### 7.4 文件系统故障排查

```
常见问题与解决：

1. 磁盘满了（No space left on device）
   → df -h 查看哪个分区满了
   → du -sh /* 找大目录
   → du -h --max-depth=1 /var | sort -h
   → 找大文件：find / -size +100M -type f
   → 日志轮转检查：ls -lh /var/log/

2. inode 满了（No space left on device 但 df -h 有空间）
   → df -i 确认
   → 找小文件多的目录：遍历计数
   → 删除无用小文件

3. 文件系统只读（Read-only file system）
   → mount | grep /  确认 ro 状态
   → 可能是磁盘错误触发的自动保护
   → 检查 dmesg 中的 I/O 错误
   → 尝试重新挂载：mount -o remount,rw /
   → 不行的话备份数据，fsck 检查

4. 文件删了空间没释放
   → 文件被进程占用（句柄未关）
   → lsof | grep deleted 找到占用进程
   → 重启进程或 truncate 文件释放空间

5. 误删文件恢复
   → 立刻卸载分区（减少覆盖）
   → ext4：extundelete / debugfs
   → XFS：xfs_restore（需要备份）
   → Btrfs/ZFS：从快照恢复
   → 最好的恢复是有备份！
```

```bash
# 查找占用已删除文件的进程
lsof | grep deleted

# 查看 I/O 错误
dmesg | grep -i error
dmesg | grep -i "I/O error"

# 文件系统检查（需卸载）
umount /dev/sdb1
fsck /dev/sdb1
# ext4
e2fsck -f /dev/sdb1
# XFS
xfs_repair /dev/sdb1
```

> ⚠️ **风险提示**：fsck 对已挂载的文件系统执行可能会造成更严重的损坏。务必先卸载再检查。根分区需要进入单用户模式或救援模式检查。

### 7.5 日志与恢复

**相关日志位置**：

| 日志 | 路径 | 用途 |
|------|------|------|
| **系统日志** | `/var/log/syslog`（Debian）<br>`/var/log/messages`（RHEL） | 系统整体信息 |
| **内核日志** | `/var/log/kern.log`（Debian）<br>`dmesg` 命令 | 内核/驱动/硬件错误 |
| **文件系统日志** | 文件系统内部（元数据日志） | 崩溃恢复 |
| **审计日志** | `/var/log/audit/audit.log` | 文件访问审计事件 |

**恢复工具**：

| 文件系统 | 检查/修复 | 备份/恢复 |
|---------|----------|----------|
| **ext4** | fsck / e2fsck | dump/restore、快照（LVM） |
| **XFS** | xfs_repair | xfsdump / xfsrestore |
| **Btrfs** | btrfs check | btrfs subvolume snapshot |
| **ZFS** | zpool scrub | zfs snapshot / zfs rollback |

### 7.6 安全加固清单

```
文件系统安全加固 TOP 15：

1. 分区策略
   □ 单独挂载 /tmp、/var、/home、/boot
   □ 合理分配各分区大小，避免占满

2. 挂载选项加固
   □ /tmp 挂载为 nodev,nosuid,noexec
   □ /var/tmp 挂载为 nodev,nosuid,noexec
   □ /dev/shm 限制大小并加固
   □ /home 挂载为 nodev,nosuid
   □ 数据分区挂载为 nodev,nosuid

3. 权限控制
   □ 关键配置文件权限正确（shadow 640、ssh_host_key 600）
   □ 关键目录权限正确（/root 700、~/.ssh 700）
   □ 审计 SUID/SGID 文件，移除不必要的
   □ 关键配置文件加 immutable 属性（chattr +i）

4. 配额管理
   □ 启用磁盘配额，防止用户占满磁盘
   □ 配置 inode 配额

5. 文件完整性
   □ 安装 AIDE 或 Tripwire，定期校验
   □ 定期检查关键文件完整性

6. 日志与审计
   □ 配置 auditd 监控关键文件访问
   □ 配置日志轮转，防止日志占满磁盘
   □ 日志集中收集

7. 特殊文件清理
   □ 定期清理 /tmp 和 /var/tmp
   □ 查找并处理无主文件（nouser/nogroup）
   □ 查找可疑的 SUID/SGID 文件

8. 数据备份
   □ 定期备份关键数据
   □ 测试恢复流程
   □ 使用快照（LVM/Btrfs/ZFS）
```

---

## 附：优化后的提示词模板

以下是可复用的文件系统知识查询提示词模板：

```markdown
# 角色
你是一名资深【系统/平台】文件系统专家，精通文件系统原理、目录标准、存储管理与安全加固，
擅长按层次和分类讲清复杂概念。

# 任务
请系统介绍【操作系统】的文件系统与目录结构，包括：
1. 文件系统基础（定义、抽象层、主流文件系统对比）
2. 磁盘、分区与挂载（分区表、格式化、挂载、fstab、LVM、RAID）
3. 目录结构标准（各目录用途、典型内容、安全关注点）
4. inode 与元数据（inode、超级块、目录项、硬软链接、inode 耗尽）
5. 权限与属性（基础权限、特殊权限、ACL、扩展属性）
6. 核心操作命令（每个命令附语法、参数、示例）
7. 安全与故障排查（权限错误、挂载加固、高风险操作、数据恢复）

# 输出要求
- 使用 Markdown
- 按大类、小类组织
- 关键内容用表格对比
- 命令附语法、核心参数、调用示例
- 重要术语给出中英文
- 面向：【系统管理员 + 运维工程师 + 安全工程师】
- 深度：操作参考 + 原理理解 + 安全加固
- 示例标注适用发行版/版本

# 约束
- 不穷举所有目录和文件，只列核心与关键内容
- 路径必须准确
- 高风险操作必须给出警告
- 修改系统配置前提示备份
- 区分不同发行版的差异
- 对需要 root 权限的命令进行标注
- 用 ASCII 图展示架构与流程
- 最后附"优化后的提示词模板"
```

**使用说明**：将【操作系统】替换为"FreeBSD""macOS""Solaris"等，即可生成同等深度的文件系统知识文档。

---

> **总结**：Linux 文件系统是一个从物理磁盘到逻辑目录树的多层体系。理解 VFS 的抽象作用、主流文件系统的特性差异、FHS 的目录标准、inode 的工作原理、权限体系（rwx/SUID/SGID/ACL/属性），以及常见的安全加固和故障排查方法，是系统管理员和安全工程师的核心基本功。记住：数据安全的底线是备份，操作前的确认胜过操作后的恢复。
