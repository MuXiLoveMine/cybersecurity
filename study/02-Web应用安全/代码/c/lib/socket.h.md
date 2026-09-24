# socket.h - C 网络编程

> C 标准库头文件（Unix/Linux），提供套接字网络编程接口。

---

## 一、引入

```c
#include <sys/socket.h>      // 核心套接字函数
#include <netinet/in.h>      // sockaddr_in, IPPROTO_*
#include <arpa/inet.h>       // inet_addr, inet_ntoa
#include <netdb.h>           // gethostbyname, getaddrinfo
#include <unistd.h>          // close, read, write
#include <errno.h>           // 错误码
```

---

## 二、基本套接字操作

### 2.1 创建套接字

```c
// socket - 创建套接字
int socket(int domain, int type, int protocol);

// IPv4 TCP 套接字
int sockfd = socket(AF_INET, SOCK_STREAM, 0);

// IPv4 UDP 套接字
int sockfd = socket(AF_INET, SOCK_DGRAM, 0);

// IPv6 TCP 套接字
int sockfd = socket(AF_INET6, SOCK_STREAM, 0);

// 原始套接字（需要 root 权限）
int sockfd = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP);

// 错误处理
if (sockfd < 0) {
    perror("socket");
    exit(1);
}
```

**domain（协议族）：**
| 值 | 含义 |
|---|------|
| `AF_INET` | IPv4 |
| `AF_INET6` | IPv6 |
| `AF_UNIX` / `AF_LOCAL` | 本地套接字 |
| `AF_PACKET` | 链路层原始套接字（Linux） |

**type（套接字类型）：**
| 值 | 含义 |
|---|------|
| `SOCK_STREAM` | TCP（可靠、面向连接、字节流） |
| `SOCK_DGRAM` | UDP（不可靠、数据报） |
| `SOCK_RAW` | 原始套接字 |

### 2.2 地址结构

```c
// IPv4 地址结构
struct sockaddr_in {
    short            sin_family;   // AF_INET
    unsigned short   sin_port;     // 端口号（网络字节序）
    struct in_addr   sin_addr;     // IP 地址
    char             sin_zero[8];  // 填充
};

struct in_addr {
    unsigned long s_addr;  // IP 地址（网络字节序）
};

// IPv6 地址结构
struct sockaddr_in6 {
    sa_family_t     sin6_family;   // AF_INET6
    in_port_t       sin6_port;     // 端口号
    uint32_t        sin6_flowinfo; // 流信息
    struct in6_addr sin6_addr;     // IPv6 地址
    uint32_t        sin6_scope_id; // 范围 ID
};

// 通用地址结构（用于函数参数）
struct sockaddr {
    unsigned short sa_family;
    char           sa_data[108];
};
```

### 2.3 字节序转换

```c
// 主机字节序 -> 网络字节序（大端）
uint16_t htons(uint16_t hostshort);  // 16 位（端口号）
uint32_t htonl(uint32_t hostlong);   // 32 位（IP 地址）

// 网络字节序 -> 主机字节序
uint16_t ntohs(uint16_t netshort);
uint32_t ntohl(uint32_t netlong);

// 示例
struct sockaddr_in addr;
addr.sin_family = AF_INET;
addr.sin_port = htons(8080);                  // 端口 8080
addr.sin_addr.s_addr = htonl(INADDR_ANY);    // 任意地址
```

### 2.4 IP 地址转换

```c
// 点分十进制 -> 网络字节序（旧函数，不推荐）
unsigned long inet_addr(const char *cp);

addr.sin_addr.s_addr = inet_addr("192.168.1.1");

// 网络字节序 -> 点分十进制（旧函数，不可重入）
char *inet_ntoa(struct in_addr in);

printf("%s\n", inet_ntoa(addr.sin_addr));

// ===== 推荐使用新函数（支持 IPv4/IPv6）=====

// 字符串 -> 二进制
int inet_pton(int af, const char *src, void *dst);

inet_pton(AF_INET, "192.168.1.1", &addr.sin_addr);
inet_pton(AF_INET6, "::1", &addr6.sin6_addr);

// 二进制 -> 字符串
const char *inet_ntop(int af, const void *src, char *dst, socklen_t size);

char ip_str[INET_ADDRSTRLEN];
inet_ntop(AF_INET, &addr.sin_addr, ip_str, sizeof(ip_str));

char ip6_str[INET6_ADDRSTRLEN];
inet_ntop(AF_INET6, &addr6.sin6_addr, ip6_str, sizeof(ip6_str));
```

