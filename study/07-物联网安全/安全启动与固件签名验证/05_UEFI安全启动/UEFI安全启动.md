# UEFI安全启动

### 5.1 UEFI安全启动概述

```
UEFI Secure Boot工作流程:

1. 平台初始化
   ┌─────────────────────────────────┐
   │  平台初始化 (SEC + PEI)         │
   │  • 初始化基本硬件                │
   │  • 加载UEFI固件                  │
   └──────────────┬──────────────────┘
                  │
2. 密钥数据库加载
   ┌──────────────┴──────────────────┐
   │  从Flash加载密钥数据库            │
   │  • PK (Platform Key)            │
   │  • KEK (Key Exchange Key)       │
   │  • db (Authorized Signature)    │
   │  • dbx (Forbidden Signature)    │
   └──────────────┬──────────────────┘
                  │
3. 启动选项验证
   ┌──────────────┴──────────────────┐
   │  对每个启动选项:                 │
   │  1. 读取EFI镜像                  │
   │  2. 提取签名证书                 │
   │  3. 在db中查找匹配签名            │
   │  4. 检查dbx中是否禁止            │
   │  5. 验证通过 → 启动              │
   │  6. 验证失败 → 拒绝/回退         │
   └─────────────────────────────────┘

密钥层次:
┌─────────────────────────────────┐
│           PK (平台密钥)           │
│  最高权限，可修改KEK               │
└──────────────┬──────────────────┘
               │
┌──────────────┴──────────────────┐
│         KEK (交换密钥)            │
│  可修改db和dbx                    │
└──────────────┬──────────────────┘
               │
┌──────────────┴──────────────────┐
│    db (授权签名数据库)             │
│  包含被授权的公钥/证书              │
├─────────────────────────────────┤
│    dbx (撤销签名数据库)            │
│  包含被撤销的公钥/证书              │
└─────────────────────────────────┘
```

### 5.2 UEFI镜像验证

```python
# UEFI镜像签名验证
class UEFISecureBoot:
    """UEFI安全启动验证"""
    
    def __init__(self, db: list, dbx: list):
        """
        db: 授权签名证书列表
        dbx: 撤销签名证书列表
        """
        self.db = db  # 授权数据库
        self.dbx = dbx  # 撤销数据库
    
    def verify_efi_image(self, image_path: str) -> bool:
        """验证EFI镜像签名"""
        # 1. 解析PE/COFF格式
        pe_data = self._read_pe_image(image_path)
        
        # 2. 检查是否存在签名
        signature = self._extract_signature(pe_data)
        if not signature:
            print("镜像未签名，拒绝启动")
            return False
        
        # 3. 提取签名证书
        cert = self._extract_certificate(signature)
        
        # 4. 检查证书是否在撤销列表中
        if self._is_in_dbx(cert):
            print(f"证书在撤销列表中，拒绝启动")
            return False
        
        # 5. 检查证书是否在授权列表中
        if not self._is_in_db(cert):
            print(f"证书不在授权列表中，拒绝启动")
            return False
        
        # 6. 验证签名
        image_hash = self._calculate_image_hash(pe_data)
        if not self._verify_signature(image_hash, signature, cert):
            print("签名验证失败")
            return False
        
        print("UEFI镜像验证通过")
        return True
    
    def _read_pe_image(self, path: str) -> bytes:
        """读取PE格式镜像"""
        with open(path, 'rb') as f:
            return f.read()
    
    def _extract_signature(self, pe_data: bytes) -> dict:
        """从PE镜像提取签名"""
        # PE签名的证书目录在可选头中
        # 简化实现
        signature = {
            'algorithm': 'RSA-SHA256',
            'data': b'',  # 实际签名数据
            'cert': b'',  # 签名证书
        }
        # ... 实际PE解析逻辑
        return signature
    
    def _is_in_dbx(self, cert: bytes) -> bool:
        """检查证书是否在撤销列表"""
        cert_hash = hashlib.sha256(cert).hexdigest()
        for entry in self.dbx:
            if cert_hash == entry['hash']:
                return True
        return False
    
    def _is_in_db(self, cert: bytes) -> bool:
        """检查证书是否在授权列表"""
        cert_hash = hashlib.sha256(cert).hexdigest()
        for entry in self.db:
            if cert_hash == entry['hash']:
                return True
        return False
```

---

---

