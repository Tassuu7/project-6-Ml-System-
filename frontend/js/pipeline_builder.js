/**
 * DataMorph Studio - Visual DAG Pipeline Builder Controller
 * Manages transformer palette, canvas step assembly, and live execution console.
 */

class PipelineBuilder {
    constructor(app) {
        this.app = app;
        this.steps = [];
        this.allTransformers = [];
        this.categories = {
            "Imputation": ["SimpleImputer", "KNNImputer", "IterativeImputer", "MissForestImputer"],
            "Scaling & Normalization": ["StandardScaler", "MinMaxScaler", "RobustScaler", "MaxAbsScaler", "QuantileTransformer", "PowerTransformer", "VectorNormalizer"],
            "Categorical Encoding": ["OneHotEncoder", "OrdinalEncoder", "FrequencyEncoder", "BinaryEncoder", "TargetEncoder", "WeightOfEvidenceEncoder", "HelmertEncoder"],
            "Outlier Handling": ["IQROutlierRemover", "ZScoreOutlierDetector", "IsolationForestDetector", "LocalOutlierFactorDetector", "Winsorizer", "EllipticEnvelopeDetector"],
            "Discretization": ["EqualWidthDiscretizer", "EqualFrequencyDiscretizer", "KMeansDiscretizer", "DecisionTreeDiscretizer"],
            "Feature Selection": ["VarianceThresholdSelector", "CorrelationFilterSelector", "SelectKBestMutualInfo", "RFEFeatureSelector", "GeneticAlgorithmSelector", "ParticleSwarmSelector", "LARSPathSelector"],
            "Temporal & Date": ["CyclicalDateTransformer", "LagFeatureExtractor", "RollingWindowFeatureExtractor", "FourierTransformFeatureExtractor"],
            "Text & NLP": ["TextCleanerTransformer", "TfidfFeatureExtractor", "WordCountExtractor"],
            "Synthetic & Copula": ["GaussianCopulaSynthesizer", "BayesianNetworkSynthesizer", "LaplaceDPMechanism"],
            "Deep Tabular": ["TabularDenoisingAutoencoder", "TabTransformer", "FTTransformerTabular"]
        };

        this.initEventListeners();
    }

    initEventListeners() {
        const searchInput = document.getElementById("palette-search-input");
        if (searchInput) {
            searchInput.addEventListener("input", (e) => this.filterPalette(e.target.value));
        }

        const runBtn = document.getElementById("btn-run-dag");
        if (runBtn) runBtn.addEventListener("click", () => this.executeDAGPipeline());

        const clearBtn = document.getElementById("btn-clear-dag");
        if (clearBtn) clearBtn.addEventListener("click", () => this.clearPipeline());

        const saveRecipeBtn = document.getElementById("btn-save-as-recipe");
        if (saveRecipeBtn) saveRecipeBtn.addEventListener("click", () => this.saveCurrentPipelineAsRecipe());
    }

    loadTransformers(transformersList) {
        this.allTransformers = transformersList || [];
        this.renderPalette();
    }

    renderPalette() {
        const container = document.getElementById("palette-category-list");
        if (!container) return;

        let html = "";
        for (const [cat, transList] of Object.entries(this.categories)) {
            html += `
                <div class="palette-category-group">
                    <div class="palette-category-header">
                        <span>${cat}</span>
                        <span style="font-size:9px; color:var(--text-muted);">(${transList.length})</span>
                    </div>
                    <div class="palette-items-wrapper">
            `;
            transList.forEach(tName => {
                html += `
                    <div class="palette-item" data-trans-type="${tName}" title="Click to add ${tName} to pipeline DAG">
                        <span>${tName}</span>
                        <span class="palette-item-add-icon">+</span>
                    </div>
                `;
            });
            html += `</div></div>`;
        }
        container.innerHTML = html;

        container.querySelectorAll(".palette-item").forEach(item => {
            item.addEventListener("click", () => {
                const tType = item.dataset.transType;
                this.addStep(tType);
            });
        });
    }

    filterPalette(query) {
        const items = document.querySelectorAll(".palette-item");
        const q = (query || "").toLowerCase();
        items.forEach(item => {
            const name = item.dataset.transType.toLowerCase();
            item.style.display = name.includes(q) ? "flex" : "none";
        });
    }

    addStep(transformerType, name = null, params = {}, columns = []) {
        const step = {
            id: `step_${Date.now()}_${Math.random().toString(36).substr(2, 4)}`,
            name: name || transformerType,
            type: transformerType,
            params: params || {},
            columns: columns || []
        };
        this.steps.push(step);
        this.renderCanvas();
    }

    addStepFromRecommendation(transformerConfig) {
        this.addStep(
            transformerConfig.type,
            transformerConfig.name,
            transformerConfig.params || {},
            transformerConfig.columns || []
        );
    }

    removeStep(index) {
        this.steps.splice(index, 1);
        this.renderCanvas();
    }

    clearPipeline() {
        this.steps = [];
        this.renderCanvas();
        const consolePanel = document.getElementById("dag-execution-console");
        if (consolePanel) consolePanel.style.display = "none";
    }

