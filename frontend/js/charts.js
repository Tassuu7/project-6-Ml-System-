class ChartRenderer {
    static renderTable(container, records) {
        if (!records || records.length === 0) {
            container.innerHTML = '<div class="empty-state">No records to display.</div>';
            return;
        }
        const cols = Object.keys(records[0]);
        let html = '<table class="data-table"><thead><tr>';
        cols.forEach(c => html += `<th>${c}</th>`);
        html += '</tr></thead><tbody>';

        records.forEach(r => {
            html += '<tr>';
            cols.forEach(c => {
                const val = r[c];
                html += `<td>${val === null ? '<span style="color:#64748b">null</span>' : val}</td>`;
            });
            html += '</tr>';
        });
        html += '</tbody></table>';
        container.innerHTML = html;
    }
}
