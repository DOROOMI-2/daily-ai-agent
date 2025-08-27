#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KIS API 전용 버전 테스트
"""

import os
from dotenv import load_dotenv
from services.stock_service import StockService

# 환경 변수 로드
load_dotenv('env_example.txt')

def test_kis_only():
    """KIS API 전용 버전 테스트"""
    print("🔧 KIS API 전용 버전 테스트...")
    
    # StockService 초기화
    stock_service = StockService()
    
    # 상태 확인
    status = stock_service.get_status()
    print(f"\n📋 서비스 상태:")
    for key, value in status.items():
        print(f"  • {key}: {value}")
    
    print(f"\n📊 설정된 API 키:")
    print(f"  • KIS APP KEY: {os.getenv('KIS_APP_KEY', 'Not Set')}")
    print(f"  • KIS APP SECRET: {'***' if os.getenv('KIS_APP_SECRET') else 'Not Set'}")
    
    # KIS API 키가 설정되지 않았을 때의 동작 확인
    if not status['kis_configured']:
        print(f"\n⚠️ KIS API 키가 설정되지 않았습니다.")
        print(f"  실제 데이터 수집은 API 키 발급 후 가능합니다.")
        
        # 한국 증시 데이터 수집 시도 (실패 예상)
        print(f"\n📈 한국 증시 데이터 수집 시도...")
        korean_data = stock_service.get_korean_market_data()
        print(f"  결과: {len(korean_data)}개 데이터 수집")
        
        # 미국 증시 데이터 수집 시도 (실패 예상)
        print(f"\n🇺🇸 미국 증시 데이터 수집 시도...")
        us_data = stock_service.get_us_market_data()
        print(f"  결과: {len(us_data)}개 데이터 수집")
    else:
        print(f"\n✅ KIS API 키가 설정되었습니다! 실제 데이터 수집을 시도할 수 있습니다.")

if __name__ == "__main__":
    test_kis_only()
