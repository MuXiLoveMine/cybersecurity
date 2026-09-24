# java.net - Java 网络编程包

> Java 标准库网络包，提供 Socket、URL、HTTP 等网络编程功能。

---

## 一、Socket 编程

### 1.1 TCP 客户端

```java
import java.net.Socket;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.io.IOException;

public class TcpClient {
    public static void main(String[] args) {
        String hostname = "example.com";
        int port = 80;
        
        try (Socket socket = new Socket(hostname, port)) {
            // 设置超时
            socket.setSoTimeout(5000);  // 5 秒读超时
            socket.setConnectTimeout(5000);  // 连接超时（构造函数中不直接支持）
            
            // 获取输出流（发送数据）
            PrintWriter out = new PrintWriter(socket.getOutputStream(), true);
            
            // 获取输入流（接收数据）
            BufferedReader in = new BufferedReader(
                new InputStreamReader(socket.getInputStream()));
            
            // 发送 HTTP 请求
            out.println("GET / HTTP/1.1");
            out.println("Host: " + hostname);
            out.println("Connection: close");
            out.println();
            
            // 读取响应
            String line;
            while ((line = in.readLine()) != null) {
                System.out.println(line);
            }
            
        } catch (IOException e) {
            System.err.println("连接错误: " + e.getMessage());
        }
    }
}
```

### 1.2 TCP 服务器

```java
import java.net.ServerSocket;
import java.net.Socket;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.io.IOException;

public class TcpServer {
    public static void main(String[] args) {
        int port = 8080;
        
        try (ServerSocket serverSocket = new ServerSocket(port)) {
            System.out.println("服务器监听端口 " + port);
            
            // 设置服务器 socket 选项
            serverSocket.setReuseAddress(true);  // 地址重用
            
            while (true) {
                // 接受连接（阻塞）
                Socket clientSocket = serverSocket.accept();
                
                System.out.println("新连接: " + 
                    clientSocket.getInetAddress().getHostAddress() +
                    ":" + clientSocket.getPort());
                
                // 新线程处理客户端
                new Thread(() -> handleClient(clientSocket)).start();
            }
            
        } catch (IOException e) {
            System.err.println("服务器错误: " + e.getMessage());
        }
    }
    
    private static void handleClient(Socket socket) {
        try (
            BufferedReader in = new BufferedReader(
                new InputStreamReader(socket.getInputStream()));
            PrintWriter out = new PrintWriter(socket.getOutputStream(), true)
        ) {
            // 读取一行
            String line = in.readLine();
            System.out.println("收到: " + line);
            
            // 回送响应
            out.println("Echo: " + line);
            
        } catch (IOException e) {
            System.err.println("客户端处理错误: " + e.getMessage());
        } finally {
            try {
                socket.close();
            } catch (IOException e) {
                // ignore
            }
        }
    }
}
```

### 1.3 Socket 常用选项

```java
Socket socket = new Socket();

// 连接超时
socket.connect(new InetSocketAddress(host, port), 5000);  // 5秒

// 读超时
socket.setSoTimeout(5000);  // read() 最多等 5 秒

// TCP_NODELAY（禁用 Nagle 算法）
socket.setTcpNoDelay(true);

// SO_KEEPALIVE
socket.setKeepAlive(true);

// SO_LINGER
socket.setSoLinger(true, 10);  // close 后等待 10 秒发送完数据

// 发送/接收缓冲区大小
socket.setSendBufferSize(65536);
socket.setReceiveBufferSize(65536);

// SO_REUSEADDR
ServerSocket ss = new ServerSocket();
ss.setReuseAddress(true);
ss.bind(new InetSocketAddress(port));
```

---

## 二、UDP 编程

### 2.1 UDP 客户端

```java
import java.net.DatagramSocket;
import java.net.DatagramPacket;
import java.net.InetAddress;

public class UdpClient {
    public static void main(String[] args) {
        try (DatagramSocket socket = new DatagramSocket()) {
            socket.setSoTimeout(5000);  // 超时
            
            InetAddress address = InetAddress.getByName("example.com");
            int port = 12345;
            
            // 发送数据
            String message = "Hello UDP";
            byte[] sendData = message.getBytes();
            
            DatagramPacket sendPacket = new DatagramPacket(
                sendData, sendData.length, address, port);
            socket.send(sendPacket);
            
            // 接收响应
            byte[] receiveData = new byte[1024];
            DatagramPacket receivePacket = new DatagramPacket(
                receiveData, receiveData.length);
            socket.receive(receivePacket);
            
            String response = new String(
                receivePacket.getData(), 0, receivePacket.getLength());
            System.out.println("收到: " + response);
            
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

### 2.2 UDP 服务器

```java
import java.net.DatagramSocket;
import java.net.DatagramPacket;

