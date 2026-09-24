#!/usr/bin/env ruby
# ============================================================
# HTTP 安全头检测工具 (HTTP Security Header Checker)
# ============================================================
#
# 【原理说明】
# HTTP 安全响应头是 Web 安全防护的重要组成部分，通过在 HTTP 响应中
# 设置适当的安全头，可以有效防御多种 Web 攻击，如 XSS、点击劫持、
# 信息泄露等。
#
# 本工具检测 7 大关键安全响应头的配置情况，并给出安全评分。
#
# 【7 大安全头说明】
# 1. X-Frame-Options
#    - 作用：防止页面被嵌入到 iframe 中，防御点击劫持攻击
#    - 推荐值：DENY 或 SAMEORIGIN
#    - 评分权重：高
#
# 2. X-Content-Type-Options
#    - 作用：禁止浏览器猜测 MIME 类型，防止 MIME 嗅探攻击
#    - 推荐值：nosniff
#    - 评分权重：中
#
# 3. X-XSS-Protection
#    - 作用：启用浏览器内置的 XSS 过滤器
#    - 推荐值：1; mode=block
#    - 评分权重：中（现代浏览器已逐渐废弃，建议使用 CSP 替代）
#
# 4. Content-Security-Policy (CSP)
#    - 作用：内容安全策略，限制资源加载来源，防御 XSS 和数据注入
#    - 推荐值：根据业务配置合理的策略
#    - 评分权重：高（最有效的 XSS 防护手段之一）
#
# 5. Strict-Transport-Security (HSTS)
#    - 作用：强制浏览器使用 HTTPS 访问，防止 SSL 剥离攻击
#    - 推荐值：max-age=31536000; includeSubDomains
#    - 评分权重：高（HTTPS 网站必备）
#
# 6. Referrer-Policy
#    - 作用：控制 Referer 信息的发送策略，保护用户隐私
#    - 推荐值：strict-origin-when-cross-origin 或 no-referrer
#    - 评分权重：中
#
# 7. Permissions-Policy (原 Feature-Policy)
#    - 作用：控制浏览器功能（如摄像头、麦克风、地理位置等）的使用权限
#    - 推荐值：根据业务需要最小化权限
#    - 评分权重：低
#
# 【额外检测】
# - Server 头信息泄露
# - X-Powered-By 头信息泄露
# - Cookie 安全性（HttpOnly、Secure、SameSite）
#
# 【使用方法】
#   ruby http_header_check.rb <目标URL>
#
# 【参数说明】
#   目标URL  - 必填，要检测的网站 URL
#
# 【示例】
#   ruby http_header_check.rb https://www.example.com
#   ruby http_header_check.rb http://127.0.0.1
#
# 【免责声明】
#   本工具仅供学习和授权测试使用，检测结果仅供参考。
#   实际安全配置需结合业务场景综合评估。
# ============================================================

require 'net/http'   # HTTP 客户端
require 'uri'        # URI 解析

