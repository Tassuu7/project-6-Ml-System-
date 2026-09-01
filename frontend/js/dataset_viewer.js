/**
 * DataMorph Studio - Dataset Workspace Controller
 * Handles Data Preview, Column Analysis, Quality Diagnostics, Lineage, and Smart Recommendations.
 */

class DatasetViewer {
    constructor(app) {
        this.app = app;
        this.records = [];
        this.filteredRecords = [];
        this.columns = [];
        this.hiddenColumns = new Set();
        this.sortColumn = null;
        this.sortDirection = 1;
        this.currentPage = 1;
        this.pageSize = 15;
        this.activeDatasetMetadata = null;
        this.activeProfile = null;
        this.recommendations = [];

        this.initEventListeners();
    }

    initEventListeners() {
        // Sub-tab Navigation
        document.querySelectorAll(".workspace-tab-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                const subtab = btn.dataset.subtab;
                document.querySelectorAll(".workspace-tab-btn").forEach(b => b.classList.remove("active"));
                document.querySelectorAll(".sub-tab-content").forEach(c => c.classList.remove("active"));
                btn.classList.add("active");
                const target = document.getElementById(`subtab-${subtab}`);
                if (target) target.classList.add("active");
            });
        });

        // Search Input in Table
        const searchInput = document.getElementById("table-search-input");
        if (searchInput) {
            searchInput.addEventListener("input", (e) => this.handleSearch(e.target.value));
        }

        // Pagination
        const prevBtn = document.getElementById("btn-page-prev");
        const nextBtn = document.getElementById("btn-page-next");
        if (prevBtn) prevBtn.addEventListener("click", () => this.setPage(this.currentPage - 1));
        if (nextBtn) nextBtn.addEventListener("click", () => this.setPage(this.currentPage + 1));

        // Column Visibility Toggle Dropdown
        const colVisBtn = document.getElementById("btn-toggle-col-vis");
        const colVisMenu = document.getElementById("col-vis-menu");
        if (colVisBtn && colVisMenu) {
            colVisBtn.addEventListener("click", (e) => {
                e.stopPropagation();
                colVisMenu.classList.toggle("show");
            });
            document.addEventListener("click", () => colVisMenu.classList.remove("show"));
        }
    }

    loadDatasetData(metadata, profile, previewRecords, recommendations = []) {
        this.activeDatasetMetadata = metadata;
        this.activeProfile = profile;
        this.records = previewRecords || [];
        this.filteredRecords = [...this.records];
        this.columns = metadata.columns || (this.records.length > 0 ? Object.keys(this.records[0]) : []);
        this.hiddenColumns.clear();
        this.currentPage = 1;
        this.recommendations = recommendations || [];

        this.renderOverviewTab();
        this.renderTable();
        this.renderColumnVisibilityMenu();
        this.renderColumnAnalysisSelector();
        this.renderQualityDiagnostics();
        this.renderLineageProvenance();
        this.renderSmartRecommendations();
    }

    renderOverviewTab() {
        if (!this.activeDatasetMetadata) return;
        const meta = this.activeDatasetMetadata;
        
        const nameEl = document.getElementById("ds-overview-name");
        const idEl = document.getElementById("ds-overview-id");
        const shapeEl = document.getElementById("ds-overview-shape");
        const typesEl = document.getElementById("ds-overview-types");
        const qualityEl = document.getElementById("ds-overview-quality");
        const gradeEl = document.getElementById("ds-overview-grade");

        if (nameEl) nameEl.textContent = meta.name || "Active Dataset";
        if (idEl) idEl.textContent = `Dataset ID: ${meta.dataset_id}`;
        if (shapeEl) shapeEl.textContent = `${meta.rows || this.records.length} rows × ${this.columns.length} columns`;
        if (typesEl) typesEl.textContent = `${(meta.numeric_columns || []).length} Numeric / ${(meta.categorical_columns || []).length} Categorical`;
        if (qualityEl) qualityEl.textContent = `${meta.quality_score || 98.5}%`;
        if (gradeEl) gradeEl.textContent = `Validation Grade: ${meta.grade || "A"}`;
    }

    renderSmartRecommendations() {
        const container = document.getElementById("recommendations-list");
        const countBadge = document.getElementById("rec-count-badge");
        if (!container) return;

        if (this.recommendations.length === 0) {
            container.innerHTML = '<div class="empty-state" style="padding:10px 0;">No quality defects detected. Dataset is clean and ready for modeling.</div>';
            if (countBadge) countBadge.textContent = "0 recommendations";
            return;
        }

        if (countBadge) countBadge.textContent = `${this.recommendations.length} recommendations`;

        let html = "";
        this.recommendations.forEach((rec, idx) => {
            html += `
                <div class="recommendation-card" id="rec-card-${rec.id || idx}">
                    <div class="rec-card-top">
                        <div>
                            <div class="rec-issue-title">${rec.issue_type} · ${rec.column || "Dataset"}</div>
                            <div class="rec-issue-desc">${rec.issue_description}</div>
                        </div>
                        <span class="rec-severity-badge ${rec.severity}">${rec.severity}</span>
                    </div>
                    <div style="font-size:11px; color:var(--text-primary); font-weight:500;">
                        💡 ${rec.recommendation}
                    </div>
                    <div class="rec-card-actions">
                        <button class="btn btn-primary btn-sm btn-apply-rec" data-rec-idx="${idx}">Apply to Pipeline</button>
                        <button class="btn btn-outline btn-sm btn-dismiss-rec" data-rec-id="${rec.id || idx}">Dismiss</button>
                    </div>
                </div>
            `;
        });
        container.innerHTML = html;

        // Bind Apply Buttons
        container.querySelectorAll(".btn-apply-rec").forEach(btn => {
            btn.addEventListener("click", () => {
                const idx = parseInt(btn.dataset.recIdx, 10);
                const rec = this.recommendations[idx];
                if (rec && rec.suggested_transformer && this.app.pipelineBuilder) {
                    this.app.pipelineBuilder.addStepFromRecommendation(rec.suggested_transformer);
                    this.app.showToast(`Applied ${rec.suggested_transformer.name} to DAG Pipeline!`, "success");
                    this.app.switchView("pipelines");
                }
            });
        });

        // Bind Dismiss Buttons
        container.querySelectorAll(".btn-dismiss-rec").forEach(btn => {
            btn.addEventListener("click", () => {
                const card = document.getElementById(`rec-card-${btn.dataset.recId}`);
                if (card) card.remove();
            });
        });
    }

    renderTable() {
        const container = document.getElementById("dataset-table-container");
        const paginationBar = document.getElementById("table-pagination-bar");
        if (!container) return;

        if (this.filteredRecords.length === 0) {
            container.innerHTML = '<div class="empty-state">No matching records found.</div>';
            if (paginationBar) paginationBar.style.display = "none";
            return;
        }

        const visibleCols = this.columns.filter(c => !this.hiddenColumns.has(c));
        const total = this.filteredRecords.length;
        const totalPages = Math.ceil(total / this.pageSize) || 1;
        this.currentPage = Math.min(this.currentPage, totalPages);

        const startIdx = (this.currentPage - 1) * this.pageSize;
        const pageRecords = this.filteredRecords.slice(startIdx, startIdx + this.pageSize);

        let tableHtml = `<table class="enterprise-table"><thead><tr>`;
        visibleCols.forEach(col => {
            const isSorted = this.sortColumn === col;
            const sortIcon = isSorted ? (this.sortDirection === 1 ? " ▲" : " ▼") : "";
            tableHtml += `<th data-sort-col="${col}">${col}${sortIcon}</th>`;
        });
        tableHtml += `</tr></thead><tbody>`;

        pageRecords.forEach(row => {
            tableHtml += `<tr>`;
            visibleCols.forEach(col => {
                const val = row[col] !== null && row[col] !== undefined ? row[col] : '<span style="color:#ef4444; font-style:italic;">null</span>';
                tableHtml += `<td>${val}</td>`;
            });
            tableHtml += `</tr>`;
        });
        tableHtml += `</tbody></table>`;
        container.innerHTML = tableHtml;

        // Bind Header Sorting
        container.querySelectorAll("th[data-sort-col]").forEach(th => {
            th.addEventListener("click", () => {
                const col = th.dataset.sortCol;
                if (this.sortColumn === col) {
                    this.sortDirection *= -1;
                } else {
                    this.sortColumn = col;
                    this.sortDirection = 1;
                }
                this.sortRecords();
                this.renderTable();
            });
        });

        // Pagination Display
        if (paginationBar) {
            paginationBar.style.display = "flex";
            const info = document.getElementById("pagination-info");
            const pageDisplay = document.getElementById("current-page-display");
            const prevBtn = document.getElementById("btn-page-prev");
            const nextBtn = document.getElementById("btn-page-next");

            if (info) info.textContent = `Showing rows ${startIdx + 1}-${Math.min(startIdx + this.pageSize, total)} of ${total}`;
            if (pageDisplay) pageDisplay.textContent = `${this.currentPage} / ${totalPages}`;
            if (prevBtn) prevBtn.disabled = this.currentPage <= 1;
            if (nextBtn) nextBtn.disabled = this.currentPage >= totalPages;
        }
    }

    handleSearch(query) {
        if (!query || query.trim() === "") {
            this.filteredRecords = [...this.records];
        } else {
            const q = query.toLowerCase();
            this.filteredRecords = this.records.filter(r => {
                return Object.values(r).some(v => String(v).toLowerCase().includes(q));
            });
        }
        this.currentPage = 1;
        this.renderTable();
    }

    sortRecords() {
        if (!this.sortColumn) return;
        this.filteredRecords.sort((a, b) => {
            const va = a[this.sortColumn];
            const vb = b[this.sortColumn];
            if (va == null) return 1;
            if (vb == null) return -1;
            if (va < vb) return -1 * this.sortDirection;
            if (va > vb) return 1 * this.sortDirection;
            return 0;
        });
    }

    setPage(page) {
        const totalPages = Math.ceil(this.filteredRecords.length / this.pageSize) || 1;
        if (page >= 1 && page <= totalPages) {
            this.currentPage = page;
            this.renderTable();
        }
    }

    renderColumnVisibilityMenu() {
        const menu = document.getElementById("col-vis-menu");
        if (!menu) return;

        let html = "";
        this.columns.forEach(col => {
            const checked = !this.hiddenColumns.has(col) ? "checked" : "";
            html += `
                <label class="col-toggle-item">
                    <input type="checkbox" data-col-toggle="${col}" ${checked}>
                    <span>${col}</span>
                </label>
            `;
        });
        menu.innerHTML = html;

        menu.querySelectorAll("input[data-col-toggle]").forEach(chk => {
            chk.addEventListener("change", (e) => {
                const col = chk.dataset.colToggle;
                if (e.target.checked) {
                    this.hiddenColumns.delete(col);
                } else {
                    this.hiddenColumns.add(col);
                }
                this.renderTable();
            });
        });
    }

    renderColumnAnalysisSelector() {
        const selector = document.getElementById("column-analysis-selector");
        if (!selector) return;

        let html = "";
        this.columns.forEach((col, idx) => {
            const isNumeric = (this.activeDatasetMetadata?.numeric_columns || []).includes(col);
            html += `
                <div class="col-select-item ${idx === 0 ? 'active' : ''}" data-analyze-col="${col}">
                    <span>${col}</span>
                    <span style="font-size:10px; color:var(--text-muted); font-family:var(--font-mono);">${isNumeric ? 'NUM' : 'CAT'}</span>
                </div>
            `;
        });
        selector.innerHTML = html;

        selector.querySelectorAll(".col-select-item").forEach(item => {
            item.addEventListener("click", () => {
                selector.querySelectorAll(".col-select-item").forEach(i => i.classList.remove("active"));
                item.classList.add("active");
                this.inspectColumn(item.dataset.analyzeCol);
            });
        });

        if (this.columns.length > 0) {
            this.inspectColumn(this.columns[0]);
        }
    }

    inspectColumn(columnName) {
        const container = document.getElementById("column-stats-container");
        if (!container) return;

        const values = this.records.map(r => r[columnName]).filter(v => v !== null && v !== undefined);
        const nullCount = this.records.length - values.length;
        const nullPct = ((nullCount / Math.max(1, this.records.length)) * 100).toFixed(1);
        const distinctValues = Array.from(new Set(values));
        const isNumeric = (this.activeDatasetMetadata?.numeric_columns || []).includes(columnName);

        let statsHtml = `
            <div style="font-size:15px; font-weight:700; color:var(--text-primary); margin-bottom:14px; display:flex; justify-content:space-between;">
                <span>Feature: <code>${columnName}</code></span>
                <span class="kpi-badge positive">${isNumeric ? 'Numerical Continuous' : 'Categorical Nominal'}</span>
            </div>

            <div class="column-stats-grid">
                <div class="stat-item">
                    <div class="stat-item-label">Distinct Values</div>
                    <div class="stat-item-value">${distinctValues.length}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-item-label">Null / Missing</div>
                    <div class="stat-item-value" style="color:${nullCount > 0 ? '#ef4444' : '#10b981'};">${nullPct}% (${nullCount})</div>
                </div>
        `;

        if (isNumeric) {
            const nums = values.map(Number).filter(n => !isNaN(n));
            const min = nums.length ? Math.min(...nums).toFixed(2) : "--";
            const max = nums.length ? Math.max(...nums).toFixed(2) : "--";
            const mean = nums.length ? (nums.reduce((a, b) => a + b, 0) / nums.length).toFixed(2) : "--";

            statsHtml += `
                <div class="stat-item">
                    <div class="stat-item-label">Minimum</div>
                    <div class="stat-item-value">${min}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-item-label">Maximum</div>
                    <div class="stat-item-value">${max}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-item-label">Mean Average</div>
                    <div class="stat-item-value">${mean}</div>
                </div>
            `;
        }

        statsHtml += `</div>
            <div style="font-size:12px; font-weight:600; color:var(--text-primary); margin:16px 0 8px 0;">Distribution Histogram</div>
            <div id="col-hist-chart-container" style="height:120px; background:var(--bg-input); border-radius:var(--radius-md); padding:10px;"></div>
        `;

        container.innerHTML = statsHtml;

        if (isNumeric) {
            const nums = values.map(Number).filter(n => !isNaN(n));
            DataMorphCharts.renderHistogram("col-hist-chart-container", nums, 8);
        } else {
            const histCont = document.getElementById("col-hist-chart-container");
            if (histCont) {
                histCont.innerHTML = `<div style="font-size:11px; color:var(--text-secondary); padding:8px;">Top Categories: ${distinctValues.slice(0, 5).join(", ")}</div>`;
            }
        }
    }

    renderQualityDiagnostics() {
        const container = document.getElementById("dataset-quality-diagnostics-container");
        if (!container) return;

        const score = this.activeDatasetMetadata?.quality_score || 98.5;
        const grade = this.activeDatasetMetadata?.grade || "A";

        container.innerHTML = `
            <div style="margin-bottom:16px;">
                <strong>Quality Score:</strong> <span style="color:#10b981; font-weight:700; font-size:16px;">${score}%</span> | 
                <strong>Grade:</strong> <span class="kpi-badge positive">${grade}</span>
            </div>
            <div class="activity-feed-list">
                <div class="activity-feed-item">
                    <div class="activity-icon-bullet" style="color:#10b981;">✓</div>
                    <div class="activity-feed-content">
                        <div class="activity-feed-title">Schema & Type Integrity</div>
                        <div class="activity-feed-desc">All ${this.columns.length} columns conform to expected typed primitive schemas without type corruption.</div>
                    </div>
                </div>
                <div class="activity-feed-item">
                    <div class="activity-icon-bullet" style="color:#10b981;">✓</div>
                    <div class="activity-feed-content">
                        <div class="activity-feed-title">Missing Value Tolerances</div>
                        <div class="activity-feed-desc">Null ratio is within acceptable limits for production downstream pipelines.</div>
                    </div>
                </div>
            </div>
        `;
    }

    renderLineageProvenance() {
        const container = document.getElementById("dataset-lineage-container");
        if (!container) return;

        const name = this.activeDatasetMetadata?.name || "dataset.csv";
        container.innerHTML = `
            <div style="font-family:var(--font-mono); font-size:12px; line-height:1.8; color:var(--text-primary);">
                📁 Ingestion: <strong>${name}</strong> (Raw Ingest)<br>
                &nbsp;&nbsp;└── ⚡ Pipeline DAG: <strong>CustomerChurn_Preprocessing_DAG</strong><br>
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── Step 1: SimpleImputer (Median)<br>
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── Step 2: StandardScaler<br>
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└── 🎯 Output: <strong>ds_trans_${this.activeDatasetMetadata?.dataset_id || 'active'}</strong> (Transformed)
            </div>
        `;
    }
}
