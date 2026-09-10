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
