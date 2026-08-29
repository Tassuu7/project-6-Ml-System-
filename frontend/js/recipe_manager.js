class RecipeManager {
    static copyCode() {
        const code = document.getElementById("compiled-python-code").textContent;
        navigator.clipboard.writeText(code).then(() => {
            alert("Compiled Python script copied to clipboard!");
        });
    }
}
