---

## 四、高级实战案例

### 4.1 Nginx/WAF 绕过脚本

使用 Lua 编写 Nginx 配置和 WAF 绕过研究脚本。

```lua
-- ===== Nginx Lua WAF 规则开发 =====
-- 用于 OpenResty / lua-nginx-module

local _M = {}

-- ===== 1. IP 黑白名单 =====
local ip_blacklist = {
    ["192.168.1.100"] = true,
    ["10.0.0.50"] = true,
}

local ip_whitelist = {
    ["127.0.0.1"] = true,
    ["::1"] = true,
}

function _M.check_ip()
    local ip = ngx.var.remote_addr
    
    if ip_whitelist[ip] then
        return true  -- 白名单放行
    end
    
    if ip_blacklist[ip] then
        ngx.log(ngx.WARN, "Blocked IP: ", ip)
        return ngx.exit(403)
    end
    
    return true
end

-- ===== 2. User-Agent 过滤 =====
local bad_user_agents = {
    "sqlmap", "nmap", "nikto", "dirbuster",
    "masscan", "zmap", "hydra", "medusa",
    "acunetix", "nessus", "openvas", "burp",
}

function _M.check_user_agent()
    local ua = ngx.var.http_user_agent or ""
    local ua_lower = ua:lower()
    
    for _, bad in ipairs(bad_user_agents) do
        if ua_lower:find(bad, 1, true) then
            ngx.log(ngx.WARN, "Bad UA: ", ua)
            return ngx.exit(403)
        end
    end
    
    return true
end

-- ===== 3. SQL 注入检测 =====
local sqli_patterns = {
    ["'"] = "单引号",
    ["\""] = "双引号",
    ["or 1=1"] = "永真式",
    ["' or '1'='1"] = "永真式",
    ["union select"] = "联合查询",
    ["union all select"] = "联合查询",
    ["select.*from"] = "SELECT 查询",
    ["insert into"] = "INSERT",
    ["drop table"] = "删表",
    ["update.*set"] = "更新注入",
    ["delete from"] = "删除注入",
    ["--"] = "SQL注释",
    ["#"] = "SQL注释",
    [";"] = "语句分隔符",
    ["sleep("] = "时间盲注",
    ["benchmark("] = "时间盲注",
    ["xp_cmdshell"] = "命令执行",
    ["into outfile"] = "写文件",
    ["load_file"] = "读文件",
}

function _M.check_sqli()
    local args = ngx.req.get_uri_args()
    local body_args = {}
    
    -- 解析 POST body (需要先读取)
    ngx.req.read_body()
    if ngx.var.request_method == "POST" then
        body_args = ngx.req.get_post_args() or {}
    end
    
    for _, params in ipairs({args, body_args}) do
        for key, val in pairs(params) do
            if type(val) == "string" then
                local val_lower = val:lower()
                for pattern, desc in pairs(sqli_patterns) do
                    if val_lower:find(pattern:lower(), 1, true) then
                        ngx.log(ngx.WARN, 
                            "SQLi detected: param=", key, 
                            ", value=", val,
                            ", pattern=", desc)
                        return ngx.exit(403)
                    end
                end
            end
        end
    end
    
    return true
end

-- ===== 4. XSS 检测 =====
local xss_patterns = {
    "<script",
    "</script",
    "javascript:",
    "onerror=",
    "onload=",
    "onclick=",
    "onmouseover=",
    "eval(",
    "document.cookie",
    "<img[^>]+onerror",
    "<svg[^>]+onload",
    "<iframe",
    "alert(",
    "confirm(",
    "prompt(",
    '<[^>]+script[^>]*>',
}

function _M.check_xss()
    local args = ngx.req.get_uri_args()
    ngx.req.read_body()
    local body_args = ngx.var.request_method == "POST" and (ngx.req.get_post_args() or {}) or {}
    
    for _, params in ipairs({args, body_args}) do
        for key, val in pairs(params) do
            if type(val) == "string" then
                for _, pattern in ipairs(xss_patterns) do
                    if val:match(pattern) then
                        ngx.log(ngx.WARN, "XSS detected: param=", key, ", value=", val)
                        return ngx.exit(403)
                    end
                end
            end
        end
    end
    
    return true
end

-- ===== 5. 速率限制（漏桶算法） =====
local rate_limit_store = ngx.shared.rate_limit

function _M.rate_limit(key, limit, window)
    limit = limit or 100   -- 次数
    window = window or 60  -- 秒
    
    local current = rate_limit_store:get(key) or 0
    
    if current >= limit then
        ngx.header["X-RateLimit-Limit"] = limit
        ngx.header["X-RateLimit-Remaining"] = 0
        return ngx.exit(429)  -- Too Many Requests
    end
    
    rate_limit_store:incr(key, 1, 0, window)
    ngx.header["X-RateLimit-Limit"] = limit
    ngx.header["X-RateLimit-Remaining"] = limit - (current + 1)
    
    return true
end

-- ===== 6. CC 攻击防护 =====
function _M.anti_cc()
    local ip = ngx.var.remote_addr
    local key = "cc:" .. ip
    return _M.rate_limit(key, 60, 10)  -- 10秒内最多60次请求
end

-- ===== 7. 文件上传检测 =====
local dangerous_extensions = {
    ".php", ".php3", ".php4", ".php5", ".phtml",
    ".asp", ".aspx", ".asa", ".cer",
    ".jsp", ".jspx",
    ".exe", ".bat", ".cmd", ".sh",
    ".pl", ".py", ".rb",
}

function _M.check_file_upload()
    local content_type = ngx.var.content_type or ""
    
    if content_type:find("multipart/form-data", 1, true) then
        -- 获取文件名
        local body = ngx.req.get_body_data()
        if body then
            for _, ext in ipairs(dangerous_extensions) do
                if body:lower():find('filename="[^"]*' .. ext .. '"') then
                    ngx.log(ngx.WARN, "Dangerous file upload: ", ext)
                    return ngx.exit(403)
                end
            end
        end
    end
    
    return true
end

-- ===== 8. 主 WAF 函数 =====
function _M.run_waf()
    -- IP 检查
    _M.check_ip()
    
    -- UA 检查
    _M.check_user_agent()
    
    -- CC 防护
    _M.anti_cc()
    
    -- 注入检测
    _M.check_sqli()
    _M.check_xss()
    
    -- 文件上传检测
    if ngx.var.request_method == "POST" then
        _M.check_file_upload()
    end
    
    return true
end

return _M

--[[
    Nginx 配置示例:

    http {
        lua_shared_dict rate_limit 10m;
        
        access_by_lua_block {
            local waf = require "waf"
            waf.run_waf()
        }
    }
]]
```

