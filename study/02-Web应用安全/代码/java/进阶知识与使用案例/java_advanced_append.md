
---

## 四、高级实战案例

### 4.1 Java 反序列化漏洞利用

Java 反序列化漏洞原理与常见 Payload。

```java
import java.io.*;
import java.util.Base64;

// ===== Java 反序列化漏洞演示 =====

// 存在漏洞的类（实现了 Serializable）
class EvilObject implements Serializable {
    private String command;
    
    public EvilObject(String cmd) {
        this.command = cmd;
    }
    
    // readObject 在反序列化时自动调用
    private void readObject(ObjectInputStream in) throws IOException, ClassNotFoundException {
        in.defaultReadObject();
        // 漏洞点：反序列化时执行命令
        Runtime.getRuntime().exec(command);
    }
}

public class DeserializeDemo {
    
    // 序列化对象为字节数组
    public static byte[] serialize(Object obj) throws IOException {
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        ObjectOutputStream oos = new ObjectOutputStream(baos);
        oos.writeObject(obj);
        oos.close();
        return baos.toByteArray();
    }
    
    // 反序列化（漏洞点）
    public static Object deserialize(byte[] data) throws Exception {
        ByteArrayInputStream bais = new ByteArrayInputStream(data);
        ObjectInputStream ois = new ObjectInputStream(bais);
        return ois.readObject();  // 危险！不可信数据反序列化
    }
    
    public static void main(String[] args) throws Exception {
        // 正常使用
        EvilObject normal = new EvilObject("whoami");
        byte[] data = serialize(normal);
        System.out.println("序列化后长度: " + data.length);
        System.out.println("Base64: " + Base64.getEncoder().encodeToString(data));
        
        // 反序列化（会触发 readObject 中的命令执行）
        // deserialize(data);  // 取消注释会执行命令
    }
}

/*
===== Java 反序列化漏洞说明 =====

常见利用链（Gadget Chains）：

1. Commons Collections 系列
   - CommonsCollections1 (CC1)
   - CommonsCollections5 (CC5)
   - CommonsCollections6 (CC6)
   - CommonsCollections7 (CC7)
   - 依赖: commons-collections 3.x 或 4.x

2. 其他利用链
   - Jdk7u21 (JDK 7u21 原生)
   - Groovy
   - Spring
   - Hibernate
   - JBoss/Jackson/Fastjson

3. 工具
   - ysoserial: https://github.com/frohoff/ysoserial
     用法: java -jar ysoserial.jar CommonsCollections1 "calc.exe" > payload.ser
   
   - marshalsec: 多种反序列化利用工具
   
   - Java Serial Killer: Burp Suite 插件

4. 防护措施
   - 禁止反序列化不可信数据
   - 使用白名单类验证 (ObjectInputFilter)
   - 升级存在漏洞的第三方库
   - 使用安全的序列化格式 (JSON/Protobuf 等)
*/
```

### 4.2 JWT 攻击与安全

JWT 安全问题与攻击手段。

```java
import io.jsonwebtoken.*;
import io.jsonwebtoken.security.Keys;
import javax.crypto.SecretKey;
import java.util.Base64;
import java.util.Date;

public class JwtSecurityDemo {
    
    // 生成正常的 JWT
    public static String generateToken(String username, SecretKey key) {
        return Jwts.builder()
            .setSubject(username)
            .claim("role", "user")
            .setIssuedAt(new Date())
            .setExpiration(new Date(System.currentTimeMillis() + 3600000))
            .signWith(key)
            .compact();
    }
    
    // 验证 JWT
    public static Claims validateToken(String token, SecretKey key) {
        return Jwts.parserBuilder()
            .setSigningKey(key)
            .build()
            .parseClaimsJws(token)
            .getBody();
    }
    
    // ===== JWT 攻击方式 =====
    
    // 攻击1: None 算法攻击
    // 修改 header 中的 alg 为 none，服务器可能接受无签名的 token
    // {"alg": "none", "typ": "JWT"}.{"role": "admin"}.
    
    // 攻击2: 密钥爆破
    // 如果密钥太弱，可以暴力破解
    // 工具: jwt-cracker, hashcat, john
    
    // 攻击3: alg 混淆攻击（RS256 -> HS256）
    // 把非对称加密算法改成对称加密算法
    // 用公钥当密钥验证签名
    
    // 攻击4: KID 参数注入
    // kid (Key ID) 参数可控时可能导致任意文件读取或 SQL 注入
    // {"kid": "../../etc/passwd", "alg": "HS256"}
    
    // 攻击5: JKU/X5U 注入
    // jku/x5u 指向攻击者控制的密钥文件
    
    public static void main(String[] args) {
        // 安全密钥生成
        SecretKey key = Keys.secretKeyFor(SignatureAlgorithm.HS256);
        
        // 生成 Token
        String token = generateToken("user1", key);
        System.out.println("Token: " + token);
        
        // 验证
        try {
            Claims claims = validateToken(token, key);
            System.out.println("用户: " + claims.getSubject());
            System.out.println("角色: " + claims.get("role"));
        } catch (JwtException e) {
            System.out.println("Token 无效: " + e.getMessage());
        }
    }
}

/*
===== JWT 安全最佳实践 =====

1. 使用强密钥
   - HS256: 密钥至少 256 位随机
   - RS256/ES256: 使用非对称加密更安全

2. 验证算法
   - 代码中明确指定算法，不要信任 header 中的 alg
   - 禁止使用 none 算法

3. 有效期
   - 设置合理的过期时间
   - 使用 refresh token 机制
   - 实现 token 黑名单/撤销机制

4. 敏感信息
   - 不要在 payload 中放敏感信息（base64 不是加密）
   - 敏感数据使用加密

5. 传输安全
   - 始终使用 HTTPS 传输
   - 设置 HttpOnly / Secure / SameSite Cookie 属性
*/
```

