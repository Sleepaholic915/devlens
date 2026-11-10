
USERS = {
    123: {"id": 123, "name": "Alice"},
    456: {"id": 456, "name": "Bob"},
}


def get_user(user_id: int):
    """Return a user by ID."""
    user = USERS.get(user_id)

    # BUG: user can be None for an unknown ID.
    return {
        "id": user["id"],
        "name": user["name"],
    }


def handle_get_user(user_id: int):
    try:
        return {"status": 200, "body": get_user(user_id)}
    except Exception:
        return {
            "status": 500,
            "body": {"error": "Internal Server Error"},
        }


if __name__ == "__main__":
    print(handle_get_user(999))