### 4.2 Lua 加解密工具库

Lua 加密与编码工具函数。

```lua
-- ===== 加密与编码工具库 =====
local crypto = {}

-- ===== Base64 编解码 =====
local b='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'

function crypto.base64_encode(data)
    return ((data:gsub('.', function(x)
        local r, b='', x:byte()
        for i=8,1,-1 do r = r .. (b % 2^i - b % 2^(i-1) > 0 and '1' or '0') end
        return r;
    end)..'0000'):gsub('%d%d%d?%d?%d?%d?', function(x)
        if (#x < 6) then return '' end
        local c=0
        for i=1,6 do c = c + (x:sub(i,i)=='1' and 2^(6-i) or 0) end
        return b:sub(c+1,c+1)
    end)..({ '', '==', '=' })[#data%3+1])
end

function crypto.base64_encode_url(data)
    local encoded = crypto.base64_encode(data)
    return encoded:gsub('+', '-'):gsub('/', '_'):gsub('=', '')
end

function crypto.base64_decode(data)
    data = string.gsub(data, '[^'..b..'=]', '')
    return (data:gsub('.', function(x)
        if (x == '=') then return '' end
        local r, f='', (b:find(x)-1)
        for i=6,1,-1 do r = r .. (f % 2^i - f % 2^(i-1) > 0 and '1' or '0') end
        return r;
    end):gsub('%d%d%d?%d?%d?%d?%d?%d?', function(x)
        if (#x ~= 8) then return '' end
        local c=0
        for i=1,8 do c = c + (x:sub(i,i)=='1' and 2^(8-i) or 0) end
        return string.char(c)
    end))
end

-- ===== 十六进制编解码 =====
function crypto.hex_encode(data)
    return (data:gsub('.', function(c)
        return string.format('%02x', string.byte(c))
    end))
end

function crypto.hex_decode(data)
    return (data:gsub('..', function(cc)
        return string.char(tonumber(cc, 16))
    end))
end

-- ===== URL 编解码 =====
function crypto.url_encode(str)
    if str then
        str = str:gsub('\n', '\r\n')
        str = str:gsub('([^%w%-%.%_%~ ])', function(c)
            return string.format('%%%02X', string.byte(c))
        end)
        str = str:gsub(' ', '+')
    end
    return str
end

function crypto.url_decode(str)
    if str then
        str = str:gsub('+', ' ')
        str = str:gsub('%%(%x%x)', function(h)
            return string.char(tonumber(h, 16))
        end)
        str = str:gsub('\r\n', '\n')
    end
    return str
end

-- ===== 简单 XOR 加密 =====
function crypto.xor_encrypt(data, key)
    local result = {}
    local key_len = #key
    for i = 1, #data do
        local char = data:byte(i)
        local k = key:byte((i - 1) % key_len + 1)
        table.insert(result, string.char(bit.bxor(char, k)))
    end
    return table.concat(result)
end

function crypto.xor_decrypt(data, key)
    -- XOR 是对称的，加密解密相同
    return crypto.xor_encrypt(data, key)
end

-- ===== ROT13 变换 =====
function crypto.rot13(str)
    local byte_a, byte_A = string.byte('a'), string.byte('A')
    return (str:gsub('[a-zA-Z]', function(c)
        local byte = string.byte(c)
        if byte >= byte_a and byte <= byte_a + 25 then
            return string.char(byte_a + (byte - byte_a + 13) % 26)
        else
            return string.char(byte_A + (byte - byte_A + 13) % 26)
        end
    end))
end

-- ===== 凯撒密码 =====
function crypto.caesar_encrypt(text, shift)
    shift = shift or 3
    local byte_a, byte_A = string.byte('a'), string.byte('A')
    return (text:gsub('[a-zA-Z]', function(c)
        local byte = string.byte(c)
        if byte >= byte_a and byte <= byte_a + 25 then
            return string.char(byte_a + (byte - byte_a + shift) % 26)
        else
            return string.char(byte_A + (byte - byte_A + shift) % 26)
        end
    end))
end

function crypto.caesar_decrypt(text, shift)
    shift = shift or 3
    return crypto.caesar_encrypt(text, 26 - shift)
end

-- ===== 字符串反转 =====
function crypto.reverse(str)
    return str:reverse()
end

-- ===== 频率分析（密码分析用） =====
function crypto.frequency_analysis(text)
    local freq = {}
    local total = 0
    
    for c in text:gmatch('%a') do
        c = c:lower()
        freq[c] = (freq[c] or 0) + 1
        total = total + 1
    end
    
    -- 转换为百分比并排序
    local result = {}
    for char, count in pairs(freq) do
        table.insert(result, {char = char, count = count, percent = count / total * 100})
    end
    table.sort(result, function(a, b) return a.count > b.count end)
    
    return result
end

-- ===== MD5 (使用 LuaJIT FFI 或外部库) =====
-- 纯 Lua 实现的 MD5 较复杂，实际使用建议用 lua-resty-md5
function crypto.md5(data)
    -- 在 OpenResty 环境中可使用 ngx.md5
    if ngx and ngx.md5 then
        return ngx.md5(data)
    end
    error("MD5 requires ngx.md5 or lua-resty-md5")
end

-- ===== 使用示例 =====
print("=== 加密编码工具 ===")

-- Base64
local encoded = crypto.base64_encode("Hello, World!")
print("Base64 编码:", encoded)
print("Base64 解码:", crypto.base64_decode(encoded))

-- URL 编码
local url_enc = crypto.url_encode("测试=test&123")
print("URL 编码:", url_enc)
print("URL 解码:", crypto.url_decode(url_enc))

-- XOR
local xor_enc = crypto.base64_encode(crypto.xor_encrypt("secret data", "key"))
print("XOR 加密 (base64):", xor_enc)

-- ROT13
print("ROT13:", crypto.rot13("Hello World"))

-- 频率分析
print("\n频率分析:")
local freq = crypto.frequency_analysis("hello world this is a test")
for i, item in ipairs(freq) do
    print(string.format("  %s: %d (%.1f%%)", item.char, item.count, item.percent))
    if i >= 5 then break end
end

return crypto
```

