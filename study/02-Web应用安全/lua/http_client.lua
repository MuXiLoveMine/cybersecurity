--[[
================================================================================
  HTTP 客户端工具 - http_client.lua
================================================================================
  功能说明：
    本脚本是一个基于 LuaSocket 的 HTTP 客户端工具，用于安全研究和学习：
    1. 支持发送 HTTP GET / POST 请求
    2. 解析 HTTP 响应状态码、响应头和响应体
    3. 支持自定义请求头（如 User-Agent、Referer 等）
    4. 支持 Cookie 管理（发送和接收 Cookie）
    5. 支持设置连接超时和读取超时
    6. 支持表单数据（application/x-www-form-urlencoded）提交
    7. 提供响应格式化输出功能

  依赖说明：
    需要安装 LuaSocket 库。
    - LuaRocks 安装:  luarocks install luasocket
    - 或在 Linux 下:  apt-get install lua-socket  (Debian/Ubuntu)

  使用方法：
    lua http_client.lua <方法> <URL> [选项]

  示例：
    -- 发送 GET 请求
    lua http_client.lua get http://example.com/

    -- 发送 GET 请求并自定义 User-Agent
    lua http_client.lua get http://example.com/ -ua "MyBrowser/1.0"

    -- 发送 POST 请求（表单数据）
    lua http_client.lua post http://example.com/login -d "user=admin&pass=123456"

    -- 发送请求并附加自定义 Header
    lua http_client.lua get http://example.com/ -H "X-Custom: value"

    -- 发送请求并携带 Cookie
    lua http_client.lua get http://example.com/ -c "sessionid=abc123"

    -- 发送请求并设置超时（3 秒）
    lua http_client.lua get http://example.com/ -t 3

    -- 显示帮助
    lua http_client.lua --help

  免责声明：
    本脚本仅供网络安全学习和授权的安全测试使用。
    请勿用于未经授权的 Web 应用测试或攻击活动。
    使用本脚本造成的一切后果由使用者自行承担。
================================================================================
--]]

-- ============================================================
-- 加载 LuaSocket 库
-- ============================================================
local socket = require("socket")
local url = require("socket.url")

-- ============================================================
-- HTTP 客户端模块
-- 封装 HTTP 请求的发送和响应解析功能
-- ============================================================
local HTTPClient = {}
HTTPClient.__index = HTTPClient

-- ============================================================
-- 函数：创建 HTTP 客户端实例
-- @param config 配置表（可选）
--   - timeout: 连接和读取超时（秒），默认 10
--   - user_agent: 默认 User-Agent 字符串
--   - cookies: 初始 Cookie 表
-- @return HTTPClient 实例
-- ============================================================
function HTTPClient.new(config)
    config = config or {}
    local self = setmetatable({}, HTTPClient)

    -- 默认配置
    self.timeout = config.timeout or 10
    self.user_agent = config.user_agent or "LuaHTTPClient/1.0"
    self.cookies = config.cookies or {}
    self.default_headers = {
        ["Accept"] = "*/*",
        ["Connection"] = "close",
    }

    return self
end

-- ============================================================
-- 函数：解析 URL，提取协议、主机、端口、路径
-- @param url_str URL 字符串
-- @return 解析结果表，包含 scheme, host, port, path, query
-- ============================================================
function HTTPClient.parse_url(url_str)
    -- 使用 socket.url 解析 URL
    local parsed = url.parse(url_str)

    -- 提取各部分
    local scheme = parsed.scheme or "http"
    local host = parsed.host
    local port = parsed.port
    local path = parsed.path or "/"
    local query = parsed.query

    -- 如果没有指定端口，根据协议使用默认端口
    if not port then
        if scheme == "https" then
            port = 443
        else
            port = 80
        end
    else
        port = tonumber(port)
    end

    -- 拼接完整路径（含查询字符串）
    local full_path = path
    if query then
        full_path = full_path .. "?" .. query
    end

    return {
        scheme = scheme,
        host = host,
        port = port,
        path = full_path,
    }
end

-- ============================================================
-- 函数：构建 Cookie 字符串
-- 将 Cookie 表转换为 HTTP 请求头中的 Cookie 格式
-- @return Cookie 头字符串
-- ============================================================
function HTTPClient:build_cookie_string()
    local parts = {}
    for name, value in pairs(self.cookies) do
        table.insert(parts, name .. "=" .. value)
    end
    return table.concat(parts, "; ")
end

