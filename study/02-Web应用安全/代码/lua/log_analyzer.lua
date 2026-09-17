--[[
================================================================================
  日志分析工具 - log_analyzer.lua
================================================================================
  功能说明：
    本脚本用于分析 Web 服务器访问日志（access.log），进行安全分析：
    1. 统计访问 IP 地址及访问次数
    2. 统计 HTTP 状态码分布
    3. 统计访问路径排名
    4. 检测 SQL 注入攻击特征
    5. 检测 XSS 攻击特征
    6. 检测扫描器/爬虫特征

  日志格式：
    支持标准 Apache/Nginx Combined Log Format：
    IP - - [时间] "方法 路径 协议" 状态码 大小 "Referer" "User-Agent"

  使用方法：
    lua log_analyzer.lua <日志文件路径> [选项]

  示例：
    -- 分析日志文件（完整分析）
    lua log_analyzer.lua access.log

    -- 仅显示攻击检测结果
    lua log_analyzer.lua access.log --attacks

    -- 显示前 20 个 IP
    lua log_analyzer.lua access.log --top 20

    -- 显示帮助
    lua log_analyzer.lua --help

  免责声明：
    本脚本仅供安全学习和授权的日志分析使用。
    攻击特征检测基于正则匹配，可能存在误报和漏报，
    仅供安全研究参考，不可作为唯一检测依据。
    使用本脚本造成的一切后果由使用者自行承担。
================================================================================
--]]

-- ============================================================
-- SQL 注入攻击特征模式
-- 这些模式用于检测常见的 SQL 注入尝试
-- ============================================================
local sql_injection_patterns = {
    -- 关键字注入
    "'%s*or%s*['\"]?1['\"]?%s*=%s*['\"]?1",     -- ' or '1'='1
    "'%s*or%s*1%s*=%s*1",                          -- ' or 1=1
    "union%s+select",                               -- UNION SELECT
    "select%s+.*%s+from",                           -- SELECT ... FROM
    "drop%s+table",                                 -- DROP TABLE
    "insert%s+into",                                -- INSERT INTO
    "delete%s+from",                                -- DELETE FROM
    "update%s+.*%s+set",                            -- UPDATE ... SET
    "--%s*$",                                       -- SQL 注释
    ";%s*drop",                                     -- ; DROP
    "'%s*;%s*--",                                   -- '; --
    "xp_cmdshell",                                  -- 存储过程注入
    "information_schema",                           -- 信息_schema
    "sleep%(",                                      -- 时间盲注
    "benchmark%(",                                  -- 时间盲注
    "concat%(",                                     -- 字符串拼接
    "char%(",                                       -- CHAR 函数
    "ascii%(",                                      -- ASCII 函数
    "substring%(",                                  -- 子串函数
    "'%s+and%s+",                                   -- ' AND
    "%%27%s*or",                                    -- URL编码的单引号 OR
}

-- ============================================================
-- XSS 攻击特征模式
-- 这些模式用于检测常见的 XSS 攻击尝试
-- ============================================================
local xss_patterns = {
    "<script",                              -- <script 标签
    "</script>",                            -- </script> 闭合标签
    "javascript:",                          -- javascript: 伪协议
    "onerror%s*=",                          -- onerror 事件
    "onload%s*=",                           -- onload 事件
    "onclick%s*=",                          -- onclick 事件
    "onmouseover%s*=",                      -- onmouseover 事件
    "onfocus%s*=",                          -- onfocus 事件
    "onblur%s*=",                           -- onblur 事件
    "onchange%s*=",                         -- onchange 事件
    "onsubmit%s*=",                         -- onsubmit 事件
    "eval%(",                               -- eval 函数
    "alert%(",                              -- alert 函数
    "document%.cookie",                     -- document.cookie
    "document%.write",                      -- document.write
    "window%.location",                     -- window.location
    "<img[^>]*src%s*=%s*[\"']javascript:", -- img 标签 XSS
    "<iframe",                              -- iframe 标签
    "<svg[^>]*on",                          -- SVG XSS
    "&#x",                                  -- HTML 实体编码
    "%3Cscript",                            -- URL编码的 <script
    "%3C/script",                           -- URL编码的 </script
}

-- ============================================================
-- 扫描器/爬虫特征模式
-- ============================================================
local scanner_patterns = {
    "sqlmap",          -- sqlmap 扫描器
    "nmap",            -- nmap 扫描器
    "nikto",           -- Nikto 扫描器
    "nessus",          -- Nessus 扫描器
    "acunetix",        -- Acunetix 扫描器
    "burpsuite",       -- Burp Suite
    "dirbuster",       -- DirBuster
    "gobuster",        -- Gobuster
    "wfuzz",           -- Wfuzz
    "masscan",         -- Masscan
    "zaproxy",         -- OWASP ZAP
    "python%-requests", -- Python requests 库
    "curl/",           -- curl 命令行
    "wget/",           -- wget 命令行
}

