import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.DataOutputStream;
import java.util.List;
import java.util.Map;

/**
 * ==============================================================================
 *   HTTP 客户端示例 - HttpClientExample.java
 * ==============================================================================
 *   功能说明：
 *     本程序使用 Java 标准库 HttpURLConnection 实现 HTTP 请求，
 *     演示 GET 和 POST 请求的发送方法，用于安全学习和研究。
 *
 *   功能特性：
 *     1. HTTP GET 请求（支持自定义请求头）
 *     2. HTTP POST 请求（表单数据/JSON 数据）
 *     3. 获取响应头信息
 *     4. 获取响应状态码和响应体
 *     5. 支持设置超时时间
 *     6. 支持设置 User-Agent 和 Cookie
 *
 *   使用方法：
 *     java HttpClientExample <URL> [方法] [数据]
 *
 *   示例：
 *     // GET 请求
 *     java HttpClientExample https://httpbin.org/get
 *
 *     // POST 表单请求
 *     java HttpClientExample https://httpbin.org/post POST "name=test&age=20"
 *
 *     // 显示响应头
 *     java HttpClientExample https://httpbin.org/get --headers
 *
 *     // 自定义 User-Agent
 *     java HttpClientExample https://httpbin.org/get --ua "MyBot/1.0"
 *
 *   编译方式：
 *     javac HttpClientExample.java
 *
 *   免责声明：
 *     本程序仅供安全学习和授权测试使用。
 *     请勿用于非法用途或对未授权的网站发起请求。
 *     使用者需对使用本程序产生的一切后果自行承担责任。
 *     请遵守当地法律法规，仅在获得明确授权的情况下使用。
 * ==============================================================================
 */
public class HttpClientExample {

    // 默认 User-Agent
    private static final String DEFAULT_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36";

    // ============================================================
    // 打印帮助信息
    // ============================================================
    private static void printHelp() {
        System.out.println("================================================================");
        System.out.println("  HTTP 客户端示例 - 安全研究用");
        System.out.println("================================================================");
        System.out.println();
        System.out.println("用法: java HttpClientExample <URL> [选项]");
        System.out.println();
        System.out.println("选项:");
        System.out.println("  <URL>              请求的URL地址（必需）");
        System.out.println("  --method <方法>    HTTP 方法: GET / POST（默认 GET）");
        System.out.println("  --data <数据>      POST 请求数据");
        System.out.println("  --type <类型>      数据类型: form / json（默认 form）");
        System.out.println("  --headers          显示响应头信息");
        System.out.println("  --ua <UA>          自定义 User-Agent");
        System.out.println("  --cookie <值>      设置请求 Cookie");
        System.out.println("  --timeout <毫秒>   超时时间（默认 10000）");
        System.out.println("  --help, -h         显示帮助信息");
        System.out.println();
        System.out.println("示例:");
        System.out.println("  java HttpClientExample https://httpbin.org/get");
        System.out.println("  java HttpClientExample https://httpbin.org/post --method POST --data \"name=test&age=20\"");
        System.out.println("  java HttpClientExample https://httpbin.org/headers --headers");
        System.out.println("  java HttpClientExample https://httpbin.org/post --method POST --type json --data \"{\\\"name\\\":\\\"test\\\"}\"");
        System.out.println("================================================================");
    }

    // ============================================================
    // 发送 HTTP GET 请求
    // 参数：
    //   urlStr   - 请求URL
    //   userAgent - User-Agent 字符串
    //   cookie   - Cookie 字符串
    //   timeout  - 超时毫秒
    // 返回：响应信息对象
    // ============================================================
    public static HttpResponse sendGet(String urlStr, String userAgent, String cookie, int timeout) throws Exception {
        URL url = new URL(urlStr);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();

        // 设置请求方法为 GET
        conn.setRequestMethod("GET");

        // 设置超时时间
        conn.setConnectTimeout(timeout);
        conn.setReadTimeout(timeout);

        // 设置 User-Agent
        conn.setRequestProperty("User-Agent", userAgent);

        // 设置 Accept
        conn.setRequestProperty("Accept", "*/*");

        // 设置 Cookie
        if (cookie != null && !cookie.isEmpty()) {
            conn.setRequestProperty("Cookie", cookie);
        }

        // 获取响应
        return getResponse(conn);
    }

