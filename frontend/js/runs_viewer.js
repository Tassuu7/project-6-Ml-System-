/**
 * DataMorph Studio - Pipeline Runs History Controller
 * Renders execution timelines, durations, status badges, and step-by-step metrics.
 */

class RunsViewer {
    constructor(app) {
        this.app = app;
        this.runs = [];
    }

    async loadRuns() {
        try {
            const res = await fetch("/api/runs");
            if (!res.ok) return;
            const data = await res.json();
            this.runs = data.runs || [];
            this.renderRunsTable();
        } catch (e) {
            console.error("Failed to load runs", e);
        }
    }

    renderRunsTable() {
        const tbody = document.getElementById("runs-history-body");
        if (!tbody) return;

        if (this.runs.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; color:var(--text-muted); padding:32px;">No pipeline runs recorded yet. Execute a pipeline to track runs.</td></tr>';
            return;
        }

        let html = "";
        this.runs.forEach(run => {
            const isSuccess = run.status === "completed";
            const badgeClass = isSuccess ? "positive" : "danger";
            const duration = run.duration_ms ? `${run.duration_ms} ms` : "--";
            const rowsInOut = `${run.rows_in || 0} → ${run.rows_out || 0}`;

            html += `
                <tr>
                    <td><code>${run.run_id}</code></td>
                    <td style="font-weight:600;">${run.pipeline_name || "ActivePreprocessingDAG"}</td>
                    <td>${run.user || "admin"}</td>
                    <td style="font-family:var(--font-mono); font-size:11px; color:var(--text-muted);">${run.created_at || "--"}</td>
                    <td style="font-family:var(--font-mono);">${duration}</td>
                    <td style="font-family:var(--font-mono);">${rowsInOut}</td>
                    <td><span class="kpi-badge ${badgeClass}">${run.status.toUpperCase()}</span></td>
                </tr>
            `;
        });
        tbody.innerHTML = html;
    }
}
