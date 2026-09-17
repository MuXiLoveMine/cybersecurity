# 第7章 IOC提取与威胁情报

IOC（Indicators of Compromise，妥协指标）是描述恶意攻击活动的技术特征，用于检测、识别和响应安全威胁。准确全面的IOC提取是恶意代码分析的重要产出。

### 7.1 IOC分类

IOC涵盖了恶意代码在攻击过程中留下的各种痕迹，根据类型可以分为以下几类。

#### 7.1.1 文件类IOC

**文件哈希：**
- **MD5**：128位哈希值，最常用的文件指纹
  - 示例：`44d88612fea8a8f36de82e1278abb02f`
  - 特点：计算快，碰撞概率较低但已被证明不安全
- **SHA-1**：160位哈希值
  - 示例：`3395856ce81f2b7382dee72602f798b642f14140`
  - 特点：比MD5更安全，但也已发现理论碰撞
- **SHA-256**：256位哈希值，目前最推荐使用
  - 示例：`275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f`
  - 特点：安全性高，是目前的标准选择

**提取方法：**
```bash
# Windows PowerShell
Get-FileHash sample.exe -Algorithm MD5
Get-FileHash sample.exe -Algorithm SHA256

# Linux
md5sum sample.exe
sha256sum sample.exe
```

**文件名与路径：**
- 恶意代码创建的文件名
- 恶意代码释放文件的路径
- 特征性的文件名模式（如随机生成的命名规则）

**文件大小：**
- 特定恶意软件家族的文件大小通常在一定范围内
- 可作为辅助特征进行筛选

#### 7.1.2 网络类IOC

**IP地址：**
- C2服务器IP
- 下载服务器IP
- 代理节点IP
- 示例：`192.0.2.123`

**域名：**
- C2域名
- 钓鱼域名
- DGA生成的域名
- 示例：`malware-c2.example.com`、`evil-update-service.net`

**URL：**
- 恶意下载链接
- 信标（Beacon）URL
- 漏洞利用页面URL
- 示例：`http://evil.example.com/update/payload.bin`

**端口：**
- C2通信使用的端口号
- 常见端口：80、443、8080、3389、4444等

**SSL证书指纹：**
- HTTPS通信使用的SSL证书
- 证书的主题、颁发者、序列号、指纹
- 自签名证书通常是可疑特征

#### 7.1.3 注册表类IOC

**自启动注册表项：**
- Run键、RunOnce键
- 服务注册表项
- 计划任务相关注册表项
- 示例：`HKCU\Software\Microsoft\Windows\CurrentVersion\Run\Malware`

**恶意软件配置键：**
- 恶意软件自身存储配置的注册表位置
- 加密的配置数据
- 感染标记（如已安装的标识）

**其他注册表修改：**
- 安全策略修改
- 防火墙规则修改
- 文件关联修改
- 映像劫持（IFEO）设置

#### 7.1.4 其他IOC类型

**互斥量（Mutex）：**
- 恶意代码使用互斥量确保单实例运行
- 互斥量名称通常具有特征性
- 示例：`Global\MalwareMutex_2024`、`{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}`

**服务名称：**
- 恶意服务的显示名和服务名
- 服务描述信息
- 示例：服务名 `WinUpdateSvc`，显示名 "Windows Update Service"

**计划任务名：**
- 恶意计划任务的名称
- 任务描述和触发器信息

**PDB路径：**
- 编译时残留的调试符号路径
- 可能泄露开发者信息和项目结构
- 示例：`C:\Projects\Malware\Release\bot.pdb`

**代码片段特征：**
- 独特的代码序列（可用于YARA规则）
- 特征常量和字符串
- 加密算法的S盒或常量表

### 7.2 IOC提取工具与方法

#### 7.2.1 静态提取方法

**字符串提取：**

使用Strings或FLOSS提取字符串是获取IOC最直接的方法：

1. **网络IOC**：
   - 搜索 `http://`、`https://`、`ftp://` 开头的URL
   - 搜索IP地址模式（正则：`\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}`）
   - 搜索域名模式（通常通过特征后缀如 `.com`、`.net`、`.onion` 筛选）

