# CoAP消息格式详解

### 3.1 消息结构

```
CoAP消息格式 (RFC 7252):

 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|Ver| T |  TKL  |      Code     |          Message ID          |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|   Token (if any, TKL = 0-8 bytes)                           ...
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|   Options (if any)                                          ...
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|1 1 1 1 1 1 1 1|    Payload (if any)                         ...
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

字段说明:
- Ver (2 bits): 版本号，固定为01
- T (2 bits): 消息类型 (CON=00, NON=01, ACK=10, RST=11)
- TKL (4 bits): Token长度 (0-8)
- Code (8 bits): 响应码/方法码
- Message ID (16 bits): 消息标识符（用于去重和匹配）
- Token (0-8 bytes): 请求-响应匹配令牌
- Options: 选项字段
- Payload Marker: 0xFF（分隔选项和负载）
- Payload: 实际数据
```

### 3.2 CoAP方法码

```
方法码 (Code = 0b.cccc.dddd):

请求方法:
  0.01 = GET
  0.02 = POST
  0.03 = PUT
  0.04 = DELETE

响应码:
  2.xx = 成功
    2.01 = Created
    2.02 = Deleted
    2.03 = Valid
    2.04 = Changed
    2.05 = Content
  
  4.xx = 客户端错误
    4.00 = Bad Request
    4.01 = Unauthorized
    4.02 = Bad Option
    4.03 = Forbidden
    4.04 = Not Found
    4.05 = Method Not Allowed
  
  5.xx = 服务端错误
    5.00 = Internal Server Error
    5.01 = Not Implemented
    5.02 = Bad Gateway
    5.03 = Service Unavailable
```

### 3.3 CoAP选项

```python
# CoAP选项解析器
class CoAPOption:
    """CoAP选项定义"""
    
    # 选项编号
    IF_NONE_MATCH = 1
    URI_HOST = 3
    URI_PORT = 7
    URI_PATH = 11
    CONTENT_FORMAT = 12
    MAX_AGE = 14
    URI_QUERY = 15
    ACCEPT = 17
    TOKEN = 19
    BLOCK1 = 23
    BLOCK2 = 27
    SIZE1 = 28
    SIZE2 = 29
    PROXY_URI = 35
    PROXY_SCHEME = 39
    OBSERVE = 6
    
    # 内容格式
    TEXT_PLAIN = 0
    APP_LINK_FORMAT = 40
    APP_XML = 41
    APP_JSON = 50
    APP_CBOR = 60
    APP_EXI = 47
    
    # 选项属性
    OPTION_PROPERTIES = {
        IF_NONE_MATCH: {'critical': True, 'unsafe': False, 'length': 0},
        URI_HOST: {'critical': True, 'unsafe': True, 'length': '1-255'},
        URI_PORT: {'critical': True, 'unsafe': True, 'length': '0-2'},
        URI_PATH: {'critical': True, 'unsafe': True, 'length': '0-255'},
        CONTENT_FORMAT: {'critical': False, 'unsafe': False, 'length': '0-2'},
        MAX_AGE: {'critical': False, 'unsafe': False, 'length': '0-4'},
        URI_QUERY: {'critical': True, 'unsafe': True, 'length': '0-255'},
        ACCEPT: {'critical': True, 'unsafe': False, 'length': '0-2'},
        BLOCK1: {'critical': False, 'unsafe': True, 'length': '0-3'},
        BLOCK2: {'critical': False, 'unsafe': True, 'length': '0-3'},
        OBSERVE: {'critical': False, 'unsafe': False, 'length': '0-3'},
    }

def parse_coap_message(data: bytes) -> dict:
    """解析CoAP消息"""
    if len(data) < 4:
        return {'error': '消息过短'}
    
    # 解析头部
    ver = (data[0] >> 6) & 0x03
    msg_type = (data[0] >> 4) & 0x03
    tkl = data[0] & 0x0F
    code = data[1]
    msg_id = (data[2] << 8) | data[3]
    
    # 解析Token
    offset = 4
    token = data[offset:offset+tkl] if tkl > 0 else b''
    offset += tkl
    
    # 解析选项
    options = []
    prev_option = 0
    while offset < len(data):
        if data[offset] == 0xFF:
            # 负载标记
            offset += 1
            break
        
        # 解析选项delta和长度
        delta = (data[offset] >> 4) & 0x0F
        length = data[offset] & 0x0F
        offset += 1
        
        # 扩展delta
        if delta == 13:
            delta = 13 + data[offset]
            offset += 1
        elif delta == 14:
            delta = 269 + (data[offset] << 8 | data[offset+1])
            offset += 2
        elif delta == 15:
            return {'error': '无效的选项delta'}
        
        # 扩展长度
        if length == 13:
            length = 13 + data[offset]
            offset += 1
        elif length == 14:
            length = 269 + (data[offset] << 8 | data[offset+1])
            offset += 2
        elif length == 15:
            return {'error': '无效的选项长度'}
        
        # 计算实际选项号
        option_num = prev_option + delta
        prev_option = option_num
        
        # 读取选项值
        option_value = data[offset:offset+length]
        offset += length
        
        options.append({
            'number': option_num,
            'value': option_value
        })
    
    # 解析负载
    payload = data[offset:] if offset < len(data) else b''
    
    return {
        'version': ver,
        'type': msg_type,
        'tkl': tkl,
        'code': code,
        'message_id': msg_id,
        'token': token.hex(),
        'options': options,
        'payload': payload,
    }
```

### 3.4 资源发现

```
CoAP资源发现:
- 标准路径: /.well-known/core
- 返回格式: Application/Link-Format (CT=40)
- 包含设备上所有可用资源的描述

请求示例:
  GET coap://[2001:db8::1]/.well-known/core

响应示例:
  </sensors/temp>;ct=50;rt="temperature-c";if="sensor",
  </sensors/humidity>;ct=50;rt="humidity";if="sensor",
  </actuators/led>;ct=0;rt="led";if="actuator",
  </firmware>;ct=50;rt="firmware";if="info"

参数说明:
- ct: 内容格式 (Content-Format)
- rt: 资源类型 (Resource Type)
- if: 接口描述 (Interface Description)
```

---

---

## 📋 内容审核与补充建议

> 针对「CoAP消息格式详解」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

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
