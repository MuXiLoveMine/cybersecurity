import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.stream.*;

/**
 * Basics.java —— Java 基础语法示例（安全从业者视角）
 *
 * 涵盖内容：
 *   1. 变量与数据类型
 *   2. 运算符与比较
 *   3. 流程控制
 *   4. 类与对象
 *   5. 集合框架
 *   6. 异常处理
 *   7. 文件 I/O
 *
 * 编译运行：
 *   javac Basics.java
 *   java Basics
 *
 * 注意：本脚本用于学习参考，包含安全视角的注释说明。
 */
public class Basics {

    // ============================================================
    // 辅助方法
    // ============================================================

    private static void printSection(String title) {
        System.out.println();
        System.out.println("============================================================");
        System.out.println("  " + title);
        System.out.println("============================================================");
        System.out.println();
    }

    private static void printSubsection(String title) {
        System.out.println();
        System.out.println("  --- " + title + " ---");
        System.out.println();
    }

    private static void printSafe(String msg) {
        System.out.println("  ✅ " + msg);
    }

    private static void printWarn(String msg) {
        System.out.println("  ⚠️  " + msg);
    }

    // ============================================================
    // 1. 变量与数据类型
    // ============================================================

    private static void demoDataTypes() {
        printSection("【1. 变量与数据类型】");

        printSubsection("1.1 8 种基本数据类型");

        // 整数类型
        byte b = 127;                    // 1 字节  -128 ~ 127
        short s = 32767;                 // 2 字节  -32768 ~ 32767
        int i = 2147483647;              // 4 字节  -2^31 ~ 2^31-1
        long l = 9223372036854775807L;   // 8 字节

        // 浮点类型
        float f = 3.14f;                 // 4 字节
        double d = 3.1415926535;         // 8 字节

        // 字符类型
        char c = 'A';                    // 2 字节 (Unicode)

        // 布尔类型
        boolean bool = true;             // true / false

        System.out.println("  byte:    " + b + " (1 字节)");
        System.out.println("  short:   " + s + " (2 字节)");
        System.out.println("  int:     " + i + " (4 字节)");
        System.out.println("  long:    " + l + "L (8 字节)");
        System.out.println("  float:   " + f + "f (4 字节)");
        System.out.println("  double:  " + d + " (8 字节)");
        System.out.println("  char:    '" + c + "' (2 字节, Unicode)");
        System.out.println("  boolean: " + bool);

        printSubsection("1.2 包装类与自动装箱/拆箱");

        // 每个基本类型都有对应的包装类
        Integer intObj = 42;       // 自动装箱 (autoboxing)
        int intVal = intObj;       // 自动拆箱 (unboxing)

        System.out.println("  Integer 对象: " + intObj);
        System.out.println("  拆箱为 int: " + intVal);
        System.out.println("  Integer.MAX_VALUE = " + Integer.MAX_VALUE);
        System.out.println("  Integer.MIN_VALUE = " + Integer.MIN_VALUE);

        System.out.println();
        printWarn("Integer 缓存陷阱：-128 ~ 127 的 Integer 会被缓存");
        Integer a1 = 100;
        Integer a2 = 100;
        Integer b1 = 200;
        Integer b2 = 200;
        System.out.println("    Integer 100 == 100: " + (a1 == a2) + " (同一对象)");
        System.out.println("    Integer 200 == 200: " + (b1 == b2) + " (不同对象!)");
        System.out.println("    💡 比较包装类用 equals()，不要用 == ");

        printSubsection("1.3 字符串");

        String str1 = "Hello";          // 字符串字面量（字符串池）
        String str2 = new String("Hello"); // 新对象
        String str3 = "Hello";          // 复用池中对象

        System.out.println("  str1 = " + str1);
        System.out.println("  str2 = " + str2);
        System.out.println("  str3 = " + str3);
        System.out.println();
        System.out.println("  str1 == str2: " + (str1 == str2) + " (引用不同)");
        System.out.println("  str1 == str3: " + (str1 == str3) + " (都来自字符串池)");
        System.out.println("  str1.equals(str2): " + str1.equals(str2) + " (内容相同)");
        System.out.println();
        printSafe("字符串比较永远用 equals()，不要用 == ");
        System.out.println("     == 比较的是引用地址，equals() 比较的是内容");

        // 常用字符串方法
        System.out.println();
        System.out.println("  常用字符串方法:");
        String s2 = "  Hello, Java!  ";
        System.out.println("    原始: '" + s2 + "'");
        System.out.println("    length(): " + s2.length());
        System.out.println("    charAt(0): '" + s2.charAt(0) + "'");
        System.out.println("    substring(0, 5): '" + s2.substring(0, 5) + "'");
        System.out.println("    contains('Java'): " + s2.contains("Java"));
        System.out.println("    indexOf('J'): " + s2.indexOf('J'));
        System.out.println("    toLowerCase(): '" + s2.toLowerCase() + "'");
        System.out.println("    toUpperCase(): '" + s2.toUpperCase() + "'");
        System.out.println("    trim(): '" + s2.trim() + "'");
        System.out.println("    replace('Java', 'World'): '" + s2.replace("Java", "World") + "'");

        printSubsection("1.4 常量");

        final int MAX_SIZE = 100;
        final double PI = 3.14159;
        System.out.println("  MAX_SIZE = " + MAX_SIZE);
        System.out.println("  PI = " + PI);
        System.out.println("  (final 修饰的变量不可修改)");
    }

