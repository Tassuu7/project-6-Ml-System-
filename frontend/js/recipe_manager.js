/**
 * DataMorph Studio - Recipe Manager Controller
 * Handles loading, rendering, and applying industry templates and custom user recipes.
 */

class RecipeManager {
    constructor(app) {
        this.app = app;
        this.templates = [];
        this.customRecipes = [];
    }

    async loadRecipes() {
        try {
            const res = await fetch("/api/recipes");
            if (!res.ok) return;
            const data = await res.json();
            this.templates = data.templates || [];
            this.customRecipes = data.custom_recipes || [];
            this.renderTemplates();
            this.renderCustomRecipes();
        } catch (e) {
            console.error("Failed to load recipes", e);
        }
    }

    renderTemplates() {
        const container = document.getElementById("recipes-templates-grid");
        if (!container) return;

        let html = "";
        this.templates.forEach((tmpl, idx) => {
            html += `
                <div class="recipe-card">
                    <div>
                        <div class="recipe-header">
                            <span class="recipe-icon">${tmpl.icon || '📋'}</span>
                            <div>
                                <div class="recipe-name">${tmpl.name}</div>
                                <span class="kpi-badge" style="background:var(--bg-surface-elevated); color:var(--text-secondary);">${tmpl.category}</span>
                            </div>
                        </div>
                        <div class="recipe-desc">${tmpl.description}</div>
                    </div>
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-top:12px;">
                        <span class="recipe-steps-count">${tmpl.steps.length} Transformer Steps</span>
                        <button class="btn btn-primary btn-sm btn-load-recipe" data-recipe-type="template" data-idx="${idx}">Load to Pipeline</button>
                    </div>
                </div>
            `;
        });
        container.innerHTML = html;

        container.querySelectorAll(".btn-load-recipe").forEach(btn => {
            btn.addEventListener("click", () => {
                const idx = parseInt(btn.dataset.idx, 10);
                const tmpl = this.templates[idx];
                if (tmpl && this.app.pipelineBuilder) {
                    this.app.pipelineBuilder.clearPipeline();
                    const nameInput = document.getElementById("pipeline-name-input");
                    if (nameInput) nameInput.value = tmpl.name.replace(/\s+/g, '_');

                    tmpl.steps.forEach(s => {
                        this.app.pipelineBuilder.addStep(s.type, s.name, s.params || {}, s.columns || []);
                    });

                    this.app.showToast(`Loaded "${tmpl.name}" into DAG Pipeline!`, "success");
                    this.app.switchView("pipelines");
                }
            });
        });
    }

    renderCustomRecipes() {
        const container = document.getElementById("custom-recipes-grid");
        if (!container) return;

        if (this.customRecipes.length === 0) {
            container.innerHTML = '<div class="empty-state" style="padding:16px 0;">No custom recipes saved yet. Build a DAG pipeline and click "Save as Recipe" to reuse.</div>';
            return;
        }

        let html = "";
        this.customRecipes.forEach((recipe, idx) => {
            html += `
                <div class="recipe-card">
                    <div>
                        <div class="recipe-header">
                            <span class="recipe-icon">${recipe.icon || '⚡'}</span>
                            <div class="recipe-name">${recipe.name}</div>
                        </div>
                        <div class="recipe-desc">${recipe.description || 'User-saved custom DAG recipe'}</div>
                    </div>
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-top:12px;">
                        <span class="recipe-steps-count">${recipe.steps?.length || 0} Steps</span>
                        <button class="btn btn-secondary btn-sm btn-load-custom-recipe" data-idx="${idx}">Load Recipe</button>
                    </div>
                </div>
            `;
        });
        container.innerHTML = html;

        container.querySelectorAll(".btn-load-custom-recipe").forEach(btn => {
            btn.addEventListener("click", () => {
                const idx = parseInt(btn.dataset.idx, 10);
                const recipe = this.customRecipes[idx];
                if (recipe && this.app.pipelineBuilder) {
                    this.app.pipelineBuilder.clearPipeline();
                    const nameInput = document.getElementById("pipeline-name-input");
                    if (nameInput) nameInput.value = recipe.name.replace(/\s+/g, '_');

                    (recipe.steps || []).forEach(s => {
                        this.app.pipelineBuilder.addStep(s.type, s.name, s.params || {}, s.columns || []);
                    });

                    this.app.showToast(`Loaded "${recipe.name}" into DAG Pipeline!`, "success");
                    this.app.switchView("pipelines");
                }
            });
        });
    }
}
