# AES题型

### 3.1 ECB模式重放

```python
from Crypto.Cipher import AES

# ECB模式特点:
# 1. 每个块独立加密
# 2. 相同明文块产生相同密文块
# 3. 可以重放/替换密文块

# 利用ECB模式替换密文块
def ecb_block_substitution(ciphertext, old_block, new_block, block_size=16):
    """替换ECB模式中的密文块"""
    blocks = [ciphertext[i:i+block_size] for i in range(0, len(ciphertext), block_size)]
    
    for i, block in enumerate(blocks):
        if block == old_block:
            blocks[i] = new_block
    
    return b''.join(blocks)

# ECB模式信息泄露
# 可以通过密文块的模式推断明文结构
# 例如: 相同密文块表示相同明文块
```

### 3.2 CBC字节翻转攻击

```python
def cbc_bit_flip_attack(ciphertext, target_block_idx, target_pos, 
                        original_byte, desired_byte, block_size=16):
    """CBC字节翻转攻击
    条件: 修改前一个密文块可以改变当前块的解密结果
    
    CBC解密: P[i] = D(C[i]) XOR C[i-1]
    如果修改C[i-1]的第j字节，则P[i]的第j字节也会改变
    """
    blocks = [bytearray(ciphertext[i:i+block_size]) 
              for i in range(0, len(ciphertext), block_size)]
    
    # 修改前一个块的对应位置
    prev_block_idx = target_block_idx - 1
    pos = target_pos
    
    # 翻转公式: new_prev[pos] = old_prev[pos] XOR original XOR desired
    blocks[prev_block_idx][pos] ^= original_byte ^ desired_byte
    
    return b''.join(bytes(b) for b in blocks)

# 使用示例
# 目标: 将第2块的解密结果中的第6字节从'A'改为';'
# original_byte = ord('A') = 0x41
# desired_byte = ord(';') = 0x3b
# 需要修改第1块的第6字节

# 实战场景: 修改Cookie中的admin=false为admin=true
def cbc_cookie_attack(ciphertext):
    """修改加密的Cookie"""
    # 假设Cookie格式: "id=1&admin=false&time=123"
    # 在第2个块中, "admin=false" 中的 'f' 改为 't'
    
    block_size = 16
    blocks = [bytearray(ciphertext[i:i+block_size]) 
              for i in range(0, len(ciphertext), block_size)]
    
    # 找到 "false" 中 'f' 在哪个块的哪个位置
    # 假设在第2块(offset=16)的第11个字节处
    # prev_block = blocks[1], target_pos = 10
    # original = ord('f'), desired = ord('t')
    
    blocks[1][10] ^= ord('f') ^ ord('t')
    
    return b''.join(bytes(b) for b in blocks)
```

### 3.3 Padding Oracle攻击

```python
import requests

def padding_oracle_attack(ciphertext, iv, oracle_url, block_size=16):
    """Padding Oracle攻击
    条件: 服务端返回Padding是否正确（通过错误信息或响应差异）
    
    原理: CBC解密时 P[i] = D(C[i]) XOR C[i-1]
    通过修改C[i-1]并观察Padding是否正确
    可以逐字节恢复中间值 D(C[i])
    然后与原始C[i-1]异或得到明文
    """
    def check_padding(c, iv):
        """检查Padding是否有效"""
        data = iv + c
        r = requests.get(oracle_url, params={"data": data.hex()})
        return "padding valid" in r.text  # 根据实际响应判断
    
    blocks = [ciphertext[i:i+block_size] 
              for i in range(0, len(ciphertext), block_size)]
    
    plaintext = b''
    
    for block_idx in range(len(blocks)):
        # 中间值
        intermediate = bytearray(block_size)
        # 当前块
        target_block = blocks[block_idx]
        # 前一个块（第0块用IV）
        prev_block = bytearray(iv) if block_idx == 0 else bytearray(blocks[block_idx - 1])
        
        # 从最后一个字节开始
        for pos in range(block_size - 1, -1, -1):
            # 当前Padding值
            pad_val = block_size - pos
            
            # 设置已知中间值
            test_prev = bytearray(block_size)
            for i in range(pos + 1, block_size):
                test_prev[i] = intermediate[i] ^ pad_val
            
            # 暴力当前字节
            found = False
            for guess in range(256):
                test_prev[pos] = guess
                
                if check_padding(bytes(target_block), bytes(test_prev)):
                    # 需要验证（可能是Padding巧合）
                    if pos > 0:
                        # 修改前一个字节验证
                        test_prev2 = bytearray(test_prev)
                        test_prev2[pos - 1] ^= 1
                        if not check_padding(bytes(target_block), bytes(test_prev2)):
                            continue
                    
                    # 中间值 = guess XOR pad_val
                    intermediate[pos] = guess ^ pad_val
                    # 明文字节 = 中间值 XOR 原始前块
                    plaintext_byte = intermediate[pos] ^ prev_block[pos]
                    print(f"[+] 块{block_idx} 位置{pos}: {chr(plaintext_byte)}")
                    found = True
                    break
            
            if not found:
                print(f"[-] 块{block_idx} 位置{pos} 破解失败")
                return None
        
        # 组装明文
        for i in range(block_size):
            plaintext += bytes([intermediate[i] ^ prev_block[i]])
    
    return plaintext

# 使用示例
ciphertext = bytes.fromhex("...")
iv = bytes.fromhex("...")
plaintext = padding_oracle_attack(ciphertext, iv, "http://example.com/decrypt")
print(plaintext)
```

---

---

