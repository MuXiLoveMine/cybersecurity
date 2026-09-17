import java.io.*;
import java.util.*;
import java.util.regex.*;
import java.util.zip.*;
import java.security.*;
import javax.xml.parsers.*;
import javax.xml.xpath.*;
import org.w3c.dom.*;
import org.xml.sax.*;

/**
 * Android安全工具集 - 综合Android应用安全分析工具
 *
 * 功能模块：
 * 1. 组件导出检查器（Activity/Service/Receiver/Provider）
 * 2. Intent安全分析器
 * 3. 权限分析器
 * 4. AndroidManifest.xml安全扫描器
 * 5. APK元数据提取器
 * 6. Shared Preferences安全检查器
 * 7. ContentProvider URI测试器
 * 8. WebView安全分析器
 *
 * 使用方法：
 *   java android_security_tools <command> [options]
 *   java android_security_tools manifest -f AndroidManifest.xml
 *   java android_security_tools apk -f app.apk
 *   java android_security_tools component -f AndroidManifest.xml
 *   java android_security_tools permission -f AndroidManifest.xml
 *   java android_security_tools webview -f AndroidManifest.xml
 *   java android_security_tools all -f app.apk
 *
 * 免责声明：仅用于授权的安全测试，未经授权分析他人应用属于违法行为。
 *
 * @author CyberSecurity Study
 * @version 1.0
 */
public class android_security_tools {

    // ========================================================================
    // 全局配置与工具方法
    // ========================================================================

    /** 安全配置常量 */
    public static class SecurityConfig {
        // 危险权限列表
        public static final String[] DANGEROUS_PERMISSIONS = {
            "android.permission.READ_SMS",
            "android.permission.SEND_SMS",
            "android.permission.RECEIVE_SMS",
            "android.permission.READ_CONTACTS",
            "android.permission.WRITE_CONTACTS",
            "android.permission.READ_CALL_LOG",
            "android.permission.WRITE_CALL_LOG",
            "android.permission.CAMERA",
            "android.permission.RECORD_AUDIO",
            "android.permission.ACCESS_FINE_LOCATION",
            "android.permission.ACCESS_COARSE_LOCATION",
            "android.permission.READ_EXTERNAL_STORAGE",
            "android.permission.WRITE_EXTERNAL_STORAGE",
            "android.permission.READ_PHONE_STATE",
            "android.permission.CALL_PHONE",
            "android.permission.ANSWER_PHONE_CALLS",
            "android.permission.READ_PHONE_NUMBERS",
            "android.permission.BODY_SENSORS",
            "android.permission.ACTIVITY_RECOGNITION",
            "android.permission.READ_CALENDAR",
            "android.permission.WRITE_CALENDAR",
            "android.permission.READ_CELL_BROADCASTS",
            "android.permission.USE_BIOMETRIC",
            "android.permission.USE_FINGERPRINT",
            "android.permission.SYSTEM_ALERT_WINDOW",
            "android.permission.REQUEST_INSTALL_PACKAGES",
            "android.permission.QUERY_ALL_PACKAGES",
        };

        // 签名权限（可被自定义权限声明绕过）
        public static final String[] SIGNATURE_PERMISSIONS = {
            "android.permission.BIND_DEVICE_ADMIN",
            "android.permission.BIND_ACCESSIBILITY_SERVICE",
            "android.permission.BIND_INPUT_METHOD",
            "android.permission.BIND_NOTIFICATION_LISTENER_SERVICE",
            "android.permission.BIND_PRINT_SERVICE",
            "android.permission.BIND_VR_LISTENER_SERVICE",
            "android.permission.BIND_TV_INPUT",
        };

        // 不安全的WebView设置
        public static final String[] UNSAFE_WEBVIEW_SETTINGS = {
            "setJavaScriptEnabled(true)",
            "setAllowFileAccess(true)",
            "setAllowFileAccessFromFileURLs(true)",
            "setAllowUniversalAccessFromFileURLs(true)",
            "setAllowContentAccess(true)",
            "setDomStorageEnabled(true)",
            "setMixedContentMode(0)", // MIXED_CONTENT_ALWAYS_ALLOW
            "addJavascriptInterface",
            "setSavePassword(true)",
        };

        // 敏感Intent Action
        public static final String[] SENSITIVE_ACTIONS = {
            "android.intent.action.VIEW",
            "android.intent.action.SEND",
            "android.intent.action.SENDTO",
            "android.intent.action.CALL",
            "android.intent.action.DIAL",
            "android.intent.action.PICK",
            "android.intent.action.GET_CONTENT",
            "android.intent.action.INSERT",
            "android.intent.action.DELETE",
            "android.intent.action.EDIT",
        };

        // 允许备份的标记
        public static final String ALLOW_BACKUP_FLAG = "android:allowBackup";

        // 调试标记
        public static final String DEBUGGABLE_FLAG = "android:debuggable";
    }

    /** 安全等级枚举 */
    public enum Severity {
        CRITICAL("严重"),
        HIGH("高危"),
        MEDIUM("中危"),
        LOW("低危"),
        INFO("信息");

        private final String label;
        Severity(String label) { this.label = label; }
        public String getLabel() { return label; }
    }

    /** 安全发现结果类 */
    public static class SecurityFinding {
        String toolName;
        Severity severity;
        String title;
        String description;
        String recommendation;
        String component;
        String evidence;

        public SecurityFinding(String toolName, Severity severity, String title,
                               String description, String recommendation,
                               String component, String evidence) {
            this.toolName = toolName;
            this.severity = severity;
            this.title = title;
            this.description = description;
            this.recommendation = recommendation;
            this.component = component;
            this.evidence = evidence;
        }

        @Override
        public String toString() {
            StringBuilder sb = new StringBuilder();
            sb.append("[").append(severity.getLabel()).append("] ");
            sb.append(title).append("\n");
            sb.append("  工具: ").append(toolName).append("\n");
            sb.append("  组件: ").append(component).append("\n");
            sb.append("  描述: ").append(description).append("\n");
            sb.append("  证据: ").append(evidence).append("\n");
            sb.append("  建议: ").append(recommendation).append("\n");
            return sb.toString();
        }
    }

    /** 全局结果收集器 */
    public static class ResultCollector {
        private List<SecurityFinding> findings = new ArrayList<>();
        private Map<String, Integer> severityCount = new LinkedHashMap<>();

        public ResultCollector() {
            for (Severity s : Severity.values()) {
                severityCount.put(s.name(), 0);
            }
        }

        public void addFinding(SecurityFinding finding) {
            findings.add(finding);
            severityCount.put(finding.severity.name(),
                severityCount.get(finding.severity.name()) + 1);
        }

        public void printSummary() {
            System.out.println("\n" + "=".repeat(60));
            System.out.println("  Android安全分析报告");
            System.out.println("=".repeat(60));
            System.out.println("  总发现数: " + findings.size());
            for (Map.Entry<String, Integer> entry : severityCount.entrySet()) {
                if (entry.getValue() > 0) {
                    System.out.println("  " + Severity.valueOf(entry.getKey()).getLabel()
                        + ": " + entry.getValue());
                }
            }
            System.out.println("=".repeat(60));
        }

        public void printDetails() {
            System.out.println("\n--- 详细发现 ---\n");
            // 按严重程度排序
            findings.sort(Comparator.comparingInt(f -> f.severity.ordinal()));
            for (SecurityFinding finding : findings) {
                System.out.println(finding.toString());
            }
        }

        public List<SecurityFinding> getFindings() { return findings; }
    }

    // ========================================================================
    // 模块1：组件导出检查器
    // ========================================================================

    /**
     * 组件导出检查器
     * 检查Activity/Service/Receiver/Provider的导出状态和权限保护
     */
    public static class ComponentExportChecker {
        private Document manifestDoc;
        private ResultCollector results;

        public ComponentExportChecker(Document manifest, ResultCollector results) {
            this.manifestDoc = manifest;
            this.results = results;
        }

        /**
         * 检查所有组件的导出状态
         */
        public void checkAllComponents() {
            System.out.println("\n[*] 开始组件导出检查...");

            checkActivities();
            checkServices();
            checkReceivers();
            checkProviders();

            System.out.println("[*] 组件导出检查完成");
        }

        /**
         * 检查Activity组件
         */
        private void checkActivities() {
            NodeList activities = manifestDoc.getElementsByTagName("activity");
            for (int i = 0; i < activities.getLength(); i++) {
                Element activity = (Element) activities.item(i);
                String name = activity.getAttribute("android:name");
                boolean exported = "true".equals(activity.getAttribute("android:exported"));
                String permission = activity.getAttribute("android:permission");

                // 检查带有intent-filter的组件默认导出（targetSdkVersion < 31）
                boolean hasIntentFilter = activity.getElementsByTagName("intent-filter").getLength() > 0;

                checkComponentSecurity("Activity", name, exported, hasIntentFilter, permission);
            }
        }

