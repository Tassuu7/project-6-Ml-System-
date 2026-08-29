document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("login-form");
    const errBanner = document.getElementById("error-banner");

    if (form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            const username = document.getElementById("username").value.trim();
            const password = document.getElementById("password").value.trim();

            try {
                const res = await fetch("/api/auth/login", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({username, password})
                });
                const data = await res.json();
                if (res.ok && data.token) {
                    localStorage.setItem("datamorph_token", data.token);
                    localStorage.setItem("datamorph_user", JSON.stringify(data.user));
                    window.location.href = "/";
                } else {
                    errBanner.textContent = data.error || "Authentication failed";
                    errBanner.style.display = "block";
                }
            } catch (err) {
                errBanner.textContent = "Unable to connect to DataMorph server";
                errBanner.style.display = "block";
            }
        });
    }
});
