# Net::HTTP - Ruby HTTP 客户端

> Ruby 标准库 HTTP 客户端，用于发送 HTTP 请求。

---

## 一、基本用法

### 1.1 简单 GET 请求

```ruby
require 'net/http'
require 'uri'

# 简单 GET
uri = URI('https://api.example.com/users')
response = Net::HTTP.get_response(uri)

puts response.code       # 状态码
puts response.message    # 状态文本
puts response.body       # 响应体

# 更简单的方式（Net::HTTP.get）
body = Net::HTTP.get(uri)
puts body

# get 打印版
Net::HTTP.get_print(uri)  # 直接输出到 stdout
```

### 1.2 URI 解析

```ruby
require 'uri'

uri = URI('https://user:pass@example.com:8080/path?q=value#frag')

puts uri.scheme      # "https"
puts uri.userinfo    # "user:pass"
puts uri.host        # "example.com"
puts uri.port        # 8080
puts uri.path        # "/path"
puts uri.query       # "q=value"
puts uri.fragment    # "frag"

# 查询参数
params = URI.decode_www_form(uri.query)
# [["q", "value"]]

# 构建查询参数
params = [['page', '1'], ['limit', '10']]
uri.query = URI.encode_www_form(params)
# "page=1&limit=10"

# 哈希方式（Ruby 2.7+）
params = { page: 1, limit: 10 }
uri.query = URI.encode_www_form(params)
```

---

## 二、HTTP 请求

### 2.1 完整的请求流程

```ruby
require 'net/http'
require 'uri'

uri = URI('https://api.example.com/data')

# 创建 HTTP 对象
http = Net::HTTP.new(uri.host, uri.port)

# 启用 HTTPS
http.use_ssl = true if uri.scheme == 'https'

# 设置超时
http.open_timeout = 5   # 连接超时（秒）
http.read_timeout = 5   # 读取超时
http.write_timeout = 5  # 写入超时

# 设置代理
# http = Net::HTTP.new(uri.host, uri.port, 'proxy.host', 8080)

# 创建请求
req = Net::HTTP::Get.new(uri)
req['Accept'] = 'application/json'
req['Authorization'] = 'Bearer token123'
req['User-Agent'] = 'MyApp/1.0'

# 发送请求
response = http.request(req)

# 处理响应
case response
when Net::HTTPSuccess
    puts "成功: #{response.body}"
when Net::HTTPRedirection
    puts "重定向到: #{response['location']}"
when Net::HTTPClientError
    puts "客户端错误: #{response.code}"
when Net::HTTPServerError
    puts "服务器错误: #{response.code}"
end
```

### 2.2 各种 HTTP 方法

```ruby
require 'net/http'
require 'uri'
require 'json'

uri = URI('https://api.example.com/users')
http = Net::HTTP.new(uri.host, uri.port)
http.use_ssl = true

# GET
req = Net::HTTP::Get.new(uri)
response = http.request(req)

# POST (表单数据)
req = Net::HTTP::Post.new(uri)
req.set_form_data({ 'username' => 'john', 'password' => 'secret' })
response = http.request(req)

# POST (JSON)
req = Net::HTTP::Post.new(uri)
req['Content-Type'] = 'application/json'
req.body = { name: 'John', email: 'john@example.com' }.to_json
response = http.request(req)

# PUT
req = Net::HTTP::Put.new(uri)
req['Content-Type'] = 'application/json'
req.body = { name: 'Updated' }.to_json
response = http.request(req)

# PATCH
req = Net::HTTP::Patch.new(uri)
req.body = { name: 'Patched' }.to_json
response = http.request(req)

# DELETE
req = Net::HTTP::Delete.new(uri)
response = http.request(req)

# HEAD
req = Net::HTTP::Head.new(uri)
response = http.request(req)
puts response['Content-Length']

# OPTIONS
req = Net::HTTP::Options.new(uri)
response = http.request(req)
```

### 2.3 响应处理

```ruby
response = http.request(req)

# 状态
response.code           # "200"（字符串）
response.code.to_i      # 200（整数）
response.message        # "OK"
response.is_a?(Net::HTTPSuccess)  # true (2xx)
response.is_a?(Net::HTTPRedirection)  # 3xx

# 响应头
response['Content-Type']
response['Set-Cookie']
response.each_header do |key, value|
    puts "#{key}: #{value}"
end

# 响应体
response.body           # 字符串
response.body.encoding  # 编码

# 流式读取（大文件）
File.open('download.bin', 'wb') do |file|
    http.request(req) do |response|
        response.read_body do |chunk|
            file.write(chunk)
        end
    end
end
```

### 2.4 块方式请求

```ruby
require 'net/http'
require 'uri'

uri = URI('https://example.com/large-file')

Net::HTTP.start(uri.host, uri.port, use_ssl: true) do |http|
    request = Net::HTTP::Get.new uri
    
    http.request(request) do |response|
        # 检查状态
        unless response.is_a?(Net::HTTPSuccess)
            raise "HTTP Error: #{response.code}"
        end
        
        # 流式处理
        total = 0
        response.read_body do |chunk|
            total += chunk.size
            puts "已下载 #{total} 字节"
        end
    end
end  # 自动关闭连接
```