        /**
         * 检查Service组件
         */
        private void checkServices() {
            NodeList services = manifestDoc.getElementsByTagName("service");
            for (int i = 0; i < services.getLength(); i++) {
                Element service = (Element) services.item(i);
                String name = service.getAttribute("android:name");
                boolean exported = "true".equals(service.getAttribute("android:exported"));
                String permission = service.getAttribute("android:permission");

                boolean hasIntentFilter = service.getElementsByTagName("intent-filter").getLength() > 0;

                checkComponentSecurity("Service", name, exported, hasIntentFilter, permission);

                // 检查Service特有的安全问题
                checkServiceSpecific(service, name);
            }
        }

        /**
         * 检查BroadcastReceiver组件
         */
        private void checkReceivers() {
            NodeList receivers = manifestDoc.getElementsByTagName("receiver");
            for (int i = 0; i < receivers.getLength(); i++) {
                Element receiver = (Element) receivers.item(i);
                String name = receiver.getAttribute("android:name");
                boolean exported = "true".equals(receiver.getAttribute("android:exported"));
                String permission = receiver.getAttribute("android:permission");

                boolean hasIntentFilter = receiver.getElementsByTagName("intent-filter").getLength() > 0;

                checkComponentSecurity("Receiver", name, exported, hasIntentFilter, permission);
            }
        }

        /**
         * 检查ContentProvider组件
         */
        private void checkProviders() {
            NodeList providers = manifestDoc.getElementsByTagName("provider");
            for (int i = 0; i < providers.getLength(); i++) {
                Element provider = (Element) providers.item(i);
                String name = provider.getAttribute("android:name");
                boolean exported = "true".equals(provider.getAttribute("android:exported"));
                String permission = provider.getAttribute("android:permission");
                String readPermission = provider.getAttribute("android:readPermission");
                String writePermission = provider.getAttribute("android:writePermission");
                String authorities = provider.getAttribute("android:authorities");
                String grantUriPermission = provider.getAttribute("android:grantUriPermissions");

                checkComponentSecurity("Provider", name, exported, false, permission);

                // 检查Provider特有的安全问题
                checkProviderSpecific(name, exported, readPermission, writePermission,
                    authorities, grantUriPermission);
            }
        }

        /**
         * 检查单个组件的安全状态
         */
        private void checkComponentSecurity(String type, String name, boolean exported,
                                            boolean hasIntentFilter, String permission) {
            if (exported && (permission == null || permission.isEmpty())) {
                // 导出但无权限保护
                results.addFinding(new SecurityFinding(
                    "组件导出检查器",
                    Severity.HIGH,
                    type + "导出且无权限保护",
                    type + "组件 '" + name + "' 被导出但未设置权限保护，" +
                        "任何应用都可以调用此组件",
                    "设置android:permission属性，限制调用者权限；" +
                        "或设置android:exported='false'取消导出",
                    name,
                    "exported=true, permission=(空)"
                ));
            }

            if (exported && hasIntentFilter && permission != null && !permission.isEmpty()) {
                // 导出且有intent-filter和权限 - 检查权限级别
                if (isDangerousPermission(permission)) {
                    results.addFinding(new SecurityFinding(
                        "组件导出检查器",
                        Severity.MEDIUM,
                        type + "使用危险权限保护",
                        type + "组件 '" + name + "' 使用危险权限 '" + permission + "' 保护，" +
                            "可能被同权限应用绕过",
                        "使用签名级别权限保护敏感组件",
                        name,
                        "permission=" + permission
                    ));
                }
            }

            // 检查是否使用了自定义权限但未定义
            if (permission != null && !permission.isEmpty()
                && !permission.startsWith("android.permission")) {
                // 检查是否在manifest中定义了该权限
                NodeList permDefs = manifestDoc.getElementsByTagName("permission");
                boolean defined = false;
                for (int i = 0; i < permDefs.getLength(); i++) {
                    Element permDef = (Element) permDefs.item(i);
                    if (permission.equals(permDef.getAttribute("android:name"))) {
                        defined = true;
                        break;
                    }
                }
                if (!defined) {
                    results.addFinding(new SecurityFinding(
                        "组件导出检查器",
                        Severity.MEDIUM,
                        type + "使用未定义的自定义权限",
                        type + "组件 '" + name + "' 使用自定义权限 '" + permission + "' " +
                            "但该权限未在应用中定义",
                        "在AndroidManifest.xml中定义<permission>标签",
                        name,
                        "自定义权限未定义: " + permission
                    ));
                }
            }
        }

        /**
         * 检查Service特有安全问题
         */
        private void checkServiceSpecific(Element service, String name) {
            // 检查前台服务类型
            String foregroundServiceType = service.getAttribute("android:foregroundServiceType");

            // 检查是否是bindService但未要求权限
            if ("true".equals(service.getAttribute("android:exported"))) {
                NodeList intentFilters = service.getElementsByTagName("intent-filter");
                for (int i = 0; i < intentFilters.getLength(); i++) {
                    Element filter = (Element) intentFilters.item(i);
                    NodeList actions = filter.getElementsByTagName("action");
                    for (int j = 0; j < actions.getLength(); j++) {
                        Element action = (Element) actions.item(j);
                        String actionName = action.getAttribute("android:name");
                        // 检查是否有绑定的权限
                        if (service.getAttribute("android:permission").isEmpty()) {
                            results.addFinding(new SecurityFinding(
                                "组件导出检查器",
                                Severity.HIGH,
                                "Service可被任意绑定",
                                "Service '" + name + "' 导出且可被任意应用绑定，" +
                                    "可能导致权限提升或数据泄露",
                                "为Service设置android:permission属性",
                                name,
                                "exported=true, action=" + actionName + ", no permission"
                            ));
                        }
                    }
                }
            }
        }

        /**
         * 检查ContentProvider特有安全问题
         */
        private void checkProviderSpecific(String name, boolean exported,
                                           String readPerm, String writePerm,
                                           String authorities, String grantUriPerm) {
            // 检查导出的Provider是否缺少读写权限
            if (exported) {
                boolean hasReadPerm = readPerm != null && !readPerm.isEmpty();
                boolean hasWritePerm = writePerm != null && !writePerm.isEmpty();
                boolean hasGeneralPerm = name != null; // 检查通用权限

                if (!hasReadPerm && !hasWritePerm) {
                    results.addFinding(new SecurityFinding(
                        "组件导出检查器",
                        Severity.HIGH,
                        "ContentProvider导出无权限保护",
                        "ContentProvider '" + name + "' 被导出但未设置读写权限，" +
                            "任何应用都可读写其数据",
                        "设置android:readPermission和android:writePermission",
                        name,
                        "exported=true, authorities=" + authorities
                    ));
                }

                // 检查grantUriPermissions
                if ("true".equals(grantUriPerm)) {
                    results.addFinding(new SecurityFinding(
                        "组件导出检查器",
                        Severity.MEDIUM,
                        "ContentProvider启用URI权限授予",
                        "ContentProvider '" + name + "' 启用了grantUriPermissions，" +
                            "可能导致URI权限绕过",
                        "仅在必要时启用grantUriPermissions，并验证URI路径",
                        name,
                        "grantUriPermissions=true"
                    ));
                }

                // 检查是否暴露了敏感数据路径
                if (authorities != null && !authorities.isEmpty()) {
                    checkProviderURIs(name, authorities);
                }
            }
        }

        /**
         * 检查Provider的URI路径安全性
         */
        private void checkProviderURIs(String providerName, String authorities) {
            // 检查常见的敏感URI路径
            String[] sensitivePaths = {
                "user_data", "account", "password", "token", "session",
                "credential", "secret", "key", "config", "settings",
                "contacts", "sms", "call_log", "location", "history"
            };

            // 注意：这里仅检查authorities名称是否暗示敏感数据
            String authoritiesLower = authorities.toLowerCase();
            for (String sensitive : sensitivePaths) {
                if (authoritiesLower.contains(sensitive)) {
                    results.addFinding(new SecurityFinding(
                        "组件导出检查器",
                        Severity.MEDIUM,
                        "ContentProvider可能暴露敏感数据",
                        "ContentProvider '" + providerName + "' 的authorities包含敏感关键词 '" +
                            sensitive + "'，可能暴露敏感数据",
                        "审查Provider暴露的数据路径，确保不包含敏感信息",
                        providerName,
                        "authorities=" + authorities
                    ));
                    break;
                }
            }
        }

