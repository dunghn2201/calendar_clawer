# 🌐 Vietnamese Calendar Web Interface

Giao diện web hiện đại để hiển thị dữ liệu lịch Việt từ API server.

## 🚀 Cách sử dụng

### 1. Khởi động API Server
```bash
cd lich-crawler
python3 android_api.py
```

### 2. Truy cập Web Interface
Mở trình duyệt và truy cập: **http://localhost:8000**

## ✨ Tính năng

### 📅 Lịch Âm Dương
- Hiển thị lịch theo tháng với ngày âm và dương
- Đánh dấu ngày lễ, ngày tốt, ngày hôm nay
- Click vào ngày để xem thông tin chi tiết
- Điều hướng qua lại các tháng dễ dàng

### 🎉 Ngày Lễ & Kỷ Niệm
- Danh sách các ngày lễ trong năm
- Hiển thị dạng card với thông tin đầy đủ
- Tự động cập nhật theo năm hiện tại

### ⭐ Ngày Tốt
- Danh sách ngày tốt theo tháng
- Bộ lọc theo loại hoạt động
- Thông tin chi tiết về hoạt động nên làm

### 🔍 Tìm Kiếm
- Tìm kiếm theo từ khóa
- Lọc theo ngày cụ thể
- Lọc theo loại (ngày tốt, ngày xấu, ngày lễ)

## 🎨 Design Features

### Modern UI/UX
- **Design System**: Sử dụng color palette chuyên nghiệp
- **Typography**: Font Inter cho giao diện hiện đại
- **Components**: Button, Card, Modal với design system nhất quán
- **Icons**: FontAwesome icons cho giao diện trực quan

### Responsive Design
- **Desktop**: Layout 2-3 cột tối ưu
- **Tablet**: Adaptive grid system
- **Mobile**: Single column với navigation collapsed

### Interactive Elements
- **Hover Effects**: Smooth transitions và animations
- **Loading States**: Spinner và skeleton loading
- **Toast Notifications**: Real-time feedback
- **Modal**: Day detail popup với overlay

## 📱 Mobile-First Approach

### Responsive Breakpoints
```css
/* Mobile */
@media (max-width: 480px)

/* Tablet */
@media (max-width: 768px)  

/* Desktop */
@media (min-width: 769px)
```

### Touch-Friendly
- **Button Size**: Minimum 44px touch targets
- **Spacing**: Adequate spacing for finger navigation
- **Gestures**: Swipe support for calendar navigation

## 🎯 Production Ready

### Performance
- **Lazy Loading**: Data loaded on demand
- **Caching**: API responses cached
- **Compression**: Optimized assets
- **CDN**: External libraries via CDN

### SEO & Accessibility
- **Semantic HTML**: Proper heading structure
- **ARIA Labels**: Screen reader support
- **Keyboard Navigation**: Full keyboard accessibility
- **Meta Tags**: Social sharing optimized

## 🔧 Customization

### Color Scheme
```css
:root {
    --primary-color: #6366f1;     /* Indigo */
    --secondary-color: #f59e0b;   /* Amber */
    --success-color: #10b981;     /* Emerald */
    --error-color: #ef4444;       /* Red */
}
```

### Themes
- **Light Theme**: Default clean white theme
- **Dark Theme**: Ready for dark mode implementation
- **Custom Themes**: Easy color variable override

## 📊 Analytics Ready

### Event Tracking
```javascript
// Example analytics events
trackEvent('calendar_date_click', {
    date: selectedDate,
    view: 'calendar'
});

trackEvent('search_performed', {
    query: searchTerm,
    results_count: results.length
});
```

## 🚀 Deployment Options

### 1. Local Development
```bash
python3 android_api.py
# Access: http://localhost:8000
```

### 2. Firebase Hosting
```bash
# Copy web files to Firebase project
cp -r web/* firebase-project/public/

# Deploy
firebase deploy
```

### 3. Vercel/Netlify
```bash
# Deploy static files
# API routes need serverless functions
```

### 4. Docker Container
```dockerfile
FROM nginx:alpine
COPY web/ /usr/share/nginx/html/
EXPOSE 80
```

## 📱 Android Integration

### WebView Integration
```kotlin
webView.loadUrl("http://localhost:8000")
webView.settings.javaScriptEnabled = true
```

### Data Sync
- API endpoints same as mobile app
- JSON format consistent
- Real-time updates available

## 🔮 Future Enhancements

### Features Roadmap
- [ ] **Dark Mode**: Toggle between light/dark themes  
- [ ] **Offline Support**: Service worker for offline access
- [ ] **Push Notifications**: Browser notifications for important dates
- [ ] **Export Features**: PDF/iCal export functionality
- [ ] **Multi-language**: English/Vietnamese language toggle
- [ ] **Widgets**: Embeddable calendar widgets
- [ ] **Social Sharing**: Share specific dates on social media

### Technical Improvements
- [ ] **PWA**: Progressive Web App functionality
- [ ] **SSR**: Server-side rendering for better SEO
- [ ] **GraphQL**: Advanced querying capabilities
- [ ] **Real-time**: WebSocket for live updates
- [ ] **Analytics**: Built-in usage analytics

## 📞 Support

### Browser Support
- ✅ Chrome 90+
- ✅ Firefox 88+  
- ✅ Safari 14+
- ✅ Edge 90+

### API Dependencies
- FastAPI server running on localhost:8000
- Calendar data in proper JSON format
- CORS enabled for cross-origin requests

---

**🎉 Enjoy your beautiful Vietnamese Calendar web interface!**
