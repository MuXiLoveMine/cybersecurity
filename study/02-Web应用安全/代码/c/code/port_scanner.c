/*
 * ============================================================
 * 文件名：port_scanner.c
 * 功能描述：TCP 端口扫描器（Winsock 实现，C 语言版）
 * 作者：网络安全学习笔记
 * 日期：2026-09-21
 * ============================================================
 *
 * 【使用说明】
 * 1. 编译方式（Windows + MinGW）：
 *    gcc port_scanner.c -o port_scanner.exe -lws2_32
 * 2. 编译方式（Linux）：
 *    gcc port_scanner.c -o port_scanner
 * 3. 命令行参数：
 *    参数1：目标主机地址（默认：127.0.0.1）
 *    参数2：起始端口（默认：1）
 *    参数3：结束端口（默认：1024）
 *    参数4：超时时间（毫秒，默认：500）
 *
 * 【示例】
 *   port_scanner.exe 192.168.1.1 1 1000 300
 *   port_scanner.exe 127.0.0.1 20 100
 *
 * 【原理说明】
 *   使用 connect() 函数尝试建立 TCP 连接，
 *   通过设置非阻塞模式和 select() 来实现超时控制。
 *   依次扫描指定范围内的每个端口，判断端口是否开放。
 *
 * 【免责声明】
 *   本工具仅供网络安全学习和授权测试使用。
 *   禁止对未授权的目标进行端口扫描，违者后果自负。
 *   使用本工具请遵守当地法律法规。
 * ============================================================
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef _WIN32
    #include <winsock2.h>
    #include <ws2tcpip.h>
    #pragma comment(lib, "ws2_32.lib")
    typedef int socklen_t;
#else
    #include <sys/socket.h>
    #include <netinet/in.h>
    #include <arpa/inet.h>
    #include <unistd.h>
    #include <fcntl.h>
    #include <sys/time.h>
    #include <errno.h>
    #define SOCKET int
    #define INVALID_SOCKET (-1)
    #define SOCKET_ERROR (-1)
    #define closesocket close
#endif

// 常见端口服务名称映射表
typedef struct {
    int port;
    const char *name;
} PortService;

PortService commonPorts[] = {
    {21, "FTP"},
    {22, "SSH"},
    {23, "Telnet"},
    {25, "SMTP"},
    {53, "DNS"},
    {80, "HTTP"},
    {110, "POP3"},
    {135, "MSRPC"},
    {139, "NetBIOS"},
    {143, "IMAP"},
    {443, "HTTPS"},
    {445, "SMB"},
    {465, "SMTPS"},
    {993, "IMAPS"},
    {995, "POP3S"},
    {1080, "SOCKS"},
    {1433, "MSSQL"},
    {1521, "Oracle"},
    {3306, "MySQL"},
    {3389, "RDP"},
    {5432, "PostgreSQL"},
    {5900, "VNC"},
    {6379, "Redis"},
    {8080, "HTTP-Proxy"},
    {8443, "HTTPS-Alt"},
    {27017, "MongoDB"},
    {0, NULL}
};

// 获取端口对应的服务名称
const char *getServiceName(int port) {
    for (int i = 0; commonPorts[i].name != NULL; i++) {
        if (commonPorts[i].port == port) {
            return commonPorts[i].name;
        }
    }
    return "unknown";
}

// 设置套接字为非阻塞模式
int setNonBlocking(SOCKET sock) {
#ifdef _WIN32
    u_long mode = 1;
    return ioctlsocket(sock, FIONBIO, &mode);
#else
    int flags = fcntl(sock, F_GETFL, 0);
    if (flags < 0) return -1;
    return fcntl(sock, F_SETFL, flags | O_NONBLOCK);
#endif
}

// 扫描单个端口
int scanPort(const char *host, int port, int timeoutMs) {
    SOCKET sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (sock == INVALID_SOCKET) {
        return 0;
    }

    // 设置为非阻塞模式
    if (setNonBlocking(sock) == SOCKET_ERROR) {
        closesocket(sock);
        return 0;
    }

    // 设置目标地址
    struct sockaddr_in serverAddr;
    memset(&serverAddr, 0, sizeof(serverAddr));
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(port);
    inet_pton(AF_INET, host, &serverAddr.sin_addr);

    // 尝试连接
    int connectResult = connect(sock, (struct sockaddr *)&serverAddr, sizeof(serverAddr));

    if (connectResult == 0) {
        closesocket(sock);
        return 1;
    }

#ifdef _WIN32
    if (WSAGetLastError() != WSAEWOULDBLOCK) {
        closesocket(sock);
        return 0;
    }
#else
    if (errno != EINPROGRESS) {
        closesocket(sock);
        return 0;
    }
#endif

    // 使用 select 等待连接完成
    fd_set writeSet;
    FD_ZERO(&writeSet);
    FD_SET(sock, &writeSet);

    struct timeval tv;
    tv.tv_sec = timeoutMs / 1000;
    tv.tv_usec = (timeoutMs % 1000) * 1000;

    int selectResult = select((int)sock + 1, NULL, &writeSet, NULL, &tv);

    if (selectResult <= 0) {
        closesocket(sock);
        return 0;
    }

    // 检查套接字是否有错误
    int optval;
    socklen_t optlen = sizeof(optval);
    int optResult = getsockopt(sock, SOL_SOCKET, SO_ERROR, (char *)&optval, &optlen);

    closesocket(sock);

    if (optResult == SOCKET_ERROR || optval != 0) {
        return 0;
    }

    return 1;
}

int main(int argc, char *argv[]) {
    // 默认参数
    const char *host = "127.0.0.1";
    int startPort = 1;
    int endPort = 1024;
    int timeoutMs = 500;

    // 解析命令行参数
    if (argc >= 2) host = argv[1];
    if (argc >= 3) startPort = atoi(argv[2]);
    if (argc >= 4) endPort = atoi(argv[3]);
    if (argc >= 5) timeoutMs = atoi(argv[4]);

    // 参数校验
    if (startPort < 1 || startPort > 65535) {
        fprintf(stderr, "[错误] 起始端口必须在 1-65535 之间\n");
        return 1;
    }
    if (endPort < 1 || endPort > 65535) {
        fprintf(stderr, "[错误] 结束端口必须在 1-65535 之间\n");
        return 1;
    }
    if (startPort > endPort) {
        fprintf(stderr, "[错误] 起始端口不能大于结束端口\n");
        return 1;
    }

    // 初始化 Winsock（Windows 平台）
#ifdef _WIN32
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        fprintf(stderr, "[错误] Winsock 初始化失败\n");
        return 1;
    }
#endif

    // 打印扫描信息
    printf("========================================\n");
    printf("    TCP 端口扫描器（C 语言版）\n");
    printf("========================================\n");
    printf("目标主机: %s\n", host);
    printf("端口范围: %d - %d\n", startPort, endPort);
    printf("超时时间: %d 毫秒\n", timeoutMs);
    printf("========================================\n");
    printf("[*] 正在扫描，请稍候...\n");
    printf("----------------------------------------\n");

    // 执行扫描
    int totalPorts = endPort - startPort + 1;
    int scanned = 0;
    int openCount = 0;
    int openPorts[1024];  // 最多记录 1024 个开放端口

    for (int port = startPort; port <= endPort; port++) {
        int isOpen = scanPort(host, port, timeoutMs);
        scanned++;

        if (isOpen) {
            openPorts[openCount++] = port;
            const char *service = getServiceName(port);
            printf("  [开放] 端口 %d/tcp - %s\n", port, service);
        }

        // 每扫描 100 个端口显示进度
        if (scanned % 100 == 0) {
            printf("  ... 进度: %d/%d\n", scanned, totalPorts);
        }
    }

    // 输出结果
    printf("----------------------------------------\n\n");
    printf("========================================\n");
    printf("            扫描结果\n");
    printf("========================================\n");
    printf("扫描端口总数: %d\n", totalPorts);
    printf("开放端口数量: %d\n", openCount);
    printf("关闭/过滤端口数量: %d\n", totalPorts - openCount);
    printf("----------------------------------------\n");

    if (openCount > 0) {
        printf("\n[开放端口列表]\n");
        printf("端口\t状态\t服务\n");
        printf("----------------------------------------\n");
        for (int i = 0; i < openCount; i++) {
            int port = openPorts[i];
            printf("%d\topen\t%s\n", port, getServiceName(port));
        }
    } else {
        printf("\n[!] 未发现开放端口\n");
    }

    printf("\n========================================\n");
    printf("            扫描完成\n");
    printf("========================================\n");

    // 清理 Winsock
#ifdef _WIN32
    WSACleanup();
#endif

    return 0;
}
