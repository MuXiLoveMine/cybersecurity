/*
 * ============================================================
 * 文件名：dir_brute.cs
 * 功能描述：Web 目录爆破工具（HttpClient 异步版）
 * 作者：网络安全学习笔记
 * 日期：2026-09-10
 * ============================================================
 *
 * 【使用说明】
 * 1. 编译运行：
 *    dotnet new console -n DirBrute
 *    将本文件替换 Program.cs，然后 dotnet run
 * 2. 或直接使用 csc 编译：
 *    csc dir_brute.cs
 * 3. 命令行参数：
 *    参数1：目标 URL（默认：http://127.0.0.1）
 *    参数2：字典文件路径（留空使用内置字典）
 *    参数3：并发数（默认：50）
 *    参数4：超时时间（秒，默认：5）
 *
 * 【示例】
 *   dir_brute.exe http://example.com
 *   dir_brute.exe http://example.com dict.txt 100
 *   dotnet run -- http://192.168.1.1 ./wordlist.txt 50
 *
 * 【技术要点】
 *   - 使用 HttpClient 发送 HTTP 请求
 *   - 使用 async/await 实现异步并发
 *   - 使用 SemaphoreSlim 控制并发数量
 *   - 支持自定义字典和内置字典
 *   - 根据状态码判断路径是否存在
 *
 * 【免责声明】
 *   本工具仅供网络安全学习和授权测试使用。
 *   禁止对未授权的网站进行目录爆破，违者后果自负。
 *   使用本工具请遵守当地法律法规。
 * ============================================================
 */

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Threading;
using System.Threading.Tasks;

// 命名空间
namespace DirBrute
{
    // 爆破结果类
    public class BruteResult
    {
        public string Path { get; set; }       // 爆破的路径
        public int StatusCode { get; set; }    // HTTP 状态码
        public long Size { get; set; }         // 响应体大小
        public bool IsFound { get; set; }      // 是否命中
    }

    // 主程序类
    class Program
    {
        // 关注的 HTTP 状态码列表
        // 这些状态码表示路径可能存在
        private static readonly HashSet<int> TargetStatusCodes = new HashSet<int>
        {
            200,  // OK - 成功
            301,  // Moved Permanently - 永久重定向
            302,  // Found - 临时重定向
            403,  // Forbidden - 禁止访问（但路径存在）
            401,  // Unauthorized - 未授权（但路径存在）
            405,  // Method Not Allowed - 方法不允许（但路径存在）
        };

        // 默认内置字典
        // 当用户没有指定字典文件时使用
        private static readonly string[] DefaultWordlist = new string[]
        {
            // 常见后台路径
            "admin", "admin.php", "admin.html", "admin/login", "admin/index",
            "admin/admin", "login", "login.php", "login.html", "signin",
            "manage", "manager", "cms", "system", "member", "user",
            // 常见文件
            "index.php", "index.html", "index.asp", "index.jsp",
            "robots.txt", "sitemap.xml", "sitemap.html",
            "readme.md", "README.md", "readme.txt", "CHANGELOG.txt",
            "config.php", "config.inc.php", "database.yml", "web.config",
            ".htaccess", ".htpasswd", "crossdomain.xml",
            // 备份文件
            "backup", "backup.sql", "backup.zip", "backup.tar", "backup.tar.gz",
            "www.zip", "wwwroot.zip", "web.zip", "site.zip",
            // 版本控制文件
            ".git/", ".git/config", ".git/HEAD", ".svn/", ".svn/entries",
            ".DS_Store", "Thumbs.db",
            // 常见目录
            "upload", "uploads", "files", "data", "static", "assets",
            "images", "img", "css", "js", "includes", "inc", "lib",
            "tmp", "temp", "cache", "logs", "log",
            // API 路径
            "api", "api/v1", "api/v2", "graphql", "swagger", "docs",
            // 常见漏洞页面
            "phpinfo.php", "test.php", "info.php", "status", "server-status",
            "actuator", "actuator/env", "actuator/health",
        };

