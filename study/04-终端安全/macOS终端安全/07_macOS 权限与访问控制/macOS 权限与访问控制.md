# macOS 权限与访问控制

### 7.1 用户权限模型

macOS 用户权限模型基于 POSIX，但加入了额外的安全层。

| 用户类型 | UID | 权限 | 说明 |
|----------|-----|------|------|
| root | 0 | 完全控制 | 受 SIP 限制，不直接登录 |
| admin | 501+ | 管理权限 | 可使用 sudo，可安装软件 |
| standard | 501+ | 普通权限 | 无 sudo，无系统修改权限 |
| 系统服务 | 1-500 | 各服务最小权限 | launchd 管理的系统服务用户 |

```bash
# 查看当前用户信息
id
# 输出：uid=501(alice) gid=20(staff) groups=20(staff),12(everyone),...

# 查看管理员用户
dscl . -read /Groups/admin GroupMembership
# 输出：GroupMembership: alice bob

# 创建标准用户
sudo sysadminctl -addUser charlie -password - -adminUser alice

# 将用户提升为管理员
sudo dseditgroup -o edit -a charlie -t user admin

# 将管理员降级为标准用户
sudo dseditgroup -o edit -d charlie -t user admin
```

### 7.2 sudo 与授权管理

```bash
# macOS sudo 配置文件
/etc/sudoers

# 安全编辑 sudoers（使用 visudo）
sudo visudo

# sudoers 配置示例
# 允许 admin 组执行所有命令（默认）
%admin  ALL=(ALL) ALL

# 允许特定用户执行特定命令
operator ALL=(root) /usr/sbin/softwareupdate, /usr/bin/ditto

# 免密码执行特定命令（自动化脚本）
deploy ALL=(root) NOPASSWD: /usr/local/bin/deploy.sh

# 使用别名组织规则
User_Alias  DBADMIN = dbuser1, dbuser2
Cmnd_Alias  DB = /usr/local/bin/db_backup, /usr/local/bin/db_restore
DBADMIN     ALL=(root) NOPASSWD: DB

# 查看 sudo 权限
sudo -l
```

### 7.3 POSIX 权限与 ACL

macOS 支持 POSIX 权限和 NFSv4 ACL 两层访问控制。

```bash
# 查看文件权限（POSIX + ACL）
ls -le /path/to/file
# 输出示例：
# -rw-r--r--+ 1 alice staff 0 Sep 1 10:00 file.txt
#  0: group:staff allow read,write
#  1: user:bob allow read

# 修改 POSIX 权限
chmod 755 /path/to/file
chmod u+x,g-w,o-r /path/to/file

# 修改 ACL（使用 chmod 的 ACL 扩展语法）
chmod +a "bob allow read,write" /path/to/file
chmod +a "group:devteam allow read" /path/to/file

# 删除 ACL
chmod -a "bob allow read,write" /path/to/file
chmod -N /path/to/file    # 删除所有 ACL

# 递归设置目录 ACL
chmod -R +a "group:staff allow read,execute,search" /path/to/dir

# ACL 权限关键词
# read, write, delete, append, execute, search, readattr, writeattr,
# readextattr, writeextattr, readsecurity, writesecurity, chown
```

### 7.4 TCC 数据库与隐私权限管理

```bash
# 重置单个应用的 TCC 权限（用户需要重新授权）
tccutil reset All com.example.app

# 重置所有应用的特定权限
tccutil reset Camera
tccutil reset Microphone
tccutil reset SystemPolicyAllFiles

# 通过 MDM 预配置 TCC 权限（Privacy Preferences Policy Control, PPPC）
# Configuration Profile 示例：
# PayloadType: com.apple.TCC.configuration-profile-policy
# PayloadContent:
#   Services:
#     SystemPolicyAllFiles:
#       Identifier: com.example.app
#       IdentifierType: bundleID
#       Allowed: true
#       CodeRequirement: identifier "com.example.app" and anchor apple...

# 监控 TCC 权限请求
log stream --predicate \
  'subsystem == "com.apple.TCC"' --info --debug
```

---

---

## 📋 内容审核与补充建议

> 针对「macOS 权限与访问控制」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

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
