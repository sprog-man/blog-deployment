#!/bin/bash
# Shell部署脚本 - 简化版

set -e

echo "=== 博客部署脚本 ==="
echo "项目目录: /root/blog-deployment"

# 创建必要目录
echo "创建目录..."
mkdir -p /root/blog-deployment/{blog-content,logs,backups}
mkdir -p /root/blog-deployment/blog-content/{content/posts,static,layouts}

# 检查并安装Hugo
if ! command -v hugo &> /dev/null; then
    echo "安装Hugo..."
    cd /tmp
    wget -q https://github.com/gohugoio/hugo/releases/download/v0.111.3/hugo_0.111.3_Linux-64bit.tar.gz
    tar -xzf hugo_0.111.3_Linux-64bit.tar.gz
    mv hugo /usr/local/bin/
    chmod +x /usr/local/bin/hugo
    rm -f hugo_0.111.3_Linux-64bit.tar.gz
fi

echo "Hugo版本: $(hugo version)"

# 创建Hugo配置文件（如果不存在）
CONFIG_FILE="/root/blog-deployment/blog-content/hugo.toml"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "创建Hugo配置文件..."
    cat > "$CONFIG_FILE" << 'EOF'
baseURL = "http://localhost/"
languageCode = "zh-cn"
title = "我的技术博客"
theme = "ananke"

[params]
  description = "记录技术学习和实践"
  author = "你的名字"
EOF
fi

# 创建示例文章（如果不存在）
POST_FILE="/root/blog-deployment/blog-content/content/posts/welcome.md"
if [ ! -f "$POST_FILE" ]; then
    echo "创建示例文章..."
    cat > "$POST_FILE" << 'EOF'
---
title: "欢迎来到我的博客"
date: 2024-01-01
draft: false
---

# 欢迎！

这是我的第一篇博客文章。
EOF
fi

# 生成静态网站
echo "生成静态网站..."
cd /root/blog-deployment/blog-content
hugo

# 部署到Nginx
echo "部署到Nginx..."
if command -v nginx &> /dev/null; then
    # 确保Nginx运行
    systemctl start nginx 2>/dev/null || true
    systemctl enable nginx 2>/dev/null || true
    
    # 部署网站
    rm -rf /usr/share/nginx/html/*
    cp -r public/* /usr/share/nginx/html/
    
    # 设置权限
    chown -R nginx:nginx /usr/share/nginx/html
    chmod -R 755 /usr/share/nginx/html
    
    # 重启Nginx
    systemctl restart nginx
    
    echo "网站已部署到Nginx"
else
    echo "Nginx未安装，网站生成在: $(pwd)/public"
    echo "安装Nginx: yum install -y nginx"
fi

# 显示访问信息
IP=$(curl -s ifconfig.me 2>/dev/null || echo "localhost")
echo "=== 部署完成 ==="
echo "访问地址: http://$IP"
echo "本地测试: curl http://localhost"