    // ============================================================
    // 发送 HTTP POST 请求
    // 参数：
    //   urlStr     - 请求URL
    //   data       - POST 数据
    //   contentType - 数据类型 (application/x-www-form-urlencoded / application/json)
    //   userAgent  - User-Agent 字符串
    //   cookie     - Cookie 字符串
    //   timeout    - 超时毫秒
    // 返回：响应信息对象
    // ============================================================
    public static HttpResponse sendPost(String urlStr, String data, String contentType,
                                         String userAgent, String cookie, int timeout) throws Exception {
        URL url = new URL(urlStr);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();

        // 设置请求方法为 POST
        conn.setRequestMethod("POST");

        // 允许输出（POST 数据）
        conn.setDoOutput(true);

        // 设置超时时间
        conn.setConnectTimeout(timeout);
        conn.setReadTimeout(timeout);

        // 设置 User-Agent
        conn.setRequestProperty("User-Agent", userAgent);

        // 设置 Accept
        conn.setRequestProperty("Accept", "*/*");

        // 设置 Cookie
        if (cookie != null && !cookie.isEmpty()) {
            conn.setRequestProperty("Cookie", cookie);
        }

        // 设置 Content-Type
        conn.setRequestProperty("Content-Type", contentType);

        // 写入 POST 数据
        if (data != null && !data.isEmpty()) {
            byte[] postData = data.getBytes("UTF-8");
            conn.setRequestProperty("Content-Length", String.valueOf(postData.length));

            try (OutputStream os = conn.getOutputStream()) {
                os.write(postData);
                os.flush();
            }
        }

        // 获取响应
        return getResponse(conn);
    }

    // ============================================================
    // 读取响应信息
    // 从 HttpURLConnection 中读取状态码、响应头和响应体
    // ============================================================
    private static HttpResponse getResponse(HttpURLConnection conn) throws Exception {
        HttpResponse response = new HttpResponse();

        // 获取状态码
        response.statusCode = conn.getResponseCode();
        response.statusMessage = conn.getResponseMessage();

        // 获取响应头
        Map<String, List<String>> headers = conn.getHeaderFields();
        response.headers = headers;

        // 读取响应体
        BufferedReader reader;
        try {
            // 正常响应（2xx）使用输入流
            reader = new BufferedReader(new InputStreamReader(conn.getInputStream(), "UTF-8"));
        } catch (Exception e) {
            // 错误响应（4xx/5xx）使用错误流
            if (conn.getErrorStream() != null) {
                reader = new BufferedReader(new InputStreamReader(conn.getErrorStream(), "UTF-8"));
            } else {
                response.body = "";
                conn.disconnect();
                return response;
            }
        }

        StringBuilder body = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            body.append(line).append("\n");
        }
        reader.close();

        response.body = body.toString();

        // 断开连接
        conn.disconnect();

