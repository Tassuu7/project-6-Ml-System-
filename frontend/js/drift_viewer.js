/**
 * DataMorph Studio - Data Drift & Quality Monitor Controller
 * Calculates Population Stability Index (PSI), Kolmogorov-Smirnov (KS) test, and Total Variation.
 */

class DriftViewer {
    constructor(app) {
        this.app = app;
        this.initEventListeners();
    }

    initEventListeners() {
        const driftBtn = document.getElementById("btn-run-drift-analysis");
        if (driftBtn) {
            driftBtn.addEventListener("click", () => this.analyzeDrift());
        }
    }

    async analyzeDrift() {
        if (!this.app.currentDatasetId) {
            this.app.showToast("Please load or upload a dataset first!", "warning");
            return;
        }

        const container = document.getElementById("drift-results-container");
        if (container) {
            container.innerHTML = '<div class="empty-state">Computing Population Stability Index (PSI) & Kolmogorov-Smirnov statistics...</div>';
        }

        try {
            const res = await fetch("/api/monitoring/drift", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    baseline_dataset_id: this.app.currentDatasetId,
                    current_dataset_id: this.app.transformedDatasetId || undefined
                })
            });

            const data = await res.json();
            if (res.ok && data.drift_report) {
                this.renderDriftReport(data.drift_report);
                this.app.showToast("Drift analysis completed!", "success");
            } else {
                if (container) {
                    container.innerHTML = `<div class="empty-state" style="color:#ef4444;">Error calculating drift: ${data.error || "Unknown error"}</div>`;
                }
            }
        } catch (err) {
            if (container) {
                container.innerHTML = `<div class="empty-state" style="color:#ef4444;">Network error: ${err.message}</div>`;
            }
        }
    }

    renderDriftReport(report) {
        const container = document.getElementById("drift-results-container");
        if (!container) return;

        const isStable = report.overall_drift_status === "STABLE";
        const statusPillClass = isStable ? "stable" : "critical";

        let html = `
            <div class="card" style="margin-bottom:16px;">
                <div class="card-body" style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <div style="font-size:15px; font-weight:700;">Overall Drift Assessment</div>
                        <div style="font-size:11px; color:var(--text-muted);">Monitored Features: ${report.total_features_monitored} | Drifted Count: ${report.features_drifted_count}</div>
                    </div>
                    <span class="drift-status-pill ${statusPillClass}">${report.overall_drift_status}</span>
                </div>
            </div>

            <div class="drift-features-grid">
        `;

        for (const [col, stats] of Object.entries(report.feature_metrics || {})) {
            const drifted = stats.drift_detected;
            const cardClass = drifted ? "alert" : "stable";
            const severityClass = (stats.severity || "low").toLowerCase();
            const metricVal = stats.psi !== undefined ? `PSI: ${stats.psi}` : `Total Var: ${stats.total_variation_drift}`;
            const ksVal = stats.ks_statistic !== undefined ? ` | KS Stat: ${stats.ks_statistic}` : "";

            html += `
                <div class="drift-card ${cardClass}">
                    <div class="drift-feature-header">
                        <div>
                            <div class="drift-feature-name">${col}</div>
                            <div style="font-size:10px; color:var(--text-muted); font-family:var(--font-mono);">${stats.type.toUpperCase()}</div>
                        </div>
                        <span class="drift-status-pill ${severityClass}">${stats.severity || 'STABLE'}</span>
                    </div>

                    <div class="drift-metrics-summary">
                        <span>${metricVal}${ksVal}</span>
                    </div>

                    <div class="drift-comparison-bar">
                        <div class="drift-fill-bar ${severityClass}" style="width: ${Math.min(100, (stats.psi || stats.total_variation_drift || 0.05) * 250)}%;"></div>
                    </div>
                </div>
            `;
        }

        html += `</div>`;
        container.innerHTML = html;
    }
}