    // ============================================================
    // 2. 运算符与比较
    // ============================================================

    private static void demoOperators() {
        printSection("【2. 运算符与比较】");

        printSubsection("2.1 算术运算符");

        int a = 17, b = 5;
        System.out.println("  a = " + a + ", b = " + b);
        System.out.println("  a + b = " + (a + b));
        System.out.println("  a - b = " + (a - b));
        System.out.println("  a * b = " + (a * b));
        System.out.println("  a / b = " + (a / b) + " (整数除法，截断小数)");
        System.out.println("  a % b = " + (a % b) + " (取余/取模)");
        System.out.println("  (double)a / b = " + ((double)a / b) + " (浮点除法)");

        printSubsection("2.2 比较运算符");

        int x = 10, y = 20;
        System.out.println("  x = " + x + ", y = " + y);
        System.out.println("  x == y: " + (x == y));
        System.out.println("  x != y: " + (x != y));
        System.out.println("  x > y:  " + (x > y));
        System.out.println("  x < y:  " + (x < y));
        System.out.println("  x >= y: " + (x >= y));
        System.out.println("  x <= y: " + (x <= y));

        System.out.println();
        printWarn("== vs equals() 的区别（重要！）");
        System.out.println("    == 比较基本类型：比较值");
        System.out.println("    == 比较对象：比较引用地址（是否同一个对象）");
        System.out.println("    equals()：比较对象内容（需要正确重写）");

        printSubsection("2.3 逻辑运算符");

        boolean p = true, q = false;
        System.out.println("  p = " + p + ", q = " + q);
        System.out.println("  p && q: " + (p && q) + " (短路与)");
        System.out.println("  p || q: " + (p || q) + " (短路或)");
        System.out.println("  !p: " + !p + " (非)");
        System.out.println("  p & q: " + (p & q) + " (非短路与)");
        System.out.println("  p | q: " + (p | q) + " (非短路或)");

        System.out.println();
        System.out.println("  💡 短路运算符（&&、||）：");
        System.out.println("     左边已经能确定结果时，右边不会执行");
        System.out.println("     常用于空指针检查：if (str != null && str.length() > 0)");

        printSubsection("2.4 位运算符");

        int m = 60;   // 0011 1100
        int n = 13;   // 0000 1101
        System.out.println("  m = " + m + " (二进制: " + Integer.toBinaryString(m) + ")");
        System.out.println("  n = " + n + " (二进制: " + Integer.toBinaryString(n) + ")");
        System.out.println("  m & n = " + (m & n) + " (按位与)");
        System.out.println("  m | n = " + (m | n) + " (按位或)");
        System.out.println("  m ^ n = " + (m ^ n) + " (按位异或)");
        System.out.println("  ~m = " + (~m) + " (按位取反)");
        System.out.println("  m << 2 = " + (m << 2) + " (左移 2 位)");
        System.out.println("  m >> 2 = " + (m >> 2) + " (右移 2 位，算术)");
        System.out.println("  m >>> 2 = " + (m >>> 2) + " (右移 2 位，逻辑)");
    }

    // ============================================================
    // 3. 流程控制
    // ============================================================