2. **文件路径IOC**：
   - 搜索包含 `%APPDATA%`、`%TEMP%`、`%SystemRoot%` 等的路径
   - 搜索 `C:\`、`D:\` 开头的绝对路径
   - 搜索特征文件名（如 `README_*.txt`）

3. **注册表IOC**：
   - 搜索 `Software\Microsoft\Windows\CurrentVersion\Run`
   - 搜索 `HKLM\`、`HKCU\` 开头的注册表路径

4. **互斥量IOC**：
   - 搜索 `CreateMutex` 相关的字符串
   - 搜索 `Global\`、`Local\` 开头的名称
   - 搜索GUID格式的字符串

**PE结构分析：**

1. **资源节分析**：
   - 使用Resource Hacker或CFF Explorer查看资源
   - 资源中可能包含配置数据、加密的Shellcode、勒索信模板
   - 自定义资源类型通常包含恶意代码的关键数据

2. **导入导出表分析**：
   - 分析导入的API函数，推断恶意代码功能
   - 导出函数名可能包含特征信息

3. **版本信息分析**：
   - 查看PE的版本资源（Version Info）
   - 公司名、产品名、版本号等信息可能具有伪造特征

#### 7.2.2 动态提取方法

**沙箱自动提取：**

现代沙箱通常会自动提取IOC并整理成结构化格式：
- 自动提取文件哈希和路径
- 自动提取网络连接信息
- 自动提取注册表修改
- 自动提取创建的服务和计划任务
- 导出为JSON、STIX、OpenIOC等标准格式

**手动监控提取：**

1. **文件系统监控**：
   - 使用Process Monitor监控文件操作
   - 记录所有创建、修改、删除的文件
   - 提取文件路径和名称

2. **注册表监控**：
   - 使用Regshot对比注册表快照
   - 使用Process Monitor过滤注册表操作
   - 记录所有新增和修改的注册表项

3. **网络流量分析**：
   - 使用Wireshark抓包
   - 提取所有DNS查询和响应
   - 提取所有HTTP/HTTPS连接的目标IP、域名、URL
   - 分析TCP/UDP连接

4. **进程监控**：
   - 使用Process Explorer查看进程树
   - 记录所有创建的进程及其命令行参数
   - 查看进程加载的可疑DLL

#### 7.2.3 内存取证提取

内存取证可以提取到静态分析无法获得的运行时信息：

**内存镜像获取：**
- 使用WinPmem、DumpIt等工具获取内存镜像
- 或直接从虚拟机内存文件（`.vmem`）获取

**内存分析工具：**
- **Volatility**：最流行的开源内存取证框架
- **Redline**：FireEye的内存分析工具
- **Rekall**：基于Volatility的增强版本

**常用Volatility命令：**
```bash
# 查看进程列表
vol.py -f mem.dmp --profile=Win7SP1x86 pslist

# 查看网络连接
vol.py -f mem.dmp --profile=Win7SP1x86 netscan

# 查看注册表配置单元
vol.py -f mem.dmp --profile=Win7SP1x86 hivelist

# 提取内存中的DLL
vol.py -f mem.dmp --profile=Win7SP1x86 dlllist

# 查找注入的代码
vol.py -f mem.dmp --profile=Win7SP1x86 malfind

# 提取密码哈希
vol.py -f mem.dmp --profile=Win7SP1x86 hashdump
```

**内存中可提取的IOC：**
- 运行中的恶意进程及其命令行
- 注入到其他进程中的代码
- 网络连接状态
- 内存中的明文密码和密钥
- 已解密的配置信息
- 注册表中的数据

### 7.3 YARA规则编写

YARA是一款用于恶意软件研究的模式匹配工具，可以基于文本或二进制特征创建规则来识别恶意软件家族。

#### 7.3.1 YARA规则基础

**规则结构：**

```yara
rule MalwareFamilyName
{
    meta:
        description = "描述信息"
        author = "作者"
        date = "2024-01-01"
        version = "1.0"
        reference = "参考链接"
        hash = "样本哈希值"

    strings:
        $string1 = "特征字符串1"
        $string2 = "特征字符串2" wide ascii
        $hex1 = { 6A 40 68 00 30 00 00 6A 14 8D 91 }
        $hex2 = { E2 34 ?? C8 A? FB }

    condition:
        2 of them or ($string1 and $hex1)
}
```

**规则组成部分：**

1. **规则名（Rule Name）**：规则的标识符，用于识别
2. **元数据（Meta）**：规则的描述信息，不影响匹配
3. **字符串（Strings）**：要匹配的特征，可以是文本或十六进制
4. **条件（Condition）**：布尔表达式，定义匹配规则

#### 7.3.2 字符串类型

**普通字符串：**
```yara
$str1 = "malware_config.dat"
$str2 = "C2_Server_Address"
```

**宽字符字符串：**
```yara
$str = "Hello World" wide    // 匹配Unicode编码的字符串
```

**不区分大小写：**
```yara
$str = "MUTEX_NAME" nocase
```

**十六进制字符串：**
```yara
$hex1 = { E8 00 00 00 00 5D }    // 精确匹配
$hex2 = { 6A 40 ?? 68 }          // ?? 匹配任意字节
$hex3 = { 83 C0 [0-5] C3 }       // [0-5] 匹配0到5个任意字节
$hex4 = { B8 ?? ?? ?? ?? FF D0 } // 常用于匹配 call eax 模式
```

**正则表达式：**
```yara
$re1 = /md5:[a-f0-9]{32}/
$re2 = /IP: \d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/
```

#### 7.3.3 条件表达式

**基本逻辑：**
```yara
condition:
    $string1 and $string2       // 都匹配
    $string1 or $string2        // 任一匹配
    not $string1                // 不匹配
    ($string1 or $string2) and $string3  // 组合
