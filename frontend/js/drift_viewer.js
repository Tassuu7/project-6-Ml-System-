class DriftViewer {
    constructor(app) {
        this.app = app;
    }

    async analyzeDrift() {
        if (!this.app.currentDatasetId || !this.app.transformedDatasetId) {
            alert("Execute a pipeline transformation first to analyze drift against baseline!");
            return;
        }

        const res = await fetch("/api/monitoring/drift", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                baseline_dataset_id: this.app.currentDatasetId,
                current_dataset_id: this.app.transformedDatasetId
            })
        });
        const data = await res.json();
        const container = document.getElementById("drift-results-container");

        if (res.ok && data.drift_report) {
            const report = data.drift_report;
            let html = `
                <div style="margin-bottom:16px;">
                    <strong>Overall Status:</strong> <span style="color:${report.overall_drift_status === 'STABLE' ? '#10b981' : '#ef4444'}; font-weight:700;">${report.overall_drift_status}</span> | 
                    <strong>Monitored Features:</strong> ${report.total_features_monitored} | 
                    <strong>Drifted Count:</strong> ${report.features_drifted_count}
                </div>
            `;
            for (const [col, stats] of Object.entries(report.feature_metrics)) {
                html += `
                    <div class="drift-card ${stats.drift_detected ? 'alert' : 'stable'}">
                        <div>
                            <div class="drift-feature-name">${col} (${stats.type})</div>
                            <div class="drift-stats">PSI: ${stats.psi || 'N/A'} | KS Stat: ${stats.ks_statistic || 'N/A'} | Severity: ${stats.severity}</div>
                        </div>
                        <div style="color:${stats.drift_detected ? '#ef4444' : '#10b981'}; font-weight:600;">
                            ${stats.drift_detected ? 'DRIFT DETECTED' : 'STABLE'}
                        </div>
                    </div>
                `;
            }
            container.innerHTML = html;
        } else {
            container.innerHTML = `<div class="empty-state">Error analyzing drift: ${data.error}</div>`;
        }
    }
}
