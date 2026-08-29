class DataMorphApp {
    constructor() {
        this.currentDatasetId = null;
        this.transformedDatasetId = null;
        this.datasetViewer = new DatasetViewer();
        this.pipelineBuilder = new PipelineBuilder(this);
        this.driftViewer = new DriftViewer(this);
        this.initEventListeners();
    }

    initEventListeners() {
        // Tab Switching
        document.querySelectorAll(".nav-item").forEach(btn => {
            btn.addEventListener("click", () => {
                document.querySelectorAll(".nav-item").forEach(b => b.classList.remove("active"));
                document.querySelectorAll(".view-panel").forEach(p => p.classList.remove("active"));
                btn.classList.add("active");
                const tab = btn.getAttribute("data-tab");
                const panel = document.getElementById(`view-${tab}`);
                if (panel) panel.classList.add("active");
                document.getElementById("current-view-title").textContent = btn.textContent.trim();
            });
        });

        // Sample Data Button
        document.getElementById("btn-sample-data").addEventListener("click", () => this.loadSampleData());

        // File Upload
        document.getElementById("file-upload-input").addEventListener("change", (e) => this.handleFileUpload(e));

        // Pipeline buttons
        document.getElementById("btn-clear-pipeline").addEventListener("click", () => this.pipelineBuilder.clearPipeline());
        document.getElementById("btn-execute-dag").addEventListener("click", () => this.pipelineBuilder.execute());

        // Drift button
        document.getElementById("btn-run-drift").addEventListener("click", () => this.driftViewer.analyzeDrift());

        // Copy Code
        document.getElementById("btn-copy-python").addEventListener("click", () => RecipeManager.copyCode());

        // Export Buttons
        document.getElementById("btn-export-csv").addEventListener("click", () => ExportManager.export(this.currentDatasetId, "csv"));
        document.getElementById("btn-export-json").addEventListener("click", () => ExportManager.export(this.currentDatasetId, "json"));

        // Logout
        document.getElementById("btn-logout").addEventListener("click", () => {
            localStorage.removeItem("datamorph_token");
            window.location.href = "/login.html";
        });
    }

    async loadSampleData() {
        const sampleCsv = `customer_id,age,annual_income,credit_score,churn,country
1001,34,65000,720,0,USA
1002,45,82000,680,1,Germany
1003,28,45000,590,0,France
1004,52,115000,790,0,USA
1005,,54000,610,1,France
1006,39,78000,740,0,Germany
1007,61,125000,810,1,USA
1008,31,49000,630,0,USA
1009,24,38000,580,1,France
1010,48,96000,710,0,Germany`;

        const res = await fetch("/api/datasets/upload", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                filename: "customer_churn_sample.csv",
                content: sampleCsv
            })
        });
        const data = await res.json();
        if (res.ok) {
            this.currentDatasetId = data.dataset.dataset_id;
            this.datasetViewer.renderDataset(data.dataset, data.preview);
        }
    }

    async handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = async (e) => {
            const content = e.target.result;
            const res = await fetch("/api/datasets/upload", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    filename: file.name,
                    content: content
                })
            });
            const data = await res.json();
            if (res.ok) {
                this.currentDatasetId = data.dataset.dataset_id;
                this.datasetViewer.renderDataset(data.dataset, data.preview);
            }
        };
        reader.readAsText(file);
    }
}

window.app = new DataMorphApp();
