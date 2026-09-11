/*
 * ============================================================
 * 文件名：hash_cracker.cs
 * 功能描述：哈希破解工具（MD5/SHA1 字典攻击，安全研究用）
 * 作者：网络安全学习笔记
 * 日期：2026-09-10
 * ============================================================
 *
 * 【使用说明】
 * 1. 编译运行：
 *    dotnet new console -n HashCracker
 *    将本文件替换 Program.cs，然后 dotnet run
 * 2. 或直接使用 csc 编译：
 *    csc hash_cracker.cs
 * 3. 命令行参数：
 *    参数1：哈希类型（md5 或 sha1）
 *    参数2：目标哈希值
 *    参数3：字典文件路径（可选，默认使用内置字典）
 *
 * 【示例】
 *   hash_cracker.exe md5 5f4dcc3b5aa765d61d8327deb882cf99
 *   hash_cracker.exe sha1 5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8 wordlist.txt
 *   dotnet run -- md5 5f4dcc3b5aa765d61d8327deb882cf99
 *
 * 【工作原理】
 *   1. 读取字典中的每个密码
 *   2. 使用 MD5 或 SHA1 算法计算密码的哈希值
 *   3. 将计算结果与目标哈希值比较
 *   4. 如果匹配，则找到原始密码
 *
 * 【免责声明】
 *   本工具仅供密码学学习和安全研究使用。
 *   用于测试自己系统的密码强度，了解弱口令的危害。
 *   禁止用于破解他人密码或进行未授权的活动。
 *   使用本工具请遵守当地法律法规。
 * ============================================================
 */

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;

// 命名空间
namespace HashCracker
{
    // 破解结果类
    public class CrackResult
    {
        public bool Found { get; set; }       // 是否找到密码
        public string Password { get; set; }  // 找到的密码
        public int Attempts { get; set; }     // 尝试次数
        public double TimeUsed { get; set; }  // 用时（秒）
    }

    // 主程序类
    class Program
    {
        // 内置弱口令字典
        // 包含常见的弱密码，用于测试和学习
        private static readonly string[] BuiltinWordlist = new string[]
        {
            "123456", "password", "12345678", "qwerty", "123456789",
            "12345", "1234", "111111", "1234567", "dragon",
            "123123", "baseball", "iloveyou", "trustno1", "sunshine",
            "princess", "admin", "welcome", "shadow", "superman",
            "michael", "football", "abc123", "monkey", "letmein",
            "696969", "master", "login", "mustang", "batman",
            "access", "hello", "charlie", "donald", "qwertyuiop",
            "passw0rd", "000000", "123321", "654321", "qazwsx",
            "123qwe", "password1", "123456a", "a123456", "1234567890",
            "test", "root", "toor", "administrator", "guest"
        };

        /// <summary>
        /// 计算字符串的 MD5 哈希值
        /// </summary>
        /// <param name="input">输入字符串</param>
        /// <returns>32 位小写十六进制 MD5 值</returns>
        private static string ComputeMD5(string input)
        {
            // 使用 MD5 加密服务提供程序
            using (MD5 md5 = MD5.Create())
            {
                // 将字符串转换为字节数组
                byte[] inputBytes = Encoding.UTF8.GetBytes(input);

                // 计算哈希值
                byte[] hashBytes = md5.ComputeHash(inputBytes);

                // 将字节数组转换为十六进制字符串
                StringBuilder sb = new StringBuilder();
                for (int i = 0; i < hashBytes.Length; i++)
                {
                    // X2 表示两位十六进制，小写
                    sb.Append(hashBytes[i].ToString("x2"));
                }

                return sb.ToString();
            }
        }

