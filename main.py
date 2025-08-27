#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
매일 오전 6시에 날씨와 증시 정보를 보고하는 AI Agent
Google Gemini LLM을 활용한 일일 리포트 생성기
"""

import os
import schedule
import time
import logging
from datetime import datetime
from dotenv import load_dotenv

from services.weather_service import WeatherService
from services.stock_service import StockService
from services.gemini_service import GeminiService
from services.notification_service import NotificationService

# 환경 변수 로드 - env_example.txt 파일 사용
load_dotenv('env_example.txt')

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('daily_agent.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class DailyAIAgent:
    """매일 아침 정보를 수집하고 보고서를 생성하는 AI Agent"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.weather_service = WeatherService()
        self.stock_service = StockService()
        self.gemini_service = GeminiService()
        self.notification_service = NotificationService()
        
        self.logger.info("Daily AI Agent 초기화 완료")
    
    def collect_weather_data(self):
        """날씨 정보 수집"""
        try:
            # 김포시 날씨
            gimpo_weather = self.weather_service.get_weather_by_city("김포시", "경기도")
            
            # 강남구 날씨
            gangnam_weather = self.weather_service.get_weather_by_city("강남구", "서울")
            
            return {
                "gimpo": gimpo_weather,
                "gangnam_teheran": gangnam_weather
            }
        except Exception as e:
            self.logger.error(f"날씨 데이터 수집 중 오류: {e}")
            return None
    
    def collect_stock_data(self):
        """증시 정보 수집"""
        try:
            # 한국 증시 (KOSPI, KOSDAQ)
            korean_stocks = self.stock_service.get_korean_market_data()
            
            # 미국 증시 (S&P 500, NASDAQ, Dow Jones)
            us_stocks = self.stock_service.get_us_market_data()
            
            return {
                "korean": korean_stocks,
                "us": us_stocks
            }
        except Exception as e:
            self.logger.error(f"증시 데이터 수집 중 오류: {e}")
            return None
    
    def generate_daily_report(self, weather_data, stock_data):
        """Gemini LLM을 활용하여 일일 보고서 생성"""
        try:
            # GeminiService의 전용 메서드 사용
            report = self.gemini_service.generate_daily_report(weather_data, stock_data)
            return report
            
        except Exception as e:
            self.logger.error(f"보고서 생성 중 오류: {e}")
            return None
    
    def run_daily_report(self):
        """매일 실행되는 메인 보고서 생성 함수"""
        self.logger.info("일일 보고서 생성 시작")
        
        try:
            # 1. 데이터 수집
            weather_data = self.collect_weather_data()
            stock_data = self.collect_stock_data()
            
            # 2. 보고서 생성
            if weather_data and stock_data:
                report = self.generate_daily_report(weather_data, stock_data)
                
                if report:
                    # 3. 보고서 저장
                    self.save_report(report)
                    
                    # 4. 알림 전송
                    self.notification_service.send_report(report)
                    
                    self.logger.info("일일 보고서 생성 및 전송 완료")
                else:
                    self.logger.error("보고서 생성 실패")
            else:
                self.logger.error("데이터 수집 실패")
                
        except Exception as e:
            self.logger.error(f"일일 보고서 실행 중 오류: {e}")
    
    def save_report(self, report):
        """보고서를 파일로 저장"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reports/daily_report_{timestamp}.txt"
            
            os.makedirs("reports", exist_ok=True)
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(report)
            
            self.logger.info(f"보고서 저장 완료: {filename}")
            
        except Exception as e:
            self.logger.error(f"보고서 저장 중 오류: {e}")
    
    def start_scheduler(self):
        """스케줄러 시작 - 매일 오전 6시 실행"""
        schedule.every().day.at("06:00").do(self.run_daily_report)
        
        self.logger.info("스케줄러 시작 - 매일 오전 6시에 보고서 생성")
        
        # 즉시 테스트 실행 (선택사항)
        self.run_daily_report()
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # 1분마다 체크

def main():
    """메인 실행 함수"""
    print("🤖 Daily AI Agent 시작")
    print("=" * 50)
    
    agent = DailyAIAgent()
    
    try:
        agent.start_scheduler()
    except KeyboardInterrupt:
        print("\n프로그램이 사용자에 의해 중단되었습니다.")
    except Exception as e:
        logging.error(f"예상치 못한 오류: {e}")

if __name__ == "__main__":
    main()