### 4.3 Java 安全审计要点

常见 Java Web 漏洞类型与审计方法。

```java
import java.io.*;
import java.sql.*;
import javax.servlet.http.*;

// ===== 常见 Java Web 漏洞示例 =====

public class VulnerableExamples {
    
    // 1. SQL 注入
    public void sqliVulnerable(HttpServletRequest req) throws SQLException {
        String username = req.getParameter("username");
        String sql = "SELECT * FROM users WHERE username = '" + username + "'";
        Statement stmt = connection.createStatement();
        ResultSet rs = stmt.executeQuery(sql);  // 漏洞点！
    }
    
    // 安全写法：预编译
    public void sqliSafe(HttpServletRequest req) throws SQLException {
        String username = req.getParameter("username");
        String sql = "SELECT * FROM users WHERE username = ?";
        PreparedStatement pstmt = connection.prepareStatement(sql);
        pstmt.setString(1, username);
        ResultSet rs = pstmt.executeQuery();  // 安全
    }
    
    // 2. XSS
    public void xssVulnerable(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        String name = req.getParameter("name");
        resp.getWriter().write("<h1>Hello " + name + "</h1>");  // 漏洞点！
    }
    
    // 3. 命令注入
    public void cmdInjectionVulnerable(String ip) throws IOException {
        Runtime.getRuntime().exec("ping " + ip);  // 漏洞点！
    }
    
    // 4. 路径遍历
    public void pathTraversalVulnerable(String filename) throws IOException {
        File file = new File("/uploads/" + filename);  // 可能被 ../ 绕过
        FileInputStream fis = new FileInputStream(file);
    }
    
    // 5. 不安全的反序列化
    public Object deserializeVulnerable(byte[] data) throws Exception {
        ObjectInputStream ois = new ObjectInputStream(new ByteArrayInputStream(data));
        return ois.readObject();  // 漏洞点！
    }
    
    // 6. 文件上传漏洞
    public void uploadVulnerable(MultipartFile file) throws IOException {
        // 只检查后缀名，容易绕过
        String filename = file.getOriginalFilename();
        if (filename.endsWith(".jpg") || filename.endsWith(".png")) {
            file.transferTo(new File("/upload/" + filename));
        }
    }
    
    // 7. 认证绕过
    public boolean authBypassVulnerable(String token) {
        // 只检查 token 是否存在，不验证签名
        return token != null && !token.isEmpty();
    }
    
    // 8. 敏感信息泄露
    public void errorDisclosure(HttpServletResponse resp, Exception e) throws IOException {
        resp.getWriter().write("错误: " + e.getMessage());  // 泄露堆栈信息
        e.printStackTrace(resp.getWriter());
    }
}

/*
===== Java 代码审计要点 =====

危险函数/类:
- Runtime.exec() / ProcessBuilder — 命令注入
- ObjectInputStream.readObject() — 反序列化
- Statement.executeQuery() — SQL 注入（非预编译）
- new File() + 用户输入 — 路径遍历
- 直接输出用户输入 — XSS
- MessageDigest/弱加密 — 不安全的密码学
- Random() — 不安全随机数

框架常见漏洞:
- Struts2: OGNL 表达式注入
- Spring: SpEL 注入、路径穿越
- MyBatis: ${} 拼接导致 SQL 注入
- Fastjson/Jackson: 反序列化漏洞
- Shiro: 反序列化、认证绕过
- Dubbo: 反序列化

审计工具:
- FindSecBugs — Java 安全静态分析
- SonarQube — 代码质量与安全
- CodeQL — 代码查询语言
- 逆向: JD-GUI / Fernflower / CFR
*/
```

