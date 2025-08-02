// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// Global State
let currentYear = 2024;  // Thay đổi từ 2025 về 2024
let currentMonth = 7;    // Thay đổi từ new Date().getMonth() + 1 về 7
let calendarData = null;
let holidaysData = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

async function initializeApp() {
    setupEventListeners();
    await loadInitialData();
    updateCalendar();
    updateUI();
}

function setupEventListeners() {
    // Navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const target = link.getAttribute('href').substring(1);
            showSection(target);
            
            // Update active nav link
            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
            link.classList.add('active');
        });
    });

    // Month/Year selectors
    document.getElementById('monthSelect').addEventListener('change', (e) => {
        currentMonth = parseInt(e.target.value);
        updateCalendar();
    });

    document.getElementById('yearSelect').addEventListener('change', (e) => {
        currentYear = parseInt(e.target.value);
        updateCalendar();
    });

    // Month navigation buttons
    document.getElementById('prevMonth').addEventListener('click', () => {
        currentMonth--;
        if (currentMonth < 1) {
            currentMonth = 12;
            currentYear--;
        }
        updateMonthYearSelectors();
        updateCalendar();
    });

    document.getElementById('nextMonth').addEventListener('click', () => {
        currentMonth++;
        if (currentMonth > 12) {
            currentMonth = 1;
            currentYear++;
        }
        updateMonthYearSelectors();
        updateCalendar();
    });

    // Day info modal
    document.getElementById('closeDayInfo').addEventListener('click', () => {
        document.getElementById('dayInfo').style.display = 'none';
    });

    // Search functionality
    document.getElementById('searchBtn').addEventListener('click', performSearch);
    document.getElementById('searchInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            performSearch();
        }
    });

    // Activity filter
    document.getElementById('activityFilter').addEventListener('change', filterGoodDays);
}

function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Show target section
    document.getElementById(sectionId).classList.add('active');
    
    // Load section-specific data
    switch(sectionId) {
        case 'holidays':
            loadHolidays();
            break;
        case 'good-days':
            loadGoodDays();
            break;
        case 'search':
            // Search section doesn't need initial data
            break;
    }
}

async function loadInitialData() {
    showLoading();
    try {
        await loadCalendarData();
        await loadHolidays();
    } catch (error) {
        console.error('Error loading initial data:', error);
        showToast('Lỗi khi tải dữ liệu', 'error');
    } finally {
        hideLoading();
    }
}

async function loadCalendarData() {
    try {
        const response = await fetch(`${API_BASE_URL}/calendar/${currentYear}/${currentMonth}`);
        if (!response.ok) throw new Error('Failed to fetch calendar data');
        calendarData = await response.json();
    } catch (error) {
        console.error('Error loading calendar data:', error);
        showToast('Không thể tải dữ liệu lịch', 'error');
    }
}

async function loadHolidays() {
    try {
        const response = await fetch(`${API_BASE_URL}/holidays/${currentYear}/${currentMonth}`);
        if (!response.ok) throw new Error('Failed to fetch holidays data');
        const result = await response.json();
        holidaysData = result.data?.holidays || [];
        displayHolidays();
    } catch (error) {
        console.error('Error loading holidays data:', error);
        showToast('Không thể tải dữ liệu ngày lễ', 'error');
    }
}

async function loadGoodDays() {
    try {
        const response = await fetch(`${API_BASE_URL}/good-days/${currentYear}/${currentMonth}`);
        if (!response.ok) throw new Error('Failed to fetch good days data');
        const result = await response.json();
        const goodDaysData = result.data?.good_days || [];
        displayGoodDays(goodDaysData);
    } catch (error) {
        console.error('Error loading good days data:', error);
        showToast('Không thể tải dữ liệu ngày tốt', 'error');
    }
}

function updateCalendar() {
    loadCalendarData().then(() => {
        renderCalendar();
    });
}

