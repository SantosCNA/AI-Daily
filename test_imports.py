#!/usr/bin/env python3
"""
测试所有核心模块的导入
"""

def test_imports():
    """测试模块导入"""
    print("🔍 开始测试模块导入...")
    
    # 测试基础模块
    try:
        import requests
        print("✅ requests 导入成功")
    except ImportError as e:
        print(f"❌ requests 导入失败: {e}")
    
    try:
        import sqlalchemy
        print("✅ sqlalchemy 导入成功")
    except ImportError as e:
        print(f"❌ sqlalchemy 导入失败: {e}")
    
    try:
        from bs4 import BeautifulSoup
        print("✅ BeautifulSoup 导入成功")
    except ImportError as e:
        print(f"❌ BeautifulSoup 导入失败: {e}")
    
    try:
        import tweepy
        print("✅ tweepy 导入成功")
    except ImportError as e:
        print(f"❌ tweepy 导入失败: {e}")
    
    # 测试项目模块
    try:
        from models import SessionLocal, RawContent, Insight
        print("✅ models 导入成功")
    except ImportError as e:
        print(f"❌ models 导入失败: {e}")
    
    try:
        from fetcher.rss_fetcher import RSSFetcher
        print("✅ RSSFetcher 导入成功")
    except ImportError as e:
        print(f"❌ RSSFetcher 导入失败: {e}")
    
    try:
        from fetcher.arxiv_fetcher import ArxivFetcher
        print("✅ ArxivFetcher 导入成功")
    except ImportError as e:
        print(f"❌ ArxivFetcher 导入失败: {e}")
    
    try:
        from fetcher.content_filter import ContentFilter
        print("✅ ContentFilter 导入成功")
    except ImportError as e:
        print(f"❌ ContentFilter 导入失败: {e}")
    
    try:
        from ai_processor.openai_client import DeepSeekClient
        print("✅ DeepSeekClient 导入成功")
    except ImportError as e:
        print(f"❌ DeepSeekClient 导入失败: {e}")
    
    try:
        from ai_processor.orchestrator import AIOrchestrator
        print("✅ AIOrchestrator 导入成功")
    except ImportError as e:
        print(f"❌ AIOrchestrator 导入失败: {e}")
    
    try:
        from digest_generator.template_renderer import DigestTemplateRenderer
        print("✅ DigestTemplateRenderer 导入成功")
    except ImportError as e:
        print(f"❌ DigestTemplateRenderer 导入失败: {e}")
    
    print("\n🔍 模块导入测试完成")

if __name__ == "__main__":
    test_imports()
