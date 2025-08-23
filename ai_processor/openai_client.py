"""
DeepSeek API客户端
负责与DeepSeek API交互，生成AI洞察
"""

import requests
import os
import json
import logging
from typing import Dict, Optional, List
from dotenv import load_dotenv
import time
import random

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DeepSeekClient:
    """DeepSeek API客户端"""
    
    def __init__(self):
        """初始化DeepSeek客户端"""
        api_key = os.getenv('DEEPSEEK_API_KEY', 'sk-7ff8f534b0304f268100e43934f53515')
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY 环境变量未设置")
        
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        
        # 配置参数
        self.model = "deepseek-chat"
        self.max_tokens = 2000
        self.temperature = 0.7
        
        logger.info("DeepSeek API客户端初始化成功")
    
    def generate_insight(self, content: str, source_type: str = "general") -> Dict:
        """
        为给定内容生成AI洞察
        
        Args:
            content: 要分析的内容
            source_type: 内容类型 (rss, twitter, arxiv)
            
        Returns:
            包含洞察信息的字典
        """
        try:
            # 根据内容类型选择合适的Prompt
            prompt = self._build_prompt(content, source_type)
            
            # 调用DeepSeek API
            response = self._call_deepseek_api(prompt)
            
            if not response:
                return self._generate_error_result(content, source_type, "API调用失败")
            
            # 尝试解析JSON响应
            try:
                result = json.loads(response)
                return self._validate_and_enhance_result(result, content, source_type)
            except json.JSONDecodeError:
                # 如果JSON解析失败，尝试提取关键信息
                logger.warning("AI响应不是有效JSON，尝试手动解析")
                return self._fallback_parsing(response, content, source_type)
                
        except Exception as e:
            logger.error(f"生成AI洞察失败: {e}")
            return self._generate_error_result(content, source_type, str(e))
    
    def _call_deepseek_api(self, prompt: str) -> Optional[str]:
        """调用DeepSeek API"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': self.model,
                'messages': [
                    {
                        'role': 'system',
                        'content': '你是一个专业的AI领域分析师，擅长从各种信息源中提取关键洞察。'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': self.max_tokens,
                'temperature': self.temperature
            }
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            else:
                logger.error(f"DeepSeek API调用失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"DeepSeek API调用异常: {e}")
            return None
    
    def _build_prompt(self, content: str, source_type: str) -> str:
        """构建针对不同内容类型的Prompt"""
        
        base_prompt = f"""
请分析以下AI领域的内容，并生成"七叔AI洞察日报"格式的洞察报告。

内容类型: {source_type}
内容长度: {len(content)} 字符

请严格按照以下JSON格式返回结果，不要包含任何其他文本：

{{
    "summary": "用一句话清晰说明核心事实（50字以内）",
    "analysis": "用一句话点明其重要性、对行业的影响或背后的商业逻辑（100字以内）",
    "category": "内容分类（技术突破、产品发布、行业动态、研究进展等）",
    "importance_score": 0.8,
    "trends": "相关趋势分析（50字以内）",
    "implications": "对AI行业的影响和启示（50字以内）",
    "news_type": "news_type"
}}

