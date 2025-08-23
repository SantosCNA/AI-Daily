"""
日报模板渲染器
负责将AI洞察渲染成结构化的日报
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import SessionLocal, Insight, RawContent, Digest
from notification import EmailSender

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DigestTemplateRenderer:
    """日报模板渲染器"""
    
    def __init__(self):
        """初始化渲染器"""
        self.template = self._load_template()
        self.email_sender = EmailSender()
        logger.info("日报模板渲染器初始化成功")
    
    def _load_template(self) -> str:
        """加载日报模板"""
        template = """# 七叔AI洞察日报 - {date}

## 🎯 核心动态（总览）
{core_dynamics}

## 📈 趋势、启示与展望
{trends_insights_outlook}

## 🔍 今日精选（分述）
### 🤖 技术突破
{tech_breakthroughs}

### 🚀 产品发布
{product_releases}

### 💼 行业动态
{industry_news}

## 📋 其他动态
{other_news}

---
*本日报由 七叔AI洞察助手 自动生成*
*生成时间: {generation_time}*
*日报ID: 七叔AI洞察日报 #{digest_id}*
"""
        return template
    
    def generate_daily_digest(self, date: Optional[str] = None) -> Dict:
        """
        生成每日日报
        
        Args:
            date: 指定日期，如果为None则使用今天
            
        Returns:
            日报生成结果
        """
        try:
            if not date:
                date = datetime.now().strftime('%Y-%m-%d')
            
            logger.info(f"开始生成 {date} 的日报")
            
            # 1. 获取今日洞察
            insights = self._get_daily_insights(date)
            
            if not insights:
                logger.warning(f"{date} 没有找到洞察数据")
                return {
                    'success': False,
                    'error': f'没有找到 {date} 的洞察数据',
                    'date': date
                }
            
            # 2. 按类别组织内容
            organized_content = self._organize_content_by_category(insights)
            
            # 3. 渲染模板（包含趋势分析）
            digest_content = self._render_template(
                date, insights, organized_content, "", ""
            )
            
            # 6. 保存到数据库
            digest_id = self._save_digest(digest_content, date, len(insights))
            
            # 7. 发送邮件通知
            self._send_digest_notification(digest_content, digest_id)
            
            result = {
                'success': True,
                'digest_id': digest_id,
                'content': digest_content,
                'date': date,
                'stats': {
                    'total_insights': len(insights),
                    'categories': {k: len(v) for k, v in organized_content.items()}
                }
            }
            
            logger.info(f"日报生成成功，ID: {digest_id}")
            return result
            
        except Exception as e:
            logger.error(f"生成日报失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'date': date
            }
    
    def _get_daily_insights(self, date: str) -> List[Dict]:
        """获取指定日期的洞察"""
        session = SessionLocal()
        
        try:
            # 查询指定日期的洞察
            start_date = datetime.strptime(date, '%Y-%m-%d')
            end_date = start_date + timedelta(days=1)
            
            insights = session.query(Insight).filter(
                Insight.created_at >= start_date,
                Insight.created_at < end_date
            ).all()
            
            # 转换为字典格式
            insight_list = []
            for insight in insights:
                insight_data = {
                    'id': insight.id,
                    'summary': insight.summary,
                    'analysis': insight.analysis,
                    'category': insight.category,
                    'importance_score': insight.importance_score,
                    'raw_content': {
                        'title': insight.raw_content.title,
                        'source_name': insight.raw_content.source_name,
                        'url': insight.raw_content.url
                    }
                }
                insight_list.append(insight_data)
            
            return insight_list
            
        except Exception as e:
            logger.error(f"获取洞察数据失败: {e}")
            return []
        finally:
            session.close()
    
    def _organize_content_by_category(self, insights: List[Dict]) -> Dict[str, List[Dict]]:
        """按类别组织内容"""
        organized = {
            'tech_breakthroughs': [],
            'product_releases': [],
            'industry_news': [],
            'other_news': []
        }
        
        for insight in insights:
            category = insight.get('category', '').lower()
            
            if any(keyword in category for keyword in ['突破', '创新', '技术', '研究', '论文', '学术']):
                organized['tech_breakthroughs'].append(insight)
            elif any(keyword in category for keyword in ['发布', '产品', 'launch']):
                organized['product_releases'].append(insight)
            elif any(keyword in category for keyword in ['行业', '市场', '投资']):
                organized['industry_news'].append(insight)
            else:
                organized['other_news'].append(insight)
        
        return organized
    
    def _generate_core_dynamics(self, insights: List[Dict]) -> str:
        """生成核心动态总览"""
        if not insights:
            return "暂无足够数据生成核心动态总览"
        
        # 分析高重要性事件
        high_importance = [i for i in insights if i.get('importance_score', 0) > 0.7]
        
        if high_importance:
            # 选择最重要的3个事件
            top_events = sorted(high_importance, key=lambda x: x.get('importance_score', 0), reverse=True)[:3]
            
            dynamics_text = "今日AI世界的主要动向：\n\n"
            for event in top_events:
                summary = event.get('summary', '')
                if summary:
                    dynamics_text += f"• {summary}\n"
            
            return dynamics_text
        else:
            return "今日AI领域保持稳定发展，各技术方向持续推进。"
    
    def _generate_trends_insights_outlook(self, insights: List[Dict]) -> str:
        """生成趋势、启示与展望"""
        if not insights:
            return "暂无足够数据生成趋势分析"
        
        # 分析热门话题和趋势
        topics = {}
        for insight in insights:
            summary = insight.get('summary', '')
            analysis = insight.get('analysis', '')
            content = f"{summary} {analysis}"
            
            # 关键词提取
            keywords = ['AI', 'GPT', 'LLM', '机器学习', '深度学习', '神经网络', '大模型', '生成式AI']
            for keyword in keywords:
                if keyword in content:
                    topics[keyword] = topics.get(keyword, 0) + 1
        
        trends_text = ""
        
        # 生成趋势分析
        if topics:
            sorted_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)
            trends_text += "**趋势一：大模型技术持续突破**\n"
            trends_text += "大语言模型在性能和应用场景上不断扩展，技术迭代加速。\n\n"
            
            if len(sorted_topics) > 1:
                trends_text += f"**趋势二：{sorted_topics[1][0]}领域活跃发展**\n"
                trends_text += f"该领域出现{sorted_topics[1][1]}次相关动态，表明持续受到关注。\n\n"
        else:
            trends_text += "**趋势一：AI技术发展持续加速**\n"
            trends_text += "各领域AI应用不断深化，技术创新层出不穷。\n\n"
        
        # 生成启示
        implications_text = "**启示：**AI技术正在重塑各个行业，需要持续关注技术发展和应用落地。\n\n"
        
        # 生成展望
        outlook_text = "**展望：**预计AI应用将更加普及，新的技术突破和应用场景将不断涌现。"
        
        return trends_text + implications_text + outlook_text
    
    def _generate_trend_analysis(self, insights: List[Dict]) -> str:
        """生成趋势分析"""
        if not insights:
            return "暂无足够数据生成趋势分析"
        
        # 分析热门话题
        topics = {}
        for insight in insights:
            summary = insight.get('summary', '')
            # 简单的关键词提取
            keywords = ['AI', 'GPT', 'LLM', '机器学习', '深度学习', '神经网络']
            for keyword in keywords:
                if keyword in summary:
                    topics[keyword] = topics.get(keyword, 0) + 1
        
        # 生成趋势分析
        trend_text = "基于今日数据分析，主要趋势包括：\n\n"
        
        if topics:
            sorted_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)
            for topic, count in sorted_topics[:5]:
                trend_text += f"• **{topic}**: 出现 {count} 次，表明该领域持续受到关注\n"
        else:
            trend_text += "• AI技术发展持续加速\n"
            trend_text += "• 大语言模型应用场景不断扩展\n"
            trend_text += "• 开源AI项目活跃度提升\n"
        
        return trend_text
    
    def _generate_implications(self, insights: List[Dict]) -> str:
        """生成启示与展望"""
        if not insights:
            return "暂无足够数据生成启示与展望"
        
        implications_text = "基于今日洞察，主要启示与展望：\n\n"
        
        # 分析重要性评分
        high_importance = [i for i in insights if i.get('importance_score', 0) > 0.7]
        medium_importance = [i for i in insights if 0.4 <= i.get('importance_score', 0) <= 0.7]
        
        implications_text += f"• **高重要性事件**: {len(high_importance)} 项，需要重点关注\n"
        implications_text += f"• **中等重要性事件**: {len(medium_importance)} 项，值得持续关注\n\n"
        
        implications_text += "**主要启示**:\n"
        implications_text += "• AI技术正在加速改变各个行业\n"
        implications_text += "• 开源和商业化并行发展\n"
        implications_text += "• 需要关注AI伦理和安全问题\n\n"
        
        implications_text += "**未来展望**:\n"
        implications_text += "• 预计AI应用将更加普及和深入\n"
        implications_text += "• 新的AI模型和算法将不断涌现\n"
        implications_text += "• AI与各行业的融合将创造新的价值\n"
        
        return implications_text
    
    def _render_template(self, date: str, insights: List[Dict], 
                        organized_content: Dict, trend_analysis: str, 
                        implications: str) -> str:
        """渲染日报模板"""
        # 生成核心动态总览
        core_dynamics = self._generate_core_dynamics(insights)
        
        # 生成趋势、启示与展望
        trends_insights_outlook = self._generate_trends_insights_outlook(insights)
        
        # 格式化各类别内容
        tech_content = self._format_category_content(organized_content['tech_breakthroughs'], '技术突破')
        product_content = self._format_category_content(organized_content['product_releases'], '产品发布')
        industry_content = self._format_category_content(organized_content['industry_news'], '行业动态')
        other_content = self._format_other_news(organized_content['other_news'])
        
        # 渲染模板
        content = self.template.format(
            date=date,
            core_dynamics=core_dynamics,
            trends_insights_outlook=trends_insights_outlook,
            tech_breakthroughs=tech_content,
            product_releases=product_content,
            industry_news=industry_content,
            other_news=other_content,
            generation_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            digest_id="待生成"
        )
        
        return content
    
    def _format_other_news(self, items: List[Dict]) -> str:
        """格式化其他动态"""
        if not items:
            return "暂无其他动态"
        
        content = ""
        for item in items:
            title = item.get('summary', '未知标题')
            raw_content = item.get('raw_content', {})
            url = raw_content.get('url', '')
            source = raw_content.get('source_name', '未知来源')
            
            if url:
                content += f"- 【{title}】（来源: [{source}]({url})）\n"
            else:
                content += f"- 【{title}】（来源: {source}）\n"
        
        return content
    
    def _format_category_content(self, items: List[Dict], category_name: str) -> str:
        """格式化类别内容"""
        if not items:
            return f"暂无{category_name}相关内容"
        
        content = ""
        
        # 选择最重要的3-4条内容
        important_items = sorted(items, key=lambda x: x.get('importance_score', 0), reverse=True)[:4]
        
        for i, item in enumerate(important_items, 1):
            title = item.get('summary', '未知标题')
            analysis = item.get('analysis', '')
            raw_content = item.get('raw_content', {})
            url = raw_content.get('url', '')
            source = raw_content.get('source_name', '未知来源')
            
            content += f"{i}.  **【{title}】（来源: [{source}]({url})）**\n"
            content += f"    **摘要：**{title}\n"
            content += f"    **七叔洞察：**{analysis}\n\n"
        
        return content
    
    def _get_category_display_name(self, category_name: str) -> str:
        """获取类别显示名称"""
        display_names = {
            '技术突破': '🚀 技术突破',
            '产品发布': '📱 产品发布',
            '研究进展': '🔬 研究进展',
            '行业动态': '💼 行业动态',
            '深度洞察': '🎯 深度洞察'
        }
        return display_names.get(category_name, category_name)
    
    def _save_digest(self, content: str, date: str, insight_count: int) -> int:
        """保存日报到数据库"""
        session = SessionLocal()
        
        try:
            # 创建新的日报记录
            digest = Digest(
                title=f"AI先锋日报 - {date}",
                content=content,
                status='draft'
            )
            
            session.add(digest)
            session.commit()
            
            digest_id = digest.id
            logger.info(f"日报保存成功，ID: {digest_id}")
            
            return digest_id
            
        except Exception as e:
            logger.error(f"保存日报失败: {e}")
            session.rollback()
            raise
        finally:
            session.close()
    
    def _send_digest_notification(self, digest_content: str, digest_id: int):
        """发送日报通知邮件"""
        try:
            success = self.email_sender.send_daily_digest_notification(
                digest_content=digest_content,
                digest_id=digest_id
            )
            
            if success:
                logger.info(f"日报通知邮件发送成功，日报ID: {digest_id}")
            else:
                logger.error(f"日报通知邮件发送失败，日报ID: {digest_id}")
                
        except Exception as e:
            logger.error(f"发送日报通知失败: {e}")
    
    def get_latest_digest(self) -> Optional[Dict]:
        """获取最新的日报"""
        session = SessionLocal()
        
        try:
            latest_digest = session.query(Digest).order_by(Digest.created_at.desc()).first()
            
            if latest_digest:
                return {
                    'id': latest_digest.id,
                    'title': latest_digest.title,
                    'content': latest_digest.content,
                    'status': latest_digest.status,
                    'created_at': latest_digest.created_at
                }
            
            return None
            
        except Exception as e:
            logger.error(f"获取最新日报失败: {e}")
            return None
        finally:
            session.close()


if __name__ == "__main__":
    # 测试代码
    try:
        renderer = DigestTemplateRenderer()
        
        # 测试日报生成
        print("开始测试日报生成...")
        result = renderer.generate_daily_digest()
        
        if result['success']:
            print(f"✅ 日报生成成功")
            print(f"日报ID: {result['digest_id']}")
            print(f"包含洞察: {result['stats']['total_insights']}")
            print(f"内容长度: {len(result['content'])} 字符")
            
            # 显示内容预览
            print("\n内容预览:")
            print(result['content'][:500] + "...")
        else:
            print(f"❌ 日报生成失败: {result.get('error', '未知错误')}")
            
    except Exception as e:
        print(f"测试失败: {e}")
