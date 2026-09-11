/*
 * ============================================================
 * 文件名：http_header_check.cs
 * 功能描述：HTTP 安全头检测工具（C# 版）
 * 作者：网络安全学习笔记
 * 日期：2026-09-10
 * ============================================================
 *
 * 【使用说明】
 * 1. 编译运行：
 *    dotnet new console -n HttpHeaderCheck
 *    将本文件替换 Program.cs，然后 dotnet run
 * 2. 或直接使用 csc 编译：
 *    csc http_header_check.cs
 * 3. 命令行参数：
 *    参数1：目标 URL（默认：http://127.0.0.1）
 *    参数2：超时时间（秒，默认：10）
 *
 * 【示例】
 *   http_header_check.exe https://example.com
 *   http_header_check.exe http://192.168.1.1:8080 5
 *   dotnet run -- https://www.example.com
 *
 * 【检测的 7 大安全头】
 *   1. X-Content-Type-Options    - 防止 MIME 类型嗅探
 *   2. X-Frame-Options           - 防止点击劫持攻击
 *   3. X-XSS-Protection          - 启用浏览器 XSS 防护
 *   4. Content-Security-Policy   - 内容安全策略（防XSS等）
 *   5. Strict-Transport-Security - 强制使用 HTTPS
 *   6. Referrer-Policy           - 控制 Referer 信息泄露
 *   7. Permissions-Policy        - 控制浏览器功能权限
 *
 * 【评分规则】
 *   - 每个安全头最高 1 分，共 7 分
 *   - 根据配置的严格程度给予部分分数
 *   - 最终给出总分和等级评定
 *
 * 【免责声明】
 *   本工具仅供网络安全学习和授权测试使用。
 *   仅用于检测目标网站的 HTTP 安全头配置情况。
 *   使用本工具请遵守当地法律法规。
 * ============================================================
 */

using System;
using System.Collections.Generic;
using System.Net;
using System.Net.Http;
using System.Net.Security;
using System.Security.Cryptography.X509Certificates;
using System.Threading.Tasks;

// 命名空间
namespace HttpHeaderCheck
{
    // 安全头检测结果类
    public class HeaderCheckResult
    {
        public string Name { get; set; }         // 安全头名称
        public bool Present { get; set; }        // 是否存在
        public string Value { get; set; }        // 头的值
        public double Score { get; set; }        // 得分（0-1）
        public string Description { get; set; }  // 头的作用说明
        public string Advice { get; set; }       // 改进建议
    }

    // 安全头配置信息类
    public class SecurityHeaderInfo
    {
        public string Name { get; set; }         // 头名称
        public string Description { get; set; }  // 作用说明
        public string BestValue { get; set; }    // 推荐配置值
    }

    // 主程序类
    class Program
    {
        // 7 大安全头定义
        private static readonly List<SecurityHeaderInfo> SecurityHeaders = new List<SecurityHeaderInfo>
        {
            new SecurityHeaderInfo
            {
                Name = "X-Content-Type-Options",
                Description = "防止浏览器进行 MIME 类型嗅探，强制使用 Content-Type 声明的类型",
                BestValue = "nosniff"
            },
            new SecurityHeaderInfo
            {
                Name = "X-Frame-Options",
                Description = "防止页面被嵌入到 iframe 中，抵御点击劫持攻击",
                BestValue = "DENY 或 SAMEORIGIN"
            },
            new SecurityHeaderInfo
            {
                Name = "X-XSS-Protection",
                Description = "启用浏览器内置的 XSS 防护机制",
                BestValue = "1; mode=block"
            },
            new SecurityHeaderInfo
            {
                Name = "Content-Security-Policy",
                Description = "内容安全策略，限制资源加载来源，有效防御 XSS 等注入攻击",
                BestValue = "严格的 CSP 策略"
            },
            new SecurityHeaderInfo
            {
                Name = "Strict-Transport-Security",
                Description = "强制浏览器使用 HTTPS 访问，防止协议降级攻击",
                BestValue = "max-age=31536000; includeSubDomains"
            },
            new SecurityHeaderInfo
            {
                Name = "Referrer-Policy",
                Description = "控制 Referer 头信息的发送，防止敏感信息泄露",
                BestValue = "strict-origin-when-cross-origin 或 no-referrer"
            },
            new SecurityHeaderInfo
            {
                Name = "Permissions-Policy",
                Description = "控制浏览器功能（如摄像头、麦克风、地理位置等）的使用权限",
                BestValue = "限制不必要的功能权限"
            }
        };