        /**
         * 判断是否为危险权限
         */
        private boolean isDangerousPermission(String permission) {
            for (String dangerous : SecurityConfig.DANGEROUS_PERMISSIONS) {
                if (dangerous.equals(permission)) {
                    return true;
                }
            }
            return false;
        }
    }

    // ========================================================================
    // 模块2：Intent安全分析器
    // ========================================================================

    /**
     * Intent安全分析器
     * 分析Intent的使用是否安全，包括隐式Intent、PendingIntent等
     */
    public static class IntentSecurityAnalyzer {
        private Document manifestDoc;
        private ResultCollector results;

        public IntentSecurityAnalyzer(Document manifest, ResultCollector results) {
            this.manifestDoc = manifest;
            this.results = results;
        }

        /**
         * 分析Intent-filter安全
         */
        public void analyzeIntentFilters() {
            System.out.println("\n[*] 开始Intent安全分析...");

            // 检查所有组件的intent-filter
            String[] componentTypes = {"activity", "service", "receiver"};
            for (String type : componentTypes) {
                NodeList components = manifestDoc.getElementsByTagName(type);
                for (int i = 0; i < components.getLength(); i++) {
                    Element component = (Element) components.item(i);
                    String componentName = component.getAttribute("android:name");

                    NodeList filters = component.getElementsByTagName("intent-filter");
                    for (int j = 0; j < filters.getLength(); j++) {
                        Element filter = (Element) filters.item(j);
                        analyzeSingleFilter(type, componentName, filter);
                    }
                }
            }

            // 检查PendingIntent使用
            checkPendingIntentPatterns();

            // 检查隐式Intent使用
            checkImplicitIntentPatterns();

            System.out.println("[*] Intent安全分析完成");
        }

        /**
         * 分析单个intent-filter
         */
        private void analyzeSingleFilter(String componentType, String componentName,
                                         Element filter) {
            NodeList actions = filter.getElementsByTagName("action");
            NodeList categories = filter.getElementsByTagName("category");
            NodeList dataElements = filter.getElementsByTagName("data");

            boolean exported = "true".equals(
                ((Element) filter.getParentNode()).getAttribute("android:exported"));

            // 检查敏感Action
            for (int i = 0; i < actions.getLength(); i++) {
                Element action = (Element) actions.item(i);
                String actionName = action.getAttribute("android:name");

                for (String sensitive : SecurityConfig.SENSITIVE_ACTIONS) {
                    if (sensitive.equals(actionName) && exported) {
                        results.addFinding(new SecurityFinding(
                            "Intent安全分析器",
                            Severity.MEDIUM,
                            "导出组件注册敏感Action",
                            componentType + " '" + componentName + "' 注册了敏感Action '" +
                                actionName + "' 且被导出",
                            "确保导出组件的Action处理逻辑安全，验证输入数据",
                            componentName,
                            "action=" + actionName + ", exported=true"
                        ));
                    }
                }

                // 检查自定义Action是否需要权限保护
                if (!actionName.startsWith("android.") && exported) {
                    String permission = ((Element) filter.getParentNode())
                        .getAttribute("android:permission");
                    if (permission == null || permission.isEmpty()) {
                        results.addFinding(new SecurityFinding(
                            "Intent安全分析器",
                            Severity.LOW,
                            "自定义Action无权限保护",
                            "组件 '" + componentName + "' 注册自定义Action '" + actionName +
                                "' 且导出但无权限保护",
                            "为自定义Action的组件设置权限保护",
                            componentName,
                            "action=" + actionName
                        ));
                    }
                }
            }

            // 检查data scheme安全
            for (int i = 0; i < dataElements.getLength(); i++) {
                Element data = (Element) dataElements.item(i);
                String scheme = data.getAttribute("android:scheme");
                String host = data.getAttribute("android:host");
                String pathPattern = data.getAttribute("android:pathPattern");

                // 检查不安全的scheme
                if ("http".equals(scheme) && exported) {
                    results.addFinding(new SecurityFinding(
                        "Intent安全分析器",
                        Severity.LOW,
                        "导出组件接受HTTP scheme",
                        componentType + " '" + componentName + "' 接受HTTP明文scheme，" +
                            "可能遭受中间人攻击",
                        "使用HTTPS scheme替代HTTP",
                        componentName,
                        "scheme=http, exported=true"
                    ));
                }

                // 检查deep link的安全性
                if (scheme != null && !scheme.isEmpty() && exported) {
                    checkDeepLinkSecurity(componentName, scheme, host, pathPattern);
                }
            }
        }

        /**
         * 检查Deep Link安全
         */
        private void checkDeepLinkSecurity(String component, String scheme,
                                           String host, String pathPattern) {
            // 检查scheme是否过于通用
            if ("http".equals(scheme) || "https".equals(scheme)) {
                if (host == null || host.isEmpty()) {
                    results.addFinding(new SecurityFinding(
                        "Intent安全分析器",
                        Severity.MEDIUM,
                        "Deep Link配置不完整",
                        "组件 '" + component + "' 注册了HTTP/HTTPS scheme但未指定host，" +
                            "可能劫持任意URL",
                        "指定明确的host参数，限制Deep Link范围",
                        component,
                        "scheme=" + scheme + ", host=(空)"
                    ));
                }
            }

            // 检查自定义scheme是否可被其他应用劫持
            if (!"http".equals(scheme) && !"https".equals(scheme)
                && !"content".equals(scheme) && !"file".equals(scheme)) {
                results.addFinding(new SecurityFinding(
                    "Intent安全分析器",
                    Severity.LOW,
                    "自定义scheme可被劫持",
                    "组件 '" + component + "' 使用自定义scheme '" + scheme + "'，" +
                        "其他应用可注册相同scheme劫持Intent",
                    "验证scheme唯一性，使用host参数增加确定性",
                    component,
                    "scheme=" + scheme
                ));
            }

            // 检查pathPattern是否使用通配符
            if (pathPattern != null && pathPattern.contains(".*")) {
                results.addFinding(new SecurityFinding(
                    "Intent安全分析器",
                    Severity.LOW,
                    "Deep Link使用通配符路径",
                    "组件 '" + component + "' 的Deep Link使用通配符路径 '" + pathPattern + "'，" +
                        "可能匹配非预期URL",
                    "使用精确路径或限制通配符范围",
                    component,
                    "pathPattern=" + pathPattern
                ));
            }
        }

        /**
         * 检查PendingIntent使用模式
         */
        private void checkPendingIntentPatterns() {
            // 注意：实际代码扫描需要在Java/Smali层面进行
            // 这里提供检查框架
            results.addFinding(new SecurityFinding(
                "Intent安全分析器",
                Severity.INFO,
                "PendingIntent安全检查提示",
                "需检查代码中PendingIntent的使用是否安全：\n" +
                    "  - 是否使用FLAG_IMMUTABLE\n" +
                    "  - 是否使用FLAG_UPDATE_CURRENT\n" +
                    "  - PendingIntent的基Intent是否为显式Intent\n" +
                    "  - 是否使用getActivity/getService/getBroadcast的安全重载",
                "使用FLAG_IMMUTABLE创建PendingIntent，使用显式Intent",
                "PendingIntent",
                "需扫描Java/Smali代码"
            ));
        }

        /**
         * 检查隐式Intent使用模式
         */
        private void checkImplicitIntentPatterns() {
            results.addFinding(new SecurityFinding(
                "Intent安全分析器",
                Severity.INFO,
                "隐式Intent安全检查提示",
                "需检查代码中隐式Intent的使用：\n" +
                    "  - 发送隐式Intent可能导致 Intent劫持\n" +
                    "  - 发送广播使用sendBroadcast可能被窃听\n" +
                    "  - 建议使用LocalBroadcastManager或显式Intent\n" +
                    "  - 敏感数据不应通过隐式Intent传递",
                "使用显式Intent，敏感数据通过安全通道传输",
                "隐式Intent",
                "需扫描Java/Smali代码"
            ));
        }
    }

    // ========================================================================
    // 模块3：权限分析器
    // ========================================================================

    /**
     * 权限分析器
     * 分析应用申请的权限是否合理，检查权限保护级别
     */
    public static class PermissionAnalyzer {
        private Document manifestDoc;
        private ResultCollector results;

        public PermissionAnalyzer(Document manifest, ResultCollector results) {
            this.manifestDoc = manifest;
            this.results = results;
        }

        /**
         * 分析所有权限
         */
        public void analyzePermissions() {
            System.out.println("\n[*] 开始权限分析...");

            analyzeDeclaredPermissions();
            analyzeUsedPermissions();
            analyzePermissionProtectionLevel();

            System.out.println("[*] 权限分析完成");
        }