    private static void demoControlFlow() {
        printSection("【3. 流程控制】");

        printSubsection("3.1 if-else");

        int score = 85;
        System.out.println("  分数: " + score);
        System.out.print("  等级: ");
        if (score >= 90) {
            System.out.println("优秀");
        } else if (score >= 80) {
            System.out.println("良好");
        } else if (score >= 60) {
            System.out.println("及格");
        } else {
            System.out.println("不及格");
        }

        // 三元运算符
        String result = score >= 60 ? "及格" : "不及格";
        System.out.println("  三元运算结果: " + result);

        printSubsection("3.2 switch");

        String day = "Wednesday";
        System.out.println("  今天是: " + day);
        System.out.print("  switch 结果: ");

        switch (day) {
            case "Monday":
                System.out.println("星期一");
                break;
            case "Tuesday":
                System.out.println("星期二");
                break;
            case "Wednesday":
                System.out.println("星期三");
                break;
            case "Friday":
                System.out.println("星期五");
                break;
            default:
                System.out.println("其他");
        }

        System.out.println();
        printWarn("不要忘记 break！没有 break 会继续执行后面的 case（穿透）");

        printSubsection("3.3 循环");

        System.out.print("  for 循环 (1-5): ");
        for (int i = 1; i <= 5; i++) {
            System.out.print(i + " ");
        }
        System.out.println();

        // 增强 for 循环（遍历数组/集合）
        int[] nums = {10, 20, 30, 40, 50};
        System.out.print("  增强 for 遍历数组: ");
        for (int n : nums) {
            System.out.print(n + " ");
        }
        System.out.println();

        System.out.print("  while 循环 (5-1): ");
        int w = 5;
        while (w >= 1) {
            System.out.print(w + " ");
            w--;
        }
        System.out.println();

        // for-each 遍历字符串
        String text = "Hello";
        System.out.print("  遍历字符串: ");
        for (char ch : text.toCharArray()) {
            System.out.print(ch + " ");
        }
        System.out.println();
    }

    // ============================================================
    // 4. 类与对象
    // ============================================================

    // 一个简单的用户类
    static class User {
        // 私有字段（封装）
        private String username;
        private String email;
        private int age;

        // 构造方法
        public User(String username, String email, int age) {
            this.username = username;
            this.email = email;
            this.age = age;
        }

        // Getter 和 Setter
        public String getUsername() {
            return username;
        }

        public void setUsername(String username) {
            this.username = username;
        }

        public String getEmail() {
            return email;
        }

        public void setEmail(String email) {
            this.email = email;
        }

        public int getAge() {
            return age;
        }

        public void setAge(int age) {
            this.age = age;
        }

        // 成员方法
        public boolean isAdult() {
            return age >= 18;
        }

        // 重写 toString()
        @Override
        public String toString() {
            return "User{username='" + username + "', email='" + email + "', age=" + age + "}";
        }
    }

    // 继承：管理员类继承自用户类
    static class Admin extends User {
        private int level;

        public Admin(String username, String email, int age, int level) {
            super(username, email, age);  // 调用父类构造方法
            this.level = level;
        }

        public int getLevel() {
            return level;
        }

        // 方法重写
        @Override
        public boolean isAdult() {
            return super.isAdult() && level >= 1;
        }

        public void doAdminTask() {
            System.out.println("    管理员 " + getUsername() + " 执行管理任务");
        }
    }

    // 接口
    interface Printable {
        void printInfo();

        default void printHeader() {  // 默认方法（Java 8+）
            System.out.println("    ===== 信息 =====");
        }
    }

    // 实现接口
    static class Product implements Printable {
        private String name;
        private double price;

        public Product(String name, double price) {
            this.name = name;
            this.price = price;
        }

        @Override
        public void printInfo() {
            printHeader();
            System.out.println("    产品: " + name);
            System.out.println("    价格: ¥" + price);
        }
    }

    private static void demoClassesAndObjects() {
        printSection("【4. 类与对象】");

        printSubsection("4.1 类与对象基础");

        User user = new User("alice", "alice@example.com", 25);
        System.out.println("  创建用户: " + user);
        System.out.println("  用户名: " + user.getUsername());
        System.out.println("  邮箱: " + user.getEmail());
        System.out.println("  年龄: " + user.getAge());
        System.out.println("  是否成年: " + user.isAdult());

        printSubsection("4.2 封装与访问控制");

        System.out.println("  访问修饰符:");
        System.out.println("    public    - 公开，任何地方都能访问");
        System.out.println("    protected - 受保护，同包和子类可访问");
        System.out.println("    (default) - 默认，同包可访问");
        System.out.println("    private   - 私有，只有本类能访问");
        System.out.println();
        printSafe("字段应该用 private，通过 public 的 getter/setter 访问");
        System.out.println("     这样可以控制访问逻辑，进行输入验证");

        printSubsection("4.3 继承与多态");

        Admin admin = new Admin("admin", "admin@example.com", 30, 2);
        System.out.println("  管理员: " + admin);
        System.out.println("  管理员等级: " + admin.getLevel());
        admin.doAdminTask();

        // 多态：父类引用指向子类对象
        User userRef = new Admin("bob", "bob@example.com", 28, 1);
        System.out.println();
        System.out.println("  多态演示 (User 引用 Admin 对象):");
        System.out.println("    isAdult() = " + userRef.isAdult() + " (调用 Admin 的实现)");
        // userRef.doAdminTask();  // 编译错误，User 类型没有这个方法

        printSubsection("4.4 接口");

        Product product = new Product("MacBook Pro", 14999.99);
        product.printInfo();
    }

