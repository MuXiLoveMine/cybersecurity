# Havex分析

### 5.1 概述

Havex发现于2013年，是一种针对工控系统的远程访问木马(RAT)。它通过感染工控软件供应商的网站，在用户下载合法工控软件时植入恶意代码。

```
Havex基本信息:
- 发现时间: 2013年
- 目标: 欧洲能源、水电、石油天然气行业
- 传播方式: 水坑攻击 (感染工控软件下载站点)
- 攻击目的: 信息收集和远程控制
- 特殊功能: OPC数据枚举
```

### 5.2 OPC数据枚举

Havex的独特之处在于能够枚举OPC服务器的标签信息：

```
Havex OPC枚举流程:

1. 发现OPC服务器:
   - 扫描本地和远程OPC服务器
   - 使用OPC枚举接口

2. 连接OPC服务器:
   - 使用DCOM连接
   - 调用IOPCServerList接口

3. 获取标签信息:
   - 枚举所有数据点 (Tag)
   - 获取标签名称、类型、地址
   - 记录到本地文件

4. 上传数据:
   - 将OPC标签信息打包
   - 通过HTTP上传到C2服务器

影响:
- 攻击者获取了完整的工艺流程信息
- 了解了传感器和执行器的布局
- 为后续攻击提供了精确的目标信息
```

```c
// Havex OPC枚举伪代码
void enumerate_opc_tags() {
    // 1. 创建OPC枚举器
    IOPCServerList* pServerList = NULL;
    CoCreateInstance(CLSID_OPCServerList, NULL, CLSCTX_ALL,
                     IID_IOPCServerList, (void**)&pServerList);
    
    // 2. 枚举可用的OPC服务器
    IEnumUnknown* pEnum = NULL;
    pServerList->EnumClassesOfCategories(..., &pEnum);
    
    // 3. 连接每个OPC服务器
    while (pEnum->Next(1, &pServer, NULL) == S_OK) {
        IOPCServer* pOPCServer = NULL;
        pServer->QueryInterface(IID_IOPCServer, (void**)&pOPCServer);
        
        if (pOPCServer) {
            // 4. 添加OPC组
            IOPCItemMgt* pItemMgt = NULL;
            pOPCServer->AddGroup(..., &pItemMgt);
            
            // 5. 枚举所有标签
            IEnumString* pEnumTags = NULL;
            // 使用IOPCBrowseServerAddressSpace接口
            pOPCServer->QueryInterface(
                IID_IOPCBrowseServerAddressSpace,
                (void**)&pBrowse);
            
            if (pBrowse) {
                LPWSTR tagName = NULL;
                while (pBrowse->Browse(&tagName) == S_OK) {
                    // 记录标签信息
                    log_tag_info(tagName);
                }
            }
        }
    }
}
```

---

---

## 📋 内容审核与补充建议

> 针对「Havex分析」部分的内容审核结果：

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
