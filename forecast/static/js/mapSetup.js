document.addEventListener('DOMContentLoaded', () => {

    // 1. HIDE LOADING OVERLAY
    const loadingOverlay = document.getElementById('loading-overlay');
    if (loadingOverlay) {
        setTimeout(() => {
            loadingOverlay.classList.remove('active');
        }, 800);
    }

    // 2. CEK ELEMEN MAP
    const mapElement = document.getElementById('bantenMap');
    if (!mapElement) {
        console.error('Element #bantenMap tidak ditemukan');
        return;
    }

    // 3. INIT MAP
    if (typeof L === 'undefined') {
        mapElement.textContent = 'Peta membutuhkan koneksi internet untuk memuat Leaflet.';
        return;
    }

    const map = L.map('bantenMap', {
        zoomControl: true,
        attributionControl: true
    }).setView([-6.4058, 106.0640], 9);

    // 4. BASE MAP (Gunakan OpenStreetMap standar agar anti-blokir AdBlock)
    L.tileLayer(
        'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        {
            attribution: '&copy; OpenStreetMap',
            maxZoom: 19
        }
    ).addTo(map);

    // Weather radar tiles require a private provider key. Keep the base map
    // available without exposing an API secret in browser-side JavaScript.

    // 6. FIX MAP SIZE
    setTimeout(() => {
        map.invalidateSize();
    }, 500);

    window.addEventListener('resize', () => {
        map.invalidateSize();
    });

    // 7. AMBIL WEATHER JSON DARI HTML
    let cityWeatherData = {};
    const weatherDataEl = document.getElementById('city-weather-json');
    if (weatherDataEl) {
        try {
            cityWeatherData = JSON.parse(weatherDataEl.textContent.trim());
        } catch (e) {
            console.error('Gagal parse weather JSON:', e);
        }
    }

    // 8. DATA KOTA
    const cities = [
        { name: "Serang", lat: -6.1104, lon: 106.1636, color: "#3b82f6" },
        { name: "Cilegon", lat: -6.0174, lon: 106.0201, color: "#f97316" },
        { name: "Tangerang", lat: -6.1702, lon: 106.6403, color: "#0ea5e9" },
        { name: "Tangerang Selatan", lat: -6.2886, lon: 106.7179, color: "#22c55e" },
        { name: "Pandeglang", lat: -6.3090, lon: 106.1045, color: "#8b5cf6" },
        { name: "Rangkasbitung", lat: -6.3619, lon: 106.2625, color: "#eab308" }
    ];

    // 9. RENDER MARKERS
    cities.forEach(city => {
        // CUSTOM MARKER HTML
        const customIcon = L.divIcon({
            className: 'custom-weather-marker',
            html: `
                <div class="weather-marker-wrapper">
                    <div class="weather-marker-pulse" style="background:${city.color};"></div>
                    <div class="weather-marker-core" style="background:${city.color}; box-shadow:0 0 18px ${city.color};"></div>
                </div>
            `,
            iconSize: [26, 26],
            iconAnchor: [13, 13]
        });

        const marker = L.marker([city.lat, city.lon], { icon: customIcon }).addTo(map);

        // AMBIL DATA CUACA KOTA SPESIFIK
        const weather = cityWeatherData[city.name] || {};
        const temp = weather.temp !== undefined ? Math.round(Number(weather.temp)) : '--';
        const hum = weather.humidity !== undefined ? Math.round(Number(weather.humidity)) : '--';
        const wind = weather.wind !== undefined ? Math.round(Number(weather.wind)) : '--';
        const rainChance = weather.chance_of_rain !== undefined ? weather.chance_of_rain : '--';
        const desc = weather.desc || 'Data tidak tersedia';

        // TOOLTIP HTML
        const escapeHtml = (value) => String(value).replace(/[&<>"']/g, (char) => ({
            '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
        }[char]));

        const tooltipHtml = `
            <div class="map-tooltip">
                <div class="tooltip-city">${escapeHtml(city.name)}</div>
                <div class="tooltip-desc">${escapeHtml(desc)}</div>
                <div class="tooltip-temp">${escapeHtml(temp)}°C</div>
                <div class="tooltip-grid">
                    <div class="tooltip-item">💧 ${escapeHtml(hum)}%</div>
                    <div class="tooltip-item">🌧️ ${escapeHtml(rainChance)}%</div>
                    <div class="tooltip-item">🌬️ ${escapeHtml(wind)}</div>
                </div>
                <div class="tooltip-footer">Klik untuk detail cuaca</div>
            </div>
        `;

        marker.bindTooltip(tooltipHtml, {
            sticky: true,
            direction: 'top',
            offset: [0, -15],
            opacity: 1
        });

        // KLIK MENUJU HALAMAN DETAIL
        marker.on('click', () => {
            if (loadingOverlay) {
                loadingOverlay.classList.add('active');
            }
            setTimeout(() => {
                window.location.href = `/weather/${encodeURIComponent(city.name)}/`;
            }, 300);
        });
    });
});