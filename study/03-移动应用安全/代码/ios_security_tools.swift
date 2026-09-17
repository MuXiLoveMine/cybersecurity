import Foundation
import Security
import UIKit
import WebKit
import LocalAuthentication

// ============================================================================
// iOS安全工具集 v1.0
// 综合iOS应用安全分析工具
//
// 功能模块：
// 1. Keychain访问分析器
// 2. iOS应用沙盒检测器
// 3. 代码签名验证器
// 4. ATS（App Transport Security）配置检查器
// 5. iOS剪贴板安全监控器
// 6. URLSession安全配置
// 7. 本地存储安全检查器（NSUserDefaults/CoreData/Realm）
//
// 免责声明：仅用于授权的安全测试，未经授权分析他人应用属于违法行为。
// ============================================================================

// MARK: - 全局常量与工具

/// 安全严重程度枚举
enum SecuritySeverity: String, CaseIterable {
    case critical = "严重"
    case high = "高危"
    case medium = "中危"
    case low = "低危"
    case info = "信息"
}

/// 安全发现结果
struct SecurityFinding {
    let tool: String
    let severity: SecuritySeverity
    let title: String
    let description: String
    let recommendation: String
    let evidence: String

    func description() -> String {
        return """
        [\(severity.rawValue)] \(title)
          工具: \(tool)
          描述: \(description)
          证据: \(evidence)
          建议: \(recommendation)
        """
    }
}

/// 结果收集器
class ResultCollector {
    var findings: [SecurityFinding] = []

    func add(_ finding: SecurityFinding) {
        findings.append(finding)
    }

    func summary() -> String {
        var counts: [SecuritySeverity: Int] = [:]
        for f in findings {
            counts[f.severity, default: 0] += 1
        }
        var summary = "总发现数: \(findings.count)\n"
        for severity in SecuritySeverity.allCases {
            if let count = counts[severity], count > 0 {
                summary += "  \(severity.rawValue): \(count)\n"
            }
        }
        return summary
    }
}

/// 日志输出工具
class SecurityLogger {
    static func info(_ message: String) {
        print("[信息] \(message)")
    }

    static func success(_ message: String) {
        print("[成功] \(message)")
    }

    static func warning(_ message: String) {
        print("[警告] \(message)")
    }

    static func error(_ message: String) {
        print("[错误] \(message)")
    }

    static func vuln(_ message: String) {
        print("[漏洞] \(message)")
    }
}

// MARK: - 模块1：Keychain访问分析器

/// Keychain访问分析器
/// 分析iOS Keychain的使用安全性，包括：
/// - Keychain项的访问控制
/// - 项的可见性（kSecAttrAccessible）
/// - 是否使用了生物识别保护
/// - Keychain项的访问组
class KeychainAccessAnalyzer {

    /// Keychain项安全性级别
    enum KeychainAccessibility: String, CaseIterable {
        case accessibleWhenUnlocked = "kSecAttrAccessibleWhenUnlocked"
        case accessibleWhenUnlockedThisDeviceOnly = "kSecAttrAccessibleWhenUnlockedThisDeviceOnly"
        case accessibleAfterFirstUnlock = "kSecAttrAccessibleAfterFirstUnlock"
        case accessibleAfterFirstUnlockThisDeviceOnly = "kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly"
        case accessibleAlways = "kSecAttrAccessibleAlways"
        case accessibleAlwaysThisDeviceOnly = "kSecAttrAccessibleAlwaysThisDeviceOnly"
        case accessibleWhenPasscodeSetThisDeviceOnly = "kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly"

        /// 安全级别评估
        var securityLevel: SecuritySeverity {
            switch self {
            case .accessibleWhenPasscodeSetThisDeviceOnly:
                return .info // 最安全
            case .accessibleWhenUnlockedThisDeviceOnly,
                 .accessibleAfterFirstUnlockThisDeviceOnly:
                return .info
            case .accessibleWhenUnlocked,
                 .accessibleAfterFirstUnlock:
                return .low
            case .accessibleAlwaysThisDeviceOnly:
                return .medium
            case .accessibleAlways:
                return .high // 最不安全
            }
        }

        /// 安全描述
        var securityDescription: String {
            switch self {
            case .accessibleWhenPasscodeSetThisDeviceOnly:
                return "最高安全级别，需要密码且不跨设备同步"
            case .accessibleWhenUnlockedThisDeviceOnly:
                return "设备解锁时可访问，不跨设备同步"
            case .accessibleAfterFirstUnlockThisDeviceOnly:
                return "首次解锁后可访问，不跨设备同步"
            case .accessibleWhenUnlocked:
                return "设备解锁时可访问，可跨设备同步"
            case .accessibleAfterFirstUnlock:
                return "首次解锁后可访问，可跨设备同步"
            case .accessibleAlwaysThisDeviceOnly:
                return "始终可访问，不跨设备同步（不推荐）"
            case .accessibleAlways:
                return "始终可访问，可跨设备同步（最不安全）"
            }
        }
    }

    private let results = ResultCollector()

