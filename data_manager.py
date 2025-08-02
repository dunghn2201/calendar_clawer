"""
Data Manager - Quản lý và tổ chức dữ liệu crawl
Tái cấu trúc hệ thống lưu trữ dữ liệu với quy tắc đặt tên rõ ràng
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class DataManager:
    """Quản lý dữ liệu crawl với cấu trúc rõ ràng"""
    
    def __init__(self, base_data_path: str = "data"):
        self.base_path = Path(base_data_path)
        self.setup_directory_structure()
        
        # Mapping các crawler với tên rõ ràng
        self.crawler_mapping = {
            "demo_data": "demo",
            "lichviet.app": "lichviet",
            "lichvn.net": "lichvn", 
            "tuvi.vn": "tuvi",
            "lichvannien.net": "lichvannien",
            "lichngaytot.com": "lichngaytot",
            "licham365.vn": "licham365",
            "lichvannien365.com": "lichvannien365"
        }
        
    def setup_directory_structure(self):
        """Tạo cấu trúc thư mục có tổ chức"""
        directories = [
            "sources",           # Dữ liệu thô từ từng website
            "sources/demo",      # Demo data
            "sources/lichviet",  # Data từ lichviet.app
            "sources/lichvn",    # Data từ lichvn.net
            "sources/tuvi",      # Data từ tuvi.vn
            "sources/lichvannien", # Data từ lichvannien.net
            "sources/lichngaytot", # Data từ lichngaytot.com
            "sources/licham365",   # Data từ licham365.vn
            "sources/lichvannien365", # Data từ lichvannien365.com
            "processed",         # Dữ liệu đã xử lý
            "merged",           # Dữ liệu đã ghép từ nhiều nguồn
            "backup",           # Backup data cũ
            "temp"              # Temporary files
        ]
        
        for directory in directories:
            (self.base_path / directory).mkdir(parents=True, exist_ok=True)
    
    def generate_filename(self, source: str, date_range: Optional[str] = None, data_type: str = "raw") -> str:
        """
        Tạo tên file có ý nghĩa
        
        Args:
            source: Nguồn dữ liệu (demo, lichviet, lichvn, ...)
            date_range: Khoảng thời gian (YYYY-MM-DD hoặc YYYY-MM)
            data_type: Loại dữ liệu (raw, processed, merged)
        
        Returns:
            Tên file theo format: {source}_{date_range}_{data_type}_{timestamp}.json
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if date_range:
            filename = f"{source}_{date_range}_{data_type}_{timestamp}.json"
        else:
            filename = f"{source}_{data_type}_{timestamp}.json"
            
        return filename
    
    def save_data(self, data: List[Dict], source: str, date_range: Optional[str] = None) -> str:
        """
        Lưu dữ liệu với tên file có ý nghĩa
        
        Args:
            data: Dữ liệu để lưu
            source: Nguồn dữ liệu 
            date_range: Khoảng thời gian
            
        Returns:
            Đường dẫn file đã lưu
        """
        # Chuẩn hóa tên source
        clean_source = self.crawler_mapping.get(source, source.replace(".", "_"))
        
        # Tạo tên file
        filename = self.generate_filename(clean_source, date_range, "raw")
        
        # Đường dẫn lưu file
        filepath = self.base_path / "sources" / clean_source / filename
        
        # Lưu dữ liệu
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Đã lưu {len(data)} records vào: {filepath}")
        return str(filepath)
    
    def reorganize_existing_data(self):
        """Tái cấu trúc dữ liệu hiện tại"""
        print("🔄 Bắt đầu tái cấu trúc dữ liệu...")
        
        # Mapping file cũ với source mới
        file_mapping = {
            "test_1.json": "demo",
            "test_6.json": "lichvannien", 
            "test_7.json": "lichngaytot",
            "test_8.json": "licham365",
            "test_9.json": "lichvannien365"
        }
        
        moved_files = 0
        
        for old_filename, source in file_mapping.items():
            old_path = self.base_path / old_filename
            
            if old_path.exists():
                # Đọc data để lấy thông tin thời gian
                try:
                    with open(old_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Xác định khoảng thời gian từ dữ liệu
                    if data and 'solar_date' in data[0]:
                        first_date = data[0]['solar_date']
                        last_date = data[-1]['solar_date'] if len(data) > 1 else first_date
                        
                        # Format date range
                        if first_date == last_date:
                            date_range = first_date
                        else:
                            date_range = f"{first_date}_to_{last_date}"
                    else:
                        date_range = "unknown"
                    
                    # Tạo tên file mới
                    new_filename = self.generate_filename(source, date_range, "raw")
                    new_path = self.base_path / "sources" / source / new_filename
                    
                    # Di chuyển file
                    shutil.move(str(old_path), str(new_path))
                    moved_files += 1
                    
                    print(f"📁 {old_filename} -> {new_path.relative_to(self.base_path)}")
                    
                except Exception as e:
                    print(f"❌ Lỗi khi xử lý {old_filename}: {e}")
        
        print(f"✅ Đã di chuyển {moved_files} files")
    
    def list_data_by_source(self) -> Dict[str, List[str]]:
        """Liệt kê dữ liệu theo từng nguồn"""
        sources_data = {}
        sources_dir = self.base_path / "sources"
        
        if sources_dir.exists():
            for source_dir in sources_dir.iterdir():
                if source_dir.is_dir():
                    files = [f.name for f in source_dir.iterdir() if f.suffix == '.json']
                    sources_data[source_dir.name] = sorted(files, reverse=True)
        
        return sources_data
    
    def get_data_summary(self) -> Dict:
        """Tóm tắt dữ liệu hiện có"""
        summary = {
            "total_sources": 0,
            "total_files": 0,
            "sources_detail": {}
        }
        
        sources_data = self.list_data_by_source()
        
        for source, files in sources_data.items():
            file_count = len(files)
            
            # Đếm records trong từng file
            total_records = 0
            latest_file = None
            
            if files:
                latest_file = files[0]  # Files đã được sort
                try:
                    latest_path = self.base_path / "sources" / source / latest_file
                    with open(latest_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        total_records = len(data)
                except:
                    total_records = 0
            
            summary["sources_detail"][source] = {
                "file_count": file_count,
                "latest_file": latest_file,
                "latest_records": total_records
            }
            
            summary["total_files"] += file_count
        
        summary["total_sources"] = len(sources_data)
        return summary
    
    def create_readme(self):
        """Tạo README cho thư mục data"""
        readme_content = """# 📊 Data Directory Structure

## 📁 Cấu trúc thư mục

```
data/
├── sources/              # Dữ liệu thô từ từng website
│   ├── demo/            # Demo data for testing
│   ├── lichviet/        # Data từ lichviet.app
│   ├── lichvn/          # Data từ lichvn.net  
│   ├── tuvi/            # Data từ tuvi.vn
│   ├── lichvannien/     # Data từ lichvannien.net
│   ├── lichngaytot/     # Data từ lichngaytot.com
│   ├── licham365/       # Data từ licham365.vn
│   └── lichvannien365/  # Data từ lichvannien365.com
├── processed/           # Dữ liệu đã xử lý và chuẩn hóa
├── merged/             # Dữ liệu đã ghép từ nhiều nguồn  
├── backup/             # Backup dữ liệu cũ
└── temp/               # Files tạm thời
```

## 📝 Quy tắc đặt tên file

Format: `{source}_{date_range}_{data_type}_{timestamp}.json`

- **source**: Tên nguồn (demo, lichviet, lichvn, ...)
- **date_range**: Khoảng thời gian (YYYY-MM-DD hoặc YYYY-MM)  
- **data_type**: Loại dữ liệu (raw, processed, merged)
- **timestamp**: Thời gian tạo file (YYYYMMDD_HHMMSS)

## 📋 Ví dụ tên file

- `lichviet_2024-07-16_raw_20250716_210652.json`
- `lichvn_2024-07_processed_20250716_210652.json`  
- `merged_2024-07-16_merged_20250716_210652.json`

## 🏷️ Mapping nguồn dữ liệu

| Website | Thư mục | Mô tả |
|---------|---------|-------|
| demo_data | demo | Dữ liệu demo cho test |
| lichviet.app | lichviet | Lịch Việt |
| lichvn.net | lichvn | Lịch VN |
| tuvi.vn | tuvi | Tử vi |
| lichvannien.net | lichvannien | Lịch Vạn Niên |
| lichngaytot.com | lichngaytot | Lịch Ngày Tốt |
| licham365.vn | licham365 | Lịch Âm 365 |
| lichvannien365.com | lichvannien365 | Lịch Vạn Niên 365 |
"""
        
        readme_path = self.base_path / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"📝 Đã tạo README.md tại: {readme_path}")

def main():
    """Chức năng chính để tái cấu trúc dữ liệu"""
    print("🗂️ DATA MANAGER - Tái cấu trúc dữ liệu")
    print("=" * 50)
    
    # Khởi tạo data manager
    dm = DataManager("/Users/dunghn2201/Documents/Python/lich-crawler/data")
    
    # Tái cấu trúc dữ liệu hiện tại
    dm.reorganize_existing_data()
    
    # Tạo README
    dm.create_readme()
    
    # Hiển thị tóm tắt
    print("\n📊 TÓMETAT DỮ LIỆU SAU KHI TÁI CẤU TRÚC:")
    print("-" * 50)
    
    summary = dm.get_data_summary()
    print(f"📁 Tổng số nguồn: {summary['total_sources']}")
    print(f"📄 Tổng số files: {summary['total_files']}")
    
    print("\n📋 Chi tiết theo nguồn:")
    for source, details in summary["sources_detail"].items():
        print(f"  {source:15} | {details['file_count']:2} files | Latest: {details['latest_records']:3} records")
    
    print("\n✅ Hoàn thành tái cấu trúc!")

if __name__ == "__main__":
    main()