---

## 三、高级用法

### 3.1 重定向处理

```ruby
require 'net/http'
require 'uri'

def fetch(uri_str, limit = 10)
    raise '重定向次数过多' if limit <= 0
    
    uri = URI(uri_str)
    
    response = Net::HTTP.get_response(uri)
    
    case response
    when Net::HTTPSuccess
        response.body
    when Net::HTTPRedirection
        location = response['location']
        puts "重定向到: #{location}"
        fetch(location, limit - 1)
    else
        response.value  # 抛出异常
    end
end

# 使用
begin
    body = fetch('http://example.com')
    puts body
rescue => e
    puts "错误: #{e.message}"
end
```

### 3.2 文件上传

```ruby
require 'net/http'
require 'uri'

uri = URI('https://api.example.com/upload')
http = Net::HTTP.new(uri.host, uri.port)
http.use_ssl = true

#  multipart 上传
boundary = "----RubyFormBoundary#{rand(1000000)}"
file_content = File.read('file.txt')

post_body = []
post_body << "--#{boundary}\r\n"
post_body << "Content-Disposition: form-data; name=\"file\"; filename=\"file.txt\"\r\n"
post_body << "Content-Type: text/plain\r\n\r\n"
post_body << file_content
post_body << "\r\n--#{boundary}--\r\n"

req = Net::HTTP::Post.new(uri)
req['Content-Type'] = "multipart/form-data; boundary=#{boundary}"
req.body = post_body.join

response = http.request(req)
```

### 3.3 Basic Auth

```ruby
require 'net/http'
require 'uri'

uri = URI('https://api.example.com/protected')

req = Net::HTTP::Get.new(uri)
req.basic_auth('username', 'password')  # 自动设置 Authorization 头

http = Net::HTTP.new(uri.host, uri.port)
http.use_ssl = true
response = http.request(req)
```

---

## 四、安全相关内容

### 4.1 SSL/TLS 安全

```ruby
require 'net/http'
require 'openssl'

# ===== 默认配置（安全）=====
# Ruby 默认验证证书
uri = URI('https://secure.example.com')
response = Net::HTTP.get_response(uri)
# 证书无效会抛出 OpenSSL::SSL::SSLError

# ===== 危险：禁用证书验证（不要这样做！）=====
# http.verify_mode = OpenSSL::SSL::VERIFY_NONE
# 这会导致中间人攻击

# ===== 自定义证书验证 =====
http = Net::HTTP.new(uri.host, uri.port)
http.use_ssl = true

# 验证模式
http.verify_mode = OpenSSL::SSL::VERIFY_PEER  # 推荐

# 指定 CA 证书
http.ca_file = '/path/to/ca.pem'
# 或
http.ca_path = '/path/to/certs/'

# 证书版本
http.ssl_version = :TLSv1_2  # 强制 TLS 1.2

# 密码套件
http.ciphers = 'ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256'
```

### 4.2 SSRF 防护

```ruby
require 'net/http'
require 'uri'
require 'ipaddr'

# 检查是否是内网/保留 IP
def private_ip?(ip_str)
    ip = IPAddr.new(ip_str)
    
    private_ranges = [
        IPAddr.new('10.0.0.0/8'),
        IPAddr.new('172.16.0.0/12'),
        IPAddr.new('192.168.0.0/16'),
        IPAddr.new('127.0.0.0/8'),
        IPAddr.new('169.254.0.0/16'),
        IPAddr.new('::1/128'),
        IPAddr.new('fc00::/7'),
        IPAddr.new('fe80::/10'),
    ]
    
    private_ranges.any? { |range| range.include?(ip) }
rescue IPAddr::InvalidAddressError
    true
end

# 安全的 HTTP 请求（防止 SSRF）
def safe_http_get(url_str)
    uri = URI(url_str)
    
    # 检查协议
    unless %w[http https].include?(uri.scheme)
        raise SecurityError, "不支持的协议: #{uri.scheme}"
    end
    
    # 解析 IP 并检查
    host = uri.host
    addresses = Addrinfo.getaddrinfo(host, nil)
    
    addresses.each do |addr|
        if private_ip?(addr.ip_address)
            raise SecurityError, "禁止访问内网地址: #{addr.ip_address}"
        end
    end
    
    # 注意：DNS 重绑定攻击可能绕过
    # 更好的方式是直接连接 IP
    
    Net::HTTP.get(uri)
end
```

### 4.3 输入验证

