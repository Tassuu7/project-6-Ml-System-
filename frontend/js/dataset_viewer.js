class DatasetViewer {
    constructor() {
        this.activeDatasetId = null;
    }

    renderDataset(meta, preview) {
        document.getElementById("active-ds-name").textContent = meta.name || meta.dataset_id;
        document.getElementById("active-ds-shape").textContent = `${meta.rows} rows × ${meta.columns.length} cols`;
        document.getElementById("metric-quality-score").textContent = `${meta.quality_score || 95}%`;
        document.getElementById("metric-quality-grade").textContent = `Grade: ${meta.grade || 'A'}`;
        document.getElementById("metric-numeric-count").textContent = meta.numeric_columns ? meta.numeric_columns.length : 0;
        document.getElementById("metric-cat-count").textContent = meta.categorical_columns ? meta.categorical_columns.length : 0;

        const container = document.getElementById("dataset-table-container");
        ChartRenderer.renderTable(container, preview);
    }
}
