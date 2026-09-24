/*
 * ============================================================
 * 文件名：dir_brute.c
 * 功能描述：目录爆破工具（C 语言版）
 * 作者：网络安全学习笔记
 * 日期：2026-09-21
 * ============================================================
 *
 * 【使用说明】
 * 1. 编译方式（Windows + MinGW）：
 *    gcc dir_brute.c -o dir_brute.exe -lws2_32
 * 2. 编译方式（Linux）：
 *    gcc dir_brute.c -o dir_brute
 * 3. 命令行参数：
 *    参数1：目标 URL（默认：http://127.0.0.1）
 *    参数2：字典文件路径（默认：dir.txt）
 *    参数3：超时时间（秒，默认：5）
 *
 * 【示例】
 *   dir_brute.exe http://192.168.1.1 dir.txt 3
 *   dir_brute.exe http://example.com common.txt
 *
 * 【原理说明】
 *   读取字典文件中的目录名，逐个构造 URL 并发送 HTTP 请求，
 *   根据响应状态码判断目录是否存在。
 *
 * 【免责声明】
 *   本工具仅供网络安全学习和授权测试使用。
 *   禁止对未授权的目标进行目录爆破，违者后果自负。
 *   使用本工具请遵守当地法律法规。
 * ============================================================
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

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
    #include <netdb.h>
    #define SOCKET int
    #define INVALID_SOCKET (-1)
    #define SOCKET_ERROR (-1)
    #define closesocket close
#endif

#define MAX_PATH_LEN 256
#define MAX_HOST_LEN 128
#define BUFFER_SIZE 4096
#define MAX_LINES 10000

// 解析 URL，提取主机和路径
int parseUrl(const char *url, char *host, int *port, char *path) {
    const char *p = url;

    // 跳过 http:// 或 https://
    if (strncmp(url, "http://", 7) == 0) {
        p = url + 7;
        *port = 80;
    } else if (strncmp(url, "https://", 8) == 0) {
        p = url + 8;
        *port = 443;
    } else {
        *port = 80;
    }

    // 提取主机名
    int i = 0;
    while (*p && *p != '/' && *p != ':' && i < MAX_HOST_LEN - 1) {
        host[i++] = *p++;
    }
    host[i] = '\0';

    // 提取端口
    if (*p == ':') {
        p++;
        *port = 0;
        while (isdigit(*p)) {
            *port = *port * 10 + (*p - '0');
            p++;
        }
    }

    // 提取路径
    if (*p == '/') {
        strncpy(path, p, MAX_PATH_LEN - 1);
        path[MAX_PATH_LEN - 1] = '\0';
    } else {
        strcpy(path, "/");
    }

    return 0;
}

// 通过域名解析 IP
int resolveHostname(const char *hostname, char *ip) {
#ifdef _WIN32
    struct hostent *he = gethostbyname(hostname);
    if (he == NULL) return -1;
    struct in_addr **addr_list = (struct in_addr **)he->h_addr_list;
    if (addr_list[0] == NULL) return -1;
    strcpy(ip, inet_ntoa(*addr_list[0]));
    return 0;
#else
    struct hostent *he = gethostbyname(hostname);
    if (he == NULL) return -1;
    struct in_addr **addr_list = (struct in_addr **)he->h_addr_list;
    if (addr_list[0] == NULL) return -1;
    strcpy(ip, inet_ntoa(*addr_list[0]));
    return 0;
#endif
}

// 设置套接字超时
int setSocketTimeout(SOCKET sock, int timeoutSec) {
    struct timeval tv;
    tv.tv_sec = timeoutSec;
    tv.tv_usec = 0;
    setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, (const char *)&tv, sizeof(tv));
    setsockopt(sock, SOL_SOCKET, SO_SNDTIMEO, (const char *)&tv, sizeof(tv));
    return 0;
}

// 发送 HTTP GET 请求，返回状态码
int httpGet(const char *ip, int port, const char *path, int timeoutSec) {
    SOCKET sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (sock == INVALID_SOCKET) return -1;

    setSocketTimeout(sock, timeoutSec);

    struct sockaddr_in serverAddr;
    memset(&serverAddr, 0, sizeof(serverAddr));
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(port);
    inet_pton(AF_INET, ip, &serverAddr.sin_addr);

    if (connect(sock, (struct sockaddr *)&serverAddr, sizeof(serverAddr)) == SOCKET_ERROR) {
        closesocket(sock);
        return -1;
    }

    // 构造 HTTP 请求
    char request[512];
    snprintf(request, sizeof(request),
             "GET %s HTTP/1.1\r\n"
             "Host: %s\r\n"
             "User-Agent: DirBruter/1.0\r\n"
             "Connection: close\r\n\r\n",
             path, ip);

    if (send(sock, request, (int)strlen(request), 0) == SOCKET_ERROR) {
        closesocket(sock);
        return -1;
    }

    // 读取响应
    char buffer[BUFFER_SIZE];
    memset(buffer, 0, sizeof(buffer));
    int totalRead = 0;

    while (totalRead < BUFFER_SIZE - 1) {
        int n = recv(sock, buffer + totalRead, BUFFER_SIZE - 1 - totalRead, 0);
        if (n <= 0) break;
        totalRead += n;
        // 读到响应头就够了
        if (strstr(buffer, "\r\n\r\n") != NULL) break;
    }

    closesocket(sock);

    if (totalRead == 0) return -1;

    // 解析状态码
    // HTTP/1.1 200 OK
    int statusCode = 0;
    if (sscanf(buffer, "HTTP/%*d.%*d %d", &statusCode) == 1) {
        return statusCode;
    }

    return -1;
}

// 读取字典文件
int readDict(const char *filename, char lines[][MAX_PATH_LEN], int maxLines) {
    FILE *fp = fopen(filename, "r");
    if (fp == NULL) {
        return -1;
    }

    int count = 0;
    char line[MAX_PATH_LEN];

    while (fgets(line, sizeof(line), fp) != NULL && count < maxLines) {
        // 去掉换行符
        int len = (int)strlen(line);
        while (len > 0 && (line[len - 1] == '\n' || line[len - 1] == '\r')) {
            line[len - 1] = '\0';
            len--;
        }

        // 跳过空行和注释
        if (len == 0 || line[0] == '#') continue;

        strncpy(lines[count], line, MAX_PATH_LEN - 1);
        lines[count][MAX_PATH_LEN - 1] = '\0';
        count++;
    }

    fclose(fp);
    return count;
}

// 检查路径是否以 / 开头
void formatPath(char *path) {
    if (path[0] != '/') {
        // 向前移动一个字符，插入 /
        memmove(path + 1, path, strlen(path) + 1);
        path[0] = '/';
    }
}

int main(int argc, char *argv[]) {
    // 默认参数
    const char *url = "http://127.0.0.1";
    const char *dictFile = "dir.txt";
    int timeoutSec = 5;

    // 解析命令行参数
    if (argc >= 2) url = argv[1];
    if (argc >= 3) dictFile = argv[2];
    if (argc >= 4) timeoutSec = atoi(argv[3]);

    // 初始化 Winsock
#ifdef _WIN32
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        fprintf(stderr, "[错误] Winsock 初始化失败\n");
        return 1;
    }
#endif

    // 解析 URL
    char host[MAX_HOST_LEN];
    int port;
    char basePath[MAX_PATH_LEN];
    parseUrl(url, host, &port, basePath);

    // 解析 IP
    char ip[64];
    if (resolveHostname(host, ip) != 0) {
        fprintf(stderr, "[错误] 无法解析主机名: %s\n", host);
#ifdef _WIN32
        WSACleanup();
#endif
        return 1;
    }

    // 读取字典
    static char dictLines[MAX_LINES][MAX_PATH_LEN];
    int dictCount = readDict(dictFile, dictLines, MAX_LINES);
    if (dictCount < 0) {
        fprintf(stderr, "[错误] 无法读取字典文件: %s\n", dictFile);
        fprintf(stderr, "请确保字典文件存在，或创建一个包含目录名的文本文件\n");
#ifdef _WIN32
        WSACleanup();
#endif
        return 1;
    }

    // 打印信息
    printf("========================================\n");
    printf("       目录爆破工具（C 语言版）\n");
    printf("========================================\n");
    printf("目标 URL: %s\n", url);
    printf("目标 IP: %s:%d\n", ip, port);
    printf("字典文件: %s\n", dictFile);
    printf("字典数量: %d 条\n", dictCount);
    printf("超时时间: %d 秒\n", timeoutSec);
    printf("========================================\n");
    printf("[*] 开始爆破...\n");
    printf("----------------------------------------\n");

    // 执行爆破
    int foundCount = 0;
    int total = dictCount;

    for (int i = 0; i < dictCount; i++) {
        char fullPath[MAX_PATH_LEN * 2];
        char dirPath[MAX_PATH_LEN];
        strncpy(dirPath, dictLines[i], MAX_PATH_LEN - 1);
        dirPath[MAX_PATH_LEN - 1] = '\0';
        formatPath(dirPath);

        // 拼接基础路径和目录路径
        if (strcmp(basePath, "/") == 0) {
            strncpy(fullPath, dirPath, sizeof(fullPath) - 1);
        } else {
            snprintf(fullPath, sizeof(fullPath), "%s%s", basePath, dirPath + 1);
        }

        int status = httpGet(ip, port, fullPath, timeoutSec);

        // 显示进度
        if ((i + 1) % 100 == 0) {
            printf("  ... 进度: %d/%d\n", i + 1, total);
        }

        // 判断结果
        if (status > 0 && status != 404) {
            foundCount++;
            const char *color = "";
            if (status == 200) {
                printf("  [%d] %s  (存在)\n", status, fullPath);
            } else if (status == 301 || status == 302) {
                printf("  [%d] %s  (重定向)\n", status, fullPath);
            } else if (status == 403) {
                printf("  [%d] %s  (禁止访问)\n", status, fullPath);
            } else {
                printf("  [%d] %s\n", status, fullPath);
            }
        }
    }

    // 输出结果
    printf("----------------------------------------\n\n");
    printf("========================================\n");
    printf("            爆破结果\n");
    printf("========================================\n");
    printf("请求总数: %d\n", total);
    printf("发现目录: %d\n", foundCount);
    printf("========================================\n");
    printf("            爆破完成\n");
    printf("========================================\n");

#ifdef _WIN32
    WSACleanup();
#endif

    return 0;
}
