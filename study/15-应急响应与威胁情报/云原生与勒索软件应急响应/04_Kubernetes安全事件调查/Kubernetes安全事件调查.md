# Kubernetes安全事件调查

### 4.1 Kubernetes审计日志分析

Kubernetes审计日志记录了对API Server的所有操作，是K8s安全调查的核心数据源。

**审计日志配置：**

```yaml
# /etc/kubernetes/audit/policy.yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
  # 记录所有Secret操作
  - level: RequestResponse
    resources:
      - group: ""
        resources: ["secrets"]
  
  # 记录所有认证授权操作
  - level: RequestResponse
    resources:
      - group: ""
        resources: ["pods/exec", "pods/portforward", "pods/attach"]
  
  # 记录所有ServiceAccount Token操作
  - level: RequestResponse
    resources:
      - group: ""
        resources: ["serviceaccounts/token"]
  
  # 记录所有RBAC变更
  - level: RequestResponse
    resources:
      - group: "rbac.authorization.k8s.io"
        resources: ["roles", "clusterroles", "rolebindings", "clusterrolebindings"]
  
  # 记录所有Pod创建/删除
  - level: Request
    resources:
      - group: ""
        resources: ["pods"]
    verbs: ["create", "delete", "update", "patch"]
  
  # 记录所有Deployment变更
  - level: Request
    resources:
      - group: "apps"
        resources: ["deployments", "daemonsets", "statefulsets"]
    verbs: ["create", "delete", "update", "patch"]
  
  # 其他请求只记录元数据
  - level: Metadata
```

**审计日志分析脚本：**

```bash
#!/bin/bash
# k8s_audit_analyzer.sh - Kubernetes审计日志分析

AUDIT_LOG="/var/log/kubernetes/audit/audit.log"

echo "=== 审计日志分析报告 ==="
echo "时间范围: $(head -1 $AUDIT_LOG | jq -r '.stageTimestamp') ~ $(tail -1 $AUDIT_LOG | jq -r '.stageTimestamp')"
echo ""

echo "--- 1. 异常API调用 ---"
# 查找被拒绝的请求
cat $AUDIT_LOG | jq -r 'select(.code >= 400) | "\(.stageTimestamp) \(.user.username) \(.verb) \(.resourceURI) -> \(.code)"' | head -30

echo ""
echo "--- 2. 敏感资源访问 ---"
# 查找Secret访问
cat $AUDIT_LOG | jq -r 'select(.resourceURI | contains("/secrets")) | "\(.stageTimestamp) \(.user.username) \(.verb) \(.resourceURI)"'

# 查找exec/exec到Pod
cat $AUDIT_LOG | jq -r 'select(.resourceURI | contains("/exec")) | "\(.stageTimestamp) \(.user.username) exec into \(.resourceURI)"'

# 查找port-forward
cat $AUDIT_LOG | jq -r 'select(.resourceURI | contains("/portforward")) | "\(.stageTimestamp) \(.user.username) port-forward \(.resourceURI)"'

echo ""
echo "--- 3. RBAC变更 ---"
# 查找ClusterRole/Role变更
cat $AUDIT_LOG | jq -r 'select(.resourceURI | test("/clusterroles|/roles|/clusterrolebindings|/rolebindings")) | "\(.stageTimestamp) \(.user.username) \(.verb) \(.resourceURI)"'

echo ""
echo "--- 4. ServiceAccount Token使用 ---"
cat $AUDIT_LOG | jq -r 'select(.user.username | startswith("system:serviceaccount:")) | "\(.stageTimestamp) \(.user.username) \(.verb) \(.resourceURI)"' | sort | uniq -c | sort -rn | head -20

echo ""
echo "--- 5. 匿名访问 ---"
cat $AUDIT_LOG | jq -r 'select(.user.username == "system:anonymous" or .user.username == "system:unauthenticated") | "\(.stageTimestamp) \(.verb) \(.resourceURI) -> \(.code)"'

echo ""
echo "--- 6. 高频操作统计 ---"
cat $AUDIT_LOG | jq -r '"\(.user.username) \(.verb) \(.resourceURI | split("/")[1] // "cluster")"' | sort | uniq -c | sort -rn | head -20

echo ""
echo "--- 7. 来自异常IP的访问 ---"
cat $AUDIT_LOG | jq -r 'select(.sourceIPs[0] != null) | "\(.sourceIPs[0]) \(.user.username)"' | sort -u
```

