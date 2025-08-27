#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Gemini AI 서비스
Google Generative AI를 활용하여 텍스트 생성 및 분석을 수행합니다.
"""

import os
import logging
from typing import Optional
import google.generativeai as genai

class GeminiService:
    """Google Gemini AI를 활용하는 서비스 클래스"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api_key = os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            self.logger.error("GEMINI_API_KEY가 설정되지 않았습니다.")
            raise ValueError("GEMINI_API_KEY 환경변수가 필요합니다.")
        
        # Gemini API 설정
        genai.configure(api_key=self.api_key)
        
        # 모델 설정
        self.model_name = "gemini-2.5-pro"
        self.model = genai.GenerativeModel(self.model_name)
        
        # 생성 설정
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 2048,
        }
        
        # 안전 설정
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
        
        self.logger.info("Gemini Service 초기화 완료")
    
    def generate_text(self, prompt: str) -> Optional[str]:
        """텍스트 생성"""
        try:
            self.logger.info("Gemini AI로 텍스트 생성 시작")
            
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
            
            if response.text:
                self.logger.info("텍스트 생성 완료")
                return response.text
            else:
                self.logger.error("Gemini API에서 텍스트를 생성하지 못했습니다.")
                return None
                
        except Exception as e:
            self.logger.error(f"Gemini API 호출 중 오류: {e}")
            return None
    
    def generate_daily_report(self, weather_data: dict, stock_data: dict) -> Optional[str]:
        """일일 보고서 생성을 위한 특화된 메서드"""
        try:
            # 날씨 데이터 포맷팅
            weather_summary = self._format_weather_for_prompt(weather_data)
            
            # 증시 데이터 포맷팅
            stock_summary = self._format_stock_for_prompt(stock_data)
            
            prompt = f"""
오늘의 일일 정보 보고서를 작성해주세요.

**날씨 정보:**
{weather_summary}

**증시 정보:**
{stock_summary}

다음 형식으로 친근하고 유용한 일일 보고서를 작성해주세요:

# 🌅 오늘의 일일 브리핑

## 📊 날씨 정보
- 현재 상황과 외출 시 주의사항
- 옷차림 추천
- 하루 날씨 전망

## 📈 증시 동향
- 한국 증시 현황 분석
- 미국 증시 현황 분석
- 주요 이슈와 투자 포인트

## 💡 오늘의 추천사항
- 날씨를 고려한 하루 계획
- 증시 상황을 고려한 경제 관련 조언
- 오늘 하루를 위한 긍정적인 메시지

보고서는 한국어로, 이모지를 적절히 사용하여 읽기 쉽고 친근하게 작성해주세요.
"""
            
            return self.generate_text(prompt)
            
        except Exception as e:
            self.logger.error(f"일일 보고서 생성 중 오류: {e}")
            return None
    
    def _format_weather_for_prompt(self, weather_data: dict) -> str:
        """날씨 데이터를 프롬프트용으로 포맷팅"""
        if not weather_data:
            return "날씨 정보를 가져올 수 없습니다."
        
        formatted_parts = []
        
        for location, data in weather_data.items():
            if data:
                part = f"""
{location}:
- 위치: {data.get('location', 'N/A')}
- 기온: {data.get('temperature', 'N/A')}°C ({data.get('temperature_description', 'N/A')})
- 체감온도: {data.get('feels_like', 'N/A')}°C
- 날씨: {data.get('weather_description', 'N/A')}
- 습도: {data.get('humidity', 'N/A')}%
- 바람: {data.get('wind_speed', 'N/A')}m/s ({data.get('wind_description', 'N/A')})
- 가시거리: {data.get('visibility', 'N/A')}km
"""
                formatted_parts.append(part.strip())
        
        return '\n\n'.join(formatted_parts) if formatted_parts else "날씨 정보 없음"
    
    def _format_stock_for_prompt(self, stock_data: dict) -> str:
        """증시 데이터를 프롬프트용으로 포맷팅 (실제 데이터만)"""
        if not stock_data:
            return "증시 정보를 가져올 수 없습니다."
        
        formatted_parts = []
        
        # 한국 증시 (KIS API 데이터만)
        if 'korean' in stock_data and stock_data['korean']:
            korean_part = "한국 증시 (KIS API):\n"
            for data in stock_data['korean']:
                change_sign = '+' if data['change'] >= 0 else ''
                korean_part += f"- {data['name']}: {data['current_price']:,} ({change_sign}{data['change']:,}, {change_sign}{data['change_percent']:.2f}%) {data.get('trend_emoji', '')}\n"
            formatted_parts.append(korean_part.strip())
        else:
            formatted_parts.append("한국 증시: 데이터 수집 실패 (KIS API 키 확인 필요)")
        
        # 미국 증시 (KIS API)
        if 'us' in stock_data and stock_data['us']:
            us_part = "미국 증시 (KIS API):\n"
            for data in stock_data['us']:
                change_sign = '+' if data['change'] >= 0 else ''
                us_part += f"- {data['name']}: ${data['current_price']:,} ({change_sign}{data['change']:,}, {change_sign}{data['change_percent']:.2f}%) {data.get('trend_emoji', '')}\n"
            formatted_parts.append(us_part.strip())
        else:
            formatted_parts.append("미국 증시: 데이터 수집 실패 (KIS API 키 확인 필요)")
        
        return '\n\n'.join(formatted_parts)
    
    def analyze_market_sentiment(self, stock_data: dict) -> Optional[str]:
        """증시 데이터 기반 시장 심리 분석"""
        try:
            stock_summary = self._format_stock_for_prompt(stock_data)
            
            prompt = f"""
다음 증시 데이터를 바탕으로 현재 시장 심리와 전망을 분석해주세요:

{stock_summary}

분석해주실 내용:
1. 전반적인 시장 심리 (호재/악재)
2. 한국과 미국 시장의 상관관계
3. 향후 단기 전망
4. 투자자들이 주의할 점

간결하고 명확하게 분석해주세요.
"""
            
            return self.generate_text(prompt)
            
        except Exception as e:
            self.logger.error(f"시장 심리 분석 중 오류: {e}")
            return None
    
    def get_weather_advice(self, weather_data: dict) -> Optional[str]:
        """날씨 데이터 기반 조언 생성"""
        try:
            weather_summary = self._format_weather_for_prompt(weather_data)
            
            prompt = f"""
다음 날씨 정보를 바탕으로 오늘 하루 외출 시 조언을 해주세요:

{weather_summary}

다음 내용을 포함해서 조언해주세요:
1. 적절한 옷차림
2. 외출 시 준비물
3. 교통 상황 고려사항
4. 건강 관리 팁

친근하고 실용적인 조언으로 작성해주세요.
"""
            
            return self.generate_text(prompt)
            
        except Exception as e:
            self.logger.error(f"날씨 조언 생성 중 오류: {e}")
            return None
