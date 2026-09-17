# Python容器安全检查脚本示例

### 8.1 Docker API安全检查脚本

```python
#!/usr/bin/env python3
"""
Docker 容器安全检查脚本
检查运行中容器的安全配置，输出安全风险报告。
"""
import docker
import json
from datetime import datetime


def check_container_security(container):
    """检查单个容器的安全配置"""
    issues = []
    info = container.attrs

    # 检查1：是否以特权模式运行
    if info["HostConfig"]["Privileged"]:
        issues.append({"severity": "CRITICAL",
                       "issue": "容器以特权模式运行，存在逃逸风险"})

    # 检查2：是否以 root 运行
    user = info["Config"].get("User", "")
    if not user or user == "root" or user == "0":
        issues.append({"severity": "HIGH",
                       "issue": "容器以 root 用户运行"})

    # 检查3：是否挂载了 Docker Socket
    binds = info["HostConfig"].get("Binds", []) or []
    for bind in binds:
        if "docker.sock" in bind:
            issues.append({"severity": "CRITICAL",
                           "issue": f"挂载了 Docker Socket: {bind}"})

    # 检查4：是否挂载了宿主机敏感目录
    for bind in binds:
        for sensitive_path in ["/", "/etc", "/root", "/var/run"]:
            if bind.startswith(sensitive_path + ":") or bind.startswith(sensitive_path):
                issues.append({"severity": "CRITICAL",
                               "issue": f"挂载了宿主机敏感目录: {bind}"})

    # 检查5：是否启用只读文件系统
    if not info["HostConfig"]["ReadonlyRootfs"]:
        issues.append({"severity": "MEDIUM",
                       "issue": "未启用只读文件系统"})

    # 检查6：是否禁止 privilege escalation
    security_opt = info["HostConfig"].get("SecurityOpt", []) or []
    if "no-new-privileges" not in security_opt:
        issues.append({"severity": "MEDIUM",
                       "issue": "未禁止 privilege escalation (no-new-privileges)"})

    # 检查7：Capabilities 是否过多
    caps = info["HostConfig"].get("CapAdd", []) or []
    caps_drop = info["HostConfig"].get("CapDrop", []) or []
    if not caps_drop and not caps:
        issues.append({"severity": "LOW",
                       "issue": "使用默认 Capabilities，建议 --cap-drop ALL"})

    # 检查8：资源限制
    mem_limit = info["HostConfig"].get("Memory", 0)
    cpu_quota = info["HostConfig"].get("CpuQuota", 0)
    if mem_limit == 0:
        issues.append({"severity": "MEDIUM", "issue": "未设置内存限制"})
    if cpu_quota == 0:
        issues.append({"severity": "MEDIUM", "issue": "未设置 CPU 限制"})

    # 检查9：网络模式
    network_mode = info["HostConfig"].get("NetworkMode", "default")
    if network_mode == "host":
        issues.append({"severity": "HIGH",
                       "issue": "使用 host 网络模式，容器可访问宿主机网络"})

    return {
        "container": container.name,
        "image": info["Config"]["Image"],
        "issues": issues
    }


def main():
    client = docker.from_env()
    containers = client.containers.list(all=True)
    report = {
        "scan_time": datetime.now().isoformat(),
        "total_containers": len(containers),
        "results": []
    }

    for container in containers:
        result = check_container_security(container)
        report["results"].append(result)

    # 统计
    critical = sum(1 for r in report["results"]
                   for i in r["issues"] if i["severity"] == "CRITICAL")
    high = sum(1 for r in report["results"]
               for i in r["issues"] if i["severity"] == "HIGH")
    print(f"\n{'='*60}")
    print(f"  Docker 容器安全检查报告")
    print(f"  扫描时间: {report['scan_time']}")
    print(f"  容器总数: {report['total_containers']}")
    print(f"  CRITICAL: {critical} | HIGH: {high}")
    print(f"{'='*60}")

    for result in report["results"]:
        if result["issues"]:
            print(f"\n  [容器] {result['container']} ({result['image']})")
            for issue in result["issues"]:
                print(f"    [{issue['severity']}] {issue['issue']}")

    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
```

### 8.2 K8s API安全审计脚本

