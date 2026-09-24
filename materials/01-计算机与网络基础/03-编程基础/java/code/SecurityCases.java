import java.io.*;
import java.security.*;
import java.security.spec.*;
import java.util.*;
import java.util.regex.*;
import javax.crypto.*;
import javax.crypto.spec.*;

/**
 * SecurityCases.java —— Java 安全案例集
 *
 * 涵盖内容（均从原理理解和防御角度）：
 *   案例 1：反序列化漏洞演示与防御
 *   案例 2：SQL 注入防御（Statement vs PreparedStatement）
 *   案例 3：输入验证安全（白名单验证、正则验证）
 *   案例 4：安全编码实践（XSS 转义、密码哈希、安全随机数）
 *   案例 5：安全编码检查清单
 *
 * 编译运行：
 *   javac SecurityCases.java
 *   java SecurityCases [案例编号]
 *
 * 重要提示：
 *   - 本文件仅用于安全学习和防御研究
 *   - 所有漏洞演示用于理解原理，不提供利用代码
 *   - 请在授权测试环境中运行
 *   - 重点关注每个案例的"修复方案"和"安全编码实践"
 */
public class SecurityCases {

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

    private static void printDanger(String msg) {
        System.out.println("  🔴 " + msg);
    }

    /**
     * HTML 转义（防止 XSS）
     */
    private static String htmlEscape(String input) {
        if (input == null) return null;
        StringBuilder sb = new StringBuilder();
        for (char c : input.toCharArray()) {
            switch (c) {
                case '<': sb.append("&lt;"); break;
                case '>': sb.append("&gt;"); break;
                case '"': sb.append("&quot;"); break;
                case '\'': sb.append("&#39;"); break;
                case '&': sb.append("&amp;"); break;
                case '/': sb.append("&#47;"); break;
                default: sb.append(c);
            }
        }
        return sb.toString();
    }

    /**
     * 字节数组转十六进制字符串
     */
    private static String bytesToHex(byte[] bytes) {
        StringBuilder sb = new StringBuilder();
        for (byte b : bytes) {
            sb.append(String.format("%02X", b));
        }
        return sb.toString();
    }

    // ============================================================
    // 案例 1：反序列化漏洞演示与防御
    // ============================================================

    // 一个普通的用户类，实现 Serializable
    static class UserData implements Serializable {
        private static final long serialVersionUID = 1L;
        private String username;
        private String email;
        private int age;

        public UserData(String username, String email, int age) {
            this.username = username;
            this.email = email;
            this.age = age;
        }

        public String getUsername() { return username; }
        public String getEmail() { return email; }
        public int getAge() { return age; }

        @Override
        public String toString() {
            return "UserData{username='" + username + "', email='" + email + "', age=" + age + "}";
        }
    }

    /**
     * 安全的 ObjectInputStream：白名单类过滤
     * 只允许反序列化指定的类
     */
    static class SafeObjectInputStream extends ObjectInputStream {
        private static final Set<String> ALLOWED_CLASSES = new HashSet<>(Arrays.asList(
            "java.lang.String",
            "java.lang.Integer",
            "java.lang.Long",
            "java.util.ArrayList",
            "java.util.HashMap",
            "SecurityCases$UserData"  // 只允许我们自己的 UserData 类
        ));

        public SafeObjectInputStream(InputStream in) throws IOException {
            super(in);
        }

        @Override
        protected Class<?> resolveClass(ObjectStreamClass desc)
                throws IOException, ClassNotFoundException {
            String className = desc.getName();
            if (!ALLOWED_CLASSES.contains(className)) {
                throw new SecurityException(
                    "[安全拦截] 不允许反序列化类: " + className
                );
            }
            return super.resolveClass(desc);
        }
    }

    // 序列化工具方法
    private static byte[] serialize(Object obj) throws IOException {
        try (ByteArrayOutputStream baos = new ByteArrayOutputStream();
             ObjectOutputStream oos = new ObjectOutputStream(baos)) {
            oos.writeObject(obj);
            return baos.toByteArray();
        }
    }

    // 危险反序列化（无防护）
    private static Object unsafeDeserialize(byte[] data)
            throws IOException, ClassNotFoundException {
        try (ObjectInputStream ois = new ObjectInputStream(
                new ByteArrayInputStream(data))) {
            return ois.readObject();
        }
    }

    // 安全反序列化（白名单过滤）
    private static Object safeDeserialize(byte[] data)
            throws IOException, ClassNotFoundException {
        try (SafeObjectInputStream sois = new SafeObjectInputStream(
                new ByteArrayInputStream(data))) {
            return sois.readObject();
        }
    }

