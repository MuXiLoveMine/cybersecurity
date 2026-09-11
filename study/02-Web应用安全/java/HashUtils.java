import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.util.Base64;
import java.nio.charset.StandardCharsets;

/**
 * ==============================================================================
 *   哈希与加密工具 - HashUtils.java
 * ==============================================================================
 *   功能说明：
 *     本程序提供多种哈希和加密功能，用于安全学习和研究：
 *     1. MD5 摘要计算
 *     2. SHA1 摘要计算
 *     3. SHA256 摘要计算
 *     4. SHA512 摘要计算
 *     5. Base64 编解码
 *     6. 加盐哈希（密码存储推荐方式）
 *     7. 哈希验证（验证密码是否匹配）
 *
 *   使用方法：
 *     java HashUtils <功能> <参数...>
 *
 *   示例：
 *     // MD5 哈希
 *     java HashUtils md5 "hello world"
 *
 *     // SHA256 哈希
 *     java HashUtils sha256 "hello world"
 *
 *     // Base64 编码
 *     java HashUtils base64_encode "hello world"
 *
 *     // Base64 解码
 *     java HashUtils base64_decode "aGVsbG8gd29ybGQ="
 *
 *     // 加盐哈希（密码存储）
 *     java HashUtils salt_hash "mypassword"
 *
 *     // 验证加盐哈希
 *     java HashUtils verify "mypassword" "盐值:哈希值"
 *
 *   编译方式：
 *     javac HashUtils.java
 *
 *   免责声明：
 *     本程序仅供安全学习和研究使用，请勿用于非法用途。
 *     MD5 和 SHA1 已被证明存在碰撞漏洞，不可用于密码存储等安全场景。
 *     密码存储推荐使用加盐的 SHA256/SHA512 或更安全的 bcrypt/Argon2。
 *     使用本程序造成的一切后果由使用者自行承担。
 * ==============================================================================
 */
public class HashUtils {

    // ============================================================
    // 打印帮助信息
    // ============================================================
    private static void printHelp() {
        System.out.println("================================================================");
        System.out.println("  哈希与加密工具 - 安全研究用");
        System.out.println("================================================================");
        System.out.println();
        System.out.println("用法: java HashUtils <功能> <参数...>");
        System.out.println();
        System.out.println("可用功能:");
        System.out.println("  md5 <字符串>              - 计算 MD5 哈希");
        System.out.println("  sha1 <字符串>             - 计算 SHA1 哈希");
        System.out.println("  sha256 <字符串>           - 计算 SHA256 哈希");
        System.out.println("  sha512 <字符串>           - 计算 SHA512 哈希");
        System.out.println("  base64_encode <字符串>    - Base64 编码");
        System.out.println("  base64_decode <字符串>    - Base64 解码");
        System.out.println("  salt_hash <密码>          - 加盐哈希（生成盐+哈希）");
        System.out.println("  verify <密码> <哈希>      - 验证密码与加盐哈希是否匹配");
        System.out.println("  all <字符串>              - 计算所有哈希类型");
        System.out.println("  help                      - 显示帮助信息");
        System.out.println();
        System.out.println("示例:");
        System.out.println("  java HashUtils md5 \"hello world\"");
        System.out.println("  java HashUtils sha256 \"password\"");
        System.out.println("  java HashUtils salt_hash \"mypassword\"");
        System.out.println("  java HashUtils verify \"mypassword\" \"<盐>$<哈希>\"");
        System.out.println("================================================================");
    }

    // ============================================================
    // 计算 MD5 哈希
    // 参数：input - 输入字符串
    // 返回：32 位小写十六进制 MD5 哈希值
    // ============================================================
    public static String md5(String input) {
        return hashString(input, "MD5");
    }

    // ============================================================
    // 计算 SHA1 哈希
    // 参数：input - 输入字符串
    // 返回：40 位小写十六进制 SHA1 哈希值
    // ============================================================
    public static String sha1(String input) {
        return hashString(input, "SHA-1");
    }

    // ============================================================
    // 计算 SHA256 哈希
    // 参数：input - 输入字符串
    // 返回：64 位小写十六进制 SHA256 哈希值
    // ============================================================
    public static String sha256(String input) {
        return hashString(input, "SHA-256");
    }

    // ============================================================
    // 计算 SHA512 哈希
    // 参数：input - 输入字符串
    // 返回：128 位小写十六进制 SHA512 哈希值
    // ============================================================
    public static String sha512(String input) {
        return hashString(input, "SHA-512");
    }