### 4.2 API Server调查

```bash
# 检查API Server配置
cat /etc/kubernetes/manifests/kube-apiserver.yaml | grep -E "audit|authorization|authentication|anonymous"

# 检查是否启用了匿名访问
kubectl get clusterrolebinding system:anonymous -o yaml 2>/dev/null
kubectl get clusterrolebinding system:discovery -o yaml 2>/dev/null

# 检查RBAC配置中的过度权限
# 查找具有cluster-admin权限的绑定
kubectl get clusterrolebinding -o json | jq -r '.items[] | select(.roleRef.name=="cluster-admin") | .metadata.name + " -> " + (.subjects // [] | map(.name) | join(","))'

# 检查所有用户证书
find /etc/kubernetes -name "*.crt" -exec openssl x509 -in {} -text -noout \; 2>/dev/null | grep -E "Subject:|Not After"

# 检查kubeconfig文件
find / -name "kubeconfig" -o -name "config" -path "*/.kube/*" 2>/dev/null | head -10

# 检查API Server是否暴露在公网
netstat -tlnp | grep 6443
ss -tlnp | grep 6443

# 检查etcd中的凭据
ETCDCTL_API=3 etcdctl --endpoints=https://127.0.0.1:2379 \
  --cert=/etc/kubernetes/pki/etcd/healthcheck-client.crt \
  --key=/etc/kubernetes/pki/etcd/healthcheck-client.key \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  get / --prefix --keys-only | grep -i secret | head -20
```

### 4.3 异常Pod检测

```bash
# 检查所有Pod的安全上下文
kubectl get pods --all-namespaces -o json | jq -r '
  .items[] |
  select(.spec.securityContext.privileged == true or
         .spec.containers[].securityContext.privileged == true) |
  "\(.metadata.namespace)/\(.metadata.name) - PRIVILEGED"'

# 检查以root运行的Pod
kubectl get pods --all-namespaces -o json | jq -r '
  .items[] |
  select(.spec.securityContext.runAsUser == 0 or
         (.spec.containers[].securityContext.runAsUser // 0) == 0) |
  "\(.metadata.namespace)/\(.metadata.name) - ROOT"'

# 检查挂载了宿主机路径的Pod
kubectl get pods --all-namespaces -o json | jq -r '
  .items[] |
  .metadata.name as $name |
  .metadata.namespace as $ns |
  .spec.volumes[]? |
  select(.hostPath != null) |
  "\($ns)/\($name) -> \(.hostPath.path)"'

# 检查挂载了docker.sock的Pod
kubectl get pods --all-namespaces -o json | jq -r '
  .items[] |
  .metadata.name as $name |
  .metadata.namespace as $ns |
  .spec.volumes[]? |
  select(.hostPath.path == "/var/run/docker.sock" or .hostPath.path == "/run/containerd/containerd.sock") |
  "\($ns)/\($name) -> \(.hostPath.path) [HIGH RISK]"'

# 检查使用了hostNetwork的Pod
kubectl get pods --all-namespaces -o json | jq -r '
  .items[] | select(.spec.hostNetwork == true) |
  "\(.metadata.namespace)/\(.metadata.name) - HOSTNETWORK"'

# 检查使用了hostPID的Pod
kubectl get pods --all-namespaces -o json | jq -r '
  .items[] | select(.spec.hostPID == true) |
  "\(.metadata.namespace)/\(.metadata.name) - HOSTPID"'

# 检查包含可疑镜像的Pod
kubectl get pods --all-namespaces -o json | jq -r '
  .items[] |
  .metadata.name as $name |
  .metadata.namespace as $ns |
  .spec.containers[].image as $image |
  select($image | test("latest|none|scratch|miner|crypto"; "i")) |
  "\($ns)/\($name) -> \($image)"'

# 检查最近创建的Pod（可能是攻击者部署的）
kubectl get pods --all-namespaces --sort-by=.metadata.creationTimestamp | tail -20

# 检查不在已知Deployment/StatefulSet/DaemonSet管理下的Pod
kubectl get pods --all-namespaces -o json | jq -r '
  .items[] |
  select(.metadata.ownerReferences == null) |
  "\(.metadata.namespace)/\(.metadata.name) - NO OWNER"'
```

**异常Pod检测脚本（Python）：**

