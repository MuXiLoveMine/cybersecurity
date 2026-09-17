# Volatility框架使用

### 3.1 安装

**Volatility 3（Python 3）：**

```bash
# 方法1：pip安装
pip3 install volatility3

# 方法2：源码安装
git clone https://github.com/volatilityfoundation/volatility3.git
cd volatility3
pip3 install -r requirements.txt
python3 setup.py install

# 方法3：使用Docker
docker pull volatilityfoundation/volatility3:latest
docker run --rm -v /forensics:/data volatilityfoundation/volatility3 \
  -f /data/memory.raw windows.pslist
```

**Volatility 2（Python 2，经典版本）：**

```bash
# 安装Volatility 2
git clone https://github.com/volatilityfoundation/volatility.git
cd volatility
python setup.py install

# 添加符号表（ISF - Intermediate Symbol Format）
# 下载符号表到symbols目录
# https://downloads.volatilityfoundation.org/volatility3/symbols/windows.zip
unzip windows.zip -d volatility3/symbols/windows/
```

### 3.2 基本命令

**Volatility 3基本命令格式：**

```bash
# 基本语法
vol -f <镜像文件> <插件>.<模块>

# 自动检测操作系统类型
vol -f memory.raw banners.Banners

# Windows分析
vol -f memory.raw windows.pslist        # 进程列表
vol -f memory.raw windows.psscan       # 进程扫描（可发现隐藏进程）
vol -f memory.raw windows.pstree       # 进程树
vol -f memory.raw windows.netscan      # 网络连接
vol -f memory.raw windows.cmdline      # 命令行参数
vol -f memory.raw windows.dlllist      # DLL列表
vol -f memory.raw windows.handles     # 句柄
vol -f memory.raw windows.registry.hivelist  # 注册表hive
vol -f memory.raw windows.registry.printkey  # 注册表键值
vol -f memory.raw windows.malfind     # 恶意代码检测
vol -f memory.raw windows.hashes      # 密码哈希
vol -f memory.raw windows.lsadump     # LSA Secrets
vol -f memory.raw windows.svcscan     # 服务
vol -f memory.raw windows.modules     # 内核模块
vol -f memory.raw windows.modscan     # 内核模块扫描
vol -f memory.raw windows.callbacks  # 回调函数
vol -f memory.raw windows.ssdt        # SSDT表
vol -f memory.raw windows.driverirp   # 驱动IRP

# Linux分析
vol -f memory.raw linux.pslist
vol -f memory.raw linux.bash
vol -f memory.raw linux.check_modules
vol -f memory.raw linux.lsof
vol -f memory.raw linux.netstat
vol -f memory.raw linux.proc_maps

# 列出所有可用插件
vol -f memory.raw --help
vol --plugins  # 查看已加载插件
```

### 3.3 插件体系

**Volatility 3插件分类：**

```
Windows插件：
├── 进程分析
│   ├── windows.pslist        — EPROCESS双向链表
│   ├── windows.psscan        — 池扫描（发现隐藏/终止进程）
│   ├── windows.pstree        — 进程树结构
│   ├── windows.psxview        — 多种方法交叉验证
│   ├── windows.cmdline        — 命令行参数
│   └── windows.dlllist        — 加载的DLL
├── 网络分析
│   ├── windows.netscan        — TCP/UDP连接
│   └── windows.netstat       — 实时网络统计
├── 注册表分析
│   ├── windows.registry.hivelist  — 注册表hive
│   ├── windows.registry.printkey  — 打印注册表键
│   ├── windows.registry.hivedump  — Hive完整转储
│   └── windows.registry.userassist — UserAssist记录
├── 凭证提取
│   ├── windows.hashes        — SAM哈希
│   ├── windows.lsadump      — LSA Secrets
│   ├── windows.cachedump    — 缓存的域凭据
│   └── windows.hashdump     — 密码哈希
├── 恶意代码检测
│   ├── windows.malfind       — 注入代码检测
│   ├── windows.apihooks      — API Hook检测
│   ├── windows.ssdt          — SSDT Hook检测
│   ├── windows.callbacks     — 内核回调检测
│   └── windows.driverirp     — IRP Hook检测
├── 文件系统
│   ├── windows.filescan     — MFT文件扫描
│   ├── windows.fileobj_scan — FILE_OBJECT扫描
│   └── windows.dumpfiles     — 提取文件
└── 其他
    ├── windows.envars        — 环境变量
    ├── windows.privileges    — 进程权限
    ├── windows.svcscan       — Windows服务
    └── windows.modules       — 内核模块

Linux插件：
├── linux.pslist              — 进程列表
├── linux.pstree              — 进程树
├── linux.bash                — Bash历史
├── linux.check_modules       — 隐藏模块检测
├── linux.lsof                — 打开文件
├── linux.netstat            — 网络连接
├── linux.proc_maps          — 进程内存映射
├── linux.tty_check          — TTY检查
└── linux.bash_env           — Bash环境变量
```

---

---

## 📋 内容审核与补充建议

> 针对「Volatility框架使用」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

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