---

## 三、TCP 编程

### 3.1 TCP 服务器

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>

#define PORT 8080
#define BUFFER_SIZE 1024

int main() {
    int server_fd, new_socket;
    struct sockaddr_in address;
    int addrlen = sizeof(address);
    char buffer[BUFFER_SIZE] = {0};
    
    // 1. 创建套接字
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        perror("socket failed");
        exit(EXIT_FAILURE);
    }
    
    // 2. 设置地址重用（避免 TIME_WAIT 问题）
    int opt = 1;
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &opt, sizeof(opt))) {
        perror("setsockopt");
        exit(EXIT_FAILURE);
    }
    
    // 3. 绑定地址
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);
    
    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        perror("bind failed");
        exit(EXIT_FAILURE);
    }
    
    // 4. 监听
    if (listen(server_fd, 3) < 0) {
        perror("listen");
        exit(EXIT_FAILURE);
    }
    
    printf("服务器监听端口 %d...\n", PORT);
    
    // 5. 接受连接
    while (1) {
        if ((new_socket = accept(server_fd, (struct sockaddr *)&address, (socklen_t*)&addrlen)) < 0) {
            perror("accept");
            continue;
        }
        
        printf("新连接: %s:%d\n", 
               inet_ntoa(address.sin_addr), 
               ntohs(address.sin_port));
        
        // 读取数据
        int valread = read(new_socket, buffer, BUFFER_SIZE);
        printf("收到: %s\n", buffer);
        
        // 发送响应
        char *response = "HTTP/1.1 200 OK\r\nContent-Length: 13\r\n\r\nHello World!";
        send(new_socket, response, strlen(response), 0);
        
        close(new_socket);
    }
    
    return 0;
}
```

### 3.2 TCP 客户端

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define PORT 8080
#define BUFFER_SIZE 1024

int main() {
    int sock = 0;
    struct sockaddr_in serv_addr;
    char buffer[BUFFER_SIZE] = {0};
    
    // 1. 创建套接字
    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        perror("socket");
        exit(EXIT_FAILURE);
    }
    
    // 2. 设置服务器地址
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(PORT);
    
    if (inet_pton(AF_INET, "127.0.0.1", &serv_addr.sin_addr) <= 0) {
        perror("invalid address");
        exit(EXIT_FAILURE);
    }
    
    // 3. 连接服务器
    if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {
        perror("connect");
        exit(EXIT_FAILURE);
    }
    
    // 4. 发送数据
    char *message = "Hello from client";
    send(sock, message, strlen(message), 0);
    printf("消息已发送\n");
    
    // 5. 接收响应
    int valread = read(sock, buffer, BUFFER_SIZE);
    printf("收到: %s\n", buffer);
    
    close(sock);
    return 0;
}
```

### 3.3 套接字选项

```c
// SO_REUSEADDR - 地址重用（服务器重启时避免 "Address already in use"）
int opt = 1;
setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

// SO_REUSEPORT - 端口重用（多进程/线程绑定同一端口）
int opt = 1;
setsockopt(sockfd, SOL_SOCKET, SO_REUSEPORT, &opt, sizeof(opt));

// SO_SNDBUF / SO_RCVBUF - 发送/接收缓冲区大小
int buf_size = 65536;
setsockopt(sockfd, SOL_SOCKET, SO_SNDBUF, &buf_size, sizeof(buf_size));
setsockopt(sockfd, SOL_SOCKET, SO_RCVBUF, &buf_size, sizeof(buf_size));

// SO_TIMEOUT - 超时（接收发送超时）
struct timeval timeout;
timeout.tv_sec = 5;    // 5 秒
timeout.tv_usec = 0;
setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));
setsockopt(sockfd, SOL_SOCKET, SO_SNDTIMEO, &timeout, sizeof(timeout));

// SO_KEEPALIVE - 保持连接检测
int opt = 1;
setsockopt(sockfd, SOL_SOCKET, SO_KEEPALIVE, &opt, sizeof(opt));

// TCP_NODELAY - 禁用 Nagle 算法（小包立即发送）
int opt = 1;
setsockopt(sockfd, IPPROTO_TCP, TCP_NODELAY, &opt, sizeof(opt));

// 获取选项值
int optval;
socklen_t optlen = sizeof(optval);
getsockopt(sockfd, SOL_SOCKET, SO_SNDBUF, &optval, &optlen);
```