---

## 五、进阶学习资源

### 5.1 Java 安全资源

- **Oracle Java 安全指南**：https://docs.oracle.com/javase/8/docs/technotes/guides/security/
- **OWASP Java 安全**：https://cheatsheetseries.owasp.org/cheatsheets/Java_Security_Cheat_Sheet.html
- **Java 反序列化**：
  - ysoserial: https://github.com/frohoff/ysoserial — 反序列化 payload 生成
  - marshalsec: https://github.com/mbechler/marshalsec
  - Java 反序列化漏洞百科

### 5.2 框架安全

- **Spring Security**：https://spring.io/projects/spring-security — Spring 安全框架
- **Apache Shiro**：https://shiro.apache.org/ — Java 安全框架
- **Struts2 安全**：S2 系列漏洞分析
- **Fastjson 安全**：Fastjson 反序列化漏洞历史
- **Log4j 漏洞**：Log4Shell (CVE-2021-44228)

### 5.3 安全工具

- **静态代码分析**：
  - FindSecBugs: https://find-sec-bugs.github.io/
  - SonarQube: https://www.sonarqube.org/
  - SpotBugs + FindSecBugs 插件
  - CodeQL: https://codeql.github.com/

- **动态分析/调试**：
  - JD-GUI — Java 反编译
  - Bytecode Viewer — 字节码查看器
  - Java Decompiler (CFR, Procyon, Fernflower)
  - JDB — Java 调试器
  - Arthas — Alibaba Java 诊断工具

- **漏洞利用**：
  - ysoserial — 反序列化 Payload 生成
  - marshalsec — 多种反序列化利用
  - JNDI-Injection-Exploit — JNDI 注入利用
  - weblogic-scan — Weblogic 漏洞扫描

### 5.4 Web 安全深入

- **SQL 注入**：MyBatis ${} 注入、Hibernate HQL 注入
- **表达式注入**：OGNL (Struts2) / SpEL (Spring) / EL (JSP)
- **反序列化**：Fastjson / Jackson / Shiro / Dubbo
- **文件上传**：各框架上传漏洞
- **SSRF**：Java 各种 HTTP 客户端的 SSRF

### 5.5 CTF 与练习平台

- **Hack The Box**：https://www.hackthebox.com/
- **TryHackMe**：https://tryhackme.com/
- **picoCTF**：https://picoctf.org/
- **Bugku**：https://ctf.bugku.com/
- **攻防世界**：https://adworld.xctf.org.cn/
- **BUUCTF**：https://buuoj.cn/
- **WebGoat**：https://owasp.org/www-project-webgoat/ — OWASP 教学平台
- **Web Security Academy**：https://portswigger.net/web-security

### 5.6 推荐书籍

- **Java 安全**：
  - 《Java 安全编程》
  - 《Java 核心技术》
  - 《深入理解 Java 虚拟机》

- **Web 安全**：
  - 《白帽子讲 Web 安全》
  - 《Web 安全深度剖析》
  - 《代码审计实战》

- **Java 高级**：
  - 《Effective Java》
  - 《Java 并发编程实战》
  - 《深入理解 Java 虚拟机》

### 5.7 社区与博客

- **FreeBuf**：https://www.freebuf.com/
- **安全客**：https://www.anquanke.com/
- **先知社区**：https://xz.aliyun.com/
- **Seebug**：https://www.seebug.org/
- **CNVD**：https://www.cnvd.org.cn/ — 国家信息安全漏洞共享平台

### 5.8 进阶学习路线

**第 1 阶段：Java 深入（2-3月）**
- JVM 原理与字节码
- 反射、动态代理、类加载器
- Java 并发编程
- 常用框架源码阅读

**第 2 阶段：Web 安全基础（2-3月）**
- SQL 注入、XSS、CSRF
- 命令注入、文件上传
- SSRF、XXE

**第 3 阶段：Java 特色漏洞（3-4月）**
- 反序列化漏洞（CC/Fastjson/Shiro）
- 表达式注入（OGNL/SpEL/EL）
- JNDI 注入
- 各种框架历史漏洞

**第 4 阶段：代码审计（2-3月）**
- 危险函数定位
- 框架漏洞分析
- CMS 代码审计
- 审计工具使用

**第 5 阶段：实战与 CTF（持续）**
- 参加 Java 方向 CTF
- 研究最新 Java 漏洞
- 开发安全工具
- 挖掘真实漏洞