        /**
         * 分析声明的权限
         */
        private void analyzeDeclaredPermissions() {
            NodeList permissions = manifestDoc.getElementsByTagName("uses-permission");
            Set<String> declaredSet = new HashSet<>();
            List<String> dangerousList = new ArrayList<>();

            for (int i = 0; i < permissions.getLength(); i++) {
                Element perm = (Element) permissions.item(i);
                String permName = perm.getAttribute("android:name");
                declaredSet.add(permName);

                // 检查危险权限
                for (String dangerous : SecurityConfig.DANGEROUS_PERMISSIONS) {
                    if (dangerous.equals(permName)) {
                        dangerousList.add(permName);
                        break;
                    }
                }
            }

            // 报告危险权限
            if (!dangerousList.isEmpty()) {
                results.addFinding(new SecurityFinding(
                    "权限分析器",
                    Severity.MEDIUM,
                    "应用申请危险权限",
                    "应用申请了 " + dangerousList.size() + " 个危险权限：\n" +
                        String.join("\n", dangerousList),
                    "审查每个危险权限的使用必要性，移除不需要的权限",
                    "uses-permission",
                    "危险权限: " + String.join(", ", dangerousList)
                ));
            }

            System.out.println("  申请权限总数: " + declaredSet.size());
            System.out.println("  危险权限数量: " + dangerousList.size());
        }

        /**
         * 分析权限使用情况
         */
        private void analyzeUsedPermissions() {
            // 检查自定义权限定义
            NodeList customPerms = manifestDoc.getElementsByTagName("permission");
            for (int i = 0; i < customPerms.getLength(); i++) {
                Element perm = (Element) customPerms.item(i);
                String name = perm.getAttribute("android:name");
                String protectionLevel = perm.getAttribute("android:protectionLevel");

                // 检查保护级别
                if (protectionLevel == null || protectionLevel.isEmpty()) {
                    protectionLevel = "normal"; // 默认
                }

                if ("normal".equals(protectionLevel)) {
                    results.addFinding(new SecurityFinding(
                        "权限分析器",
                        Severity.MEDIUM,
                        "自定义权限保护级别过低",
                        "自定义权限 '" + name + "' 的保护级别为 'normal'，" +
                            "任何应用都可声明此权限",
                        "将敏感自定义权限的保护级别设为 'signature'",
                        name,
                        "protectionLevel=normal"
                    ));
                }

                // 检查signature权限是否正确配置
                if ("signature".equals(protectionLevel) || "signatureOrSystem".equals(protectionLevel)) {
                    // signature级别是安全的
                }
            }
        }

        /**
         * 分析权限保护级别
         */
        private void analyzePermissionProtectionLevel() {
            // 检查组件权限与声明的权限是否匹配
            NodeList components = manifestDoc.getElementsByTagName("*");
            Set<String> usedPermissions = new HashSet<>();

            // 收集所有组件使用的权限
            String[] componentTags = {"activity", "service", "receiver", "provider"};
            for (String tag : componentTags) {
                NodeList nodes = manifestDoc.getElementsByTagName(tag);
                for (int i = 0; i < nodes.getLength(); i++) {
                    Element comp = (Element) nodes.item(i);
                    String perm = comp.getAttribute("android:permission");
                    String readPerm = comp.getAttribute("android:readPermission");
                    String writePerm = comp.getAttribute("android:writePermission");

                    if (perm != null && !perm.isEmpty()) usedPermissions.add(perm);
                    if (readPerm != null && !readPerm.isEmpty()) usedPermissions.add(readPerm);
                    if (writePerm != null && !writePerm.isEmpty()) usedPermissions.add(writePerm);
                }
            }

            // 检查是否有组件使用了未声明的权限
            NodeList declaredPerms = manifestDoc.getElementsByTagName("uses-permission");
            Set<String> declaredSet = new HashSet<>();
            for (int i = 0; i < declaredPerms.getLength(); i++) {
                Element perm = (Element) declaredPerms.item(i);
                declaredSet.add(perm.getAttribute("android:name"));
            }

            for (String used : usedPermissions) {
                if (!declaredSet.contains(used) && !used.startsWith("android.permission")) {
                    results.addFinding(new SecurityFinding(
                        "权限分析器",
                        Severity.LOW,
                        "使用未声明的自定义权限",
                        "组件使用了自定义权限 '" + used + "' 但应用未声明此权限",
                        "在<uses-permission>中声明使用的自定义权限",
                        used,
                        "权限未声明: " + used
                    ));
                }
            }
        }
    }

    // ========================================================================
    // 模块4：AndroidManifest.xml安全扫描器
    // ========================================================================

    /**
     * AndroidManifest.xml安全扫描器
     * 全面扫描manifest文件中的安全配置
     */
    public static class ManifestSecurityScanner {
        private Document manifestDoc;
        private String manifestContent;
        private ResultCollector results;

        public ManifestSecurityScanner(Document manifest, String content,
                                        ResultCollector results) {
            this.manifestDoc = manifest;
            this.manifestContent = content;
            this.results = results;
        }

        /**
         * 执行全面扫描
         */
        public void scanAll() {
            System.out.println("\n[*] 开始AndroidManifest.xml安全扫描...");

            checkDebuggable();
            checkAllowBackup();
            checkNetworkSecurityConfig();
            checkClearTextTraffic();
            checkPackageVisibility();
            checkTaskAffinity();
            checkLaunchMode();
            checkExportedAttribute();
            checkUsesCleartextTraffic();
            checkIntentFilterData();

            System.out.println("[*] AndroidManifest.xml安全扫描完成");
        }

        /**
         * 检查debuggable标志
         */
        private void checkDebuggable() {
            Element application = getApplicationElement();
            if (application != null) {
                String debuggable = application.getAttribute("android:debuggable");
                if ("true".equals(debuggable)) {
                    results.addFinding(new SecurityFinding(
                        "Manifest安全扫描器",
                        Severity.HIGH,
                        "应用可调试",
                        "android:debuggable=true 允许应用被调试器附加，" +
                            "攻击者可在运行时修改应用行为",
                        "在发布版本中设置android:debuggable=false或移除该属性",
                        "application",
                        "android:debuggable=true"
                    ));
                }
            }
        }

        /**
         * 检查allowBackup标志
         */
        private void checkAllowBackup() {
            Element application = getApplicationElement();
            if (application != null) {
                String allowBackup = application.getAttribute("android:allowBackup");
                // allowBackup默认为true
                if (allowBackup == null || allowBackup.isEmpty() || "true".equals(allowBackup)) {
                    results.addFinding(new SecurityFinding(
                        "Manifest安全扫描器",
                        Severity.MEDIUM,
                        "允许应用数据备份",
                        "android:allowBackup=true（或默认）允许通过adb backup提取应用数据，" +
                            "可能导致敏感数据泄露",
                        "设置android:allowBackup=false",
                        "application",
                        "android:allowBackup=" + (allowBackup.isEmpty() ? "true(默认)" : allowBackup)
                    ));
                }
            }
        }

        /**
         * 检查网络安全配置
         */
        private void checkNetworkSecurityConfig() {
            Element application = getApplicationElement();
            if (application != null) {
                String networkConfig = application.getAttribute("android:networkSecurityConfig");
                if (networkConfig == null || networkConfig.isEmpty()) {
                    results.addFinding(new SecurityFinding(
                        "Manifest安全扫描器",
                        Severity.MEDIUM,
                        "未配置网络安全策略",
                        "应用未配置android:networkSecurityConfig，" +
                            "在Android 7.0以下默认允许明文HTTP流量",
                        "创建network_security_config.xml并配置网络安全策略",
                        "application",
                        "android:networkSecurityConfig=(未设置)"
                    ));
                }
            }
        }

        /**
         * 检查明文流量
         */
        private void checkClearTextTraffic() {
            Element application = getApplicationElement();
            if (application != null) {
                String cleartextTraffic = application.getAttribute("android:usesCleartextTraffic");
                if ("true".equals(cleartextTraffic)) {
                    results.addFinding(new SecurityFinding(
                        "Manifest安全扫描器",
                        Severity.HIGH,
                        "允许明文HTTP流量",
                        "android:usesCleartextTraffic=true 允许应用发送明文HTTP流量，" +
                            "可能导致数据在传输中被窃听",
                        "设置android:usesCleartextTraffic=false，使用HTTPS",
                        "application",
                        "android:usesCleartextTraffic=true"
                    ));
                }
            }
        }

        /**
         * 检查包可见性
         */
        private void checkPackageVisibility() {
            NodeList queryElements = manifestDoc.getElementsByTagName("queries");
            if (queryElements.getLength() > 0) {
                Element queries = (Element) queryElements.item(0);
                // 检查是否查询所有包
                NodeList packages = queries.getElementsByTagName("package");
                if (packages.getLength() > 50) {
                    results.addFinding(new SecurityFinding(
                        "Manifest安全Scanner",
                        Severity.LOW,
                        "查询大量应用包名",
                        "应用在<queries>中查询了 " + packages.getLength() + " 个包名，" +
                            "可能导致用户隐私泄露",
                        "仅查询必要的应用包名",
                        "queries",
                        "查询包数量: " + packages.getLength()
                    ));
                }
            }
        }

