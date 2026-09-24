# Java 代码审计

### 3.1 Java Web 应用架构理解

```
请求 → DispatcherServlet → Filter 链 → Interceptor → Controller → Service → DAO → DB
```

| 组件 | 职责 | 审计关注点 |
|------|------|-----------|
| Servlet | 最底层请求处理 | `doGet/doPost` 中参数直接使用 |
| Filter | 请求过滤/鉴权 | 是否所有路由都经过安全 Filter |
| Interceptor | 业务拦截 | 鉴权逻辑是否完整 |
| Controller | 参数接收 | `@RequestParam`、`@PathVariable` 注入的参数流向 |

### 3.2 SQL 注入审计

```java
// —— 漏洞代码：JDBC 拼接 ——
String sql = "SELECT * FROM users WHERE name = '" + username + "'";
Statement stmt = conn.createStatement();
ResultSet rs = stmt.executeQuery(sql);
```

```java
// —— 漏洞代码：MyBatis ${} 注入 ——
// UserMapper.xml
@Select("SELECT * FROM users WHERE name = ${name}")  // ${} 是文本替换
List<User> findByName(@Param("name") String name);
```

```java
// —— 修复代码：PreparedStatement ——
String sql = "SELECT * FROM users WHERE name = ?";
PreparedStatement ps = conn.prepareStatement(sql);
ps.setString(1, username);
ResultSet rs = ps.executeQuery();

// —— 修复代码：MyBatis #{} ——
@Select("SELECT * FROM users WHERE name = #{name}")  // #{} 使用预编译占位符
List<User> findByName(@Param("name") String name);
```

审计要点：全局搜索 `Statement`、`createStatement`、`${`，判断 SQL 是否拼接用户输入。MyBatis 中 `${}` 是文本替换（危险），`#{}` 是预编译占位符（安全）。

### 3.3 命令注入审计

```java
// —— 漏洞代码 ——
String cmd = "ping " + request.getParameter("host");
Runtime.getRuntime().exec(cmd);
```

```java
// —— 修复代码 ——
String host = request.getParameter("host");
// 白名单校验
if (!host.matches("^[a-zA-Z0-9.\\-]+$")) {
    throw new IllegalArgumentException("非法参数");
}
ProcessBuilder pb = new ProcessBuilder("ping", host);
pb.start();
```

审计要点：搜索 `Runtime.exec`、`ProcessBuilder`，检查命令参数是否来自用户输入且未做白名单过滤。

### 3.4 反序列化漏洞审计

```java
// —— 漏洞代码：原生反序列化 ——
ObjectInputStream ois = new ObjectInputStream(request.getInputStream());
Object obj = ois.readObject();  // 可触发任意 readObject/readResolve
```

```java
// —— 漏洞代码：Fastjson ——
String json = request.getParameter("data");
Object obj = JSON.parseObject(json, Object.class);  // Fastjson <1.2.68 可 RCE
```

```java
// —— 修复代码 ——
// 使用 ObjectInputFilter（JDK 9+）
ObjectInputStream ois = new ObjectInputStream(request.getInputStream());
ois.setObjectInputFilter(info -> {
    return info.serialClass() != null ? ObjectInputFilter.Status.REJECTED
                                       : ObjectInputFilter.Status.UNDECIDED;
});

// Fastjson 修复：升级到最新版 + 关闭 AutoType
ParserConfig.getGlobalInstance().setAutoTypeSupport(false);
```

审计要点：搜索 `readObject(`、`JSON.parseObject`、`ObjectMapper.readValue`（开启默认类型），检查反序列化输入是否用户可控。

### 3.5 SSRF 审计

```java
// —— 漏洞代码 ——
URL url = new URL(request.getParameter("url"));
HttpURLConnection conn = (HttpURLConnection) url.openConnection();
InputStream is = conn.getInputStream();  // 可探测内网/读云元数据
```

```java
// —— 修复代码 ——
String urlStr = request.getParameter("url");
URL url = new URL(urlStr);
String host = url.getHost();
InetAddress addr = InetAddress.getByName(host);
// 拒绝内网地址
if (addr.isSiteLocalAddress() || addr.isLoopbackAddress()
        || addr.isLinkLocalAddress() || addr.isAnyLocalAddress()) {
    throw new SecurityException("禁止访问内网地址");
}
// 限制协议与端口
if (!url.getProtocol().matches("https?") || !url.getPort() isInAllowedPorts) {
    throw new SecurityException("协议或端口非法");
}
```

审计要点：搜索 `new URL(`、`HttpClient.execute`、`OkHttpClient.newCall`，检查 URL 参数是否用户可控且未做内网地址过滤。

### 3.6 表达式注入审计

| 引擎 | 触发场景 |
|------|----------|
| OGNL | Struts2 参数传递 |
| SpEL | Spring `@Value`、`ExpressionParser` |
| EL | JSP `${}`、`#{}` |

```java
// —— 漏洞代码：SpEL 注入 ——
ExpressionParser parser = new SpelExpressionParser();
Expression exp = parser.parseExpression(request.getParameter("expr"));
String result = exp.getValue(String.class);  // 可执行任意代码
```

```java
// —— 修复代码 ——
// 避免将用户输入传入表达式引擎
// 若必须使用，采用 SimpleEvaluationContext 限制能力
EvaluationContext context = SimpleEvaluationContext.forReadOnlyDataBinding().build();
Expression exp = parser.parseExpression(safeExpr);
String result = exp.getValue(context, String.class);
```

审计要点：搜索 `parseExpression`、`Ognl.getValue`、`MethodExpression`，检查表达式字符串是否用户可控。

### 3.7 文件上传审计

```java
// —— 漏洞代码 ——
// ServletFileUpload 直接保存用户文件名
String filename = item.getName();
File file = new File(uploadDir, filename);  // 路径穿越 + 任意文件类型
item.write(file);
```

```java
// —— 修复代码 ——
String filename = item.getName();
// 去除路径穿越
filename = new File(filename).getName();
// 白名单校验后缀
String ext = filename.substring(filename.lastIndexOf(".") + 1).toLowerCase();
if (!Arrays.asList("jpg", "png", "gif").contains(ext)) {
    throw new SecurityException("非法文件类型");
}
// 重命名文件
String safeName = UUID.randomUUID() + "." + ext;
item.write(new File(uploadDir, safeName));
```

### 3.8 Java 框架审计要点

| 框架 | 高危模式 |
|------|----------|
| **Spring** | SpEL 注入、`@PathVariable` 可控路由、Actuator 端点暴露 |
| **Struts2** | OGNL 表达式注入（S2-045 等历史漏洞） |

### 3.9 审计实战：模拟审计 Spring Boot 应用

```java
// UserController.java
@GetMapping("/user")
public User getUser(@RequestParam String name) {
    // —— 审计发现 1：MyBatis ${} 注入 ——
    return userMapper.findByName(name);  // XML 中使用 ${name}
    // —— 审计发现 2：SSRF ——
    // return httpService.fetch("http://internal-api/user?name=" + name);
}
```

```java
// 修复后
@GetMapping("/user")
public User getUser(@RequestParam String name) {
    return userMapper.findByName(name);  // XML 改为 #{name}
}
```

---

---

