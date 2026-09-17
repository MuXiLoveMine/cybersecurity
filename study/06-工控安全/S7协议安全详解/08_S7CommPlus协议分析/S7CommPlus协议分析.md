# S7CommPlus协议分析

### 7.1 S7CommPlus概述

S7CommPlus是西门子为S7-1200/1500 PLC设计的新一代通信协议，解决了S7Comm的安全缺陷。

```
S7Comm与S7CommPlus对比:

┌────────────────────┬──────────────┬────────────────┐
│ 特性               │ S7Comm       │ S7CommPlus     │
├────────────────────┼──────────────┼────────────────┤
│ 认证               │ 无/弱密码    │ 强认证+证书    │
│ 加密               │ 无           │ AES-128/256    │
│ 完整性             │ 无           │ HMAC-SHA256   │
│ 防重放             │ 无           │ 序列号+时间戳  │
│ 密钥协商           │ 无           │ ECDH           │
│ 会话绑定           │ 无           │ 会话ID         │
│ 支持设备           │ S7-300/400   │ S7-1200/1500   │
│ 端口               │ 102          │ 102            │
└────────────────────┴──────────────┴────────────────┘
```

### 7.2 S7CommPlus帧结构

```
S7CommPlus帧结构:

┌──────────────────────────────────────────────────────────────┐
│ TPKT (4 bytes) - 同S7Comm                                     │
├──────────────────────────────────────────────────────────────┤
│ COTP (3+ bytes) - 同S7Comm                                    │
├──────────────────────────────────────────────────────────────┤
│ S7Plus协议层                                                  │
│  ┌──────────┬──────────┬──────────┬─────────────────────┐    │
│  │Protocol  │ PDU Type │ Protocol │ Session             │    │
│  │Version   │          │ ID       │ Info                │    │
│  │(1byte)   │(1byte)   │(2bytes) │ (变长)               │    │
│  │ =0x72    │          │          │                      │    │
│  └──────────┴──────────┴──────────┴─────────────────────┘    │
├──────────────────────────────────────────────────────────────┤
│ TLV (Type-Length-Value) 编码的参数和数据                      │
│  ┌──────────┬──────────┬──────────────────────────────┐      │
│  │ Type     │ Length   │ Value                        │      │
│  │ (变长)   │ (变长)   │ (变长)                       │      │
│  └──────────┴──────────┴──────────────────────────────┘      │
└──────────────────────────────────────────────────────────────┘

Protocol Version: 0x72 (S7CommPlus V1)
PDU Types:
  0x01 - Request
  0x02 - Notification
  0x03 - Response
  0x05 - Request (advanced)
  0x06 - Notification (advanced)
  0x07 - Response (advanced)
```

### 7.3 S7CommPlus安全机制

```
S7CommPlus安全机制:

1. 密钥协商 (Key Exchange):
   ┌────────────────────────────────────────────────────┐
   │ 客户端                    │ PLC                    │
   │                          │                        │
   │ 1. 生成临时ECDH密钥对    │                        │
   │    private_key_c,        │                        │
   │    public_key_c           │                        │
   │                          │                        │
   │ 2. 发送public_key_c      │                        │
   │ ─────────────────────────>│                        │
   │                          │ 3. 生成临时ECDH密钥对   │
   │                          │    private_key_s,      │
   │                          │    public_key_s        │
   │                          │                        │
   │ 4. 返回public_key_s      │                        │
   │ <─────────────────────────│                        │
   │                          │                        │
   │ 5. 计算共享密钥          │ 5. 计算共享密钥         │
   │    shared_secret =       │    shared_secret =     │
   │    ECDH(priv_c, pub_s)   │    ECDH(priv_s, pub_c) │
   │                          │                        │
   │ 6. 派生会话密钥          │ 6. 派生会话密钥         │
   │    enc_key, mac_key,     │    enc_key, mac_key,   │
   │    iv                    │    iv                   │
   └────────────────────────────────────────────────────┘

2. 加密传输:
   - 算法: AES-128-CBC 或 AES-256-CBC
   - 密钥: 从共享密钥派生
   - IV: 从共享密钥派生
   - 填充: PKCS7

3. 完整性校验:
   - 算法: HMAC-SHA256
   - 密钥: 从共享密钥派生
   - 覆盖: 整个PDU (包括头部)

4. 防重放保护:
   - 序列号: 每个PDU递增
   - 时间戳: 带有过期检查
   - 窗口: 接受序列号在窗口内

5. 认证:
   - 方式1: 共享密码 (改进的挑战-响应)
   - 方式2: X.509证书 (S7-1500 V2.5+)
   - 方式3: 基于角色的访问控制
```

