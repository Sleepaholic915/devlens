
"""Simulated order API with a discount calculation bug."""


def calculate_total(price: float, quantity: int, discount: float):
    """Return the discounted order total."""
    subtotal = price * quantity

    total = subtotal - discount

    return {
        "status": 200,
        "body": {"total": round(total, 2)},
    }


if __name__ == "__main__":
    print(calculate_total(100, 2, 0.10))
