"""
Công cụ phát hiện và test trang web lịch âm
Tìm kiếm các trang web hoạt động và format URL đúng
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import re
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebsiteDiscovery:
    """Công cụ phát hiện trang web lịch âm hoạt động"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Danh sách các trang web tiềm năng
        self.potential_sites = [
            'lichviet.app',
            'lichvn.net', 
            'tuvi.vn',
            'lichvannien.net',
            'lichngaytot.com',
            'licham365.vn',
            'lichvannien365.com',
            'lich.com.vn',
            'lichamnguyet.net',
            'lichvansu.net',
            '24h.com.vn',
            'dantri.com.vn',
            'vietnamnet.vn',
            'vnexpress.net',
            'baomoi.com',
            'kenh14.vn',
            'cafef.vn',
            'tinhte.vn'
        ]
        
        # Các pattern URL phổ biến cho lịch âm
        self.url_patterns = [
            '/lich-am/{year}/{month}',
            '/lich-van-nien/{year}-{month:02d}',
            '/lich-van-nien/thang-{month}-{year}.html',
            '/lich/{year}/{month}',
            '/calendar/{year}/{month}',
            '/{year}/{month:02d}',
            '/lich-am/{year}/{month:02d}',
            '/lich-am-duong/{year}/{month}',
            '/lunar-calendar/{year}/{month}',
            '/lich/{year}-{month:02d}',
            '/van-nien/{year}/{month}'
        ]
        
        # Selector patterns để tìm calendar data
        self.calendar_selectors = [
            '.calendar',
            '.calendar-container',
            '.lich-container',
            '.month-calendar',
            '.date-picker',
            '.calendar-wrapper',
            'table.calendar',
            '.lunar-calendar',
            '.am-lich',
            '.lich-am',
            '[class*="calendar"]',
            '[class*="lich"]',
            'td[data-date]',
            '.day-cell',
            '.calendar-day'
        ]

    def test_site_homepage(self, domain: str) -> Dict:
        """Test trang chủ của website"""
        result = {
            'domain': domain,
            'status': 'error',
            'accessible': False,
            'has_calendar_links': False,
            'calendar_links': [],
            'title': '',
            'error': None
        }
        
        try:
            url = f"https://{domain}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                result['status'] = 'success'
                result['accessible'] = True
                
                soup = BeautifulSoup(response.content, 'html.parser')
                title_text = soup.title.string if soup.title and soup.title.string else 'No title'
                result['title'] = title_text.strip() if title_text else 'No title'
                
                # Tìm links liên quan đến lịch
                calendar_keywords = ['lich', 'calendar', 'am', 'duong', 'van-nien', 'lunar']
                links = soup.find_all('a', href=True)
                
                for link in links:
                    href_attr = link.get('href') if hasattr(link, 'get') else None
                    href = str(href_attr).lower() if href_attr else ''
                    text = link.get_text().lower()
                    
                    if any(keyword in href or keyword in text for keyword in calendar_keywords):
                        full_url = urljoin(url, str(href_attr))
                        result['calendar_links'].append({
                            'url': full_url,
                            'text': link.get_text().strip()
                        })
                
                result['has_calendar_links'] = len(result['calendar_links']) > 0
                
            else:
                result['status'] = f'status_{response.status_code}'
                
        except requests.exceptions.RequestException as e:
            result['error'] = str(e)
            logger.warning(f"Lỗi kết nối {domain}: {e}")
            
        return result

    def test_calendar_url(self, domain: str, pattern: str, year: int = 2025, month: int = 7) -> Dict:
        """Test một URL pattern cụ thể"""
        result = {
            'domain': domain,
            'pattern': pattern,
            'url': '',
            'status': 'error',
            'has_calendar_data': False,
            'calendar_elements': 0,
            'content_length': 0,
            'title': '',
            'error': None
        }
        
        try:
            # Tạo URL từ pattern
            path = pattern.format(year=year, month=month)
            url = f"https://{domain}{path}"
            result['url'] = url
            
            response = self.session.get(url, timeout=10)
            result['content_length'] = len(response.content)
            
            if response.status_code == 200:
                result['status'] = 'success'
                
                soup = BeautifulSoup(response.content, 'html.parser')
                title_text = soup.title.string if soup.title and soup.title.string else 'No title'
                result['title'] = title_text.strip() if title_text else 'No title'
                
                # Kiểm tra có calendar data không
                calendar_elements = 0
                for selector in self.calendar_selectors:
                    elements = soup.select(selector)
                    calendar_elements += len(elements)
                
                result['calendar_elements'] = calendar_elements
                result['has_calendar_data'] = calendar_elements > 0
                
                # Tìm dữ liệu ngày cụ thể
                date_patterns = [
                    r'\d{1,2}\/\d{1,2}\/\d{4}',  # dd/mm/yyyy
                    r'\d{4}-\d{1,2}-\d{1,2}',    # yyyy-mm-dd
                    r'ngày \d{1,2}',              # ngày dd
                    r'can.*chi',                  # can chi
                    r'giáp|ất|bính|đinh|mậu|kỷ|canh|tân|nhâm|quý',  # can
                    r'tý|sửu|dần|mão|thìn|tỵ|ngọ|mùi|thân|dậu|tuất|hợi'  # chi
                ]
                
                text_content = soup.get_text().lower()
                for pattern_regex in date_patterns:
                    if re.search(pattern_regex, text_content):
                        result['has_calendar_data'] = True
                        break
                        
            else:
                result['status'] = f'status_{response.status_code}'
                
        except requests.exceptions.RequestException as e:
            result['error'] = str(e)
            
        return result

    def discover_working_sites(self) -> Dict:
        """Tìm kiếm tất cả trang web hoạt động"""
        logger.info("🔍 Bắt đầu phát hiện trang web hoạt động...")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'sites_tested': len(self.potential_sites),
            'patterns_tested': len(self.url_patterns),
            'homepage_results': [],
            'calendar_results': [],
            'working_sites': [],
            'summary': {}
        }
        
        # Test trang chủ
        logger.info("📖 Testing homepages...")
        for domain in self.potential_sites:
            logger.info(f"Testing {domain}...")
            result = self.test_site_homepage(domain)
            results['homepage_results'].append(result)
            time.sleep(1)  # Rate limiting
        
        # Test calendar URLs
        logger.info("📅 Testing calendar URLs...")
        for domain in self.potential_sites:
            for pattern in self.url_patterns:
                logger.info(f"Testing {domain} with pattern {pattern}...")
                result = self.test_calendar_url(domain, pattern)
                results['calendar_results'].append(result)
                time.sleep(0.5)  # Rate limiting
        
        # Phân tích kết quả
        working_sites = []
        accessible_sites = [r for r in results['homepage_results'] if r['accessible']]
        calendar_sites = [r for r in results['calendar_results'] if r['has_calendar_data']]
        
        # Tổng hợp sites hoạt động
        for site in calendar_sites:
            domain = site['domain']
            
            # Tìm thông tin homepage tương ứng
            homepage_info = next((r for r in accessible_sites if r['domain'] == domain), None)
            
            working_site = {
                'domain': domain,
                'homepage_accessible': homepage_info is not None,
                'calendar_url': site['url'],
                'calendar_pattern': site['pattern'],
                'calendar_elements': site['calendar_elements'],
                'title': site['title'],
                'calendar_links': homepage_info['calendar_links'] if homepage_info else []
            }
            
            working_sites.append(working_site)
        
        results['working_sites'] = working_sites
        
        # Tạo summary
        results['summary'] = {
            'total_sites': len(self.potential_sites),
            'accessible_homepages': len(accessible_sites),
            'sites_with_calendar_data': len(calendar_sites),
            'working_sites': len(working_sites),
            'success_rate': f"{len(working_sites)/len(self.potential_sites)*100:.1f}%"
        }
        
        logger.info(f"✅ Hoàn thành! Tìm thấy {len(working_sites)} trang web hoạt động")
        return results

    def save_results(self, results: Dict, filename: Optional[str] = None):
        """Lưu kết quả phát hiện"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"website_discovery_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 Đã lưu kết quả vào {filename}")

def main():
    """Chạy website discovery"""
    discovery = WebsiteDiscovery()
    results = discovery.discover_working_sites()
    
    discovery.save_results(results)
    
    # In kết quả summary
    print("\n" + "="*50)
    print("📊 KẾT QUẢ PHÁT HIỆN WEBSITE")
    print("="*50)
    
    summary = results['summary']
    print(f"🌐 Tổng số sites test: {summary['total_sites']}")
    print(f"✅ Homepages accessible: {summary['accessible_homepages']}")
    print(f"📅 Sites có calendar data: {summary['sites_with_calendar_data']}")
    print(f"🎯 Sites hoạt động tốt: {summary['working_sites']}")
    print(f"📈 Tỷ lệ thành công: {summary['success_rate']}")
    
    print("\n🎯 DANH SÁCH SITES HOẠT động:")
    print("-"*30)
    for site in results['working_sites']:
        print(f"• {site['domain']}")
        print(f"  📍 URL: {site['calendar_url']}")
        print(f"  📊 Elements: {site['calendar_elements']}")
        print(f"  📖 Title: {site['title']}")
        print()

if __name__ == "__main__":
    main()
