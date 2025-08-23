#!/usr/bin/env python3
"""
启动审核界面的便捷脚本
"""

import os
import sys
import subprocess
import webbrowser
import time

def main():
    """启动审核界面"""
    print("🤖 AI洞察助手 - 审核界面启动器")
    print("=" * 50)
    
    # 检查环境
    if not os.path.exists('.env'):
        print("❌ 未找到 .env 配置文件")
        print("请先复制 env.example 为 .env 并配置必要的API密钥")
        return 1
    
    # 检查数据库
    if not os.path.exists('app.db'):
        print("⚠️  未找到数据库文件，正在初始化...")
        try:
            subprocess.run([sys.executable, 'init_db.py'], check=True)
            print("✅ 数据库初始化完成")
        except subprocess.CalledProcessError:
            print("❌ 数据库初始化失败")
            return 1
    
    # 启动Flask应用
    print("🚀 正在启动审核界面...")
    
    try:
        # 启动Flask应用
        process = subprocess.Popen([
            sys.executable, 'review_app/app.py'
        ])
        
        # 等待应用启动
        print("⏳ 等待应用启动...")
        time.sleep(3)
        
        # 打开浏览器
        print("🌐 正在打开浏览器...")
        webbrowser.open('http://localhost:9000')
        
        print("✅ 审核界面已启动！")
        print("📱 访问地址: http://localhost:9000")
        print("⏹️  按 Ctrl+C 停止服务")
        
        # 等待用户中断
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n⏹️  正在停止服务...")
            process.terminate()
            process.wait()
            print("✅ 服务已停止")
        
        return 0
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
