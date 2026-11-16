document.addEventListener('DOMContentLoaded', () => {
    const tempEl = document.getElementById('temp-value');
    const descEl = document.querySelector('.desc');
    const cityNameEl = document.getElementById('cityName');
    const cityName = cityNameEl ? cityNameEl.innerText.trim() : '';
    if (!cityName) return;

    const commonOptions = {
        responsive: true, maintainAspectRatio: false,
        animation: { duration: 0 },
        scales: {
            x: { display: false },
            y: { ticks: { color: "#aaa", font: {size: 10} }, grid: { color: "rgba(255,255,255,0.1)" } }
        },
        plugins: { legend: { display: false } }
    };

    const createChart = (id, color, label) => {
        const canvas = document.getElementById(id);
        if (!canvas || typeof Chart === "undefined") return null;
        return new Chart(canvas.getContext("2d"), {
            type: "line",
            data: {
                labels: Array(20).fill(""), 
                datasets: [{ data: Array(20).fill(null), borderColor: color, tension: 0.4, borderWidth: 2 }]
            },
            options: commonOptions
        });
    };

    const rtTemp = createChart("rtTempChart", "#38bdf8", "Suhu");
    const rtWind = createChart("rtWindChart", "#22c55e", "Angin");
    const rtHum = createChart("rtHumChart", "#facc15", "Kelembapan");

    // ================= FETCH & UPDATE DATA =================
    async function fetchRealtime() {
        try {
            const res = await fetch(`/api/weather/?city=${encodeURIComponent(cityName)}`);
            const data = await res.json();

            // Mempertahankan presisi desimal
            if (data.temp !== undefined && tempEl) {
                tempEl.innerHTML = Number(data.temp).toFixed(1);
            }
            if (data.desc && descEl) {
                descEl.innerText = data.desc;
            }

            // Gunakan cast Number secara murni
            if (data.temp !== undefined) updateRealtimeChart(rtTemp, Number(data.temp));
            if (data.wind !== undefined) updateRealtimeChart(rtWind, Number(data.wind));
            if (data.hum !== undefined) updateRealtimeChart(rtHum, Number(data.hum));

        } catch (e) {
            console.log("Realtime fetch error:", e);
        }
    }

    function updateRealtimeChart(chart, newValue) {
        if (!chart || !Number.isFinite(newValue)) return;
        const dataset = chart.data.datasets[0].data;
        dataset.push(newValue);
        dataset.shift(); 
        chart.update();
    }

    fetchRealtime();
    window.setInterval(fetchRealtime, 15000);
});