    private static void caseDeserialization() {
        printSection("【案例 1：反序列化漏洞演示与防御】");

        System.out.println("  Java 反序列化漏洞：当应用反序列化用户可控的数据时，");
        System.out.println("  攻击者可以构造恶意序列化数据，利用已有的 Gadget 类，");
        System.out.println("  通过 readObject() 等方法调用链实现远程代码执行（RCE）。");
        System.out.println("  这是 Java 安全中最经典也是最复杂的漏洞类型之一。");

        printSubsection("1.1 序列化基础演示");

        try {
            UserData user = new UserData("alice", "alice@example.com", 25);
            byte[] serialized = serialize(user);

            System.out.println("  原始对象: " + user);
            System.out.println("  序列化后字节数: " + serialized.length + " 字节");
            System.out.println("  十六进制 (前 64 字节): " +
                bytesToHex(
                    Arrays.copyOfRange(serialized, 0, Math.min(64, serialized.length))
                )
            );

            // 正常反序列化
            UserData restored = (UserData) unsafeDeserialize(serialized);
            System.out.println("  反序列化后: " + restored);
            printSafe("正常的序列化/反序列化工作正常");

        } catch (Exception e) {
            System.out.println("  错误: " + e.getMessage());
        }

        printSubsection("1.2 反序列化漏洞原理");

        System.out.println("  漏洞成因：");
        System.out.println("    1. 应用使用 ObjectInputStream.readObject() 反序列化");
        System.out.println("    2. 反序列化的数据来自不可信源（用户输入、网络等）");
        System.out.println("    3. 攻击者构造恶意的序列化字节流");
        System.out.println("    4. 反序列化时自动调用对象的 readObject() 等方法");
        System.out.println("    5. 通过 Gadget 链（利用链）调用危险方法");
        System.out.println("    6. 最终导致任意代码执行");
        System.out.println();

        System.out.println("  常见利用链（Gadget Chain）：");
        System.out.println("    - Apache Commons Collections (CC1 ~ CC10)");
        System.out.println("    - JDK 原生链 (Jdk7u21, Jdk8u20)");
        System.out.println("    - Fastjson / Jackson 反序列化");
        System.out.println("    - XStream 反序列化");
        System.out.println("    - Log4j2 JNDI 注入（Log4Shell）");

        printDanger("反序列化漏洞危害等级：极高（通常直接 RCE）");

        printSubsection("1.3 防御方案 1：白名单类过滤");

        System.out.println("  原理：自定义 ObjectInputStream，重写 resolveClass() 方法，");
        System.out.println("        只允许反序列化白名单中的类。");
        System.out.println();

        try {
            UserData user = new UserData("bob", "bob@example.com", 30);
            byte[] data = serialize(user);

            // 用安全的方式反序列化我们自己的类（应该成功）
            System.out.println("  测试 1：反序列化白名单中的 UserData 类");
            Object result = safeDeserialize(data);
            System.out.println("    结果: " + result);
            printSafe("白名单类反序列化成功");

        } catch (SecurityException e) {
            System.out.println("    安全拦截: " + e.getMessage());
        } catch (Exception e) {
            System.out.println("    错误: " + e.getMessage());
        }

        System.out.println();
        System.out.println("  测试 2：如果攻击者构造了恶意类（如 Runtime 等）");
        System.out.println("    SafeObjectInputStream 会在 resolveClass 阶段拦截");
        System.out.println("    不允许白名单之外的类被反序列化");
        System.out.println();
        printSafe("白名单过滤能有效阻止绝大多数反序列化利用链");

        printSubsection("1.4 防御方案 2：使用 JSON 替代（最佳实践）");

        System.out.println("  最佳实践：完全避免 Java 原生序列化，");
        System.out.println("        使用 JSON、XML、Protobuf 等数据格式替代。");
        System.out.println();

        System.out.println("  JSON 相比 Java 序列化的优势：");
        System.out.println("    1. 纯数据格式，不会执行代码");
        System.out.println("    2. 人类可读，易于调试");
        System.out.println("    3. 跨语言支持好");
        System.out.println("    4. 没有 Gadget 链的问题");
        System.out.println();

        System.out.println("  示例（使用 Jackson/Gson）：");
        System.out.println("    // 序列化");
        System.out.println("    String json = objectMapper.writeValueAsString(user);");
        System.out.println("    // 反序列化");
        System.out.println("    User u = objectMapper.readValue(json, User.class);");
        System.out.println();

        printSafe("优先使用 JSON 等纯数据格式，避免 Java 原生序列化");

        printSubsection("1.5 防御方案 3：JVM 全局过滤（Java 9+）");

        System.out.println("  Java 9+ 内置了序列化过滤机制：");
        System.out.println();
        System.out.println("    启动参数配置：");
        System.out.println("    -Djdk.serialFilter=com.example.*;!*");
        System.out.println("    含义：只允许 com.example 包下的类，其他全部拒绝");
        System.out.println();
        System.out.println("    也可以通过代码设置：");
        System.out.println("    ObjectInputFilter.Config.setSerialFilter(filter);");
        System.out.println();

        printSafe("多层防御：白名单类 + JSON 替代 + JVM 全局过滤");

        printSubsection("1.6 代码审计要点");

        System.out.println("  审计 Java 反序列化漏洞时，查找以下关键方法：");
        System.out.println("    - ObjectInputStream.readObject()");
        System.out.println("    - ObjectInputStream.readUnshared()");
        System.out.println("    - XMLDecoder.readObject()");
        System.out.println("    - XStream.fromXML() / fromJSON()");
        System.out.println("    - ObjectMapper.readValue() (Jackson 多态)");
        System.out.println("    - JSON.parseObject() (Fastjson autoType)");
        System.out.println("    - Yaml.load() (SnakeYAML)");
        System.out.println();
        System.out.println("  追踪这些方法的数据源：");
        System.out.println("    - 如果数据来自用户可控的输入 → 高危！");
        System.out.println("    - 如果数据来自内部服务、签名保护 → 风险较低");
    }

