#!/usr/bin/env python3
"""
测试内容筛选配置和筛选器功能
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_config_manager():
    """测试配置管理器"""
    print("🔧 测试配置管理器...")
    
    try:
        from fetcher.config_manager import config_manager
        
        # 测试配置加载
        print("  ✅ 配置管理器初始化成功")
        
        # 获取配置摘要
        summary = config_manager.get_config_summary()
        print(f"  📊 配置摘要:")
        print(f"     - 版本: {summary['config_version']}")
        print(f"     - 严格度: {summary['filter_strictness']}")
        print(f"     - 备用规则: {'启用' if summary['fallback_rules_enabled'] else '禁用'}")
        print(f"     - 配置源: {summary['config_source']}")
        
        # 测试保留率配置
        retention_rates = summary['retention_rates']
        print(f"  📈 保留率配置:")
        for source, rate in retention_rates.items():
            print(f"     - {source}: {rate*100:.1f}%")
        
        # 测试配置获取方法
        strictness = config_manager.get_filter_strictness()
        rss_rate = config_manager.get_retention_rate('rss')
        fallback_rules = config_manager.get_fallback_rules()
        
        print(f"  ✅ 配置获取测试通过:")
        print(f"     - 严格度: {strictness}")
        print(f"     - RSS保留率: {rss_rate*100:.1f}%")
        print(f"     - 备用规则: {fallback_rules}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 配置管理器测试失败: {e}")
        return False

def test_content_filter():
    """测试内容筛选器"""
    print("\n🔍 测试内容筛选器...")
    
    try:
        from fetcher.content_filter import content_filter
        
        # 测试筛选器初始化
        print("  ✅ 内容筛选器初始化成功")
        
        # 测试筛选统计
        stats = content_filter.get_filter_stats()
        print(f"  📊 筛选器统计:")
        print(f"     - 筛选方法: {stats['filter_methods']}")
        print(f"     - 性能配置: {stats['performance_config']}")
        
        # 测试RSS筛选（模拟数据）
        test_articles = [
            {
                'title': 'OpenAI发布GPT-5模型，性能大幅提升',
                'url': 'https://example.com/gpt5',
                'source_name': 'OpenAI Blog',
                'content': 'GPT-5模型在多个基准测试中表现优异'
            },
            {
                'title': 'Google发布Gemini 2.0，支持多模态',
                'url': 'https://example.com/gemini2',
                'source_name': 'Google Blog',
                'content': 'Gemini 2.0支持文本、图像、音频输入'
            },
            {
                'title': '日常AI新闻更新',
                'url': 'https://example.com/daily',
                'source_name': 'General News',
                'content': '今日AI行业的一般性新闻'
            }
        ]
        
        print(f"  🧪 测试RSS筛选（模拟数据）:")
        print(f"     - 原始数量: {len(test_articles)}")
        
        # 注意：这里只是测试筛选器初始化，不实际调用LLM
        print("  ✅ 内容筛选器测试通过（跳过LLM调用）")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 内容筛选器测试失败: {e}")
        return False

def test_config_file():
    """测试配置文件"""
    print("\n📁 测试配置文件...")
    
    try:
        import yaml
        
        config_path = "configs/filter_config.yaml"
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            print("  ✅ 配置文件加载成功")
            
            # 检查关键配置项
            system_config = config_data.get('system', {})
            if 'filter_strictness' in system_config:
                print(f"  ✅ 筛选严格度配置: {system_config['filter_strictness']}")
            
            if 'retention_rates' in system_config:
                rates = system_config['retention_rates']
                print(f"  ✅ 保留率配置: {len(rates)} 个信源类型")
                for source, rate in rates.items():
                    print(f"     - {source}: {rate*100:.1f}%")
            
            if 'fallback_rules' in system_config:
                rules = system_config['fallback_rules']
                print(f"  ✅ 备用规则配置: {'启用' if rules.get('enable_rule_based') else '禁用'}")
            
            return True
        else:
            print(f"  ❌ 配置文件不存在: {config_path}")
            return False
            
    except Exception as e:
        print(f"  ❌ 配置文件测试失败: {e}")
        return False

def test_prompts():
    """测试提示词文件"""
    print("\n💬 测试提示词文件...")
    
    try:
        prompt_files = [
            "prompts/rss_filter_prompt.txt",
            "prompts/arxiv_filter_prompt.txt",
            "prompts/twitter_filter_prompt.txt"
        ]
        
        all_exist = True
        for prompt_file in prompt_files:
            if os.path.exists(prompt_file):
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"  ✅ {prompt_file}: {len(content)} 字符")
            else:
                print(f"  ❌ {prompt_file}: 文件不存在")
                all_exist = False
        
        return all_exist
        
    except Exception as e:
        print(f"  ❌ 提示词文件测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 AI洞察助手 - 内容筛选配置测试")
    print("=" * 60)
    
    # 运行所有测试
    tests = [
        test_config_file,
        test_config_manager,
        test_content_filter,
        test_prompts
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"  ❌ 测试异常: {e}")
    
    print("\n" + "=" * 60)
    print("📊 测试结果汇总:")
    print(f"  通过: {passed}/{total}")
    
    if passed == total:
        print("🎉 所有测试通过！内容筛选系统配置完成。")
        print("\n📋 下一步操作:")
        print("1. 运行 python main.py 测试完整流水线")
        print("2. 检查日志中的筛选效果")
        print("3. 根据需要调整 configs/filter_config.yaml")
    else:
        print(f"⚠️  有 {total - passed} 项测试失败，请检查配置。")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
