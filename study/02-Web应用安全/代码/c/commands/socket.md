# socket

> **分类**：网络编程
> **说明**：创建套接字，用于网络通信
> **头文件**：`<sys/socket.h (Linux) / winsock2.h (Windows)>`

---

## 语法

```c
int socket(int domain, int type, int protocol);
```

## 参数说明

- domain: AF_INET (IPv4), AF_INET6 (IPv6)
- type: SOCK_STREAM (TCP), SOCK_DGRAM (UDP)
- protocol: 0 (默认协议)

## 示例代码

```c
// TCP 客户端示例
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>

int main() {
    // 创建 socket
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        perror("socket");
        return 1;
    }

    // 设置服务器地址
    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(80);  // 端口80

    // 解析主机名
    struct hostent *server = gethostbyname("example.com");
    if (server == NULL) {
        herror("gethostbyname");
        return 1;
    }
    memcpy(&server_addr.sin_addr.s_addr, server->h_addr, server->h_length);

    // 连接
    if (connect(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("connect");
        return 1;
    }

    // 发送数据
    const char *request = "GET / HTTP/1.0\r\n\r\n";
    send(sockfd, request, strlen(request), 0);

    // 接收响应
    char buffer[4096];
    ssize_t n;
    while ((n = recv(sockfd, buffer, sizeof(buffer)-1, 0)) > 0) {
        buffer[n] = '\0';
        printf("%s", buffer);
    }

    close(sockfd);
    return 0;
}

// TCP 服务器示例（伪代码结构）
/*
int server_fd = socket(AF_INET, SOCK_STREAM, 0);
// 设置地址复用
int opt = 1;
setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
// bind
bind(server_fd, (struct sockaddr *)&addr, sizeof(addr));
// listen
listen(server_fd, 5);
// accept
int client_fd = accept(server_fd, (struct sockaddr *)&client_addr, &len);
// 处理客户端...
close(client_fd);
close(server_fd);
*/
```