    // ============================================================
    // 通用哈希计算函数
    // 使用 Java 标准库 MessageDigest 计算哈希
    // 参数：
    //   input     - 输入字符串
    //   algorithm - 哈希算法名称（MD5, SHA-1, SHA-256, SHA-512）
    // 返回：小写十六进制哈希字符串
    // ============================================================
    private static String hashString(String input, String algorithm) {
        try {
            // 获取 MessageDigest 实例
            MessageDigest digest = MessageDigest.getInstance(algorithm);

            // 将字符串转换为字节数组并计算哈希
            byte[] hashBytes = digest.digest(input.getBytes(StandardCharsets.UTF_8));

            // 将字节数组转换为十六进制字符串
            return bytesToHex(hashBytes);

        } catch (NoSuchAlgorithmException e) {
            return "[错误] 不支持的算法: " + algorithm;
        }
    }

    // ============================================================
    // 字节数组转十六进制字符串
    // 参数：bytes - 字节数组
    // 返回：小写十六进制字符串
    // ============================================================
    private static String bytesToHex(byte[] bytes) {
        StringBuilder hexString = new StringBuilder();
        for (byte b : bytes) {
            // 将每个字节转换为两位十六进制
            String hex = Integer.toHexString(0xff & b);
            if (hex.length() == 1) {
                hexString.append('0'); // 补零
            }
            hexString.append(hex);
        }
        return hexString.toString();
    }

    // ============================================================
    // Base64 编码
    // 参数：input - 输入字符串
    // 返回：Base64 编码后的字符串
    // ============================================================
    public static String base64Encode(String input) {
        byte[] encodedBytes = Base64.getEncoder().encode(input.getBytes(StandardCharsets.UTF_8));
        return new String(encodedBytes, StandardCharsets.UTF_8);
    }

    // ============================================================
    // Base64 解码
    // 参数：input - Base64 编码的字符串
    // 返回：解码后的原始字符串
    // ============================================================
    public static String base64Decode(String input) {
        try {
            byte[] decodedBytes = Base64.getDecoder().decode(input.getBytes(StandardCharsets.UTF_8));
            return new String(decodedBytes, StandardCharsets.UTF_8);
        } catch (IllegalArgumentException e) {
            return "[错误] 无效的 Base64 编码: " + e.getMessage();
        }
    }

    // ============================================================
    // 生成随机盐值
    // 使用 SecureRandom 生成安全的随机盐
    // 参数：length - 盐的字节长度
    // 返回：十六进制表示的盐值
    // ============================================================
    public static String generateSalt(int length) {
        SecureRandom random = new SecureRandom();
        byte[] salt = new byte[length];
        random.nextBytes(salt);
        return bytesToHex(salt);
    }

    // ============================================================
    // 加盐哈希（用于密码存储）
    // 算法：SHA256(盐 + 密码)
    // 格式：盐值$哈希值
    // 参数：password - 明文密码
    // 返回：盐+哈希的组合字符串（格式：盐$哈希）
    // ============================================================
    public static String saltHash(String password) {
        // 生成 16 字节（32 位十六进制）随机盐
        String salt = generateSalt(16);

        // 计算加盐哈希：SHA256(盐 + 密码)
        String saltedPassword = salt + password;
        String hash = sha256(saltedPassword);

        // 返回格式：盐$哈希
        return salt + "$" + hash;
    }

    // ============================================================
    // 验证加盐哈希
    // 参数：
    //   password   - 明文密码
    //   storedHash - 存储的加盐哈希（格式：盐$哈希）
    // 返回：true（匹配）/ false（不匹配）
    // ============================================================
    public static boolean verifySaltHash(String password, String storedHash) {
        // 拆分盐和哈希
        String[] parts = storedHash.split("\\$", 2);
        if (parts.length != 2) {
            System.out.println("[错误] 哈希格式不正确，应为：盐$哈希");
            return false;
        }

        String salt = parts[0];
        String expectedHash = parts[1];

        // 使用相同的盐重新计算哈希
        String saltedPassword = salt + password;
        String actualHash = sha256(saltedPassword);

        // 比较哈希值
        return expectedHash.equalsIgnoreCase(actualHash);
    }

    // ============================================================
    // 计算所有哈希类型并显示
    // ============================================================
    private static void hashAll(String input) {
        System.out.println();
        System.out.println("================================================================");
        System.out.println("  所有哈希类型计算结果");
        System.out.println("================================================================");
        System.out.println();
        System.out.println("  输入字符串: " + input);
        System.out.println();
        System.out.println("  MD5:    " + md5(input));
        System.out.println("  SHA1:   " + sha1(input));
        System.out.println("  SHA256: " + sha256(input));
        System.out.println("  SHA512: " + sha512(input));
        System.out.println();
        System.out.println("  Base64: " + base64Encode(input));
        System.out.println();
        System.out.println("  加盐哈希 (SHA256): " + saltHash(input));
        System.out.println();
        System.out.println("================================================================");
        System.out.println("  安全提示：");
        System.out.println("  - MD5 和 SHA1 已不安全，不应用于密码存储");
        System.out.println("  - 密码存储推荐使用加盐 SHA256+ 或 bcrypt/Argon2");
        System.out.println("  - 每个密码应使用唯一的随机盐");
        System.out.println("================================================================");
    }

