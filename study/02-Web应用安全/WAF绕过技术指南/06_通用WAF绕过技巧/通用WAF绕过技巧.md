# 通用WAF绕过技巧

### 6.1 HTTP参数污染（HPP）

HPP适用于多种攻击场景，核心是利用前后端对同名参数的不同处理方式：

```
HPP在各场景的应用:
├── SQL注入
│   → 分割SQL关键字到不同参数
│   → 利用后端拼接绕过WAF
│
├── XSS
│   → 分割XSS Payload
│   → 利用后端拼接渲染
│
├── 命令注入
│   → 分割命令到不同参数
│
└── 路径穿越
    → 分割../序列
```

**后端参数处理差异表：**

| 后端语言 | 同名参数处理 | 示例(id=1&id=2) |
|----------|-------------|-----------------|
| PHP | 取最后一个 | id=2 |
| ASP.NET | 逗号拼接 | id=1,2 |
| JSP/Servlet | 取第一个 | id=1 |
| Python Flask | 取第一个 | id=1 |
| Node.js Express | 数组 | id=["1","2"] |
| Python Django | 取最后一个 | id=2 |

### 6.2 分块传输编码（Chunked Transfer）

利用HTTP/1.1的分块传输机制绕过WAF的内容检测：

```
分块传输绕过原理:
1. 请求体被分为多个chunk
2. WAF可能:
   a. 不支持分块解析 → 看不到完整Payload
   b. 逐chunk检查 → 每个chunk都是碎片
   c. 重组后检查 → 可被超时绕过
3. 后端完整重组执行

关键技术:
- 利用chunk大小字段混淆
- 在chunk间插入干扰数据
- 超长chunk耗尽WAF缓冲
```

**分块变形：**

```
POST /target.php HTTP/1.1
Transfer-Encoding: chunked

4
TE
4
st1
0

→ 重组后: TEst1

变形1: chunk大小带空格
0x 4\r\n  → 某些WAF解析失败

变形2: 多余数据
4\r\n
Test\r\n
;comment\r\n  → 注释行干扰WAF
0\r\n

变形3: 超长chunk
10000000\r\n  → 声称很大但发送少量数据
```

### 6.3 超长URL/请求体

利用WAF对请求体长度限制，将恶意Payload淹没在大量数据中：

```
超长请求绕过:
1. 在参数中填充大量垃圾数据
2. WAF因性能限制不检查超长请求体
3. 后端截取有效部分执行Payload

示例:
POST /search.php HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Content-Length: 1048576

id=1 UNION SELECT 1,user(),3&junk=AAAA...(100万字符)...AAAA
```

**防御：** WAF应配置合理的请求体大小限制和深度检测。

### 6.4 请求方法变换

利用非标准HTTP方法绕过WAF的规则匹配：

```
请求方法变换:
├── GET → POST/PUT/PATCH
├── GET → DEBUG (IIS特有)
├── GET → PROPFIND (WebDAV)
├── GET → 自定义方法 (如JENKINS)
└── 利用TRACE/XST

原理:
- WAF可能仅对GET/POST做深度检测
- 其他方法的检测规则可能不完善
- 后端通过$_REQUEST获取参数时忽略方法
```

### 6.5 协议层绕过

利用HTTP协议本身的特性绕过WAF：

```
协议层绕过:
├── HTTP/0.9
│   └── 不发送HTTP头，仅发送请求行
│
├── HTTP/2
│   ├── 二进制帧可能不被WAF正确解析
│   └── HPACK头压缩可能绕过检测
│
├── 请求走私（HTTP Request Smuggling）
│   ├── 利用前后端CL/TE差异
│   ├── CL.TE: 前端用Content-Length，后端用Transfer-Encoding
│   └── TE.CL: 前端用Transfer-Encoding，后端用Content-Length
│
├── HTTP响应拆分
│   ├── 利用CRLF注入修改响应
│   └── 注入Set-Cookie/Location
│
└── WebSocket
    ├── WAF可能不检查WebSocket流量
    └── 通过WebSocket传递攻击Payload
```

**请求走私示例（CL.TE）：**

```
POST / HTTP/1.1
Content-Length: 13
Transfer-Encoding: chunked

0

SMUGGLED
```

前端（WAF）用Content-Length=13读取完整请求，后端用Transfer-Encoding读到`0\r\n\r\n`结束，剩余的`SMUGGLED`被当作下一个请求的开头。

### 6.6 超时绕过

```
超时绕过策略:
├── 慢速HTTP攻击
│   ├── Slowloris: 缓慢发送HTTP头
│   └── 超长等待消耗WAF资源
│
├── 时间盲注配合
│   ├── WAF有超时限制（如5秒）
│   ├── 时间盲注sleep(10)超过WAF超时
│   └── WAF放弃检测，放行请求
│
└── 大数据慢传
    └── 以极低速率传输大量数据
```

---

---

