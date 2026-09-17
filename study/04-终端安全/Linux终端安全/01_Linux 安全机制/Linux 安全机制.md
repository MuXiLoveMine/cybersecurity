# Linux 安全机制

### 1.1 用户权限模型

**Linux 用户体系**

Linux 是多用户操作系统，每个用户都有唯一的 UID（用户标识）和 GID（组标识）。

| 用户类型 | UID 范围 | 说明 |
|----------|----------|------|
| root 用户 | 0 | 超级用户，拥有所有权限 |
| 系统用户 | 1-999（不同发行版可能不同） | 运行系统服务的用户 |
| 普通用户 | 1000+ | 登录用户 |

**相关文件**

| 文件 | 作用 |
|------|------|
| /etc/passwd | 用户账户信息 |
| /etc/shadow | 用户密码哈希（需 root 权限读取） |
| /etc/group | 组信息 |
| /etc/gshadow | 组密码信息 |
| /etc/sudoers | sudo 配置 |

**/etc/passwd 格式**

```
用户名:密码占位符:UID:GID:用户信息:主目录:登录shell
示例：
root:x:0:0:root:/root:/bin/bash
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
user:x:1000:1000:User:/home/user:/bin/bash
```

**/etc/shadow 格式**

```
用户名:密码哈希:最后修改时间:最小使用天数:最大使用天数:警告天数:非活动天数:过期时间:保留字段
示例：
root:$6$abcdefgh$ijklmnopqrstuvwxyz:19000:0:99999:7:::

密码哈希格式：$id$salt$hashed
- $1$: MD5
- $2a$: Blowfish
- $5$: SHA-256
- $6$: SHA-512
- $y$: yescrypt
```

### 1.2 文件权限

**UGO 权限模型**

Linux 文件权限分为三类用户：所有者（User）、组（Group）、其他（Other），每类用户有三种权限：读（Read）、写（Write）、执行（Execute）。

```
权限表示：
r = 读 (4)
w = 写 (2)
x = 执行 (1)

示例：
-rw-r--r--  1 user group  1234 Sep 11 10:00 file.txt
drwxr-xr-x  2 user group  4096 Sep 11 10:00 dir/

第一个字符：文件类型
- = 普通文件
d = 目录
l = 符号链接
b = 块设备
c = 字符设备
s = 套接字
p = 管道

后面9个字符分为三组：
所有者权限: rw- (6)
组权限:     r-- (4)
其他权限:   r-- (4)
```

**特殊权限**

| 权限 | 文件上的作用 | 目录上的作用 | 八进制值 |
|------|-------------|-------------|----------|
| SUID | 以文件所有者身份执行 | 无意义 | 4000 |
| SGID | 以文件所属组身份执行 | 新文件继承目录的组 | 2000 |
| Sticky Bit | 无意义 | 只有文件所有者才能删除文件 | 1000 |

```
SUID 示例：
-rwsr-xr-x 1 root root 43696 Jan  1 00:00 /usr/bin/passwd
（所有者执行位的 x 变成了 s，表示设置了 SUID）

SGID 示例：
drwxrwsr-x 2 root group 4096 Jan  1 00:00 /dir
（组执行位的 x 变成了 s，表示设置了 SGID）

Sticky Bit 示例：
drwxrwxrwt 10 root root 4096 Jan  1 00:00 /tmp
（其他执行位的 x 变成了 t，表示设置了 Sticky Bit）
```

**查找 SUID/SGID 文件**

```bash
# 查找所有 SUID 文件
find / -perm -4000 -type f 2>/dev/null

# 查找所有 SGID 文件
find / -perm -2000 -type f 2>/dev/null

# 查找所有可写的 SUID 文件（高危）
find / -perm -4000 -writable -type f 2>/dev/null
```

### 1.3 ACL（访问控制列表）

**ACL 概述**

ACL（Access Control List）是对标准 UGO 权限的扩展，允许为特定用户或组设置更细粒度的权限。

**常用命令**