    // ============================================================
    // 5. 集合框架
    // ============================================================

    private static void demoCollections() {
        printSection("【5. 集合框架】");

        printSubsection("5.1 List - 有序，可重复");

        List<String> list = new ArrayList<>();
        list.add("apple");
        list.add("banana");
        list.add("orange");
        list.add("apple");  // 可以重复

        System.out.println("  ArrayList: " + list);
        System.out.println("  大小: " + list.size());
        System.out.println("  第一个元素: " + list.get(0));
        System.out.println("  包含 'banana': " + list.contains("banana"));
        System.out.println("  'apple' 的索引: " + list.indexOf("apple"));

        System.out.println();
        System.out.print("  增强 for 遍历: ");
        for (String fruit : list) {
            System.out.print(fruit + " ");
        }
        System.out.println();

        printSubsection("5.2 Set - 无序，不可重复");

        Set<String> set = new HashSet<>();
        set.add("a");
        set.add("b");
        set.add("c");
        set.add("a");  // 重复，不会被添加

        System.out.println("  HashSet: " + set);
        System.out.println("  大小: " + set.size());
        System.out.println("  包含 'b': " + set.contains("b"));

        printSubsection("5.3 Map - 键值对");

        Map<String, Integer> map = new HashMap<>();
        map.put("Alice", 25);
        map.put("Bob", 30);
        map.put("Charlie", 35);
        map.put("Alice", 26);  // 覆盖已有键

        System.out.println("  HashMap: " + map);
        System.out.println("  大小: " + map.size());
        System.out.println("  Alice 的年龄: " + map.get("Alice"));
        System.out.println("  包含键 'Bob': " + map.containsKey("Bob"));
        System.out.println("  包含值 30: " + map.containsValue(30));

        System.out.println();
        System.out.println("  遍历 entrySet:");
        for (Map.Entry<String, Integer> entry : map.entrySet()) {
            System.out.println("    " + entry.getKey() + " -> " + entry.getValue());
        }

        printSubsection("5.4 Stream API (Java 8+)");

        List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);
        System.out.println("  原始列表: " + numbers);

        List<Integer> evensDoubled = numbers.stream()
            .filter(n -> n % 2 == 0)       // 过滤偶数
            .map(n -> n * 2)                // 每个乘 2
            .sorted(Comparator.reverseOrder()) // 降序
            .collect(Collectors.toList());  // 收集为 List

        System.out.println("  偶数翻倍后降序: " + evensDoubled);

        // 其他常用操作
        long count = numbers.stream().filter(n -> n > 5).count();
        int sum = numbers.stream().mapToInt(Integer::intValue).sum();
        Optional<Integer> max = numbers.stream().max(Integer::compareTo);

        System.out.println("  大于 5 的数量: " + count);
        System.out.println("  总和: " + sum);
        System.out.println("  最大值: " + max.orElse(0));

        printSubsection("5.5 集合安全注意");

        printWarn("ArrayList、HashMap 等不是线程安全的");
        System.out.println("    多线程环境下使用：");
        System.out.println("    - Collections.synchronizedList(new ArrayList<>())");
        System.out.println("    - CopyOnWriteArrayList (读多写少)");
        System.out.println("    - ConcurrentHashMap");
        System.out.println();

