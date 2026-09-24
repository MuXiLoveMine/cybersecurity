# socket - LuaSocket 网络库

> LuaSocket 是 Lua 最常用的网络库，支持 TCP/UDP 等协议。

---

## 一、安装与引入

```lua
-- LuaRocks 安装
-- luarocks install luasocket

-- 引入
local socket = require("socket")
```

---

## 二、TCP 编程

### 2.1 TCP 客户端

```lua
local socket = require("socket")

-- 创建 TCP 客户端套接字
local client = socket.tcp()

-- 设置超时（秒）
client:settimeout(5)

-- 连接服务器
local ok, err = client:connect("example.com", 80)
if not ok then
    print("连接失败:", err)
    return
end

-- 发送数据
client:send("GET / HTTP/1.1\r\nHost: example.com\r\nConnection: close\r\n\r\n")

-- 接收响应
local response = ""
while true do
    local chunk, err, partial = client:receive("*a")
    if chunk then
        response = response .. chunk
        break
    elseif err == "timeout" then
        -- 超时处理
        if partial then
            response = response .. partial
        end
        break
    else
        print("接收错误:", err)
        break
    end
end

print(response)

-- 关闭连接
client:close()
```

### 2.2 TCP 服务器

```lua
local socket = require("socket")

-- 创建服务器套接字
local server = socket.tcp()

-- 设置地址重用
server:setoption("reuseaddr", true)

-- 绑定地址和端口
local ok, err = server:bind("*", 8080)
if not ok then
    print("绑定失败:", err)
    return
end

-- 开始监听（backlog = 32）
server:listen(32)

print("服务器监听端口 8080...")

-- 设置超时（非阻塞 accept）
server:settimeout(0)

-- 主循环
local clients = {}

while true do
    -- 接受新连接
    local client, err = server:accept()
    if client then
        print("新连接:", client:getpeername())
        client:settimeout(0)  -- 非阻塞模式
        table.insert(clients, client)
    end
    
    -- 处理客户端
    local i = 1
    while i <= #clients do
        local client = clients[i]
        local data, err, partial = client:receive("*l")  -- 读一行
        
        if data then
            print("收到:", data)
            client:send("Echo: " .. data .. "\n")
            i = i + 1
        elseif err == "timeout" then
            i = i + 1  -- 没有数据，继续
        else
            -- 连接关闭或出错
            print("连接关闭:", err)
            client:close()
            table.remove(clients, i)
        end
    end
    
    -- 简单的 sleep 避免 CPU 占用过高
    socket.sleep(0.01)
end
```

### 2.3 receive 模式

```lua
-- "*a" - 读取所有数据（直到连接关闭）
local data, err = client:receive("*a")

-- "*l" - 读取一行（不含换行符）
local line, err = client:receive("*l")

-- 数字 - 读取指定字节数
local data, err = client:receive(1024)  -- 读 1024 字节

-- partial 参数
-- 当 receive 返回错误时，第三个参数是已接收的部分数据
local data, err, partial = client:receive(1024)
if err == "timeout" and partial then
    -- 处理已收到的部分数据
end
```

### 2.4 套接字选项

```lua
local sock = socket.tcp()

-- 设置超时
sock:settimeout(5)        -- 总超时 5 秒
sock:settimeout(5, 't')   -- 仅总超时
sock:settimeout(5, 'b')   -- 阻塞超时

-- 地址重用
sock:setoption("reuseaddr", true)

-- TCP_NODELAY（禁用 Nagle 算法）
sock:setoption("tcp-nodelay", true)

-- SO_KEEPALIVE
sock:setoption("keepalive", true)

-- 发送/接收缓冲区
-- LuaSocket 不直接支持设置缓冲区大小
```

---

## 三、UDP 编程

### 3.1 UDP 客户端

```lua
local socket = require("socket")

-- 创建 UDP 套接字
local udp = socket.udp()

-- 设置超时
udp:settimeout(3)

-- 设置对等地址（可选）
udp:setpeername("127.0.0.1", 12345)

-- 发送数据
udp:send("Hello UDP")

-- 接收响应
local data, err = udp:receive()
if data then
    print("收到:", data)
else
    print("错误:", err)
end

udp:close()
```

### 3.2 UDP 服务器

