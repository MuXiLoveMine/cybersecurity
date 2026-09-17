#!/bin/bash
# batch_rename.sh
# 综合示例：批量重命名脚本
# 功能：批量重命名文件，支持前缀、后缀、序号、替换、大小写转换

set -euo pipefail

# ============================================================
# 帮助信息
# ============================================================
usage() {
    cat << 'EOF'
批量重命名工具

用法：
  batch_rename.sh [选项] <目录> <模式>

选项：
  -p, --prefix <前缀>    添加前缀
  -s, --suffix <后缀>    添加后缀（扩展名前）
  -n, --number           添加序号（如 file_001.jpg）
  -w, --width <数字>     序号位数，默认 3
      --start <数字>     序号起始值，默认 1
  -r, --replace <旧:新>  替换文件名中的字符串
  -u, --upper            文件名转大写
  -l, --lower            文件名转小写
  -e, --ext <扩展名>     只处理指定扩展名的文件（可多次使用）
  -d, --dry-run          预览模式，不实际修改
  -h, --help             显示帮助

示例：
  # 为所有 jpg 文件添加前缀 vacation_
  ./batch_rename.sh -p vacation_ -e jpg ./photos

  # 批量序号重命名（photo_001.jpg, photo_002.jpg...）
  ./batch_rename.sh -p photo_ -n -w 3 ./photos

  # 将文件名中的空格替换为下划线
  ./batch_rename.sh -r " :_" ./files

  # 预览执行效果（不实际修改）
  ./batch_rename.sh -d -l ./files

EOF
    exit 0
}

# ============================================================
# 参数解析
# ============================================================
PREFIX=""
SUFFIX=""
ADD_NUMBER=0
NUMBER_WIDTH=3
NUMBER_START=1
REPLACE_FROM=""
REPLACE_TO=""
TO_UPPER=0
TO_LOWER=0
DRY_RUN=0
TARGET_DIR=""
EXTENSIONS=()

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -h|--help)
                usage
                ;;
            -p|--prefix)
                PREFIX="$2"
                shift 2
                ;;
            -s|--suffix)
                SUFFIX="$2"
                shift 2
                ;;
            -n|--number)
                ADD_NUMBER=1
                shift
                ;;
            -w|--width)
                NUMBER_WIDTH="$2"
                shift 2
                ;;
            --start)
                NUMBER_START="$2"
                shift 2
                ;;
            -r|--replace)
                REPLACE_FROM="${2%%:*}"
                REPLACE_TO="${2#*:}"
                shift 2
                ;;
            -u|--upper)
                TO_UPPER=1
                shift
                ;;
            -l|--lower)
                TO_LOWER=1
                shift
                ;;
            -e|--ext)
                EXTENSIONS+=("$2")
                shift 2
                ;;
            -d|--dry-run)
                DRY_RUN=1
                shift
                ;;
            -*)
                echo "错误：未知选项 $1"
                usage
                ;;
            *)
                if [[ -z "$TARGET_DIR" ]]; then
                    TARGET_DIR="$1"
                fi
                shift
                ;;
        esac
    done
}

# ============================================================
# 验证参数
# ============================================================
validate() {
    if [[ -z "$TARGET_DIR" ]]; then
        echo "错误：请指定目标目录"
        usage
    fi

    if [[ ! -d "$TARGET_DIR" ]]; then
        echo "错误：目录不存在 - $TARGET_DIR"
        exit 1
    fi

    if (( TO_UPPER == 1 && TO_LOWER == 1 )); then
        echo "错误：--upper 和 --lower 不能同时使用"
        exit 1
    fi
}

# ============================================================
# 检查文件扩展名是否匹配
# ============================================================
match_ext() {
    local file="$1"
    local ext="${file##*.}"

    # 没有指定扩展名，全部匹配
    if [[ ${#EXTENSIONS[@]} -eq 0 ]]; then
        return 0
    fi

    for e in "${EXTENSIONS[@]}"; do
        if [[ "${ext,,}" == "${e,,}" ]]; then
            return 0
        fi
    done
    return 1
}

# ============================================================
# 重命名单个文件
# ============================================================
rename_file() {
    local old_name="$1"
    local dir="$2"
    local index="$3"

    # 分离文件名和扩展名
    local base="${old_name%.*}"
    local ext=""
    if [[ "$old_name" == *.* ]]; then
        ext=".${old_name##*.}"
    fi

    local new_base="$base"

    # 替换
    if [[ -n "$REPLACE_FROM" ]]; then
        new_base="${new_base//$REPLACE_FROM/$REPLACE_TO}"
    fi

    # 大小写转换
    if (( TO_UPPER == 1 )); then
        new_base="${new_base^^}"
        ext="${ext^^}"
    elif (( TO_LOWER == 1 )); then
        new_base="${new_base,,}"
        ext="${ext,,}"
    fi

    # 添加序号
    if (( ADD_NUMBER == 1 )); then
        local num=$(( NUMBER_START + index - 1 ))
        local formatted_num=$(printf "%0${NUMBER_WIDTH}d" "$num")
        new_base="${new_base}_${formatted_num}"
    fi

    # 添加前缀
    if [[ -n "$PREFIX" ]]; then
        new_base="${PREFIX}${new_base}"
    fi

    # 添加后缀
    if [[ -n "$SUFFIX" ]]; then
        new_base="${new_base}${SUFFIX}"
    fi

    local new_name="${new_base}${ext}"

    # 如果名字没变，跳过
    if [[ "$old_name" == "$new_name" ]]; then
        return 1
    fi

    echo "  $old_name  →  $new_name"

    if (( DRY_RUN == 0 )); then
        mv "$dir/$old_name" "$dir/$new_name"
    fi

    return 0
}

# ============================================================
# 主函数
# ============================================================
main() {
    parse_args "$@"
    validate

    echo "批量重命名工具"
    echo "=========================================="
    echo "目标目录：$TARGET_DIR"
    [[ -n "$PREFIX" ]] && echo "前缀：$PREFIX"
    [[ -n "$SUFFIX" ]] && echo "后缀：$SUFFIX"
    (( ADD_NUMBER == 1 )) && echo "序号：位数=$NUMBER_WIDTH，起始=$NUMBER_START"
    [[ -n "$REPLACE_FROM" ]] && echo "替换：'$REPLACE_FROM' → '$REPLACE_TO'"
    (( TO_UPPER == 1 )) && echo "转大写"
    (( TO_LOWER == 1 )) && echo "转小写"
    [[ ${#EXTENSIONS[@]} -gt 0 ]] && echo "指定扩展名：${EXTENSIONS[*]}"
    (( DRY_RUN == 1 )) && echo "模式：预览（不实际修改）"
    echo "=========================================="
    echo ""

    # 收集文件列表
    local files=()
    for f in "$TARGET_DIR"/*; do
        if [[ -f "$f" ]]; then
            local name=$(basename "$f")
            if match_ext "$name"; then
                files+=("$name")
            fi
        fi
    done

    if [[ ${#files[@]} -eq 0 ]]; then
        echo "没有找到匹配的文件"
        exit 0
    fi

    echo "找到 ${#files[@]} 个文件，开始处理："
    echo ""

    local count=0
    for i in "${!files[@]}"; do
        if rename_file "${files[$i]}" "$TARGET_DIR" $((i + 1)); then
            count=$((count + 1))
        fi
    done

    echo ""
    if (( DRY_RUN == 1 )); then
        echo "预览完成，将重命名 $count 个文件（未实际执行）"
    else
        echo "完成，共重命名 $count 个文件"
    fi
}

main "$@"