    // ============================================================
    // 案例 2：SQL 注入防御
    // ============================================================

    private static void caseSqlInjection() {
        printSection("【案例 2：SQL 注入防御】");

        System.out.println("  SQL 注入是最经典的 Web 安全漏洞之一。");
        System.out.println("  当用户输入被直接拼接到 SQL 语句中时，攻击者可以");
        System.out.println("  构造恶意输入修改 SQL 逻辑，从而读取、修改、删除数据。");

        printSubsection("2.1 危险写法（仅演示，绝对不要这么写！）");

        // 模拟用户输入
        String username = "admin";
        String password = "123456";

        System.out.println("  正常登录场景:");
        System.out.println("    用户名: " + username);
        System.out.println("    密码: " + password);
        System.out.println();

        // ⚠️ 危险：字符串拼接 SQL
        String sql = "SELECT * FROM users WHERE username = '" + username
                   + "' AND password = '" + password + "'";
        System.out.println("  生成的 SQL: " + sql);
        System.out.println("  (正常情况下，查询匹配用户记录)");

        System.out.println();
        System.out.println("  攻击场景（经典的 ' OR '1'='1 绕过）:");

        // 攻击者构造的输入
        String hackerUsername = "' OR '1'='1";
        String hackerPassword = "' OR '1'='1";

        String sqlInjected = "SELECT * FROM users WHERE username = '" + hackerUsername
                           + "' AND password = '" + hackerPassword + "'";
        System.out.println("    攻击者输入的用户名: " + htmlEscape(hackerUsername));
        System.out.println("    生成的 SQL: " + sqlInjected);
        System.out.println("    结果：WHERE 条件永远为真，返回所有用户 → 登录绕过！");

        System.out.println();
        printDanger("SQL 注入的危害：数据泄露、数据篡改、权限绕过、拖库、甚至获取服务器权限");

        printSubsection("2.2 安全写法：PreparedStatement 参数化查询");

        System.out.println("  参数化查询（PreparedStatement）是防御 SQL 注入的最佳方法。");
        System.out.println("  SQL 结构和数据分离，用户输入永远作为数据处理，");
        System.out.println("  不会被当成语句的一部分执行。");
        System.out.println();

        System.out.println("  代码示例:");
        System.out.println();
        System.out.println("    // 1. 加载驱动，建立连接");
        System.out.println("    Connection conn = DriverManager.getConnection(url, user, pass);");
        System.out.println();
        System.out.println("    // 2. 预处理 SQL（用 ? 作为占位符）");
        System.out.println("    String sql = \"SELECT * FROM users WHERE username = ? AND password = ?\";");
        System.out.println("    PreparedStatement pstmt = conn.prepareStatement(sql);");
        System.out.println();
        System.out.println("    // 3. 设置参数（下标从 1 开始）");
        System.out.println("    pstmt.setString(1, username);");
        System.out.println("    pstmt.setString(2, password);");
        System.out.println();
        System.out.println("    // 4. 执行查询");
        System.out.println("    ResultSet rs = pstmt.executeQuery();");
        System.out.println("    if (rs.next()) { /* 登录成功 */ }");
        System.out.println();

        printSafe("参数化查询下，攻击者输入只会被当作用户名/密码的值处理");
        System.out.println("     不会改变 SQL 结构，因此无法注入");

        printSubsection("2.3 其他正确做法");

        System.out.println("  1. 使用 ORM 框架（MyBatis、JPA/Hibernate）");
        System.out.println("     - MyBatis 使用 #{} 是参数化（安全）");
        System.out.println("     - MyBatis 使用 ${} 是字符串替换（危险！）");
        System.out.println("     - JPA / Hibernate 同样使用参数化查询");
        System.out.println();

        System.out.println("  2. 存储过程（注意：存储过程内部也不能拼接 SQL）");
        System.out.println();

        System.out.println("  3. 白名单验证（用于表名、列名、排序字段等");
        System.out.println("     不能用参数化的地方）");
        System.out.println("     示例：排序字段只能是 'id', 'name', 'date' 之一");

        printSubsection("2.4 MyBatis 安全注意");

        System.out.println("  MyBatis 中两种占位符的区别：");
        System.out.println();
        System.out.println("    #{}  →  参数化查询，预编译，安全 ✅");
        System.out.println("    ${}  →  字符串替换，直接拼接，危险 ❌");
        System.out.println();

        System.out.println("  安全示例（使用 #{}）:");
        System.out.println("    <select id=\"getUserById\" resultType=\"User\">");
        System.out.println("        SELECT * FROM users WHERE id = #{id}");
        System.out.println("    </select>");
        System.out.println();

        System.out.println("  危险示例（使用 ${}，SQL 注入）:");
        System.out.println("    <select id=\"getUserByName\" resultType=\"User\">");
        System.out.println("        SELECT * FROM users WHERE name = '${name}'");
        System.out.println("    </select>");

        System.out.println();
        printWarn("MyBatis 代码审计时重点搜索 $ {（中间可能有空格）}");
        System.out.println("     特别是在 WHERE 条件、LIKE、ORDER BY 等位置");

        printSubsection("2.5 SQL 注入防御总结");

        System.out.println("  防御层级（从主要到辅助）：");
        System.out.println();
        System.out.println("    1. ✅ 参数化查询（PreparedStatement / #{}）");
        System.out.println("    2. ✅ 输入验证（类型、长度、格式、白名单）");
        System.out.println("    3. ✅ 最小权限原则（数据库账号权限）");
        System.out.println("    4. ✅ 错误信息处理（不向用户暴露详细错误）");
        System.out.println("    5. ✅ WAF（Web 应用防火墙，纵深防御）");
        System.out.println("    6. ✅ 定期备份 + 审计日志");
    }

