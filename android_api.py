"""
Android API Server - FastAPI server để phục vụ data cho Android app
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Optional, List, Dict, Any
import json
from pathlib import Path
from datetime import datetime, timedelta
import uvicorn

# Import models
import sys
sys.path.append(str(Path(__file__).parent))
from models.calendar_models import CalendarDay, MonthlyCalendar

app = FastAPI(
    title="Vietnamese Calendar API",
    description="API for Vietnamese Lunar Calendar data for Android app",
    version="1.0.0"
)

# CORS middleware cho Android app và web interface
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong production nên specify domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for web interface
web_dir = Path(__file__).parent / "web"
if web_dir.exists():
    app.mount("/static", StaticFiles(directory=str(web_dir)), name="static")

# Data directory
DATA_DIR = Path(__file__).parent / "data" / "api"

class CalendarAPI:
    """Calendar API handlers"""
    
    @staticmethod
    def load_month_data(year: int, month: int) -> Optional[Dict]:
        """Load calendar data for specific month"""
        # Thử cả format 1 chữ số và 2 chữ số
        filenames = [
            f"calendar_{year}_{month}.json",      # 1 chữ số (từ generator)
            f"calendar_{year}_{month:02d}.json"   # 2 chữ số (backup)
        ]
        
        for filename in filenames:
            file_path = DATA_DIR / filename
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception:
                    continue
        
        return None
    
    @staticmethod
    def get_available_months() -> List[str]:
        """Get list of available months"""
        months = []
        
        if DATA_DIR.exists():
            for file in DATA_DIR.glob("calendar_*.json"):
                filename = file.stem
                parts = filename.split('_')
                if len(parts) >= 3:
                    try:
                        year = int(parts[1])
                        month = int(parts[2])
                        months.append(f"{year}-{month:02d}")
                    except:
                        pass
        
        return sorted(months)

# API endpoints
@app.get("/")
async def serve_web_app():
    """Serve the web application"""
    web_file = Path(__file__).parent / "web" / "index.html"
    if web_file.exists():
        return FileResponse(web_file)
    else:
        return {"message": "Vietnamese Calendar API", "docs": "/docs", "web_interface": "Web files not found"}

@app.get("/api")
async def api_info():
    """API information endpoint"""
    return {
        "message": "Vietnamese Calendar API",
        "version": "1.0.0",
        "endpoints": {
            "/calendar/{year}/{month}": "Get calendar data for specific month",
            "/calendar/current": "Get current month calendar",
            "/holidays/{year}/{month}": "Get holidays for specific month",
            "/good-days/{year}/{month}": "Get good days for specific month",
            "/available-months": "Get list of available months"
        }
    }

@app.get("/calendar/{year}/{month}")
async def get_calendar(year: int, month: int):
    """Get calendar data for specific month"""
    
    # Validate year and month
    if year < 2020 or year > 2030:
        raise HTTPException(status_code=400, detail="Year must be between 2020 and 2030")
    
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12")
    
    data = CalendarAPI.load_month_data(year, month)
    
    if not data:
        raise HTTPException(
            status_code=404, 
            detail=f"Calendar data not found for {year}-{month:02d}"
        )
    
    return {
        "success": True,
        "data": data,
        "requested": f"{year}-{month:02d}"
    }

@app.get("/calendar/current")
async def get_current_calendar():
    """Get current month calendar"""
    now = datetime.now()
    return await get_calendar(now.year, now.month)

@app.get("/holidays/{year}/{month}")
async def get_holidays(year: int, month: int):
    """Get holidays for specific month"""
    
    data = CalendarAPI.load_month_data(year, month)
    
    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"Data not found for {year}-{month:02d}"
        )
    
    holidays = []
    for day in data.get("days", []):
        solar_holiday = day.get("holidays", {}).get("solar")
        lunar_holiday = day.get("holidays", {}).get("lunar")
        
        if solar_holiday or lunar_holiday:
            holidays.append({
                "date": day["solar_date"],
                "lunar_date": day["lunar_date"],
                "solar_holiday": solar_holiday,
                "lunar_holiday": lunar_holiday
            })
    
    return {
        "success": True,
        "data": {
            "year": year,
            "month": month,
            "holidays": holidays,
            "total": len(holidays)
        }
    }

@app.get("/good-days/{year}/{month}")
async def get_good_days(year: int, month: int):
    """Get good days for specific month"""
    
    data = CalendarAPI.load_month_data(year, month)
    
    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"Data not found for {year}-{month:02d}"
        )
    
    good_days = []
    for day in data.get("days", []):
        activities = day.get("activities", {})
        if activities.get("is_good_day") is True:
            good_days.append({
                "date": day["solar_date"],
                "lunar_date": day["lunar_date"],
                "can_chi_day": day.get("can_chi", {}).get("day"),
                "good_activities": activities.get("good_activities", []),
                "good_hours": day.get("feng_shui", {}).get("good_hours", [])
            })
    
    return {
        "success": True,
        "data": {
            "year": year,
            "month": month,
            "good_days": good_days,
            "total": len(good_days)
        }
    }

@app.get("/bad-days/{year}/{month}")
async def get_bad_days(year: int, month: int):
    """Get bad days for specific month"""
    
    data = CalendarAPI.load_month_data(year, month)
    
    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"Data not found for {year}-{month:02d}"
        )
    
    bad_days = []
    for day in data.get("days", []):
        activities = day.get("activities", {})
        if activities.get("is_good_day") is False:
            bad_days.append({
                "date": day["solar_date"],
                "lunar_date": day["lunar_date"],
                "can_chi_day": day.get("can_chi", {}).get("day"),
                "bad_activities": activities.get("bad_activities", []),
                "bad_hours": day.get("feng_shui", {}).get("bad_hours", [])
            })
    
    return {
        "success": True,
        "data": {
            "year": year,
            "month": month,
            "bad_days": bad_days,
            "total": len(bad_days)
        }
    }

@app.get("/available-months")
async def get_available_months():
    """Get list of available months"""
    
    months = CalendarAPI.get_available_months()
    
    return {
        "success": True,
        "data": {
            "available_months": months,
            "total": len(months)
        }
    }

@app.get("/day/{year}/{month}/{day}")
async def get_day_details(year: int, month: int, day: int):
    """Get detailed information for specific day"""
    
    data = CalendarAPI.load_month_data(year, month)
    
    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"Data not found for {year}-{month:02d}"
        )
    
    target_date = f"{year}-{month:02d}-{day:02d}"
    
    for day_data in data.get("days", []):
        if day_data["solar_date"] == target_date:
            return {
                "success": True,
                "data": day_data
            }
    
    raise HTTPException(
        status_code=404,
        detail=f"Day {target_date} not found"
    )

@app.get("/search")
async def search_by_lunar_date(
    lunar_day: int = Query(..., description="Lunar day (1-30)"),
    lunar_month: int = Query(..., description="Lunar month (1-12)"),
    year: Optional[int] = Query(None, description="Year to search in")
):
    """Search for solar dates by lunar date"""
    
    if year is None:
        year = datetime.now().year
    
    target_lunar = f"{lunar_day:02d}/{lunar_month:02d}"
    results = []
    
    # Search through all months in the year
    for month in range(1, 13):
        data = CalendarAPI.load_month_data(year, month)
        if data:
            for day_data in data.get("days", []):
                if day_data["lunar_date"] == target_lunar:
                    results.append({
                        "solar_date": day_data["solar_date"],
                        "lunar_date": day_data["lunar_date"],
                        "can_chi_day": day_data.get("can_chi", {}).get("day"),
                        "is_good_day": day_data.get("activities", {}).get("is_good_day")
                    })
    
    return {
        "success": True,
        "data": {
            "query": f"Lunar {lunar_day:02d}/{lunar_month:02d} in {year}",
            "results": results,
            "total": len(results)
        }
    }

if __name__ == "__main__":
    print("🚀 Starting Vietnamese Calendar API Server...")
    print("📱 Serving data for Android app")
    print("🌐 API Documentation: http://localhost:8000/docs")
    
    uvicorn.run(
        "android_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
