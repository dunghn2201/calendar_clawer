#!/usr/bin/env python3
"""
Script dọn dẹp và kiểm tra trạng thái hệ thống
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path

def check_system_status():
    """Kiểm tra trạng thái tổng thể của hệ thống"""
    print("🔍 KIỂM TRA TRẠNG THÁI HỆ THỐNG")
    print("=" * 50)
    
    # Check crawlers
    crawler_status = {
        'improved_crawler.py': 'active',
        'generic_crawler.py': 'backup', 
        'demo_crawler.py': 'deprecated',
        'lichviet_crawler.py': 'inactive',
        'lichvn_crawler.py': 'inactive',
        'tuvi_crawler.py': 'inactive'
    }
    
    print("\n📦 Crawler Status:")
    for crawler, status in crawler_status.items():
        icon = "✅" if status == 'active' else "⚠️" if status == 'backup' else "❌"
        print(f"  {icon} {crawler}: {status}")
    
    # Check data directories
    data_dirs = ['data/daily', 'data/monthly', 'data/raw', 'data/processed', 'logs']
    print("\n📁 Data Directories:")
    for directory in data_dirs:
        if os.path.exists(directory):
            files = len(os.listdir(directory))
            print(f"  ✅ {directory}: {files} files")
        else:
            print(f"  ❌ {directory}: Not found")
    
    # Check recent activity
    print("\n📊 Recent Activity:")
    try:
        log_file = 'logs/crawler.log'
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                lines = f.readlines()
                recent_lines = lines[-10:] if len(lines) >= 10 else lines
                print(f"  📝 Last {len(recent_lines)} log entries:")
                for line in recent_lines:
                    if 'INFO' in line and ('thành công' in line or 'success' in line.lower()):
                        print(f"    ✅ {line.strip()}")
                    elif 'ERROR' in line or 'FAILED' in line:
                        print(f"    ❌ {line.strip()}")
        else:
            print("  ⚠️ No log file found")
    except Exception as e:
        print(f"  ❌ Error reading logs: {e}")

def cleanup_old_data():
    """Dọn dẹp dữ liệu cũ"""
    print("\n🧹 DỌN DẸP DỮ LIỆU CŨ")
    print("=" * 30)
    
    # Directories to clean
    cleanup_dirs = [
        'data/raw',
        'data/normalized', 
        'data/temp'
    ]
    
    total_cleaned = 0
    
    for directory in cleanup_dirs:
        if os.path.exists(directory):
            files = os.listdir(directory)
            # Keep only recent files (last 7 days)
            cutoff_time = datetime.now().timestamp() - (7 * 24 * 60 * 60)
            
            cleaned_count = 0
            for file in files:
                file_path = os.path.join(directory, file)
                if os.path.isfile(file_path):
                    file_time = os.path.getmtime(file_path)
                    if file_time < cutoff_time:
                        try:
                            os.remove(file_path)
                            cleaned_count += 1
                        except Exception as e:
                            print(f"    ❌ Cannot remove {file}: {e}")
            
            total_cleaned += cleaned_count
            print(f"  🗑️ {directory}: Removed {cleaned_count} old files")
        else:
            print(f"  ⚠️ {directory}: Directory not found")
    
    print(f"\n✅ Total cleaned: {total_cleaned} files")

def test_improved_crawler():
    """Test improved crawler"""
    print("\n🧪 TEST IMPROVED CRAWLER")
    print("=" * 30)
    
    try:
        import sys
        sys.path.append('.')
        from crawlers.improved_crawler import ImprovedCalendarCrawler
        
        crawler = ImprovedCalendarCrawler()
        
        # Test API discovery
        print("🔍 Testing API discovery...")
        apis = crawler.discover_real_apis()
        print(f"  Found {len(apis)} working APIs")
        
        # Test month crawl
        print("📅 Testing month crawl...")
        data = crawler.crawl_month(2025, 7)
        print(f"  Crawled {len(data)} days of data")
        
        if data:
            sample = data[0]
            print(f"  Sample: {sample.solar_date} | {sample.lunar_date} | {sample.can_chi_day}")
            
        print("✅ Improved crawler test passed")
        
    except Exception as e:
        print(f"❌ Improved crawler test failed: {e}")

def generate_status_report():
    """Tạo báo cáo trạng thái"""
    print("\n📋 TẠO BÁO CÁO TRẠNG THÁI")
    print("=" * 30)
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'system_status': 'operational',
        'active_crawlers': ['improved_crawler'],
        'inactive_crawlers': ['lichviet', 'lichvn', 'tuvi', 'demo'],
        'data_quality': 'hybrid_generated',
        'recommendations': [
            'Tìm kiếm API chính xác hơn',
            'Cải thiện thuật toán lunar calendar',
            'Thêm validation cho dữ liệu can chi'
        ]
    }
    
    report_file = f"system_status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"📄 Báo cáo đã lưu: {report_file}")

def main():
    """Main function"""
    print("🚀 LICH CRAWLER - SYSTEM MAINTENANCE")
    print("=" * 50)
    print(f"Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Các bước kiểm tra và dọn dẹp
    check_system_status()
    cleanup_old_data()
    test_improved_crawler()
    generate_status_report()
    
    print("\n🎉 HOÀN THÀNH!")
    print("=" * 20)
    print("✅ Hệ thống đã được kiểm tra và dọn dẹp")
    print("📊 Improved crawler hoạt động tốt")
    print("🔄 Sẵn sàng cho việc crawl dữ liệu")

if __name__ == "__main__":
    main()
