class ExportManager {
    static async export(datasetId, format) {
        if (!datasetId) {
            alert("No active dataset to export!");
            return;
        }
        const res = await fetch("/api/export", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({dataset_id: datasetId, format: format})
        });
        const data = await res.json();
        if (res.ok) {
            alert(`Export ready! Saved to ${data.filepath} (${data.rows} rows)`);
        }
    }
}
