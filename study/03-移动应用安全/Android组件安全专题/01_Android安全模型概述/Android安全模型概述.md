# Android安全模型概述

### 1.1 沙箱隔离机制

Android的安全模型基于Linux内核的沙箱隔离机制。每个应用运行在独立的Linux进程中，拥有唯一的Linux用户ID（UID）。应用之间的隔离通过以下机制实现：

```
应用A (UID=10042)          应用B (UID=10043)
+-------------------+      +-------------------+
| Dalvik/ART VM     |      | Dalvik/ART VM     |
| - 进程隔离         |      | - 进程隔离         |
| - UID不同          |      | - UID不同          |
| - 文件权限隔离     |      | - 文件权限隔离     |
+-------------------+      +-------------------+
         |                          |
         v                          v
+-------------------------------------------------+
|              Linux Kernel                       |
| - 用户空间隔离 (UID/GID)                        |
| - 文件系统权限 (rwx)                             |
| - 进程间通信需显式权限                           |
+-------------------------------------------------+
```

关键隔离特性：

- **进程隔离**：每个应用运行在独立进程中，通过Binder IPC进行跨进程通信
- **文件系统隔离**：应用数据目录（/data/data/package_name/）仅对应用自身可读写
- **UID隔离**：每个应用在安装时分配唯一UID，应用以该UID运行
- **共享用户ID（sharedUserId）**：使用相同签名和sharedUserId的应用可共享UID（已废弃）

### 1.2 权限模型

Android权限模型经历了从安装时权限到运行时权限的演进：

**安装时权限（Android 5.x及以下）**

用户在安装应用时一次性授予所有声明权限，无法选择性拒绝。这导致过度权限请求成为常态。

**运行时权限（Android 6.0+）**

危险权限（Dangerous Permissions）需要在运行时动态请求用户授权。权限分为：

| 权限类型 | 保护级别 | 示例 |
|----------|----------|------|
| Normal | 正常 | INTERNET, SET_WALLPAPER |
| Dangerous | 危险 | READ_CONTACTS, CAMERA, ACCESS_FINE_LOCATION |
| Signature | 签名 | 仅同签名应用可申请 |
| SignatureOrSystem | 签名或系统 | 系统应用或同签名应用 |

危险权限分组（同一组内授权一个即授权全组）：

```
权限组                    权限
-----------------------   --------------------------------
CALENDAR                  READ_CALENDAR, WRITE_CALENDAR
CAMERA                    CAMERA
CONTACTS                  READ_CONTACTS, WRITE_CONTACTS, GET_ACCOUNTS
LOCATION                  ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION
MICROPHONE                RECORD_AUDIO
PHONE                     READ_PHONE_STATE, CALL_PHONE, READ_CALL_LOG, ...
SENSORS                   BODY_SENSORS
SMS                       SEND_SMS, RECEIVE_SMS, READ_SMS, ...
STORAGE                   READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE
```

**特殊权限（Android 11+）**

Android 11引入了特殊权限访问机制，如所有文件访问（MANAGE_EXTERNAL_STORAGE）、精确位置访问等。

### 1.3 签名机制

Android应用签名确保应用完整性并建立信任关系：

- **V1签名（JAR签名）**：基于JAR的签名方式，兼容性好但安全性较低
- **V2签名（APK签名方案v2）**：Android 7.0引入，对整个APK进行签名
- **V3签名（APK签名方案v3）**：Android 9.0引入，支持密钥轮换
- **V4签名（APK签名方案v4）**：Android 11引入，支持增量安装

签名在组件安全中的作用：

- **同一签名的应用**可以共享UID（通过sharedUserId）
- **同一签名的应用**可以申请signature保护级别的自定义权限
- **签名验证**确保应用未被篡改

---

---

## 📋 内容审核与补充建议

> 针对「Android安全模型概述」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

### ⚔️ 攻击技术
- ⚠️ 缺少attack相关内容

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
