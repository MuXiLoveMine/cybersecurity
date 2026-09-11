--[[
================================================================================
  TCP 端口扫描器 - port_scanner.lua
================================================================================
  功能说明：
    本脚本是一个基于 LuaSocket 的 TCP 端口扫描器，用于安全学习和授权测试：
    1. 支持指定目标 IP 地址和端口范围进行扫描
    2. 使用 TCP 全连接（Full Connect）方式探测端口开放状态
    3. 扫描时支持设置超时时间，避免长时间阻塞
    4. 对开放端口尝试匹配常见服务名称（如 22=SSH, 80=HTTP, 443=HTTPS 等）
    5. 支持单端口扫描和端口范围扫描
    6. 输出扫描结果摘要（开放/关闭/过滤数量统计）

  依赖说明：
    需要安装 LuaSocket 库。
    - LuaRocks 安装:  luarocks install luasocket
    - 或在 Linux 下:  apt-get install lua-socket  (Debian/Ubuntu)
    - Windows 下可通过 LuaRocks 或预编译包安装

  使用方法：
    lua port_scanner.lua <目标IP> <起始端口> [结束端口] [超时秒数]

  示例：
    -- 扫描单个端口（扫描 192.168.1.1 的 80 端口）
    lua port_scanner.lua 192.168.1.1 80

    -- 扫描端口范围（扫描 192.168.1.1 的 1~1024 端口）
    lua port_scanner.lua 192.168.1.1 1 1024

    -- 设置超时为 0.5 秒（扫描 192.168.1.1 的 1~100 端口，超时 0.5s）
    lua port_scanner.lua 192.168.1.1 1 100 0.5

    -- 扫描常见端口（快速扫描模式，内置常用端口列表）
    lua port_scanner.lua 192.168.1.1 --common

  免责声明：
    本脚本仅供网络安全学习和授权的安全测试使用。
    未经授权对他人系统进行端口扫描可能违反相关法律法规，
    使用者需确保已获得目标系统所有者的明确授权。
    使用本脚本造成的一切后果由使用者自行承担。
================================================================================
--]]

-- ============================================================
-- 加载 LuaSocket 库
-- ============================================================
local socket = require("socket")

-- ============================================================
-- 常见端口与服务名映射表
-- 用于根据端口号推断可能运行的服务
-- ============================================================
local common_services = {
    [21]   = "FTP",        -- 文件传输协议
    [22]   = "SSH",        -- 安全 Shell
    [23]   = "Telnet",     -- 远程登录
    [25]   = "SMTP",       -- 简单邮件传输协议
    [53]   = "DNS",        -- 域名系统
    [80]   = "HTTP",       -- 超文本传输协议
    [110]  = "POP3",       -- 邮局协议
    [143]  = "IMAP",       -- 互联网消息访问协议
    [443]  = "HTTPS",      -- 安全超文本传输协议
    [445]  = "SMB",        -- Server Message Block
    [3306] = "MySQL",      -- MySQL 数据库
    [3389] = "RDP",        -- 远程桌面协议
    [5432] = "PostgreSQL", -- PostgreSQL 数据库
    [6379] = "Redis",      -- Redis 缓存
    [8080] = "HTTP-Proxy", -- HTTP 代理/备用 Web 端口
    [8443] = "HTTPS-Alt",  -- 备用 HTTPS 端口
    [27017]= "MongoDB",    -- MongoDB 数据库
    [9200] = "Elasticsearch", -- Elasticsearch 搜索引擎
}

-- ============================================================
-- 常见高危端口列表（用于 --common 快速扫描模式）
-- ============================================================
local common_ports = {
    21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445,
    993, 995, 1433, 1521, 3306, 3389, 5432, 5900, 6379,
    8080, 8443, 9200, 27017
}

-- ============================================================
-- 函数：获取端口对应的服务名
-- @param port 端口号
-- @return 服务名字符串，未知则返回 "unknown"
-- ============================================================
local function get_service_name(port)
    return common_services[port] or "unknown"
end

-- ============================================================
-- 函数：扫描单个 TCP 端口
-- 使用 TCP 全连接方式：尝试与目标 IP:Port 建立 TCP 连接
-- 如果连接成功，说明端口开放；连接失败或超时，说明端口关闭或被过滤
--
-- @param ip       目标 IP 地址
-- @param port     目标端口号
-- @param timeout  超时时间（秒）
-- @return status  状态字符串："open" / "closed" / "filtered"
-- @return time_ms 连接耗时（毫秒），仅 open 时有意义
-- ============================================================
local function scan_port(ip, port, timeout)
    -- 创建 TCP 套接字
    local sock = socket.tcp()

    -- 设置连接超时，避免长时间阻塞
    -- timeout 为 nil 时使用默认值 1 秒
    sock:settimeout(timeout or 1)

    -- 记录开始时间
    local start_time = socket.gettime()

    -- 尝试连接目标地址和端口
    -- connect 返回 1 表示成功，返回 nil + err 表示失败
    local ok, err = sock:connect(ip, port)

    -- 计算连接耗时
    local elapsed = (socket.gettime() - start_time) * 1000

    if ok then
        -- 连接成功，端口开放
        -- 关闭套接字，释放资源
        sock:close()
        return "open", elapsed
    elseif err == "timeout" then
        -- 连接超时，端口可能被防火墙过滤（无响应）
        sock:close()
        return "filtered", elapsed
    else
        -- 连接被拒绝（connection refused），端口关闭
        -- 目标主机返回了 RST 包，说明端口没有服务监听
        sock:close()
        return "closed", elapsed
    end
end