    // ============================================================
    // 主程序入口
    // ============================================================
    public static void main(String[] args) {
        // 参数检查
        if (args.length < 1 || args[0].equals("help") || args[0].equals("--help") || args[0].equals("-h")) {
            printHelp();
            return;
        }

        String command = args[0].toLowerCase();

        // 处理各功能
        switch (command) {
            case "md5":
                if (args.length < 2) {
                    System.out.println("[错误] 请提供要哈希的字符串");
                    return;
                }
                System.out.println();
                System.out.println("[MD5 哈希]");
                System.out.println("  输入: " + args[1]);
                System.out.println("  结果: " + md5(args[1]));
                System.out.println();
                break;

            case "sha1":
                if (args.length < 2) {
                    System.out.println("[错误] 请提供要哈希的字符串");
                    return;
                }
                System.out.println();
                System.out.println("[SHA1 哈希]");
                System.out.println("  输入: " + args[1]);
                System.out.println("  结果: " + sha1(args[1]));
                System.out.println();
                break;

            case "sha256":
                if (args.length < 2) {
                    System.out.println("[错误] 请提供要哈希的字符串");
                    return;
                }
                System.out.println();
                System.out.println("[SHA256 哈希]");
                System.out.println("  输入: " + args[1]);
                System.out.println("  结果: " + sha256(args[1]));
                System.out.println();
                break;

            case "sha512":
                if (args.length < 2) {
                    System.out.println("[错误] 请提供要哈希的字符串");
                    return;
                }
                System.out.println();
                System.out.println("[SHA512 哈希]");
                System.out.println("  输入: " + args[1]);
                System.out.println("  结果: " + sha512(args[1]));
                System.out.println();
                break;

            case "base64_encode":
                if (args.length < 2) {
                    System.out.println("[错误] 请提供要编码的字符串");
                    return;
                }
                System.out.println();
                System.out.println("[Base64 编码]");
                System.out.println("  输入: " + args[1]);
                System.out.println("  结果: " + base64Encode(args[1]));
                System.out.println();
                break;

            case "base64_decode":
                if (args.length < 2) {
                    System.out.println("[错误] 请提供要解码的字符串");
                    return;
                }
                System.out.println();
                System.out.println("[Base64 解码]");
                System.out.println("  输入: " + args[1]);
                System.out.println("  结果: " + base64Decode(args[1]));
                System.out.println();
                break;

            case "salt_hash":
            case "salthash":
                if (args.length < 2) {
                    System.out.println("[错误] 请提供密码");
                    return;
                }
                System.out.println();
                System.out.println("[加盐哈希 (SHA256)]");
                System.out.println("  密码: " + maskPassword(args[1]));
                String result = saltHash(args[1]);
                System.out.println("  结果: " + result);
                System.out.println();
                System.out.println("  格式说明: 盐值$哈希值");
                System.out.println("  安全提示: 请妥善保管盐值和哈希值");
                System.out.println();
                break;

            case "verify":
                if (args.length < 3) {
                    System.out.println("[错误] 请提供密码和存储的哈希值");
                    System.out.println("用法: java HashUtils verify <密码> <盐$哈希>");
                    return;
                }
                System.out.println();
                System.out.println("[密码验证]");
                System.out.println("  密码:   " + maskPassword(args[1]));
                System.out.println("  哈希:   " + args[2]);
                boolean valid = verifySaltHash(args[1], args[2]);
                System.out.println();
                if (valid) {
                    System.out.println("  [成功] 密码匹配！");
                } else {
                    System.out.println("  [失败] 密码不匹配");
                }
                System.out.println();
                break;

            case "all":
                if (args.length < 2) {
                    System.out.println("[错误] 请提供要处理的字符串");
                    return;
                }
                hashAll(args[1]);
                break;

            default:
                System.out.println("[错误] 未知功能: " + command);
                System.out.println("输入 'java HashUtils help' 查看帮助");
                break;
        }
    }

    // ============================================================
    // 工具方法：密码脱敏显示
    // ============================================================
    private static String maskPassword(String password) {
        if (password.length() <= 2) {
            return "***";
        }
        return password.charAt(0) + "***" + password.charAt(password.length() - 1);
    }
}