    /// 查询Keychain中所有的项
    func queryAllKeychainItems() -> [[String: Any]] {
        SecurityLogger.info("开始Keychain项查询...")

        // 查询所有Keychain项
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecReturnAttributes as String: true,
            kSecMatchLimit as String: kSecMatchLimitAll,
            kSecReturnData as String: false
        ]

        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)

        if status == errSecSuccess {
            if let items = result as? [[String: Any]] {
                SecurityLogger.success("发现 \(items.count) 个Keychain项")
                return items
            }
        } else if status == errSecItemNotFound {
            SecurityLogger.info("Keychain中未找到项")
        } else {
            SecurityLogger.error("Keychain查询失败，状态码: \(status)")
        }

        return []
    }

    /// 分析Keychain项的访问控制
    func analyzeKeychainSecurity() -> [SecurityFinding] {
        SecurityLogger.info("开始Keychain安全分析...")

        let items = queryAllKeychainItems()

        for item in items {
            let service = item[kSecAttrService as String] as? String ?? "未知"
            let account = item[kSecAttrAccount as String] as? String ?? "未知"
            let accessGroup = item[kSecAttrAccessGroup as String] as? String ?? "无"

            // 检查访问控制属性
            let accessible = item[kSecAttrAccessible as String] as? String

            if let accessibleValue = accessible {
                let accessibility = KeychainAccessibility(rawValue: accessibleValue)
                let level = accessibility?.securityLevel ?? .medium
                let desc = accessibility?.securityDescription ?? "未知访问级别"

                if level == .high || level == .medium {
                    results.add(SecurityFinding(
                        tool: "Keychain访问分析器",
                        severity: level,
                        title: "Keychain项访问级别不安全",
                        description: "Keychain项 (service: \(service), account: \(account)) 使用不安全的访问级别: \(accessibleValue)。\(desc)",
                        recommendation: "使用kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly或kSecAttrAccessibleWhenUnlockedThisDeviceOnly",
                        evidence: "accessible=\(accessibleValue), service=\(service), account=\(account)"
                    ))
                }
            }

            // 检查是否使用了访问控制（生物识别等）
            let accessControl = item[kSecAttrAccessControl as String]
            if accessControl == nil {
                results.add(SecurityFinding(
                    tool: "Keychain访问分析器",
                    severity: .low,
                    title: "Keychain项未设置访问控制",
                    description: "Keychain项 (service: \(service)) 未设置AccessControl，无法使用生物识别保护",
                    recommendation: "为敏感数据设置SecAccessControl，要求Face ID/Touch ID验证",
                    evidence: "无kSecAttrAccessControl, service=\(service)"
                ))
            }

            // 检查访问组
            if !accessGroup.isEmpty {
                SecurityLogger.info("Keychain项访问组: \(accessGroup) (service: \(service))")
            }
        }

        // 检查是否有未加密的敏感数据
        checkForSensitiveDataInKeychain(items)

        SecurityLogger.info("Keychain安全分析完成，发现 \(results.findings.count) 个问题")
        return results.findings
    }

    /// 检查Keychain中是否存储了敏感数据
    private func checkForSensitiveDataInKeychain(_ items: [[String: Any]]) {
        let sensitiveKeys = ["password", "token", "secret", "key", "credential",
                           "auth", "session", "api_key", "private"]

        for item in items {
            let service = (item[kSecAttrService as String] as? String ?? "").lowercased()
            let account = (item[kSecAttrAccount as String] as? String ?? "").lowercased()

            for sensitive in sensitiveKeys {
                if service.contains(sensitive) || account.contains(sensitive) {
                    results.add(SecurityFinding(
                        tool: "Keychain访问分析器",
                        severity: .info,
                        title: "Keychain中存储敏感数据",
                        description: "Keychain中存储了可能敏感的数据 (service: \(service), account: \(account))",
                        recommendation: "确保使用最高级别的访问控制和生物识别保护",
                        evidence: "service=\(service), account=\(account), 关键词=\(sensitive)"
                    ))
                    break
                }
            }
        }
    }

    /// 安全地存储数据到Keychain
    static func saveToKeychain(key: String, data: Data,
                                accessibility: CFString = kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly,
                                requireBiometric: Bool = false) -> Bool {
        // 删除旧项
        let deleteQuery: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key
        ]
        SecItemDelete(deleteQuery as CFDictionary)

        // 构建添加查询
        var addQuery: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecValueData as String: data,
            kSecAttrAccessible as String: accessibility
        ]

        // 如果需要生物识别
        if requireBiometric {
            var error: Unmanaged<CFError>?
            if let accessControl = SecAccessControlCreateWithFlags(
                kCFAllocatorDefault,
                accessibility,
                .userPresence,
                &error
            ) {
                addQuery[kSecAttrAccessControl as String] = accessControl
                addQuery.removeValue(forKey: kSecAttrAccessible as String)
            }
        }

        let status = SecItemAdd(addQuery as CFDictionary, nil)
        return status == errSecSuccess
    }

    /// 从Keychain读取数据
    static func loadFromKeychain(key: String) -> Data? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]

        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)

        if status == errSecSuccess {
            return result as? Data
        }
        return nil
    }

    /// 删除Keychain项
    static func deleteFromKeychain(key: String) -> Bool {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key
        ]
        let status = SecItemDelete(query as CFDictionary)
        return status == errSecSuccess || status == errSecItemNotFound
    }
}

// MARK: - 模块2：iOS应用沙盒检测器

/// iOS应用沙盒检测器
/// 检测应用的沙盒环境，包括：
/// - 沙盒目录结构
/// - 文件权限
/// - 越狱环境检测
/// - 敏感文件位置
class SandboxDetector {

    private let results = ResultCollector()

    /// 检测沙盒环境
    func detectSandboxEnvironment() -> [SecurityFinding] {
        SecurityLogger.info("开始沙盒环境检测...")

        checkSandboxDirectories()
        checkFilePermissions()
        checkJailbreakIndicators()
        checkSensitiveFileAccess()

        SecurityLogger.info("沙盒环境检测完成")
        return results.findings
    }

    /// 检查沙盒目录结构
    private func checkSandboxDirectories() {
        let fileManager = FileManager.default

        // 获取沙盒根目录
        let homeDir = NSHomeDirectory()
        SecurityLogger.info("沙盒根目录: \(homeDir)")

        // 检查各目录
        let directories = [
            ("Documents", homeDir + "/Documents"),
            ("Library", homeDir + "/Library"),
            ("Library/Caches", homeDir + "/Library/Caches"),
            ("Library/Preferences", homeDir + "/Library/Preferences"),
            ("tmp", homeDir + "/tmp")
        ]

        for (name, path) in directories {
            if fileManager.fileExists(atPath: path) {
                SecurityLogger.success("目录存在: \(name) -> \(path)")

                // 列出目录内容
                do {
                    let contents = try fileManager.contentsOfDirectory(atPath: path)
                    if name == "Preferences" && !contents.isEmpty {
                        results.add(SecurityFinding(
                            tool: "沙盒检测器",
                            severity: .low,
                            title: "Preferences目录包含plist文件",
                            description: "Preferences目录中包含 \(contents.count) 个文件，可能存储敏感配置",
                            recommendation: "敏感配置应使用Keychain或EncryptedCoreData存储",
                            evidence: "目录: \(path), 文件数: \(contents.count)"
                        ))
                    }
                } catch {
                    // 忽略错误
                }
            }
        }
    }

    /// 检查文件权限
    private func checkFilePermissions() {
        let fileManager = FileManager.default
        let homeDir = NSHomeDirectory()

        // 检查Documents目录中文件的权限
        let documentsPath = homeDir + "/Documents"
        if let contents = try? fileManager.contentsOfDirectory(atPath: documentsPath) {
            for file in contents {
                let filePath = documentsPath + "/" + file
                if let attrs = try? fileManager.attributesOfItem(atPath: filePath),
                   let permissions = attrs[.posixPermissions] as? NSNumber {

                    let perm = permissions.int16Value
                    let octalPerms = String(perm, radix: 8)

                    // 检查是否过于宽松
                    if perm & 0o077 != 0 {
                        results.add(SecurityFinding(
                            tool: "沙盒检测器",
                            severity: .low,
                            title: "文件权限过于宽松",
                            description: "文件 \(file) 的权限为 \(octalPerms)，允许组/其他用户访问",
                            recommendation: "设置文件权限为0600（仅所有者可读写）",
                            evidence: "文件: \(filePath), 权限: \(octalPerms)"
                        ))
                    }
                }
            }
        }
    }

