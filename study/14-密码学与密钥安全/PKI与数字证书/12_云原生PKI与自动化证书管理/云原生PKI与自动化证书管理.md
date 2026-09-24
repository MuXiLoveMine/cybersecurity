# 云原生PKI与自动化证书管理

### 12.1 cert-manager（Kubernetes证书管理）

**cert-manager** 是Kubernetes生态中最流行的证书管理工具。

```yaml
# cert-manager安装（Helm）
# helm repo add jetstack https://charts.jetstack.io
# helm install cert-manager jetstack/cert-manager

# 1. 配置Let's Encrypt签发者
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx

---
# 2. 申请证书
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: example-com-tls
  namespace: default
spec:
  secretName: example-com-tls
  duration: 2160h  # 90天
  renewBefore: 360h  # 提前15天续期
  dnsNames:
  - example.com
  - www.example.com
  - api.example.com
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer

---
# 3. 使用证书的Ingress
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: example-ingress
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - example.com
    - www.example.com
    secretName: example-com-tls
  rules:
  - host: example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: example-service
            port:
              number: 80
```

### 12.2 内部CA自动化

```python
"""
HashiCorp Vault作为内部CA
Vault可以充当PKI后端，提供自动化证书管理
"""

# Vault PKI配置（命令行）
"""
# 1. 启用PKI密钥引擎
vault secrets enable -path=pki pki

# 2. 配置CA
vault write pki/root/generate/internal \
    common_name="Internal Root CA" \
    ttl=87600h  # 10年

# 3. 配置URL
vault write pki/config/urls \
    issuing_certificates="https://vault.internal:8200/v1/pki/ca" \
    crl_distribution_points="https://vault.internal:8200/v1/pki/crl"

# 4. 创建角色（定义证书策略）
vault write pki/roles/example-dot-com \
    allowed_domains="example.com" \
    allow_subdomains=true \
    max_ttl="720h"  # 30天

# 5. 签发证书
vault write pki/issue/example-dot-com \
    common_name="www.example.com" \
    ttl="24h"
"""

# Python客户端
import hvac

class VaultCAClient:
    """Vault PKI客户端"""
    
    def __init__(self, url: str, token: str, pki_path: str = "pki"):
        self.client = hvac.Client(url=url, token=token)
        self.pki_path = pki_path
    
    def issue_certificate(
        self,
        common_name: str,
        role: str,
        ttl: str = "24h",
        alt_names: str = None,
        ip_sans: str = None
    ) -> dict:
        """
        通过Vault签发证书
        
        Args:
            common_name: 通用名称
            role: Vault PKI角色名
            ttl: 有效期
            alt_names: 备用域名
            ip_sans: IP SAN
            
        Returns:
            包含证书和私钥的字典
        """
        data = {
            "common_name": common_name,
            "ttl": ttl
        }
        
        if alt_names:
            data["alt_names"] = alt_names
        if ip_sans:
            data["ip_sans"] = ip_sans
        
        response = self.client.write(
            f"{self.pki_path}/issue/{role}",
            **data
        )
        
        return response['data']
    
    def revoke_certificate(self, serial_number: str) -> dict:
        """撤销证书"""
        response = self.client.write(
            f"{self.pki_path}/revoke",
            serial_number=serial_number
        )
        return response['data']
    
    def get_crl(self, format_type: str = "pem") -> str:
        """获取CRL"""
        response = self.client.read(
            f"{self.pki_path}/crl"
        )
        return response['data']['crl']
```

### 12.3 SPIFFE/SPIRE

**SPIFFE（Secure Production Identity Framework for Everyone）** 是云原生工作负载身份标准。

```
SPIFFE身份格式：
  spiffe://<trust-domain>/<workload-identifier>
  
示例：
  spiffe://example.com/backend/payments
  spiffe://example.com/frontend/web
  spiffe://staging.example.com/database/mysql

SPIFFE组件：
  SPIRE Server  - 签发SVID（SPIFFE身份验证文件）
  SPIRE Agent   - 在节点上运行，为工作负载提供SVID
  
SVID类型：
  X.509 SVID  - 基于X.509证书的工作负载身份
  JWT SVID    - 基于JWT的工作负载身份
```

---

---

