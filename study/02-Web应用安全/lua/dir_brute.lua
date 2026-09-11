--[[
================================================================================
  Web 目录爆破工具 - dir_brute.lua
================================================================================
  功能说明：
    本脚本是一个基于 HTTP 请求的 Web 目录扫描/爆破工具，用于安全学习：
    1. 对目标 Web 站点进行目录和文件路径枚举
    2. 内置常见 Web 路径字典（管理后台、配置文件、备份文件等）
    3. 根据 HTTP 响应状态码判断路径是否存在
    4. 支持自定义文件扩展名（如 .php, .html, .txt, .bak 等）
    5. 支持多线程（协程）并发扫描，提高效率
    6. 显示发现的路径及其状态码和响应大小

  依赖说明：
    需要安装 LuaSocket 库。
    - LuaRocks 安装:  luarocks install luasocket

  使用方法：
    lua dir_brute.lua <目标URL> [选项]

  示例：
    -- 基本扫描（使用内置字典）
    lua dir_brute.lua http://example.com/

    -- 指定扩展名扫描
    lua dir_brute.lua http://example.com/ -e php,html,txt

    -- 设置超时和并发数
    lua dir_brute.lua http://example.com/ -t 3 -c 10

    -- 使用自定义字典文件
    lua dir_brute.lua http://example.com/ -w wordlist.txt

    -- 仅显示存在的路径（静默模式）
    lua dir_brute.lua http://example.com/ -q

    -- 显示帮助
    lua dir_brute.lua --help

  免责声明：
    本脚本仅供网络安全学习和授权的安全测试使用。
    未经授权对他人 Web 站点进行目录扫描可能违反相关法律法规。
    使用者需确保已获得目标系统所有者的明确授权。
    使用本脚本造成的一切后果由使用者自行承担。
================================================================================
--]]

-- ============================================================
-- 加载 LuaSocket 库
-- ============================================================
local socket = require("socket")

-- ============================================================
-- 内置常见路径字典
-- 包含常见的 Web 目录、管理后台、配置文件、备份文件等路径
-- ============================================================
local builtin_wordlist = {
    -- 管理后台
    "admin", "admin/", "admin/login", "admin/index",
    "administrator", "administrator/",
    "admin.php", "admin.html", "admin.asp",
    "wp-admin", "wp-admin/", "wp-login.php",
    "manager", "manager/html", "console",

    -- 常见目录
    "backup", "backup/", "backups/",
    "config", "config/", "configuration/",
    "data", "data/", "database/",
    "tmp", "temp", "test", "debug",
    "upload", "uploads/", "files/",
    "images/", "img/", "static/",
    "css/", "js/", "lib/",
    "log", "logs/", "logfile",

    -- 配置文件
    "config.php", "config.ini", "config.json", "config.xml", "config.yml",
    "configuration.php", "settings.php", "settings.json",
    ".env", ".git/config", ".git/HEAD",
    "web.config", "robots.txt", "sitemap.xml",
    "crossdomain.xml", ".htaccess", ".htpasswd",

    -- 备份和压缩文件
    "backup.zip", "backup.tar.gz", "backup.rar", "backup.sql",
    "db.sql", "database.sql", "dump.sql",
    "www.zip", "www.tar.gz", "web.zip",
    "site.zip", "html.zip", "release.zip",

    -- 常见框架入口
    "index.php", "index.html", "index.asp", "index.aspx",
    "info.php", "phpinfo.php", "test.php",
    "login.php", "login.html", "register.php",
    "api", "api/", "api/v1/", "api/v2/",
    "swagger", "swagger-ui", "swagger.json",
    "graphql", "graphiql",

    -- 敏感文件
    ".svn/entries", ".svn/wc.db",
    ".DS_Store", "Thumbs.db",
    "composer.json", "composer.lock",
    "package.json", "package-lock.json",
    "Gemfile", "Gemfile.lock",
    "Dockerfile", "docker-compose.yml",
    "README", "README.md", "CHANGELOG", "LICENSE",

    -- 服务器信息
    "server-status", "server-info",
    "phpmyadmin", "phpmyadmin/",
    "pma", "pma/", "mysqladmin",
    "manager/html", "jmx-console",
    "actuator", "actuator/health", "actuator/env",

    -- 常见 CMS 路径
    "wp-content/", "wp-includes/",
    "wp-config.php", "wp-config.bak",
    "wp-content/uploads/",
    "wp-content/plugins/",
    "wp-content/themes/",
    "xmlrpc.php", "wp-cron.php",
    "wp-trackback.php",

    -- 其他
    "include", "includes/", "inc/",
    "src", "src/", "source/",
    "doc", "docs/", "documentation/",
    "help", "help/",
    "old", "old/", "new/", "v1/", "v2/",
    "cgi-bin/", "cgi-bin/printenv",
    "scripts/", "script/",
    "bin/", "exec/", "run/",
    "vendor/", "node_modules/",
    "storage/", "cache/",
    "session/", "sessions/",
}