        /// <summary>
        /// 评估单个安全头的配置质量
        /// </summary>
        /// <param name="header">安全头配置信息</param>
        /// <param name="value">实际的头值</param>
        /// <param name="score">输出得分</param>
        /// <param name="advice">输出改进建议</param>
        private static void EvaluateHeader(SecurityHeaderInfo header, string value,
                                            out double score, out string advice)
        {
            // 如果值为空，表示头不存在
            if (string.IsNullOrEmpty(value))
            {
                score = 0;
                advice = $"未设置 {header.Name} 头，建议添加：{header.BestValue}";
                return;
            }

            string valueLower = value.ToLower();

            // 根据不同的头进行评分
            switch (header.Name)
            {
                case "X-Content-Type-Options":
                    if (valueLower.Contains("nosniff"))
                    {
                        score = 1.0;
                        advice = "配置正确";
                    }
                    else
                    {
                        score = 0.3;
                        advice = "建议设置为 nosniff";
                    }
                    break;

                case "X-Frame-Options":
                    if (valueLower.Contains("deny"))
                    {
                        score = 1.0;
                        advice = "配置严格（DENY）";
                    }
                    else if (valueLower.Contains("sameorigin"))
                    {
                        score = 0.8;
                        advice = "配置较好（SAMEORIGIN）";
                    }
                    else if (valueLower.Contains("allow-from"))
                    {
                        score = 0.5;
                        advice = "配置了白名单（ALLOW-FROM）";
                    }
                    else
                    {
                        score = 0.2;
                        advice = "配置值不正确";
                    }
                    break;

                case "X-XSS-Protection":
                    if (valueLower.Contains("1; mode=block"))
                    {
                        score = 1.0;
                        advice = "配置正确，启用强制拦截模式";
                    }
                    else if (valueLower.Contains("1"))
                    {
                        score = 0.6;
                        advice = "启用了 XSS 防护，但建议添加 mode=block";
                    }
                    else if (valueLower.Contains("0"))
                    {
                        score = 0;
                        advice = "已禁用 XSS 防护，建议启用";
                    }
                    else
                    {
                        score = 0.3;
                        advice = "建议设置为 1; mode=block";
                    }
                    break;

                case "Content-Security-Policy":
                    if (valueLower.Contains("default-src 'self'"))
                    {
                        score = 1.0;
                        advice = "配置了严格的默认源策略";
                    }
                    else if (valueLower.Contains("default-src"))
                    {
                        score = 0.8;
                        advice = "配置了 default-src，建议限制为 'self'";
                    }
                    else if (valueLower.Contains("script-src"))
                    {
                        score = 0.7;
                        advice = "配置了 script-src，建议也配置 default-src";
                    }
                    else if (value.Length > 10)
                    {
                        score = 0.5;
                        advice = "已配置 CSP，但策略可能不够严格";
                    }
                    else
                    {
                        score = 0.3;
                        advice = "CSP 配置过于简单";
                    }
                    break;

                case "Strict-Transport-Security":
                    if (valueLower.Contains("max-age="))
                    {
                        if (valueLower.Contains("includesubdomains") &&
                            valueLower.Contains("preload"))
                        {
                            score = 1.0;
                            advice = "配置完整，包含子域名和 preload";
                        }
                        else if (valueLower.Contains("includesubdomains"))
                        {
                            score = 0.85;
                            advice = "配置较好，包含子域名";
                        }
                        else
                        {
                            score = 0.7;
                            advice = "已配置 HSTS，建议添加 includeSubDomains";
                        }
                    }
                    else
                    {
                        score = 0.2;
                        advice = "HSTS 配置不正确";
                    }
                    break;

                case "Referrer-Policy":
                    if (valueLower.Contains("no-referrer"))
                    {
                        score = 1.0;
                        advice = "配置最严格（no-referrer）";
                    }
                    else if (valueLower.Contains("strict-origin-when-cross-origin"))
                    {
                        score = 0.9;
                        advice = "配置较好，平衡安全与可用性";
                    }
                    else if (valueLower.Contains("same-origin"))
                    {
                        score = 0.7;
                        advice = "同源策略，跨域不发送 referrer";
                    }
                    else if (valueLower.Contains("origin"))
                    {
                        score = 0.5;
                        advice = "仅发送 origin 信息";
                    }
                    else
                    {
                        score = 0.3;
                        advice = "建议设置为 strict-origin-when-cross-origin";
                    }
                    break;

                case "Permissions-Policy":
                    if (valueLower.Contains("geolocation=()") ||
                        valueLower.Contains("camera=()") ||
                        valueLower.Contains("microphone=()"))
                    {
                        score = 1.0;
                        advice = "已限制敏感权限";
                    }
                    else if (value.Length > 10)
                    {
                        score = 0.6;
                        advice = "已配置权限策略，建议进一步限制";
                    }
                    else
                    {
                        score = 0.3;
                        advice = "权限策略配置过于简单";
                    }
                    break;

                default:
                    score = 0.5;
                    advice = "已配置";
                    break;
            }
        }

        /// <summary>
        /// 根据总分获取安全等级
        /// </summary>
        /// <param name="score">总得分</param>
        /// <returns>等级字符串</returns>
        private static string GetGrade(double score)
        {
            switch (score)
            {
                case double s when s >= 6.5:
                    return "A (优秀)";
                case double s when s >= 5.5:
                    return "B (良好)";
                case double s when s >= 4.0:
                    return "C (一般)";
                case double s when s >= 2.5:
                    return "D (较差)";
                default:
                    return "F (危险)";
            }
        }