    /// 检查越狱指示器
    private func checkJailbreakIndicators() {
        SecurityLogger.info("检测越狱指示器...")

        // 越狱文件路径
        let jailbreakPaths = [
            "/Applications/Cydia.app",
            "/Applications/Sileo.app",
            "/Applications/Zebra.app",
            "/Applications/Installer.app",
            "/Applications/SSH.app",
            "/Library/MobileSubstrate/MobileSubstrate.dylib",
            "/bin/bash",
            "/usr/sbin/sshd",
            "/etc/apt",
            "/usr/bin/ssh",
            "/private/var/lib/apt",
            "/usr/lib/sbsettings",
            "/bin/su",
            "/usr/bin/su",
            "/usr/sbin/inject",
            "/var/cache/apt",
            "/var/lib/cydia",
            "/var/log/syslog",
            "/var/tmp/cydia.log"
        ]

        let fileManager = FileManager.default
        var jailbreakIndicators: [String] = []

        for path in jailbreakPaths {
            if fileManager.fileExists(atPath: path) {
                jailbreakIndicators.append(path)
            }
        }

        // 检查是否能写入沙盒外路径
        let testPath = "/private/jailbreak_test"
        do {
            try "test".write(toFile: testPath, atomically: true, encoding: .utf8)
            try fileManager.removeItem(atPath: testPath)
            jailbreakIndicators.append("可写入沙盒外路径")
        } catch {
            // 正常情况 - 无法写入
        }

        // 检查URL Scheme
        if let url = URL(string: "cydia://package/com.example"),
           UIApplication.shared.canOpenURL(url) {
            jailbreakIndicators.append("Cydia URL scheme可用")
        }

        // 检查fork()能力
        var status: Int32 = 0
        let pid = fork()
        if pid >= 0 {
            if pid == 0 {
                exit(0)
            } else {
                waitpid(pid, &status, 0)
                jailbreakIndicators.append("fork()可用")
            }
        }

        if !jailbreakIndicators.isEmpty {
            results.add(SecurityFinding(
                tool: "沙盒检测器",
                severity: .critical,
                title: "检测到越狱环境",
                description: "检测到 \(jailbreakIndicators.count) 个越狱指示器: \(jailbreakIndicators.joined(separator: ", "))",
                recommendation: "在越狱设备上应增加额外的安全防护，或拒绝运行",
                evidence: jailbreakIndicators.joined(separator: "\n")
            ))
        } else {
            SecurityLogger.success("未检测到越狱指示器")
        }
    }

    /// 检查敏感文件访问
    private func checkSensitiveFileAccess() {
        let sensitivePaths = [
            "/etc/passwd",
            "/etc/master.passwd",
            "/etc/sudoers",
            "/private/var/log/syslog",
            "/var/log/syslog"
        ]

        for path in sensitivePaths {
            let content = try? String(contentsOfFile: path, encoding: .utf8)
            if content != nil {
                results.add(SecurityFinding(
                    tool: "沙盒检测器",
                    severity: .high,
                    title: "可读取系统敏感文件",
                    description: "应用可以读取系统文件: \(path)，表明沙盒可能被绕过",
                    recommendation: "确保应用在非越狱设备上运行，沙盒应阻止此类访问",
                    evidence: "可访问: \(path)"
                ))
            }
        }
    }
}

// MARK: - 模块3：代码签名验证器

/// 代码签名验证器
/// 验证应用的代码签名，包括：
/// - 签名有效性
/// - 证书信息
/// - 授权 entitlements
/// - provisioning profile
class CodeSignatureVerifier {

    private let results = ResultCollector()

    /// 验证代码签名
    func verifyCodeSignature() -> [SecurityFinding] {
        SecurityLogger.info("开始代码签名验证...")

        checkCodeSignatureStatus()
        checkEntitlements()
        checkProvisioningProfile()

        SecurityLogger.info("代码签名验证完成")
        return results.findings
    }

    /// 检查代码签名状态
    private func checkCodeSignatureStatus() {
        // 使用SecStaticCodeCheckValidity检查签名
        // 这里提供框架，实际需要Security.framework

        let bundlePath = Bundle.main.bundlePath

        // 使用codesign命令行工具（需要沙盒外执行）
        let task = Process()
        task.launchPath = "/usr/bin/codesign"
        task.arguments = ["-dv", "--verbose=4", bundlePath]

        let pipe = Pipe()
        task.standardOutput = pipe
        task.standardError = pipe

        do {
            try task.run()
            task.waitUntilExit()

            let data = pipe.fileHandleForReading.readDataToEndOfFile()
            if let output = String(data: data, encoding: .utf8) {
                SecurityLogger.success("代码签名信息获取成功")
                parseCodeSignOutput(output)
            }
        } catch {
            // 沙盒内可能无法执行
            results.add(SecurityFinding(
                tool: "代码签名验证器",
                severity: .info,
                title: "无法执行代码签名检查",
                description: "在应用沙盒内无法直接执行codesign命令，需要使用Security.framework API",
                recommendation: "使用SecStaticCodeCheckValidity API检查签名",
                evidence: "sandbox限制"
            ))
        }
    }

    /// 解析codesign输出
    private func parseCodeSignOutput(_ output: String) {
        let lines = output.split(separator: "\n")

        for line in lines {
            let trimmed = line.trimmingCharacters(in: .whitespaces)

            // 检查TeamIdentifier
            if trimmed.contains("TeamIdentifier=") {
                let teamId = trimmed.replacingOccurrences(of: "TeamIdentifier=", with: "")
                SecurityLogger.info("团队标识: \(teamId)")
            }

            // 检查Authority
            if trimmed.contains("Authority=") {
                let authority = trimmed.replacingOccurrences(of: "Authority=", with: "")
                SecurityLogger.info("签名权威: \(authority)")

                if authority.contains("iPhone Developer") {
                    results.add(SecurityFinding(
                        tool: "代码签名验证器",
                        severity: .medium,
                        title: "使用开发者签名",
                        description: "应用使用开发者证书签名，非App Store分发签名",
                        recommendation: "发布版本应使用App Store分发签名",
                        evidence: "Authority=\(authority)"
                    ))
                }
            }

            // 检查签名格式
            if trimmed.contains("format=") {
                let format = trimmed.replacingOccurrences(of: ".*format=", with: "")
                if format.contains("wrapper") {
                    results.add(SecurityFinding(
                        tool: "代码签名验证器",
                        severity: .info,
                        title: "签名格式信息",
                        description: "代码签名格式: \(format)",
                        recommendation: "确保使用最新签名格式",
                        evidence: "format=\(format)"
                    ))
                }
            }
        }
    }