```ruby
require 'uri'

# 安全的 URL 验证
def safe_url?(url_str)
    uri = URI.parse(url_str)
    
    # 只允许 http 和 https
    return false unless %w[http https].include?(uri.scheme)
    
    # 必须有主机名
    return false if uri.host.nil? || uri.host.empty?
    
    # 检查主机名格式
    return false unless uri.host.match?(/\A[a-zA-Z0-9.-]+\z/)
    
    true
rescue URI::InvalidURIError
    false
end

# 验证端口
def valid_port?(port)
    port.is_a?(Integer) && port >= 1 && port <= 65535
end

# 限制响应大小（防止大文件攻击）
def http_get_with_limit(uri, max_bytes = 10 * 1024 * 1024)
    http = Net::HTTP.new(uri.host, uri.port)
    http.use_ssl = uri.scheme == 'https'
    
    request = Net::HTTP::Get.new(uri)
    
    data = ''
    http.request(request) do |response|
        unless response.is_a?(Net::HTTPSuccess)
            raise "HTTP Error: #{response.code}"
        end
        
        content_length = response['Content-Length']&.to_i
        if content_length && content_length > max_bytes
            raise "响应过大: #{content_length} 字节"
        end
        
        response.read_body do |chunk|
            data << chunk
            if data.bytesize > max_bytes
                raise "响应超过最大限制"
            end
        end
    end
    
    data
end
```

### 4.4 常见安全问题

```ruby
=begin
    Ruby Net::HTTP 常见安全问题：
    
    1. SSL 证书验证被禁用
       - 有时为了方便设置 VERIFY_NONE
       - 导致中间人攻击
    
    2. SSRF（服务端请求伪造）
       - 用户可控的 URL
       - 访问内网资源
    
    3. 超时设置不当
       - 默认没有超时
       - 可能被慢连接耗尽资源
    
    4. 响应大小未限制
       - 大响应导致内存耗尽
    
    5. 重定向未验证
       - 跟随重定向到内网地址
    
    6. 敏感信息泄露
       - 错误信息包含 URL、请求头等
=end

# 安全的 HTTP 客户端封装
class SafeHttpClient
    MAX_REDIRECTS = 5
    DEFAULT_TIMEOUT = 10
    MAX_BODY_SIZE = 10 * 1024 * 1024  # 10 MB
    
    def initialize(options = {})
        @timeout = options[:timeout] || DEFAULT_TIMEOUT
        @max_redirects = options[:max_redirects] || MAX_REDIRECTS
        @max_body_size = options[:max_body_size] || MAX_BODY_SIZE
    end
    
    def get(url, headers = {})
        request(:get, url, nil, headers)
    end
    
    def post(url, body = nil, headers = {})
        request(:post, url, body, headers)
    end
    
    private
    
    def request(method, url, body, headers, redirect_count = 0)
        raise "重定向次数过多" if redirect_count > @max_redirects
        
        uri = URI(url)
        
        # 验证 URL
        validate_uri(uri)
        
        http = Net::HTTP.new(uri.host, uri.port)
        http.use_ssl = uri.scheme == 'https'
        http.open_timeout = @timeout
        http.read_timeout = @timeout
        http.write_timeout = @timeout if http.respond_to?(:write_timeout=)
        
        # 确保 SSL 验证开启
        if http.use_ssl?
            http.verify_mode = OpenSSL::SSL::VERIFY_PEER
        end
        
        req = build_request(method, uri, body, headers)
        response = http.request(req)
        
        case response
        when Net::HTTPSuccess
            read_body_with_limit(response)
        when Net::HTTPRedirection
            location = response['location']
            request(method, location, body, headers, redirect_count + 1)
        else
            raise "HTTP Error: #{response.code} #{response.message}"
        end
    end
    
    def validate_uri(uri)
        unless %w[http https].include?(uri.scheme)
            raise SecurityError, "不支持的协议: #{uri.scheme}"
        end
    end
    
    def build_request(method, uri, body, headers)
        req_class = case method
                    when :get then Net::HTTP::Get
                    when :post then Net::HTTP::Post
                    when :put then Net::HTTP::Put
                    when :delete then Net::HTTP::Delete
                    else raise "不支持的方法: #{method}"
                    end
        
        req = req_class.new(uri)
        headers.each { |k, v| req[k] = v }
        
        if body
            req['Content-Type'] ||= 'application/json'
            req.body = body.is_a?(Hash) ? body.to_json : body.to_s
        end
        
        req
    end
    
    def read_body_with_limit(response)
        data = ''
        response.read_body do |chunk|
            data << chunk
            raise "响应过大" if data.bytesize > @max_body_size
        end
        data
    end
end
```

---

## 五、响应状态码速查

| 类 | 状态码范围 | 含义 |
|----|-----------|------|
| `Net::HTTPInformation` | 1xx | 信息 |
| `Net::HTTPSuccess` | 2xx | 成功 |
| `Net::HTTPRedirection` | 3xx | 重定向 |
| `Net::HTTPClientError` | 4xx | 客户端错误 |
| `Net::HTTPServerError` | 5xx | 服务器错误 |
| `Net::HTTPNotFound` | 404 | 未找到 |
| `Net::HTTPUnauthorized` | 401 | 未授权 |
| `Net::HTTPForbidden` | 403 | 禁止访问 |
