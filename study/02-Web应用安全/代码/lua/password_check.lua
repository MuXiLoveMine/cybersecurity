--[[
================================================================================
  密码强度检测工具 - password_check.lua
================================================================================
  功能说明：
    本脚本用于检测密码强度和安全性评估，用于安全学习：
    1. 密码强度评分（0-100 分）
    2. 弱密码检测（常见弱密码字典检查）
    3. 密码复杂度分析（长度、大小写、数字、特殊字符）
    4. 常见模式检测（键盘序列、重复字符、连续数字等）
    5. 密码改进建议

  使用方法：
    lua password_check.lua <密码> [选项]

  示例：
    -- 检测单个密码
    lua password_check.lua "MyP@ssw0rd123"

    -- 检测并显示详细分析
    lua password_check.lua "123456" --detail

    -- 显示帮助
    lua password_check.lua --help

  免责声明：
    本脚本仅供安全学习和密码安全研究使用。
    密码强度评分仅供参考，高分不代表绝对安全。
    弱密码字典内置有限，实际使用应结合更完整的字典。
    请勿用本工具破解他人密码，使用本脚本造成的一切后果由使用者自行承担。
================================================================================
--]]

-- ============================================================
-- 常见弱密码字典（内置常用弱密码 Top 100）
-- 实际生产环境应使用更完整的字典如 rockyou.txt
-- ============================================================
local weak_passwords = {
    -- 数字类
    "123456", "123456789", "12345", "12345678", "111111",
    "1234567", "1234", "1234567890", "123321", "121212",
    "000000", "654321", "123123", "888888", "666666",
    "123456789", "123", "123abc", "a123456", "123456a",
    -- 字母类
    "password", "qwerty", "abc123", "password1", "123qwe",
    "qwertyuiop", "qwer1234", "abcdef", "qazwsx", "zxcvbnm",
    "asdfgh", "asdfghjkl", "qwe123", "123qweasd", "admin",
    "admin123", "root", "toor", "guest", "user",
    "test", "test123", "welcome", "welcome1", "letmein",
    "monkey", "dragon", "master", "princess", "sunshine",
    "iloveyou", "trustno1", "football", "baseball", "superman",
    -- 日期类
    "123456789", "2020", "2021", "2022", "2023",
    "00000000", "11111111", "88888888", "password123",
    -- 拼音类
    "woaini", "nihao", "wangjing", "123456a", "a123456",
    "123456abc", "abc123456", "qq123456", "123456qq",
    -- 其他
    "p@ssw0rd", "passw0rd", "password!", "admin@123",
    "123456!", "1q2w3e4r", "q1w2e3r4", "zxcvbnm,.",
}

-- ============================================================
-- 键盘序列模式（检测键盘连续按键）
-- ============================================================
local keyboard_rows = {
    "1234567890-=",
    "qwertyuiop[]\\",
    "asdfghjkl;'",
    "zxcvbnm,./",
    "QWERTYUIOP{}|",
    "ASDFGHJKL:\"",
    "ZXCVBNM<>?",
}

-- ============================================================
-- 检查密码是否在弱密码字典中
-- 参数：
--   password - 待检测的密码
-- 返回：是否为弱密码，匹配到的密码
-- ============================================================
function is_weak_password(password)
    local lower_pwd = string.lower(password)
    for _, weak in ipairs(weak_passwords) do
        if lower_pwd == string.lower(weak) then
            return true, weak
        end
    end
    return false, nil
end

-- ============================================================
-- 密码复杂度分析
-- 参数：
--   password - 待分析的密码
-- 返回：复杂度分析表
-- ============================================================
function analyze_complexity(password)
    local analysis = {
        length = #password,
        has_lower = false,
        has_upper = false,
        has_digit = false,
        has_special = false,
        lower_count = 0,
        upper_count = 0,
        digit_count = 0,
        special_count = 0,
        unique_chars = 0,
    }

    local char_set = {}

    for i = 1, #password do
        local char = string.sub(password, i, i)
        local byte = string.byte(char)

        if byte >= 97 and byte <= 122 then       -- a-z
            analysis.has_lower = true
            analysis.lower_count = analysis.lower_count + 1
        elseif byte >= 65 and byte <= 90 then    -- A-Z
            analysis.has_upper = true
            analysis.upper_count = analysis.upper_count + 1
        elseif byte >= 48 and byte <= 57 then    -- 0-9
            analysis.has_digit = true
            analysis.digit_count = analysis.digit_count + 1
        else                                      -- 特殊字符
            analysis.has_special = true
            analysis.special_count = analysis.special_count + 1
        end

        -- 统计唯一字符
        if not char_set[char] then
            char_set[char] = true
            analysis.unique_chars = analysis.unique_chars + 1
        end
    end

    -- 字符类型数量
    analysis.char_types = 0
    if analysis.has_lower then analysis.char_types = analysis.char_types + 1 end
    if analysis.has_upper then analysis.char_types = analysis.char_types + 1 end
    if analysis.has_digit then analysis.char_types = analysis.char_types + 1 end
    if analysis.has_special then analysis.char_types = analysis.char_types + 1 end

    return analysis