---

## 五、进阶学习资源

### 5.1 Lua 安全资源

- **Lua 官方文档**：https://www.lua.org/docs.html
- **Lua 编程指南**：https://www.lua.org/pil/contents.html
- **OpenResty 安全**：https://openresty.org/en/
- **LuaJIT**：https://luajit.org/

### 5.2 安全工具与库

- **Web 安全**：
  - lua-resty-waf — OpenResty WAF：https://github.com/p0pr0ck5/lua-resty-waf
  - lua-resty-lock — 分布式锁
  - lua-resty-limit-traffic — 流量限制
  - ngx_lua — Nginx Lua 模块

- **加密库**：
  - lua-resty-string — 字符串与加密
  - luaossl — OpenSSL 绑定
  - luacrypto — 加密库
  - lua-resty-jwt — JWT 处理

- **游戏安全**：
  - Lua 逆向与脱壳
  - LuaJIT 字节码分析
  - unluac — Lua 反编译
  - luadec — Lua 反编译器

### 5.3 OpenResty / Nginx

- **OpenResty 官方文档**：https://openresty.org/en/documentation.html
- **lua-nginx-module**：https://github.com/openresty/lua-nginx-module
- **OpenResty 最佳实践**：https://openresty.org/download/agentzh-nginx-tutorials-en.html
- **WAF 实现参考**：https://github.com/loveshell/ngx_lua_waf

