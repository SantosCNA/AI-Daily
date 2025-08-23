"""
Hugging Face数据抓取器
负责抓取Hugging Face上的热门AI模型和趋势信息
"""

import requests
import json
from datetime import datetime
from typing import List, Dict, Optional
import logging
import time
import random

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HuggingFaceFetcher:
    """Hugging Face数据抓取器"""
    
    def __init__(self):
        """初始化Hugging Face抓取器"""
        self.base_url = "https://huggingface.co/api"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_trending_models(self, limit: int = 50) -> List[Dict]:
        """
        抓取热门模型
        
        Args:
            limit: 获取模型数量
            
        Returns:
            模型信息列表
        """
        try:
            logger.info(f"开始抓取Hugging Face热门模型，数量: {limit}")
            
            # 构建API请求
            params = {
                'sort': 'trending',
                'limit': limit,
                'full': 'true'  # 获取完整信息
            }
            
            response = self.session.get(f"{self.base_url}/models", params=params)
            response.raise_for_status()
            
            models_data = response.json()
            
            if not models_data:
                logger.warning("未获取到模型数据")
                return []
            
            # 处理模型数据
            processed_models = []
            for model in models_data:
                try:
                    processed_model = self._process_model_data(model)
                    if processed_model:
                        processed_models.append(processed_model)
                except Exception as e:
                    logger.error(f"处理模型数据时出错: {e}")
                    continue
            
            logger.info(f"成功抓取 {len(processed_models)} 个热门模型")
            return processed_models
            
        except Exception as e:
            logger.error(f"抓取Hugging Face热门模型失败: {e}")
            return []
    
    def fetch_models_by_pipeline(self, pipeline_tag: str, limit: int = 30) -> List[Dict]:
        """
        根据pipeline标签抓取模型
        
        Args:
            pipeline_tag: 模型类型标签 (如 text-generation, image-generation等)
            limit: 获取模型数量
            
        Returns:
            模型信息列表
        """
        try:
            logger.info(f"开始抓取pipeline为 {pipeline_tag} 的模型，数量: {limit}")
            
            params = {
                'pipeline_tag': pipeline_tag,
                'sort': 'downloads',
                'limit': limit,
                'full': 'true'
            }
            
            response = self.session.get(f"{self.base_url}/models", params=params)
            response.raise_for_status()
            
            models_data = response.json()
            
            if not models_data:
                logger.warning(f"未找到pipeline为 {pipeline_tag} 的模型")
                return []
            
            # 处理模型数据
            processed_models = []
            for model in models_data:
                try:
                    processed_model = self._process_model_data(model)
                    if processed_model:
                        processed_models.append(processed_model)
                except Exception as e:
                    logger.error(f"处理模型数据时出错: {e}")
                    continue
            
            logger.info(f"成功抓取 {len(processed_models)} 个 {pipeline_tag} 模型")
            return processed_models
            
        except Exception as e:
            logger.error(f"抓取pipeline {pipeline_tag} 模型失败: {e}")
            return []
    
    def _process_model_data(self, model: Dict) -> Optional[Dict]:
        """处理单个模型数据"""
        try:
            # 提取基本信息
            model_id = model.get('id', '')
            author = model.get('author', '')
            last_modified = model.get('lastModified', '')
            downloads = model.get('downloads', 0)
            likes = model.get('likes', 0)
            
            # 提取标签和pipeline信息
            tags = model.get('tags', [])
            pipeline_tag = model.get('pipeline_tag', '')
            
            # 构建描述
            description = model.get('description', '')
            if not description:
                description = f"AI模型: {model_id}"
            
            # 构建内容摘要
            content_summary = f"""
模型名称: {model_id}
作者: {author}
类型: {pipeline_tag if pipeline_tag else '未知'}
标签: {', '.join(tags[:5]) if tags else '无'}
下载量: {downloads:,}
点赞数: {likes}
描述: {description[:200]}{'...' if len(description) > 200 else ''}
            """.strip()
            
            # 构建模型信息
            processed_model = {
                'title': f"Hugging Face模型: {model_id}",
                'content': content_summary,
                'url': f"https://huggingface.co/{model_id}",
                'published_at': self._parse_timestamp(last_modified),
                'source_name': f"Hugging Face {pipeline_tag if pipeline_tag else 'AI模型'}",
                'source_type': 'huggingface',
                'model_id': model_id,
                'author': author,
                'pipeline_tag': pipeline_tag,
                'tags': tags,
                'downloads': downloads,
                'likes': likes,
                'last_modified': last_modified
            }
            
            return processed_model
            
        except Exception as e:
            logger.error(f"处理模型数据失败: {e}")
            return None
    
    def _parse_timestamp(self, timestamp: str) -> Optional[datetime]:
        """解析时间戳"""
        if not timestamp:
            return None
        
        try:
            # Hugging Face使用ISO 8601格式
            return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except Exception as e:
            logger.error(f"解析时间戳失败: {timestamp}, 错误: {e}")
            return datetime.now()
    
    def fetch_ai_related_models(self, limit: int = 50) -> List[Dict]:
        """
        抓取AI相关的热门模型
        
        Args:
            limit: 获取模型数量
            
        Returns:
            AI模型信息列表
        """
        # AI相关的pipeline标签
        ai_pipelines = [
            'text-generation',
            'text2text-generation',
            'image-generation',
            'image-to-text',
            'text-to-image',
            'translation',
            'summarization',
            'question-answering',
            'sentiment-analysis',
            'zero-shot-classification'
        ]
        
        all_models = []
        
        for pipeline in ai_pipelines[:5]:  # 限制pipeline数量避免请求过多
            try:
                models = self.fetch_models_by_pipeline(pipeline, limit // len(ai_pipelines))
                all_models.extend(models)
                
                # 添加延迟避免请求过快
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                logger.error(f"抓取pipeline {pipeline} 失败: {e}")
                continue
        
        # 去重（基于model_id）
        unique_models = {}
        for model in all_models:
            if model['model_id'] not in unique_models:
                unique_models[model['model_id']] = model
        
        unique_models_list = list(unique_models.values())
        logger.info(f"总共抓取到 {len(unique_models_list)} 个唯一AI模型")
        
        return unique_models_list
    
    def search_models(self, query: str, limit: int = 30) -> List[Dict]:
        """
        搜索模型
        
        Args:
            query: 搜索关键词
            limit: 搜索结果数量
            
        Returns:
            搜索结果列表
        """
        try:
            logger.info(f"开始搜索模型: {query}")
            
            params = {
                'search': query,
                'sort': 'downloads',
                'limit': limit,
                'full': 'true'
            }
            
            response = self.session.get(f"{self.base_url}/models", params=params)
            response.raise_for_status()
            
            models_data = response.json()
            
            if not models_data:
                logger.info(f"搜索 '{query}' 没有结果")
                return []
            
            # 处理搜索结果
            processed_models = []
            for model in models_data:
                try:
                    processed_model = self._process_model_data(model)
                    if processed_model:
                        processed_models.append(processed_model)
                except Exception as e:
                    logger.error(f"处理搜索结果时出错: {e}")
                    continue
            
            logger.info(f"搜索 '{query}' 成功找到 {len(processed_models)} 个模型")
            return processed_models
            
        except Exception as e:
            logger.error(f"搜索模型失败 '{query}': {e}")
            return []


if __name__ == "__main__":
    # 测试代码
    fetcher = HuggingFaceFetcher()
    
    print("开始测试Hugging Face抓取器...")
    
    # 测试抓取热门模型
    trending_models = fetcher.fetch_trending_models(limit=5)
    print(f"测试抓取结果: {len(trending_models)} 个热门模型")
    
    for model in trending_models[:3]:
        print(f"模型: {model['model_id']}")
        print(f"类型: {model['pipeline_tag']}")
        print(f"下载量: {model['downloads']}")
        print("---")
    
    # 测试抓取特定pipeline的模型
    text_models = fetcher.fetch_models_by_pipeline('text-generation', limit=3)
    print(f"\n文本生成模型: {len(text_models)} 个")
    
    for model in text_models[:2]:
        print(f"模型: {model['model_id']}")
        print(f"作者: {model['author']}")
        print("---")
