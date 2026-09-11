/*
 * ============================================================
 * 文件名：simple_http_client.cpp
 * 功能描述：简易 HTTP 客户端（Winsock 实现）
 * 作者：网络安全学习笔记
 * 日期：2026-09-10
 * ============================================================
 *
 * 【使用说明】
 * 1. 编译方式（Windows + MinGW）：
 *    g++ simple_http_client.cpp -o simple_http_client.exe -lws2_32
 * 2. 编译方式（Visual Studio）：
 *    cl simple_http_client.cpp ws2_32.lib
 * 3. 命令行参数：
 *    参数1：URL（如 http://example.com/index.html）
 *    参数2：请求方法（GET 或 POST，默认 GET）
 *    参数3：POST 数据（仅 POST 方法时使用）
 *
 * 【示例】
 *   simple_http_client.exe http://example.com
 *   simple_http_client.exe http://example.com/form POST "username=admin&password=123"
 *   simple_http_client.exe http://127.0.0.1:8080/test GET
 *
 * 【功能说明】
 *   1. 支持 HTTP GET 和 POST 请求
 *   2. 解析 URL，提取主机、端口、路径
 *   3. 发送原始 HTTP 请求
 *   4. 接收并显示响应头和响应体
 *   5. 显示响应状态码和 Content-Length
 *
 * 【免责声明】
 *   本工具仅供网络安全学习使用。
 *   通过手动实现 HTTP 协议理解 Web 通信原理。
 *   使用本工具请遵守当地法律法规。
 * ============================================================
 */

// 引入必要的头文件
#include <iostream>        // 标准输入输出
#include <string>          // 字符串处理
#include <winsock2.h>      // Winsock2 网络编程
#include <ws2tcpip.h>      // TCP/IP 协议相关

// 链接 Winsock 库
#pragma comment(lib, "ws2_32.lib")

using namespace std;

// URL 解析结果结构体
struct UrlInfo {
    string host;      // 主机名/IP
    int port;         // 端口号
    string path;      // 请求路径
    string protocol;  // 协议（http/https）
};

// HttpResponse 结构体，存储 HTTP 响应信息
struct HttpResponse {
    int statusCode;       // 状态码
    string statusText;    // 状态描述
    string headers;       // 响应头
    string body;          // 响应体
    int contentLength;    // 内容长度
};

// 解析 URL 字符串
// 参数：url - 完整的 URL 字符串
// 返回：UrlInfo 结构体，包含解析后的主机、端口、路径等信息
UrlInfo parseUrl(const string& url) {
    UrlInfo info;
    info.port = 80;          // 默认 HTTP 端口
    info.protocol = "http";  // 默认协议
    info.path = "/";         // 默认路径

    size_t pos = 0;

    // 1. 提取协议
    size_t protoEnd = url.find("://");
    if (protoEnd != string::npos) {
        info.protocol = url.substr(0, protoEnd);
        pos = protoEnd + 3;  // 跳过 "://"
    }

    // 2. 提取主机和端口
    size_t pathStart = url.find('/', pos);
    string hostPort;

    if (pathStart != string::npos) {
        hostPort = url.substr(pos, pathStart - pos);
        info.path = url.substr(pathStart);  // 包含开头的 /
    } else {
        hostPort = url.substr(pos);
        info.path = "/";
    }

    // 3. 分离主机和端口
    size_t colonPos = hostPort.find(':');
    if (colonPos != string::npos) {
        info.host = hostPort.substr(0, colonPos);
        info.port = atoi(hostPort.substr(colonPos + 1).c_str());
    } else {
        info.host = hostPort;
        // 根据协议设置默认端口
        if (info.protocol == "https") {
            info.port = 443;
        } else {
            info.port = 80;
        }
    }

    return info;
}

// 解析 HTTP 响应
// 参数：response - 完整的 HTTP 响应字符串
// 返回：HttpResponse 结构体
HttpResponse parseHttpResponse(const string& response) {
    HttpResponse result;
    result.statusCode = 0;
    result.contentLength = 0;

    // 查找响应头和响应体的分隔符（空行：\r\n\r\n）
    size_t headerEnd = response.find("\r\n\r\n");
    if (headerEnd == string::npos) {
        // 没有找到分隔符，全部当作头
        result.headers = response;
        result.body = "";
    } else {
        result.headers = response.substr(0, headerEnd);
        result.body = response.substr(headerEnd + 4);  // 跳过 \r\n\r\n
    }

    // 解析状态行（第一行）
    size_t firstLineEnd = result.headers.find("\r\n");
    if (firstLineEnd != string::npos) {
        string firstLine = result.headers.substr(0, firstLineEnd);

        // 状态行格式：HTTP/1.1 200 OK
        // 找到第一个空格和第二个空格
        size_t space1 = firstLine.find(' ');
        if (space1 != string::npos) {
            size_t space2 = firstLine.find(' ', space1 + 1);
            if (space2 != string::npos) {
                string statusCodeStr = firstLine.substr(space1 + 1, space2 - space1 - 1);
                result.statusCode = atoi(statusCodeStr.c_str());
                result.statusText = firstLine.substr(space2 + 1);
            }
        }
    }

    // 解析 Content-Length
    size_t clPos = response.find("Content-Length:");
    if (clPos != string::npos) {
        size_t clEnd = response.find("\r\n", clPos);
        string clStr = response.substr(clPos + 15, clEnd - clPos - 15);
        result.contentLength = atoi(clStr.c_str());
    }

    return result;
}

