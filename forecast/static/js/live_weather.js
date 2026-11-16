document.addEventListener("DOMContentLoaded", () => {
    if (typeof Chart === "undefined") {
        console.error("Chart.js gagal dimuat");
        return;
    }
    const labels = WEATHER_CONFIG.labelsHist || [];
    const temps = WEATHER_CONFIG.tempsHist || [];
    const hums = WEATHER_CONFIG.humsHist || [];
    const winds = WEATHER_CONFIG.windsHist || [];

    function createChart(canvasId, label, data, color) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.warn(`Canvas ${canvasId} tidak ditemukan`);
            return;
        }
        new Chart(canvas.getContext("2d"), {
            type: "line",
            data: { labels, datasets: [{ label, data, borderColor: color, backgroundColor: color + "20", fill: true, tension: 0.4, borderWidth: 3, pointRadius: 3, pointHoverRadius: 5 }] },
            options: { responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { x: { ticks: { color: "#64748b" }, grid: { color: "#e2e8f0" } }, y: { ticks: { color: "#64748b" }, grid: { color: "#e2e8f0" } } }
            }
        });
    }
    createChart("tempChart", "Temperature", temps, "#ef4444");
    createChart("humChart", "Humidity", hums, "#3b82f6");
    createChart("windChart", "Wind", winds, "#22c55e");
});
