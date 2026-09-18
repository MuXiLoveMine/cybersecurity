# Web 框架与中间件安全

> Web 框架与中间件是应用运行的基座，其自身缺陷或配置不当会直接导致从信息泄露到远程代码执行的全链路风险。本文档系统覆盖主流框架、Web 服务器与中间件的安全原理、典型案例与加固方案，填补学习指南中 15 个子领域仅 2 个部分覆盖的缺口。

---

## 一、Web 框架安全概述

### 1.1 框架安全 vs 原生代码安全

原生代码安全关注开发者编写的业务逻辑缺陷（拼接 SQL、未转义输出等）；框架安全则关注框架自身机制被滥用或框架内置高危功能默认开启所引入的系统性风险。二者的核心差异：

| 维度 | 原生代码安全 | 框架安全 |
|------|-------------|---------|
| 漏洞归属 | 开发者业务逻辑 | 框架设计/默认配置 |
| 影响范围 | 单一应用点 | 所有使用该框架的应用 |
| 修复方式 | 修改业务代码 | 升级框架版本/改配置 |
| 典型案例 | 手写 SQL 注入 | Struts2 OGNL 注入 |

### 1.2 框架漏洞的普遍性影响

框架漏洞具有"一损俱损"的特征：同一漏洞影响全球大量应用，且由于框架封装层级深，开发者往往误以为"用了框架就安全"。典型如 Spring4Shell（CVE-2022-22965）一次曝光即影响全球数十万 Java 应用，Struts2 OGNL 系列漏洞（S2-001 到 S2-061）更是推动了"框架即攻击面"的认知转变。

---

## 二、Java 框架安全

### 2.1 Spring 框架安全

#### 2.1.1 Spring MVC 常见漏洞

**SpEL 注入**

Spring 表达式语言（SpEL）在 `@Value`、`@Conditional` 等注解中被广泛使用。当用户输入流入 SpEL 解析上下文时，可构造任意表达式实现 RCE。

漏洞示例：
```java
// 危险写法：用户可控参数直接进入 SpEL
ExpressionParser parser = new SpelExpressionParser();
Expression exp = parser.parseExpression(userInput); // T(java.lang.Runtime).getRuntime().exec('calc')
exp.getValue();
```

安全加固：
- 禁止用户输入进入 SpEL 表达式
- 使用 `SimpleEvaluationContext` 限制表达式能力（默认禁用类型引用与方法调用）
```java
EvaluationContext context = SimpleEvaluationContext.forReadOnlyDataBinding().build();
parser.parseExpression(expr).getValue(context);
```

**路径遍历**

Spring MVC 的 `Resource` 解析器在特定版本下可被构造 `../` 序列绕过静态资源映射，读取应用类路径外的文件。

#### 2.1.2 Spring Boot Actuator 暴露

Actuator 端点默认提供 `/env`、`/heapdump`、`/mappings` 等调试接口。若未配置安全策略直接暴露到公网，攻击者可读取环境变量中的数据库密码、下载堆转储分析内存中的密钥，甚至通过 `/jolokia` 实现 RCE。

安全加固清单：
```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info   # 仅暴露必要端点
  endpoint:
    env:
      enabled: false           # 禁用敏感端点
    heapdump:
      enabled: false
```

#### 2.1.3 Spring Security 配置误区

常见误区：
- `permitAll()` 范围过大，覆盖了需认证的接口
- CSRF 防护被全局 `csrf().disable()` 关闭
- 密码编码器使用已废弃的 `NoOpPasswordEncoder`（明文存储）

#### 2.1.4 CVE-2022-22965（Spring4Shell）案例分析

**漏洞原理**：Spring 通过 `CachedIntrospectionResults` 缓存 Java Bean 属性描述符。当 Spring 使用反射将 HTTP 参数绑定到对象时，攻击者可通过 `class.module.classLoader.xxx` 的属性链访问到 `Tomcat` 的 `WebappClassLoader`，进而写入 JSP WebShell 实现 RCE。