```bash
# 查看 ACL
getfacl /path/to/file

# 设置 ACL（给特定用户读写权限）
setfacl -m u:username:rw /path/to/file

# 设置 ACL（给特定组读权限）
setfacl -m g:groupname:r /path/to/file

# 删除特定用户的 ACL
setfacl -x u:username /path/to/file

# 删除所有 ACL
setfacl -b /path/to/file

# 设置默认 ACL（对目录，新文件继承）
setfacl -m d:u:username:rw /path/to/dir
```

### 1.4 SELinux

**SELinux 概述**

SELinux（Security-Enhanced Linux）是由美国国家安全局（NSA）开发的强制访问控制（MAC）安全模块，已集成到 Linux 内核中。它为 Linux 提供了细粒度的强制访问控制能力。

**SELinux 三种模式**

| 模式 | 说明 |
|------|------|
| Enforcing | 强制模式，SELinux 策略被强制执行，违反策略的操作会被拒绝并记录 |
| Permissive | 宽容模式，策略不会强制执行，只会记录违反操作（用于调试） |
| Disabled | 禁用，SELinux 完全关闭 |

**查看和切换 SELinux 模式**

```bash
# 查看当前 SELinux 状态
getenforce
sestatus

# 临时切换模式（重启后失效）
setenforce 0  # 切换到 Permissive
setenforce 1  # 切换到 Enforcing

# 永久切换（修改配置文件，需要重启）
vim /etc/selinux/config
SELINUX=enforcing  # 或 permissive / disabled
```

**SELinux 安全上下文**

每个文件、进程、端口都有安全上下文（Security Context），格式为：

```
user:role:type:level
示例：
system_u:object_r:httpd_sys_content_t:s0 /var/www/html/index.html
system_u:system_r:httpd_t:s0 /usr/sbin/httpd
```

- **user**：SELinux 用户（system_u、unconfined_u 等）
- **role**：SELinux 角色（object_r、system_r 等）
- **type**：SELinux 类型（最重要，用于类型强制）
- **level**：多级安全级别（MLS/MCS）

**常用 SELinux 管理命令**

```bash
# 查看文件安全上下文
ls -Z /path/to/file

# 查看进程安全上下文
ps -eZ

# 查看端口安全上下文
semanage port -l

# 修改文件安全上下文
chcon -t httpd_sys_content_t /path/to/file

# 恢复默认安全上下文
restorecon -Rv /path/to/dir

# 添加端口规则
semanage port -a -t http_port_t -p tcp 8080

# 查看布尔值
getsebool -a
getsebool httpd_enable_homedirs

# 设置布尔值
setsebool httpd_enable_homedirs on
setsebool -P httpd_enable_homedirs on  # 永久设置

# 查看 SELinux 日志
ausearch -m avc -ts recent
sealert -a /var/log/audit/audit.log
```

**SELinux 日志分析**

```bash
# 查看 SELinux 拒绝日志
ausearch -m AVC -ts today

# 使用 sealert 分析日志（更友好的输出）
sealert -a /var/log/audit/audit.log

# 实时监控 SELinux 事件
tail -f /var/log/audit/audit.log | grep avc
```

### 1.5 AppArmor

**AppArmor 概述**

AppArmor 是另一种强制访问控制（MAC）系统，与 SELinux 相比，AppArmor 使用路径名来标识文件，配置相对简单。主要用于 Ubuntu、SUSE 等发行版。

**AppArmor 状态管理**

```bash
# 查看 AppArmor 状态
aa-status
apparmor_status

# 启用/禁用 AppArmor 配置
aa-enforce /etc/apparmor.d/usr.bin.nginx
aa-complain /etc/apparmor.d/usr.bin.nginx  # 投诉模式（只记录不阻止）
aa-disable /etc/apparmor.d/usr.bin.nginx

# 重新加载配置
apparmor_parser -r /etc/apparmor.d/usr.bin.nginx
```

**AppArmor 配置文件示例**

```
# /etc/apparmor.d/usr.bin.nginx
#include <tunables/global>

/usr/sbin/nginx {
  #include <abstractions/base>
  #include <abstractions/nameservice>
  
  capability setuid,
  capability setgid,
  capability net_bind_service,
  
  /usr/sbin/nginx mr,
  /var/log/nginx/*.log w,
  /etc/nginx/** r,
  /var/www/** r,
  
  /run/nginx.pid rw,
}
```