-- ============================================================
-- 常见文件扩展名列表
-- 用于在路径后追加扩展名进行探测
-- ============================================================
local default_extensions = { "", ".php", ".html", ".htm", ".txt", ".bak", ".old", ".zip", ".tar.gz" }

-- ============================================================
-- HTTP 状态码含义映射
-- ============================================================
local status_meaning = {
    [200] = "OK - 资源存在",
    [201] = "Created - 资源已创建",
    [204] = "No Content - 无内容",
    [301] = "Moved Permanently - 永久重定向",
    [302] = "Found - 临时重定向",
    [303] = "See Other - 查看其他位置",
    [307] = "Temporary Redirect - 临时重定向",
    [308] = "Permanent Redirect - 永久重定向",
    [400] = "Bad Request - 错误请求",
    [401] = "Unauthorized - 未授权",
    [403] = "Forbidden - 禁止访问",
    [404] = "Not Found - 未找到",
    [405] = "Method Not Allowed - 方法不允许",
    [500] = "Internal Server Error - 服务器内部错误",
    [502] = "Bad Gateway - 网关错误",
    [503] = "Service Unavailable - 服务不可用",
}

-- ============================================================
-- 函数：获取状态码含义
-- @param code HTTP 状态码
-- @return 含义描述字符串
-- ============================================================
local function get_status_meaning(code)
    return status_meaning[code] or "Unknown"
end

-- ============================================================
-- 函数：发送 HTTP GET 请求并获取状态码和响应大小
-- 这是一个精简的 HTTP 客户端，仅获取状态码和内容长度
--
-- @param host    目标主机
-- @param port    目标端口
-- @param path    请求路径
-- @param timeout 超时时间
-- @return status_code, content_length, location(重定向地址)
-- ============================================================
local function http_get(host, port, path, timeout)
    -- 创建 TCP 套接字
    local sock = socket.tcp()
    sock:settimeout(timeout or 5)

    -- 连接服务器
    local ok, err = sock:connect(host, port)
    if not ok then
        sock:close()
        return nil, err
    end

    -- 构建 HTTP GET 请求
    local request = "GET " .. path .. " HTTP/1.1\r\n"
                   .. "Host: " .. host .. "\r\n"
                   .. "User-Agent: Mozilla/5.0 (DirBrute/1.0)\r\n"
                   .. "Accept: */*\r\n"
                   .. "Connection: close\r\n"
                   .. "\r\n"

    -- 发送请求
    local sent, send_err = sock:send(request)
    if not sent then
        sock:close()
        return nil, send_err
    end

    -- 接收响应
    local response = ""
    while true do
        local chunk, recv_err, partial = sock:receive(4096)
        if chunk then
            response = response .. chunk
        else
            response = response .. (partial or "")
            break
        end
    end

    sock:close()

    -- 解析状态码
    -- 响应行格式: HTTP/1.1 200 OK
    local status_code = tonumber(response:match("HTTP/%d%.%d%s+(%d+)"))
    if not status_code then
        return nil, "无法解析状态码"
    end

    -- 解析 Content-Length
    local content_length = tonumber(response:match("[Cc]ontent%-[Ll]ength:%s*(%d+)"))

    -- 如果没有 Content-Length，用响应体大小估算
    if not content_length then
        -- 找到 \r\n\r\n 分隔点后的主体长度
        local _, body_start = response:find("\r\n\r\n")
        if body_start then
            content_length = #response - body_start
        else
            content_length = 0
        end
    end

    -- 解析 Location（重定向地址）
    local location = response:match("[Ll]ocation:%s*(%S+)")

    return status_code, content_length, location
end