    // ============================================================
    // 案例 3：输入验证安全
    // ============================================================

    private static boolean validateUsername(String username) {
        if (username == null || username.isEmpty()) return false;
        // 白名单：只允许字母、数字、下划线，3-20 位
        Pattern pattern = Pattern.compile("^[a-zA-Z0-9_]{3,20}$");
        return pattern.matcher(username).matches();
    }

    private static boolean validateEmail(String email) {
        if (email == null || email.isEmpty()) return false;
        if (email.length() > 254) return false;
        // 简单的邮箱格式验证（实际项目建议用成熟的验证库）
        Pattern pattern = Pattern.compile(
            "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
        );
        return pattern.matcher(email).matches();
    }

    private static boolean validateAge(int age) {
        return age >= 0 && age <= 150;
    }

    private static boolean validatePhone(String phone) {
        if (phone == null || phone.isEmpty()) return false;
        // 中国大陆手机号：1 开头，第二位 3-9，共 11 位
        Pattern pattern = Pattern.compile("^1[3-9]\\d{9}$");
        return pattern.matcher(phone).matches();
    }

    // 防止路径遍历的安全文件名检查
    private static boolean isSafeFilename(String filename) {
        if (filename == null || filename.isEmpty()) return false;
        // 禁止路径遍历字符
        if (filename.contains("..") ||
            filename.contains("/") ||
            filename.contains("\\") ||
            filename.contains("\0")) {
            return false;
        }
        // 白名单：只允许字母、数字、下划线、点、中划线
        Pattern pattern = Pattern.compile("^[a-zA-Z0-9_.\\-]+$");
        return pattern.matcher(filename).matches();
    }

