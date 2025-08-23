"""
审核应用主文件
提供Web界面用于审核和发布AI生成的日报
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import sys
import os
import logging
from datetime import datetime
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import SessionLocal, Digest, Insight, RawContent
from digest_generator import DigestTemplateRenderer

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app():
    """创建Flask应用"""
    app = Flask(__name__)
    app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
    
    @app.route('/')
    def index():
        """主页 - 显示最新的日报草稿"""
        try:
            # 获取最新的日报草稿
            session = SessionLocal()
            latest_draft = session.query(Digest).filter_by(status='draft').order_by(Digest.created_at.desc()).first()
            
            if not latest_draft:
                # 如果没有草稿，尝试生成一个
                renderer = DigestTemplateRenderer()
                result = renderer.generate_daily_digest()
                
                if result['success']:
                    latest_draft = session.query(Digest).filter_by(id=result['digest_id']).first()
                else:
                    flash(f"无法生成日报: {result.get('error', '未知错误')}", 'error')
                    return render_template('index.html', digest=None, error=result.get('error'))
            
            session.close()
            
            return render_template('index.html', digest=latest_draft)
            
        except Exception as e:
            logger.error(f"加载主页失败: {e}")
            flash(f"加载失败: {str(e)}", 'error')
            return render_template('index.html', digest=None, error=str(e))
    
    @app.route('/digest/<int:digest_id>')
    def view_digest(digest_id):
        """查看指定日报"""
        try:
            session = SessionLocal()
            digest = session.query(Digest).filter_by(id=digest_id).first()
            session.close()
            
            if not digest:
                flash('日报不存在', 'error')
                return redirect(url_for('index'))
            
            return render_template('view_digest.html', digest=digest)
            
        except Exception as e:
            logger.error(f"查看日报失败: {e}")
            flash(f"查看失败: {str(e)}", 'error')
            return redirect(url_for('index'))
    
    def deploy_to_github_pages(digest):
        """部署日报到GitHub Pages"""
        try:
            import os
            import requests
            import json
            from datetime import datetime
            
            # GitHub配置
            github_token = os.getenv('GH_TOKEN')
            github_repo = os.getenv('GITHUB_REPO', 'your-username/ai-daily')  # 替换为你的仓库
            
            if not github_token:
                logger.warning("未设置GH_TOKEN环境变量，跳过GitHub部署")
                return {"status": "skipped", "reason": "未设置GitHub Token"}
            
            # 准备API调用参数
            url = f"https://api.github.com/repos/{github_repo}/dispatches"
            headers = {
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.everest-preview+json"
            }
            
            # 获取当前日期
            today = datetime.now().strftime('%Y-%m-%d')
            
            data = {
                "event_type": "deploy-daily",
                "client_payload": {
                    "date": today,
                    "digest_content": digest.content,
                    "digest_id": digest.id
                }
            }
            
            # 调用GitHub API触发工作流
            response = requests.post(url, headers=headers, data=json.dumps(data))
            
            if response.status_code == 204:
                logger.info(f"GitHub Pages部署任务已触发，日报ID: {digest.id}")
                return {
                    "status": "success",
                    "message": "部署任务已触发",
                    "date": today,
                    "github_repo": github_repo
                }
            else:
                logger.error(f"GitHub API调用失败: {response.status_code} - {response.text}")
                return {
                    "status": "error",
                    "message": f"GitHub API调用失败: {response.status_code}",
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"GitHub Pages部署失败: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    @app.route('/api/digest/<int:digest_id>/publish', methods=['POST'])
    def publish_digest(digest_id):
        """发布日报"""
        try:
            session = SessionLocal()
            digest = session.query(Digest).filter_by(id=digest_id).first()
            
            if not digest:
                return jsonify({'success': False, 'error': '日报不存在'}), 404
            
            # 更新状态为已发布
            digest.status = 'published'
            digest.published_at = datetime.now()
            
            session.commit()
            
            logger.info(f"日报 {digest_id} 已发布")
            
            # 触发GitHub Pages部署
            deploy_result = deploy_to_github_pages(digest)
            
            session.close()
            
            return jsonify({
                'success': True, 
                'message': '日报发布成功',
                'github_deploy': deploy_result
            })
            
        except Exception as e:
            logger.error(f"发布日报失败: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/digest/<int:digest_id>/content', methods=['GET'])
    def get_digest_content(digest_id):
        """获取日报内容（用于复制到剪贴板）"""
        try:
            session = SessionLocal()
            digest = session.query(Digest).filter_by(id=digest_id).first()
            session.close()
            
            if not digest:
                return jsonify({'success': False, 'error': '日报不存在'}), 404
            
            return jsonify({
                'success': True,
                'content': digest.content,
                'title': digest.title
            })
            
        except Exception as e:
            logger.error(f"获取日报内容失败: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/digest/<int:digest_id>/edit', methods=['POST'])
    def edit_digest(digest_id):
        """编辑日报内容"""
        try:
            data = request.get_json()
            new_content = data.get('content', '')
            
            if not new_content:
                return jsonify({'success': False, 'error': '内容不能为空'}), 400
            
            session = SessionLocal()
            digest = session.query(Digest).filter_by(id=digest_id).first()
            
            if not digest:
                return jsonify({'success': False, 'error': '日报不存在'}), 404
            
            # 更新内容
            digest.content = new_content
            digest.updated_at = datetime.now()
            
            session.commit()
            session.close()
            
            logger.info(f"日报 {digest_id} 内容已更新")
            return jsonify({'success': True, 'message': '内容更新成功'})
            
        except Exception as e:
            logger.error(f"编辑日报失败: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/stats')
    def get_stats():
        """获取系统统计信息"""
        try:
            session = SessionLocal()
            
            # 统计各种数据
            total_digests = session.query(Digest).count()
            published_digests = session.query(Digest).filter_by(status='published').count()
            draft_digests = session.query(Digest).filter_by(status='draft').count()
            
            total_insights = session.query(Insight).count()
            total_raw_content = session.query(RawContent).count()
            processed_content = session.query(RawContent).filter_by(is_processed=True).count()
            
            session.close()
            
            stats = {
                'total_digests': total_digests,
                'published_digests': published_digests,
                'draft_digests': draft_digests,
                'total_insights': total_insights,
                'total_raw_content': total_raw_content,
                'processed_content': processed_content,
                'processing_rate': (processed_content / total_raw_content * 100) if total_raw_content > 0 else 0
            }
            
            return jsonify({'success': True, 'stats': stats})
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/regenerate', methods=['POST'])
    def regenerate_digest():
        """重新生成日报"""
        try:
            data = request.get_json()
            date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
            
            renderer = DigestTemplateRenderer()
            result = renderer.generate_daily_digest(date)
            
            if result['success']:
                return jsonify({
                    'success': True, 
                    'message': f'{date} 的日报重新生成成功',
                    'digest_id': result['digest_id']
                })
            else:
                return jsonify({'success': False, 'error': result.get('error')}), 400
                
        except Exception as e:
            logger.error(f"重新生成日报失败: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/history')
    def history():
        """查看历史日报"""
        try:
            session = SessionLocal()
            digests = session.query(Digest).order_by(Digest.created_at.desc()).limit(20).all()
            session.close()
            
            return render_template('history.html', digests=digests)
            
        except Exception as e:
            logger.error(f"加载历史日报失败: {e}")
            flash(f"加载失败: {str(e)}", 'error')
            return render_template('history.html', digests=[])
    
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('500.html'), 500
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=9000)
