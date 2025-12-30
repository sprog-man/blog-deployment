#!/bin/bash
# 日志分析脚本

LOG_PATH="/var/log/nginx"
ERROR_LOG="$LOG_PATH/error.log"
ACCESS_LOG="$LOG_PATH/access.log"
REPORT_FILE="/root/blog-project/logs/log_report_$(date +%Y%m%d).txt"

echo "=== Nginx日志分析报告 - $(date '+%Y-%m-%d %H:%M:%S') ===" > $REPORT_FILE

if [ -f "$ERROR_LOG" ]; then
    echo -e "\n1. 今日错误日志统计:" >> $REPORT_FILE
    grep "$(date '+%d/%b/%Y')" $ERROR_LOG | wc -l >> $REPORT_FILE
    
    echo -e "\n2. 最常见的5个错误:" >> $REPORT_FILE
    grep "$(date '+%d/%b/%Y')" $ERROR_LOG | awk -F']' '{print $2}' | sort | uniq -c | sort -rn | head -5 >> $REPORT_FILE
fi

if [ -f "$ACCESS_LOG" ]; then
    echo -e "\n3. 今日访问量统计:" >> $REPORT_FILE
    grep "$(date '+%d/%b/%Y')" $ACCESS_LOG | wc -l >> $REPORT_FILE
    
    echo -e "\n4. 访问最多的5个IP:" >> $REPORT_FILE
    awk '{print $1}' $ACCESS_LOG | sort | uniq -c | sort -rn | head -5 >> $REPORT_FILE
    
    echo -e "\n5. 最常访问的5个页面:" >> $REPORT_FILE
    awk '{print $7}' $ACCESS_LOG | sort | uniq -c | sort -rn | head -5 >> $REPORT_FILE
fi

echo -e "\n6. 系统日志关键错误 (最近1小时):" >> $REPORT_FILE
journalctl --since "1 hour ago" -p err | tail -10 >> $REPORT_FILE

echo "报告已生成: $REPORT_FILE"