    private static void caseInputValidation() {
        printSection("【案例 3：输入验证安全】");

        System.out.println("  输入验证是所有 Web 应用安全的第一道防线。");
        System.out.println("  永远不要信任来自客户端的任何输入。");
        System.out.println("  验证原则：白名单优于黑名单。");

        printSubsection("3.1 白名单 vs 黑名单");

        System.out.println("  白名单验证（推荐）：只允许符合规则的输入通过");
        System.out.println("  黑名单验证（不推荐）：只禁止已知的危险输入");
        System.out.println();
        System.out.println("  为什么白名单更好：");
        System.out.println("    - 黑名单可能遗漏（攻击者总能想到你没考虑到的）");
        System.out.println("    - 业务变化时白名单更容易维护");
        System.out.println("    - 白名单更符合最小权限原则");

        printSubsection("3.2 常见输入验证示例");

        // 用户名验证
        String[] testUsernames = {
            "alice_123",     // 有效
            "admin",         // 有效
            "a",             // 太短
            "this_is_a_very_long_username_12345", // 太长
            "alice;drop table", // 包含特殊字符
            "<script>",      // XSS 尝试
            ""               // 空
        };

        System.out.println("  用户名验证 (字母数字下划线，3-20位):");
        for (String u : testUsernames) {
            boolean valid = validateUsername(u);
            String status = valid ? "✅ 有效" : "❌ 无效";
            System.out.println("    '" + htmlEscape(u) + "' → " + status);
        }

        System.out.println();

        // 邮箱验证
        String[] testEmails = {
            "user@example.com",
            "user.name+tag@domain.co.uk",
            "invalid-email",
            "@example.com",
            "user@",
            ""
        };

        System.out.println("  邮箱验证:");
        for (String e : testEmails) {
            boolean valid = validateEmail(e);
            String status = valid ? "✅ 有效" : "❌ 无效";
            System.out.println("    '" + e + "' → " + status);
        }

        System.out.println();

        // 手机号验证
        String[] testPhones = {
            "13812345678",
            "19912345678",
            "12345678901",   // 第二位不对
            "1381234567",    // 长度不够
            "138123456789",  // 太长
            ""
        };

        System.out.println("  手机号验证 (中国大陆 11 位):");
        for (String p : testPhones) {
            boolean valid = validatePhone(p);
            String status = valid ? "✅ 有效" : "❌ 无效";
            System.out.println("    '" + p + "' → " + status);
        }

        printSubsection("3.3 路径遍历防护");

        System.out.println("  路径遍历（Path Traversal）：攻击者通过 ../ 等方式");
        System.out.println("  访问到 Web 根目录之外的文件。");
        System.out.println();

        String[] testFilenames = {
            "avatar.jpg",
            "report_2024.pdf",
            "../etc/passwd",
            "..\\..\\windows\\system32",
            "file name with spaces.jpg",
            "shell.php",
            "file;rm -rf /"
        };

        System.out.println("  安全文件名检查:");
        for (String f : testFilenames) {
            boolean safe = isSafeFilename(f);
            String status = safe ? "✅ 安全" : "❌ 危险";
            System.out.println("    '" + htmlEscape(f) + "' → " + status);
        }

        System.out.println();
        System.out.println("  更严格的路径遍历防护：");
        System.out.println("    1. 规范化路径（Path.normalize()）");
        System.out.println("    2. 检查规范化后的路径是否在允许的目录内");
        System.out.println("    3. 使用 getCanonicalPath() 获取真实路径");
        System.out.println("    4. 白名单校验扩展名");
        System.out.println("    5. 随机生成文件名（不使用用户提供的文件名）");

        printSubsection("3.4 输入验证最佳实践");

        System.out.println("  1. 所有外部输入都要验证");
        System.out.println("     - URL 参数、表单数据、Cookie、HTTP Header");
        System.out.println("     - 文件上传、JSON/XML 请求体");
        System.out.println("     - 第三方 API 返回结果");
        System.out.println();

        System.out.println("  2. 使用白名单，而非黑名单");
        System.out.println();

        System.out.println("  3. 验证内容：类型、长度、范围、格式、语义");
        System.out.println();

        System.out.println("  4. 使用成熟的验证框架");
        System.out.println("     - Jakarta Bean Validation (JSR 380)");
        System.out.println("     - Hibernate Validator");
        System.out.println("     - Spring Validation");
        System.out.println();

        System.out.println("  5. 验证失败时拒绝请求，不尝试修复");
        System.out.println("     （不要自作主张去除'危险字符'，可能被绕过）");
        System.out.println();

        System.out.println("  6. 服务端验证是必须的，客户端验证只是辅助");
        System.out.println("     （前端验证可以被轻易绕过）");

        printSafe("输入验证是安全的第一道防线，也是最重要的防线之一");
    }

