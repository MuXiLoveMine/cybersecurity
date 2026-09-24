# Magisk框架

### 4.1 Magisk简介

Magisk是目前最流行的Android Root解决方案，由topjohnwu开发。Magisk的核心理念是"无系统修改"（Systemless Root），通过在启动时挂载覆盖层来修改系统，不修改系统分区。

Magisk核心功能：

- **Root授权管理**：通过su和MagiskSU提供Root权限
- **无系统修改**：不修改/system分区，通过OverlayFS/mount覆盖
- **MagiskHide/DenyList**：隐藏Root状态
- **模块系统**：通过模块扩展功能
- **Zygisk**：在Zygote中注入代码

### 4.2 Magisk架构

```
+----------------------------------------------------+
|                    Magisk 架构                      |
+----------------------------------------------------+
|                                                    |
|  +-------------+    +-------------+               |
|  | Magisk Daemon|    | MagiskInit  |               |
|  | (守护进程)    |    | (启动初始化)  |               |
|  | - su授权     |    | - 挂载镜像    |               |
|  | - 模块加载   |    | - 初始化Root  |               |
|  | - Hide管理   |    | - Zygisk启动  |               |
|  +-------------+    +-------------+               |
|         |                  |                      |
|         v                  v                      |
|  +-------------+    +-------------+               |
|  | MagiskSU    |    | Magisk Image|               |
|  | (su二进制)   |    | (.img挂载)   |               |
|  +-------------+    +-------------+               |
|         |                  |                      |
|         |          +-------+-------+               |
|         |          |               |               |
|         |          v               v               |
|         |    +-----------+  +-----------+         |
|         |    |  Zygisk   |  |  Modules  |         |
|         |    | (注入引擎) |  | (功能模块) |         |
|         |    +-----------+  +-----------+         |
|         |          |               |              |
|         |          v               v              |
|         |    +-----------+  +-----------+         |
|         |    |DenyList   |  |MagiskHide |         |
|         |    |(隐藏Root)  |  |(已废弃)    |         |
|         |    +-----------+  +-----------+         |
|         |                                           |
|         v                                           |
|    +-----------+                                    |
|    | Magisk    |                                    |
|    | Manager   |                                    |
|    | (管理APP)  |                                    |
|    +-----------+                                    |
|                                                    |
+----------------------------------------------------+
```

### 4.3 Magisk启动流程

```
设备启动流程：

1. 内核启动
   |
2. init进程启动
   |
3. MagiskInit执行 (替换的/init或init.rc注入)
   |   - 挂载magisk.img到 /sbin/.magisk
   |   - 处理启动脚本
   |   - 启动Zygisk (如果启用)
   |
4. Zygote启动
   |   - Magisk通过Zygisk注入Zygote
   |   - DenyList配置生效
   |
5. 系统服务启动
   |   - Magisk Daemon启动
   |   - su二进制就绪
   |
6. 用户解锁
   |   - Magisk Manager可用
   |   - 模块完全加载
```

### 4.4 Magisk模块系统

Magisk模块是一个包含特定文件结构的ZIP包：

```
mymodule.zip
|-- module.prop          # 模块信息
|-- post-fs-data.sh      # post-fs-data阶段脚本
|-- service.sh           # late_start阶段脚本
|-- customize.sh         # 安装时脚本
|-- system/              # 覆盖系统文件
|   `-- ...
|-- system.prop          # 系统属性
|-- sepolicy.rule       # SELinux策略
`-- META-INF/            # 安装脚本
```

**module.prop示例**

```properties
id=my_module
name=My Custom Module
version=v1.0.0
versionCode=10000
author=Developer
description=This is a custom Magisk module
```

**service.sh示例**

```bash
#!/system/bin/sh
# 在late_start service阶段执行
# 网络已可用

# 启动自定义服务
while [ "$(getprop sys.boot_completed)" != "1" ]; do
    sleep 1
done

# 执行自定义逻辑
log -p i -t MyModule "Service started"
```

**创建简单Magisk模块**

```bash
# 创建模块目录结构
mkdir -p mymodule/system/app/MyApp
echo 'id=myapp' > mymodule/module.prop
echo 'name=My App' >> mymodule/module.prop
echo 'version=1.0' >> mymodule/module.prop
echo 'versionCode=1' >> mymodule/module.prop
echo 'author=Me' >> mymodule/module.prop
echo 'description=My custom module' >> mymodule/module.prop

# 添加文件
cp MyApp.apk mymodule/system/app/MyApp/MyApp.apk

# 打包
cd mymodule && zip -r ../mymodule.zip . && cd ..
```

---

---

