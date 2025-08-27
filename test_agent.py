#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Daily AI Agent 테스트 스크립트
각 서비스의 기능을 개별적으로 테스트합니다.
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 프로젝트 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.weather_service import WeatherService
from services.stock_service import StockService
from services.gemini_service import GeminiService
from services.notification_service import NotificationService

def test_weather_service():
    """WeatherService 테스트"""
    print("🌤️ WeatherService 테스트 시작...")
    
    try:
        weather_service = WeatherService()
        
        # 김포시 날씨 테스트
        print("📍 김포시 날씨 조회 중...")
        gimpo_weather = weather_service.get_weather_by_city("김포시", "경기도")
        
        if gimpo_weather:
            print("✅ 김포시 날씨 조회 성공")
            print(weather_service.get_weather_summary(gimpo_weather))
        else:
            print("❌ 김포시 날씨 조회 실패")
        
        # 강남구 날씨 테스트
        print("\n📍 강남구 날씨 조회 중...")
        gangnam_weather = weather_service.get_weather_by_city("강남구", "서울")
        
        if gangnam_weather:
            print("✅ 강남구 날씨 조회 성공")
            print(weather_service.get_weather_summary(gangnam_weather))
        else:
            print("❌ 강남구 날씨 조회 실패")
        
        return {
            "gimpo": gimpo_weather,
            "gangnam_teheran": gangnam_weather
        }
        
    except Exception as e:
        print(f"❌ WeatherService 테스트 중 오류: {e}")
        return None

def test_stock_service():
    """StockService 테스트 (KIS API + Alpha Vantage 전용)"""
    print("\n📈 StockService 테스트 시작 (KIS API 전용)...")
    
    try:
        stock_service = StockService()
        
        # 상태 확인
        print("📊 StockService 상태 확인:")
        status = stock_service.get_status()
        for key, value in status.items():
            print(f"  {key}: {value}")
        
        # KIS API 설정 확인
        if not status['kis_configured']:
            print("⚠️ KIS API 키가 설정되지 않았습니다. 한국 증시는 더미 데이터로 대체됩니다.")
        
        # 한국 증시 테스트 (KIS API)
        print("\n📊 한국 증시 데이터 조회 중 (KIS API)...")
        korean_stocks = stock_service.get_korean_market_data()
        
        if korean_stocks:
            print(f"✅ 한국 증시 데이터 조회 성공 ({len(korean_stocks)}개 지수)")
            for stock in korean_stocks:
                print(f"  {stock['name']}: {stock['current_price']} ({stock['change_percent']:+.2f}%) [KIS API]")
        else:
            print("❌ 한국 증시 데이터 조회 실패 - KIS API 키를 확인하세요")
        
        # Alpha Vantage 설정 확인
        if not status['alpha_vantage_configured']:
            print("⚠️ Alpha Vantage API 키가 설정되지 않았습니다. 미국 증시 데이터를 수집할 수 없습니다.")
        
        # 미국 증시 테스트 (Alpha Vantage)
        print("\n📊 미국 증시 데이터 조회 중 (Alpha Vantage)...")
        us_stocks = stock_service.get_us_market_data()
        
        if us_stocks:
            print(f"✅ 미국 증시 데이터 조회 성공 ({len(us_stocks)}개 지수)")
            for stock in us_stocks:
                print(f"  {stock['name']}: ${stock['current_price']} ({stock['change_percent']:+.2f}%) [Alpha Vantage]")
        else:
            print("❌ 미국 증시 데이터 조회 실패 - Alpha Vantage API 키를 확인하세요")
        
        return {
            "korean": korean_stocks,
            "us": us_stocks
        }
        
    except Exception as e:
        print(f"❌ StockService 테스트 중 오류: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_gemini_service(weather_data, stock_data):
    """GeminiService 테스트"""
    print("\n🤖 GeminiService 테스트 시작...")
    
    try:
        # API 키 확인
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ GEMINI_API_KEY가 설정되지 않았습니다.")
            print("⚠️ env_example.txt를 참고하여 .env 파일을 생성하고 API 키를 설정해주세요.")
            return None
        
        gemini_service = GeminiService()
        
        print("📝 일일 보고서 생성 중...")
        report = gemini_service.generate_daily_report(weather_data, stock_data)
        
        if report:
            print("✅ 일일 보고서 생성 성공")
            print(f"보고서 길이: {len(report)} 문자")
            print("\n--- 생성된 보고서 미리보기 ---")
            print(report[:300] + "..." if len(report) > 300 else report)
        else:
            print("❌ 일일 보고서 생성 실패")
        
        return report
        
    except Exception as e:
        print(f"❌ GeminiService 테스트 중 오류: {e}")
        return None

def test_notification_service(report):
    """NotificationService 테스트"""
    print("\n📧 NotificationService 테스트 시작...")
    
    try:
        notification_service = NotificationService()
        
        # 상태 확인
        status = notification_service.get_status()
        print(f"이메일 활성화: {status['email_enabled']}")
        print(f"텔레그램 활성화: {status['telegram_enabled']}")
        print(f"텔레그램 라이브러리: {status['telegram_available']}")
        
        if report:
            print("📤 테스트 보고서 전송 중...")
            success = notification_service.send_report(report, method="console")
            
            if success:
                print("✅ 알림 전송 성공")
            else:
                print("❌ 알림 전송 실패")
        else:
            print("❌ 전송할 보고서가 없습니다.")
        
        # 테스트 알림 전송
        print("\n📤 테스트 알림 전송 중...")
        test_success = notification_service.send_test_notification()
        
        if test_success:
            print("✅ 테스트 알림 전송 성공")
        else:
            print("❌ 테스트 알림 전송 실패")
        
        return True
        
    except Exception as e:
        print(f"❌ NotificationService 테스트 중 오류: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("🚀 Daily AI Agent 통합 테스트 시작")
    print("=" * 60)
    print(f"📅 테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 환경 변수 확인
    print("\n🔍 환경 변수 확인...")
    required_vars = ['OPENWEATHER_API_KEY', 'GEMINI_API_KEY']
    optional_vars = ['EMAIL_USER', 'TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID']
    missing_vars = []
    
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var}: 설정됨")
        else:
            print(f"❌ {var}: 설정되지 않음")
            missing_vars.append(var)
    
    print("\n선택사항 환경 변수:")
    for var in optional_vars:
        if os.getenv(var):
            print(f"✅ {var}: 설정됨")
        else:
            print(f"⚪ {var}: 설정되지 않음 (선택사항)")
    
    if missing_vars:
        print(f"\n⚠️ 누락된 환경 변수: {', '.join(missing_vars)}")
        print("env_example.txt를 참고하여 .env 파일을 생성해주세요.")
    
    # 개별 서비스 테스트
    weather_data = test_weather_service()
    stock_data = test_stock_service()
    
    if weather_data and stock_data:
        report = test_gemini_service(weather_data, stock_data)
        test_notification_service(report)
    else:
        print("\n❌ 데이터 수집 실패로 인해 보고서 생성을 건너뜁니다.")
    
    print("\n" + "=" * 60)
    print("🏁 테스트 완료")
    print("=" * 60)

if __name__ == "__main__":
    main()