-- ============================================================
-- 函数：打印扫描结果
-- @param ip      目标 IP
-- @param port    端口号
-- @param status  端口状态
-- @param time_ms 耗时（毫秒）
-- @param service 服务名
-- ============================================================
local function print_result(ip, port, status, time_ms, service)
    -- 使用不同标记区分端口状态
    -- [+] 开放  [-] 关闭  [?] 过滤
    local marker = {
        open     = "[+]",
        closed   = "[-]",
        filtered = "[?]",
    }

    local mark = marker[status] or "[ ]"
    local time_str = string.format("%.1fms", time_ms or 0)

    -- 格式化输出
    -- 只详细显示开放的端口，关闭的端口简单列出
    if status == "open" then
        print(string.format("  %s %-6d  %-10s  %-8s  %s:%d",
            mark, port, status, time_str, ip, port))
        print(string.format("      └─ 服务: %s", service))
    end
end

-- ============================================================
-- 函数：打印帮助信息
-- ============================================================
local function print_help()
    print([[
============================================
  TCP 端口扫描器 - port_scanner.lua
============================================

用法:
  lua port_scanner.lua <目标IP> <起始端口> [结束端口] [超时秒数]
  lua port_scanner.lua <目标IP> --common [超时秒数]

参数说明:
  目标IP      要扫描的目标 IP 地址（如 192.168.1.1）
  起始端口    扫描的起始端口号（1-65535）
  结束端口    扫描的结束端口号（可选，默认等于起始端口）
  超时秒数    每个端口的连接超时时间（可选，默认 1.0 秒）
  --common    快速扫描常见高危端口

示例:
  lua port_scanner.lua 192.168.1.1 80
  lua port_scanner.lua 192.168.1.1 1 1024
  lua port_scanner.lua 192.168.1.1 1 65535 0.3
  lua port_scanner.lua 192.168.1.1 --common
]])
end

-- ============================================================
-- 函数：执行端口扫描主流程
-- @param ip        目标 IP
-- @param ports     要扫描的端口列表
-- @param timeout   超时时间
-- ============================================================
local function run_scan(ip, ports, timeout)
    -- 扫描统计
    local stats = {
        open     = 0,
        closed   = 0,
        filtered = 0,
        total    = #ports,
    }

    -- 记录开放的端口
    local open_ports = {}

    -- 打印扫描头部信息
    print(string.rep("=", 60))
    print(string.format("  TCP 端口扫描"))
    print(string.format("  目标: %s", ip))
    print(string.format("  端口数: %d", #ports))
    print(string.format("  超时: %.1f 秒", timeout))
    print(string.rep("=", 60))
    print()
    print(string.format("  %-4s %-6s  %-10s  %-8s  %s",
        "状态", "端口", "状态", "耗时", "地址"))
    print(string.rep("-", 60))

    -- 记录扫描开始时间
    local scan_start = socket.gettime()

    -- 遍历端口列表逐个扫描
    for i, port in ipairs(ports) do
        -- 调用单个端口扫描函数
        local status, time_ms = scan_port(ip, port, timeout)
        local service = get_service_name(port)

        -- 更新统计
        stats[status] = (stats[status] or 0) + 1

        -- 如果端口开放，记录到开放列表
        if status == "open" then
            table.insert(open_ports, {
                port = port,
                service = service,
                time_ms = time_ms,
            })
        end

        -- 打印扫描结果
        print_result(ip, port, status, time_ms, service)
    end

    -- 计算扫描总耗时
    local total_time = socket.gettime() - scan_start

    -- 打印扫描摘要
    print()
    print(string.rep("=", 60))
    print("  扫描完成 - 结果摘要")
    print(string.rep("=", 60))
    print(string.format("  总耗时:   %.2f 秒", total_time))
    print(string.format("  扫描端口: %d 个", stats.total))
    print(string.format("  开放:     %d 个", stats.open))
    print(string.format("  关闭:     %d 个", stats.closed))
    print(string.format("  过滤:     %d 个", stats.filtered))

    -- 如果有开放端口，打印开放端口列表
    if #open_ports > 0 then
        print()
        print(string.rep("=", 60))
        print("  开放端口列表")
        print(string.rep("=", 60))
        for _, info in ipairs(open_ports) do
            print(string.format("  %d/%-8s  %s  (%.1fms)",
                info.port, "tcp", info.service, info.time_ms))
        end
    end

    print()
    print(string.rep("=", 60))
end

-- ============================================================
-- 主函数：解析命令行参数并启动扫描
-- ============================================================
local function main()
    -- 检查参数数量
    local args = arg
    if #args < 1 or args[1] == "--help" or args[1] == "-h" then
        print_help()
        return
    end

    -- 解析目标 IP
    local ip = args[1]

    -- 检查是否为 --common 模式
    if args[2] == "--common" then
        -- 快速扫描常见端口
        local timeout = tonumber(args[3]) or 1.0
        run_scan(ip, common_ports, timeout)
        return
    end

    -- 解析起始端口
    local start_port = tonumber(args[2])
    if not start_port then
        print("错误: 起始端口必须为数字")
        print_help()
        return
    end

    -- 解析结束端口（可选，默认等于起始端口）
    local end_port = tonumber(args[3]) or start_port

    -- 解析超时时间（可选，默认 1.0 秒）
    local timeout = tonumber(args[4]) or 1.0

    -- 参数校验
    if start_port < 1 or start_port > 65535 then
        print("错误: 起始端口范围必须在 1-65535 之间")
        return
    end
    if end_port < start_port then
        print("错误: 结束端口不能小于起始端口")
        return
    end
    if end_port > 65535 then
        print("错误: 结束端口范围必须在 1-65535 之间")
        return
    end

    -- 构建端口列表
    local ports = {}
    for p = start_port, end_port do
        table.insert(ports, p)
    end

    -- 启动扫描
    run_scan(ip, ports, timeout)
end

-- ============================================================
-- 执行主函数
-- ============================================================
main()
