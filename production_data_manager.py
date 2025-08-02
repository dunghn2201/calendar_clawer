"""
Improved Data Manager - Chỉ xử lý data thật, loại bỏ demo data
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import sys

# Add models to path
sys.path.append(str(Path(__file__).parent))
from models.calendar_models import CalendarDay, MonthlyCalendar, DataNormalizer

class ProductionDataManager:
    """Data Manager chỉ cho production data - không có demo/fake data"""
    
    def __init__(self, base_data_path: str = "data"):
        self.base_path = Path(base_data_path)
        self.setup_directory_structure()
        
        # Chỉ mapping các nguồn data thật
        self.real_sources = {
            "lichviet.app": "lichviet",
            "lichvn.net": "lichvn", 
            "tuvi.vn": "tuvi",
            "lichvannien.net": "lichvannien",
            "lichngaytot.com": "lichngaytot",
            "licham365.vn": "licham365",
            "lichvannien365.com": "lichvannien365"
        }
        
    def setup_directory_structure(self):
        """Tạo cấu trúc thư mục chỉ cho production data"""
        directories = [
            "raw",              # Dữ liệu thô từ websites
            "raw/lichviet",     # Data từ lichviet.app
            "raw/lichvn",       # Data từ lichvn.net
            "raw/tuvi",         # Data từ tuvi.vn
            "raw/lichvannien",  # Data từ lichvannien.net
            "raw/lichngaytot",  # Data từ lichngaytot.com
            "raw/licham365",    # Data từ licham365.vn
            "raw/lichvannien365", # Data từ lichvannien365.com
            "normalized",       # Dữ liệu đã chuẩn hóa
            "api",             # Dữ liệu cho API Android
            "backup",          # Backup
            "logs"             # Logs crawling
        ]
        
        for directory in directories:
            (self.base_path / directory).mkdir(parents=True, exist_ok=True)
    
    def clean_fake_data(self):
        """Xóa tất cả demo/fake data"""
        print("🧹 Dọn dẹp demo/fake data...")
        
        # Xóa demo directories
        demo_paths = [
            self.base_path / "sources" / "demo",
            self.base_path / "sources" / "api_demo"
        ]
        
        removed_count = 0
        for demo_path in demo_paths:
            if demo_path.exists():
                shutil.rmtree(demo_path)
                removed_count += 1
                print(f"🗑️ Đã xóa: {demo_path}")
        
        # Xóa các file demo trong data root
        demo_files = [
            "demo_*.json",
            "*demo*.json", 
            "test_*.json"
        ]
        
        for pattern in demo_files:
            for file in self.base_path.glob(pattern):
                if file.is_file():
                    file.unlink()
                    removed_count += 1
                    print(f"🗑️ Đã xóa: {file.name}")
        
        print(f"✅ Đã dọn dẹp {removed_count} items")
    
    def normalize_raw_data(self, source: str) -> int:
        """Chuẩn hóa raw data từ một nguồn"""
        source_dir = self.base_path / "raw" / source
        if not source_dir.exists():
            return 0
        
        normalized_count = 0
        
        for raw_file in source_dir.glob("*.json"):
            try:
                # Đọc raw data
                with open(raw_file, 'r', encoding='utf-8') as f:
                    raw_data = json.load(f)
                
                if not raw_data:
                    continue
                
                # Chuẩn hóa từng record
                normalized_days = []
                for item in raw_data:
                    try:
                        calendar_day = CalendarDay.from_raw_data(item)
                        normalized_days.append(calendar_day)
                    except Exception as e:
                        print(f"⚠️ Lỗi chuẩn hóa record từ {source}: {e}")
                        continue
                
                if normalized_days:
                    # Lưu vào normalized directory
                    normalized_file = self.base_path / "normalized" / f"{source}_{raw_file.stem}_normalized.json"
                    normalized_data = [day.to_dict() for day in normalized_days]
                    
                    with open(normalized_file, 'w', encoding='utf-8') as f:
                        json.dump(normalized_data, f, ensure_ascii=False, indent=2)
                    
                    normalized_count += len(normalized_days)
                    print(f"✅ Chuẩn hóa {len(normalized_days)} records từ {raw_file.name}")
                    
            except Exception as e:
                print(f"❌ Lỗi xử lý {raw_file}: {e}")
        
        return normalized_count
    
    def merge_sources_by_month(self, year: int, month: int) -> Optional[MonthlyCalendar]:
        """Ghép dữ liệu từ nhiều nguồn theo tháng"""
        print(f"🔄 Ghép dữ liệu tháng {month:02d}/{year}...")
        
        # Dictionary để group theo ngày
        days_data = {}
        
        # Đọc dữ liệu từ tất cả nguồn
        normalized_dir = self.base_path / "normalized"
        for file in normalized_dir.glob("*_normalized.json"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for item in data:
                    solar_date = item.get('solar_date', '')
                    if not solar_date:
                        continue
                    
                    # Chỉ lấy data của tháng cần thiết
                    try:
                        date_obj = datetime.strptime(solar_date, '%Y-%m-%d')
                        if date_obj.year == year and date_obj.month == month:
                            if solar_date not in days_data:
                                days_data[solar_date] = []
                            days_data[solar_date].append(item)
                    except:
                        continue
                        
            except Exception as e:
                print(f"⚠️ Lỗi đọc {file}: {e}")
        
        if not days_data:
            print(f"❌ Không có dữ liệu cho tháng {month:02d}/{year}")
            return None
        
        # Merge data cho từng ngày
        merged_days = []
        for solar_date in sorted(days_data.keys()):
            day_records = days_data[solar_date]
            
            # Merge logic: ưu tiên nguồn có data đầy đủ nhất
            best_record = max(day_records, key=lambda x: len([v for v in x.values() if v]))
            
            # Bổ sung thông tin từ các nguồn khác
            for record in day_records:
                for key, value in record.items():
                    if value and not best_record.get(key):
                        best_record[key] = value
            
            # Tạo CalendarDay object
            try:
                calendar_day = CalendarDay.from_raw_data(best_record)
                merged_days.append(calendar_day)
            except Exception as e:
                print(f"⚠️ Lỗi merge ngày {solar_date}: {e}")
        
        if merged_days:
            monthly_calendar = MonthlyCalendar(
                year=year,
                month=month,
                days=merged_days,
                total_days=len(merged_days)
            )
            
            # Lưu merged data
            merged_file = self.base_path / "api" / f"calendar_{year}_{month:02d}.json"
            with open(merged_file, 'w', encoding='utf-8') as f:
                json.dump(monthly_calendar.to_dict(), f, ensure_ascii=False, indent=2)
            
            print(f"✅ Đã merge {len(merged_days)} ngày cho tháng {month:02d}/{year}")
            return monthly_calendar
        
        return None
    
    def get_available_data_summary(self) -> Dict:
        """Tóm tắt dữ liệu thật hiện có"""
        summary = {
            "real_sources": {},
            "total_raw_files": 0,
            "total_normalized_files": 0,
            "available_months": []
        }
        
        # Check raw data
        raw_dir = self.base_path / "raw"
        if raw_dir.exists():
            for source in self.real_sources.values():
                source_dir = raw_dir / source
                if source_dir.exists():
                    files = list(source_dir.glob("*.json"))
                    summary["real_sources"][source] = {
                        "raw_files": len(files),
                        "latest_file": files[-1].name if files else None
                    }
                    summary["total_raw_files"] += len(files)
        
        # Check normalized data  
        normalized_dir = self.base_path / "normalized"
        if normalized_dir.exists():
            files = list(normalized_dir.glob("*_normalized.json"))
            summary["total_normalized_files"] = len(files)
        
        # Check API data
        api_dir = self.base_path / "api"
        if api_dir.exists():
            for file in api_dir.glob("calendar_*.json"):
                filename = file.stem
                # Extract year_month from filename
                parts = filename.split('_')
                if len(parts) >= 3:
                    try:
                        year = int(parts[1])
                        month = int(parts[2])
                        summary["available_months"].append(f"{year}-{month:02d}")
                    except:
                        pass
        
        summary["available_months"] = sorted(summary["available_months"])
        return summary
    
    def reorganize_existing_real_data(self):
        """Tái tổ chức chỉ data thật từ cấu trúc cũ"""
        print("🔄 Tái tổ chức dữ liệu thật...")
        
        # Di chuyển từ sources/ sang raw/
        sources_dir = self.base_path / "sources"
        if sources_dir.exists():
            moved_count = 0
            
            for source_name in self.real_sources.values():
                old_source_dir = sources_dir / source_name
                new_source_dir = self.base_path / "raw" / source_name
                
                if old_source_dir.exists():
                    # Di chuyển tất cả files
                    for file in old_source_dir.glob("*.json"):
                        new_file_path = new_source_dir / file.name
                        shutil.move(str(file), str(new_file_path))
                        moved_count += 1
                        print(f"📁 {file.name} -> raw/{source_name}/")
                    
                    # Xóa thư mục cũ nếu rỗng
                    if not any(old_source_dir.iterdir()):
                        old_source_dir.rmdir()
            
            print(f"✅ Đã di chuyển {moved_count} files")
    
    def create_android_api_structure(self):
        """Tạo cấu trúc API cho Android app"""
        api_dir = self.base_path / "api"
        
        # Tạo API endpoints structure
        endpoints = {
            "calendar": "Dữ liệu lịch theo tháng",
            "holidays": "Danh sách ngày lễ", 
            "good_days": "Ngày tốt trong tháng",
            "bad_days": "Ngày xấu trong tháng"
        }
        
        for endpoint, description in endpoints.items():
            endpoint_dir = api_dir / endpoint
            endpoint_dir.mkdir(exist_ok=True)
            
            # Tạo README cho endpoint
            readme_content = f"# {endpoint.upper()} API\n\n{description}\n\n## Format\n\nJSON files organized by year/month\n"
            (endpoint_dir / "README.md").write_text(readme_content)
        
        print("✅ Đã tạo cấu trúc API cho Android")

def main():
    """Main function để setup production data"""
    print("🏭 PRODUCTION DATA MANAGER")
    print("=" * 50)
    print("Loại bỏ demo data và chuẩn hóa data thật cho Android app")
    print()
    
    # Khởi tạo production data manager
    pdm = ProductionDataManager("/Users/dunghn2201/Documents/Python/lich-crawler/data")
    
    # 1. Dọn dẹp demo data
    pdm.clean_fake_data()
    print()
    
    # 2. Tái tổ chức data thật
    pdm.reorganize_existing_real_data()
    print()
    
    # 3. Chuẩn hóa raw data
    print("📝 Chuẩn hóa dữ liệu thô...")
    total_normalized = 0
    for source in pdm.real_sources.values():
        count = pdm.normalize_raw_data(source)
        total_normalized += count
    
    print(f"✅ Đã chuẩn hóa {total_normalized} records")
    print()
    
    # 4. Tạo cấu trúc API
    pdm.create_android_api_structure()
    print()
    
    # 5. Merge data theo tháng (example: tháng hiện tại)
    current_month = datetime.now().month
    current_year = datetime.now().year
    monthly_data = pdm.merge_sources_by_month(current_year, current_month)
    print()
    
    # 6. Hiển thị tóm tắt
    print("📊 TÓM TẮT DỮ LIỆU PRODUCTION:")
    print("-" * 40)
    
    summary = pdm.get_available_data_summary()
    print(f"📁 Raw files: {summary['total_raw_files']}")
    print(f"📄 Normalized files: {summary['total_normalized_files']}")
    print(f"📅 Available months: {len(summary['available_months'])}")
    
    print("\n📋 Chi tiết nguồn data:")
    for source, details in summary["real_sources"].items():
        if details['raw_files'] > 0:
            print(f"  ✅ {source:15} | {details['raw_files']:2} files")
        else:
            print(f"  ⭕ {source:15} | No data")
    
    print("\n🎯 PRODUCTION READY!")
    print("Data đã được chuẩn hóa và sẵn sàng cho Android app")

if __name__ == "__main__":
    main()
