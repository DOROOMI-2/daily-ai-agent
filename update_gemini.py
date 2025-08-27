#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini 서비스에서 Alpha Vantage 언급을 KIS API로 변경
"""

def update_gemini_service():
    """gemini_service.py에서 Alpha Vantage 언급을 KIS API로 변경"""
    
    # 원본 파일 읽기
    with open('services/gemini_service.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Alpha Vantage 언급을 KIS API로 변경
    replacements = [
        ('미국 증시 (Alpha Vantage):', '미국 증시 (KIS API):'),
        ('Alpha Vantage API 키 확인 필요', 'KIS API 키 확인 필요'),
        ('# 미국 증시 (Alpha Vantage 데이터만)', '# 미국 증시 (KIS API)'),
    ]
    
    for old, new in replacements:
        content = content.replace(old, new)
    
    # 파일 저장
    with open('services/gemini_service.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Gemini 서비스에서 Alpha Vantage 언급이 KIS API로 변경되었습니다!")

if __name__ == "__main__":
    update_gemini_service()