        /// <summary>
        /// 从文件加载字典
        /// </summary>
        /// <param name="filePath">字典文件路径</param>
        /// <returns>路径列表</returns>
        private static List<string> LoadWordlist(string filePath)
        {
            var wordlist = new List<string>();

            try
            {
                // 读取文件所有行
                string[] lines = File.ReadAllLines(filePath);

                foreach (string line in lines)
                {
                    // 去除首尾空白
                    string trimmed = line.Trim();

                    // 跳过空行和注释行（以 # 开头）
                    if (string.IsNullOrEmpty(trimmed) || trimmed.StartsWith("#"))
                    {
                        continue;
                    }

                    wordlist.Add(trimmed);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[错误] 加载字典文件失败: {ex.Message}");
            }

            return wordlist;
        }

        /// <summary>
        /// 对单个路径进行爆破
        /// </summary>
        /// <param name="client">HttpClient 实例</param>
        /// <param name="baseUrl">基础 URL</param>
        /// <param name="path">待爆破路径</param>
        /// <returns>爆破结果</returns>
        private static async Task<BruteResult> BrutePathAsync(HttpClient client, string baseUrl, string path)
        {
            var result = new BruteResult
            {
                Path = path,
                StatusCode = 0,
                Size = 0,
                IsFound = false
            };

            try
            {
                // 构造完整 URL
                // 确保 baseURL 结尾没有斜杠，path 开头没有斜杠
                string cleanBase = baseUrl.TrimEnd('/');
                string cleanPath = path.TrimStart('/');
                string fullUrl = $"{cleanBase}/{cleanPath}";

                // 发送 GET 请求
                // 使用 GetAsync 异步发送请求
                HttpResponseMessage response = await client.GetAsync(fullUrl);

                // 获取状态码
                result.StatusCode = (int)response.StatusCode;

                // 获取响应体大小
                // 使用 Content.ReadAsByteArrayAsync 读取内容
                byte[] content = await response.Content.ReadAsByteArrayAsync();
                result.Size = content.Length;

                // 判断是否命中（状态码在目标列表中）
                result.IsFound = TargetStatusCodes.Contains(result.StatusCode);
            }
            catch (HttpRequestException)
            {
                // HTTP 请求异常（连接失败等）
                result.StatusCode = 0;
                result.IsFound = false;
            }
            catch (TaskCanceledException)
            {
                // 请求超时
                result.StatusCode = 0;
                result.IsFound = false;
            }
            catch (Exception)
            {
                // 其他异常
                result.StatusCode = 0;
                result.IsFound = false;
            }

            return result;
        }

        /// <summary>
        /// 并发爆破路径
        /// </summary>
        /// <param name="client">HttpClient 实例</param>
        /// <param name="baseUrl">基础 URL</param>
        /// <param name="wordlist">字典列表</param>
        /// <param name="maxConcurrency">最大并发数</param>
        /// <returns>所有结果列表</returns>
        private static async Task<List<BruteResult>> BrutePathsAsync(
            HttpClient client, string baseUrl, List<string> wordlist, int maxConcurrency)
        {
            var results = new List<BruteResult>();
            var allTasks = new List<Task<BruteResult>>();

            // 使用 SemaphoreSlim 控制并发数量
            using (var semaphore = new SemaphoreSlim(maxConcurrency, maxConcurrency))
            {
                int completed = 0;

                foreach (string path in wordlist)
                {
                    // 等待信号量
                    await semaphore.WaitAsync();

                    // 捕获本地变量，避免闭包问题
                    string currentPath = path;

                    var task = Task.Run(async () =>
                    {
                        try
                        {
                            return await BrutePathAsync(client, baseUrl, currentPath);
                        }
                        finally
                        {
                            // 释放信号量
                            semaphore.Release();

                            // 原子递增完成计数，每 100 个显示一次进度
                            int current = Interlocked.Increment(ref completed);
                            if (current % 100 == 0)
                            {
                                Console.WriteLine($"  ... 进度: {current}/{wordlist.Count}");
                            }
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
            string baseUrl = "http://127.0.0.1";  // 目标 URL
            string wordlistFile = "";              // 字典文件路径
            int maxConcurrency = 50;               // 最大并发数
            int timeoutSec = 5;                    // 超时时间（秒）

            if (args.Length >= 1)
            {
                baseUrl = args[0];
            }
            if (args.Length >= 2)
            {
                wordlistFile = args[1];
            }
            if (args.Length >= 3)
            {
                int.TryParse(args[2], out maxConcurrency);
            }
            if (args.Length >= 4)
            {
                int.TryParse(args[3], out timeoutSec);
            }

            // 确保 URL 有协议前缀
            if (!baseUrl.StartsWith("http://") && !baseUrl.StartsWith("https://"))
            {
                baseUrl = "http://" + baseUrl;
            }

            // ===================== 加载字典 =====================
            List<string> wordlist;

            if (!string.IsNullOrEmpty(wordlistFile))
            {
                // 从文件加载字典
                wordlist = LoadWordlist(wordlistFile);
                if (wordlist.Count == 0)
                {
                    Console.WriteLine("[错误] 字典文件为空或加载失败");
                    return;
                }
                Console.WriteLine($"[*] 已加载字典文件: {wordlistFile} (共 {wordlist.Count} 条)");
            }
            else
            {
                // 使用内置字典
                wordlist = new List<string>(DefaultWordlist);
                Console.WriteLine($"[*] 使用内置字典 (共 {wordlist.Count} 条)");
            }

            // ===================== 打印信息 =====================
            Console.WriteLine("========================================");
            Console.WriteLine("    Web 目录爆破工具（C# 异步版）");
            Console.WriteLine("========================================");
            Console.WriteLine($"目标 URL: {baseUrl}");
            Console.WriteLine($"字典数量: {wordlist.Count}");
            Console.WriteLine($"并发数量: {maxConcurrency}");
            Console.WriteLine($"超时时间: {timeoutSec} 秒");
            Console.WriteLine("========================================");
            Console.WriteLine("[*] 正在爆破，请稍候...");
            Console.WriteLine("----------------------------------------");

            // ===================== 初始化 HttpClient =====================
            // 创建 HttpClientHandler，配置是否自动重定向
            var handler = new HttpClientHandler();
            handler.AllowAutoRedirect = false;  // 不自动跟随重定向，方便观察 301/302
            handler.UseCookies = true;

            // 创建 HttpClient 实例
            // HttpClient 设计为可复用，不要为每个请求创建新实例
            using (var client = new HttpClient(handler))
            {
                // 设置超时时间
                client.Timeout = TimeSpan.FromSeconds(timeoutSec);

                // 设置默认请求头（模拟浏览器）
                client.DefaultRequestHeaders.Add("User-Agent",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36");
                client.DefaultRequestHeaders.Add("Accept",
                    "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8");
                client.DefaultRequestHeaders.Add("Accept-Language",
                    "zh-CN,zh;q=0.9,en;q=0.8");
            }

            // 重新创建 client（上面的 using 已经释放了，这里是为了演示流程）
            // 实际使用时应该在整个生命周期内复用同一个 HttpClient
            var httpHandler = new HttpClientHandler
            {
                AllowAutoRedirect = false,
                UseCookies = true
            };

            using (var httpClient = new HttpClient(httpHandler))
            {
                httpClient.Timeout = TimeSpan.FromSeconds(timeoutSec);
                httpClient.DefaultRequestHeaders.Add("User-Agent",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36");
                httpClient.DefaultRequestHeaders.Add("Accept",
                    "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8");
                httpClient.DefaultRequestHeaders.Add("Accept-Language",
                    "zh-CN,zh;q=0.9,en;q=0.8");

                // 记录开始时间
                Stopwatch stopwatch = Stopwatch.StartNew();

                // ===================== 执行爆破 =====================
                var results = await BrutePathsAsync(httpClient, baseUrl, wordlist, maxConcurrency);

                // 停止计时
                stopwatch.Stop();

                // ===================== 处理结果 =====================
                var foundResults = results.Where(r => r.IsFound).OrderBy(r => r.StatusCode).ToList();

                // ===================== 输出结果 =====================
                Console.WriteLine("----------------------------------------");
                Console.WriteLine();
                Console.WriteLine("========================================");
                Console.WriteLine("            爆破结果汇总");
                Console.WriteLine("========================================");
                Console.WriteLine($"请求总数: {results.Count}");
                Console.WriteLine($"命中数量: {foundResults.Count}");
                Console.WriteLine($"用时: {stopwatch.Elapsed.TotalSeconds:F2} 秒");

                if (stopwatch.Elapsed.TotalSeconds > 0)
                {
                    Console.WriteLine($"速度: {(int)(results.Count / stopwatch.Elapsed.TotalSeconds)} 次/秒");
                }

                if (foundResults.Count > 0)
                {
                    Console.WriteLine();
                    Console.WriteLine("[命中路径列表]");
                    Console.WriteLine($"{"状态码",-8} {"响应大小",-12} 路径");
                    Console.WriteLine("----------------------------------------");
                    foreach (var result in foundResults)
                    {
                        Console.WriteLine($"{result.StatusCode,-8} {result.Size + "字节",-12} /{result.Path}");
                    }
                }
                else
                {
                    Console.WriteLine();
                    Console.WriteLine("[!] 未发现可访问的路径");
                }

                Console.WriteLine();
                Console.WriteLine("========================================");
                Console.WriteLine("            爆破完成");
                Console.WriteLine("========================================");
            }
        }
    }
}