**利用条件**：JDK 9+、运行于 Tomcat 容器、参数绑定使用 `@ModelAttribute` 或表单绑定。

**影响**：该漏洞利用了 Java 模块系统（JDK 9 引入的 `class.getModule()`），是典型的"语言特性 + 框架机制"组合型漏洞。

**加固方案**：升级至 Spring Framework 5.3.18+/5.2.20+，或在 `WebMvcConfigurer` 中注册全局参数过滤策略。

### 2.2 Struts2 安全

#### 2.2.1 OGNL 表达式注入原理

Struts2 使用 OGNL（Object-Graph Navigation Language）作为表达式语言，将 HTTP 参数绑定到 Action 属性。OGNL 支持方法调用、静态方法访问、类实例化，当用户可控数据进入 OGNL 解析上下文时即可执行任意代码。

经典 Payload 结构：
```
%{#_memberAccess=@java.lang.Runtime@getRuntime().exec('id')}
```

#### 2.2.2 CVE-2017-5638（S2-045）案例分析

**漏洞原理**：Struts2 的 Jakarta Multipart 解析器在处理异常的 Content-Type 头时，将错误信息直接拼入 OGNL 表达式执行。攻击者只需在 Content-Type 中注入 OGNL 表达式即可 RCE，无需任何业务参数。

**利用特征**：单 HTTP 请求即可触发，Payload 位于请求头，极易被 WAF 通过特征检测拦截，但通过编码变形可绕过。

**影响**：该漏洞导致大量政府、金融网站被攻陷，是推动"框架漏洞应急响应"标准化的标志性事件。

#### 2.2.3 Struts2 安全配置建议

- 升级至 Struts 2.5.30+（最终安全版本线）
- 若无法升级，移除 Jakarta Multipart 解析器，改用其他上传处理方式
- 配置 OGNL 黑名单（`struts.ognl.blacklist`）并禁用静态方法访问
- 部署 WAF 规则拦截 Content-Type 中的 `%{`、`${` 特征

### 2.3 MyBatis / Hibernate 安全

**MyBatis 动态 SQL 注入**

MyBatis 使用 `#{}` 进行参数预编译（安全），但 `${}` 直接拼接 SQL（危险）。开发者误用 `${}` 接收用户输入即导致注入：

```xml
<!-- 危险：直接拼接 -->
<select id="findByName">
  SELECT * FROM users WHERE name = '${name}'
</select>
<!-- 安全：预编译参数 -->
<select id="findByName">
  SELECT * FROM users WHERE name = #{name}
</select>
```

加固原则：除表名/列名等无法预编译的场景外，一律使用 `#{}`；对排序字段等动态值使用白名单校验。

**Hibernate HQL 注入**

HQL（Hibernate Query Language）使用命名参数可防注入，但拼接式 HQL 同样存在注入风险：
```java
// 危险：字符串拼接 HQL
String hql = "FROM User WHERE name = '" + name + "'";
// 安全：命名参数
String hql = "FROM User WHERE name = :name";
query.setParameter("name", name);
```

---

## 三、Python 框架安全

### 3.1 Django 安全

**Django ORM SQL 注入**

Django ORM 默认使用参数化查询，安全度高。但 `QuerySet.extra()` 和 `RawSQL()` 可绕过保护，`raw()` 方法接收原始 SQL 时若拼接用户输入则可注入。CVE-2022-28346 修复了 `QuerySet.order_by()` 接受整数参数时的注入问题。

**模板注入（SSTI）**

Django 模板引擎默认开启自动转义（auto-escape），XSS 风险较低。但 `mark_safe()` 标记内容为安全后会跳过转义，若标记了用户可控数据则导致 XSS。Django 模板本身不支持任意 Python 代码执行，SSTI 风险低于 Flask/Jinja2。

