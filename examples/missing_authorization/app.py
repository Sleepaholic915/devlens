
"""Simulated order API with missing ownership authorization."""

ORDERS = {
    101: {"id": 101, "owner_id": 1, "total": 50},
    102: {"id": 102, "owner_id": 2, "total": 75},
}


def get_order(order_id: int, current_user_id: int):
    """Return an order for the authenticated user."""
    order = ORDERS.get(order_id)

    if order is None:
        return {
            "status": 404,
            "body": {"error": "Order not found"},
        }

    return {
        "status": 200,
        "body": order,
    }


if __name__ == "__main__":
    print(get_order(102, current_user_id=1))
