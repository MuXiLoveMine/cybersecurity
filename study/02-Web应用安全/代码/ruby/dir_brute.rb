#!/usr/bin/env ruby
# ============================================================
# Web 目录爆破工具 (Directory Brute Force)
# ============================================================
#
# 【原理说明】
# 目录爆破是 Web 安全测试中用于发现隐藏目录和文件的常用技术。
# 本工具通过字典枚举的方式，向目标 Web 服务器发送大量 HTTP 请求，
# 根据响应状态码判断目录/文件是否存在。
#
# 【常见状态码含义】
#   200 OK          - 页面/文件存在且可正常访问
#   301/302 重定向   - 页面存在但发生了跳转
#   403 Forbidden    - 页面存在但禁止访问
#   404 Not Found    - 页面不存在
#   500 Internal Error - 服务器内部错误
#
# 【使用方法】
#   ruby dir_brute.rb <目标URL> [字典文件] [线程数] [超时时间]
#
# 【参数说明】
#   目标URL   - 必填，目标网站 URL，例如 http://example.com
#   字典文件  - 可选，字典文件路径，每行一个路径
#               不指定则使用内置字典
#   线程数    - 可选，并发线程数，默认 20
#   超时时间  - 可选，请求超时时间（秒），默认 10
#
# 【示例】
#   ruby dir_brute.rb http://127.0.0.1
#   ruby dir_brute.rb http://example.com wordlist.txt 30
#   ruby dir_brute.rb https://target.com /path/to/dict.txt 50 15
#
# 【内置字典说明】
#   内置了常见的后台、备份、配置、敏感文件路径约 100 个，
#   适用于快速检测。实际使用建议加载更大的字典文件。
#
# 【免责声明】
#   本工具仅供学习和授权测试使用，未经授权对他人网站进行
#   目录爆破属于违法行为。使用本工具请遵守当地法律法规。
# ============================================================

require 'net/http'   # Ruby 标准库 HTTP 客户端
require 'uri'        # URI 解析
require 'thread'     # 多线程
require 'timeout'    # 超时处理

# ============================================================
# 内置字典：常见 Web 目录和敏感文件路径
# 涵盖后台管理、备份文件、配置文件、测试页面等
# ============================================================
DEFAULT_WORDLIST = %w[
  # 后台管理入口
  admin admin/ administrator admin.php admin.html admin/login
  login login.php login.html admin/index.php admin/login.php
  manage manager backend system user users member members
  dashboard console controlpanel cpanel wp-admin wp-login.php
  phpmyadmin pma myadmin admin_area admin_area.php

  # 备份和配置文件
  backup backup.zip backup.tar backup.tar.gz backup.sql
  .git .git/config .git/HEAD .svn .hg
  config config.php config.inc.php configuration.php
  database.sql db.sql dump.sql backup.sql
  web.config .htaccess .htpasswd robots.txt
  phpinfo.php info.php test.php

  # 编辑器和 IDE 残留
  .vscode .idea .DS_Store
  index.php~ index.php.bak index.php.swp
  .env .env.local

  # 常见目录
  upload uploads upload/files images img css js
  data cache temp tmp logs log
  api api/v1 api/v2 rest restful
  docs documentation doc files download
  forum blog news article
  search about contact faq
  install install.php setup setup.php
  upgrade update.php install/index.php

  # 常见文件
  index.html index.php index.asp index.jsp
  default.html default.php default.asp
  home.html home.php main.php
  readme README README.md CHANGELOG
  crossdomain.xml clientaccesspolicy.xml
  sitemap.xml sitemap.html
].freeze

