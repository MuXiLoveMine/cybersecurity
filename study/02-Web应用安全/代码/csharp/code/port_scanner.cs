/*
 * ============================================================
 * 文件名：port_scanner.cs
 * 功能描述：TCP 端口扫描器（TcpClient 异步并发版）
 * 作者：网络安全学习笔记
 * 日期：2026-09-10
 * ============================================================
 *
 * 【使用说明】
 * 1. 编译运行：
 *    dotnet new console -n PortScanner
 *    将本文件替换 Program.cs，然后 dotnet run
 * 2. 或直接使用 csc 编译：
 *    csc port_scanner.cs
 * 3. 命令行参数：
 *    参数1：目标主机地址（默认：127.0.0.1）
 *    参数2：起始端口（默认：1）
 *    参数3：结束端口（默认：1024）
 *    参数4：并发数（默认：100）
 *    参数5：超时时间（毫秒，默认：500）
 *
 * 【示例】
 *   port_scanner.exe 192.168.1.1 1 1000 200 300
 *   dotnet run -- 127.0.0.1 20 100
 *
 * 【技术要点】
 *   - 使用 TcpClient 类进行 TCP 连接
 *   - 使用 async/await 实现异步并发扫描
 *   - 使用 SemaphoreSlim 控制并发数量
 *   - 使用 ConnectAsync 异步连接，支持超时
 *
 * 【免责声明】
 *   本工具仅供网络安全学习和授权测试使用。
 *   禁止对未授权的目标进行端口扫描，违者后果自负。
 *   使用本工具请遵守当地法律法规。
 * ============================================================
 */

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Net.Sockets;
using System.Threading;
using System.Threading.Tasks;

// 命名空间
namespace PortScanner
{
    // 扫描结果类
    public class ScanResult
    {
        public int Port { get; set; }         // 端口号
        public bool IsOpen { get; set; }      // 是否开放
        public string Service { get; set; }   // 服务名称
    }

    // 主程序类
    class Program
    {
        // 常见端口服务名称映射字典
        // 用于在扫描结果中显示对应的服务名
        private static readonly Dictionary<int, string> CommonPorts = new Dictionary<int, string>()
        {
            { 21, "FTP" },          // 文件传输协议
            { 22, "SSH" },          // 安全外壳协议
            { 23, "Telnet" },       // 远程登录
            { 25, "SMTP" },         // 简单邮件传输协议
            { 53, "DNS" },          // 域名系统
            { 80, "HTTP" },         // 超文本传输协议
            { 110, "POP3" },        // 邮局协议第3版
            { 135, "MSRPC" },       // Microsoft RPC
            { 139, "NetBIOS" },     // 网络基本输入输出系统
            { 143, "IMAP" },        // 互联网消息访问协议
            { 443, "HTTPS" },       // 安全超文本传输协议
            { 445, "SMB" },         // 服务器消息块
            { 465, "SMTPS" },       // SMTP over SSL
            { 993, "IMAPS" },       // IMAP over SSL
            { 995, "POP3S" },       // POP3 over SSL
            { 1080, "SOCKS" },      // SOCKS 代理
            { 1433, "MSSQL" },      // Microsoft SQL Server
            { 1521, "Oracle" },     // Oracle 数据库
            { 3306, "MySQL" },      // MySQL 数据库
            { 3389, "RDP" },        // 远程桌面协议
            { 5432, "PostgreSQL" }, // PostgreSQL 数据库
            { 5900, "VNC" },        // 虚拟网络计算
            { 6379, "Redis" },      // Redis 数据库
            { 8080, "HTTP-Proxy" }, // HTTP 代理
            { 8443, "HTTPS-Alt" },  // 备用 HTTPS
            { 27017, "MongoDB" },   // MongoDB 数据库
        };

        /// <summary>
        /// 获取端口对应的服务名称
        /// </summary>
        /// <param name="port">端口号</param>
        /// <returns>服务名称，未知端口返回 "unknown"</returns>
        private static string GetServiceName(int port)
        {
            if (CommonPorts.ContainsKey(port))
            {
                return CommonPorts[port];
            }
            return "unknown";
        }

        /// <summary>
        /// 异步扫描单个端口
        /// </summary>
        /// <param name="host">目标主机地址</param>
        /// <param name="port">端口号</param>
        /// <param name="timeoutMs">超时时间（毫秒）</param>
        /// <returns>扫描结果对象</returns>
        private static async Task<ScanResult> ScanPortAsync(string host, int port, int timeoutMs)
        {
            var result = new ScanResult
            {
                Port = port,
                IsOpen = false,
                Service = GetServiceName(port)
            };

            try
            {
                // 创建 TcpClient 实例
                using (var client = new TcpClient())
                {
                    // 创建取消令牌源，用于实现连接超时
                    using (var cts = new CancellationTokenSource(timeoutMs))
                    {
                        // 异步连接到目标主机和端口
                        // ConnectAsync 是异步方法，不会阻塞线程
                        var connectTask = client.ConnectAsync(host, port);

                        // 等待连接完成或超时
                        // 使用 WhenAny 等待第一个完成的任务
                        var completedTask = await Task.WhenAny(connectTask, Task.Delay(timeoutMs, cts.Token));

                        if (completedTask == connectTask)
                        {
                            // 连接任务先完成
                            // 检查是否连接成功
                            if (client.Connected)
                            {
                                result.IsOpen = true;
                            }
                            cts.Cancel(); // 取消延迟任务
                        }
                        else
                        {
                            // 超时了
                            result.IsOpen = false;
                        }
                    }
                }
            }
            catch (SocketException)
            {
                // 连接被拒绝或其他 Socket 错误，端口关闭
                result.IsOpen = false;
            }
            catch (Exception)
            {
                // 其他异常，视为端口关闭/过滤
                result.IsOpen = false;
            }

            return result;
        }