**Security 中间件配置**

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    ...
]
SECURE_SSL_REDIRECT = True           # 强制 HTTPS
SECURE_HSTS_SECONDS = 31536000       # HSTS 一年
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True    # 防 MIME 嗅探
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SECURE = True         # Cookie 仅 HTTPS 传输
CSRF_COOKIE_SECURE = True
```

### 3.2 Flask 安全

**Jinja2 SSTI**

Flask 默认使用 Jinja2 模板。当用户输入被直接作为模板字符串渲染时（`render_template_string(user_input)`），攻击者可注入 `{{ }}` 语法调用 Python 内置对象链实现 RCE：

```python
# 危险
return render_template_string(request.args.get('name'))
# Payload: {{ ''.__class__.__mro__[1].__subclasses__()[xxx]('id',shell=True) }}
```

安全加固：
- 使用 `render_template()` 渲染文件模板，禁止 `render_template_string` 接收用户输入
- 开启 Jinja2 沙箱模式（`SandboxedEnvironment`）
- 对用户输入做字符串级别的输出编码，而非模板渲染

**Flask debug 模式风险**

`app.run(debug=True)` 启用 Werkzeug 调试器，允许在浏览器中执行任意 Python 代码（PIN 码可被爆破或预测）。生产环境严禁开启 debug，应使用 `waitress`/`gunicorn` 部署。

**Flask 安全加固清单**
- `SESSION_COOKIE_SECURE = True`、`SESSION_COOKIE_HTTPONLY = True`、`SESSION_COOKIE_SAMESITE = 'Lax'`
- `app.config['SECRET_KEY']` 使用随机长密钥，禁止硬编码默认值
- 启用 `flask_talisman` 添加安全响应头与 CSP
- `debug=False`，生产环境用 WSGI 服务器部署

### 3.3 FastAPI 安全

**输入验证**

FastAPI 基于 Pydantic 模型进行输入校验，类型不符自动拒绝。但仍需注意：
- 正则约束字段格式（邮箱、手机号）
- 字符串长度限制防 DoS
- 嵌套对象深度限制

```python
from pydantic import BaseModel, Field, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=20, pattern=r'^[a-zA-Z0-9_]+$')
```

**认证与授权**

FastAPI 内置 OAuth2 与 JWT 支持。注意 `Depends(get_current_user)` 必须覆盖所有需认证的路由，避免遗漏导致未授权访问。

---

## 四、PHP 框架安全

### 4.1 Laravel 安全特性

Laravel 内置 CSRF 令牌（`@csrf`）、Eloquent ORM 参数绑定、Blade 模板自动转义，安全基线较高。主要风险点：
- `unserialize()` 调用链导致的反序列化 RCE（Laravel CVE-2018-15133 通过 API Token 触发）
- `.env` 文件泄露（调试模式开启时 `whoops` 页面会暴露环境变量）

### 4.2 ThinkPHP RCE 漏洞系列分析

ThinkPHP 因框架路由与控制器调度机制缺陷，多次出现 RCE 漏洞：

- **ThinkPHP 5.x RCE**：路由解析时未过滤 `controller` 与 `method` 参数，可通过 `s=index/\think\app/invokefunction` 调用任意类的任意方法。Payload 形如 `?s=index/think\app/invokefunction&function=call_user_func_array&vars[0]=phpinfo`
- **ThinkPHP 5.0.23/5.1.30 RCE**：方法名中可注入 `\think\` 命名空间路径调用系统类
- **ThinkPHP 6.x**：改进了路由与控制器调度，但 `composer` 依赖与中间件配置仍需审计

加固方案：升级至最新稳定版；生产环境关闭 `app_debug` 与 `app_trace`；限制路由调度范围，使用严格路由匹配。

### 4.3 Symfony 组件漏洞

Symfony 的 `VarDumper`、`Serializer` 等组件被广泛复用（Laravel 也依赖部分 Symfony 组件）。CVE-2022-23614 中 `Uid` 组件的反序列化缺陷影响了所有依赖该组件的项目。这体现了"组件级供应链风险"——漏洞不在你直接使用的框架中，而在其传递依赖中。

---

## 五、Node.js 框架安全

### 5.1 Express 安全

**原型链污染**

JavaScript 中对象默认继承自 `Object.prototype`。当使用不安全的合并函数（如 `merge`/`extend`/`defaultsDeep`）处理用户 JSON 输入时，攻击者可注入 `{"__proto__": {"isAdmin": true}}` 污染原型，影响所有对象实例。

```javascript
// 危险：不安全的递归合并
function merge(target, source) {
  for (let key in source) {
    target[key] = (typeof source[key] === 'object') ? merge(target[key], source[key]) : source[key];
  }
  return target;
}
// Payload: {"__proto__": {"isAdmin": true}}
```

加固方案：使用 `Object.create(null)` 创建无原型对象；使用 `Object.getOwnPropertyNames` 替代 `for...in`；使用已修复原型链污染的库版本（lodash >= 4.17.20）。

**中间件安全**

Express 中间件执行顺序决定安全边界。常见误区：`bodyParser` 全局启用解析大文件导致 DoS；静态文件中间件未限制路径导致目录穿越；`cors` 中间件配置 `origin: '*'` 与 `credentials: true` 同时使用导致 CORS 失控。

### 5.2 Vue / React 服务端渲染安全

SSR（服务端渲染）将模板在服务端执行，若模板中插入了未转义的用户数据，XSS 风险从客户端迁移到服务端。Vue 的 `v-html` 和 React 的 `dangerouslySetInnerHTML` 是主要危险点。SSR 场景下还可能将服务端变量（如数据库连接信息）渲染进 HTML 源码导致泄露。

---

## 六、Web 服务器安全

### 6.1 Nginx 安全配置

**配置不当导致目录穿越**

```nginx
location /files {
  alias /data/share/;   # 若 location 无尾斜杠而 alias 有，可穿越
}
# 请求 /files../etc/passwd → 读取 /data/share/../etc/passwd
```

加固：`location` 与 `alias` 路径的尾部斜杠必须一致，或使用 `root` 替代。

**CRLF 注入**

Nginx 在 `$uri` 变量中未过滤 `\r\n`，若将 `$uri` 反射到响应头（如重定向 `Location`），攻击者可注入 `%0d%0a` 实现 HTTP 响应拆分。

```nginx
# 危险
return 302 https://example.com$uri;
# 安全：使用 $request_uri（已编码）或显式过滤
return 302 https://example.com/;
```

**Nginx 安全加固清单**
```nginx
server_tokens off;              # 隐藏版本号
client_max_body_size 1m;         # 限制请求体大小
limit_req_zone ... zone=req:10m rate=10r/s;  # 限速防 CC
add_header X-Frame-Options SAMEORIGIN;
add_header X-Content-Type-Options nosniff;
add_header Content-Security-Policy "default-src 'self'";
ssl_protocols TLSv1.2 TLSv1.3;  # 禁用旧版 TLS
```

### 6.2 Apache 安全配置

**.htaccess 滥用**

Apache 允许目录级 `.htaccess` 覆盖主配置。若攻击者能上传 `.htaccess` 文件，可将任意扩展名解析为 PHP 执行：
```
AddType application/x-httpd-php .jpg
```

加固：生产环境 `AllowOverride None` 禁用 `.htaccess`，配置集中在 httpd.conf。

**路径穿越**

Apache 的 `<Directory>` 配置与 `mod_alias` 的 `Alias` 指令路径处理不一致时可导致穿越。

**Apache 安全加固清单**
- 隐藏版本号：`ServerTokens Prod`、`ServerSignature Off`
- 禁用 `.htaccess`：`AllowOverride None`
- 限制 HTTP 方法：仅允许 GET/POST/HEAD
- 关闭目录列表：`Options -Indexes`
- 移除不必要的模块（mod_info、mod_status）

### 6.3 IIS 安全

**短文件名枚举**

IIS 在 NTFS 文件系统上利用 8.3 短文件名机制（如 `SECRET~1.TXT`），攻击者可通过 `~` 通配符逐字符探测，枚举出完整文件名。该漏洞虽不直接泄露内容，但暴露了文件结构信息。

**解析漏洞**

IIS 6.0 存在经典解析漏洞：
- 分号解析：`test.asp;.jpg` → 按 ASP 执行
- 目录解析：`test.asp/test.jpg` → 按 ASP 执行

IIS 7.x 在 `cgi.fix_pathinfo=1`（PHP 配置）时，`test.jpg/.php` 会按 PHP 执行。

加固：升级 IIS 版本；PHP 配置 `cgi.fix_pathinfo=0`；禁止上传目录的执行权限。

---

## 七、中间件安全

### 7.1 Tomcat 安全

**Manager 后台弱口令**

Tomcat Manager 应用默认路径 `/manager/html`，若配置了弱口令或默认凭据（`tomcat/tomcat`），攻击者可上传 WAR 包直接 getshell。

**AJP 协议漏洞（CVE-2020-1938 Ghostcat）**

Tomcat AJP（Apache JServ Protocol）端口默认 8009，用于反向代理与 Tomcat 通信。Ghostcat 漏洞允许攻击者通过 AJP 协议读取 `webapps` 下任意文件，配合文件包含可 RCE。

加固：生产环境关闭 AJP 连接器，或配置 `secret` 与 `secretRequired` 属性限制访问。

**WAR 部署安全**

禁止自动热部署（`autoDeploy="false"`），限制 Manager 应用访问来源 IP，部署后删除默认示例应用。

### 7.2 Weblogic 安全

**T3 协议漏洞**

Weblogic T3 协议用于 RMI 通信，反序列化漏洞密集（CVE-2015-4852、CVE-2018-2628 等）。攻击者发送恶意序列化对象即可 RCE。

加固：通过网络层限制 T3 端口仅对可信主机开放；配置反序列化白名单过滤器。

**XMLDecoder 反序列化**

Weblogic 的 WLS Security 组件使用 `XMLDecoder` 解析 XML 数据，CVE-2017-10271 通过构造恶意 XML 实现 RCE。

**SSRF 漏洞**

Weblogic 的 UDDI 模块（`/uddiexplorer`）存在 SSRF，可用于探测内网与攻击 Redis 等组件。

加固：删除或限制 UDDI 模块访问；升级补丁；配置 Weblogic 安全域。

### 7.3 JBoss / WildFly 安全

主要风险：JMX 控制台（`/jmx-console`）与 Web 控制台未授权访问，攻击者可通过 JMX `deploy` 方法部署恶意 WAR 包。`invoker/JMXInvokerServlet` 的反序列化漏洞也是常见入口。

加固：移除管理控制台或配置认证；关闭 JMX 远程访问；升级 WildFly 替代旧版 JBoss。

### 7.4 Redis 安全

**未授权访问**

Redis 默认无密码且监听 `0.0.0.0:6379`，攻击者可直接连接执行任意命令。

**主从复制 RCE**

Redis 2.8+ 支持主从复制。攻击者伪装为主节点，受害 Redis 作为从节点同步恶意 `.so` 模块并 `MODULE LOAD` 加载，实现任意命令执行。

**Lua 脚本安全**

Redis `EVAL` 执行 Lua 脚本，`loadstring` 等函数可加载恶意代码。CVE-2022-0543 在 Debian/Ubuntu 打包的 Redis 中，Lua 沙箱可被绕过实现 RCE（沙箱未禁用 `package` 模块）。

加固清单：
```conf
bind 127.0.0.1           # 仅监听本地
requirepass <强密码>      # 配置认证
rename-command FLUSHALL ""  # 禁用危险命令
rename-command CONFIG ""
protected-mode yes       # 开启保护模式
```

### 7.5 MongoDB 安全

默认无认证且监听 `0.0.0.0:27017`。未授权访问可读取/修改全部数据库。曾出现大规模 MongoDB 数据库被勒索删除的事件（攻击者删除数据后留勒索信）。

加固：启用 `authorization: enabled`；绑定内网 IP；配置防火墙白名单。

### 7.6 RabbitMQ / Kafka 消息队列安全

**RabbitMQ**：默认管理控制台 `15672` 端口，弱口令（`guest/guest`）在旧版本可远程登录。加固：删除默认 guest 账户；配置 TLS 传输加密；限制管理端口访问来源。

**Kafka**：无认证时任意客户端可读写 Topic。加固：启用 SASL 认证（PLAIN/SCRAM）+ ACL 授权；配置 TLS 加密传输；Kafka Manager / Kafka Eagle 等管理工具需配置认证。

---

## 八、容器化中间件安全

### 8.1 Docker 中的中间件安全考量

容器化部署改变了中间件的暴露方式，引入新的安全考量：

- **端口映射风险**：`-p 6379:6379` 将内部服务暴露到宿主机所有接口，绕过应用层网络隔离
- **特权容器**：`--privileged` 赋予容器近乎宿主机 root 权限，中间件容器不应使用
- **挂载敏感路径**：挂载 `/var/run/docker.sock` 使容器可控制 Docker 守护进程
- **镜像供应链**：拉取的中间件镜像可能内置后门或使用过时版本

加固方案：
```dockerfile
# 最小化镜像、指定版本
FROM redis:7.2-alpine
USER nobody              # 非 root 运行
# docker run 时限制资源与能力
docker run --cap-drop ALL --cap-add CHOWN \
  --network=internal-net -p 127.0.0.1:6379:6379 \
  redis:7.2-alpine