```lua
local socket = require("socket")

-- 创建 UDP 套接字
local udp = socket.udp()

-- 绑定端口
udp:setsockname("*", 12345)

-- 设置超时
udp:settimeout(0)

print("UDP 服务器监听端口 12345...")

while true do
    -- 接收数据（同时获取发送方地址）
    local data, ip, port = udp:receivefrom()
    
    if data then
        print(string.format("收到来自 %s:%d 的消息: %s", ip, port, data))
        
        -- 回送响应
        udp:sendto("Echo: " .. data, ip, port)
    end
    
    socket.sleep(0.01)
end
```

---

## 四、HTTP 客户端

### 4.1 HTTP 模块

```lua
local http = require("socket.http")
local ltn12 = require("ltn12")

-- 简单 GET
local response_body, response_code, response_headers, response_status = 
    http.request("http://example.com")

print("状态码:", response_code)
print("响应:", response_body)

-- POST 请求
local request_body = "name=John&email=john@example.com"

local response_body = {}
local response_code, response_headers = http.request{
    url = "http://api.example.com/users",
    method = "POST",
    headers = {
        ["Content-Type"] = "application/x-www-form-urlencoded",
        ["Content-Length"] = #request_body,
        ["Accept"] = "application/json",
    },
    source = ltn12.source.string(request_body),
    sink = ltn12.sink.table(response_body),
}

print("状态码:", response_code)
print("响应:", table.concat(response_body))
```

### 4.2 URL 编码

```lua
local url = require("socket.url")

-- 解析 URL
local parsed = url.parse("http://user:pass@example.com:8080/path?q=value#frag")

-- parsed.scheme     = "http"
-- parsed.userinfo   = "user:pass"
-- parsed.host       = "example.com"
-- parsed.port       = "8080"
-- parsed.path       = "/path"
-- parsed.query      = "q=value"
-- parsed.fragment   = "frag"

-- 构建 URL
local url_str = url.build(parsed)

-- URL 编码/解码
local mime = require("mime")  -- 来自 LuaSec 或 mime 模块
-- 或手动实现简单的 URL 编码
function url_encode(str)
    if str then
        str = string.gsub(str, "\n", "\r\n")
        str = string.gsub(str, "([^%w %-%_%.%~])", function(c)
            return string.format("%%%02X", string.byte(c))
        end)
        str = string.gsub(str, " ", "+")
    end
    return str
end
```

---

## 五、安全相关内容

### 5.1 常见安全问题

```lua
--[[
    LuaSocket 安全注意事项：
    
    1. 没有内置 TLS/SSL
       - 纯 HTTP 传输不加密
       - 需要 LuaSec 库支持 HTTPS
       
    2. 缓冲区溢出风险
       - 读取大量数据时注意内存使用
       
    3. 超时设置
       - 默认没有超时，可能导致永久阻塞
       
    4. 输入验证
       - 网络数据是不可信的
       
    5. 没有沙箱保护
       - Lua 本身是安全的，但网络数据可能触发漏洞
]]
```

### 5.2 HTTPS (LuaSec)

```lua
-- 需要安装 LuaSec
-- luarocks install luasec

local https = require("ssl.https")
local ltn12 = require("ltn12")

-- HTTPS GET 请求
local response_body, response_code, response_headers = 
    https.request("https://example.com")

print("状态码:", response_code)
print("响应:", response_body)

-- 自定义 SSL 选项
local response_body = {}
local response_code = https.request{
    url = "https://secure.example.com",
    method = "GET",
    sink = ltn12.sink.table(response_body),
    mode = "client",
    protocol = "tlsv1_2",  -- TLS 版本
    verify = "peer",        -- 验证证书（推荐）
    options = "all",
    cafile = "/path/to/ca.pem",  -- CA 证书
}

--[[
    SSL 模式选项：
    - "tlsv1"   - TLS 1.0
    - "tlsv1_1" - TLS 1.1
    - "tlsv1_2" - TLS 1.2（推荐）
    - "tlsv1_3" - TLS 1.3
    
    验证选项：
    - "none"    - 不验证（危险！）
    - "peer"    - 验证对等方证书（推荐）
    - "client"  - 客户端证书验证
]]
```

### 5.3 输入验证

