# WebShell检测与防御

### 6.1 静态检测

静态检测通过分析文件内容特征来发现WebShell：

```
静态检测方法:
├── 特征匹配
│   ├── 关键字检测: eval/assert/system/exec/passthru
│   ├── 敏感函数组合: eval+$_POST/assert+$_REQUEST
│   └── 已知Shell特征库: 中国菜刀/暗剑/C99等特征
│
├── 语法分析
│   ├── PHP AST分析: 识别危险语法结构
│   ├── 变量追踪: 追踪数据从输入到执行的流
│   └── 污点分析: 标记外部输入到执行函数的路径
│
├── 统计分析
│   ├── 信息熵: 加密WebShell熵值偏高
│   ├── 文件特征: 超短文件/异常文件名
│   └── 文件权限: Web目录中可执行文件
│
└── 机器学习分类
    ├── 基于AST特征的分类模型
    ├── 基于N-gram的文本分类
    └── 基于TF-IDF的相似度检测
```

**常见静态检测工具：**

| 工具 | 说明 | 适用 |
|------|------|------|
| WebShellKill（D盾） | Windows平台查杀 | PHP/ASP/JSP |
| 河马（HMShell） | 云查杀+本地引擎 | 多语言 |
| NEO-İnn　| 智能分析引擎 | PHP/Java |
| LOKI | IOC检测 | 多类型 |
| YARA | 规则引擎 | 自定义规则 |

**YARA规则示例：**

```yara
rule WebShell_PHP_OneLiner {
    meta:
        description = "PHP One-liner WebShell"
        author = "Security Team"
    strings:
        $eval_post = /eval\s*\(\s*\$_(POST|GET|REQUEST|COOKIE)/
        $assert_post = /assert\s*\(\s*\$_(POST|GET|REQUEST|COOKIE)/
        $system_call = /(system|exec|passthru|shell_exec)\s*\(/
        $base64_eval = /eval\s*\(\s*(base64_decode|gzinflate|gzuncompress)/
    condition:
        any of ($eval_post, $assert_post) or
        ($base64_eval) or
        (filesize < 500 and $system_call)
}
```

### 6.2 动态检测

动态检测通过运行时行为分析来发现WebShell：

```
动态检测维度:
├── 文件操作行为
│   ├── Web目录文件创建/修改
│   ├── 异常文件写入（隐藏文件/深目录）
│   └── 文件权限变更
│
├── 进程行为
│   ├── Web进程派生子进程（如/bin/sh）
│   ├── 异常命令执行（whoami/id/ifconfig）
│   └── 反弹Shell连接
│
├── 网络行为
│   ├── 外连异常IP/端口
│   ├── DNS异常查询
│   └── 加密流量通信模式
│
├── 系统调用
│   ├── hook execve/system等系统调用
│   ├── 监控文件系统调用(inotify)
│   └── 网络连接监控
│
└── 运行时信息
    ├── PHP运行时: disable_functions检查
    ├── Java: JMX监控、Instrumentation检测
    └── 进程内存分析
```

### 6.3 流量检测

流量检测是发现WebShell通信的关键手段：

```
流量检测策略:
├── 菜刀流量检测
│   ├── 规则: POST参数含base64编码的命令
│   ├── 特征: 明文命令关键字
│   └── 告警: 命中规则即告警
│
├── 蚁剑流量检测
│   ├── 规则: 请求参数含eval+编码
│   ├── 特征: Base64编码的PHP代码
│   └── 告警: 异常编码+执行模式
│
├── 冰蝎流量检测
│   ├── 规则: AES加密流量+密钥协商阶段
│   ├── 特征: 前几个请求的特殊模式
│   ├── 统计: 加密流量的熵值分析
│   └── 告警: 异常加密通信模式
│
└── Godzilla流量检测
    ├── 规则: 组合加密+Session维持
    ├── 特征: 密码+密钥分离模式
    └── 告警: 加密POST+频繁通信
```

**Snort规则示例：**

```
# 检测菜刀流量
alert tcp any any -> $HOME_NET $HTTP_PORTS (msg:"WebShell Chopper Traffic"; 
    content:"POST"; http_method; 
    content:"eval"; http_client_body; 
    content:"base64_decode"; http_client_body; 
    reference:url,security/chopper; sid:1000001;)

# 检测蚁剑流量
alert tcp any any -> $HOME_NET $HTTP_PORTS (msg:"WebShell AntSword Traffic"; 
    content:"ant="; http_client_body;
    pcre:"/eval\s*\(\s*base64_decode/Ui";
    sid:1000002;)
```

### 6.4 内存马检测

内存马不落地文件，检测需要从运行时入手：

```
Java内存马检测:
├── Filter/Listener检测
│   ├── 枚举所有已注册Filter和Listener
│   ├── 对比标准配置与实际注册项
│   └── 检查Filter的doFilter实现是否含恶意逻辑
│
├── Agent检测
│   ├── 检查JVM启动参数-javaagent
│   ├── 检测运行时Attach操作
│   ├── 对比磁盘class与内存class定义
│   └── 检测ClassFileTransformer列表
│
├── Valve检测
│   ├── 枚举Tomcat Container的Pipeline
│   ├── 检查Valve列表是否有异常项
│   └── 分析Valve实现类来源
│
└── 综合检测
    ├── JVM内存dump分析
    ├── Java Agent注入检测工具（如arthas/jstack）
    └── RASP实时监控
```

### 6.5 防御措施

**Web层防御：**

| 防御措施 | 说明 | 效果 |
|----------|------|------|
| 文件上传限制 | 白名单后缀+内容检测 | 阻断植入 |
| disable_functions | 禁用eval/system/exec等 | 限制执行 |
| open_basedir | 限制PHP文件访问范围 | 限制操作 |
| WAF防护 | 规则+语义分析 | 流量拦截 |
| 文件监控 | Web目录文件变更告警 | 快速发现 |
| 定期查杀 | 静态+动态扫描 | 清除Shell |
| RASP防护 | 运行时自我保护 | 拦截执行 |

**系统层防御：**

```bash
# 1. 文件完整性监控
# AIDE (Advanced Intrusion Detection Environment)
aide --init        # 初始化数据库
aide --check       # 检查文件完整性

# 2. 进程监控
# 监控Web进程派生的异常子进程
ps aux | grep -E 'www-data.*\ (sh|bash|python)'

# 3. 网络连接监控
# 检测反弹Shell
ss -tlnp | grep -v -E ':(80|443|22)\ '
netstat -antp | grep ESTABLISHED

# 4. cron监控
ls -la /etc/cron.d/ /var/spool/cron/
cat /etc/crontab

# 5. 日志审计
# 检查异常的命令执行日志
grep -i "system\|exec\|eval" /var/log/nginx/access.log
```

---

---

## 📋 内容审核与补充建议

> 针对「WebShell检测与防御」部分的内容审核结果：

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

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
