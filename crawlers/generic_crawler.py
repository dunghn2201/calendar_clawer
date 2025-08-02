"""
Generic Vietnamese Calendar Crawler
Crawler linh hoạt cho nhiều trang web lịch âm khác nhau
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import json
import re
import time
import logging

if __name__ == "__main__":
    # Fix import for standalone run
    import sys
    sys.path.append('..')
    from base_crawler import BaseCrawler, LichData
else:
    from .base_crawler import BaseCrawler, LichData

class GenericCalendarCrawler(BaseCrawler):
    """Crawler tổng quát cho các trang lịch âm"""
    
    def __init__(self, delay: float = 1.0, max_retries: int = 3):
        super().__init__(delay, max_retries)
        self.source_name = "generic_calendar"
        
        # Cấu hình các patterns để phát hiện dữ liệu lịch
        self.date_patterns = {
            'solar_date': [
                r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',
                r'(\d{4})-(\d{1,2})-(\d{1,2})',
                r'ngày\s*(\d{1,2})',
                r'(\d{1,2})\s*tháng\s*(\d{1,2})'
            ],
            'lunar_date': [
                r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})\s*âm',
                r'âm\s*(\d{1,2})[/-](\d{1,2})',
                r'ngày\s*(\d{1,2})\s*tháng\s*(\d{1,2})\s*âm',
                r'(\d{1,2})\s*\/\s*(\d{1,2})\s*AL'
            ],
            'can_chi': [
                r'(Giáp|Ất|Bính|Đinh|Mậu|Kỷ|Canh|Tân|Nhâm|Quý)\s*(Tý|Sửu|Dần|Mão|Thìn|Tỵ|Ngọ|Mùi|Thân|Dậu|Tuất|Hợi)',
                r'(甲|乙|丙|丁|戊|己|庚|辛|壬|癸)\s*(子|丑|寅|卯|辰|巳|午|未|申|酉|戌|亥)'
            ]
        }
        
        # Cấu hình trang web và URL patterns  
        self.site_configs = {
            'vietnamcalendar.com': {
                'base_url': 'https://vietnamcalendar.com',
                'calendar_path': '/calendar/{year}/{month}',
                'selectors': {
                    'day_cells': '.day, .calendar-day, [data-date]',
                    'lunar_info': '.lunar, .am-lich, .lunar-date',
                    'can_chi': '.can-chi, .canchi'
                }
            },
            'lichamnguyet.org': {
                'base_url': 'https://lichamnguyet.org',
                'calendar_path': '/lich-am/{year}/{month}',
                'selectors': {
                    'day_cells': 'td.day, .calendar-cell',
                    'lunar_info': '.lunar-date, .am-lich'
                }
            }
        }

    def discover_calendar_apis(self) -> List[Dict]:
        """Phát hiện các API lịch âm khả dụng"""
        potential_apis = [
            {
                'name': 'Vietnamese Lunar Calendar API',
                'base_url': 'https://api.vietnamcalendar.com',
                'endpoints': [
                    '/lunar/{year}/{month}',
                    '/calendar/{year}/{month}',
                    '/am-lich/{year}/{month}'
                ]
            },
            {
                'name': 'Lich Am API',
                'base_url': 'https://lichapi.com',
                'endpoints': [
                    '/v1/calendar/{year}/{month}',
                    '/lunar-calendar'
                ]
            }
        ]
        
        working_apis = []
        
        for api_config in potential_apis:
            for endpoint in api_config['endpoints']:
                try:
                    test_url = api_config['base_url'] + endpoint.format(year=2025, month=7)
                    response = requests.get(test_url, timeout=5)
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            if data and isinstance(data, (dict, list)):
                                working_apis.append({
                                    'name': api_config['name'],
                                    'url': test_url,
                                    'response_type': type(data).__name__,
                                    'sample_keys': list(data.keys()) if isinstance(data, dict) else []
                                })
                                self.logger.info(f"✅ Tìm thấy API hoạt động: {test_url}")
                        except json.JSONDecodeError:
                            pass
                            
                except Exception as e:
                    test_url = "unknown"
                    self.logger.debug(f"API test failed for {test_url}: {e}")
                    
        return working_apis

    def crawl_date(self, date: datetime) -> Optional[LichData]:
        """Crawl dữ liệu cho một ngày cụ thể"""
        data = self.crawl_month(date.year, date.month)
        target_date = date.strftime('%Y-%m-%d')
        
        for item in data:
            if item.solar_date == target_date:
                return item
        return None

    def crawl_month(self, year: int, month: int) -> List[LichData]:
        """Crawl dữ liệu một tháng từ nhiều nguồn"""
        all_data = []
        
        # Thử API trước
        api_data = self.try_apis(year, month)
        if api_data:
            all_data.extend(api_data)
            
        # Thử các trang web
        if not all_data:
            web_data = self.try_websites(year, month)
            all_data.extend(web_data)
            
        # Nếu vẫn không có dữ liệu, tạo dữ liệu cơ bản từ calendar Python
        if not all_data:
            self.logger.warning(f"Không tìm thấy dữ liệu online, tạo dữ liệu cơ bản cho {month}/{year}")
            all_data = self.generate_basic_calendar(year, month)
            
        return all_data

    def try_apis(self, year: int, month: int) -> List[LichData]:
        """Thử crawl từ các API"""
        data = []
        apis = self.discover_calendar_apis()
        
        for api in apis:
            try:
                response = requests.get(api['url'], timeout=10)
                if response.status_code == 200:
                    json_data = response.json()
                    parsed_data = self.parse_api_response(json_data, year, month)
                    if parsed_data:
                        data.extend(parsed_data)
                        self.logger.info(f"✅ Crawl API thành công: {api['name']}")
                        break
            except Exception as e:
                self.logger.debug(f"API crawl failed: {e}")
                
        return data

    def try_websites(self, year: int, month: int) -> List[LichData]:
        """Thử crawl từ các trang web"""
        data = []
        
        for site_name, config in self.site_configs.items():
            try:
                calendar_url = config['base_url'] + config['calendar_path'].format(year=year, month=month)
                response = requests.get(calendar_url, timeout=10, headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                })
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    site_data = self.parse_website_response(soup, config, year, month)
                    if site_data:
                        data.extend(site_data)
                        self.logger.info(f"✅ Crawl website thành công: {site_name}")
                        break
                        
            except Exception as e:
                self.logger.debug(f"Website crawl failed for {site_name}: {e}")
                
        return data

    def parse_api_response(self, json_data: Any, year: int, month: int) -> List[LichData]:
        """Parse dữ liệu từ API response"""
        data = []
        
        # Xử lý các format API khác nhau
        if isinstance(json_data, dict):
            # Format 1: {days: [{date: "", lunar: ""}]}
            if 'days' in json_data:
                for day_info in json_data['days']:
                    lich_item = self.extract_lich_data_from_dict(day_info)
                    if lich_item:
                        data.append(lich_item)
                        
            # Format 2: {"2025-07-01": {lunar: ""}, "2025-07-02": {...}}
            elif any(self.is_date_key(key) for key in json_data.keys()):
                for date_key, day_info in json_data.items():
                    if self.is_date_key(date_key):
                        lich_item = self.extract_lich_data_from_dict(day_info, date_key)
                        if lich_item:
                            data.append(lich_item)
                            
        elif isinstance(json_data, list):
            # Format 3: [{date: "", lunar: ""}, ...]
            for day_info in json_data:
                lich_item = self.extract_lich_data_from_dict(day_info)
                if lich_item:
                    data.append(lich_item)
                    
        return data

    def parse_website_response(self, soup: BeautifulSoup, config: Dict, year: int, month: int) -> List[LichData]:
        """Parse dữ liệu từ website HTML"""
        data = []
        selectors = config['selectors']
        
        # Tìm các ô ngày trong calendar
        day_cells = soup.select(selectors['day_cells'])
        
        for cell in day_cells:
            try:
                lich_item = self.extract_lich_data_from_html(cell, year, month)
                if lich_item:
                    data.append(lich_item)
            except Exception as e:
                self.logger.debug(f"Error parsing day cell: {e}")
                
        return data

    def extract_lich_data_from_dict(self, day_info: Dict, date_key: Optional[str] = None) -> Optional[LichData]:
        """Trích xuất LichData từ dictionary"""
        try:
            # Tìm solar date
            solar_date = None
            if date_key:
                solar_date = date_key
            elif 'date' in day_info:
                solar_date = day_info['date']
            elif 'solar_date' in day_info:
                solar_date = day_info['solar_date']
                
            if not solar_date:
                return None
                
            # Chuẩn hóa format date
            if not re.match(r'\d{4}-\d{2}-\d{2}', solar_date):
                # Thử parse các format khác
                solar_date = self.normalize_date(solar_date)
                
            if not solar_date:
                return None
                
            # Trích xuất thông tin khác
            lunar_date = day_info.get('lunar_date', day_info.get('lunar', ''))
            can_chi_day = day_info.get('can_chi_day', day_info.get('can_chi', ''))
            can_chi_month = day_info.get('can_chi_month', '')
            can_chi_year = day_info.get('can_chi_year', '')
            holiday = day_info.get('holiday', day_info.get('event', ''))
            notes = day_info.get('notes', day_info.get('description', ''))
            
            return LichData(
                solar_date=solar_date,
                lunar_date=lunar_date,
                can_chi_day=can_chi_day,
                can_chi_month=can_chi_month,
                can_chi_year=can_chi_year,
                holiday=holiday,
                notes=notes,
                source=self.source_name
            )
            
        except Exception as e:
            self.logger.debug(f"Error extracting from dict: {e}")
            return None

    def extract_lich_data_from_html(self, cell, year: int, month: int) -> Optional[LichData]:
        """Trích xuất LichData từ HTML element"""
        try:
            # Lấy text content của cell
            text = cell.get_text(strip=True)
            
            # Tìm solar date
            solar_day = None
            data_date = cell.get('data-date')
            if data_date:
                solar_day = data_date
            else:
                # Tìm số ngày trong text
                day_match = re.search(r'\b(\d{1,2})\b', text)
                if day_match:
                    solar_day = f"{year}-{month:02d}-{int(day_match.group(1)):02d}"
                    
            if not solar_day:
                return None
                
            # Tìm thông tin lunar
            lunar_date = ''
            can_chi = ''
            
            # Tìm lunar date trong text
            lunar_matches = re.findall(r'(\d{1,2})[\/\-](\d{1,2})', text)
            if lunar_matches:
                lunar_date = f"{lunar_matches[0][0]}/{lunar_matches[0][1]}"
                
            # Tìm can chi
            can_chi_match = re.search(r'(Giáp|Ất|Bính|Đinh|Mậu|Kỷ|Canh|Tân|Nhâm|Quý)\s*(Tý|Sửu|Dần|Mão|Thìn|Tỵ|Ngọ|Mùi|Thân|Dậu|Tuất|Hợi)', text)
            if can_chi_match:
                can_chi = f"{can_chi_match.group(1)} {can_chi_match.group(2)}"
                
            return LichData(
                solar_date=solar_day,
                lunar_date=lunar_date,
                can_chi_day=can_chi,
                can_chi_month='',
                can_chi_year='',
                holiday='',
                notes='',
                source=self.source_name
            )
            
        except Exception as e:
            self.logger.debug(f"Error extracting from HTML: {e}")
            return None

    def generate_basic_calendar(self, year: int, month: int) -> List[LichData]:
        """Tạo dữ liệu calendar cơ bản từ thư viện Python"""
        import calendar
        
        data = []
        cal = calendar.monthcalendar(year, month)
        
        for week in cal:
            for day in week:
                if day == 0:  # Ngày trống
                    continue
                    
                solar_date = f"{year}-{month:02d}-{day:02d}"
                
                # Tạo một số thông tin cơ bản
                lich_item = LichData(
                    solar_date=solar_date,
                    lunar_date='',  # Để trống, cần tính toán phức tạp
                    can_chi_day='',
                    can_chi_month='',
                    can_chi_year='',
                    holiday='',
                    notes='Dữ liệu cơ bản từ calendar Python',
                    source='python_calendar'
                )
                
                data.append(lich_item)
                
        return data

    def is_date_key(self, key: str) -> bool:
        """Kiểm tra key có phải là date format không"""
        return bool(re.match(r'\d{4}-\d{2}-\d{2}', key))

    def normalize_date(self, date_str: str) -> Optional[str]:
        """Chuẩn hóa date string về format YYYY-MM-DD"""
        try:
            # Thử các format khác nhau
            formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%m/%d/%Y']
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue
                    
            return None
        except:
            return None

def main():
    """Test crawler"""
    crawler = GenericCalendarCrawler()
    
    # Test discovery
    apis = crawler.discover_calendar_apis()
    print(f"Found {len(apis)} working APIs:")
    for api in apis:
        print(f"  - {api['name']}: {api['url']}")
    
    # Test crawl
    data = crawler.crawl_month(2025, 7)
    print(f"\nCrawled {len(data)} days of data")
    
    if data:
        print("Sample data:")
        for item in data[:3]:
            print(f"  {item.solar_date}: {item.lunar_date} ({item.source})")

if __name__ == "__main__":
    main()
