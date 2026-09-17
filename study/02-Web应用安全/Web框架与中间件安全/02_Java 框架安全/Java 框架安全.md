# Java 框架安全

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

---

## 📋 内容审核与补充建议

> 针对「Java 框架安全」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

---

## 📌 拓展学习资源

### 推荐学习路径
- 理论基础 → 工具实践 → 实战演练 → 深度研究
- 建议搭建本地实验环境进行动手练习

### 相关工具与资源
- 在线实验平台：Hack The Box、TryHackMe、VulnHub
- 技术文档：官方文档、RFC、OWASP 指南
- 社区资源：GitHub、安全论坛、技术博客
