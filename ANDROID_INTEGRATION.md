# 📱 Android Integration Guide

## 🚀 Quick Start

### 1. Start API Server
```bash
pip install -r requirements.txt
python3 android_api.py
```

API sẽ chạy tại: `http://localhost:8000`

### 2. Main Endpoints

#### Get Calendar Month
```
GET /calendar/{year}/{month}
```

Response:
```json
{
  "success": true,
  "data": {
    "year": 2024,
    "month": 7,
    "total_days": 31,
    "days": [
      {
        "solar_date": "2024-07-01",
        "lunar_date": "22/06",
        "day_of_week": 2,
        "can_chi": {
          "day": "Bính Tuất",
          "month": "Quý Mùi", 
          "year": "Ất Tỵ"
        },
        "feng_shui": {
          "good_hours": ["Dần (3h-5h)", "Thìn (7h-9h)"],
          "bad_hours": [],
          "lucky_direction": "Đông Nam",
          "unlucky_direction": "Tây Bắc"
        },
        "activities": {
          "is_good_day": true,
          "good_activities": ["Xuất hành", "Khai trương"],
          "bad_activities": ["Cưới hỏi", "An táng"]
        },
        "holidays": {
          "solar": null,
          "lunar": null
        },
        "solar_term": "Tiểu thử",
        "notes": "Ngày hoàng đạo...",
        "metadata": {
          "source": "lichviet.app",
          "crawled_at": "2025-07-16T22:00:00"
        }
      }
    ],
    "summary": {
      "good_days": 15,
      "bad_days": 5,
      "holidays": 2,
      "sources": ["lichviet.app", "lichvn.net"]
    }
  }
}
```

#### Get Current Month
```
GET /calendar/current
```

#### Get Holidays
```
GET /holidays/{year}/{month}
```

#### Search by Lunar Date
```
GET /search?lunar_day=15&lunar_month=8&year=2024
```

## 🔧 Android Implementation

### 1. Data Models (Kotlin)

```kotlin
data class CalendarResponse(
    val success: Boolean,
    val data: MonthlyCalendar
)

data class MonthlyCalendar(
    val year: Int,
    val month: Int,
    val total_days: Int,
    val days: List<CalendarDay>,
    val summary: CalendarSummary
)

data class CalendarDay(
    val solar_date: String,
    val lunar_date: String,
    val day_of_week: Int,
    val can_chi: CanChi,
    val feng_shui: FengShui,
    val activities: Activities,
    val holidays: Holidays,
    val solar_term: String?,
    val notes: String?,
    val metadata: Metadata
)

data class CanChi(
    val day: String?,
    val month: String?,
    val year: String?
)

data class FengShui(
    val good_hours: List<String>,
    val bad_hours: List<String>,
    val lucky_direction: String?,
    val unlucky_direction: String?
)

data class Activities(
    val is_good_day: Boolean?,
    val good_activities: List<String>,
    val bad_activities: List<String>
)
```

### 2. API Service (Retrofit)

```kotlin
interface CalendarApiService {
    @GET("calendar/{year}/{month}")
    suspend fun getCalendar(
        @Path("year") year: Int,
        @Path("month") month: Int
    ): CalendarResponse
    
    @GET("calendar/current")
    suspend fun getCurrentCalendar(): CalendarResponse
    
    @GET("holidays/{year}/{month}")
    suspend fun getHolidays(
        @Path("year") year: Int,
        @Path("month") month: Int
    ): HolidaysResponse
    
    @GET("search")
    suspend fun searchByLunarDate(
        @Query("lunar_day") lunarDay: Int,
        @Query("lunar_month") lunarMonth: Int,
        @Query("year") year: Int?
    ): SearchResponse
}
```

### 3. Repository

```kotlin
class CalendarRepository(private val api: CalendarApiService) {
    
    suspend fun getCalendarMonth(year: Int, month: Int): Result<MonthlyCalendar> {
        return try {
            val response = api.getCalendar(year, month)
            if (response.success) {
                Result.success(response.data)
            } else {
                Result.failure(Exception("API returned error"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun getCurrentMonth(): Result<MonthlyCalendar> {
        return try {
            val response = api.getCurrentCalendar()
            if (response.success) {
                Result.success(response.data)
            } else {
                Result.failure(Exception("API returned error"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

## 📊 Data Quality Features

✅ **Merged Data**: Dữ liệu được merge từ nhiều nguồn uy tín
✅ **Normalized**: Tất cả data đều được chuẩn hóa format
✅ **Validated**: Đã validate và clean data
✅ **Consistent**: Schema nhất quán cho tất cả endpoints
✅ **Reliable**: Error handling và fallback values

## 🎯 Best Practices

1. **Caching**: Cache data tại client để reduce API calls
2. **Offline Support**: Store essential data locally
3. **Error Handling**: Handle network errors gracefully
4. **Loading States**: Show loading indicators
5. **Data Validation**: Validate API responses

## 🔄 Data Updates

Data được update thường xuyên. Sử dụng endpoint `/available-months` để check tháng nào có data mới.
