"""
内容筛选器
负责在AI处理前对抓取的内容进行智能筛选
"""

import json
import logging
import time
from typing import List, Dict, Any, Optional
from .config_manager import config_manager
import os

logger = logging.getLogger(__name__)


class ContentFilter:
    """内容筛选器"""
    
    def __init__(self):
        self.config = config_manager
        self.performance_config = self.config.get_performance_config()
        
        logger.info("内容筛选器初始化成功")
    
    def _get_ai_client(self):
        """延迟初始化AI客户端，避免循环导入"""
        try:
            from ai_processor.openai_client import DeepSeekClient
            return DeepSeekClient()
        except ImportError:
            logger.warning("无法导入DeepSeekClient，跳过LLM筛选")
            return None
    
    def filter_rss_content(self, articles: List[Dict]) -> List[Dict]:
        """筛选RSS内容"""
        if not articles:
            return []
        
        try:
            # 获取保留率
            retention_rate = self.config.get_retention_rate('rss')
            target_count = max(1, int(len(articles) * retention_rate))
            
            logger.info(f"开始筛选RSS内容，原始数量: {len(articles)}，目标数量: {target_count}")
            
            # 尝试LLM筛选
            filtered_articles = self._llm_filter_rss(articles, target_count)
            
            if filtered_articles:
                logger.info(f"LLM筛选成功，筛选后数量: {len(filtered_articles)}")
                return filtered_articles
            else:
                logger.warning("LLM筛选失败，使用规则基础筛选")
                return self._rule_based_filter_rss(articles, target_count)
                
        except Exception as e:
            logger.error(f"RSS内容筛选失败: {e}，使用规则基础筛选")
            return self._rule_based_filter_rss(articles, target_count)
    
    def filter_arxiv_papers(self, papers: List[Dict]) -> List[Dict]:
        """筛选arXiv论文"""
        if not papers:
            return []
        
        try:
            retention_rate = self.config.get_retention_rate('arxiv')
            target_count = max(1, int(len(papers) * retention_rate))
            
            logger.info(f"开始筛选arXiv论文，原始数量: {len(papers)}，目标数量: {target_count}")
            
            # 尝试LLM筛选
            filtered_papers = self._llm_filter_arxiv(papers, target_count)
            
            if filtered_papers:
                logger.info(f"LLM筛选成功，筛选后数量: {len(filtered_papers)}")
                return filtered_papers
            else:
                logger.warning("LLM筛选失败，使用规则基础筛选")
                return self._rule_based_filter_arxiv(papers, target_count)
                
        except Exception as e:
            logger.error(f"arXiv论文筛选失败: {e}，使用规则基础筛选")
            return self._rule_based_filter_arxiv(papers, target_count)
    
    def filter_twitter_posts(self, tweets: List[Dict]) -> List[Dict]:
        """筛选Twitter内容"""
        if not tweets:
            return []
        
        try:
            retention_rate = self.config.get_retention_rate('twitter')
            target_count = max(1, int(len(tweets) * retention_rate))
            
            logger.info(f"开始筛选Twitter内容，原始数量: {len(tweets)}，目标数量: {target_count}")
            
            # 尝试LLM筛选
            filtered_tweets = self._llm_filter_twitter(tweets, target_count)
            
            if filtered_tweets:
                logger.info(f"LLM筛选成功，筛选后数量: {len(filtered_tweets)}")
                return filtered_tweets
            else:
                logger.warning("LLM筛选失败，使用规则基础筛选")
                return self._rule_based_filter_twitter(tweets, target_count)
                
        except Exception as e:
            logger.error(f"Twitter内容筛选失败: {e}，使用规则基础筛选")
            return self._rule_based_filter_twitter(tweets, target_count)
    
    def _llm_filter_rss(self, articles: List[Dict], target_count: int) -> List[Dict]:
        """使用LLM筛选RSS内容"""
        try:
            ai_client = self._get_ai_client()
            if not ai_client:
                return []
                
            # 准备输入数据
            input_data = []
            for article in articles[:20]:  # 限制数量
                input_data.append(f"[{article.get('title', '')}] - [{article.get('url', '')}]")
            
            # 使用专门的筛选方法
            response = ai_client.filter_content(input_data, "rss")
            
            if response and 'selected_indices' in response:
                selected_indices = response['selected_indices']
                if isinstance(selected_indices, list) and len(selected_indices) <= target_count:
                    selected_articles = [articles[i] for i in selected_indices if i < len(articles)]
                    return selected_articles[:target_count]
            
            return []
            
        except Exception as e:
            logger.error(f"LLM筛选RSS失败: {e}")
            return []
    
    def _llm_filter_arxiv(self, papers: List[Dict], target_count: int) -> List[Dict]:
        """使用LLM筛选arXiv论文"""
        try:
            ai_client = self._get_ai_client()
            if not ai_client:
                return []
                
            # 准备输入数据
            input_data = []
            for paper in papers[:20]:  # 限制数量
                input_data.append(f"[{paper.get('title', '')}] - [{paper.get('content', '')[:200]}] - [{paper.get('url', '')}]")
            
            # 使用专门的筛选方法
            response = ai_client.filter_content(input_data, "arxiv")
            
            if response and 'selected_indices' in response:
                selected_indices = response['selected_indices']
                if isinstance(selected_indices, list) and len(selected_indices) <= target_count:
                    selected_papers = [papers[i] for i in selected_indices if i < len(papers)]
                    return selected_papers[:target_count]
            
            return []
            
        except Exception as e:
            logger.error(f"LLM筛选arXiv失败: {e}")
            return []
    
    def _llm_filter_twitter(self, tweets: List[Dict], target_count: int) -> List[Dict]:
        """使用LLM筛选Twitter内容"""
        try:
            ai_client = self._get_ai_client()
            if not ai_client:
                return []
                
            # 准备输入数据
            input_data = []
            for tweet in tweets[:20]:  # 限制数量
                input_data.append(f"[@{tweet.get('source_name', 'Unknown')}]: [{tweet.get('content', '')[:100]}] - [{tweet.get('url', '')}]")
            
            # 使用专门的筛选方法
            response = ai_client.filter_content(input_data, "twitter")
            
            if response and 'selected_indices' in response:
                selected_indices = response['selected_indices']
                if isinstance(selected_indices, list) and len(selected_indices) <= target_count:
                    selected_tweets = [tweets[i] for i in selected_indices if i < len(tweets)]
                    return selected_tweets[:target_count]
            
            return []
            
        except Exception as e:
            logger.error(f"LLM筛选Twitter失败: {e}")
            return []
    
    def _rule_based_filter_rss(self, articles: List[Dict], target_count: int) -> List[Dict]:
        """规则基础筛选RSS内容"""
        fallback_rules = self.config.get_fallback_rules()
        keyword_boost = fallback_rules.get('keyword_boost', [])
        source_priority = fallback_rules.get('source_priority', {})
        
        # 计算重要性分数
        scored_articles = []
        for article in articles:
            score = 0.0
            title = article.get('title', '').lower()
            source = article.get('source_name', '').lower()
            
            # 关键词加分
            for keyword in keyword_boost:
                if keyword.lower() in title:
                    score += 0.3
            
            # 信源优先级加分
            for priority, sources in source_priority.items():
                if any(src.lower() in source for src in sources):
                    if priority == 'high':
                        score += 0.4
                    elif priority == 'medium':
                        score += 0.2
                    break
            
            # 标题长度加分（避免过短标题）
            if len(title) > 20:
                score += 0.1
            
            scored_articles.append((article, score))
        
        # 按分数排序并选择前N个
        scored_articles.sort(key=lambda x: x[1], reverse=True)
        selected_articles = [article for article, score in scored_articles[:target_count]]
        
        logger.info(f"规则基础筛选完成，选择 {len(selected_articles)} 篇文章")
        return selected_articles
    
    def _rule_based_filter_arxiv(self, papers: List[Dict], target_count: int) -> List[Dict]:
        """规则基础筛选arXiv论文"""
        # 简单的规则筛选：优先选择标题包含关键词的论文
        keywords = ['gpt', 'llm', 'transformer', 'attention', 'diffusion', 'gan', 'bert']
        
        scored_papers = []
        for paper in papers:
            score = 0.0
            title = paper.get('title', '').lower()
            
            # 关键词加分
            for keyword in keywords:
                if keyword in title:
                    score += 0.5
            
            # 摘要长度加分
            content = paper.get('content', '')
            if len(content) > 100:
                score += 0.2
            
            scored_papers.append((paper, score))
        
        # 按分数排序
        scored_papers.sort(key=lambda x: x[1], reverse=True)
        selected_papers = [paper for paper, score in scored_papers[:target_count]]
        
        logger.info(f"规则基础筛选完成，选择 {len(selected_papers)} 篇论文")
        return selected_papers
    
    def _rule_based_filter_twitter(self, tweets: List[Dict], target_count: int) -> List[Dict]:
        """规则基础筛选Twitter内容"""
        # 简单的规则筛选：过滤转发和回复
        filtered_tweets = []
        
        for tweet in tweets:
            content = tweet.get('content', '')
            
            # 跳过转发和回复
            if content.startswith('RT ') or content.startswith('@'):
                continue
            
            # 跳过过短内容
            if len(content) < 20:
                continue
            
            filtered_tweets.append(tweet)
            
            if len(filtered_tweets) >= target_count:
                break
        
        logger.info(f"规则基础筛选完成，选择 {len(filtered_tweets)} 条推文")
        return filtered_tweets
    
    def _get_default_rss_prompt(self) -> str:
        """获取默认RSS筛选提示词"""
        return """你是一位资深的AI行业分析师，负责从海量信息中筛选出最重要的AI动态。

请严格评估以下文章列表，并仅筛选出符合"重要性标准"的文章。

重要性标准：
一条信息必须满足以下至少一点，才被视为"重要"：
1. 技术突破：提到了新的State-of-the-Art (SOTA)模型、重大性能提升、开创性的新方法
2. 产品发布：知名公司/机构发布了新产品、新模型或重大更新
3. 市场事件：涉及重大融资(>千万美元)、收购、合并、或有深远影响的政策监管新闻
4. 行业洞察：来自顶级风投或公认KOL的深度分析报告

请仅返回一个纯粹的JSON对象，格式如下：
{{
    "selected_indices": [0, 2, 5]
}}

其中selected_indices是一个整数数组，包含符合标准的文章在列表中的索引位置（从0开始）。

文章列表：
{input_article_list}

请返回包含 'selected_indices' 的JSON响应，其中 'selected_indices' 是一个整数列表，
表示符合重要性标准的文章索引。"""
    
    def _get_default_arxiv_prompt(self) -> str:
        """获取默认arXiv筛选提示词"""
        return """你是一位AI技术专家，负责从arXiv的机器学习论文中筛选出非研究背景人士也能理解的、具有重大应用潜力的技术进展。

重要性标准：
一篇论文值得被选中，如果：
1. 高性能：在多个基准测试中达到了SOTA或接近SOTA的水平
2. 高效率：提出了显著降低计算成本、内存消耗或模型大小的新方法
3. 新颖性：提出了一种全新的、反直觉的解决问题的方法
4. 实用性：代码已开源，或方法简单易于复现，预计很快会被开发者社区采用

请仅返回一个纯粹的JSON对象，格式如下：
{{
    "selected_indices": [0, 1, 3]
}}

其中selected_indices是一个整数数组，包含符合标准的论文在列表中的索引位置（从0开始）。

论文列表：
{input_paper_list}

请返回包含 'selected_indices' 的JSON响应，其中 'selected_indices' 是一个整数列表，
表示符合重要性标准的论文索引。"""
    
    def _get_default_twitter_prompt(self) -> str:
        """获取默认Twitter筛选提示词"""
        return """你是一位AI情报员，需要监控关键人物的Twitter动态。请从以下推文中筛选出具有实质性内容的信息，忽略个人感慨、闲聊、纯转发和重复内容。

重要性标准：
一条推文值得被选中，如果它是：
1. 官方公告：宣布新产品、新功能、公司动态、融资等
2. 技术解读：分享了对新论文、新技术的独到见解或线程(Thread)
3. 趋势预测：发布了关于行业未来的预测或分析
4. 重要数据：包含了新鲜的、有价值的数据或图表

请仅返回一个纯粹的JSON对象，格式如下：
{{
    "selected_indices": [0, 2, 4]
}}

其中selected_indices是一个整数数组，包含符合标准的推文在列表中的索引位置（从0开始）。

推文列表：
{input_tweet_list}

请返回包含 'selected_indices' 的JSON响应，其中 'selected_indices' 是一个整数列表，
表示符合重要性标准的推文索引。"""
    
    def get_filter_stats(self) -> Dict[str, Any]:
        """获取筛选统计信息"""
        return {
            'config_summary': self.config.get_config_summary(),
            'performance_config': self.performance_config,
            'filter_methods': {
                'rss': 'LLM + Rule-based fallback',
                'arxiv': 'LLM + Rule-based fallback',
                'twitter': 'LLM + Rule-based fallback'
            }
        }


# 全局内容筛选器实例
content_filter = ContentFilter()