    /// 检查Entitlements
    private func checkEntitlements() {
        // 检查应用的entitlements
        // 实际需要使用SecCodeCopySigningInformation API
        // 或解析embedded.mobileprovision文件

        let entitlementsPath = Bundle.main.path(forResource: "embedded", ofType: "mobileprovision")
        if entitlementsPath != nil {
            SecurityLogger.info("发现Provisioning Profile")

            // 解析Provisioning Profile
            // 实际需要解析plist格式的provisioning profile
        }

        // 检查危险entitlements
        results.add(SecurityFinding(
            tool: "代码签名验证器",
            severity: .info,
            title: "Entitlements检查清单",
            description: "需要检查以下entitlements: \n" +
                "  - com.apple.developer.networking.networkextension\n" +
                "  - com.apple.developer.kernel.extended-virtual-addressing\n" +
                "  - com.apple.developer.networking.HDLC.HDLC-Routing=1\n" +
                "  - get-task-allow（允许调试）\n" +
                "  - com.apple.developer.devicecheck.appattest-environment\n" +
                "  - keychain-access-groups\n" +
                "  - com.apple.developer.applesignin\n",
            recommendation: "检查entitlements是否合理，移除不需要的权限",
            evidence: "需检查embedded.mobileprovision"
        ))
    }

    /// 检查Provisioning Profile
    private func checkProvisioningProfile() {
        results.add(SecurityFinding(
            tool: "代码签名验证器",
            severity: .info,
            title: "Provisioning Profile检查",
            description: "检查embedded.mobileprovision：\n" +
                "  1. Profile是否过期\n" +
                "  2. 是否为Debug profile（get-task-allow=true）\n" +
                "  3. 设备UDID列表是否匹配\n" +
                "  4. App ID是否正确\n" +
                "  5. Team ID是否匹配\n",
            recommendation: "发布版本应移除Provisioning Profile或使用Distribution profile",
            evidence: "embedded.mobileprovision"
        ))
    }
}

// MARK: - 模块4：ATS配置检查器

/// ATS（App Transport Security）配置检查器
/// 检查Info.plist中的ATS配置，确保HTTPS安全策略
class ATSChecker {

    private let results = ResultCollector()

    /// 检查ATS配置
    func checkATSConfiguration() -> [SecurityFinding] {
        SecurityLogger.info("开始ATS配置检查...")

        guard let infoPlist = Bundle.main.infoDictionary else {
            SecurityLogger.error("无法读取Info.plist")
            return results.findings
        }

        // 获取NSAppTransportSecurity字典
        if let atsConfig = infoPlist["NSAppTransport安全"] as? [String: Any] {
            analyzeATSConfig(atsConfig)
        } else {
            // 检查是否存在NSAppTransportSecurity
            let atsKey = "NSAppTransportSecurity"
            if let atsConfig = infoPlist[atsKey] as? [String: Any] {
                analyzeATSConfig(atsConfig)
            } else {
                // 默认ATS配置（iOS 9+默认启用ATS）
                SecurityLogger.success("使用默认ATS配置（安全）")
            }
        }

        SecurityLogger.info("ATS配置检查完成")
        return results.findings
    }

    /// 分析ATS配置
    private func analyzeATSConfig(_ config: [String: Any]) {
        // 检查NSAllowsArbitraryLoads（允许任意HTTP）
        if let allowsArbitrary = config["NSAllowsArbitraryLoads"] as? Bool, allowsArbitrary {
            results.add(SecurityFinding(
                tool: "ATS检查器",
                severity: .high,
                title: "ATS全局禁用",
                description: "NSAllowsArbitraryLoads=true 禁用了App Transport Security，" +
                    "允许所有HTTP明文流量",
                recommendation: "设置NSAllowsArbitraryLoads=false，使用HTTPS",
                evidence: "NSAllowsArbitraryLoads=true"
            ))
        }

        // 检查NSAllowsArbitraryLoadsForMedia
        if let allowsMedia = config["NSAllowsArbitraryLoadsForMedia"] as? Bool, allowsMedia {
            results.add(SecurityFinding(
                tool: "ATS检查器",
                severity: .medium,
                title: "允许媒体内容HTTP加载",
                description: "NSAllowsArbitraryLoadsForMedia=true 允许媒体内容通过HTTP加载",
                recommendation: "使用HTTPS加载媒体内容",
                evidence: "NSAllowsArbitraryLoadsForMedia=true"
            ))
        }

        // 检查NSAllowsLocalNetworking
        if let allowsLocal = config["NSAllowsLocalNetworking"] as? Bool, allowsLocal {
            results.add(SecurityFinding(
                tool: "ATS检查器",
                severity: .low,
                title: "允许本地网络HTTP",
                description: "NSAllowsLocalNetworking=true 允许本地网络的HTTP流量",
                recommendation: "仅在与本地服务通信时使用",
                evidence: "NSAllowsLocalNetworking=true"
            ))
        }

        // 检查例外域名
        if let exceptions = config["NSExceptionDomains"] as? [String: Any] {
            for (domain, config) in exceptions {
                analyzeExceptionDomain(domain, config as? [String: Any] ?? [:])
            }
        }
    }

