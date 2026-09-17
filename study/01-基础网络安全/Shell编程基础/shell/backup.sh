#!/bin/bash
# backup.sh
# 综合示例：自动备份脚本
# 功能：将指定目录压缩备份到指定位置，支持保留策略和日志记录

set -euo pipefail

# ============================================================
# 配置
# ============================================================
SOURCE_DIR="${1:-/tmp}"         # 要备份的源目录
BACKUP_DIR="${2:-/tmp/backups}" # 备份存放目录
BACKUP_PREFIX="backup"          # 备份文件名前缀
KEEP_DAYS=7                     # 保留天数
KEEP_COUNT=10                   # 保留份数

# ============================================================
# 日志函数
# ============================================================
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

# ============================================================
# 前置检查
# ============================================================
pre_check() {
    log "开始备份检查..."

    # 检查源目录是否存在
    if [[ ! -d "$SOURCE_DIR" ]]; then
        log "错误：源目录不存在 - $SOURCE_DIR"
        exit 1
    fi

    # 创建备份目录
    mkdir -p "$BACKUP_DIR"

    # 检查磁盘空间
    local source_size=$(du -sb "$SOURCE_DIR" | awk '{print $1}')
    local backup_free=$(df -B1 "$BACKUP_DIR" | awk 'NR==2 {print $4}')

    if (( source_size > backup_free )); then
        log "警告：备份目录空间可能不足"
    fi

    log "检查通过：源目录大小 $(du -sh "$SOURCE_DIR" | awk '{print $1}')"
}

# ============================================================
# 执行备份
# ============================================================
do_backup() {
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local hostname=$(hostname)
    local dir_name=$(basename "$SOURCE_DIR")
    local backup_file="${BACKUP_DIR}/${BACKUP_PREFIX}_${dir_name}_${hostname}_${timestamp}.tar.gz"

    log "开始备份：$SOURCE_DIR → $backup_file"

    # 执行打包压缩
    if tar -czf "$backup_file" -C "$(dirname "$SOURCE_DIR")" "$(basename "$SOURCE_DIR")" 2>/dev/null; then
        local size=$(du -h "$backup_file" | awk '{print $1}')
        log "备份成功：$backup_file ($size)"
        BACKUP_RESULT="$backup_file"
        return 0
    else
        log "错误：备份失败"
        rm -f "$backup_file"
        return 1
    fi
}

# ============================================================
# 清理旧备份
# ============================================================
cleanup_old() {
    log "清理旧备份（保留最近 $KEEP_COUNT 份，超过 $KEEP_DAYS 天的也删除）..."

    # 按时间删除（超过 KEEP_DAYS 天）
    local deleted_by_time=0
    while IFS= read -r file; do
        if [[ -f "$file" ]]; then
            rm -f "$file"
            log "  删除过期备份：$(basename "$file")"
            deleted_by_time=$((deleted_by_time + 1))
        fi
    done < <(find "$BACKUP_DIR" -name "${BACKUP_PREFIX}_*.tar.gz" -type f -mtime +$KEEP_DAYS 2>/dev/null)

    # 按数量删除（超过 KEEP_COUNT 份）
    local deleted_by_count=0
    local count=$(find "$BACKUP_DIR" -name "${BACKUP_PREFIX}_*.tar.gz" -type f 2>/dev/null | wc -l)

    if (( count > KEEP_COUNT )); then
        local remove_count=$((count - KEEP_COUNT))
        while IFS= read -r file; do
            if [[ -f "$file" && $remove_count -gt 0 ]]; then
                rm -f "$file"
                log "  删除超出数量备份：$(basename "$file")"
                deleted_by_count=$((deleted_by_count + 1))
                remove_count=$((remove_count - 1))
            fi
        done < <(find "$BACKUP_DIR" -name "${BACKUP_PREFIX}_*.tar.gz" -type f -printf '%T@ %p\n' 2>/dev/null | sort -n | awk '{print $2}')
    fi

    log "清理完成：按时间删除 $deleted_by_time 份，按数量删除 $deleted_by_count 份"
}

# ============================================================
# 统计信息
# ============================================================
show_stats() {
    local total=$(find "$BACKUP_DIR" -name "${BACKUP_PREFIX}_*.tar.gz" -type f 2>/dev/null | wc -l)
    local total_size=$(du -sh "$BACKUP_DIR" 2>/dev/null | awk '{print $1}')

    log "=========================================="
    log "备份统计："
    log "  备份目录：$BACKUP_DIR"
    log "  备份总数：$total 份"
    log "  总大小：$total_size"
    log "=========================================="
}

# ============================================================
# 主函数
# ============================================================
main() {
    log "=========================================="
    log "自动备份脚本启动"
    log "源目录：$SOURCE_DIR"
    log "备份目录：$BACKUP_DIR"
    log "保留天数：$KEEP_DAYS 天"
    log "保留份数：最多 $KEEP_COUNT 份"
    log "=========================================="

    pre_check
    do_backup
    cleanup_old
    show_stats

    log "备份任务完成！"
}

main "$@"