# ============================================================
# 7 大安全头配置要求
# ============================================================
# 每个安全头的详细配置要求和评分标准
SECURITY_HEADERS = [
  {
    name: 'X-Frame-Options',
    description: '防止点击劫持攻击',
    weight: 15,  # 评分权重（满分 100 中的占比）
    recommended: ['DENY', 'SAMEORIGIN'],
    check: lambda { |value|
      return false if value.nil? || value.empty?
      upval = value.upcase.strip
      # 检查是否为推荐值之一
      ['DENY', 'SAMEORIGIN'].include?(upval) ||
      upval.start_with?('ALLOW-FROM')
    },
    risk: '未设置可能导致页面被恶意网站嵌入 iframe，引发点击劫持攻击',
    fix_advice: '建议设置为 DENY 或 SAMEORIGIN'
  },
  {
    name: 'X-Content-Type-Options',
    description: '防止 MIME 类型嗅探攻击',
    weight: 10,
    recommended: ['nosniff'],
    check: lambda { |value|
      return false if value.nil? || value.empty?
      value.downcase.strip == 'nosniff'
    },
    risk: '未设置可能导致浏览器猜测文件类型，引发 MIME 嗅探攻击',
    fix_advice: '建议设置为 nosniff'
  },
  {
    name: 'X-XSS-Protection',
    description: '浏览器 XSS 过滤器',
    weight: 10,
    recommended: ['1; mode=block'],
    check: lambda { |value|
      return false if value.nil? || value.empty?
      # 检查是否启用了 XSS 保护
      value =~ /^1/i && value =~ /mode=block/i
    },
    risk: '未设置可能降低浏览器对反射型 XSS 的防护能力',
    fix_advice: '建议设置为 1; mode=block（注意：现代浏览器已逐渐废弃，建议配合 CSP 使用）'
  },
  {
    name: 'Content-Security-Policy',
    description: '内容安全策略（防御 XSS）',
    weight: 20,
    recommended: ['根据业务配置合理策略'],
    check: lambda { |value|
      return false if value.nil? || value.empty?
      # 只要设置了 CSP 就算通过（实际配置合理性需人工评估）
      !value.strip.empty?
    },
    risk: '未设置 CSP 会大幅增加 XSS 攻击的风险',
    fix_advice: '建议根据业务配置合理的 CSP 策略，优先使用 nonce 或 strict-dynamic 模式'
  },
  {
    name: 'Strict-Transport-Security',
    description: '强制 HTTPS 访问（HSTS）',
    weight: 20,
    recommended: ['max-age=31536000; includeSubDomains'],
    check: lambda { |value|
      return false if value.nil? || value.empty?
      # 检查是否设置了合理的 max-age
      value =~ /max-age=\d+/i
    },
    risk: '未设置 HSTS 可能导致 SSL 剥离攻击，用户可能被降级到 HTTP 连接',
    fix_advice: '建议设置为 max-age=31536000; includeSubDomains（HTTPS 网站必备）'
  },
  {
    name: 'Referrer-Policy',
    description: '控制 Referer 信息发送',
    weight: 10,
    recommended: ['strict-origin-when-cross-origin', 'no-referrer'],
    check: lambda { |value|
      return false if value.nil? || value.empty?
      # 检查是否设置了安全的 Referrer 策略
      ['no-referrer', 'no-referrer-when-downgrade', 'same-origin',
       'strict-origin', 'strict-origin-when-cross-origin'].include?(value.downcase.strip)
    },
    risk: '未设置可能导致敏感信息通过 Referer 头泄露',
    fix_advice: '建议设置为 strict-origin-when-cross-origin 或 no-referrer'
  },
  {
    name: 'Permissions-Policy',
    description: '控制浏览器功能权限',
    weight: 5,
    recommended: ['根据业务最小化权限'],
    check: lambda { |value|
      return false if value.nil? || value.empty?
      !value.strip.empty?
    },
    risk: '未设置可能导致页面滥用浏览器功能（摄像头、麦克风等）',
    fix_advice: '建议根据业务需要设置，最小化功能权限，如 geolocation=(), microphone=()'
  },
  {
    name: 'X-Permitted-Cross-Domain-Policies',
    description: '控制跨域策略文件',
    weight: 5,
    recommended: ['none', 'master-only'],
    check: lambda { |value|
      return false if value.nil? || value.empty?
      ['none', 'master-only', 'by-content-type', 'all'].include?(value.downcase.strip)
    },
    risk: '未设置可能导致 Flash 等插件跨域读取数据',
    fix_advice: '建议设置为 none 或 master-only'
  },
].freeze

# ============================================================
# 信息泄露头检测
# ============================================================
INFO_LEAK_HEADERS = [
  {
    name: 'Server',
    description: '服务器版本信息',
    risk: '泄露服务器类型和版本，便于攻击者针对性攻击'
  },
  {
    name: 'X-Powered-By',
    description: '技术栈信息',
    risk: '泄露后端技术栈和版本，便于攻击者寻找对应漏洞'
  },
  {
    name: 'X-AspNet-Version',
    description: 'ASP.NET 版本',
    risk: '泄露 ASP.NET 版本信息'
  },
  {
    name: 'X-AspNetMvc-Version',
    description: 'ASP.NET MVC 版本',
    risk: '泄露 ASP.NET MVC 版本信息'
  },
].freeze

