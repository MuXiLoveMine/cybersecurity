# ============================================================
# Ruby Net::HTTP 网络请求：GET、POST、自定义 Header
# 运行方式：ruby 08_http.rb
# ============================================================

require 'net/http'
require 'uri'
require 'json'

# ---------- 1. 简单 GET 请求 ----------
puts "========== 1. 简单 GET 请求 =========="

# 使用 Net::HTTP.get 最简单的 GET 请求
uri = URI("http://httpbin.org/get")

begin
  puts "请求 URL：#{uri}"
  response = Net::HTTP.get(uri)
  puts "响应内容："
  puts response
rescue => e
  puts "请求失败：#{e.message}"
  puts "提示：请确保网络连接正常，或可以访问 httpbin.org"
end

# ---------- 2. 带参数的 GET 请求 ----------
puts "\n========== 2. 带参数的 GET 请求 =========="

# 使用 URI.encode_www_form 构建查询参数
params = { name: "张三", age: 25, city: "北京" }
uri = URI("http://httpbin.org/get")
uri.query = URI.encode_www_form(params)

begin
  puts "请求 URL：#{uri}"
  response = Net::HTTP.get(uri)
  data = JSON.parse(response)
  puts "请求参数：#{data['args'].inspect}"
rescue => e
  puts "请求失败：#{e.message}"
end

# ---------- 3. 完整的 HTTP 请求（可自定义更多选项）----------
puts "\n========== 3. 完整的 HTTP GET 请求 =========="

uri = URI("http://httpbin.org/get")

begin
  # 创建 HTTP 连接
  http = Net::HTTP.new(uri.host, uri.port)
  http.open_timeout = 10   # 打开连接超时
  http.read_timeout = 10   # 读取超时

  # 创建请求对象
  request = Net::HTTP::Get.new(uri.request_uri)

  # 发送请求
  response = http.request(request)

  puts "状态码：#{response.code}"
  puts "状态信息：#{response.message}"
  puts "响应体长度：#{response.body.length} 字节"
  puts "响应体（前 200 字符）："
  puts response.body[0..200]
rescue => e
  puts "请求失败：#{e.message}"
end

# ---------- 4. 自定义 Request Header ----------
puts "\n========== 4. 自定义 Request Header =========="

uri = URI("http://httpbin.org/headers")

begin
  http = Net::HTTP.new(uri.host, uri.port)
  request = Net::HTTP::Get.new(uri.request_uri)

  # 添加自定义 Header
  request["User-Agent"] = "MyRubyClient/1.0 (Ruby #{RUBY_VERSION})"
  request["Accept"] = "application/json"
  request["Authorization"] = "Bearer my-token-123"
  request["X-Custom-Header"] = "custom-value"
  request["X-Request-Id"] = "req-#{Time.now.to_i}"

  puts "发送的自定义 Header："
  puts "  User-Agent: #{request['User-Agent']}"
  puts "  Accept: #{request['Accept']}"
  puts "  Authorization: #{request['Authorization']}"
  puts "  X-Custom-Header: #{request['X-Custom-Header']}"

  response = http.request(request)
  data = JSON.parse(response.body)

  puts "\n服务器收到的 Header："
  data["headers"].each do |key, value|
    puts "  #{key}: #{value}"
  end
rescue => e
  puts "请求失败：#{e.message}"
end

# ---------- 5. POST 请求（表单数据）----------
puts "\n========== 5. POST 请求（表单数据）=========="

uri = URI("http://httpbin.org/post")

begin
  http = Net::HTTP.new(uri.host, uri.port)
  request = Net::HTTP::Post.new(uri.request_uri)

  # 设置表单数据
  form_data = {
    username: "admin",
    password: "123456",
    remember_me: "1"
  }
  request.set_form_data(form_data)

  response = http.request(request)
  data = JSON.parse(response.body)

  puts "状态码：#{response.code}"
  puts "提交的表单数据：#{data['form'].inspect}"
rescue => e
  puts "请求失败：#{e.message}"
end

# ---------- 6. POST 请求（JSON 数据）----------
puts "\n========== 6. POST 请求（JSON 数据）=========="

uri = URI("http://httpbin.org/post")

begin
  http = Net::HTTP.new(uri.host, uri.port)
  request = Net::HTTP::Post.new(uri.request_uri)

  # 设置 Content-Type 为 JSON
  request["Content-Type"] = "application/json"
  request["Accept"] = "application/json"

  # 构造 JSON 请求体
  payload = {
    user: {
      name: "张三",
      email: "zhangsan@example.com",
      age: 25
    },
    action: "create"
  }
  request.body = payload.to_json

  puts "请求体：#{request.body}"

  response = http.request(request)
  data = JSON.parse(response.body)

  puts "\n状态码：#{response.code}"
  puts "服务器收到的数据：#{data['json'].inspect}"
  puts "Content-Type：#{data['headers']['Content-Type']}"
rescue => e
  puts "请求失败：#{e.message}"
