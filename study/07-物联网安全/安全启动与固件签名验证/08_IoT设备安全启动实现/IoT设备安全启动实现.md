# IoT设备安全启动实现

### 7.1 基于MCU的轻量级安全启动

```c
// 基于Cortex-M的轻量级安全启动

#include "sha256.h"
#include "ecc256.h"  // ECC P-256验证
#include "flash.h"
#include "efuse.h"

// 固件头格式
typedef struct {
    uint32_t magic;          // 魔数 0x46575331 ("FWS1")
    uint32_t version;       // 固件版本
    uint32_t size;          // 固件大小
    uint8_t  hash[32];      // 固件SHA-256哈希
    uint8_t  signature[64]; // ECDSA-P256签名
} __attribute__((packed)) firmware_header_t;

// 安全启动验证
int secure_boot_verify(void) {
    firmware_header_t header;
    uint8_t *firmware_data;
    uint8_t calc_hash[32];
    
    // 1. 读取固件头
    flash_read(FIRMWARE_BASE, &header, sizeof(header));
    
    // 2. 验证魔数
    if (header.magic != 0x46575331) {
        log_error("固件魔数无效");
        return BOOT_FAIL_MAGIC;
    }
    
    // 3. 读取固件数据
    firmware_data = (uint8_t *)malloc(header.size);
    flash_read(FIRMWARE_BASE + sizeof(header), firmware_data, header.size);
    
    // 4. 计算哈希
    sha256_context ctx;
    sha256_init(&ctx);
    sha256_update(&ctx, firmware_data, header.size);
    sha256_final(&ctx, calc_hash);
    
    // 5. 比较哈希
    if (memcmp(calc_hash, header.hash, 32) != 0) {
        log_error("固件哈希不匹配");
        free(firmware_data);
        return BOOT_FAIL_HASH;
    }
    
    // 6. 从eFuse读取公钥
    uint8_t pubkey[64];
    efuse_read_pulickey(pubkey);
    
    // 7. 验证签名
    if (ecdsa_verify(pubkey, calc_hash, header.signature) != 0) {
        log_error("固件签名无效");
        free(firmware_data);
        return BOOT_FAIL_SIGNATURE;
    }
    
    // 8. 检查防回滚
    uint32_t min_version = efuse_read(EFUSE_MIN_VERSION);
    if (header.version < min_version) {
        log_error("固件版本过低(回滚)");
        free(firmware_data);
        return BOOT_FAIL_ROLLBACK;
    }
    
    // 9. 验证通过
    log_info("固件验证通过");
    
    // 10. 跳转到固件
    void (*firmware_entry)(void) = 
        (void (*)(void))(FIRMWARE_BASE + sizeof(header));
    
    free(firmware_data);
    firmware_entry();
    
    return BOOT_SUCCESS;
}
```

### 7.2 基于Linux的IoT安全启动

```bash
#!/bin/bash
# IoT设备安全启动配置

# 1. U-Boot安全启动配置
cat > /boot/uboot.env << 'EOF'
# 安全启动使能
secure_boot=yes

# 启动验证
bootargs=console=ttyS0,115200 root=/dev/mmcblk0p2 ro rootwait
bootcmd=run verify_kernel; run boot_linux

# 内核验证
verify_kernel=if test "${secure_boot}" = "yes"; then \
    echo "验证内核签名..."; \
    imskey load ${kernel_key_addr}; \
    if iminfo ${kernel_addr}; then \
        echo "内核验证通过"; \
    else \
        echo "内核验证失败"; \
        reset; \
    fi; \
fi

# 启动Linux
boot_linux=bootz ${kernel_addr} - ${fdt_addr}
EOF

# 2. Linux内核配置
# CONFIG_SECURITY_DM_VERITY=y
# CONFIG_DM_VERITY_FEC=y
# CONFIG_MODULE_SIG=y
# CONFIG_MODULE_SIG_FORCE=y
# CONFIG_MODULE_SIG_SHA256=y
# CONFIG_IMA=y
# CONFIG_IMA_APPRAISE=y

# 3. dm-verity配置 (根文件系统完整性)
veritysetup format /dev/mmcblk0p2 /dev/mmcblk0p3 > /root/hashtree
# 生成哈希树，存储在独立分区

cat > /etc/dm-verity.conf << 'EOF'
# dm-verity配置
VERITY=/dev/mmcblk0p3
ROOT=/dev/mmcblk0p2
HASH=sha256
EOF

# 4. IMA策略配置
cat > /etc/ima/ima-policy << 'EOF'
# 签名验证策略
appraise func=FILE_CHECK mask=MAY_EXEC
appraise func=MODULE_CHECK
appraise func=FIRMWARE_CHECK
measure func=FILE_CHECK mask=MAY_READ
measure func=BPRM_CHECK
EOF

# 5. 内核模块签名密钥
# 编译内核时指定:
# CONFIG_MODULE_SIG_KEY="certs/signing_key.pem"
# 或使用自签名证书:
openssl req -new -x509 -newkey rsa:2048 \
    -keyout certs/module_signing.key \
    -out certs/module_signing.crt \
    -nodes -days 3650 \
    -subj "/CN=IoT Module Signing/"
```

---

---

## 📋 内容审核与补充建议

> 针对「IoT设备安全启动实现」部分的内容审核结果：

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