    // ============================================================
    // 案例 4：安全编码实践
    // ============================================================

    private static void caseSecureCoding() {
        printSection("【案例 4：安全编码实践】");

        System.out.println("  日常 Java 开发中的安全编码最佳实践。");

        printSubsection("4.1 XSS 防护：输出编码");

        String userInput = "<script>alert('XSS')</script>";
        System.out.println("  用户输入: " + htmlEscape(userInput));
        System.out.println();

        System.out.println("  ❌ 直接输出（危险）:");
        System.out.println("    输出: " + userInput);
        System.out.println("    浏览器会执行这段脚本！");
        System.out.println();

        System.out.println("  ✅ HTML 转义后输出（安全）:");
        System.out.println("    输出: " + htmlEscape(userInput));
        System.out.println("    特殊字符被转义为 HTML 实体，浏览器不会执行");
        System.out.println();

        System.out.println("  不同上下文的编码方式：");
        System.out.println("    HTML 内容/属性 → HTML 转义 (htmlEscape)");
        System.out.println("    JavaScript 代码 → JSON 序列化");
        System.out.println("    URL 参数 → URLEncoder.encode");
        System.out.println("    CSS → CSS 编码");
        System.out.println();

        printSafe("Java 推荐使用:");
        System.out.println("     - Spring: HtmlUtils.htmlEscape()");
        System.out.println("     - Apache Commons: StringEscapeUtils.escapeHtml()");
        System.out.println("     - 模板引擎自动转义 (Thymeleaf 默认开启)");

        printSubsection("4.2 密码安全存储");

        System.out.println("  密码绝对不能明文存储，也不能用 MD5/SHA1 等快速哈希。");
        System.out.println("  应该使用专门的密码哈希算法：bcrypt、Argon2、PBKDF2 等。");
        System.out.println();

        String password = "MySecurePass123!";
        System.out.println("  原文密码: " + password);
        System.out.println();

        try {
            // 使用 Java 自带的 PBKDF2 算法
            String hash1 = hashPasswordPBKDF2(password, "salt1234567890".getBytes());
            String hash2 = hashPasswordPBKDF2(password, "salt1234567890".getBytes());
            String hash3 = hashPasswordPBKDF2(password + "wrong", "salt1234567890".getBytes());

            System.out.println("  PBKDF2 哈希 (相同密码 + 相同 salt):");
            System.out.println("    hash1 = " + hash1);
            System.out.println("    hash2 = " + hash2);
            System.out.println("    相同密码 + 相同 salt → 相同结果: " + hash1.equals(hash2));
            System.out.println();

            System.out.println("  错误密码的哈希:");
            System.out.println("    hash3 = " + hash3);
            System.out.println("    密码错误 → 结果不同: " + !hash1.equals(hash3));
            System.out.println();

        } catch (Exception e) {
            System.out.println("  哈希出错: " + e.getMessage());
        }

        System.out.println("  推荐的密码哈希算法：");
        System.out.println("    1. Argon2 (最新，OWASP 推荐)");
        System.out.println("    2. bcrypt (最常用，简单可靠)");
        System.out.println("    3. PBKDF2 (Java 自带，NIST 推荐)");
        System.out.println();

        System.out.println("  Spring Security 中使用 BCrypt:");
        System.out.println("    BCryptPasswordEncoder encoder = new BCryptPasswordEncoder();");
        System.out.println("    String hash = encoder.encode(password);");
        System.out.println("    boolean matches = encoder.matches(password, hash);");
        System.out.println();

        printWarn("绝对不要使用 MD5、SHA1、SHA-256 等快速哈希存储密码");
        System.out.println("     这些算法太快，容易被暴力破解/彩虹表攻击");
        System.out.println("     密码哈希必须是慢哈希算法");

        printSubsection("4.3 安全随机数");

        System.out.println("  安全敏感场景（Token、密钥、验证码）");
        System.out.println("  必须使用密码学安全的随机数生成器。");
        System.out.println();

        System.out.println("  ❌ 不安全的随机数：");
        System.out.println("    new Random().nextInt()  // 可预测，基于时间种子");
        System.out.println("    Math.random()          // 同样不安全");
        System.out.println();

        System.out.println("  ✅ 安全的随机数：");
        System.out.println("    SecureRandom.getInstanceStrong().nextInt()");
        System.out.println();

        try {
            SecureRandom secureRandom = SecureRandom.getInstanceStrong();

            System.out.println("  SecureRandom 生成的随机数:");
            System.out.println("    随机整数: " + secureRandom.nextInt(1000000));
            System.out.println("    随机长整数: " + secureRandom.nextLong());

            // 生成安全的随机 Token
            byte[] tokenBytes = new byte[32];
            secureRandom.nextBytes(tokenBytes);
            String token = Base64.getUrlEncoder().withoutPadding().encodeToString(tokenBytes);
            System.out.println("    随机 Token (32字节): " + token);

        } catch (NoSuchAlgorithmException e) {
            System.out.println("  生成安全随机数失败: " + e.getMessage());
        }

        System.out.println();
        printSafe("安全敏感场景（Session ID、CSRF Token、密码重置 Token）");
        System.out.println("     必须使用 SecureRandom");

        printSubsection("4.4 敏感信息保护");

        System.out.println("  敏感信息保护要点：");
        System.out.println();
        System.out.println("  1. 日志中不记录敏感信息");
        System.out.println("     ❌ log.info(\"用户密码: \" + password);");
        System.out.println("     ✅ 日志中脱敏或不记录");
        System.out.println();
        System.out.println("  2. 异常信息不泄露细节");
        System.out.println("     ❌ 把堆栈跟踪返回给用户");
        System.out.println("     ✅ 返回通用错误信息，详细错误记录在服务端日志");
        System.out.println();
        System.out.println("  3. 内存中的敏感数据用完即清理");
        System.out.println("     用 char[] 存密码，用完后填充 0");
        System.out.println("     （String 不可变，可能留在内存中）");
        System.out.println();
        System.out.println("  4. 配置文件中的敏感信息加密");
        System.out.println("     数据库密码、API Key 等不要明文存储");
        System.out.println("     使用 Jasypt 等加密配置");

        printSubsection("4.5 并发安全");

        System.out.println("  并发安全问题可能导致数据不一致和安全漏洞：");
        System.out.println();
        System.out.println("  1. 竞态条件（Race Condition）");
        System.out.println("     典型场景：扣减库存、转账、用户注册");
        System.out.println("     防御：synchronized、Lock、原子类、数据库锁");
        System.out.println();
        System.out.println("  2. 线程安全的集合");
        System.out.println("     ❌ HashMap、ArrayList 不是线程安全的");
        System.out.println("     ✅ ConcurrentHashMap、CopyOnWriteArrayList");
        System.out.println();
        System.out.println("  3. SimpleDateFormat 线程不安全");
        System.out.println("     ❌ 把 SimpleDateFormat 当静态变量");
        System.out.println("     ✅ 使用 DateTimeFormatter（Java 8+，线程安全）");
        System.out.println("     ✅ 每次使用新建 SimpleDateFormat");
    }