end

-- ============================================================
-- 检测键盘序列（连续的键盘按键）
-- 参数：
--   password - 待检测的密码
-- 返回：是否包含键盘序列，最长序列长度
-- ============================================================
function detect_keyboard_pattern(password)
    local max_seq_len = 0
    local found_seq = nil

    for _, row in ipairs(keyboard_rows) do
        -- 正向检测
        for i = 1, #row - 2 do
            for j = i + 3, #row do
                local seq = string.sub(row, i, j)
                if string.find(password, seq, 1, true) then
                    if #seq > max_seq_len then
                        max_seq_len = #seq
                        found_seq = seq
                    end
                end
            end
        end
        -- 反向检测
        local reverse_row = string.reverse(row)
        for i = 1, #reverse_row - 2 do
            for j = i + 3, #reverse_row do
                local seq = string.sub(reverse_row, i, j)
                if string.find(password, seq, 1, true) then
                    if #seq > max_seq_len then
                        max_seq_len = #seq
                        found_seq = seq
                    end
                end
            end
        end
    end

    return max_seq_len >= 3, max_seq_len, found_seq
end

-- ============================================================
-- 检测重复字符模式
-- 参数：
--   password - 待检测的密码
-- 返回：是否有重复字符，最大重复次数，重复字符
-- ============================================================
function detect_repeated_chars(password)
    local max_repeat = 1
    local current_repeat = 1
    local repeat_char = nil

    for i = 2, #password do
        if string.sub(password, i, i) == string.sub(password, i - 1, i - 1) then
            current_repeat = current_repeat + 1
            if current_repeat > max_repeat then
                max_repeat = current_repeat
                repeat_char = string.sub(password, i, i)
            end
        else
            current_repeat = 1
        end
    end

    return max_repeat >= 3, max_repeat, repeat_char
end

-- ============================================================
-- 检测连续数字/字母
-- 参数：
--   password - 待检测的密码
-- 返回：是否有连续序列，最大连续长度
-- ============================================================
function detect_sequential_chars(password)
    local max_seq = 1
    local current_seq = 1

    for i = 2, #password do
        local curr_byte = string.byte(password, i)
        local prev_byte = string.byte(password, i - 1)

        -- 正向连续
        if curr_byte == prev_byte + 1 then
            current_seq = current_seq + 1
            if current_seq > max_seq then
                max_seq = current_seq
            end
        elseif curr_byte == prev_byte - 1 then
            -- 反向连续
            current_seq = current_seq + 1
            if current_seq > max_seq then
                max_seq = current_seq
            end
        else
            current_seq = 1
        end
    end

    return max_seq >= 3, max_seq
end

