#!/usr/bin/env python3
"""
查看生成的日报内容
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def view_latest_digest():
    """查看最新的日报"""
    try:
        from models import SessionLocal, Digest
        from digest_generator.template_renderer import DigestTemplateRenderer
        
        # 获取最新日报
        renderer = DigestTemplateRenderer()
        latest_digest = renderer.get_latest_digest()
        
        if latest_digest:
            print("📰 最新日报信息")
            print("=" * 50)
            print(f"日报ID: {latest_digest['id']}")
            print(f"标题: {latest_digest['title']}")
            print(f"状态: {latest_digest['status']}")
            print(f"创建时间: {latest_digest['created_at']}")
            print("=" * 50)
            
            # 显示内容预览
            content = latest_digest['content']
            print("\n📝 日报内容预览:")
            print("-" * 30)
            print(content[:1000] + "..." if len(content) > 1000 else content)
            
            # 保存到文件
            with open(f"digest_{latest_digest['id']}.md", "w", encoding="utf-8") as f:
                f.write(content)
            print(f"\n💾 完整日报已保存到: digest_{latest_digest['id']}.md")
            
        else:
            print("❌ 没有找到日报")
            
    except Exception as e:
        print(f"查看日报失败: {e}")

def view_insights():
    """查看洞察数据"""
    try:
        from models import SessionLocal, Insight, RawContent
        
        session = SessionLocal()
        
        # 获取所有洞察
        insights = session.query(Insight).all()
        
        print(f"\n🤖 洞察数据统计")
        print("=" * 30)
        print(f"总洞察数: {len(insights)}")
        
        if insights:
            print("\n📊 前5条洞察:")
            for i, insight in enumerate(insights[:5], 1):
                print(f"\n{i}. 摘要: {insight.summary[:100]}...")
                print(f"   分析: {insight.analysis[:100]}...")
                print(f"   分类: {insight.category}")
                print(f"   重要性: {insight.importance_score}")
        
        session.close()
        
    except Exception as e:
        print(f"查看洞察失败: {e}")

def main():
    """主函数"""
    print("🔍 AI洞察助手 - 日报查看器")
    print("=" * 50)
    
    # 查看最新日报
    view_latest_digest()
    
    # 查看洞察数据
    view_insights()
    
    print("\n" + "=" * 50)
    print("🎯 日报查看完成")

if __name__ == "__main__":
    main()
