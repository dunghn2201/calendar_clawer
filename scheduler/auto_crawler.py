"""
Auto scheduler để tự động crawl dữ liệu lịch âm
Chạy theo lịch trình đã định
"""

import schedule
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import threading
import json
from pathlib import Path

# Import crawlers (sẽ work sau khi cài đặt dependencies)
try:
    from crawlers.improved_crawler import ImprovedCalendarCrawler
    CRAWLERS_AVAILABLE = True
except ImportError as e:
    logging.error(f"Cannot import crawlers: {e}")
    CRAWLERS_AVAILABLE = False
    from processors.data_processor import LichDataProcessor
except ImportError as e:
    print(f"Import warning: {e}")
    print("Cần cài đặt dependencies trước khi chạy")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scheduler.log'),
        logging.StreamHandler()
    ]
)

class AutoCrawler:
    """Tự động crawl dữ liệu theo lịch trình"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.crawlers = {}
        self.is_running = False
        
        # Tạo thư mục cần thiết
        Path('logs').mkdir(exist_ok=True)
        Path('data').mkdir(exist_ok=True)
        Path('data/daily').mkdir(exist_ok=True)
        Path('data/monthly').mkdir(exist_ok=True)
        
        # Khởi tạo crawlers
        self.init_crawlers()
    
    def init_crawlers(self):
        """Khởi tạo các crawler"""
        if not CRAWLERS_AVAILABLE:
            self.logger.error("❌ Không thể import crawlers")
            self.crawlers = {}
            return
            
        try:
            self.crawlers = {
                'improved': ImprovedCalendarCrawler(delay=1.0),  # Crawler chính
            }
            self.logger.info("✅ Đã khởi tạo improved crawler")
        except Exception as e:
            self.logger.error(f"❌ Lỗi khởi tạo crawlers: {e}")
            self.crawlers = {}
    
    def crawl_today(self):
        """Crawl dữ liệu ngày hôm nay"""
        today = datetime.now()
        self.logger.info(f"🚀 Bắt đầu crawl ngày {today.strftime('%Y-%m-%d')}")
        
        all_data = []
        results = {}
        
        for name, crawler in self.crawlers.items():
            try:
                self.logger.info(f"📡 Crawling {name}...")
                data = crawler.crawl_date(today)
                
                if data:
                    all_data.append(data)
                    results[name] = "✅ Thành công"
                    self.logger.info(f"✅ {name}: Crawl thành công")
                else:
                    results[name] = "⚠️ Không có dữ liệu"
                    self.logger.warning(f"⚠️ {name}: Không có dữ liệu")
                
            except Exception as e:
                results[name] = f"❌ Lỗi: {str(e)}"
                self.logger.error(f"❌ {name}: {e}")
        
        # Lưu kết quả
        if all_data:
            filename = f"data/daily/lich_{today.strftime('%Y_%m_%d')}.json"
            self.save_daily_data(all_data, filename)
        
        # Log tổng kết
        self.logger.info("📋 Tổng kết crawl hôm nay:")
        for name, result in results.items():
            self.logger.info(f"  {name}: {result}")
        
        return results
    
    def crawl_current_month(self):
        """Crawl dữ liệu tháng hiện tại"""
        now = datetime.now()
        self.logger.info(f"🗓️ Bắt đầu crawl tháng {now.strftime('%m/%Y')}")
        
        all_data = []
        results = {}
        
        for name, crawler in self.crawlers.items():
            try:
                self.logger.info(f"📡 Crawling {name} for month {now.month}/{now.year}...")
                month_data = crawler.crawl_month(now.year, now.month)
                
                if month_data:
                    all_data.extend(month_data)
                    results[name] = f"✅ {len(month_data)} ngày"
                    self.logger.info(f"✅ {name}: {len(month_data)} ngày")
                else:
                    results[name] = "⚠️ Không có dữ liệu"
                    self.logger.warning(f"⚠️ {name}: Không có dữ liệu")
                
            except Exception as e:
                results[name] = f"❌ Lỗi: {str(e)}"
                self.logger.error(f"❌ {name}: {e}")
        
        # Xử lý và lưu dữ liệu
        if all_data:
            filename = f"data/monthly/lich_{now.strftime('%Y_%m')}.json"
            self.save_monthly_data(all_data, filename)
            
            # Xử lý dữ liệu
            self.process_monthly_data(filename)
        
        # Log tổng kết
        self.logger.info("📋 Tổng kết crawl tháng:")
        for name, result in results.items():
            self.logger.info(f"  {name}: {result}")
        
        return results
    
    def save_daily_data(self, data, filename: str):
        """Lưu dữ liệu ngày"""
        try:
            data_dict = [item.to_dict() if hasattr(item, 'to_dict') else item for item in data]
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data_dict, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"💾 Đã lưu dữ liệu ngày: {filename}")
            
        except Exception as e:
            self.logger.error(f"❌ Lỗi lưu dữ liệu ngày: {e}")
    
    def save_monthly_data(self, data, filename: str):
        """Lưu dữ liệu tháng"""
        try:
            data_dict = [item.to_dict() if hasattr(item, 'to_dict') else item for item in data]
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data_dict, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"💾 Đã lưu dữ liệu tháng: {filename} ({len(data_dict)} records)")
            
        except Exception as e:
            self.logger.error(f"❌ Lỗi lưu dữ liệu tháng: {e}")
    
    def process_monthly_data(self, filename: str):
        """Xử lý dữ liệu tháng"""
        try:
            processor = LichDataProcessor(filename)
            cleaned = processor.clean_and_process()
            
            if not cleaned.empty:
                # Export các format
                base_name = filename.replace('.json', '')
                processor.export_to_sqlite(f"{base_name}.db")
                processor.export_to_csv(f"{base_name}.csv")
                
                # Thống kê
                stats = processor.get_statistics()
                self.logger.info(f"📊 Thống kê: {stats['total_records']} records hợp lệ")
            
        except Exception as e:
            self.logger.error(f"❌ Lỗi xử lý dữ liệu: {e}")
    
    def setup_schedule(self):
        """Thiết lập lịch trình tự động"""
        # Crawl hàng ngày lúc 6:00 sáng
        schedule.every().day.at("06:00").do(self.crawl_today)
        
        # Crawl tháng hiện tại vào ngày 1 hàng tháng lúc 7:00
        schedule.every().month.do(self.crawl_current_month)
        
        # Crawl hàng tuần vào Chủ nhật lúc 8:00
        schedule.every().sunday.at("08:00").do(self.crawl_today)
        
        self.logger.info("⏰ Đã thiết lập lịch trình:")
        self.logger.info("  - Hàng ngày: 06:00")
        self.logger.info("  - Hàng tuần: Chủ nhật 08:00") 
        self.logger.info("  - Hàng tháng: Ngày 1 lúc 07:00")
    
    def start_scheduler(self):
        """Bắt đầu scheduler"""
        self.setup_schedule()
        self.is_running = True
        
        self.logger.info("🚀 Bắt đầu Auto Crawler...")
        self.logger.info("Nhấn Ctrl+C để dừng")
        
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check mỗi phút
                
        except KeyboardInterrupt:
            self.logger.info("⏹️ Dừng Auto Crawler")
            self.is_running = False
    
    def start_in_background(self):
        """Chạy scheduler trong background thread"""
        def run():
            self.start_scheduler()
        
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        self.logger.info("🔄 Auto Crawler đang chạy trong background")
        return thread
    
    def stop(self):
        """Dừng scheduler"""
        self.is_running = False
        schedule.clear()
        self.logger.info("⏹️ Đã dừng Auto Crawler")
    
    def run_test_crawl(self):
        """Chạy test crawl để kiểm tra"""
        self.logger.info("🧪 Chạy test crawl...")
        
        if not self.crawlers:
            self.logger.error("❌ Không có crawler nào được khởi tạo")
            return
        
        # Test crawl ngày hôm nay
        results = self.crawl_today()
        
        self.logger.info("✅ Test crawl hoàn thành!")
        return results

# Chạy thử nghiệm
if __name__ == "__main__":
    print("🤖 Auto Crawler cho Lịch Âm")
    print("=" * 40)
    
    crawler = AutoCrawler()
    
    # Menu
    while True:
        print("\n📋 Chọn chức năng:")
        print("1. Test crawl ngày hôm nay")
        print("2. Crawl tháng hiện tại")
        print("3. Bắt đầu scheduler tự động")
        print("4. Thoát")
        
        choice = input("\nNhập lựa chọn (1-4): ").strip()
        
        if choice == "1":
            crawler.run_test_crawl()
        elif choice == "2":
            crawler.crawl_current_month()
        elif choice == "3":
            crawler.start_scheduler()
        elif choice == "4":
            print("👋 Tạm biệt!")
            break
        else:
            print("❌ Lựa chọn không hợp lệ")