内容内容：
{content[:4000]}  # 限制内容长度避免超Token
"""

        # 根据内容类型调整Prompt
        if source_type == "arxiv":
            base_prompt += "\n\n注意：这是学术论文，请重点关注研究方法、技术创新和学术贡献。"
        elif source_type == "twitter":
            base_prompt += "\n\n注意：这是社交媒体内容，请关注讨论热度、观点碰撞和行业反应。"
        elif source_type == "rss":
            base_prompt += "\n\n注意：这是新闻或博客内容，请关注时效性、影响范围和商业价值。"
        
        return base_prompt
    
    def _validate_and_enhance_result(self, result: Dict, content: str, source_type: str) -> Dict:
        """验证和增强AI生成的结果"""
        
        # 确保必要字段存在
        required_fields = ['summary', 'analysis', 'category']
        for field in required_fields:
            if field not in result or not result[field]:
                result[field] = self._generate_default_value(field, content, source_type)
        
        # 验证重要性评分
        if 'importance_score' not in result or not isinstance(result['importance_score'], (int, float)):
            result['importance_score'] = 0.5
        
        # 确保评分在0-1范围内
        result['importance_score'] = max(0.0, min(1.0, float(result['importance_score'])))
        
        # 添加元数据
        result['processed_at'] = time.time()
        result['source_type'] = source_type
        result['content_length'] = len(content)
        
        return result
    
    def _generate_default_value(self, field: str, content: str, source_type: str) -> str:
        """为缺失字段生成默认值"""
        if field == 'summary':
            return f"来自{source_type}源的内容，需要进一步分析"
        elif field == 'analysis':
            return f"这是一篇关于AI领域的内容，内容长度为{len(content)}字符"
        elif field == 'category':
            return "AI技术动态"
        else:
            return "待分析"
    
    def _fallback_parsing(self, ai_response: str, content: str, source_type: str) -> Dict:
        """当JSON解析失败时的备用解析方法"""
        logger.info("使用备用解析方法")
        
        # 尝试从文本中提取关键信息
        summary = ai_response[:200] if len(ai_response) > 200 else ai_response
        
        # 简单的分类判断
        category = self._simple_category_detection(content, source_type)
        
        return {
            'summary': summary,
            'analysis': ai_response,
            'category': category,
            'importance_score': 0.5,
            'key_points': [],
            'trends': "需要进一步分析",
            'implications': "需要进一步分析",
            'processed_at': time.time(),
            'source_type': source_type,
            'content_length': len(content),
            'parsing_method': 'fallback'
        }
    
    def _simple_category_detection(self, content: str, source_type: str) -> str:
        """简单的分类检测"""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['paper', 'research', 'study', 'method']):
            return "研究进展"
        elif any(word in content_lower for word in ['release', 'launch', 'announce', 'product']):
            return "产品发布"
        elif any(word in content_lower for word in ['breakthrough', 'innovation', 'advance']):
            return "技术突破"
        elif any(word in content_lower for word in ['industry', 'market', 'business']):
            return "行业动态"
        else:
            return "AI技术动态"
    
    def _generate_error_result(self, content: str, source_type: str, error_msg: str) -> Dict:
        """生成错误结果"""
        return {
            'summary': f"内容分析失败: {error_msg}",
            'analysis': f"由于技术原因无法完成AI分析。错误信息: {error_msg}",
            'category': "分析失败",
            'importance_score': 0.0,
            'key_points': [],
            'trends': "无法分析",
            'implications': "无法分析",
            'processed_at': time.time(),
            'source_type': source_type,
            'content_length': len(content),
            'error': error_msg
        }
    
    def batch_generate_insights(self, contents: List[Dict]) -> List[Dict]:
        """
        批量生成洞察
        
        Args:
            contents: 内容列表，每个元素包含content和source_type
            
        Returns:
            洞察结果列表
        """
        results = []
        
        for i, content_info in enumerate(contents):
            try:
                logger.info(f"处理第 {i+1}/{len(contents)} 个内容")
                
                insight = self.generate_insight(
                    content_info['content'], 
                    content_info.get('source_type', 'general')
                )
                
                results.append({
                    'original_content': content_info,
                    'insight': insight
                })
                
                # 添加延迟避免API限制
                if i < len(contents) - 1:
                    time.sleep(random.uniform(1, 3))
                    
            except Exception as e:
                logger.error(f"批量处理第 {i+1} 个内容失败: {e}")
                results.append({
                    'original_content': content_info,
                    'insight': self._generate_error_result(
                        content_info['content'],
                        content_info.get('source_type', 'general'),
                        str(e)
                    )
                })
        
        return results
    
    def test_connection(self) -> bool:
        """测试DeepSeek API连接"""
        try:
            test_prompt = "请回复'Hello'"
            response = self._call_deepseek_api(test_prompt)
            
            if response and 'Hello' in response:
                logger.info("DeepSeek API连接测试成功")
                return True
            else:
                logger.error("DeepSeek API连接测试失败: 响应异常")
                return False
                
        except Exception as e:
            logger.error(f"DeepSeek API连接测试失败: {e}")
            return False


if __name__ == "__main__":
    # 测试代码
    try:
        client = DeepSeekClient()
        
        # 测试连接
        if client.test_connection():
            print("✓ DeepSeek API连接正常")
            
            # 测试洞察生成
            test_content = "OpenAI发布了GPT-4，这是一个多模态大语言模型，能够理解和生成文本、图像等多种类型的内容。"
            
            insight = client.generate_insight(test_content, "rss")
            print("\n生成的洞察:")
            print(json.dumps(insight, indent=2, ensure_ascii=False))
        else:
            print("✗ DeepSeek API连接失败")
            
    except Exception as e:
        print(f"初始化失败: {e}")
