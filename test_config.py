#!/usr/bin/env python3
"""
配置测试脚本
测试AI洞察助手的各项配置是否正常
"""

import os
import sys
from dotenv import load_dotenv

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import SessionLocal, SourceConfig
from notification import EmailSender

# 加载环境变量
load_dotenv()


def test_environment_variables():
    """测试环境变量配置"""
    print("🔍 测试环境变量配置...")
    
    required_vars = [
        'DEEPSEEK_API_KEY',
        'TWITTER_BEARER_TOKEN',
        'TWITTER_API_KEY',
        'TWITTER_API_SECRET',
        'SMTP_USERNAME',
        'SMTP_PASSWORD'
    ]
    
    all_good = True
    for var in required_vars:
        value = os.getenv(var)
        if value and value != 'your-xxx-here':
            print(f"  ✅ {var}: 已配置")
        else:
            print(f"  ❌ {var}: 未配置或使用默认值")
            all_good = False
    
    return all_good


def test_database_config():
    """测试数据库配置"""
    print("\n🗄️  测试数据库配置...")
    
    try:
        session = SessionLocal()
        
        # 检查信源配置
        sources = session.query(SourceConfig).all()
        print(f"  ✅ 数据库连接正常，找到 {len(sources)} 个信源配置")
        
        # 检查Twitter List配置
        twitter_list = session.query(SourceConfig).filter_by(
            source_name='AI KOL Twitter List'
        ).first()
        
        if twitter_list and twitter_list.source_url != "your_twitter_list_id_here":
            print(f"  ✅ Twitter List ID已配置: {twitter_list.source_url}")
        else:
            print("  ❌ Twitter List ID未配置")
        
        session.close()
        return True
        
    except Exception as e:
        print(f"  ❌ 数据库配置测试失败: {e}")
        return False


def test_email_config():
    """测试邮件配置"""
    print("\n📧 测试邮件配置...")
    
    try:
        sender = EmailSender()
        
        # 测试连接
        if sender.test_connection():
            print("  ✅ 邮件服务器连接正常")
            
            # 测试发送
            test_success = sender.send_system_notification(
                title="AI洞察助手 - 配置测试",
                message="这是一条配置测试邮件，如果您收到此邮件，说明邮件配置正常。"
            )
            
            if test_success:
                print("  ✅ 测试邮件发送成功")
                print("  📬 请检查您的邮箱: tahminasantos273@gmail.com")
            else:
                print("  ❌ 测试邮件发送失败")
        else:
            print("  ❌ 邮件服务器连接失败")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ 邮件配置测试失败: {e}")
        return False


def test_twitter_config():
    """测试Twitter配置"""
    print("\n🐦 测试Twitter配置...")
    
    try:
        from fetcher.twitter_fetcher import TwitterFetcher
        
        fetcher = TwitterFetcher()
        
        if fetcher.is_available():
            print("  ✅ Twitter API配置正常")
            
            # 测试连接
            if fetcher.test_connection():
                print("  ✅ Twitter API连接成功")
                
                # 测试获取用户推文
                try:
                    tweets = fetcher.fetch_user_tweets('OpenAI', count=1)
                    if tweets:
                        print("  ✅ Twitter API调用成功")
                        print(f"  📝 获取到 {len(tweets)} 条推文")
                    else:
                        print("  ⚠️  Twitter API调用成功但无数据")
                except Exception as e:
                    print(f"  ⚠️  Twitter API调用异常: {e}")
                
                # 测试Twitter List功能
                try:
                    from models import SessionLocal, SourceConfig
                    session = SessionLocal()
                    twitter_list = session.query(SourceConfig).filter_by(
                        source_name='AI KOL Twitter List'
                    ).first()
                    session.close()
                    
                    if twitter_list and twitter_list.source_url != "your_twitter_list_id_here":
                        print(f"  ✅ Twitter List ID已配置: {twitter_list.source_url}")
                        
                        # 测试List抓取
                        try:
                            list_tweets = fetcher.fetch_list_tweets(twitter_list.source_url, count=2)
                            if list_tweets:
                                print(f"  ✅ Twitter List抓取成功，获取 {len(list_tweets)} 条推文")
                            else:
                                print("  ⚠️  Twitter List抓取成功但无数据")
                        except Exception as e:
                            print(f"  ⚠️  Twitter List抓取异常: {e}")
                    else:
                        print("  ❌ Twitter List ID未配置")
                        
                except Exception as e:
                    print(f"  ⚠️  Twitter List测试异常: {e}")
                
                return True
            else:
                print("  ❌ Twitter API连接失败")
                return False
                
        else:
            print("  ❌ Twitter API不可用")
            return False
            
    except Exception as e:
        print(f"  ❌ Twitter配置测试失败: {e}")
        return False


def test_deepseek_config():
    """测试DeepSeek配置"""
    print("\n🤖 测试DeepSeek配置...")
    
    try:
        from ai_processor.openai_client import DeepSeekClient
        
        client = DeepSeekClient()
        
        if client.test_connection():
            print("  ✅ DeepSeek API连接正常")
            
            # 测试洞察生成
            try:
                test_content = "OpenAI发布了GPT-4，这是一个多模态大语言模型。"
                insight = client.generate_insight(test_content, "rss")
                
                if insight and 'summary' in insight:
                    print("  ✅ DeepSeek API洞察生成成功")
                    print(f"  📝 生成摘要: {insight['summary'][:100]}...")
                else:
                    print("  ⚠️  DeepSeek API响应异常")
            except Exception as e:
                print(f"  ⚠️  DeepSeek API调用异常: {e}")
            
            return True
        else:
            print("  ❌ DeepSeek API连接失败")
            return False
            
    except Exception as e:
        print(f"  ❌ DeepSeek配置测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🧪 AI洞察助手 - 配置测试")
    print("=" * 40)
    
    # 运行各项测试
    tests = [
        ("环境变量", test_environment_variables),
        ("数据库", test_database_config),
        ("邮件", test_email_config),
        ("Twitter", test_twitter_config),
        ("DeepSeek", test_deepseek_config)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"  ❌ {test_name}测试异常: {e}")
            results[test_name] = False
    
    # 显示测试结果
    print("\n" + "=" * 40)
    print("📊 测试结果汇总:")
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总体结果: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("\n🎉 所有配置测试通过！系统可以正常运行。")
        print("\n下一步操作:")
        print("1. 运行 python main.py 启动完整流水线")
        print("2. 运行 python start_review_app.py 启动审核界面")
        print("3. 检查邮件通知是否正常")
    else:
        print(f"\n⚠️  有 {total - passed} 项配置需要修复。")
        print("\n修复建议:")
        if not results.get("环境变量", False):
            print("- 检查 .env 文件配置")
        if not results.get("数据库", False):
            print("- 运行 python init_db.py 初始化数据库")
        if not results.get("邮件", False):
            print("- 检查SMTP配置和邮箱密码")
        if not results.get("Twitter", False):
            print("- 检查Twitter API密钥配置")
        if not results.get("DeepSeek", False):
            print("- 检查DeepSeek API密钥配置")


if __name__ == "__main__":
    main()
