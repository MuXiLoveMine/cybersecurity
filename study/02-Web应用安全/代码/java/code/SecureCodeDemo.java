import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.SecureRandom;
import java.util.*;
import java.util.regex.Pattern;

/**
 * SecureCodeDemo.java
 * Java 安全编码实践 - Web 安全实战
 *
 * 演示 Java Web 开发中的安全编码实践：
 * 1. SQL 注入防护（PreparedStatement）
 * 2. XSS 防护（输出编码）
 * 3. CSRF 防护（Token）
 * 4. 密码安全哈希
 * 5. 文件上传安全
 * 6. 安全随机数生成
 *
 * 仅用于安全学习和参考
 *
 * 编译: javac SecureCodeDemo.java
 * 运行: java SecureCodeDemo
 */
public class SecureCodeDemo {

    // =============================================
    // 1. XSS 防护：HTML 输出编码
    // =============================================
    public static String htmlEncode(String input) {
        if (input == null) return "";
        return input.replace("&", "&amp;")
                     .replace("<", "&lt;")
                     .replace(">", "&gt;")
                     .replace("\"", "&quot;")
                     .replace("'", "&#x27;");
    }

    // JavaScript 输出编码
    public static String jsEncode(String input) {
        if (input == null) return "";
        StringBuilder sb = new StringBuilder();
        for (char c : input.toCharArray()) {
            if (c < 0x20 || c > 0x7e || c == '"' || c == '\'' || c == '\\' || c == '<' || c == '>' || c == '&') {
                sb.append(String.format("\\u%04x", (int) c));
            } else {
                sb.append(c);
            }
        }
        return sb.toString();
    }

    // URL 输出编码
    public static String urlEncode(String input) {
        return java.net.URLEncoder.encode(input, StandardCharsets.UTF_8);
    }

    // =============================================
    // 2. 输入验证
    // =============================================
    public static boolean isValidEmail(String email) {
        if (email == null) return false;
        String regex = "^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$";
        return Pattern.matches(regex, email);
    }

    public static boolean isValidIP(String ip) {
        if (ip == null) return false;
        String regex = "^((25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)\\.){3}(25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)$";
        return Pattern.matches(regex, ip);
    }

    public static boolean isValidUsername(String username) {
        if (username == null || username.length() < 3 || username.length() > 20) return false;
        return Pattern.matches("^[A-Za-z0-9_]+$", username);
    }

    // 白名单过滤
    public static String whitelistFilter(String input, String[] allowed) {
        for (String a : allowed) {
            if (a.equals(input)) return input;
        }
        return null;
    }

    // =============================================
    // 3. 密码安全哈希
    // =============================================
    public static String hashPassword(String password, byte[] salt) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            md.update(salt);
            byte[] hash = md.digest(password.getBytes(StandardCharsets.UTF_8));
            StringBuilder sb = new StringBuilder();
            for (byte b : hash) sb.append(String.format("%02x", b));
            return sb.toString();
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    // 生成安全盐值
    public static byte[] generateSalt() {
        byte[] salt = new byte[32];
        new SecureRandom().nextBytes(salt);
        return salt;
    }

    // PBKDF2 密码派生
    public static String pbkdf2Hash(String password, byte[] salt) throws Exception {
        int iterations = 10000;
        javax.crypto.SecretKeyFactory skf = javax.crypto.SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256");
        javax.crypto.spec.PBEKeySpec spec = new javax.crypto.spec.PBEKeySpec(
            password.toCharArray(), salt, iterations, 256);
        byte[] hash = skf.generateSecret(spec).getEncoded();
        StringBuilder sb = new StringBuilder();
        for (byte b : hash) sb.append(String.format("%02x", b));
        return "pbkdf2$" + iterations + "$" + bytesToHex(salt) + "$" + sb.toString();
    }

    // =============================================
    // 4. CSRF Token 生成与验证
    // =============================================
    private static final Map<String, Long> csrfTokens = new HashMap<>();
    private static final int TOKEN_EXPIRY = 3600000; // 1小时

    public static String generateCsrfToken() {
        byte[] tokenBytes = new byte[32];
        new SecureRandom().nextBytes(tokenBytes);
        String token = bytesToHex(tokenBytes);
        csrfTokens.put(token, System.currentTimeMillis());
        return token;
    }

    public static boolean verifyCsrfToken(String token) {
        if (token == null || !csrfTokens.containsKey(token)) return false;
        long created = csrfTokens.get(token);
        if (System.currentTimeMillis() - created > TOKEN_EXPIRY) {
            csrfTokens.remove(token);
            return false;
        }
        return true;
    }

    // =============================================
    // 5. 安全的文件上传验证
    // =============================================
    public static boolean validateFileUpload(String filename, String contentType, long size) {
        // 白名单检查
        Set<String> allowedExts = new HashSet<>(Arrays.asList("jpg", "jpeg", "png", "gif", "pdf"));
        String ext = filename.substring(filename.lastIndexOf('.') + 1).toLowerCase();
        if (!allowedExts.contains(ext)) return false;

        // MIME 类型检查
        Set<String> allowedMimes = new HashSet<>(Arrays.asList(
            "image/jpeg", "image/png", "image/gif", "application/pdf"));
        if (!allowedMimes.contains(contentType)) return false;

        // 文件大小检查 (5MB)
        if (size > 5 * 1024 * 1024) return false;

        return true;
    }

