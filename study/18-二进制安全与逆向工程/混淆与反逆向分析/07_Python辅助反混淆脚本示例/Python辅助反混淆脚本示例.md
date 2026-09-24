# Python辅助反混淆脚本示例

### 7.1 简单控制流平坦化检测

```python
#!/usr/bin/env python3
# detect_cff.py - 检测二进制中的控制流平坦化
# 原理：CFF的特征是一个dispatcher基本块被大量其他块引用

import networkx as nx

# 假设已通过angr/IDA提取了控制流图（CFG）
# nodes: 基本块地址列表
# edges: [(src_addr, dst_addr), ...]

def detect_control_flow_flattening(cfg_graph):
    """
    检测控制流平坦化：
    1. 找入度异常高的节点（dispatcher）
    2. 检查是否存在switch-case模式的dispatcher
    """
    suspicious_nodes = []

    in_degree = dict(cfg_graph.in_degree())
    out_degree = dict(cfg_graph.out_degree())

    # 计算平均入度
    avg_in = sum(in_degree.values()) / len(in_degree) if in_degree else 0

    # dispatcher特征：入度远高于平均，且出度也高
    for node, deg in in_degree.items():
        if deg > avg_in * 3 and out_degree[node] > 5:
            suspicious_nodes.append({
                "address": node,
                "in_degree": deg,
                "out_degree": out_degree[node],
                "avg_in_degree": avg_in
            })

    # 检查dispatcher的后继是否形成switch-case模式
    for node_info in suspicious_nodes:
        successors = list(cfg_graph.successors(node_info["address"]))
        # 检查这些后继是否都有回到dispatcher的边
        back_edges = sum(1 for s in successors
                        if node_info["address"] in cfg_graph.successors(s))
        if back_edges > len(successors) * 0.5:
            node_info["confidence"] = "HIGH"
            node_info["back_edge_ratio"] = back_edges / len(successors)
        else:
            node_info["confidence"] = "MEDIUM"

    return suspicious_nodes

# 使用angr提取CFG
import angr
proj = angr.Project("./obfuscated", auto_load_libs=False)
cfg = proj.analyses.CFGFast()
cfg_graph = cfg.graph

# 检测
results = detect_control_flow_flattening(cfg_graph)
print(f"\n=== 控制流平坦化检测结果 ===")
print(f"总基本块数: {len(cfg_graph.nodes)}")
print(f"可疑dispatcher节点: {len(results)}")
for r in results:
    print(f"  地址: 0x{r['address']:x}")
    print(f"  入度: {r['in_degree']} (平均: {r['avg_in_degree']:.1f})")
    print(f"  出度: {r['out_degree']}")
    print(f"  置信度: {r['confidence']}")
```

### 7.2 字符串解密辅助脚本

```python
#!/usr/bin/env python3
# string_decrypt_helper.py - 通用字符串解密辅助工具
# 支持多种加密模式自动识别和解密

import struct

class StringDecryptor:
    """通用字符串解密器"""

    def __init__(self, data_provider):
        """
        data_provider: 回调函数，接受(address, length)返回bytes
        """
        self.read_memory = data_provider
        self.decrypt_methods = {
            "xor_single": self._xor_single_key,
            "xor_rolling": self._xor_rolling_key,
            "add_sub": self._add_sub,
            "base64": self._custom_base64,
        }

    def _xor_single_key(self, data, key=0x37):
        """单字节XOR"""
        return bytes([b ^ key for b in data])

    def _xor_rolling_key(self, data, key_bytes=b"ABCD"):
        """多字节滚动XOR"""
        return bytes([b ^ key_bytes[i % len(key_bytes)]
                     for i, b in enumerate(data)])

    def _add_sub(self, data, delta=0x10):
        """加减法"""
        return bytes([(b - delta) & 0xFF for b in data])

    def _custom_base64(self, data, charset=None):
        """自定义Base64变体"""
        import base64
        if charset:
            # 自定义字符表替换
            std = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
            trans = bytes.maketrans(charset, std)
            data = data.translate(trans)
        try:
            return base64.b64decode(data)
        except:
            return None

    def auto_detect(self, data):
        """自动检测加密方式并解密"""
        results = []

        # 尝试单字节XOR（所有256种密钥）
        for key in range(256):
            decrypted = self._xor_single_key(data, key)
            if self._is_printable(decrypted):
                results.append(("xor_single", key, decrypted))

        # 尝试加减法
        for delta in range(-128, 128):
            decrypted = self._add_sub(data, delta)
            if self._is_printable(decrypted):
                results.append(("add_sub", delta, decrypted))

        return results

    def _is_printable(self, data, threshold=0.8):
        """判断是否为可打印字符串"""
        if not data or len(data) < 2:
            return False
        printable = sum(1 for b in data if 0x20 <= b <= 0x7E or b == 0)
        return printable / len(data) >= threshold

    def decrypt_range(self, start_addr, end_addr, step=1):
        """批量解密地址范围内的数据"""
        all_results = []
        addr = start_addr
        while addr < end_addr:
            # 尝试不同长度的数据块
            for length in [8, 16, 32, 64]:
                data = self.read_memory(addr, length)
                if not data:
                    continue
                results = self.auto_detect(data)
                for method, key, decrypted in results:
                    if len(decrypted) >= 4:  # 过滤太短的
                        all_results.append({
                            "address": addr,
                            "method": method,
                            "key": key,
                            "encrypted": data.hex(),
                            "decrypted": decrypted
                        })
            addr += step
        return all_results

# 使用示例（配合IDA Python）
# def ida_read(addr, length):
#     import idaapi
#     return idaapi.get_bytes(addr, length)
#
# decryptor = StringDecryptor(ida_read)
# results = decryptor.decrypt_range(0x402000, 0x403000)
# for r in results:
#     print(f"0x{r['address']:x} [{r['method']} key={r['key']}] "
#           f"-> {r['decrypted']}")

# 独立使用（从二进制文件读取）
if __name__ == "__main__":
    with open("target.bin", "rb") as f:
        binary_data = f.read()

    def file_read(addr, length):
        if addr + length <= len(binary_data):
            return binary_data[addr:addr+length]
        return None

    decryptor = StringDecryptor(file_read)
    results = decryptor.decrypt_range(0x2000, 0x3000)

    print(f"找到 {len(results)} 个可能的加密字符串:")
    for r in results[:20]:  # 只显示前20个
        try:
            text = r["decrypted"].decode('ascii', errors='replace')
        except:
            text = str(r["decrypted"])
        print(f"  0x{r['address']:04x} [{r['method']} k={r['key']}] -> {text}")
```

---

---