# ============================================================
# 发送 HTTP 请求并获取响应头
# ============================================================
# @param url [String] 目标 URL
# @param timeout [Integer] 超时时间（秒）
# @return [Hash] 响应头和状态码
def fetch_headers(url, timeout = 15)
  uri = URI(url)
  result = {
    status_code: 0,
    headers: {},
    cookies: [],
    error: nil
  }

  begin
    http = Net::HTTP.new(uri.host, uri.port)
    http.open_timeout = timeout
    http.read_timeout = timeout

    if uri.scheme == 'https'
      http.use_ssl = true
      http.verify_mode = OpenSSL::SSL::VERIFY_NONE
    end

    # 发送 HEAD 请求获取响应头（更高效）
    request = Net::HTTP::Head.new(uri.request_uri)
    request['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    request['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'

    response = http.request(request)

    # 如果 HEAD 请求失败（如 405 Method Not Allowed），改用 GET 请求
    if response.code.to_i == 405
      request = Net::HTTP::Get.new(uri.request_uri)
      request['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      response = http.request(request)
    end

    result[:status_code] = response.code.to_i

    # 收集所有响应头（转为小写键名，方便匹配）
    response.each_header do |name, value|
      result[:headers][name.downcase] = value
    end

    # 收集 Set-Cookie
    cookies = response.get_fields('set-cookie')
    result[:cookies] = cookies || []

  rescue => e
    result[:error] = e.message
  end

  result
end

# ============================================================
# 获取响应头值（不区分大小写）
# ============================================================
# @param headers [Hash] 响应头哈希
# @param name [String] 头名称
# @return [String, nil] 头的值
def get_header_value(headers, name)
  headers[name.downcase]
end

# ============================================================
# 检查 Cookie 安全性
# ============================================================
# @param cookies [Array] Cookie 列表
# @return [Hash] 检测结果
def check_cookie_security(cookies)
  result = {
    total: cookies.length,
    httponly: 0,
    secure: 0,
    samesite: 0,
    details: []
  }

  cookies.each do |cookie|
    cookie_down = cookie.downcase
    name = cookie.split('=').first

    info = { name: name, httponly: false, secure: false, samesite: nil }

    if cookie_down.include?('httponly')
      info[:httponly] = true
      result[:httponly] += 1
    end

    if cookie_down.include?('secure')
      info[:secure] = true
      result[:secure] += 1
    end

    # 提取 SameSite 值
    if cookie =~ /SameSite=(\w+)/i
      info[:samesite] = $1
      result[:samesite] += 1
    end

    result[:details] << info
  end

  result
end

# ============================================================
# 安全头检测主函数
# ============================================================
# @param url [String] 目标 URL
def check_security_headers(url)
  puts "\n" + '=' * 60
  puts '[*] HTTP 安全头检测工具 (Ruby 版)'
  puts '=' * 60
  puts "[*] 目标 URL: #{url}"
  puts '=' * 60

  # 获取响应头
  puts "\n[*] 正在获取响应头..."
  result = fetch_headers(url)

  if result[:error]
    puts "[!] 请求失败: #{result[:error]}"
    return nil
  end

  puts "[+] 连接成功，状态码: #{result[:status_code]}"
  puts "[+] 响应头数量: #{result[:headers].length}"

  headers = result[:headers]
  total_score = 0     # 总得分
  max_score = 0       # 满分
  passed_count = 0    # 通过的安全头数量

  # ============================================================
  # 检测 7 大安全头
  # ============================================================
  puts "\n" + '=' * 60
  puts '[*] 安全头检测结果'
  puts '=' * 60

  SECURITY_HEADERS.each do |header_config|
    header_name = header_config[:name]
    header_value = get_header_value(headers, header_name)
    weight = header_config[:weight]
    max_score += weight

    puts "\n[#{header_name}]"
    puts "  说明: #{header_config[:description]}"
    puts "  权重: #{weight} 分"

    if header_value.nil?
      # 未设置
      puts "  状态: [未设置] - 未通过"
      puts "  风险: #{header_config[:risk]}"
      puts "  建议: #{header_config[:fix_advice]}"
    else
      # 已设置，检查配置是否合理
      is_good = header_config[:check].call(header_value)

      if is_good
        puts "  状态: [已设置] - 通过"
        puts "  当前值: #{header_value}"
        total_score += weight
        passed_count += 1
      else
        puts "  状态: [已设置] - 配置不规范"
        puts "  当前值: #{header_value}"
        puts "  推荐值: #{header_config[:recommended].join(' / ')}"
        puts "  建议: #{header_config[:fix_advice]}"
        # 配置不规范给一半分
        total_score += weight / 2
      end
    end
  end

  # ============================================================
  # 信息泄露头检测
  # ============================================================
  puts "\n" + '=' * 60
  puts '[*] 信息泄露头检测'
  puts '=' * 60

  leaked_headers = []
  INFO_LEAK_HEADERS.each do |info_header|
    header_value = get_header_value(headers, info_header[:name])
    unless header_value.nil?
      leaked_headers << { name: info_header[:name], value: header_value, risk: info_header[:risk] }
      puts "\n[!] #{info_header[:name]}: #{header_value}"
      puts "    风险: #{info_header[:risk]}"
      puts "    建议: 建议移除或模糊化该响应头"
    end
  end

  if leaked_headers.empty?
    puts "\n[+] 未发现明显的信息泄露头"
  end

  # ============================================================
  # Cookie 安全检测
  # ============================================================
  puts "\n" + '=' * 60
  puts '[*] Cookie 安全检测'
  puts '=' * 60

  cookie_result = check_cookie_security(result[:cookies])

  if cookie_result[:total] == 0
    puts "\n[-] 未检测到 Set-Cookie 响应头"
  else
    puts "\n[*] 共检测到 #{cookie_result[:total]} 个 Cookie:"

    cookie_result[:details].each do |cookie|
      puts "\n  Cookie: #{cookie[:name]}"
      puts "    HttpOnly: #{cookie[:httponly] ? '[+] 是' : '[-] 否（XSS 风险）'}"
      puts "    Secure:   #{cookie[:secure] ? '[+] 是' : '[-] 否（中间人攻击风险）'}"
      samesite_str = cookie[:samesite] ? cookie[:samesite] : '未设置'
      puts "    SameSite: #{cookie[:samesite] ? '[+] ' + samesite_str : '[-] ' + samesite_str + '（CSRF 风险）'}"
    end

    # Cookie 安全评分（额外加分项，最多加 5 分）
    if cookie_result[:total] > 0
      cookie_score = 0
      cookie_score += 2 if cookie_result[:httponly] == cookie_result[:total]
      cookie_score += 2 if cookie_result[:secure] == cookie_result[:total]
      cookie_score += 1 if cookie_result[:samesite] == cookie_result[:total]
      total_score += cookie_score
      max_score += 5
    end
  end

  # ============================================================
  # 安全评分汇总
  # ============================================================
  puts "\n" + '=' * 60
  puts '[*] 安全评分汇总'
  puts '=' * 60

  score_percent = max_score > 0 ? (total_score.to_f / max_score * 100).round(1) : 0

  puts "\n  总分: #{total_score} / #{max_score} 分"
  puts "  得分率: #{score_percent}%"
  puts "  通过的安全头: #{passed_count} / #{SECURITY_HEADERS.length}"

  # 安全等级评定
  level = case score_percent
          when 90..100
            { grade: 'A', desc: '优秀', color: '绿色', advice: '安全配置良好，继续保持' }
          when 75...90
            { grade: 'B', desc: '良好', color: '蓝色', advice: '整体不错，建议补充缺失的安全头' }
          when 60...75
            { grade: 'C', desc: '一般', color: '黄色', advice: '存在较多安全隐患，建议尽快修复' }
          when 40...60
            { grade: 'D', desc: '较差', color: '橙色', advice: '安全配置严重不足，需要立即修复' }
          else
            { grade: 'F', desc: '危险', color: '红色', advice: '几乎没有安全配置，风险极高！' }
          end

  puts "\n  安全等级: #{level[:grade]} - #{level[:desc]}"
  puts "  评价: #{level[:advice]}"

  # ============================================================
  # 改进建议
  # ============================================================
  puts "\n" + '=' * 60
  puts '[*] 改进建议'
  puts '=' * 60

  missing_headers = SECURITY_HEADERS.select do |h|
    val = get_header_value(headers, h[:name])
    val.nil?
  end

  if missing_headers.any?
    puts "\n  缺少的安全头（建议优先添加）:"
    missing_headers.each_with_index do |h, i|
      puts "    #{i + 1}. #{h[:name]} - #{h[:description]}"
    end
  end

  if leaked_headers.any?
    puts "\n  建议移除/模糊化的信息泄露头:"
    leaked_headers.each_with_index do |h, i|
      puts "    #{i + 1}. #{h[:name]}: #{h[:value]}"
    end
  end

  puts "\n" + '=' * 60
  puts '[*] 检测完成'
  puts '=' * 60

  {
    score: total_score,
    max_score: max_score,
    score_percent: score_percent,
    passed_count: passed_count,
    total_headers: SECURITY_HEADERS.length,
    level: level[:grade]
  }
end

# ============================================================
# 主程序入口
# ============================================================
def main
  if ARGV.length < 1
    puts '用法: ruby http_header_check.rb <目标URL>'
    puts '示例: ruby http_header_check.rb https://www.example.com'
    puts '      ruby http_header_check.rb http://127.0.0.1'
    exit 1
  end

  url = ARGV[0]

  # 验证 URL 格式
  unless url =~ /^https?:\/\//i
    puts '[!] 错误：URL 必须以 http:// 或 https:// 开头'
    exit 1
  end

  # 执行检测
  begin
    check_security_headers(url)
  rescue Interrupt
    puts "\n[!] 用户中断检测"
    exit 0
  rescue => e
    puts "\n[!] 检测出错: #{e.message}"
    puts e.backtrace.first(5).join("\n") if $DEBUG
    exit 1
  end
end

# 运行主程序
main if __FILE__ == $0