-- ============================================================
-- 解析单行日志
-- 支持标准 Combined Log Format
-- 参数：line - 日志行
-- 返回：解析后的日志信息表，解析失败返回 nil
-- ============================================================
function parse_log_line(line)
    -- 日志格式：IP - - [时间] "方法 路径 协议" 状态码 大小 "Referer" "User-Agent"
    -- 示例：192.168.1.1 - - [10/Sep/2023:10:30:00 +0800] "GET /index.html HTTP/1.1" 200 1234 "-" "Mozilla/5.0"

    local pattern = '^(%S+)%s+%S+%s+%S+%s+%[([^%]]+)%]%s+"(%S+)%s+(%S+)%s+(%S+)"%s+(%d+)%s+(%d+|-)%s+"([^"]*)"%s+"([^"]*)"'

    local ip, time, method, path, protocol, status, size, referer, user_agent = string.match(line, pattern)

    if not ip then
        -- 尝试匹配更简单的格式（Common Log Format，没有 Referer 和 UA）
        pattern = '^(%S+)%s+%S+%s+%S+%s+%[([^%]]+)%]%s+"(%S+)%s+(%S+)%s+(%S+)"%s+(%d+)%s+(%d+|-)'
        ip, time, method, path, protocol, status, size = string.match(line, pattern)
        referer = "-"
        user_agent = "-"
    end

    if ip then
        return {
            ip = ip,
            time = time,
            method = method,
            path = path,
            protocol = protocol,
            status = tonumber(status),
            size = size,
            referer = referer,
            user_agent = user_agent,
            raw = line
        }
    end

    return nil
end

-- ============================================================
-- 检测攻击特征
-- 参数：log_entry - 解析后的日志条目
-- 返回：攻击类型列表
-- ============================================================
function detect_attacks(log_entry)
    local attacks = {}
    local path = log_entry.path
    local ua = log_entry.user_agent or ""
    local ref = log_entry.referer or ""

    -- 同时检查路径、Referer 和 User-Agent
    local check_str = path .. " " .. ref .. " " .. ua

    -- 检测 SQL 注入
    for _, pattern in ipairs(sql_injection_patterns) do
        if string.match(string.lower(check_str), pattern) then
            table.insert(attacks, "SQL注入")
            break  -- 每种攻击类型只记录一次
        end
    end

    -- 检测 XSS
    for _, pattern in ipairs(xss_patterns) do
        if string.match(string.lower(check_str), pattern) then
            table.insert(attacks, "XSS")
            break
        end
    end

    -- 检测扫描器
    for _, pattern in ipairs(scanner_patterns) do
        if string.match(string.lower(check_str), pattern) then
            table.insert(attacks, "扫描器")
            break
        end
    end

    return attacks
end

-- ============================================================
-- 统计函数：向统计表中添加条目
-- ============================================================
function increment_stat(tbl, key)
    if tbl[key] then
        tbl[key] = tbl[key] + 1
    else
        tbl[key] = 1
    end
end

