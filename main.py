"""
Main entry point cho Lich Crawler
Chạy file này để bắt đầu sử dụng
"""

import sys
import os
from pathlib import Path

# Thêm project root vào Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def show_data_structure():
    """Hiển thị cấu trúc dữ liệu hiện tại"""
    from data_manager import DataManager
    
    print("\n📊 CẤU TRÚC DỮ LIỆU HIỆN TẠI")
    print("=" * 50)
    
    dm = DataManager()
    summary = dm.get_data_summary()
    
    print(f"📁 Tổng số nguồn: {summary['total_sources']}")
    print(f"📄 Tổng số files: {summary['total_files']}")
    
    print("\n📋 Chi tiết theo nguồn:")
    for source, details in summary["sources_detail"].items():
        status = "✅" if details['file_count'] > 0 else "⭕"
        print(f"  {status} {source:15} | {details['file_count']:2} files | {details['latest_records']:3} records")
    
    print("\n📁 Cấu trúc thư mục:")
    print("  data/")
    print("  ├── sources/              # Dữ liệu thô từ từng website")
    for source in summary["sources_detail"].keys():
        icon = "├──" if source != list(summary["sources_detail"].keys())[-1] else "└──"
        print(f"  │   {icon} {source}/")
    print("  ├── processed/           # Dữ liệu đã xử lý")
    print("  ├── merged/             # Dữ liệu đã ghép")
    print("  └── backup/             # Backup")

def cleanup_old_data():
    """Dọn dẹp dữ liệu cũ không có cấu trúc"""
    from data_manager import DataManager
    import os
    from pathlib import Path
    
    print("\n🧹 DỌN DẸP DỮ LIỆU CŨ")
    print("=" * 50)
    
    data_dir = Path("data")
    old_files = [
        "test_1_processed.csv",
        "test_1_processed.db"
    ]
    
    moved_count = 0
    for old_file in old_files:
        old_path = data_dir / old_file
        if old_path.exists():
            backup_path = data_dir / "backup" / old_file
            backup_path.parent.mkdir(exist_ok=True)
            old_path.rename(backup_path)
            moved_count += 1
            print(f"📦 Đã di chuyển {old_file} vào backup/")
    
    if moved_count > 0:
        print(f"✅ Đã di chuyển {moved_count} files vào thư mục backup")
    else:
        print("✅ Không có files cũ cần dọn dẹp")

def main():
    """Main function"""
    print("🗓️ LICH CRAWLER - Vietnamese Lunar Calendar Data Scraper")
    print("=" * 60)
    
    # Kiểm tra dependencies
    missing_deps = check_dependencies()
    if missing_deps:
        print("❌ Thiếu dependencies:")
        for dep in missing_deps:
            print(f"  - {dep}")
        print("\n🔧 Để cài đặt, chạy:")
        print("pip install -r requirements.txt")
        print("playwright install chromium")
        return
    
    print("✅ Tất cả dependencies đã được cài đặt")
    
    # Import sau khi check dependencies
    try:
        from crawlers.demo_crawler import DemoCrawler, VietnameseCalendarAPI
        from crawlers.lichviet_crawler import LichVietCrawler
        from crawlers.lichvn_crawler import LichVnCrawler
        from crawlers.tuvi_crawler import TuviCrawler
        from crawlers.lichvannien_crawler import LichVannienCrawler
        from crawlers.lichngaytot_crawler import LichNgayTotCrawler
        from crawlers.licham365_crawler import LichAm365Crawler
        from crawlers.lichvannien365_crawler import LichVanNien365Crawler
        from processors.data_processor import LichDataProcessor
    except ImportError as e:
        print(f"❌ Lỗi import: {e}")
        print("Vui lòng cài đặt dependencies trước")
        return
    
    # Menu chính
    while True:
        print("\n📋 MENU CHÍNH:")
        print("1. 🚀 Test crawl một trang web")
        print("2. 📅 Crawl ngày hôm nay từ tất cả trang")
        print("3. 🗓️ Crawl tháng hiện tại")
        print("4. 📊 Xử lý dữ liệu đã crawl")
        print("5. ⏰ Bắt đầu scheduler tự động")
        print("6. 📈 Xem thống kê")
        print("7. 📊 Xem cấu trúc dữ liệu")
        print("8. 🧹 Dọn dẹp dữ liệu cũ")
        print("9. ❓ Hướng dẫn sử dụng")
        print("10. 🚪 Thoát")
        
        choice = input("\nNhập lựa chọn (1-10): ").strip()
        
        if choice == "1":
            test_single_crawler()
        elif choice == "2":
            crawl_today()
        elif choice == "3":
            crawl_current_month()
        elif choice == "4":
            process_data()
        elif choice == "5":
            start_scheduler()
        elif choice == "6":
            show_statistics()
        elif choice == "7":
            show_data_structure()
        elif choice == "8":
            cleanup_old_data()
        elif choice == "9":
            show_help()
        elif choice == "10":
            print("👋 Cảm ơn bạn đã sử dụng Lich Crawler!")
            break
        else:
            print("❌ Lựa chọn không hợp lệ")