        // 线程安全的 Map
        Map<String, String> concurrentMap = new java.util.concurrent.ConcurrentHashMap<>();
        concurrentMap.put("key1", "value1");
        System.out.println("  ConcurrentHashMap: " + concurrentMap);
        printSafe("并发环境使用 ConcurrentHashMap");
    }

    // ============================================================
    // 6. 异常处理
    // ============================================================

    // 自定义异常
    static class SecurityValidationException extends RuntimeException {
        public SecurityValidationException(String message) {
            super(message);
        }
    }

    private static void demoExceptions() {
        printSection("【6. 异常处理】");

        printSubsection("6.1 异常体系");

        System.out.println("  Throwable");
        System.out.println("  ├── Error（严重错误，一般无法处理）");
        System.out.println("  │   ├── OutOfMemoryError");
        System.out.println("  │   └── StackOverflowError");
        System.out.println("  └── Exception");
        System.out.println("      ├── RuntimeException（非受检，可不用声明）");
        System.out.println("      │   ├── NullPointerException");
        System.out.println("      │   ├── IllegalArgumentException");
        System.out.println("      │   └── IndexOutOfBoundsException");
        System.out.println("      └── 受检异常（必须声明或捕获）");
        System.out.println("          ├── IOException");
        System.out.println("          └── SQLException");

        printSubsection("6.2 try-catch-finally");

        try {
            int result = 10 / 0;  // 会抛出 ArithmeticException
            System.out.println("  这行不会执行");
        } catch (ArithmeticException e) {
            System.out.println("  捕获到算术异常: " + e.getMessage());
        } catch (Exception e) {
            System.out.println("  捕获到其他异常: " + e.getMessage());
        } finally {
            System.out.println("  finally 块：无论是否异常都会执行");
            System.out.println("  通常用于释放资源（关闭文件、连接等）");
        }

        printSubsection("6.3 try-with-resources (推荐)");

        System.out.println("  try-with-resources 自动关闭实现 AutoCloseable 的资源");
        System.out.println("  语法：try (资源声明) { ... } catch (...) { ... }");
        System.out.println("  比手动在 finally 中关闭更安全");
        System.out.println();

        // 示例：使用 try-with-resources 读取文件
        String testFile = "java_basics_test.txt";
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(testFile))) {
            writer.write("Hello, Java!");
            writer.newLine();
            writer.write("这是测试文件");
            printSafe("文件写入成功");
        } catch (IOException e) {
            System.out.println("  写入文件出错: " + e.getMessage());
        }

        try (BufferedReader reader = new BufferedReader(new FileReader(testFile))) {
            String line;
            System.out.println("  文件内容:");
            while ((line = reader.readLine()) != null) {
                System.out.println("    " + line);
            }
        } catch (IOException e) {
            System.out.println("  读取文件出错: " + e.getMessage());
        }

        // 清理测试文件
        try {
            Files.deleteIfExists(Paths.get(testFile));
        } catch (IOException e) {
            // 忽略
        }

        printSubsection("6.4 抛出异常");

        System.out.println("  使用 throw 抛出异常");
        System.out.println("  使用 throws 声明方法可能抛出的受检异常");
        System.out.println();

        try {
            validateAge(-5);
        } catch (SecurityValidationException e) {
            System.out.println("  捕获到自定义异常: " + e.getMessage());
        }

        printSubsection("6.5 异常处理安全要点");

        printWarn("不要在异常信息中泄露敏感信息");
        System.out.println("    生产环境不要输出 e.printStackTrace()");
        System.out.println("    不要把堆栈跟踪返回给用户");
        System.out.println();
        printWarn("不要吞异常（catch 块空着什么都不做）");
        System.out.println("    至少要记录日志");
        System.out.println();
        printWarn("不要捕获 Throwable 或 Exception 然后忽略");
        System.out.println("    捕获具体的异常类型");
    }

    private static void validateAge(int age) {
        if (age < 0 || age > 150) {
            throw new SecurityValidationException("无效的年龄: " + age);
        }
    }

    // ============================================================
    // 7. 文件 I/O
    // ============================================================

    private static void demoFileIO() {
        printSection("【7. 文件 I/O】");

        String testFile = "java_basics_io_test.txt";
        String testDir = "java_basics_test_dir";

        printSubsection("7.1 写入文件");

        // 方式 1：Files.write (NIO.2, 最简单)
        try {
            String content = "Hello, Java NIO.2!\n第二行\n第三行: 12345\n";
            Files.write(Paths.get(testFile), content.getBytes());
            printSafe("使用 Files.write 写入成功");
        } catch (IOException e) {
            System.out.println("  写入失败: " + e.getMessage());
        }

        // 方式 2：BufferedWriter
        try (BufferedWriter bw = new BufferedWriter(new FileWriter(testFile, true))) {
            bw.write("追加的一行");
            bw.newLine();
            printSafe("使用 BufferedWriter 追加成功");
        } catch (IOException e) {
            System.out.println("  追加失败: " + e.getMessage());
        }

        printSubsection("7.2 读取文件");

        // 方式 1：Files.readAllLines
        try {
            List<String> lines = Files.readAllLines(Paths.get(testFile));
            System.out.println("  Files.readAllLines 读取 (" + lines.size() + " 行):");
            for (int i = 0; i < lines.size(); i++) {
                System.out.println("    " + (i + 1) + ": " + lines.get(i));
            }
        } catch (IOException e) {
            System.out.println("  读取失败: " + e.getMessage());
        }

        System.out.println();

        // 方式 2：BufferedReader
        try (BufferedReader br = new BufferedReader(new FileReader(testFile))) {
            System.out.println("  BufferedReader 逐行读取:");
            String line;
            int lineNum = 0;
            while ((line = br.readLine()) != null) {
                lineNum++;
                System.out.println("    " + lineNum + ": " + line);
            }
        } catch (IOException e) {
            System.out.println("  读取失败: " + e.getMessage());
        }

        printSubsection("7.3 文件属性检查");

        Path path = Paths.get(testFile);
        System.out.println("  文件路径: " + path.toAbsolutePath());
        System.out.println("  存在: " + Files.exists(path));
        System.out.println("  是普通文件: " + Files.isRegularFile(path));
        System.out.println("  是目录: " + Files.isDirectory(path));
        System.out.println("  可读: " + Files.isReadable(path));
        System.out.println("  可写: " + Files.isWritable(path));
        try {
            System.out.println("  大小: " + Files.size(path) + " 字节");
            System.out.println("  最后修改: " + Files.getLastModifiedTime(path));
        } catch (IOException e) {
            System.out.println("  获取属性失败: " + e.getMessage());
        }

        printSubsection("7.4 目录操作");

        try {
            Path dirPath = Paths.get(testDir);
            Files.createDirectories(dirPath);
            System.out.println("  创建目录: " + dirPath.toAbsolutePath());

            // 列出目录内容
            System.out.println("  当前目录内容 (前 10 个):");
            try (DirectoryStream<Path> stream = Files.newDirectoryStream(Paths.get("."))) {
                int count = 0;
                for (Path p : stream) {
                    if (count >= 10) {
                        System.out.println("    ... 还有更多");
                        break;
                    }
                    String type = Files.isDirectory(p) ? "[DIR]" : "[FILE]";
                    System.out.println("    " + type + " " + p.getFileName());
                    count++;
                }
            }

            // 删除测试目录
            Files.deleteIfExists(dirPath);

        } catch (IOException e) {
            System.out.println("  目录操作失败: " + e.getMessage());
        }

        // 清理测试文件
        try {
            Files.deleteIfExists(Paths.get(testFile));
            System.out.println();
            printSafe("已清理测试文件");
        } catch (IOException e) {
            // 忽略
        }

        printSubsection("7.5 安全注意");

        printWarn("文件路径如果用户可控，可能导致路径遍历漏洞");
        System.out.println("    攻击者输入 ../../../etc/passwd 可以访问系统文件");
        System.out.println("    防御：验证路径、规范化路径、白名单校验");
        System.out.println();
        printWarn("文件上传是高危操作，必须严格校验");
        System.out.println("    扩展名白名单、MIME 校验、文件内容检查、随机文件名");
    }

    // ============================================================
    // 主方法
    // ============================================================

    public static void main(String[] args) {
        System.out.println();
        System.out.println("============================================================");
        System.out.println("  Java 基础语法示例（安全从业者视角）");
        System.out.println("  Java Basics for Security Practitioners");
        System.out.println("============================================================");
        System.out.println();
        System.out.println("  Java 版本: " + System.getProperty("java.version"));
        System.out.println("  操作系统: " + System.getProperty("os.name"));

        // 1. 变量与数据类型
        demoDataTypes();

        // 2. 运算符与比较
        demoOperators();

        // 3. 流程控制
        demoControlFlow();

        // 4. 类与对象
        demoClassesAndObjects();

        // 5. 集合框架
        demoCollections();

        // 6. 异常处理
        demoExceptions();

        // 7. 文件 I/O
        demoFileIO();

        System.out.println();
        System.out.println("============================================================");
        System.out.println("  所有示例执行完毕");
        System.out.println("  涵盖：数据类型、运算符、流程控制、类与对象、");
        System.out.println("  集合框架、异常处理、文件 I/O");
        System.out.println("============================================================");
        System.out.println();
    }
}