    /// 分析例外域名配置
    private func analyzeExceptionDomain(_ domain: String, _ config: [String: Any]) {
        // 检查NSExceptionAllowsInsecureHTTPLoads
        if let allowsInsecure = config["NSExceptionAllowsInsecureHTTPLoads"] as? Bool, allowsInsecure {
            results.add(SecurityFinding(
                tool: "ATS检查器",
                severity: .medium,
                title: "域名例外允许HTTP",
                description: "域名 '\(domain)' 配置了NSExceptionAllowsInsecureHTTPLoads=true，" +
                    "允许HTTP明文流量",
                recommendation: "移除例外配置，使用HTTPS",
                evidence: "domain=\(domain), NSExceptionAllowsInsecureHTTPLoads=true"
            ))
        }

        // 检查NSExceptionMinimumTLSVersion
        if let minTLS = config["NSExceptionMinimumTLSVersion"] as? String {
            if minTLS == "TLSv1.0" || minTLS == "TLSv1.1" {
                results.add(SecurityFinding(
                    tool: "ATS检查器",
                    severity: .medium,
                    title: "最低TLS版本过低",
                    description: "域名 '\(domain)' 的最低TLS版本为 \(minTLS)，" +
                        "TLS 1.0/1.1已不安全",
                    recommendation: "使用TLSv1.2或更高版本",
                    evidence: "domain=\(domain), minTLS=\(minTLS)"
                ))
            }
        }

        // 检查NSRequiresCertificateTransparency
        if let requiresCT = config["NSRequiresCertificateTransparency"] as? Bool, requiresCT {
            SecurityLogger.success("域名 '\(domain)' 要求证书透明度")
        }

        // 检查NSIncludesSubdomains
        if let includesSubdomains = config["NSIncludesSubdomains"] as? Bool, includesSubdomains {
            results.add(SecurityFinding(
                tool: "ATS检查器",
                severity: .low,
                title: "ATS例外包含子域名",
                description: "域名 '\(domain)' 的例外配置包含所有子域名",
                recommendation: "限制例外范围，仅对必要域名配置",
                evidence: "domain=\(domain), NSIncludesSubdomains=true"
            ))
        }
    }
}

// MARK: - 模块5：iOS剪贴板安全监控器

/// iOS剪贴板安全监控器
/// 监控和检查剪贴板的使用安全，防止敏感数据泄露
class PasteboardSecurityMonitor {

    private let results = ResultCollector()
    private var monitorTimer: Timer?
    private var lastChangeCount: Int = 0

    /// 开始监控剪贴板
    func startMonitoring(interval: TimeInterval = 1.0) {
        SecurityLogger.info("开始监控剪贴板...")

        lastChangeCount = UIPasteboard.general.changeCount

        monitorTimer = Timer.scheduledTimer(withTimeInterval: interval, repeats: true) { _ in
            self.checkPasteboard()
        }
    }

    /// 停止监控
    func stopMonitoring() {
        monitorTimer?.invalidate()
        monitorTimer = nil
        SecurityLogger.info("剪贴板监控已停止")
    }

    /// 检查剪贴板内容
    private func checkPasteboard() {
        let pasteboard = UIPasteboard.general

        // 检查changeCount是否有变化
        if pasteboard.changeCount == lastChangeCount {
            return
        }

        lastChangeCount = pasteboard.changeCount

        // 获取剪贴板内容
        if let content = pasteboard.string {
            checkSensitiveContent(content)
        }

        // 检查URL
        if let url = pasteboard.url {
            checkURLSecurity(url)
        }

        // 检查图片
        if let image = pasteboard.image {
            results.add(SecurityFinding(
                tool: "剪贴板监控器",
                severity: .info,
                title: "剪贴板包含图片",
                description: "剪贴板中包含图片数据，可能包含敏感信息（如截图）",
                recommendation: "敏感截图不应长时间留在剪贴板中",
                evidence: "image size: \(image.size)"
            ))
        }

        // 检查颜色（可能是密码管理器自动清除）
        if let color = pasteboard.color {
            SecurityLogger.info("剪贴板包含颜色数据（可能是密码管理器清除标记）")
        }
    }

    /// 检查敏感内容
    private func checkSensitiveContent(_ content: String) {
        // 敏感数据模式
        let patterns: [(String, String)] = [
            ("信用卡号", "\\b\\d{4}[\\s-]?\\d{4}[\\s-]?\\d{4}[\\s-]?\\d{4}\\b"),
            ("邮箱", "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}"),
            ("手机号", "\\b1[3-9]\\d{9}\\b"),
            ("JWT", "eyJ[A-Za-z0-9-_]+\\.[A-Za-z0-9-_]+\\.[A-Za-z0-9-_]+"),
            ("API密钥", "(?:api[_-]?key|secret[_-]?key)[=:][\\s]*[A-Za-z0-9]{20,}"),
            ("密码", "(?:password|passwd|pwd)[=:][\\s]*\\S+"),
            ("SSN", "\\b\\d{3}-\\d{2}-\\d{4}\\b"),
            ("IP地址", "\\b\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\b"),
            ("私钥", "-----BEGIN (?:RSA |EC )?PRIVATE KEY-----"),
        ]

        for (name, pattern) in patterns {
            if let regex = try? NSRegularExpression(pattern: pattern, options: .caseInsensitive) {
                let range = NSRange(content.startIndex..., in: content)
                if regex.firstMatch(in: content, options: [], range: range) != nil {
                    results.add(SecurityFinding(
                        tool: "剪贴板监控器",
                        severity: .high,
                        title: "剪贴板包含敏感数据: \(name)",
                        description: "检测到剪贴板中包含 \(name) 格式的数据",
                        recommendation: "敏感数据不应长时间留在剪贴板中，应自动清除",
                        evidence: "检测到 \(name) 格式数据"
                    ))
                }
            }
        }

        // 检查内容长度（可能是长文本如令牌）
        if content.count > 100 {
            results.add(SecurityFinding(
                tool: "剪贴板监控器",
                severity: .low,
                title: "剪贴板包含长文本",
                description: "剪贴板中包含 \(content.count) 字符的长文本，可能包含令牌或密钥",
                recommendation: "定期清除剪贴板内容",
                evidence: "内容长度: \(content.count)"
            ))
        }
    }

    /// 检查URL安全性
    private func checkURLSecurity(_ url: URL) {
        if url.scheme == "http" {
            results.add(SecurityFinding(
                tool: "剪贴板监控器",
                severity: .medium,
                title: "剪贴板包含HTTP URL",
                description: "剪贴板中包含HTTP明文URL: \(url.absoluteString)",
                recommendation: "使用HTTPS URL",
                evidence: url.absoluteString
            ))
        }

        // 检查是否是敏感URL
        let sensitivePaths = ["admin", "secret", "token", "key", "password", "auth"]
        let path = url.path.lowercased()
        for sensitive in sensitivePaths {
            if path.contains(sensitive) {
                results.add(SecurityFinding(
                    tool: "剪贴板监控器",
                    severity: .medium,
                    title: "剪贴板包含敏感路径URL",
                    description: "剪贴板中的URL路径包含敏感关键词: \(sensitive)",
                    recommendation: "不要复制敏感URL到剪贴板",
                    evidence: url.absoluteString
                ))
                break
            }
        }
    }

    /// 安全地清除剪贴板
    static func clearPasteboard() {
        UIPasteboard.general.items = []
        SecurityLogger.info("剪贴板已清除")
    }

