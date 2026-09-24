# 内核模糊测试（syzkaller）

syzkaller是Google开发的Linux内核模糊测试框架，已发现大量内核漏洞。

**安装syzkaller：**

```bash
# 依赖安装
sudo apt install debootstrap

# 克隆syzkaller
git clone https://github.com/google/syzkaller.git
cd syzkaller

# 编译
make

# 配置文件
cat > my.cfg << 'EOF'
{
    "target": "linux/amd64",
    "http": "localhost:56700",
    "workdir": "/syzkaller/workdir",
    "kernel_obj": "/linux/build",
    "image": "/syzkaller/image",
    "syzkaller": "/syzkaller",
    "type": "qemu",
    "vm": {
        "count": 4,
        "cpu": 2,
        "mem": 2048
    }
}
EOF

# 运行
./bin/syz-manager -config=my.cfg
```

**自定义系统调用描述：**

```go
// custom_device.go
// 自定义设备驱动的系统调用描述

include <uapi/linux/fs.h>

resource fd_custom : fd

open$custom(filename filename) fd_custom
ioctl$custom(fd fd_custom, cmd int32, arg ptr[in, custom_struct]) int32

type custom_struct {
    field1 int32
    field2 int32
    field3 array[int8, 16]
}
```

---

---

