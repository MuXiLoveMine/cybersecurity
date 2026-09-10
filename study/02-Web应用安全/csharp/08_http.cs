// ============================================================
// 08_http.cs - HttpClient 网络请求：GET、POST、JSON、自定义Header
// 运行方式：dotnet run --project .  或  csc 08_http.cs && 08_http.exe
// ============================================================

using System;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

// ============================================================
// 注意：HttpClient 设计为单例模式，整个应用共享一个实例
// 不要每次请求都 new 一个新的 HttpClient
// ============================================================
static readonly HttpClient _httpClient = new HttpClient
{
    Timeout = TimeSpan.FromSeconds(30)  // 设置超时时间
};

// 设置默认 User-Agent
_httpClient.DefaultRequestHeaders.Add("User-Agent", "CSharp-HttpDemo/1.0");

// ---------- 1. GET 请求 ----------
Console.WriteLine("========== 1. GET 请求 ==========");

await GetExampleAsync();

Console.WriteLine();

// ---------- 2. GET 请求获取 JSON 并反序列化 ----------
Console.WriteLine("========== 2. GET + JSON 反序列化 ==========");

await GetJsonExampleAsync();

Console.WriteLine();

// ---------- 3. POST 请求（JSON） ----------
Console.WriteLine("========== 3. POST 请求（JSON） ==========");

await PostJsonExampleAsync();

Console.WriteLine();

// ---------- 4. POST 请求（表单数据） ----------
Console.WriteLine("========== 4. POST 请求（表单数据） ==========");

await PostFormExampleAsync();

Console.WriteLine();

// ---------- 5. 自定义 Header ----------
Console.WriteLine("========== 5. 自定义 Header ==========");

await CustomHeadersExampleAsync();

Console.WriteLine();

// ---------- 6. 响应处理（状态码、Header） ----------
Console.WriteLine("========== 6. 响应处理 ==========");

await ResponseHandlingExampleAsync();

Console.WriteLine();

// ---------- 7. 异常处理 ----------
Console.WriteLine("========== 7. 异常处理 ==========");

await ExceptionHandlingExampleAsync();

Console.WriteLine();

// ---------- 8. 安全领域：HTTP 请求工具示例 ----------
Console.WriteLine("========== 8. 安全领域应用示例 ==========");

await SecurityExampleAsync();

Console.WriteLine();
Console.WriteLine("========== 程序结束 ==========");

// ============================================================
// 方法定义
// ============================================================

// 1. GET 请求示例
static async Task GetExampleAsync()
{
    string url = "https://httpbin.org/get";
    Console.WriteLine($"请求 URL：{url}");

    try
    {
        // GetStringAsync：直接获取字符串响应
        string responseBody = await _httpClient.GetStringAsync(url);
        Console.WriteLine("响应内容：");
        Console.WriteLine(responseBody);
    }
    catch (HttpRequestException ex)
    {
        Console.WriteLine($"请求失败：{ex.Message}");
    }
}

// 2. GET + JSON 反序列化示例
static async Task GetJsonExampleAsync()
{
    string url = "https://httpbin.org/get";
    Console.WriteLine($"请求 URL：{url}");

    try
    {
        // 先获取 JSON 字符串
        string json = await _httpClient.GetStringAsync(url);

        // 使用 System.Text.Json 反序列化
        var options = new JsonSerializerOptions
        {
            PropertyNameCaseInsensitive = true  // 忽略大小写
        };
        HttpBinResponse? response = JsonSerializer.Deserialize<HttpBinResponse>(json, options);

        if (response != null)
        {
            Console.WriteLine($"来源 IP：{response.Origin}");
            Console.WriteLine($"User-Agent：{response.Headers?.UserAgent}");
            Console.WriteLine($"URL：{response.Url}");
        }
        else
        {
            Console.WriteLine("JSON 反序列化失败");
        }
    }
    catch (JsonException ex)
    {
        Console.WriteLine($"JSON 解析失败：{ex.Message}");
    }
    catch (HttpRequestException ex)
    {
        Console.WriteLine($"请求失败：{ex.Message}");
    }
}