// 发送 HTTP GET 请求
// 参数：
//   host - 主机名
//   port - 端口号
//   path - 请求路径
// 返回：完整的 HTTP 响应字符串
string httpGet(const string& host, int port, const string& path) {
    // 构建 HTTP 请求报文
    string request;
    request += "GET " + path + " HTTP/1.1\r\n";
    request += "Host: " + host + "\r\n";
    request += "User-Agent: SimpleHttpClient/1.0 (C++ Study)\r\n";
    request += "Accept: text/html,application/xhtml+xml,*/*\r\n";
    request += "Accept-Language: zh-CN,zh;q=0.9\r\n";
    request += "Connection: close\r\n";  // 请求完成后关闭连接
    request += "\r\n";  // 空行分隔头和体（GET 请求没有请求体）

    // 打印请求报文（调试用）
    cout << "[请求报文]" << endl;
    cout << "----------------------------------------" << endl;
    cout << request;
    cout << "----------------------------------------" << endl;

    // 创建套接字
    SOCKET sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (sock == INVALID_SOCKET) {
        return "Error: 创建套接字失败";
    }

    // 设置目标地址
    sockaddr_in serverAddr;
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(port);
    inet_pton(AF_INET, host.c_str(), &serverAddr.sin_addr);

    // 注意：这里假设 host 是 IP 地址
    // 如果是域名，需要使用 getaddrinfo() 进行 DNS 解析
    // 为了简化代码，这里直接使用 IP，或者尝试解析域名

    // 连接服务器
    if (connect(sock, (sockaddr*)&serverAddr, sizeof(serverAddr)) == SOCKET_ERROR) {
        // 尝试使用 getaddrinfo 解析域名
        addrinfo hints, *result;
        ZeroMemory(&hints, sizeof(hints));
        hints.ai_family = AF_INET;
        hints.ai_socktype = SOCK_STREAM;
        hints.ai_protocol = IPPROTO_TCP;

        char portStr[10];
        itoa(port, portStr, 10);

        if (getaddrinfo(host.c_str(), portStr, &hints, &result) != 0) {
            closesocket(sock);
            return "Error: 无法连接到服务器（可能是 DNS 解析失败）";
        }

        // 关闭旧的套接字，用新地址重新连接
        closesocket(sock);
        sock = socket(result->ai_family, result->ai_socktype, result->ai_protocol);
        if (connect(sock, result->ai_addr, (int)result->ai_addrlen) == SOCKET_ERROR) {
            freeaddrinfo(result);
            closesocket(sock);
            return "Error: 连接服务器失败";
        }
        freeaddrinfo(result);
    }

    // 发送请求
    int sendResult = send(sock, request.c_str(), (int)request.length(), 0);
    if (sendResult == SOCKET_ERROR) {
        closesocket(sock);
        return "Error: 发送请求失败";
    }

    // 接收响应
    string response;
    char buffer[4096];
    int bytesReceived;

    while ((bytesReceived = recv(sock, buffer, sizeof(buffer) - 1, 0)) > 0) {
        buffer[bytesReceived] = '\0';
        response += buffer;
    }

    // 关闭套接字
    closesocket(sock);

    return response;
}