# ============================================================
# 发送 HTTP 请求并获取响应信息
# ============================================================
# @param url [String] 目标 URL
# @param timeout [Integer] 超时时间（秒）
# @return [Hash] 响应结果，包含状态码、重定向地址、响应长度等
def http_request(url, timeout = 10)
  uri = URI(url)
  result = {
    status_code: 0,
    redirect_url: nil,
    content_length: 0,
    error: nil
  }

  begin
    # 创建 HTTP 连接对象
    http = Net::HTTP.new(uri.host, uri.port)
    http.open_timeout = timeout  # 连接超时
    http.read_timeout = timeout  # 读取超时

    # 如果是 HTTPS，启用 SSL
    if uri.scheme == 'https'
      http.use_ssl = true
      http.verify_mode = OpenSSL::SSL::VERIFY_NONE  # 跳过证书验证（测试用）
    end

    # 构造 GET 请求
    request = Net::HTTP::Get.new(uri.request_uri)
    # 设置常见的请求头，模拟浏览器访问
    request['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    request['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    request['Accept-Language'] = 'zh-CN,zh;q=0.9,en;q=0.8'
    request['Connection'] = 'close'

    # 发送请求（不跟随重定向）
    response = http.request(request)

    result[:status_code] = response.code.to_i
    result[:content_length] = response.body ? response.body.length : 0

    # 如果是重定向，获取重定向地址
    if response.code =~ /^3[0-9][0-9]$/
      result[:redirect_url] = response['location']
    end

  rescue Timeout::Error
    result[:error] = 'timeout'
  rescue Errno::ECONNREFUSED
    result[:error] = 'connection_refused'
  rescue Errno::EHOSTUNREACH
    result[:error] = 'host_unreachable'
  rescue Errno::ECONNRESET
    result[:error] = 'connection_reset'
  rescue OpenURI::HTTPError
    result[:error] = 'http_error'
  rescue => e
    result[:error] = e.message
  end

  result
end

# ============================================================
# 判断结果是否为"有效"（即值得关注的）路径
# ============================================================
# 排除 404 和一些明显的无效状态
# @param status_code [Integer] HTTP 状态码
# @return [Boolean] 是否为有效结果
def is_valid_result?(status_code)
  # 2xx 成功、3xx 重定向、403 禁止访问 都算有效结果
  case status_code
  when 200..299, 300..399, 401, 403
    true
  else
    false
  end
end

# ============================================================
# 加载字典文件
# ============================================================
# @param file_path [String] 字典文件路径
# @return [Array] 路径列表
def load_wordlist(file_path)
  paths = []
  begin
    File.foreach(file_path) do |line|
      path = line.strip
      # 跳过空行和注释行
      next if path.empty? || path.start_with?('#')
      # 去掉开头的斜杠，统一处理
      path = path.sub(/^\//, '')
      paths << path unless path.empty?
    end
    puts "[*] 已从字典文件加载 #{paths.length} 个路径"
  rescue => e
    puts "[!] 加载字典文件失败: #{e.message}"
    puts "[*] 将使用内置字典"
    paths = DEFAULT_WORDLIST.dup
  end
  paths
end

# ============================================================
# 目录爆破主函数
# ============================================================
# @param base_url [String] 目标 URL
# @param wordlist [Array] 字典路径列表
# @param thread_count [Integer] 线程数
# @param timeout [Integer] 超时时间
def dir_brute(base_url, wordlist, thread_count = 20, timeout = 10)
  total_paths = wordlist.length
  found_paths = []       # 存储发现的有效路径
  path_queue = wordlist.dup  # 路径队列
  scanned_count = 0      # 已扫描数量
  mutex = Mutex.new      # 互斥锁

  # 确保基础 URL 以 / 结尾，方便拼接
  base_url = base_url.chomp('/') + '/'

  puts "\n[*] 开始目录爆破"
  puts "[*] 目标 URL: #{base_url}"
  puts "[*] 字典数量: #{total_paths}"
  puts "[*] 线程数: #{thread_count}"
  puts "[*] 超时时间: #{timeout}秒"
  puts '=' * 60

  start_time = Time.now

  # ============================================================
  # 多线程并发扫描
  # 使用线程池模式，每个线程从队列中取路径进行扫描
  # ============================================================
  threads = []

  thread_count.times do
    threads << Thread.new do
      loop do
        # 从队列中取出下一个路径
        path = nil
        mutex.synchronize do
          path = path_queue.shift
        end

        break if path.nil?

        # 构造完整 URL 并发送请求
        target_url = base_url + path
        result = http_request(target_url, timeout)

        # 处理结果
        mutex.synchronize do
          scanned_count += 1

          # 如果是有效结果，记录并打印
          if result[:status_code] != 0 && is_valid_result?(result[:status_code])
            entry = {
              path: path,
              status_code: result[:status_code],
              content_length: result[:content_length],
              redirect_url: result[:redirect_url]
            }
            found_paths << entry

            # 根据状态码显示不同颜色提示
            status_str = result[:status_code].to_s
            case result[:status_code]
            when 200..299
              puts "[+] [#{status_str}] /#{path} (#{result[:content_length]} bytes)"
            when 300..399
              redirect = result[:redirect_url] ? " -> #{result[:redirect_url]}" : ''
              puts "[*] [#{status_str}] /#{path}#{redirect}"
            when 401, 403
              puts "[!] [#{status_str}] /#{path} (需要认证/禁止访问)"
            end
          end

          # 打印进度
          if scanned_count % 50 == 0 || scanned_count == total_paths
            progress = (scanned_count.to_f / total_paths * 100).round(1)
            print "\r[*] 扫描进度: #{scanned_count}/#{total_paths} (#{progress}%)  发现: #{found_paths.length}"
            $stdout.flush
          end
        end
      end
    end
  end

  # 等待所有线程完成
  threads.each(&:join)

  end_time = Time.now
  duration = (end_time - start_time).round(2)

  # ============================================================
  # 输出扫描结果汇总
  # ============================================================
  puts "\n" + '=' * 60
  puts "[*] 扫描完成！耗时: #{duration} 秒"
  puts "[*] 扫描路径总数: #{total_paths}"
  puts "[+] 发现有效路径: #{found_paths.length} 个"

  if found_paths.length > 0
    puts "\n[*] 发现的路径列表:"
    puts '-' * 50

    # 按状态码分组
    by_status = found_paths.group_by { |p| p[:status_code] }
    by_status.keys.sort.each do |status|
      puts "\n  状态码 #{status}:"
      by_status[status].each do |entry|
        extra = entry[:redirect_url] ? " -> #{entry[:redirect_url]}" : ""
        puts "    /#{entry[:path]}  (#{entry[:content_length]} bytes)#{extra}"
      end
    end
  end

  found_paths
end

# ============================================================
# 主程序入口
# ============================================================
def main
  if ARGV.length < 1
    puts '用法: ruby dir_brute.rb <目标URL> [字典文件] [线程数] [超时时间]'
    puts '示例: ruby dir_brute.rb http://127.0.0.1'
    puts '      ruby dir_brute.rb http://example.com wordlist.txt 30'
    exit 1
  end

  base_url = ARGV[0]
  wordlist_file = ARGV[1]
  thread_count = (ARGV[2] || 20).to_i
  timeout = (ARGV[3] || 10).to_i

  # 验证 URL 格式
  unless base_url =~ /^https?:\/\//i
    puts '[!] 错误：URL 必须以 http:// 或 https:// 开头'
    exit 1
  end

  # 参数检查
  if thread_count < 1 || thread_count > 200
    puts '[!] 错误：线程数应在 1-200 之间'
    exit 1
  end

  # 加载字典
  wordlist = if wordlist_file && File.exist?(wordlist_file)
               load_wordlist(wordlist_file)
             else
               puts '[*] 使用内置字典'
               DEFAULT_WORDLIST.dup
             end

  if wordlist.empty?
    puts '[!] 错误：字典为空'
    exit 1
  end

  # 执行目录爆破
  begin
    dir_brute(base_url, wordlist, thread_count, timeout)
  rescue Interrupt
    puts "\n[!] 用户中断扫描"
    exit 0
  rescue => e
    puts "\n[!] 扫描出错: #{e.message}"
    puts e.backtrace.first(5).join("\n") if $DEBUG
    exit 1
  end
end

# 运行主程序
main if __FILE__ == $0
