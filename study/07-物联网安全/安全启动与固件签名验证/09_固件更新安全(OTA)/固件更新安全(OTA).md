# 固件更新安全(OTA)

### 9.1 安全OTA更新流程

```
安全OTA更新流程:

1. 更新准备
   ┌─────────────────────────────────────┐
   │  服务器: 准备新固件                  │
   │  • 编译固件                          │
   │  • 生成哈希和签名                    │
   │  • 打包固件(.signed)                 │
   │  • 上传到分发服务器                  │
   │  • 注册版本信息                      │
   └──────────────┬──────────────────────┘
                  │
2. 更新检查
   ┌──────────────┴──────────────────────┐
   │  设备: 检查更新                      │
   │  • 连接更新服务器                    │
   │  • 发送当前版本和设备信息             │
   │  • 接收更新信息(版本/大小/签名)       │
   └──────────────┬──────────────────────┘
                  │
3. 下载固件
   ┌──────────────┴──────────────────────┐
   │  设备: 下载固件                      │
   │  • 使用HTTPS下载                    │
   │  • 分块下载(支持断点续传)            │
   │  • 下载到备用分区                    │
   └──────────────┬──────────────────────┘
                  │
4. 验证固件
   ┌──────────────┴──────────────────────┐
   │  设备: 完整验证                      │
   │  • 验证签名                          │
   │  • 验证哈希                          │
   │  • 验证版本(防回滚)                  │
   │  • 验证设备兼容性                    │
   └──────────────┬──────────────────────┘
                  │
5. 安装固件
   ┌──────────────┴──────────────────────┐
   │  设备: 安装固件                      │
   │  • 写入备用分区                      │
   │  • 更新引导配置                      │
   │  • 设置下次启动为新固件              │
   │  • 保留回滚选项                      │
   └──────────────┬──────────────────────┘
                  │
6. 重启验证
   ┌──────────────┴──────────────────────┐
   │  设备: 重启并验证                     │
   │  • 安全启动验证新固件                 │
   │  • 成功: 提交新版本, 禁止回滚         │
   │  • 失败: 回退到旧固件                 │
   └─────────────────────────────────────┘
```

### 9.2 A/B分区更新方案

```
A/B分区更新架构:

┌─────────────────────────────────────────┐
│              Flash存储布局               │
├─────────────────────────────────────────┤
│  ┌─────────┐  Bootloader (只读)        │
│  ├─────────┤                            │
│  │ A分区   │  当前活动固件              │
│  ├─────────┤                            │
│  │ B分区   │  备用固件(更新目标)        │
│  ├─────────┤                            │
│  │ Data    │  用户数据(共享)            │
│  ├─────────┤                            │
│  │ 配置    │  启动配置                  │
│  └─────────┘                            │
└─────────────────────────────────────────┘

更新流程:
1. 当前运行A分区
2. 下载新固件到B分区
3. 验证B分区固件签名
4. 修改配置: 下次启动B分区
5. 重启
6. 安全启动验证B分区固件
7. 如果验证通过:
   - 启动B分区固件
   - 标记B为活动分区
   - 标记A为备用分区
8. 如果验证失败:
   - 回退到A分区
   - 记录失败原因
```

```python
# A/B分区管理器
class ABPartitionManager:
    """A/B分区管理器"""
    
    def __init__(self):
        self.partitions = {
            'A': {'active': True, 'boot_attempts': 0, 'version': ''},
            'B': {'active': False, 'boot_attempts': 0, 'version': ''},
        }
        self.max_boot_attempts = 3
    
    def get_active_partition(self) -> str:
        """获取当前活动分区"""
        for name, info in self.partitions.items():
            if info['active']:
                return name
        return 'A'
    
    def get_inactive_partition(self) -> str:
        """获取非活动分区"""
        active = self.get_active_partition()
        return 'B' if active == 'A' else 'A'
    
    def prepare_update(self, firmware_data: bytes) -> bool:
        """准备更新"""
        inactive = self.get_inactive_partition()
        
        # 写入固件到非活动分区
        self._write_partition(inactive, firmware_data)
        
        # 设置启动尝试计数
        self.partitions[inactive]['boot_attempts'] = 0
        
        # 标记下次启动该分区
        self._set_next_boot(inactive)
        
        return True
    
    def on_boot_success(self):
        """启动成功后调用"""
        active = self.get_active_partition()
        
        # 提交当前分区为活动
        self.partitions[active]['boot_attempts'] = 0
        inactive = self.get_inactive_partition()
        self.partitions[active]['active'] = True
        self.partitions[inactive]['active'] = False
        
        # 更新防回滚计数器
        self._update_rollback_counter(
            self.partitions[active]['version']
        )
        
        logger.info(f"分区 {active} 启动成功并提交")
    
    def on_boot_failure(self):
        """启动失败后调用"""
        # 此函数由Bootloader在多次失败后调用
        active = self.get_active_partition()
        inactive = self.get_inactive_partition()
        
        logger.error(f"分区 {active} 启动失败, 回退到 {inactive}")
        
        # 切换回旧分区
        self.partitions[active]['active'] = False
        self.partitions[inactive]['active'] = True
        self._set_next_boot(inactive)
```

---

---

## 📋 内容审核与补充建议

> 针对「固件更新安全(OTA)」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

### ⚔️ 攻击技术
- ⚠️ 缺少attack相关内容

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