    /// 延迟清除剪贴板（用于密码管理器）
    static func clearPasteboardAfterDelay(_ delay: TimeInterval = 30.0) {
        DispatchQueue.main.asyncAfter(deadline: .now() + delay) {
            clearPasteboard()
        }
    }
}

// MARK: - 模块6：URLSession安全配置

/// URLSession安全配置
/// 配置安全的网络请求，包括：
/// - TLS版本和密码套件
/// - 证书锁定
/// - Cookie安全
/// - 缓存安全
class URLSessionSecurityConfig {

    private let results = ResultCollector()

    /// 创建安全的URLSession配置
    func createSecureURLSession() -> URLSession {
        // 创建配置
        let config = URLSessionConfiguration.ephemeral // 不持久化

        // 安全配置
        config.httpCookieAcceptPolicy = .never // 不接受Cookie
        config.httpCookieStorage = nil // 不存储Cookie
        config.httpShouldSetCookies = false

        // 缓存配置
        config.urlCache = nil // 不缓存
        config.requestCachePolicy = .reloadIgnoringLocalAndRemoteCacheData

        // 超时设置
        config.timeoutIntervalForRequest = 30
        config.timeoutIntervalForResource = 60

        // 限制最大连接数
        config.httpMaximumConnectionsPerHost = 5

        // 创建安全委托
        let delegate = SecureURLSessionDelegate()
        let session = URLSession(configuration: config, delegate: delegate, delegateQueue: nil)

        return session
    }

    /// 检查URLSession安全配置
    func checkURLSessionSecurity() -> [SecurityFinding] {
        SecurityLogger.info("检查URLSession安全配置...")

        // 检查默认配置
        let defaultConfig = URLSessionConfiguration.default
        checkConfiguration(defaultConfig, name: "default")

        // 检查ephemeral配置
        let ephemeralConfig = URLSessionConfiguration.ephemeral
        checkConfiguration(ephemeralConfig, name: "ephemeral")

        SecurityLogger.info("URLSession安全配置检查完成")
        return results.findings
    }

    /// 检查单个配置
    private func checkConfiguration(_ config: URLSessionConfiguration, name: String) {
        // 检查Cookie存储
        if config.httpCookieStorage != nil {
            results.add(SecurityFinding(
                tool: "URLSession配置检查器",
                severity: .low,
                title: "\(name)配置使用Cookie存储",
                description: "URLSession配置 '\(name)' 使用了HTTPCookieStorage，" +
                    "Cookie可能被持久化存储",
                recommendation: "使用ephemeral配置或不存储Cookie",
                evidence: "\(name): httpCookieStorage != nil"
            ))
        }

        // 检查缓存
        if config.urlCache != nil {
            results.add(SecurityFinding(
                tool: "URLSession配置检查器",
                severity: .low,
                title: "\(name)配置使用URL缓存",
                description: "URLSession配置 '\(name)' 使用了URLCache，" +
                    "响应数据可能被缓存到磁盘",
                recommendation: "对于敏感数据，设置urlCache=nil",
                evidence: "\(name): urlCache != nil"
            ))
        }

        // 检查是否允许Cellular访问
        if config.allowsCellularAccess {
            results.add(SecurityFinding(
                tool: "URLSession配置检查器",
                severity: .info,
                title: "\(name)配置允许蜂窝网络访问",
                description: "URLSession配置 '\(name)' 允许蜂窝网络访问",
                recommendation: "敏感请求可考虑限制为WiFi",
                evidence: "\(name): allowsCellularAccess=true"
            ))
        }

        // 检查是否使用HTTP/2
        if !config.httpAdditionalHeaders.isEmpty {
            results.add(SecurityFinding(
                tool: "URLSession配置检查器",
                severity: .info,
                title: "\(name)配置包含额外HTTP头",
                description: "URLSession配置 '\(name)' 包含 \(config.httpAdditionalHeaders.count) 个额外HTTP头",
                recommendation: "检查额外头是否包含敏感信息",
                evidence: "\(name): \(config.httpAdditionalHeaders.keys)"
            ))
        }
    }

    /// 验证TLS配置
    func verifyTLSConfiguration(hostname: String) -> [SecurityFinding] {
        SecurityLogger.info("验证TLS配置: \(hostname)...")

        let url = URL(string: "https://\(hostname)")!
        let session = createSecureURLSession()

        let semaphore = DispatchSemaphore(value: 0)

        var findings: [SecurityFinding] = []

        let task = session.dataTask(with: url) { _, response, error in
            if let error = error {
                findings.append(SecurityFinding(
                    tool: "URLSession配置检查器",
                    severity: .high,
                    title: "TLS连接失败",
                    description: "连接 \(hostname) 失败: \(error.localizedDescription)",
                    recommendation: "检查TLS配置和证书有效性",
                    evidence: error.localizedDescription
                ))
            } else if let response = response as? HTTPURLResponse {
                let tlsVersion = response.value(forKey: "tlsVersion") as? String ?? "未知"
                findings.append(SecurityFinding(
                    tool: "URLSession配置检查器",
                    severity: .info,
                    title: "TLS连接成功",
                    description: "连接 \(hostname) 成功，TLS版本: \(tlsVersion)",
                    recommendation: "确保使用TLS 1.2或更高版本",
                    evidence: "TLS版本: \(tlsVersion), 状态码: \(response.statusCode)"
                ))
            }
            semaphore.signal()
        }

        task.resume()
        semaphore.wait()

        return findings
    }
}

/// 安全的URLSession委托
class SecureURLSessionDelegate: NSObject, URLSessionDelegate {

    /// 证书锁定哈希集合
    var pinnedCertificateHashes: Set<String> = []

    /// 验证服务器证书
    func urlSession(_ session: URLSession,
                     didReceive challenge: URLAuthenticationChallenge,
                     completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void) {

        // 处理服务器信任验证
        if challenge.protectionSpace.authenticationMethod == NSURLAuthenticationMethodServerTrust {
            guard let serverTrust = challenge.protectionSpace.serverTrust else {
                completionHandler(.cancelAuthenticationChallenge, nil)
                return
            }

            // 如果有证书锁定
            if !pinnedCertificateHashes.isEmpty {
                if let chain = SecTrustCopyCertificateChain(serverTrust) as? [SecCertificate] {
                    for cert in chain {
                        let hash = calculateCertificateHash(cert)
                        if pinnedCertificateHashes.contains(hash) {
                            // 匹配成功
                            completionHandler(.useCredential, URLCredential(trust: serverTrust))
                            return
                        }
                    }
                    // 未匹配 - 拒绝
                    completionHandler(.cancelAuthenticationChallenge, nil)
                    return
                }
            }

            // 默认验证（系统信任链）
            var error: CFError?
            if SecTrustEvaluateWithError(serverTrust, &error) {
                completionHandler(.useCredential, URLCredential(trust: serverTrust))
            } else {
                SecurityLogger.error("证书验证失败: \(error?.localizedDescription ?? "未知错误")")
                completionHandler(.cancelAuthenticationChallenge, nil)
            }
        } else {
            completionHandler(.performDefaultHandling, nil)
        }
    }

