let chartInstance = null;
let donutChartInstance = null;

function safeParse(id) {
    const el = document.getElementById(id);
    if (!el) return [];
    try { return JSON.parse(el.textContent.trim()); } catch { return []; }
}

function buildCharts() {
    if (typeof Chart === "undefined") {
        console.error("Chart.js gagal dimuat; grafik tidak dapat ditampilkan.");
        return;
    }

    const lineCanvas = document.getElementById('chart');
    if (lineCanvas) {
        const ctx = lineCanvas.getContext("2d");
        const labels = safeParse('chart-labels');
        const hist   = safeParse('chart-hist');
        const pred   = safeParse('chart-pred');

        if (labels.length) {
            chartInstance = new Chart(ctx, {
                data: {
                    labels: labels,
                    datasets: [
                        {
                            type: "line", label: "Histori Suhu (°C)", data: hist,
                            borderColor: "#0ea5e9", backgroundColor: "rgba(14, 165, 233, 0.1)",
                            borderWidth: 3, tension: 0.4, pointRadius: 4, fill: true
                        },
                        {
                            type: "line", label: "Prediksi Suhu (°C)", data: pred,
                            borderColor: "#10b981", backgroundColor: "rgba(16, 185, 129, 0.1)",
                            borderDash: [5,5], borderWidth: 3, tension: 0.4, pointRadius: 4, spanGaps: true, fill: true
                        }
                    ]
                },
                options: {
                    responsive: true, maintainAspectRatio: false,
                    interaction: { mode: 'index', intersect: false },
                    plugins: { 
                        legend: { labels: { color: "#64748b", usePointStyle: true, boxWidth: 8 } },
                        tooltip: { backgroundColor: 'rgba(15, 23, 42, 0.9)', titleFont: {size: 13}, bodyFont: {size: 13}, padding: 10, cornerRadius: 8 }
                    },
                    scales: {
                        x: { ticks: { color: "#94a3b8" }, grid: { display: false } },
                        y: { ticks: { color: "#94a3b8" }, grid: { color: "#f1f5f9", drawBorder: false } }
                    }
                }
            });
        }
    }

    const donutCanvas = document.getElementById('weatherDonutChart');
    if (donutCanvas) {
        const rainValues = safeParse('forecast-rain-values').map(Number).filter(Number.isFinite);
        const rainCounts = [0, 0, 0, 0];
        rainValues.forEach((rain) => {
            if (rain <= 0) rainCounts[0] += 1;
            else if (rain <= 2) rainCounts[1] += 1;
            else if (rain <= 10) rainCounts[2] += 1;
            else rainCounts[3] += 1;
        });

        const ctxDonut = donutCanvas.getContext('2d');
        donutChartInstance = new Chart(ctxDonut, {
            type: 'doughnut',
            data: {
                labels: ['Tidak hujan (0 mm)', 'Ringan (0–2 mm)', 'Sedang (>2–10 mm)', 'Lebat (>10 mm)'],
                datasets: [{
                    data: rainCounts,
                    backgroundColor: ['#f59e0b', '#3b82f6', '#0ea5e9', '#8b5cf6'],
                    borderWidth: 3, borderColor: '#ffffff', hoverOffset: 4
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false, cutout: '70%',
                plugins: { legend: { position: 'bottom', labels: { boxWidth: 10, usePointStyle: true, color: '#64748b' } } }
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', buildCharts);