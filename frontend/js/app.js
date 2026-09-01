/**
 * DataMorph Studio - Master Application Controller
 * Orchestrates navigation, global state, API communications, and sub-controllers.
 */

class DataMorphApp {
    constructor() {
        this.currentView = "overview";
        this.currentDatasetId = null;
        this.transformedDatasetId = null;
        this.latestPythonCode = null;

        // Sub-controllers
        this.datasetViewer = new DatasetViewer(this);
        this.pipelineBuilder = new PipelineBuilder(this);
        this.driftViewer = new DriftViewer(this);
        this.recipeManager = new RecipeManager(this);
        this.runsViewer = new RunsViewer(this);
        this.exportModal = new ExportModal(this);

        this.init();
    }

    async init() {
        this.initNavigation();
        this.initSidebarToggle();
        this.initGlobalSearch();
        this.initKeyboardShortcuts();
        this.initModals();
        this.initFileUploads();
        this.initSandboxLab();
        this.initSettings();

        // Initial Data Fetch
        await this.loadTransformersList();
        await this.refreshOverviewMetrics();
        await this.recipeManager.loadRecipes();
        await this.runsViewer.loadRuns();
        await this.loadActivityFeed();
        await this.loadNotifications();

        // Render trend sparkline
        DataMorphCharts.renderTrendSparkline("overview-trend-chart", [96, 97, 95, 98, 98.5, 99.2]);
    }

    /* ---------------- Navigation & View Routing ---------------- */
    initNavigation() {
        document.querySelectorAll(".nav-item").forEach(btn => {
            btn.addEventListener("click", () => {
                const view = btn.dataset.view;
                if (view) this.switchView(view);
            });
        });

        document.querySelectorAll("[data-nav-target]").forEach(btn => {
            btn.addEventListener("click", () => {
                const target = btn.dataset.navTarget;
                if (target) this.switchView(target);
            });
        });
    }

    switchView(viewName) {
        this.currentView = viewName;

        // Update sidebar active state
        document.querySelectorAll(".nav-item").forEach(btn => {
            btn.classList.toggle("active", btn.dataset.view === viewName);
        });

        // Update view pane
        document.querySelectorAll(".view-pane").forEach(pane => {
            pane.classList.toggle("active", pane.id === `view-${viewName}`);
        });

        // Update topbar breadcrumbs
        const breadcrumbEl = document.getElementById("breadcrumb-current-view");
        if (breadcrumbEl) {
            breadcrumbEl.textContent = viewName.charAt(0).toUpperCase() + viewName.slice(1);
        }

        // View-specific refreshes
        if (viewName === "overview") this.refreshOverviewMetrics();
        if (viewName === "runs") this.runsViewer.loadRuns();
        if (viewName === "recipes") this.recipeManager.loadRecipes();
        if (viewName === "activity") this.loadActivityFeed();
    }

    /* ---------------- Sidebar Collapse & Storage ---------------- */
    initSidebarToggle() {
        const toggleBtn = document.getElementById("btn-toggle-sidebar");
        const sidebar = document.getElementById("app-sidebar");

        const savedState = localStorage.getItem("datamorph_sidebar_collapsed");
        if (savedState === "true" && sidebar) {
            sidebar.classList.add("collapsed");
        }

        if (toggleBtn && sidebar) {
            toggleBtn.addEventListener("click", () => {
                sidebar.classList.toggle("collapsed");
                localStorage.setItem("datamorph_sidebar_collapsed", sidebar.classList.contains("collapsed"));
            });
        }
    }

