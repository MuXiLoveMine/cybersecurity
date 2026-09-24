/*
 * ============================================================
 * 文件名：port_scanner.cpp
 * 功能描述：TCP 端口扫描器（Winsock 实现）
 * 作者：网络安全学习笔记
 * 日期：2026-09-10
 * ============================================================
 *
 * 【使用说明】
 * 1. 编译方式（Windows + MinGW）：
 *    g++ port_scanner.cpp -o port_scanner.exe -lws2_32
 * 2. 编译方式（Visual Studio）：
 *    cl port_scanner.cpp ws2_32.lib
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
 *   使用 Winsock2 的 connect() 函数尝试建立 TCP 连接，
 *   通过设置非阻塞模式和 select() 来实现超时控制。
 *   依次扫描指定范围内的每个端口，判断端口是否开放。
 *
 * 【免责声明】
 *   本工具仅供网络安全学习和授权测试使用。
 *   禁止对未授权的目标进行端口扫描，违者后果自负。
 *   使用本工具请遵守当地法律法规。
 * ============================================================
 */

// 引入必要的头文件
#include <iostream>        // 标准输入输出
#include <string>          // 字符串处理
#include <vector>          // 动态数组
#include <winsock2.h>      // Winsock2 网络编程
#include <ws2tcpip.h>      // TCP/IP 协议相关
#include <algorithm>       // 排序算法

// 告诉链接器链接 ws2_32.lib 库
#pragma comment(lib, "ws2_32.lib")

// 使用标准命名空间，简化代码
using namespace std;

// 常见端口服务名称映射表
// 用于在扫描结果中显示对应服务名
struct PortService {
    int port;          // 端口号
    const char* name;  // 服务名称
};

// 常见端口及其服务名称
PortService commonPorts[] = {
    {21, "FTP"},          // 文件传输协议
    {22, "SSH"},          // 安全外壳协议
    {23, "Telnet"},       // 远程登录
    {25, "SMTP"},         // 简单邮件传输协议
    {53, "DNS"},          // 域名系统
    {80, "HTTP"},         // 超文本传输协议
    {110, "POP3"},        // 邮局协议第3版
    {135, "MSRPC"},       // Microsoft RPC
    {139, "NetBIOS"},     // 网络基本输入输出系统
    {143, "IMAP"},        // 互联网消息访问协议
    {443, "HTTPS"},       // 安全超文本传输协议
    {445, "SMB"},         // 服务器消息块
    {465, "SMTPS"},       // SMTP over SSL
    {993, "IMAPS"},       // IMAP over SSL
    {995, "POP3S"},       // POP3 over SSL
    {1080, "SOCKS"},      // SOCKS 代理
    {1433, "MSSQL"},      // Microsoft SQL Server
    {1521, "Oracle"},     // Oracle 数据库
    {3306, "MySQL"},      // MySQL 数据库
    {3389, "RDP"},        // 远程桌面协议
    {5432, "PostgreSQL"}, // PostgreSQL 数据库
    {5900, "VNC"},        // 虚拟网络计算
    {6379, "Redis"},      // Redis 数据库
    {8080, "HTTP-Proxy"}, // HTTP 代理
    {8443, "HTTPS-Alt"},  // 备用 HTTPS
    {27017, "MongoDB"},   // MongoDB 数据库
    {0, NULL}             // 结束标记
};

// 获取端口对应的服务名称
// 参数：port - 端口号
// 返回：服务名称字符串，未知端口返回 "unknown"
string getServiceName(int port) {
    for (int i = 0; commonPorts[i].name != NULL; i++) {
        if (commonPorts[i].port == port) {
            return commonPorts[i].name;
        }
    }
    return "unknown";
}

// 扫描单个端口
// 参数：
//   host - 目标主机地址
//   port - 端口号
//   timeoutMs - 超时时间（毫秒）
// 返回：true 表示端口开放，false 表示关闭或过滤
bool scanPort(const char* host, int port, int timeoutMs) {
    // 创建 TCP 套接字
    SOCKET sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (sock == INVALID_SOCKET) {
        return false;
    }

    // 设置套接字为非阻塞模式
    // 非阻塞模式下 connect() 会立即返回，便于实现超时控制
    u_long mode = 1;  // 1 = 非阻塞，0 = 阻塞
    if (ioctlsocket(sock, FIONBIO, &mode) == SOCKET_ERROR) {
        closesocket(sock);
        return false;
    }

    // 设置目标地址结构
    sockaddr_in serverAddr;
    serverAddr.sin_family = AF_INET;           // IPv4 协议
    serverAddr.sin_port = htons(port);         // 端口号（转换为网络字节序）
    inet_pton(AF_INET, host, &serverAddr.sin_addr);  // IP 地址转换

    // 尝试连接
    int connectResult = connect(sock, (sockaddr*)&serverAddr, sizeof(serverAddr));

    if (connectResult == 0) {
        // 立即连接成功（通常是本地端口）
        closesocket(sock);
        return true;
    }

    // 检查是否是 WSAEWOULDBLOCK 错误（非阻塞模式下的正常现象）
    if (WSAGetLastError() != WSAEWOULDBLOCK) {
        closesocket(sock);
        return false;
    }

    // 使用 select() 等待连接完成，实现超时控制
    fd_set writeSet;       // 可写集合（连接成功时套接字变为可写）
    FD_ZERO(&writeSet);    // 清空集合
    FD_SET(sock, &writeSet);  // 将套接字加入集合

    // 设置超时时间
    timeval tv;
    tv.tv_sec = timeoutMs / 1000;          // 秒
    tv.tv_usec = (timeoutMs % 1000) * 1000; // 微秒

    // 等待套接字变为可写（连接完成）
    int selectResult = select(0, NULL, &writeSet, NULL, &tv);

    if (selectResult <= 0) {
        // 超时或错误
        closesocket(sock);
        return false;
    }

    // 检查套接字是否有错误
    // 即使 select 返回可写，也可能是连接失败
    int optval;
    int optlen = sizeof(optval);
    int optResult = getsockopt(sock, SOL_SOCKET, SO_ERROR, (char*)&optval, &optlen);

    closesocket(sock);

    if (optResult == SOCKET_ERROR || optval != 0) {
        return false;  // 连接失败
    }

    return true;  // 端口开放
}