-- ============================================================
-- 密码强度评分（0-100 分）
-- 评分算法：
--   基础分 + 长度加分 + 字符类型加分 - 模式扣分
-- 参数：
--   password - 待评分的密码
-- 返回：分数，等级，详细评分项
-- ============================================================
function score_password(password)
    local score = 0
    local details = {}

    -- 基础长度评分
    local len = #password
    if len < 6 then
        score = score + 5
        table.insert(details, "密码过短 (< 6 位): +5 分")
    elseif len < 8 then
        score = score + 15
        table.insert(details, "密码较短 (6-7 位): +15 分")
    elseif len < 10 then
        score = score + 30
        table.insert(details, "密码长度适中 (8-9 位): +30 分")
    elseif len < 12 then
        score = score + 45
        table.insert(details, "密码长度良好 (10-11 位): +45 分")
    elseif len < 16 then
        score = score + 60
        table.insert(details, "密码长度优秀 (12-15 位): +60 分")
    else
        score = score + 70
        table.insert(details, "密码长度极优 (>= 16 位): +70 分")
    end

    -- 字符类型评分
    local analysis = analyze_complexity(password)

    if analysis.has_lower then
        score = score + 5
        table.insert(details, "包含小写字母: +5 分")
    end
    if analysis.has_upper then
        score = score + 10
        table.insert(details, "包含大写字母: +10 分")
    end
    if analysis.has_digit then
        score = score + 10
        table.insert(details, "包含数字: +10 分")
    end
    if analysis.has_special then
        score = score + 15
        table.insert(details, "包含特殊字符: +15 分")
    end

    -- 字符多样性加分
    if analysis.char_types >= 3 then
        score = score + 10
        table.insert(details, "字符类型多样 (>=3 种): +10 分")
    end
    if analysis.char_types == 4 then
        score = score + 10
        table.insert(details, "字符类型全面 (4 种): +10 分")
    end

    -- 唯一字符比例
    if len > 0 then
        local unique_ratio = analysis.unique_chars / len
        if unique_ratio >= 0.8 then
            score = score + 5
            table.insert(details, "字符多样性高: +5 分")
        elseif unique_ratio < 0.5 then
            score = score - 5
            table.insert(details, "字符重复率高: -5 分")
        end
    end

    -- 弱密码扣分
    local is_weak, matched = is_weak_password(password)
    if is_weak then
        score = score - 50
        table.insert(details, "命中弱密码字典 (" .. matched .. "): -50 分")
    end

    -- 键盘序列扣分
    local has_kb, kb_len, kb_seq = detect_keyboard_pattern(password)
    if has_kb then
        score = score - 15
        table.insert(details, "包含键盘序列 (" .. kb_seq .. "): -15 分")
    end

    -- 重复字符扣分
    local has_rep, rep_count, rep_char = detect_repeated_chars(password)
    if has_rep then
        local penalty = rep_count * 3
        score = score - penalty
        table.insert(details, "重复字符 (" .. rep_char .. "x" .. rep_count .. "): -" .. penalty .. " 分")
    end

    -- 连续数字/字母扣分
    local has_seq, seq_len = detect_sequential_chars(password)
    if has_seq then
        local penalty = seq_len * 2
        score = score - penalty
        table.insert(details, "连续字符 (" .. seq_len .. " 个): -" .. penalty .. " 分")
    end

    -- 确保分数在 0-100 之间
    score = math.max(0, math.min(100, score))

    -- 评定等级
    local level
    if score >= 90 then
        level = "极强"
    elseif score >= 75 then
        level = "强"
    elseif score >= 60 then
        level = "中等"
    elseif score >= 40 then
        level = "弱"
    else
        level = "极弱"
    end

    return score, level, details
end

-- ============================================================
-- 生成密码改进建议
-- ============================================================
function generate_suggestions(password)
    local suggestions = {}
    local analysis = analyze_complexity(password)

    if #password < 8 then
        table.insert(suggestions, "增加密码长度到至少 8 位，推荐 12 位以上")
    end

    if not analysis.has_upper then
        table.insert(suggestions, "添加大写字母以增加复杂度")
    end

    if not analysis.has_lower then
        table.insert(suggestions, "添加小写字母以增加复杂度")
    end

    if not analysis.has_digit then
        table.insert(suggestions, "添加数字以增加复杂度")
    end

    if not analysis.has_special then
        table.insert(suggestions, "添加特殊字符（如 !@#$%^&*）以增加复杂度")
    end

    local is_weak = is_weak_password(password)
    if is_weak then
        table.insert(suggestions, "该密码在弱密码字典中，请更换为更独特的密码")
    end

    local has_kb = detect_keyboard_pattern(password)
    if has_kb then
        table.insert(suggestions, "避免使用键盘连续序列（如 qwerty、12345）")
    end

    local has_rep = detect_repeated_chars(password)
    if has_rep then
        table.insert(suggestions, "避免使用大量重复字符")
    end

    local has_seq = detect_sequential_chars(password)
    if has_seq then
        table.insert(suggestions, "避免使用连续的数字或字母序列")
    end

    if #suggestions == 0 then
        table.insert(suggestions, "密码强度良好，继续保持！")
    end

    return suggestions
end

