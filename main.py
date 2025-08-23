"""
AI洞察助手主入口脚本
负责协调整个自动化流水线的执行
"""

import os
import sys
import logging
import argparse
from datetime import datetime
from dotenv import load_dotenv

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_processor import AIOrchestrator
from digest_generator import DigestTemplateRenderer

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def run_full_pipeline():
    """运行完整的AI处理流水线"""
    try:
        logger.info("🚀 开始运行AI洞察助手完整流水线")
        
        # 1. 运行AI处理流水线
        orchestrator = AIOrchestrator()
        pipeline_result = orchestrator.run_full_pipeline()
        
        if not pipeline_result['success']:
            logger.error(f"❌ AI处理流水线失败: {pipeline_result.get('error', '未知错误')}")
            return False
        
        logger.info(f"✅ AI处理流水线完成")
        logger.info(f"   获取内容: {pipeline_result['total_fetched']}")
        logger.info(f"   存储内容: {pipeline_result['total_stored']}")
        logger.info(f"   处理内容: {pipeline_result['total_processed']}")
        logger.info(f"   耗时: {pipeline_result['processing_time_seconds']:.2f} 秒")
        
        # 2. 生成日报
        logger.info("📰 开始生成AI日报")
        renderer = DigestTemplateRenderer()
        digest_result = renderer.generate_daily_digest()
        
        if not digest_result['success']:
            logger.error(f"❌ 日报生成失败: {digest_result.get('error', '未知错误')}")
            return False
        
        logger.info(f"✅ 日报生成成功")
        logger.info(f"   日报ID: {digest_result['digest_id']}")
        logger.info(f"   包含洞察: {digest_result['stats']['total_insights']}")
        logger.info(f"   内容长度: {len(digest_result['content'])} 字符")
        
        # 3. 显示统计信息
        stats = orchestrator.get_processing_stats()
        logger.info("📊 系统统计信息:")
        logger.info(f"   原始内容总数: {stats.get('total_raw_content', 0)}")
        logger.info(f"   已处理内容: {stats.get('processed_content', 0)}")
        logger.info(f"   未处理内容: {stats.get('unprocessed_content', 0)}")
        logger.info(f"   洞察总数: {stats.get('total_insights', 0)}")
        logger.info(f"   处理率: {stats.get('processing_rate', 0):.1f}%")
        
        logger.info("🎉 完整流水线执行成功！")
        logger.info("📧 请检查您的邮箱，或访问审核界面进行最终审核和发布")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 流水线执行失败: {e}")
        return False


def run_data_fetching_only():
    """仅运行数据获取阶段"""
    try:
        logger.info("📥 开始运行数据获取阶段")
        
        orchestrator = AIOrchestrator()
        
        # 只运行数据获取和存储
        raw_contents = orchestrator._fetch_all_content()
        stored_count = orchestrator._store_raw_content(raw_contents)
        
        logger.info(f"✅ 数据获取完成")
        logger.info(f"   获取内容: {len(raw_contents)}")
        logger.info(f"   存储内容: {stored_count}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 数据获取失败: {e}")
        return False


def run_ai_processing_only():
    """仅运行AI处理阶段"""
    try:
        logger.info("🤖 开始运行AI处理阶段")
        
        orchestrator = AIOrchestrator()
        processed_count = orchestrator._process_unprocessed_content()
        
        logger.info(f"✅ AI处理完成")
        logger.info(f"   处理内容: {processed_count}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ AI处理失败: {e}")
        return False


def run_digest_generation_only():
    """仅运行日报生成阶段"""
    try:
        logger.info("📰 开始运行日报生成阶段")
        
        renderer = DigestTemplateRenderer()
        result = renderer.generate_daily_digest()
        
        if not result['success']:
            logger.error(f"❌ 日报生成失败: {result.get('error', '未知错误')}")
            return False
        
        logger.info(f"✅ 日报生成成功")
        logger.info(f"   日报ID: {result['digest_id']}")
        logger.info(f"   包含洞察: {result['stats']['total_insights']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 日报生成失败: {e}")
        return False


def show_status():
    """显示系统状态"""
    try:
        logger.info("📊 显示系统状态")
        
        orchestrator = AIOrchestrator()
        stats = orchestrator.get_processing_stats()
        
        print("\n" + "="*50)
        print("🤖 AI洞察助手系统状态")
        print("="*50)
        print(f"📅 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 原始内容总数: {stats.get('total_raw_content', 0)}")
        print(f"✅ 已处理内容: {stats.get('processed_content', 0)}")
        print(f"⏳ 未处理内容: {stats.get('unprocessed_content', 0)}")
        print(f"💡 洞察总数: {stats.get('total_insights', 0)}")
        print(f"📈 处理率: {stats.get('processing_rate', 0):.1f}%")
        
        # 检查日报状态
        renderer = DigestTemplateRenderer()
        latest_digest = renderer.get_latest_digest()
        
        if latest_digest:
            print(f"\n📰 最新日报:")
            print(f"   标题: {latest_digest['title']}")
            print(f"   状态: {latest_digest['status']}")
            print(f"   创建时间: {latest_digest['created_at']}")
            print(f"   内容长度: {len(latest_digest['content'])} 字符")
        else:
            print("\n📰 暂无日报")
        
        print("="*50)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 获取状态失败: {e}")
        return False


def cleanup_old_data():
    """清理旧数据"""
    try:
        logger.info("🧹 开始清理旧数据")
        
        orchestrator = AIOrchestrator()
        deleted_count = orchestrator.cleanup_old_content(days=30)
        
        logger.info(f"✅ 数据清理完成")
        logger.info(f"   删除内容: {deleted_count}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 数据清理失败: {e}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='AI洞察助手 - 自动化AI内容分析流水线')
    parser.add_argument('--mode', choices=['full', 'fetch', 'process', 'digest', 'status', 'cleanup'], 
                       default='full', help='运行模式')
    parser.add_argument('--date', help='指定日期 (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    # 确保日志目录存在
    os.makedirs('logs', exist_ok=True)
    
    logger.info("🤖 AI洞察助手启动")
    logger.info(f"运行模式: {args.mode}")
    if args.date:
        logger.info(f"指定日期: {args.date}")
    
    try:
        if args.mode == 'full':
            success = run_full_pipeline()
        elif args.mode == 'fetch':
            success = run_data_fetching_only()
        elif args.mode == 'process':
            success = run_ai_processing_only()
        elif args.mode == 'digest':
            success = run_digest_generation_only()
        elif args.mode == 'status':
            success = show_status()
        elif args.mode == 'cleanup':
            success = cleanup_old_data()
        else:
            logger.error(f"未知的运行模式: {args.mode}")
            return 1
        
        if success:
            logger.info("✅ 操作执行成功")
            return 0
        else:
            logger.error("❌ 操作执行失败")
            return 1
            
    except KeyboardInterrupt:
        logger.info("⏹️ 用户中断操作")
        return 1
    except Exception as e:
        logger.error(f"❌ 程序执行异常: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