public class UdpServer {
    public static void main(String[] args) {
        int port = 12345;
        
        try (DatagramSocket socket = new DatagramSocket(port)) {
            System.out.println("UDP 服务器监听端口 " + port);
            
            byte[] buffer = new byte[1024];
            
            while (true) {
                DatagramPacket packet = new DatagramPacket(buffer, buffer.length);
                socket.receive(packet);
                
                String message = new String(
                    packet.getData(), 0, packet.getLength());
                
                System.out.println("收到来自 " + 
                    packet.getAddress().getHostAddress() + 
                    ":" + packet.getPort() + " 的消息: " + message);
                
                // 回送响应
                String response = "Echo: " + message;
                byte[] responseData = response.getBytes();
                
                DatagramPacket responsePacket = new DatagramPacket(
                    responseData, responseData.length,
                    packet.getAddress(), packet.getPort());
                socket.send(responsePacket);
            }
            
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

---

## 三、URL 与 HTTP

### 3.1 URL 类

```java
import java.net.URL;
import java.net.MalformedURLException;

URL url = new URL("https://www.example.com:8080/path?query=value#fragment");

System.out.println("协议: " + url.getProtocol());    // https
System.out.println("主机: " + url.getHost());        // www.example.com
System.out.println("端口: " + url.getPort());        // 8080
System.out.println("默认端口: " + url.getDefaultPort());  // 443
System.out.println("路径: " + url.getPath());        // /path
System.out.println("查询: " + url.getQuery());       // query=value
System.out.println("锚点: " + url.getRef());         // fragment
System.out.println("文件: " + url.getFile());        // /path?query=value
System.out.println("权限: " + url.getAuthority());   // www.example.com:8080
```

### 3.2 URLConnection / HttpURLConnection

```java
import java.net.URL;
import java.net.HttpURLConnection;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;

public class HttpExample {
    // GET 请求
    public static String get(String urlStr) throws Exception {
        URL url = new URL(urlStr);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        
        conn.setRequestMethod("GET");
        conn.setRequestProperty("Accept", "application/json");
        conn.setRequestProperty("User-Agent", "MyApp/1.0");
        conn.setConnectTimeout(5000);   // 连接超时
        conn.setReadTimeout(5000);      // 读超时
        
        int responseCode = conn.getResponseCode();
        System.out.println("响应码: " + responseCode);
        
        // 读取响应
        BufferedReader in = new BufferedReader(
            new InputStreamReader(conn.getInputStream()));
        
        StringBuilder response = new StringBuilder();
        String line;
        while ((line = in.readLine()) != null) {
            response.append(line);
        }
        in.close();
        
        conn.disconnect();
        return response.toString();
    }
    
    // POST 请求
    public static String post(String urlStr, String jsonBody) throws Exception {
        URL url = new URL(urlStr);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        
        conn.setRequestMethod("POST");
        conn.setRequestProperty("Content-Type", "application/json");
        conn.setRequestProperty("Accept", "application/json");
        conn.setDoOutput(true);  // 允许输出
        conn.setConnectTimeout(5000);
        conn.setReadTimeout(5000);
        
        // 发送请求体
        try (OutputStream os = conn.getOutputStream()) {
            byte[] input = jsonBody.getBytes("utf-8");
            os.write(input, 0, input.length);
        }
        
        // 读取响应
        BufferedReader in = new BufferedReader(
            new InputStreamReader(conn.getInputStream(), "utf-8"));
        
        StringBuilder response = new StringBuilder();
        String line;
        while ((line = in.readLine()) != null) {
            response.append(line);
        }
        in.close();
        
        conn.disconnect();
        return response.toString();
    }
}
```

### 3.3 InetAddress

```java
import java.net.InetAddress;
import java.net.Inet4Address;
import java.net.Inet6Address;
import java.net.UnknownHostException;

// 根据域名获取 IP
InetAddress[] addresses = InetAddress.getAllByName("www.example.com");
for (InetAddress addr : addresses) {
    System.out.println(addr.getHostAddress());
}

// 获取本机地址
InetAddress localHost = InetAddress.getLocalHost();
System.out.println(localHost.getHostAddress());

// 检查是否可达
InetAddress addr = InetAddress.getByName("8.8.8.8");
boolean reachable = addr.isReachable(3000);  // 3 秒超时

// IP 地址信息
InetAddress addr = InetAddress.getByName("192.168.1.1");
addr.isLoopbackAddress();     // 是否回环地址
addr.isSiteLocalAddress();    // 是否站点本地地址（内网）
addr.isLinkLocalAddress();    // 是否链路本地地址
addr.isMulticastAddress();    // 是否组播地址
```

---

## 四、安全相关内容

### 4.1 常见网络安全问题

```java
/*
    Java 网络编程常见安全问题：
    
    1. SSL/TLS 证书验证问题
       - 禁用证书验证（信任所有证书）
       - 禁用主机名验证
       
    2. SSRF（服务端请求伪造）
       - 用户可控 URL
       - 访问内网资源
       
    3. 资源耗尽（DoS）
       - 不限制连接数
       - 不限制读取数据大小
       
    4. 输入验证不足
       - 未验证输入长度、格式
       - 缓冲区相关问题
    
    5. 敏感信息泄露
       - 错误信息包含敏感数据
*/

// ===== 危险：信任所有证书（不要这样做！）=====
// 有时开发人员为了方便会写这样的代码：
// TrustManager[] trustAll = new TrustManager[] { ... 信任所有 ... };
// 这会导致中间人攻击

// ===== 正确：使用默认证书验证 =====
// Java 默认会验证证书链和主机名
URL url = new URL("https://secure.example.com");
HttpURLConnection conn = (HttpURLConnection) url.openConnection();
// 自动使用系统信任的 CA 证书
```

### 4.2 输入验证与大小限制

```java
// 安全的读取（防止超大数据导致内存溢出）
public String readLimited(BufferedReader reader, int maxBytes) throws IOException {
    StringBuilder sb = new StringBuilder();
    int total = 0;
    char[] buffer = new char[4096];
    
    while (total < maxBytes) {
        int read = reader.read(buffer, 0, Math.min(buffer.length, maxBytes - total));
        if (read == -1) break;
        sb.append(buffer, 0, read);
        total += read;
    }
    
    if (total >= maxBytes) {
        throw new IOException("数据超过最大限制");
    }
    
    return sb.toString();
}

// 端口范围验证
public boolean isValidPort(int port) {
    return port >= 1 && port <= 65535;
}

// IP 地址格式验证
public boolean isValidIp(String ip) {
    try {
        InetAddress.getByName(ip);
        return true;
    } catch (UnknownHostException e) {
        return false;
    }
}
```

### 4.3 SSRF 防护

```java
import java.net.InetAddress;
import java.net.URL;

public class SsrfProtection {
    
    // 检查是否是内网 IP
    public static boolean isInternalIp(String ipStr) {
        try {
            InetAddress addr = InetAddress.getByName(ipStr);
            return addr.isLoopbackAddress() ||
                   addr.isSiteLocalAddress() ||
                   addr.isLinkLocalAddress() ||
                   addr.isAnyLocalAddress();
        } catch (Exception e) {
            return true;  // 解析失败也算不安全
        }
    }
    
    // 安全的 HTTP 请求（防止 SSRF）
    public static String safeHttpGet(String urlStr, int maxSize) throws Exception {
        URL url = new URL(urlStr);
        
        // 检查协议
        String protocol = url.getProtocol().toLowerCase();
        if (!protocol.equals("http") && !protocol.equals("https")) {
            throw new SecurityException("不支持的协议: " + protocol);
        }
        
        // 解析 IP 并检查
        String host = url.getHost();
        InetAddress[] addresses = InetAddress.getAllByName(host);
        
        for (InetAddress addr : addresses) {
            if (isInternalIp(addr.getHostAddress())) {
                throw new SecurityException("禁止访问内网地址: " + addr.getHostAddress());
            }
        }
        
        // 注意：DNS 重绑定攻击可能绕过（解析和连接之间 DNS 变了）
        // 更安全的做法是直接连接 IP 而不是域名
        
        // 发送请求
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setConnectTimeout(5000);
        conn.setReadTimeout(5000);
        
        // 限制响应大小
        int contentLength = conn.getContentLength();
        if (contentLength > maxSize) {
            conn.disconnect();
            throw new IOException("响应过大");
        }
        
        // 读取并限制大小
        // ... 读取逻辑 ...
        
        conn.disconnect();
        return null;
    }
}
```

---

## 五、HttpClient（Java 11+）

```java
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;

// Java 11+ 内置的 HttpClient（推荐使用）
public class HttpClientExample {
    
    public static void main(String[] args) throws Exception {
        // 创建客户端
        HttpClient client = HttpClient.newBuilder()
            .version(HttpClient.Version.HTTP_2)
            .connectTimeout(Duration.ofSeconds(5))
            .followRedirects(HttpClient.Redirect.NORMAL)
            .build();
        
        // GET 请求
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create("https://api.example.com/data"))
            .timeout(Duration.ofSeconds(5))
            .header("Accept", "application/json")
            .GET()
            .build();
        
        HttpResponse<String> response = client.send(
            request, HttpResponse.BodyHandlers.ofString());
        
        System.out.println("状态码: " + response.statusCode());
        System.out.println("响应体: " + response.body());
        
        // POST 请求
        HttpRequest postRequest = HttpRequest.newBuilder()
            .uri(URI.create("https://api.example.com/users"))
            .timeout(Duration.ofSeconds(5))
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString(
                "{\"name\":\"John\",\"email\":\"john@example.com\"}"))
            .build();
        
        HttpResponse<String> postResponse = client.send(
            postRequest, HttpResponse.BodyHandlers.ofString());
        
        // 异步请求
        client.sendAsync(request, HttpResponse.BodyHandlers.ofString())
            .thenApply(HttpResponse::body)
            .thenAccept(System.out::println);
    }
}
```

---

## 六、常用异常

| 异常 | 含义 |
|------|------|
| `UnknownHostException` | 主机名解析失败 |
| `ConnectException` | 连接被拒绝 |
| `SocketTimeoutException` | 连接或读取超时 |
| `BindException` | 端口已被占用 |
| `IOException` | 通用 I/O 错误 |
| `MalformedURLException` | URL 格式错误 |
| `ProtocolException` | HTTP 协议错误 |