    /// 计算证书哈希
    private func calculateCertificateHash(_ certificate: SecCertificate) -> String {
        let data = SecCertificateCopyData(certificate) as Data
        let digest = Digest.sha256(data)
        return digest.base64EncodedString()
    }
}

// MARK: - 模块7：本地存储安全检查器

/// 本地存储安全检查器
/// 检查iOS本地存储的安全性，包括：
/// - NSUserDefaults
/// - CoreData
/// - Realm
/// - 文件存储
class LocalStorageSecurityChecker {

    private let results = ResultCollector()

    /// 检查所有本地存储
    func checkAllLocalStorage() -> [SecurityFinding] {
        SecurityLogger.info("开始本地存储安全检查...")

        checkUserDefaults()
        checkCoreData()
        checkRealm()
        checkFileStorage()

        SecurityLogger.info("本地存储安全检查完成")
        return results.findings
    }

    /// 检查UserDefaults安全
    private func checkUserDefaults() {
        let defaults = UserDefaults.standard

        // 获取所有键
        let allKeys = defaults.dictionaryRepresentation().keys

        // 敏感键名模式
        let sensitivePatterns = ["password", "token", "secret", "key", "credential",
                                  "auth", "session", "api", "private", "pin"]

        for key in allKeys {
            let keyLower = key.lowercased()
            for pattern in sensitivePatterns {
                if keyLower.contains(pattern) {
                    let value = defaults.object(forKey: key)
                    results.add(SecurityFinding(
                        tool: "本地存储检查器",
                        severity: .high,
                        title: "UserDefaults中存储敏感数据",
                        description: "UserDefaults中键 '\(key)' 包含敏感关键词 '\(pattern)'，" +
                            "可能存储了敏感数据",
                        recommendation: "敏感数据应使用Keychain存储，不应放在UserDefaults中",
                        evidence: "key=\(key), value_type=\(type(of: value))"
                    ))
                    break
                }
            }
        }

        // 检查UserDefaults是否为明文
        let prefsPath = NSHomeDirectory() + "/Library/Preferences/" +
            Bundle.main.bundleIdentifier! + ".plist"
        if FileManager.default.fileExists(atPath: prefsPath) {
            results.add(SecurityFinding(
                tool: "本地存储检查器",
                severity: .info,
                title: "UserDefaults为明文Plist",
                description: "UserDefaults存储在明文plist文件中: \(prefsPath)",
                recommendation: "了解UserDefaults不加密，敏感数据应使用Keychain",
                evidence: prefsPath
            ))
        }
    }

    /// 检查CoreData安全
    private func checkCoreData() {
        // 检查CoreData数据库文件
        let storePaths = [
            NSHomeDirectory() + "/Documents/",
            NSHomeDirectory() + "/Library/Application Support/"
        ]

        for path in storePaths {
            if let contents = try? FileManager.default.contentsOfDirectory(atPath: path) {
                for file in contents {
                    if file.hasSuffix(".sqlite") || file.hasSuffix(".db") {
                        let filePath = path + file
                        results.add(SecurityFinding(
                            tool: "本地存储检查器",
                            severity: .medium,
                            title: "发现CoreData/SQLite数据库",
                            description: "发现SQLite数据库文件: \(filePath)，" +
                                "可能包含敏感数据且未加密",
                            recommendation: "使用NSPersistentStoreCoordinator的加密选项，" +
                                "或使用SQLCipher",
                            evidence: filePath
                        ))

                        // 检查文件是否加密
                        if let attrs = try? FileManager.default.attributesOfItem(atPath: filePath),
                           let permissions = attrs[.posixPermissions] as? NSNumber {
                            let perm = String(permissions.int16Value, radix: 8)
                            results.add(SecurityFinding(
                                tool: "本地存储检查器",
                                severity: .low,
                                title: "数据库文件权限",
                                description: "数据库文件权限: \(perm)",
                                recommendation: "设置权限为0600（仅所有者可读写）",
                                evidence: "文件: \(file), 权限: \(perm)"
                            ))
                        }
                    }
                }
            }
        }

        // 检查是否使用了CoreData加密
        results.add(SecurityFinding(
            tool: "本地存储检查器",
            severity: .info,
            title: "CoreData加密检查",
            description: "需检查CoreData是否使用了加密存储：\n" +
                "  - NSPersistentStoreDescription是否设置了加密选项\n" +
                "  - 是否使用了CoreData + SQLCipher\n" +
                "  - 是否使用了NSFileProtectionComplete\n\n" +
                "  安全配置示例：\n" +
                "    description.setOption(FileProtectionType.complete as NSObject, " +
                "forKey: NSPersistentStoreFileProtectionKey)",
            recommendation: "使用FileProtectionType.complete保护CoreData数据",
            evidence: "需检查CoreData配置代码"
        ))
    }

    /// 检查Realm数据库安全
    private func checkRealm() {
        // 检查Realm数据库文件
        let realmPaths = [
            NSHomeDirectory() + "/Documents/default.realm",
            NSHomeDirectory() + "/Documents/realm/",
        ]

        for path in realmPaths {
            if FileManager.default.fileExists(atPath: path) {
                results.add(SecurityFinding(
                    tool: "本地存储检查器",
                    severity: .medium,
                    title: "发现Realm数据库",
                    description: "发现Realm数据库文件: \(path)，" +
                        "需检查是否启用了加密",
                    recommendation: "使用Realm加密：RealmConfiguration(encryptionKey: key)",
                    evidence: path
                ))
            }
        }

        // Realm安全检查清单
        results.add(SecurityFinding(
            tool: "本地存储检查器",
            severity: .info,
            title: "Realm安全检查清单",
            description: "Realm数据库安全检查：\n" +
                "  1. 是否使用了加密密钥\n" +
                "  2. 加密密钥是否存储在Keychain中\n" +
                "  3. 数据库文件是否设置了FileProtectionType\n" +
                "  4. 是否定期备份和验证密钥\n\n" +
                "  安全配置示例：\n" +
                "    let config = Realm.Configuration(\n" +
                "        encryptionKey: getKeyFromKeychain(),\n" +
                "        fileProtection: .complete\n" +
                "    )\n" +
                "    let realm = try! Realm(configuration: config)",
            recommendation: "使用Realm加密和FileProtectionType保护数据库",
            evidence: "需检查Realm配置代码"
        ))
    }

