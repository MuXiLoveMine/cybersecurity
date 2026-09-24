# Hajime隐蔽僵尸网络

### 4.1 概述

Hajime（日语意为"开始"）于2016年10月被发现，与Mirai同期活跃但采取了完全不同的策略：

| 对比项 | Mirai | Hajime |
|--------|-------|--------|
| 架构 | 中心化C2 | 去中心化P2P |
| 持久性 | 重启即清除 | 使用init.d持久化 |
| 通信 | 明文TCP | 加密通信 |
| 功能 | DDoS攻击 | 仅扫描传播 |
| 可见性 | 明显 | 高度隐蔽 |
| 目的 | 商业DDoS | 安全加固? |

### 4.2 Hajime技术特征

```c
// Hajime的隐蔽通信机制
void hajime_communicate() {
    // 1. 使用NAT穿透建立P2P连接
    int sock = create_dht_socket();
    
    // 2. 通过DHT网络发现其他节点
    struct node *peers = dht_bootstrap(BOOTSTRAP_NODES);
    
    // 3. 加密通信
    // 使用ECC (secp256k1)进行密钥交换
    // 使用AES-256-CBC进行数据加密
    
    // 4. 接收指令
    // Hajime没有实施过DDoS攻击
    // 其主要活动是扫描和感染新设备
    // 同时会关闭Telnet服务、阻止23端口
    
    // 5. 持久化
    // 修改/etc/init.d/实现开机自启
    write_init_script();
    
    // 6. 反追踪
    // 删除自身二进制文件
    // 仅在内存中运行
    unlink("/tmp/.hajime");
}
```

### 4.3 Hajime的争议性

Hajime的行为引发了安全社区的争议：

- **白帽子论**：有人认为Hajime是"善意"僵尸网络，它感染设备后会关闭Telnet端口，阻止其他恶意软件感染
- **灰帽子论**：未经授权感染他人设备本身就是非法的，且其真实意图不明确
- **潜伏论**：Hajime可能在积累足够的设备数量后发动大规模攻击

---

---