// 3. POST JSON 示例
static async Task PostJsonExampleAsync()
{
    string url = "https://httpbin.org/post";
    Console.WriteLine($"请求 URL：{url}");

    try
    {
        // 创建请求数据对象
        var postData = new
        {
            username = "admin",
            password = "123456",
            email = "admin@example.com",
            age = 25
        };

        // 序列化为 JSON
        string json = JsonSerializer.Serialize(postData, new JsonSerializerOptions
        {
            WriteIndented = true  // 格式化输出
        });
        Console.WriteLine("POST 数据：");
        Console.WriteLine(json);

        // 创建 StringContent（application/json）
        var content = new StringContent(json, Encoding.UTF8, "application/json");

        // 发送 POST 请求
        HttpResponseMessage response = await _httpClient.PostAsync(url, content);
        response.EnsureSuccessStatusCode();  // 确保成功（非 2xx 会抛异常）

        // 读取响应
        string responseBody = await response.Content.ReadAsStringAsync();
        Console.WriteLine("\n响应内容：");
        Console.WriteLine(responseBody);
    }
    catch (HttpRequestException ex)
    {
        Console.WriteLine($"请求失败：{ex.Message}");
    }
}

// 4. POST 表单数据示例
static async Task PostFormExampleAsync()
{
    string url = "https://httpbin.org/post";
    Console.WriteLine($"请求 URL：{url}");

    try
    {
        // 表单数据键值对
        var formData = new Dictionary<string, string>
        {
            ["username"] = "testuser",
            ["password"] = "testpass",
            ["remember"] = "1",
            ["submit"] = "登录"
        };

        // 使用 FormUrlEncodedContent
        var content = new FormUrlEncodedContent(formData);

        Console.WriteLine("提交表单数据：");
        foreach (var kvp in formData)
        {
            Console.WriteLine($"  {kvp.Key} = {kvp.Value}");
        }

        // 发送 POST 请求
        HttpResponseMessage response = await _httpClient.PostAsync(url, content);
        response.EnsureSuccessStatusCode();

        string responseBody = await response.Content.ReadAsStringAsync();
        Console.WriteLine("\n响应：");
        Console.WriteLine(responseBody);
    }
    catch (HttpRequestException ex)
    {
        Console.WriteLine($"请求失败：{ex.Message}");
    }
}

// 5. 自定义 Header 示例
static async Task CustomHeadersExampleAsync()
{
    string url = "https://httpbin.org/headers";
    Console.WriteLine($"请求 URL：{url}");

    try
    {
        // 使用 HttpRequestMessage 自定义请求
        var request = new HttpRequestMessage(HttpMethod.Get, url);

        // 添加自定义 Header
        request.Headers.Add("X-Custom-Header", "MyCustomValue");
        request.Headers.Add("X-Request-Id", Guid.NewGuid().ToString());
        request.Headers.Referrer = new Uri("https://example.com/referer");

        // 添加 Authorization Header
        request.Headers.Authorization = new AuthenticationHeaderValue(
            "Bearer", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...");

        // 添加 Accept Header
        request.Headers.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));

        Console.WriteLine("自定义请求头：");
        foreach (var header in request.Headers)
        {
            Console.WriteLine($"  {header.Key}: {string.Join(", ", header.Value)}");
        }

        // 发送请求
        HttpResponseMessage response = await _httpClient.SendAsync(request);
        response.EnsureSuccessStatusCode();

        string responseBody = await response.Content.ReadAsStringAsync();
        Console.WriteLine("\n响应（服务器看到的 Headers）：");
        Console.WriteLine(responseBody);
    }
    catch (HttpRequestException ex)
    {
        Console.WriteLine($"请求失败：{ex.Message}");
    }
}

