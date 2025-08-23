"""
通知模块
负责发送各种通知，包括邮件通知等
"""

from .email_sender import EmailSender

__all__ = ['EmailSender']
