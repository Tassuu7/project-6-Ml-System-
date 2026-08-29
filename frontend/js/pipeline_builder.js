class PipelineBuilder {
    constructor(app) {
        this.app = app;
        this.steps = [];
        this.initPalette();
    }

    async initPalette() {
        try {
            const res = await fetch("/api/transformers");
            const data = await res.json();
            const palette = document.getElementById("palette-list");
            if (palette && data.transformers) {
                palette.innerHTML = "";
                data.transformers.forEach(t => {
                    const item = document.createElement("div");
                    item.className = "palette-item";
                    item.innerHTML = `<span>${t}</span> <span>+</span>`;
                    item.addEventListener("click", () => this.addStep(t));
                    palette.appendChild(item);
                });
            }
        } catch (e) {
            console.error("Failed loading transformers", e);
        }
    }

    addStep(transformerType) {
        this.steps.push({
            name: `${transformerType}_${this.steps.length + 1}`,
            type: transformerType,
            columns: [],
            params: {}
        });
        this.renderPipeline();
    }

    clearPipeline() {
        this.steps = [];
        this.renderPipeline();
    }

    renderPipeline() {
        const canvas = document.getElementById("pipeline-steps-list");
        if (!canvas) return;
        if (this.steps.length === 0) {
            canvas.innerHTML = '<div class="empty-pipeline">Add transformers from the palette to construct a DAG pipeline.</div>';
            return;
        }

        canvas.innerHTML = "";
        this.steps.forEach((s, idx) => {
            const node = document.createElement("div");
            node.className = "stage-node";
            node.innerHTML = `
                <div class="stage-info">
                    <div class="stage-name">${idx + 1}. ${s.name}</div>
                    <div class="stage-detail">Type: ${s.type}</div>
                </div>
                <button class="btn btn-sm btn-outline" style="color:#ef4444;" onclick="window.app.pipelineBuilder.removeStep(${idx})">✕</button>
            `;
            canvas.appendChild(node);
        });
    }

    removeStep(idx) {
        this.steps.splice(idx, 1);
        this.renderPipeline();
    }

    async execute() {
        if (!this.app.currentDatasetId) {
            alert("Please upload or load a dataset first!");
            return;
        }
        if (this.steps.length === 0) {
            alert("Please add at least one transformer step to the pipeline!");
            return;
        }

        try {
            const res = await fetch("/api/pipeline/execute", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    dataset_id: this.app.currentDatasetId,
                    steps: this.steps
                })
            });
            const data = await res.json();
            if (res.ok) {
                alert(`Pipeline Executed Successfully! Processed shape: ${data.shape[0]}x${data.shape[1]}`);
                document.getElementById("compiled-python-code").textContent = data.python_code || "";
                this.app.transformedDatasetId = data.transformed_dataset_id;
                this.app.datasetViewer.renderDataset({
                    name: `Transformed_${this.app.currentDatasetId}`,
                    rows: data.shape[0],
                    columns: Object.keys(data.preview[0] || {}),
                    quality_score: 98,
                    grade: 'A+'
                }, data.preview);
            } else {
                alert(`Pipeline execution error: ${data.error}`);
            }
        } catch (e) {
            alert(`Execution failed: ${e}`);
        }
    }
}
