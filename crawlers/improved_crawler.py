"""
Cải tiến Generic Crawler với khả năng tìm kiếm API và trang web thực
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import json
import re
import logging

if __name__ == "__main__":
    import sys
    sys.path.append('..')
    from base_crawler import BaseCrawler, LichData
else:
    from .base_crawler import BaseCrawler, LichData

class ImprovedCalendarCrawler(BaseCrawler):
    """Crawler cải tiến với khả năng tự động tìm kiếm nguồn dữ liệu"""
    
    def __init__(self, delay: float = 1.0, max_retries: int = 3):
        super().__init__(delay, max_retries)
        self.source_name = "improved_calendar"
        
        # APIs có thể hoạt động
        self.working_apis = []
        self.last_api_check = None
        
        # Các trang web backup
        self.backup_sites = [
            {
                'name': 'lichsu.org',
                'url': 'http://lichsu.org/lich-van-nien-{year}.html',
                'parser': self.parse_lichsu_org
            },
            {
                'name': 'thiendia.com',
                'url': 'https://thiendia.com/lich-am-{year}-{month:02d}.html',
                'parser': self.parse_thiendia_com
            }
        ]

    def discover_real_apis(self) -> List[Dict]:
        """Tìm kiếm APIs thực sự hoạt động"""
        
        # Một số API endpoint khả thi
        potential_endpoints = [
            "https://api.batdongsan.com.vn/v2/lich-van-nien/{year}/{month}",
            "https://services.vnexpress.net/calendar/lunar/{year}/{month}",
            "https://api.24h.com.vn/calendar/{year}-{month:02d}",
            "https://lichapi.thuongmai.vn/v1/calendar/{year}/{month}",
            "https://calendar-api.vietnamnet.vn/lunar/{year}/{month}",
            # GitHub-hosted APIs
            "https://raw.githubusercontent.com/vietnamese-lunar-calendar/data/main/{year}/{month:02d}.json",
            "https://api.github.com/repos/lichvannien-vietnam/data/contents/{year}/{month:02d}.json"
        ]
        
        working = []
        
        for endpoint_template in potential_endpoints:
            try:
                # Test với tháng hiện tại
                test_url = endpoint_template.format(year=2025, month=7)
                response = requests.get(test_url, timeout=5, headers={
                    'User-Agent': 'Vietnamese Calendar Crawler/1.0'
                })
                
                if response.status_code == 200:
                    # Kiểm tra content có hợp lệ không
                    content = response.text.strip()
                    if content and len(content) > 50:  # Có data
                        try:
                            json_data = response.json()
                            if json_data:  # Có JSON hợp lệ
                                working.append({
                                    'endpoint': endpoint_template,
                                    'test_url': test_url,
                                    'sample_response': json_data
                                })
                                self.logger.info(f"✅ Tìm thấy API hoạt động: {test_url}")
                        except json.JSONDecodeError:
                            # Không phải JSON nhưng có thể là HTML có ích
                            if 'lich' in content.lower() or 'calendar' in content.lower():
                                working.append({
                                    'endpoint': endpoint_template,
                                    'test_url': test_url,
                                    'type': 'html',
                                    'sample_length': len(content)
                                })
                                
            except Exception as e:
                self.logger.debug(f"API test failed for {endpoint_template}: {e}")
                
        self.working_apis = working
        self.last_api_check = datetime.now()
        return working

    def crawl_month(self, year: int, month: int) -> List[LichData]:
        """Crawl dữ liệu tháng với multiple fallback strategies"""
        
        # 1. Thử APIs đã tìm thấy
        if not self.working_apis or (self.last_api_check and 
            (datetime.now() - self.last_api_check).total_seconds() > 86400):  # 24 hours
            self.discover_real_apis()
            
        for api in self.working_apis:
            try:
                data = self.crawl_from_api(api, year, month)
                if data:
                    self.logger.info(f"✅ Crawl thành công từ API: {api['endpoint']}")
                    return data
            except Exception as e:
                self.logger.debug(f"API crawl failed: {e}")
        
        # 2. Thử các trang web backup
        for site in self.backup_sites:
            try:
                data = self.crawl_from_website(site, year, month)
                if data:
                    self.logger.info(f"✅ Crawl thành công từ website: {site['name']}")
                    return data
            except Exception as e:
                self.logger.debug(f"Website crawl failed for {site['name']}: {e}")
        
        # 3. Fallback: Tạo dữ liệu cơ bản nhưng có thêm thông tin lunar
        self.logger.warning(f"Không tìm thấy dữ liệu online, tạo dữ liệu hybrid cho {month}/{year}")
        return self.generate_hybrid_calendar(year, month)

    def crawl_from_api(self, api: Dict, year: int, month: int) -> List[LichData]:
        """Crawl từ API endpoint"""
        try:
            url = api['endpoint'].format(year=year, month=month)
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Vietnamese Calendar Crawler/1.0'
            })
            
            if response.status_code == 200:
                if api.get('type') == 'html':
                    soup = BeautifulSoup(response.content, 'html.parser')
                    return self.parse_html_content(soup, year, month)
                else:
                    json_data = response.json()
                    return self.parse_json_content(json_data, year, month)
                    
        except Exception as e:
            self.logger.debug(f"API crawl error: {e}")
            
        return []

    def crawl_from_website(self, site: Dict, year: int, month: int) -> List[LichData]:
        """Crawl từ website backup"""
        try:
            url = site['url'].format(year=year, month=month)
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            })
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                return site['parser'](soup, year, month)
                
        except Exception as e:
            self.logger.debug(f"Website crawl error: {e}")
            
        return []

    def parse_json_content(self, json_data: Any, year: int, month: int) -> List[LichData]:
        """Parse JSON response từ API"""
        data = []
        
        try:
            if isinstance(json_data, dict):
                # Xử lý format: {"days": [...]}
                if 'days' in json_data:
                    for day_info in json_data['days']:
                        item = self.parse_day_json(day_info)
                        if item:
                            data.append(item)
                            
                # Xử lý format: {"2025-07-01": {...}}
                elif any(self.looks_like_date(key) for key in json_data.keys()):
                    for date_key, day_info in json_data.items():
                        if self.looks_like_date(date_key):
                            item = self.parse_day_json(day_info, date_key)
                            if item:
                                data.append(item)
                                
            elif isinstance(json_data, list):
                # Xử lý format: [{date: "", lunar: ""}, ...]
                for day_info in json_data:
                    item = self.parse_day_json(day_info)
                    if item:
                        data.append(item)
                        
        except Exception as e:
            self.logger.debug(f"JSON parse error: {e}")
            
        return data

    def parse_html_content(self, soup: BeautifulSoup, year: int, month: int) -> List[LichData]:
        """Parse HTML content để tìm dữ liệu lịch"""
        data = []
        
        # Tìm tables, divs có chứa calendar data
        calendar_containers = soup.find_all(['table', 'div'], 
                                          class_=re.compile(r'calendar|lich|month', re.I))
        
        for container in calendar_containers:
            # Tìm các cells/ngày
            day_elements = []
            if hasattr(container, 'find_all'):
                day_elements = container.find_all(['td', 'div', 'span'], 
                                                class_=re.compile(r'day|date|ngay', re.I))
            
            for element in day_elements:
                try:
                    item = self.extract_day_from_html(element, year, month)
                    if item:
                        data.append(item)
                except Exception as e:
                    self.logger.debug(f"HTML element parse error: {e}")
                    
        return data

    def parse_day_json(self, day_info: Dict, date_key: Optional[str] = None) -> Optional[LichData]:
        """Parse thông tin 1 ngày từ JSON"""
        try:
            # Tìm solar date
            solar_date = date_key or day_info.get('date') or day_info.get('solar_date')
            if not solar_date:
                return None
                
            # Chuẩn hóa date format
            if not re.match(r'\d{4}-\d{2}-\d{2}', solar_date):
                solar_date = self.normalize_date_format(solar_date)
                
            if not solar_date:
                return None
                
            return LichData(
                solar_date=solar_date,
                lunar_date=day_info.get('lunar_date', day_info.get('lunar', '')),
                can_chi_day=day_info.get('can_chi_day', day_info.get('can_chi', '')),
                can_chi_month=day_info.get('can_chi_month', ''),
                can_chi_year=day_info.get('can_chi_year', ''),
                holiday=day_info.get('holiday', day_info.get('event', '')),
                notes=day_info.get('notes', day_info.get('description', '')),
                source=self.source_name
            )
            
        except Exception as e:
            self.logger.debug(f"Day JSON parse error: {e}")
            return None

    def extract_day_from_html(self, element, year: int, month: int) -> Optional[LichData]:
        """Trích xuất thông tin ngày từ HTML element"""
        try:
            text = element.get_text(strip=True)
            
            # Tìm số ngày
            day_match = re.search(r'\b(\d{1,2})\b', text)
            if not day_match:
                return None
                
            day = int(day_match.group(1))
            if day < 1 or day > 31:
                return None
                
            solar_date = f"{year}-{month:02d}-{day:02d}"
            
            # Tìm thông tin lunar và can chi trong text
            lunar_date = ''
            can_chi = ''
            
            lunar_match = re.search(r'(\d{1,2})[\/\-](\d{1,2})', text)
            if lunar_match:
                lunar_date = f"{lunar_match.group(1)}/{lunar_match.group(2)}"
                
            can_chi_match = re.search(r'(Giáp|Ất|Bính|Đinh|Mậu|Kỷ|Canh|Tân|Nhâm|Quý)\s*(Tý|Sửu|Dần|Mão|Thìn|Tỵ|Ngọ|Mùi|Thân|Dậu|Tuất|Hợi)', text)
            if can_chi_match:
                can_chi = f"{can_chi_match.group(1)} {can_chi_match.group(2)}"
                
            return LichData(
                solar_date=solar_date,
                lunar_date=lunar_date,
                can_chi_day=can_chi,
                can_chi_month='',
                can_chi_year='',
                holiday='',
                notes='',
                source=self.source_name
            )
            
        except Exception as e:
            self.logger.debug(f"HTML extraction error: {e}")
            return None

    def generate_hybrid_calendar(self, year: int, month: int) -> List[LichData]:
        """Tạo calendar hybrid có thêm thông tin lunar đơn giản"""
        import calendar
        
        data = []
        cal = calendar.monthcalendar(year, month)
        
        # Lunar calendar offset đơn giản (không chính xác 100% nhưng có thể sử dụng)
        lunar_offset = self.calculate_simple_lunar_offset(year, month)
        
        for week in cal:
            for day in week:
                if day == 0:
                    continue
                    
                solar_date = f"{year}-{month:02d}-{day:02d}"
                
                # Tính lunar date đơn giản
                lunar_day = (day + lunar_offset) % 30 + 1
                lunar_month = month
                if lunar_day > 29:
                    lunar_month = (month % 12) + 1
                    lunar_day = lunar_day - 29
                    
                lunar_date = f"{lunar_day:02d}/{lunar_month:02d}"
                
                # Tạo can chi đơn giản (không chính xác nhưng có pattern)
                can_chi = self.generate_simple_can_chi(year, month, day)
                
                data.append(LichData(
                    solar_date=solar_date,
                    lunar_date=lunar_date,
                    can_chi_day=can_chi,
                    can_chi_month='',
                    can_chi_year='',
                    holiday='',
                    notes='Dữ liệu hybrid - cần xác thực',
                    source='hybrid_generator'
                ))
                
        return data

    def calculate_simple_lunar_offset(self, year: int, month: int) -> int:
        """Tính offset đơn giản cho lunar calendar"""
        # Công thức đơn giản, không chính xác nhưng có pattern
        base_offset = (year - 2000) * 11 + (month - 1) * 2
        return base_offset % 30

    def generate_simple_can_chi(self, year: int, month: int, day: int) -> str:
        """Tạo can chi đơn giản"""
        can = ['Giáp', 'Ất', 'Bính', 'Đinh', 'Mậu', 'Kỷ', 'Canh', 'Tân', 'Nhâm', 'Quý']
        chi = ['Tý', 'Sửu', 'Dần', 'Mão', 'Thìn', 'Tỵ', 'Ngọ', 'Mùi', 'Thân', 'Dậu', 'Tuất', 'Hợi']
        
        # Tính index dựa trên ngày
        total_days = year * 365 + month * 30 + day
        can_index = total_days % 10
        chi_index = total_days % 12
        
        return f"{can[can_index]} {chi[chi_index]}"

    def parse_lichsu_org(self, soup: BeautifulSoup, year: int, month: int) -> List[LichData]:
        """Parser cho lichsu.org"""
        # Placeholder - cần implement dựa trên HTML structure thực
        return []

    def parse_thiendia_com(self, soup: BeautifulSoup, year: int, month: int) -> List[LichData]:
        """Parser cho thiendia.com"""
        # Placeholder - cần implement dựa trên HTML structure thực
        return []

    def looks_like_date(self, text: str) -> bool:
        """Kiểm tra text có giống date format không"""
        return bool(re.match(r'\d{4}-\d{2}-\d{2}', text))

    def normalize_date_format(self, date_str: str) -> Optional[str]:
        """Chuẩn hóa date format"""
        try:
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

    def crawl_date(self, date: datetime) -> Optional[LichData]:
        """Crawl dữ liệu cho một ngày cụ thể"""
        data = self.crawl_month(date.year, date.month)
        target_date = date.strftime('%Y-%m-%d')
        
        for item in data:
            if item.solar_date == target_date:
                return item
        return None

def main():
    """Test improved crawler"""
    crawler = ImprovedCalendarCrawler()
    
    print("🔍 Discovering APIs...")
    apis = crawler.discover_real_apis()
    print(f"Found {len(apis)} working APIs:")
    for api in apis:
        print(f"  - {api['endpoint']}")
        if 'sample_response' in api:
            print(f"    Sample keys: {list(api['sample_response'].keys()) if isinstance(api['sample_response'], dict) else 'list'}")
    
    print("\n📅 Testing month crawl...")
    data = crawler.crawl_month(2025, 7)
    print(f"Crawled {len(data)} days")
    
    if data:
        print("\n📊 Sample data:")
        for item in data[:5]:
            print(f"  {item.solar_date}: {item.lunar_date} | {item.can_chi_day} | {item.source}")

if __name__ == "__main__":
    main()
