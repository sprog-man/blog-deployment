#!/usr/bin/env python3
"""
静态博客自动部署脚本
功能：拉取代码、生成静态文件、部署到Nginx
"""

import os
import sys
import shutil
import subprocess
import logging
from datetime import datetime
import argparse

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/root/blog-project/logs/deploy.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class BlogDeployer:
    def __init__(self, config):
        self.config = config
        self.setup_directories()
        
    def setup_directories(self):
        """创建必要的目录"""
        dirs = [
            self.config['blog_repo_dir'],
            self.config['backup_dir'],
            self.config['log_dir']
        ]
        
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
            logger.info(f"确保目录存在: {dir_path}")
    
    def run_command(self, cmd, cwd=None):
        """执行shell命令"""
        logger.info(f"执行命令: {cmd}")
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                logger.info(f"命令成功: {cmd}")
                if result.stdout:
                    logger.debug(f"输出: {result.stdout}")
            else:
                logger.error(f"命令失败: {cmd}")
                logger.error(f"错误: {result.stderr}")
                return False
                
            return True
        except subprocess.TimeoutExpired:
            logger.error(f"命令超时: {cmd}")
            return False
        except Exception as e:
            logger.error(f"执行命令异常: {e}")
            return False
    
    def backup_current_site(self):
        """备份当前网站"""
        if not os.path.exists(self.config['nginx_webroot']):
            return True
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(
            self.config['backup_dir'], 
            f"backup_{timestamp}"
        )
        
        try:
            shutil.copytree(self.config['nginx_webroot'], backup_path)
            logger.info(f"网站已备份到: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"备份失败: {e}")
            return False
    
    def clone_or_pull_repo(self):
        """克隆或拉取博客仓库"""
        if os.path.exists(os.path.join(self.config['blog_repo_dir'], '.git')):
            # 已有仓库，执行拉取
            cmds = [
                "git reset --hard HEAD",
                "git clean -fd",
                f"git pull origin {self.config['git_branch']}"
            ]
        else:
            # 克隆新仓库
            cmds = [
                f"git clone {self.config['git_repo_url']} .",
                f"git checkout {self.config['git_branch']}"
            ]
        
        for cmd in cmds:
            if not self.run_command(cmd, self.config['blog_repo_dir']):
                return False
        return True
    
    def install_hugo(self):
        """安装Hugo静态网站生成器"""
        hugo_path = "/usr/local/bin/hugo"
        
        if os.path.exists(hugo_path):
            # 检查Hugo版本
            result = subprocess.run(
                "hugo version",
                shell=True,
                capture_output=True,
                text=True
            )
            if "hugo v" in result.stdout:
                logger.info(f"Hugo已安装: {result.stdout.strip()}")
                return True
        
        # 下载并安装Hugo
        logger.info("正在安装Hugo...")
        install_cmds = [
            "wget https://github.com/gohugoio/hugo/releases/download/v0.111.3/hugo_0.111.3_Linux-64bit.tar.gz",
            "tar -xzf hugo_0.111.3_Linux-64bit.tar.gz",
            "mv hugo /usr/local/bin/",
            "chmod +x /usr/local/bin/hugo",
            "rm -f hugo_0.111.3_Linux-64bit.tar.gz LICENSE README.md"
        ]
        
        for cmd in install_cmds:
            if not self.run_command(cmd, "/tmp"):
                return False
        
        # 验证安装
        return self.run_command("hugo version")
    
    def generate_static_site(self):
        """生成静态网站"""
        # 检查Hugo项目配置
        config_file = os.path.join(
            self.config['blog_repo_dir'], 
            'hugo.toml'
        )
        if not os.path.exists(config_file):
            config_file = os.path.join(
                self.config['blog_repo_dir'], 
                'config.toml'
            )
        
        if not os.path.exists(config_file):
            logger.error("未找到Hugo配置文件")
            return False
        
        # 生成静态文件
        return self.run_command(
            "hugo --minify --cleanDestinationDir",
            self.config['blog_repo_dir']
        )
    
    def deploy_to_nginx(self):
        """部署到Nginx目录"""
        # 清理旧文件
        if os.path.exists(self.config['nginx_webroot']):
            shutil.rmtree(self.config['nginx_webroot'])
        
        # 复制新文件
        public_dir = os.path.join(
            self.config['blog_repo_dir'], 
            'public'
        )
        
        if not os.path.exists(public_dir):
            logger.error(f"未找到生成的静态文件: {public_dir}")
            return False
        
        try:
            shutil.copytree(public_dir, self.config['nginx_webroot'])
            logger.info(f"已部署到: {self.config['nginx_webroot']}")
            
            # 设置正确的权限
            self.run_command(f"chown -R nginx:nginx {self.config['nginx_webroot']}")
            self.run_command(f"chmod -R 755 {self.config['nginx_webroot']}")
            
            return True
        except Exception as e:
            logger.error(f"部署失败: {e}")
            return False
    
    def restart_nginx(self):
        """重启Nginx服务"""
        return self.run_command("systemctl restart nginx")
    
    def check_nginx_status(self):
        """检查Nginx状态"""
        return self.run_command("systemctl is-active --quiet nginx")
    
    def deploy(self):
        """执行完整的部署流程"""
        logger.info("开始部署流程...")
        
        steps = [
            ("备份当前网站", self.backup_current_site),
            ("克隆/拉取代码", self.clone_or_pull_repo),
            ("安装Hugo", self.install_hugo),
            ("生成静态网站", self.generate_static_site),
            ("部署到Nginx", self.deploy_to_nginx),
            ("重启Nginx", self.restart_nginx),
            ("检查Nginx状态", self.check_nginx_status)
        ]
        
        for step_name, step_func in steps:
            logger.info(f"执行步骤: {step_name}")
            if not step_func():
                logger.error(f"步骤失败: {step_name}")
                return False
        
        logger.info("部署成功完成!")
        return True

def main():
    parser = argparse.ArgumentParser(description='静态博客自动部署脚本')
    parser.add_argument('--config', default='deploy_config.json', 
                       help='配置文件路径')
    parser.add_argument('--repo-url', help='Git仓库URL')
    parser.add_argument('--dry-run', action='store_true', 
                       help='只显示将要执行的操作，不实际执行')
    
    args = parser.parse_args()
    
    # 默认配置
    config = {
        'git_repo_url': args.repo_url or 'https://github.com/yourusername/blog-content.git',
        'git_branch': 'main',
        'blog_repo_dir': '/root/blog-project/blog-content',
        'nginx_webroot': '/usr/share/nginx/html',
        'backup_dir': '/root/blog-project/backups',
        'log_dir': '/root/blog-project/logs'
    }
    
    # 如果有配置文件，从文件加载
    if os.path.exists(args.config):
        try:
            import json
            with open(args.config, 'r') as f:
                file_config = json.load(f)
                config.update(file_config)
        except Exception as e:
            logger.warning(f"读取配置文件失败: {e}")
    
    if args.dry_run:
        logger.info("DRY RUN模式 - 不会实际执行操作")
        logger.info(f"配置: {config}")
        return
    
    deployer = BlogDeployer(config)
    
    if deployer.deploy():
        logger.info("部署成功!")
        sys.exit(0)
    else:
        logger.error("部署失败!")
        sys.exit(1)

if __name__ == "__main__":
    main()