"""
邮件通知模块
负责发送AI洞察助手的日报通知
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from typing import Optional, List
import logging
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailSender:
    """邮件发送器"""
    
    def __init__(self):
        """初始化邮件发送器"""
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.username = os.getenv('SMTP_USERNAME', 'tahminasantos273@gmail.com')
        self.password = os.getenv('SMTP_PASSWORD', 'Edison1982')
        
        # Gmail需要应用专用密码，不是普通密码
        # 请访问: https://myaccount.google.com/apppasswords
        # 生成应用专用密码并更新.env文件
        
        logger.info(f"邮件发送器初始化成功，使用邮箱: {self.username}")
        logger.warning("注意: Gmail需要使用应用专用密码，不是普通密码")
        logger.info("请访问: https://myaccount.google.com/apppasswords 生成应用专用密码")
    
    def send_daily_digest_notification(self, digest_content: str, digest_id: int, 
                                      recipient_email: Optional[str] = None) -> bool:
        """
        发送日报通知邮件
        
        Args:
            digest_content: 日报内容
            digest_id: 日报ID
            recipient_email: 收件人邮箱，如果为None则发送给自己
            
        Returns:
            发送是否成功
        """
        try:
            if not recipient_email:
                recipient_email = self.username
            
            # 构建邮件内容
            subject = f"【AI洞察助手】每日日报草稿已生成，待您审核 ({datetime.now().strftime('%Y-%m-%d')})"
            
            # 构建HTML邮件内容
            html_content = self._build_digest_email_html(digest_content, digest_id)
            
            # 发送邮件
            success = self._send_email(
                to_email=recipient_email,
                subject=subject,
                html_content=html_content
            )
            
            if success:
                logger.info(f"日报通知邮件发送成功，收件人: {recipient_email}")
            else:
                logger.error(f"日报通知邮件发送失败，收件人: {recipient_email}")
            
            return success
            
        except Exception as e:
            logger.error(f"发送日报通知邮件失败: {e}")
            return False
    
    def send_system_notification(self, title: str, message: str, 
                                recipient_email: Optional[str] = None) -> bool:
        """
        发送系统通知邮件
        
        Args:
            title: 邮件标题
            message: 邮件内容
            recipient_email: 收件人邮箱
            
        Returns:
            发送是否成功
        """
        try:
            if not recipient_email:
                recipient_email = self.username
            
            success = self._send_email(
                to_email=recipient_email,
                subject=title,
                text_content=message
            )
            
            if success:
                logger.info(f"系统通知邮件发送成功，收件人: {recipient_email}")
            else:
                logger.error(f"系统通知邮件发送失败，收件人: {recipient_email}")
            
            return success
            
        except Exception as e:
            logger.error(f"发送系统通知邮件失败: {e}")
            return False
    
    def _build_digest_email_html(self, digest_content: str, digest_id: int) -> str:
        """构建日报邮件的HTML内容"""
        html_template = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI洞察助手 - 日报通知</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            border-bottom: 3px solid #007bff;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #007bff;
            margin: 0;
            font-size: 28px;
        }}
        .header .subtitle {{
            color: #666;
            font-size: 16px;
            margin-top: 10px;
        }}
        .content {{
            margin-bottom: 30px;
        }}
        .digest-preview {{
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 20px;
            margin: 20px 0;
        }}
        .digest-preview h3 {{
            color: #495057;
            margin-top: 0;
        }}
        .digest-preview p {{
            margin: 10px 0;
            color: #6c757d;
        }}
        .action-buttons {{
            text-align: center;
            margin: 30px 0;
        }}
        .btn {{
            display: inline-block;
            padding: 12px 24px;
            margin: 0 10px;
            background-color: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            transition: background-color 0.3s;
        }}
        .btn:hover {{
            background-color: #0056b3;
        }}
        .btn-secondary {{
            background-color: #6c757d;
        }}
        .btn-secondary:hover {{
            background-color: #545b62;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
            color: #666;
            font-size: 14px;
        }}
        .stats {{
            background-color: #e9ecef;
            border-radius: 5px;
            padding: 15px;
            margin: 20px 0;
            text-align: center;
        }}
        .stats .stat-item {{
            display: inline-block;
            margin: 0 20px;
        }}
        .stats .stat-number {{
            font-size: 24px;
            font-weight: bold;
            color: #007bff;
        }}
        .stats .stat-label {{
            font-size: 14px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI洞察助手</h1>
            <div class="subtitle">每日AI领域洞察报告</div>
        </div>
        
        <div class="content">
            <h2>📰 日报草稿已生成</h2>
            <p>您好！AI洞察助手已经为您生成了今日的《AI先锋日报》草稿，请及时审核和发布。</p>
            
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-number">{digest_id}</div>
                    <div class="stat-label">日报ID</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{datetime.now().strftime('%Y-%m-%d')}</div>
                    <div class="stat-label">生成日期</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{len(digest_content)}</div>
                    <div class="stat-label">内容长度</div>
                </div>
            </div>
            
            <div class="digest-preview">
                <h3>📋 日报内容预览</h3>
                <p>{digest_content[:500]}{'...' if len(digest_content) > 500 else ''}</p>
            </div>
            
            <div class="action-buttons">
                <a href="http://localhost:5000" class="btn">🔍 查看完整日报</a>
                <a href="http://localhost:5000/history" class="btn btn-secondary">📚 查看历史日报</a>
            </div>
            
            <h3>📋 审核步骤</h3>
            <ol>
                <li><strong>查看内容</strong>: 点击上方按钮查看完整日报</li>
                <li><strong>审核内容</strong>: 检查AI生成的内容是否准确</li>
                <li><strong>编辑调整</strong>: 根据需要修改或删除条目</li>
                <li><strong>确认发布</strong>: 满意后点击"确认并发布"</li>
                <li><strong>分发到群</strong>: 复制内容到微信群发送</li>
            </ol>
        </div>
        
        <div class="footer">
            <p>此邮件由AI洞察助手自动发送，请勿回复</p>
            <p>如有问题，请查看系统日志或联系技术支持</p>
            <p>发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
        """
        
        return html_template
    
    def _send_email(self, to_email: str, subject: str, 
                    text_content: str = None, html_content: str = None) -> bool:
        """发送邮件"""
        try:
            # 创建邮件对象
            msg = MIMEMultipart('alternative')
            msg['From'] = self.username
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # 添加文本内容
            if text_content:
                text_part = MIMEText(text_content, 'plain', 'utf-8')
                msg.attach(text_part)
            
            # 添加HTML内容
            if html_content:
                html_part = MIMEText(html_content, 'html', 'utf-8')
                msg.attach(html_part)
            
            # 连接SMTP服务器
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # 启用TLS加密
            
            # 登录
            server.login(self.username, self.password)
            
            # 发送邮件
            server.send_message(msg)
            
            # 关闭连接
            server.quit()
            
            return True
            
        except Exception as e:
            logger.error(f"邮件发送失败: {e}")
            return False
    
    def test_connection(self) -> bool:
        """测试邮件服务器连接"""
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.quit()
            
            logger.info("邮件服务器连接测试成功")
            return True
            
        except Exception as e:
            logger.error(f"邮件服务器连接测试失败: {e}")
            return False


if __name__ == "__main__":
    # 测试代码
    try:
        sender = EmailSender()
        
        # 测试连接
        if sender.test_connection():
            print("✅ 邮件服务器连接正常")
            
            # 测试发送通知
            test_content = "这是一条测试邮件，用于验证邮件发送功能是否正常。"
            success = sender.send_system_notification(
                title="AI洞察助手 - 邮件测试",
                message=test_content
            )
            
            if success:
                print("✅ 测试邮件发送成功")
            else:
                print("❌ 测试邮件发送失败")
        else:
            print("❌ 邮件服务器连接失败")
            
    except Exception as e:
        print(f"邮件发送器初始化失败: {e}")
