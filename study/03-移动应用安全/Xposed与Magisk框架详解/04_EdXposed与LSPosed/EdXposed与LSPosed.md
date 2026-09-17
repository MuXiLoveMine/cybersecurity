# EdXposed与LSPosed

### 3.1 EdXposed框架

EdXposed（Enterprise Xposed）是针对Android 8.1+的Xposed替代方案，基于Riru和SandHook/YAHFA。

**EdXposed架构**

```
+-----------------------------+
|     EdXposed Manager        |
+-----------------------------+
              |
              v
+-----------------------------+
|        Riru (Riru模块)      |
|  - 注入Zygote进程             |
|  - 不修改系统分区              |
+-----------------------------+
              |
              v
+-----------------------------+
|    EdXposed Framework      |
|  - EdXposed Bridge          |
|  - SandHook / YAHFA        |
|  - 兼容Xposed API            |
+-----------------------------+
              |
              v
+-----------------------------+
|    Xposed Modules          |
|  (兼容原版Xposed模块)         |
+-----------------------------+
```

**EdXposed特点**

- 支持Android 8.1-10（部分支持11-13）
- 不需要修改/system分区（基于Riru注入Zygote）
- 兼容原版Xposed模块API
- 通过Magisk模块安装
- 已停止维护，被LSPosed取代

### 3.2 LSPosed框架

LSPosed是EdXposed的精神继承者，由LSPosed团队开发，支持Android 8.1+，是目前最活跃的Xposed框架实现。

**LSPosed架构**

```
+-----------------------------+
|     LSPosed Manager         |
|  - 模块管理（含作用域配置）    |
|  - 兼容性检测                 |
|  - 日志查看                  |
+-----------------------------+
              |
              v
+-----------------------------+
|    LSPosed Framework        |
|  - LSPlant (ART Hook引擎)   |
|  - 兼容Xposed API 82+       |
|  - 支持Zygisk和Riru         |
+-----------------------------+
              |
      +-------+-------+
      |               |
      v               v
+-----------+   +-----------+
|  Zygisk   |   |  Riru    |
| (推荐)    |   | (传统)    |
+-----------+   +-----------+
```

**LSPosed核心优势**

- **LSPlant Hook引擎**：自研的ART Hook引擎，支持Android 8.1-14+
- **Zygisk支持**：基于Zygisk，不修改系统分区
- **作用域管理**：精确控制模块作用于哪些应用
- **模块兼容性**：完全兼容原版Xposed模块
- **隐藏能力**：配合Zygisk DenyList隐藏自身
- **持续维护**：活跃的社区和更新

**LSPosed安装**

```
前提条件：
  - 已Root设备（Magisk或KernelSU）
  - Android 8.1+
  - Zygisk已启用（Magisk设置中）

安装步骤：
  1. 下载LSPosed Zygisk模块 (LSPosed-vX.X.X-xxxx-zygisk-release.zip)
  2. 在Magisk中安装模块
  3. 重启设备
  4. 安装LSPosed Manager
  5. 在LSPosed Manager中配置模块作用域
```

### 3.3 Riru与Zygisk对比

| 特性 | Riru | Zygisk |
|------|------|--------|
| 注入方式 | 替换/system/lib/libmemTrack.so | Magisk守护进程注入 |
| 系统修改 | 需要替换系统库 | 不修改系统库 |
| 兼容性 | 较好（但部分ROM不兼容） | 更广泛兼容 |
| 隐藏能力 | 较弱 | 更强（配合DenyList） |
| 性能开销 | 略高 | 较低 |
| 维护状态 | 逐渐被Zygisk取代 | 活跃维护 |

---

---

## 📋 内容审核与补充建议

> 针对「EdXposed与LSPosed」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

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
