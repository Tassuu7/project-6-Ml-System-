/**
 * DataMorph Studio - Native SVG Data Visualization & Charting Subsystem
 * Zero-dependency SVG renderer for histograms, quality gauges, and trend curves.
 */

class DataMorphCharts {
    /**
     * Renders a clean SVG distribution histogram into a target container.
     */
    static renderHistogram(containerId, dataPoints, binCount = 8) {
        const container = document.getElementById(containerId);
        if (!container || !dataPoints || dataPoints.length === 0) return;

        const nums = dataPoints.map(Number).filter(n => !isNaN(n));
        if (nums.length === 0) {
            container.innerHTML = '<div class="empty-state">No numerical distribution available.</div>';
            return;
        }

        const min = Math.min(...nums);
        const max = Math.max(...nums);
        const range = max - min || 1;
        const binStep = range / binCount;
        const bins = new Array(binCount).fill(0);

        nums.forEach(val => {
            const idx = Math.min(Math.floor((val - min) / binStep), binCount - 1);
            bins[idx]++;
        });

        const maxCount = Math.max(...bins, 1);
        const width = 360;
        const height = 120;
        const barWidth = (width - (binCount * 4)) / binCount;

        let svg = `<svg viewBox="0 0 ${width} ${height}" class="chart-svg">`;
        bins.forEach((count, i) => {
            const barHeight = (count / maxCount) * (height - 30);
            const x = i * (barWidth + 4) + 6;
            const y = height - barHeight - 20;
            const binMin = (min + i * binStep).toFixed(1);

            svg += `
                <rect x="${x}" y="${y}" width="${barWidth}" height="${barHeight}" fill="#3b82f6" rx="2" opacity="0.85">
                    <title>Range: ${binMin}+ | Count: ${count}</title>
                </rect>
                <text x="${x + barWidth / 2}" y="${height - 6}" font-size="9" fill="#94a3b8" text-anchor="middle">${binMin}</text>
            `;
        });
        svg += '</svg>';
        container.innerHTML = svg;
    }

    /**
     * Renders an SVG Sparkline Trend Curve for quality/drift metrics.
     */
    static renderTrendSparkline(containerId, series = [95, 96, 94, 98, 98.5, 99]) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const width = 280;
        const height = 140;
        const padding = 16;
        const max = Math.max(...series, 100);
        const min = Math.min(...series, 90);
        const range = max - min || 1;

        const stepX = (width - padding * 2) / (series.length - 1);
        const points = series.map((val, idx) => {
            const x = padding + idx * stepX;
            const y = height - padding - ((val - min) / range) * (height - padding * 2);
            return `${x},${y}`;
        }).join(" ");

        let svg = `
            <svg viewBox="0 0 ${width} ${height}" class="chart-svg">
                <polyline fill="none" stroke="#10b981" stroke-width="2.5" points="${points}" />
                ${series.map((val, idx) => {
                    const x = padding + idx * stepX;
                    const y = height - padding - ((val - min) / range) * (height - padding * 2);
                    return `<circle cx="${x}" cy="${y}" r="3.5" fill="#10b981" />`;
                }).join("")}
            </svg>
        `;
        container.innerHTML = svg;
    }
}