-- ============================================================
-- 函数：解析 Set-Cookie 响应头
-- 从服务器返回的 Set-Cookie 头中提取 Cookie 并保存
-- @param set_cookie_str Set-Cookie 头的值
-- ============================================================
function HTTPClient:parse_set_cookie(set_cookie_str)
    if not set_cookie_str then return end

    -- Set-Cookie 的格式为: name=value; Path=/; HttpOnly
    -- 只提取 name=value 部分
    local name, value = set_cookie_str:match("^([^=]+)=([^;]*)")
    if name and value then
        self.cookies[name:trim and name:trim() or name] = value
    end
end

-- ============================================================
-- 函数：构建 HTTP 请求
-- 根据方法、URL、头部、主体组装完整的 HTTP 请求报文
--
-- @param method  HTTP 方法（GET / POST 等）
-- @param url_str 目标 URL
-- @param headers 自定义请求头表
-- @param body    请求主体（POST 数据等）
-- @return 请求字符串, 解析后的 URL 信息
-- ============================================================
function HTTPClient:build_request(method, url_str, headers, body)
    -- 解析 URL
    local url_info = self.parse_url(url_str)

    -- 合并默认头部和自定义头部
    local all_headers = {}
    for k, v in pairs(self.default_headers) do
        all_headers[k] = v
    end
    if headers then
        for k, v in pairs(headers) do
            all_headers[k] = v
        end
    end

    -- 设置 Host 头
    all_headers["Host"] = url_info.host

    -- 设置 User-Agent（如果未自定义）
    if not all_headers["User-Agent"] then
        all_headers["User-Agent"] = self.user_agent
    end

    -- 设置 Cookie（如果有）
    local cookie_str = self:build_cookie_string()
    if cookie_str ~= "" then
        all_headers["Cookie"] = cookie_str
    end

    -- 如果有请求体，设置 Content-Type 和 Content-Length
    if body then
        if not all_headers["Content-Type"] then
            all_headers["Content-Type"] = "application/x-www-form-urlencoded"
        end
        all_headers["Content-Length"] = tostring(#body)
    end

    -- 组装 HTTP 请求行
    -- 格式: METHOD /path HTTP/1.1
    local request = method:upper() .. " " .. url_info.path .. " HTTP/1.1\r\n"

    -- 添加请求头
    for name, value in pairs(all_headers) do
        request = request .. name .. ": " .. value .. "\r\n"
    end

    -- 空行分隔头部和主体
    request = request .. "\r\n"

    -- 添加请求主体（如果有）
    if body then
        request = request .. body
    end

    return request, url_info
end

-- ============================================================
-- 函数：解析 HTTP 响应
-- 将原始 HTTP 响应文本解析为结构化数据
--
-- @param response_raw 原始响应字符串
-- @return 响应表 { status_code, status_text, headers, body, cookies }
-- ============================================================
function HTTPClient.parse_response(response_raw)
    -- 查找头部和主体的分隔位置（空行 \r\n\r\n）
    local header_end = response_raw:find("\r\n\r\n")
    if not header_end then
        -- 没有找到分隔符，整个响应视为主体
        return {
            status_code = 0,
            status_text = "Invalid Response",
            headers = {},
            body = response_raw,
            raw = response_raw,
        }
    end

    -- 分离头部和主体
    local header_part = response_raw:sub(1, header_end - 1)
    local body_part = response_raw:sub(header_end + 4)

    -- 解析状态行
    -- 格式: HTTP/1.1 200 OK
    local status_line, rest = header_part:match("^(HTTP/%d%.%d%s+(%d+)%s+(.-))\r\n(.*)$")
    local status_code, status_text

    if status_line then
        -- 使用已捕获的值
        local code_str = header_part:match("^HTTP/%d%.%d%s+(%d+)")
        status_code = tonumber(code_str)
        status_text = header_part:match("^HTTP/%d%.%d%s+%d+%s+(.-)\r\n")
        rest = header_part:match("^.-\r\n(.*)$")
    else
        -- 备用解析方式
        status_code = tonumber(header_part:match("HTTP/%d%.%d%s+(%d+)")) or 0
        status_text = header_part:match("HTTP/%d%.%d%s+%d+%s+(.-)\r\n") or "Unknown"
        rest = header_part:match("^.-\r\n(.*)$") or ""
    end

    -- 解析响应头
    local headers = {}
    local cookies = {}

    -- 逐行解析头部字段
    for line in rest:gmatch("([^\r\n]+)") do
        -- 头部格式: Name: Value
        local name, value = line:match("^([^:]+):%s*(.*)$")
        if name and value then
            name = name:lower()  -- 头部名统一转小写，便于查找
            if name == "set-cookie" then
                -- 收集所有 Set-Cookie
                table.insert(cookies, value)
            else
                headers[name] = value
            end
        end
    end

    return {
        status_code = status_code,
        status_text = status_text,
        headers = headers,
        body = body_part,
        cookies = cookies,
        raw = response_raw,
    }
end

-- ============================================================
-- 函数：发送 HTTP 请求
-- 建立 TCP 连接，发送请求，接收响应
--
-- @param method  HTTP 方法
-- @param url_str URL
-- @param headers 自定义请求头（可选）
-- @param body    请求主体（可选）
-- @return 响应表，或 nil + 错误信息
-- ============================================================
function HTTPClient:request(method, url_str, headers, body)
    -- 构建请求报文
    local request, url_info = self:build_request(method, url_str, headers, body)

    -- 创建 TCP 套接字
    local sock = socket.tcp()
    sock:settimeout(self.timeout)

    -- 连接目标服务器
    local ok, err = sock:connect(url_info.host, url_info.port)
    if not ok then
        sock:close()
        return nil, "连接失败: " .. (err or "unknown error")
    end

    -- 发送 HTTP 请求
    local sent, send_err = sock:send(request)
    if not sent then
        sock:close()
        return nil, "发送请求失败: " .. (send_err or "unknown error")
    end

    -- 接收响应数据
    -- 使用 ltn12 风格的逐步接收方式
    local response = ""
    while true do
        local chunk, recv_err, partial = sock:receive(1024)
        if chunk then
            response = response .. chunk
        elseif recv_err == "closed" then
            -- 连接已关闭，附加可能剩余的部分数据
            response = response .. (partial or "")
            break
        elseif recv_err == "timeout" then
            -- 读取超时，附加已接收的部分数据后结束
            response = response .. (partial or "")
            break
        else
            -- 其他错误
            sock:close()
            return nil, "接收响应失败: " .. (recv_err or "unknown error")
        end
    end

    -- 关闭套接字
    sock:close()

    -- 解析响应
    local response_data = self.parse_response(response)

    -- 处理 Set-Cookie，保存到客户端 Cookie 存储
    if response_data.cookies then
        for _, cookie_str in ipairs(response_data.cookies) do
            self:parse_set_cookie(cookie_str)
        end
    end

    return response_data
end

-- ============================================================
-- 函数：发送 GET 请求（便捷方法）
-- ============================================================
function HTTPClient:get(url_str, headers)
    return self:request("GET", url_str, headers, nil)
end

-- ============================================================
-- 函数：发送 POST 请求（便捷方法）
-- @param url_str URL
-- @param data    POST 数据字符串或表
-- @param headers 自定义请求头
-- ============================================================
function HTTPClient:post(url_str, data, headers)
    -- 如果 data 是表，则编码为 URL 格式
    if type(data) == "table" then
        local parts = {}
        for k, v in pairs(data) do
            table.insert(parts, url.escape(k) .. "=" .. url.escape(tostring(v)))
        end
        data = table.concat(parts, "&")
    end
    return self:request("POST", url_str, headers, data)
end

-- ============================================================
-- 函数：格式化打印 HTTP 响应
-- @param resp 响应表
-- @param verbose 是否显示完整响应头和主体
-- ============================================================
local function print_response(resp, verbose)
    if not resp then
        print("  无响应数据")
        return
    end

    -- 打印状态行
    print(string.format("  HTTP 状态码: %d %s", resp.status_code, resp.status_text or ""))

    if verbose then
        -- 打印响应头
        print()
        print("  --- 响应头 ---")
        for name, value in pairs(resp.headers) do
            print(string.format("  %s: %s", name, value))
        end

        -- 打印 Set-Cookie
        if resp.cookies and #resp.cookies > 0 then
            print()
            print("  --- Set-Cookie ---")
            for _, c in ipairs(resp.cookies) do
                print(string.format("  %s", c))
            end
        end
    end

    -- 打印响应体（截断过长的内容）
    print()
    print("  --- 响应体 ---")
    local body = resp.body or ""
    if #body > 2000 then
        -- 响应体过长，只显示前 2000 字符
        print(body:sub(1, 2000))
        print(string.format("\n  ... [响应体已截断，共 %d 字节]", #body))
    else
        print(body)
    end
end

-- ============================================================
-- 函数：解析命令行中的自定义 Header 参数
-- 格式: -H "Header-Name: value"
-- @param args 命令行参数列表
-- @return headers 表, 剩余参数索引
-- ============================================================
local function parse_args(args)
    local config = {
        method = nil,
        url = nil,
        data = nil,
        headers = {},
        timeout = 10,
        verbose = false,
    }

    local i = 1
    while i <= #args do
        local arg = args[i]
        if arg == "--help" or arg == "-h" then
            config.help = true
            i = i + 1
        elseif arg == "get" or arg == "post" or arg == "head" or arg == "put" or arg == "delete" then
            config.method = arg
            i = i + 1
        elseif arg:match("^https?://") then
            config.url = arg
            i = i + 1
        elseif arg == "-d" or arg == "--data" then
            -- POST 数据
            config.data = args[i + 1]
            i = i + 2
        elseif arg == "-H" or arg == "--header" then
            -- 自定义 Header: "Name: value"
            local header_str = args[i + 1]
            if header_str then
                local name, value = header_str:match("^([^:]+):%s*(.*)$")
                if name and value then
                    config.headers[name] = value
                end
            end
            i = i + 2
        elseif arg == "-c" or arg == "--cookie" then
            -- Cookie
            config.cookie = args[i + 1]
            i = i + 2
        elseif arg == "-ua" or arg == "--user-agent" then
            -- 自定义 User-Agent
            config.headers["User-Agent"] = args[i + 1]
            i = i + 2
        elseif arg == "-t" or arg == "--timeout" then
            -- 超时时间
            config.timeout = tonumber(args[i + 1]) or 10
            i = i + 2
        elseif arg == "-v" or arg == "--verbose" then
            -- 详细输出模式
            config.verbose = true
            i = i + 1
        else
            i = i + 1
        end
    end

    return config
end

-- ============================================================
-- 函数：打印帮助信息
-- ============================================================
local function print_help()
    print([[
============================================
  HTTP 客户端工具 - http_client.lua
============================================

用法:
  lua http_client.lua <方法> <URL> [选项]

方法:
  get, post, head, put, delete

选项:
  -d, --data <数据>       POST 请求数据（表单格式: key=value&key2=value2）
  -H, --header <头部>     自定义请求头（格式: "Name: value"）
  -c, --cookie <Cookie>   请求携带的 Cookie
  -ua, --user-agent <UA>  自定义 User-Agent
  -t, --timeout <秒数>    连接和读取超时（默认 10 秒）
  -v, --verbose           显示完整响应头
  -h, --help              显示帮助

示例:
  lua http_client.lua get http://example.com/
  lua http_client.lua post http://example.com/api -d "name=test&age=20"
  lua http_client.lua get http://example.com/ -ua "MyBrowser/1.0" -v
  lua http_client.lua get http://example.com/ -H "X-Token: abc123" -c "sid=xyz"
]])
end

-- ============================================================
-- 主函数
-- ============================================================
local function main()
    local args = arg
    if #args == 0 then
        print_help()
        return
    end

    -- 解析命令行参数
    local config = parse_args(args)

    -- 检查是否需要显示帮助
    if config.help then
        print_help()
        return
    end

    -- 校验必要参数
    if not config.method then
        print("错误: 请指定 HTTP 方法 (get/post/...)")
        print_help()
        return
    end
    if not config.url then
        print("错误: 请指定目标 URL")
        print_help()
        return
    end

    -- 创建 HTTP 客户端实例
    local client = HTTPClient.new({
        timeout = config.timeout,
    })

    -- 如果有 Cookie 参数，解析并设置
    if config.cookie then
        for name, value in config.cookie:gmatch("([^=;]+)=([^;]+)") do
            client.cookies[name:gsub("^%s+", "")] = value:gsub("^%s+", "")
        end
    end

    -- 打印请求信息
    print(string.rep("=", 60))
    print("  HTTP 请求信息")
    print(string.rep("=", 60))
    print(string.format("  方法:   %s", config.method:upper()))
    print(string.format("  URL:    %s", config.url))
    print(string.format("  超时:   %d 秒", config.timeout))

    if config.data then
        print(string.format("  数据:   %s", config.data))
    end

    -- 打印自定义头部
    for name, value in pairs(config.headers) do
        print(string.format("  头部:   %s: %s", name, value))
    end

    -- 打印 Cookie
    local cookie_str = client:build_cookie_string()
    if cookie_str ~= "" then
        print(string.format("  Cookie: %s", cookie_str))
    end

    print(string.rep("=", 60))
    print()

    -- 发送请求
    local resp, err = client:request(config.method, config.url, config.headers, config.data)

    if err then
        -- 请求失败
        print("  请求失败: " .. err)
        print()
        return
    end

    -- 打印响应
    print(string.rep("=", 60))
    print("  HTTP 响应")
    print(string.rep("=", 60))
    print_response(resp, config.verbose)
    print()
    print(string.rep("=", 60))
end

-- ============================================================
-- 执行主函数
-- ============================================================
main()