        /**
         * 检查taskAffinity
         */
        private void checkTaskAffinity() {
            NodeList activities = manifestDoc.getElementsByTagName("activity");
            for (int i = 0; i < activities.getLength(); i++) {
                Element activity = (Element) activities.item(i);
                String affinity = activity.getAttribute("android:taskAffinity");
                boolean exported = "true".equals(activity.getAttribute("android:exported"));
                String launchMode = activity.getAttribute("android:launchMode");

                // 导出的Activity使用singleTask可能导致Task Hijacking
                if (exported && "singleTask".equals(launchMode)) {
                    results.addFinding(new SecurityFinding(
                        "Manifest安全扫描器",
                        Severity.MEDIUM,
                        "导出Activity使用singleTask",
                        "导出Activity '" + activity.getAttribute("android:name") +
                            "' 使用singleTask启动模式，可能导致Task Hijacking攻击",
                        "导出Activity使用standard或singleTop启动模式，" +
                            "或设置taskAffinity为空字符串",
                        activity.getAttribute("android:name"),
                        "exported=true, launchMode=singleTask"
                    ));
                }
            }
        }

        /**
         * 检查启动模式
         */
        private void checkLaunchMode() {
            NodeList activities = manifestDoc.getElementsByTagName("activity");
            for (int i = 0; i < activities.getLength(); i++) {
                Element activity = (Element) activities.item(i);
                String launchMode = activity.getAttribute("android:launchMode");
                boolean exported = "true".equals(activity.getAttribute("android:exported"));

                // singleInstance模式可能导致安全问题
                if (exported && "singleInstance".equals(launchMode)) {
                    results.addFinding(new SecurityFinding(
                        "Manifest安全扫描器",
                        Severity.LOW,
                        "导出Activity使用singleInstance",
                        "导出Activity '" + activity.getAttribute("android:name") +
                            "' 使用singleInstance启动模式，可能导致Activity栈异常",
                        "评估是否需要singleInstance模式，考虑使用singleTask",
                        activity.getAttribute("android:name"),
                        "launchMode=singleInstance"
                    ));
                }
            }
        }

        /**
         * 检查导出属性
         */
        private void checkExportedAttribute() {
            // 检查是否所有组件都显式设置了exported属性
            String[] componentTypes = {"activity", "service", "receiver", "provider"};
            for (String type : componentTypes) {
                NodeList components = manifestDoc.getElementsByTagName(type);
                for (int i = 0; i < components.getLength(); i++) {
                    Element comp = (Element) components.item(i);
                    String exportedAttr = comp.getAttribute("android:exported");
                    boolean hasIntentFilter = comp.getElementsByTagName("intent-filter").getLength() > 0;

                    // 如果没有显式设置exported且有intent-filter
                    if (exportedAttr.isEmpty() && hasIntentFilter) {
                        results.addFinding(new SecurityFinding(
                            "Manifest安全扫描器",
                            Severity.MEDIUM,
                            "组件未显式设置exported属性",
                            type + " '" + comp.getAttribute("android:name") +
                                "' 有intent-filter但未显式设置android:exported属性，" +
                                "默认为导出",
                            "显式设置android:exported属性",
                            comp.getAttribute("android:name"),
                            "exported=(未设置, 默认导出)"
                        ));
                    }
                }
            }
        }

        /**
         * 检查usesCleartextTraffic
         */
        private void checkUsesCleartextTraffic() {
            // 已在checkClearTextTraffic中处理
        }

        /**
         * 检查intent-filter中的data元素
         */
        private void checkIntentFilterData() {
            NodeList dataElements = manifestDoc.getElementsByTagName("data");
            for (int i = 0; i < dataElements.getLength(); i++) {
                Element data = (Element) dataElements.item(i);
                String mimeType = data.getAttribute("android:mimeType");

                // 检查危险的MIME类型
                if (mimeType != null && mimeType.contains("application/*")) {
                    results.addFinding(new SecurityFinding(
                        "Manifest安全扫描器",
                        Severity.LOW,
                        "接受通用MIME类型",
                        "intent-filter接受通配MIME类型 '" + mimeType + "'，" +
                            "可能处理非预期类型的数据",
                        "使用精确的MIME类型",
                        "data",
                        "mimeType=" + mimeType
                    ));
                }
            }
        }

        /**
         * 获取application元素
         */
        private Element getApplicationElement() {
            NodeList apps = manifestDoc.getElementsByTagName("application");
            if (apps.getLength() > 0) {
                return (Element) apps.item(0);
            }
            return null;
        }
    }

    // ========================================================================
    // 模块5：APK元数据提取器
    // ========================================================================

    /**
     * APK元数据提取器
     * 从APK文件中提取安全相关的元数据
     */
    public static class APKMetadataExtractor {
        private String apkPath;
        private ResultCollector results;

        public APKMetadataExtractor(String apkPath, ResultCollector results) {
            this.apkPath = apkPath;
            this.results = results;
        }

        /**
         * 提取APK元数据
         */
        public Map<String, String> extractMetadata() {
            System.out.println("\n[*] 开始APK元数据提取...");

            Map<String, String> metadata = new LinkedHashMap<>();

            try (ZipFile apkFile = new ZipFile(apkPath)) {
                // 提取基本信息
                metadata.put("文件大小", String.format("%.2f MB",
                    new File(apkPath).length() / (1024.0 * 1024.0)));
                metadata.put("条目数量", String.valueOf(apkFile.size()));

                // 提取AndroidManifest.xml
                ZipEntry manifestEntry = apkFile.getEntry("AndroidManifest.xml");
                if (manifestEntry != null) {
                    metadata.put("Manifest存在", "是");
                }

                // 检查classes.dex
                int dexCount = 0;
                Enumeration<? extends ZipEntry> entries = apkFile.entries();
                while (entries.hasMoreElements()) {
                    ZipEntry entry = entries.nextElement();
                    if (entry.getName().startsWith("classes") && entry.getName().endsWith(".dex")) {
                        dexCount++;
                    }

                    // 检查native库
                    if (entry.getName().endsWith(".so")) {
                        String libPath = entry.getName();
                        if (libPath.contains("arm64-v8a")) {
                            metadata.put("ARM64支持", "是");
                        }
                        if (libPath.contains("armeabi-v7a")) {
                            metadata.put("ARMv7支持", "是");
                        }
                        if (libPath.contains("x86")) {
                            metadata.put("x86支持", "是");
                        }
                    }

                    // 检查证书
                    if (entry.getName().startsWith("META-INF/") && entry.getName().endsWith(".RSA")) {
                        metadata.put("签名存在", "是");
                        checkSignature(apkFile, entry, results);
                    }

                    // 检查是否有调试相关文件
                    if (entry.getName().contains("debugger")) {
                        results.addFinding(new SecurityFinding(
                            "APK元数据提取器",
                            Severity.HIGH,
                            "APK包含调试文件",
                            "APK中包含调试相关文件: " + entry.getName(),
                            "移除调试文件",
                            entry.getName(),
                            "调试文件: " + entry.getName()
                        ));
                    }

                    // 检查是否有测试相关文件
                    if (entry.getName().contains("test") || entry.getName().contains("Test")) {
                        results.addFinding(new SecurityFinding(
                            "APK元数据提取器",
                            Severity.LOW,
                            "APK包含测试文件",
                            "APK中包含测试相关文件: " + entry.getName(),
                            "移除测试文件",
                            entry.getName(),
                            "测试文件: " + entry.getName()
                        ));
                    }
                }
                metadata.put("DEX文件数", String.valueOf(dexCount));

                // 检查是否有assets目录中的敏感文件
                checkAssetsDirectory(apkFile);

            } catch (IOException e) {
                System.err.println("[!] APK文件读取失败: " + e.getMessage());
            }

            // 打印元数据
            System.out.println("\n  APK元数据:");
            for (Map.Entry<String, String> entry : metadata.entrySet()) {
                System.out.println("    " + entry.getKey() + ": " + entry.getValue());
            }

            System.out.println("[*] APK元数据提取完成");
            return metadata;
        }

