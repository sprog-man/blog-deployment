#!/usr/bin/env python3
"""
博客部署脚本 - 统一路径版本
在服务器上运行：python3 /root/blog-deployment/scripts/deploy.py
"""

import os
import sys
import subprocess
import json
from datetime import datetime

class Deployer:
    def __init__(self):
        # 基础路径 - 在服务器上是固定的
        self.base_dir = "/root/blog-deployment"
        self.blog_dir = os.path.join(self.base_dir, "blog-content")
        self.nginx_dir = "/usr/share/nginx/html"
        
        # 创建日志目录
        self.log_dir = os.path.join(self.base_dir, "logs")
        self.backup_dir = os.path.join(self.base_dir, "backups")
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # 日志文件
        self.log_file = os.path.join(self.log_dir, "deploy.log")
    
    def log(self, message):
        """记录日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        
        # 写入日志文件
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_msg + '\n')
    
    def run(self, cmd, cwd=None):
        """执行命令"""
        self.log(f"执行: {cmd}")
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            if result.returncode == 0:
                if result.stdout:
                    self.log(f"输出: {result.stdout.strip()}")
                return True
            else:
                self.log(f"错误: {result.stderr.strip()}")
                return False
        except Exception as e:
            self.log(f"异常: {e}")
            return False
    
    def check_environment(self):
        """检查环境"""
        self.log("检查环境...")
        
        checks = [
            ("Python3", "python3 --version"),
            ("Git", "git --version"),
            ("Hugo", "hugo version"),
            ("Nginx", "nginx -v 2>&1 | head -1"),
        ]
        
        for name, cmd in checks:
            if self.run(cmd):
                self.log(f"✓ {name} 已安装")
            else:
                self.log(f"✗ {name} 未安装")
        
        return True
    
    def create_blog_content(self):
        """创建博客内容（如果不存在）"""
        self.log("检查博客内容...")
        
        # 创建Hugo配置文件
        hugo_config = os.path.join(self.blog_dir, "hugo.toml")
        if not os.path.exists(hugo_config):
            self.log("创建Hugo配置文件...")
            with open(hugo_config, 'w', encoding='utf-8') as f:
                f.write('''baseURL = "http://localhost/"
languageCode = "zh-cn"
title = "我的技术博客"
theme = "ananke"

[params]
  description = "记录技术学习和实践"
  author = "你的名字"
''')
        
        # 创建目录结构
        os.makedirs(os.path.join(self.blog_dir, "content", "posts"), exist_ok=True)
        
        # 创建示例文章
        post_file = os.path.join(self.blog_dir, "content", "posts", "welcome.md")
        if not os.path.exists(post_file):
            self.log("创建示例文章...")
            with open(post_file, 'w', encoding='utf-8') as f:
                f.write('''---
title: "欢迎来到我的博客"
date: 2024-01-01
draft: false
tags: ["博客", "Hugo", "Nginx"]
---

# 欢迎！

这是我的第一篇博客文章。

## 技术栈

- Hugo 静态网站生成器
- Nginx Web服务器
- Python 自动化脚本

感谢访问！
''')
        
        return True
    
    def build_site(self):
        """生成静态网站"""
        self.log("生成静态网站...")
        
        if not os.path.exists(self.blog_dir):
            self.create_blog_content()
        
        return self.run("hugo", self.blog_dir)
    
    def deploy_to_nginx(self):
        """部署到Nginx"""
        self.log("部署到Nginx...")
        
        public_dir = os.path.join(self.blog_dir, "public")
        if not os.path.exists(public_dir):
            self.log("错误：public目录不存在，请先生成网站")
            return False
        
        # 确保Nginx运行
        self.run("systemctl start nginx 2>/dev/null || true")
        self.run("systemctl enable nginx 2>/dev/null || true")
        
        # 部署网站
        cmds = [
            f"rm -rf {self.nginx_dir}/*",
            f"cp -r {public_dir}/* {self.nginx_dir}/",
            f"chown -R nginx:nginx {self.nginx_dir}",
            f"chmod -R 755 {self.nginx_dir}"
        ]
        
        for cmd in cmds:
            if not self.run(cmd):
                return False
        
        return True
    
    def main(self):
        """主部署流程"""
        self.log("=" * 50)
        self.log("开始博客部署")
        self.log("=" * 50)
        
        steps = [
            ("检查环境", self.check_environment),
            ("准备博客内容", self.create_blog_content),
            ("生成静态网站", self.build_site),
            ("部署到Nginx", self.deploy_to_nginx),
        ]
        
        for step_name, step_func in steps:
            self.log(f"步骤: {step_name}")
            if not step_func():
                self.log(f"部署失败: {step_name}")
                return False
        
        # 获取服务器IP
        ip_result = subprocess.run(
            "curl -s ifconfig.me",
            shell=True,
            capture_output=True,
            text=True
        )
        server_ip = ip_result.stdout.strip() if ip_result.returncode == 0 else "localhost"
        
        self.log("=" * 50)
        self.log("部署成功完成!")
        self.log(f"访问地址: http://{server_ip}")
        self.log(f"本地测试: curl http://localhost")
        self.log("=" * 50)
        
        return True

if __name__ == "__main__":
    deployer = Deployer()
    if deployer.main():
        sys.exit(0)
    else:
        sys.exit(1)