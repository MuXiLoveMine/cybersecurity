import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * DirBrute.java
 * Web 目录爆破工具 - Java 安全实战
 *
 * 基于 HttpURLConnection 的目录/文件扫描
 * 内置常见路径字典，支持多线程并发
 *
 * 仅用于安全学习和授权测试
 *
 * 编译: javac DirBrute.java
 * 运行: java DirBrute http://example.com [threads]
 */
public class DirBrute {

    // 内置字典
    private static final List<String> DICT = Arrays.asList(
        "admin", "administrator", "login", "manage", "backend",
        "backup", "config", "test", "debug", "tmp", "temp",
        "api", "v1", "v2", "swagger", "graphql",
        ".git", ".svn", ".env", ".htaccess", "web.config",
        "phpinfo", "phpmyadmin", "pma", "adminer", "wp-admin",
        "upload", "uploads", "files", "data", "shell",
        "logs", "robots.txt", "sitemap.xml", "README",
        "install", "setup", "old", "new", "dev", "stage",
        "include", "lib", "src", "static", "public",
        "assets", "js", "css", "index.php", "index.html",
        "backup.zip", "backup.sql", "dump.sql",
        ".DS_Store", ".gitignore", "Dockerfile",
        "vendor", "composer.json", "package.json"
    );

    private static final String[] EXTENSIONS = {"", ".php", ".html", ".bak", ".txt"};

    private static void scanPath(String baseUrl, String path) {
        try {
            URL url = new URL(baseUrl + "/" + path);
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("GET");
            conn.setConnectTimeout(5000);
            conn.setReadTimeout(5000);
            conn.setInstanceFollowRedirects(false);
            conn.setRequestProperty("User-Agent", "Mozilla/5.0 (Security Scanner)");

            int code = conn.getResponseCode();
            int length = conn.getContentLength();

            if (code == 200 || code == 301 || code == 302 || code == 401 || code == 403) {
                String status;
                switch (code) {
                    case 200: status = "200 OK"; break;
                    case 301: case 302: status = code + " Redirect"; break;
                    case 401: status = "401 Unauthorized"; break;
                    case 403: status = "403 Forbidden"; break;
                    default: status = String.valueOf(code);
                }
                System.out.printf("  [%s] /%s  (%d bytes)%n", status, path, length);
            }
            conn.disconnect();
        } catch (Exception e) {
            // 忽略超时和连接失败
        }
    }

    public static void main(String[] args) {
        System.out.println("========================================");
        System.out.println("  Web 目录爆破工具 (Java)");
        System.out.println("  仅用于安全学习和授权测试");
        System.out.println("========================================");

        if (args.length < 1) {
            System.out.println("用法: java DirBrute <URL> [threads]");
            System.out.println("示例: java DirBrute http://example.com 20");
            System.exit(1);
        }

        String baseUrl = args[0].replaceAll("/$", "");
        int threads = args.length > 1 ? Integer.parseInt(args[1]) : 10;

        // 构建路径列表
        java.util.List<String> paths = new java.util.ArrayList<>();
        for (String word : DICT) {
            for (String ext : EXTENSIONS) {
                paths.add(word + ext);
            }
        }

        System.out.println("[*] 目标: " + baseUrl);
        System.out.println("[*] 路径数: " + paths.size());
        System.out.println("[*] 并发: " + threads);
        System.out.println("[*] 开始扫描...\n");

        ExecutorService executor = Executors.newFixedThreadPool(threads);
        AtomicInteger scanned = new AtomicInteger(0);
        AtomicInteger found = new AtomicInteger(0);
        int total = paths.size();

        for (String path : paths) {
            executor.submit(() -> {
                scanPath(baseUrl, path);
                int done = scanned.incrementAndGet();
                if (done % 50 == 0) {
                    System.out.printf("  [进度] %d / %d%n", done, total);
                }
            });
        }

        executor.shutdown();
        try {
            executor.awaitTermination(5, TimeUnit.MINUTES);
        } catch (InterruptedException e) {
            System.err.println("[!] 扫描被中断");
        }

        System.out.println("\n===== 扫描完成 =====");
        System.out.println("总请求: " + total);
    }
}
