--[[
================================================================================
  OpenResty WAF 示例 - waf_example.lua
================================================================================
  功能说明：
    本脚本是一个基于 OpenResty / ngx_lua 的 Web 应用防火墙（WAF）规则示例，
    用于学习 WAF 的工作原理和 Lua 在 Nginx WAF 中的应用：
    1. 检测 SQL 注入攻击特征
    2. 检测 XSS 跨站脚本攻击特征
    3. 检测恶意 User-Agent（扫描器、爬虫等）
    4. 检测路径遍历攻击
    5. 检测命令注入攻击
    6. IP 黑白名单过滤
    7. 请求频率限制（简易 CC 防护）
    8. 记录攻击日志

  运行环境说明：
    本脚本需要在 OpenResty 或安装了 ngx_lua 模块的 Nginx 中运行。
    脚本中使用 ngx.* API（如 ngx.var, ngx.req, ngx.exit 等），
    无法在标准 Lua 解释器中直接运行。

    OpenResty 安装: https://openresty.org/
    配置方式见本文件末尾的"Nginx 配置示例"部分。

  Nginx 配置示例（在 nginx.conf 中引用本脚本）：
    http {
        # 共享内存区域，用于存储 WAF 状态数据
        lua_shared_dict waf_cache 10m;
        lua_shared_dict waf_limit 10m;

        # 设置 Lua 包搜索路径
        lua_package_path "/path/to/lua/?.lua;;";

        server {
            listen 80;
            server_name example.com;

            # 在 access 阶段执行 WAF 检测
            access_by_lua_file /path/to/waf_example.lua;

            location / {
                proxy_pass http://backend;
            }
        }
    }

  免责声明：
    本脚本仅为 WAF 规则示例，用于安全学习和研究。
    规则基于正则匹配，可能存在误报和漏报，不可作为生产环境唯一防护手段。
    在生产环境中使用前，请充分测试规则并配合其他安全措施。
    使用本脚本造成的一切后果由使用者自行承担。
================================================================================
--]]

-- ============================================================
-- 检查是否在 ngx 环境中运行
-- 如果直接用 lua 解释器运行，提供模拟说明
-- ============================================================
if not ngx then
    -- 不在 OpenResty 环境中，输出说明信息
    print([[
============================================
  OpenResty WAF 示例 - waf_example.lua
============================================

  本脚本需要在 OpenResty / ngx_lua 环境中运行，无法直接用 lua 命令执行。

  请将本脚本部署到 OpenResty 中，通过 Nginx 配置的 access_by_lua_file 指令加载。

  Nginx 配置示例：

    http {
        lua_shared_dict waf_cache 10m;
        lua_shared_dict waf_limit 10m;
        lua_package_path "/path/to/lua/?.lua;;";

        server {
            listen 80;
            access_by_lua_file /path/to/waf_example.lua;
            location / {
                proxy_pass http://backend;
            }
        }
    }

  也可以运行测试模式查看内置规则：
    lua waf_example.lua --test
    lua waf_example.lua --rules
]])
    return
end

-- ============================================================
-- WAF 配置参数
-- 可根据实际需求调整这些配置
-- ============================================================
local waf_config = {
    -- 是否启用 WAF
    enable = true,

    -- 是否处于学习模式（仅记录日志，不拦截）
    -- 生产环境建议先开启学习模式观察一段时间
    learning_mode = false,

    -- 动作：deny(拒绝) / redirect(重定向) / log(仅记录)
    action = "deny",

    -- 拦截后的 HTTP 状态码
    deny_status = 403,

    -- 拦截后返回的内容
    deny_message = "Request Blocked by WAF",

    -- 请求频率限制（每秒最大请求数）
    rate_limit_per_sec = 60,

    -- IP 黑名单（精确匹配）
    ip_blacklist = {
        "192.168.1.100",
        "10.0.0.50",
    },

    -- IP 白名单（白名单中的 IP 不做任何检测）
    ip_whitelist = {
        "127.0.0.1",
        "192.168.0.0/24",  -- 支持 CIDR
    },

    -- URL 白名单（这些 URL 路径不做检测）
    url_whitelist = {
        "/api/public/",
        "/health",
        "/favicon.ico",
    },

    -- 是否记录攻击日志
    log_attacks = true,

    -- 日志文件路径（通过 ngx.log 输出到 Nginx 错误日志）
    -- 也可以通过 Lua io.write 写入独立文件
    log_level = ngx.ERR,
}

