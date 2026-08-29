class DatasetViewer {
    constructor() {
        this.records = [];
        this.filteredRecords = [];
        this.columns = [];
        this.pageSize = 10;
        this.currentPage = 1;
        this.sortColumn = null;
        this.sortAsc = true;
        this.initControls();
    }

    initControls() {
        const searchInput = document.getElementById("table-search-input");
        if (searchInput) {
            searchInput.addEventListener("input", (e) => {
                const term = e.target.value.toLowerCase().trim();
                if (!term) {
                    this.filteredRecords = [...this.records];
                } else {
                    this.filteredRecords = this.records.filter(row => {
                        return Object.values(row).some(v => String(v).toLowerCase().includes(term));
                    });
                }
                this.currentPage = 1;
                this.renderTablePage();
            });
        }

        const prevBtn = document.getElementById("btn-page-prev");
        const nextBtn = document.getElementById("btn-page-next");
        if (prevBtn) {
            prevBtn.addEventListener("click", () => {
                if (this.currentPage > 1) {
                    this.currentPage--;
                    this.renderTablePage();
                }
            });
        }
        if (nextBtn) {
            nextBtn.addEventListener("click", () => {
                const maxPage = Math.ceil(this.filteredRecords.length / this.pageSize);
                if (this.currentPage < maxPage) {
                    this.currentPage++;
                    this.renderTablePage();
                }
            });
        }
    }

    renderDataset(meta, preview) {
        document.getElementById("active-ds-name").textContent = meta.name || meta.dataset_id;
        document.getElementById("active-ds-shape").textContent = `${meta.rows} rows × ${meta.columns.length} cols`;
        document.getElementById("metric-quality-score").textContent = `${meta.quality_score || 96}%`;
        document.getElementById("metric-quality-grade").textContent = `Grade: ${meta.grade || 'A+'}`;
        document.getElementById("metric-numeric-count").textContent = meta.numeric_columns ? meta.numeric_columns.length : 0;
        document.getElementById("metric-cat-count").textContent = meta.categorical_columns ? meta.categorical_columns.length : 0;

        this.records = preview || [];
        this.filteredRecords = [...this.records];
        this.columns = meta.columns || Object.keys(this.records[0] || {});
        this.currentPage = 1;

        // Update Column Dropdown in Transformer Lab
        const colSelect = document.getElementById("lab-column-select");
        if (colSelect) {
            colSelect.innerHTML = "";
            this.columns.forEach(col => {
                const opt = document.createElement("option");
                opt.value = col;
                opt.textContent = col;
                colSelect.appendChild(opt);
            });
        }

        const pagControls = document.getElementById("table-pagination-controls");
        if (pagControls) pagControls.style.display = "flex";

        this.renderTablePage();
    }

    renderTablePage() {
        const container = document.getElementById("dataset-table-container");
        if (!container) return;

        if (this.filteredRecords.length === 0) {
            container.innerHTML = '<div class="empty-state">No matching records found.</div>';
            return;
        }

        const start = (this.currentPage - 1) * this.pageSize;
        const end = Math.min(start + this.pageSize, this.filteredRecords.length);
        const pageRows = this.filteredRecords.slice(start, end);

        let html = '<table class="data-table"><thead><tr>';
        this.columns.forEach(col => {
            const isSorted = this.sortColumn === col;
            const arrow = isSorted ? (this.sortAsc ? ' ↑' : ' ↓') : '';
            html += `<th onclick="window.app.datasetViewer.toggleSort('${col}')" style="cursor:pointer;">${col}${arrow}</th>`;
        });
        html += '</tr></thead><tbody>';

        pageRows.forEach(row => {
            html += '<tr>';
            this.columns.forEach(col => {
                const val = row[col];
                if (val === null || val === undefined || val === '') {
                    html += `<td><span class="null-badge">NULL</span></td>`;
                } else if (typeof val === 'number') {
                    html += `<td style="color:#38bdf8; font-variant-numeric: tabular-nums;">${val}</td>`;
                } else {
                    html += `<td>${val}</td>`;
                }
            });
            html += '</tr>';
        });
        html += '</tbody></table>';

        container.innerHTML = html;

        // Update pagination info
        const info = document.getElementById("pagination-info");
        const pageDisp = document.getElementById("current-page-display");
        if (info) info.textContent = `Showing rows ${start + 1}-${end} of ${this.filteredRecords.length}`;
        if (pageDisp) pageDisp.textContent = `${this.currentPage} / ${Math.ceil(this.filteredRecords.length / this.pageSize)}`;
    }

    toggleSort(col) {
        if (this.sortColumn === col) {
            this.sortAsc = !this.sortAsc;
        } else {
            this.sortColumn = col;
            this.sortAsc = true;
        }

        this.filteredRecords.sort((a, b) => {
            const vA = a[col];
            const vB = b[col];
            if (vA === null) return 1;
            if (vB === null) return -1;
            if (vA < vB) return this.sortAsc ? -1 : 1;
            if (vA > vB) return this.sortAsc ? 1 : -1;
            return 0;
        });

        this.renderTablePage();
    }
}