function renderCalendar() {
    const calendarGrid = document.getElementById('calendarGrid');
    calendarGrid.innerHTML = '';

    // Add day headers
    const dayHeaders = ['CN', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7'];
    dayHeaders.forEach(day => {
        const header = document.createElement('div');
        header.className = 'calendar-header';
        header.textContent = day;
        header.style.cssText = `
            padding: 1rem;
            text-align: center;
            font-weight: 700;
            background: var(--primary-color);
            color: white;
            font-size: 0.875rem;
        `;
        calendarGrid.appendChild(header);
    });

    if (!calendarData || !calendarData.days) {
        showToast('Không có dữ liệu lịch', 'warning');
        return;
    }

    // Calculate first day of month and number of days
    const firstDay = new Date(currentYear, currentMonth - 1, 1).getDay();
    const daysInMonth = new Date(currentYear, currentMonth, 0).getDate();
    const today = new Date();
    const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;

    // Add empty cells for days before the first day of month
    for (let i = 0; i < firstDay; i++) {
        const emptyDay = document.createElement('div');
        emptyDay.className = 'calendar-day other-month';
        calendarGrid.appendChild(emptyDay);
    }

    // Add days of the month
    for (let day = 1; day <= daysInMonth; day++) {
        const dateStr = `${currentYear}-${String(currentMonth).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
        const dayData = calendarData.days.find(d => d.solar_date === dateStr);
        
        const dayElement = document.createElement('div');
        dayElement.className = 'calendar-day';
        
        if (dateStr === todayStr) {
            dayElement.classList.add('today');
        }

        if (dayData) {
            // Check if it's a holiday
            const isHoliday = holidaysData && holidaysData.some(h => h.date === dateStr);
            if (isHoliday) {
                dayElement.classList.add('holiday');
            }

            // Check if it's a good day
            if (dayData.feng_shui && dayData.feng_shui.includes('tốt')) {
                dayElement.classList.add('good-day');
            }

            dayElement.innerHTML = `
                <div class="solar-date">${day}</div>
                <div class="lunar-date">${dayData.lunar_date || ''}</div>
                <div class="day-indicators">
                    ${isHoliday ? '<div class="indicator" style="background: var(--error-color);"></div>' : ''}
                    ${dayData.feng_shui && dayData.feng_shui.includes('tốt') ? '<div class="indicator" style="background: var(--success-color);"></div>' : ''}
                </div>
            `;

            dayElement.addEventListener('click', () => showDayInfo(dayData));
        } else {
            dayElement.innerHTML = `<div class="solar-date">${day}</div>`;
        }

        calendarGrid.appendChild(dayElement);
    }
}

function showDayInfo(dayData) {
    const dayInfo = document.getElementById('dayInfo');
    const selectedDate = document.getElementById('selectedDate');
    const lunarDate = document.getElementById('lunarDate');
    const canChi = document.getElementById('canChi');
    const fengShui = document.getElementById('fengShui');
    const activities = document.getElementById('activities');

    selectedDate.textContent = formatDate(dayData.solar_date);
    lunarDate.textContent = dayData.lunar_date || 'Không có dữ liệu';
    canChi.textContent = dayData.can_chi || 'Không có dữ liệu';
    fengShui.textContent = dayData.feng_shui || 'Không có dữ liệu';

    // Display activities
    activities.innerHTML = '';
    if (dayData.activities && dayData.activities.length > 0) {
        dayData.activities.forEach(activity => {
            const activityTag = document.createElement('div');
            activityTag.className = 'activity-tag';
            if (activity.includes('tốt') || activity.includes('nên')) {
                activityTag.classList.add('good');
            } else if (activity.includes('xấu') || activity.includes('không nên')) {
                activityTag.classList.add('bad');
            }
            activityTag.textContent = activity;
            activities.appendChild(activityTag);
        });
    } else {
        activities.innerHTML = '<span>Không có thông tin hoạt động</span>';
    }

    dayInfo.style.display = 'block';
}

function displayHolidays() {
    const holidaysGrid = document.getElementById('holidaysGrid');
    holidaysGrid.innerHTML = '';

    if (!holidaysData || holidaysData.length === 0) {
        holidaysGrid.innerHTML = '<p>Không có dữ liệu ngày lễ</p>';
        return;
    }

    holidaysData.forEach(holiday => {
        const holidayCard = document.createElement('div');
        holidayCard.className = 'holiday-card';
        holidayCard.innerHTML = `
            <h3>${holiday.name}</h3>
            <div class="holiday-date">${formatDate(holiday.date)}</div>
            <div class="holiday-description">${holiday.description || 'Ngày lễ quan trọng'}</div>
        `;
        holidaysGrid.appendChild(holidayCard);
    });
}

function displayGoodDays(goodDaysData) {
    const goodDaysList = document.getElementById('goodDaysList');
    goodDaysList.innerHTML = '';

    if (!goodDaysData || goodDaysData.length === 0) {
        goodDaysList.innerHTML = '<p>Không có dữ liệu ngày tốt cho tháng này</p>';
        return;
    }

    goodDaysData.forEach(day => {
        const goodDayItem = document.createElement('div');
        goodDayItem.className = 'good-day-item';
        
        const activities = day.activities || [];
        const activitiesHtml = activities.map(activity => 
            `<div class="activity-tag good">${activity}</div>`
        ).join('');

        goodDayItem.innerHTML = `
            <div class="good-day-header">
                <div class="good-day-date">${formatDate(day.solar_date)}</div>
                <div class="good-day-score">Tốt</div>
            </div>
            <div class="good-day-activities">
                ${activitiesHtml || '<span>Ngày tốt chung</span>'}
            </div>
        `;
        goodDaysList.appendChild(goodDayItem);
    });
}

async function performSearch() {
    const searchInput = document.getElementById('searchInput');
    const dateFilter = document.getElementById('dateFilter');
    const typeFilter = document.getElementById('typeFilter');
    const searchResults = document.getElementById('searchResults');

    const query = searchInput.value.trim();
    const date = dateFilter.value;
    const type = typeFilter.value;

    if (!query && !date && !type) {
        showToast('Vui lòng nhập từ khóa hoặc chọn bộ lọc', 'warning');
        return;
    }

    showLoading();
    try {
        let url = `${API_BASE_URL}/search?`;
        if (query) url += `q=${encodeURIComponent(query)}&`;
        if (date) url += `date=${date}&`;
        if (type) url += `type=${type}&`;

        const response = await fetch(url);
        if (!response.ok) throw new Error('Search failed');
        
        const results = await response.json();
        displaySearchResults(results);
    } catch (error) {
        console.error('Search error:', error);
        showToast('Lỗi khi tìm kiếm', 'error');
    } finally {
        hideLoading();
    }
}

function displaySearchResults(results) {
    const searchResults = document.getElementById('searchResults');
    searchResults.innerHTML = '';

    if (!results || results.length === 0) {
        searchResults.innerHTML = '<p>Không tìm thấy kết quả nào</p>';
        return;
    }

    results.forEach(result => {
        const resultItem = document.createElement('div');
        resultItem.className = 'search-result-item';
        resultItem.innerHTML = `
            <h3>${formatDate(result.solar_date)}</h3>
            <p><strong>Âm lịch:</strong> ${result.lunar_date || 'N/A'}</p>
            <p><strong>Can Chi:</strong> ${result.can_chi || 'N/A'}</p>
            <p><strong>Phong thủy:</strong> ${result.feng_shui || 'N/A'}</p>
            ${result.activities ? `<p><strong>Hoạt động:</strong> ${result.activities.join(', ')}</p>` : ''}
        `;
        resultItem.addEventListener('click', () => showDayInfo(result));
        searchResults.appendChild(resultItem);
    });
}

function filterGoodDays() {
    const filter = document.getElementById('activityFilter').value;
    // Reload good days with filter
    loadGoodDays();
}

function updateMonthYearSelectors() {
    document.getElementById('monthSelect').value = currentMonth;
    document.getElementById('yearSelect').value = currentYear;
}

function updateUI() {
    updateMonthYearSelectors();
}

function formatDate(dateStr) {
    const date = new Date(dateStr);
    const options = { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    };
    return date.toLocaleDateString('vi-VN', options);
}

function showLoading() {
    document.getElementById('loading').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
}

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;

    const container = document.getElementById('toastContainer');
    container.appendChild(toast);

    // Show toast
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);

    // Hide and remove toast
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            container.removeChild(toast);
        }, 300);
    }, 3000);
}

// Handle API connection errors
window.addEventListener('error', (event) => {
    if (event.message.includes('fetch')) {
        showToast('Không thể kết nối đến server. Vui lòng kiểm tra API server.', 'error');
    }
});

// Auto-refresh data every 5 minutes
setInterval(() => {
    loadInitialData();
}, 5 * 60 * 1000);
