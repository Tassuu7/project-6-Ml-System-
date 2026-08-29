"""
DataMorph Studio - Authentication API Router
Handles login, token issuance, user profile, and session verification.
"""

from datamorph.utils.security import hash_password, verify_password, generate_token, verify_token


def handle_login(db, body: dict) -> tuple:
    username = body.get("username", "").strip()
    password = body.get("password", "").strip()

    if not username or not password:
        return 400, {"error": "Username and password required"}

    users = db.get_all("users")
    user = users.get(username)

    # Auto-seed default admin if database is new
    if not user and username == "admin" and password == "admin123":
        user_id = "usr_admin"
        hashed = hash_password(password)
        user = {"user_id": user_id, "username": "admin", "password_hash": hashed, "role": "lead_data_scientist"}
        db.set("users", "admin", user)

    if not user or not verify_password(password, user.get("password_hash", "")):
        return 401, {"error": "Invalid credentials"}

    token = generate_token(user["user_id"], user["username"], role=user.get("role", "engineer"))
    return 200, {
        "token": token,
        "user": {
            "user_id": user["user_id"],
            "username": user["username"],
            "role": user.get("role", "engineer")
        }
    }
