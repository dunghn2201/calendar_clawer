"""
Test crawler cho các website lịch Việt để tìm nguồn data tốt nhất
"""

import requests
from bs4 import BeautifulSoup
import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import json

class WebsiteTest:
    """Test tính khả dụng của các website lịch"""
    
    def __init__(self):
        self.results = {}
        
    async def test_lichamnguyet_vn(self):
        """Test lichamnguyet.vn - Website mới"""
        try:
            url = "https://lichamnguyet.vn/lich-am-duong/2024/7"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                calendar_data = soup.find('table', class_='calendar') or soup.find('div', class_='calendar')
                if calendar_data:
                    return {"status": "success", "has_data": True, "url": url}
            return {"status": "no_data", "url": url}
        except Exception as e:
            return {"status": "error", "error": str(e), "url": url}
    
    async def test_24h_com_vn(self):
        """Test 24h.com.vn - Trang tin tức có section lịch"""
        try:
            url = "https://www.24h.com.vn/lich-van-nien/7-2024.html"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                calendar_data = soup.find('table') or soup.find('div', class_='calendar')
                if calendar_data and len(soup.text) > 5000:  # Có nội dung đủ nhiều
                    return {"status": "success", "has_data": True, "url": url}
            return {"status": "no_data", "url": url}
        except Exception as e:
            return {"status": "error", "error": str(e), "url": url}
    
    async def test_lich123_vn(self):
        """Test lich123.vn"""
        try:
            url = "https://lich123.vn/lich-am/2024/7"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                calendar_data = soup.find('table') or soup.find('.calendar')
                if calendar_data:
                    return {"status": "success", "has_data": True, "url": url}
            return {"status": "no_data", "url": url}  
        except Exception as e:
            return {"status": "error", "error": str(e), "url": url}
    
    async def test_amlich_vn(self):
        """Test amlich.vn"""
        try:
            url = "https://amlich.vn/lich-am/2024/7"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                calendar_data = soup.find('table') or soup.find('.calendar')
                if calendar_data:
                    return {"status": "success", "has_data": True, "url": url}
            return {"status": "no_data", "url": url}
        except Exception as e:
            return {"status": "error", "error": str(e), "url": url}
    
    async def test_existing_websites(self):
        """Test lại các website hiện tại với năm 2024"""
        websites = [
            "https://lichviet.app/2024/07",
            "https://lichvn.net/lich-van-nien/2024-07", 
            "https://tuvi.vn/lich-am/2024/7",
            "https://lichvannien.net/lich-van-nien/thang-7-2024.html",
            "https://lichngaytot.com/lich-am/2024/7",
            "https://licham365.vn/lich-am/2024/7",
            "https://lichvannien365.com/lich-am/2024/7"
        ]
        
        results = {}
        for url in websites:
            try:
                response = requests.get(url, timeout=10)
                status = "success" if response.status_code == 200 else f"status_{response.status_code}"
                soup = BeautifulSoup(response.content, 'html.parser')
                has_calendar = bool(soup.find('table') or soup.find('.calendar') or soup.find('.day'))
                content_length = len(soup.text)
                
                results[url] = {
                    "status": status,
                    "has_calendar": has_calendar,
                    "content_length": content_length,
                    "title": soup.title.text if soup.title else "No title"
                }
            except Exception as e:
                results[url] = {"status": "error", "error": str(e)}
        
        return results
    
    async def run_all_tests(self):
        """Chạy tất cả test"""
        print("🔍 TESTING VIETNAMESE CALENDAR WEBSITES")
        print("=" * 50)
        
        # Test existing websites
        print("📊 Testing existing websites with 2024 data...")
        existing_results = await self.test_existing_websites()
        
        # Test new websites
        print("🆕 Testing new potential websites...")
        new_tests = [
            ("lichamnguyet.vn", self.test_lichamnguyet_vn()),
            ("24h.com.vn", self.test_24h_com_vn()),
            ("lich123.vn", self.test_lich123_vn()),
            ("amlich.vn", self.test_amlich_vn())
        ]
        
        new_results = {}
        for name, test in new_tests:
            try:
                result = await test
                new_results[name] = result
                print(f"  {name}: {result['status']}")
            except Exception as e:
                new_results[name] = {"status": "error", "error": str(e)}
                print(f"  {name}: error - {e}")
        
        # Summary
        print("\n📋 DETAILED RESULTS:")
        print("-" * 30)
        
        print("\n🔄 Existing Websites:")
        for url, result in existing_results.items():
            site_name = url.split('/')[2]
            status_icon = "✅" if result.get('status') == 'success' and result.get('has_calendar') else "❌"
            print(f"  {status_icon} {site_name}: {result.get('status')} | Calendar: {result.get('has_calendar')} | Content: {result.get('content_length', 0)} chars")
        
        print("\n🆕 New Websites:")
        for name, result in new_results.items():
            status_icon = "✅" if result.get('status') == 'success' else "❌"
            print(f"  {status_icon} {name}: {result.get('status')}")
        
        # Find best candidates
        print("\n🏆 BEST CANDIDATES:")
        print("-" * 20)
        
        best_existing = []
        for url, result in existing_results.items():
            if (result.get('status') == 'success' and 
                result.get('has_calendar') and 
                result.get('content_length', 0) > 5000):
                best_existing.append((url.split('/')[2], url))
        
        if best_existing:
            print("✅ Working existing sites:")
            for site, url in best_existing:
                print(f"  • {site}: {url}")
        else:
            print("❌ No existing sites have good data")
        
        best_new = []
        for name, result in new_results.items():
            if result.get('status') == 'success' and result.get('has_data'):
                best_new.append((name, result.get('url')))
        
        if best_new:
            print("✅ Working new sites:")
            for name, url in best_new:
                print(f"  • {name}: {url}")
        else:
            print("❌ No new sites found")
        
        return {
            "existing": existing_results,
            "new": new_results,
            "best_existing": best_existing,
            "best_new": best_new
        }

async def main():
    tester = WebsiteTest()
    results = await tester.run_all_tests()
    
    # Save results
    with open('website_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Results saved to website_test_results.json")

if __name__ == "__main__":
    asyncio.run(main())