```python
#!/usr/bin/env python3
"""Kubernetes异常Pod检测工具"""
import json
import subprocess
from datetime import datetime, timedelta

class PodChecker:
    def __init__(self):
        self.alerts = []

    def get_all_pods(self):
        """获取所有Pod"""
        result = subprocess.run(
            ["kubectl", "get", "pods", "--all-namespaces", "-o", "json"],
            capture_output=True, text=True
        )
        return json.loads(result.stdout)

    def check_privileged(self, pods_data):
        """检查特权Pod"""
        for pod in pods_data['items']:
            ns = pod['metadata']['namespace']
            name = pod['metadata']['name']
            
            sc = pod.get('spec', {}).get('securityContext', {})
            if sc.get('privileged'):
                self.alerts.append({
                    'severity': 'CRITICAL',
                    'pod': f'{ns}/{name}',
                    'issue': 'Pod以特权模式运行',
                    'recommendation': '移除privileged: true'
                })
            
            for c in pod.get('spec', {}).get('containers', []):
                csc = c.get('securityContext', {})
                if csc.get('privileged'):
                    self.alerts.append({
                        'severity': 'CRITICAL',
                        'pod': f'{ns}/{name}',
                        'container': c['name'],
                        'issue': f'容器 {c["name"]} 以特权模式运行',
                        'recommendation': '移除privileged: true'
                    })

    def check_host_paths(self, pods_data):
        """检查宿主机路径挂载"""
        sensitive_paths = [
            '/var/run/docker.sock',
            '/run/containerd/containerd.sock',
            '/proc',
            '/sys',
            '/root',
            '/etc',
            '/var/lib/kubelet',
            '/var/lib/docker',
        ]
        
        for pod in pods_data['items']:
            ns = pod['metadata']['namespace']
            name = pod['metadata']['name']
            
            for vol in pod.get('spec', {}).get('volumes', []):
                if vol.get('hostPath'):
                    path = vol['hostPath']['path']
                    if path in sensitive_paths:
                        self.alerts.append({
                            'severity': 'CRITICAL',
                            'pod': f'{ns}/{name}',
                            'issue': f'挂载敏感宿主机路径: {path}',
                            'recommendation': '移除hostPath挂载或使用最小权限'
                        })

    def check_root_user(self, pods_data):
        """检查root用户"""
        for pod in pods_data['items']:
            ns = pod['metadata']['namespace']
            name = pod['metadata']['name']
            
            sc = pod.get('spec', {}).get('securityContext', {})
            if sc.get('runAsUser') == 0 or not sc.get('runAsUser'):
                self.alerts.append({
                    'severity': 'HIGH',
                    'pod': f'{ns}/{name}',
                    'issue': 'Pod可能以root用户运行',
                    'recommendation': '设置runAsUser为非0值'
                })

    def check_network_policies(self, pods_data):
        """检查是否有网络策略"""
        result = subprocess.run(
            ["kubectl", "get", "networkpolicies", "--all-namespaces", "-o", "json"],
            capture_output=True, text=True
        )
        policies = json.loads(result.stdout)
        
        namespaces = set()
        for pod in pods_data['items']:
            namespaces.add(pod['metadata']['namespace'])
        
        for ns in namespaces:
            ns_has_policy = any(
                p['metadata']['namespace'] == ns
                for p in policies.get('items', [])
            )
            if not ns_has_policy:
                self.alerts.append({
                    'severity': 'MEDIUM',
                    'pod': f'{ns}/*',
                    'issue': f'命名空间 {ns} 缺少网络策略',
                    'recommendation': '部署默认拒绝的网络策略'
                })

    def run_all_checks(self):
        """执行所有检查"""
        pods_data = self.get_all_pods()
        self.check_privileged(pods_data)
        self.check_host_paths(pods_data)
        self.check_root_user(pods_data)
        self.check_network_policies(pods_data)
        
        # 输出报告
        print("=" * 60)
        print("Kubernetes Pod安全检查报告")
        print(f"检查时间: {datetime.now()}")
        print("=" * 60)
        
        for alert in self.alerts:
            print(f"\n[{alert['severity']}] {alert['pod']}")
            print(f"  问题: {alert['issue']}")
            print(f"  建议: {alert['recommendation']}")
        
        print(f"\n总计: {len(self.alerts)} 个告警")

if __name__ == "__main__":
    checker = PodChecker()
    checker.run_all_checks()
```

---

---