        /**
         * 检查签名信息
         */
        private void checkSignature(ZipFile apkFile, ZipEntry certEntry, ResultCollector results) {
            try (InputStream is = apkFile.getInputStream(certEntry)) {
                // 读取证书信息（简化版，实际需要解析PKCS7）
                byte[] certData = new byte[(int) certEntry.getSize()];
                is.read(certData);

                // 检查签名方案
                if (certEntry.getName().contains("v1")) {
                    results.addFinding(new SecurityFinding(
                        "APK元数据提取器",
                        Severity.LOW,
                        "使用V1签名方案",
                        "APK使用V1签名方案（JAR签名），不支持APK Signature Scheme v2+",
                        "使用APK Signature Scheme v2/v3进行签名",
                        "签名",
                        "签名方案: V1 (JAR signing)"
                    ));
                }

            } catch (IOException e) {
                System.err.println("[!] 签名读取失败: " + e.getMessage());
            }
        }

        /**
         * 检查assets目录
         */
        private void checkAssetsDirectory(ZipFile apkFile) {
            Enumeration<? extends ZipEntry> entries = apkFile.entries();
            while (entries.hasMoreElements()) {
                ZipEntry entry = entries.nextElement();
                String name = entry.getName();

                if (name.startsWith("assets/")) {
                    // 检查敏感文件
                    String[] sensitiveFiles = {
                        ".env", "config.json", "config.xml", "secrets.json",
                        "credentials", "api_keys", "private_key",
                        "database.db", "users.db", ".sqlite"
                    };

                    String nameLower = name.toLowerCase();
                    for (String sensitive : sensitiveFiles) {
                        if (nameLower.contains(sensitive)) {
                            results.addFinding(new SecurityFinding(
                                "APK元数据提取器",
                                Severity.HIGH,
                                "assets目录包含敏感文件",
                                "assets目录中包含可能敏感的文件: " + name,
                                "移除敏感文件或加密存储",
                                name,
                                "敏感文件: " + name
                            ));
                            break;
                        }
                    }

                    // 检查备份文件
                    if (nameLower.endsWith(".bak") || nameLower.endsWith(".old")
                        || nameLower.endsWith(".tmp")) {
                        results.addFinding(new SecurityFinding(
                            "APK元数据提取器",
                            Severity.LOW,
                            "assets目录包含备份文件",
                            "assets目录中包含备份文件: " + name,
                            "移除备份文件",
                            name,
                            "备份文件: " + name
                        ));
                    }
                }
            }
        }
    }

    // ========================================================================
    // 模块6：Shared Preferences安全检查器
    // ========================================================================

    /**
     * Shared Preferences安全检查器
     * 检查SharedPreferences的使用是否安全
     */
    public static class SharedPreferencesChecker {
        private ResultCollector results;

        public SharedPreferencesChecker(ResultCollector results) {
            this.results = results;
        }

        /**
         * 执行SharedPreferences安全检查
         */
        public void check() {
            System.out.println("\n[*] 开始SharedPreferences安全检查...");

            // 注意：实际检查需要扫描Java/Smali代码
            // 这里提供检查框架和常见问题

            checkStorageMode();
            checkSensitiveData();
            checkAccessControl();

            System.out.println("[*] SharedPreferences安全检查完成");
        }

        /**
         * 检查存储模式
         */
        private void checkStorageMode() {
            results.addFinding(new SecurityFinding(
                "SharedPreferences检查器",
                Severity.INFO,
                "SharedPreferences存储模式检查",
                "需检查代码中SharedPreferences的创建方式：\n" +
                    "  - 使用MODE_PRIVATE（安全）\n" +
                    "  - 使用MODE_WORLD_READABLE（已弃用，危险）\n" +
                    "  - 使用MODE_WORLD_WRITEABLE（已弃用，危险）\n" +
                    "  - 使用MODE_MULTI_PROCESS（已弃用）\n\n" +
                    "  安全写法: getSharedPreferences(name, MODE_PRIVATE)\n" +
                    "  危险写法: getSharedPreferences(name, MODE_WORLD_READABLE)",
                "使用MODE_PRIVATE创建SharedPreferences，敏感数据使用EncryptedSharedPreferences",
                "SharedPreferences",
                "需扫描Java/Smali代码检查创建模式"
            ));
        }

        /**
         * 检查敏感数据存储
         */
        private void checkSensitiveData() {
            results.addFinding(new SecurityFinding(
                "SharedPreferences检查器",
                Severity.INFO,
                "SharedPreferences敏感数据检查",
                "需检查SharedPreferences中是否存储了以下敏感数据：\n" +
                    "  - 用户密码/Token\n" +
                    "  - Session ID\n" +
                    "  - API密钥\n" +
                    "  - 个人身份信息（PII）\n" +
                    "  - 信用卡号\n" +
                    "  - 私钥\n\n" +
                    "  检查方法：\n" +
                    "  1. 在/data/data/<package>/shared_prefs/目录下查看XML文件\n" +
                    "  2. 在代码中搜索 getString/putString 调用\n" +
                    "  3. 检查key名称是否暗示敏感数据",
                "敏感数据不应存储在明文SharedPreferences中，应使用加密存储",
                "SharedPreferences",
                "需检查存储的key-value对"
            ));
        }

        /**
         * 检查访问控制
         */
        private void checkAccessControl() {
            results.addFinding(new SecurityFinding(
                "SharedPreferences检查器",
                Severity.INFO,
                "SharedPreferences访问控制检查",
                "需检查：\n" +
                    "  1. SharedPreferences文件权限是否为0600\n" +
                    "  2. 是否使用了apply()而非commit()\n" +
                    "  3. 备份是否包含SharedPreferences数据\n" +
                    "  4. 是否使用了 EncryptedSharedPreferences\n\n" +
                    "  安全写法:\n" +
                    "  - 使用 EncryptedSharedPreferences (Jetpack Security)\n" +
                    "  - 使用 MasterKey 保护密钥\n" +
                    "  - 使用 apply() 异步写入",
                "使用Jetpack Security库的EncryptedSharedPreferences保护敏感数据",
                "SharedPreferences",
                "需检查访问控制配置"
            ));
        }
    }

    // ========================================================================
    // 模块7：ContentProvider URI测试器
    // ========================================================================

    /**
     * ContentProvider URI测试器
     * 测试ContentProvider的URI安全性
     */
    public static class ContentProviderURITester {
        private Document manifestDoc;
        private ResultCollector results;

        public ContentProviderURITester(Document manifest, ResultCollector results) {
            this.manifestDoc = manifest;
            this.results = results;
        }

        /**
         * 测试所有ContentProvider的URI
         */
        public void testAllProviders() {
            System.out.println("\n[*] 开始ContentProvider URI测试...");

            NodeList providers = manifestDoc.getElementsByTagName("provider");
            for (int i = 0; i < providers.getLength(); i++) {
                Element provider = (Element) providers.item(i);
                String name = provider.getAttribute("android:name");
                String authorities = provider.getAttribute("android:authorities");
                boolean exported = "true".equals(provider.getAttribute("android:exported"));
                String readPerm = provider.getAttribute("android:readPermission");
                String writePerm = provider.getAttribute("android:writePermission");
                String grantUri = provider.getAttribute("android:grantUriPermissions");

                if (exported) {
                    testProviderURI(name, authorities, readPerm, writePerm, grantUri);
                }
            }

            System.out.println("[*] ContentProvider URI测试完成");
        }

        /**
         * 测试单个Provider的URI
         */
        private void testProviderURI(String name, String authorities,
                                     String readPerm, String writePerm, String grantUri) {
            // 构造测试URI
            String baseUri = "content://" + authorities;

            // 测试URI列表
            String[] testUris = {
                baseUri,
                baseUri + "/",
                baseUri + "/*",
                baseUri + "/1",
                baseUri + "/-1",
                baseUri + "/0",
                baseUri + "/999999",
                baseUri + "/..",
                baseUri + "/%2e%2e",
                baseUri + "/../../../",
                baseUri + "/.svn",
                baseUri + "/.git",
                baseUri + "/config",
                baseUri + "/settings",
                baseUri + "/users",
                baseUri + "/password",
                baseUri + "/token",
                baseUri + "/admin",
            };

            results.addFinding(new SecurityFinding(
                "ContentProvider URI测试器",
                Severity.INFO,
                "ContentProvider URI测试清单",
                "Provider: " + name + "\n" +
                    "Authorities: " + authorities + "\n" +
                    "导出: true\n" +
                    "读权限: " + (readPerm.isEmpty() ? "(无)" : readPerm) + "\n" +
                    "写权限: " + (writePerm.isEmpty() ? "(无)" : writePerm) + "\n" +
                    "grantUriPermissions: " + grantUri + "\n\n" +
                    "建议测试的URI:\n" +
                    String.join("\n", testUris),
                "使用adb shell content query测试每个URI，检查返回的数据",
                name,
                "Authorities: " + authorities
            ));

            // 检查无权限的Provider
            if (readPerm.isEmpty() && writePerm.isEmpty()) {
                results.addFinding(new SecurityFinding(
                    "ContentProvider URI测试器",
                    Severity.HIGH,
                    "导出Provider无读写权限",
                    "Provider '" + name + "' 被导出但未设置读写权限，" +
                        "所有应用都可读写其数据",
                    "设置android:readPermission和android:writePermission",
                    name,
                    "exported=true, readPermission=(空), writePermission=(空)"
                ));
            }

            // 检查grantUriPermissions
            if ("true".equals(grantUri)) {
                results.addFinding(new SecurityFinding(
                    "ContentProvider URI测试器",
                    Severity.MEDIUM,
                    "Provider启用URI权限授予",
                    "Provider '" + name + "' 启用了grantUriPermissions，" +
                        "可能导致URI权限绕过攻击",
                    "仅在必要时启用，限制可授权的URI路径",
                    name,
                    "grantUriPermissions=true"
                ));
            }

            // 检查path权限定义
            NodeList pathPerms = manifestDoc.getElementsByTagName("path-permission");
            if (pathPerms.getLength() == 0 && exported) {
                results.addFinding(new SecurityFinding(
                    "ContentProvider URI测试器",
                    Severity.LOW,
                    "Provider未定义path权限",
                    "Provider '" + name + "' 未定义path-permission，" +
                        "无法对不同路径设置不同权限",
                    "为敏感路径定义path-permission",
                    name,
                    "无path-permission定义"
                ));
            }
        }
    }