def check_dependencies():
    """Kiểm tra dependencies cần thiết"""
    required_packages = [
        'requests', 'beautifulsoup4', 'lxml', 'pandas', 
        'playwright', 'schedule', 'aiohttp'
    ]
    
    missing = []
    for package in required_packages:
        try:
            if package == 'beautifulsoup4':
                import bs4
            elif package == 'lxml':
                import lxml
            else:
                __import__(package)
        except ImportError:
            missing.append(package)
    
    return missing

def test_single_crawler():
    """Test một crawler"""
    print("\n🧪 TEST CRAWLER")
    print("Chọn trang web để test:")
    print("1. Demo Crawler (luôn hoạt động)")
    print("2. API Demo Crawler")  
    print("3. lichviet.app")
    print("4. lichvn.net") 
    print("5. tuvi.vn")
    print("6. lichvannien.net")
    print("7. lichngaytot.com")
    print("8. licham365.vn")
    print("9. lichvannien365.com")
    
    choice = input("Nhập lựa chọn (1-9): ").strip()
    
    try:
        if choice == "1":
            from crawlers.demo_crawler import DemoCrawler
            crawler = DemoCrawler()
            print("🚀 Testing Demo Crawler...")
        elif choice == "2":
            from crawlers.demo_crawler import VietnameseCalendarAPI
            crawler = VietnameseCalendarAPI()
            print("🚀 Testing API Demo Crawler...")
        elif choice == "3":
            from crawlers.lichviet_crawler import LichVietCrawler
            crawler = LichVietCrawler()
            print("🚀 Testing lichviet.app...")
        elif choice == "4":
            from crawlers.lichvn_crawler import LichVnCrawler
            crawler = LichVnCrawler()
            print("🚀 Testing lichvn.net...")
        elif choice == "5":
            from crawlers.tuvi_crawler import TuviCrawler
            crawler = TuviCrawler()
            print("🚀 Testing tuvi.vn...")
        elif choice == "6":
            from crawlers.lichvannien_crawler import LichVannienCrawler
            crawler = LichVannienCrawler()
            print("🚀 Testing lichvannien.net...")
        elif choice == "7":
            from crawlers.lichngaytot_crawler import LichNgayTotCrawler
            crawler = LichNgayTotCrawler()
            print("🚀 Testing lichngaytot.com...")
        elif choice == "8":
            from crawlers.licham365_crawler import LichAm365Crawler
            crawler = LichAm365Crawler()
            print("🚀 Testing licham365.vn...")
        elif choice == "9":
            from crawlers.lichvannien365_crawler import LichVanNien365Crawler
            crawler = LichVanNien365Crawler()
            print("🚀 Testing lichvannien365.com...")
        else:
            print("❌ Lựa chọn không hợp lệ")
            return
        
        # Test crawl tháng 7/2024 (thay vì 1/2024)
        data = crawler.crawl_month(2024, 7)
        print(f"✅ Crawl thành công: {len(data)} ngày")
        
        if data:
            print("\n📋 Dữ liệu mẫu:")
            for i, item in enumerate(data[:5]):
                print(f"  {i+1}. {item.solar_date} - {item.lunar_date} - {item.can_chi_day}")
            
            # Lưu test data
            crawler.data = data
            filename = f"test_{choice}.json"
            crawler.save_to_json(filename)
            print(f"💾 Đã lưu vào {filename}")
    
    except Exception as e:
        print(f"❌ Lỗi: {e}")

def crawl_today():
    """Crawl ngày hôm nay"""
    print("\n📅 CRAWL NGÀY HÔM NAY")
    
    try:
        from scheduler.auto_crawler import AutoCrawler
        crawler = AutoCrawler()
        results = crawler.crawl_today()
        
        print("\n📋 Kết quả:")
        for site, result in results.items():
            print(f"  {site}: {result}")
    
    except Exception as e:
        print(f"❌ Lỗi: {e}")

def crawl_current_month():
    """Crawl tháng hiện tại"""
    print("\n🗓️ CRAWL THÁNG HIỆN TẠI")
    
    try:
        from scheduler.auto_crawler import AutoCrawler
        crawler = AutoCrawler()
        results = crawler.crawl_current_month()
        
        print("\n📋 Kết quả:")
        for site, result in results.items():
            print(f"  {site}: {result}")
    
    except Exception as e:
        print(f"❌ Lỗi: {e}")