### 5.4 CTF 与练习平台

- **Hack The Box**：https://www.hackthebox.com/
- **TryHackMe**：https://tryhackme.com/
- **CTFtime**：https://ctftime.org/
- **攻防世界**：https://adworld.xctf.org.cn/
- **BUUCTF**：https://buuoj.cn/

### 5.5 推荐书籍

- **Lua 编程**：
  - 《Lua 程序设计》（Programming in Lua）
  - 《Lua 编程入门》
  - 《Lua 游戏开发实践指南》

- **OpenResty**：
  - 《OpenResty 最佳实践》
  - 《Nginx 与 Lua 开发实战》
  - 《自己动手写 WAF》

- **安全方向**：
  - 《Web 安全深度剖析》
  - 《白帽子讲 Web 安全》

### 5.6 社区与博客

- **Lua 官方**：https://www.lua.org/
- **OpenResty 官方博客**：https://blog.openresty.com/
- **Lua 中文社区**：http://lua-users.org/
- **FreeBuf**：https://www.freebuf.com/
- **先知社区**：https://xz.aliyun.com/

### 5.7 进阶学习路线

**第 1 阶段：Lua 精通（1月）**
- 基础语法与数据结构
- 元表与元方法
- 协程与闭包
- 模块与包

**第 2 阶段：OpenResty 开发（2-3月）**
- Nginx Lua 模块
- OpenResty 生态
- WAF 开发
- 高性能 Web 服务

**第 3 阶段：游戏安全（2-3月）**
- Lua 逆向
- 脱壳与反编译
- Hook 与修改
- 内存分析

**第 4 阶段：安全工具（2-3月）**
- WAF 规则开发
- 流量分析
- 自动化脚本
- 协议分析

**第 5 阶段：实战与研究（持续）**
- CTF 比赛
- 安全工具开发
- Lua 漏洞研究
- 游戏安全研究
