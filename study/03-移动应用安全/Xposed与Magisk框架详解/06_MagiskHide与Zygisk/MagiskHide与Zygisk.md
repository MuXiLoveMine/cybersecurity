# MagiskHide与Zygisk

### 5.1 MagiskHide原理

MagiskHide是Magisk早期版本提供的隐藏Root状态的功能。其工作原理：

```
MagiskHide工作流程：

1. 监控进程启动
   - 通过/proc监控新进程
   - 读取目标应用的AndroidManifest判断是否需要隐藏

2. 解除挂载Magisk覆盖
   - 在目标进程的mount namespace中
   - 卸载magisk.img挂载的所有覆盖
   - 使/system恢复原样

3. 清理Root痕迹
   - 隐藏su二进制
   - 修改/proc/self/maps
   - 隐藏Magisk相关文件
```

**MagiskHide配置**

```
# 在Magisk Manager中配置
Settings -> MagiskHide -> 选择需要隐藏的应用

# 或通过命令行
magisk --hide com.example.app     # 添加到隐藏列表
magisk --hide --rm com.example.app # 从列表移除
magisk --hide --ls                  # 列出隐藏列表
```

### 5.2 MagiskHide局限与废弃

MagiskHide存在以下局限：

- **仅处理mount namespace**：不处理进程内的Root检测
- **性能开销**：需要监控所有新进程
- **容易被检测**：留下的痕迹可被高级检测发现
- **不支持Zygisk**：与Zygisk不兼容

从Magisk 24.0起，MagiskHide被移除，被Zygisk DenyList取代。

### 5.3 Zygisk机制

Zygisk是Magisk 24.0+引入的新机制，在Zygote进程内注入代码，实现更强大的功能。

**Zygisk工作原理**

```
Zygisk启动流程：

1. MagiskInit阶段
   |   - 加载libzygisk.so到Zygote进程
   |   - 注册Zygisk入口点
   |
2. Zygote fork前
   |   - Zygisk初始化
   |   - 加载所有Zygisk模块
   |   - 模块可以Hook系统级方法
   |
3. Zygote fork应用进程
   |   - 检查目标进程是否在DenyList中
   |   - 如果在DenyList中：
   |     - 在fork后立即清理Magisk痕迹
   |     - 卸载所有Magisk挂载
   |     - 隐藏Zygisk自身
   |   - 如果不在DenyList中：
   |     - 正常加载模块
   |     - 模块Hook生效
   |
4. 应用进程运行
       - DenyList应用看不到Root痕迹
       - 普通应用Root和模块正常工作
```

**Zygisk API（模块开发）**

```cpp
// Zygisk模块使用C/C++开发
#include "zygisk.hpp"

class MyModule : public zygisk::Module {
public:
    void onLoad(zygisk::Api *api, JNIEnv *env) override {
        this->api = api;
        this->env = env;
    }

    void preAppSpecialize(const zygisk::AppSpecializeArgs *args) override {
        // 应用进程fork前调用
        // 可以获取包名等信息
        const char *process = env->GetStringUTFChars(args->nice_name, nullptr);
        if (strcmp(process, "com.example.target") == 0) {
            // 对特定应用执行操作
        }
        env->ReleaseStringUTFChars(args->nice_name, process);
    }

    void postAppSpecialize(const zygisk::AppSpecializeArgs *args) override {
        // 应用进程fork后调用
        // 此时可以安全地Hook
    }

private:
    zygisk::Api *api;
    JNIEnv *env;
};

REGISTER_ZYGISK_MODULE(MyModule)
```

### 5.4 DenyList

DenyList是Zygisk时代的隐藏机制，替代了MagiskHide：

**DenyList配置**

```
# Magisk Manager中
Settings -> Zygisk -> Enable
Settings -> Enforce DenyList -> Enable
Configure -> 选择需要隐藏的应用

# 命令行
magisk --denylist add com.example.app
magisk --denylist rm com.example.app
magisk --denylist ls
magisk --denylist enable
magisk --denylist disable
```

**DenyList的作用**

```
DenyList中的进程：
  - Magisk挂载被卸载
  - su不可用
  - Magisk文件不可见
  - Zygisk模块不加载
  - 系统属性恢复默认
  - /proc/self/maps清理

非DenyList中的进程：
  - Root正常可用
  - Zygisk模块正常工作
  - Magisk功能完整
```

**DenyList配置清单**

```
建议添加到DenyList的应用：
  - 银行类：各银行APP
  - 支付类：支付宝、微信支付、Google Pay
  - DRM类：Netflix、Disney+、Prime Video
  - 游戏类：带有反作弊的游戏
  - 企业类：MDM应用、企业邮箱
  - 安全类：Google Play Integrity
```

---

---

## 📋 内容审核与补充建议

> 针对「MagiskHide与Zygisk」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

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
