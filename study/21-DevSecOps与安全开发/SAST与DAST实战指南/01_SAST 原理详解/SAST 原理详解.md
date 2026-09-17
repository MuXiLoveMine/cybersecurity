# SAST 原理详解

### 1.1 SAST 分析层次

SAST 通过多层次分析源代码来检测安全漏洞，每个层次逐步深入：

```
源代码
  │
  ├─ 1. 词法分析（Lexical Analysis）
  │     将源代码分解为 Token 流
  │     例：x = 1 + 2 → [ID:x, EQ, NUM:1, PLUS, NUM:2]
  │
  ├─ 2. 语法分析（Syntax Analysis）
  │     构建 AST（抽象语法树）
  │     例：Assign(x, Add(1, 2))
  │
  ├─ 3. 语义分析（Semantic Analysis）
  │     理解代码含义，类型检查
  │     例：x 是整数赋值
  │
  ├─ 4. 数据流分析（Data Flow Analysis）
  │     追踪数据在程序中的流动
  │     例：request.getParameter("id") → 变量 id → SQL 查询
  │
  ├─ 5. 控制流分析（Control Flow Analysis）
  │     理解程序执行路径
  │     例：if/else 分支可达性分析
  │
  └─ 6. 污点分析（Taint Analysis）
        追踪不可信数据的传播路径
        Source → 传播 → Sink
```

### 1.2 污点分析详解

污点分析是 SAST 检测注入类漏洞的核心技术。

**基本概念**
- **Source（污点源）**：不可信数据入口（如用户输入）
- **Sink（汇点）**：敏感操作执行点（如 SQL 执行、命令执行）
- **传播路径**：数据从 Source 到 Sink 的流动路径
- **Sanitizer（净化器）**：对污点数据进行清洗的函数

**污点分析流程示例**
```python
# Python 污点分析示例

# Source: 用户输入（污点源）
user_input = request.getParameter("id")  # [TAINT] 污点源：用户输入

# 传播：污点数据赋值给新变量
data = user_input                        # [TAINT] 传播：data 被污染

# 传播：污点数据进入函数
processed = process_data(data)           # [TAINT] 传播：processed 被污染

# Sink: SQL 查询执行（危险！污点到达 Sink）
query = "SELECT * FROM users WHERE id=" + processed
cursor.execute(query)                    # [ALERT] SQL 注入风险！

# 安全示例：使用参数化查询
cursor.execute("SELECT * FROM users WHERE id=%s", (user_input,))
# [SAFE] 参数化查询，污点被隔离
```

**污点分析规则定义示例（Semgrep）**
```yaml
# Semgrep 污点分析规则：检测 Python SQL 注入
rules:
  - id: python-sql-injection
    mode: taint
    pattern-sources:
      # 定义污点源：所有用户输入
      - patterns:
          - pattern: flask.request.form.get(...)
      - patterns:
          - pattern: flask.request.args.get(...)
      - patterns:
          - pattern: flask.request.cookies.get(...)
      - patterns:
          - pattern-either:
              - pattern: input(...)
              - pattern: sys.stdin.readline()

    pattern-sinks:
      # 定义汇点：所有 SQL 执行
      - patterns:
          - pattern: $CUR.execute(...)
          - pattern-not: $CUR.execute("...", ...)
      - patterns:
          - pattern: $CUR.executemany(...)
          - pattern-not: $CUR.executemany("...", ...)

    pattern-sanitizers:
      # 定义净化器：安全转换函数
      - pattern: int(...)
      - pattern: float(...)

    message: 检测到SQL注入风险，请使用参数化查询
    languages: [python]
    severity: ERROR
    metadata:
      cwe: "CWE-89: SQL Injection"
      owasp: "A03:2021-Injection"
```

### 1.3 控制流分析

控制流分析用于理解程序执行路径，检测可达性和逻辑漏洞。

**控制流图（CFG）示例**
```
        [Entry]
           │
           ▼
      [Input Validation]
       /         \
    Pass         Fail
     │             │
     ▼             ▼
[Process Data]  [Error Response]
     │             │
     ▼             ▼
[Output]      [Return Error]
     │             │
     └──────┬──────┘
            ▼
        [Exit]
```

**控制流分析应用场景**
- 检测不可达代码
- 验证错误处理路径
- 检查权限验证分支
- 分析资源释放路径
- 检测逻辑死锁

---

---

## 📋 内容审核与补充建议

> 针对「SAST 原理详解」部分的内容审核结果：

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
