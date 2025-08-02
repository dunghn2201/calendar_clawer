"""
Cập nhật Base Crawler để sử dụng Data Manager mới
"""

import os
import sys
from pathlib import Path

# Thêm project root vào Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from data_manager import DataManager

def update_base_crawler():
    """Cập nhật base crawler để sử dụng data manager"""
    
    base_crawler_path = project_root / "crawlers" / "base_crawler.py"
    
    # Đọc file hiện tại
    with open(base_crawler_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Tìm và thay thế phần save_data
    old_save_method = '''    def save_data(self, data: List[LichData], filename: str = None) -> str:
        """Lưu dữ liệu ra file JSON"""
        if not data:
            print("⚠️ Không có dữ liệu để lưu")
            return ""
        
        # Tạo filename nếu không có
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"lich_{timestamp}.json"
        
        # Tạo thư mục data nếu chưa có
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        filepath = data_dir / filename
        
        # Convert LichData objects to dict
        data_dicts = []
        for item in data:
            if isinstance(item, LichData):
                data_dicts.append(item.to_dict())
            else:
                data_dicts.append(item)
        
        # Lưu file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data_dicts, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Đã lưu {len(data)} records vào: {filepath}")
        return str(filepath)'''

    new_save_method = '''    def save_data(self, data: List[LichData], filename: str = None) -> str:
        """Lưu dữ liệu với cấu trúc có tổ chức"""
        if not data:
            print("⚠️ Không có dữ liệu để lưu")
            return ""
        
        # Import data manager
        from data_manager import DataManager
        dm = DataManager()
        
        # Convert LichData objects to dict
        data_dicts = []
        for item in data:
            if isinstance(item, LichData):
                data_dicts.append(item.to_dict())
            else:
                data_dicts.append(item)
        
        # Xác định date range từ dữ liệu
        date_range = None
        if data_dicts:
            first_date = data_dicts[0].get('solar_date', '')
            last_date = data_dicts[-1].get('solar_date', '') if len(data_dicts) > 1 else first_date
            
            if first_date:
                if first_date == last_date:
                    date_range = first_date
                else:
                    date_range = f"{first_date}_to_{last_date}"
        
        # Lưu với data manager
        filepath = dm.save_data(data_dicts, self.source_name, date_range)
        return filepath'''
    
    # Thay thế nội dung
    if old_save_method in content:
        new_content = content.replace(old_save_method, new_save_method)
        
        # Lưu file đã cập nhật
        with open(base_crawler_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Đã cập nhật base_crawler.py để sử dụng DataManager")
    else:
        print("⚠️ Không tìm thấy phương thức save_data cũ để thay thế")

def update_main_py():
    """Cập nhật main.py để hiển thị cấu trúc dữ liệu mới"""
    
    main_py_path = project_root / "main.py"
    
    # Thêm chức năng xem cấu trúc dữ liệu vào main.py
    additional_functions = '''
def show_data_structure():
    """Hiển thị cấu trúc dữ liệu hiện tại"""
    from data_manager import DataManager
    
    print("\\n📊 CẤU TRÚC DỮ LIỆU HIỆN TẠI")
    print("=" * 50)
    
    dm = DataManager()
    summary = dm.get_data_summary()
    
    print(f"📁 Tổng số nguồn: {summary['total_sources']}")
    print(f"📄 Tổng số files: {summary['total_files']}")
    
    print("\\n📋 Chi tiết theo nguồn:")
    for source, details in summary["sources_detail"].items():
        status = "✅" if details['file_count'] > 0 else "⭕"
        print(f"  {status} {source:15} | {details['file_count']:2} files | {details['latest_records']:3} records")
    
    print("\\n📁 Cấu trúc thư mục:")
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
    
    print("\\n🧹 DỌN DẸP DỮ LIỆU CŨ")
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
'''
    
    # Đọc file main.py
    with open(main_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Thêm chức năng mới vào trước def main()
    if "def show_data_structure():" not in content:
        # Tìm vị trí def main()
        main_pos = content.find("def main():")
        if main_pos != -1:
            new_content = content[:main_pos] + additional_functions + "\n" + content[main_pos:]
            
            # Cập nhật menu trong main
            old_menu = '''        print("6. 📈 Xem thống kê")
        print("7. ❓ Hướng dẫn sử dụng")
        print("8. 🚪 Thoát")'''
            
            new_menu = '''        print("6. 📈 Xem thống kê")
        print("7. 📊 Xem cấu trúc dữ liệu")
        print("8. 🧹 Dọn dẹp dữ liệu cũ")
        print("9. ❓ Hướng dẫn sử dụng")
        print("10. 🚪 Thoát")'''
            
            new_content = new_content.replace(old_menu, new_menu)
            
            # Cập nhật logic xử lý choice
            old_choices = '''        if choice == "1":
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
            show_help()
        elif choice == "8":
            print("👋 Cảm ơn bạn đã sử dụng Lich Crawler!")
            break'''
            
            new_choices = '''        if choice == "1":
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
            break'''
            
            new_content = new_content.replace(old_choices, new_choices)
            
            # Cập nhật input validation
            old_input = '''        choice = input("\\nNhập lựa chọn (1-8): ").strip()'''
            new_input = '''        choice = input("\\nNhập lựa chọn (1-10): ").strip()'''
            
            new_content = new_content.replace(old_input, new_input)
            
            # Lưu file
            with open(main_py_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("✅ Đã cập nhật main.py với chức năng quản lý dữ liệu mới")
        else:
            print("⚠️ Không tìm thấy hàm main() để cập nhật")
    else:
        print("✅ main.py đã có chức năng quản lý dữ liệu")

if __name__ == "__main__":
    print("🔧 CẬP NHẬT HỆ THỐNG")
    print("=" * 30)
    
    update_base_crawler()
    update_main_py()
    
    print("\\n✅ Hoàn thành cập nhật hệ thống!")
    print("\\nBây giờ bạn có thể:")
    print("1. Chạy python3 main.py để xem menu mới")
    print("2. Sử dụng tùy chọn 7 để xem cấu trúc dữ liệu")
    print("3. Sử dụng tùy chọn 8 để dọn dẹp dữ liệu cũ")
