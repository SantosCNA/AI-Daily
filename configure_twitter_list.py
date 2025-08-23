#!/usr/bin/env python3
"""
Twitter List配置脚本
帮助用户配置Twitter List ID并更新数据库
"""

import os
import sys
from dotenv import load_dotenv

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import SessionLocal, SourceConfig

# 加载环境变量
load_dotenv()


def check_twitter_config():
    """检查Twitter API配置"""
    print("🔍 检查Twitter API配置...")
    
    bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
    api_key = os.getenv('TWITTER_API_KEY')
    api_secret = os.getenv('TWITTER_API_SECRET')
    
    if not bearer_token or not api_key or not api_secret:
        print("❌ Twitter API配置不完整")
        print("请检查 .env 文件中的以下配置:")
        print("  TWITTER_BEARER_TOKEN")
        print("  TWITTER_API_KEY") 
        print("  TWITTER_API_SECRET")
        return False
    
    print("✅ Twitter API配置完整")
    return True


def get_current_list_id():
    """获取当前配置的List ID"""
    session = SessionLocal()
    
    try:
        source = session.query(SourceConfig).filter_by(
            source_name='AI KOL Twitter List'
        ).first()
        
        if source:
            current_id = source.source_url
            if current_id == "your_twitter_list_id_here":
                return None
            return current_id
        else:
            return None
            
    except Exception as e:
        print(f"❌ 获取当前List ID失败: {e}")
        return None
    finally:
        session.close()


def update_list_id(new_list_id):
    """更新List ID"""
    session = SessionLocal()
    
    try:
        source = session.query(SourceConfig).filter_by(
            source_name='AI KOL Twitter List'
        ).first()
        
        if source:
            source.source_url = new_list_id
            session.commit()
            print(f"✅ 成功更新List ID为: {new_list_id}")
            return True
        else:
            print("❌ 未找到Twitter List信源配置")
            return False
            
    except Exception as e:
        print(f"❌ 更新List ID失败: {e}")
        session.rollback()
        return False
    finally:
        session.close()


def show_twitter_list_guide():
    """显示Twitter List创建指南"""
    print("\n📋 Twitter List创建指南:")
    print("=" * 50)
    print("1. 登录Twitter账户")
    print("2. 点击左侧菜单的 'Lists'")
    print("3. 点击 'Create new List'")
    print("4. 输入列表名称: 'AI KOL'")
    print("5. 选择隐私设置 (建议选择 'Private')")
    print("6. 点击 'Next' 创建列表")
    print("\n📝 添加AI领域专家到列表:")
    print("推荐添加以下KOL:")
    print("  • @karpathy (Andrej Karpathy)")
    print("  • @ylecun (Yann LeCun)")
    print("  • @AndrewYNg (Andrew Ng)")
    print("  • @sama (Sam Altman)")
    print("  • @gdb (Geoffrey Hinton)")
    print("  • @jasonwei (Jason Wei)")
    print("  • @JimFan (Jim Fan)")
    print("  • @_akhaliq (Aran Komatsuzaki)")
    print("  • @rowancheung (Rowan Cheung)")
    print("  • @alexandra_amos (Alexandra Amos)")
    print("  • @mckaywrigley (McKay Wrigley)")
    print("  • @lennysan (Lenny Rachitsky)")
    print("\n🔍 获取List ID:")
    print("1. 访问您创建的列表页面")
    print("2. 从URL中提取List ID")
    print("   例如: https://twitter.com/i/lists/1234567890")
    print("   List ID就是: 1234567890")


def main():
    """主函数"""
    print("🐦 Twitter List配置工具")
    print("=" * 30)
    
    # 检查Twitter API配置
    if not check_twitter_config():
        print("\n请先配置Twitter API密钥，然后重新运行此脚本")
        return
    
    # 获取当前List ID
    current_id = get_current_list_id()
    
    if current_id:
        print(f"✅ 当前已配置List ID: {current_id}")
        print("如需更新，请继续操作")
    else:
        print("❌ 当前未配置List ID")
    
    # 显示创建指南
    show_twitter_list_guide()
    
    # 获取用户输入
    print("\n" + "=" * 50)
    new_list_id = input("请输入您的Twitter List ID (或按Enter跳过): ").strip()
    
    if new_list_id:
        if update_list_id(new_list_id):
            print(f"\n🎉 Twitter List配置完成!")
            print(f"List ID: {new_list_id}")
            print("\n现在可以运行以下命令测试系统:")
            print("  python main.py --mode status  # 查看状态")
            print("  python main.py --mode fetch   # 测试数据获取")
        else:
            print("\n❌ 配置失败，请检查错误信息")
    else:
        print("\n⏭️  跳过List ID配置")
        if not current_id:
            print("⚠️  注意: 未配置List ID将无法抓取Twitter List内容")
    
    print("\n📚 更多配置信息请查看 SOURCE_CONFIG.md")


if __name__ == "__main__":
    main()