---

## 四、UDP 编程

### 4.1 UDP 服务器

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>

#define PORT 8080
#define BUFFER_SIZE 1024

int main() {
    int sockfd;
    char buffer[BUFFER_SIZE];
    struct sockaddr_in servaddr, cliaddr;
    
    // 创建 UDP 套接字
    if ((sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        perror("socket");
        exit(EXIT_FAILURE);
    }
    
    // 绑定
    memset(&servaddr, 0, sizeof(servaddr));
    memset(&cliaddr, 0, sizeof(cliaddr));
    
    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = INADDR_ANY;
    servaddr.sin_port = htons(PORT);
    
    if (bind(sockfd, (const struct sockaddr *)&servaddr, sizeof(servaddr)) < 0) {
        perror("bind");
        exit(EXIT_FAILURE);
    }
    
    printf("UDP 服务器监听端口 %d...\n", PORT);
    
    while (1) {
        socklen_t len = sizeof(cliaddr);
        int n = recvfrom(sockfd, buffer, BUFFER_SIZE, 0,
                         (struct sockaddr *)&cliaddr, &len);
        buffer[n] = '\0';
        
        printf("收到来自 %s:%d 的消息: %s\n",
               inet_ntoa(cliaddr.sin_addr),
               ntohs(cliaddr.sin_port),
               buffer);
        
        // 回送响应
        char *response = "Message received";
        sendto(sockfd, response, strlen(response), 0,
               (const struct sockaddr *)&cliaddr, len);
    }
    
    close(sockfd);
    return 0;
}
```

### 4.2 UDP 客户端

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define PORT 8080
#define BUFFER_SIZE 1024

int main() {
    int sockfd;
    char buffer[BUFFER_SIZE];
    struct sockaddr_in servaddr;
    
    // 创建套接字
    if ((sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        perror("socket");
        exit(EXIT_FAILURE);
    }
    
    // 设置服务器地址
    memset(&servaddr, 0, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_port = htons(PORT);
    inet_pton(AF_INET, "127.0.0.1", &servaddr.sin_addr);
    
    // 发送数据
    char *message = "Hello from UDP client";
    sendto(sockfd, message, strlen(message), 0,
           (const struct sockaddr *)&servaddr, sizeof(servaddr));
    printf("消息已发送\n");
    
    // 接收响应
    socklen_t len = sizeof(servaddr);
    int n = recvfrom(sockfd, buffer, BUFFER_SIZE, 0,
                     (struct sockaddr *)&servaddr, &len);
    buffer[n] = '\0';
    printf("收到: %s\n", buffer);
    
    close(sockfd);
    return 0;
}
```

---

## 五、域名解析

### 5.1 getaddrinfo（推荐）

```c
#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int resolve_hostname(const char *hostname, const char *port) {
    struct addrinfo hints, *res, *p;
    int status;
    char ipstr[INET6_ADDRSTRLEN];
    
    memset(&hints, 0, sizeof hints);
    hints.ai_family = AF_UNSPEC;      // IPv4 或 IPv6
    hints.ai_socktype = SOCK_STREAM;  // TCP
    
    if ((status = getaddrinfo(hostname, port, &hints, &res)) != 0) {
        fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(status));
        return -1;
    }
    
    printf("%s 的 IP 地址:\n", hostname);
    
    for (p = res; p != NULL; p = p->ai_next) {
        void *addr;
        char *ipver;
        
        if (p->ai_family == AF_INET) {
            struct sockaddr_in *ipv4 = (struct sockaddr_in *)p->ai_addr;
            addr = &(ipv4->sin_addr);
            ipver = "IPv4";
        } else {
            struct sockaddr_in6 *ipv6 = (struct sockaddr_in6 *)p->ai_addr;
            addr = &(ipv6->sin6_addr);
            ipver = "IPv6";
        }
        
        inet_ntop(p->ai_family, addr, ipstr, sizeof ipstr);
        printf("  %s: %s\n", ipver, ipstr);
    }
    
    freeaddrinfo(res);
    return 0;
}
```

### 5.2 旧函数（不推荐）

```c
#include <netdb.h>

// gethostbyname - 域名解析（不可重入，不推荐）
struct hostent *gethostbyname(const char *name);

struct hostent *he = gethostbyname("www.example.com");
if (he) {
    printf("官方名称: %s\n", he->h_name);
    // IP 地址列表在 he->h_addr_list
    char **addr_list = he->h_addr_list;
    for (int i = 0; addr_list[i] != NULL; i++) {
        printf("%s\n", inet_ntoa(*(struct in_addr *)addr_list[i]));
    }
}

// getservbyname - 服务名转端口号
struct servent *getservbyname(const char *name, const char *proto);

struct servent *se = getservbyname("http", "tcp");
if (se) {
    printf("http 端口: %d\n", ntohs(se->s_port));  // 80
}
```

---

## 六、安全相关内容

### 6.1 常见网络安全问题

```c
/*
    C 网络编程常见安全问题：
    
    1. 缓冲区溢出
       - read/recv 读取的数据超过缓冲区大小
       - 未检查数据长度直接操作
       
    2. 格式化字符串漏洞
       - printf(client_data) 直接输出客户端数据
       
    3. 整数溢出
       - 长度计算溢出导致分配过小的缓冲区
       
    4. 竞争条件
       - 多线程/多进程访问共享资源不同步
       
    5. 输入验证不足
       - 未验证客户端发送的数据格式、长度
       
    6. 信息泄露
       - 错误信息包含敏感数据
       - 返回过多的系统信息
*/

// 安全的读取（避免缓冲区溢出）
#define BUF_SIZE 1024

void safe_read(int sockfd) {
    char buf[BUF_SIZE];
    ssize_t n = recv(sockfd, buf, BUF_SIZE - 1, 0);  // 留一位给 '\0'
    if (n > 0) {
        buf[n] = '\0';  // ✅ 手动加结束符
        // 处理 buf...
    }
}
```

### 6.2 端口扫描器实现

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/select.h>
#include <sys/time.h>

int scan_port(const char *ip, int port, int timeout_sec) {
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) return -1;
    
    // 设置非阻塞模式
    int flags = fcntl(sockfd, F_GETFL, 0);
    fcntl(sockfd, F_SETFL, flags | O_NONBLOCK);
    
    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);
    inet_pton(AF_INET, ip, &addr.sin_addr);
    
    // 非阻塞连接
    int ret = connect(sockfd, (struct sockaddr *)&addr, sizeof(addr));
    
    if (ret < 0 && errno != EINPROGRESS) {
        close(sockfd);
        return 0;
    }
    
    // 使用 select 等待连接完成
    fd_set wfds;
    FD_ZERO(&wfds);
    FD_SET(sockfd, &wfds);
    
    struct timeval tv;
    tv.tv_sec = timeout_sec;
    tv.tv_usec = 0;
    
    ret = select(sockfd + 1, NULL, &wfds, NULL, &tv);
    
    if (ret > 0) {
        int error = 0;
        socklen_t len = sizeof(error);
        getsockopt(sockfd, SOL_SOCKET, SO_ERROR, &error, &len);
        
        close(sockfd);
        return (error == 0) ? 1 : 0;
    }
    
    close(sockfd);
    return 0;  // 超时或错误
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("用法: %s <IP> [起始端口] [结束端口]\n", argv[0]);
        return 1;
    }
    
    const char *ip = argv[1];
    int start = argc > 2 ? atoi(argv[2]) : 1;
    int end = argc > 3 ? atoi(argv[3]) : 1000;
    
    printf("扫描 %s 端口 %d-%d...\n", ip, start, end);
    
    for (int port = start; port <= end; port++) {
        if (scan_port(ip, port, 1)) {
            printf("  端口 %d 开放\n", port);
        }
    }
    
    return 0;
}
```

---

## 七、常见错误码

| errno 值 | 含义 |
|---------|------|
| `EACCES` | 权限不足 |
| `EADDRINUSE` | 地址已被占用 |
| `ECONNREFUSED` | 连接被拒绝 |
| `ETIMEDOUT` | 连接超时 |
| `EWOULDBLOCK` / `EAGAIN` | 非阻塞操作暂时无法完成 |
| `EINPROGRESS` | 非阻塞连接进行中 |
| `ENETUNREACH` | 网络不可达 |
| `EHOSTUNREACH` | 主机不可达 |
| `ECONNRESET` | 连接被重置 |