```

**数量匹配：**
```yara
condition:
    2 of them                   // 匹配至少2个字符串
    all of them                 // 匹配所有字符串
    3 of ($s*)                  // 匹配以$s开头的字符串中的至少3个
```

**位置匹配：**
```yara
condition:
    $string1 at 0x401000       // 字符串在指定偏移处
    $string1 in (0..1024)       // 字符串在前1024字节内
```

**文件大小：**
```yara
condition:
    filesize < 200KB and $string1
```

**PE文件特征：**
```yara
condition:
    uint16(0) == 0x5A4D and    // MZ头
    $string1
```

#### 7.3.4 YARA规则编写实战

**编写步骤：**

1. **收集样本**：收集同一恶意软件家族的多个样本
2. **提取特征**：分析样本，提取共同的特征字符串、代码序列
3. **编写规则**：基于共同特征编写YARA规则
4. **测试规则**：使用阳性样本和阴性样本测试规则
5. **优化规则**：调整规则，提高检出率，降低误报率

**示例：勒索软件YARA规则**

```yara
rule Ransomware_LockCrypto
{
    meta:
        description = "Detects LockCrypto ransomware"
        author = "Security Analyst"
        date = "2024-01-15"
        version = "1.0"
        category = "ransomware"
        family = "LockCrypto"

    strings:
        // 勒索信文件名
        $ransom_note = "README_DECRYPT.txt"

        // 加密相关字符串
        $aes_str = "AES-256"
        $rsa_str = "RSA-2048"

        // 加密文件扩展名
        $ext = ".lock"

        // Tor C2地址特征
        $onion = /[a-z2-7]{16}\.onion/

        // 代码特征：CryptEncrypt调用模式
        $code1 = { 6A 00 6A 00 6A 00 6A 00 FF 15 ?? ?? ?? ?? }

        // 互斥量特征
        $mutex = "LockCrypto_Mutex"

        // 注册表路径
        $reg = "Software\\LockCrypto"

    condition:
        // 匹配以下条件中的至少3个
        3 of them or
        // 或者匹配勒索信 + 扩展名 + 加密算法（强特征）
        ($ransom_note and $ext and 1 of ($aes_str, $rsa_str))
}
```

**编写注意事项：**
- 规则应该足够具体，避免误报
- 规则应该有足够的弹性，能够检测变种
- 使用多个特征组合，而不是依赖单个字符串
- 注意字符串的编码方式（ASCII/Unicode）
- 避免使用过于常见的字符串（如 "error"、"failed"）
- 测试时使用干净的系统文件作为阴性样本
- 定期更新规则以适应新的变种

#### 7.3.5 YARA使用方法

**命令行使用：**
```bash
# 扫描单个文件
yara rule.yar sample.exe

# 扫描目录
yara rule.yar /path/to/malware/

# 递归扫描
yara -r rule.yar /path/to/scan/

# 显示匹配的字符串
yara -s rule.yar sample.exe