// 发送 HTTP POST 请求
// 参数：
//   host - 主机名
//   port - 端口号
//   path - 请求路径
//   postData - POST 数据（如 "key1=value1&key2=value2"）
// 返回：完整的 HTTP 响应字符串
string httpPost(const string& host, int port, const string& path, const string& postData) {
    // 构建 HTTP POST 请求报文
    string request;
    request += "POST " + path + " HTTP/1.1\r\n";
    request += "Host: " + host + "\r\n";
    request += "User-Agent: SimpleHttpClient/1.0 (C++ Study)\r\n";
    request += "Accept: text/html,application/xhtml+xml,*/*\r\n";
    request += "Accept-Language: zh-CN,zh;q=0.9\r\n";
    request += "Content-Type: application/x-www-form-urlencoded\r\n";  // POST 数据格式
    char contentLen[32];
    itoa((int)postData.length(), contentLen, 10);
    request += "Content-Length: " + string(contentLen) + "\r\n";  // POST 数据长度
    request += "Connection: close\r\n";
    request += "\r\n";  // 空行分隔头和体
    request += postData;  // POST 数据

    // 打印请求报文
    cout << "[请求报文]" << endl;
    cout << "----------------------------------------" << endl;
    cout << request << endl;
    cout << "----------------------------------------" << endl;

    // 创建套接字并连接（同 GET）
    addrinfo hints, *result;
    ZeroMemory(&hints, sizeof(hints));
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_protocol = IPPROTO_TCP;

    char portStr[10];
    itoa(port, portStr, 10);

    if (getaddrinfo(host.c_str(), portStr, &hints, &result) != 0) {
        return "Error: DNS 解析失败";
    }

    SOCKET sock = socket(result->ai_family, result->ai_socktype, result->ai_protocol);
    if (connect(sock, result->ai_addr, (int)result->ai_addrlen) == SOCKET_ERROR) {
        freeaddrinfo(result);
        closesocket(sock);
        return "Error: 连接服务器失败";
    }
    freeaddrinfo(result);

    // 发送请求
    send(sock, request.c_str(), (int)request.length(), 0);

    // 接收响应
    string response;
    char buffer[4096];
    int bytesReceived;

    while ((bytesReceived = recv(sock, buffer, sizeof(buffer) - 1, 0)) > 0) {
        buffer[bytesReceived] = '\0';
        response += buffer;
    }

    closesocket(sock);

    return response;
}

int main(int argc, char* argv[]) {
    // ===================== 参数解析 =====================
    string urlStr = "http://example.com";  // 默认 URL
    string method = "GET";                  // 默认方法
    string postData = "";                   // POST 数据

    if (argc >= 2) {
        urlStr = argv[1];
    }
    if (argc >= 3) {
        method = argv[2];
    }
    if (argc >= 4) {
        postData = argv[3];
    }

    // ===================== 初始化 Winsock =====================
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        cerr << "[错误] Winsock 初始化失败" << endl;
        return 1;
    }

    // ===================== 打印信息 =====================
    cout << "========================================" << endl;
    cout << "   简易 HTTP 客户端（C++ Winsock 版）" << endl;
    cout << "========================================" << endl;

    // 解析 URL
    UrlInfo urlInfo = parseUrl(urlStr);
    cout << "协议: " << urlInfo.protocol << endl;
    cout << "主机: " << urlInfo.host << endl;
    cout << "端口: " << urlInfo.port << endl;
    cout << "路径: " << urlInfo.path << endl;
    cout << "方法: " << method << endl;

    if (urlInfo.protocol == "https") {
        cout << endl << "[警告] HTTPS 需要 SSL/TLS 支持，本工具仅支持 HTTP" << endl;
        cout << "         请使用 HTTP 协议进行测试" << endl;
        WSACleanup();
        return 1;
    }

    cout << "========================================" << endl;
    cout << "[*] 正在发送请求..." << endl;
    cout << endl;

    // ===================== 发送请求 =====================
    string responseStr;

    if (method == "GET" || method == "get") {
        responseStr = httpGet(urlInfo.host, urlInfo.port, urlInfo.path);
    } else if (method == "POST" || method == "post") {
        responseStr = httpPost(urlInfo.host, urlInfo.port, urlInfo.path, postData);
    } else {
        cerr << "[错误] 不支持的请求方法: " << method << endl;
        WSACleanup();
        return 1;
    }

    // ===================== 解析并显示响应 =====================
    cout << endl;
    cout << "========================================" << endl;
    cout << "            响应结果" << endl;
    cout << "========================================" << endl;

    if (responseStr.substr(0, 5) == "Error") {
        cout << responseStr << endl;
        WSACleanup();
        return 1;
    }

    HttpResponse response = parseHttpResponse(responseStr);

    cout << "状态码: " << response.statusCode << " " << response.statusText << endl;
    cout << "内容长度: " << response.contentLength << " 字节" << endl;
    cout << "----------------------------------------" << endl;
    cout << endl;

    cout << "[响应头]" << endl;
    cout << "----------------------------------------" << endl;
    cout << response.headers << endl;
    cout << "----------------------------------------" << endl;
    cout << endl;

    cout << "[响应体（前 2000 字符）]" << endl;
    cout << "----------------------------------------" << endl;
    if (response.body.length() > 2000) {
        cout << response.body.substr(0, 2000) << endl;
        cout << "... (内容过长，已截断)" << endl;
    } else {
        cout << response.body << endl;
    }
    cout << "----------------------------------------" << endl;

    cout << endl;
    cout << "========================================" << endl;
    cout << "            请求完成" << endl;
    cout << "========================================" << endl;

    // ===================== 清理 =====================
    WSACleanup();

    return 0;
}