```python
#!/usr/bin/env python3
"""
Kubernetes 集群安全审计脚本
使用 client-python 检查 K8s 集群安全配置。
依赖: pip install kubernetes
"""
from kubernetes import client, config


class K8sSecurityAuditor:
    def __init__(self):
        config.load_kube_config()
        self.v1 = client.CoreV1Api()
        self.rbac = client.RbacAuthorizationV1Api()
        self.policy = client.PolicyV1Api()

    def check_anonymous_access(self):
        """检查API Server是否允许匿名访问"""
        # 模拟匿名访问（实际应通过 --anonymous-auth=false 关闭）
        issues = []
        try:
            # 检查是否有 system:anonymous 绑定
            bindings = self.rbac.list_cluster_role_binding()
            for b in bindings.items:
                for subject in (b.subjects or []):
                    if subject.name == "system:anonymous":
                        issues.append({
                            "severity": "CRITICAL",
                            "issue": f"匿名用户绑定了角色: {b.metadata.name}"
                        })
        except Exception as e:
            issues.append({"severity": "INFO",
                           "issue": f"检查异常: {e}"})
        return issues

    def check_overprivileged_rbac(self):
        """检查过度授权的RBAC配置"""
        issues = []
        # 检查 cluster-admin 绑定
        crbs = self.rbac.list_cluster_role_binding()
        for crb in crbs.items:
            if crb.role_ref.name == "cluster-admin":
                for subject in (crb.subjects or []):
                    if subject.kind == "ServiceAccount":
                        issues.append({
                            "severity": "HIGH",
                            "issue": f"ServiceAccount '{subject.name}' 拥有 cluster-admin 权限"
                        })
        return issues

    def check_pod_security(self):
        """检查Pod安全配置"""
        issues = []
        pods = self.v1.list_pod_for_all_namespaces()
        for pod in pods.items:
            for cs in pod.spec.containers:
                sc = cs.security_context
                name = f"{pod.metadata.namespace}/{pod.metadata.name}/{cs.name}"

                # 检查特权容器
                if sc and sc.privileged:
                    issues.append({
                        "severity": "CRITICAL",
                        "issue": f"特权容器: {name}"
                    })

                # 检查 root 运行
                if not sc or not sc.run_as_non_root:
                    issues.append({
                        "severity": "HIGH",
                        "issue": f"未设置 runAsNonRoot: {name}"
                    })

                # 检查 privilege escalation
                if not sc or sc.allow_privilege_escalation is not False:
                    issues.append({
                        "severity": "MEDIUM",
                        "issue": f"未禁止 allowPrivilegeEscalation: {name}"
                    })

                # 检查 capabilities
                if sc and sc.capabilities:
                    drops = sc.capabilities.drop or []
                    if "ALL" not in drops:
                        issues.append({
                            "severity": "MEDIUM",
                            "issue": f"未 drop ALL capabilities: {name}"
                        })
                else:
                    issues.append({
                        "severity": "MEDIUM",
                        "issue": f"未配置 capabilities drop: {name}"
                    })
        return issues

    def check_namespaces_with_secrets(self):
        """检查默认命名空间是否包含敏感Secret"""
        issues = []
        secrets = self.v1.list_secret_for_all_namespaces()
        for secret in secrets.items:
            if secret.type == "kubernetes.io/service-account-token":
                continue  # 跳过SA token
            if secret.data:
                issues.append({
                    "severity": "INFO",
                    "issue": f"Secret存在: {secret.metadata.namespace}/{secret.metadata.name}"
                })
        return issues

    def audit(self):
        """执行完整审计"""
        print(f"\n{'='*60}")
        print("  Kubernetes 安全审计报告")
        print(f"{'='**60}".replace("*", ""))

        checks = [
            ("匿名访问检查", self.check_anonymous_access),
            ("过度授权RBAC检查", self.check_overprivileged_rbac),
            ("Pod安全检查", self.check_pod_security),
            ("Secret检查", self.check_namespaces_with_secrets),
        ]

        for name, func in checks:
            print(f"\n  [{name}]")
            results = func()
            if not results:
                print("    通过 - 未发现问题")
            for r in results:
                print(f"    [{r['severity']}] {r['issue']}")


if __name__ == "__main__":
    auditor = K8sSecurityAuditor()
    auditor.audit()
```

---

---

## 📋 内容审核与补充建议

> 针对「Python容器安全检查脚本示例」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

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
