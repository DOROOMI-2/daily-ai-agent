"""
주식 시장 데이터를 수집하는 서비스
한국투자증권(KIS) API를 사용하여 한국 증시 데이터 수집
Alpha Vantage API를 사용하여 미국 증시 데이터 수집
"""

import logging
import os
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any


class StockService:
    """증시 정보를 수집하는 서비스 클래스 (KIS API 전용)"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Alpha Vantage API 설정 (미국 증시용)
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.av_base_url = "https://www.alphavantage.co/query"
        
        # KIS API 설정 (한국 증시용)
        self.kis_app_key = os.getenv('KIS_APP_KEY')
        self.kis_app_secret = os.getenv('KIS_APP_SECRET')
        self.kis_base_url = "https://openapi.koreainvestment.com:9443"
        self.kis_access_token = None
        
        self.logger.info("StockService 초기화 완료 (KIS API 전용)")
    
    def _get_kis_access_token(self) -> Optional[str]:
        """KIS API 액세스 토큰 발급"""
        if not self.kis_app_key or not self.kis_app_secret:
            self.logger.warning("KIS API 키가 설정되지 않았습니다.")
            return None
        
        try:
            headers = {'content-type': 'application/json'}
            body = {
                'grant_type': 'client_credentials',
                'appkey': self.kis_app_key,
                'appsecret': self.kis_app_secret
            }
            
            url = f"{self.kis_base_url}/oauth2/tokenP"
            response = requests.post(url, headers=headers, json=body, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            access_token = data.get('access_token')
            
            if access_token:
                self.kis_access_token = access_token
                self.logger.info("KIS API 액세스 토큰 발급 성공")
                return access_token
            else:
                self.logger.error("KIS API 토큰 발급 실패: 토큰이 응답에 없음")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"KIS API 토큰 요청 실패: {e}")
            return None
        except (KeyError, ValueError) as e:
            self.logger.error(f"KIS API 토큰 파싱 오류: {e}")
            return None
        except Exception as e:
            self.logger.error(f"KIS API 토큰 발급 중 예상치 못한 오류: {e}")
            return None
    
    def _get_kis_korean_index_data(self, index_name: str) -> Optional[Dict]:
        """KIS API로 한국 지수 데이터 수집"""
        if not self.kis_access_token:
            token = self._get_kis_access_token()
            if not token:
                return None
        
        try:
            # KIS API 지수 코드 매핑
            index_codes = {
                'KOSPI': '0001',    # KOSPI 지수
                'KOSDAQ': '1001'    # KOSDAQ 지수
            }
            
            if index_name not in index_codes:
                self.logger.warning(f"KIS API에서 지원하지 않는 지수: {index_name}")
                return None
            
            headers = {
                'authorization': f'Bearer {self.kis_access_token}',
                'appkey': self.kis_app_key,
                'appsecret': self.kis_app_secret,
                'tr_id': 'FHPST01010000'  # 지수 시세 조회
            }
            
            params = {
                'fid_cond_mrkt_div_code': 'U',  # 지수
                'fid_input_iscd': index_codes[index_name]
            }
            
            url = f"{self.kis_base_url}/uapi/domestic-stock/v1/quotations/inquire-index-price"
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'output' in data:
                output = data['output']
                
                current_price = float(output.get('bstp_nmix_prpr', 0))  # 지수
                change = float(output.get('bstp_nmix_prdy_vrss', 0))   # 전일대비
                change_percent = float(output.get('prdy_vrss_sign', 0))  # 등락률
                
                # 전일 종가 계산
                previous_close = current_price - change
                
                data_dict = {
                    'name': index_name,
                    'ticker': f'KIS_{index_codes[index_name]}',
                    'current_price': round(current_price, 2),
                    'previous_close': round(previous_close, 2),
                    'change': round(change, 2),
                    'change_percent': round(change_percent, 2),
                    'volume': 0,  # 지수는 거래량 없음
                    'high': round(current_price, 2),  # 임시값
                    'low': round(current_price, 2),   # 임시값
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # 상승/하락 상태 추가
                if change > 0:
                    data_dict['trend'] = '상승'
                    data_dict['trend_emoji'] = '📈'
                elif change < 0:
                    data_dict['trend'] = '하락'
                    data_dict['trend_emoji'] = '📉'
                else:
                    data_dict['trend'] = '보합'
                    data_dict['trend_emoji'] = '➡️'
                
                self.logger.info(f"{index_name} KIS API 데이터 수집 성공: {current_price} ({change_percent:+.2f}%)")
                return data_dict
            else:
                self.logger.error(f"KIS API {index_name} 응답 형식 오류: {data}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"KIS API {index_name} 요청 실패: {e}")
            # 토큰 만료 시 재발급 시도
            if hasattr(e, 'response') and e.response and e.response.status_code == 401:
                self.kis_access_token = None
            return None
        except (KeyError, ValueError, TypeError) as e:
            self.logger.error(f"KIS API {index_name} 데이터 파싱 오류: {e}")
            return None
        except Exception as e:
            self.logger.error(f"KIS API {index_name} 데이터 수집 중 오류: {e}")
            return None
    
    def _get_alpha_vantage_data(self, symbol: str, index_name: str) -> Optional[Dict]:
        """Alpha Vantage API로 미국 증시 데이터 수집"""
        if not self.alpha_vantage_key:
            self.logger.warning("Alpha Vantage API 키가 설정되지 않았습니다.")
            return None
        
        try:
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol,
                'apikey': self.alpha_vantage_key
            }
            
            response = requests.get(self.av_base_url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            if 'Global Quote' in data:
                quote = data['Global Quote']
                
                current_price = float(quote.get('05. price', 0))
                previous_close = float(quote.get('08. previous close', 0))
                change = float(quote.get('09. change', 0))
                change_percent = float(quote.get('10. change percent', '0%').replace('%', ''))
                
                data_dict = {
                    'name': index_name,
                    'ticker': symbol,
                    'current_price': round(current_price, 2),
                    'previous_close': round(previous_close, 2),
                    'change': round(change, 2),
                    'change_percent': round(change_percent, 2),
                    'volume': int(quote.get('06. volume', 0)),
                    'high': round(float(quote.get('03. high', 0)), 2),
                    'low': round(float(quote.get('04. low', 0)), 2),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # 상승/하락 상태 추가
                if change > 0:
                    data_dict['trend'] = '상승'
                    data_dict['trend_emoji'] = '📈'
                elif change < 0:
                    data_dict['trend'] = '하락'
                    data_dict['trend_emoji'] = '📉'
                else:
                    data_dict['trend'] = '보합'
                    data_dict['trend_emoji'] = '➡️'
                
                self.logger.info(f"{index_name} Alpha Vantage 데이터 수집 성공: ${current_price} ({change_percent:+.2f}%)")
                return data_dict
            else:
                self.logger.error(f"Alpha Vantage {symbol} 응답 형식 오류: {data}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Alpha Vantage {symbol} 요청 실패: {e}")
            return None
        except (KeyError, ValueError, TypeError) as e:
            self.logger.error(f"Alpha Vantage {symbol} 데이터 파싱 오류: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Alpha Vantage {symbol} 데이터 수집 중 오류: {e}")
            return None
    

    
    def get_korean_market_data(self) -> List[Dict]:
        """한국 증시 데이터 수집 (KIS API 전용) - 실제 데이터만 반환"""
        self.logger.info("한국 증시 데이터 수집 시작 (KIS API)")
        
        if not self.kis_app_key or not self.kis_app_secret:
            self.logger.error("KIS API 키가 설정되지 않았습니다. 한국 증시 데이터를 수집할 수 없습니다.")
            return []
        
        korean_indices = ['KOSPI', 'KOSDAQ']
        results = []
        
        for index_name in korean_indices:
            self.logger.info(f"{index_name} 데이터 수집 중...")
            
            # KIS API로 시도 - 실패하면 그냥 제외
            data = self._get_kis_korean_index_data(index_name)
            
            if data:
                results.append(data)
                self.logger.info(f"{index_name} 수집 성공: {data['current_price']} ({data['change_percent']:+.2f}%)")
            else:
                self.logger.warning(f"{index_name} KIS API 실패 - 해당 지수 제외")
        
        if results:
            self.logger.info(f"한국 증시 데이터 수집 완료: {len(results)}개 지수")
        else:
            self.logger.error("한국 증시 데이터를 전혀 수집하지 못했습니다.")
        
        return results
    
    def get_us_market_data(self) -> List[Dict]:
        """미국 증시 데이터 수집 (Alpha Vantage API) - 실제 데이터만 반환"""
        self.logger.info("미국 증시 데이터 수집 시작 (Alpha Vantage)")
        
        if not self.alpha_vantage_key:
            self.logger.error("Alpha Vantage API 키가 설정되지 않았습니다. 미국 증시 데이터를 수집할 수 없습니다.")
            return []
        
        us_indices = {
            'S&P 500': 'SPY',
            'NASDAQ': 'QQQ', 
            'Dow Jones': 'DIA'
        }
        
        results = []
        
        for index_name, symbol in us_indices.items():
            self.logger.info(f"{index_name} 데이터 수집 중...")
            
            # Alpha Vantage API로 시도 - 실패하면 그냥 제외
            data = self._get_alpha_vantage_data(symbol, index_name)
            
            if data:
                results.append(data)
                self.logger.info(f"{index_name} 수집 성공: ${data['current_price']} ({data['change_percent']:+.2f}%)")
            else:
                self.logger.warning(f"{index_name} Alpha Vantage 실패 - 해당 지수 제외")
        
        if results:
            self.logger.info(f"미국 증시 데이터 수집 완료: {len(results)}개 지수")
        else:
            self.logger.error("미국 증시 데이터를 전혀 수집하지 못했습니다.")
        
        return results
    
    def get_all_market_data(self) -> Dict[str, List[Dict]]:
        """전체 증시 데이터 수집"""
        self.logger.info("전체 증시 데이터 수집 시작")
        
        korean_data = self.get_korean_market_data()
        us_data = self.get_us_market_data()
        
        result = {
            'korean_markets': korean_data,
            'us_markets': us_data
        }
        
        total_count = len(korean_data) + len(us_data)
        self.logger.info(f"전체 증시 데이터 수집 완료: 총 {total_count}개 지수")
        
        return result
    
    def get_status(self) -> Dict[str, Any]:
        """StockService 상태 확인"""
        status = {
            'service_name': 'StockService (KIS API 전용)',
            'kis_configured': bool(self.kis_app_key and self.kis_app_secret),
            'alpha_vantage_configured': bool(self.alpha_vantage_key),
            'kis_token_valid': bool(self.kis_access_token),
            'supported_korean_indices': ['KOSPI', 'KOSDAQ'],
            'supported_us_indices': ['S&P 500', 'NASDAQ', 'Dow Jones']
        }
        
        return status