-- ============================================================
-- 打印帮助信息
-- ============================================================
function print_help()
    print("================================================")
    print("  密码强度检测工具 - 安全研究用")
    print("================================================")
    print("")
    print("用法: lua password_check.lua <密码> [选项]")
    print("")
    print("选项:")
    print("  --detail, -d    显示详细分析报告")
    print("  --help, -h      显示帮助信息")
    print("")
    print("功能:")
    print("  - 密码强度评分 (0-100 分)")
    print("  - 弱密码字典检测")
    print("  - 密码复杂度分析")
    print("  - 键盘序列检测")
    print("  - 重复字符检测")
    print("  - 连续字符检测")
    print("  - 密码改进建议")
    print("")
    print("示例:")
    print("  lua password_check.lua \"MyP@ssw0rd\"")
    print("  lua password_check.lua \"123456\" --detail")
    print("================================================")
end

-- ============================================================
-- 主程序入口
-- ============================================================
function main(...)
    local args = {...}

    -- 解析参数
    local password = nil
    local show_detail = false

    for _, arg in ipairs(args) do
        if arg == "--help" or arg == "-h" then
            print_help()
            return
        elseif arg == "--detail" or arg == "-d" then
            show_detail = true
        elseif not password then
            password = arg
        end
    end

    if not password then
        print("[错误] 请提供要检测的密码")
        print("输入 'lua password_check.lua --help' 查看帮助")
        return
    end

    print("================================================================")
    print("  密码强度检测报告")
    print("================================================================")
    print("")

    -- 评分
    local score, level, details = score_password(password)

    print("  密码: " .. string.rep("*", math.min(#password, 20)) .. " (" .. #password .. " 位)")
    print("")
    print("  强度评分: " .. score .. " / 100")
    print("  安全等级: " .. level)
    print("")

    -- 强度条
    local bar_len = 30
    local filled = math.floor(score / 100 * bar_len)
    local bar = "[" .. string.rep("#", filled) .. string.rep("-", bar_len - filled) .. "]"
    print("  " .. bar)
    print("")

    if show_detail then
        -- 详细评分项
        print("----------------------------------------------------------------")
        print("  评分明细")
        print("----------------------------------------------------------------")
        for _, detail in ipairs(details) do
            print("  " .. detail)
        end
        print("")

        -- 复杂度分析
        local analysis = analyze_complexity(password)
        print("----------------------------------------------------------------")
        print("  复杂度分析")
        print("----------------------------------------------------------------")
        print("  长度:         " .. analysis.length .. " 位")
        print("  小写字母:     " .. analysis.lower_count .. " 个 " .. (analysis.has_lower and "[是]" or "[否]"))
        print("  大写字母:     " .. analysis.upper_count .. " 个 " .. (analysis.has_upper and "[是]" or "[否]"))
        print("  数字:         " .. analysis.digit_count .. " 个 " .. (analysis.has_digit and "[是]" or "[否]"))
        print("  特殊字符:     " .. analysis.special_count .. " 个 " .. (analysis.has_special and "[是]" or "[否]"))
        print("  唯一字符数:   " .. analysis.unique_chars .. " 个")
        print("  字符类型数:   " .. analysis.char_types .. " 种")
        print("")

        -- 模式检测
        print("----------------------------------------------------------------")
        print("  模式检测")
        print("----------------------------------------------------------------")
        local is_weak, matched = is_weak_password(password)
        print("  弱密码字典:   " .. (is_weak and ("[危险] 匹配: " .. matched) or "[通过]"))

        local has_kb, kb_len, kb_seq = detect_keyboard_pattern(password)
        print("  键盘序列:     " .. (has_kb and ("[警告] " .. kb_seq .. " (" .. kb_len .. " 位)") or "[通过]"))

        local has_rep, rep_count, rep_char = detect_repeated_chars(password)
        print("  重复字符:     " .. (has_rep and ("[警告] '" .. rep_char .. "' 重复 " .. rep_count .. " 次") or "[通过]"))

        local has_seq, seq_len = detect_sequential_chars(password)
        print("  连续字符:     " .. (has_seq and ("[警告] 连续 " .. seq_len .. " 个") or "[通过]"))
        print("")
    end

    -- 改进建议
    local suggestions = generate_suggestions(password)
    print("----------------------------------------------------------------")
    print("  改进建议")
    print("----------------------------------------------------------------")
    for i, s in ipairs(suggestions) do
        print("  " .. i .. ". " .. s)
    end
    print("")
    print("================================================================")
    print("  提示：本工具评分仅供参考，建议使用专业密码管理器生成密码")
    print("================================================================")
end

-- 运行主程序
main(...)
