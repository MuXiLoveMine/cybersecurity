import java.io.IOException;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * PortScanner.java
 * TCP 端口扫描器 - Java 安全实战
 *
 * 使用 Socket 进行 TCP 全连接扫描，线程池并发
 *
 * 仅用于安全学习和授权测试，禁止非法用途
 *
 * 编译: javac PortScanner.java
 * 运行: java PortScanner <IP> [startPort] [endPort] [threads]
 * 示例: java PortScanner 192.168.1.1 1 1000 100
 *       java PortScanner 192.168.1.1 22 443 50
 */
public class PortScanner {

    // 常见端口服务名
    private static final Map<Integer, String> SERVICE_MAP = new HashMap<>();
    static {
        SERVICE_MAP.put(21, "FTP"); SERVICE_MAP.put(22, "SSH");
        SERVICE_MAP.put(23, "Telnet"); SERVICE_MAP.put(25, "SMTP");
        SERVICE_MAP.put(53, "DNS"); SERVICE_MAP.put(80, "HTTP");
        SERVICE_MAP.put(110, "POP3"); SERVICE_MAP.put(143, "IMAP");
        SERVICE_MAP.put(443, "HTTPS"); SERVICE_MAP.put(445, "SMB");
        SERVICE_MAP.put(1433, "MSSQL"); SERVICE_MAP.put(3306, "MySQL");
        SERVICE_MAP.put(3389, "RDP"); SERVICE_MAP.put(5432, "PostgreSQL");
        SERVICE_MAP.put(6379, "Redis"); SERVICE_MAP.put(8080, "HTTP-Alt");
        SERVICE_MAP.put(9200, "Elasticsearch"); SERVICE_MAP.put(27017, "MongoDB");
    }

    // 扫描单个端口
    private static boolean scanPort(String host, int port, int timeout) {
        try (Socket socket = new Socket()) {
            socket.connect(new InetSocketAddress(host, port), timeout);
            return true;
        } catch (IOException e) {
            return false;
        }
    }

    public static void main(String[] args) {
        System.out.println("========================================");
        System.out.println("  TCP 端口扫描器 (Java)");
        System.out.println("  仅用于安全学习和授权测试");
        System.out.println("========================================");

        if (args.length < 1) {
            System.out.println("用法: java PortScanner <IP> [startPort] [endPort] [threads]");
            System.out.println("示例: java PortScanner 192.168.1.1 1 1000 100");
            System.exit(1);
        }

        String host = args[0];
        int startPort = args.length > 1 ? Integer.parseInt(args[1]) : 1;
        int endPort = args.length > 2 ? Integer.parseInt(args[2]) : 1024;
        int threads = args.length > 3 ? Integer.parseInt(args[3]) : 50;
        int timeout = 1500;

        int totalPorts = endPort - startPort + 1;
        System.out.println("[*] 目标: " + host);
        System.out.println("[*] 端口范围: " + startPort + "-" + endPort);
        System.out.println("[*] 并发线程: " + threads);
        System.out.println("[*] 开始扫描...\n");

        ExecutorService executor = Executors.newFixedThreadPool(threads);
        AtomicInteger scanned = new AtomicInteger(0);
        AtomicInteger foundCount = new AtomicInteger(0);
        long startTime = System.currentTimeMillis();

        for (int port = startPort; port <= endPort; port++) {
            final int p = port;
            executor.submit(() -> {
                if (scanPort(host, p, timeout)) {
                    String service = SERVICE_MAP.getOrDefault(p, "unknown");
                    System.out.println("  [+] " + host + ":" + p + "  OPEN  (" + service + ")");
                    foundCount.incrementAndGet();
                }
                int done = scanned.incrementAndGet();
                if (done % 100 == 0) {
                    int progress = (done * 100 / totalPorts);
                    System.out.printf("  [进度] %d / %d (%d%%)\r", done, totalPorts, progress);
                }
            });
        }

        executor.shutdown();
        try {
            executor.awaitTermination(5, TimeUnit.MINUTES);
        } catch (InterruptedException e) {
            System.err.println("[!] 扫描被中断");
        }

        long elapsed = (System.currentTimeMillis() - startTime) / 1000;

        System.out.println("\n\n===== 扫描结果 =====");
        System.out.println("目标: " + host);
        System.out.println("扫描端口: " + totalPorts);
        System.out.println("开放端口: " + foundCount.get());
        System.out.println("耗时: " + elapsed + "s");
    }
}