        return response;
    }

    // ============================================================
    // 响应信息内部类
    // ============================================================
    static class HttpResponse {
        int statusCode;           // HTTP 状态码
        String statusMessage;     // 状态描述
        Map<String, List<String>> headers;  // 响应头
        String body;              // 响应体
    }

    // ============================================================
    // 打印响应信息
    // ============================================================
    private static void printResponse(HttpResponse response, boolean showHeaders) {
        System.out.println();
        System.out.println("================================================================");
        System.out.println("  HTTP 响应");
        System.out.println("================================================================");
        System.out.println();
        System.out.println("  状态码: " + response.statusCode + " " + response.statusMessage);
        System.out.println();

        // 显示响应头
        if (showHeaders) {
            System.out.println("----------------------------------------------------------------");
            System.out.println("  响应头");
            System.out.println("----------------------------------------------------------------");
            System.out.println();

            if (response.headers != null) {
                for (Map.Entry<String, List<String>> entry : response.headers.entrySet()) {
                    String key = entry.getKey();
                    if (key == null) key = "(状态行)";
                    String values = String.join(", ", entry.getValue());
                    System.out.println("  " + key + ": " + values);
                }
            }
            System.out.println();
        }

        // 显示响应体
        System.out.println("----------------------------------------------------------------");
        System.out.println("  响应体");
        System.out.println("----------------------------------------------------------------");
        System.out.println();

        if (response.body != null && !response.body.isEmpty()) {
            // 如果响应体太长，只显示前 50 行
            String[] lines = response.body.split("\n");
            int maxLines = Math.min(lines.length, 50);
            for (int i = 0; i < maxLines; i++) {
                System.out.println("  " + lines[i]);
            }
            if (lines.length > 50) {
                System.out.println("  ... (共 " + lines.length + " 行，已截断)");
            }
        } else {
            System.out.println("  (空响应体)");
        }

        System.out.println();
        System.out.println("================================================================");
    }

    // ============================================================
    // 主程序入口
    // ============================================================
    public static void main(String[] args) {
        // 参数检查
        if (args.length < 1 || args[0].equals("--help") || args[0].equals("-h")) {
            printHelp();
            return;
        }

        String url = args[0];
        String method = "GET";
        String postData = "";
        String contentType = "application/x-www-form-urlencoded";
        boolean showHeaders = false;
        String userAgent = DEFAULT_UA;
        String cookie = "";
        int timeout = 10000;

        // 解析参数
        for (int i = 1; i < args.length; i++) {
            switch (args[i]) {
                case "--method":
                    if (i + 1 < args.length) {
                        method = args[++i].toUpperCase();
                    }
                    break;
                case "--data":
                    if (i + 1 < args.length) {
                        postData = args[++i];
                    }
                    break;
                case "--type":
                    if (i + 1 < args.length) {
                        String type = args[++i].toLowerCase();
                        if (type.equals("json")) {
                            contentType = "application/json";
                        } else {
                            contentType = "application/x-www-form-urlencoded";
                        }
                    }
                    break;
                case "--headers":
                    showHeaders = true;
                    break;
                case "--ua":
                    if (i + 1 < args.length) {
                        userAgent = args[++i];
                    }
                    break;
                case "--cookie":
                    if (i + 1 < args.length) {
                        cookie = args[++i];
                    }
                    break;
                case "--timeout":
                    if (i + 1 < args.length) {
                        try {
                            timeout = Integer.parseInt(args[++i]);
                        } catch (NumberFormatException e) {
                            System.out.println("[错误] 超时时间必须是数字");
                            return;
                        }
                    }
                    break;
            }
        }

        // 验证 URL
        if (!url.startsWith("http://") && !url.startsWith("https://")) {
            url = "https://" + url;
        }

        System.out.println();
        System.out.println("================================================================");
        System.out.println("  HTTP 客户端");
        System.out.println("================================================================");
        System.out.println();
        System.out.println("[信息] 请求URL:    " + url);
        System.out.println("[信息] 请求方法:   " + method);
        System.out.println("[信息] User-Agent: " + userAgent);
        System.out.println("[信息] 超时时间:   " + timeout + " 毫秒");

        if (method.equals("POST") && !postData.isEmpty()) {
            System.out.println("[信息] POST 数据:  " + postData);
            System.out.println("[信息] 内容类型:   " + contentType);
        }

        System.out.println();
        System.out.println("[信息] 正在发送请求...");

        try {
            HttpResponse response;

            if (method.equals("POST")) {
                // POST 请求
                response = sendPost(url, postData, contentType, userAgent, cookie, timeout);
            } else {
                // GET 请求
                response = sendGet(url, userAgent, cookie, timeout);
            }

            // 打印响应
            printResponse(response, showHeaders);

        } catch (Exception e) {
            System.out.println();
            System.out.println("[错误] 请求失败: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