        static async Task Main(string[] args)
        {
            // ===================== 参数解析 =====================
            string targetUrl = "http://127.0.0.1";
            int timeoutSec = 10;

            if (args.Length >= 1)
            {
                targetUrl = args[0];
            }
            if (args.Length >= 2)
            {
                int.TryParse(args[1], out timeoutSec);
            }

            // 确保 URL 有协议前缀
            if (!targetUrl.StartsWith("http://") && !targetUrl.StartsWith("https://"))
            {
                targetUrl = "http://" + targetUrl;
            }

            // ===================== 打印信息 =====================
            Console.WriteLine("========================================");
            Console.WriteLine("    HTTP 安全头检测工具（C# 版）");
            Console.WriteLine("========================================");
            Console.WriteLine($"目标 URL: {targetUrl}");
            Console.WriteLine($"超时时间: {timeoutSec} 秒");
            Console.WriteLine("========================================");
            Console.WriteLine("[*] 正在检测，请稍候...");

            // ===================== 初始化 HttpClient =====================
            // 创建 HttpClientHandler，配置跳过 SSL 证书验证（用于测试自签名证书）
            var handler = new HttpClientHandler();
            handler.ServerCertificateCustomValidationCallback =
                (HttpRequestMessage message, X509Certificate2 cert, X509Chain chain, SslPolicyErrors errors) =>
                {
                    return true; // 跳过证书验证，仅用于测试
                };
            handler.AllowAutoRedirect = false; // 不跟随重定向

            using (var client = new HttpClient(handler))
            {
                client.Timeout = TimeSpan.FromSeconds(timeoutSec);

                // 设置请求头
                client.DefaultRequestHeaders.Add("User-Agent",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36");
                client.DefaultRequestHeaders.Add("Accept",
                    "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8");

                // ===================== 发送请求 =====================
                HttpResponseMessage response;
                try
                {
                    response = await client.GetAsync(targetUrl);
                }
                catch (HttpRequestException ex)
                {
                    Console.WriteLine($"[错误] 请求失败: {ex.Message}");
                    return;
                }
                catch (TaskCanceledException)
                {
                    Console.WriteLine("[错误] 请求超时");
                    return;
                }

                Console.WriteLine($"[*] 响应状态码: {(int)response.StatusCode} {response.StatusCode}");
                Console.WriteLine("----------------------------------------");

                // ===================== 检测安全头 =====================
                var results = new List<HeaderCheckResult>();
                double totalScore = 0;

                foreach (var header in SecurityHeaders)
                {
                    // 获取响应头的值
                    string value = "";
                    if (response.Headers.TryGetValues(header.Name, out var values))
                    {
                        value = string.Join(", ", values);
                    }

                    // 评估该头的配置
                    EvaluateHeader(header, value, out double score, out string advice);

                    var result = new HeaderCheckResult
                    {
                        Name = header.Name,
                        Present = !string.IsNullOrEmpty(value),
                        Value = value,
                        Score = score,
                        Description = header.Description,
                        Advice = advice
                    };

                    results.Add(result);
                    totalScore += score;
                }

                // ===================== 输出检测结果 =====================
                Console.WriteLine();
                Console.WriteLine("========================================");
                Console.WriteLine("            检测结果详情");
                Console.WriteLine("========================================");

                for (int i = 0; i < results.Count; i++)
                {
                    var result = results[i];
                    string status = result.Present ? "[已设置]" : "[未设置]";

                    Console.WriteLine();
                    Console.WriteLine($"{i + 1}. {result.Name} {status}");
                    Console.WriteLine($"   作用: {result.Description}");
                    Console.WriteLine($"   得分: {result.Score:F1} / 1.0");

                    if (result.Present)
                    {
                        Console.WriteLine($"   当前值: {result.Value}");
                    }
                    Console.WriteLine($"   建议: {result.Advice}");
                }

                // ===================== 输出评分汇总 =====================
                Console.WriteLine();
                Console.WriteLine("========================================");
                Console.WriteLine("           安全评分汇总");
                Console.WriteLine("========================================");
                Console.WriteLine($"总得分: {totalScore:F1} / 7.0");
                Console.WriteLine($"安全等级: {GetGrade(totalScore)}");

                // 计算百分比
                double percentage = (totalScore / 7.0) * 100;
                Console.WriteLine($"完成度: {percentage:F1}%");

                // 显示进度条
                Console.Write("进度条: [");
                int filled = (int)totalScore;
                for (int i = 0; i < filled; i++)
                {
                    Console.Write("=");
                }
                for (int i = filled; i < 7; i++)
                {
                    Console.Write("-");
                }
                Console.WriteLine("]");

                Console.WriteLine();
                Console.WriteLine("========================================");
                Console.WriteLine("            检测完成");
                Console.WriteLine("========================================");
                Console.WriteLine();
                Console.WriteLine("[提示] 以上评分仅供参考，实际安全性还需结合其他因素综合评估。");
            }
        }
    }
}