-- ============================================================
-- 函数：从文件加载自定义字典
-- @param file_path 字典文件路径
-- @return 路径列表
-- ============================================================
local function load_wordlist(file_path)
    local words = {}
    local file = io.open(file_path, "r")
    if not file then
        return nil, "无法打开字典文件: " .. file_path
    end

    for line in file:lines() do
        -- 去除首尾空白字符，跳过空行和注释
        line = line:match("^%s*(.-)%s*$")
        if line ~= "" and not line:match("^#") then
            table.insert(words, line)
        end
    end

    file:close()
    return words
end

-- ============================================================
-- 函数：解析 URL
-- @param url_str URL 字符串
-- @return scheme, host, port, base_path
-- ============================================================
local function parse_url(url_str)
    -- 解析协议
    local scheme = url_str:match("^(https?)://")
    scheme = scheme or "http"

    -- 去除协议部分
    local rest = url_str:gsub("^https?://", "")

    -- 分离主机和路径
    local host_part, path_part = rest:match("^([^/]+)(/.*)$")
    if not host_part then
        host_part = rest
        path_part = "/"
    end

    -- 分离主机和端口
    local host, port_str = host_part:match("^([^:]+):?(%d*)$")
    local port
    if port_str and port_str ~= "" then
        port = tonumber(port_str)
    else
        port = (scheme == "https") and 443 or 80
    end

    return scheme, host, port, path_part
end

-- ============================================================
-- 函数：打印帮助信息
-- ============================================================
local function print_help()
    print([[
============================================
  Web 目录爆破工具 - dir_brute.lua
============================================

用法:
  lua dir_brute.lua <目标URL> [选项]

选项:
  -w, --wordlist <文件>    自定义字典文件路径（默认使用内置字典）
  -e, --extensions <列表>  文件扩展名，逗号分隔（如: php,html,txt）
  -t, --timeout <秒数>     请求超时时间（默认 5 秒）
  -c, --concurrency <数>   并发请求数（默认 5）
  -q, --quiet             静默模式，仅显示存在的路径
  -s, --show-all          显示所有状态码的结果（包括 404）
  -h, --help              显示帮助

示例:
  lua dir_brute.lua http://example.com/
  lua dir_brute.lua http://example.com/ -e php,html,bak
  lua dir_brute.lua http://example.com/ -w my_wordlist.txt
  lua dir_brute.lua http://example.com/ -t 3 -c 10 -q
]])
end

