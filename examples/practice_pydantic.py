from pydantic import BaseModel, ValidationError


class APIFailure(BaseModel):
    endpoint: str
    status_code: int
    has_error: bool


# Case 1: Valid input
valid_data = {
    "endpoint": "/api/users/123",
    "status_code": 500,
    "has_error": True,
}

failure = APIFailure.model_validate(valid_data)

print("=== Valid Input ===")
print(failure)
print("Endpoint:", failure.endpoint)
print("As JSON:", failure.model_dump_json(indent=2))


# Case 2: Invalid input
invalid_data = {
    "endpoint": "/api/users/123",
    "status_code": "not a number",
    "has_error": True,
}

print("\n=== Invalid Input ===")

try:
    APIFailure.model_validate(invalid_data)
except ValidationError as e:
    print("Validation failed:")
    print(e)