```

### 8.2 Kubernetes 中间件隔离

在 K8s 中，中间件通过 Pod 暴露，需关注：
- **NetworkPolicy**：默认 Pod 间网络互通，必须配置命名空间与标签级网络策略隔离数据库与中间件 Pod
- **RBAC**：ServiceAccount 的 ClusterRoleBinding 范围最小化，禁止中间件 Pod 使用默认高权限 SA
- **Secret 管理**：中间件密码以 K8s Secret 注入，而非环境变量明文；敏感配置使用外部密钥管理（Vault、Sealed Secrets）
- **Pod Security Standards**：设置 `restricted` 级别，禁止 `privileged`、`hostPath`、`hostNetwork`

---

## 九、中间件漏洞扫描与检测

### 9.1 Nmap 服务识别

Nmap 的服务版本探测（`-sV`）与脚本引擎（NSE）可识别中间件类型与版本：
```bash
nmap -sV -p 8080,6379,27017 --script=http-title,banner target
nmap --script=http-enum -p 80 target   # 探测 Web 路径与中间件类型
```

### 9.2 中间件指纹识别

指纹识别方法：
- **HTTP 响应头**：`Server: nginx/1.18.0`、`X-Powered-By: PHP/7.4`
- **默认页面特征**：Tomcat 默认主页、Weblogic 登录页
- **错误页面**：IIS、Nginx、Apache 的错误页 HTML 结构差异
- **Cookie 特征**：`JSESSIONID`（Java）、`PHPSESSID`（PHP）、`connect.sid`（Node.js）
- **工具辅助**：Wappalyzer（浏览器插件）、WhatWeb（CLI）、httpx（批量探测）

### 9.3 已知漏洞利用检测（理论）

识别版本后，匹配 CVE 数据库判断是否存在已知漏洞。常用方法：
- Nuclei 模板化检测（`nuclei -t cves/ -u target`）
- 搜索 NVD（National Vulnerability Database）匹配版本范围
- 中间件官方安全公告对照

注意：实际利用测试仅在授权范围内进行，本节仅介绍检测原理。

### 9.4 Python 中间件安全检查脚本示例

以下脚本整合常见中间件指纹识别与未授权访问检测逻辑，适用于授权安全评估：

```python
import socket
import requests
from concurrent.futures import ThreadPoolExecutor