    /// 检查文件存储安全
    private func checkFileStorage() {
        let directories = [
            ("Documents", NSHomeDirectory() + "/Documents"),
            ("Library", NSHomeDirectory() + "/Library"),
            ("tmp", NSHomeDirectory() + "/tmp")
        ]

        for (name, path) in directories {
            if let contents = try? FileManager.default.contentsOfDirectory(atPath: path) {
                for file in contents {
                    let filePath = path + "/" + file

                    // 检查文件类型
                    if file.hasSuffix(".json") || file.hasSuffix(".xml") ||
                       file.hasSuffix(".txt") || file.hasSuffix(".plist") {
                        // 检查是否包含敏感数据
                        if let content = try? String(contentsOfFile: filePath, encoding: .utf8) {
                            checkFileContentForSensitiveData(filePath, content, file)
                        }
                    }

                    // 检查文件保护属性
                    checkFileProtection(filePath, file)
                }
            }
        }
    }

    /// 检查文件内容是否包含敏感数据
    private func checkFileContentForSensitiveData(_ filePath: String, _ content: String, _ fileName: String) {
        let sensitiveKeywords = ["password", "token", "secret", "key", "credential",
                                 "auth", "session", "api_key", "private"]

        let contentLower = content.lowercased()
        for keyword in sensitiveKeywords {
            if contentLower.contains(keyword) {
                results.add(SecurityFinding(
                    tool: "本地存储检查器",
                    severity: .high,
                    title: "文件中包含敏感数据",
                    description: "文件 '\(fileName)' 的内容包含敏感关键词 '\(keyword)'",
                    recommendation: "敏感数据应加密存储或使用Keychain",
                    evidence: "文件: \(filePath), 关键词: \(keyword)"
                ))
                break
            }
        }
    }

    /// 检查文件保护属性
    private func checkFileProtection(_ filePath: String, _ fileName: String) {
        if let attrs = try? FileManager.default.attributesOfItem(atPath: filePath) {
            // 检查文件保护类型
            if let protection = attrs[.protectionKey] as? FileProtectionType {
                switch protection {
                case .none:
                    results.add(SecurityFinding(
                        tool: "本地存储检查器",
                        severity: .medium,
                        title: "文件无保护",
                        description: "文件 '\(fileName)' 没有设置文件保护类型，" +
                            "设备锁定后文件仍可被访问",
                        recommendation: "设置FileProtectionType.complete或.completeUnlessOpen",
                        evidence: "文件: \(filePath), 保护: 无"
                    ))
                case .complete:
                    SecurityLogger.success("文件 '\(fileName)' 使用了complete保护")
                case .completeUnlessOpen:
                    SecurityLogger.success("文件 '\(fileName)' 使用了completeUnlessOpen保护")
                default:
                    results.add(SecurityFinding(
                        tool: "本地存储检查器",
                        severity: .low,
                        title: "文件保护类型较弱",
                        description: "文件 '\(fileName)' 的保护类型为 \(protection.rawValue)",
                        recommendation: "考虑使用.complete或.completeUnlessOpen保护",
                        evidence: "文件: \(filePath), 保护: \(protection.rawValue)"
                    ))
                }
            } else {
                results.add(SecurityFinding(
                    tool: "本地存储检查器",
                    severity: .medium,
                    title: "文件未设置保护类型",
                    description: "文件 '\(fileName)' 未设置FileProtectionType",
                    recommendation: "设置文件保护类型为.complete",
                    evidence: "文件: \(filePath), 保护: 未设置"
                ))
            }
        }
    }
}

// MARK: - 主入口

/// iOS安全工具集主类
class IOSSecurityToolkit {

    static func runAllChecks() {
        print("=".repeating(60))
        print("  iOS安全工具集 v1.0")
        print("  综合iOS应用安全分析工具")
        print("=".repeating(60))

        let allResults = ResultCollector()

        // 1. Keychain分析
        print("\n[1] Keychain访问分析")
        let keychainAnalyzer = KeychainAccessAnalyzer()
        allResults.findings.append(contentsOf: keychainAnalyzer.analyzeKeychainSecurity())

        // 2. 沙盒检测
        print("\n[2] 沙盒环境检测")
        let sandboxDetector = SandboxDetector()
        allResults.findings.append(contentsOf: sandboxDetector.detectSandboxEnvironment())

        // 3. 代码签名验证
        print("\n[3] 代码签名验证")
        let codeSignVerifier = CodeSignatureVerifier()
        allResults.findings.append(contentsOf: codeSignVerifier.verifyCodeSignature())

        // 4. ATS检查
        print("\n[4] ATS配置检查")
        let atsChecker = ATSChecker()
        allResults.findings.append(contentsOf: atsChecker.checkATSConfiguration())

        // 5. 剪贴板监控
        print("\n[5] 剪贴板安全")
        let pasteboardMonitor = PasteboardSecurityMonitor()
        pasteboardMonitor.startMonitoring()
        // 监控5秒
        Thread.sleep(forTimeInterval: 5)
        pasteboardMonitor.stopMonitoring()

        // 6. URLSession配置
        print("\n[6] URLSession安全配置")
        let urlSessionChecker = URLSessionSecurityConfig()
        allResults.findings.append(contentsOf: urlSessionChecker.checkURLSessionSecurity())

        // 7. 本地存储检查
        print("\n[7] 本地存储安全检查")
        let storageChecker = LocalStorageSecurityChecker()
        allResults.findings.append(contentsOf: storageChecker.checkAllLocalStorage())

        // 打印结果
        print("\n" + "=".repeating(60))
        print("  安全分析报告")
        print("=".repeating(60))
        print(allResults.summary())
        print("=".repeating(60))

        for finding in allResults.findings {
            print(finding.description())
        }

        print("\n免责声明: 仅用于授权的安全测试！")
    }
}

// MARK: - String扩展
extension String {
    func repeating(_ n: Int) -> String {
        return String(repeating: self, count: n)
    }
}

// MARK: - Digest工具（简化版）
struct Digest {
    static func sha256(_ data: Data) -> Data {
        var hash = [UInt8](repeating: 0, count: 32)
        data.withUnsafeBytes { buffer in
            _ = CC_SHA256(buffer.baseAddress, CC_LONG(data.count), &hash)
        }
        return Data(hash)
    }
}

import CommonCrypto

// MARK: - 主函数
// IOSSecurityToolkit.runAllChecks()
