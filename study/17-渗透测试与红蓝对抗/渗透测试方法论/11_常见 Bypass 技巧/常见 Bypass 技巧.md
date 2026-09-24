# 常见 Bypass 技巧

### 11.1 WAF 绕过

```
SQL 注入 WAF 绕过：

1. 大小写混合：
   UnIoN SeLeCt → UNION SELECT

2. 编码绕过：
   URL 编码：%55NION
   双重 URL 编码：%2555NION
   Unicode 编码：\u0055NION
   Hex 编码：0x554E494F4E

3. 注释绕过：
   /*!50000UNION*/ SELECT
   UN/**/ION SE/**/LECT

4. 空格替代：
   %09(TAB) %0a(LF) %0d(CR) %0c(FF)
   /**/ () +—

5. 关键字替代：
   UNION → UNION ALL
   SELECT → SELECT%0a
   AND → && 或 %26%26
   OR → || 或 %7C%7C

6. 函数替代：
   SUBSTRING → MID / SUBSTR
   ASCII → ORD
   CONCAT → CONCAT_WS / GROUP_CONCAT

XSS WAF 绕过：

1. 标签替代：
   <script> → <svg onload> <img onerror> <body onload>
   <a href="javascript:"> → <a href="ja%76ascript:">

2. 事件替代：
   onclick → onfocus onmouseover ontoggle

3. 编码绕过：
   <script>alert(1)</script>
   → <script>eval(String.fromCharCode(97,108,101,114,116,40,49,41))</script>
   → <script>\u0061\u006c\u0065\u0072\u0074(1)</script>
```

### 11.2 AV 绕过

```
AV（杀毒软件）绕过技术：

1. 编码混淆：
   - Shellcode 编码（Shikata Ga Nai）
   - XOR 编码
   - Base64 编码

2. 分离免杀：
   - Shellcode 与加载器分离
   - 从远程下载 Shellcode
   - 使用进程注入

3. 白名单利用：
   - 使用签名工具（如 sigthief）
   - 利用微软签名二进制（LOLBins）
   - 使用 certutil、bitsadmin 等

4. 内存加载：
   - 反射 DLL 注入
   - Shellcode 直接内存执行
   - AMSI Bypass

5. 工具免杀：
   - Veil Framework
   - Shellter
   - Avet
   - 自定义加载器
```

### 11.3 EDR 绕过

```
EDR（终端检测与响应）绕过技术：

1. API 直接调用：
   - Direct System Calls（直接系统调用）
   - Nt/Zw API 调用
   - 绕过用户态 Hook

2. 进程注入变体：
   - Process Hollowing（进程镂空）
   - Process Doppelgänging
   - Process Herpaderping

3. 驱动级操作：
   - 加载内核驱动
   - 直接操作 EDR 驱动

4. 间接执行：
   - 通过 COM 对象执行
   - 利用计划任务
   - 利用 WMI

5. 禁用/绕过 EDR：
   - 修改 EDR 注册表项
   - 停止 EDR 服务
   - 利用 EDR 漏洞
```

---

---