class MiddlewareScanner:
    """中间件安全扫描器：指纹识别 + 未授权访问检测"""

    # 常见中间件指纹与默认端口
    FINGERPRINTS = {
        'Redis':    {'port': 6379, 'probe': b'INFO\r\n', 'keyword': b'redis_version'},
        'MongoDB':  {'port': 27017, 'probe': b'\x3a\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\xd4\x07\x00\x00\x00\x00\x00\x00admin.$cmd\x00\x00\x00\x00\x01\x00\x00\x00\x15\x00\x00\x00\x10listdatabases\x00\x01\x00\x00\x00', 'keyword': b'databases'},
        'Tomcat':   {'port': 8080, 'http': True, 'path': '/', 'header_keyword': 'Apache-Coyote'},
        'Weblogic': {'port': 7001, 'http': True, 'path': '/console/login/LoginForm.jsp', 'body_keyword': 'WebLogic'},
        'Elasticsearch': {'port': 9200, 'http': True, 'path': '/', 'body_keyword': 'cluster_name'},
    }

    def __init__(self, target, timeout=3):
        self.target = target
        self.timeout = timeout
        self.results = []

    def check_tcp_service(self, port, probe, keyword):
        """TCP 协议指纹探测（Redis/MongoDB 等）"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((self.target, port))
            sock.send(probe)
            resp = sock.recv(4096)
            sock.close()
            return keyword in resp
        except (socket.timeout, ConnectionRefusedError, OSError):
            return False

    def check_http_service(self, port, path, header_keyword=None, body_keyword=None):
        """HTTP 协议指纹探测（Tomcat/Weblogic 等）"""
        url = f'http://{self.target}:{port}{path}'
        try:
            resp = requests.get(url, timeout=self.timeout, verify=False)
            if header_keyword and header_keyword in resp.headers.get('Server', ''):
                return True
            if body_keyword and body_keyword in resp.text:
                return True
        except requests.RequestException:
            pass
        return False

    def scan(self):
        for name, fp in self.FINGERPRINTS.items():
            if fp.get('http'):
                found = self.check_http_service(
                    fp['port'], fp.get('path', '/'),
                    fp.get('header_keyword'), fp.get('body_keyword')
                )
            else:
                found = self.check_tcp_service(fp['port'], fp['probe'], fp['keyword'])

            if found:
                self.results.append({
                    'middleware': name,
                    'port': fp['port'],
                    'risk': 'identified - 需进一步检查未授权访问与版本漏洞'
                })

    def report(self):
        if not self.results:
            print('[*] 未识别到常见中间件服务')
            return
        print(f'{"中间件":<18}{"端口":<10}{"风险提示"}')
        print('-' * 60)
        for r in self.results:
            print(f'{r["middleware"]:<18}{r["port"]:<10}{r["risk"]}')


# 使用示例（仅限授权测试）
if __name__ == '__main__':
    scanner = MiddlewareScanner('127.0.0.1')
    scanner.scan()
    scanner.report()
```

> **合规声明**：上述脚本仅用于授权安全评估与自测环境。对未授权目标进行扫描属于违法行为，可能违反《网络安全法》与《刑法》第 285 条。

---

## 十、安全加固总结

### 10.1 通用加固原则

1. **最小暴露面**：关闭非必要端口与管理界面，中间件仅监听内网接口
2. **认证与授权**：所有管理控制台配置强认证，默认账户删除或改密码
3. **版本管理**：关注 CVE 公告，建立中间件版本台账与定期更新机制
4. **配置审计**：生产环境关闭调试模式、trace 页面、示例应用
5. **网络隔离**：数据库/消息队列与 Web 应用分网段，配置防火墙策略
6. **加密传输**：管理通道与数据传输启用 TLS，禁用旧版协议

### 10.2 框架安全生命周期

- 开发阶段：使用框架内置安全机制（ORM 参数化、模板自动转义），禁止绕过
- 部署阶段：关闭调试端点，配置安全响应头与 HTTPS
- 运维阶段：监控 CVE 公告，建立补丁管理与应急响应流程
- 容器化阶段：镜像版本锁定，网络策略隔离，非特权运行

> 框架与中间件安全的本质是"减少攻击面、消除默认信任"。开发者应建立"框架即攻击面"的意识——使用框架不等于安全，正确配置与持续维护才是安全的基石。