-- ============================================================
-- 主函数
-- ============================================================
local function main()
    local args = arg
    if #args == 0 or args[1] == "--help" or args[1] == "-h" then
        print_help()
        return
    end

    -- 解析参数
    local target_url = nil
    local wordlist_file = nil
    local extensions = default_extensions
    local timeout = 5
    local concurrency = 5
    local quiet = false
    local show_all = false

    local i = 1
    while i <= #args do
        local a = args[i]
        if a:match("^https?://") then
            target_url = a
            i = i + 1
        elseif a == "-w" or a == "--wordlist" then
            wordlist_file = args[i + 1]
            i = i + 2
        elseif a == "-e" or a == "--extensions" then
            -- 解析扩展名列表
            local ext_str = args[i + 1] or ""
            extensions = {}
            for ext in ext_str:gmatch("([^,]+)") do
                ext = ext:match("^%s*(.-)%s*$")
                -- 确保 . 前缀
                if not ext:match("^%.") then
                    ext = "." .. ext
                end
                table.insert(extensions, ext)
            end
            -- 添加空扩展名（原始路径）
            table.insert(extensions, "")
            i = i + 2
        elseif a == "-t" or a == "--timeout" then
            timeout = tonumber(args[i + 1]) or 5
            i = i + 2
        elseif a == "-c" or a == "--concurrency" then
            concurrency = tonumber(args[i + 1]) or 5
            i = i + 2
        elseif a == "-q" or a == "--quiet" then
            quiet = true
            i = i + 1
        elseif a == "-s" or a == "--show-all" then
            show_all = true
            i = i + 1
        else
            i = i + 1
        end
    end

    -- 校验 URL
    if not target_url then
        print("错误: 请指定目标 URL")
        print_help()
        return
    end

    -- 解析 URL
    local scheme, host, port, base_path = parse_url(target_url)
    if not host then
        print("错误: 无法解析 URL: " .. target_url)
        return
    end

    -- 确保基础路径以 / 结尾
    if not base_path:match("/$") then
        base_path = base_path .. "/"
    end

    -- 加载字典
    local wordlist
    if wordlist_file then
        wordlist = load_wordlist(wordlist_file)
        if not wordlist then
            print("错误: 无法加载字典文件: " .. wordlist_file)
            return
        end
    else
        wordlist = builtin_wordlist
    end

    -- 构建完整探测路径列表（路径 + 扩展名组合）
    local all_paths = {}
    for _, word in ipairs(wordlist) do
        for _, ext in ipairs(extensions) do
            -- 确保路径格式正确
            local path = base_path .. word .. ext
            table.insert(all_paths, path)
        end
    end

    -- 打印扫描头部信息
    print(string.rep("=", 60))
    print("  Web 目录爆破扫描")
    print(string.rep("=", 60))
    print(string.format("  目标:     %s", target_url))
    print(string.format("  主机:     %s:%d", host, port))
    print(string.format("  字典:     %s", wordlist_file or "内置字典"))
    print(string.format("  路径数:   %d", #wordlist))
    print(string.format("  扩展名:   %d 个", #extensions))
    print(string.format("  总请求数: %d", #all_paths))
    print(string.format("  超时:     %d 秒", timeout))
    print(string.rep("=", 60))
    print()
    print(string.format("  %-6s  %-40s  %-10s  %s",
        "状态", "路径", "大小", "说明"))
    print(string.rep("-", 60))

    -- 扫描统计
    local stats = {
        found = 0,     -- 发现的路径数（非 404）
        not_found = 0, -- 404 数量
        errors = 0,    -- 错误数量
        total = #all_paths,
    }

    -- 记录扫描开始时间
    local start_time = socket.gettime()

    -- 逐个发送请求进行扫描
    -- 注意：这里使用顺序请求（Lua 协程实现并发较复杂，简化为顺序请求）
    -- 如需真正并发，可使用 LuaSocket 的 select 配合协程
    for idx, path in ipairs(all_paths) do
        -- 发送 HTTP GET 请求
        local status_code, content_length, location = http_get(host, port, path, timeout)

        if not status_code then
            -- 请求出错
            stats.errors = stats.errors + 1
            if not quiet then
                print(string.format("  %-6s  %-40s  %-10s  %s",
                    "ERR", path:sub(1, 40), "-", content_length or "错误"))
            end
        else
            -- 根据状态码判断
            if status_code == 404 then
                stats.not_found = stats.not_found + 1
                -- 显示 404（仅在 --show-all 模式）
                if show_all and not quiet then
                    print(string.format("  %-6d  %-40s  %-10s  %s",
                        status_code, path:sub(1, 40),
                        (content_length or 0) .. "B", get_status_meaning(status_code)))
                end
            else
                -- 非持续 404，视为发现
                stats.found = stats.found + 1

                -- 获取状态码含义
                local meaning = get_status_meaning(status_code)
                if location then
                    meaning = meaning .. " -> " .. location
                end

                -- 打印发现结果
                print(string.format("  %-6d  %-40s  %-10s  %s",
                    status_code, path:sub(1, 40),
                    (content_length or 0) .. "B", meaning))
            end
        end

        -- 进度显示（每 50 个请求显示一次，非静默模式）
        if not quiet and idx % 50 == 0 then
            io.write(string.format("\r  进度: %d/%d (%.1f%%)  发现: %d",
                idx, stats.total, idx / stats.total * 100, stats.found))
            io.flush()
        end
    end

    -- 清除进度行
    if not quiet then
        io.write("\r" .. string.rep(" ", 60) .. "\r")
    end

    -- 计算总耗时
    local total_time = socket.gettime() - start_time

    -- 打印扫描摘要
    print()
    print(string.rep("=", 60))
    print("  扫描完成 - 结果摘要")
    print(string.rep("=", 60))
    print(string.format("  总耗时:   %.2f 秒", total_time))
    print(string.format("  总请求:   %d", stats.total))
    print(string.format("  发现:     %d 个路径", stats.found))
    print(string.format("  未找到:   %d", stats.not_found))
    print(string.format("  错误:     %d", stats.errors))
    print(string.format("  平均速度: %.1f 请求/秒", stats.total / (total_time > 0 and total_time or 1)))
    print(string.rep("=", 60))
end

-- ============================================================
-- 执行主函数
-- ============================================================
main()
