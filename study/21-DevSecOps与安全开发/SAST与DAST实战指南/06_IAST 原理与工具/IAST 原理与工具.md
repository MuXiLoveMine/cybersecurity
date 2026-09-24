# IAST 原理与工具

### 6.1 IAST 工作原理

```
┌─────────────────────────────────────────────────────────┐
│                     IAST 工作原理                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  测试请求                                               │
│     │                                                    │
│     ▼                                                    │
│  ┌─────────┐    ┌─────────────────────┐                  │
│  │ 测试工具 │───→│   应用服务器         │                  │
│  │(功能测试)│    │  ┌───────────────┐ │                  │
│  └─────────┘    │  │  IAST Agent   │ │                  │
│                  │  │  (运行时插桩)  │ │                  │
│                  │  │               │ │                  │
│                  │  │ • 监控数据流   │ │                  │
│                  │  │ • 追踪污点     │ │                  │
│                  │  │ • 检测Sink     │ │                  │
│                  │  │ • 代码级定位   │ │                  │
│                  │  └───────┬───────┘ │                  │
│                  └──────────┼──────────┘                  │
│                             │                            │
│                             ▼                            │
│                    ┌────────────────┐                    │
│                    │  IAST 服务器     │                    │
│                    │  (结果聚合)     │                    │
│                    │  • 实时告警     │                    │
│                    │  • 漏洞报告     │                    │
│                    │  • 代码定位     │                    │
│                    └────────────────┘                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 6.2 OpenRASP-IAST 配置

```json
{
  "iast": {
    "enabled": true,
    "server_url": "http://iast-server:8080",
    "agent_token": "your-agent-token",
    "project_name": "ecommerce-app",
    "language": "java",

    "hooks": {
      "sql": {
        "enabled": true,
        "hook_points": [
          "java.sql.Statement.execute",
          "java.sql.Statement.executeQuery",
          "java.sql.PreparedStatement.execute"
        ]
      },
      "ssrf": {
        "enabled": true,
        "hook_points": [
          "java.net.URL.openConnection",
          "org.apache.http.client.methods.HttpGet"
        ]
      },
      "command_exec": {
        "enabled": true,
        "hook_points": [
          "java.lang.Runtime.exec",
          "java.lang.ProcessBuilder.start"
        ]
      },
      "file_include": {
        "enabled": true,
        "hook_points": [
          "java.io.FileInputStream",
          "java.io.FileReader"
        ]
      },
      "xss": {
        "enabled": true,
        "hook_points": [
          "javax.servlet.ServletOutputStream.print",
          "javax.servlet.jsp.JspWriter.print"
        ]
      },
      "deserialization": {
        "enabled": true,
        "hook_points": [
          "java.io.ObjectInputStream.readObject"
        ]
      }
    },

    "report": {
      "realtime": true,
      "interval": 5,
      "max_queue_size": 1000
    },

    "performance": {
      "max_hook_depth": 10,
      "max_data_length": 4096,
      "exclude_packages": [
        "java.lang",
        "sun.",
        "com.sun."
      ]
    }
  }
}
```

---

---

