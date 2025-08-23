#!/usr/bin/env python3
"""
测试修复后的功能
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_imports():
    """测试所有模块导入"""
    print("🔍 测试模块导入...")
    
    try:
        from fetcher.rss_fetcher import RSSFetcher
        print("  ✅ RSSFetcher 导入成功")
    except Exception as e:
        print(f"  ❌ RSSFetcher 导入失败: {e}")
    
    try:
        from fetcher.twitter_fetcher import TwitterFetcher
        print("  ✅ TwitterFetcher 导入成功")
    except Exception as e:
        print(f"  ❌ TwitterFetcher 导入失败: {e}")
    
    try:
        from fetcher.huggingface_fetcher import HuggingFaceFetcher
        print("  ✅ HuggingFaceFetcher 导入成功")
    except Exception as e:
        print(f"  ❌ HuggingFaceFetcher 导入失败: {e}")
    
    try:
        from ai_processor.openai_client import DeepSeekClient
        print("  ✅ DeepSeekClient 导入成功")
    except Exception as e:
        print(f"  ❌ DeepSeekClient 导入失败: {e}")

def test_rss_fetcher():
    """测试RSS抓取器"""
    print("\n📰 测试RSS抓取器...")
    
    try:
        from fetcher.rss_fetcher import RSSFetcher
        fetcher = RSSFetcher()
        
        # 测试单个RSS源
        test_url = "https://openai.com/blog/rss.xml"
        articles = fetcher.fetch_rss_feed(test_url, "OpenAI Blog")
        
        if articles:
            print(f"  ✅ RSS抓取成功，获取 {len(articles)} 篇文章")
            sample = articles[0]
            print(f"  📝 示例文章: {sample.get('title', 'NO_TITLE')[:50]}...")
            print(f"  🔗 示例URL: {sample.get('url', 'NO_URL')}")
            print(f"  📅 示例日期: {sample.get('published_at', 'NO_DATE')}")
        else:
            print("  ❌ RSS抓取失败，未获取到文章")
            
    except Exception as e:
        print(f"  ❌ RSS抓取器测试失败: {e}")

def test_huggingface_fetcher():
    """测试Hugging Face抓取器"""
    print("\n🤗 测试Hugging Face抓取器...")
    
    try:
        from fetcher.huggingface_fetcher import HuggingFaceFetcher
        fetcher = HuggingFaceFetcher()
        
        # 测试参数修复
        models = fetcher.fetch_ai_related_models(limit=5)
        
        if models:
            print(f"  ✅ Hugging Face抓取成功，获取 {len(models)} 个模型")
            sample = models[0]
            print(f"  📝 示例模型: {sample.get('model_id', 'NO_ID')}")
        else:
            print("  ❌ Hugging Face抓取失败，未获取到模型")
            
    except Exception as e:
        print(f"  ❌ Hugging Face抓取器测试失败: {e}")

def test_deepseek_client():
    """测试DeepSeek客户端"""
    print("\n🤖 测试DeepSeek客户端...")
    
    try:
        from ai_processor.openai_client import DeepSeekClient
        client = DeepSeekClient()
        
        # 测试连接
        if client.test_connection():
            print("  ✅ DeepSeek API连接成功")
            
            # 测试洞察生成
            test_content = "OpenAI发布了GPT-4模型，这是一个多模态大语言模型。"
            insight = client.generate_insight(test_content, "news")
            
            if insight and 'summary' in insight:
                print("  ✅ DeepSeek API洞察生成成功")
                print(f"  📝 生成摘要: {insight['summary'][:100]}...")
            else:
                print("  ❌ DeepSeek API洞察生成失败")
        else:
            print("  ❌ DeepSeek API连接失败")
            
    except Exception as e:
        print(f"  ❌ DeepSeek客户端测试失败: {e}")

def main():
    """主测试函数"""
    print("🧪 AI洞察助手 - 修复验证测试")
    print("=" * 50)
    
    # 测试模块导入
    test_imports()
    
    # 测试RSS抓取器
    test_rss_fetcher()
    
    # 测试Hugging Face抓取器
    test_huggingface_fetcher()
    
    # 测试DeepSeek客户端
    test_deepseek_client()
    
    print("\n" + "=" * 50)
    print("🎯 修复验证测试完成")

if __name__ == "__main__":
    main()