    // PBKDF2 密码哈希
    private static String hashPasswordPBKDF2(String password, byte[] salt)
            throws NoSuchAlgorithmException, InvalidKeySpecException {
        int iterations = 10000;
        int keyLength = 256;
        SecretKeyFactory skf = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256");
        PBEKeySpec spec = new PBEKeySpec(password.toCharArray(), salt, iterations, keyLength);
        byte[] hash = skf.generateSecret(spec).getEncoded();
        return bytesToHex(hash);
    }

    // ============================================================
    // 案例 5：安全编码检查清单
    // ============================================================

    private static void printSecurityChecklist() {
        printSection("【附：Java 安全编码检查清单】");

        System.out.println("  输入验证:");
        System.out.println("    [ ] 所有外部输入都验证（参数、Header、Cookie、文件）");
        System.out.println("    [ ] 使用白名单验证，而非黑名单");
        System.out.println("    [ ] 验证数据类型、长度、范围、格式");
        System.out.println("    [ ] 使用 Bean Validation (JSR-380)");
        System.out.println("    [ ] 验证失败时拒绝请求");
        System.out.println();

        System.out.println("  数据库安全:");
        System.out.println("    [ ] 所有查询使用 PreparedStatement 参数化查询");
        System.out.println("    [ ] MyBatis 使用 #{}，不使用 ${}");
        System.out.println("    [ ] 数据库账号最小权限");
        System.out.println("    [ ] 生产环境不显示详细数据库错误");
        System.out.println("    [ ] 密码使用 bcrypt/argon2 存储");
        System.out.println();

        System.out.println("  输出安全:");
        System.out.println("    [ ] HTML 输出进行转义");
        System.out.println("    [ ] JavaScript 输出使用 JSON 序列化");
        System.out.println("    [ ] 设置 Content-Security-Policy 头");
        System.out.println("    [ ] 设置 X-Content-Type-Options: nosniff");
        System.out.println();

        System.out.println("  反序列化安全:");
        System.out.println("    [ ] 避免使用 Java 原生序列化");
        System.out.println("    [ ] 优先使用 JSON 等纯数据格式");
        System.out.println("    [ ] 必须使用时实现白名单类过滤");
        System.out.println("    [ ] 配置全局序列化过滤器");
        System.out.println("    [ ] 审计 readObject() 调用的数据源");
        System.out.println();

        System.out.println("  认证与授权:");
        System.out.println("    [ ] 使用成熟的安全框架（Spring Security）");
        System.out.println("    [ ] 密码使用强哈希算法");
        System.out.println("    [ ] Session Cookie 设置 HttpOnly、Secure、SameSite");
        System.out.println("    [ ] 接口级别的权限校验");
        System.out.println("    [ ] 防止水平越权和垂直越权");
        System.out.println();

        System.out.println("  文件操作:");
        System.out.println("    [ ] 上传文件白名单校验扩展名");
        System.out.println("    [ ] 校验文件内容（MIME + 文件头）");
        System.out.println("    [ ] 随机生成文件名");
        System.out.println("    [ ] 防止路径遍历");
        System.out.println("    [ ] 上传目录禁止执行脚本");
        System.out.println();

        System.out.println("  依赖安全:");
        System.out.println("    [ ] 定期更新依赖版本");
        System.out.println("    [ ] 使用 OWASP Dependency-Check / Snyk 扫描");
        System.out.println("    [ ] 移除未使用的依赖");
        System.out.println("    [ ] 关注第三方组件安全公告");
        System.out.println();

        System.out.println("  日志与错误:");
        System.out.println("    [ ] 不记录敏感信息（密码、身份证等）");
        System.out.println("    [ ] 生产环境不向用户显示堆栈跟踪");
        System.out.println("    [ ] 使用参数化日志（log.info(\"User: {}\", user)）");
        System.out.println("    [ ] 安全事件有专门的审计日志");
        System.out.println();

        System.out.println("  代码质量工具:");
        System.out.println("    [ ] SpotBugs + Find Security Bugs");
        System.out.println("    [ ] SonarQube 代码质量检测");
        System.out.println("    [ ] Semgrep 安全规则扫描");
        System.out.println("    [ ] OWASP Dependency-Check 依赖扫描");
    }