```lua
-- 端口验证
function is_valid_port(port)
    local p = tonumber(port)
    return p and p >= 1 and p <= 65535 and p == math.floor(p)
end

-- IP 地址格式验证（简单）
function is_valid_ip(ip)
    if type(ip) ~= "string" then return false end
    
    local parts = {ip:match("(%d+)%.(%d+)%.(%d+)%.(%d+)")}
    if #parts ~= 4 then return false end
    
    for _, part in ipairs(parts) do
        local num = tonumber(part)
        if num < 0 or num > 255 then return false end
    end
    
    return true
end

-- 安全的读取（限制大小）
function safe_receive(sock, max_bytes)
    local total = 0
    local data = ""
    local chunk_size = 4096
    
    while total < max_bytes do
        local to_read = math.min(chunk_size, max_bytes - total)
        local chunk, err, partial = sock:receive(to_read)
        
        if chunk then
            data = data .. chunk
            total = total + #chunk
        elseif err == "timeout" then
            if partial and #partial > 0 then
                data = data .. partial
                total = total + #partial
            end
            break
        else
            return nil, err
        end
    end
    
    if total >= max_bytes then
        return nil, "data too large"
    end
    
    return data
end
```

### 5.4 安全的服务器实践

```lua
local socket = require("socket")

-- 安全的 TCP 服务器模板
local server = {}

function server.new(port, handler)
    local self = setmetatable({}, {__index = server})
    
    self.port = port
    self.handler = handler
    self.clients = {}
    self.max_clients = 100  -- 最大连接数
    self.max_data_size = 1024 * 1024  -- 最大数据 1MB
    
    return self
end

function server:start()
    self.socket = socket.tcp()
    self.socket:setoption("reuseaddr", true)
    self.socket:bind("*", self.port)
    self.socket:listen(32)
    self.socket:settimeout(0)
    
    print("服务器启动，端口:", self.port)
    
    self.running = true
    while self.running do
        self:accept_clients()
        self:process_clients()
        socket.sleep(0.01)
    end
end

function server:accept_clients()
    while #self.clients < self.max_clients do
        local client, err = self.socket:accept()
        if client then
            client:settimeout(0)
            client.ip, client.port = client:getpeername()
            client.buffer = ""
            table.insert(self.clients, client)
            print("新连接:", client.ip .. ":" .. client.port)
        else
            break  -- 没有更多连接
        end
    end
end

function server:process_clients()
    local i = 1
    while i <= #self.clients do
        local client = self.clients[i]
        
        local data, err, partial = client:receive(4096)
        local chunk = data or partial or ""
        
        if #chunk > 0 then
            client.buffer = client.buffer .. chunk
            
            -- 检查是否超过最大限制
            if #client.buffer > self.max_data_size then
                print("数据过大，断开连接:", client.ip)
                client:close()
                table.remove(self.clients, i)
                goto continue
            end
            
            -- 处理完整的行
            while true do
                local line, rest = client.buffer:match("^(.-)\r?\n(.*)$")
                if not line then break end
                
                client.buffer = rest
                
                -- 调用处理函数
                local ok, err = pcall(self.handler, client, line)
                if not ok then
                    print("处理错误:", err)
                end
            end
        end
        
        if err and err ~= "timeout" then
            print("连接断开:", client.ip, err)
            client:close()
            table.remove(self.clients, i)
        else
            i = i + 1
        end
        
        ::continue::
    end
end

-- 使用示例
local srv = server.new(8080, function(client, line)
    print("收到:", line)
    client:send("Echo: " .. line .. "\n")
end)

srv:start()
```

---

## 六、其他功能

```lua
local socket = require("socket")

-- 睡眠
socket.sleep(1)         -- 睡眠 1 秒
socket.sleep(0.001)     -- 睡眠 1 毫秒

-- 获取时间（高精度）
local t1 = socket.gettime()
-- 做一些操作
local t2 = socket.gettime()
print("耗时:", t2 - t1, "秒")

-- DNS 解析
local ip = socket.dns.toip("www.example.com")
print("IP:", ip)

local hostname = socket.dns.tohostname("8.8.8.8")
print("主机名:", hostname)

-- 获取本机地址
local local_ip, local_hostname = socket.dns.getaddrinfo()
-- 或
local ip = socket.dns.toip(socket.dns.gethostname())
```

---

## 七、常见错误

| 错误 | 含义 |
|------|------|
| `timeout` | 操作超时 |
| `closed` | 连接已关闭 |
| `connection refused` | 连接被拒绝 |
| `host not found` | 主机名解析失败 |
| `address already in use` | 地址已被占用 |
| `permission denied` | 权限不足（如低端口） |