    renderCanvas() {
        const canvas = document.getElementById("dag-steps-canvas");
        if (!canvas) return;

        if (this.steps.length === 0) {
            canvas.innerHTML = `
                <div class="empty-state" style="margin:auto;">
                    <div class="empty-state-icon">☊</div>
                    <div class="empty-state-title">No Steps in Pipeline DAG</div>
                    <div class="empty-state-desc">Select transformers from the left catalog or load a domain recipe template to assemble your preprocessing pipeline.</div>
                </div>
            `;
            return;
        }

        let html = "";
        this.steps.forEach((step, idx) => {
            const isLast = idx === this.steps.length - 1;
            html += `
                <div class="dag-step-node" id="node-${step.id}">
                    <div class="dag-step-left">
                        <div class="dag-step-order">${idx + 1}</div>
                        <div class="dag-step-info">
                            <div class="dag-step-title">${step.name}</div>
                            <div class="dag-step-meta">Algorithm: <code>${step.type}</code> | Columns: ${step.columns.length ? step.columns.join(', ') : 'Auto-All'}</div>
                        </div>
                    </div>
                    <div class="dag-step-actions">
                        <button class="btn btn-outline btn-sm btn-delete-step" data-step-idx="${idx}" title="Remove Step">✕</button>
                    </div>
                </div>
            `;
            if (!isLast) {
                html += `<div class="dag-connector-line">↓</div>`;
            }
        });
        canvas.innerHTML = html;

        canvas.querySelectorAll(".btn-delete-step").forEach(btn => {
            btn.addEventListener("click", (e) => {
                e.stopPropagation();
                this.removeStep(parseInt(btn.dataset.stepIdx, 10));
            });
        });
    }

    async executeDAGPipeline() {
        if (!this.app.currentDatasetId) {
            this.app.showToast("Please load or ingest a dataset first!", "warning");
            return;
        }
        if (this.steps.length === 0) {
            this.app.showToast("Add at least one transformer step to the pipeline DAG!", "warning");
            return;
        }

        const consolePanel = document.getElementById("dag-execution-console");
        const stepsList = document.getElementById("console-steps-list");
        const statusBadge = document.getElementById("console-status-badge");
        const nameInput = document.getElementById("pipeline-name-input");
        const pipelineName = (nameInput && nameInput.value) ? nameInput.value : "ActivePreprocessingDAG";

        if (consolePanel) consolePanel.style.display = "flex";
        if (statusBadge) {
            statusBadge.className = "kpi-badge warning";
            statusBadge.textContent = "Executing...";
        }

        if (stepsList) {
            let initialHtml = `<div class="console-step-item running"><span>⚡ Initializing Execution Context & Ingesting DataFrame...</span><span>RUNNING</span></div>`;
            this.steps.forEach(s => {
                initialHtml += `<div class="console-step-item"><span>▷ ${s.name} (${s.type})</span><span>QUEUED</span></div>`;
            });
            stepsList.innerHTML = initialHtml;
        }

        try {
            const res = await fetch("/api/pipeline/execute", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    dataset_id: this.app.currentDatasetId,
                    name: pipelineName,
                    steps: this.steps
                })
            });

            const data = await res.json();
            if (res.ok && data.status === "success") {
                this.app.transformedDatasetId = data.transformed_dataset_id;
                this.app.latestPythonCode = data.python_code;

                if (statusBadge) {
                    statusBadge.className = "kpi-badge positive";
                    statusBadge.textContent = `Completed in ${data.duration_ms || 15}ms`;
                }

                if (stepsList) {
                    let doneHtml = `<div class="console-step-item success"><span>✓ Dataset Ingested (${data.shape[0]} rows × ${data.shape[1]} features)</span><span>100%</span></div>`;
                    this.steps.forEach(s => {
                        doneHtml += `<div class="console-step-item success"><span>✓ ${s.name} executed cleanly</span><span>SUCCESS</span></div>`;
                    });
                    doneHtml += `<div class="console-step-item success"><span>✓ Output validated and registered as ${data.transformed_dataset_id}</span><span>DONE</span></div>`;
                    stepsList.innerHTML = doneHtml;
                }

                const codeEl = document.getElementById("compiled-python-code");
                if (codeEl && data.python_code) {
                    codeEl.textContent = data.python_code;
                }

                this.app.showToast("Pipeline executed successfully!", "success");
                this.app.refreshOverviewMetrics();
            } else {
                if (statusBadge) {
                    statusBadge.className = "kpi-badge danger";
                    statusBadge.textContent = "Failed";
                }
                if (stepsList) {
                    stepsList.innerHTML += `<div class="console-step-item error"><span>✕ Error: ${data.error || "Pipeline execution failed"}</span><span>FAILED</span></div>`;
                }
                this.app.showToast(`Pipeline execution failed: ${data.error}`, "error");
            }
        } catch (err) {
            this.app.showToast(`Network error: ${err.message}`, "error");
        }
    }

    async saveCurrentPipelineAsRecipe() {
        if (this.steps.length === 0) {
            this.app.showToast("Add steps to the pipeline before saving as a recipe!", "warning");
            return;
        }

        const nameInput = document.getElementById("pipeline-name-input");
        const recipeName = prompt("Enter a name for this custom recipe:", nameInput?.value || "Custom Preprocessing Recipe");
        if (!recipeName) return;

        const res = await fetch("/api/recipes", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                name: recipeName,
                category: "Custom User Recipes",
                steps: this.steps
            })
        });

        if (res.ok) {
            this.app.showToast(`Recipe "${recipeName}" saved successfully!`, "success");
            if (this.app.recipeManager) this.app.recipeManager.loadRecipes();
        } else {
            this.app.showToast("Failed to save recipe.", "error");
        }
    }
}
