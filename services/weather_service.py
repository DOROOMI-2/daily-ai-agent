#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
날씨 정보 수집 서비스
OpenWeatherMap API를 활용하여 날씨 정보를 가져옵니다.
"""

import os
import requests
import logging
from datetime import datetime
from typing import Dict, Optional

class WeatherService:
    """날씨 정보를 수집하는 서비스 클래스"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        
        if not self.api_key:
            self.logger.warning("OPENWEATHER_API_KEY가 설정되지 않았습니다.")
    
    def get_weather_by_city(self, city: str, state: str = "") -> Optional[Dict]:
        """도시명으로 날씨 정보 조회"""
        try:
            query = f"{city},{state}" if state else city
            
            params = {
                'q': query,
                'appid': self.api_key,
                'units': 'metric',  # 섭씨 온도
                'lang': 'kr'  # 한국어
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return self._format_weather_data(data)
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"날씨 API 요청 실패 ({city}): {e}")
            return None
        except Exception as e:
            self.logger.error(f"날씨 데이터 처리 중 오류 ({city}): {e}")
            return None
    
    def get_weather_by_location(self, location: str, city: str = "") -> Optional[Dict]:
        """특정 위치로 날씨 정보 조회"""
        try:
            # 위치 정보를 도시와 함께 검색
            query = f"{location},{city}" if city else location
            
            params = {
                'q': query,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'kr'
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return self._format_weather_data(data)
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"날씨 API 요청 실패 ({location}): {e}")
            return None
        except Exception as e:
            self.logger.error(f"날씨 데이터 처리 중 오류 ({location}): {e}")
            return None
    
    def get_weather_by_coordinates(self, lat: float, lon: float) -> Optional[Dict]:
        """위도/경도로 날씨 정보 조회"""
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'kr'
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return self._format_weather_data(data)
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"날씨 API 요청 실패 (위경도: {lat}, {lon}): {e}")
            return None
        except Exception as e:
            self.logger.error(f"날씨 데이터 처리 중 오류 (위경도: {lat}, {lon}): {e}")
            return None
    
    def _format_weather_data(self, raw_data: Dict) -> Dict:
        """API 응답 데이터를 포맷팅"""
        try:
            weather = raw_data['weather'][0]
            main = raw_data['main']
            wind = raw_data.get('wind', {})
            
            formatted_data = {
                'location': raw_data['name'],
                'country': raw_data['sys']['country'],
                'temperature': round(main['temp']),
                'feels_like': round(main['feels_like']),
                'humidity': main['humidity'],
                'pressure': main['pressure'],
                'weather_main': weather['main'],
                'weather_description': weather['description'],
                'wind_speed': wind.get('speed', 0),
                'wind_direction': wind.get('deg', 0),
                'visibility': raw_data.get('visibility', 0) / 1000,  # km 단위
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # 온도 체감 설명 추가
            temp = formatted_data['temperature']
            if temp >= 30:
                temp_feel = "매우 더운"
            elif temp >= 25:
                temp_feel = "더운"
            elif temp >= 20:
                temp_feel = "따뜻한"
            elif temp >= 15:
                temp_feel = "선선한"
            elif temp >= 10:
                temp_feel = "쌀쌀한"
            elif temp >= 5:
                temp_feel = "추운"
            else:
                temp_feel = "매우 추운"
            
            formatted_data['temperature_description'] = temp_feel
            
            # 바람 강도 설명 추가
            wind_speed = formatted_data['wind_speed']
            if wind_speed < 1:
                wind_desc = "바람 없음"
            elif wind_speed < 3.3:
                wind_desc = "약한 바람"
            elif wind_speed < 7.9:
                wind_desc = "보통 바람"
            elif wind_speed < 13.8:
                wind_desc = "강한 바람"
            else:
                wind_desc = "매우 강한 바람"
            
            formatted_data['wind_description'] = wind_desc
            
            return formatted_data
            
        except KeyError as e:
            self.logger.error(f"날씨 데이터 형식 오류: {e}")
            return None
        except Exception as e:
            self.logger.error(f"날씨 데이터 포맷팅 중 오류: {e}")
            return None
    
    def get_weather_summary(self, weather_data: Dict) -> str:
        """날씨 데이터를 요약 문자열로 변환"""
        if not weather_data:
            return "날씨 정보를 가져올 수 없습니다."
        
        try:
            summary = f"""
📍 {weather_data['location']}
🌡️ 기온: {weather_data['temperature']}°C ({weather_data['temperature_description']})
🤚 체감온도: {weather_data['feels_like']}°C
☁️ 날씨: {weather_data['weather_description']}
💧 습도: {weather_data['humidity']}%
💨 바람: {weather_data['wind_speed']}m/s ({weather_data['wind_description']})
👁️ 가시거리: {weather_data['visibility']}km
            """.strip()
            
            return summary
            
        except Exception as e:
            self.logger.error(f"날씨 요약 생성 중 오류: {e}")
            return "날씨 요약 생성에 실패했습니다."