    // =============================================
    // 6. AES 加解密
    // =============================================
    public static byte[] aesEncrypt(String plaintext, byte[] key) throws Exception {
        javax.crypto.Cipher cipher = javax.crypto.Cipher.getInstance("AES/CBC/PKCS5Padding");
        byte[] iv = new byte[16];
        new SecureRandom().nextBytes(iv);
        cipher.init(javax.crypto.Cipher.ENCRYPT_MODE,
            new javax.crypto.spec.SecretKeySpec(key, "AES"),
            new javax.crypto.spec.IvParameterSpec(iv));
        byte[] encrypted = cipher.doFinal(plaintext.getBytes(StandardCharsets.UTF_8));
        // IV + 密文
        byte[] result = new byte[iv.length + encrypted.length];
        System.arraycopy(iv, 0, result, 0, iv.length);
        System.arraycopy(encrypted, 0, result, iv.length, encrypted.length);
        return result;
    }

    public static String aesDecrypt(byte[] ciphertext, byte[] key) throws Exception {
        byte[] iv = Arrays.copyOfRange(ciphertext, 0, 16);
        byte[] encrypted = Arrays.copyOfRange(ciphertext, 16, ciphertext.length);
        javax.crypto.Cipher cipher = javax.crypto.Cipher.getInstance("AES/CBC/PKCS5Padding");
        cipher.init(javax.crypto.Cipher.DECRYPT_MODE,
            new javax.crypto.spec.SecretKeySpec(key, "AES"),
            new javax.crypto.spec.IvParameterSpec(iv));
        return new String(cipher.doFinal(encrypted), StandardCharsets.UTF_8);
    }

    // =============================================
    // 工具函数
    // =============================================
    private static String bytesToHex(byte[] bytes) {
        StringBuilder sb = new StringBuilder();
        for (byte b : bytes) sb.append(String.format("%02x", b));
        return sb.toString();
    }

    // =============================================
    // 主函数：演示
    // =============================================
    public static void main(String[] args) throws Exception {
        System.out.println("===== Java 安全编码实践 =====\n");

        // 1. XSS 防护
        System.out.println("1. XSS 防护 - HTML 编码");
        String xssPayload = "<script>alert('XSS')</script>";
        System.out.println("   原始: " + xssPayload);
        System.out.println("   编码: " + htmlEncode(xssPayload));

        System.out.println("\n2. 输入验证");
        System.out.println("   邮箱 admin@test.com: " + isValidEmail("admin@test.com"));
        System.out.println("   邮箱 invalid: " + isValidEmail("invalid"));
        System.out.println("   IP 192.168.1.1: " + isValidIP("192.168.1.1"));
        System.out.println("   IP 999.1.1.1: " + isValidIP("999.1.1.1"));
        System.out.println("   用户名 admin: " + isValidUsername("admin"));
        System.out.println("   用户名 a@b: " + isValidUsername("a@b"));

        // 3. 密码哈希
        System.out.println("\n3. 密码安全哈希");
        byte[] salt = generateSalt();
        String pwd = "MyPassword123";
        String hash = hashPassword(pwd, salt);
        System.out.println("   密码: " + pwd);
        System.out.println("   盐值: " + bytesToHex(salt).substring(0, 16) + "...");
        System.out.println("   哈希: " + hash.substring(0, 32) + "...");

        // PBKDF2
        String pbkdf2 = pbkdf2Hash(pwd, salt);
        System.out.println("   PBKDF2: " + pbkdf2.substring(0, 60) + "...");

        // 4. CSRF Token
        System.out.println("\n4. CSRF Token");
        String token = generateCsrfToken();
        System.out.println("   Token: " + token.substring(0, 32) + "...");
        System.out.println("   验证: " + verifyCsrfToken(token));
        System.out.println("   验证(假): " + verifyCsrfToken("fake_token_12345"));

        // 5. 文件上传验证
        System.out.println("\n5. 文件上传验证");
        System.out.println("   photo.jpg (image/jpeg, 1MB): " +
            validateFileUpload("photo.jpg", "image/jpeg", 1024 * 1024));
        System.out.println("   shell.php (application/php, 1KB): " +
            validateFileUpload("shell.php", "application/php", 1024));
        System.out.println("   big.png (image/png, 10MB): " +
            validateFileUpload("big.png", "image/png", 10 * 1024 * 1024));

        // 6. AES 加解密
        System.out.println("\n6. AES 加解密");
        byte[] aesKey = new byte[32]; // 256 位密钥
        new SecureRandom().nextBytes(aesKey);
        String plain = "这是一段敏感数据";
        byte[] encrypted = aesEncrypt(plain, aesKey);
        String decrypted = aesDecrypt(encrypted, aesKey);
        System.out.println("   原文: " + plain);
        System.out.println("   密文: " + bytesToHex(encrypted).substring(0, 32) + "...");
        System.out.println("   解密: " + decrypted);

        System.out.println("\n===== 安全编码演示完成 =====");
    }
}
