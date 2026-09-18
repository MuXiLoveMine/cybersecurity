# 第七章：Java Web 基础

> Java 详细内容和代码示例请查看 `java/Java基础.md` 和 `java/` 目录中的示例文件。

### 7.1 Java 简介

Java 是一种面向对象的编程语言，以"一次编写，到处运行"著称。Java Web 是企业级应用的主流技术栈。

**特点**：
- 强类型、面向对象
- 跨平台（JVM）
- 生态庞大，企业级框架成熟
- 性能好，稳定性高

### 7.2 Java 基本语法

```java
// HelloWorld.java
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");

        // 变量（强类型）
        String name = "张三";
        int age = 25;
        double height = 1.75;
        boolean isStudent = true;

        // 输出
        System.out.println("姓名: " + name + ", 年龄: " + age);
        System.out.printf("姓名: %s, 年龄: %d%n", name, age);
    }
}
```

### 7.3 数据类型

| 类型 | 分类 | 大小 | 范围 |
|------|------|------|------|
| `byte` | 基本类型 | 1字节 | -128~127 |
| `short` | 基本类型 | 2字节 | -32768~32767 |
| `int` | 基本类型 | 4字节 | -21亿~21亿 |
| `long` | 基本类型 | 8字节 | -9e18~9e18 |
| `float` | 基本类型 | 4字节 | 单精度浮点数 |
| `double` | 基本类型 | 8字节 | 双精度浮点数 |
| `char` | 基本类型 | 2字节 | 单个字符 |
| `boolean` | 基本类型 | 1位 | true/false |
| `String` | 引用类型 | - | 字符串 |
| 数组/对象 | 引用类型 | - | 引用传递 |

### 7.4 数组

```java
// 声明和初始化
int[] nums = new int[5];
int[] nums = {1, 2, 3, 4, 5};
String[] names = {"张三", "李四", "王五"};

// 访问
System.out.println(nums[0]);
System.out.println(nums.length);

// 遍历
for (int i = 0; i < nums.length; i++) {
    System.out.println(nums[i]);
}

for (int num : nums) {  // 增强 for 循环
    System.out.println(num);
}
```

### 7.5 条件与循环

```java
// if-else
int score = 85;
if (score >= 90) {
    System.out.println("A");
} else if (score >= 80) {
    System.out.println("B");
} else {
    System.out.println("C");
}

// switch
int day = 1;
switch (day) {
    case 1:
        System.out.println("星期一");
        break;
    case 2:
        System.out.println("星期二");
        break;
    default:
        System.out.println("其他");
}

// for 循环
for (int i = 0; i < 5; i++) {
    System.out.println(i);
}

// while
int count = 0;
while (count < 5) {
    count++;
}

// do-while
do {
    count--;
} while (count > 0);
```

### 7.6 面向对象

```java
// 类定义
public class Person {
    // 成员变量
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

    // getter / setter
    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public int getAge() {
        return age;
    }
}

// 使用
Person p = new Person("张三", 25);
p.greet();
System.out.println(p.getName());
```

### 7.7 集合框架

```java
import java.util.*;

// ArrayList
List<String> list = new ArrayList<>();
list.add("apple");
list.add("banana");
list.get(0);
list.size();

// HashMap
Map<String, Integer> map = new HashMap<>();
map.put("张三", 25);
map.put("李四", 30);
map.get("张三");
map.containsKey("张三");

// 遍历
for (String item : list) {
    System.out.println(item);
}

for (Map.Entry<String, Integer> entry : map.entrySet()) {
    System.out.println(entry.getKey() + ": " + entry.getValue());
}
```

### 7.8 Java Web 核心技术

| 技术 | 说明 |
|------|------|
| **Servlet** | Java Web 的基础，处理 HTTP 请求 |
| **JSP** | Java Server Pages，在 HTML 中嵌入 Java 代码 |
| **JDBC** | Java 数据库连接 API |
| **Filter** | 过滤器，用于请求预处理 |
| **Listener** | 监听器，监听 Web 事件 |
| **Session / Cookie** | 会话管理 |
| **JSTL** | JSP 标准标签库 |
| **Spring MVC** | MVC 框架，企业级主流 |
| **Spring Boot** | 快速开发框架，约定优于配置 |
| **MyBatis / JPA** | 持久层框架（操作数据库） |

### 7.9 Servlet 示例

```java
// HelloServlet.java
import javax.servlet.*;
import javax.servlet.http.*;
import java.io.*;

public class HelloServlet extends HttpServlet {
    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        response.setContentType("text/html;charset=UTF-8");
        PrintWriter out = response.getWriter();

        String name = request.getParameter("name");
        if (name == null) name = "访客";

        out.println("<html><body>");
        out.println("<h1>你好，" + name + "！</h1>");
        out.println("</body></html>");
    }

    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        doGet(request, response);
    }
}
```

### 7.10 JDBC 示例

```java
import java.sql.*;

public class JdbcExample {
    public static void main(String[] args) {
        String url = "jdbc:mysql://localhost:3306/testdb?useSSL=false";
        String user = "root";
        String password = "123456";

        try {
            // 加载驱动
            Class.forName("com.mysql.cj.jdbc.Driver");

            // 建立连接
            Connection conn = DriverManager.getConnection(url, user, password);

            // 查询
            Statement stmt = conn.createStatement();
            ResultSet rs = stmt.executeQuery("SELECT id, name, age FROM users");

            while (rs.next()) {
                int id = rs.getInt("id");
                String name = rs.getString("name");
                int age = rs.getInt("age");
                System.out.println(id + ": " + name + ", " + age);
            }

            // 防止 SQL 注入：预处理
            String sql = "INSERT INTO users (name, age) VALUES (?, ?)";
            PreparedStatement pstmt = conn.prepareStatement(sql);
            pstmt.setString(1, "张三");
            pstmt.setInt(2, 25);
            pstmt.executeUpdate();

            rs.close();
            stmt.close();
            conn.close();

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

---

---

## 📋 内容审核与补充建议

> 针对「第七章：Java Web 基础」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

### ⚔️ 攻击技术
- ⚠️ 缺少attack相关内容

---

## 📌 拓展学习资源

### 推荐学习路径
- 理论基础 → 工具实践 → 实战演练 → 深度研究
- 建议搭建本地实验环境进行动手练习

### 相关工具与资源
- 在线实验平台：Hack The Box、TryHackMe、VulnHub
- 技术文档：官方文档、RFC、OWASP 指南
- 社区资源：GitHub、安全论坛、技术博客