-- ============================================================
-- 按值排序并返回前 N 个
-- ============================================================
function top_n(tbl, n)
    local arr = {}
    for k, v in pairs(tbl) do
        table.insert(arr, {key = k, value = v})
    end
    table.sort(arr, function(a, b) return a.value > b.value end)

    local result = {}
    for i = 1, math.min(n, #arr) do
        table.insert(result, arr[i])
    end
    return result
end

-- ============================================================
-- 分析日志文件
-- ============================================================
function analyze_log(filepath, options)
    local file = io.open(filepath, "r")
    if not file then
        print("[错误] 无法打开文件: " .. filepath)
        return nil
    end

    -- 初始化统计数据
    local stats = {
        total_lines = 0,
        parsed_lines = 0,
        failed_lines = 0,
        ip_stats = {},
        status_stats = {},
        path_stats = {},
        method_stats = {},
        attack_records = {},
        attack_type_counts = {},
    }

    -- 逐行读取并分析
    for line in file:lines() do
        stats.total_lines = stats.total_lines + 1

        -- 跳过空行
        if line == "" then
            goto continue
        end

        -- 解析日志行
        local entry = parse_log_line(line)
        if not entry then
            stats.failed_lines = stats.failed_lines + 1
            goto continue
        end

        stats.parsed_lines = stats.parsed_lines + 1

        -- 统计 IP
        increment_stat(stats.ip_stats, entry.ip)

        -- 统计状态码
        increment_stat(stats.status_stats, entry.status)

        -- 统计路径（去除查询参数）
        local path_only = string.match(entry.path, "^([^%?]+)") or entry.path
        increment_stat(stats.path_stats, path_only)

        -- 统计请求方法
        increment_stat(stats.method_stats, entry.method)

        -- 攻击检测
        local attacks = detect_attacks(entry)
        if #attacks > 0 then
            table.insert(stats.attack_records, {
                ip = entry.ip,
                path = entry.path,
                attacks = attacks,
                time = entry.time,
                status = entry.status,
            })
            for _, atk in ipairs(attacks) do
                increment_stat(stats.attack_type_counts, atk)
            end
        end

        ::continue::
    end

    file:close()
    return stats
end

-- ============================================================
-- 打印分析报告
-- ============================================================
function print_report(stats, options)
    local top_n_count = options.top_n or 10
    local only_attacks = options.only_attacks or false

    print("================================================================")
    print("  日志分析报告")
    print("================================================================")
    print("")
    print("  总日志行数:   " .. stats.total_lines)
    print("  成功解析:     " .. stats.parsed_lines)
    print("  解析失败:     " .. stats.failed_lines)
    print("")

    if not only_attacks then
        -- IP 统计
        print("----------------------------------------------------------------")
        print("  Top " .. top_n_count .. " 访问 IP")
        print("----------------------------------------------------------------")
        local top_ips = top_n(stats.ip_stats, top_n_count)
        for i, item in ipairs(top_ips) do
            print(string.format("  %2d. %-20s %d 次", i, item.key, item.value))
        end
        print("")

        -- 状态码统计
        print("----------------------------------------------------------------")
        print("  HTTP 状态码分布")
        print("----------------------------------------------------------------")
        for code, count in pairs(stats.status_stats) do
            local desc = ""
            if code >= 200 and code < 300 then
                desc = "（成功）"
            elseif code >= 300 and code < 400 then
                desc = "（重定向）"
            elseif code >= 400 and code < 500 then
                desc = "（客户端错误）"
            elseif code >= 500 then
                desc = "（服务器错误）"
            end
            print(string.format("  %d %-20s %d 次", code, desc, count))
        end
        print("")

        -- 路径统计
        print("----------------------------------------------------------------")
        print("  Top " .. top_n_count .. " 访问路径")
        print("----------------------------------------------------------------")
        local top_paths = top_n(stats.path_stats, top_n_count)
        for i, item in ipairs(top_paths) do
            print(string.format("  %2d. %-40s %d 次", i, item.key, item.value))
        end
        print("")

        -- 请求方法统计
        print("----------------------------------------------------------------")
        print("  请求方法分布")
        print("----------------------------------------------------------------")
        for method, count in pairs(stats.method_stats) do
            print(string.format("  %-10s %d 次", method, count))
        end
        print("")
    end

    -- 攻击检测结果
    print("----------------------------------------------------------------")
    print("  攻击检测结果")
    print("----------------------------------------------------------------")
    if #stats.attack_records == 0 then
        print("  未检测到明显的攻击特征")
    else
        print("  检测到 " .. #stats.attack_records .. " 条可疑记录")
        print("")

        -- 攻击类型统计
        print("  攻击类型统计:")
        for atk_type, count in pairs(stats.attack_type_counts) do
            print(string.format("    %-15s %d 次", atk_type, count))
        end
        print("")

        -- 显示前 N 条攻击记录
        print("  可疑记录详情（前 " .. math.min(20, #stats.attack_records) .. " 条）:")
        for i = 1, math.min(20, #stats.attack_records) do
            local rec = stats.attack_records[i]
            local atk_str = table.concat(rec.attacks, ", ")
            print(string.format("  %2d. [%s] %s -> %s [%s] (%s)",
                i, rec.time or "?", rec.ip, rec.path, atk_str, rec.status))
        end
    end
    print("")
    print("================================================================")
    print("  注意：攻击检测基于特征匹配，可能存在误报和漏报")
    print("================================================================")
end

-- ============================================================
-- 打印帮助信息
-- ============================================================
function print_help()
    print("================================================")
    print("  日志分析工具 - 安全研究用")
    print("================================================")
    print("")
    print("用法: lua log_analyzer.lua <日志文件> [选项]")
    print("")
    print("选项:")
    print("  --attacks      仅显示攻击检测结果")
    print("  --top <数量>   显示前 N 个条目（默认 10）")
    print("  --help, -h     显示帮助信息")
    print("")
    print("支持的日志格式:")
    print("  Apache/Nginx Combined Log Format")
    print("  Common Log Format")
    print("")
    print("示例:")
    print("  lua log_analyzer.lua access.log")
    print("  lua log_analyzer.lua access.log --top 20")
    print("  lua log_analyzer.lua access.log --attacks")
    print("================================================")
end

-- ============================================================
-- 主程序入口
-- ============================================================
function main(...)
    local args = {...}

    -- 解析参数
    local filepath = nil
    local options = {
        top_n = 10,
        only_attacks = false,
    }

    local i = 1
    while i <= #args do
        local arg = args[i]
        if arg == "--help" or arg == "-h" then
            print_help()
            return
        elseif arg == "--attacks" then
            options.only_attacks = true
        elseif arg == "--top" then
            i = i + 1
            if i <= #args then
                options.top_n = tonumber(args[i]) or 10
            end
        elseif not filepath then
            filepath = arg
        end
        i = i + 1
    end

    if not filepath then
        print("[错误] 请提供日志文件路径")
        print("输入 'lua log_analyzer.lua --help' 查看帮助")
        return
    end

    print("[信息] 正在分析日志文件: " .. filepath)
    local stats = analyze_log(filepath, options)

    if stats then
        print_report(stats, options)
    end
end

-- 运行主程序
main(...)
