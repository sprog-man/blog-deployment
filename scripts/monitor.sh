#!/bin/bash
# 系统监控脚本

LOG_DIR="/root/blog-deployment/logs"
REPORT_FILE="$LOG_DIR/monitor_$(date +%Y%m%d_%H%M%S).txt"

mkdir -p "$LOG_DIR"

echo "=== 系统监控报告 ===" | tee "$REPORT_FILE"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

echo "1. 系统信息:" | tee -a "$REPORT_FILE"
echo "主机名: $(hostname)" | tee -a "$REPORT_FILE"
echo "内核: $(uname -r)" | tee -a "$REPORT_FILE"
echo "系统: $(cat /etc/redhat-release 2>/dev/null || echo 'Unknown')" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

echo "2. 系统负载:" | tee -a "$REPORT_FILE"
uptime | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

echo "3. 内存使用:" | tee -a "$REPORT_FILE"
free -h | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

echo "4. 磁盘使用:" | tee -a "$REPORT_FILE"
df -h | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

echo "5. 服务状态:" | tee -a "$REPORT_FILE"
echo "Nginx: $(systemctl is-active nginx 2>/dev/null || echo '未安装')" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

echo "6. 网站状态:" | tee -a "$REPORT_FILE"
if curl -s -o /dev/null -w "%{http_code}" http://localhost > /dev/null 2>&1; then
    echo "网站: 正常 (HTTP 200)" | tee -a "$REPORT_FILE"
else
    echo "网站: 异常" | tee -a "$REPORT_FILE"
fi
echo "" | tee -a "$REPORT_FILE"

echo "7. 最近部署:" | tee -a "$REPORT_FILE"
if [ -f "/root/blog-deployment/logs/deploy.log" ]; then
    echo "最后部署时间:" | tee -a "$REPORT_FILE"
    tail -3 "/root/blog-deployment/logs/deploy.log" | tee -a "$REPORT_FILE"
else
    echo "无部署记录" | tee -a "$REPORT_FILE"
fi
echo "" | tee -a "$REPORT_FILE"

echo "报告已保存: $REPORT_FILE"