# EDR 检测技术

### 3.1 特征检测

基于已知威胁特征（IOC）的精确匹配：

```json
// EDR 规则示例 - IOC 匹配
{
  "rule_name": "检测 Cobalt Strike Beacon",
  "rule_type": "ioc_match",
  "severity": "high",
  "conditions": {
    "match_any": [
      {
        "field": "process.command_line",
        "operator": "contains",
        "value": "cmd.exe /c powershell -enc"
      },
      {
        "field": "network.dns_query",
        "operator": "in",
        "value": ["evil-c2.com", "malware-cnc.net"]
      },
      {
        "field": "process.hash_sha256",
        "operator": "in",
        "value": ["a1b2c3...", "d4e5f6..."]
      },
      {
        "field": "file.path",
        "operator": "matches_regex",
        "value": ".*\\\\AppData\\\\Local\\\\Temp\\\\[a-z]{8}\\.exe$"
      }
    ]
  },
  "response": {
    "action": "quarantine_process",
    "block_network": true,
    "alert": true
  }
}
```

### 3.2 行为检测

基于行为模式的检测，不依赖具体特征：

```
行为检测规则 - 勒索软件检测

触发条件（满足3个以上即告警）：
├── 1. 短时间内大量文件修改 (>100次/分钟)
├── 2. 文件扩展名批量变更 (.docx → .locked)
├── 3. 文件内容被大量覆写
├── 4. 卷影副本被删除 (vssadmin delete shadows)
├── 5. 备份文件被删除
├── 6. 进程操作异常目录 (Documents/Desktop 全盘遍历)
└── 7. 存在已知勒索扩展名列表匹配
```

```python
# 行为检测伪代码 - 进程链分析
def detect_suspicious_process_chain(events):
    """
    检测可疑进程链，例如:
    Word → cmd.exe → powershell.exe → certutil.exe
    """
    suspicious_patterns = [
        # Office 文档 → 子进程执行
        ["winword.exe|excel.exe|powerpnt.exe", 
         "cmd.exe|powershell.exe"],
        # PowerShell → 编码执行
        ["powershell.exe", ".*-enc.*|-e "],
        # Certutil 下载
        ["cmd.exe", "certutil.exe", ".*-urlcache.*|.*-split.*"],
        # WMI 横向移动
        ["wmiprvse.exe", "cmd.exe|powershell.exe"],
        # SQL 注入执行命令
        ["sqlservr.exe", "cmd.exe|powershell.exe"],
    ]
    
    # 构建进程树
    process_tree = build_process_tree(events)
    
    # 遍历进程链匹配模式
    for leaf in process_tree.leaves():
        chain = get_chain_to_root(leaf)
        for pattern in suspicious_patterns:
            if match_pattern(chain, pattern):
                generate_alert(
                    severity="high",
                    chain=chain,
                    pattern=pattern
                )
```

### 3.3 机器学习检测

EDR 使用机器学习模型识别未知威胁：

| 模型类型 | 用途 | 特征示例 |
|----------|------|----------|
| 二分类模型 | 恶意/良性判定 | 文件熵值、API 调用序列 |
| 异常检测 | 行为基线偏离 | 进程行为基线对比 |
| 序列模型 | 时序行为分析 | 进程创建序列 LSTM |
| 图神经网络 | 攻击图分析 | 进程-文件-网络关系图 |

### 3.4 关联分析

将离散的安全事件关联为完整的攻击链：

```
MITRE ATT&CK 关联分析示例

攻击时间线:
T-0    用户收到钓鱼邮件，打开附件 invoice.docx
T+5s   Word 启动，加载恶意宏
T+10s  Word 创建子进程 powershell.exe (T1059)
T+12s  PowerShell 执行编码命令下载 Payload (T1105)
T+15s  PowerShell 创建计划任务实现持久化 (T1053)
T+20s  Payload 建立 C2 连接 (T1071)
T+30s  C2 下发命令，执行 whoami /priv (T1082)
T+35s  执行 net view 探测内网 (T1018)
T+60s  尝试 SMB 横向移动 (T1021)

EDR 关联分析输出:
├── 攻击阶段: 初始访问 → 执行 → 持久化 → 命令控制 → 横向移动
├── 入口点: invoice.docx (钓鱼邮件附件)
├── C2 通信: 192.168.x.x:443
├── 受影响主机: 终端A (初始感染) + 终端B (横向移动目标)
└── ATT&CK 覆盖: T1566, T1059, T1105, T1053, T1071, T1082, T1018, T1021
```

---

---