// 6. 响应处理示例
static async Task ResponseHandlingExampleAsync()
{
    string url = "https://httpbin.org/status/200";
    Console.WriteLine($"请求 URL：{url}");

    try
    {
        HttpResponseMessage response = await _httpClient.GetAsync(url);

        // 状态码
        Console.WriteLine($"状态码：{(int)response.StatusCode} {response.StatusCode}");
        Console.WriteLine($"是否成功：{response.IsSuccessStatusCode}");

        // 响应头
        Console.WriteLine("\n响应头：");
        foreach (var header in response.Headers)
        {
            Console.WriteLine($"  {header.Key}: {string.Join(", ", header.Value)}");
        }

        // 内容头
        Console.WriteLine("\n内容头：");
        if (response.Content.Headers.ContentType != null)
        {
            Console.WriteLine($"  Content-Type: {response.Content.Headers.ContentType}");
        }
        Console.WriteLine($"  Content-Length: {response.Content.Headers.ContentLength}");

        // 读取响应内容
        string body = await response.Content.ReadAsStringAsync();
        Console.WriteLine($"\n响应内容长度：{body.Length} 字节");

        // 读取为字节数组
        byte[] bytes = await response.Content.ReadAsByteArrayAsync();
        Console.WriteLine($"字节数组长度：{bytes.Length}");

        // 读取为流
        using var stream = await response.Content.ReadAsStreamAsync();
        using var reader = new StreamReader(stream);
        string streamContent = reader.ReadToEnd();
        Console.WriteLine($"流读取长度：{streamContent.Length}");
    }
    catch (HttpRequestException ex)
    {
        Console.WriteLine($"请求失败：{ex.Message}");
    }
}

// 7. 异常处理示例
static async Task ExceptionHandlingExampleAsync()
{
    // 测试各种异常场景
    string[] testUrls = {
        "https://httpbin.org/status/200",   // 正常
        "https://httpbin.org/status/404",   // 404 Not Found
        "https://httpbin.org/status/500",   // 500 Internal Server Error
        "https://nonexistent-domain-12345.com",  // DNS 错误
    };

    foreach (string url in testUrls)
    {
        Console.WriteLine($"测试：{url}");
        try
        {
            HttpResponseMessage response = await _httpClient.GetAsync(url);

            if (response.IsSuccessStatusCode)
            {
                Console.WriteLine($"  ✓ 成功：{(int)response.StatusCode}");
            }
            else
            {
                Console.WriteLine($"  ✗ 失败：{(int)response.StatusCode} {response.StatusCode}");
                // 不抛异常，手动处理
            }
        }
        catch (HttpRequestException ex)
        {
            Console.WriteLine($"  ✗ 请求异常：{ex.Message}");
        }
        catch (TaskCanceledException ex) when (ex.InnerException is TimeoutException)
        {
            Console.WriteLine($"  ✗ 请求超时：{ex.Message}");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"  ✗ 未知异常：{ex.Message}");
        }
    }

    // EnsureSuccessStatusCode 会抛异常
    Console.WriteLine("\nEnsureSuccessStatusCode 示例：");
    try
    {
        var response = await _httpClient.GetAsync("https://httpbin.org/status/404");
        response.EnsureSuccessStatusCode();  // 404 会抛出 HttpRequestException
    }
    catch (HttpRequestException ex)
    {
        Console.WriteLine($"  捕获到异常：{ex.Message}");
    }
}

