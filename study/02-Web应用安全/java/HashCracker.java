import java.io.BufferedReader;
import java.io.FileReader;
import java.security.MessageDigest;
import java.util.HashSet;
import java.util.Set;

/**
 * HashCracker.java
 * 哈希破解工具 - Java 安全实战
 *
 * 使用字典攻击破解 MD5/SHA1 哈希
 * 安全研究用途：测试密码强度
 *
 * 仅用于安全学习和授权测试，禁止非法用途
 *
 * 编译: javac HashCracker.java
 * 运行: java HashCracker <hash> [algorithm] [wordlist]
 * 示例:
 *   java HashCracker 5d41402abc4b2a76b9719d911017c592
 *   java HashCracker 5d41402abc4b2a76b9719d911017c592 md5 passwords.txt
 *   java HashCracker aaf4c61ddcc5e8a2dab6b1e6f887b892 sha1
 */
public class HashCracker {

    // 内置弱口令字典
    private static final String[] BUILTIN_DICT = {
        "123456", "password", "123456789", "12345678", "12345", "1234567",
        "admin", "root", "test", "guest", "user", "qwerty",
        "abc123", "111111", "000000", "password1", "password123",
        "admin123", "root123", "letmein", "welcome", "monkey",
        "dragon", "master", "login", "superman", "hello",
        "1q2w3e4r", "pass", "pass123", "p@ssw0rd", "P@ssword1",
        "iloveyou", "trustno1", "sunshine", "shadow", "football",
        "baseball", "michael", "charlie", "access", "hello123",
        "123", "1", "a", "11", "12", "1234", "1234567890",
        "q1w2e3r4", "asdf", "zxcv", "aaa", "bbb", "ccc",
    };

    // 计算哈希
    private static String computeHash(String input, String algorithm) {
        try {
            MessageDigest md = MessageDigest.getInstance(algorithm);
            byte[] hashBytes = md.digest(input.getBytes("UTF-8"));
            StringBuilder sb = new StringBuilder();
            for (byte b : hashBytes) {
                sb.append(String.format("%02x", b));
            }
            return sb.toString();
        } catch (Exception e) {
            return "";
        }
    }

    public static void main(String[] args) {
        System.out.println("========================================");
        System.out.println("  哈希破解工具 (Java)");
        System.out.println("  支持 MD5/SHA1/SHA256 字典攻击");
        System.out.println("  仅用于安全学习和授权测试");
        System.out.println("========================================");

        if (args.length < 1) {
            System.out.println("用法: java HashCracker <hash> [algorithm] [wordlist]");
            System.out.println("算法: md5 (默认), sha1, sha256");
            System.out.println("示例:");
            System.out.println("  java HashCracker 5d41402abc4b2a76b9719d911017c592");
            System.out.println("  java HashCracker aaf4c61ddcc5e8a2dab6b1e6f887b892 sha1");
            System.out.println("  java HashCracker 5d41402abc4b2a76b9719d911017c592 md5 custom.txt");
            System.exit(1);
        }

        String targetHash = args[0].toLowerCase();
        String algorithm = args.length > 1 ? args[1].toLowerCase() : "md5";
        String wordlistFile = args.length > 2 ? args[2] : null;

        // 验证算法
        if (!algorithm.matches("md5|sha-?1|sha-?256")) {
            System.out.println("[!] 不支持的算法: " + algorithm);
            System.out.println("    支持: md5, sha1, sha256");
            System.exit(1);
        }

        // 标准化算法名
        algorithm = algorithm.replace("sha1", "SHA-1").replace("sha-1", "SHA-1")
                            .replace("sha256", "SHA-256").replace("sha-256", "SHA-256");
        if (algorithm.equals("md5")) algorithm = "MD5";

        System.out.println("[*] 目标哈希: " + targetHash);
        System.out.println("[*] 算法: " + algorithm);

        // 加载字典
        Set<String> wordlist = new HashSet<>();
        if (wordlistFile != null) {
            System.out.println("[*] 加载字典文件: " + wordlistFile);
            try (BufferedReader br = new BufferedReader(new FileReader(wordlistFile))) {
                String line;
                while ((line = br.readLine()) != null) {
                    line = line.trim();
                    if (!line.isEmpty() && !line.startsWith("#")) {
                        wordlist.add(line);
                    }
                }
                System.out.println("[*] 字典条目: " + wordlist.size());
            } catch (Exception e) {
                System.err.println("[!] 无法读取字典文件: " + e.getMessage());
                System.out.println("[*] 回退到内置字典");
                wordlist.addAll(Arrays.asList(BUILTIN_DICT));
            }
        } else {
            System.out.println("[*] 使用内置字典: " + BUILTIN_DICT.length + " 条");
            wordlist.addAll(Arrays.asList(BUILTIN_DICT));
        }

        // 开始破解
        System.out.println("[*] 开始破解...\n");

        int tried = 0;
        boolean found = false;
        long startTime = System.currentTimeMillis();

        for (String word : wordlist) {
            tried++;
            String hash = computeHash(word, algorithm);

            if (tried % 1000 == 0) {
                System.out.printf("  [进度] 已尝试 %d 条\r", tried);
            }

            if (hash.equals(targetHash)) {
                long elapsed = System.currentTimeMillis() - startTime;
                System.out.println("\n[+] 破解成功！");
                System.out.println("    明文: " + word);
                System.out.println("    哈希: " + hash);
                System.out.println("    算法: " + algorithm);
                System.out.println("    尝试次数: " + tried);
                System.out.println("    耗时: " + (elapsed / 1000.0) + "s");
                found = true;
                break;
            }
        }

        if (!found) {
            long elapsed = System.currentTimeMillis() - startTime;
            System.out.println("\n[-] 破解失败");
            System.out.println("    尝试次数: " + tried);
            System.out.println("    耗时: " + (elapsed / 1000.0) + "s");
            System.out.println("    建议: 尝试更大的字典或使用彩虹表");
        }
    }
}