### 1.6 chroot 与容器隔离

**chroot**

chroot 是将进程的根目录切换到指定目录的操作，使进程无法访问该目录之外的文件系统。

```bash
# 创建 chroot 环境
mkdir -p /chroot_env/{bin,lib,lib64,etc}

# 复制需要的程序和库
cp /bin/bash /chroot_env/bin/
cp /bin/ls /chroot_env/bin/
ldd /bin/bash  # 查看依赖的库
# 复制所有依赖的库文件到相应目录

# 进入 chroot 环境
chroot /chroot_env /bin/bash
```

**chroot 的局限性**

- 不是安全边界，可以被有足够权限的进程逃逸
- 只隔离文件系统，不隔离网络、进程等
- 需要 root 权限才能使用

**Linux Namespace（命名空间）**

命名空间是 Linux 内核提供的隔离机制，是容器技术的基础：

| 命名空间 | 隔离内容 |
|----------|----------|
| Mount (mnt) | 文件系统挂载点 |
| Process ID (pid) | 进程 ID |
| Network (net) | 网络栈 |
| Interprocess Communication (ipc) | 进程间通信 |
| UTS | 主机名和域名 |
| User ID (user) | 用户和组 ID |
| Control group (cgroup) | 控制组根目录 |

### 1.7 Linux Capabilities

**Capabilities 概述**

Linux Capabilities 将 root 用户的特权划分为不同的能力，允许进程只获得其需要的特权，而不需要完整的 root 权限。

**常用 Capabilities**

| Capability | 说明 |
|------------|------|
| CAP_NET_BIND_SERVICE | 绑定小于 1024 的端口 |
| CAP_NET_ADMIN | 网络管理（配置接口、路由表、防火墙等） |
| CAP_NET_RAW | 使用原始套接字（ping、抓包等） |
| CAP_SYS_ADMIN | 系统管理（多种特权，功能强大） |
| CAP_SYS_PTRACE | ptrace 调试其他进程 |
| CAP_DAC_OVERRIDE | 绕过文件 DAC 权限检查 |
| CAP_DAC_READ_SEARCH | 绕过文件读和目录搜索权限 |
| CAP_SETUID | 操作进程 UID |
| CAP_SETGID | 操作进程 GID |
| CAP_CHOWN | 修改文件所有者 |
| CAP_FOWNER | 绕过文件所有者权限检查 |
| CAP_KILL | 向任意进程发送信号 |
| CAP_MKNOD | 创建特殊文件 |
| CAP_SYS_MODULE | 加载/卸载内核模块 |
| CAP_SYS_RAWIO | 直接 I/O 端口访问 |

**Capabilities 操作**

```bash
# 查看文件的 capabilities
getcap /usr/bin/ping
# 输出：/usr/bin/ping = cap_net_admin,cap_net_raw+p

# 设置文件 capabilities
setcap cap_net_bind_service=ep /usr/bin/nginx

# 清除文件 capabilities
setcap -r /usr/bin/nginx

# 查看进程的 capabilities
cat /proc/<pid>/status | grep Cap
# 或使用 capsh
capsh --print
```

### 1.8 seccomp

**seccomp 概述**

seccomp（secure computing mode）是 Linux 内核的安全特性，允许进程限制自己可以调用的系统调用。这是一种沙箱机制，可以减少内核攻击面。

**seccomp 模式**

- **SECCOMP_MODE_STRICT**：严格模式，只允许 read、write、_exit、sigreturn 四个系统调用
- **SECCOMP_MODE_FILTER**：过滤器模式，使用 BPF 过滤器定义允许的系统调用

**seccomp 应用场景**

- 容器运行时（Docker、containerd）
- 浏览器沙箱（Chrome、Firefox）
- 服务程序沙箱（systemd、vsftpd）
- 漏洞利用缓解

```bash
# 查看 Docker 默认 seccomp 配置
docker run --rm alpine cat /proc/self/status | grep Seccomp

# 运行时禁用 seccomp（不推荐）
docker run --rm --security-opt seccomp=unconfined alpine sh
```

---

---

## 📋 内容审核与补充建议

> 针对「Linux 安全机制」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

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