        /// <summary>
        /// 异步并发扫描端口范围
        /// </summary>
        /// <param name="host">目标主机</param>
        /// <param name="startPort">起始端口</param>
        /// <param name="endPort">结束端口</param>
        /// <param name="maxConcurrency">最大并发数</param>
        /// <param name="timeoutMs">超时时间</param>
        /// <returns>所有扫描结果列表</returns>
        private static async Task<List<ScanResult>> ScanPortRangeAsync(
            string host, int startPort, int endPort, int maxConcurrency, int timeoutMs)
        {
            var results = new List<ScanResult>();
            var allTasks = new List<Task<ScanResult>>();

            // 使用 SemaphoreSlim 控制并发数量
            // 信号量初始化为 maxConcurrency，表示最多同时运行 maxConcurrency 个任务
            using (var semaphore = new SemaphoreSlim(maxConcurrency, maxConcurrency))
            {
                // 为每个端口创建一个扫描任务
                for (int port = startPort; port <= endPort; port++)
                {
                    // 等待信号量（获取一个并发槽位）
                    await semaphore.WaitAsync();

                    // 启动异步扫描任务
                    // 使用本地变量保存端口号，避免闭包问题
                    int currentPort = port;
                    var task = Task.Run(async () =>
                    {
                        try
                        {
                            return await ScanPortAsync(host, currentPort, timeoutMs);
                        }
                        finally
                        {
                            // 任务完成后释放信号量
                            semaphore.Release();
                        }
                    });

                    allTasks.Add(task);
                }

                // 等待所有任务完成
                var allResults = await Task.WhenAll(allTasks);
                results.AddRange(allResults);
            }

            return results;
        }

        static async Task Main(string[] args)
        {
            // ===================== 参数解析 =====================
            // 默认参数值
            string host = "127.0.0.1";  // 目标主机
            int startPort = 1;          // 起始端口
            int endPort = 1024;         // 结束端口
            int maxConcurrency = 100;   // 最大并发数
            int timeoutMs = 500;        // 超时时间（毫秒）

            // 解析命令行参数
            if (args.Length >= 1)
            {
                host = args[0];
            }
            if (args.Length >= 2)
            {
                int.TryParse(args[1], out startPort);
            }
            if (args.Length >= 3)
            {
                int.TryParse(args[2], out endPort);
            }
            if (args.Length >= 4)
            {
                int.TryParse(args[3], out maxConcurrency);
            }
            if (args.Length >= 5)
            {
                int.TryParse(args[4], out timeoutMs);
            }

            // 参数合法性校验
            if (startPort < 1 || startPort > 65535)
            {
                Console.WriteLine("[错误] 起始端口必须在 1-65535 之间");
                return;
            }
            if (endPort < 1 || endPort > 65535)
            {
                Console.WriteLine("[错误] 结束端口必须在 1-65535 之间");
                return;
            }
            if (startPort > endPort)
            {
                Console.WriteLine("[错误] 起始端口不能大于结束端口");
                return;
            }
            if (maxConcurrency < 1)
            {
                Console.WriteLine("[错误] 并发数不能小于 1");
                return;
            }

            // ===================== 打印扫描信息 =====================
            Console.WriteLine("========================================");
            Console.WriteLine("  TCP 端口扫描器（C# 异步并发版）");
            Console.WriteLine("========================================");
            Console.WriteLine($"目标主机: {host}");
            Console.WriteLine($"端口范围: {startPort} - {endPort}");
            Console.WriteLine($"并发数量: {maxConcurrency}");
            Console.WriteLine($"超时时间: {timeoutMs} 毫秒");
            Console.WriteLine("========================================");
            Console.WriteLine("[*] 正在扫描，请稍候...");
            Console.WriteLine("----------------------------------------");

            // 记录开始时间
            Stopwatch stopwatch = Stopwatch.StartNew();

            // ===================== 执行扫描 =====================
            var results = await ScanPortRangeAsync(host, startPort, endPort, maxConcurrency, timeoutMs);

            // 停止计时
            stopwatch.Stop();

            // ===================== 处理结果 =====================
            // 分离开放端口和关闭端口
            var openPorts = results.Where(r => r.IsOpen).OrderBy(r => r.Port).ToList();
            var closedPorts = results.Where(r => !r.IsOpen).ToList();

            // ===================== 输出结果 =====================
            Console.WriteLine("----------------------------------------");
            Console.WriteLine();
            Console.WriteLine("========================================");
            Console.WriteLine("            扫描结果");
            Console.WriteLine("========================================");
            Console.WriteLine($"扫描端口总数: {endPort - startPort + 1}");
            Console.WriteLine($"开放端口数量: {openPorts.Count}");
            Console.WriteLine($"关闭/过滤端口数量: {closedPorts.Count}");
            Console.WriteLine($"扫描用时: {stopwatch.Elapsed.TotalSeconds:F2} 秒");
            Console.WriteLine("----------------------------------------");

            if (openPorts.Count > 0)
            {
                Console.WriteLine();
                Console.WriteLine("[开放端口列表]");
                Console.WriteLine($"{"端口",-8} {"状态",-10} {"服务"}");
                Console.WriteLine("----------------------------------------");
                foreach (var result in openPorts)
                {
                    Console.WriteLine($"{result.Port,-8} {"open",-10} {result.Service}");
                }
            }
            else
            {
                Console.WriteLine();
                Console.WriteLine("[!] 未发现开放端口");
            }

            Console.WriteLine();
            Console.WriteLine("========================================");
            Console.WriteLine("            扫描完成");
            Console.WriteLine("========================================");
        }
    }
}
