# iOS 权限机制

### 4.1 权限分类

iOS 的权限控制比 Android 更严格，所有需要访问用户隐私或系统功能的操作都需要用户授权。

#### 系统级权限（需用户授权）

| 权限 | 说明 | Info.plist Key |
|------|------|---------------|
| 相机 | 访问摄像头拍照/录像 | NSCameraUsageDescription |
| 照片 | 访问相册 | NSPhotoLibraryUsageDescription |
| 麦克风 | 录音、语音通话 | NSMicrophoneUsageDescription |
| 位置 | 定位服务 | NSLocationWhenInUseUsageDescription / NSLocationAlwaysAndWhenInUseUsageDescription |
| 通讯录 | 访问联系人 | NSContactsUsageDescription |
| 日历 | 访问日历事件 | NSCalendarsUsageDescription |
| 提醒事项 | 访问提醒事项 | NSRemindersUsageDescription |
| 蓝牙 | 蓝牙通信 | NSBluetoothAlwaysUsageDescription |
| 健康数据 | 访问 HealthKit | NSHealthShareUsageDescription / NSHealthUpdateUsageDescription |
| HomeKit | 智能家居控制 | NSHomeKitUsageDescription |
| Face ID / Touch ID | 生物识别 | NSFaceIDUsageDescription |
| 本地网络 | 本地网络扫描 | NSLocalNetworkUsageDescription |
| 追踪 | 跨应用跟踪用户 | AppTrackingTransparency |

#### 特殊权限（需 Apple 审核）

| 权限 | 说明 | 获取方式 |
|------|------|---------|
| VoIP | 后台语音通话 | 申请特殊 entitlement |
| 推送通知 | 远程推送 | 开发者后台配置 |
| 后台定位 | 持续后台定位 | 需说明用途 |
| 后台音频 | 后台播放音乐 | Capability 配置 |
| 后台下载 | 后台下载数据 | Background Modes |
| Network Extension | 网络扩展（VPN、代理等） | 需 Apple 批准 |

### 4.2 权限申请与检测

#### 权限申请流程

```
应用调用 API
   │
   ▼
系统检查权限状态
   ├── 未决定 ──→ 弹出授权对话框 → 用户选择 → 记录结果
   ├── 已授权 ──→ 正常执行
   └── 已拒绝 ──→ 返回错误/空数据
```

#### 代码示例

```swift
import AVFoundation
import Photos
import CoreLocation

// 相机权限检测
func checkCameraPermission() {
    let status = AVCaptureDevice.authorizationStatus(for: .video)
    switch status {
    case .authorized:
        print("已授权")
    case .denied, .restricted:
        print("已拒绝/受限制")
    case .notDetermined:
        // 请求授权
        AVCaptureDevice.requestAccess(for: .video) { granted in
            print("用户\(granted ? "同意" : "拒绝")")
        }
    @unknown default:
        break
    }
}

// 位置权限检测
let locationManager = CLLocationManager()
locationManager.delegate = self
locationManager.requestWhenInUseAuthorization()
```

### 4.3 权限安全问题

#### 常见问题

**1. 权限滥用**
- 申请不必要的权限，过度收集用户数据
- 例如：手电筒 App 请求通讯录权限

**2. 权限绕过**
- 利用系统漏洞绕过权限检查
- 例如：通过剪贴板间接获取数据

**3. 权限提升**
- 从普通应用权限提升到系统权限
- 通常利用系统服务漏洞

**4. 敏感 API 滥用**
- 滥用后台定位、麦克风等权限
- 偷录、偷拍、偷收集位置信息

#### 安全建议

- 只申请必要的权限
- 在需要使用时才请求权限
- 清晰说明权限用途（Usage Description）
- 处理用户拒绝权限的情况
- 定期审计权限使用情况

---

---

