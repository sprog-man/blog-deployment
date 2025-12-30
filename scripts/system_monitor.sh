#!/bin/bash
# 系统监控脚本

LOG_FILE="/root/blog-project/logs/system_monitor.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "=== 系统监控报告 - $DATE ===" | tee -a $LOG_FILE
echo "1. 系统负载:" | tee -a $LOG_FILE
uptime | tee -a $LOG_FILE

echo -e "\n2. 内存使用情况:" | tee -a $LOG_FILE
free -h | tee -a $LOG_FILE

echo -e "\n3. 磁盘使用情况:" | tee -a $LOG_FILE
df -h | tee -a $LOG_FILE

echo -e "\n4. 前5个内存占用进程:" | tee -a $LOG_FILE
ps aux --sort=-%mem | head -6 | tee -a $LOG_FILE

echo -e "\n5. 前5个CPU占用进程:" | tee -a $LOG_FILE
ps aux --sort=-%cpu | head -6 | tee -a $LOG_FILE

echo -e "\n6. 网络连接统计:" | tee -a $LOG_FILE
ss -s | tee -a $LOG_FILE

echo -e "\n7. Nginx进程状态 (如果运行):" | tee -a $LOG_FILE
if systemctl is-active --quiet nginx; then
    systemctl status nginx --no-pager | tail -10 | tee -a $LOG_FILE
else
    echo "Nginx未运行" | tee -a $LOG_FILE
fi

echo -e "\n=== 报告结束 ===\n" | tee -a $LOG_FILE