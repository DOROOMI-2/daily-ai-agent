#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
알림 전송 서비스
이메일, 콘솔 출력 등을 통해 보고서를 전송합니다.
"""

import os
import smtplib
import logging
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from typing import Optional, List

# 텔레그램 봇 import (선택적)
try:
    from telegram import Bot
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    print("⚠️ python-telegram-bot이 설치되지 않았습니다. 텔레그램 기능이 비활성화됩니다.")

class NotificationService:
    """알림 전송을 담당하는 서비스 클래스"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 이메일 설정
        self.email_user = os.getenv('EMAIL_USER')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        self.email_recipient = os.getenv('EMAIL_RECIPIENT')
        
        # 텔레그램 설정
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        # SMTP 설정 (Gmail 기준)
        self.smtp_server = 'smtp.gmail.com'
        self.smtp_port = 587
        
        # 이메일 활성화 여부
        if not all([self.email_user, self.email_password, self.email_recipient]):
            self.logger.warning("이메일 설정이 완료되지 않았습니다.")
            self.email_enabled = False
        else:
            self.email_enabled = True
            self.logger.info("이메일 알림 서비스가 활성화되었습니다.")
        
        # 텔레그램 활성화 여부
        if not TELEGRAM_AVAILABLE:
            self.telegram_enabled = False
            self.logger.warning("python-telegram-bot이 설치되지 않았습니다.")
        elif not all([self.telegram_bot_token, self.telegram_chat_id]):
            self.logger.warning("텔레그램 설정이 완료되지 않았습니다.")
            self.telegram_enabled = False
        else:
            self.telegram_enabled = True
            self.telegram_bot = Bot(token=self.telegram_bot_token)
            self.logger.info("텔레그램 알림 서비스가 활성화되었습니다.")
    
    def send_report(self, report: str, method: str = "all") -> bool:
        """보고서 전송"""
        try:
            success = True
            
            if method in ["all", "console"]:
                self._send_to_console(report)
            
            if method in ["all", "email"] and self.email_enabled:
                email_success = self._send_email(report)
                success = success and email_success
            
            if method in ["all", "telegram"] and self.telegram_enabled:
                telegram_success = self._send_telegram(report)
                success = success and telegram_success
            
            return success
            
        except Exception as e:
            self.logger.error(f"보고서 전송 중 오류: {e}")
            return False
    
    def _send_to_console(self, report: str) -> None:
        """콘솔에 보고서 출력"""
        try:
            print("\n" + "="*60)
            print("🤖 DAILY AI AGENT REPORT")
            print("="*60)
            print(report)
            print("="*60)
            print(f"📅 생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*60 + "\n")
            
            self.logger.info("콘솔 출력 완료")
            
        except Exception as e:
            self.logger.error(f"콘솔 출력 중 오류: {e}")
    
    def _send_email(self, report: str, subject_prefix: str = "") -> bool:
        """이메일로 보고서 전송"""
        try:
            # 이메일 제목
            date_str = datetime.now().strftime('%Y-%m-%d')
            subject = f"{subject_prefix}📊 일일 AI 보고서 - {date_str}"
            
            # 이메일 본문 HTML 포맷팅
            html_body = self._format_report_to_html(report)
            
            # 이메일 메시지 생성
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_user
            msg['To'] = self.email_recipient
            msg['Subject'] = subject
            
            # 텍스트 버전
            text_part = MIMEText(report, 'plain', 'utf-8')
            msg.attach(text_part)
            
            # HTML 버전
            html_part = MIMEText(html_body, 'html', 'utf-8')
            msg.attach(html_part)
            
            # SMTP 서버 연결 및 전송
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
            
            self.logger.info(f"이메일 전송 완료: {self.email_recipient}")
            return True
            
        except Exception as e:
            self.logger.error(f"이메일 전송 중 오류: {e}")
            return False
    
    def _send_telegram(self, report: str) -> bool:
        """텔레그램으로 보고서 전송"""
        try:
            # 텔레그램 메시지 길이 제한 (4096자)
            max_length = 4000  # 안전 마진
            
            if len(report) > max_length:
                # 메시지가 너무 길면 분할 전송
                chunks = [report[i:i+max_length] for i in range(0, len(report), max_length)]
                
                for i, chunk in enumerate(chunks):
                    message = f"📊 일일 보고서 ({i+1}/{len(chunks)})\n\n{chunk}"
                    
                    # 동기 방식으로 전송
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        loop.run_until_complete(
                            self.telegram_bot.send_message(
                                chat_id=self.telegram_chat_id,
                                text=message,
                                parse_mode='Markdown'
                            )
                        )
                    finally:
                        loop.close()
            else:
                # 한 번에 전송
                message = f"🤖 Daily AI Agent 보고서\n\n{report}"
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(
                        self.telegram_bot.send_message(
                            chat_id=self.telegram_chat_id,
                            text=message,
                            parse_mode='Markdown'
                        )
                    )
                finally:
                    loop.close()
            
            self.logger.info(f"텔레그램 전송 완료: {self.telegram_chat_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"텔레그램 전송 중 오류: {e}")
            return False
    
    def _format_report_to_html(self, report: str) -> str:
        """보고서를 HTML 형식으로 변환"""
        try:
            # 마크다운 스타일의 텍스트를 HTML로 변환
            html_content = report.replace('\n', '<br>')
            
            # 제목 스타일링
            html_content = html_content.replace('# ', '<h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px;">')
            html_content = html_content.replace('<br>## ', '</h2><h3 style="color: #34495e; margin-top: 20px;">')
            html_content = html_content.replace('## ', '<h3 style="color: #34495e; margin-top: 20px;">')
            
            # 이모지와 불릿 포인트 스타일링
            html_content = html_content.replace('- ', '<li style="margin: 5px 0;">')
            html_content = html_content.replace('<li style="margin: 5px 0;">', '<ul style="padding-left: 20px;"><li style="margin: 5px 0;">', 1)
            
            # 기본 HTML 템플릿
            html_template = f"""
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        line-height: 1.6;
                        color: #2c3e50;
                        max-width: 800px;
                        margin: 0 auto;
                        padding: 20px;
                        background-color: #f8f9fa;
                    }}
                    .container {{
                        background-color: white;
                        padding: 30px;
                        border-radius: 10px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    .header {{
                        text-align: center;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 20px;
                        border-radius: 10px;
                        margin-bottom: 20px;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 30px;
                        padding: 15px;
                        background-color: #ecf0f1;
                        border-radius: 5px;
                        font-size: 12px;
                        color: #7f8c8d;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🤖 Daily AI Agent Report</h1>
                        <p>📅 {datetime.now().strftime('%Y년 %m월 %d일 (%A)')}</p>
                    </div>
                    <div class="content">
                        {html_content}
                    </div>
                    <div class="footer">
                        <p>이 보고서는 Daily AI Agent에 의해 자동 생성되었습니다.</p>
                        <p>생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return html_template
            
        except Exception as e:
            self.logger.error(f"HTML 포맷팅 중 오류: {e}")
            return f"<html><body><pre>{report}</pre></body></html>"
    
    def send_error_notification(self, error_message: str) -> bool:
        """오류 알림 전송"""
        try:
            error_report = f"""
⚠️ Daily AI Agent 오류 발생

시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
오류 내용: {error_message}

시스템을 확인해주세요.
"""
            
            success = True
            
            # 콘솔 출력
            self._send_to_console(error_report)
            
            # 이메일 전송 (가능한 경우)
            if self.email_enabled:
                email_success = self._send_email(error_report, "[오류] ")
                success = success and email_success
            
            # 텔레그램 전송 (가능한 경우)
            if self.telegram_enabled:
                telegram_success = self._send_telegram(error_report)
                success = success and telegram_success
            
            return success
            
        except Exception as e:
            self.logger.error(f"오류 알림 전송 중 오류: {e}")
            return False
    
    def send_test_notification(self) -> bool:
        """테스트 알림 전송"""
        try:
            test_report = f"""
🧪 Daily AI Agent 테스트 알림

이것은 테스트 메시지입니다.
시스템이 정상적으로 작동하고 있습니다.

시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
상태: ✅ 정상
"""
            
            return self.send_report(test_report)
            
        except Exception as e:
            self.logger.error(f"테스트 알림 전송 중 오류: {e}")
            return False
    
    def configure_email(self, email_user: str, email_password: str, email_recipient: str) -> bool:
        """이메일 설정 업데이트"""
        try:
            self.email_user = email_user
            self.email_password = email_password
            self.email_recipient = email_recipient
            self.email_enabled = True
            
            self.logger.info("이메일 설정이 업데이트되었습니다.")
            return True
            
        except Exception as e:
            self.logger.error(f"이메일 설정 업데이트 중 오류: {e}")
            return False
    
    def get_status(self) -> dict:
        """알림 서비스 상태 반환"""
        return {
            'email_enabled': self.email_enabled,
            'email_user': self.email_user,
            'email_recipient': self.email_recipient,
            'smtp_server': self.smtp_server,
            'smtp_port': self.smtp_port,
            'telegram_enabled': self.telegram_enabled,
            'telegram_chat_id': self.telegram_chat_id,
            'telegram_available': TELEGRAM_AVAILABLE
        }