// 8. 安全领域应用示例
static async Task SecurityExampleAsync()
{
    Console.WriteLine("安全工具示例：");

    // 示例1：目录探测（简单版）
    Console.WriteLine("\n1. 目录探测示例（模拟）：");
    string baseUrl = "https://httpbin.org/";
    string[] paths = { "get", "post", "admin", "config", "backup" };

    foreach (string path in paths)
    {
        try
        {
            var request = new HttpRequestMessage(HttpMethod.Head, baseUrl + path);
            var response = await _httpClient.SendAsync(request);
            string status = response.IsSuccessStatusCode
                ? $"✓ 存在 ({(int)response.StatusCode})"
                : $"✗ 不存在 ({(int)response.StatusCode})";
            Console.WriteLine($"  {path} -> {status}");
        }
        catch
        {
            Console.WriteLine($"  {path} -> 请求失败");
        }
    }

    // 示例2：HTTP 响应头安全检测
    Console.WriteLine("\n2. HTTP 安全头检测：");
    string targetUrl = "https://httpbin.org/headers";

    try
    {
        var response = await _httpClient.GetAsync(targetUrl);

        string[] securityHeaders = {
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Strict-Transport-Security",
            "Content-Security-Policy",
            "Referrer-Policy"
        };

        Console.WriteLine($"目标：{targetUrl}");
        foreach (string header in securityHeaders)
        {
            bool hasHeader = response.Headers.Contains(header) ||
                           (response.Content.Headers.Contains(header));
            string status = hasHeader ? "✓ 已设置" : "✗ 缺失";
            Console.WriteLine($"  {status}: {header}");
        }

        // 检查 Server 头（信息泄露）
        if (response.Headers.TryGetValues("Server", out var serverValues))
        {
            Console.WriteLine($"  ⚠ 信息泄露: Server: {string.Join(", ", serverValues)}");
        }
    }
    catch (Exception ex)
    {
        Console.WriteLine($"  检测失败：{ex.Message}");
    }

    // 示例3：Web 请求封装类
    Console.WriteLine("\n3. 简单 HTTP 请求工具类使用：");
    var httpTool = new HttpTool(_httpClient);
    var result = await httpTool.GetAsync("https://httpbin.org/get");
    Console.WriteLine($"  状态码：{result.StatusCode}");
    Console.WriteLine($"  响应长度：{result.Body?.Length ?? 0}");
}

// ============================================================
// 辅助类
// ============================================================

// httpbin.org 响应模型
public class HttpBinResponse
{
    public HttpBinHeaders? Headers { get; set; }
    public string? Origin { get; set; }
    public string? Url { get; set; }
}

public class HttpBinHeaders
{
    public string? UserAgent { get; set; }
    public string? Host { get; set; }
}

// HTTP 请求结果
public class HttpResult
{
    public int StatusCode { get; set; }
    public string? Body { get; set; }
    public Dictionary<string, string> Headers { get; set; } = new();
    public bool IsSuccess { get; set; }
}

// HTTP 工具类封装
public class HttpTool
{
    private readonly HttpClient _client;

    public HttpTool(HttpClient client)
    {
        _client = client;
    }

    public async Task<HttpResult> GetAsync(string url)
    {
        var result = new HttpResult();
        try
        {
            var response = await _client.GetAsync(url);
            result.StatusCode = (int)response.StatusCode;
            result.IsSuccess = response.IsSuccessStatusCode;
            result.Body = await response.Content.ReadAsStringAsync();

            foreach (var header in response.Headers)
            {
                result.Headers[header.Key] = string.Join(", ", header.Value);
            }
        }
        catch (Exception ex)
        {
            result.Body = ex.Message;
            result.IsSuccess = false;
        }
        return result;
    }

    public async Task<HttpResult> PostJsonAsync(string url, string json)
    {
        var result = new HttpResult();
        try
        {
            var content = new StringContent(json, Encoding.UTF8, "application/json");
            var response = await _client.PostAsync(url, content);
            result.StatusCode = (int)response.StatusCode;
            result.IsSuccess = response.IsSuccessStatusCode;
            result.Body = await response.Content.ReadAsStringAsync();
        }
        catch (Exception ex)
        {
            result.Body = ex.Message;
            result.IsSuccess = false;
        }
        return result;
    }
}