def process_data():
    """Xử lý dữ liệu"""
    print("\n📊 XỬ LÝ DỮ LIỆU")
    
    # Tìm file dữ liệu
    data_files = list(Path("data").rglob("*.json"))
    
    if not data_files:
        print("❌ Không tìm thấy file dữ liệu nào")
        return
    
    print("Chọn file để xử lý:")
    for i, file in enumerate(data_files):
        print(f"  {i+1}. {file}")
    
    try:
        choice = int(input("Nhập số: ")) - 1
        if 0 <= choice < len(data_files):
            from processors.data_processor import LichDataProcessor
            
            processor = LichDataProcessor(str(data_files[choice]))
            cleaned = processor.clean_and_process()
            
            if not cleaned.empty:
                stats = processor.get_statistics()
                print(f"✅ Xử lý thành công: {stats['total_records']} records")
                
                # Export
                base_name = str(data_files[choice]).replace('.json', '_processed')
                processor.export_to_sqlite(f"{base_name}.db")
                processor.export_to_csv(f"{base_name}.csv")
                print(f"💾 Đã export: {base_name}.db, {base_name}.csv")
        else:
            print("❌ Lựa chọn không hợp lệ")
    
    except Exception as e:
        print(f"❌ Lỗi: {e}")

def start_scheduler():
    """Bắt đầu scheduler"""
    print("\n⏰ BẮT ĐẦU SCHEDULER TỰ ĐỘNG")
    print("Scheduler sẽ crawl theo lịch trình:")
    print("  - Hàng ngày: 06:00")
    print("  - Hàng tuần: Chủ nhật 08:00")
    print("  - Hàng tháng: Ngày 1 lúc 07:00")
    print("\nNhấn Ctrl+C để dừng")
    
    try:
        from scheduler.auto_crawler import AutoCrawler
        crawler = AutoCrawler()
        crawler.start_scheduler()
    except KeyboardInterrupt:
        print("\n⏹️ Đã dừng scheduler")
    except Exception as e:
        print(f"❌ Lỗi: {e}")

def show_statistics():
    """Hiển thị thống kê"""
    print("\n📈 THỐNG KÊ DỮ LIỆU")
    
    # Đếm files
    json_files = list(Path("data").rglob("*.json"))
    db_files = list(Path("data").rglob("*.db"))
    csv_files = list(Path("data").rglob("*.csv"))
    
    print(f"📁 Tổng file dữ liệu: {len(json_files + db_files + csv_files)}")
    print(f"  - JSON: {len(json_files)}")
    print(f"  - SQLite: {len(db_files)}")
    print(f"  - CSV: {len(csv_files)}")
    
    # Thống kê từ file gần nhất
    if json_files:
        latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
        print(f"\n📄 File gần nhất: {latest_file.name}")
        
        try:
            import json
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"📊 Số records: {len(data)}")
            
            # Thống kê nguồn
            sources = {}
            for item in data:
                source = item.get('source', 'unknown')
                sources[source] = sources.get(source, 0) + 1
            
            print("📡 Theo nguồn:")
            for source, count in sources.items():
                print(f"  - {source}: {count}")
        
        except Exception as e:
            print(f"❌ Lỗi đọc file: {e}")

def show_help():
    """Hiển thị hướng dẫn"""
    print("\n❓ HƯỚNG DẪN SỬ DỤNG")
    print("=" * 50)
    print("""
🎯 GIỚI THIỆU:
Lich Crawler là công cụ Python để crawl dữ liệu lịch âm từ các trang web Việt Nam.

🚀 BƯỚC ĐẦU:
1. Cài đặt dependencies: pip install -r requirements.txt
2. Cài đặt browser: playwright install chromium
3. Chạy: python main.py

📊 CÁC CHỨC NĂNG:
- Test crawler: Thử nghiệm crawl từ 1 trang web
- Crawl hàng ngày: Lấy dữ liệu ngày hiện tại
- Crawl tháng: Lấy dữ liệu cả tháng
- Xử lý dữ liệu: Làm sạch và export
- Scheduler: Tự động crawl theo lịch trình

💾 DỮ LIỆU:
- Lưu trong thư mục data/
- Format: JSON, CSV, SQLite
- Tự động backup và làm sạch

🛠️ TROUBLESHOOTING:
- Lỗi import: Cài đặt lại dependencies
- Lỗi network: Kiểm tra internet
- Lỗi website: Thử crawler khác

📞 HỖ TRỢ:
- Đọc README.md để biết thêm chi tiết
- Check logs/ folder để debug
- GitHub Issues để báo lỗi
""")

if __name__ == "__main__":
    main()