    /* ---------------- Global Search & Quick Jump ---------------- */
    initGlobalSearch() {
        const input = document.getElementById("global-search-input");
        if (!input) return;

        input.addEventListener("keydown", (e) => {
            if (e.key === "Enter") {
                const val = input.value.trim().toLowerCase();
                if (val.includes("data") || val.includes("table")) this.switchView("datasets");
                else if (val.includes("pipe") || val.includes("dag")) this.switchView("pipelines");
                else if (val.includes("drift") || val.includes("psi")) this.switchView("drift");
                else if (val.includes("recipe") || val.includes("churn")) this.switchView("recipes");
                else if (val.includes("run") || val.includes("history")) this.switchView("runs");
                else if (val.includes("code") || val.includes("export")) this.switchView("exports");
                else if (val.includes("setting")) this.switchView("settings");
                else this.switchView("datasets");
                input.value = "";
            }
        });
    }

    /* ---------------- Keyboard Shortcuts ---------------- */
    initKeyboardShortcuts() {
        document.addEventListener("keydown", (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
                e.preventDefault();
                const search = document.getElementById("global-search-input");
                if (search) search.focus();
            } else if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "b") {
                e.preventDefault();
                const sidebar = document.getElementById("app-sidebar");
                if (sidebar) sidebar.classList.toggle("collapsed");
            } else if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
                if (this.currentView === "pipelines") {
                    e.preventDefault();
                    this.pipelineBuilder.executeDAGPipeline();
                }
            }
        });
    }

    /* ---------------- Modals & Help ---------------- */
    initModals() {
        const helpBtn = document.getElementById("btn-help-modal");
        const helpModal = document.getElementById("help-modal");
        if (helpBtn && helpModal) {
            helpBtn.addEventListener("click", () => helpModal.classList.add("active"));
        }

        const notifBtn = document.getElementById("btn-notifications-toggle");
        const notifModal = document.getElementById("notifications-modal");
        if (notifBtn && notifModal) {
            notifBtn.addEventListener("click", () => notifModal.classList.add("active"));
        }

        document.querySelectorAll("[data-close-modal]").forEach(btn => {
            btn.addEventListener("click", () => {
                const modalId = btn.dataset.closeModal;
                const m = document.getElementById(modalId);
                if (m) m.classList.remove("active");
            });
        });

        document.querySelectorAll(".modal-overlay").forEach(overlay => {
            overlay.addEventListener("click", (e) => {
                if (e.target === overlay) overlay.classList.remove("active");
            });
        });

        const logoutBtn = document.getElementById("btn-logout");
        if (logoutBtn) {
            logoutBtn.addEventListener("click", () => {
                if (confirm("Are you sure you want to sign out of DataMorph Studio?")) {
                    window.location.href = "/login.html";
                }
            });
        }
    }

    /* ---------------- Dataset Ingestion & Uploads ---------------- */
    initFileUploads() {
        const topbarInput = document.getElementById("topbar-file-input");
        if (topbarInput) {
            topbarInput.addEventListener("change", (e) => this.handleFileUpload(e.target.files[0]));
        }

        const sampleBtn = document.getElementById("btn-quick-sample");
        if (sampleBtn) {
            sampleBtn.addEventListener("click", () => this.loadSampleData());
        }
    }

    async handleFileUpload(file) {
        if (!file) return;
        this.showToast(`Ingesting ${file.name}...`, "info");

        const reader = new FileReader();
        reader.onload = async (e) => {
            const content = e.target.result;
            try {
                const res = await fetch("/api/datasets/upload", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({
                        filename: file.name,
                        content: content
                    })
                });

                const data = await res.json();
                if (res.ok && data.dataset) {
                    this.currentDatasetId = data.dataset.dataset_id;
                    this.transformedDatasetId = null;
                    await this.fetchAndLoadDataset(this.currentDatasetId);
                    this.showToast(`Dataset "${file.name}" ingested successfully!`, "success");
                    this.switchView("datasets");
                    this.refreshOverviewMetrics();
                } else {
                    this.showToast(`Upload error: ${data.error || "Failed to parse file"}`, "error");
                }
            } catch (err) {
                this.showToast(`Network error: ${err.message}`, "error");
            }
        };
        reader.readAsText(file);
    }

    async loadSampleData() {
        const sampleCsv = `customer_id,age,annual_income,credit_score,tenure_years,churn,country
1001,34,65000,720,3,0,USA
1002,45,82000,680,5,1,Germany
1003,28,45000,590,1,0,France
1004,52,115000,790,8,0,USA
1005,,54000,610,2,1,France
1006,39,71000,640,4,0,Germany
1007,61,95000,750,12,0,USA
1008,23,31000,520,1,1,France
1009,47,88000,700,6,0,Germany
1010,31,58000,660,3,0,USA`;

        const blob = new Blob([sampleCsv], { type: "text/csv" });
        const file = new File([blob], "customer_churn_sample.csv");
        await this.handleFileUpload(file);
    }

    async fetchAndLoadDataset(datasetId) {
        try {
            const res = await fetch(`/api/datasets?id=${datasetId}`);
            if (!res.ok) return;
            const data = await res.json();

            this.datasetViewer.loadDatasetData(
                data.metadata,
                data.profile,
                data.preview,
                data.recommendations || []
            );

            // Populate Lab Column Selectors
            const labColSelect = document.getElementById("lab-column-select");
            if (labColSelect && data.metadata?.columns) {
                labColSelect.innerHTML = data.metadata.columns.map(c => `<option value="${c}">${c}</option>`).join("");
            }
        } catch (e) {
            console.error("Error fetching dataset", e);
        }
    }

    /* ---------------- Transformers List & Sandbox Lab ---------------- */
    async loadTransformersList() {
        try {
            const res = await fetch("/api/transformers");
            if (!res.ok) return;
            const data = await res.json();
            const list = data.transformers || [];

            this.pipelineBuilder.loadTransformers(list);

            const labSelect = document.getElementById("lab-transformer-select");
            if (labSelect) {
                labSelect.innerHTML = list.map(t => `<option value="${t}">${t}</option>`).join("");
            }
        } catch (e) {
            console.error("Failed to load transformers", e);
        }
    }

    initSandboxLab() {
        const runLabBtn = document.getElementById("btn-run-lab-preview");
        if (!runLabBtn) return;

        runLabBtn.addEventListener("click", async () => {
            if (!this.currentDatasetId) {
                this.showToast("Load a dataset first to test transformations!", "warning");
                return;
            }

            const tSelect = document.getElementById("lab-transformer-select");
            const colSelect = document.getElementById("lab-column-select");
            const selectedCols = Array.from(colSelect.selectedOptions).map(o => o.value);

            const container = document.getElementById("lab-preview-table-container");
            if (container) container.innerHTML = '<div class="empty-state">Computing transformation matrix...</div>';

            try {
                const res = await fetch("/api/transform/preview", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({
                        dataset_id: this.currentDatasetId,
                        transformer_type: tSelect.value,
                        columns: selectedCols.length ? selectedCols : undefined
                    })
                });

                const data = await res.json();
                if (res.ok && data.preview) {
                    this.renderPreviewTable(container, data.preview);
                    this.showToast(`Applied ${tSelect.value} preview cleanly!`, "success");
                } else {
                    if (container) container.innerHTML = `<div class="empty-state" style="color:#ef4444;">Error: ${data.error || "Preview failed"}</div>`;
                }
            } catch (err) {
                if (container) container.innerHTML = `<div class="empty-state" style="color:#ef4444;">Network error: ${err.message}</div>`;
            }
        });
    }

    renderPreviewTable(container, records) {
        if (!records || records.length === 0) {
            container.innerHTML = '<div class="empty-state">No transformed records returned.</div>';
            return;
        }

        const cols = Object.keys(records[0]);
        let html = `<table class="enterprise-table"><thead><tr>`;
        cols.forEach(c => html += `<th>${c}</th>`);
        html += `</tr></thead><tbody>`;

        records.slice(0, 15).forEach(row => {
            html += `<tr>`;
            cols.forEach(c => html += `<td>${row[c] !== null && row[c] !== undefined ? row[c] : 'null'}</td>`);
            html += `</tr>`;
        });
        html += `</tbody></table>`;
        container.innerHTML = html;
    }

    /* ---------------- Overview Metrics & Catalog ---------------- */
    async refreshOverviewMetrics() {
        try {
            const res = await fetch("/api/overview");
            if (!res.ok) return;
            const data = await res.json();

            const kpis = data.kpis || {};
            const totalDsEl = document.getElementById("kpi-total-datasets");
            const totalRunsEl = document.getElementById("kpi-total-runs");
            const avgQualEl = document.getElementById("kpi-avg-quality");
            const driftAlertsEl = document.getElementById("kpi-drift-alerts");

            if (totalDsEl) totalDsEl.textContent = kpis.total_datasets || 0;
            if (totalRunsEl) totalRunsEl.textContent = kpis.total_runs || 0;
            if (avgQualEl) avgQualEl.textContent = `${kpis.avg_quality_score || 98.5}%`;
            if (driftAlertsEl) driftAlertsEl.textContent = kpis.drift_alerts_count || 0;

            // Render Recent Datasets
            const dsBody = document.getElementById("dashboard-datasets-body");
            if (dsBody && data.recent_datasets?.length) {
                let html = "";
                data.recent_datasets.forEach(ds => {
                    html += `
                        <tr>
                            <td><strong>${ds.name}</strong></td>
                            <td style="font-family:var(--font-mono);">${ds.rows || 0} × ${(ds.columns || []).length}</td>
                            <td><span style="color:#10b981; font-weight:700;">${ds.quality_score || 98.5}%</span></td>
                            <td><span class="kpi-badge positive">${ds.grade || 'A'}</span></td>
                            <td><button class="btn btn-secondary btn-sm btn-inspect-ds" data-ds-id="${ds.dataset_id}">Inspect</button></td>
                        </tr>
                    `;
                });
                dsBody.innerHTML = html;

                dsBody.querySelectorAll(".btn-inspect-ds").forEach(b => {
                    b.addEventListener("click", () => {
                        this.currentDatasetId = b.dataset.dsId;
                        this.fetchAndLoadDataset(this.currentDatasetId);
                        this.switchView("datasets");
                    });
                });
            }

            // Render Recent Runs
            const runsBody = document.getElementById("dashboard-runs-body");
            if (runsBody && data.recent_runs?.length) {
                let html = "";
                data.recent_runs.forEach(r => {
                    html += `
                        <tr>
                            <td><code>${r.run_id}</code></td>
                            <td>${r.pipeline_name}</td>
                            <td style="font-family:var(--font-mono);">${r.duration_ms ? r.duration_ms + ' ms' : '--'}</td>
                            <td style="font-family:var(--font-mono);">${r.rows_in || 0} → ${r.rows_out || 0}</td>
                            <td><span class="kpi-badge ${r.status === 'completed' ? 'positive' : 'danger'}">${r.status.toUpperCase()}</span></td>
                        </tr>
                    `;
                });
                runsBody.innerHTML = html;
            }
        } catch (e) {
            console.error("Failed to refresh overview", e);
        }
    }

    /* ---------------- Activity & Notifications ---------------- */
    async loadActivityFeed() {
        try {
            const res = await fetch("/api/activity");
            if (!res.ok) return;
            const data = await res.json();
            const acts = data.activities || [];

            const overviewFeed = document.getElementById("overview-activity-feed");
            const fullFeed = document.getElementById("activity-full-feed");

            let html = "";
            if (acts.length === 0) {
                html = '<div class="empty-state" style="padding:16px 0;">No system activities recorded.</div>';
            } else {
                acts.forEach(a => {
                    const icon = a.level === "success" ? "✓" : (a.level === "error" ? "✕" : "ℹ");
                    const iconColor = a.level === "success" ? "#10b981" : (a.level === "error" ? "#ef4444" : "#3b82f6");
                    html += `
                        <div class="activity-feed-item">
                            <div class="activity-icon-bullet" style="color:${iconColor};">${icon}</div>
                            <div class="activity-feed-content">
                                <div class="activity-feed-title">${a.title}</div>
                                <div class="activity-feed-desc">${a.details}</div>
                                <div class="activity-feed-time">${a.timestamp}</div>
                            </div>
                        </div>
                    `;
                });
            }

            if (overviewFeed) overviewFeed.innerHTML = html;
            if (fullFeed) fullFeed.innerHTML = html;
        } catch (e) {
            console.error("Failed to load activity", e);
        }
    }

    async loadNotifications() {
        try {
            const res = await fetch("/api/notifications");
            if (!res.ok) return;
            const data = await res.json();
            const notifs = data.notifications || [];
            const badge = document.getElementById("notification-badge-count");
            const modalBody = document.getElementById("notifications-modal-body");

            if (badge) {
                if (data.unread_count > 0) {
                    badge.style.display = "block";
                    badge.textContent = data.unread_count;
                } else {
                    badge.style.display = "none";
                }
            }

            if (modalBody && notifs.length > 0) {
                let html = '<div class="activity-feed-list">';
                notifs.forEach(n => {
                    html += `
                        <div class="activity-feed-item">
                            <div class="activity-icon-bullet" style="color:${n.level === 'success' ? '#10b981' : '#f59e0b'};">●</div>
                            <div class="activity-feed-content">
                                <div class="activity-feed-title">${n.title}</div>
                                <div class="activity-feed-desc">${n.details}</div>
                                <div class="activity-feed-time">${n.timestamp}</div>
                            </div>
                        </div>
                    `;
                });
                html += '</div>';
                modalBody.innerHTML = html;
            }
        } catch (e) {
            console.error("Failed to load notifications", e);
        }
    }

    /* ---------------- Settings & Theme Manager ---------------- */
    initSettings() {
        const themeSelect = document.getElementById("settings-theme-select");
        const applyThemeBtn = document.getElementById("btn-apply-theme");

        if (applyThemeBtn && themeSelect) {
            applyThemeBtn.addEventListener("click", () => {
                const theme = themeSelect.value;
                document.documentElement.setAttribute("data-theme", theme);
                localStorage.setItem("datamorph_theme", theme);
                this.showToast(`Theme updated to ${theme}!`, "success");
            });
        }

        const savedTheme = localStorage.getItem("datamorph_theme");
        if (savedTheme) {
            document.documentElement.setAttribute("data-theme", savedTheme);
            if (themeSelect) themeSelect.value = savedTheme;
        }

        const saveProfileBtn = document.getElementById("btn-save-profile-settings");
        if (saveProfileBtn) {
            saveProfileBtn.addEventListener("click", () => {
                const name = document.getElementById("settings-fullname")?.value;
                const role = document.getElementById("settings-role")?.value;
                if (name) {
                    const nameEl = document.getElementById("sidebar-user-name");
                    if (nameEl) nameEl.textContent = name;
                }
                if (role) {
                    const roleEl = document.getElementById("sidebar-user-role");
                    if (roleEl) roleEl.textContent = role;
                }
                this.showToast("Profile updated successfully!", "success");
            });
        }
    }

    /* ---------------- Toast Notification Center ---------------- */
    showToast(message, type = "info") {
        const container = document.getElementById("toast-container");
        if (!container) return;

        const toast = document.createElement("div");
        toast.className = `toast ${type}`;
        const icon = type === "success" ? "✓" : (type === "error" ? "✕" : (type === "warning" ? "⚠" : "ℹ"));
        toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;

        container.appendChild(toast);
        setTimeout(() => {
            toast.style.opacity = "0";
            setTimeout(() => toast.remove(), 200);
        }, 3500);
    }
}

// Global App Bootstrapper
document.addEventListener("DOMContentLoaded", () => {
    window.DataMorph = new DataMorphApp();
});
