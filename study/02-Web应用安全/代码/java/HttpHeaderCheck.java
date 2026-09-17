import java.net.HttpURLConnection;
import java.net.URL;
import java.util.*;

/**
 * HttpHeaderCheck.java
 * HTTP 安全头检测工具 - Java 安全实战
 *
 * 检测目标网站的 HTTP 安全响应头配置
 * 给出安全评分和修复建议
 *
 * 仅用于安全学习和授权测试
 *
 * 编译: javac HttpHeaderCheck.java
 * 运行: java HttpHeaderCheck https://example.com
 */
public class HttpHeaderCheck {

    // 安全头配置
    static class HeaderConfig {
        String name;
        int score;
        String risk;
        String desc;
        String fix;

        HeaderConfig(String name, int score, String risk, String desc, String fix) {
            this.name = name;
            this.score = score;
            this.risk = risk;
            this.desc = desc;
            this.fix = fix;
        }
    }

    private static final List<HeaderConfig> SECURITY_HEADERS = Arrays.asList(
        new HeaderConfig("X-Frame-Options", 10, "高", "防止点击劫持", "X-Frame-Options: SAMEORIGIN"),
        new HeaderConfig("X-Content-Type-Options", 10, "高", "防止 MIME 嗅探", "X-Content-Type-Options: nosniff"),
        new HeaderConfig("X-XSS-Protection", 5, "中", "浏览器 XSS 过滤器", "X-XSS-Protection: 1; mode=block"),
        new HeaderConfig("Content-Security-Policy", 15, "高", "内容安全策略", "Content-Security-Policy: default-src 'self'"),
        new HeaderConfig("Strict-Transport-Security", 10, "高", "HSTS 强制 HTTPS", "Strict-Transport-Security: max-age=31536000"),
        new HeaderConfig("Referrer-Policy", 5, "中", "控制 Referer 泄露", "Referrer-Policy: no-referrer-when-downgrade"),
        new HeaderConfig("Permissions-Policy", 5, "低", "浏览器功能权限控制", "Permissions-Policy: geolocation=()")
    );

    private static final String[] LEAK_HEADERS = {
        "Server", "X-Powered-By", "X-AspNet-Version", "Via", "X-Runtime"
    };

    public static void main(String[] args) {
        System.out.println("========================================");
        System.out.println("  HTTP 安全头检测工具 (Java)");
        System.out.println("  仅用于安全学习和授权测试");
        System.out.println("========================================");

        if (args.length < 1) {
            System.out.println("用法: java HttpHeaderCheck <URL>");
            System.out.println("示例: java HttpHeaderCheck https://example.com");
            System.exit(1);
        }

        String targetUrl = args[0];
        System.out.println("[*] 目标: " + targetUrl + "\n");

        try {
            URL url = new URL(targetUrl);
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("GET");
            conn.setConnectTimeout(15000);
            conn.setReadTimeout(15000);
            conn.setInstanceFollowRedirects(false);
            conn.setRequestProperty("User-Agent", "Mozilla/5.0 (Security Scanner)");

            // 获取响应头
            Map<String, List<String>> headers = conn.getHeaderFields();
            int statusCode = conn.getResponseCode();
            System.out.println("[*] HTTP 状态码: " + statusCode + "\n");

            // 转为小写键查找
            Map<String, String> headerMap = new HashMap<>();
            for (Map.Entry<String, List<String>> entry : headers.entrySet()) {
                if (entry.getKey() != null) {
                    headerMap.put(entry.getKey().toLowerCase(),
                        String.join(", ", entry.getValue()));
                }
            }

            // 安全头检测
            System.out.println("===== 安全响应头检查 =====");
            int totalScore = 0;
            int maxScore = 0;
            List<HeaderConfig> missing = new ArrayList<>();

            for (HeaderConfig config : SECURITY_HEADERS) {
                maxScore += config.score;
                String key = config.name.toLowerCase();
                if (headerMap.containsKey(key)) {
                    String value = headerMap.get(key);
                    totalScore += config.score;
                    System.out.println("  [+] " + config.name + " : " + value);
                } else {
                    System.out.println("  [-] " + config.name + " : 缺失 (风险:" + config.risk +
                        " | " + config.desc + " | 建议:" + config.fix + ")");
                    missing.add(config);
                }
            }

            // 信息泄露检测
            System.out.println("\n===== 信息泄露检测 =====");
            boolean leakFound = false;
            for (String lh : LEAK_HEADERS) {
                String key = lh.toLowerCase();
                if (headerMap.containsKey(key)) {
                    System.out.println("  [!] " + lh + " : " + headerMap.get(key));
                    leakFound = true;
                    totalScore -= 5;
                }
            }
            if (!leakFound) {
                System.out.println("  [+] 未检测到信息泄露头");
            }

            // Cookie 安全检测
            System.out.println("\n===== Cookie 安全检测 =====");
            String setCookie = headerMap.get("set-cookie");
            if (setCookie != null) {
                boolean hasSecure = setCookie.toLowerCase().contains("secure");
                boolean hasHttpOnly = setCookie.toLowerCase().contains("httponly");
                boolean hasSameSite = setCookie.toLowerCase().contains("samesite");

                if (!hasSecure) System.out.println("  [-] Cookie 缺少 Secure 属性");
                if (!hasHttpOnly) System.out.println("  [-] Cookie 缺少 HttpOnly 属性");
                if (!hasSameSite) System.out.println("  [-] Cookie 缺少 SameSite 属性");
                if (hasSecure && hasHttpOnly && hasSameSite) {
                    System.out.println("  [+] Cookie 安全属性完整");
                }
            } else {
                System.out.println("  [*] 未设置 Cookie");
            }

            // 评分
            int percentage = maxScore > 0 ? (totalScore * 100 / maxScore) : 0;
            String grade = percentage >= 90 ? "A" : (percentage >= 80 ? "B" :
                          (percentage >= 70 ? "C" : (percentage >= 60 ? "D" : "F")));

            System.out.println("\n===== 安全评分 =====");
            System.out.println("  得分: " + totalScore + " / " + maxScore + " (" + percentage + "%)");
            System.out.println("  等级: " + grade);

            // 修复建议
            System.out.println("\n===== 修复建议 =====");
            if (!missing.isEmpty()) {
                for (HeaderConfig m : missing) {
                    System.out.println("  [" + m.risk + "] " + m.fix);
                }
            } else {
                System.out.println("  所有安全头已正确配置！");
            }

            conn.disconnect();

        } catch (Exception e) {
            System.err.println("[!] 请求失败: " + e.getMessage());
        }
    }
}