int main(int argc, char* argv[]) {
    // ===================== 参数解析 =====================
    // 默认参数值
    string host = "127.0.0.1";  // 目标主机
    int startPort = 1;          // 起始端口
    int endPort = 1024;         // 结束端口
    int timeoutMs = 500;        // 超时时间（毫秒）

    // 解析命令行参数
    if (argc >= 2) {
        host = argv[1];
    }
    if (argc >= 3) {
        startPort = atoi(argv[2]);
    }
    if (argc >= 4) {
        endPort = atoi(argv[3]);
    }
    if (argc >= 5) {
        timeoutMs = atoi(argv[4]);
    }

    // 参数合法性校验
    if (startPort < 1 || startPort > 65535) {
        cerr << "[错误] 起始端口必须在 1-65535 之间" << endl;
        return 1;
    }
    if (endPort < 1 || endPort > 65535) {
        cerr << "[错误] 结束端口必须在 1-65535 之间" << endl;
        return 1;
    }
    if (startPort > endPort) {
        cerr << "[错误] 起始端口不能大于结束端口" << endl;
        return 1;
    }

    // ===================== 初始化 Winsock =====================
    WSADATA wsaData;
    // 请求使用 Winsock 2.2 版本
    int wsaResult = WSAStartup(MAKEWORD(2, 2), &wsaData);
    if (wsaResult != 0) {
        cerr << "[错误] Winsock 初始化失败，错误码: " << wsaResult << endl;
        return 1;
    }

    // ===================== 打印扫描信息 =====================
    cout << "========================================" << endl;
    cout << "    TCP 端口扫描器（C++ Winsock 版）" << endl;
    cout << "========================================" << endl;
    cout << "目标主机: " << host << endl;
    cout << "端口范围: " << startPort << " - " << endPort << endl;
    cout << "超时时间: " << timeoutMs << " 毫秒" << endl;
    cout << "========================================" << endl;
    cout << "[*] 正在扫描，请稍候..." << endl;
    cout << "----------------------------------------" << endl;

    // ===================== 执行端口扫描 =====================
    vector<int> openPorts;    // 开放端口列表
    vector<int> closedPorts;  // 关闭端口列表

    int totalPorts = endPort - startPort + 1;
    int scanned = 0;

    for (int port = startPort; port <= endPort; port++) {
        bool isOpen = scanPort(host.c_str(), port, timeoutMs);
        scanned++;

        if (isOpen) {
            openPorts.push_back(port);
            string service = getServiceName(port);
            cout << "  [开放] 端口 " << port << "/tcp - " << service << endl;
        } else {
            closedPorts.push_back(port);
        }

        // 每扫描 100 个端口显示一次进度
        if (scanned % 100 == 0) {
            cout << "  ... 进度: " << scanned << "/" << totalPorts << endl;
        }
    }

    // 对开放端口排序（按顺序扫描的，其实已经有序了，但保留一下习惯）
    sort(openPorts.begin(), openPorts.end());

    // ===================== 输出扫描结果 =====================
    cout << "----------------------------------------" << endl;
    cout << endl;
    cout << "========================================" << endl;
    cout << "            扫描结果" << endl;
    cout << "========================================" << endl;
    cout << "扫描端口总数: " << totalPorts << endl;
    cout << "开放端口数量: " << openPorts.size() << endl;
    cout << "关闭/过滤端口数量: " << closedPorts.size() << endl;
    cout << "----------------------------------------" << endl;

    if (openPorts.size() > 0) {
        cout << endl << "[开放端口列表]" << endl;
        cout << "端口\t状态\t服务" << endl;
        cout << "----------------------------------------" << endl;
        for (size_t i = 0; i < openPorts.size(); i++) {
            int port = openPorts[i];
            string service = getServiceName(port);
            cout << port << "\topen\t" << service << endl;
        }
    } else {
        cout << endl << "[!] 未发现开放端口" << endl;
    }

    cout << endl;
    cout << "========================================" << endl;
    cout << "            扫描完成" << endl;
    cout << "========================================" << endl;

    // ===================== 清理 Winsock =====================
    WSACleanup();

    return 0;
}