-- ============================================================
-- WAF 规则定义
-- 每条规则包含：名称、类型、正则模式、风险等级、描述
-- ============================================================
local waf_rules = {

    -- ============================================================
    -- SQL 注入检测规则
    -- 检测常见的 SQL 注入攻击特征
    -- ============================================================
    {
        id = "sqli_001",
        type = "sql_injection",
        severity = "high",
        description = "SQL 注入 - UNION SELECT 语句",
        -- 匹配 UNION SELECT 及其变体
        pattern = [=[(?i)\bunion\b.+\bselect\b]=],
        fields = { "uri", "args", "body" },
    },
    {
        id = "sqli_002",
        type = "sql_injection",
        severity = "high",
        description = "SQL 注入 - OR 1=1 永真条件",
        -- 匹配 ' OR '1'='1 或 OR 1=1 等
        pattern = [=[(?i)(['"]\s*(or|and)\s+['"]?\d+['"]?\s*=\s*['"]?\d+|or\s+1\s*=\s*1)]=],
        fields = { "uri", "args", "body" },
    },
    {
        id = "sqli_003",
        type = "sql_injection",
        severity = "high",
        description = "SQL 注入 - 注释符",
        -- 匹配 SQL 注释 -- 或 # 或 /*
        pattern = [=[(--|#|/\*)]=],
        fields = { "uri", "args" },
    },
    {
        id = "sqli_004",
        type = "sql_injection",
        severity = "medium",
        description = "SQL 注入 - 常见 SQL 关键字组合",
        -- 匹配 select ... from, insert into, drop table 等
        pattern = [=[(?i)((select|insert|update|delete|drop|create|alter)\s+.{0,50}(from|into|table|database|schema))]=],
        fields = { "uri", "args", "body" },
    },
    {
        id = "sqli_005",
        type = "sql_injection",
        severity = "high",
        description = "SQL 注入 - 时间盲注函数",
        -- 匹配 SLEEP(), BENCHMARK(), WAITFOR DELAY 等
        pattern = [=[(?i)(sleep\s*\(|benchmark\s*\(|waitfor\s+delay|pg_sleep)]=],
        fields = { "uri", "args", "body" },
    },

    -- ============================================================
    -- XSS 跨站脚本检测规则
    -- 检测常见的 XSS 攻击特征
    -- ============================================================
    {
        id = "xss_001",
        type = "xss",
        severity = "high",
        description = "XSS - script 标签",
        -- 匹配 <script> 标签
        pattern = [=[(?i)<\s*script[^>]*>]=],
        fields = { "uri", "args", "body" },
    },
    {
        id = "xss_002",
        type = "xss",
        severity = "high",
        description = "XSS - 事件处理函数",
        -- 匹配 onerror=, onload=, onclick= 等
        pattern = [=[(?i)\bon(error|load|click|mouseover|focus|blur|submit|change)\s*=]=],
        fields = { "uri", "args", "body" },
    },
    {
        id = "xss_003",
        type = "xss",
        severity = "medium",
        description = "XSS - JavaScript 伪协议",
        -- 匹配 javascript: 协议
        pattern = [=[(?i)javascript\s*:]=],
        fields = { "uri", "args", "body" },
    },
    {
        id = "xss_004",
        type = "xss",
        severity = "high",
        description = "XSS - eval/alert/prompt/confirm 函数",
        -- 匹配 eval(), alert(), prompt(), confirm()
        pattern = [=[(?i)(eval|alert|prompt|confirm|document\.cookie|document\.write)\s*\(([\s\S]*?)\))]=],
        fields = { "uri", "args", "body" },
    },
    {
        id = "xss_005",
        type = "xss",
        severity = "medium",
        description = "XSS - SVG/iframe 嵌入标签",
        -- 匹配 <svg>, <iframe>, <object>, <embed> 标签
        pattern = [=[(?i)<\s*(svg|iframe|object|embed|img)[^>]*\bon\w+\s*=]=],
        fields = { "uri", "args", "body" },
    },

    -- ============================================================
    -- 命令注入检测规则
    -- 检测操作系统命令注入攻击
    -- ============================================================
    {
        id = "cmdi_001",
        type = "command_injection",
        severity = "high",
        description = "命令注入 - 管道符和分号",
        -- 匹配管道符 | 或分号 ; 或 && 或 || 后接命令
        pattern = [=[([|;`&]{1,2}\s*(cat|ls|id|whoami|uname|wget|curl|bash|sh|nc|python|perl))]=],
        fields = { "uri", "args", "body" },
    },
    {
        id = "cmdi_002",
        type = "command_injection",
        severity = "high",
        description = "命令注入 - 命令替换",
        -- 匹配 $(cmd) 或 `cmd` 命令替换
        pattern = [=[(\$\([^)]+\)|`[^`]+`)]=],
        fields = { "uri", "args", "body" },
    },

    -- ============================================================
    -- 路径遍历检测规则
    -- ============================================================
    {
        id = "lfi_001",
        type = "path_traversal",
        severity = "high",
        description = "路径遍历 - ../ 序列",
        -- 匹配 ../ 或 ..\ 路径遍历
        pattern = [=[(\.\.[/\\]|\.\.%2f|\.\.%5c)]=],
        fields = { "uri", "args" },
    },
    {
        id = "lfi_002",
        type = "path_traversal",
        severity = "high",
        description = "路径遍历 - 敏感文件访问",
        -- 匹配 /etc/passwd, /proc/self 等敏感路径
        pattern = [=[(/etc/passwd|/etc/shadow|/proc/self|/proc/version|c:\\windows\\system32)]=],
        fields = { "uri", "args" },
    },
    {
        id = "lfi_003",
        type = "path_traversal",
        severity = "high",
        description = "路径遍历 - PHP 包装器",
        -- 匹配 php://filter, php://input 等协议
        pattern = [=[(?i)(php://|file://|expect://|data://)]=],
        fields = { "uri", "args" },
    },

    -- ============================================================
    -- 恶意 User-Agent 检测规则
    -- 检测常见扫描器、爬虫和攻击工具的 UA
    -- ============================================================
    {
        id = "ua_001",
        type = "malicious_ua",
        severity = "medium",
        description = "恶意 UA - SQL 注入工具",
        -- 匹配 sqlmap 等工具特征
        pattern = [=[(?i)(sqlmap|sqlninja|havij|bbqsql)]=],
        fields = { "user_agent" },
    },
    {
        id = "ua_002",
        type = "malicious_ua",
        severity = "medium",
        description = "恶意 UA - 漏洞扫描器",
        -- 匹配常见扫描器
        pattern = [=[(?i)(nmap|nikto|nessus|acunetix|w3af|openvas|zgrab|masscan|nuclei)]=],
        fields = { "user_agent" },
    },
    {
        id = "ua_003",
        type = "malicious_ua",
        severity = "low",
        description = "恶意 UA - 爬虫/机器人",
        -- 匹配自动化工具
        pattern = [=[(?i)(curl|wget|python-requests|scrapy|go-http-client|httpclient|libwww)]=],
        fields = { "user_agent" },
    },
    {
        id = "ua_004",
        type = "malicious_ua",
        severity = "medium",
        description = "恶意 UA - 空 UA 或异常 UA",
        -- 匹配空 UA 或过短的 UA
        pattern = [=[^$|^.{0,10}$]=],
        fields = { "user_agent" },
    },
}

-- ============================================================
-- 工具函数：获取客户端真实 IP
-- 考虑代理转发的情况，优先从 X-Forwarded-For 等头部获取
-- ============================================================
local function get_client_ip()
    -- 从 X-Forwarded-For 头获取（处理多层代理）
    local xff = ngx.var.http_x_forwarded_for
    if xff then
        -- X-Forwarded-For 可能包含多个 IP，取第一个（最原始的客户端 IP）
        local ip = xff:match("([^,]+)")
        if ip then
            return ip:gsub("^%s+", ""):gsub("%s+$", "")
        end
    end

    -- 从 X-Real-IP 头获取
    local xri = ngx.var.http_x_real_ip
    if xri and xri ~= "" then
        return xri
    end

    -- 直接使用 remote_addr
    return ngx.var.remote_addr or "unknown"
end

-- ============================================================
-- 工具函数：检查 IP 是否在白名单中
-- 支持精确匹配和 CIDR 匹配
-- @param ip 要检查的 IP
-- @param list IP 列表
-- @return boolean
-- ============================================================
local function ip_in_list(ip, list)
    for _, entry in ipairs(list) do
        -- 检查是否为 CIDR 格式（如 192.168.0.0/24）
        local cidr_ip, mask = entry:match("^(%d+\.%d+\.%d+\.%d+)/(%d+)$")
        if cidr_ip and mask then
            -- 简化 CIDR 检查：仅做前缀比较
            -- 完整实现需要将 IP 转为整数进行位运算
            local prefix_len = tonumber(mask)
            local ip_parts = {}
            for part in ip:gmatch("(%d+)") do
                table.insert(ip_parts, tonumber(part))
            end
            local cidr_parts = {}
            for part in cidr_ip:gmatch("(%d+)") do
                table.insert(cidr_parts, tonumber(part))
            end

            -- 简单的前缀匹配（按字节比较）
            local match_bytes = math.floor(prefix_len / 8)
            local match_bits = prefix_len % 8
            local matched = true

            for i = 1, match_bytes do
                if ip_parts[i] ~= cidr_parts[i] then
                    matched = false
                    break
                end
            end

            -- 处理剩余的位
            if matched and match_bits > 0 and match_bytes < 4 then
                local mask_byte = (0xFF << (8 - match_bits)) & 0xFF
                if (ip_parts[match_bytes + 1] & mask_byte) ~= (cidr_parts[match_bytes + 1] & mask_byte) then
                    matched = false
                end
            end

            if matched then return true end
        else
            -- 精确匹配
            if ip == entry then
                return true
            end
        end
    end
    return false
end

-- ============================================================
-- 工具函数：检查 URL 是否在白名单中
-- @param uri 请求 URI
-- @param whitelist URL 白名单
-- @return boolean
-- ============================================================
local function url_in_whitelist(uri, whitelist)
    for _, pattern in ipairs(whitelist) do
        -- 支持前缀匹配
        if uri:sub(1, #pattern) == pattern then
            return true
        end
    end
    return false
end

-- ============================================================
-- 工具函数：收集请求数据
-- 获取请求的各个部分用于规则匹配
-- @return 包含各部分请求数据的表
-- ============================================================
local function collect_request_data()
    local data = {
        uri = ngx.var.uri or "",
        args = "",
        body = "",
        user_agent = ngx.var.http_user_agent or "",
        method = ngx.req.get_method(),
        headers = ngx.req.get_headers(),
    }

    -- 获取查询参数（原始字符串）
    data.args = ngx.var.args or ""

    -- 获取请求体（仅对 POST/PUT 请求）
    if data.method == "POST" or data.method == "PUT" or data.method == "PATCH" then
        -- 读取请求体
        ngx.req.read_body()
        data.body = ngx.req.get_body_data() or ""

        -- 如果请求体存储在文件中，读取文件
        if data.body == "" then
            local body_file = ngx.req.get_body_file()
            if body_file then
                local f = io.open(body_file, "r")
                if f then
                    data.body = f:read("*a")
                    f:close()
                end
            end
        end
    end

    return data
end

-- ============================================================
-- 工具函数：对单个字段应用规则匹配
-- @param rule    规则定义
-- @param field   字段名称
-- @param value   字段值
-- @return 匹配到的内容，或 nil
-- ============================================================
local function match_rule(rule, field, value)
    if not value or value == "" then return nil end

    -- 使用 ngx.re.find 进行正则匹配（PCRE 正则）
    -- 参数说明：
    --   value: 要匹配的字符串
    --   rule.pattern: 正则模式
    --   "ijo": i=不区分大小写, j=启用 PCRE, o=编译一次优化
    local match, err = ngx.re.find(value, rule.pattern, "ijo")
    if match then
        -- 返回匹配的子串
        local matched_str = value:sub(match, ngx.re.find(value, rule.pattern, "ijo") or match)
        return value:sub(match, match + 50)  -- 返回匹配位置附近的内容
    end
    return nil
end

-- ============================================================
-- 工具函数：记录攻击日志
-- 将检测到的攻击信息记录到 Nginx 错误日志
-- @param attack_info 攻击信息表
-- ============================================================
local function log_attack(attack_info)
    local log_msg = string.format(
        "[WAF] 攻击告警 | ID: %s | 类型: %s | 风险: %s | 描述: %s | "
        .. "客户端IP: %s | 方法: %s | URI: %s | UA: %s | 匹配字段: %s",
        attack_info.rule_id or "unknown",
        attack_info.rule_type or "unknown",
        attack_info.severity or "unknown",
        attack_info.description or "",
        attack_info.client_ip or "",
        attack_info.method or "",
        attack_info.uri or "",
        attack_info.user_agent or "",
        attack_info.matched_field or ""
    )
    ngx.log(waf_config.log_level, log_msg)
end

-- ============================================================
-- 函数：执行 WAF 规则检测
-- 遍历所有规则，对请求数据进行匹配
-- @param request_data 请求数据表
-- @return 匹配到的规则信息，或 nil（未匹配）
-- ============================================================
local function run_waf_checks(request_data)
    -- 字段名到实际数据的映射
    local field_map = {
        uri         = request_data.uri,
        args        = request_data.args,
        body        = request_data.body,
        user_agent  = request_data.user_agent,
    }

    -- 遍历所有规则
    for _, rule in ipairs(waf_rules) do
        -- 遍历规则指定要检测的字段
        for _, field_name in ipairs(rule.fields) do
            local value = field_map[field_name]
            if value and value ~= "" then
                -- 执行正则匹配
                local matched = match_rule(rule, field_name, value)
                if matched then
                    -- 匹配成功，返回攻击信息
                    return {
                        rule_id       = rule.id,
                        rule_type     = rule.type,
                        severity      = rule.severity,
                        description   = rule.description,
                        matched_field = field_name,
                        matched_value = matched,
                        uri           = request_data.uri,
                        method        = request_data.method,
                        user_agent    = request_data.user_agent,
                        client_ip     = get_client_ip(),
                    }
                end
            end
        end
    end

    -- 未匹配任何规则
    return nil
end

-- ============================================================
-- 函数：请求频率限制（简易 CC 防护）
-- 使用共享内存字典记录每个 IP 的请求次数
-- @param client_ip 客户端 IP
-- @return 是否允许通过
-- ============================================================
local function check_rate_limit(client_ip)
    -- 获取共享内存字典
    local limit_dict = ngx.shared.waf_limit
    if not limit_dict then
        -- 共享内存未配置，跳过频率限制
        return true
    end

    -- 使用 IP 作为键，当前秒数作为后缀
    local key = "rate:" .. client_ip .. ":" .. os.time()

    -- 原子递增计数器
    local count, err = limit_dict:incr(key, 1, 0, 1)  -- 过期时间 1 秒
    if not count then
        -- 计数失败，放行（fail-open 策略）
        return true
    end

    -- 检查是否超过阈值
    if count > waf_config.rate_limit_per_sec then
        -- 超过频率限制
        ngx.log(ngx.WARN,
            "[WAF] 频率限制 | IP: " .. client_ip ..
            " | 请求数: " .. count ..
            " | 限制: " .. waf_config.rate_limit_per_sec .. "/s")
        return false
    end

    return true
end

-- ============================================================
-- 函数：执行拦截动作
-- 根据配置决定如何处理被拦截的请求
-- @param attack_info 攻击信息
-- ============================================================
local function take_action(attack_info)
    -- 记录攻击日志
    if waf_config.log_attacks then
        log_attack(attack_info)
    end

    -- 学习模式：仅记录日志，不拦截
    if waf_config.learning_mode then
        ngx.log(ngx.INFO, "[WAF] 学习模式 - 记录但不拦截: " .. attack_info.description)
        return
    end

    -- 根据配置的动作类型执行拦截
    if waf_config.action == "deny" then
        -- 直接拒绝请求
        ngx.status = waf_config.deny_status
        ngx.header["Content-Type"] = "text/plain; charset=utf-8"
        ngx.say(waf_config.deny_message)
        ngx.exit(waf_config.deny_status)

    elseif waf_config.action == "redirect" then
        -- 重定向到警告页面
        ngx.redirect("/waf/blocked", 302)

    elseif waf_config.action == "log" then
        -- 仅记录日志，不拦截
        return
    end
end

-- ============================================================
-- WAF 主入口函数
-- 在 Nginx access 阶段执行
-- ============================================================
local function waf_main()
    -- 检查 WAF 是否启用
    if not waf_config.enable then
        return
    end

    -- 获取客户端 IP
    local client_ip = get_client_ip()

    -- 1. IP 白名单检查（白名单优先，直接放行）
    if ip_in_list(client_ip, waf_config.ip_whitelist) then
        return
    end

    -- 2. IP 黑名单检查
    if ip_in_list(client_ip, waf_config.ip_blacklist) then
        ngx.log(ngx.WARN, "[WAF] IP 黑名单拦截 | IP: " .. client_ip)
        if not waf_config.learning_mode then
            ngx.status = 403
            ngx.header["Content-Type"] = "text/plain"
            ngx.say("Access Denied")
            ngx.exit(403)
        end
        return
    end

    -- 3. URL 白名单检查
    local uri = ngx.var.uri or ""
    if url_in_whitelist(uri, waf_config.url_whitelist) then
        return
    end

    -- 4. 请求频率限制
    if not check_rate_limit(client_ip) then
        if not waf_config.learning_mode then
            ngx.status = 429  -- Too Many Requests
            ngx.header["Content-Type"] = "text/plain"
            ngx.header["Retry-After"] = "1"
            ngx.say("Too Many Requests")
            ngx.exit(429)
        end
        return
    end

    -- 5. 收集请求数据
    local request_data = collect_request_data()

    -- 6. 执行 WAF 规则检测
    local attack_info = run_waf_checks(request_data)

    -- 7. 如果检测到攻击，执行拦截动作
    if attack_info then
        take_action(attack_info)
    end

    -- 未检测到攻击，放行请求
end

-- ============================================================
-- 执行 WAF 主函数
-- ============================================================
waf_main()
