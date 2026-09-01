/**
 * DataMorph Studio - Export & Code Generation Modal Controller
 */

class ExportModal {
    constructor(app) {
        this.app = app;
        this.initEventListeners();
    }

    initEventListeners() {
        const copyBtn = document.getElementById("btn-copy-python-code");
        if (copyBtn) {
            copyBtn.addEventListener("click", () => {
                const codeEl = document.getElementById("compiled-python-code");
                if (codeEl) {
                    navigator.clipboard.writeText(codeEl.textContent);
                    this.app.showToast("Python code copied to clipboard!", "success");
                }
            });
        }

        const exportCsvBtn = document.getElementById("btn-export-csv");
        if (exportCsvBtn) {
            exportCsvBtn.addEventListener("click", () => this.exportData("csv"));
        }

        const exportJsonBtn = document.getElementById("btn-export-json");
        if (exportJsonBtn) {
            exportJsonBtn.addEventListener("click", () => this.exportData("json"));
        }
    }

    async exportData(format = "csv") {
        const dsId = this.app.transformedDatasetId || this.app.currentDatasetId;
        if (!dsId) {
            this.app.showToast("Load or transform a dataset first before exporting!", "warning");
            return;
        }

        try {
            const res = await fetch("/api/export", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    dataset_id: dsId,
                    format: format
                })
            });

            const data = await res.json();
            if (res.ok && data.status === "success") {
                const blob = new Blob([data.content], { type: format === "csv" ? "text/csv" : "application/json" });
                const url = URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = data.filename || `export.${format}`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
                this.app.showToast(`Exported ${format.toUpperCase()} successfully!`, "success");
            } else {
                this.app.showToast(`Export failed: ${data.error || "Unknown error"}`, "error");
            }
        } catch (e) {
            this.app.showToast(`Network error: ${e.message}`, "error");
        }
    }
}