end

# ---------- 7. HTTPS 请求 ----------
puts "\n========== 7. HTTPS 请求 =========="

uri = URI("https://httpbin.org/get")

begin
  http = Net::HTTP.new(uri.host, uri.port)
  http.use_ssl = true               # 启用 SSL
  http.verify_mode = OpenSSL::SSL::VERIFY_PEER  # 验证证书（推荐）

  # 如果需要跳过证书验证（不推荐，仅用于测试）
  # http.verify_mode = OpenSSL::SSL::VERIFY_NONE

  request = Net::HTTP::Get.new(uri.request_uri)
  response = http.request(request)

  puts "HTTPS 状态码：#{response.code}"
  puts "响应体（前 100 字符）：#{response.body[0..100]}..."
rescue => e
  puts "HTTPS 请求失败：#{e.message}"
end

# ---------- 8. 其他 HTTP 方法 ----------
puts "\n========== 8. 其他 HTTP 方法 =========="

uri = URI("http://httpbin.org/put")

begin
  http = Net::HTTP.new(uri.host, uri.port)

  # PUT 请求
  puts "PUT 请求："
  request = Net::HTTP::Put.new(uri.request_uri)
  request["Content-Type"] = "application/json"
  request.body = { id: 1, name: "更新后名称" }.to_json
  response = http.request(request)
  puts "  状态码：#{response.code}"

  # PATCH 请求
  puts "\nPATCH 请求："
  uri_patch = URI("http://httpbin.org/patch")
  request = Net::HTTP::Patch.new(uri_patch.request_uri)
  request["Content-Type"] = "application/json"
  request.body = { name: "部分更新" }.to_json
  response = http.request(request)
  puts "  状态码：#{response.code}"

  # DELETE 请求
  puts "\nDELETE 请求："
  uri_delete = URI("http://httpbin.org/delete")
  request = Net::HTTP::Delete.new(uri_delete.request_uri)
  response = http.request(request)
  puts "  状态码：#{response.code}"
rescue => e
  puts "请求失败：#{e.message}"
end

# ---------- 9. 响应头与状态码处理 ----------
puts "\n========== 9. 响应头与状态码处理 =========="

uri = URI("http://httpbin.org/response-headers?X-Custom=test_value&Server=MyServer")

begin
  http = Net::HTTP.new(uri.host, uri.port)
  request = Net::HTTP::Get.new(uri.request_uri)
  response = http.request(request)

  puts "状态码：#{response.code}"
  puts "状态码类别："
  case response
  when Net::HTTPSuccess
    puts "  2xx 成功"
  when Net::HTTPRedirection
    puts "  3xx 重定向"
  when Net::HTTPClientError
    puts "  4xx 客户端错误"
  when Net::HTTPServerError
    puts "  5xx 服务端错误"
  end

  puts "\n响应头："
  response.each_header do |name, value|
    puts "  #{name}: #{value}"
  end

  # 获取特定响应头
  puts "\nContent-Type：#{response['content-type']}"
  puts "Content-Length：#{response['content-length']}"
rescue => e
  puts "请求失败：#{e.message}"
end

# ---------- 10. 重定向跟随 ----------
puts "\n========== 10. 重定向跟随 =========="

def fetch_with_redirect(uri, limit = 5)
  raise "重定向次数过多" if limit <= 0

  http = Net::HTTP.new(uri.host, uri.port)
  http.use_ssl = true if uri.scheme == "https"

  request = Net::HTTP::Get.new(uri.request_uri)
  response = http.request(request)

  if response.is_a?(Net::HTTPRedirection)
    puts "  重定向到：#{response['location']}"
    new_uri = URI.parse(response['location'])
    # 处理相对路径重定向
    new_uri = uri + new_uri if new_uri.relative?
    fetch_with_redirect(new_uri, limit - 1)
  else
    response
  end
end

uri = URI("http://httpbin.org/redirect/2")
begin
  puts "请求 URL：#{uri}"
  response = fetch_with_redirect(uri)
  puts "最终状态码：#{response.code}"
  puts "最终 URL：#{uri}"
rescue => e
  puts "请求失败：#{e.message}"
end

# ---------- 11. 安全领域的 HTTP 示例 ----------
puts "\n========== 11. 安全场景示例 =========="

# 1. 模拟端口指纹识别（HTTP Banner 获取）
puts "--- 1. HTTP Banner 获取 ---"
targets = [
  { host: "httpbin.org", port: 80 },
]

targets.each do |target|
  begin
    uri = URI("http://#{target[:host]}:#{target[:port]}/")
    http = Net::HTTP.new(uri.host, uri.port)
    http.open_timeout = 5
    http.read_timeout = 5

    request = Net::HTTP::Get.new(uri.request_uri)
    request["User-Agent"] = "Mozilla/5.0 (compatible; SecurityScanner/1.0)"

    response = http.request(request)

    puts "  目标：#{target[:host]}:#{target[:port]}"
    puts "  状态码：#{response.code}"
    puts "  Server：#{response['server'] || '未知'}"
    puts "  X-Powered-By：#{response['x-powered-by'] || '未泄露'}"
    puts ""
  rescue => e
    puts "  目标 #{target[:host]}:#{target[:port]} 连接失败：#{e.message}"
  end