        /// <summary>
        /// 计算字符串的 SHA1 哈希值
        /// </summary>
        /// <param name="input">输入字符串</param>
        /// <returns>40 位小写十六进制 SHA1 值</returns>
        private static string ComputeSHA1(string input)
        {
            // 使用 SHA1 加密服务提供程序
            using (SHA1 sha1 = SHA1.Create())
            {
                // 将字符串转换为字节数组
                byte[] inputBytes = Encoding.UTF8.GetBytes(input);

                // 计算哈希值
                byte[] hashBytes = sha1.ComputeHash(inputBytes);

                // 将字节数组转换为十六进制字符串
                StringBuilder sb = new StringBuilder();
                for (int i = 0; i < hashBytes.Length; i++)
                {
                    sb.Append(hashBytes[i].ToString("x2"));
                }

                return sb.ToString();
            }
        }

        /// <summary>
        /// 从文件加载字典
        /// </summary>
        /// <param name="filePath">字典文件路径</param>
        /// <returns>密码列表</returns>
        private static List<string> LoadWordlistFromFile(string filePath)
        {
            var wordlist = new List<string>();

            try
            {
                // 读取文件所有行
                string[] lines = File.ReadAllLines(filePath, Encoding.UTF8);

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
        /// MD5 字典攻击
        /// </summary>
        /// <param name="targetHash">目标哈希值</param>
        /// <param name="wordlist">字典列表</param>
        /// <returns>破解结果</returns>
        private static CrackResult CrackMD5(string targetHash, List<string> wordlist)
        {
            var result = new CrackResult
            {
                Found = false,
                Password = "",
                Attempts = 0
            };

            // 将目标哈希转为小写，便于比较
            string targetLower = targetHash.ToLower();

            // 记录开始时间
            Stopwatch stopwatch = Stopwatch.StartNew();

            // 遍历字典中的每个密码
            foreach (string password in wordlist)
            {
                result.Attempts++;

                // 计算当前密码的 MD5 哈希
                string hash = ComputeMD5(password);

                // 比较哈希值
                if (hash == targetLower)
                {
                    result.Found = true;
                    result.Password = password;
                    break;
                }

                // 每尝试 1000 个显示进度
                if (result.Attempts % 1000 == 0)
                {
                    Console.WriteLine($"  ... 已尝试 {result.Attempts} 个密码");
                }
            }

            // 停止计时
            stopwatch.Stop();
            result.TimeUsed = stopwatch.Elapsed.TotalSeconds;

            return result;
        }

        /// <summary>
        /// SHA1 字典攻击
        /// </summary>
        /// <param name="targetHash">目标哈希值</param>
        /// <param name="wordlist">字典列表</param>
        /// <returns>破解结果</returns>
        private static CrackResult CrackSHA1(string targetHash, List<string> wordlist)
        {
            var result = new CrackResult
            {
                Found = false,
                Password = "",
                Attempts = 0
            };

            // 将目标哈希转为小写
            string targetLower = targetHash.ToLower();

            Stopwatch stopwatch = Stopwatch.StartNew();

            foreach (string password in wordlist)
            {
                result.Attempts++;

                // 计算当前密码的 SHA1 哈希
                string hash = ComputeSHA1(password);

                // 比较哈希值
                if (hash == targetLower)
                {
                    result.Found = true;
                    result.Password = password;
                    break;
                }

                if (result.Attempts % 1000 == 0)
                {
                    Console.WriteLine($"  ... 已尝试 {result.Attempts} 个密码");
                }
            }

            stopwatch.Stop();
            result.TimeUsed = stopwatch.Elapsed.TotalSeconds;

            return result;
        }

        static void Main(string[] args)
        {
            Console.WriteLine("========================================");
            Console.WriteLine("   哈希破解工具（C# 字典攻击版）");
            Console.WriteLine("========================================");

            // ===================== 参数检查 =====================
            if (args.Length < 2)
            {
                Console.WriteLine("用法: hash_cracker.exe <哈希类型> <目标哈希> [字典文件]");
                Console.WriteLine("哈希类型: md5 或 sha1");
                Console.WriteLine();
                Console.WriteLine("示例:");
                Console.WriteLine("  hash_cracker.exe md5 5f4dcc3b5aa765d61d8327deb882cf99");
                Console.WriteLine("  hash_cracker.exe sha1 <hash> wordlist.txt");
                Console.WriteLine();
                Console.WriteLine("测试用例（密码是 password）:");
                Console.WriteLine("  MD5:  5f4dcc3b5aa765d61d8327deb882cf99");
                Console.WriteLine("  SHA1: 5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8");
                return;
            }

            // 解析参数
            string hashType = args[0].ToLower();  // 哈希类型（转小写）
            string targetHash = args[1];          // 目标哈希值
            string wordlistFile = args.Length >= 3 ? args[2] : "";  // 字典文件

            // 校验哈希类型
            if (hashType != "md5" && hashType != "sha1")
            {
                Console.WriteLine($"[错误] 不支持的哈希类型: {hashType}（仅支持 md5 或 sha1）");
                return;
            }

            // 校验哈希长度
            if (hashType == "md5" && targetHash.Length != 32)
            {
                Console.WriteLine("[错误] MD5 哈希长度应为 32 位");
                return;
            }
            if (hashType == "sha1" && targetHash.Length != 40)
            {
                Console.WriteLine("[错误] SHA1 哈希长度应为 40 位");
                return;
            }

            // ===================== 加载字典 =====================
            List<string> wordlist;

            if (!string.IsNullOrEmpty(wordlistFile))
            {
                // 从文件加载字典
                wordlist = LoadWordlistFromFile(wordlistFile);
                if (wordlist.Count == 0)
                {
                    Console.WriteLine("[错误] 字典文件为空或加载失败");
                    return;
                }
                Console.WriteLine($"[*] 已加载字典文件: {wordlistFile}");
            }
            else
            {
                // 使用内置字典
                wordlist = new List<string>(BuiltinWordlist);
                Console.WriteLine("[*] 使用内置弱口令字典");
            }

            // ===================== 打印信息 =====================
            Console.WriteLine("----------------------------------------");
            Console.WriteLine($"哈希类型: {hashType.ToUpper()}");
            Console.WriteLine($"目标哈希: {targetHash}");
            Console.WriteLine($"字典大小: {wordlist.Count} 条");
            Console.WriteLine("========================================");
            Console.WriteLine("[*] 开始破解...");
            Console.WriteLine("----------------------------------------");

            // ===================== 执行破解 =====================
            CrackResult result;

            if (hashType == "md5")
            {
                result = CrackMD5(targetHash, wordlist);
            }
            else
            {
                result = CrackSHA1(targetHash, wordlist);
            }

            // ===================== 输出结果 =====================
            Console.WriteLine("----------------------------------------");
            Console.WriteLine();
            Console.WriteLine("========================================");
            Console.WriteLine("            破解结果");
            Console.WriteLine("========================================");

            if (result.Found)
            {
                Console.WriteLine("[成功] 密码已找到！");
                Console.WriteLine("----------------------------------------");
                Console.WriteLine($"原始密码: {result.Password}");
                Console.WriteLine($"目标哈希: {targetHash}");
                Console.WriteLine($"尝试次数: {result.Attempts}");
                Console.WriteLine($"用时: {result.TimeUsed:F2} 秒");

                if (result.TimeUsed > 0)
                {
                    Console.WriteLine($"速度: {(int)(result.Attempts / result.TimeUsed)} 次/秒");
                }
            }
            else
            {
                Console.WriteLine("[失败] 未在字典中找到匹配的密码");
                Console.WriteLine("----------------------------------------");
                Console.WriteLine($"尝试次数: {result.Attempts}");
                Console.WriteLine($"用时: {result.TimeUsed:F2} 秒");
                Console.WriteLine();
                Console.WriteLine("[提示] 可能的原因:");
                Console.WriteLine("  1. 密码不在字典中");
                Console.WriteLine("  2. 哈希值不正确");
                Console.WriteLine("  3. 使用了其他哈希算法");
            }

            Console.WriteLine("========================================");
        }
    }
}