    // ============================================================
    // 主方法
    // ============================================================

    public static void main(String[] args) {
        System.out.println();
        System.out.println("============================================================");
        System.out.println("  Java 安全案例集");
        System.out.println("  Java Security Cases");
        System.out.println("============================================================");
        System.out.println();
        System.out.println("  本程序从防御角度演示常见 Java 安全漏洞的");
        System.out.println("  原理与防护方法。所有案例均用于学习研究，");
        System.out.println("  请在授权环境中使用。");

        // 获取案例编号
        int caseNum = 0;
        if (args.length > 0) {
            try {
                caseNum = Integer.parseInt(args[0]);
            } catch (NumberFormatException e) {
                caseNum = 0;
            }
        }

        switch (caseNum) {
            case 0:
                // 运行所有案例
                caseDeserialization();
                caseSqlInjection();
                caseInputValidation();
                caseSecureCoding();
                printSecurityChecklist();
                break;
            case 1:
                caseDeserialization();
                break;
            case 2:
                caseSqlInjection();
                break;
            case 3:
                caseInputValidation();
                break;
            case 4:
                caseSecureCoding();
                break;
            case 5:
                printSecurityChecklist();
                break;
            default:
                System.out.println();
                System.out.println("  用法: java SecurityCases [案例编号]");
                System.out.println();
                System.out.println("  案例:");
                System.out.println("    1 = 反序列化漏洞防御");
                System.out.println("    2 = SQL 注入防御");
                System.out.println("    3 = 输入验证安全");
                System.out.println("    4 = 安全编码实践");
                System.out.println("    5 = 安全编码检查清单");
                System.out.println("    0 或不指定 = 全部运行");
                return;
        }

        System.out.println();
        System.out.println("============================================================");
        System.out.println("  演示完成。记住：理解漏洞原理是为了更好地防御。");
        System.out.println("  请遵守法律法规，仅在授权环境中进行安全测试。");
        System.out.println("============================================================");
        System.out.println();
    }
}
