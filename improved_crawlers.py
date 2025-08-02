"""
Improved Real Data Crawler - Tập trung vào data thật chất lượng cao
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests
import json
import re
from bs4 import BeautifulSoup
import time

from crawlers.base_crawler import BaseCrawler, LichData
from models.calendar_models import CalendarDay, DataNormalizer

class ImprovedLichVnCrawler(BaseCrawler):
    """Improved crawler cho lichvn.net với data chất lượng cao"""
    
    def __init__(self, delay: float = 2.0, max_retries: int = 3):
        super().__init__(delay, max_retries)
        self.source_name = "lichvn.net"
        self.base_url = "https://lichvn.net"
    
    def crawl_month(self, year: int, month: int) -> List[CalendarDay]:
        """Crawl data cho một tháng"""
        self.logger.info(f"Crawling lichvn.net for {year}/{month:02d}")
        
        # Try different URL patterns
        url_patterns = [
            f"{self.base_url}/lich-van-nien/{year}/{month:02d}",
            f"{self.base_url}/lich-am/{year}/{month:02d}",
            f"{self.base_url}/lich/{year}-{month:02d}"
        ]
        
        for url in url_patterns:
            try:
                response = self.retry_request(url)
                if response and response.status_code == 200:
                    return self._parse_month_page(response.text, year, month)
                    
            except Exception as e:
                self.logger.warning(f"Failed URL {url}: {e}")
                continue
        
        self.logger.error(f"All URLs failed for {year}/{month:02d}")
        return []
    
    def _parse_month_page(self, html: str, year: int, month: int) -> List[CalendarDay]:
        """Parse trang tháng để lấy dữ liệu"""
        soup = BeautifulSoup(html, 'html.parser')
        days = []
        
        # Look for calendar table or grid
        calendar_selectors = [
            '.calendar-month table',
            '.lich-thang table',
            '.month-calendar',
            'table.calendar'
        ]
        
        calendar_element = None
        for selector in calendar_selectors:
            calendar_element = soup.select_one(selector)
            if calendar_element:
                break
        
        if not calendar_element:
            self.logger.warning("Không tìm thấy calendar table")
            return []
        
        # Parse calendar table
        rows = calendar_element.find_all('tr')
        
        for row in rows[1:]:  # Skip header row
            cells = row.find_all(['td', 'th'])
            
            for cell in cells:
                day_data = self._parse_day_cell(cell, year, month)
                if day_data:
                    days.append(day_data)
        
        return days
    
    def _parse_day_cell(self, cell, year: int, month: int) -> Optional[CalendarDay]:
        """Parse một ô ngày"""
        try:
            # Extract solar day number
            day_num = None
            day_text = cell.get_text(strip=True)
            
            # Look for day number
            day_match = re.search(r'(\d+)', day_text)
            if day_match:
                day_num = int(day_match.group(1))
            else:
                return None
            
            if day_num < 1 or day_num > 31:
                return None
            
            solar_date = f"{year}-{month:02d}-{day_num:02d}"
            
            # Extract lunar date
            lunar_date = ""
            lunar_match = re.search(r'(\d+/\d+)', day_text)
            if lunar_match:
                lunar_date = lunar_match.group(1)
            
            # Extract can chi
            can_chi_day = None
            can_chi_patterns = [
                r'([A-ZĂÂÔƯÊỐĐ][a-zăâôưêếốớữ]+\s+[A-ZĂÂÔƯÊỐĐ][a-zăâôưêếốớữ]+)',
                r'(Giáp|Ất|Bính|Đinh|Mậu|Kỷ|Canh|Tân|Nhâm|Quý)\s+(Tý|Sửu|Dần|Mão|Thìn|Tỵ|Ngọ|Mùi|Thân|Dậu|Tuất|Hợi)'
            ]
            
            for pattern in can_chi_patterns:
                match = re.search(pattern, day_text)
                if match:
                    can_chi_day = match.group(1)
                    break
            
            # Determine day of week
            try:
                date_obj = datetime.strptime(solar_date, '%Y-%m-%d')
                day_of_week = date_obj.isoweekday() % 7 + 1
            except:
                day_of_week = 1
            
            # Create CalendarDay
            return CalendarDay(
                solar_date=solar_date,
                lunar_date=DataNormalizer.normalize_lunar_date(lunar_date),
                day_of_week=day_of_week,
                can_chi_day=DataNormalizer.normalize_can_chi(can_chi_day),
                source=self.source_name,
                crawled_at=datetime.now().isoformat(),
                notes=day_text
            )
            
        except Exception as e:
            self.logger.warning(f"Error parsing day cell: {e}")
            return None

class ImprovedLichVietCrawler(BaseCrawler):
    """Improved crawler cho lichviet.app với Playwright"""
    
    def __init__(self, delay: float = 2.0, max_retries: int = 3):
        super().__init__(delay, max_retries)
        self.source_name = "lichviet.app"
        self.base_url = "https://lichviet.app"
    
    def crawl_month(self, year: int, month: int) -> List[CalendarDay]:
        """Crawl với Playwright cho dynamic content"""
        self.logger.info(f"Crawling lichviet.app for {year}/{month:02d}")
        
        try:
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # Set longer timeout for slow pages
                page.set_default_timeout(30000)
                
                url = f"{self.base_url}/{year}/{month:02d}"
                page.goto(url)
                
                # Wait for calendar to load
                try:
                    page.wait_for_selector('.calendar-container, .lich-thang, .month-view', timeout=15000)
                except:
                    self.logger.warning("Calendar container not found, trying alternative selectors")
                
                # Get page content
                html = page.content()
                browser.close()
                
                return self._parse_lichviet_html(html, year, month)
                
        except Exception as e:
            self.logger.error(f"Playwright crawl failed: {e}")
            return []
    
    def _parse_lichviet_html(self, html: str, year: int, month: int) -> List[CalendarDay]:
        """Parse HTML từ lichviet.app"""
        soup = BeautifulSoup(html, 'html.parser')
        days = []
        
        # Look for day elements
        day_selectors = [
            '.day-item',
            '.calendar-day',
            '.lich-ngay',
            '[data-date]'
        ]
        
        day_elements = []
        for selector in day_selectors:
            day_elements = soup.select(selector)
            if day_elements:
                break
        
        if not day_elements:
            self.logger.warning("Không tìm thấy day elements")
            return []
        
        for element in day_elements:
            day_data = self._parse_lichviet_day(element, year, month)
            if day_data:
                days.append(day_data)
        
        return days
    
    def _parse_lichviet_day(self, element, year: int, month: int) -> Optional[CalendarDay]:
        """Parse một ngày từ lichviet.app"""
        try:
            # Get date from data attribute or text
            date_str = element.get('data-date')
            if not date_str:
                # Extract from text
                text = element.get_text()
                day_match = re.search(r'(\d+)', text)
                if day_match:
                    day_num = int(day_match.group(1))
                    date_str = f"{year}-{month:02d}-{day_num:02d}"
                else:
                    return None
            
            # Parse other information
            lunar_date = ""
            can_chi_day = ""
            
            # Look for lunar date in sub-elements
            lunar_elem = element.select_one('.lunar-date, .am-lich, .ngay-am')
            if lunar_elem:
                lunar_date = lunar_elem.get_text(strip=True)
            
            # Look for can chi
            canchi_elem = element.select_one('.can-chi, .canchi')
            if canchi_elem:
                can_chi_day = canchi_elem.get_text(strip=True)
            
            # Check if good/bad day
            is_good_day = None
            if 'good-day' in element.get('class', []) or 'hoang-dao' in element.get('class', []):
                is_good_day = True
            elif 'bad-day' in element.get('class', []) or 'hac-dao' in element.get('class', []):
                is_good_day = False
            
            # Get day of week
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                day_of_week = date_obj.isoweekday() % 7 + 1
            except:
                day_of_week = 1
            
            return CalendarDay(
                solar_date=date_str,
                lunar_date=DataNormalizer.normalize_lunar_date(lunar_date),
                day_of_week=day_of_week,
                can_chi_day=DataNormalizer.normalize_can_chi(can_chi_day),
                is_good_day=is_good_day,
                source=self.source_name,
                crawled_at=datetime.now().isoformat(),
                notes=element.get_text()
            )
            
        except Exception as e:
            self.logger.warning(f"Error parsing lichviet day: {e}")
            return None

class QualityDataCrawler:
    """Manager cho các improved crawlers để lấy data chất lượng cao"""
    
    def __init__(self):
        self.crawlers = {
            'lichvn': ImprovedLichVnCrawler(),
            'lichviet': ImprovedLichVietCrawler()
        }
    
    def crawl_month_from_all_sources(self, year: int, month: int) -> Dict[str, List[CalendarDay]]:
        """Crawl từ tất cả nguồn cho một tháng"""
        results = {}
        
        for source_name, crawler in self.crawlers.items():
            print(f"🔍 Crawling {source_name} for {year}/{month:02d}...")
            
            try:
                days = crawler.crawl_month(year, month)
                if days:
                    results[source_name] = days
                    print(f"✅ {source_name}: {len(days)} days")
                else:
                    print(f"⚠️ {source_name}: No data")
                    
                # Rate limiting
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ {source_name}: {e}")
        
        return results
    
    def save_quality_data(self, year: int, month: int, data: Dict[str, List[CalendarDay]]):
        """Lưu data chất lượng cao"""
        from production_data_manager import ProductionDataManager
        
        pdm = ProductionDataManager()
        
        for source_name, days in data.items():
            if days:
                # Convert to dict format
                data_dicts = [day.to_dict() for day in days]
                
                # Save raw data
                date_range = f"{year}-{month:02d}"
                pdm.save_data(data_dicts, f"{source_name}.improved", date_range)
        
        # Merge and create API data
        monthly_calendar = pdm.merge_sources_by_month(year, month)
        if monthly_calendar:
            print(f"🎯 Tạo API data thành công cho {year}/{month:02d}")

def main():
    """Test improved crawlers"""
    print("🚀 IMPROVED DATA CRAWLER")
    print("=" * 40)
    
    crawler = QualityDataCrawler()
    
    # Test với tháng hiện tại
    now = datetime.now()
    year, month = now.year, now.month
    
    print(f"Testing crawl for {year}/{month:02d}")
    
    # Crawl from all sources
    results = crawler.crawl_month_from_all_sources(year, month)
    
    # Save quality data
    if results:
        crawler.save_quality_data(year, month, results)
        print("✅ Quality data saved!")
    else:
        print("❌ No quality data obtained")

if __name__ == "__main__":
    main()