# 多个规则文件
yara rule1.yar rule2.yar sample.exe
```

**集成到其他工具：**
- 沙箱系统通常集成YARA规则检测
- 杀毒软件支持YARA规则扩展
- SIEM系统可以集成YARA进行文件分析
- Cuckoo Sandbox内置YARA扫描模块

### 7.4 威胁情报平台利用

威胁情报平台汇集了全球的威胁数据，能够帮助分析人员快速了解样本的威胁等级、家族归属和关联信息。

#### 7.4.1 VirusTotal

VirusTotal是最知名的多引擎扫描和威胁情报平台，集成了数十家杀毒引擎和多种扫描工具。

**核心功能：**

1. **文件扫描**：
   - 上传文件进行多引擎扫描
   - 查看各杀毒引擎的检测结果
   - 查看文件的基本信息（大小、类型、哈希、数字签名）

2. **文件详情**：
   - 行为分析报告（动态分析结果）
   - 社区评论和标签
   - 文件关系图（传播链、家族关系）
   - 详细的PE结构信息
   - 字符串提取结果

3. **URL/域名扫描**：
   - 检测URL是否为恶意
   - 查看域名的WHOIS信息
   - 查看解析的IP地址
   - 查看关联的恶意样本

4. **IP地址查询**：
   - 查看IP的地理位置和运营商
   - 查看IP上托管的恶意样本
   - 查看IP的信誉评分
   - 查看关联的域名

5. **搜索功能**：
   - 按文件哈希搜索
   - 按URL/域名/IP搜索
   - 高级搜索（按检测名、文件类型、大小等）
   - 内容搜索（VirusTotal Enterprise）

**使用技巧：**
- 文件上传后，搜索结果中的检测率是重要参考
- 关注行为分析报告中的IOC信息
- 查看"Relations"标签页发现关联样本
- 查看"Community"标签页获取社区分析
- 使用VirusTotal API进行批量查询

#### 7.4.2 Hybrid Analysis

Hybrid Analysis是基于Falcon Sandbox的在线威胁分析平台，以深度行为分析著称。

**特色功能：**
- 详细的行为分析报告
- 内存取证分析
- 恶意软件家族自动识别
- 威胁标签系统
- 共享社区报告
- 支持搜索样本中的字符串、API调用等

**使用场景：**
- 获取详细的行为分析报告
- 提取内存中的Payload
- 查询特定恶意软件家族的样本
- 下载PCAP和内存Dump进行深入分析

#### 7.4.3 ANY.RUN

ANY.RUN是交互式在线沙箱，最大的特点是可以实时操作虚拟机。

**特色功能：**
- 实时交互式操作虚拟机
- 实时显示进程、文件、注册表、网络活动
- 支持手动触发恶意行为
- 支持文件上传和下载
- 完整的抓包文件下载
- 丰富的过滤和搜索功能

**适用场景：**
- 分析需要用户交互的恶意软件
- 手动触发特定的恶意行为
- 实时观察恶意代码执行过程
- 验证静态分析的结论

#### 7.4.4 其他威胁情报平台

**MalwareBazaar：**
- 由abuse.ch运营的恶意软件样本库
- 免费下载恶意样本
- 按家族、标签、时间筛选
- 提供SHA-256查询

**URLhaus：**
- 同样由abuse.ch运营
- 专注于恶意URL情报
- 实时更新恶意URL
- 提供API和数据导出

**ThreatFox：**
- IOC共享平台
- 社区驱动的IOC情报
- 支持按威胁类型、家族筛选

**MISP（Malware Information Sharing Platform）：**
- 开源的威胁情报共享平台
- 企业和组织内部部署
- 支持IOC管理、事件关联、自动化工作流
- 支持STIX/TAXII等标准格式

#### 7.4.5 威胁情报利用流程

**日常分析工作流：**

1. **获取样本**：从告警、邮件、终端等渠道获取可疑文件
2. **初步查询**：
   - 计算文件哈希
   - 在VirusTotal、Hybrid Analysis等平台查询哈希
   - 如果已有分析结果，快速了解威胁情况
3. **本地分析**：
   - 静态分析和动态分析
   - 提取IOC
4. **情报关联**：
   - 将提取的IOC与威胁情报平台数据关联
   - 查询IP/域名的信誉和历史记录
   - 查找同家族的其他样本
5. **情报产出**：
   - 编写分析报告
   - 生成检测规则（YARA、Snort等）
   - 更新威胁情报库
6. **防御部署**：
   - 将IOC导入防火墙、IDS、EDR等防护设备
   - 更新检测规则
   - 加强相关威胁的监控

---