    // ========================================================================
    // 模块8：WebView安全分析器
    // ========================================================================

    /**
     * WebView安全分析器
     * 分析WebView的使用是否存在安全问题
     */
    public static class WebViewSecurityAnalyzer {
        private ResultCollector results;

        public WebViewSecurityAnalyzer(ResultCollector results) {
            this.results = results;
        }

        /**
         * 执行WebView安全分析
         */
        public void analyze() {
            System.out.println("\n[*] 开始WebView安全分析...");

            checkJavaScriptEnabled();
            checkFileAccess();
            checkUniversalAccess();
            checkJavaScriptInterface();
            checkSSLHandling();
            checkMixedContent();
            checkURLValidation();
            checkDownloadListener();

            System.out.println("[*] WebView安全分析完成");
        }

        /**
         * 检查JavaScript启用
         */
        private void checkJavaScriptEnabled() {
            results.addFinding(new SecurityFinding(
                "WebView安全分析器",
                Severity.INFO,
                "JavaScript启用检查",
                "需检查代码中是否调用了 setJavaScriptEnabled(true)\n" +
                    "  危险：启用JavaScript后加载不可信URL可能导致XSS攻击\n" +
                    "  检查方法：\n" +
                    "    grep -r 'setJavaScriptEnabled' src/\n\n" +
                    "  安全写法：\n" +
                    "    // 仅在加载可信内容时启用JavaScript\n" +
                    "    webView.getSettings().setJavaScriptEnabled(false);\n" +
                    "    // 或仅加载本地可信HTML",
                "仅在加载可信内容时启用JavaScript，禁止加载外部URL",
                "WebView",
                "需扫描Java代码"
            ));
        }

        /**
         * 检查文件访问
         */
        private void checkFileAccess() {
            results.addFinding(new SecurityFinding(
                "WebView安全分析器",
                Severity.INFO,
                "文件访问检查",
                "需检查以下WebView设置：\n" +
                    "  - setAllowFileAccess(true) - 允许访问file://URL\n" +
                    "  - setAllowFileAccessFromFileURLs(true) - 允许file://URL访问其他file://URL\n" +
                    "  - setAllowUniversalAccessFromFileURLs(true) - 允许file://URL访问任意源\n\n" +
                    "  危险配置：\n" +
                    "    settings.setAllowFileAccess(true);\n" +
                    "    settings.setAllowFileAccessFromFileURLs(true);\n" +
                    "    settings.setAllowUniversalAccessFromFileURLs(true);\n\n" +
                    "  安全配置：\n" +
                    "    settings.setAllowFileAccess(false);\n" +
                    "    settings.setAllowFileAccessFromFileURLs(false);\n" +
                    "    settings.setAllowUniversalAccessFromFileURLs(false);",
                "禁用所有文件访问设置，除非绝对必要",
                "WebView",
                "需扫描Java代码中的WebSettings配置"
            ));
        }

        /**
         * 检查Universal Access
         */
        private void checkUniversalAccess() {
            results.addFinding(new SecurityFinding(
                "WebView安全分析器",
                Severity.INFO,
                "Universal Access检查",
                "需检查 setAllowUniversalAccessFromFileURLs() 设置\n" +
                    "  启用后，file:// URL中的JavaScript可以访问任何源的内容\n" +
                    "  这是最危险的WebView配置之一\n\n" +
                    "  检查方法：\n" +
                    "    grep -r 'setAllowUniversalAccessFromFileURLs' src/\n\n" +
                    "  安全设置：\n" +
                    "    settings.setAllowUniversalAccessFromFileURLs(false);",
                "禁用Universal Access，使用HTTPS替代file:// URL",
                "WebView",
                "需扫描Java代码"
            ));
        }

        /**
         * 检查JavaScript Interface
         */
        private void checkJavaScriptInterface() {
            results.addFinding(new SecurityFinding(
                "WebView安全分析器",
                Severity.INFO,
                "JavaScript Interface检查",
                "需检查 addJavascriptInterface() 的使用\n" +
                    "  危险：JavaScript可以通过接口调用Java方法\n" +
                    "  在Android 4.2以下有远程代码执行漏洞\n\n" +
                    "  检查方法：\n" +
                    "    grep -r 'addJavascriptInterface' src/\n\n" +
                    "  安全建议：\n" +
                    "    1. 仅在加载可信内容时添加接口\n" +
                    "    2. 使用@JavascriptInterface注解限制可调用方法\n" +
                    "    3. 对接口方法进行输入验证\n" +
                    "    4. targetSdkVersion >= 17",
                "限制JavaScript Interface的使用，使用@JavascriptInterface注解",
                "WebView",
                "需扫描Java代码中的addJavascriptInterface调用"
            ));
        }

        /**
         * 检查SSL处理
         */
        private void checkSSLHandling() {
            results.addFinding(new SecurityFinding(
                "WebView安全分析器",
                Severity.INFO,
                "SSL证书处理检查",
                "需检查WebViewClient的SSL错误处理\n" +
                    "  危险：覆盖onReceivedSslError并调用handler.proceed()接受所有SSL错误\n\n" +
                    "  检查方法：\n" +
                    "    grep -r 'onReceivedSslError' src/\n\n" +
                    "  危险写法：\n" +
                    "    @Override\n" +
                    "    public void onReceivedSslError(WebView view, SslErrorHandler handler, SslError error) {\n" +
                    "        handler.proceed(); // 接受所有SSL错误！\n" +
                    "    }\n\n" +
                    "  安全写法：\n" +
                    "    @Override\n" +
                    "    public void onReceivedSslError(WebView view, SslErrorHandler handler, SslError error) {\n" +
                    "        handler.cancel(); // 拒绝SSL错误\n" +
                    "    }",
                "不要接受SSL证书错误，使用handler.cancel()或证书锁定",
                "WebView",
                "需扫描Java代码中的onReceivedSslError方法"
            ));
        }

        /**
         * 检查混合内容
         */
        private void checkMixedContent() {
            results.addFinding(new SecurityFinding(
                "WebView安全分析器",
                Severity.INFO,
                "混合内容检查",
                "需检查 setMixedContentMode() 设置\n" +
                    "  MIXED_CONTENT_ALWAYS_ALLOW (0) - 允许HTTPS页面加载HTTP资源\n" +
                    "  MIXED_CONTENT_COMPATIBILITY_MODE (1) - 兼容模式\n" +
                    "  MIXED_CONTENT_NEVER_ALLOW (2) - 禁止混合内容\n\n" +
                    "  安全设置：\n" +
                    "    settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);",
                "禁止混合内容，确保所有资源通过HTTPS加载",
                "WebView",
                "需扫描Java代码"
            ));
        }

        /**
         * 检查URL验证
         */
        private void checkURLValidation() {
            results.addFinding(new SecurityFinding(
                "WebView安全分析器",
                Severity.INFO,
                "URL验证检查",
                "需检查 shouldOverrideUrlLoading() 中是否验证URL\n" +
                    "  应验证加载的URL是否为可信域名\n\n" +
                    "  安全写法：\n" +
                    "    @Override\n" +
                    "    public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {\n" +
                    "        String url = request.getUrl().toString();\n" +
                    "        if (isUrlSafe(url)) {\n" +
                    "            return false; // 允许加载\n" +
                    "        }\n" +
                    "        return true; // 拒绝加载\n" +
                    "    }\n\n" +
                    "    private boolean isUrlSafe(String url) {\n" +
                    "        return url.startsWith(\"https://\")\n" +
                    "            && (url.contains(\"trusted.com\"));\n" +
                    "    }",
                "验证WebView加载的URL，仅允许可信域名",
                "WebView",
                "需扫描Java代码中的shouldOverrideUrlLoading方法"
            ));
        }

