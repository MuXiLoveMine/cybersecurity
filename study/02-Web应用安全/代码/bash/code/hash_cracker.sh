#!/bin/bash
# ============================================================
# hash_cracker.sh - 哈希破解工具
# 支持: MD5, SHA1, SHA256, SHA512
# 用法: ./hash_cracker.sh <哈希值> <字典文件> [哈希类型]
# ============================================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 参数检查
if [ $# -lt 2 ]; then
    echo "用法: $0 <哈希值> <字典文件> [哈希类型]"
    echo ""
    echo "支持的哈希类型:"
    echo "  md5    - MD5 哈希 (32位)"
    echo "  sha1   - SHA1 哈希 (40位)"
    echo "  sha256 - SHA256 哈希 (64位)"
    echo "  sha512 - SHA512 哈希 (128位)"
    echo "  auto   - 自动检测 (默认)"
    echo ""
    echo "示例: $0 5f4dcc3b5aa765d61d8327deb882cf99 wordlist.txt"
    echo "示例: $0 e10adc3949ba59abbe56e057f20f883e rockyou.txt md5"
    exit 1
fi

HASH="$1"
WORDLIST="$2"
HASH_TYPE="${3:-auto}"

# 检查字典文件
if [ ! -f "$WORDLIST" ]; then
    echo -e "${RED}[错误] 字典文件不存在: $WORDLIST${NC}"
    exit 1
fi

echo "========================================"
echo "  Bash 哈希破解工具"
echo "========================================"
echo -e "目标哈希: ${YELLOW}$HASH${NC}"

# 自动检测哈希类型
detect_hash_type() {
    local hash="$1"
    local len=${#hash}
    
    case "$len" in
        32)
            # 检查是否为十六进制
            if [[ "$hash" =~ ^[a-fA-F0-9]{32}$ ]]; then
                echo "md5"
            else
                echo "unknown"
            fi
            ;;
        40)
            if [[ "$hash" =~ ^[a-fA-F0-9]{40}$ ]]; then
                echo "sha1"
            else
                echo "unknown"
            fi
            ;;
        64)
            if [[ "$hash" =~ ^[a-fA-F0-9]{64}$ ]]; then
                echo "sha256"
            else
                echo "unknown"
            fi
            ;;
        128)
            if [[ "$hash" =~ ^[a-fA-F0-9]{128}$ ]]; then
                echo "sha512"
            else
                echo "unknown"
            fi
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

# 确定哈希类型
if [ "$HASH_TYPE" = "auto" ]; then
    HASH_TYPE=$(detect_hash_type "$HASH")
    if [ "$HASH_TYPE" = "unknown" ]; then
        echo -e "${RED}[错误] 无法自动检测哈希类型，请手动指定${NC}"
        exit 1
    fi
    echo -e "检测到哈希类型: ${GREEN}$HASH_TYPE${NC}"
else
    echo -e "哈希类型: ${GREEN}$HASH_TYPE${NC}"
fi

# 统一转为小写
HASH=$(echo "$HASH" | tr '[:upper:]' '[:lower:]')

echo -e "字典文件: ${YELLOW}$WORDLIST${NC}"
echo "========================================"
echo ""

# 哈希计算函数
compute_hash() {
    local input="$1"
    local type="$2"
    
    case "$type" in
        md5)
            echo -n "$input" | md5sum 2>/dev/null | awk '{print $1}'
            ;;
        sha1)
            echo -n "$input" | sha1sum 2>/dev/null | awk '{print $1}'
            ;;
        sha256)
            echo -n "$input" | sha256sum 2>/dev/null | awk '{print $1}'
            ;;
        sha512)
            echo -n "$input" | sha512sum 2>/dev/null | awk '{print $1}'
            ;;
        *)
            echo ""
            ;;
    esac
}

# 检查哈希工具是否可用
check_tools() {
    case "$HASH_TYPE" in
        md5)
            command -v md5sum &>/dev/null || command -v md5 &>/dev/null
            ;;
        sha1)
            command -v sha1sum &>/dev/null || command -v shasum &>/dev/null
            ;;
        sha256)
            command -v sha256sum &>/dev/null || command -v shasum &>/dev/null
            ;;
        sha512)
            command -v sha512sum &>/dev/null || command -v shasum &>/dev/null
            ;;
    esac
}

if ! check_tools; then
    echo -e "${RED}[错误] 系统缺少所需的哈希计算工具${NC}"
    exit 1
fi

# 统计字典行数
total=$(wc -l < "$WORDLIST")
echo -e "字典条目数: ${YELLOW}$total${NC}"
echo ""

# 破解主循环
found=false
password=""
count=0
start_time=$(date +%s)

while IFS= read -r line; do
    # 跳过空行
    [ -z "$line" ] && continue
    
    count=$((count + 1))
    
    # 显示进度
    if [ $((count % 1000)) -eq 0 ]; then
        current_time=$(date +%s)
        elapsed=$((current_time - start_time))
        if [ $elapsed -gt 0 ]; then
            speed=$((count / elapsed))
            printf "\r进度: %d/%d (%.2f%%)  速度: %d 行/秒  当前: %-30s" \
                "$count" "$total" "$((count * 100 / total))" "$speed" "$line"
        fi
    fi
    
    # 计算哈希并比较
    computed=$(compute_hash "$line" "$HASH_TYPE")
    
    if [ "$computed" = "$HASH" ]; then
        found=true
        password="$line"
        break
    fi
    
done < "$WORDLIST"

echo ""
echo ""
echo "========================================"
echo "  破解结果"
echo "========================================"

if $found; then
    end_time=$(date +%s)
    elapsed=$((end_time - start_time))
    
    echo -e "  ${GREEN}[+] 破解成功！${NC}"
    echo -e "  哈希: ${YELLOW}$HASH${NC}"
    echo -e "  明文: ${GREEN}$password${NC}"
    echo -e "  尝试次数: $count"
    echo -e "  耗时: ${elapsed} 秒"
else
    echo -e "  ${RED}[-] 破解失败${NC}"
    echo -e "  已尝试: $count 个密码"
    echo -e "  ${YELLOW}[!] 密码不在字典中${NC}"
fi

echo ""
echo "哈希破解完成。"
