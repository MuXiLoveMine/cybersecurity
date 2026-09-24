# ACR122U详细使用

### 14.1 ACR122U APDU命令参考

```python
# ACR122U PC/SC APDU命令参考
from smartcard.scard import *
from smartcard.util import *

class ACR122U:
    """ACR122U NFC读写器封装"""

    # PC/SC直接命令
    GET_FIRMWARE_VERSION = [0xFF, 0x00, 0x48, 0x00, 0x00]
    SET_LED = [0xFF, 0x00, 0x40, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00]
    SET_BUZZER = [0xFF, 0x00, 0x40, 0x00, 0x04, 0x00, 0x00, 0x00, 0x02]
    GET_RESPONSE = [0xFF, 0xCA, 0x00, 0x00, 0x00]
    LOAD_AUTH_KEYS = [0xFF, 0x82, 0x00, 0x00, 0x06]
    AUTHENTICATE = [0xFF, 0x86, 0x00, 0x00, 0x05, 0x01, 0x00]

    def __init__(self):
        self.hcontext = None
        self.hcard = None
        self.protocol = None

    def connect(self):
        """连接读卡器"""
        hresult, self.hcontext = SCardEstablishContext(SCARD_SCOPE_USER)
        if hresult != SCARD_S_SUCCESS:
            raise Exception(f"无法建立上下文: {hresult}")

        hresult, readers = SCardListReaders(self.hcontext, [])
        if not readers:
            raise Exception("未找到读卡器")

        reader = readers[0]
        hresult, self.hcard, self.protocol = SCardConnect(
            self.hcontext, reader,
            SCARD_SHARE_SHARED,
            SCARD_PROTOCOL_T0 | SCARD_PROTOCOL_T1
        )
        if hresult != SCARD_S_SUCCESS:
            raise Exception(f"无法连接: {hresult}")

        print(f"已连接: {reader}")
        return reader

    def get_firmware_version(self):
        """获取固件版本"""
        response, sw1, sw2 = self._transmit(self.GET_FIRMWARE_VERSION)
        return ''.join(chr(b) for b in response)

    def get_uid(self):
        """获取卡片UID"""
        response, sw1, sw2 = self._transmit(self.GET_RESPONSE)
        if sw1 == 0x90:
            return toHexString(response)
        return None

    def load_auth_key(self, key_number, key):
        """加载认证密钥
        key_number: 0 或 1
        key: 6字节密钥
        """
        cmd = self.LOAD_AUTH_KEYS + [key_number] + list(key)
        _, sw1, sw2 = self._transmit(cmd)
        return sw1 == 0x90

    def authenticate(self, block_number, key_type, key_number):
        """认证扇区
        block_number: 块号
        key_type: 0x60 (Key A) 或 0x61 (Key B)
        key_number: 0 或 1 (对应load_auth_key)
        """
        cmd = self.AUTHENTICATE + [block_number, key_type, key_number]
        _, sw1, sw2 = self._transmit(cmd)
        return sw1 == 0x90

    def read_block(self, block_number):
        """读取块"""
        cmd = [0xFF, 0xB0, 0x00, block_number, 0x10]
        response, sw1, sw2 = self._transmit(cmd)
        if sw1 == 0x90:
            return bytes(response)
        return None

    def write_block(self, block_number, data):
        """写入块(16字节)"""
        if len(data) != 16:
            raise ValueError("数据必须为16字节")
        cmd = [0xFF, 0xD6, 0x00, block_number, 0x10] + list(data)
        _, sw1, sw2 = self._transmit(cmd)
        return sw1 == 0x90

    def read_mifare_classic(self, key_a=bytes([0xFF]*6)):
        """读取Mifare Classic 1K"""
        uid = self.get_uid()
        print(f"UID: {uid}")

        all_data = {}
        for sector in range(16):
            # 加载密钥
            self.load_auth_key(0, key_a)
            # 认证
            block = sector * 4
            if self.authenticate(block, 0x60, 0):
                # 读取扇区所有块
                sector_data = []
                for b in range(4):
                    data = self.read_block(block + b)
                    if data:
                        sector_data.append(data.hex())
                    else:
                        sector_data.append(None)
                all_data[sector] = sector_data
                print(f"Sector {sector}: {sector_data}")
            else:
                print(f"Sector {sector}: 认证失败")
                all_data[sector] = None

        return all_data

    def clone_mifare_classic(self, source_data, magic_card=True):
        """克隆Mifare Classic到Magic卡"""
        if not magic_card:
            print("警告: 非Magic卡无法写入Block 0(UID)")

        for sector, blocks in source_data.items():
            if blocks is None:
                continue
            for block_offset, block_data in enumerate(blocks):
                if block_data is None:
                    continue
                block_number = sector * 4 + block_offset
                data = bytes.fromhex(block_data)

                # 跳过密钥块(除非有Key B写入权限)
                if block_offset == 3 and not magic_card:
                    continue

                self.write_block(block_number, data)
                print(f"写入 Block {block_number}: OK")

    def _transmit(self, apdu):
        """发送APDU"""
        if not self.hcard:
            raise Exception("未连接读卡器")
        hresult, response = SCardTransmit(
            self.hcard, self.protocol, apdu
        )
        if hresult != SCARD_S_SUCCESS:
            raise Exception(f"传输失败: {hresult}")
        data = list(response[:-2])
        sw1 = response[-2]
        sw2 = response[-1]
        return data, sw1, sw2

    def disconnect(self):
        """断开连接"""
        if self.hcard:
            SCardDisconnect(self.hcard, SCARD_UNPOWER_CARD)
        if self.hcontext:
            SCardReleaseContext(self.hcontext)

# 使用示例
reader = ACR122U()
reader.connect()
print(f"固件: {reader.get_firmware_version()}")
data = reader.read_mifare_classic()
reader.disconnect()
```

---

---