end

# 2. 模拟 SQL 注入检测
puts "--- 2. SQL 注入检测（模拟）---"

def test_sql_injection(base_url, param)
  uri = URI(base_url)
  http = Net::HTTP.new(uri.host, uri.port)
  http.use_ssl = true if uri.scheme == "https"
  http.open_timeout = 5
  http.read_timeout = 5

  # 正常请求
  normal_params = URI.encode_www_form(param => "1")
  normal_uri = URI("#{base_url}?#{normal_params}")
  normal_request = Net::HTTP::Get.new(normal_uri.request_uri)
  normal_response = http.request(normal_request)

  # 注入测试（单引号测试）
  injection_params = URI.encode_www_form(param => "1'")
  injection_uri = URI("#{base_url}?#{injection_params}")
  injection_request = Net::HTTP::Get.new(injection_uri.request_uri)
  injection_response = http.request(injection_request)

  # 比较响应长度和状态码
  len_diff = (normal_response.body.length - injection_response.body.length).abs
  puts "  正常响应长度：#{normal_response.body.length}"
  puts "  注入响应长度：#{injection_response.body.length}"
  puts "  长度差：#{len_diff}"

  # 检查常见 SQL 错误信息
  sql_errors = /(SQL syntax|mysql_fetch|Warning.*mysql|ORA-\d+|PostgreSQL.*ERROR|Microsoft SQL Server|Unclosed quotation mark)/i
  if injection_response.body.match?(sql_errors)
    puts "  [!] 发现 SQL 错误信息，可能存在注入漏洞！"
  elsif len_diff > 100
    puts "  [?] 响应长度差异较大，可能存在注入（需进一步验证）"
  else
    puts "  [-] 未发现明显注入迹象"
  end
end

# 注意：实际使用时请确保有授权，这里仅作示例
puts "  （示例函数已定义，实际使用需在授权范围内测试）"

# 3. 模拟 Cookie 安全性检测
puts "\n--- 3. Cookie 安全性检测（模拟）---"

def check_cookie_security(response)
  cookies = response.get_fields('set-cookie') || []
  puts "  找到 #{cookies.length} 个 Cookie"

  cookies.each do |cookie|
    name = cookie.split('=').first
    puts "\n  Cookie: #{name}"

    # 检查 HttpOnly
    if cookie.downcase.include?('httponly')
      puts "    [+] HttpOnly: 是"
    else
      puts "    [-] HttpOnly: 否（XSS 风险）"
    end

    # 检查 Secure
    if cookie.downcase.include?('secure')
      puts "    [+] Secure: 是"
    else
      puts "    [-] Secure: 否（中间人攻击风险）"
    end

    # 检查 SameSite
    if cookie.downcase.include?('samesite')
      samesite = cookie[/SameSite=(\w+)/i, 1]
      puts "    [+] SameSite: #{samesite}"
    else
      puts "    [-] SameSite: 未设置（CSRF 风险）"
    end
  end
end

begin
  uri = URI("http://httpbin.org/cookies/set/sessionid/abc123")
  http = Net::HTTP.new(uri.host, uri.port)
  request = Net::HTTP::Get.new(uri.request_uri)
  response = http.request(request)
  check_cookie_security(response)
rescue => e
  puts "  Cookie 检测失败：#{e.message}"
end

# 4. 简单的目录扫描函数
puts "\n--- 4. 目录扫描函数（示例）---"

def dir_brute_force(base_url, wordlist)
  uri = URI(base_url)
  http = Net::HTTP.new(uri.host, uri.port)
  http.use_ssl = true if uri.scheme == "https"
  http.open_timeout = 5
  http.read_timeout = 5

  found = []
  wordlist.each do |path|
    begin
      target_path = uri.path + path
      request = Net::HTTP::Get.new(target_path)
      response = http.request(request)

      case response.code
      when "200"
        puts "  [200] /#{path} - 存在"
        found << path
      when "301", "302"
        puts "  [#{response.code}] /#{path} - 重定向到 #{response['location']}"
      when "403"
        puts "  [403] /#{path} - 禁止访问"
      when "404"
        # 不输出 404，保持界面整洁
      else
        puts "  [#{response.code}] /#{path}"
      end
    rescue => e
      puts "  [ERR] /#{path} - #{e.message}"
    end
  end

  found
end

# 示例字典（实际使用中会加载更大的字典）
wordlist = %w[admin login upload backup test robots.txt .git config]
puts "  示例字典：#{wordlist.inspect}"
puts "  （实际使用需在授权范围内进行目录扫描）"

puts "\n========== 示例运行结束 =========="
