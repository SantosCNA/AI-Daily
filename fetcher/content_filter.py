"""
内容筛选器
负责在AI处理前对抓取的内容进行智能筛选
"""

import json
import logging
import time
from typing import List, Dict, Any, Optional
from .config_manager import config_manager
from ai_processor.openai_client import DeepSeekClient
import os

logger = logging.getLogger(__name__)


class ContentFilter:
    """内容筛选器"""
    
    def __init__(self):
        self.config = config_manager
        self.ai_client = DeepSeekClient()
        self.performance_config = self.config.get_performance_config()
        
        logger.info("内容筛选器初始化成功")
    
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
            # 准备输入数据
            input_data = []
            for article in articles[:20]:  # 限制数量避免token超限
                input_data.append(f"[{article.get('title', '')}] - [{article.get('url', '')}]")
            
            input_text = "\n".join(input_data)
            
            # 读取提示词
            prompt_path = "prompts/rss_filter_prompt.txt"
            if os.path.exists(prompt_path):
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    prompt_template = f.read()
            else:
                # 使用内置提示词
                prompt_template = self._get_default_rss_prompt()
            
            prompt = prompt_template.format(input_article_list=input_text)
            
            # 调用LLM
            response = self.ai_client.generate_insight(prompt, "filter")
            
            if response and 'analysis' in response:
                # 解析JSON响应
                try:
                    filtered_data = json.loads(response['analysis'])
                    if isinstance(filtered_data, list):
                        # 根据筛选结果找到对应的文章
                        filtered_articles = []
                        for item in filtered_data:
                            if 'url' in item:
                                # 根据URL找到原文章
                                for article in articles:
                                    if article.get('url') == item['url']:
                                        filtered_articles.append(article)
                                        break
                        
                        # 限制数量
                        return filtered_articles[:target_count]
                except json.JSONDecodeError:
                    logger.warning("LLM返回的JSON格式无效")
            
            return []
            
        except Exception as e:
            logger.error(f"LLM筛选RSS失败: {e}")
            return []
    
    def _llm_filter_arxiv(self, papers: List[Dict], target_count: int) -> List[Dict]:
        """使用LLM筛选arXiv论文"""
        try:
            # 准备输入数据
            input_data = []
            for paper in papers[:15]:  # 限制数量
                title = paper.get('title', '')
                summary = paper.get('content', '')[:200]  # 限制摘要长度
                url = paper.get('url', '')
                input_data.append(f"[{title}] - [{summary}] - [{url}]")
            
            input_text = "\n".join(input_data)
            
            # 读取提示词
            prompt_path = "prompts/arxiv_filter_prompt.txt"
            if os.path.exists(prompt_path):
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    prompt_template = f.read()
            else:
                prompt_template = self._get_default_arxiv_prompt()
            
            prompt = prompt_template.format(input_paper_list=input_text)
            
            # 调用LLM
            response = self.ai_client.generate_insight(prompt, "filter")
            
            if response and 'analysis' in response:
                try:
                    filtered_data = json.loads(response['analysis'])
                    if isinstance(filtered_data, list):
                        filtered_papers = []
                        for item in filtered_data:
                            if 'url' in item:
                                for paper in papers:
                                    if paper.get('url') == item['url']:
                                        filtered_papers.append(paper)
                                        break
                        
                        return filtered_papers[:target_count]
                except json.JSONDecodeError:
                    logger.warning("LLM返回的JSON格式无效")
            
            return []
            
        except Exception as e:
            logger.error(f"LLM筛选arXiv失败: {e}")
            return []
    
    def _llm_filter_twitter(self, tweets: List[Dict], target_count: int) -> List[Dict]:
        """使用LLM筛选Twitter内容"""
        try:
            # 准备输入数据
            input_data = []
            for tweet in tweets[:20]:
                author = tweet.get('source_name', 'Unknown')
                text = tweet.get('content', '')[:100]  # 限制文本长度
                url = tweet.get('url', '')
                input_data.append(f"[@{author}]: [{text}] - [{url}]")
            
            input_text = "\n".join(input_data)
            
            # 读取提示词
            prompt_path = "prompts/twitter_filter_prompt.txt"
            if os.path.exists(prompt_path):
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    prompt_template = f.read()
            else:
                prompt_template = self._get_default_twitter_prompt()
            
            prompt = prompt_template.format(input_tweet_list=input_text)
            
            # 调用LLM
            response = self.ai_client.generate_insight(prompt, "filter")
            
            if response and 'analysis' in response:
                try:
                    filtered_data = json.loads(response['analysis'])
                    if isinstance(filtered_data, list):
                        filtered_tweets = []
                        for item in filtered_data:
                            if 'url' in item:
                                for tweet in tweets:
                                    if tweet.get('url') == item['url']:
                                        filtered_tweets.append(tweet)
                                        break
                        
                        return filtered_tweets[:target_count]
                except json.JSONDecodeError:
                    logger.warning("LLM返回的JSON格式无效")
            
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
        return """你是一位AI行业分析师，请从以下文章中选择最重要的AI动态：
        
        选择标准：
        1. 技术突破：新模型、重大性能提升
        2. 产品发布：知名公司新产品
        3. 市场事件：重大融资、收购
        4. 行业洞察：顶级风投分析
        
        请返回JSON格式：
        [{"title": "标题", "url": "链接", "reason": "选择理由"}]
        
        文章列表：
        {input_article_list}"""
    
    def _get_default_arxiv_prompt(self) -> str:
        """获取默认arXiv筛选提示词"""
        return """你是AI技术专家，请从以下论文中选择有应用潜力的：
        
        选择标准：
        1. 高性能：达到SOTA水平
        2. 高效率：降低计算成本
        3. 新颖性：全新方法
        4. 实用性：代码开源
        
        请返回JSON格式：
        [{"title": "标题", "url": "链接", "summary": "摘要", "reason": "选择理由"}]
        
        论文列表：
        {input_paper_list}"""
    
    def _get_default_twitter_prompt(self) -> str:
        """获取默认Twitter筛选提示词"""
        return """你是AI情报员，请从以下推文中选择有价值信息：
        
        选择标准：
        1. 官方公告：新产品、功能
        2. 技术解读：独到见解
        3. 趋势预测：行业分析
        4. 重要数据：有价值信息
        
        请返回JSON格式：
        [{"text": "推文内容", "url": "链接", "author": "作者", "reason": "选择理由"}]
        
        推文列表：
        {input_tweet_list}"""
    
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