        /**
         * 检查下载监听器
         */
        private void checkDownloadListener() {
            results.addFinding(new SecurityFinding(
                "WebView安全分析器",
                Severity.INFO,
                "下载监听器检查",
                "需检查 setDownloadListener() 的使用\n" +
                    "  应验证下载的文件类型和来源\n\n" +
                    "  安全写法：\n" +
                    "    webView.setDownloadListener(new DownloadListener() {\n" +
                    "        @Override\n" +
                    "        public void onDownloadStart(String url, String userAgent,\n" +
                    "                String contentDisposition, String mimeType, long contentLength) {\n" +
                    "            // 验证下载URL和文件类型\n" +
                    "            if (isDownloadSafe(url, mimeType)) {\n" +
                    "                // 使用DownloadManager安全下载\n" +
                    "            }\n" +
                    "        }\n" +
                    "    });",
                "验证下载URL和文件类型，使用安全的下载方式",
                "WebView",
                "需扫描Java代码"
            ));
        }
    }

    // ========================================================================
    // 工具方法：XML解析
    // ========================================================================

    /**
     * 解析AndroidManifest.xml
     */
    public static Document parseManifest(String filePath) throws Exception {
        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
        factory.setNamespaceAware(true);
        factory.setFeature("http://apache.org/xml/features/nonvalidating/load-external-dtd", false);
        factory.setFeature("http://xml.org/sax/features/external-general-entities", false);
        factory.setFeature("http://xml.org/sax/features/external-parameter-entities", false);

        DocumentBuilder builder = factory.newDocumentBuilder();
        builder.setErrorHandler(new ErrorHandler() {
            @Override
            public void warning(SAXParseException e) {}

            @Override
            public void error(SAXParseException e) {}

            @Override
            public void fatalError(SAXParseException e) throws SAXException {
                throw e;
            }
        });

        return builder.parse(new File(filePath));
    }

    /**
     * 从APK中提取AndroidManifest.xml（简化版）
     * 注意：实际的APK中的AndroidManifest.xml是二进制格式，需要AXML解析器
     */
    public static String extractManifestFromAPK(String apkPath) throws Exception {
        // 实际需要使用AXML解析器解析二进制XML
        // 这里提供框架
        try (ZipFile apk = new ZipFile(apkPath)) {
            ZipEntry entry = apk.getEntry("AndroidManifest.xml");
            if (entry != null) {
                // 注意：这里获取的是二进制XML，需要专门的解析器
                // 如Android Asset Packaging Tool (AAPT) 或 Androguard
                System.out.println("[!] 注意：APK中的AndroidManifest.xml为二进制格式");
                System.out.println("[!] 请使用aapt或Androguard工具提取XML");
                return null;
            }
        }
        return null;
    }

    /**
     * 从文件读取文本内容
     */
    public static String readFileContent(String filePath) throws Exception {
        StringBuilder content = new StringBuilder();
        try (BufferedReader reader = new BufferedReader(new FileReader(filePath))) {
            String line;
            while ((line = reader.readLine()) != null) {
                content.append(line).append("\n");
            }
        }
        return content.toString();
    }

    // ========================================================================
    // 主函数与CLI入口
    // ========================================================================

    public static void main(String[] args) {
        System.out.println("=".repeat(60));
        System.out.println("  Android安全工具集 v1.0");
        System.out.println("  综合Android应用安全分析工具");
        System.out.println("=".repeat(60));

        if (args.length < 2) {
            printUsage();
            System.exit(1);
        }

        String command = args[0];
        String filePath = null;

        // 解析参数
        for (int i = 1; i < args.length; i++) {
            if ("-f".equals(args[i]) || "--file".equals(args[i])) {
                if (i + 1 < args.length) {
                    filePath = args[i + 1];
                    i++;
                }
            }
        }

        if (filePath == null) {
            System.err.println("[!] 未指定文件路径，请使用 -f 参数");
            printUsage();
            System.exit(1);
        }

        // 创建结果收集器
        ResultCollector results = new ResultCollector();

        try {
            switch (command) {
                case "manifest":
                    scanManifest(filePath, results);
                    break;
                case "apk":
                    scanAPK(filePath, results);
                    break;
                case "component":
                    scanComponents(filePath, results);
                    break;
                case "permission":
                    scanPermissions(filePath, results);
                    break;
                case "webview":
                    scanWebView(filePath, results);
                    break;
                case "all":
                    scanAll(filePath, results);
                    break;
                default:
                    System.err.println("[!] 未知命令: " + command);
                    printUsage();
                    System.exit(1);
            }

            // 打印结果
            results.printSummary();
            results.printDetails();

        } catch (Exception e) {
            System.err.println("[!] 执行失败: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }

    /**
     * 扫描AndroidManifest.xml
     */
    private static void scanManifest(String filePath, ResultCollector results) throws Exception {
        Document manifest = parseManifest(filePath);
        String content = readFileContent(filePath);

        ManifestSecurityScanner scanner = new ManifestSecurityScanner(manifest, content, results);
        scanner.scanAll();
    }

    /**
     * 扫描APK文件
     */
    private static void scanAPK(String apkPath, ResultCollector results) throws Exception {
        // 提取元数据
        APKMetadataExtractor metadataExtractor = new APKMetadataExtractor(apkPath, results);
        metadataExtractor.extractMetadata();

        // 注意：实际需要使用AXML解析器从APK中提取Manifest
        System.out.println("\n[!] 提示：APK中的Manifest为二进制格式");
        System.out.println("[!] 请先使用 aapt dump xmltree 或 androguard 提取Manifest XML");
        System.out.println("[!] 然后使用 manifest 命令进行扫描");
    }

    /**
     * 扫描组件
     */
    private static void scanComponents(String filePath, ResultCollector results) throws Exception {
        Document manifest = parseManifest(filePath);

        ComponentExportChecker checker = new ComponentExportChecker(manifest, results);
        checker.checkAllComponents();

        IntentSecurityAnalyzer intentAnalyzer = new IntentSecurityAnalyzer(manifest, results);
        intentAnalyzer.analyzeIntentFilters();

        ContentProviderURITester providerTester = new ContentProviderURITester(manifest, results);
        providerTester.testAllProviders();
    }

    /**
     * 扫描权限
     */
    private static void scanPermissions(String filePath, ResultCollector results) throws Exception {
        Document manifest = parseManifest(filePath);

        PermissionAnalyzer analyzer = new PermissionAnalyzer(manifest, results);
        analyzer.analyzePermissions();
    }

    /**
     * 扫描WebView
     */
    private static void scanWebView(String filePath, ResultCollector results) throws Exception {
        // WebView检查需要扫描Java/Smali代码
        // 这里检查Manifest中是否有WebView相关声明
        Document manifest = parseManifest(filePath);

        WebViewSecurityAnalyzer analyzer = new WebViewSecurityAnalyzer(results);
        analyzer.analyze();

        // 同时检查SharedPreferences
        SharedPreferencesChecker spChecker = new SharedPreferencesChecker(results);
        spChecker.check();
    }

    /**
     * 执行全面扫描
     */
    private static void scanAll(String filePath, ResultCollector results) throws Exception {
        // 判断是APK还是Manifest
        if (filePath.endsWith(".apk")) {
            scanAPK(filePath, results);
            System.out.println("\n[!] 请提取Manifest后运行全面扫描");
        } else {
            scanManifest(filePath, results);
            scanComponents(filePath, results);
            scanPermissions(filePath, results);
            scanWebView(filePath, results);
        }
    }

    /**
     * 打印使用说明
     */
    private static void printUsage() {
        System.out.println("\n使用方法:");
        System.out.println("  java android_security_tools <command> -f <file>");
        System.out.println("\n命令:");
        System.out.println("  manifest    - 扫描AndroidManifest.xml安全配置");
        System.out.println("  apk         - 提取APK元数据");
        System.out.println("  component   - 检查组件导出和Intent安全");
        System.out.println("  permission  - 分析权限使用");
        System.out.println("  webview     - 分析WebView和SharedPreferences安全");
        System.out.println("  all         - 执行全面安全扫描");
        System.out.println("\n示例:");
        System.out.println("  java android_security_tools manifest -f AndroidManifest.xml");
        System.out.println("  java android_security_tools apk -f app.apk");
        System.out.println("  java android_security_tools all -f AndroidManifest.xml");
        System.out.println("\n免责声明: 仅用于授权的安全测试！");
    }
}
