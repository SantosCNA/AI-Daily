"""
AI处理协调器
负责协调整个AI处理流程，包括内容获取、AI分析和结果存储
"""

import logging
import time
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import SessionLocal, RawContent, Insight, SourceConfig
from fetcher import (
    RSSFetcher, TwitterFetcher, ArxivFetcher,
    HuggingFaceFetcher, GitHubFetcher, WebScraper
)
from fetcher.content_filter import ContentFilter
from .openai_client import DeepSeekClient

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIOrchestrator:
    """AI处理协调器"""
    
    def __init__(self):
        """初始化协调器"""
        try:
            # 初始化各个组件
            self.rss_fetcher = RSSFetcher()
            self.twitter_fetcher = TwitterFetcher()
            self.arxiv_fetcher = ArxivFetcher()
            self.huggingface_fetcher = HuggingFaceFetcher()
            self.github_fetcher = GitHubFetcher()
            self.web_scraper = WebScraper()
            self.ai_client = DeepSeekClient()
            self.content_filter = ContentFilter()
            
            logger.info("AI处理协调器初始化成功")
            
        except Exception as e:
            logger.error(f"AI处理协调器初始化失败: {e}")
            raise
    
    def run_full_pipeline(self) -> Dict:
        """
        运行完整的AI处理流水线
        
        Returns:
            处理结果统计
        """
        start_time = time.time()
        logger.info("开始运行AI处理流水线")
        
        try:
            # 1. 数据获取阶段
            logger.info("=== 第一阶段：数据获取 ===")
            raw_contents = self._fetch_all_content()
            logger.info(f"数据获取完成，共获取 {len(raw_contents)} 条内容")
            
            # 2. 数据存储阶段
            logger.info("=== 第二阶段：数据存储 ===")
            stored_count = self._store_raw_content(raw_contents)
            logger.info(f"数据存储完成，共存储 {stored_count} 条内容")
            
            # 3. AI处理阶段
            logger.info("=== 第三阶段：AI处理 ===")
            processed_count = self._process_unprocessed_content()
            logger.info(f"AI处理完成，共处理 {processed_count} 条内容")
            
            # 4. 生成统计报告
            end_time = time.time()
            processing_time = end_time - start_time
            
            result = {
                'total_fetched': len(raw_contents),
                'total_stored': stored_count,
                'total_processed': processed_count,
                'processing_time_seconds': processing_time,
                'success': True,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"流水线执行完成，耗时 {processing_time:.2f} 秒")
            return result
            
        except Exception as e:
            logger.error(f"流水线执行失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _fetch_all_content(self) -> List[Dict]:
        """获取所有信源的内容"""
        all_content = []
        
        try:
            # 获取数据库中的信源配置
            session = SessionLocal()
            source_configs = session.query(SourceConfig).filter_by(is_active=True).all()
            session.close()
            
            # 按类型分组信源
            rss_sources = [s for s in source_configs if s.source_type == 'rss']
            twitter_sources = [s for s in source_configs if s.source_type == 'twitter']
            arxiv_sources = [s for s in source_configs if s.source_type == 'arxiv']
            huggingface_sources = [s for s in source_configs if s.source_type == 'huggingface']
            github_sources = [s for s in source_configs if s.source_type == 'github']
            web_scrape_sources = [s for s in source_configs if s.source_type == 'web_scrape']
            twitter_list_sources = [s for s in source_configs if s.source_type == 'twitter_list']
            
            # 1. 抓取RSS内容
            if rss_sources:
                logger.info(f"开始抓取 {len(rss_sources)} 个RSS源")
                rss_configs = [{'source_url': s.source_url, 'source_name': s.source_name} for s in rss_sources]
                rss_content = self.rss_fetcher.fetch_multiple_feeds(rss_configs)
                logger.info(f"RSS抓取完成，获取 {len(rss_content)} 条内容")
                
                # 内容筛选
                if rss_content:
                    logger.info("开始RSS内容筛选...")
                    filtered_rss = self.content_filter.filter_rss_content(rss_content)
                    logger.info(f"RSS筛选完成，筛选前: {len(rss_content)}，筛选后: {len(filtered_rss)}")
                    all_content.extend(filtered_rss)
                else:
                    logger.warning("RSS抓取结果为空")
            
            # 2. 抓取Twitter内容
            if twitter_sources and self.twitter_fetcher.is_available():
                logger.info("开始抓取Twitter内容")
                twitter_content = self.twitter_fetcher.fetch_ai_influencers_tweets()
                all_content.extend(twitter_content)
                logger.info(f"Twitter抓取完成，获取 {len(twitter_content)} 条内容")
            
            # 3. 抓取arXiv内容
            if arxiv_sources:
                logger.info("开始抓取arXiv内容")
                arxiv_content = self.arxiv_fetcher.fetch_ai_related_papers(max_results=50)
                logger.info(f"arXiv抓取完成，获取 {len(arxiv_content)} 条内容")
                
                # 内容筛选
                if arxiv_content:
                    logger.info("开始arXiv内容筛选...")
                    filtered_arxiv = self.content_filter.filter_arxiv_papers(arxiv_content)
                    logger.info(f"arXiv筛选完成，筛选前: {len(arxiv_content)}，筛选后: {len(filtered_arxiv)}")
                    all_content.extend(filtered_arxiv)
                else:
                    logger.warning("arXiv抓取结果为空")
            
            # 4. 抓取Hugging Face内容
            if huggingface_sources:
                logger.info("开始抓取Hugging Face内容")
                hf_content = self.huggingface_fetcher.fetch_ai_related_models(limit=30)
                all_content.extend(hf_content)
                logger.info(f"Hugging Face抓取完成，获取 {len(hf_content)} 条内容")
            
            # 5. 抓取GitHub Trending内容
            if github_sources:
                logger.info("开始抓取GitHub Trending内容")
                github_content = self.github_fetcher.fetch_ai_ml_trending(limit=20)
                all_content.extend(github_content)
                logger.info(f"GitHub Trending抓取完成，获取 {len(github_content)} 条内容")
            
            # 6. 抓取Web爬虫内容
            if web_scrape_sources:
                logger.info(f"开始抓取 {len(web_scrape_sources)} 个Web爬虫信源")
                try:
                    # 将SourceConfig对象转换为字典格式
                    web_source_configs = []
                    for source in web_scrape_sources:
                        web_source_configs.append({
                            'source_type': source.source_type,
                            'source_name': source.source_name,
                            'source_url': source.source_url
                        })
                    
                    web_content = self.web_scraper.scrape_multiple_sources(web_source_configs)
                    all_content.extend(web_content)
                    logger.info(f"Web爬虫抓取完成，获取 {len(web_content)} 条内容")
                except Exception as e:
                    logger.error(f"Web爬虫抓取失败: {e}")
                    logger.info("继续处理其他信源内容")
            
            # 7. 抓取Twitter List内容（需要配置List ID）
            if twitter_list_sources:
                logger.info("开始抓取Twitter List内容")
                for source in twitter_list_sources:
                    if source.source_url != "your_twitter_list_id_here":
                        try:
                            logger.info(f"抓取Twitter List: {source.source_name}")
                            list_tweets = self.twitter_fetcher.fetch_list_tweets(
                                list_id=source.source_url,
                                count=20
                            )
                            all_content.extend(list_tweets)
                            logger.info(f"成功获取List {source.source_name} 的 {len(list_tweets)} 条推文")
                        except Exception as e:
                            logger.error(f"抓取Twitter List失败 {source.source_name}: {e}")
                    else:
                        logger.warning(f"Twitter List {source.source_name} 未配置List ID，跳过")
            
            # 去重处理（基于URL或内容哈希）
            unique_content = self._deduplicate_content(all_content)
            logger.info(f"去重后剩余 {len(unique_content)} 条内容")
            
            return unique_content
            
        except Exception as e:
            logger.error(f"内容获取失败: {e}")
            return []
    
    def _deduplicate_content(self, content_list: List[Dict]) -> List[Dict]:
        """对内容进行去重处理"""
        seen_urls = set()
        seen_titles = set()
        unique_content = []
        
        for content in content_list:
            # 使用URL作为主要去重依据
            url = content.get('url', '')
            title = content.get('title', '')
            
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_content.append(content)
            elif title and title not in seen_titles:
                seen_titles.add(title)
                unique_content.append(content)
            else:
                # 如果都没有，检查内容相似性
                if not self._is_similar_content(content, unique_content):
                    unique_content.append(content)
        
        return unique_content
    
    def _is_similar_content(self, content: Dict, existing_content: List[Dict]) -> bool:
        """检查内容是否与现有内容相似"""
        # 简单的相似性检查：标题和内容的前100个字符
        content_preview = content.get('title', '') + content.get('content', '')[:100]
        
        for existing in existing_content:
            existing_preview = existing.get('title', '') + existing.get('content', '')[:100]
            
            # 计算简单的相似度（这里使用简单的包含关系）
            if (content_preview in existing_preview or 
                existing_preview in content_preview):
                return True
        
        return False
    
    def _store_raw_content(self, content_list: List[Dict]) -> int:
        """将原始内容存储到数据库"""
        if not content_list:
            return 0
        
        # 添加调试日志
        logger.info(f"准备存储 {len(content_list)} 条内容")
        if content_list:
            sample_content = content_list[0]
            logger.info(f"示例内容格式: {list(sample_content.keys())}")
            logger.info(f"示例URL: {sample_content.get('url', 'NO_URL')}")
            logger.info(f"示例标题: {sample_content.get('title', 'NO_TITLE')[:50]}...")
            logger.info(f"示例source_type: {sample_content.get('source_type', 'NO_TYPE')}")
            logger.info(f"示例source_name: {sample_content.get('source_name', 'NO_NAME')}")
        
        session = SessionLocal()
        stored_count = 0
        skipped_count = 0
        
        try:
            for i, content in enumerate(content_list):
                try:
                    logger.debug(f"处理第 {i+1} 条内容: {content.get('title', 'NO_TITLE')[:30]}...")
                    
                    # 检查是否已存在（基于URL）
                    if content.get('url'):
                        existing = session.query(RawContent).filter_by(url=content['url']).first()
                        if existing:
                            logger.debug(f"内容已存在，跳过: {content['url']}")
                            skipped_count += 1
                            continue
                    else:
                        logger.warning(f"第 {i+1} 条内容没有URL: {content.get('title', 'NO_TITLE')[:30]}...")
                    
                    # 创建新的RawContent记录
                    raw_content = RawContent(
                        source_type=content.get('source_type', 'unknown'),
                        source_name=content.get('source_name', 'Unknown'),
                        title=content.get('title', ''),
                        content=content.get('content', ''),
                        url=content.get('url', ''),
                        published_at=content.get('published_at'),
                        is_processed=False
                    )
                    
                    session.add(raw_content)
                    stored_count += 1
                    
                    # 每存储10条内容提交一次，避免事务过大
                    if stored_count % 10 == 0:
                        session.commit()
                        logger.info(f"已存储 {stored_count} 条内容")
                    
                except Exception as e:
                    logger.error(f"存储第 {i+1} 条内容失败: {e}")
                    logger.error(f"内容数据: {content}")
                    continue
            
            # 最终提交
            if stored_count > 0:
                session.commit()
                logger.info(f"成功存储 {stored_count} 条内容到数据库")
            else:
                logger.warning("没有内容被存储")
            
            logger.info(f"存储统计: 成功 {stored_count} 条，跳过 {skipped_count} 条")
            
        except Exception as e:
            logger.error(f"批量存储失败: {e}")
            session.rollback()
        finally:
            session.close()
        
        return stored_count
    
    def _process_unprocessed_content(self) -> int:
        """处理所有未处理的内容"""
        session = SessionLocal()
        processed_count = 0
        
        try:
            # 获取所有未处理的内容
            unprocessed_contents = session.query(RawContent).filter_by(is_processed=False).all()
            
            if not unprocessed_contents:
                logger.info("没有未处理的内容")
                return 0
            
            logger.info(f"开始处理 {len(unprocessed_contents)} 条未处理内容")
            
            for i, content in enumerate(unprocessed_contents):
                try:
                    logger.info(f"处理第 {i+1}/{len(unprocessed_contents)} 条内容")
                    
                    # 调用AI生成洞察
                    insight_data = self.ai_client.generate_insight(
                        content.content, 
                        content.source_type
                    )
                    
                    # 创建Insight记录
                    insight = Insight(
                        raw_content_id=content.id,
                        summary=insight_data.get('summary', ''),
                        analysis=insight_data.get('analysis', ''),
                        category=insight_data.get('category', ''),
                        importance_score=insight_data.get('importance_score', 0.5)
                    )
                    
                    session.add(insight)
                    
                    # 标记为已处理
                    content.is_processed = True
                    content.processing_error = None
                    
                    processed_count += 1
                    
                    # 每处理10条内容提交一次，避免事务过大
                    if processed_count % 10 == 0:
                        session.commit()
                        logger.info(f"已处理 {processed_count} 条内容")
                    
                except Exception as e:
                    logger.error(f"处理内容 {content.id} 失败: {e}")
                    content.processing_error = str(e)
                    continue
            
            # 最终提交
            session.commit()
            logger.info(f"AI处理完成，共处理 {processed_count} 条内容")
            
        except Exception as e:
            logger.error(f"批量处理失败: {e}")
            session.rollback()
        finally:
            session.close()
        
        return processed_count
    
    def get_processing_stats(self) -> Dict:
        """获取处理统计信息"""
        session = SessionLocal()
        
        try:
            total_raw = session.query(RawContent).count()
            processed_raw = session.query(RawContent).filter_by(is_processed=True).count()
            unprocessed_raw = session.query(RawContent).filter_by(is_processed=False).count()
            total_insights = session.query(Insight).count()
            
            # 按信源类型统计
            source_stats = {}
            for source_type in ['rss', 'twitter', 'arxiv', 'huggingface', 'github', 'web_scrape']:
                count = session.query(RawContent).filter_by(source_type=source_type).count()
                source_stats[source_type] = count
            
            stats = {
                'total_raw_content': total_raw,
                'processed_content': processed_raw,
                'unprocessed_content': unprocessed_raw,
                'total_insights': total_insights,
                'processing_rate': (processed_raw / total_raw * 100) if total_raw > 0 else 0,
                'source_type_stats': source_stats,
                'timestamp': datetime.now().isoformat()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}
        finally:
            session.close()
    
    def cleanup_old_content(self, days: int = 30) -> int:
        """清理旧内容"""
        session = SessionLocal()
        deleted_count = 0
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # 删除旧的已处理内容
            old_content = session.query(RawContent).filter(
                RawContent.is_processed == True,
                RawContent.created_at < cutoff_date
            ).all()
            
            for content in old_content:
                session.delete(content)
                deleted_count += 1
            
            session.commit()
            logger.info(f"清理了 {deleted_count} 条旧内容")
            
        except Exception as e:
            logger.error(f"清理旧内容失败: {e}")
            session.rollback()
        finally:
            session.close()
        
        return deleted_count


if __name__ == "__main__":
    # 测试代码
    try:
        orchestrator = AIOrchestrator()
        
        # 获取统计信息
        stats = orchestrator.get_processing_stats()
        print("当前处理统计:")
        print(f"原始内容总数: {stats.get('total_raw_content', 0)}")
        print(f"已处理内容: {stats.get('processed_content', 0)}")
        print(f"未处理内容: {stats.get('unprocessed_content', 0)}")
        print(f"洞察总数: {stats.get('total_insights', 0)}")
        
        # 显示信源类型统计
        source_stats = stats.get('source_type_stats', {})
        if source_stats:
            print("\n信源类型统计:")
            for source_type, count in source_stats.items():
                print(f"  {source_type}: {count}")
        
        # 运行完整流水线
        print("\n开始运行完整流水线...")
        result = orchestrator.run_full_pipeline()
        
        if result['success']:
            print(f"✓ 流水线执行成功")
            print(f"获取内容: {result['total_fetched']}")
            print(f"存储内容: {result['total_stored']}")
            print(f"处理内容: {result['total_processed']}")
            print(f"耗时: {result['processing_time_seconds']:.2f} 秒")
        else:
            print(f"✗ 流水线执行失败: {result.get('error', '未知错误')}")
            
    except Exception as e:
        print(f"测试失败: {e}")