### 7.4 S7CommPlus TLV编码

```python
#!/usr/bin/env python3
"""S7CommPlus TLV编码/解码工具"""

class TLV:
    """S7CommPlus TLV (Type-Length-Value) 编码"""
    
    # 类型定义
    TYPE_NULL = 0x00
    TYPE_BOOL = 0x01
    TYPE_UINT8 = 0x02
    TYPE_UINT16 = 0x03
    TYPE_UINT32 = 0x04
    TYPE_UINT64 = 0x05
    TYPE_INT8 = 0x06
    TYPE_INT16 = 0x07
    TYPE_INT32 = 0x08
    TYPE_INT64 = 0x09
    TYPE_FLOAT32 = 0x0A
    TYPE_FLOAT64 = 0x0B
    TYPE_STRING = 0x0C
    TYPE_BYTES = 0x0D
    TYPE_ARRAY = 0x0E
    TYPE_STRUCT = 0x0F
    
    @staticmethod
    def encode_length(length):
        """编码长度字段"""
        if length < 0x80:
            return bytes([length])
        elif length < 0x4000:
            return bytes([(length >> 8) | 0x80, length & 0xFF])
        elif length < 0x200000:
            return bytes([
                (length >> 16) | 0xC0,
                (length >> 8) & 0xFF,
                length & 0xFF
            ])
        else:
            return bytes([
                (length >> 24) | 0xE0,
                (length >> 16) & 0xFF,
                (length >> 8) & 0xFF,
                length & 0xFF
            ])
    
    @staticmethod
    def decode_length(data, offset=0):
        """解码长度字段"""
        if offset >= len(data):
            return 0, 0
        
        first_byte = data[offset]
        
        if first_byte < 0x80:
            return first_byte, 1
        elif first_byte < 0xC0:
            length = ((first_byte & 0x3F) << 8) | data[offset + 1]
            return length, 2
        elif first_byte < 0xE0:
            length = ((first_byte & 0x1F) << 16) | \
                     (data[offset + 1] << 8) | data[offset + 2]
            return length, 3
        else:
            length = ((first_byte & 0x0F) << 24) | \
                     (data[offset + 1] << 16) | \
                     (data[offset + 2] << 8) | data[offset + 3]
            return length, 4
    
    @staticmethod
    def encode(type_id, value):
        """编码TLV"""
        if type_id == TLV.TYPE_UINT8:
            data = bytes([value & 0xFF])
        elif type_id == TLV.TYPE_UINT16:
            import struct
            data = struct.pack('>H', value)
        elif type_id == TLV.TYPE_UINT32:
            import struct
            data = struct.pack('>I', value)
        elif type_id == TLV.TYPE_STRING:
            data = value.encode('utf-8')
        elif type_id == TLV.TYPE_BYTES:
            data = value
        else:
            data = value
        
        encoded = bytes([type_id])
        encoded += TLV.encode_length(len(data))
        encoded += data
        
        return encoded
    
    @staticmethod
    def decode(data, offset=0):
        """解码TLV"""
        if offset >= len(data):
            return None, 0, 0
        
        type_id = data[offset]
        length, len_size = TLV.decode_length(data, offset + 1)
        value_offset = offset + 1 + len_size
        value = data[value_offset:value_offset + length]
        
        return type_id, value, 1 + len_size + length

# 使用示例
if __name__ == '__main__':
    # 编码示例
    encoded = TLV.encode(TLV.TYPE_UINT16, 0x1234)
    print(f"编码 uint16(0x1234): {encoded.hex()}")
    
    encoded = TLV.encode(TLV.TYPE_STRING, "Hello S7CommPlus")
    print(f"编码 string: {encoded.hex()}")
    
    # 解码示例
    data = bytes.fromhex('031234' + '0C0F48656C6C6F205337436F6D6D506C7573')
    offset = 0
    while offset < len(data):
        type_id, value, consumed = TLV.decode(data, offset)
        if type_id is None:
            break
        print(f"类型: 0x{type_id:02X}, 值: {value.hex() if isinstance(value, bytes) else value}")
        offset += consumed
```

---

---

## 📋 内容审核与补充建议

> 针对「S7CommPlus协议分析」部分的内容审核结果：

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
